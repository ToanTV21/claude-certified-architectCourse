# Session 04: Tool Use with Claude

## Lessons trong section này
- [x] Introducing tool use
- [x] Project overview
- [x] Tool functions
- [x] Tool schemas
- [x] Handling message blocks
- [x] Sending tool results
- [x] Multi-turn conversations with tools
- [x] Implementing multiple turns
- [x] Using multiple tools
- [x] The Batch tool
- [x] Tools for structured data
- [x] Fine grained tool calling
- [x] The text edit tool
- [x] The web search tool
- [ ] Quiz on tool use with Claude

## Key Concepts

### Tool use là gì
Mặc định Claude chỉ biết những gì có trong **training data** — không có thông tin real-time
(thời tiết hiện tại, giờ hiện tại, dữ liệu nội bộ công ty...). **Tool use** là cơ chế cho phép
Claude "xin" server chạy code để lấy thêm dữ liệu bên ngoài, rồi dùng dữ liệu đó để trả lời.

Luồng tool use cơ bản (5 bước):
1. Gửi request ban đầu tới Claude kèm khai báo `tools` (schema mô tả các tool khả dụng)
2. Claude tự đánh giá có cần dữ liệu ngoài không → nếu cần, trả về `tool_use` block yêu cầu gọi tool
3. Server (code của mình) chạy hàm Python tương ứng để lấy dữ liệu
4. Gửi request tiếp theo kèm kết quả tool (`tool_result`) trong lịch sử hội thoại
5. Claude sinh câu trả lời cuối cùng dựa trên prompt gốc + dữ liệu vừa lấy được

Ví dụ end-to-end trong khóa học — **Project Overview: reminder app**. Mục tiêu dạy Claude set
reminder theo thời gian (vd "nhắc tôi khám bệnh, thứ Năm tuần sau"). 3 vấn đề Claude không tự
giải quyết được, cần 3 tool tương ứng:
| Vấn đề | Tool cần build |
|---|---|
| Claude không biết giờ hiện tại chính xác | `get_current_datetime` |
| Claude tính sai khi cộng/trừ thời gian (vd cộng 379 ngày) | `add_duration_to_datetime` |
| Claude hiểu khái niệm reminder nhưng không có cơ chế thực thi | `set_reminder` |

Cách tiếp cận: build từng tool một, sau đó phối hợp nhiều tool trong 1 cuộc hội thoại
(tool chaining).

### Tool Functions (hàm Python thực thi tool)
Là hàm Python bình thường, được Claude "gọi" khi nó xác định cần thêm dữ liệu. Best practice:
- Đặt tên hàm + tên argument rõ ràng, mô tả đúng chức năng (Claude dựa vào tên để hiểu công dụng)
- **Validate input ngay đầu hàm**, raise lỗi có message rõ ràng — vì error message này Claude
  **nhìn thấy được** và có thể tự retry với tham số đã sửa
- Đối chiếu Java: giống việc validate argument đầu method rồi `throw new IllegalArgumentException("...")`
  — khác biệt là ở đây "caller" bắt lỗi lại chính là Claude, không phải code Java gọi trực tiếp

```python
def get_current_datetime(date_format="%Y%m%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date format cannot be empty")
    return datetime.now().strftime(date_format)
```

Ví dụ cụ thể từ lesson "Tool functions" (bài đầu tiên trong loạt 3 tool của reminder app):
`get_current_datetime(date_format="%Y-%m-%d %H:%M:%S")` — dùng `datetime.now().strftime(date_format)`
để trả string đã format theo yêu cầu. Test nhanh với format khác nhau:
```python
get_current_datetime()          # "2024-01-15 14:30:25" (default format)
get_current_datetime("%H:%M")   # "14:30"
```
Validate `date_format` rỗng chỉ để minh hoạ pattern validate-input, không phải case Claude hay
gặp thực tế — nhưng vẫn nên giữ vì dạy đúng thói quen: **luôn validate + raise error rõ ràng ở
tool function**, vì Claude nhìn thấy error message và có thể tự sửa tham số rồi gọi lại.

### Tool Schemas (JSON Schema mô tả tool cho Claude)
**JSON Schema** là chuẩn validate dữ liệu JSON nói chung (không riêng cho ML), được cộng đồng ML
dùng lại để mô tả tool cho các model. Một tool schema gồm 3 phần:
- `name`: định danh tool
- `description`: 3-4 câu giải thích tool làm gì, dùng khi nào, trả về dữ liệu gì
  (Claude chỉ dựa vào phần này để quyết định có gọi tool hay không → viết càng rõ càng chính xác)
- `input_schema`: JSON Schema mô tả các argument (type, description, required)

Mẹo tạo schema nhanh: đưa hàm Python cho Claude.ai, prompt "viết JSON schema chuẩn cho
tool calling, theo best practice trong docs đính kèm", đính kèm trang docs tool use của Anthropic.

Convention đặt tên: `[ten_ham]_schema` cho biến schema, import `ToolParam` từ `anthropic.types`
để wrap dict schema (giúp bắt lỗi type sớm hơn khi code sai cấu trúc).

**Ví dụ end-to-end** — hàm `get_current_datetime` (1 trong 3 tool của reminder app) và schema
tương ứng, đặt tên theo convention `<function_name>_schema`:

```python
from anthropic.types import ToolParam  # wrap dict để có type-check ở dev-time

def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)

# ToolParam bọc ngoài dict — không đổi cấu trúc runtime, chỉ giúp IDE/type-checker
# báo lỗi sớm nếu key sai tên hoặc thiếu field bắt buộc (vd thiếu "input_schema")
get_current_datetime_schema = ToolParam({
    "name": "get_current_datetime",
    "description": "Returns the current date and time formatted according to the specified format. "
                    "Use this whenever the conversation needs to know 'now' — e.g. to compute a "
                    "reminder time relative to the present moment. Returns a single formatted string.",
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": "strftime format code, e.g. '%Y-%m-%d %H:%M:%S' or '%H:%M'.",
                "default": "%Y-%m-%d %H:%M:%S",
            }
        },
        "required": [],  # optional — không bắt buộc Claude phải truyền
    },
})
```

Đối chiếu Java: `input_schema` giống 1 interface mô tả tham số cho 1 "Builder" — mỗi `properties`
là 1 field, `required` giống list field không có default value trong constructor. `ToolParam`
tương tự việc dùng 1 class DTO có validate thay vì truyền thẳng 1 `Map<String, Object>` — bắt lỗi
compile-time thay vì runtime.

### Handling Message Blocks (message nhiều block)
Khi dùng tool, `message.content` không còn là 1 block text đơn giản nữa mà là **list nhiều block**:
- `text` block = phần Claude giải thích cho người dùng
- `tool_use` block = tên tool + argument Claude muốn gọi

→ Vì API **không lưu lịch sử hội thoại** (đã học ở session 01), mọi lần gửi tiếp phải tự
append **toàn bộ `response.content`** (không chỉ lấy text) vào `messages`. Các hàm helper
`add_user_message` / `add_assistant_message` phải sửa lại để nhận list block thay vì chỉ nhận string.

Đối chiếu Java: giống việc 1 response object có nhiều "field" khác kiểu (text vs action-request)
thay vì chỉ 1 String trả về — phải xử lý theo dạng polymorphic list thay vì giá trị đơn.

**Cấu trúc 1 multi-block assistant message** khi Claude quyết định gọi tool, `response.content`
là 1 list gồm (thứ tự có thể khác nhau tùy lần gọi):
- **Text block** — phần Claude giải thích cho user trước khi gọi tool (vd "Let me check that for
  you") — có thể có hoặc không, tùy Claude quyết định
- **ToolUse block** — gồm `type="tool_use"`, `id` (dùng để khớp với `tool_result` sau này),
  `name` (tên tool), `input` (dict tham số Claude tự suy ra từ user message)

**Cập nhật helper functions** để nhận cả string (single text) lẫn list block (multi-block), thay
vì chỉ nhận string như ở session 01:

```python
def add_user_message(messages: list, content) -> None:
    # content có thể là str (message thường) hoặc list block (vd tool_result)
    messages.append({"role": "user", "content": content})


def add_assistant_message(messages: list, content) -> None:
    # content có thể là str, hoặc trực tiếp response.content (list block text + tool_use)
    # khi content là response object thì lấy .content, còn lại giữ nguyên
    messages.append({"role": "assistant", "content": content})
```

Thực chất chỉ cần bỏ ép kiểu `str` ở signature — `content` giờ nhận `str | list`, logic append
không đổi vì Anthropic API tự hiểu cả 2 dạng (string được coi như 1 text block ngầm định).

**Luồng đầy đủ khi dùng tool** (5 bước):
1. Gửi user message + khai báo `tools=[...]` cho Claude
2. Nhận về assistant message multi-block (text block + tool_use block)
3. Đọc `tool_use` block, thực thi hàm Python tương ứng ở phía server mình
4. Gửi lại **toàn bộ** `response.content` (làm assistant message) + `tool_result` (làm user
   message mới) — đầy đủ lịch sử để Claude có context
5. Nhận response cuối cùng từ Claude, dựa trên kết quả tool vừa có

### Sending Tool Results (gửi kết quả tool lại cho Claude)
Sau khi server chạy xong tool function, đóng gói kết quả thành `tool_result` block và gửi lại
trong 1 **user message** mới (không phải assistant message):

| Field | Ý nghĩa |
|---|---|
| `tool_use_id` | Phải khớp đúng `id` của `tool_use` block gốc — để Claude biết kết quả này ứng với lần gọi tool nào |
| `content` | Output của hàm, thường convert sang string (JSON) |
| `is_error` | `true`/`false` — báo cho Claude biết tool chạy lỗi hay thành công |

`tool_use_id` quan trọng khi Claude gọi **nhiều tool cùng lúc** trong 1 message — mỗi tool_use
cần đúng 1 tool_result khớp id, nếu không Claude không biết ghép kết quả nào với lời gọi nào.
Request tiếp theo vẫn phải gửi kèm `tools` schema dù không dùng tool nữa, và gửi đủ toàn bộ
lịch sử hội thoại trước đó.

### Multi-Turn Conversations with Tools + Implementing Multiple Turns
Một câu hỏi user có thể cần Claude gọi **nhiều tool nối tiếp nhau** (vd: hỏi "103 ngày nữa là
ngày nào" → cần gọi `get_current_datetime` trước rồi mới gọi `add_duration_to_datetime`).
Không thể đoán trước cần bao nhiêu vòng gọi tool → phải dùng **while loop** lặp cho tới khi
Claude không còn yêu cầu tool nữa.

Field quan trọng: **`stop_reason`** trên response — cho biết *tại sao* Claude ngừng sinh text.
Nếu `stop_reason == "tool_use"` nghĩa là Claude còn muốn gọi tool → phải lặp tiếp; các giá trị
khác đều coi là kết thúc vòng lặp (Claude đã xong, dù xong theo cách nào):

| `stop_reason` | Ý nghĩa |
|---|---|
| `"tool_use"` | Claude quyết định cần gọi 1 (hoặc nhiều) tool trước khi trả lời tiếp |
| `"end_turn"` | Claude đã sinh xong assistant message — trường hợp kết thúc bình thường |
| `"max_tokens"` | Chạm giới hạn `max_tokens`, Claude bị cắt ngang, không sinh thêm được nữa |
| `"stop_sequence"` | Claude gặp đúng 1 trong các `stop_sequences` đã khai báo, dừng lại |

Đối chiếu Java: giống 1 `enum ExitReason` trả về từ 1 vòng lặp/state machine — khác với chỉ có
1 flag `done: boolean`, ở đây biết luôn *lý do* dừng để xử lý khác nhau (vd `max_tokens` nên cảnh
báo/log riêng vì output có thể bị cắt cụt giữa chừng, không giống 1 câu trả lời hoàn chỉnh).

Kiến trúc vòng lặp (3 hàm chính):
- `run_conversation(messages)`: gọi Claude → append response vào history → check `stop_reason`,
  nếu không phải `tool_use` thì `break` → nếu có thì gọi `run_tools()` → append tool results
  (dạng user message) → lặp lại
- `run_tools(message)`: lọc các block có `type == "tool_use"` trong `message.content`, chạy từng
  tool qua `run_tool()`, gói mỗi kết quả thành 1 `tool_result` block, trả về list
- `run_tool(tool_name, tool_input)`: dispatcher — dùng if/elif map tên tool → hàm Python tương
  ứng, bọc trong try/except để set `is_error=True` + message lỗi nếu hàm raise exception

Đối chiếu Java: giống pattern `switch` dispatch theo command name (Command Pattern), vòng lặp
tương tự event loop xử lý cho tới khi nhận "done" signal.

**Refactor helper functions cho conversation loop** — trước khi implement `run_conversation()`
gọn gàng, course refactor lại 3 chỗ:

1. **`add_user_message` / `add_assistant_message` nhận cả `Message` object** — không chỉ str
   hay list block như trước, mà còn nhận thẳng response trả về từ `client.messages.create()`,
   tự `isinstance(message, Message)` để lấy `.content` ra:
   ```python
   from anthropic.types import Message

   def add_user_message(messages, message):
       user_message = {
           "role": "user",
           "content": message.content if isinstance(message, Message) else message,
       }
       messages.append(user_message)
   ```
   Đối chiếu Java: giống method overload nhận nhiều kiểu tham số, tự branch xử lý theo
   runtime type (`instanceof` check) thay vì bắt caller phải tự `.content` trước khi gọi.

2. **`chat()` nhận thêm `tools` param, trả về full `Message`** (không ép về text nữa) —
   để giữ lại `tool_use` block cho vòng lặp xử lý tiếp:
   ```python
   def chat(messages, system=None, temperature=1.0, stop_sequences=[], tools=None):
       params = {
           "model": model, "max_tokens": 1000, "messages": messages,
           "temperature": temperature, "stop_sequences": stop_sequences,
       }
       if tools:
           params["tools"] = tools
       if system:
           params["system"] = system
       return client.messages.create(**params)
   ```

3. **`text_from_message()`** — helper tách text ra khi cần hiển thị cho user (vì `chat()`
   giờ trả `Message` chứ không phải string nữa):
   ```python
   def text_from_message(message):
       return "\n".join(block.text for block in message.content if block.type == "text")
   ```

Xem implementation đầy đủ (bài toán "103 ngày nữa là ngày nào?", cần 2 tool nối tiếp
`get_current_datetime` → `add_duration_to_datetime`) trong
[10_conversation_loop_chat_helper.py](exercises/10_conversation_loop_chat_helper.py).

### Using Multiple Tools (thêm tool mới vào hệ thống có sẵn)
Sau khi đã có khung sườn (tool schema + dispatcher + tool function), thêm 1 tool mới chỉ cần
3 bước lặp lại pattern:
1. Thêm schema mới vào list `tools` gửi cho Claude
2. Thêm 1 nhánh `elif` trong `run_tool()` dispatcher để route tới tool mới
3. Viết hàm Python thực thi tool đó

Claude có thể tự chain nhiều tool khác nhau trong 1 cuộc hội thoại (vd tính ngày trước, rồi
dùng kết quả đó gọi `set_reminder`).

### The Batch Tool (gộp nhiều lời gọi tool trong 1 message)
Vấn đề: về lý thuyết Claude có thể trả về nhiều `tool_use` block trong cùng 1 message (gọi song
song), nhưng thực tế Claude thường gọi tuần tự từng round → tốn nhiều round-trip không cần thiết.

Giải pháp: định nghĩa 1 tool "ảo" tên `batch`, nhận vào `invocations` — 1 list các lời gọi tool
(mỗi item có tên tool + argument). Thay vì gọi trực tiếp N tool riêng lẻ, Claude chỉ cần gọi
1 lần tool `batch` với danh sách N lời gọi bên trong.

Implementation: `run_batch()` loop qua từng `invocation`, parse tên tool + argument (JSON), gọi
lại `run_tool()` cho từng cái, gom kết quả vào `batch_output`, trả về 1 lần.

→ Bản chất là "đánh lừa" Claude thực hiện song song bằng cách cho nó 1 abstraction cấp cao hơn,
giảm số round-trip request/response.

### Tools for Structured Data (dùng tool để ép output có cấu trúc)
Cách khác thay cho kỹ thuật pre-fill message + stop sequence (đã học ở session 01/03) để lấy
JSON có cấu trúc: định nghĩa 1 tool có `input_schema` chính là cấu trúc dữ liệu mong muốn, rồi
**ép Claude luôn gọi tool đó** bằng `tool_choice`:

```python
tool_choice = {"type": "tool", "name": "ten_tool_extract"}
```

Khi đó Claude không trả lời bằng text nữa mà luôn trả về `tool_use` block với `input` chính là
dữ liệu có cấu trúc — lấy trực tiếp qua `response.content[0].input`, **không cần** gửi lại
`tool_result` (không giống flow tool use thông thường, vì mục đích chỉ là extract dữ liệu chứ
không cần Claude xử lý tiếp).

So sánh 2 cách:
| Cách | Ưu điểm | Nhược điểm |
|---|---|---|
| Prefill + stop sequence | Đơn giản, nhanh setup | Kém tin cậy hơn với cấu trúc phức tạp |
| Tool + `tool_choice` ép buộc | Tin cậy cao, validate theo schema | Setup phức tạp hơn |

### Fine Grained Tool Calling (streaming JSON argument của tool)
Khi **streaming** + có tool, ngoài `content_block_delta` bình thường còn có thêm event
`input_json_delta` chứa 2 field:
- `partial_json`: chunk JSON mới vừa sinh ra
- `snapshot`: bản JSON tích lũy từ đầu tới hiện tại (gộp toàn bộ chunk đã nhận)

**Mặc định**: API tự **validate JSON** trước khi gửi chunk cho client — Claude sinh JSON theo
từng phần, nhưng API chờ tới khi **đủ 1 cặp key-value hoàn chỉnh** mới validate rồi mới gửi
→ hiện tượng: có độ trễ, sau đó chunk đổ về dồn dập (burst) thay vì mượt.

**Fine-grained mode** (`fine_grained: true` trong tool schema): tắt validation phía API, gửi
chunk ngay khi Claude sinh ra → trải nghiệm streaming mượt hơn (giống streaming text thường),
nhưng **đổi lại** client phải tự xử lý trường hợp JSON chưa hợp lệ (vd `undefined` thay vì
`null`) vì không còn được validate trước.

| Chế độ | Ưu điểm | Nhược điểm |
|---|---|---|
| Mặc định (có validate) | JSON luôn hợp lệ khi tới client | Có độ trễ, chunk dồn cục |
| `fine_grained: true` | Streaming mượt, cập nhật UI ngay lập tức | Client phải tự bắt lỗi JSON không hợp lệ |

Dùng `fine_grained` khi cần cập nhật UI theo thời gian thực ngay khi Claude đang gõ argument
(vd hiển thị preview trong lúc Claude đang soạn); dùng mặc định khi độ trễ chấp nhận được.

### The Text Editor Tool (built-in tool sửa file)
**Text Editor Tool** = 1 trong số ít tool có **JSON schema built-in sẵn trong Claude** (không
cần tự viết `input_schema`) — nhưng **phần thực thi (implementation) vẫn phải tự code**, Claude
chỉ biết "yêu cầu" thao tác (view file, string replace, create file, undo...) chứ không tự thao
tác trên máy mình.

Cách dùng: chỉ cần gửi 1 **schema stub** rất gọn (chỉ `name` + `type`), API tự động expand
thành full schema phía server. Bảng version schema theo model (tra đúng docs
[text-editor-tool](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/text-editor-tool),
không được cố định 1 giá trị vì `type` đi kèm ngày tháng khác nhau tùy version model):

| Model | `type` | `name` |
|---|---|---|
| Claude 4.x (Opus/Sonnet/Haiku 4.5, kể cả `claude-haiku-4-5` project này đang dùng) | `text_editor_20250728` | `str_replace_based_edit_tool` |
| Claude Sonnet 3.7 | `text_editor_20250124` | `str_replace_editor` |
| Claude Sonnet 3.5 | `text_editor_20241022` | `str_replace_editor` |

```python
# Model hiện tại của project là claude-haiku-4-5 -> dùng schema Claude 4.x
text_editor_tool = {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}
```

**Lưu ý quan trọng:** trên Claude 4.x, **cả 2 field `type` lẫn `name` đều phải đổi cùng lúc**
— chỉ đổi `type` mà giữ `name="str_replace_editor"` (name cũ của bản 3.x) sẽ bị lỗi 400.
Ngoài ra bản 4.x **không còn hỗ trợ command `undo_edit`** (có ở bản 3.x) — nếu code implementation
có xử lý command này thì bản 4.x sẽ không bao giờ nhận được request đó từ Claude.

Vẫn theo đúng flow tool use thông thường: Claude trả `tool_use` block (vd `command="str_replace"`,
`path`, `old_str`, `new_str`) → code tự viết hàm thực thi (đọc/ghi file thật) → gửi lại
`tool_result`. Không có sẵn code đọc/ghi file — Anthropic chỉ cung cấp *hình dạng* tool, hành vi
thật do mình implement (đối chiếu Java: giống 1 `interface` được định nghĩa sẵn, còn `impl` là
việc của dev).

Các `command` khả dụng trên bản 4.x (`str_replace_based_edit_tool`):
| `command` | Input | Hành động |
|---|---|---|
| `view` | `path`, optional `view_range` | Xem nội dung file hoặc liệt kê thư mục |
| `create` | `path`, `file_text` | Tạo mới/ghi đè file |
| `str_replace` | `path`, `old_str`, `new_str` | Thay thế đúng 1 chỗ khớp — lỗi nếu khớp 0 hoặc >1 lần |
| `insert` | `path`, `insert_line`, `insert_text` | Chèn text sau dòng `insert_line` (0 = đầu file) |

**Security khi tự implement:** `path` là input do Claude (model output) sinh ra — **không đáng
tin cậy**. Phải resolve `path` về dạng canonical rồi kiểm tra nó còn nằm trong 1 thư mục gốc cố
định trước khi đọc/ghi (chặn `../`, symlink, absolute path ra ngoài root) — tương tự lỗi path
traversal trong Java nếu dùng thẳng `new File(userInput)` không validate.

Use case: build 1 code editor tự động (kiểu Claude Code) mà không có GUI, thao tác file hàng loạt.

Xem implementation đầy đủ trong
[12_text_editor_tool.py](exercises/12_text_editor_tool.py) — minh họa `view`, `create`,
`str_replace`, `insert`, kèm sandbox path validation.

### The Web Search Tool (built-in tool tìm kiếm web)
**Web Search Tool** = built-in tool **không cần tự code implementation** — khác hẳn Text Editor
Tool ở trên. Chỉ cần khai báo schema, Claude tự chạy search và trả kết quả trực tiếp trong response.

**Bắt buộc:** phải **bật tính năng này trong Console settings** trước khi dùng, ở
[console.anthropic.com/settings/privacy](https://console.anthropic.com/settings/privacy) —
nếu chưa bật, request sẽ lỗi dù schema đúng 100%. Đây là setting ở mức **organization**, không
phải thứ chỉnh trong code.

Schema:
```python
web_search_tool = {
    "type": "web_search_20250305",   # type cố định cho web search tool
    "name": "web_search",
    "max_uses": 5,                    # giới hạn tổng số lần search trong 1 request (default 5)
    "allowed_domains": ["nih.gov"],   # optional — giới hạn search chỉ trong domain cụ thể
}
```

`allowed_domains` hữu ích khi cần đảm bảo chất lượng nguồn (vd chỉ lấy thông tin y tế/thể dục từ
NIH.gov thay vì web chung chung không kiểm chứng được).

Response trả về nhiều loại block khác nhau, cần phân biệt khi render UI:
| Block type | Ý nghĩa |
|---|---|
| Text block | Câu trả lời Claude viết cho user |
| Tool use block | Câu query Claude đã search |
| Web search result block | Trang tìm được (title, URL) |
| Citation block | Đoạn text cụ thể được trích dẫn, gắn với nguồn hỗ trợ tuyên bố đó |

Không giống flow tool use tự viết — **không cần** tự gửi lại `tool_result`, Claude tự chạy search
và tự nối kết quả vào response cuối cùng trong cùng 1 lần gọi `client.messages.create()`. Có thể
Claude search **nhiều lần** trong cùng 1 request (tối đa `max_uses`).

## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
| `tools` | `list[dict]` (create()) | không truyền | Khai báo danh sách tool khả dụng cho Claude |
| `tool_choice` | `dict` (create()) | `{"type": "auto"}` | `{"type": "tool", "name": "..."}` ép Claude luôn gọi đúng 1 tool cụ thể |
| `stop_reason` | `str` (response field) | — | `"tool_use"` / `"end_turn"` / `"max_tokens"` / `"stop_sequence"` — chỉ `"tool_use"` cần lặp tiếp |
| `tool_use_id` | `str` (trong tool_use / tool_result block) | — | Khóa nối kết quả tool với đúng lời gọi tool tương ứng |
| `is_error` | `bool` (trong tool_result block) | `false` | Báo Claude biết tool chạy lỗi để nó tự điều chỉnh/retry |
| `ToolParam` | class (`anthropic.types`) | — | Wrap dict schema để có type-check khi code |
| `fine_grained` | `bool` (field trong tool schema) | `false` | `true` = tắt validate JSON phía API khi stream, đổi lại gửi chunk nhanh hơn |
| `max_uses` | `int` (web_search tool schema) | `5` | Giới hạn tổng số lần Claude được search trong 1 request |
| `allowed_domains` | `list[str]` (web_search tool schema) | không giới hạn | Giới hạn search chỉ trong các domain chỉ định |
| `citations` | `dict` (create() param) | không bật | `{"enabled": true}` — bật trích dẫn nguồn cho response |

## Gotchas
- [x] `tool_choice` mặc định là `{"type": "auto"}` — muốn ép gọi 1 tool cụ thể phải set
  `{"type": "tool", "name": "..."}`, không phải truyền tên tool trực tiếp vào `tools`
- [x] Khi có tool, `message.content` là **list nhiều block** (text + tool_use) — không được chỉ
  lấy `content[0].text` như session 01, phải lọc theo `block.type`
- [x] Phải append **toàn bộ** `response.content` (không chỉ text) vào lịch sử hội thoại, nếu
  không Claude sẽ mất context về lời gọi tool đã thực hiện
- [x] `tool_result` phải nằm trong **user message**, không phải assistant message
- [x] Vẫn phải gửi kèm `tools` schema ở mọi request tiếp theo trong cùng hội thoại, kể cả khi
  không cần gọi tool nữa — nếu bỏ đi Claude có thể mất khả năng nhận diện các tool_use cũ trong history
- [x] Khi dùng `tool_choice` ép buộc để lấy structured data, **không cần** gửi `tool_result` quay
  lại — khác với luồng tool use thông thường
- [x] Web Search Tool và Text Editor Tool đều là **built-in tool** nhưng khác nhau: Web Search
  tự chạy luôn, không cần gửi lại `tool_result`; Text Editor chỉ có sẵn schema, phần thực thi
  (đọc/ghi file thật) vẫn phải tự code y như tool tự định nghĩa
- [x] `type` của Text Editor Tool đi kèm ngày tháng khác nhau tùy version model — dùng sai version
  dễ gây lỗi 400, phải tra đúng docs cho model đang dùng. Trên Claude 4.x, `name` cũng đổi theo
  (`str_replace_based_edit_tool`, không phải `str_replace_editor` của bản 3.x) — đổi `type` mà
  quên đổi `name` (hoặc ngược lại) đều bị lỗi 400. Bản 4.x cũng bỏ command `undo_edit`.
- [ ] Web Search Tool phải được **bật trong Console settings** (Privacy settings, cấp
  organization) trước khi dùng — thiếu bước này request sẽ lỗi dù code/schema đúng
- [x] `content` trong `tool_result` block nên dùng `json.dumps(tool_output)` thay vì `str(result)`
  khi tool trả về `dict`/`list` — `str()` cho ra Python repr (dấu `'` thay vì `"`) không phải JSON
  hợp lệ, Claude vẫn đọc được nhưng dễ nhầm lẫn/parse sai nếu code phía sau cố `json.loads` lại

## Code Snippets
```python
# Ép Claude luôn extract dữ liệu qua 1 tool cụ thể (structured data pattern)
response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    tools=[extract_schema],
    tool_choice={"type": "tool", "name": "extract_schema"},  # ép gọi đúng tool này
    messages=[{"role": "user", "content": prompt}],
)
structured_data = response.content[0].input  # dict đã theo đúng input_schema
```

## Questions / Unclear Points
- ?
