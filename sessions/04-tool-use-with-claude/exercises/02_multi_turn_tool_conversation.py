"""
Exercise 02: Multi-Turn Conversations with Tools
Session: Tool Use with Claude
Objective: Lặp vòng request/tool_result bằng while loop cho tới khi Claude không còn
    yêu cầu tool nữa (stop_reason != "tool_use") — dùng cho câu hỏi cần gọi NHIỀU tool
    nối tiếp nhau (weather rồi mới đến time) mà không biết trước cần bao nhiêu vòng.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env, không hardcode API key
import anthropic  # SDK chính thức để gọi Claude API
from anthropic.types import ToolParam  # wrap dict schema để bắt lỗi type sớm ở dev-time

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung cho cả file

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test


def add_user_message(messages: list, content) -> None:
    """Thêm 1 user message vào messages list.

    content có thể là str (câu hỏi thường) hoặc list block (vd list các tool_result
    block khi trả kết quả tool về cho Claude).
    """
    messages.append({"role": "user", "content": content})


def add_assistant_message(messages: list, content) -> None:
    """Thêm 1 assistant message vào messages list.

    content thường chính là response.content — list block (text + tool_use) —
    phải giữ nguyên toàn bộ, không được chỉ lấy phần text.
    """
    messages.append({"role": "assistant", "content": content})


def get_weather(city: str) -> str:
    """Fake weather lookup — stand-in cho API thời tiết thật."""
    # city: str — tên thành phố Claude truyền vào
    if not city:
        raise ValueError("city cannot be empty")
    return f"Sunny, 28C in {city}."


def get_time(city: str) -> str:
    """Fake local-time lookup — stand-in cho API múi giờ thật."""
    # city: str — tên thành phố Claude truyền vào
    if not city:
        raise ValueError("city cannot be empty")
    return f"It's 14:30 local time in {city}."


# Schema đặt tên theo convention "<ten_ham>_schema"
get_weather_schema = ToolParam(
    {
        "name": "get_weather",
        "description": "Get the current weather for a city. Use this whenever the user asks about weather conditions.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name, e.g. 'Tokyo'."}},
            "required": ["city"],
        },
    }
)

get_time_schema = ToolParam(
    {
        "name": "get_time",
        "description": "Get the current local time for a city. Use this whenever the user asks what time it is somewhere.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name, e.g. 'Tokyo'."}},
            "required": ["city"],
        },
    }
)

TOOLS = [get_weather_schema, get_time_schema]  # danh sách tool khả dụng gửi cho Claude


def run_tool(tool_name: str, tool_input: dict):
    """Dispatcher: map tên tool -> hàm Python thực thi tương ứng."""
    if tool_name == "get_weather":
        return get_weather(**tool_input)
    if tool_name == "get_time":
        return get_time(**tool_input)
    raise ValueError(f"Unknown tool: {tool_name}")


def run_tools(message) -> list:
    """Chạy tất cả tool_use block có trong 1 assistant message, trả về list tool_result block."""
    tool_result_blocks = []
    for block in message.content:
        if block.type != "tool_use":
            continue  # bỏ qua text block, chỉ xử lý tool_use block

        print(f"  -> calling tool: {block.name}({block.input})  [id={block.id}]")
        try:
            result = run_tool(block.name, block.input)
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,  # PHẢI khớp id của tool_use block gốc
                    "content": str(result),
                    "is_error": False,
                }
            )
        except Exception as exc:
            # nếu tool function raise lỗi -> vẫn trả tool_result, chỉ set is_error=True
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(exc),
                    "is_error": True,
                }
            )
    return tool_result_blocks


def run_conversation(messages: list, max_turns: int = 5) -> str:
    """Lặp vòng request -> tool_result cho tới khi Claude trả lời cuối cùng hoặc hết max_turns."""
    # messages: list[dict] — lịch sử hội thoại, được mutate (append) qua từng vòng lặp
    # max_turns: int — chặn vòng lặp vô hạn nếu Claude cứ gọi tool mãi không dừng
    for _ in range(max_turns):
        response = client.messages.create(
            model=MODEL, max_tokens=512, messages=messages, tools=TOOLS
        )

        # stop_reason != "tool_use" nghĩa là Claude đã có câu trả lời cuối cùng
        if response.stop_reason != "tool_use":
            return response.content[0].text

        # append TOÀN BỘ response.content (không chỉ text) làm assistant message
        add_assistant_message(messages, response.content)

        # chạy hết các tool_use block trong response này, gom thành list tool_result
        tool_results = run_tools(response)

        # gửi toàn bộ tool_results (có thể nhiều tool) trong 1 user message duy nhất
        add_user_message(messages, tool_results)

    return "Max turns reached without a final answer."  # tránh loop vô hạn nếu Claude không bao giờ dừng


def main():
    messages = []
    # câu hỏi cần đến 2 tool khác nhau (weather + time) để trả lời đầy đủ
    add_user_message(messages, "What's the weather and local time in Tokyo right now?")

    try:
        print(run_conversation(messages))
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
