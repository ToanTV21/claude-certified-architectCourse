"""
Defining tools with MCP / Defining resources / Defining prompts
Session: Model Context Protocol
Objective: A single MCP server exposing one of each primitive: a Tool, a
Resource, and a Prompt.
"""

from mcp.server.fastmcp import FastMCP  # framework dựng MCP server nhanh, decorator-based
from pydantic import Field  # dùng Field để mô tả từng argument của tool cho Claude hiểu

mcp = FastMCP("study-mcp-server")  # khởi tạo server, tên này client sẽ thấy khi kết nối


@mcp.tool(
    name="word_count",
    description="Count the number of words in the given text.",
)
def word_count(
    # text: str — đoạn văn bản cần đếm từ, do client (hoặc Claude) truyền vào khi gọi tool
    text: str = Field(description="Text to count words in"),
) -> int:
    return len(text.split())


@mcp.resource("notes://study-log")
def study_log() -> str:
    """Application-controlled data the client can read directly."""
    # resource: dữ liệu client tự chủ động đọc (không cần Claude quyết định gọi hay không)
    return "2026-08-08: Started Model Context Protocol session."


@mcp.prompt()
def summarize_prompt(text: str) -> str:
    """User-triggered prompt template for summarizing text."""
    # text: str — nội dung user muốn tóm tắt, được chèn vào template prompt cố định
    return f"Summarize the following text in 2 sentences:\n\n{text}"


if __name__ == "__main__":
    mcp.run()  # chạy server, mặc định giao tiếp qua stdio với client
