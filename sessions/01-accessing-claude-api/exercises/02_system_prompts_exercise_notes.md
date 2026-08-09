# Giải thích code: 02_system_prompts_exercise.py

Đi kèm với [02_system_prompts_exercise.py](02_system_prompts_exercise.py) — giải thích cẩn thận
từng đoạn code trong hàm `chat()`, dành cho người mới đọc lại Python cú pháp mới (type hints,
dict unpacking...).

## Hàm `chat()`

```python
def chat(messages: list, system: str | None = None) -> str:
    """Gọi Claude với danh sách messages, có thể kèm hoặc không kèm system prompt.

    messages: list[dict] — lịch sử hội thoại, mỗi phần tử {"role": ..., "content": ...}
    system: str | None — nếu truyền vào, sẽ set persona/hướng dẫn hành vi cho Claude
      (system là top-level param của API, KHÔNG nhét vào messages)
    """
    params = {
        "model": MODEL,
        "max_tokens": 1000,
        "messages": messages,
    }

    # API không chấp nhận system=None -> chỉ thêm field system khi thực sự có giá trị
    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text  # lấy text từ content block đầu tiên
```

### 1. Dòng khai báo hàm

```python
def chat(messages: list, system: str | None = None) -> str:
```

- `def chat(...)`: khai báo một hàm tên `chat`.
- `messages: list`: tham số bắt buộc, kiểu `list` (một danh sách). Đây là **type hint** — chỉ để
  người đọc/IDE biết kiểu dữ liệu mong đợi, Python không ép buộc kiểu này lúc chạy.
- `system: str | None = None`:
  - `system` là tham số **tùy chọn** (optional) vì có giá trị mặc định `= None`.
  - `str | None` nghĩa là kiểu dữ liệu của `system` có thể là `str` (chuỗi) **hoặc** `None`. Đây là
    cú pháp "Union type" của Python 3.10+ (thay cho cách viết cũ `Optional[str]`).
  - Nếu gọi `chat(messages)` mà không truyền `system`, nó sẽ tự nhận giá trị `None`.
- `-> str`: type hint cho biết hàm này **trả về** một chuỗi `str`.

→ Tóm lại: hàm nhận vào 1 list bắt buộc, và 1 chuỗi tùy chọn, trả về 1 chuỗi.

### 2. Docstring

```python
"""Gọi Claude với danh sách messages, có thể kèm hoặc không kèm system prompt.
...
"""
```

Đây là chuỗi mô tả nằm ngay sau `def`, gọi là **docstring** — giải thích hàm làm gì, không phải
code chạy thật sự. Dùng để người khác (hoặc chính mình sau này) đọc hiểu nhanh mà không cần đọc
hết logic bên trong.

### 3. Tạo dict `params`

```python
params = {
    "model": MODEL,
    "max_tokens": 1000,
    "messages": messages,
}
```

- Tạo một **dictionary** (kiểu dữ liệu key-value, giống object trong JS hoặc Map) tên `params`.
- 3 field bắt buộc của Claude API: `model`, `max_tokens`, `messages`.
- `"messages": messages` — key là chuỗi `"messages"`, value là biến `messages` (tham số truyền
  vào hàm). Tên trùng nhau nhưng bản chất là gán giá trị tham số vào key của dict.

### 4. Điều kiện thêm `system`

```python
if system:
    params["system"] = system
```

- `if system:` — kiểm tra `system` có phải giá trị "truthy" không. Trong Python, `None` và chuỗi
  rỗng `""` đều được coi là **falsy** (tương đương `False`); bất kỳ chuỗi khác rỗng nào đều là
  **truthy**.
  - Nếu `system = None` → điều kiện `False` → bỏ qua, không thêm gì vào `params`.
  - Nếu `system = "You are a math tutor..."` → điều kiện `True` → chạy dòng bên dưới.
- `params["system"] = system` — thêm key mới `"system"` vào dict `params`, với value là chuỗi
  system prompt.

**Vì sao phải làm vậy?** Vì Claude API không cho phép gửi `system=None` (sẽ báo lỗi validation).
Nên thay vì luôn gửi field `system` (có thể là `None`), code chỉ gửi field đó **khi thực sự có
giá trị**.

### 5. Gọi API bằng `**params`

```python
message = client.messages.create(**params)
```

- `client.messages.create(...)` là hàm thật sự gọi tới Claude API.
- `**params` là cú pháp **unpacking dictionary** — "bung" tất cả key-value trong `params` ra
  thành các keyword argument riêng lẻ.

Ví dụ nếu `params = {"model": "claude-haiku-4-5", "max_tokens": 1000, "messages": [...]}`, thì:

```python
client.messages.create(**params)
```

tương đương với viết tay:

```python
client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=1000,
    messages=[...]
)
```

→ Lợi ích: không cần viết `if system: ... else: ...` để gọi 2 kiểu khác nhau (có/không có
`system`). Chỉ cần build dict linh hoạt rồi unpack 1 lần.

### 6. Trả kết quả

```python
return message.content[0].text
```

- `message` là object trả về từ API, có field `content` là một **list** các "content block" (vì
  Claude có thể trả về nhiều khối nội dung khác nhau, ví dụ text, tool_use...).
- `message.content[0]` — lấy content block **đầu tiên** trong list đó (`[0]` là index đầu tiên,
  Python đếm từ 0).
- `.text` — lấy thuộc tính `text` (chuỗi nội dung thật sự) của content block đó.
- `return ...` — trả chuỗi text này ra ngoài làm kết quả của hàm `chat()`.

## Tóm tắt luồng chạy

1. Build dict tham số cơ bản (`model`, `max_tokens`, `messages`).
2. Nếu có `system` thì thêm vào dict.
3. Unpack dict (`**params`) để gọi API.
4. Lấy text từ response trả về.
