"""
Routing workflows
Session: Agents and Workflows
Objective: Classify an incoming request, then route to a category-specific prompt.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test

# Map category -> system prompt tương ứng, dùng để route request sau khi classify
ROUTES = {
    "billing": "You are a billing support agent. Be precise about numbers and dates.",
    "technical": "You are a technical support agent. Give step-by-step troubleshooting.",
    "general": "You are a general support agent. Be friendly and concise.",
}


def classify(user_message: str) -> str:
    """Gọi Claude để phân loại tin nhắn user vào 1 trong 3 category."""
    # user_message: str — nội dung gốc user gửi, cần được phân loại trước khi route
    response = client.messages.create(
        model=MODEL,
        max_tokens=10,  # chỉ cần 1 từ ngắn (billing/technical/general) nên giới hạn rất thấp
        system="Classify the user message into exactly one word: billing, technical, or general.",
        messages=[{"role": "user", "content": user_message}],
    )
    category = response.content[0].text.strip().lower()
    # fallback về "general" nếu Claude trả về giá trị lạ không nằm trong ROUTES
    return category if category in ROUTES else "general"


def handle(user_message: str) -> str:
    """Phân loại rồi gọi Claude lần 2 với system prompt phù hợp category đó."""
    # user_message: str — tin nhắn gốc của user, dùng chung cho cả bước classify và bước trả lời
    category = classify(user_message)  # bước routing: xác định category
    system = ROUTES[category]  # lấy system prompt tương ứng category đã chọn
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=system,  # persona/hướng dẫn riêng theo từng category
        messages=[{"role": "user", "content": user_message}],
    )
    return category, response.content[0].text


def main():
    # 3 tin nhắn mẫu, mỗi cái kỳ vọng rơi vào 1 category khác nhau
    messages = [
        "I was charged twice this month, can you check?",
        "My app crashes every time I open settings.",
        "What are your business hours?",
    ]
    try:
        for msg in messages:
            category, reply = handle(msg)  # route + trả lời cho từng tin nhắn
            print(f"[{category}] {msg}\n  -> {reply}\n")
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
