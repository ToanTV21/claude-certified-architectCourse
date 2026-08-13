# Session 06: Features of Claude

## Lessons trong section này
- [x] Extended thinking
- [x] Image support
- [x] PDF support
- [x] Citations
- [x] Prompt caching
- [x] Rules of prompt caching
- [x] Prompt caching in action
- [x] Code execution and the Files API
- [ ] Quiz on features of Claude

## Key Concepts

### 1. Extended Thinking
Extended thinking là chế độ cho Claude "giấy nháp" để suy luận (reasoning) trước khi trả lời câu
hỏi phức tạp. Khi bật, response không còn chỉ là 1 text block đơn giản, mà gồm 2 phần: 1 `thinking`
block (quá trình suy luận) + phần câu trả lời cuối cùng.

- **Lợi ích:** reasoning tốt hơn, độ chính xác cao hơn với bài khó, minh bạch (xem được luồng suy nghĩ).
- **Đánh đổi:** tốn thêm token (phải trả tiền cho thinking tokens), tăng latency, code xử lý response
  phức tạp hơn.
- **Khi nào dùng:** nguyên tắc là dựa vào **prompt evaluation**. Chạy prompt không có thinking trước,
  nếu đã tối ưu prompt mà accuracy vẫn chưa đạt yêu cầu, lúc đó mới bật thinking. Không bật thinking
  ngay từ đầu như một quy tắc mặc định.
- **Signature (cryptographic token):** mỗi thinking block có 1 signature để đảm bảo nội dung không
  bị chỉnh sửa — ngăn developer "tamper" quá trình suy luận của Claude theo hướng không an toàn.
- **Redacted thinking block:** đôi khi internal safety system của Claude flag nội dung thinking →
  trả về block đã bị redact (mã hoá). Bạn vẫn phải gửi nguyên block này lại trong các lượt hội thoại
  sau để giữ context, dù không đọc được nội dung.
- **Không tương thích với:** message prefilling, `temperature` (xem link compatibility trong docs).

**Implementation:**
```python
def chat(
    messages,
    system=None,
    temperature=1.0,
    stop_sequences=[],
    tools=None,
    thinking=False,
    thinking_budget=1024,
):
    ...
    if thinking:
        params["thinking"] = {
            "type": "enabled",
            "budget": thinking_budget,  # tối thiểu 1024 token
        }
```
- `thinking_budget`: số token tối đa dành cho suy luận, **tối thiểu 1024**.
- `max_tokens` **phải lớn hơn** `thinking_budget`.
- Gọi: `chat(messages, thinking=True)`.
- Để test redacted response: gửi 1 trigger string đặc biệt (dùng cho testing để đảm bảo app xử lý
  redacted block không bị crash).

### 2. Image Support
Claude có khả năng vision — mô tả, so sánh, đếm object, phân tích ảnh phức tạp.

**Giới hạn cần nhớ:**
- Tối đa 100 ảnh / 1 request (tính trên toàn bộ messages).
- Max 5MB / ảnh.
- Gửi 1 ảnh: max 8000px chiều rộng/cao.
- Gửi nhiều ảnh: max 2000px chiều rộng/cao (mỗi ảnh).
- Có thể gửi ảnh dạng base64 hoặc URL.
- Token cost mỗi ảnh: `tokens = (width px × height px) / 750`.

**Structure của image block:**
```python
add_user_message(messages, [
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": image_bytes,
        }
    },
    {"type": "text", "text": "What do you see in this image?"}
])
```

**Prompting techniques cho ảnh** (giống hệt kỹ thuật prompt engineering cho text — không phải kỹ
thuật riêng cho vision):
- Prompt đơn giản ("How many marbles...?") → kết quả kém chính xác.
- Cải thiện bằng: methodology từng bước (step-by-step analysis), one-shot example (cho ảnh mẫu +
  đáp án đúng để làm reference point), chia nhỏ task phức tạp thành nhiều bước.

**Ví dụ thực tế — Fire Risk Assessment:** phân tích ảnh vệ tinh để đánh giá rủi ro cháy nhà (bảo hiểm),
thay vì hỏi trực tiếp "cho điểm rủi ro cháy", breakdown prompt thành 5 bước rõ ràng: xác định vị trí
nhà, phân tích tán cây phủ lên mái, đánh giá rủi ro cháy, xác định defensible space, và cuối cùng mới
gán Fire Risk Rating (1-4). Kết quả chính xác/đáng tin hơn nhiều so với hỏi 1 câu đơn giản.

### 3. PDF Support
Claude đọc và phân tích PDF trực tiếp — cơ chế gần giống hệt xử lý ảnh, chỉ khác vài chỗ.

**So với image processing, cần đổi:**
- Đuôi file `.png` → `.pdf`
- Tên biến `image_bytes` → `file_bytes` (chỉ là convention đặt tên cho rõ)
- `"type": "image"` → `"type": "document"`
- `media_type`: `"image/png"` → `"application/pdf"`

```python
with open("earth.pdf", "rb") as f:
    file_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

add_user_message(messages, [
    {
        "type": "document",
        "source": {
            "type": "base64",
            "media_type": "application/pdf",
            "data": file_bytes,
        },
    },
    {"type": "text", "text": "Summarize the document in one sentence"},
])
```

Claude đọc được: text nội dung, ảnh/chart nhúng trong PDF, table + quan hệ dữ liệu, cấu trúc/định
dạng tài liệu — gần như 1 giải pháp "tất cả trong một" để trích xuất thông tin từ PDF.

### 4. Citations
Citations cho phép Claude trích dẫn chính xác đoạn nào trong document nguồn đã tạo ra câu trả lời —
giải quyết vấn đề minh bạch: nếu không có citations, user không biết Claude đang dựa vào document cụ
thể hay chỉ "bịa" từ training data.

**Cách bật citations** — thêm 2 field vào document block:
```python
{
    "type": "document",
    "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": file_bytes,
    },
    "title": "earth.pdf",
    "citations": {"enabled": True},
}
```
- `title`: tên đọc được của document (để hiển thị trong citation).
- `citations: {"enabled": True}`: bảo Claude track được nó lấy thông tin từ đâu.

**Cấu trúc citation trong response** (mỗi citation gồm):
| Field | Ý nghĩa |
|-------|---------|
| `cited_text` | đoạn text chính xác trong document hỗ trợ cho câu Claude vừa nói |
| `document_index` | document nào (hữu ích khi gửi nhiều document) |
| `document_title` | title đã gán cho document |
| `start_page_number` / `end_page_number` | vị trí trang bắt đầu/kết thúc đoạn cited |

**Citations với plain text** (không phải PDF): dùng `source.type = "text"`, `media_type = "text/plain"`.
Lúc này thay vì `page_number` sẽ có **character position** (vị trí ký tự) để xác định chính xác đoạn
trích.

**Dùng khi nào:** user cần verify thông tin, làm việc với tài liệu authoritative cần trace được nguồn,
tính minh bạch quan trọng, hoặc user muốn đào sâu vào context xung quanh 1 fact cụ thể.

### 5. Prompt Caching
Cơ chế tăng tốc + giảm chi phí bằng cách **tái sử dụng** phần xử lý (tokenize, tạo embedding, phân
tích context) đã làm ở request trước, thay vì bỏ đi và làm lại từ đầu mỗi lần.

- Bình thường: mỗi request Claude phải tokenize + embed + phân tích context lại từ đầu, dù nội dung
  giống hệt request trước → lãng phí compute.
- Có cache: request đầu tiên **ghi** kết quả xử lý vào cache; các request sau (nội dung giống hệt)
  **đọc** từ cache thay vì xử lý lại.

**Lợi ích:** response nhanh hơn, rẻ hơn, tối ưu tự động (request đầu ghi cache, request sau đọc cache).
**Giới hạn:** cache chỉ sống **1 giờ**; chỉ hữu ích khi gửi lặp lại **cùng 1 nội dung** với tần suất cao
(ví dụ: hỏi nhiều câu về cùng 1 document dài, hoặc chỉnh sửa lặp lại trên cùng 1 base content).

### 6. Rules of Prompt Caching
**Cache breakpoint:** caching **không tự động bật** — phải chủ động thêm 1 "cache breakpoint" vào 1
block cụ thể trong message.
- Mọi công việc xử lý **trước và bao gồm** breakpoint sẽ được cache.
- Cache chỉ được dùng ở request sau nếu nội dung **tính đến breakpoint giống hệt** (dù chỉ thêm 1 từ
  như "please" cũng làm invalidate toàn bộ cache của phần đó).

**Cú pháp:** phải dùng **dạng dài (longhand)** của text block (không dùng shorthand), vì shorthand
không có chỗ để đặt field `cache_control: {"type": "ephemeral"}`.

**Cross-message caching:** breakpoint có thể đặt ở message sau, khi đó **toàn bộ các message trước đó**
(user, assistant...) đều được gộp vào phần cache. Hữu ích để cache toàn bộ context hội thoại tính đến
1 điểm nào đó.

**Có thể cache ở đâu (không chỉ text block):**
- System prompts
- Tool definitions
- Image blocks
- Tool use / tool result blocks

System prompt và tool definitions là ứng viên tốt nhất để cache vì chúng **ít khi đổi** giữa các
request → tiết kiệm nhiều nhất.

**Thứ tự xử lý của Claude** (quan trọng để đặt breakpoint đúng chỗ):
1. Tools
2. System prompt
3. Messages

→ Có thể đặt **tối đa 4 cache breakpoint** trong 1 request (vd: 1 breakpoint ở tools, 1 breakpoint
giữa conversation history...).

**Ngưỡng tối thiểu để cache:** nội dung phải **>= 1024 token** (tính tổng tất cả message/block muốn
cache, không phải từng block riêng lẻ). Một tin nhắn ngắn kiểu "Hi there!" sẽ không đủ ngưỡng, nhưng
lặp lại 500 lần (hoặc 1 system prompt dài thật sự) thì đủ điều kiện.

### 7. Prompt Caching in Action
Ví dụ thực tế: cache 1 system prompt lớn (~6K token) hoặc tool schema phức tạp (~1.7K token cho nhiều
tool) — chỉ hữu ích khi **lặp lại đúng nội dung đó nhiều lần**.

**Cache tool schema** (thêm `cache_control` vào **tool cuối cùng** trong list, không sửa trực tiếp
tool gốc — tạo bản copy để tránh side-effect nếu sau này reorder tools):
```python
if tools:
    tools_clone = tools.copy()
    last_tool = tools_clone[-1].copy()
    last_tool["cache_control"] = {"type": "ephemeral"}
    tools_clone[-1] = last_tool
    params["tools"] = tools_clone
```

**Cache system prompt** (chuyển từ string đơn giản → structured block):
```python
if system:
    params["system"] = [
        {
            "type": "text",
            "text": system,
            "cache_control": {"type": "ephemeral"},
        }
    ]
```

**Đọc usage để kiểm tra cache hoạt động:**
- Request đầu tiên: `cache_creation_input_tokens` > 0 — Claude đang **ghi** vào cache.
- Request tiếp theo (nội dung giống hệt): `cache_read_input_tokens` > 0 — Claude **đọc** từ cache.
- Nếu nội dung thay đổi: xuất hiện `cache_creation_input_tokens` mới (ghi lại cache mới).

Cache **rất nhạy** — chỉ cần đổi 1 ký tự trong tools hoặc system prompt là invalidate toàn bộ cache
của phần đó. Nếu đổi system prompt nhưng giữ nguyên tools → sẽ thấy cache **read một phần** (tools)
và cache **write một phần** (system prompt mới) — cache hoạt động ở mức **granular** (chỉ tính tiền
cho phần thực sự thay đổi).

### 8. Code Execution and the Files API
Hai tính năng độc lập nhưng phối hợp cực tốt để giao task phức tạp cho Claude tự làm.

**Files API:** cách khác để upload file ngoài base64-encode trực tiếp trong message.
1. Upload file (ảnh, PDF, text...) qua 1 API call riêng.
2. Nhận về metadata object chứa `file_id` duy nhất.
3. Reference `file_id` đó trong các message sau, không cần gửi lại raw data.

Hữu ích khi: cần reference cùng 1 file nhiều lần, hoặc file lớn gửi kèm mỗi request sẽ rất cồng kềnh.

**Code Execution tool:** server-based tool — Claude tự chạy Python trong container Docker cô lập, bạn
không cần tự implement logic thực thi (chỉ cần khai báo tool schema).
- Chạy trong Docker container cô lập.
- **Không có network access** (không gọi được API bên ngoài).
- Claude có thể chạy code **nhiều lần** trong cùng 1 conversation.
- Kết quả được Claude đọc và diễn giải lại trong câu trả lời cuối.

**Kết hợp cả hai:** vì container không có network, Files API là cách chính để đưa data vào/ra khỏi
môi trường thực thi.

Luồng chạy điển hình:
1. Upload data file (vd CSV) qua Files API.
2. Đính kèm `container_upload` block với `file_id` trong message.
3. Yêu cầu Claude phân tích data.
4. Claude tự viết + chạy code Python để xử lý file.
5. Claude có thể tạo output (vd biểu đồ) → tải về được.

```python
file_metadata = upload('streaming.csv')

messages = []
add_user_message(
    messages,
    [
        {
            "type": "text",
            "text": "Run a detailed analysis... include at least one detailed plot."
        },
        {"type": "container_upload", "file_id": file_metadata.id},
    ],
)

chat(
    messages,
    tools=[{"type": "code_execution_20250522", "name": "code_execution"}]
)
```

**Đọc response khi Claude dùng code execution** — có nhiều loại block:
- Text blocks — phần giải thích/phân tích của Claude
- Server tool use blocks — code thực tế Claude quyết định chạy
- Code execution tool result blocks — output của lần chạy code đó

Claude có thể chạy code **nhiều vòng** trong 1 response (build up phân tích dần dần).

**Tải file Claude tạo ra:** tìm block có `type: "code_execution_output"` → chứa `file_id` của file
được tạo (vd ảnh plot) → gọi `download_file(file_id)` để tải về.

**Ứng dụng ngoài data analysis:** xử lý/biến đổi ảnh, parse/transform document, tính toán/modeling
toán học, generate report với format tuỳ chỉnh.

## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
| `thinking` | dict | disabled | `{"type": "enabled", "budget": N}` — bật extended thinking |
| `thinking.budget` | int | — | tối thiểu 1024 token; `max_tokens` phải > budget này |
| `image` content block | dict | — | `source.type` = `base64` hoặc `url`; max 100 ảnh/request |
| `document` content block | dict | — | dùng cho PDF/text; `media_type = application/pdf` hoặc `text/plain` |
| `citations` | dict | disabled | `{"enabled": True}` trong `document` block để bật trích dẫn |
| `cache_control` | dict | — | `{"type": "ephemeral"}`; đặt trên block cuối muốn cache (system, tools, message) |
| `container_upload` content block | dict | — | `{"type": "container_upload", "file_id": ...}` — đưa file vào code execution container |
| `code_execution` tool | dict | — | `{"type": "code_execution_20250522", "name": "code_execution"}` — server tool, không cần tự implement |

## Gotchas
- [ ] `thinking_budget` tối thiểu 1024 token, và `max_tokens` phải lớn hơn `thinking_budget`, nếu
      không sẽ lỗi.
- [ ] Extended thinking **không tương thích** với message prefilling và `temperature`.
- [ ] Gửi 1 ảnh: max 8000px/chiều. Gửi nhiều ảnh trong cùng request: giới hạn giảm còn max 2000px/chiều.
- [ ] Cache breakpoint phải dùng **longhand form** của text block — shorthand không hỗ trợ `cache_control`.
- [ ] Cache cực nhạy: đổi dù chỉ 1 ký tự trong nội dung tính đến breakpoint → invalidate toàn bộ cache
      phần đó, phải ghi lại từ đầu.
- [ ] Nội dung phải >= 1024 token (tổng cộng) mới đủ điều kiện được cache — message ngắn sẽ không cache.
- [ ] Cache chỉ sống 1 giờ — không phải cơ chế lưu trữ dài hạn.
- [ ] Thứ tự xử lý cố định: tools → system prompt → messages; tối đa 4 cache breakpoint / request.
- [ ] Code execution container **không có network access** — không thể gọi API ngoài, chỉ trao đổi
      data qua Files API.

## Code Snippets
```python
# Extended thinking — thêm vào params khi gọi API
if thinking:
    params["thinking"] = {
        "type": "enabled",
        "budget": thinking_budget,
    }
```

```python
# Cache breakpoint cho system prompt (longhand form bắt buộc)
params["system"] = [
    {
        "type": "text",
        "text": system,
        "cache_control": {"type": "ephemeral"},
    }
]
```

## Questions / Unclear Points
- Redacted thinking block: cần verify chính xác trigger string dùng để test trong sandbox — docs
  chỉ nói chung chung "special trigger string", chưa rõ giá trị cụ thể.
