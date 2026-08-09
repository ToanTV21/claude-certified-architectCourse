"""
Implementing multiple turns / multi-turn conversations with tools
Session: Tool Use with Claude
Objective: Loop the request/tool-result cycle until Claude stops asking for tools.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test


def get_weather(city: str) -> str:
    """Fake weather lookup — stand-in cho API thời tiết thật."""
    # city: str — tên thành phố Claude truyền vào
    return f"Sunny, 28C in {city}."


def get_time(city: str) -> str:
    """Fake local-time lookup — stand-in cho API múi giờ thật."""
    # city: str — tên thành phố Claude truyền vào
    return f"It's 14:30 local time in {city}."


# Danh sách tool schema — mô tả cho Claude biết có 2 tool nào, mỗi tool cần input gì
TOOLS = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
    {
        "name": "get_time",
        "description": "Get current local time for a city.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
]

# Map tên tool -> hàm Python thực thi tương ứng, dùng để dispatch động theo block.name
TOOL_FUNCTIONS = {"get_weather": get_weather, "get_time": get_time}


def run_conversation(messages: list, max_turns: int = 5):
    """Lặp vòng request -> tool_result cho tới khi Claude trả lời cuối cùng hoặc hết max_turns."""
    # messages: list[dict] — lịch sử hội thoại, sẽ được mutate (append) qua từng vòng lặp
    # max_turns: int — chặn vòng lặp vô hạn nếu Claude cứ gọi tool mãi không dừng
    for _ in range(max_turns):
        response = client.messages.create(
            model=MODEL, max_tokens=512, tools=TOOLS, messages=messages
        )

        # nếu Claude không cần gọi tool nữa -> đây là câu trả lời cuối cùng, thoát vòng lặp
        if response.stop_reason != "tool_use":
            return response.content[0].text

        # lưu lại response (chứa các tool_use block) vào history dưới dạng assistant message
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []  # gom kết quả của TẤT CẢ tool_use block trong response này
        for block in response.content:
            if block.type == "tool_use":
                fn = TOOL_FUNCTIONS[block.name]  # tra hàm Python tương ứng theo tên tool
                result = fn(**block.input)  # gọi hàm thật với input Claude yêu cầu
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )

        # gửi toàn bộ tool_results (có thể nhiều tool) trong 1 user message duy nhất
        messages.append({"role": "user", "content": tool_results})

    return "Max turns reached without a final answer."  # tránh loop vô hạn nếu Claude không bao giờ dừng


def main():
    messages = [
        {
            "role": "user",
            # câu hỏi cần đến 2 tool khác nhau (weather + time) để trả lời đầy đủ
            "content": "What's the weather and local time in Tokyo right now?",
        }
    ]
    try:
        print(run_conversation(messages))
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
