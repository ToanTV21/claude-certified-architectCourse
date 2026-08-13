"""
Exercise 10: Multi-Turn Conversation Loop (refactored chat() helper)
Session: Tool Use with Claude
Objective: Refactor helper functions theo course — add_user_message nhận cả plain
    content lẫn full Message object (dùng isinstance check), chat() nhận list tools
    và trả về full Message object thay vì chỉ text, text_from_message() để tách text
    ra khi cần hiển thị cho user. Sau đó dùng run_conversation() (while loop) để giải
    quyết câu hỏi "103 ngày nữa kể từ hôm nay là ngày nào?" -- Claude cần gọi
    get_current_datetime trước, rồi add_duration_to_datetime, mới trả lời được.
"""

import sys  # ép stdout in UTF-8, tránh lỗi UnicodeEncodeError trên terminal Windows (cp1252)
from datetime import datetime, timedelta  # dùng để implement 2 tool function thật (không mock)
from dotenv import load_dotenv  # load biến môi trường từ file .env, không hardcode API key
import anthropic  # SDK chính thức để gọi Claude API
from anthropic.types import Message, ToolParam  # Message: type để check isinstance; ToolParam: wrap schema

sys.stdout.reconfigure(encoding="utf-8")  # cho phép print() tiếng Việt có dấu an toàn

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung cho cả file

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test


# ---------------------------------------------------------------------------
# Helper functions (refactor theo course — thay vì chỉ nhận string như session 01)
# ---------------------------------------------------------------------------

def add_user_message(messages: list, message) -> None:
    """Thêm 1 user message vào messages list.

    `message` có thể là:
    - str: câu hỏi thường
    - list block: vd list các tool_result block
    - Message: full response object trả về từ client.messages.create() -- khi đó
      lấy `.content` ra để dùng làm content của user message
    """
    # isinstance check: nếu message là 1 Message object (SDK trả về) thì lấy .content,
    # còn lại (str hoặc list block) thì giữ nguyên -- giống overload method trong Java
    # (1 method nhận nhiều kiểu tham số khác nhau, tự branch xử lý theo runtime type)
    user_message = {
        "role": "user",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(user_message)


def add_assistant_message(messages: list, message) -> None:
    """Thêm 1 assistant message vào messages list -- cùng logic isinstance như trên."""
    assistant_message = {
        "role": "assistant",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(assistant_message)


def text_from_message(message: Message) -> str:
    """Gộp tất cả text block trong 1 Message thành 1 string, dùng khi cần hiển thị
    câu trả lời cuối cùng cho user (bỏ qua các tool_use block nếu có)."""
    return "\n".join(block.text for block in message.content if block.type == "text")


def chat(
    messages: list,
    system: str = None,
    temperature: float = 1.0,
    stop_sequences: list = None,
    tools: list = None,
) -> Message:
    """Gọi Claude API, trả về full Message object (không chỉ text) để giữ lại mọi
    block (text + tool_use) cho vòng lặp tool-use xử lý tiếp.
    """
    # params: dict tham số gửi cho client.messages.create -- build động vì system/tools
    # là optional, không phải lúc nào cũng truyền (giống Builder pattern trong Java,
    # chỉ set field nào có giá trị thay vì luôn truyền đủ constructor)
    params = {
        "model": MODEL,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences or [],
    }

    if tools:
        params["tools"] = tools  # chỉ thêm key "tools" nếu có tool khả dụng

    if system:
        params["system"] = system  # system luôn là top-level param, không nằm trong messages

    message = client.messages.create(**params)
    return message  # trả full Message, không ép về text nữa


# ---------------------------------------------------------------------------
# Tool functions cho ví dụ "103 ngày nữa là ngày nào?"
# ---------------------------------------------------------------------------

def get_current_datetime(date_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Trả về ngày giờ hiện tại đã format -- Claude không tự biết "now" nên cần tool này."""
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)


def add_duration_to_datetime(
    datetime_str: str,
    days: int = 0,
    date_format: str = "%Y-%m-%d %H:%M:%S",
) -> str:
    """Cộng thêm `days` ngày vào 1 datetime string, trả về datetime string mới cùng format.

    Claude tính cộng/trừ ngày tháng không đáng tin (đặc biệt số ngày lớn, qua năm
    nhuận...) nên phải giao hẳn phép tính này cho code Python xử lý.
    """
    parsed = datetime.strptime(datetime_str, date_format)  # parse string -> datetime object
    result = parsed + timedelta(days=days)  # timedelta: đối chiếu Java ~ java.time.Period/Duration
    return result.strftime(date_format)


get_current_datetime_schema = ToolParam(
    {
        "name": "get_current_datetime",
        "description": (
            "Returns the current date and time formatted according to the specified format. "
            "Use this whenever you need to know 'now', e.g. as the starting point for a "
            "date calculation. Returns a single formatted string."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": "strftime format code, e.g. '%Y-%m-%d %H:%M:%S'.",
                    "default": "%Y-%m-%d %H:%M:%S",
                }
            },
            "required": [],
        },
    }
)

add_duration_to_datetime_schema = ToolParam(
    {
        "name": "add_duration_to_datetime",
        "description": (
            "Adds a number of days to a given datetime string and returns the resulting "
            "datetime string in the same format. Use this to compute a date that is N days "
            "before or after a known datetime -- do not compute this yourself, always call "
            "this tool for date arithmetic."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "datetime_str": {
                    "type": "string",
                    "description": "Starting datetime string, e.g. '2026-08-13 10:00:00'.",
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to add (can be negative to subtract).",
                },
                "date_format": {
                    "type": "string",
                    "description": "strftime format code matching datetime_str.",
                    "default": "%Y-%m-%d %H:%M:%S",
                },
            },
            "required": ["datetime_str", "days"],
        },
    }
)

TOOLS = [get_current_datetime_schema, add_duration_to_datetime_schema]


def run_tool(tool_name: str, tool_input: dict):
    """Dispatcher: map tên tool -> hàm Python thực thi tương ứng."""
    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)
    if tool_name == "add_duration_to_datetime":
        return add_duration_to_datetime(**tool_input)
    raise ValueError(f"Unknown tool: {tool_name}")


def run_tools(message: Message) -> list:
    """Chạy tất cả tool_use block trong 1 Message, trả về list tool_result block."""
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
            # tool lỗi -> vẫn trả tool_result, chỉ set is_error=True để Claude tự điều chỉnh
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(exc),
                    "is_error": True,
                }
            )
    return tool_result_blocks


def run_conversation(messages: list, max_turns: int = 6) -> Message:
    """Vòng lặp hội thoại: gọi chat() lặp lại cho tới khi Claude không còn yêu cầu
    tool nữa (stop_reason != "tool_use"), hoặc hết max_turns.

    Trả về Message cuối cùng (để dùng text_from_message() lấy câu trả lời) -- `messages`
    (list truyền vào) cũng được mutate đầy đủ lịch sử qua từng vòng, giữ nguyên
    convention pseudo code trong course: while True + break khi không còn tool_use.
    """
    response = None
    for turn in range(max_turns):
        print(f"[TURN {turn + 1}] Gửi request tới Claude (kèm {len(TOOLS)} tool schema)")
        response = chat(messages, tools=TOOLS)

        # append TOÀN BỘ response (add_assistant_message tự lấy .content nhờ isinstance check)
        add_assistant_message(messages, response)

        print(f"          stop_reason={response.stop_reason!r}")
        if response.stop_reason != "tool_use":
            break  # Claude đã có câu trả lời cuối cùng, không cần tool nữa

        # còn tool_use -> chạy tool, gửi lại tool_result trong 1 user message mới
        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return response


def main():
    messages = []
    # Câu hỏi kinh điển của lesson: cần 2 tool nối tiếp (get_current_datetime rồi mới
    # add_duration_to_datetime) -- không thể trả lời chỉ với 1 tool call
    add_user_message(messages, "What day is 103 days from today?")

    try:
        final_response = run_conversation(messages)
        print(f"\nFinal answer: {text_from_message(final_response)}")
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
