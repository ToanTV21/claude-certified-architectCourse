"""
Exercise 07: JSON Schema cho tool calling — get_current_datetime + ToolParam
Session: Tool Use with Claude
Objective: Viết 1 tool schema chuẩn (name/description/input_schema) theo convention
    <function_name>_schema, dùng ToolParam để type-check, và chạy đủ luồng
    sending-tool-results (run_tool dispatcher + tool_result block) end-to-end.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env, không hardcode API key
from datetime import datetime  # dùng để lấy giờ hiện tại
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
    """Tool function: trả về giờ hiện tại đã format theo date_format."""
    # date_format: str — format code kiểu strftime, vd "%Y-%m-%d %H:%M:%S" hoặc "%H:%M"
    if not date_format:
        # validate ngay đầu hàm — raise lỗi rõ ràng vì Claude nhìn thấy được message này
        # và có thể tự sửa tham số rồi gọi lại tool
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)


# Schema đặt tên theo convention "<ten_ham>_schema" để dễ đối chiếu với hàm gốc.
# ToolParam chỉ bọc type ở dev-time, không đổi cấu trúc dict lúc runtime.
get_current_datetime_schema = ToolParam(
    {
        "name": "get_current_datetime",  # phải khớp chính xác tên hàm Python thực thi
        "description": (
            "Returns the current date and time formatted according to the specified format. "
            "Use this whenever the conversation needs to know the current date/time, for example "
            "to compute a reminder time relative to 'now'. Returns a single formatted date/time string."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": "A strftime format code, e.g. '%Y-%m-%d %H:%M:%S' or '%H:%M'.",
                    "default": "%Y-%m-%d %H:%M:%S",
                }
            },
            "required": [],  # không field nào bắt buộc — có default value
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
    # câu hỏi user cố tình yêu cầu format giờ dạng "HH:MM" để Claude phải truyền date_format
    add_user_message(messages, "What time is it right now? Just give me HH:MM.")

    try:
        response = client.messages.create(
            model=MODEL, max_tokens=512, messages=messages, tools=[get_current_datetime_schema]
        )

        print(f"Claude stop reason: {response.stop_reason}")

        # duyệt content blocks — có thể có cả text lẫn tool_use trong cùng 1 response
        for block in response.content:
            if block.type == "text":
                print(f"[text block] {block.text}")
            elif block.type == "tool_use":
                print(f"[tool_use block] {block.name}({block.input})")

        if response.stop_reason == "tool_use":
            # append TOÀN BỘ response.content (không chỉ text) làm assistant message
            add_assistant_message(messages, response.content)

            tool_results = run_tools(response)

            # tool_result phải nằm trong 1 USER message mới, không phải assistant message
            add_user_message(messages, tool_results)

            # gọi lại API lần 2 với full history để Claude trả lời cuối cùng cho user
            final = client.messages.create(
                model=MODEL, max_tokens=256, messages=messages, tools=[get_current_datetime_schema]
            )
            print(f"Final response: {final.content[0].text}")
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
