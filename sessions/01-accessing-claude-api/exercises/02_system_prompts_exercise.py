"""
Exercise 01-02: System prompts
Module: Accessing Claude with the API
Objective: So sánh câu trả lời của Claude khi có và không có system prompt,
           đồng thời viết một hàm chat() tái sử dụng được, nhận system prompt
           như một tham số tùy chọn.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client, tự đọc API key từ env

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test
QUESTION = "How do I solve 5x + 2 = 3 for x?"  # câu hỏi cố định để so sánh có/không system prompt

# system prompt của một "math tutor" kiên nhẫn: không đưa đáp án trực tiếp,
# mà dẫn dắt học sinh từng bước để tự tìm ra lời giải
MATH_TUTOR_SYSTEM = """
You are a patient math tutor.
Do not directly answer a student's questions.
Guide them to a solution step by step.
"""


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


def main():
    messages = [{"role": "user", "content": QUESTION}]

    try:
        print("-- Không có system prompt --")
        # gọi không có system -> Claude trả lời theo giọng mặc định,
        # thường sẽ giải trực tiếp toàn bộ bài toán ngay lập tức
        print(chat(messages))

        print("\n-- Có system prompt (math tutor) --")
        # gọi có system -> Claude đóng vai gia sư, chỉ gợi ý từng bước
        # thay vì đưa đáp án hoàn chỉnh ngay
        print(chat(messages, system=MATH_TUTOR_SYSTEM))
    except anthropic.APIError as exc:
        # bắt lỗi API để in ra thay vì crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
