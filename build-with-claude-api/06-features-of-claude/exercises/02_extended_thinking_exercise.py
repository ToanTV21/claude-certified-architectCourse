"""
Exercise 02: Extended thinking
Session: Features of Claude
Objective: Bật extended thinking cho 1 câu hỏi lập luận phức tạp, tách riêng
thinking block và text block cuối cùng trong response để hiển thị cho user.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung

# Dev: dùng haiku để tiết kiệm cost khi code/test
MODEL = "claude-haiku-4-5"

# Extended thinking chỉ hữu ích thật sự với model hỗ trợ + bài toán khó (reasoning nhiều bước).
THINKING_BUDGET = 1024  # số token tối đa Claude được dùng để "suy nghĩ" -- tối thiểu bắt buộc là 1024
MAX_TOKENS = 2000  # PHẢI lớn hơn THINKING_BUDGET, vì max_tokens tính luôn cả phần thinking + câu trả lời


def ask_with_thinking(question: str):
    """Gửi 1 câu hỏi với extended thinking được bật."""
    # question: str -- câu hỏi lập luận (reasoning) cần Claude "suy nghĩ" trước khi trả lời
    return client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        thinking={
            "type": "enabled",  # bật chế độ extended thinking
            "budget_tokens": THINKING_BUDGET,  # giới hạn số token dành cho reasoning
        },
        messages=[{"role": "user", "content": question}],
        # Lưu ý: extended thinking KHÔNG tương thích với `temperature` và message prefilling,
        # nên không truyền temperature ở đây.
    )


def print_response(response) -> None:
    """Tách riêng thinking block và text block cuối cùng để in ra rõ ràng."""
    for block in response.content:
        # block.type có thể là "thinking", "redacted_thinking", hoặc "text"
        if block.type == "thinking":
            print("--- THINKING (scratch paper của Claude) ---")
            print(block.thinking)
            print()
        elif block.type == "redacted_thinking":
            # nội dung thinking đã bị hệ thống an toàn redact -- không đọc được, chỉ giữ lại
            # để gửi kèm trong các lượt hội thoại sau, tránh mất context
            print("--- THINKING BỊ REDACTED (không đọc được nội dung) ---\n")
        elif block.type == "text":
            print("--- CÂU TRẢ LỜI CUỐI CÙNG ---")
            print(block.text)


def main():
    question = (
        "A farmer has 17 sheep. All but 9 die. How many sheep does the farmer "
        "have left? Explain your reasoning step by step."
    )
    try:
        response = ask_with_thinking(question)
        print_response(response)
        # usage cho biết chi phí thực tế -- thinking tokens cũng được tính vào output tokens
        print("\nUsage:", response.usage)
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình, in lỗi rõ ràng ra màn hình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
