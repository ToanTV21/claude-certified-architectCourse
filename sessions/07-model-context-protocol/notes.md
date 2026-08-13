# Session 07: Model Context Protocol

## Lessons trong section này
- [x] Introducing MCP
- [x] MCP clients
- [x] Project setup
- [x] Defining tools with MCP
- [x] The server inspector
- [x] Implementing a client
- [x] Defining resources
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

### Lesson 5 — The server inspector

**MCP Inspector** là 1 tool debug/test dạng browser, đi kèm sẵn trong Python MCP SDK — giúp test
server mà **không cần** kết nối vào 1 application đầy đủ (vd không cần wire tới Claude).

- Chạy inspector bằng lệnh:
  ```bash
  mcp dev mcp_server.py
  ```
  → khởi động 1 dev server (mặc định port **6277**) và cung cấp 1 local URL để mở trên browser.
- Sau khi mở URL, bấm **Connect** để start MCP server → thấy navigation bar gồm các mục
  **Resources**, **Prompts**, **Tools**...
- Test tool: vào mục **Tools** → **List Tools** để xem danh sách tools → chọn 1 tool → điền
  parameters → bấm **Run Tool** để chạy và xem kết quả.
- Có thể **chain nhiều thao tác** để verify — vd sau khi edit document xong, chạy lại tool read
  để confirm nội dung đã đổi đúng.
- Vòng lặp dev hiệu quả: sửa code server → test từng tool qua inspector → verify kết quả → debug
  cô lập (isolation) — không cần setup toàn bộ app mỗi lần test.

Thử với bài tập: [01_mcp_server.py](exercises/01_mcp_server.py) hoặc
[03_document_mcp_server.py](exercises/03_document_mcp_server.py) — xem lệnh `mcp dev` ở
[exercises/README.md](exercises/README.md).

### Lesson 6 — Implementing a client

Sau khi có server, cần build phía **client** — thành phần cho phép application giao tiếp với
MCP server và dùng functionality của nó.

**Lưu ý kiến trúc:** trong hầu hết project thực tế, bạn chỉ implement **1 trong 2** phía (client
HOẶC server) — không phải cả 2 (giống lesson "Project setup").

**Client gồm 2 thành phần chính:**
- **MCP Client** — 1 custom class tự viết để dùng session dễ hơn, đồng thời lo việc cleanup
  resource (đóng kết nối...) tự động khi dùng xong.
- **Client Session** (`ClientSession`) — kết nối thực sự tới server, là 1 phần của MCP Python SDK.

**2 method cốt lõi cần implement:**
- `list_tools()` — lấy danh sách tools available từ server:
  ```python
  async def list_tools(self) -> list[types.Tool]:
      result = await self.session().list_tools()
      return result.tools
  ```
- `call_tool(tool_name, tool_input)` — thực thi 1 tool cụ thể trên server với input do Claude
  cung cấp:
  ```python
  async def call_tool(
      self, tool_name: str, tool_input: dict
  ) -> types.CallToolResult | None:
      return await self.session().call_tool(tool_name, tool_input)
  ```

**Test client trực tiếp** (không qua Claude):
```python
async with MCPClient(
    command="uv", args=["run", "mcp_server.py"]
) as client:
    result = await client.list_tools()
    print(result)
```

**Luồng hoàn chỉnh khi hỏi Claude về 1 document** (vd "What is the contents of the report.pdf
document?"):
1. Code dùng client để lấy danh sách tools available.
2. Tools này được gửi kèm câu hỏi user tới Claude.
3. Claude quyết định cần dùng tool `read_doc_contents`.
4. Code dùng client để execute tool đó.
5. Kết quả được gửi ngược lại cho Claude → Claude trả lời user.

→ Client đóng vai trò "cầu nối" giữa application logic và MCP server, giúp bạn không cần quan tâm
chi tiết kết nối bên dưới.

Bài tập minh họa (dùng `ClientSession`/`stdio_client` trực tiếp từ SDK thay vì tự viết class
wrapper, nhưng cùng ý tưởng `list_tools`/`call_tool`):
[02_mcp_client.py](exercises/02_mcp_client.py).

### Lesson 7 — Defining resources

**Resources** trong MCP server dùng để **expose data** cho client — tương tự GET request handler
trong 1 HTTP server thông thường. Phù hợp cho các trường hợp cần **lấy thông tin (fetch)**, khác
với **tools** vốn dùng để **thực hiện hành động (perform actions)**.

**Ví dụ minh hoạ:** feature "document mention" — user gõ `@document_name` để reference file. Cần
2 thao tác: (1) lấy danh sách toàn bộ documents (cho autocomplete khi gõ `@`), (2) lấy nội dung
1 document cụ thể (khi mention được submit, tự động chèn nội dung đó vào prompt gửi Claude).

**Cách hoạt động:** theo pattern request-response — client gửi `ReadResourceRequest` kèm 1 **URI**,
MCP server trả lại data. URI đóng vai trò như địa chỉ của resource cần truy cập.

**2 loại resource:**
- **Direct Resource** — URI tĩnh, không đổi. Vd: `docs://documents`.
- **Templated Resource** — URI có tham số. Vd: `docs://documents/{doc_id}`. Python SDK tự parse
  tham số từ URI và truyền vào function dưới dạng keyword argument.

**Định nghĩa resource bằng decorator `@mcp.resource(...)`:**
```python
# Direct Resource — liệt kê toàn bộ documents
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())

# Templated Resource — lấy nội dung 1 document theo doc_id
@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]
```

**`mime_type`** — gợi ý cho client biết kiểu dữ liệu trả về, vd `application/json` (dữ liệu JSON
có cấu trúc), `text/plain` (plain text)... SDK tự động serialize giá trị trả về, không cần tự
convert sang JSON string thủ công.

**Test resources qua MCP Inspector** (`uv run mcp dev mcp_server.py` hoặc `mcp dev mcp_server.py`):
mục **Resources** hiển thị direct/static resources, mục **Resource Templates** hiển thị templated
resources có tham số. Click vào để test và xem chính xác cấu trúc response mà client sẽ nhận.

**Key points:**
- Resources expose data, tools thực hiện hành động.
- Direct resource cho static data, templated resource cho parameterized query.
- MIME type giúp client hiểu định dạng response.
- SDK tự lo phần serialize.
- Tên tham số trong templated URI trở thành function argument tương ứng.

Bài tập minh họa: đã bổ sung 2 resources (`list_docs`, `fetch_doc`) vào
[03_document_mcp_server.py](exercises/03_document_mcp_server.py).

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
| `mcp dev <server.py>` | CLI command | — | Chạy MCP Inspector (browser-based) để test tool/resource/prompt, mặc định port 6277 |
| `ClientSession` | Class (MCP SDK) | — | Kết nối thực sự tới MCP server; cung cấp `list_tools()`, `call_tool()`, `read_resource()`... |
| `@mcp.resource(uri, mime_type=...)` | Decorator | — | Định nghĩa 1 resource (direct hoặc templated); dùng để expose data, không phải thực hiện action |
| `ReadResourceRequest` | MCP message type | — | Client gửi kèm URI để yêu cầu server trả về data của resource đó |

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
- Phân biệt rõ **tools** (perform actions — có side effect) vs **resources** (expose/fetch data —
  giống GET handler, không side effect) — đề thi hay hỏi "khi nào dùng tool, khi nào dùng resource".
- **Direct resource** (URI tĩnh, vd `docs://documents`) khác **Templated resource** (URI có
  `{param}`, vd `docs://documents/{doc_id}`) — SDK tự parse param từ URI thành keyword argument.
- `mime_type` chỉ là **gợi ý định dạng** cho client, SDK vẫn tự serialize return value — không cần
  tự `json.dumps()` thủ công.

## Code Snippets
```python
# snippet
```

## Questions / Unclear Points
- ?
