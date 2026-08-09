"""
Exercise 01-03: Structured data
Module: Accessing Claude with the API
Objective: Dùng kỹ thuật "assistant message prefilling + stop sequences" để
           bắt Claude trả về JSON thuần, không kèm markdown code block hay
           câu giải thích thừa -> dễ parse/copy trực tiếp trong app thực tế.
"""

import json  # để parse chuỗi JSON Claude trả về thành dict Python
from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client, tự đọc API key từ env

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test


def add_user_message(messages: list, text: str) -> None:
    """Thêm 1 user message vào messages list (giữ style đồng nhất với các bài trước)."""
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages: list, text: str) -> None:
    """Thêm 1 assistant message vào messages list.

    Dùng để "prefill" — giả vờ Claude đã bắt đầu trả lời bằng đoạn text cho
    trước (vd "```json"), khiến Claude nghĩ nó đang viết tiếp câu đã dở dang
    thay vì bắt đầu 1 response mới từ đầu.
    """
    messages.append({"role": "assistant", "content": text})


def chat(messages: list, stop_sequences: list[str] | None = None) -> str:
    """Gọi Claude, có thể kèm stop_sequences để cắt generation ngay khi gặp
    chuỗi ký tự chỉ định (vd cắt ngay khi Claude bắt đầu gõ dấu đóng ```).
    """
    params = {
        "model": MODEL,
        "max_tokens": 512,  # response JSON ngắn, không cần nhiều token
        "messages": messages,
    }

    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    message = client.messages.create(**params)
    return message.content[0].text


def extract_json_no_prefill(text: str) -> str:
    """Cách mặc định (KHÔNG dùng kỹ thuật prefill) — chỉ yêu cầu suông trong
    prompt. Claude thường vẫn bọc JSON trong ```json ... ``` kèm câu giải
    thích phía sau -> không thể json.loads() thẳng, phải tự xử lý thêm.
    """
    messages = []
    add_user_message(messages, text)
    return chat(messages)


def extract_json_with_prefill(text: str) -> str:
    """Kỹ thuật chính của bài học: prefill + stop_sequences.

    1. User message: yêu cầu Claude generate JSON như bình thường
    2. Assistant message được prefill sẵn "```json" -> Claude nghĩ nó đã tự
       mở code block markdown rồi, nên sẽ viết tiếp phần nội dung JSON
    3. stop_sequences=["```"] -> ngay khi Claude định gõ dấu đóng code block,
       generation dừng lại ngay lập tức

    Kết quả: response trả về CHỈ chứa JSON thuần, không có ``` ở đầu/cuối,
    không có câu giải thích kèm theo -> parse thẳng bằng json.loads() được.
    """
    messages = []
    add_user_message(messages, text)
    add_assistant_message(messages, "```json")  # prefill: giả vờ đã mở code block

    raw = chat(messages, stop_sequences=["```"])

    # Claude có thể để lại vài ký tự newline thừa ở đầu/cuối -> strip() cho sạch
    return raw.strip()


def main():
    source_text = (
        "Extract name, age, and city as JSON from: "
        "'Toan is 30 years old and lives in Tokyo.'"
    )

    try:
        print("-- KHÔNG dùng prefill (cách mặc định) --")
        raw_default = extract_json_no_prefill(source_text)
        print(f"Raw response:\n{raw_default}\n")
        # ở đây thường sẽ FAIL vì raw_default còn kèm ```json ... ``` + text giải thích
        try:
            data_default = json.loads(raw_default)
            print(f"Parsed OK: {data_default}")
        except json.JSONDecodeError:
            print("-> json.loads() thất bại vì response không phải JSON thuần.\n")

        print("-- CÓ prefill + stop_sequences (kỹ thuật của bài học) --")
        raw_clean = extract_json_with_prefill(source_text)
        print(f"Raw response:\n{raw_clean}\n")
        data_clean = json.loads(raw_clean)  # parse thẳng, không cần xử lý gì thêm
        print(f"Parsed OK: {data_clean}")

    except anthropic.APIError as exc:
        # bắt lỗi API để in ra thay vì crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
