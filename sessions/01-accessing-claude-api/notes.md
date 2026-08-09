# Session 01: Accessing Claude with the API

## Lessons trong section này
- [ ] Accessing the API
- [ ] Getting an API key
- [x] Making a request
- [x] Multi-Turn conversations
- [ ] Chat exercise
- [ ] System prompts
- [ ] System prompts exercise
- [ ] Temperature
- [ ] Course satisfaction survey
- [ ] Response streaming
- [ ] Structured data
- [ ] Structured data exercise
- [ ] Quiz on accessing Claude with the API

## Key Concepts

### Luồng request 5 bước (Five-Step Request Flow)
Mỗi lần gọi Claude API đi qua 5 bước:
1. **Request to server** — client (web/mobile app) gửi request tới server của mình (không gọi thẳng Anthropic API)
2. **Request to Anthropic API** — server dùng SDK hoặc HTTP request thuần, kèm API key, gọi Anthropic API
3. **Model processing** — Claude xử lý qua 4 giai đoạn (xem bên dưới)
4. **Response to server** — Anthropic trả response có cấu trúc về server
5. **Response to client** — server forward text đã generate về lại UI

### Vì sao luôn cần server trung gian (không gọi thẳng client-side)
- API request cần API key bí mật để authenticate
- Nếu để key trong code client-side (web/mobile) → lộ key, ai cũng lấy được và gọi API trái phép
- → Kiến trúc chuẩn: `Client app → Server của mình (giữ key) → Anthropic API`

### Request tối thiểu cần có field gì (Required Fields)
- **API Key** — định danh request với Anthropic
- **Model** — tên model (vd `claude-3-sonnet`)
- **Messages** — list chứa input text của user
- **Max Tokens** — giới hạn số token Claude được generate

### Bên trong quá trình xử lý của Claude (4 giai đoạn)
1. **Tokenization** — cắt input text thành các token nhỏ (từ, phần của từ, khoảng trắng, ký hiệu). Đơn giản hoá: coi mỗi từ ~ 1 token
2. **Embedding** — mỗi token được convert thành 1 embedding (dãy số dài, đại diện toàn bộ nghĩa có thể có của token đó). Vd "quantum" có thể mang nghĩa vật lý, cơ học lượng tử, "cực nhỏ", hoặc quantum computing
3. **Contextualization** — Claude tinh chỉnh embedding dựa vào các từ xung quanh để xác định nghĩa phù hợp nhất trong ngữ cảnh
4. **Generation** — embedding đã contextualize đi qua output layer, tính xác suất cho từ tiếp theo. Claude KHÔNG luôn chọn từ có xác suất cao nhất — có kết hợp randomness (temperature) để câu trả lời tự nhiên/đa dạng hơn. Sau khi chọn 1 từ, thêm vào sequence rồi lặp lại toàn bộ quá trình cho từ kế tiếp

### Khi nào Claude dừng generate — check 3 điều kiện sau mỗi token
- **Max tokens reached** — đã chạm giới hạn `max_tokens` chưa?
- **Natural ending** — model tự sinh ra end-of-sequence token chưa?
- **Stop sequence** — có gặp `stop_sequences` định nghĩa trước không?

### Cấu trúc Response trả về
- **Message** — text đã generate
- **Usage** — số input token + output token đã dùng
- **Stop Reason** — lý do generation kết thúc (map với 3 điều kiện dừng ở trên)

Server nhận response này rồi forward text về lại client app để hiển thị lên UI.

### Setup môi trường trước khi gọi API
- Cài package: `%pip install anthropic python-dotenv` (trong Jupyter notebook)
- Tạo file `.env` cùng thư mục, lưu `ANTHROPIC_API_KEY="your-api-key-here"` — giữ key ngoài code, tránh commit nhầm lên git → luôn thêm `.env` vào `.gitignore`
- Load env var và khởi tạo client:
  ```python
  from dotenv import load_dotenv
  load_dotenv()
  from anthropic import Anthropic
  client = Anthropic()
  model = "claude-sonnet-4-0"
  ```

### `client.messages.create()` — hàm cốt lõi để gọi request
3 param bắt buộc:
- **`model`** — tên model Claude muốn dùng
- **`max_tokens`** — giới hạn an toàn cho độ dài response, KHÔNG phải target. Claude không cố viết cho đủ tới giới hạn — nó viết những gì thấy hợp lý rồi dừng; nếu chưa viết xong mà chạm giới hạn thì bị cắt ngang
- **`messages`** — lịch sử hội thoại muốn gửi cho Claude

### Messages — cấu trúc hội thoại
Giống hội thoại trong chat app, gồm 2 loại:
- **User messages** — nội dung mình gửi cho Claude (do người viết)
- **Assistant messages** — response do Claude generate ra

Mỗi message là 1 dict gồm `role` (`"user"` hoặc `"assistant"`) và `content` (text thật sự).

### Đọc kết quả trả về
Response object chứa nhiều field, nhưng phần text generate ra nằm ở:
```python
message.content[0].text
```

### Multi-turn conversations — Claude không tự nhớ hội thoại (stateless)
Claude API **không lưu trữ** conversation history ở phía server. Mỗi request là hoàn toàn độc lập, Claude không có memory về các lần gọi trước đó.

**Vấn đề:** Hỏi "What is quantum computing?" → Claude trả lời tốt. Follow-up "Write another sentence" → Claude KHÔNG biết đang nói về chủ đề gì, vì nó không nhớ câu hỏi trước. Kết quả sẽ là 1 câu bất kỳ, không liên quan.

**Cách xử lý:** muốn Claude "nhớ" ngữ cảnh, phải tự quản lý conversation state ở phía mình:
1. Tự maintain 1 list chứa toàn bộ messages trong code
2. Mỗi lần gọi request, gửi lại **toàn bộ** message history (không chỉ message mới nhất)

**Luồng hoạt động:**
1. Gửi user message đầu tiên cho Claude
2. Lấy response của Claude, append vào messages list dưới dạng `assistant` message
3. Append câu hỏi follow-up tiếp theo dưới dạng `user` message
4. Gửi lại toàn bộ messages list (đã có đủ 3 message ở trên) cho Claude

→ Vì gửi full history, Claude "hiểu" được "Write another sentence" đang nói tiếp về quantum computing.

**Helper functions thường dùng** để đỡ phải viết lặp lại dict `{role, content}`:
```python
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

def chat(messages):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
    )
    return message.content[0].text
```

**Ví dụ dùng:**
```python
messages = []

add_user_message(messages, "Define quantum computing in one sentence")
answer = chat(messages)
add_assistant_message(messages, answer)   # lưu response của Claude vào history

add_user_message(messages, "Write another sentence")
final_answer = chat(messages)             # gửi full history → Claude hiểu ngữ cảnh
```

## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
| `api_key` | str | từ `ANTHROPIC_API_KEY` env | luôn load qua `python-dotenv`, không hardcode |
| `model` | str | — | vd `claude-haiku-4-5` (dev), `claude-sonnet-4-6` (prod) |
| `messages` | list[dict] | — | list các message `{role, content}`, KHÔNG chứa system prompt |
| `system` | str | — | top-level param riêng, không nằm trong `messages` |
| `max_tokens` | int | — | bắt buộc, giới hạn output token |
| `temperature` | float | `1.0` | không phải `0.7` — dễ nhầm với OpenAI |
| `stop_sequences` | list[str] | None | 1 trong 3 điều kiện dừng generation |

## Gotchas
- [ ] Không bao giờ gọi Anthropic API trực tiếp từ client-side code (lộ API key)
- [ ] `temperature` default là `1.0`, không phải `0.7`
- [ ] `system` là top-level param, KHÔNG phải `messages[0]["role"] = "system"`
- [ ] `system=None` sẽ gây validation error — phải bỏ hẳn field hoặc truyền string
- [ ] Khi streaming, text thật sự chỉ nằm trong `ContentBlockDelta` events, các event khác (message_start, content_block_start...) không chứa text để hiển thị
- [ ] `tool_choice` để force gọi tool cụ thể: `{"type": "tool", "name": "..."}`, không phải `{"type": "auto"}`
- [ ] `stop_reason` trong response cần được handle khác nhau tuỳ giá trị (`end_turn`, `max_tokens`, `stop_sequence`, `tool_use`)
- [ ] API là stateless — Claude không tự nhớ hội thoại, phải tự gửi lại full `messages` history mỗi request nếu muốn multi-turn

## Code Snippets
```python
from dotenv import load_dotenv
import anthropic
import os

load_dotenv()
client = anthropic.Anthropic()  # tự đọc ANTHROPIC_API_KEY từ .env

MODEL_DEV = "claude-haiku-4-5"   # dev/test: tiết kiệm cost
MODEL_MAIN = "claude-sonnet-4-6"  # prod

response = client.messages.create(
    model=MODEL_DEV,
    max_tokens=1024,
    system="You are a helpful assistant.",  # top-level, không nằm trong messages
    messages=[
        {"role": "user", "content": "Xin chào Claude!"}
    ],
)

print(response.content[0].text)
print(response.usage)       # input_tokens, output_tokens
print(response.stop_reason) # vd "end_turn"
```

## Questions / Unclear Points
- ?
