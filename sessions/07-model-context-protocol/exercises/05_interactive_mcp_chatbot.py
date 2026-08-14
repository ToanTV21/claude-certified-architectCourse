"""
Exercise 05: Interactive MCP + Claude chatbot (REPL với @mention document)
Session: Model Context Protocol
Objective: Biến luồng 9 bước ở 04_mcp_chatbot_with_claude.py thành 1 vòng lặp
chat tương tác trên terminal (giống demo "mcp uv run main.py" trong khóa học):
  - User gõ câu hỏi trực tiếp trong terminal (input())
  - Có thể chèn "@doc_id" trong câu hỏi để tham chiếu 1 document cụ thể
    (vd: "Whats in the @report.pdf document?")
  - "@doc_id" được thay bằng nội dung resource "docs://documents/{doc_id}"
    (đọc qua MCP resource, không phải tool) trước khi gửi cho Claude
  - Nếu Claude cần thêm thông tin, nó vẫn có thể tự gọi tool read_doc_contents
    qua đúng luồng 9 bước cũ
  - Gõ "quit" hoặc "exit" để thoát vòng lặp
"""

import asyncio  # MCP client SDK + vòng lặp async cho toàn bộ chat loop
import re  # regex để tìm pattern "@doc_id" trong câu hỏi user gõ
import sys  # lấy đường dẫn python hiện tại để spawn server con qua stdio

# console mặc định trên Windows dùng codepage cp1252, không encode được dấu tiếng
# Việt trong log -> ép stdout sang UTF-8 để tránh UnicodeEncodeError
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv  # load ANTHROPIC_API_KEY từ .env, không hardcode key
import anthropic  # Anthropic SDK để gọi Claude thật

from mcp import ClientSession, StdioServerParameters  # session quản lý kết nối MCP
from mcp.client.stdio import stdio_client  # transport stdio tới server con

load_dotenv()
client = anthropic.Anthropic()  # tự đọc ANTHROPIC_API_KEY từ .env

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test theo convention CLAUDE.md

# đường dẫn tới server đã định nghĩa tools/resources (docs, read_doc_contents, ...)
SERVER_SCRIPT = __file__.replace(
    "05_interactive_mcp_chatbot.py", "03_document_mcp_server.py"
)

# pattern bắt "@doc_id" — doc_id gồm chữ/số/dấu chấm/gạch ngang/gạch dưới
MENTION_PATTERN = re.compile(r"@([\w.\-]+)")


def mcp_tool_to_claude_schema(tool) -> dict:
    """Convert 1 mcp.types.Tool sang format tool schema mà Claude Messages API cần."""
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema,
    }


async def resolve_mentions(session: ClientSession, user_query: str) -> str:
    """Thay mọi "@doc_id" trong user_query bằng nội dung document tương ứng,
    đọc qua MCP resource "docs://documents/{doc_id}" (giống @-mention trong
    Claude Code khi user gõ @file.py để đính kèm nội dung file).

    Nếu doc_id không tồn tại, giữ nguyên "@doc_id" trong text — để Claude tự
    quyết định xử lý (vd thông báo lỗi cho user) thay vì crash cả chương trình.
    """
    mentions = MENTION_PATTERN.findall(user_query)
    if not mentions:
        return user_query

    resolved_query = user_query
    for doc_id in mentions:
        try:
            resource_result = await session.read_resource(f"docs://documents/{doc_id}")
            doc_text = resource_result.contents[0].text
            # chèn nội dung document ngay sau mention, kèm markup rõ ràng để Claude
            # phân biệt được đâu là câu hỏi gốc, đâu là nội dung document đính kèm
            resolved_query = resolved_query.replace(
                f"@{doc_id}",
                f"@{doc_id}\n\n<document id=\"{doc_id}\">\n{doc_text}\n</document>",
            )
        except Exception:
            # doc_id không tồn tại hoặc lỗi đọc resource -> bỏ qua, giữ nguyên mention gốc
            continue

    return resolved_query


async def ask_claude(session: ClientSession, claude_tools: list[dict], messages: list) -> str:
    """Chạy đúng luồng 9 bước (rút gọn còn bước 4-9, vì bước 1-3 đã làm 1 lần ở
    main loop) cho 1 lượt hỏi-đáp, hỗ trợ Claude tự gọi tool nhiều lần liên tiếp
    (loop thay vì if 1 lần) trong trường hợp cần đọc nhiều document khác nhau.
    """
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=messages,
            tools=claude_tools,
        )

        if response.stop_reason != "tool_use":
            # Claude đã có câu trả lời cuối cùng, không cần gọi tool nữa
            messages.append({"role": "assistant", "content": response.content})
            return "".join(block.text for block in response.content if block.type == "text")

        # Claude yêu cầu gọi tool -> lưu lại assistant turn (gồm tool_use block)
        messages.append({"role": "assistant", "content": response.content})

        # 1 lượt trả lời của Claude có thể chứa nhiều tool_use block cùng lúc
        tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
        tool_results = []
        for tool_use_block in tool_use_blocks:
            print(f"  -> Claude gọi tool: {tool_use_block.name}({tool_use_block.input})")
            tool_result = await session.call_tool(tool_use_block.name, tool_use_block.input)
            result_text = tool_result.content[0].text
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": result_text,
                }
            )

        # gửi tất cả tool_result về Claude trong 1 follow-up message duy nhất
        messages.append({"role": "user", "content": tool_results})


async def chat_loop():
    server_params = StdioServerParameters(command=sys.executable, args=[SERVER_SCRIPT])

    # mở kết nối stdio tới MCP server con (03_document_mcp_server.py), giữ mở
    # xuyên suốt cả vòng lặp chat thay vì tạo mới mỗi lượt hỏi
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()  # bắt tay MCP handshake 1 lần duy nhất

            list_tools_result = await session.list_tools()
            claude_tools = [mcp_tool_to_claude_schema(t) for t in list_tools_result.tools]

            messages: list = []  # history giữ nguyên xuyên suốt phiên chat

            print("MCP chatbot đã sẵn sàng. Gõ @doc_id để đính kèm document, 'quit' để thoát.")
            print(f"Tools khả dụng: {[t['name'] for t in claude_tools]}\n")

            while True:
                user_query = input("> ").strip()
                if not user_query:
                    continue
                if user_query.lower() in {"quit", "exit"}:
                    print("Bye!")
                    break

                resolved_query = await resolve_mentions(session, user_query)
                messages.append({"role": "user", "content": resolved_query})

                final_text = await ask_claude(session, claude_tools, messages)
                print(f"\nResponse:\n{final_text}\n")


if __name__ == "__main__":
    asyncio.run(chat_loop())  # chạy event loop cho toàn bộ chat REPL
