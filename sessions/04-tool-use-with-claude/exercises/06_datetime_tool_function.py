"""
Exercise 06: Tool function get_current_datetime (reminder app - tool 1/3)
Session: Tool Use with Claude
Objective: Viết 1 tool function chuẩn best-practice (validate input, error message rõ ràng),
khai báo schema tương ứng, và để Claude tự gọi tool này khi cần biết giờ hiện tại.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API
from datetime import datetime  # dùng để lấy thời gian hiện tại của máy

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client, tự đọc API key từ env

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test theo convention project


def get_current_datetime(date_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Trả về ngày giờ hiện tại, format theo `date_format` (kiểu strftime)."""
    # date_format: str — pattern strftime, vd "%H:%M" chỉ lấy giờ:phút
    # Validate input ngay đầu hàm: nếu Claude lỡ gọi với format rỗng, raise lỗi rõ ràng
    # để Claude "nhìn thấy" error message và có thể tự retry với tham số đã sửa
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)  # format thời gian hiện tại theo pattern


# Tool schema — mô tả cho Claude: tên tool, khi nào dùng, input cần gì
DATETIME_TOOL = {
    "name": "get_current_datetime",  # phải khớp tên hàm Python thực thi bên dưới
    "description": (
        "Get the current date and time. Use this whenever the user's request depends on "
        "knowing what time it is right now (e.g. 'remind me in 3 days', 'what time is it')."
    ),  # Claude chỉ dựa vào description này để quyết định có gọi tool hay không
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": (
                    "Python strftime format string, e.g. '%Y-%m-%d %H:%M:%S' or '%H:%M'. "
                    "Optional — defaults to '%Y-%m-%d %H:%M:%S'."
                ),
            }
        },
        "required": [],  # date_format có default value nên không bắt buộc
    },
}


def run_tool(tool_name: str, tool_input: dict) -> tuple[str, bool]:
    """Dispatcher: map tên tool -> hàm Python thực thi. Trả về (content, is_error)."""
    # tool_name: str — tên tool Claude yêu cầu gọi
    # tool_input: dict — argument Claude truyền vào, unpack bằng **tool_input
    try:
        if tool_name == "get_current_datetime":
            result = get_current_datetime(**tool_input)
            return str(result), False  # is_error=False vì chạy thành công
        raise ValueError(f"Unknown tool: {tool_name}")
    except Exception as exc:
        # bắt mọi lỗi (kể cả ValueError từ validate input) để báo cho Claude qua is_error=True
        return str(exc), True


def main():
    # user hỏi 1 câu cần biết giờ hiện tại -> Claude sẽ tự quyết định gọi tool
    messages = [{"role": "user", "content": "What time is it right now? Just give me HH:MM."}]

    try:
        response = client.messages.create(
            model=MODEL, max_tokens=512, tools=[DATETIME_TOOL], messages=messages
        )

        # in ra từng content block để quan sát Claude phản hồi thế nào
        for block in response.content:
            if block.type == "text":
                print(f"[text] {block.text}")
            elif block.type == "tool_use":
                print(f"[tool_use] {block.name}({block.input})")

        # nếu Claude muốn gọi tool trước khi trả lời -> thực thi rồi gửi kết quả lại
        if response.stop_reason == "tool_use":
            tool_block = next(b for b in response.content if b.type == "tool_use")
            content, is_error = run_tool(tool_block.name, tool_block.input)

            # phải append nguyên response.content (chứa tool_use block) vào lịch sử
            messages.append({"role": "assistant", "content": response.content})
            # gửi tool_result trong 1 user message mới, tool_use_id phải khớp id gốc
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_block.id,
                            "content": content,
                            "is_error": is_error,  # báo Claude biết tool chạy lỗi hay không
                        }
                    ],
                }
            )

            # gọi lại API với full history để Claude sinh câu trả lời cuối cùng
            final = client.messages.create(
                model=MODEL, max_tokens=256, tools=[DATETIME_TOOL], messages=messages
            )
            print(f"[final answer] {final.content[0].text}")
    except anthropic.APIError as exc:
        # bắt lỗi gọi API (network, rate limit, invalid request...) để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
