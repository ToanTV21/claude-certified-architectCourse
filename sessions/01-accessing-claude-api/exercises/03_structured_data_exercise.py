"""
Structured data exercise
Session: Accessing Claude with the API
Objective: Ask Claude to return structured JSON output and parse it.
"""

import json  # để parse chuỗi JSON Claude trả về thành dict Python
from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test


def main():
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=512,  # giới hạn output vì response JSON ngắn, không cần nhiều token
            # system prompt ép Claude CHỈ trả JSON thuần, không kèm giải thích/markdown
            system=(
                "You extract structured data from text. "
                "Always respond with ONLY valid JSON, no other text."
            ),
            messages=[
                {
                    "role": "user",
                    # yêu cầu cụ thể: extract 3 field name/age/city từ 1 câu văn bản thô
                    "content": (
                        "Extract name, age, and city as JSON from: "
                        "'Toan is 30 years old and lives in Tokyo.'"
                    ),
                }
            ],
        )
        raw = response.content[0].text  # text thô Claude trả về, kỳ vọng là 1 JSON string
        data = json.loads(raw)  # parse JSON string -> dict Python
        print(data)
    except json.JSONDecodeError:
        # Claude đôi khi trả JSON không hợp lệ (thiếu dấu ngoặc, kèm text thừa...)
        print(f"Failed to parse JSON, raw output was:\n{raw}")
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
