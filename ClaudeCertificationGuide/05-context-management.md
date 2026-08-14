# Domain 5: Context Management & Reliability (15%)

> Nguồn: https://claudecertificationguide.com/learn/5-context-management/

---

## 5.1 Context Window Management

### Khái niệm cốt lõi
Context window management là nền tảng cho hệ thống Claude-based đáng tin cậy. Tài liệu nói: "Mọi conversation multi-turn, mọi pipeline multi-agent, mọi task extraction document dài phụ thuộc vào cái gì bạn cho vào context window."

### Bẫy Progressive Summarisation
**Vấn đề**: khi conversation dài ra, team thường dùng progressive summarisation để giải phóng context. Tuy nhiên cách này phá hủy có hệ thống dữ liệu giao dịch quan trọng gồm giá trị số, ngày tháng, phần trăm, kỳ vọng khách hàng.

**Ví dụ**:
- Gốc: "I'd like a refund of $247.83 for order #8891 placed on March 3rd"
- Sau summarise: "Customer wants a refund for a recent order"

Số tiền, order ID, ngày tháng — thiết yếu để xử lý — biến mất hoàn toàn.

**Giải pháp: Persistent Case Facts Block**. Trích xuất fact giao dịch vào 1 block có cấu trúc include trong mọi prompt, nằm ngoài history bị summarise. Block này không bao giờ bị summarise, tồn tại xuyên suốt mọi turn.

```json
{
  "caseFactsBlock": {
    "customerId": "C-4421",
    "issues": [
      {
        "orderId": "#8891",
        "orderDate": "2024-03-03",
        "refundAmount": "$247.83",
        "status": "pending_refund",
        "itemDescription": "Wireless headphones — defective"
      }
    ]
  }
}
```
Với session nhiều vấn đề, tạo entry riêng cho mỗi problem kèm đầy đủ order ID, số tiền, status để tránh nhiễu chéo trong lúc summarise.

### Hiệu ứng "Lost in the Middle"
**Vấn đề**: model xử lý đáng tin cậy thông tin ở đầu và cuối input dài. Nội dung chôn giữa nhận ít attention hơn hoặc có thể bị bỏ sót hoàn toàn — hiện tượng đã được tài liệu hóa kỹ ở LLM.

**Fix cấu trúc**: đặt tóm tắt finding chính ở đầu input tổng hợp và dùng section header tường minh xuyên suốt.

```
## Key Findings Summary
- Source A: 12% market growth in renewable sector (2023)
- Source B: Patent filings increased 34% year-on-year
- Source C: Regulatory framework delayed until Q3 2025

## Detailed Findings

### Source A: Market Analysis Report
[Full details here...]

### Source B: Patent Database Analysis
[Full details here...]

### Source C: Regulatory Review
[Full details here...]
```

**Insight chính**: fix là cấu trúc, không phải prompt. Bảo model "chú ý tới mọi thứ" không đáng tin cậy để vượt qua hiệu ứng vị trí.

### Tool Result Trimming
**Kẻ giết context thầm lặng**: order lookup thường trả 40+ field gồm internal audit timestamp, warehouse code, shipping carrier ID, fulfilment centre identifier. Phần lớn không liên quan nhu cầu thực của khách (có thể chỉ 5 field quan trọng), nhưng tốn token qua mỗi turn sau khi conversation history tích lũy.

```python
def trim_order_result(raw_result, relevant_fields=None):
    if relevant_fields is None:
        relevant_fields = [
            "order_id", "order_date", "total_amount",
            "return_eligible", "item_description"
        ]
    return {k: v for k, v in raw_result.items() if k in relevant_fields}
```
Trim nên xảy ra trong `PostToolUse` hook hoặc trong chính tool, trước khi kết quả vào conversation history. Một khi data verbose tích lũy trong context, nó tồn tại qua mọi turn.

### Yêu cầu Full Conversation History
Claude API không giữ server-side session state. Mỗi request phải include toàn bộ conversation history để giữ coherence hội thoại. Bỏ sót message trước đó khiến model mất hiểu context. Điều này tạo căng thẳng: cần full history cho coherence, nhưng history phình to theo mỗi turn. Persistent case facts block giải quyết bằng cách tách fact quan trọng khỏi narrative có thể summarise.

### Tối ưu Upstream Agent
Trong pipeline multi-agent, agent upstream thường truyền reasoning chain verbose và raw content mà downstream agent không dùng được. Khi research subagent gửi toàn bộ thought process cho synthesis agent với context giới hạn, token lãng phí vào reasoning không dùng được.

**Giải pháp: Structured Outputs**. Sửa agent upstream để trả data có cấu trúc gồm key fact, citation, relevance score thay vì nội dung và reasoning verbose.

```json
{
  "findings": [
    {
      "claim": "Renewable energy investment grew 12% in 2023",
      "source": "IEA World Energy Report 2024",
      "sourceUrl": "https://example.com/report",
      "relevanceScore": 0.92,
      "publicationDate": "2024-01-15"
    }
  ]
}
```
Lợi ích: tiết kiệm token và cho phép downstream agent xử lý finding mà không cần re-parse prose verbose.

### Prompt Caching
Prompt caching là nửa còn lại của kinh tế học context. Thay vì giảm nội dung hiển thị, caching tránh reprocess phần chưa đổi.

**Cách hoạt động**: đánh dấu prefix ổn định với breakpoint `cache_control`. API lưu prefix đã xử lý và tái sử dụng ở request sau, tính phí 1 phần nhỏ input cost cho token cached.

**Quy tắc layout quan trọng**: caching match từ đầu prompt, prefix theo prefix. Layout quyết định cache hit thành công.

**Thứ tự đúng**:
```python
messages = [
    {
        "role": "system",
        "content": [
            {"type": "text", "text": LONG_STATIC_INSTRUCTIONS},
            {"type": "text", "text": REFERENCE_DOC,
             "cache_control": {"type": "ephemeral"}},
        ],
    },
    {"role": "user", "content": dynamic_user_message},
]
```
**Cảnh báo quan trọng**: đặt nội dung tĩnh trước (system instruction, tool definition, reference document) theo sau bởi breakpoint, rồi tới nội dung động. Đảo ngược thứ tự loại bỏ hoàn toàn lợi ích caching. Ephemeral breakpoint tồn tại khoảng 5 phút kể từ lần dùng cuối, khiến caching hiệu quả cho burst request liên quan nhưng không hiệu quả cho nội dung tái dùng cách nhau vài giờ.

### Exam traps

**Trap 1 — Ngộ nhận Progressive Summarisation an toàn**: tin rằng progressive summarisation an toàn cho dữ liệu giao dịch. Thực tế: summarisation phá hủy có hệ thống giá trị số, ngày tháng, identifier cụ thể. Persistent case facts block phải giữ chúng ngoài history bị summarise.

**Trap 2 — Fix "Lost in Middle" bằng prompt**: giả định bảo model "chú ý mọi thứ" giải quyết được hiệu ứng lost-in-middle. Fix thực sự là cấu trúc: đặt finding chính ở đầu, dùng section header tường minh. Nhắc nhở dựa trên prompt không đáng tin cậy cho hiệu ứng vị trí.

**Trap 3 — Giữ nguyên toàn bộ Tool Result**: giữ full tool result trong context vì "model có thể cần sau này". Tool result 40+ field không trim nhanh chóng làm cạn token budget qua các turn. Trim về field liên quan trước khi kết quả vào conversation history là thiết yếu, không phải optional.

**Trap 4 — Truncate Conversation có chọn lọc**: tin rằng conversation history có thể truncate có chọn lọc mà không hệ quả. API stateless. Mỗi request cần full conversation history. Truncate có chọn lọc phá vỡ coherence hội thoại. Dùng case facts block và summarisation làm alternative cho truncation.

### Practice scenario
Customer support agent trong session nhiều vấn đề sau đó reference "your recent refund request" thay vì cụ thể "$247.83 refund for order #8891". Conversation history bị summarise để quản lý độ dài context. **Đáp án đúng**: trích xuất fact giao dịch (số tiền, ngày tháng, order number) vào 1 persistent case facts block include trong mọi prompt, nằm ngoài history bị summarise.

**Vì sao option khác fail**: bảo model giữ nguyên giá trị không vượt qua được mất mát data có hệ thống của summarisation; retrieval database ngoài thêm phức tạp không giải quyết root cause; tăng kích thước context window đắt và chỉ trì hoãn chứ không giải quyết vấn đề.

### Key takeaway
"Persistent case facts block là pattern quan trọng nhất trong context window management. Trích xuất fact giao dịch (số tiền, ngày tháng, order number) vào 1 block có cấu trúc include trong mọi prompt và không bao giờ summarise."

---

## 5.2 Escalation & Ambiguity Resolution

### Tổng quan
Lesson này bao phủ việc calibrate escalation trigger trong agent customer support, tập trung phân biệt lý do escalation hợp lệ khỏi anti-pattern không đáng tin.

### 3 trigger escalation hợp lệ

**1. Yêu cầu tường minh gặp người thật**: khi khách trực tiếp hỏi nói chuyện với người thật, agent phải escalate ngay lập tức không cố resolve trước. Guide nhấn mạnh đây là "quy tắc tuyệt đối không ngoại lệ".

**2. Policy Exception hoặc Gap**: escalation cần thiết khi yêu cầu nằm ngoài policy đã document. Phân biệt quan trọng: **Policy gap** — policy không đề cập tình huống (cần escalation); **Policy violation** — policy có câu trả lời đã document (không cần escalation).

**3. Không thể tiến triển ý nghĩa**: sau khi thử resolve thực sự thất bại, escalation phù hợp khi: tool trả error không giải quyết được, không có access hệ thống cần thiết, vấn đề liên quan bug kỹ thuật cần engineering can thiệp.

### 2 trigger không đáng tin (Anti-pattern)

**Sentiment-Based Escalation**: "Frustration không tương quan với độ phức tạp case." Khách bực bội với giao hàng trễ đơn giản có thể giải quyết được, trong khi khách bình tĩnh yêu cầu policy exception cần human judgment. Sentiment đo trạng thái cảm xúc, không phải độ khó vấn đề.

**Self-Reported Confidence Scores**: output confidence của LLM được calibrate kém. Model thường thể hiện confidence sai trên case khó trong khi do dự với case rõ ràng — chính xác lỗi được mô tả trong scenario trên đề thi.

### Sắc thái về Frustration

3 scenario khác nhau cần response khác nhau:

| Scenario | Response |
|---|---|
| Vấn đề đơn giản, khách bực bội | Ghi nhận frustration; đề xuất resolution trực tiếp |
| Khách lặp lại thích người thật sau khi được đề xuất giúp | Escalate (họ từ chối resolution của agent) |
| Khách yêu cầu tường minh người thật từ đầu | Escalate ngay, không điều tra |

### Matching khách hàng mơ hồ
Khi search query trả nhiều match (vd 3 record "John Smith"), agent phải yêu cầu thông tin phân biệt: email, số điện thoại, hoặc order number.

**Không bao giờ dùng heuristic selection** dựa trên: record gần nhất, record hoạt động nhiều nhất, hay ưu tiên thuật toán khác. Rủi ro: vi phạm privacy hoặc hành động sai tài khoản.

### Calibrate System Prompt
Cách tiếp cận hiệu quả nhất liên quan thêm escalation criteria tường minh kèm few-shot example thể hiện: khi nào escalate, khi nào tự resolve, format escalation chính xác (structured handoff với customer ID, root cause, recommended action).

Guide nói: "Prompt optimisation nên luôn đi trước thay đổi kiến trúc."

### Key concept summary
Có 3 trigger hợp lệ; 2 approach phổ biến thất bại. Sentiment analysis và confidence scoring đều thiếu tương quan với độ phức tạp case thực sự hay khả năng resolution.

### Exam traps

| Trap | Thực tế |
|---|---|
| Escalation dựa sentiment có vẻ hợp lý | Frustration ≠ độ phức tạp case |
| Confidence score cung cấp tín hiệu đáng tin | Self-assessment của LLM được calibrate kém |
| Cố resolve trước khi tôn trọng yêu cầu tường minh | Vi phạm quy tắc tuyệt đối |
| Chọn từ match mơ hồ theo heuristic | Rủi ro vi phạm privacy |

### Practice scenario
Support agent có first-contact resolution 55% (mục tiêu: 80%), escalate case đơn giản trong khi cố resolve policy exception phức tạp. **Đáp án đúng (Option A)**: "Thêm escalation criteria tường minh vào system prompt kèm few-shot example thể hiện khi nào escalate vs tự resolve." Cách này giải quyết trực tiếp root cause qua prompt optimization trước thay đổi kiến trúc.

### Build exercise
1. Implement 3 trigger escalation hợp lệ trong system prompt
2. Thêm few-shot example phủ escalation ngay lập tức, case bực bội nhưng giải quyết được, và policy gap
3. Tạo logic matching mơ hồ yêu cầu identifier bổ sung
4. Test 4 scenario quan trọng
5. Verify absolute rule giữ vững: không điều tra trước yêu cầu tường minh gặp người thật; không heuristic selection từ match mơ hồ

---

## 5.3 Error Propagation trong hệ thống Multi-Agent

### Tổng quan
Error propagation quyết định hệ thống recover uyển chuyển hay fail âm thầm. Thách thức cốt lõi: khi subagent fail, thông tin đó trả về coordinator như thế nào để cho phép quyết định recovery thông minh?

### 4 yếu tố của Structured Error Context

**1. Phân loại loại failure**:
- Transient (timeout, rate limit — retry có thể thành công)
- Validation (input sai — cần sửa query)
- Business (vi phạm rule — escalate hoặc tìm alternative)
- Permission (access denied — không thể retry nếu không có authorization)

**2. Tài liệu hành động đã thử**: query cụ thể và tham số đã dùng; target system đã xác định. Ví dụ: "Searched academic database for 'renewable energy policy' with date range 2022-2024".

**3. Bảo toàn Partial Results**: giữ data đã lấy được trước khi fail. Ví dụ: nếu 3/5 source đã lấy trước khi timeout, giữ 3 source đó.

**4. Đề xuất Alternative Approaches**: subagent đề xuất chiến lược recovery. Ví dụ: retry với tham số hẹp hơn, thử database thay thế, dùng cached result.

```json
{
  "status": "partial_failure",
  "failureType": "transient",
  "attemptedAction": {
    "tool": "search_academic_db",
    "query": "renewable energy policy",
    "dateRange": "2022-2024"
  },
  "partialResults": [
    {
      "title": "EU Renewable Energy Directive 2023",
      "source": "EUR-Lex",
      "retrieved": true
    }
  ],
  "alternativeApproaches": [
    "Retry with narrower date range (2023-2024)",
    "Search alternative database: government_publications",
    "Use cached results from previous research session"
  ]
}
```

### 2 Anti-pattern quan trọng

**Anti-pattern 1: Silent Suppression** — trả empty result đánh dấu thành công khi thực sự fail. Subagent gặp timeout nhưng trả `{ "results": [], "status": "success" }`. Coordinator giả định search hoàn thành thành công và không tìm thấy gì. Hệ quả: không retry, không trigger alternative, output cuối trông đầy đủ nhưng có khoảng trống không phát hiện được. Ví dụ customer support: báo "no orders found" khi hệ thống lookup thực sự đang down. **Vì sao tệ nhất**: failure vẫn vô hình; output trông đúng dù thiếu nội dung quan trọng.

**Anti-pattern 2: Workflow Termination** — kill toàn bộ pipeline khi 1 subagent fail. 1 subagent timeout crash toàn bộ research pipeline. Hệ quả: kết quả từ 4 subagent thành công bị vứt bỏ; response không tương xứng với 1 failure; lãng phí công việc đã hoàn thành; không có đường recovery. **Cách đúng**: structured error propagation cho phép coordinator đánh giá thiệt hại và tiếp tục với partial result hoặc recovery có mục tiêu.

### Access Failure vs Valid Empty Result
Phân biệt này được test tường minh trên đề thi.

| Đặc điểm | Access Failure | Valid Empty Result |
|---|---|---|
| Định nghĩa | Tool không tới được data source | Tool tới được source và execute query |
| Ví dụ | Timeout, connection error, permission denial | Query hoàn thành thành công, không match |
| Trạng thái query | Query không execute | Query execute thành công |
| Hành động retry | Cân nhắc retry với tham số y hệt/sửa đổi | Không cần retry — đây LÀ câu trả lời |
| Ví dụ response | `"shouldRetry": True` | `"shouldRetry": False` |

**Access failure response**:
```python
{
    "status": "error",
    "failureType": "transient",
    "message": "Connection timeout after 30s",
    "shouldRetry": True
}
```

**Valid empty result response**:
```python
{
    "status": "success",
    "results": [],
    "message": "Query executed successfully. No matching records found.",
    "shouldRetry": False
}
```

**Vấn đề từ nhầm lẫn**: coi access failure như valid empty result — không bao giờ retry khi lẽ ra nên; coi valid empty result như access failure — lãng phí resource retry query luôn trả về rỗng.

### Coverage Annotations
Synthesis agent nên document topic nào có support tốt vs có gap.

**Ví dụ annotation**: "Section on geothermal energy is limited due to unavailable journal access during research."

**Lợi ích**: người tiêu thụ report biết cái gì được cover đầy đủ; ghi chú tường minh về giới hạn đã biết; gap xuất hiện như source không sẵn có, không phải topic không liên quan; vượt trội hơn hẳn việc âm thầm bỏ qua topic.

### Local Recovery cho Transient Failures
Subagent nên implement local recovery trước khi escalate: retry logic, fallback source, response giảm chất lượng. **Chỉ propagate error subagent không resolve được local.** Giảm độ phức tạp coordinator — coordinator không quản lý retry logic cho mọi subagent; mỗi subagent tự xử lý transient failure của mình.

### Key concept summary
"Structured error context (loại failure, hành động đã thử, partial result, alternative) cho phép coordinator recovery thông minh. 2 anti-pattern là silent suppression (empty result như success) và workflow termination (kill pipeline trên 1 failure). Access failure cần cân nhắc retry; valid empty result thì không."

### Exam traps

| Trap | Vấn đề |
|---|---|
| Catch timeout, trả empty result như success | Silent suppression ngăn mọi recovery; coordinator không bao giờ thử alternative |
| Kill toàn bộ pipeline khi 1 subagent timeout | Workflow termination lãng phí partial result từ subagent thành công |
| Trả 'search unavailable' generic sau khi hết retry | Error generic che giấu query, partial result, alternative khỏi coordinator |
| Retry valid empty result như failure | Lãng phí resource; empty hợp lệ CHÍNH LÀ câu trả lời |

### Practice scenario
Web search subagent timeout trong lúc research topic phức tạp. Thiết kế cách thông tin failure trả về coordinator. **Đáp án đúng (Option C)**: trả structured error context gồm loại failure, query đã thử, partial result, và alternative approach tiềm năng.

### Build exercise — 5 bước
1. Schema error structured với 4 field bắt buộc
2. Phân biệt access failure với valid empty result
3. Local retry logic kèm exponential backoff
4. Coordinator quyết định recovery
5. Coverage annotation cho transparency

---

## 5.4 Codebase Exploration & Context Degradation

### Vấn đề cốt lõi: Context Degradation
**Định nghĩa**: context degradation xảy ra khi model mất nắm bắt các finding cụ thể trước đó khi output verbose tích lũy trong session khảo sát codebase kéo dài. Khác biệt hoàn toàn với token exhaustion.

**Đặc điểm chính**: model chuyển từ reference chi tiết kỹ thuật cụ thể sang nhận xét chung chung. Ví dụ, thay vì trích dẫn "class `OrderRepository` tại `src/repos/order.ts` implement interface base `Repository<T>` kèm custom caching", agent nói "cái này theo repository pattern điển hình".

**Cơ chế root cause**:
1. Mỗi bước khảo sát sinh output verbose (nội dung file, search result, directory listing)
2. Output tích lũy trong conversation context
3. Finding chính xác trước đó bị đẩy sâu hơn vào history context
4. Output verbose gần đây chi phối attention của model
5. Reference cụ thể tới finding trước mờ dần khỏi focus

**Insight quan trọng**: "Context degradation không phải vấn đề token limit. Tăng context window không fix được nó."

### Chiến lược 1: Scratchpad Files
**Mục đích**: lưu finding chính ngoài conversation context, làm cho discovery miễn nhiễm với attention degradation.

**Cái gì được ghi lại**: tên class và path file cụ thể; method signature và implementation; dependency chain đầy đủ chi tiết; finding và issue quan trọng; metric test coverage.

```markdown
# Exploration Scratchpad — Order Service

## Key Classes
- `OrderRepository` (src/repos/order.ts) — implements Repository<T>, custom findById caching
- `OrderService` (src/services/order.ts) — orchestrates OrderRepository + PaymentGateway
- `RefundProcessor` (src/services/refund.ts) — depends on OrderService.getOrderWithItems()

## Dependency Chain
RefundProcessor → OrderService → OrderRepository → PostgreSQL
RefundProcessor → PaymentGateway → Stripe API

## Critical Findings
- RefundProcessor has no retry logic for Stripe API failures
- OrderRepository caches by orderId but cache invalidation on status change is missing
- Test coverage: OrderService has 87% coverage, RefundProcessor has 12%
```

**Pattern triển khai**: agent đọc file scratchpad ở đầu mỗi bước khảo sát tiếp theo thay vì dựa vào history conversation. **Timing**: thiết lập maintain scratchpad ngay từ đầu khảo sát kéo dài, không phải như biện pháp cứu vãn sau khi degrade xảy ra.

### Chiến lược 2: Subagent Delegation
**Lợi ích chính**: context isolation, không phải parallelization. Giá trị thực sự là ngăn context của main agent bị lấp đầy output verbose.

**Pattern delegation**: coordinator agent chính xử lý orchestration cấp cao; subagent nhận task điều tra cụ thể, tập trung; mỗi subagent hoạt động trong context isolated; subagent trả về summary structured cho coordinator.

**Ví dụ task delegate**: "Tìm mọi file test cho order service và report trạng thái coverage"; "Trace refund flow từ API endpoint tới database và liệt kê mọi service trung gian"; "Xác định mọi external API integration và error handling pattern của chúng".

**Phân biệt chính**: "Giá trị thực sự là context isolation. Context của main agent giữ sạch cho orchestration cấp cao trong khi subagent xử lý khảo sát verbose."

### Chiến lược 3: Summary Injection giữa các Phase
**Vấn đề giải quyết**: ngăn "cold start" khi subagent Phase 2 lặp lại công việc khảo sát của Phase 1.

**Triển khai**: tóm tắt finding Phase 1 và tiêm vào prompt subagent Phase 2.

```
- System follows layered architecture: Controllers → Services → Repositories → Database
- Refund flow: RefundController → RefundProcessor → OrderService → PaymentGateway
- Key concern: RefundProcessor has no retry logic for external API failures
- Phase 2 objective: Investigate error handling in RefundProcessor and PaymentGateway
```

**Lợi ích**: agent Phase 2 nhận hiểu biết kiến trúc cần thiết để hỏi câu hỏi chính xác mà không cần khám phá lại cấu trúc hệ thống.

### Chiến lược 4: Lệnh `/compact`
**Mục đích**: chủ động giảm sử dụng context trong session kéo dài bằng cách tóm tắt output khảo sát verbose.

**Pattern dùng**: dùng trong lúc khảo sát, không chỉ khi chạm giới hạn. Giữ thông tin chính trong khi giải phóng không gian context.

**Áp dụng**: "Dùng `/compact` chủ động trong session khảo sát kéo dài, không chỉ khi chạm context limit. Nó ở đó để bảo vệ chất lượng context, không chỉ số lượng."

### Chiến lược 5: Crash Recovery qua Structured State Manifest
**Vấn đề**: session kéo dài có thể fail vì crash, gián đoạn mạng, hay context exhaustion, mất toàn bộ tiến độ.

**Giải pháp**: export state hiện tại ra file manifest tại checkpoint.

**Nội dung manifest**: session ID; số phase hiện tại; danh sách path đã khảo sát (file đã đọc, search đã thực hiện); finding chính đã phát hiện; phase điều tra hiện tại; bước tiếp theo và câu hỏi đang chờ.

```json
{
  "sessionId": "explore-order-service-001",
  "phase": 2,
  "exploredPaths": [
    "src/repos/order.ts",
    "src/services/order.ts",
    "src/services/refund.ts"
  ],
  "keyFindings": {
    "architecture": "Layered: Controllers → Services → Repositories → DB",
    "criticalIssue": "RefundProcessor has no retry logic for Stripe API failures",
    "testCoverage": {"OrderService": "87%", "RefundProcessor": "12%"}
  },
  "nextSteps": [
    "Investigate PaymentGateway error handling",
    "Review RefundProcessor test files",
    "Check cache invalidation logic in OrderRepository"
  ]
}
```

**Quy trình resume**: coordinator load manifest và tiêm vào prompt agent, cho phép khảo sát tiếp tục từ checkpoint gần nhất.

### Exam traps

**Trap 1**: "Tăng context window để giải quyết context degradation" — context degradation không phải về không gian token; window lớn hơn vẫn lấp đầy output verbose và không giải quyết vấn đề attention quality.

**Trap 2**: "Giả định subagent delegation chỉ về parallelisation" — lợi ích chính là context isolation giữ context main agent sạch.

**Trap 3**: "Restart session để fix context degradation mà không lưu state" — restart mất toàn bộ kiến thức tích lũy; lưu finding vào scratchpad file và state manifest trước.

**Trap 4**: "Dùng /compact chỉ khi chạm context limit" — nên dùng chủ động để duy trì chất lượng context suốt session kéo dài.

### Key concept summary
"Context degradation không phải vấn đề token limit — đó là model mất nắm bắt finding cụ thể khi output verbose tích lũy. Scratchpad file lưu discovery chính ngoài context. Subagent delegation isolate khảo sát verbose. Crash recovery manifest ngăn mất tiến độ qua các session."

### Practice scenario
Agent bắt đầu reference "repository pattern điển hình" thay vì tên class cụ thể và dependency chain sau khi khảo sát vài module. **Đáp án đúng (Option B)**: agent maintain scratchpad file ghi finding chính và reference lại cho câu hỏi sau. Vì sao: giải quyết trực tiếp root cause bằng cách lưu chi tiết kỹ thuật cụ thể ngoài conversation context đang degrade, ngăn chuyển sang mô tả chung chung.

---

## 5.5 Human Review & Confidence Calibration

### Mục tiêu học tập
Lesson này xem xét khi nào và cách nào deploy human reviewer trong hệ thống extraction tự động. Thách thức nền tảng liên quan phân bổ năng lực reviewer giới hạn để tối đa accuracy trong khi giảm thiểu cost qua hiểu biết về confidence calibration, cạm bẫy aggregate metric, và cách tiếp cận stratified sampling.

### Bẫy Aggregate Metrics
**Định nghĩa**: ngộ nhận nguy hiểm khi thống kê performance tổng thể che giấu thất bại thảm khốc ở segment cụ thể.

**Minh họa**: hệ thống báo cáo "97% overall accuracy" trên mọi loại document. Có vẻ tuyệt vời, nhưng breakdown lộ ra:

| Document Type | Date Accuracy | Amount Accuracy | Name Accuracy |
|---|---|---|---|
| Standard invoices | 99.5% | 98.2% | 97.8% |
| Handwritten receipts | 60.1% | 55.3% | 71.2% |
| Scanned PDFs | 72.4% | 69.8% | 80.1% |
| International formats | 45.2% | 52.1% | 63.4% |
| **Aggregate** | **97.0%** | **96.1%** | **95.8%** |

**Insight chính**: "97% đó che giấu tỷ lệ fail thảm khốc trên loại document cụ thể." Standard invoice chiếm phần lớn volume, tạo average trọng số theo volume che giấu performance kém ở nơi khác.

**Quy tắc quan trọng**: "luôn validate accuracy theo loại document VÀ field segment trước khi tự động hóa." Không bao giờ dùng aggregate metric đơn lẻ cho quyết định tự động hóa.

### Stratified Random Sampling
**Mục đích**: chọn sample đại diện từ mỗi stratum (loại document, dải confidence, loại field) cho verify của con người trong lúc vận hành liên tục.

**Nguyên tắc thiết yếu**: sample cả extraction confidence cao, không chỉ confidence thấp. Item confidence thấp đã nhận human review; item confidence cao được tự động hóa. Pattern lỗi mới nổi chỉ ảnh hưởng extraction confidence cao mới lộ ra qua stratified sampling.

**2 chức năng chính**: 1) đo accuracy liên tục xác nhận mỗi segment duy trì tỷ lệ accuracy đã validate; 2) phát hiện pattern lỗi mới — khám phá failure mode mới vắng mặt từ validation set gốc.

**Rủi ro không sampling**: "bạn đang bay mù về extraction tự động của mình." Lỗi hệ thống trên format document mới có thể tích lũy không phát hiện được tới khi business process downstream fail.

### Field-Level Confidence Calibration

**Ví dụ scenario**:
```json
{
  "vendorName": {"value": "Acme Corp", "confidence": 0.98},
  "invoiceDate": {"value": "2024-03-15", "confidence": 0.95},
  "totalAmount": {"value": "$1,247.83", "confidence": 0.72},
  "lineItems": {"value": [...], "confidence": 0.61}
}
```

**Vấn đề quan trọng**: "confidence score raw của model không được calibrate." Confidence score 0.95 mang ý nghĩa khác nhau qua các context:
- Field date ở confidence 0.95 = 94% accuracy thực tế
- Field amount ở confidence 0.95 = 82% accuracy thực tế

**Quy trình calibration**: "cần labeled validation set (ground truth data)". Quy trình gồm: 1) lấy document với extraction verify chính xác; 2) chạy model và capture confidence score; 3) so sánh confidence score với ground truth; 4) xây calibration curve theo loại field và loại document.

**Áp dụng routing**: field trên threshold calibrated → tự động hóa (kèm verify bằng stratified sampling); field dưới threshold calibrated → human review; field ở vùng mơ hồ → human review ưu tiên.

### Ưu tiên năng lực Reviewer
**Nguyên tắc nền tảng**: human reviewer là resource đắt đỏ, giới hạn cần phân bổ chiến lược.

**Chiến lược routing**: "Route item độ không chắc chắn cao nhất cho reviewer trước." Ưu tiên gồm: field confidence model thấp; extraction từ document nguồn mơ hồ hoặc mâu thuẫn; loại document có lịch sử accuracy kém; field thể hiện model không chắc chắn (nhiều diễn giải khả thi).

**Cảnh báo anti-pattern**: "KHÔNG rải năng lực reviewer đều khắp mọi extraction." Phân bổ đều lãng phí thời gian vào item confidence cao trong khi item không chắc chắn thiếu judgment con người.

**Triển khai động**: review queue nên sắp theo mức độ không chắc chắn liên tục. Khi reviewer xong item, assignment kế tiếp nên là item độ không chắc chắn cao nhất còn lại, không theo thứ tự thời gian.

### Trình tự Validation trước Tự động hóa
Thứ tự được quy định ngăn failure mode cụ thể:

1. **Đo accuracy theo loại document và field segment** (không phải aggregate)
2. **Calibrate confidence score** dùng labeled validation set
3. **Set threshold calibrated** cho tự động hóa vs human review
4. **Implement stratified random sampling** cho verify liên tục
5. **Chỉ sau đó giảm human review** trên segment thể hiện accuracy nhất quán, đã validate

Nhảy thẳng bước 5 dựa trên aggregate metric là bẫy chính.

### Key concept summary
"97% aggregate accuracy có thể che giấu tỷ lệ lỗi 40% trên loại document cụ thể. Validate accuracy theo loại document VÀ field segment. Calibrate confidence score dùng labeled validation set. Sample extraction confidence cao qua stratified sampling. Ưu tiên năng lực reviewer giới hạn cho item độ không chắc chắn cao nhất."

### Exam traps

| Trap | Vấn đề | Giải pháp |
|---|---|---|
| Dùng aggregate accuracy cho quyết định tự động hóa | Aggregate metric che giấu performance theo loại; 97% overall có thể nghĩa 40% accuracy ở loại cụ thể | Validate theo loại document VÀ field segment trước khi tự động hóa |
| Chỉ sample extraction confidence thấp | Extraction tự động confidence cao có thể phát triển pattern lỗi mới không phát hiện được | Implement stratified random sampling gồm cả item confidence cao |
| Dùng raw confidence score model không calibrate | Confidence score giống nhau mang accuracy thực khác nhau qua field và loại document | Calibrate dùng labeled validation set để thiết lập threshold đáng tin |
| Rải năng lực reviewer đều | Phân bổ đều lãng phí thời gian ở item confidence cao, làm đói item không chắc chắn | Ưu tiên item độ không chắc chắn cao nhất nơi human judgment thêm giá trị tối đa |

### Build exercise — 5 thành phần
1. Mock extraction system: field-level confidence scoring qua loại document (invoice, receipt, scanned PDF, international document) sinh confidence 0.0-1.0 với variation đáng kể theo loại
2. Accuracy tracking theo segment: xây bảng accuracy hiển thị loại document và field kết hợp riêng biệt
3. Calibration module: xây calibration curve map dải confidence với accuracy % thực tế theo loại field/document
4. Stratified random sampling: implement sampling chọn extraction confidence cao để verify, tỷ lệ theo loại document và dải confidence
5. Dynamic review router: xây priority queue sắp item theo độ không chắc chắn, reorder động khi extraction tới, phục vụ item độ không chắc chắn cao nhất cho reviewer sẵn có

---

## 5.6 Information Provenance & Multi-Source Synthesis

### Tổng quan
Lesson này bao phủ cách duy trì output đáng tin trong hệ thống research multi-agent bằng cách bảo toàn claim attribution xuyên suốt pipeline synthesis và xử lý nguồn mâu thuẫn phù hợp.

### Structured Claim-Source Mappings
Mỗi finding cần cấu trúc chuẩn chứa 5 yếu tố bắt buộc:

| Yếu tố | Mục đích |
|---|---|
| Claim | Assertion cụ thể được đưa ra |
| Source URL | Thông tin bắt nguồn từ đâu |
| Document Name | Title của source material |
| Relevant Excerpt | Đoạn văn hỗ trợ nguyên văn |
| Publication Date | Khi source được publish hoặc data thu thập |

**Vấn đề quan trọng**: "Attribution chết trong lúc summarisation" trừ khi được bảo toàn tường minh. Synthesis agent tự nhiên nén finding thành statement paraphrase như "Investment has grown significantly" — mất toàn bộ quantitative data, source, và ngày tháng.

**Ví dụ schema**:
```json
{
  "claim": "Global renewable energy investment reached $495B in 2023",
  "sourceUrl": "https://example.com/iea-report-2024",
  "documentName": "IEA World Energy Investment Report 2024",
  "relevantExcerpt": "Total investment in renewable energy technologies reached approximately $495 billion...",
  "publicationDate": "2024-06-15"
}
```

**Yêu cầu triển khai**: 1) subagent output finding theo format claim-source có cấu trúc; 2) synthesis agent duy trì tường minh mapping trong lúc kết hợp; 3) output cuối include inline citation hoặc reference section trace claim về source.

### Chiến lược giải quyết Conflict
**Anti-pattern**: chọn tùy tiện 1 giá trị khi nguồn mâu thuẫn nhau (vd chọn publication gần nhất hoặc lấy trung bình giá trị).

**Cách đúng**: annotate cả 2 giá trị với attribution đầy đủ và ngày publication, cho phép người tiêu thụ diễn giải khác biệt theo context.

**Ví dụ**:
```
Market growth estimates vary by source:
- 12% growth — IEA World Energy Report (June 2024, 2023 calendar data)
- 8% growth — Bloomberg NEF Annual Review (March 2024, July 2022–June 2023 data)

The difference may reflect different reporting periods and methodologies.
```

### Nhận thức thời gian (Temporal Awareness)
Ngày publication khác nhau giải thích số liệu khác nhau; đây là trend, không phải mâu thuẫn. Không có temporal context, "trend hợp lệ bị hiểu lầm thành vấn đề chất lượng data".

**Thực hành**: yêu cầu ngày publication/thu thập data trong mọi output structured và bảo toàn chúng qua mỗi bước synthesis.

### Content-Appropriate Rendering
Synthesis không nên flatten mọi output thành format đồng nhất:

| Loại nội dung | Format | Lý do |
|---|---|---|
| Dữ liệu tài chính | Table | Cho phép so sánh giá trị và nhận diện pattern |
| Tin tức/sự kiện hiện tại | Prose | Giữ context tường thuật và tính nhân quả |
| Finding kỹ thuật | Structured list | Làm rõ hierarchy và API specification |

### Attribution qua Pipeline nhiều bước
Điểm fail quan trọng: Bước 3 (synthesis), nơi finding được kết hợp mà không bảo toàn claim-source mapping.

**Pipeline bắt buộc**:
1. Research subagent → thu thập finding kèm mapping
2. Analysis subagent → đánh giá trong khi bảo toàn nguyên bản
3. Synthesis subagent → merge trong khi mang theo mapping tiếp
4. Report generation → sinh output kèm inline citation

**Pattern hoàn thiện Conflict**:
```json
{
  "field": "annualRevenue",
  "conflictDetected": true,
  "values": [
    {
      "value": "$4.2M",
      "source": "Annual Report 2023",
      "context": "Audited financial statements, fiscal year ending December 2023"
    },
    {
      "value": "$3.8M",
      "source": "SEC Filing Q4 2023",
      "context": "Preliminary unaudited figures, calendar year 2023"
    }
  ],
  "possibleExplanation": "Difference may reflect audited vs preliminary figures..."
}
```
Coordinator quyết định xử lý conflict thế nào: trình bày cả 2, điều tra thêm, hoặc escalate.

### Exam traps

| Trap | Sửa lại |
|---|---|
| Chọn nguồn gần nhất khi có conflict | Annotate cả 2 kèm attribution và ngày tháng; để người tiêu thụ tự quyết |
| Coi số liệu khác nhau là mâu thuẫn | Yêu cầu ngày tháng; ngày khác nhau giải thích khác biệt như 1 trend |
| Synthesis agent paraphrase mà không bảo toàn mapping | Duy trì tường minh cặp claim-source xuyên suốt |
| Format đồng nhất cho mọi nội dung | Dùng table cho tài chính, prose cho tin tức, list cho kỹ thuật |

### Practice scenario
2 nguồn đáng tin báo growth rate khác nhau (Source A: 12% [2023 data]; Source B: 8% [2024 data]). Synthesis agent hiện tại chọn giá trị gần đây hơn. **Đáp án đúng (Option D)**: "Annotate cả 2 giá trị kèm source attribution và ngày publication, để người tiêu thụ tự diễn giải sự khác biệt."

### Build exercise — 5 phần
1. Thiết kế schema claim-source mapping với đủ 5 field bắt buộc
2. Implement research subagent output finding có cấu trúc
3. Xây synthesis agent bảo toàn mapping qua quá trình merge
4. Xử lý conflict bằng annotate cả 2 giá trị kèm giải thích
5. Áp dụng format content-appropriate rendering

**Nguyên tắc cốt lõi**: "Attribution chết trong lúc summarisation trừ khi được bảo toàn tường minh."
