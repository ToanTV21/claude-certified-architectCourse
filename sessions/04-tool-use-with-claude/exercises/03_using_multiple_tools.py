"""
Using multiple tools / fine grained tool calling
Session: Tool Use with Claude
Objective: Give Claude several tools at once and observe which it picks.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test

# 2 tool khác nhau về mục đích để xem Claude tự chọn đúng tool nào theo từng câu hỏi
TOOLS = [
    {
        "name": "search_web",
        "description": "Search the web for up-to-date information.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "calculate",
        "description": "Evaluate a basic arithmetic expression.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
]


def main():
    # 2 prompt cố tình thiết kế để mỗi câu khớp với 1 tool khác nhau
    prompts = [
        "What is 1523 * 88?",  # kỳ vọng Claude chọn tool "calculate"
        "What's the latest news about Claude models?",  # kỳ vọng Claude chọn tool "search_web"
    ]

    for prompt in prompts:
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=256,
                tools=TOOLS,  # cung cấp cả 2 tool, để tool_choice mặc định "auto" tự quyết định
                messages=[{"role": "user", "content": prompt}],
            )
            # lọc ra các content block có type tool_use để biết Claude đã chọn tool nào
            tool_calls = [b for b in response.content if b.type == "tool_use"]
            if tool_calls:
                for call in tool_calls:
                    print(f"Prompt: {prompt!r} -> tool: {call.name}({call.input})")
            else:
                # không có tool_use nghĩa là Claude tự trả lời thẳng, không cần tool
                print(f"Prompt: {prompt!r} -> no tool called, direct answer")
        except anthropic.APIError as exc:
            # bắt lỗi API cho từng prompt riêng, không dừng cả vòng lặp
            print(f"API error: {exc}")


if __name__ == "__main__":
    main()
