# Domain 2: Tool Design & MCP Integration (18%)

> Nguồn: https://claudecertificationguide.com/learn/2-tool-design-mcp/

---

## 2.1 Tool Schema / Interface Design

### Nguyên tắc cốt lõi
"Tool description là cơ chế CHÍNH mà LLM dùng để chọn tool. Không phải metadata phụ. Không phải chuyện thêm cho có." Khi nhận tool, model dựa vào description để quyết định gọi cái nào. Description tối giản gây nhầm lẫn khi lựa chọn giữa các tool có phạm vi chồng lấn.

### 5 yếu tố của tool description chuẩn production
1. **Primary Purpose** — nói rõ ràng tool làm gì
2. **Input Expectations** — data type, format, constraint, field bắt buộc vs optional
3. **Example Queries** — use case cụ thể để model bám vào
4. **Edge Cases & Limitations** — tool KHÔNG làm gì, hành vi ngoài phạm vi kỳ vọng
5. **Explicit Boundaries** — phân biệt tường minh với tool tương tự trong bộ tool

### So sánh Minimal vs Production-Grade

**Minimal (gây misrouting)**:
```
get_customer: "Retrieves customer information"
lookup_order: "Retrieves order details"
```

**Production-grade (chọn tool đáng tin cậy)**:
```
get_customer: "Looks up a customer account by email address, phone number,
or customer ID. Returns customer profile (name, contact details, account
status, loyalty tier). Use this when you need to verify who the customer is.
Do NOT use for order-specific queries — use lookup_order for those."

lookup_order: "Retrieves order details by order number (format: #NNNNN) or
tracking ID. Returns order status, items, shipping details, and refund
eligibility. Use this when a customer asks about a specific order. Do NOT
use for customer identity verification — use get_customer for that."
```

Version production cung cấp phân biệt rõ ràng: identifier chấp nhận, giá trị trả về, và quan trọng nhất — khi nào KHÔNG dùng mỗi tool.

### Vấn đề Misrouting
2 tool có description chồng lấn/gần giống hệt gây nhầm khi chọn. Ví dụ: agent route "check my order #12345" tới `get_customer` thay vì `lookup_order`. **Root cause**: description thiếu phân biệt và điều kiện ranh giới.

### 4 phương án giải quyết — góc nhìn đề thi

| Option | Cách tiếp cận | Kết luận đề thi | Vì sao |
|---|---|---|---|
| Mở rộng description | Thêm purpose, input, example, edge case, boundary | ✓ Đúng | Effort thấp, leverage cao, xử lý đúng root cause |
| Few-shot example | Thêm token overhead với ví dụ | ✗ Sai | Chữa triệu chứng, không phải nguyên nhân |
| Routing classifier | Pre-parse input để pre-select tool | ✗ Sai | Bước đầu quá kỹ thuật; bỏ qua natural language understanding của LLM |
| Tool consolidation | Merge tool tương tự thành 1 | ✗ Sai | Lựa chọn kiến trúc dài hạn hợp lý nhưng cần nhiều effort hơn mở rộng description |

**Pattern trên đề thi**: certification luôn ưu tiên fix effort thấp, leverage cao — description tốt hơn trước classifier, scoped access trước broad access, community server trước custom build.

### Chiến lược Tool Splitting
**Vấn đề**: tool generic với trách nhiệm rộng gây mơ hồ.

**Trước khi split**:
```
analyze_document: "Analyses a document and returns results"
```

**Sau khi split**:
```
extract_data_points: "Extracts structured data fields (dates, amounts,
names) from a document"

summarize_content: "Produces a concise summary of a document's key
arguments and conclusions"

verify_claim_against_source: "Checks whether a specific claim is supported
by the source document, returning supporting/contradicting evidence"
```

### Rename tool để rõ ràng
Khi 2 tool có tên gây nhầm lẫn tương tự, rename làm rõ mục đích ở cấp interface. Đổi `analyze_content` thành `extract_web_results` với description web-specific — mục đích trở nên rõ ràng mà không đụng vào implementation.

### Tương tác với System Prompt
**Failure mode quan trọng**: instruction nhạy keyword trong system prompt có thể tạo association tool ngoài ý muốn, override description viết tốt. Ví dụ system prompt nói "always check customer details before proceeding" có thể route mọi query liên quan customer tới `get_customer` bất kể description. **Hành động**: sau khi update tool description, đọc lại system prompt xem có conflict không.

### Ranh giới của giải pháp
"Tool description là fix khi agent có số lượng tool khả thi và đơn giản là không phân biệt được 2 tool. KHÔNG phải fix khi bản thân toolkit là vấn đề: quá khoảng 4-5 tool/agent, selection suy giảm do độ phức tạp quyết định, viết lại 22 description không giải quyết được gì." Chẩn đoán: ambiguous description (fix: mở rộng description) hay toolkit overload (fix: cách khác, xem Task 2.3).

### Exam traps
1. Few-shot example cho misrouting — thêm token overhead không xử lý root cause (description yếu).
2. Routing classifier làm bước đầu — over-engineered, bypass LLM understanding.
3. Tool consolidation làm bước đầu — hợp lý dài hạn nhưng effort cao hơn mở rộng description.
4. Bỏ qua system prompt sau khi update description — instruction nhạy keyword âm thầm override.

### Practice scenario
Log production cho thấy agent gọi `get_customer` cho query order (vd "check my order #12345") thay vì `lookup_order`. **Đáp án đúng**: mở rộng mỗi tool description bao gồm input format, example query, edge case, và boundary giải thích khi nào dùng tool nào.

---

## 2.2 Structured Error Responses

### Khái niệm cốt lõi
"Khi MCP tool fail, error response nó trả về quyết định agent có recover thông minh được không hay fail mù quáng." Error message generic ngăn agent reasoning về phương án recovery. Flag `isError` của MCP protocol báo hiệu tool fail, cho phép model phân biệt execution failure với result thành công.

### 4 loại error

**1. Transient Errors** — service tạm không sẵn sàng: timeout, downtime, rate limiting. Request hợp lệ, hệ thống tạm không tới được. **Recovery**: retry sau delay ngắn.
```json
{
  "isError": true,
  "content": [{ "type": "text", "text": "Service temporarily unavailable" }],
  "errorCategory": "transient",
  "isRetryable": true,
  "description": "Database experiencing high load. Request valid, succeeds on retry."
}
```

**2. Validation Errors** — request malformed: sai format, thiếu field, giá trị ngoài range. **Recovery**: sửa input rồi retry.
```json
{
  "isError": true,
  "content": [{ "type": "text", "text": "Invalid order ID format" }],
  "errorCategory": "validation",
  "isRetryable": true,
  "description": "Order ID format #NNNNN required. Received 'order-abc'. Reformat and retry."
}
```

**3. Business Errors** — vi phạm policy, xung đột business rule, vượt limit. Request kỹ thuật hợp lệ nhưng vi phạm ràng buộc business. **Recovery**: KHÔNG retry — cần workflow thay thế (escalation).
```json
{
  "isError": true,
  "content": [{ "type": "text", "text": "Refund exceeds policy limit" }],
  "errorCategory": "business",
  "isRetryable": false,
  "description": "Refund £750 exceeds £500 limit. Manager approval required. Escalate with details."
}
```
`isRetryable: false` báo hiệu "vi phạm policy y hệt sẽ xảy ra mỗi lần." Retry cho ra kết quả fail giống hệt.

**4. Permission Errors** — access denied, credential không đủ, authorization fail. **Recovery**: escalate hoặc dùng credential khác.
```json
{
  "isError": true,
  "content": [{ "type": "text", "text": "Access denied" }],
  "errorCategory": "permission",
  "isRetryable": false,
  "description": "Current service account lacks financial record access. Escalate to senior agent."
}
```

### Hiểu về `isRetryable`
Flag `isRetryable` trả lời: "Có đường retry nào thành công không?" Không đảm bảo thành công không đổi; recovery khác nhau theo category:
- Transient + Retryable: gửi lại request y hệt sau khi hệ thống hồi phục
- Validation + Retryable: agent tự sửa input (reformat data) rồi retry
- Business + Non-retryable: policy chặn request vĩnh viễn; cần workflow thay thế
- Permission + Non-retryable: cần principal/credential khác, không phải reword request

### Phân biệt quan trọng nhất trên đề thi: Access Failure vs Valid Empty Result

**Access Failure**: tool KHÔNG tới được data source. Timeout, auth fail, service down. Data có thể tồn tại nhưng không tới được. Agent nên quyết định retry.
```json
{
  "isError": true,
  "content": [{ "type": "text", "text": "Could not reach customer database" }],
  "errorCategory": "transient",
  "isRetryable": true,
  "description": "Database connection timed out after 5 seconds. Query did not execute."
}
```

**Valid Empty Result**: tool query THÀNH CÔNG data source. Không có record khớp. Query chạy đúng, kết quả 0. Agent KHÔNG nên retry.
```json
{
  "isError": false,
  "content": [{ "type": "text", "text": "No customer found for 'john@example.com'. Query successful, no matches." }],
  "resultCount": 0
}
```

**Vấn đề thực tế**: tool trả empty array sau customer lookup. Agent retry 3 lần, rồi escalate lên human. Phân tích: tài khoản khách hàng không tồn tại. Tool đã thành công nhưng response không structure khác biệt, gây lãng phí retry.

### Error Propagation trong Multi-Agent
1. **Subagent xử lý transient failure cục bộ** — retry timeout nội bộ trước khi report lên coordinator.
2. **Chỉ propagate error không thể phục hồi lên trên** — sau khi retry local hết, report failure kèm context.
3. **Include partial result và chi tiết attempt** — vd "Searched 3 of 5 sources successfully. Sources 4-5 timed out. Partial results from successful sources attached."

**Anti-pattern cần tránh**: silent error suppression (trả empty result như success); workflow termination trên 1 failure (coordinator quyết định mù quáng).

### Exam traps (bảng)

| Anti-pattern | Vì sao fail | Cách đúng |
|---|---|---|
| Retry empty result từ query thành công | Empty result nghĩa là "không match"; retry cho ra empty giống hệt | Chấp nhận kết quả, trả "no data found" |
| Error message generic ("Operation failed") | Không có `errorCategory`, `isRetryable`, description, agent không phân biệt được transient vs business | Include metadata structured cho mỗi loại error |
| Coi business error là retryable | Vi phạm policy y hệt mỗi lần retry | Đánh dấu `isRetryable: false`, escalate với workflow thay thế |
| Suppress error subagent âm thầm | Coordinator không phân biệt được "không tìm thấy gì" với "không search được" | Propagate error kèm context và partial result |

### Practice scenario
Tool trả empty array sau customer lookup. Agent retry 3 lần rồi escalate. Phân tích: khách không tồn tại. **Đáp án đúng**: tool không phân biệt access failure với valid empty result, nên agent coi "không match" như 1 failure có thể retry.

### 3 field metadata bắt buộc

| Field | Type | Mục đích |
|---|---|---|
| `errorCategory` | String (transient/validation/business/permission) | Phân loại failure để route recovery |
| `isRetryable` | Boolean | Báo có đường retry nào tồn tại không |
| `description` | String | Giải thích error và gợi ý hành động recovery |

### Key takeaways
1. "Message generic như 'Operation failed' vô dụng với LLM."
2. Structure error response để access failure khác biệt về mặt cấu trúc/hình thức với valid empty result.
3. Business và permission error KHÔNG BAO GIỜ retryable — cần workflow thay thế.
4. Validation và transient error retryable nhưng cần fix khác nhau (sửa input vs hồi phục hệ thống).
5. Hệ thống multi-agent phải propagate error kèm context, không suppress âm thầm.

---

## 2.3 Tool Distribution & Tool Choice

### Khái niệm cốt lõi
"Số lượng tool giao cho agent ảnh hưởng trực tiếp tới độ tin cậy khi chọn tool đúng" — là 1 quyết định kiến trúc quyết định hệ thống multi-agent có hoạt động được trong production hay không.

### Vấn đề Tool Overload
**Nguyên tắc**: toolkit size tối ưu là **4-5 tool/agent**, mỗi tool scoped đúng role của agent đó.

Giao 18 tool cho 1 agent làm giảm độ tin cậy chọn tool; error rate tăng khi toolkit phình to. Relevance quan trọng ngang quantity. **Nguyên tắc giải pháp**: "Mỗi agent chỉ nhận tool nó cần cho role được định nghĩa. Không hơn."

### Consolidate tool gần trùng lặp
**Tình huống**: data platform có 22 tool: 3 tool query (mỗi data source 1) cộng 19 transformation (`pivot_table`, `calculate_percentile`, `normalise_currency`,...). Split theo role vẫn để lại 1 agent transformation với 19 tool — đẩy vấn đề overload xuống 1 tầng.

**Giải pháp — Parameterized Tool Consolidation**: gộp 19 tool gần giống thành 1 tool có tham số:
```json
{
  "name": "transform_data",
  "description": "Apply a transformation to a dataset. Use transform_type to select the operation.",
  "input_schema": {
    "type": "object",
    "properties": {
      "dataset": { "type": "string" },
      "transform_type": {
        "type": "string",
        "enum": ["pivot", "percentile", "normalise_currency", "..."]
      },
      "options": { "type": "object" }
    },
    "required": ["dataset", "transform_type"]
  }
}
```
Kết quả: 22 tool giảm còn 4, mọi transformation vẫn tiếp cận được.

### Bảng chẩn đoán

| Tình huống | Cách fix |
|---|---|
| Ít tool, nhưng 2 tool đọc na ná nhau | Sắc nét description (Task 2.1) |
| Job khác nhau (query, transform, export) | Split theo role, 4-5 tool mỗi role |
| Biến thể của cùng 1 job chung shape | Consolidate thành parameterized tool |
| Agent làm nhiều hơn cần | Constrain năng lực tool |

**Lưu ý**: "Đếm số tool trước khi chọn cách fix." Viết lại description cho vấn đề 22-tool không giải quyết được gì về decision complexity; consolidation mới là fix đúng.

**Ngộ nhận về server boundary**: chuyển tool sang MCP server thứ 2 KHÔNG giải quyết overload — "Server boundary vô hình với model. Client trao cho nó mọi tool từ mọi server kết nối thành 1 list phẳng."

### Cấu hình `tool_choice`

**1. `"auto"` (mặc định)** — model tự quyết định gọi tool hay trả text. Dùng cho vận hành chung cần linh hoạt hội thoại.
```json
{ "tool_choice": { "type": "auto" } }
```

**2. `"any"`** — model PHẢI gọi 1 tool nhưng tự chọn tool nào. Đảm bảo structured output từ 1 trong nhiều schema. Use case chính: extraction pipeline nhiều schema (invoice, receipt, contract).
```json
{ "tool_choice": { "type": "any" } }
```

**3. Forced selection** — model PHẢI gọi 1 tool đích danh cụ thể. Enforce bước workflow bắt buộc, model không thể bỏ hay đổi thứ tự operation bắt buộc.
```json
{ "tool_choice": { "type": "tool", "name": "extract_metadata" } }
```
Sau khi forced call xong, các turn sau dùng `"auto"` cho các bước còn lại.

### Scoped Cross-Role Tools
**Vấn đề**: route mọi request qua coordinator thêm "2-3 round trip mỗi request và có thể tăng latency 40% trở lên."

**Giải pháp — Scoped cross-role tool**: cho agent access hạn chế vào capability của role khác thông qua 1 phiên bản constrained.

**Ví dụ thực tế — fact verification**:
- Naive: synthesis agent route mọi fact verification qua coordinator → coordinator delegate cho search agent → chờ kết quả.
- Optimized: cho synthesis agent 1 tool `verify_fact` scoped cho lookup đơn giản.
  - 85% verification (lookup đơn giản, milliseconds) xử lý local
  - 15% verification (phức tạp, đa nguồn) vẫn route qua coordinator
  - **Kết quả**: giảm latency tới 40%

### Thay tool generic bằng biến thể constrained
**Anti-pattern**: cho subagent `fetch_url` (có thể fetch mọi thứ từ mọi nơi).
**Best practice**: thay bằng `load_document` constrained chỉ validate document URL.
**Lợi ích**: ngăn misuse, làm rõ mục đích tool, giảm rủi ro side effect ngoài ý muốn, áp dụng nguyên tắc least privilege.

### Ví dụ scoping theo role — hệ thống research multi-agent

| Agent | Tool (4-5 mỗi role) |
|---|---|
| Web Search | `search_web`, `fetch_page`, `extract_links`, `save_snippet` |
| Document Analysis | `extract_metadata`, `extract_data_points`, `summarize_content`, `verify_claim` |
| Synthesis | `compile_report`, `verify_fact` (scoped), `format_citation`, `assess_coverage` |
| Coordinator | `Agent`, `review_output`, `request_revision` |

### Exam traps

| Trap | Vì sao fail | Cách đúng |
|---|---|---|
| Route mọi verification đơn giản qua coordinator | Thêm 2-3 hop mỗi request; lãng phí resource cho 85% case đơn giản | Thêm scoped `verify_fact` tool cho synthesis agent |
| Dùng `tool_choice: 'auto'` khi cần structured output | Model có thể trả text hội thoại thay vì tool call | Dùng `'any'` để đảm bảo tool call hoặc forced selection cho tool cụ thể |
| Cho agent 18 tool mong đợi selection đáng tin | Độ tin cậy giảm khi tool tăng; tăng decision complexity | Giới hạn 4-5 tool/agent; consolidate tool trùng |
| Cho subagent tool generic `fetch_url` | Tool generic dễ bị misuse; vi phạm least privilege | Dùng `load_document` constrained chỉ validate document URL |

### Practice scenario
Synthesis agent thường xuyên quay lại coordinator để verify fact đơn giản, thêm 2-3 round trip mỗi task và 40% latency. Phân tích: 85% verification là lookup đơn giản. **Đáp án đúng**: cho synthesis agent 1 scoped `verify_fact` tool cho lookup đơn giản, chỉ route verification phức tạp qua coordinator.

---

## 2.4 MCP Server Integration

### Tổng quan
`MCP (Model Context Protocol) server` mở rộng khả năng của Claude bằng cách kết nối tới hệ thống bên ngoài như database, API, dev tool, issue tracker. Cấu hình đúng đảm bảo consistency cho team và tránh vấn đề setup.

### Cấp độ scoping

**Project-Level Configuration (`.mcp.json`)** — location: root repository; sharing: version-controlled, chia sẻ cho toàn team; use case: integration team-wide (Jira, GitHub, internal API).
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "jira": {
      "command": "npx",
      "args": ["-y", "@community/mcp-server-jira"],
      "env": { "JIRA_URL": "${JIRA_URL}", "JIRA_TOKEN": "${JIRA_TOKEN}" }
    }
  }
}
```

**User-Level Configuration (`~/.claude.json`)** — location: home directory user; sharing: cá nhân, KHÔNG version-controlled hay chia sẻ; use case: server thử nghiệm, integration cá nhân, test trước khi team adopt.

**Nguyên tắc chính**: "Mọi tool từ mọi server đã cấu hình (cả project-level và user-level) được discover lúc connection và có sẵn cùng lúc. Không có bước activate thủ công — nếu server được cấu hình và reachable, tool của nó xuất hiện."

### Environment Variable Expansion
`.mcp.json` hỗ trợ cú pháp `${VARIABLE_NAME}` để quản lý credential.
```json
{ "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}", "DATABASE_URL": "${DATABASE_URL}" } }
```
**Lợi ích**: file config an toàn để version control; mỗi dev authenticate bằng credential riêng; xoay token không cần đổi file config; secret không bao giờ vào history repo.

### MCP Resources
`Resources` expose danh mục content cho agent mà không cần exploratory tool call, giảm call lãng phí.

**Ví dụ resource**: tóm tắt issue (Jira issue với title và status), hệ thống tài liệu (mục lục docs nội bộ), schema database (tên bảng, kiểu cột, quan hệ).

**Khái niệm**: "Resources cho agent thấy data nào có sẵn. Tool cho phép agent hành động lên data đó."

### Build-vs-Use Decision Framework
**Dùng community server khi**: integration chuẩn (Jira, GitHub, Slack, Linear, Notion); solution community đã test, maintain; tiết kiệm thời gian và maintenance.

**Chỉ build custom server khi**: team có workflow đặc thù mà community server không xử lý được; cần business logic tùy chỉnh ở tool layer; hệ thống nội bộ proprietary cần integration.

**Nguyên tắc chính**: "Đề thi luôn ưu tiên lựa chọn pragmatic. 'Evaluate community server trước' luôn đúng khi liên quan tới integration chuẩn."

### Nâng cấp MCP Tool Description
Description sơ sài khiến agent thích dùng built-in tool hơn vì tài liệu phong phú hơn.

**Description kém**:
```
search_codebase: "Searches code"
```

**Description tốt**:
```
search_codebase: "Performs semantic code search across the entire repository
using AST-aware indexing. Returns matching functions, classes, and methods
with full context including file path, line numbers, and surrounding code.
More accurate than text-based grep for finding code by intent rather than
exact string match. Use this instead of Grep when searching for code by
what it does rather than what it contains."
```

### Exam traps

| Trap | Cách đúng |
|---|---|
| Build custom MCP server cho integration chuẩn như Jira | Evaluate community server trước; chỉ build custom cho workflow team-specific |
| Đặt config MCP team-wide trong `~/.claude.json` | Server team phải nằm trong `.mcp.json` ở root project |
| Commit credential trực tiếp trong `.mcp.json` | Dùng cú pháp `${VARIABLE}` để expand env variable |
| Để description MCP tool sơ sài | Viết description 3-5 câu giải thích năng lực, output, use case, so sánh với alternative |

### Practice scenario
Team cần integration Jira, dev đề xuất build custom server. **Đáp án đúng**: "Evaluate community MCP server có sẵn cho Jira, chỉ build custom nếu chúng không xử lý được workflow team-specific."

---

## 2.5 Built-in Tools

### Tổng quan
Claude Code có 6 built-in tool để làm việc với codebase: Read, Write, Edit, Bash, Grep, Glob. Mỗi tool phục vụ mục đích riêng, chọn sai tool lãng phí thời gian hoặc context token.

### Phân biệt cốt lõi: Grep vs Glob

**Grep — Content Search**: search NỘI DUNG file theo pattern. Dùng khi tìm: người gọi hàm, error message, câu lệnh import, gán biến, bất kỳ text nào trong file.
```
// Find all files that call processLegacyOrder()
Grep: "processLegacyOrder"

// Find all error messages containing "timeout"
Grep: "timeout"

// Find all files that import a specific module
Grep: "import.*from 'utils/auth'"
```

**Glob — Path Matching**: match ĐƯỜNG DẪN file theo pattern tên. Dùng khi tìm: file test, file config, file theo extension, file theo cấu trúc thư mục.
```
// Find all test files
Glob: "**/*.test.tsx"

// Find all configuration files
Glob: "**/config.*"

// Find all MDX files in the domains directory
Glob: "content/domains/**/*.mdx"
```

**Phân biệt chính**: "Grep tìm cái gì BÊN TRONG file. Glob tìm file theo TÊN."

### Read, Write, và Edit

**Edit — Sửa có mục tiêu**: thực hiện sửa chính xác dùng unique text matching. Chỉ định exact text cần tìm và text thay thế; nhanh và chính xác, chỉ đụng vào đúng text được chỉ định.
```
Edit:
  old_string: "function processOrder(id: string)"
  new_string: "function processOrder(id: string, validate: boolean = true)"
```

### Xử lý khi Edit fail
Edit yêu cầu unique text matching. Nếu text chỉ định xuất hiện nhiều lần, Edit không xác định được sửa chỗ nào.

**Chiến lược recovery (theo thứ tự)**:
1. **Mở rộng anchor** — thêm context xung quanh `old_string` cho tới khi chỉ match đúng 1 chỗ
2. **Dùng `replace_all: true`** — nếu thực sự muốn sửa mọi occurrence
3. **Read + Write fallback** — chỉ khi cả 2 cách trên không phân biệt được target

**Vì sao KHÔNG mặc định Read + Write**: Read + Write load toàn bộ file cho việc thường chỉ là sửa 1 dòng; lãng phí context token. Đề thi phạt việc nhảy thẳng qua Read + Write sau khi Edit báo non-unique match.

### Hiểu Codebase từng bước (Incremental)
**Cách sai**: đọc hết file ngay từ đầu — "context-budget killer". Codebase 200 file đọc hết ngốn toàn bộ context window, chủ yếu vào file không liên quan.

**Cách đúng — Incremental Discovery**:
1. **Grep để tìm entry point** — search tên hàm, class, error message làm điểm neo điều tra, tiết lộ file nào liên quan.
2. **Read để trace import và flow** — sau khi xác định file liên quan, đọc để hiểu cấu trúc code và theo dõi import.
3. **Grep lại để trace usage** — nếu tìm thấy wrapper function hay re-export, grep tên đó khắp codebase để tìm consumer.
4. **Chỉ đọc file cần thiết** — mỗi lần đọc file phải được justify bởi bước phát hiện trước đó.

Kết quả: tốn ít context nhất cho hiểu biết tối đa qua progressive mapping.

### Trace Function Usage qua Wrapper Module
**Pattern thường gặp**: hàm định nghĩa ở 1 module, re-export qua wrapper, được dùng qua tên wrapper. Grep đơn giản cho tên gốc bỏ sót consumer gián tiếp.

**Cách đúng**:
1. Grep tìm định nghĩa hàm để xác định nơi định nghĩa
2. Read file định nghĩa để xác định tên export
3. Grep từng tên export khắp codebase để tìm consumer
4. Nếu re-export qua barrel file (vd `index.ts`), Grep tên module barrel file để tìm consumer import từ đó

### Kịch bản Deprecation (pattern hay gặp trên đề thi)
**Yêu cầu**: tìm mọi file gọi hàm deprecated VÀ file test của chúng.

**Trình tự đúng**:
1. **Grep tên hàm** — tìm mọi file có nội dung reference tới nó, gồm cả test import trực tiếp
2. **Glob cho sibling test file** — tìm test file đi kèm mỗi caller theo naming convention (vd `OrderProcessor.ts` → `OrderProcessor.test.tsx`), kể cả khi test exercise hàm gián tiếp
3. **Grep lại cho wrapper name** — khi caller expose hàm qua wrapper, Grep tên wrapper để tìm transitive coverage

**Pattern**: Grep (content), rồi Glob (path), rồi Grep lại (indirect reference). KHÔNG phải Glob trước.

### Exam traps

| Trap | Vì sao fail |
|---|---|
| Dùng Glob để tìm người gọi hàm | Glob search path, không phải content. Dùng Grep để search content cho tên hàm, import, error message |
| Dùng Grep để tìm file theo extension/naming pattern | Glob mới đúng cho path matching như `**/*.test.tsx`, `**/config.*` |
| Đọc hết file source ngay từ đầu | Context-budget killer. Dùng cách incremental: Grep entry point trước, rồi chỉ Read file liên quan |
| Mặc định dùng Read + Write cho mọi sửa đổi | Edit nhanh hơn và tốn ít context hơn. Luôn thử Edit trước; mở rộng anchor hoặc dùng replace_all khi non-unique match |
| Nhảy qua Read + Write ngay sau khi Edit báo non-unique match | Recovery được document là mở rộng old_string hoặc dùng replace_all. Read + Write là last resort, không phải phản ứng chuẩn |

### Practice scenario
Tìm mọi file gọi hàm deprecated `processLegacyOrder()` và test file của các caller đó. **Đáp án đúng**: Grep `processLegacyOrder` để tìm caller (lộ ra cả test import trực tiếp hàm), rồi Glob cho sibling test file (vd `**/OrderProcessor.test.*`) để bắt được test exercise hàm qua source module mà không nêu tên hàm.

### Key takeaway
"Grep search content file. Glob match path file. Edit là mặc định cho sửa đổi. Non-unique match thì mở rộng anchor hoặc dùng replace_all. Read + Write là fallback cuối cùng. Xây dựng hiểu biết codebase từng bước. Không bao giờ đọc hết file ngay từ đầu."
