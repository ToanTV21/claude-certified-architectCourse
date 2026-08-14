"""
Exercise 06: Tool function get_current_datetime (reminder app - tool 1/3)
Session: Tool Use with Claude
Objective: Viết 1 tool function chuẩn best-practice (validate input, error message rõ ràng),
    khai báo schema tương ứng bằng ToolParam, và chạy đủ luồng sending-tool-results để
    Claude tự gọi tool này khi cần biết giờ hiện tại.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env, không hardcode API key
from datetime import datetime  # dùng để lấy thời gian hiện tại của máy
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


def get_current_datetime(date_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Trả về ngày giờ hiện tại, format theo `date_format` (kiểu strftime).

    Validate input ngay đầu hàm: nếu Claude lỡ gọi với format rỗng, raise lỗi rõ ràng
    để Claude "nhìn thấy" error message qua tool_result và có thể tự retry.
    """
    # date_format: str — pattern strftime, vd "%H:%M" chỉ lấy giờ:phút
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)


# Schema đặt tên theo convention "<ten_ham>_schema"
get_current_datetime_schema = ToolParam(
    {
        "name": "get_current_datetime",  # phải khớp tên hàm Python thực thi
        "description": (
            "Get the current date and time. Use this whenever the user's request depends on "
            "knowing what time it is right now (e.g. 'remind me in 3 days', 'what time is it')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": (
                        "Python strftime format string, e.g. '%Y-%m-%d %H:%M:%S' or '%H:%M'. "
                        "Optional — defaults to '%Y-%m-%d %H:%M:%S'."
                    ),
                    "default": "%Y-%m-%d %H:%M:%S",
                }
            },
            "required": [],  # date_format có default value nên không bắt buộc
        },
    }
)


def run_tool(tool_name: str, tool_input: dict):
    """Dispatcher: map tên tool -> hàm Python thực thi tương ứng."""
    if tool_name == "get_current_datetime":
        # **tool_input unpack dict thành keyword argument cho hàm get_current_datetime
        return get_current_datetime(**tool_input)
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
            # bắt mọi lỗi (kể cả ValueError từ validate input) để báo Claude qua is_error=True
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(exc),
                    "is_error": True,
                }
            )
    return tool_result_blocks


def main():
    messages = []
    # user hỏi 1 câu cần biết giờ hiện tại -> Claude sẽ tự quyết định gọi tool
    add_user_message(messages, "What time is it right now? Just give me HH:MM.")

    try:
        response = client.messages.create(
            model=MODEL, max_tokens=512, messages=messages, tools=[get_current_datetime_schema]
        )

        # in ra từng content block để quan sát Claude phản hồi thế nào
        for block in response.content:
            if block.type == "text":
                print(f"[text] {block.text}")
            elif block.type == "tool_use":
                print(f"[tool_use] {block.name}({block.input})")

        if response.stop_reason == "tool_use":
            # append TOÀN BỘ response.content (không chỉ text) làm assistant message
            add_assistant_message(messages, response.content)

            tool_results = run_tools(response)

            # tool_result phải nằm trong 1 USER message mới, không phải assistant message
            add_user_message(messages, tool_results)

            # gọi lại API với full history để Claude sinh câu trả lời cuối cùng
            final = client.messages.create(
                model=MODEL, max_tokens=256, messages=messages, tools=[get_current_datetime_schema]
            )
            print(f"[final answer] {final.content[0].text}")
    except anthropic.APIError as exc:
        # bắt lỗi gọi API (network, rate limit, invalid request...) để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
