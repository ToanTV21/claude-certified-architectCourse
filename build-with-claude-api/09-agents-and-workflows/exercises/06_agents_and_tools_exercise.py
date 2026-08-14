"""
Agents and tools
Session: Agents and Workflows
Objective: Minh hoa agent tu ket hop nhieu tool don gian (get_current_datetime,
    add_duration_to_datetime, set_reminder) theo cach khong lap trinh san -- khac voi
    workflow, o day khong ep san thu tu goi tool nao, Claude tu quyet dinh dua vao
    tung request cu the (co the goi 1, 2, hoac ca 3 tool tuy cau hoi).
"""

from datetime import datetime, timedelta  # tinh toan/cong tru thoi gian cho tool datetime

from dotenv import load_dotenv  # load bien moi truong tu file .env, khong hardcode API key
import anthropic  # SDK chinh thuc de goi Claude API
from anthropic.types import ToolParam  # wrap dict schema de bat loi type som o dev-time

load_dotenv()  # doc ANTHROPIC_API_KEY tu .env
client = anthropic.Anthropic()  # khoi tao client dung chung cho ca file

MODEL = "claude-haiku-4-5"  # model re, dung cho dev/test

# "Database" reminder gia lap trong memory -- set_reminder se ghi vao day
REMINDERS: list[dict] = []


def add_user_message(messages: list, content) -> None:
    """Them 1 user message vao messages list.

    content co the la str (cau hoi thuong) hoac list block (vd list cac tool_result
    block khi tra ket qua tool ve cho Claude).
    """
    messages.append({"role": "user", "content": content})


def add_assistant_message(messages: list, content) -> None:
    """Them 1 assistant message vao messages list.

    content thuong chinh la response.content -- list block (text + tool_use) --
    phai giu nguyen toan bo, khong duoc chi lay phan text.
    """
    messages.append({"role": "assistant", "content": content})


def get_current_datetime(date_format: str = "%Y-%m-%d %H:%M:%S (%A)") -> str:
    """Tool 1/3: tra ve ngay gio hien tai, format theo date_format (kieu strftime).

    %A trong default format tra ve luon ten thu (Monday, Tuesday...) de Claude
    khong can tinh toan tay thu trong tuan.
    """
    # date_format: str -- pattern strftime, vd "%Y-%m-%d" chi lay ngay
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)


def add_duration_to_datetime(base_datetime: str, days: int) -> str:
    """Tool 2/3: cong (hoac tru neu days am) so ngay vao 1 thoi diem cho truoc.

    base_datetime PHAI la string dang "%Y-%m-%d %H:%M:%S" -- thuong la output cua
    tool get_current_datetime, the hien dung tinh chat "chain" giua 2 tool.
    """
    # base_datetime: str -- thoi diem goc, format "%Y-%m-%d %H:%M:%S"
    # days: int -- so ngay can cong them (co the la so am de tru lui)
    base = datetime.strptime(base_datetime, "%Y-%m-%d %H:%M:%S")
    result = base + timedelta(days=days)
    return result.strftime("%Y-%m-%d %H:%M:%S (%A)")


def set_reminder(message: str, remind_at: str) -> str:
    """Tool 3/3: tao 1 reminder moi, luu vao REMINDERS (in-memory list).

    remind_at nen la output tu add_duration_to_datetime hoac get_current_datetime --
    the hien Claude phai chain qua tool truoc do de co du input cho tool nay.
    """
    # message: str -- noi dung reminder
    # remind_at: str -- thoi diem nhac, format "%Y-%m-%d %H:%M:%S"
    if not message or not remind_at:
        raise ValueError("message and remind_at are required")
    REMINDERS.append({"message": message, "remind_at": remind_at})
    return f"Reminder set: '{message}' at {remind_at}"


# Schema dat ten theo convention "<ten_ham>_schema" -- moi tool giu muc do tru tuong
# vua phai (khong hyper-specialized), de Claude tu quyet dinh khi nao chain tool nao
get_current_datetime_schema = ToolParam(
    {
        "name": "get_current_datetime",
        "description": "Get the current date and time. Use this as the starting point for any request involving 'now', 'today', or relative dates.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": "Python strftime format string. Optional, defaults to a format that includes the weekday name.",
                }
            },
            "required": [],
        },
    }
)

add_duration_to_datetime_schema = ToolParam(
    {
        "name": "add_duration_to_datetime",
        "description": "Add (or subtract, using a negative number) a number of days to a given datetime. Use this to compute future/past dates relative to a base datetime.",
        "input_schema": {
            "type": "object",
            "properties": {
                "base_datetime": {
                    "type": "string",
                    "description": "Base datetime in '%Y-%m-%d %H:%M:%S' format, e.g. from get_current_datetime.",
                },
                "days": {"type": "integer", "description": "Number of days to add (negative to subtract)."},
            },
            "required": ["base_datetime", "days"],
        },
    }
)

set_reminder_schema = ToolParam(
    {
        "name": "set_reminder",
        "description": "Create a reminder for a specific date and time. Use this only after you have computed the exact target datetime.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "What the reminder is about."},
                "remind_at": {
                    "type": "string",
                    "description": "Target datetime in '%Y-%m-%d %H:%M:%S' format.",
                },
            },
            "required": ["message", "remind_at"],
        },
    }
)

TOOLS = [get_current_datetime_schema, add_duration_to_datetime_schema, set_reminder_schema]


def run_tool(tool_name: str, tool_input: dict):
    """Dispatcher: map ten tool -> ham Python thuc thi tuong ung."""
    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)
    if tool_name == "add_duration_to_datetime":
        return add_duration_to_datetime(**tool_input)
    if tool_name == "set_reminder":
        return set_reminder(**tool_input)
    raise ValueError(f"Unknown tool: {tool_name}")


def run_tools(message) -> list:
    """Chay tat ca tool_use block co trong 1 assistant message, tra ve list tool_result block."""
    tool_result_blocks = []
    for block in message.content:
        if block.type != "tool_use":
            continue  # bo qua text block, chi xu ly tool_use block

        print(f"  -> calling tool: {block.name}({block.input})")
        try:
            result = run_tool(block.name, block.input)
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,  # PHAI khop id cua tool_use block goc
                    "content": str(result),
                    "is_error": False,
                }
            )
        except Exception as exc:
            # bat moi loi de van tra tool_result, chi danh dau is_error=True
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(exc),
                    "is_error": True,
                }
            )
    return tool_result_blocks


def run_agent(user_request: str, max_turns: int = 6) -> str:
    """Vong lap agent: Claude tu quyet dinh goi bao nhieu tool, theo thu tu nao,
    cho toi khi co cau tra loi cuoi cung (stop_reason != "tool_use").

    Day chinh la diem khac biet voi workflow -- khong co thu tu goi tool nao duoc
    hardcode san, tat ca do Claude tu "formulate plan" dua vao goal (user_request).
    """
    # user_request: str -- cau hoi/yeu cau goc cua user, co the can 0, 1, 2 hay 3 tool
    # max_turns: int -- chan vong lap vo han neu Claude cu goi tool mai khong dung
    messages = []
    add_user_message(messages, user_request)

    for _ in range(max_turns):
        response = client.messages.create(
            model=MODEL, max_tokens=512, messages=messages, tools=TOOLS
        )

        if response.stop_reason != "tool_use":
            return response.content[0].text

        add_assistant_message(messages, response.content)
        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return "Max turns reached without a final answer."


def main():
    # 3 vi du minh hoa agent tu chain SO LUONG TOOL KHAC NHAU tuy do phuc tap cua request
    requests = [
        "What's the time right now?",  # can 1 tool
        "What day of the week is it in 11 days?",  # can chain 2 tool
        "Set a reminder to go to the gym in 3 days.",  # can chain ca 3 tool
    ]

    try:
        for req in requests:
            print(f"\n=== Request: {req} ===")
            print(run_agent(req))

        print(f"\nREMINDERS hien co: {REMINDERS}")
    except anthropic.APIError as exc:
        # bat loi API de khong crash chuong trinh
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
