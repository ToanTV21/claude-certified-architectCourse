"""
Exercise 07: JSON Schema cho tool calling — get_current_datetime + ToolParam
Session: Tool Use with Claude
Objective: Viết 1 tool schema chuẩn (name/description/input_schema) theo convention
    <function_name>_schema, dùng ToolParam để type-check, và gọi thử end-to-end.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
from datetime import datetime  # dùng để lấy giờ hiện tại
import anthropic  # SDK chính thức để gọi Claude API
from anthropic.types import ToolParam  # wrap dict schema để bắt lỗi type sớm ở dev-time

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test


def get_current_datetime(date_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Tool function: trả về giờ hiện tại đã format theo date_format."""
    # date_format: str — format code kiểu strftime, vd "%Y-%m-%d %H:%M:%S" hoặc "%H:%M"
    if not date_format:
        # validate ngay đầu hàm — raise lỗi rõ ràng vì Claude nhìn thấy được message này
        # và có thể tự sửa tham số rồi gọi lại tool
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)


# Tool schema — đặt tên theo convention "<ten_ham>_schema" để dễ đối chiếu với hàm gốc.
# ToolParam chỉ bọc type ở dev-time, không đổi cấu trúc dict lúc runtime.
get_current_datetime_schema = ToolParam(
    {
        "name": "get_current_datetime",  # phải khớp chính xác tên hàm Python thực thi
        "description": (
            "Returns the current date and time formatted according to the specified format. "
            "Use this whenever the conversation needs to know the current date/time, for example "
            "to compute a reminder time relative to 'now'. Returns a single formatted date/time string."
        ),
        "input_schema": {  # JSON Schema mô tả argument của hàm
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


def main():
    # câu hỏi user cố tình yêu cầu format giờ dạng "HH:MM" để Claude phải truyền date_format
    messages = [{"role": "user", "content": "What time is it right now? Just give me HH:MM."}]

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=512,
            tools=[get_current_datetime_schema],  # khai báo tool cho Claude biết
            messages=messages,
        )

        print(f"Claude stop reason: {response.stop_reason}")

        # duyệt content blocks — có thể có cả text lẫn tool_use trong cùng 1 response
        for block in response.content:
            if block.type == "text":
                print(f"[text block] {block.text}")
            elif block.type == "tool_use":
                print(f"[tool_use block] {block.name}({block.input})")

        if response.stop_reason == "tool_use":
            # lấy block tool_use đầu tiên để biết Claude muốn gọi tool nào với argument gì
            tool_block = next(b for b in response.content if b.type == "tool_use")
            result = get_current_datetime(**tool_block.input)  # thực thi tool thật ở phía mình
            print(f"Tool executed → {result}")

            # append toàn bộ response.content (không chỉ text) làm assistant message
            messages.append({"role": "assistant", "content": response.content})
            # gửi kết quả tool lại dưới dạng user message chứa tool_result block
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_block.id,  # phải khớp id của tool_use tương ứng
                            "content": result,
                        }
                    ],
                }
            )

            # gọi lại API lần 2 với full history để Claude trả lời cuối cùng cho user
            final = client.messages.create(
                model=MODEL,
                max_tokens=256,
                tools=[get_current_datetime_schema],
                messages=messages,
            )
            print(f"Final response: {final.content[0].text}")
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
