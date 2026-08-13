"""
Exercise 09: Sending Tool Results
Session: Tool Use with Claude
Objective: Minh hoạ đúng luồng "Sending tool results" trong course — extract input từ
    tool_use block bằng response.content[i].input, unpack **kwargs để gọi hàm Python,
    đóng gói tool_result block (tool_use_id / content / is_error), và xử lý trường hợp
    Claude yêu cầu NHIỀU tool call trong cùng 1 message (vd "10+10 và 30+30 là bao nhiêu?"),
    phải khớp đúng tool_use_id cho từng tool_result tương ứng.
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


def add_numbers(a: int, b: int) -> int:
    """Tool function đơn giản: cộng 2 số nguyên.

    Dùng làm ví dụ tool "tính toán" để Claude không tự làm phép cộng bằng
    training data mà bắt buộc phải gọi tool — dễ quan sát rõ luồng tool_use.
    """
    # a, b: int — 2 số hạng Claude truyền vào qua tool_use.input
    return a + b


# Schema đặt tên theo convention "<ten_ham>_schema"
add_numbers_schema = ToolParam(
    {
        "name": "add_numbers",
        "description": (
            "Adds two integers together and returns the sum. Use this any time the "
            "user asks for the result of adding two numbers, instead of computing it yourself."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "integer", "description": "First addend."},
                "b": {"type": "integer", "description": "Second addend."},
            },
            "required": ["a", "b"],  # cả 2 field bắt buộc, Claude phải truyền đủ
        },
    }
)


def run_tool(tool_name: str, tool_input: dict):
    """Dispatcher: map tên tool -> hàm Python thực thi tương ứng.

    Bọc trong try/except ở nơi gọi (run_tools) để bắt lỗi và set is_error=True
    thay vì để chương trình crash khi hàm tool raise exception.
    """
    if tool_name == "add_numbers":
        # **tool_input unpack dict thành keyword argument cho hàm add_numbers(a, b)
        # vì hàm expect keyword argument, không nhận thẳng 1 dict
        return add_numbers(**tool_input)
    raise ValueError(f"Unknown tool: {tool_name}")


def run_tools(message) -> list:
    """Chạy TẤT CẢ tool_use block có trong 1 assistant message, trả về list tool_result block.

    Claude có thể yêu cầu nhiều tool call trong cùng 1 message (vd user hỏi 2 phép
    tính cùng lúc) -> mỗi tool_use có 1 id riêng, tool_result phải khớp đúng
    tool_use_id đó để Claude biết kết quả nào ứng với lời gọi nào.
    """
    tool_result_blocks = []
    for block in message.content:
        if block.type != "tool_use":
            continue  # bỏ qua text block, chỉ xử lý tool_use block

        print(f"  -> calling tool: {block.name}({block.input})  [id={block.id}]")
        try:
            # response.content[i].input là dict tham số Claude tự suy ra
            # unpack **block.input để gọi đúng hàm Python với keyword argument
            result = run_tool(block.name, block.input)
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,  # PHẢI khớp id của tool_use block gốc
                    "content": str(result),  # content luôn serialize thành string
                    "is_error": False,
                }
            )
        except Exception as exc:
            # nếu tool function raise lỗi -> vẫn phải trả tool_result, chỉ set is_error=True
            # để Claude biết và có thể tự điều chỉnh / báo lại cho user
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
    # Câu hỏi cố ý yêu cầu 2 phép tính -> Claude thường trả về 2 tool_use block
    # trong cùng 1 response, minh hoạ rõ việc phải khớp tool_use_id cho từng cái
    add_user_message(messages, "What's 10 + 10 and what's 30 + 30?")

    try:
        # Request đầu tiên: kèm tools để Claude biết có thể gọi add_numbers
        response = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            messages=messages,
            tools=[add_numbers_schema],
        )

        if response.stop_reason == "tool_use":
            # Bước: append TOÀN BỘ response.content (không chỉ text) làm assistant message,
            # vì lịch sử hội thoại cần đủ context về các tool_use đã yêu cầu
            add_assistant_message(messages, response.content)

            # Chạy hết các tool_use block, gom thành list tool_result block
            tool_results = run_tools(response)

            # tool_result phải nằm trong 1 USER message mới, không phải assistant message
            add_user_message(messages, tool_results)

            # Request tiếp theo: vẫn phải kèm tools schema dù không mong Claude
            # gọi tool nữa -- Claude cần schema để hiểu các tool_use trong history
            final_response = client.messages.create(
                model=MODEL,
                max_tokens=1000,
                messages=messages,
                tools=[add_numbers_schema],
            )
            final_text = next(
                (b.text for b in final_response.content if b.type == "text"), ""
            )
            print(f"\nFinal answer: {final_text}")
        else:
            # Trường hợp Claude không cần gọi tool (hiếm với prompt này)
            print(response.content[0].text)
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
