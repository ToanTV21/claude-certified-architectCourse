"""
Exercise 04: End-to-end MCP + Claude flow (MCP clients / Implementing a client review)
Session: Model Context Protocol
Objective: Nối MCP client (03_document_mcp_server.py) với Claude API thật, minh
hoạ đúng luồng 9 bước đã note trong notes.md lesson "MCP clients":
  1. User gửi query
  2. Server (ở đây là script này) cần tools trước khi gọi Claude
  3. MCP client gửi ListToolsRequest -> nhận ListToolsResult
  4. Gọi Claude lần đầu kèm (query + tools)
  5. Claude trả về tool_use nếu cần
  6. MCP client gửi CallToolRequest -> MCP server thực thi
  7. Kết quả (CallToolResult) chảy ngược về
  8. Gửi tool_result về Claude trong follow-up message
  9. Claude trả lời cuối cùng cho user
"""

import asyncio  # MCP client SDK + vòng lặp async cho toàn bộ luồng
import sys  # lấy đường dẫn python hiện tại để spawn server con qua stdio

from dotenv import load_dotenv  # load ANTHROPIC_API_KEY từ .env, không hardcode key
import anthropic  # Anthropic SDK để gọi Claude thật

from mcp import ClientSession, StdioServerParameters  # session quản lý kết nối MCP
from mcp.client.stdio import stdio_client  # transport stdio tới server con

load_dotenv()
client = anthropic.Anthropic()  # tự đọc ANTHROPIC_API_KEY từ .env

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test theo convention CLAUDE.md

# đường dẫn tới server đã định nghĩa tool read_doc_contents/edit_document (bước 2-3)
SERVER_SCRIPT = __file__.replace(
    "04_mcp_chatbot_with_claude.py", "03_document_mcp_server.py"
)


def mcp_tool_to_claude_schema(tool) -> dict:
    """Convert 1 mcp.types.Tool sang format tool schema mà Claude Messages API cần.

    MCP Tool đã có sẵn name/description/inputSchema (SDK tự sinh từ Field ở
    server) -> chỉ cần map field 'inputSchema' -> 'input_schema' cho đúng
    tên field Claude API mong đợi.
    """
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema,
    }


async def main():
    user_query = "What is the contents of the deposition.md document?"  # bước 1: user query
    print(f"[1] User query: {user_query!r}")

    server_params = StdioServerParameters(command=sys.executable, args=[SERVER_SCRIPT])

    # mở kết nối stdio tới MCP server con (03_document_mcp_server.py)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()  # bắt tay MCP handshake
            print("[2] MCP handshake done -> server sẵn sàng, cần tools trước khi gọi Claude")

            # --- bước 2-3: MCP client gửi ListToolsRequest, nhận ListToolsResult ---
            list_tools_result = await session.list_tools()
            claude_tools = [mcp_tool_to_claude_schema(t) for t in list_tools_result.tools]
            print(
                f"[3] ListToolsRequest -> ListToolsResult: "
                f"{[t['name'] for t in claude_tools]}"
            )

            messages = [{"role": "user", "content": user_query}]

            # --- bước 4: gọi Claude lần đầu, kèm theo query + danh sách tools ---
            print("[4] Calling Claude (1st call) with query + tools...")
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                messages=messages,
                tools=claude_tools,
            )
            print(f"[4] Claude responded, stop_reason={response.stop_reason!r}")

            # --- bước 5: kiểm tra Claude có yêu cầu gọi tool không (stop_reason == "tool_use") ---
            if response.stop_reason == "tool_use":
                # lưu lại toàn bộ assistant turn (gồm cả tool_use block) vào history
                messages.append({"role": "assistant", "content": response.content})

                # tìm block tool_use trong content (có thể có text block đi kèm)
                tool_use_block = next(
                    block for block in response.content if block.type == "tool_use"
                )
                print(
                    f"[5] Claude requested tool_use: name={tool_use_block.name!r}, "
                    f"input={tool_use_block.input!r}"
                )

                # --- bước 6: MCP client gửi CallToolRequest tới MCP server để thực thi ---
                print("[6] Sending CallToolRequest to MCP server...")
                tool_result = await session.call_tool(
                    tool_use_block.name, tool_use_block.input
                )

                # --- bước 7: kết quả (CallToolResult) đã có ở đây, lấy phần text đầu tiên ---
                result_text = tool_result.content[0].text
                print(f"[7] CallToolResult received: {result_text!r}")

                # --- bước 8: gửi tool_result về Claude trong 1 follow-up message ---
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_block.id,
                                "content": result_text,
                            }
                        ],
                    }
                )
                print("[8] Sending tool_result back to Claude (follow-up call)...")

                response = client.messages.create(
                    model=MODEL,
                    max_tokens=1024,
                    messages=messages,
                    tools=claude_tools,
                )
            else:
                print("[5] Claude did not request a tool (stop_reason != 'tool_use')")

            # --- bước 9: in câu trả lời cuối cùng của Claude cho user ---
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            print(f"[9] Final answer -> Claude: {final_text}")


if __name__ == "__main__":
    asyncio.run(main())  # chạy event loop cho hàm async main()
