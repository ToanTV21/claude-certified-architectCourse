# Session 07: Model Context Protocol

## Lessons trong section này
- [x] Introducing MCP
- [x] MCP clients
- [x] Project setup
- [x] Defining tools with MCP
- [ ] The server inspector
- [ ] Implementing a client
- [ ] Defining resources
- [ ] Accessing resources
- [ ] Defining prompts
- [ ] Prompts in the client
- [ ] MCP review
- [ ] Quiz on Model Context Protocol

## Key Concepts

### Lesson 1 — Introducing MCP

**MCP (Model Context Protocol)** là 1 communication layer/protocol giúp Claude nhận được
context và tools mà **không cần** tự tay viết integration code phức tạp cho từng service bên ngoài.

- Kiến trúc cơ bản gồm 2 phía:
  - **MCP Client** — chính là server/app của bạn (server bạn đang build), đóng vai trò kết nối tới các MCP Server.
  - **MCP Server** — 1 process/service độc lập, đóng gói sẵn **tools**, **resources**, **prompts**
    để expose cho client dùng, đóng vai trò như 1 interface/wrapper xung quanh 1 outside service
    (vd GitHub API, Slack API, database...).

**Vấn đề "The Tool Function Problem"** (lý do MCP ra đời):
- Ví dụ: build 1 chatbot trả lời câu hỏi về GitHub data (vd "What open pull requests are there
  across all my repositories?"). Nếu không có MCP, dev phải tự viết **toàn bộ** tools để gọi
  GitHub API — mỗi tool cần cả **schema definition** (mô tả tool cho Claude) lẫn **function
  implementation** (code thực thi gọi API thật).
- GitHub có rất nhiều functionality (repos, PRs, issues, projects...) → số lượng tools cần viết
  là rất lớn → tốn nhiều công sức viết, test, và maintain lâu dài.

**MCP giải quyết vấn đề này như thế nào:**
- MCP **chuyển gánh nặng** viết + duy trì tool definitions và tool execution logic từ phía server
  của bạn sang 1 **dedicated MCP server** riêng.
- MCP server đóng vai trò như 1 lớp wrapper bọc quanh functionality của service ngoài (vd GitHub),
  cung cấp sẵn các tools đã được author + implement hoàn chỉnh — bạn chỉ việc **connect và dùng**,
  không cần tự viết lại.
- Bất kỳ ai cũng có thể author 1 MCP server. Nhiều service provider tự phát hành **official MCP
  server** cho chính service của họ (vd AWS release official MCP server cho các dịch vụ AWS).

**MCP khác gì so với gọi thẳng API?**
- Gọi thẳng API (direct API call) → tự bạn chịu trách nhiệm viết tool schema + function cho từng
  endpoint muốn dùng.
- Dùng MCP server → tool schema + function đã có sẵn, bạn không cần tự implement, chỉ cần connect.

**MCP có phải chỉ là "tool use" không? (Common misconception)**
- **Không.** MCP servers và tool use là 2 khái niệm **bổ trợ nhau (complementary)** nhưng khác nhau.
- Tool use = cơ chế Claude gọi tool (khái niệm chung, không quan tâm ai viết tool).
- MCP = quyết định **ai là người viết và maintain** các tools đó. Với MCP, người khác (author của
  MCP server) đã viết sẵn schema + function, đóng gói bên trong MCP server — bạn chỉ dùng lại.

**Insight cốt lõi:** MCP servers cung cấp sẵn tool schemas và tool functions, giúp bạn không phải
tự build và maintain các integration phức tạp.

### Lesson 2 — MCP clients

**MCP Client** là cầu nối giao tiếp (communication bridge) giữa server của bạn và MCP server —
coi nó như "access point" để dùng mọi tools mà 1 MCP server cung cấp. Client lo toàn bộ việc
truyền message + chi tiết protocol, bạn không cần tự implement lại phần này.

**Transport agnostic:**
- MCP client/server có thể giao tiếp qua nhiều kiểu **transport** khác nhau — đây là điểm mạnh của MCP.
- Phổ biến nhất: cả client và server chạy **trên cùng 1 máy**, giao tiếp qua **standard input/output (stdio)**.
- Ngoài ra còn hỗ trợ: **HTTP**, **WebSockets**, và các network protocol khác — tức client/server
  không nhất thiết phải cùng máy.

**Message types chính (theo MCP spec):**
- `ListToolsRequest` / `ListToolsResult` — client hỏi server "bạn có những tools nào?", server trả
  về danh sách tools available.
- `CallToolRequest` / `CallToolResult` — client yêu cầu server chạy 1 tool cụ thể kèm arguments,
  rồi nhận lại kết quả thực thi.

**Complete flow ví dụ** — user hỏi "What repositories do I have?":
1. User gửi query tới server của bạn.
2. Server nhận ra cần cung cấp cho Claude danh sách tools available trước khi gọi Claude.
3. Server nhờ **MCP client** lấy tools → client gửi `ListToolsRequest` tới **MCP server** → nhận
   về `ListToolsResult`.
4. Server giờ có đủ (câu hỏi của user + danh sách tools) để gọi Claude lần đầu.
5. Claude xem xét tools, quyết định cần gọi 1 tool để trả lời → Claude trả về 1 tool use request.
6. Server nhờ MCP client thực thi tool đó → client gửi `CallToolRequest` tới MCP server → MCP
   server thực sự gọi GitHub API.
7. GitHub trả dữ liệu repo → chảy ngược lại qua MCP server (đóng gói thành `CallToolResult`) →
   về MCP client → về server của bạn.
8. Server gửi kết quả tool đó về lại cho Claude trong 1 message tiếp theo (follow-up message).
9. Claude giờ có đủ thông tin, trả về câu trả lời hoàn chỉnh → server trả lời lại cho user.

Nhiều bước, nhưng mỗi component có trách nhiệm rõ ràng: **MCP client** che giấu hết độ phức tạp
của việc giao tiếp với server, giúp bạn tập trung vào application logic thay vì lo chi tiết protocol.

Lưu ý: file bài tập [01_mcp_server.py](exercises/01_mcp_server.py) và
[02_mcp_client.py](exercises/02_mcp_client.py) đã minh họa sẵn phần implementation cụ thể của
client/server này (sẽ được note chi tiết hơn ở lesson "Implementing a client").

### Lesson 3 — Project setup

Lesson này giới thiệu 1 hands-on project: xây dựng **CLI-based chatbot** để hiểu rõ hơn cách MCP
client và MCP server phối hợp với nhau trong thực tế.

- Chatbot cho phép user tương tác với 1 tập hợp documents qua command-line interface.
- Gồm 2 thành phần chính:
  - 1 **MCP client** — xử lý tương tác với user.
  - 1 **custom MCP server** — quản lý document operations (đọc + update), lưu documents
    **in-memory** (không cần database) để đơn giản hoá.

**Lưu ý kiến trúc quan trọng:** trong các dự án thực tế, thường bạn chỉ implement **1 trong 2**
phía — hoặc là MCP server (để expose service của mình cho dev khác dùng), hoặc là MCP client (để
kết nối tới các MCP server có sẵn). Project này xây **cả 2** chỉ vì mục đích học tập, để hiểu cách
chúng giao tiếp với nhau.

**Setup project** (theo lesson gốc, dùng file `cli_project.zip` đính kèm bài học, không áp dụng
trực tiếp trong workspace này):
1. Thêm Anthropic API key vào file `.env`.
2. Cài dependencies bằng UV (khuyến nghị) hoặc pip.
3. Chạy thử app khởi điểm để verify mọi thứ hoạt động (`uv run main.py` hoặc `python main.py`).
4. Project gốc có các file chính: `main.py`, `mcp_client.py`, `mcp_server.py`.

→ Trong workspace `fpt-claude-study`, phần thực hành tương đương được thể hiện qua
[01_mcp_server.py](exercises/01_mcp_server.py) và [02_mcp_client.py](exercises/02_mcp_client.py)
(không cần download file zip riêng).

### Lesson 4 — Defining tools with MCP

Dùng **official Python MCP SDK** (`mcp.server.fastmcp.FastMCP`) giúp việc viết MCP server đơn
giản hơn nhiều so với tự tay viết JSON schema thủ công — SDK tự lo phần đó thông qua
**decorators** và **type hints**.

**Khởi tạo server chỉ với 1 dòng:**
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("DocumentMCP", log_level="ERROR")
```

**Lưu documents in-memory** bằng 1 Python `dict` đơn giản (key = doc id, value = nội dung).

**Định nghĩa tool bằng decorator `@mcp.tool(...)`:**
- Tham số `name` và `description` mô tả tool cho Claude (thay cho việc tự viết JSON schema).
- Mỗi argument của function dùng `Field(description=...)` (từ **Pydantic**) để mô tả rõ ràng
  argument đó dùng để làm gì — Claude dựa vào các description này để biết cách gọi tool đúng.
- SDK tự động sinh JSON schema từ type hints + `Field` description → không cần viết schema thủ công.

**2 tools ví dụ trong lesson:**
- `read_doc_contents(doc_id)` — đọc nội dung 1 document theo id, raise `ValueError` nếu không
  tìm thấy id.
- `edit_document(doc_id, old_str, new_str)` — tìm-và-thay-thế (find-and-replace) 1 đoạn text
  trong document, dùng method `str.replace()` có sẵn của Python.

**Error handling:** cả 2 tools đều raise `ValueError` kèm message rõ ràng khi `doc_id` không tồn
tại — Claude có thể đọc message này và phản ứng phù hợp (vd báo lại cho user, hoặc thử id khác).

**Lợi ích chính của cách dùng SDK này:**
- Tự động sinh JSON schema từ Python type hints.
- Code sạch, dễ maintain.
- Validation tham số có sẵn nhờ Pydantic.
- Giảm boilerplate so với viết schema thủ công.
- Có type safety + IDE hỗ trợ tốt hơn khi code.

Bài tập minh họa: [03_document_mcp_server.py](exercises/03_document_mcp_server.py).

## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
| MCP Client | Concept/component | — | Chính là server/app của bạn, kết nối tới MCP Server(s) |
| MCP Server | Concept/component | — | Process độc lập, đóng gói sẵn tools/resources/prompts cho 1 outside service |
| `ListToolsRequest`/`ListToolsResult` | MCP message type | — | Client hỏi server "có tools gì?" / server trả về danh sách tools |
| `CallToolRequest`/`CallToolResult` | MCP message type | — | Client yêu cầu server chạy 1 tool + args / server trả kết quả thực thi |
| Transport (stdio/HTTP/WebSocket) | Concept | stdio (cùng máy) | MCP transport agnostic — client/server có thể giao tiếp qua nhiều kênh khác nhau |
| `FastMCP(name, log_level=...)` | Class (Python MCP SDK) | — | Khởi tạo MCP server chỉ với 1 dòng, không cần viết JSON schema thủ công |
| `@mcp.tool(name=..., description=...)` | Decorator | — | Đánh dấu 1 function Python là 1 MCP tool; SDK tự sinh JSON schema từ type hints |
| `Field(description=...)` | Pydantic | — | Mô tả từng argument của tool để Claude hiểu cách truyền tham số đúng |

## Gotchas
- [ ] MCP **không thay thế** tool use — MCP chỉ giải quyết vấn đề "ai viết và maintain tool
      schema/function", còn cơ chế Claude gọi tool (tool use) vẫn hoạt động như bình thường.
- [ ] Không phải cứ có API là cần MCP — nếu chỉ cần 1-2 tools đơn giản, tự viết trực tiếp có thể
      nhanh hơn setup + connect tới 1 MCP server.

## CCA-F Exam Tips
- Câu hỏi hay đánh lừa dạng "MCP is the same as tool use" — **sai**, MCP và tool use là 2 khái
  niệm complementary nhưng khác nhau (MCP quyết định *ai* viết tool, tool use là *cơ chế gọi* tool).
- Nhớ đúng vai trò 2 phía: **MCP Client** = app/server của bạn; **MCP Server** = process đóng gói
  sẵn tools/resources/prompts cho 1 service ngoài.
- Nhớ đúng thứ tự flow: `ListToolsRequest` (lấy danh sách tools) luôn xảy ra **trước** khi gọi
  Claude lần đầu; `CallToolRequest` chỉ xảy ra **sau khi** Claude quyết định cần dùng tool nào đó.
- MCP là **transport agnostic** — đề bài có thể hỏi transport nào là phổ biến nhất khi client/server
  cùng máy → đáp án là **stdio (standard input/output)**, không phải HTTP.
- Trong 1 project thực tế thường chỉ implement **1 trong 2** phía (client HOẶC server), không phải
  cả 2 — làm cả 2 chỉ để mục đích học tập.
- `@mcp.tool` + Pydantic `Field` thay thế hoàn toàn việc viết JSON schema thủ công — đây là điểm
  khác biệt chính giữa dùng SDK và tự viết tool schema tay (theo cách "trước MCP" ở lesson 1).

## Code Snippets
```python
# snippet
```

## Questions / Unclear Points
- ?
