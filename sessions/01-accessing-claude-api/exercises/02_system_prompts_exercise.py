"""
System prompts exercise
Session: Accessing Claude with the API
Objective: Compare responses with and without a system prompt.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test
QUESTION = "How do I center a div?"  # câu hỏi cố định để so sánh có/không system prompt


def ask(system: str | None = None) -> str:
    """Gọi Claude với QUESTION cố định, có thể kèm hoặc không kèm system prompt."""
    # system: str | None — nếu truyền vào, sẽ set persona/hướng dẫn hành vi cho Claude
    #   (system là top-level param, KHÔNG nhét vào messages)
    kwargs = {"model": MODEL, "max_tokens": 256, "messages": [{"role": "user", "content": QUESTION}]}
    if system:
        kwargs["system"] = system  # chỉ thêm field system khi có giá trị, tránh system=None (validation error)
    response = client.messages.create(**kwargs)
    return response.content[0].text  # lấy text từ content block đầu tiên


def main():
    try:
        print("-- No system prompt --")
        print(ask())  # gọi không có system -> Claude trả lời theo giọng mặc định

        print("\n-- With system prompt (sarcastic senior dev) --")
        # gọi có system -> ép Claude theo persona + giới hạn độ dài câu trả lời
        print(ask(system="You are a sarcastic senior frontend developer. Keep answers under 3 sentences."))
    except anthropic.APIError as exc:
        # bắt lỗi API để in ra thay vì crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
