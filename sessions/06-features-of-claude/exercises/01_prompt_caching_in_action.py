"""
Prompt caching in action
Session: Features of Claude
Objective: Mark a large static system block with cache_control and observe
cache_creation vs. cache_read token usage across two identical calls.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test

# A cache block should be reasonably large (docs recommend 1024+ tokens for
# most models) — this toy example is short but demonstrates the mechanics.
# Nhân chuỗi lên 50 lần để đủ dài giả lập 1 system prompt lớn, ổn định, ít đổi giữa các lần gọi
LARGE_STATIC_CONTEXT = (
    "You are a support agent for a fictional product called Acme Widgets. "
    "Product policy: refunds within 30 days, no questions asked. "
) * 50


def ask(question: str):
    """Gửi 1 câu hỏi kèm system block được đánh dấu cache_control."""
    # question: str — câu hỏi cụ thể của user, phần này KHÔNG được cache (đổi mỗi lần gọi)
    return client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=[
            {
                "type": "text",
                "text": LARGE_STATIC_CONTEXT,  # phần context tĩnh, lặp lại giữa các request
                "cache_control": {"type": "ephemeral"},  # đánh dấu block này để Anthropic cache lại
            }
        ],
        messages=[{"role": "user", "content": question}],
    )


def main():
    try:
        first = ask("What's the refund policy?")
        # lần gọi đầu: chưa có cache -> tốn cache_creation_input_tokens để tạo cache
        print("Call 1 usage:", first.usage)

        second = ask("Can I get a refund after 20 days?")
        # lần gọi thứ 2: system block giống hệt lần 1 -> được phục vụ từ cache, rẻ hơn
        print("Call 2 usage:", second.usage)
        print(
            "\ncache_read_input_tokens on call 2 shows how much of the "
            "system block was served from cache instead of reprocessed."
        )
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
