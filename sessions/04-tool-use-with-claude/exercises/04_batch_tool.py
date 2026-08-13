"""
Exercise 04: The Batch Tool
Session: Tool Use with Claude
Objective: Gom nhiều lời gọi tool vào 1 message duy nhất bằng cách định nghĩa 1 tool
    "batch" ảo, thay vì để Claude gọi tuần tự từng tool riêng lẻ từng round — giảm số
    round-trip request/response.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env, không hardcode API key
import anthropic  # SDK chính thức để gọi Claude API
from anthropic.types import ToolParam  # wrap dict schema để bắt lỗi type sớm ở dev-time
import json  # parse chuỗi JSON argument của từng invocation trong batch

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


def get_weather(city: str) -> dict:
    """Tool function: trả về thời tiết giả lập cho 1 thành phố (mock, không gọi API thật)."""
    # city: str — tên thành phố Claude truyền vào
    if not city:
        raise ValueError("city cannot be empty")
    fake_data = {"Tokyo": "28C, nang", "Hanoi": "33C, mua rao", "Osaka": "30C, may"}
    return {"city": city, "forecast": fake_data.get(city, "khong co du lieu")}


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Tool function: quy đổi tiền tệ giả lập bằng tỷ giá cố định (mock)."""
    # amount: float, from_currency/to_currency: str (mã tiền tệ 3 ký tự)
    fake_rates = {("USD", "JPY"): 150.0, ("USD", "VND"): 25000.0}
    rate = fake_rates.get((from_currency, to_currency))
    if rate is None:
        raise ValueError(f"unsupported currency pair {from_currency}->{to_currency}")
    return {"amount": amount * rate, "currency": to_currency}


# Schema đặt tên theo convention "<ten_ham>_schema" — 2 tool thật Claude có thể gọi trực tiếp
get_weather_schema = ToolParam(
    {
        "name": "get_weather",
        "description": "Get the current weather forecast for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name."}},
            "required": ["city"],
        },
    }
)

convert_currency_schema = ToolParam(
    {
        "name": "convert_currency",
        "description": "Convert an amount of money from one currency to another.",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Amount to convert."},
                "from_currency": {"type": "string", "description": "Source currency code, e.g. USD."},
                "to_currency": {"type": "string", "description": "Target currency code, e.g. JPY."},
            },
            "required": ["amount", "from_currency", "to_currency"],
        },
    }
)

# Schema của tool "batch" ảo — Claude sẽ gọi tool này với 1 list các invocation thay vì
# gọi riêng lẻ từng tool thật, giúp gom nhiều tool call vào 1 round duy nhất
batch_schema = ToolParam(
    {
        "name": "batch",
        "description": (
            "Invoke multiple other tools in a single call. Use this whenever you need to "
            "call more than one tool to answer the user's request, instead of calling "
            "tools one at a time across multiple turns."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "invocations": {
                    "type": "array",
                    "description": "List of tool calls to run.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the tool to call."},
                            "arguments": {
                                "type": "string",
                                "description": "Arguments for the tool, as a JSON string.",
                            },
                        },
                        "required": ["name", "arguments"],
                    },
                }
            },
            "required": ["invocations"],
        },
    }
)

TOOLS = [get_weather_schema, convert_currency_schema, batch_schema]


def run_tool(tool_name: str, tool_input: dict):
    """Dispatcher: map tên tool -> hàm Python thực thi tương ứng."""
    if tool_name == "get_weather":
        return get_weather(**tool_input)
    if tool_name == "convert_currency":
        return convert_currency(**tool_input)
    raise ValueError(f"Unknown tool: {tool_name}")


def run_batch(batch_input: dict) -> list:
    """Chạy tất cả lời gọi tool bên trong 1 batch, trả về list kết quả tương ứng."""
    # batch_input: dict — chính là tool_use.input của tool "batch", có key "invocations"
    batch_output = []
    for invocation in batch_input["invocations"]:
        tool_name = invocation["name"]  # tên tool thật sự cần chạy
        # arguments được Claude gửi dưới dạng chuỗi JSON, cần parse lại thành dict
        tool_input = json.loads(invocation["arguments"])
        try:
            result = run_tool(tool_name, tool_input)
            batch_output.append({"name": tool_name, "output": result, "is_error": False})
        except Exception as exc:
            # lỗi của 1 tool không làm sập cả batch, chỉ đánh dấu is_error cho item đó
            batch_output.append({"name": tool_name, "output": str(exc), "is_error": True})
    return batch_output


def run_tools(message) -> list:
    """Chạy tất cả tool_use block trong message — xử lý riêng block "batch" (nhiều tool con)
    và các tool_use thường (1 tool), rồi gom hết thành list tool_result block."""
    tool_result_blocks = []
    for block in message.content:
        if block.type != "tool_use":
            continue  # bỏ qua text block, chỉ xử lý tool_use block

        if block.name == "batch":
            print(f"  -> calling batch with {len(block.input['invocations'])} invocation(s)  [id={block.id}]")
            batch_results = run_batch(block.input)
            for r in batch_results:
                print(f"     - {r['name']} -> {r['output']} (is_error={r['is_error']})")
            # cả batch chỉ có 1 tool_use_id (của tool "batch") -> gộp toàn bộ kết quả
            # con vào 1 tool_result content duy nhất, khớp đúng id đó
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(batch_results),
                    "is_error": any(r["is_error"] for r in batch_results),
                }
            )
            continue

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
    # câu hỏi cần 2 tool khác nhau -> kỳ vọng Claude dùng 1 lần gọi "batch" thay vì 2 round riêng
    add_user_message(messages, "What's the weather in Tokyo, and how much is 100 USD in JPY?")

    try:
        response = client.messages.create(
            model=MODEL, max_tokens=1024, messages=messages, tools=TOOLS
        )

        if response.stop_reason == "tool_use":
            add_assistant_message(messages, response.content)
            tool_results = run_tools(response)
            add_user_message(messages, tool_results)

            final_response = client.messages.create(
                model=MODEL, max_tokens=512, messages=messages, tools=TOOLS
            )
            final_text = next(
                (b.text for b in final_response.content if b.type == "text"), ""
            )
            print(f"\nFinal answer: {final_text}")
        else:
            print(response.content[0].text)
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
