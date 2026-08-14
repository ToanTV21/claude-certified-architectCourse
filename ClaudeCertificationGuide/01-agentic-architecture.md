# Domain 1: Agentic Architecture & Orchestration (27%)

> Nguồn: https://claudecertificationguide.com/learn/1-agentic-architecture/

---

## 1.1 Agentic Loops

### Vòng đời của agentic loop
`Agentic loop` là **chu trình thực thi cốt lõi** đứng sau mọi agent dùng Claude. Vòng lặp gồm 4 bước lặp lại tới khi task xong:

1. **Send Request** — gửi request tới Claude qua Messages API, kèm conversation history (system prompt, message trước đó, và tool result của các vòng trước).
2. **Inspect `stop_reason`** — đây là "tín hiệu xác thực duy nhất" quyết định bước tiếp theo:
   - `"tool_use"` — Claude muốn gọi 1 hoặc nhiều tool → vòng lặp tiếp tục
   - `"end_turn"` — Claude đã xong việc → vòng lặp kết thúc
3. **Handle Tool Use** — khi `stop_reason == "tool_use"`: thực thi tool được yêu cầu, append kết quả vào conversation history như 1 message mới, rồi gửi lại conversation đã cập nhật cho Claude. **Điểm quan trọng**: tool result **bắt buộc** phải được append vào history — nếu bỏ sót, Claude không có dữ liệu để reasoning tiếp.
4. **Handle Completion** — khi `stop_reason == "end_turn"`: trả response cuối cùng cho user.

### `stop_reason` là tín hiệu điều khiển duy nhất đáng tin
> "`stop_reason` là tín hiệu **duy nhất** đáng tin cậy để điều khiển loop."

Đây là tín hiệu deterministic, không mơ hồ. **Không bao giờ** thay thế bằng: parse ngôn ngữ tự nhiên, check nội dung text, hoặc cap số vòng lặp tùy ý.

### Các giá trị `stop_reason` khác trong production API

| Giá trị | Cách xử lý |
|---|---|
| `pause_turn` | Tiếp tục turn dài với server tool |
| `max_tokens` | Response đã đầy giới hạn token |
| `stop_sequence` | Chạm stop sequence đã cấu hình |
| `refusal` | Model từ chối trả lời |
| `model_context_window_exceeded` | Context window đã đầy |

**Chiến lược**: coi mọi giá trị khác `end_turn` là "chưa xong, cần điều tra thêm."

### Model-driven vs Pre-configured
- **Model-driven**: Claude tự đọc task, đánh giá tool có sẵn, chọn tool phù hợp theo context.
- **Pre-configured**: developer hard-code sẵn chuỗi tool call và decision tree.

Đề thi ưu tiên cách tiếp cận model-driven vì Claude thích nghi được các tình huống developer chưa lường trước. **Ngoại lệ**: khi business logic đòi hỏi tuân thủ deterministic (tài chính, bảo mật, quy định pháp lý) → dùng programmatic enforcement thay vì để model tự quyết.

### 3 Anti-pattern khi kết thúc loop
1. **Parse natural language signal** — check Claude nói "tôi xong rồi" → SAI vì ngôn ngữ tự nhiên mơ hồ (Claude có thể nói "đã xong file đầu tiên" nhưng ý định là tiếp tục làm các file khác).
2. **Cap số vòng lặp tùy ý làm cơ chế chính** — set "dừng sau 10 loop" → SAI vì cap hoặc cắt ngang việc hợp lệ, hoặc chạy dư vòng không cần thiết. Cap chỉ chấp nhận được như safety net, không phải cơ chế điều khiển chính.
3. **Check content type** — dùng `response.content[0].type == "text"` để kết luận đã xong → SAI vì Claude có thể trả text kèm `tool_use` block cùng lúc (vd giải thích "Để tôi tra cứu đơn hàng" rồi gọi tool ngay sau).

### Ví dụ thực tế: bug dừng sớm (premature termination)
Agent customer support dừng giữa chừng với request phức tạp vì code check `if response.content[0].type == "text"`. Claude trả text giải thích kèm `tool_use` block, code thấy text ở vị trí [0] liền kết luận sai là đã xong. **Fix**: thay content-type check bằng kiểm tra `stop_reason`.

### Exam traps

| Trap | Vì sao sai |
|---|---|
| Dùng `response.content[0].type == 'text'` để check hoàn thành | Text và tool call có thể tồn tại cùng lúc |
| Cap vòng lặp tùy ý làm cơ chế dừng chính | Cắt ngang việc hợp lệ hoặc chạy dư; dùng `stop_reason` |
| Parse ngôn ngữ tự nhiên ("tôi xong rồi") | Mơ hồ; `stop_reason` mới deterministic |
| Ép `tool_choice: 'any'` để tránh text | Tạo vòng lặp tool vô hạn |

### Practice scenario
Agent dừng sớm khi Claude trả text kèm tool call, loop check `content[0].type == 'text'`. **Đáp án đúng**: check field `stop_reason` thay vì content type — tiếp tục khi `tool_use`, dừng khi `end_turn`.

### Key takeaways
- Agentic loop là control flow deterministic, code-driven — không phải trick của prompt.
- `stop_reason` là nguồn chân lý duy nhất để điều khiển loop.
- Tool result phải được append vào history để Claude reasoning được.
- Phân biệt model-driven decision (được ưu tiên trên đề thi) với pre-configured sequence.
- Loại bỏ 3 anti-pattern: parse ngôn ngữ tự nhiên, cap vòng lặp làm cơ chế chính, check content type.
- Cap vòng lặp an toàn chấp nhận được như fallback, không bao giờ là cơ chế dừng chính.

---

## 1.2 Orchestration Patterns

### Kiến trúc Hub-and-Spoke
Đề thi dạy đúng 1 pattern multi-agent cụ thể: **hub-and-spoke** với 2 role riêng biệt:

1. **Coordinator Agent** (hub): nhận task ban đầu, decompose thành subtask, chọn subagent nào để invoke, truyền context cho subagent, tổng hợp kết quả, xử lý lỗi, và route toàn bộ thông tin giữa các agent.
2. **Subagents** (spoke): xử lý task chuyên biệt (web search, document analysis, synthesis, report generation...). Nhận instruction từ coordinator và chỉ trả kết quả về coordinator.

**Quy tắc nền tảng**: "TOÀN BỘ giao tiếp phải đi qua coordinator. Subagent KHÔNG BAO GIỜ giao tiếp trực tiếp với nhau."

Việc tập trung hóa này mang lại 3 lợi ích:
- **Observability**: mọi message đều log/monitor được tại 1 chỗ
- **Error handling nhất quán**: coordinator áp dụng policy phục hồi thống nhất
- **Kiểm soát luồng thông tin**: coordinator quyết định context nào mỗi subagent nhận được

### Isolation Principle (khái niệm hay bị hiểu sai nhất)
Subagent **KHÔNG tự động thừa hưởng** conversation history của coordinator. Khi được spawn, subagent chỉ nhận thông tin được include tường minh:
- Không tự động access system prompt của coordinator
- Không access message trước đó trong conversation của coordinator
- Không tự động access kết quả từ subagent khác
- Không có "shared memory" hay global state nào tồn tại

**Memory Independence**: nếu coordinator invoke web search subagent 2 lần, lần thứ 2 hoàn toàn không biết gì về lần đầu — mỗi lần invoke độc lập hoàn toàn.

**Hệ quả cho thiết kế coordinator**: coordinator phải chủ động (deliberate) về việc truyền context. Mọi thông tin subagent cần phải được include tường minh trong prompt của nó.

### 4 trách nhiệm chính của Coordinator
1. **Dynamic Subagent Selection** — phân tích yêu cầu query để chọn động subagent nào cần invoke, KHÔNG route mọi query qua toàn bộ pipeline.
2. **Research Scope Partitioning** — phân chia phạm vi nghiên cứu giữa các subagent để giảm trùng lặp (vd 1 agent search academic paper, agent khác search tin tức).
3. **Iterative Refinement Loops** — coordinator đánh giá output synthesis, nếu thiếu thì re-delegate cho search/analysis subagent với query có mục tiêu cụ thể, lặp lại tới khi coverage đủ.
4. **Centralized Communication Routing** — toàn bộ giao tiếp giữa subagent đi qua coordinator để đảm bảo observability, error handling nhất quán, kiểm soát luồng thông tin.

### Failure pattern: Narrow Decomposition (decompose quá hẹp)
**Pattern kinh điển trên đề thi**: coordinator decompose "impact of AI on creative industries" chỉ thành các subtopic về visual arts, bỏ sót âm nhạc, viết lách, phim ảnh.

**Root cause**: KHÔNG phải subagent downstream fail, mà là task decomposition của coordinator. Web search agent search kỹ những gì được giao. Synthesis agent tổng hợp đầy đủ những gì nhận được. Nhưng coordinator chỉ giao visual arts nên các domain khác chưa bao giờ được research.

**Nguyên tắc chẩn đoán**: "Khi hệ thống multi-agent cho ra report thiếu hẳn cả nhóm category, đừng đổ lỗi cho subagent — kiểm tra decomposition của coordinator."

Khi output thiếu về **phạm vi** (scope), không phải độ sâu (depth), gần như luôn là do decomposition của coordinator.

### Ví dụ thực tế
Task "renewable energy technologies", coordinator chỉ decompose thành "solar panel efficiency" và "wind turbine design". Mỗi subagent research kỹ, có nguồn tốt về đúng chủ đề được giao. Report cuối cùng đầy đủ về solar và wind nhưng không có gì về geothermal, tidal, biomass, hay nuclear fusion. **Fix**: không phải cải thiện search query, không phải synthesis agent mạnh hơn, không phải thêm subagent — mà là cải thiện decomposition của coordinator để phủ đủ breadth của topic.

### 4 Exam traps

1. **Đổ lỗi subagent downstream cho coverage gap** — subagent chỉ research đúng những gì được giao; lỗi truy về decomposition của coordinator.
2. **Giả định subagent share memory hoặc thừa hưởng context** — subagent hoàn toàn isolated; mọi thông tin phải truyền tường minh trong prompt.
3. **Đề xuất giao tiếp trực tiếp giữa subagent** — phá vỡ observability, error handling nhất quán, và kiểm soát luồng thông tin.
4. **Thêm subagent để fix vấn đề decomposition** — nếu coordinator decompose quá hẹp, thêm subagent không giải quyết gì vì chúng cũng sẽ nhận assignment hẹp tương tự.

### Practice scenario
Report "renewable energy technologies" chỉ phủ solar và wind, mỗi subagent làm tốt phần được giao. **Root cause đúng**: coordinator chỉ decompose thành solar và wind, chưa bao giờ giao geothermal/tidal/biomass/fusion cho subagent nào.

### Key takeaways
1. Hub-and-spoke yêu cầu **toàn bộ** giao tiếp inter-subagent đi qua coordinator — không bao giờ giao tiếp trực tiếp subagent-to-subagent.
2. Subagent hoạt động hoàn toàn isolated, không thừa hưởng context hay shared memory; mọi thông tin cần thiết phải truyền tường minh.
3. Trách nhiệm coordinator: dynamic selection, scope partitioning, iterative refinement, centralized routing.
4. Narrow decomposition ở cấp coordinator là failure pattern chính trên đề thi.
5. Chẩn đoán: khi output multi-agent thiếu, truy nguồn về decomposition của coordinator.

---

## 1.3 Subagent Invocation & Context Passing

### Task Tool
`Task tool` là cơ chế API cho phép coordinator spawn subagent trong Claude Agent SDK. Claude Code hiện tại (v2.1.63, June 2026) đổi tên thành `Agent`, nhưng `Task` vẫn còn như alias.

**Yêu cầu bắt buộc**: `allowedTools` của coordinator phải include tường minh `"Task"` (hoặc `"Agent"`) mới spawn được subagent — đây là 1 binary gate, thiếu nó thì không spawn được bất kỳ subagent nào bất kể được định nghĩa ra sao.

**Thành phần của AgentDefinition**: mỗi subagent cần 3 phần:
1. **Description** — làm rõ mục đích subagent để coordinator quyết định
2. **System prompt** — chứa instruction cho subagent
3. **Tool restrictions** — giới hạn tool đúng phạm vi role của subagent

### 3 quy tắc truyền context

**Rule 1 — Complete Findings Transfer**: nếu synthesis subagent cần kết quả web search và document analysis, coordinator phải truyền cả 2 — đầy đủ — trong prompt của synthesis subagent. Subagent không thể tự lấy lại kết quả trước đó.

**Rule 2 — Structured Data with Metadata**: truyền data tách content khỏi metadata. Mỗi finding cần:
- Content field (claim, nội dung phân tích)
- Metadata field (source URL, document name, page number)

Bỏ sót metadata làm downstream agent mất khả năng attribution (trích dẫn nguồn).

**Rule 3 — Goal-Oriented Coordinator Prompts**: thiết kế prompt coordinator theo goal và tiêu chí chất lượng thay vì quy trình từng bước cứng nhắc — giúp subagent thích nghi khi gặp tình huống bất ngờ.

### Ví dụ structured metadata format
```json
{
  "findings": [
    {
      "claim": "Solar panel efficiency has increased 25% in the last decade",
      "source_url": "https://example.com/solar-report",
      "document_name": "Annual Solar Industry Report 2024",
      "page_number": 14,
      "confidence": "high",
      "retrieved_by": "web_search_agent"
    }
  ]
}
```

### Parallel Spawning
**Pattern**: emit nhiều Task tool call trong 1 response duy nhất của coordinator cho các task subagent độc lập.

**Vì sao**: invoke tuần tự (mỗi turn 1 subagent) tăng latency không cần thiết; task độc lập nên chạy đồng thời.

**Tín hiệu trên đề thi**: đáp án nào nhắc "single response" hoặc "simultaneously" ám chỉ pattern parallel spawning.

### `fork_session` vs `--resume`

| Đặc điểm | fork_session | --resume |
|---|---|---|
| Mục đích | Tạo nhánh độc lập để khám phá phân kỳ | Tiếp tục 1 session named cụ thể |
| Điểm bắt đầu | Nhánh từ baseline chung | Resume từ dòng điều tra trước đó |
| Chia sẻ context | Các nhánh hoạt động độc lập | Cùng 1 dòng điều tra tiếp diễn |

### Ví dụ thực tế: Attribution Failure Pattern
Synthesis agent viết report tốt nhưng không có trích dẫn nguồn, dù research agent upstream hoạt động đúng. **Root cause thực sự**: coordinator strip mất metadata khi truyền content cho synthesis agent — truyền claim mà không kèm source URL, document name, page number. **Fix**: bắt coordinator truyền structured metadata kèm content, giữ nguyên attribution cho mỗi finding.

### Exam traps
1. **Automatic Context Inheritance** — tránh giả định subagent access được history của coordinator hay output của subagent khác.
2. **Đổ lỗi Synthesis Agent** — đừng sửa prompt của synthesis agent để fix claim thiếu nguồn; synthesis agent chỉ trích dẫn được nguồn nó nhận được. Vấn đề thật là context truyền thiếu metadata.
3. **Sequential thay vì Parallel** — đừng đề xuất invoke tuần tự cho task độc lập; gây latency không cần thiết.
4. **Nhầm lẫn fork_session** — phân biệt fork_session (khám phá phân kỳ) với --resume (tiếp tục).

### Practice scenario
Synthesis agent viết report có claim thiếu attribution, các subagent khác hoạt động đúng. **Đáp án đúng**: coordinator truyền content cho synthesis agent mà không kèm structured metadata — source URL, document name, page number không được include.

### Build exercise — 6 bước học
1. Yêu cầu Task/Agent trong `allowedTools` (binary gate để spawn)
2. Định nghĩa subagent có scope rõ, đúng field AgentDefinition
3. Thiết kế format structured tách content khỏi metadata
4. Giữ nguyên metadata đầy đủ khi handoff coordinator → synthesis
5. Verify attribution trong output synthesis
6. Refactor sang parallel Task call để giảm latency

---

## 1.4 Workflow Enforcement & Handoff

### Enforcement Spectrum

**Prompt-Based Guidance**: instruction nhúng trong system prompt để định hướng hành vi model. Độ tin cậy: hoạt động "phần lớn thời gian — khoảng 90-95% trường hợp". Bản chất: probabilistic (không deterministic). Failure mode: model có thể bỏ bước, đổi thứ tự, hoặc hiểu lỏng lẻo instruction.

**Programmatic Enforcement**: hook cấp code, prerequisite gate, hoặc check chặn vật lý downstream tool execution. Độ tin cậy: deterministic, luôn đúng không ngoại lệ. Không thể bị model bypass. Ví dụ: tool `process_refund` không thể chạy cho tới khi `get_customer` trả về verified customer ID.

### Quy tắc quyết định

| Loại tình huống | Cơ chế enforcement | Lý do |
|---|---|---|
| Financial operations (refund, transfer, payment) | Programmatic enforcement | 1 giao dịch chưa verify = mất tiền |
| Security operations (verify identity, access control) | Programmatic enforcement | 1 lần bypass = security breach |
| Compliance operations (AML check, regulatory) | Programmatic enforcement | 1 lần bỏ sót check = phạt pháp lý |
| Low-stakes operations (formatting, style, thứ tự output) | Prompt-based guidance chấp nhận được | Inconsistency không phải rủi ro business |

**Nguyên tắc cốt lõi**: "nếu 1 lần fail duy nhất gây mất tiền, security breach, hoặc vi phạm compliance → dùng programmatic enforcement."

### Prerequisite Gates trong thực tế
Prerequisite gate là check programmatic chặn tool execution tới khi điều kiện tiên quyết được đáp ứng.

**Ví dụ flow customer support**:
1. Agent có access: `get_customer`, `lookup_order`, `process_refund`
2. Prerequisite gate check: `get_customer` đã trả về verified customer ID trong session này chưa?
3. Nếu có → `process_refund` chạy bình thường
4. Nếu chưa → `process_refund` trả error: "Cannot process refund — customer identity not verified. Please call get_customer first."

Gate là code, không phải prompt. Model không thể bypass bằng cách quyết định bỏ qua verification.

### Subagent Lifecycle Hooks

**SubagentStart** — fire khi subagent được spawn qua Task tool (Agent trong Claude Code hiện tại). Chỉ mang tính observational: nhận subagent type/ID, log spawn event, inject thêm context vào subagent run. **Không** block hay modify invocation. Muốn enforcement: attach PreToolUse hook vào Agent tool để rate limit hoặc verify coordinator đã truyền context bắt buộc.

**SubagentStop** — fire khi subagent xong việc và trả kết quả về coordinator. Nhận subagent ID và final message; validate output conformance; log completion; có thể block completion bằng `decision: "block"` nếu validation fail (gửi subagent quay lại làm tiếp). Không transform được output trả về — muốn reshape output dùng PostToolUse hook trên Agent tool call (field `updatedToolOutput`).

**Subagent-Scoped Hooks** — subagent tự định nghĩa PreToolUse/PostToolUse hook trong AgentDefinition frontmatter, chỉ chặn call của chính subagent đó (không ảnh hưởng coordinator hay subagent khác) — cho phép policy per-subagent (vd billing subagent chặn refund trên ngưỡng, technical support subagent không bị giới hạn).

**Stop Hook Auto-Conversion** — khi subagent frontmatter định nghĩa Stop hooks, tự động convert thành SubagentStop event lúc runtime.

### Xử lý request đa vấn đề (multi-concern)
**Đúng**: 1) Decompose request thành các item riêng biệt, 2) Investigate song song dùng shared context, 3) Synthesize thành 1 resolution thống nhất phủ hết các item.

**Sai**: xử lý tuần tự với các conversation riêng, hoặc chỉ giải quyết item đầu rồi quên các item còn lại.

### Structured Handoff Protocol
**Ràng buộc quan trọng**: human agent KHÔNG có access vào conversation transcript, không thể scroll xem lịch sử chat.

**5 field bắt buộc trong handoff summary**:
1. Customer ID
2. Conversation Summary — khách yêu cầu gì, đã thử gì
3. Root Cause Analysis
4. Refund Amount (nếu có) — số cụ thể, không nói vague
5. Recommended Action

Thiếu bất kỳ field nào → human agent phải bắt khách lặp lại từ đầu, trải nghiệm giảm.

### Ví dụ thực tế: tỷ lệ fail 8%
Prompt "Always verify the customer's identity before processing any refund" chỉ đúng 92%, fail 8% dẫn tới refund sai tài khoản. Prompt mạnh hơn giảm còn 3-4% nhưng không bao giờ về 0% vì prompt-based guidance mãi là probabilistic. **Fix**: prerequisite gate programmatic loại bỏ 8% fail hoàn toàn — không phải bằng cách cải thiện prompt, mà bằng cách vật lý ngăn thứ tự thực thi sai.

### Exam traps
1. **Tăng cường instruction trong system prompt** — cải thiện accuracy nhưng không đạt deterministic guarantee.
2. **Few-shot example là đủ** — cải thiện hành vi model nhưng vẫn probabilistic.
3. **Routing classifier để fix workflow enforcement** — classifier xử lý routing, không xử lý per-agent workflow enforcement.
4. **Handoff summary thiếu field** — buộc khách lặp lại toàn bộ.

### Build exercise
1. Customer support agent 3 tool: `get_customer`, `lookup_order`, `process_refund`
2. Prerequisite gate cấp session chặn `process_refund` tới khi có verified customer ID
3. Test bypass — xác nhận gate chặn cả khi cố gọi refund trực tiếp
4. Structured handoff protocol đủ 5 field
5. Xử lý multi-concern request — decompose và giải quyết tất cả trong 1 resolution thống nhất

---

## 1.5 Agent SDK Hooks

### Khái niệm cốt lõi
Agent SDK hooks tiêm hành vi deterministic vào hệ thống probabilistic bằng cách intercept tool call và tool result để enforce business rule và chuẩn hóa dữ liệu. Hoạt động ở ranh giới giữa quyết định của model và thực thi thực tế.

### 2 loại hook

**PostToolUse Hooks**: chạy SAU khi tool execute nhưng TRƯỚC khi model xử lý kết quả. Chức năng: intercept và transform tool result trước khi model thấy. Kết quả: model luôn nhận data sạch, chuẩn hóa bất kể tool nguồn nào.

**PreToolUse Hooks**: chạy TRƯỚC khi tool execute. Chức năng: intercept outgoing tool call; có thể block, modify, hoặc redirect. Kết quả: tool không bao giờ chạy nếu hook quyết định block.

> "PostToolUse hook transform data sau khi execute. PreToolUse hook enforce policy trước khi execute."

### PostToolUse: chuẩn hóa data
**Vấn đề**: các tool MCP khác nhau trả format khác nhau (Unix timestamp, ISO 8601, numeric status code, string status...) → model phải interpret format lẫn lộn mỗi vòng lặp, gây inconsistency.

**Giải pháp**: PostToolUse hook chuẩn hóa mọi format trước khi model xử lý: Unix timestamp → ISO 8601, numeric status code → chuỗi dễ đọc, currency → decimal chuẩn kèm mã tiền tệ, date format vùng miền → 1 chuẩn duy nhất.

### PreToolUse: policy enforcement
- **Refund threshold**: chặn `process_refund` khi vượt $500, redirect sang human escalation.
- **Compliance prerequisite gate**: chặn `transfer_funds` khi AML check chưa hoàn thành.
- **Manager approval workflow**: chặn `approve_discount` trên 20%, route qua approval queue.

### Decision Framework

| Yêu cầu | Cơ chế | Đảm bảo |
|---|---|---|
| Phải tuân thủ 100% thời gian | Hooks | Deterministic |
| Ưu tiên nhưng chấp nhận lệch đôi khi | Prompts | Probabilistic |

- Ảnh hưởng tài chính → dùng hooks
- Rủi ro pháp lý → dùng hooks
- Sở thích formatting → prompts được chấp nhận

### So sánh Hooks vs Prompts qua các scenario
- **AML check cho international transfer**: prompt ~95% đúng, 5% fail = vi phạm quy định. Hook: PreToolUse chặn `transfer_funds` tới khi `aml_check` trả pass → 100% đúng.
- **Format response markdown**: prompt hoạt động phần lớn, response text thuần thi thoảng không gây rủi ro business — hook không cần thiết (overhead thừa).
- **Refund trên $500**: prompt fail 1 lần = refund lớn không qua duyệt. Hook: intercept, check amount, block nếu >$500, route escalation — 100% đúng.

### Ví dụ thực tế: data format hỗn loạn
3 tool trả 3 format date khác nhau (Unix timestamp, ISO 8601, DD/MM/YYYY) và 3 kiểu status khác nhau. **Fix**: PostToolUse hook chuẩn hóa tất cả về ISO 8601 và status dạng chữ dễ đọc.

### Exam traps
1. **PostToolUse để block policy violation** — SAI, PostToolUse chạy SAU execute, action đã xảy ra rồi; dùng PreToolUse để ngăn trước.
2. **Prompt mạnh hơn cho compliance 100%** — SAI, prompt chỉ probabilistic; cần hooks cho deterministic guarantee.
3. **Model tự transform data** — SAI, phải dùng PostToolUse hook để đảm bảo data sạch, nhất quán mỗi lần.
4. **Nhầm lẫn hướng hook** — PostToolUse sau execute (normalization), PreToolUse trước execute (blocking).

### Practice scenario
Agent thi thoảng xử lý international transfer thiếu compliance check dù prompt yêu cầu. **Đáp án đúng**: implement PreToolUse hook chặn `transfer_funds` tới khi `aml_check` trả pass verified.

### Build exercise
1. Tạo 3 MCP tool trả data 3 format khác nhau
2. Implement PostToolUse hook chuẩn hóa date/status
3. Test multi-tool query cho output nhất quán
4. Thêm PreToolUse hook chặn `process_refund` trên $500
5. Thêm PreToolUse hook chặn `transfer_funds` tới khi AML check session-level hoàn thành
6. Test cả 2 hook bằng cách thử operation bị chặn

---

## 1.6 Task Decomposition

### Tổng quan
Task decomposition là cách chia nhỏ công việc phức tạp thành phần agentic system xử lý được. Đề thi tập trung vào 2 pattern decomposition và 1 failure mode quan trọng (attention dilution).

### Pattern 1: Fixed Sequential Pipelines (Prompt Chaining)
**Định nghĩa**: công việc chia thành các bước xác định trước, chạy theo thứ tự, output bước này là input bước sau.

**Cơ chế**: workflow định nghĩa sẵn; kết quả trung gian không đổi thứ tự chạy.

**Ví dụ — Code review pipeline**:
```
Step 1: Local analysis per file (style, bugs, complexity)
         ↓
Step 2: Cross-file integration pass (data flow, API consistency, imports)
         ↓
Step 3: Compile unified review report
```

**Dùng khi**: task cấu trúc rõ, có thể dự đoán được bước từ trước — code review, document processing, data extraction pipeline, compliance check.

**Điểm mạnh**: consistency và reliability được đảm bảo; input giống hệt luôn đi cùng 1 đường; dễ debug, dễ monitor theo từng step.

**Điểm yếu**: không thể pivot khi phát hiện điều mới ở bước trung gian. "Nếu Step 2 phát hiện điều gì đó cần đổi hướng cho Step 3, pipeline không adjust được."

### Pattern 2: Dynamic Adaptive Decomposition
**Định nghĩa**: subtask sinh ra dựa trên phát hiện tại mỗi phase; execution plan tự adapt theo thông tin mới.

**Cơ chế**: agent bắt đầu với mục tiêu cấp cao, khảo sát ban đầu, sinh plan từ finding, adapt các bước còn lại khi có dữ liệu mới.

**Ví dụ — Test legacy codebase**:
```
Phase 1: Map structure (directories, modules, dependencies)
Phase 2: Identify high-impact areas (most-used, bug-prone, untested critical paths)
Phase 3: Create prioritized test plan
Phase 4: Write tests → Discover Module A depends on untested Module B
Phase 5: Reprioritize—test Module B first
Phase 6: Continue adapting as dependencies emerge
```

**Dùng khi**: điều tra open-ended, scope ban đầu chưa xác định — khảo sát legacy system, security audit, research project, debug codebase lạ.

**Điểm mạnh**: phản ứng được với độ phức tạp phát hiện trong lúc chạy; phát hiện và xử lý được yếu tố bất ngờ; kết quả thorough không ép theo plan định trước.

**Điểm yếu**: predictability thấp, thời gian chạy thay đổi tùy phát hiện, khó ước lượng resource/thời gian hoàn thành, debug phức tạp hơn.

### Bảng chọn pattern

| Đặc điểm task | Pattern khuyến nghị | Lý do |
|---|---|---|
| Bước biết trước; input có cấu trúc | Fixed pipeline | Ưu tiên consistency hơn adaptability |
| Open-ended; scope chưa biết | Dynamic decomposition | Adaptability cần thiết khi vấn đề chưa xác định |
| Multi-file code review | Fixed pipeline | Per-file + cross-file analysis dự đoán được |
| Khảo sát legacy codebase | Dynamic decomposition | Dependency/issue lộ diện trong lúc điều tra |
| Document extraction | Fixed pipeline | Field và format định trước |
| Debug hệ thống lạ | Dynamic decomposition | Root cause chưa biết; điều tra phải adapt |

### Attention Dilution Problem
**Định nghĩa**: lỗi kiến trúc xảy ra khi agent xử lý quá nhiều item trong 1 pass duy nhất, dẫn tới độ sâu phân tích không nhất quán — kỹ lưỡng với item này, hời hợt với item khác.

**Triệu chứng quan sát được**:
- Feedback chi tiết cho file đầu, càng về sau càng hời hợt
- Pattern giống hệt bị flag ở file này, được approve ở file khác
- Bug rõ ràng bắt được ở đầu, bỏ sót ở cuối; issue style bắt không nhất quán

**Cơ chế root cause**: "Model phân bổ attention trên toàn bộ item trong context. Khi item quá nhiều, attention/item giảm. Item đầu được ưu ái quá mức, item sau bị lướt qua."

### Giải pháp cấu trúc: Multi-Pass Architecture
- **Layer 1 — Per-item local analysis passes**: phân tích riêng từng file/document/module trong pass riêng, mỗi pass dành trọn attention budget cho 1 item — bắt lỗi local nhất quán.
- **Layer 2 — Cross-item integration pass**: chạy sau khi mọi local pass xong, xem xét quan hệ giữa các item — phát hiện data flow issue, pattern không nhất quán, cross-file dependency.

**Ví dụ cụ thể — review 14 file**:
- Single-pass: file 1-5 feedback chi tiết; file 6-9 feedback vừa; file 10-14 hời hợt, bỏ sót null pointer bug và SQL injection vulnerability; forEach bị flag ở file 3 nhưng code y hệt ở file 11 không được comment gì.
- Multi-pass: per-file pass bắt được null pointer bug ở file 10-14 (dành trọn attention/file); integration pass phát hiện việc đánh giá forEach không nhất quán giữa các file.

### Exam traps
1. **Fix bằng model/context window lớn hơn** — SAI, attention dilution là vấn đề kiến trúc, không phải năng lực model hay kích thước context.
2. **Prompt mạnh hơn tương đương giải pháp** — cải thiện chất lượng trung bình nhưng không giải quyết root cause phân bổ attention.
3. **Fixed pipeline cho task open-ended** — điều tra open-ended cần adaptability; fixed pipeline không phản ứng được finding bất ngờ.
4. **Batching mà không có integration pass** — chia batch giảm dilution trong batch nhưng bỏ sót issue cross-batch.

### Practice scenario
Agent review 14 file — feedback chi tiết file 1-5, bỏ sót bug rõ ràng file 10-14, flag forEach không nhất quán. **Đáp án đúng**: chia review thành per-file local analysis pass cộng với cross-file integration pass riêng để tránh attention dilution.

---

## 1.7 Session State & Resumption

### 3 lựa chọn quản lý session

**Option 1 — `--resume <session-name>`**: resume 1 session named cụ thể, khôi phục toàn bộ conversation history gồm mọi tool result, phân tích, reasoning chain. **Dùng khi**: context trước vẫn valid phần lớn, file chưa đổi nhiều, muốn tiếp tục đúng chỗ dừng. **Không dùng khi**: file đã sửa, tool result không còn phản ánh state hiện tại (nguy cơ stale context).

**Option 2 — `fork_session`**: tạo nhánh độc lập từ baseline phân tích chung. Mỗi nhánh hoạt động độc lập, thay đổi ở nhánh này không ảnh hưởng nhánh kia, các nhánh không thấy kết quả của nhau. **Dùng khi**: đã hoàn thành phân tích ban đầu, muốn khám phá các approach phân kỳ từ cùng điểm xuất phát (vd so sánh 2 chiến lược refactor). **Không dùng khi**: chỉ đơn giản tiếp tục cùng 1 điều tra.

**Option 3 — Fresh Start with Summary Injection**: bắt đầu session hoàn toàn mới nhưng tiêm structured summary của finding từ session trước vào context ban đầu. Session mới không có tool result cũ — chỉ có summary được chọn lọc. **Dùng khi**: tool result session trước đã stale (file đổi, API update, dependency thay đổi), context bị degrade sau session dài. **Không dùng khi**: context trước vẫn valid.

### Stale Context Problem
**Cách biểu hiện**: dev phân tích codebase với Claude Code, sửa 3 file, rồi resume session → Claude đưa ra lời khuyên mâu thuẫn — đề xuất thay đổi đã làm rồi, hoặc reference code không còn tồn tại — vì đang reasoning từ tool result cũ vẫn còn trong conversation history.

**Vì sao xảy ra**: khi resume, toàn bộ conversation history được khôi phục kèm mọi tool result trước đó. Nếu 1 file đã được đọc trước đó và sửa sau đó, nội dung file cũ vẫn còn là tool result trong history. Model reasoning từ data cũ lẫn data mới, gây mâu thuẫn.

**Fix ngây thơ (không đủ)**: chỉ resume và bảo agent đọc lại file đã sửa — cải thiện tình huống nhưng tool result cũ vẫn còn trong history, model vẫn có thể reference thông tin cũ cho các quyết định không liên quan trực tiếp tới file đã sửa.

**Fix đúng**: bắt đầu session mới với structured summary của finding trước, chỉ rõ file nào đã đổi để agent re-analyze có mục tiêu (targeted re-analysis). Session mới không có tool result cũ; summary tiêm vào giữ lại kiến thức cũ mà không kèm data lỗi thời.

> **Exam trap**: "chỉ đơn giản resume và bảo agent đọc lại file đã đổi KHÔNG phải đáp án tốt nhất — tool result stale vẫn còn trong history và có thể ảnh hưởng reasoning. Fresh start với summary injection đáng tin cậy hơn."

### Targeted Re-Analysis vs Full Re-Exploration
Khi file thay đổi, agent không cần re-analyze toàn bộ codebase. Đọc lại 50 file vì 3 file đổi là lãng phí. **Cách đúng**: targeted re-analysis — báo agent về đúng các file đã đổi, để nó re-analyze chỉ những file đó. Summary từ session trước bao phủ phần chưa đổi.

### Decision Matrix

| Tình huống | Option tốt nhất | Lý do |
|---|---|---|
| Tiếp tục việc hôm qua, chưa đổi file | `--resume` | Context trước valid, full history hữu ích |
| So sánh 2 approach refactor | `fork_session` | Khám phá phân kỳ từ baseline chung |
| Resume sau khi sửa 3/50 file | Fresh start + summary | Tool result stale cho file đã sửa gây mâu thuẫn |
| Session dài, history bị clutter | Fresh start + summary | Context degrade cần baseline sạch |
| So sánh chiến lược test vs docs | `fork_session` | 2 approach độc lập từ cùng phân tích |
| Resume sau dependency update | Fresh start + summary | Nhiều file có thể đổi gián tiếp |

### Ví dụ thực tế: bug lời khuyên mâu thuẫn
Dev dùng Claude Code phân tích codebase 50 file trong 2 ngày. Ngày 1: phân tích module auth, phát hiện 3 issue. Đêm: sửa cả 3 bằng cách sửa `auth.ts`, `session.ts`, `middleware.ts`. Ngày 2 resume: Claude đề xuất sửa lại 3 issue đã fix — tool result cũ vẫn cho thấy code chưa sửa. **Fix**: session mới với summary: "Phân tích trước phát hiện 3 issue auth trong auth.ts, session.ts, middleware.ts. Đã fix hết. Re-analyze 3 file này để verify fix và tìm issue mới nếu có."

### Exam traps
1. **Full re-exploration sau thay đổi 1 phần** — lãng phí; targeted re-analysis mới đúng.
2. **Resume sau khi file đã sửa** — history vẫn giữ tool result stale, gây mâu thuẫn.
3. **Nhầm fork_session với --resume** — fork tạo nhánh độc lập cho khám phá khác nhau; resume tiếp tục cùng conversation.
4. **Dùng fork_session cho stale context** — fork_session branch từ session hiện có, vẫn chứa tool result stale; fresh start + summary mới đúng cho data lỗi thời.

### Practice scenario
Dev resume Claude Code session sau khi sửa 3/50 file, agent đưa lời khuyên mâu thuẫn. **Đáp án đúng**: bắt đầu session mới với summary finding trước đó, báo rõ 3 file đã đổi để re-analyze có mục tiêu.

### Build exercise — 6 task
1. Tạo named Claude Code session (`--name`), phân tích codebase 10 file
2. Ghi structured summary (tên file, issue tìm được, khuyến nghị)
3. Sửa 3 file trong codebase
4. Thử `--resume` và quan sát vấn đề stale context
5. Bắt đầu fresh session với summary tiêm sẵn, chỉ rõ 3 file đã đổi
6. So sánh chất lượng lời khuyên giữa resume (stale) và fresh start (targeted re-analysis)
