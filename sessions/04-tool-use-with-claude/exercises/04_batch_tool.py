"""
Exercise 04: The Batch Tool
Session: Tool Use with Claude
Objective: Gom nhieu loi goi tool vao 1 message duy nhat bang cach dinh nghia
mot "batch" tool ao, thay vi de Claude goi tuan tu tung tool rieng le tung round.
"""

from dotenv import load_dotenv  # doc ANTHROPIC_API_KEY tu file .env, khong hardcode key
import anthropic  # SDK chinh thuc cua Anthropic
import json  # parse chuoi JSON argument cua tung invocation trong batch

load_dotenv()  # nap bien moi truong tu .env vao os.environ
client = anthropic.Anthropic()  # tao client, tu doc ANTHROPIC_API_KEY tu env

MODEL = "claude-haiku-4-5"  # model nhanh + re, dung cho dev/test theo rule CLAUDE.md


# --- 2 tool function that su te (khong goi API ngoai, chi de minh hoa) ---
def get_weather(city: str) -> dict:
    """Tra ve thoi tiet gia lap cho 1 thanh pho (mock, khong goi API that)."""
    if not city:
        # validate input ngay dau ham, raise loi ro rang de Claude thay va tu sua
        raise ValueError("city khong duoc de trong")
    fake_data = {"Tokyo": "28C, nang", "Hanoi": "33C, mua rao", "Osaka": "30C, may"}
    return {"city": city, "forecast": fake_data.get(city, "khong co du lieu")}


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Quy doi tien te gia lap bang ty gia co dinh (mock)."""
    fake_rates = {("USD", "JPY"): 150.0, ("USD", "VND"): 25000.0}
    rate = fake_rates.get((from_currency, to_currency))
    if rate is None:
        raise ValueError(f"khong ho tro cap ty gia {from_currency}->{to_currency}")
    return {"amount": amount * rate, "currency": to_currency}


# dispatcher: anh xa ten tool -> ham Python thuc thi tuong ung
def run_tool(tool_name: str, tool_input: dict):
    if tool_name == "get_weather":
        return get_weather(**tool_input)
    if tool_name == "convert_currency":
        return convert_currency(**tool_input)
    # tool khong ton tai -> raise de bao loi ro rang thay vi fail am tham
    raise ValueError(f"Unknown tool: {tool_name}")


def run_batch(batch_input: dict) -> list:
    """Chay tat ca cac loi goi tool ben trong 1 batch, tra ve list ket qua tuong ung."""
    batch_output = []
    for invocation in batch_input["invocations"]:
        tool_name = invocation["name"]  # ten tool that su can chay
        # arguments duoc Claude gui duoi dang chuoi JSON, can parse lai thanh dict
        tool_input = json.loads(invocation["arguments"])
        try:
            result = run_tool(tool_name, tool_input)
            batch_output.append({"name": tool_name, "output": result, "is_error": False})
        except Exception as exc:
            # loi cua 1 tool khong lam sap ca batch, chi danh dau is_error cho item do
            batch_output.append({"name": tool_name, "output": str(exc), "is_error": True})
    return batch_output


# schema cua 2 tool that (Claude co the goi truc tiep neu khong dung batch)
WEATHER_SCHEMA = {
    "name": "get_weather",
    "description": "Get the current weather forecast for a given city.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "Ten thanh pho"}},
        "required": ["city"],
    },
}

CURRENCY_SCHEMA = {
    "name": "convert_currency",
    "description": "Convert an amount of money from one currency to another.",
    "input_schema": {
        "type": "object",
        "properties": {
            "amount": {"type": "number", "description": "So tien can quy doi"},
            "from_currency": {"type": "string", "description": "Ma tien te goc, vd USD"},
            "to_currency": {"type": "string", "description": "Ma tien te dich, vd JPY"},
        },
        "required": ["amount", "from_currency", "to_currency"],
    },
}

# schema cua tool "batch" ao - Claude se goi tool nay voi 1 list cac invocation
# thay vi goi rieng le tung tool that, giup gom nhieu tool call vao 1 round duy nhat
BATCH_SCHEMA = {
    "name": "batch",
    "description": (
        "Invoke multiple other tools in a single call. Use this whenever you need "
        "to call more than one tool to answer the user's request, instead of "
        "calling tools one at a time across multiple turns."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "invocations": {
                "type": "array",
                "description": "Danh sach cac tool can goi",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Ten tool can goi"},
                        "arguments": {
                            "type": "string",
                            "description": "Argument cua tool, dang chuoi JSON",
                        },
                    },
                    "required": ["name", "arguments"],
                },
            }
        },
        "required": ["invocations"],
    },
}


def main():
    # cau hoi can 2 tool khac nhau -> ky vong Claude dung 1 lan goi "batch"
    # thay vi 2 round rieng le
    user_prompt = (
        "What's the weather in Tokyo, and how much is 100 USD in JPY?"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        # dua ca 2 tool that + tool batch vao cung 1 danh sach de Claude chon
        tools=[WEATHER_SCHEMA, CURRENCY_SCHEMA, BATCH_SCHEMA],
        messages=[{"role": "user", "content": user_prompt}],
    )

    # tim block tool_use co ten "batch" trong response
    batch_calls = [b for b in response.content if b.type == "tool_use" and b.name == "batch"]

    if batch_calls:
        for call in batch_calls:
            print(f"Claude goi batch voi {len(call.input['invocations'])} invocation(s)")
            results = run_batch(call.input)
            for r in results:
                print(f"  - {r['name']} -> {r['output']} (is_error={r['is_error']})")
    else:
        # Claude co the van goi tool rieng le neu khong thay batch phu hop
        tool_calls = [b for b in response.content if b.type == "tool_use"]
        for call in tool_calls:
            print(f"Claude goi rieng le: {call.name}({call.input})")
        if not tool_calls:
            print("Claude tra loi thang, khong goi tool nao.")


if __name__ == "__main__":
    main()
