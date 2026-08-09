"""
Tool functions + tool schemas + handling message blocks + sending tool results
Session: Tool Use with Claude
Objective: End-to-end single tool call: define function, schema, call, and reply.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test


def get_stock_price(ticker: str) -> float:
    """Fake stock price lookup — stand-in for a real API call."""
    # ticker: str — mã cổ phiếu, vd "AAPL", "GOOG"
    fake_prices = {"AAPL": 227.5, "GOOG": 175.2}
    return fake_prices.get(ticker.upper(), 100.0)  # default 100.0 nếu không có trong dict


# Tool schema — mô tả cho Claude biết tool này tên gì, làm gì, cần input gì
STOCK_TOOL = {
    "name": "get_stock_price",  # tên tool, phải khớp với tên hàm Python thực thi
    "description": "Get the current stock price for a given ticker symbol.",  # Claude dựa vào đây để quyết định có gọi tool không
    "input_schema": {  # JSON Schema mô tả input tool cần
        "type": "object",
        "properties": {"ticker": {"type": "string", "description": "e.g. 'AAPL'"}},
        "required": ["ticker"],  # field bắt buộc phải có
    },
}


def main():
    messages = [{"role": "user", "content": "What's the price of AAPL stock?"}]

    try:
        response = client.messages.create(
            model=MODEL, max_tokens=512, tools=[STOCK_TOOL], messages=messages
        )

        # A response can contain multiple content blocks (text + tool_use).
        # duyệt qua từng content block để in ra loại block (text hoặc tool_use)
        for block in response.content:
            if block.type == "text":
                print(f"[text block] {block.text}")
            elif block.type == "tool_use":
                print(f"[tool_use block] {block.name}({block.input})")

        # stop_reason == "tool_use" nghĩa là Claude muốn gọi tool trước khi trả lời tiếp
        if response.stop_reason == "tool_use":
            # tìm block đầu tiên có type tool_use để lấy tên tool + input Claude yêu cầu
            tool_block = next(b for b in response.content if b.type == "tool_use")
            price = get_stock_price(**tool_block.input)  # thực thi tool thật ở phía mình

            # phải append lại chính response.content (chứa tool_use block) làm assistant message
            messages.append({"role": "assistant", "content": response.content})
            # gửi kết quả tool dưới dạng user message với content type "tool_result"
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_block.id,  # phải khớp id của tool_use block tương ứng
                            "content": str(price),  # kết quả tool trả về, convert sang string
                        }
                    ],
                }
            )

            # gọi lại API lần 2 với full history (đã có tool_result) để Claude trả lời cuối cùng
            final = client.messages.create(
                model=MODEL, max_tokens=256, tools=[STOCK_TOOL], messages=messages
            )
            print(final.content[0].text)
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
