"""
Exercise 03: Using Multiple Tools (fine-grained tool calling)
Session: Tool Use with Claude
Objective: Cho Claude nhiều tool khác mục đích cùng lúc (tool_choice mặc định "auto"),
    quan sát Claude tự chọn đúng tool nào theo từng câu hỏi, rồi vẫn chạy đủ luồng
    sending-tool-results (run_tool dispatcher + tool_result block) để lấy câu trả lời cuối.
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


def search_web(query: str) -> str:
    """Fake web search — stand-in cho 1 search API thật."""
    # query: str — nội dung cần tìm kiếm
    if not query:
        raise ValueError("query cannot be empty")
    return f"Top result for '{query}': (mock search result, no real network call)."


def calculate(expression: str) -> str:
    """Đánh giá 1 biểu thức số học cơ bản bằng eval, chỉ cho phép ký tự số học an toàn."""
    # expression: str — biểu thức toán, vd "1523 * 88"
    allowed_chars = set("0123456789+-*/(). ")
    if not expression or not set(expression) <= allowed_chars:
        # validate chặt để tránh eval() chạy code tuỳ ý -> raise lỗi rõ ràng cho Claude thấy
        raise ValueError(f"invalid arithmetic expression: {expression!r}")
    return str(eval(expression))  # an toàn vì đã validate chỉ còn ký tự số học


# Schema đặt tên theo convention "<ten_ham>_schema" — 2 tool khác mục đích để Claude tự chọn
search_web_schema = ToolParam(
    {
        "name": "search_web",
        "description": "Search the web for up-to-date information not in Claude's training data.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search query text."}},
            "required": ["query"],
        },
    }
)

calculate_schema = ToolParam(
    {
        "name": "calculate",
        "description": "Evaluate a basic arithmetic expression (+, -, *, /). Use instead of computing math yourself.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Arithmetic expression, e.g. '1523 * 88'."}
            },
            "required": ["expression"],
        },
    }
)

TOOLS = [search_web_schema, calculate_schema]  # danh sách tool khả dụng gửi cho Claude


def run_tool(tool_name: str, tool_input: dict):
    """Dispatcher: map tên tool -> hàm Python thực thi tương ứng."""
    if tool_name == "search_web":
        return search_web(**tool_input)
    if tool_name == "calculate":
        return calculate(**tool_input)
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


def ask(prompt: str) -> None:
    """Gửi 1 prompt, để Claude tự chọn tool (nếu cần), rồi chạy tool + lấy câu trả lời cuối."""
    messages = []
    add_user_message(messages, prompt)

    response = client.messages.create(
        model=MODEL, max_tokens=256, messages=messages, tools=TOOLS
    )

    if response.stop_reason != "tool_use":
        # Claude tự trả lời thẳng, không cần tool nào
        print(f"Prompt: {prompt!r} -> no tool called")
        print(f"  answer: {response.content[0].text}\n")
        return

    add_assistant_message(messages, response.content)
    tool_results = run_tools(response)
    add_user_message(messages, tool_results)

    final_response = client.messages.create(
        model=MODEL, max_tokens=256, messages=messages, tools=TOOLS
    )
    final_text = next((b.text for b in final_response.content if b.type == "text"), "")
    print(f"Prompt: {prompt!r}")
    print(f"  answer: {final_text}\n")


def main():
    # 2 prompt cố tình thiết kế để mỗi câu khớp với 1 tool khác nhau
    prompts = [
        "What is 1523 * 88?",  # kỳ vọng Claude chọn tool "calculate"
        "What's the latest news about Claude models?",  # kỳ vọng Claude chọn tool "search_web"
    ]

    for prompt in prompts:
        try:
            ask(prompt)
        except anthropic.APIError as exc:
            # bắt lỗi API cho từng prompt riêng, không dừng cả vòng lặp
            print(f"API error: {exc}")


if __name__ == "__main__":
    main()
