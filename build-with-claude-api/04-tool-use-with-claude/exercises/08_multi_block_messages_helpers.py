"""
Exercise 08: Multi-block messages + updated add_user_message/add_assistant_message
Session: Tool Use with Claude
Objective: Cập nhật helper functions để nhận cả string lẫn list block (tool_use/tool_result),
    rồi chạy đúng luồng 5 bước tool use, in ra từng block để thấy rõ cấu trúc multi-block.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
from datetime import datetime  # dùng để lấy giờ hiện tại cho tool function
import anthropic  # SDK chính thức để gọi Claude API
from anthropic.types import ToolParam  # wrap dict schema để bắt lỗi type sớm ở dev-time

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test


def add_user_message(messages: list, content) -> None:
    """Thêm 1 user message vào messages list.

    content có thể là str (message text thường) hoặc list block (vd list chứa
    1 tool_result block) — khác với bản ở session 01 chỉ nhận str.
    """
    messages.append({"role": "user", "content": content})


def add_assistant_message(messages: list, content) -> None:
    """Thêm 1 assistant message vào messages list.

    content có thể là str, hoặc response.content (list block gồm text + tool_use)
    khi Claude vừa trả lời vừa muốn gọi tool — phải giữ nguyên list, không được
    chỉ lấy phần text ra rồi bỏ mất tool_use block.
    """
    messages.append({"role": "assistant", "content": content})


def get_current_datetime(date_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Tool function: trả về giờ hiện tại đã format theo date_format."""
    # date_format: str — format code kiểu strftime
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)


# Schema đặt tên theo convention "<ten_ham>_schema"
get_current_datetime_schema = ToolParam(
    {
        "name": "get_current_datetime",
        "description": (
            "Returns the current date and time formatted according to the specified format. "
            "Use this whenever the user asks what time or date it is right now. "
            "Returns a single formatted date/time string."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": "strftime format code, e.g. '%H:%M:%S'.",
                    "default": "%Y-%m-%d %H:%M:%S",
                }
            },
            "required": [],
        },
    }
)


def print_content_blocks(content, label: str) -> None:
    """In ra từng block trong 1 content list — minh hoạ rõ cấu trúc multi-block."""
    # content: list các block (text/tool_use/tool_result) — không phải string đơn
    print(f"--- {label} ({len(content)} block(s)) ---")
    for block in content:
        block_type = block.type if hasattr(block, "type") else block.get("type")
        if block_type == "text":
            text = block.text if hasattr(block, "text") else block.get("text")
            print(f"  [text] {text}")
        elif block_type == "tool_use":
            name = block.name if hasattr(block, "name") else block.get("name")
            tool_input = block.input if hasattr(block, "input") else block.get("input")
            print(f"  [tool_use] {name}({tool_input})")
        elif block_type == "tool_result":
            print(f"  [tool_result] {block.get('content')}")


def main():
    messages = []
    # Bước 1: gửi user message + khai báo tools cho Claude
    add_user_message(messages, "What is the exact time, formatted as HH:MM:SS?")

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            messages=messages,
            tools=[get_current_datetime_schema],
        )

        # Bước 2: nhận assistant message multi-block (text block + tool_use block)
        print_content_blocks(response.content, "assistant response")

        if response.stop_reason == "tool_use":
            # Bước 3: đọc tool_use block, thực thi hàm Python tương ứng
            tool_block = next(b for b in response.content if b.type == "tool_use")
            result = get_current_datetime(**tool_block.input)
            print(f"Tool executed → {result}")

            # Bước 4: append toàn bộ response.content (không chỉ text) làm assistant message,
            # rồi gửi tool_result làm user message mới
            add_assistant_message(messages, response.content)
            add_user_message(
                messages,
                [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,  # khớp id với tool_use block gốc
                        "content": result,
                    }
                ],
            )

            # Bước 5: gọi lại API với full history để Claude trả lời cuối cùng
            final = client.messages.create(
                model=MODEL,
                max_tokens=256,
                messages=messages,
                tools=[get_current_datetime_schema],
            )
            print_content_blocks(final.content, "final response")
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
