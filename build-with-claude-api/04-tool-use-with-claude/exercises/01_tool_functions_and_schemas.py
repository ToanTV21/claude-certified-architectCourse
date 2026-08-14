"""
Exercise 01: Tool Functions + Tool Schemas + Sending Tool Results
Session: Tool Use with Claude
Objective: End-to-end 1 tool call đơn giản — viết tool function, khai báo schema bằng
    ToolParam, đọc tool_use block, thực thi hàm, đóng gói tool_result (tool_use_id /
    content / is_error) và gửi lại cho Claude để lấy câu trả lời cuối cùng.
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


def get_stock_price(ticker: str) -> float:
    """Fake stock price lookup — stand-in cho 1 API thật.

    Best practice: validate input ngay đầu hàm, raise lỗi rõ ràng để Claude
    "nhìn thấy" error message qua tool_result và có thể tự retry.
    """
    # ticker: str — mã cổ phiếu, vd "AAPL", "GOOG"
    if not ticker:
        raise ValueError("ticker cannot be empty")
    fake_prices = {"AAPL": 227.5, "GOOG": 175.2}
    return fake_prices.get(ticker.upper(), 100.0)  # default 100.0 nếu không có trong dict


# Schema đặt tên theo convention "<ten_ham>_schema"
get_stock_price_schema = ToolParam(
    {
        "name": "get_stock_price",  # phải khớp tên hàm Python thực thi
        "description": (
            "Get the current stock price for a given ticker symbol. Use this any time "
            "the user asks for a stock's price instead of guessing a value."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. 'AAPL'."}
            },
            "required": ["ticker"],  # field bắt buộc phải có
        },
    }
)


def run_tool(tool_name: str, tool_input: dict):
    """Dispatcher: map tên tool -> hàm Python thực thi tương ứng."""
    if tool_name == "get_stock_price":
        # **tool_input unpack dict thành keyword argument cho hàm get_stock_price(ticker)
        return get_stock_price(**tool_input)
    raise ValueError(f"Unknown tool: {tool_name}")


def run_tools(message) -> list:
    """Chạy tất cả tool_use block có trong 1 assistant message, trả về list tool_result block."""
    tool_result_blocks = []
    for block in message.content:
        if block.type != "tool_use":
            continue  # bỏ qua text block, chỉ xử lý tool_use block

        print(f"  -> calling tool: {block.name}({block.input})  [id={block.id}]")
        try:
            # response.content[i].input là dict tham số Claude tự suy ra
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
            # nếu tool function raise lỗi -> vẫn trả tool_result, chỉ set is_error=True
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
    add_user_message(messages, "What's the price of AAPL stock?")

    try:
        # Request đầu tiên: kèm tools để Claude biết có thể gọi get_stock_price
        response = client.messages.create(
            model=MODEL,
            max_tokens=512,
            messages=messages,
            tools=[get_stock_price_schema],
        )

        # in ra từng content block (text hoặc tool_use) để quan sát cấu trúc multi-block
        for block in response.content:
            if block.type == "text":
                print(f"[text] {block.text}")
            elif block.type == "tool_use":
                print(f"[tool_use] {block.name}({block.input})")

        if response.stop_reason == "tool_use":
            # append TOÀN BỘ response.content (không chỉ text) làm assistant message
            add_assistant_message(messages, response.content)

            # chạy hết các tool_use block, gom thành list tool_result block
            tool_results = run_tools(response)

            # tool_result phải nằm trong 1 USER message mới, không phải assistant message
            add_user_message(messages, tool_results)

            # request tiếp theo: vẫn phải kèm tools schema dù không mong Claude gọi tool nữa
            final_response = client.messages.create(
                model=MODEL,
                max_tokens=256,
                messages=messages,
                tools=[get_stock_price_schema],
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
