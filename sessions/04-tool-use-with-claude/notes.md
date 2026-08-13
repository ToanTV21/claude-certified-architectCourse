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
- [ ] Fine grained tool calling
- [ ] The text edit tool
- [ ] The web search tool
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

Field quan trọng: **`stop_reason`** trên response — nếu `stop_reason == "tool_use"` nghĩa là
Claude còn muốn gọi tool, ngược lại thì đó là câu trả lời cuối cùng.

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

## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
| `tools` | `list[dict]` (create()) | không truyền | Khai báo danh sách tool khả dụng cho Claude |
| `tool_choice` | `dict` (create()) | `{"type": "auto"}` | `{"type": "tool", "name": "..."}` ép Claude luôn gọi đúng 1 tool cụ thể |
| `stop_reason` | `str` (response field) | — | `"tool_use"` = Claude còn muốn gọi tool, cần lặp tiếp |
| `tool_use_id` | `str` (trong tool_use / tool_result block) | — | Khóa nối kết quả tool với đúng lời gọi tool tương ứng |
| `is_error` | `bool` (trong tool_result block) | `false` | Báo Claude biết tool chạy lỗi để nó tự điều chỉnh/retry |
| `ToolParam` | class (`anthropic.types`) | — | Wrap dict schema để có type-check khi code |

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
- [ ] Khi dùng `tool_choice` ép buộc để lấy structured data, **không cần** gửi `tool_result` quay
  lại — khác với luồng tool use thông thường

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
