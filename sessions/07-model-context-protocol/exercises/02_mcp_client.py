"""
Implementing a client / Accessing resources / Prompts in the client
Session: Model Context Protocol
Objective: Connect to 01_mcp_server.py over stdio and call its tool, resource,
and prompt directly (without going through Claude).
"""

import asyncio  # MCP client SDK dùng async/await
import sys  # lấy đường dẫn python executable hiện tại để spawn server

from mcp import ClientSession, StdioServerParameters  # session quản lý kết nối MCP qua stdio
from mcp.client.stdio import stdio_client  # context manager mở transport stdio tới server

# suy ra đường dẫn tới file server (01_mcp_server.py) từ đường dẫn file client này
SERVER_SCRIPT = __file__.replace("02_mcp_client.py", "01_mcp_server.py")


async def main():
    # tham số để spawn server con: dùng đúng python hiện tại, chạy script server
    server_params = StdioServerParameters(command=sys.executable, args=[SERVER_SCRIPT])

    # mở kết nối stdio tới server -> nhận về 2 stream đọc/ghi
    async with stdio_client(server_params) as (read, write):
        # ClientSession bọc read/write thành API tiện dùng (list_tools, call_tool...)
        async with ClientSession(read, write) as session:
            await session.initialize()  # bắt tay ban đầu với server (MCP handshake)

            tools = await session.list_tools()  # liệt kê tool server expose
            print("Tools:", [t.name for t in tools.tools])

            # gọi tool "word_count" với input {"text": ...} theo đúng schema tool đã khai báo
            tool_result = await session.call_tool("word_count", {"text": "hello from mcp"})
            print("word_count result:", tool_result.content[0].text)

            # đọc resource theo URI đã đăng ký ở server (notes://study-log)
            resource = await session.read_resource("notes://study-log")
            print("Resource content:", resource.contents[0].text)

            # lấy prompt template đã render sẵn với arg {"text": ...}
            prompt = await session.get_prompt("summarize_prompt", {"text": "MCP is great."})
            print("Prompt messages:", prompt.messages)


if __name__ == "__main__":
    asyncio.run(main())  # chạy event loop cho hàm async main()
