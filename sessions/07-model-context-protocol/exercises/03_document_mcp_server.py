"""
Exercise 03: Defining tools with MCP (Document server)
Session: Model Context Protocol
Objective: Build an MCP server that manages in-memory documents, using the
official Python MCP SDK (FastMCP + Pydantic Field) to auto-generate tool
schemas instead of hand-writing JSON schemas.
"""

from mcp.server.fastmcp import FastMCP  # SDK dựng MCP server nhanh, decorator-based
from mcp.server.fastmcp import base  # base.UserMessage/base.Message dùng cho prompt trả về
from pydantic import Field  # dùng Field để mô tả từng argument của tool cho Claude hiểu

# log_level="ERROR" — giảm log ồn ào khi chạy dev, chỉ in ra khi có lỗi thật sự
mcp = FastMCP("DocumentMCP", log_level="ERROR")

# Lưu documents in-memory bằng 1 dict đơn giản: key = document id, value = nội dung document
# (không cần database — phù hợp cho mục đích học tập / demo)
docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditure",
    "outlook.pdf": "This document presents the projected future performance of the",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment",
}


@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_document(
    # Field(description=...) — Pydantic tự sinh JSON schema kèm mô tả cho Claude,
    # không cần tự viết schema tay như cách "trước MCP" ở lesson Introducing MCP
    doc_id: str = Field(description="Id of the document to read")
):
    if doc_id not in docs:
        # raise ValueError kèm message rõ ràng — Claude đọc được message này để phản ứng phù hợp
        raise ValueError(f"Doc with id {doc_id} not found")

    return docs[doc_id]


@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with a new string.",
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(
        description="The text to replace. Must match exactly, including whitespace."
    ),
    new_str: str = Field(description="The new text to insert in place of the old text."),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")

    # str.replace() có sẵn của Python — đủ dùng cho find-and-replace đơn giản
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)


# --- Resources (lesson "Defining resources") ---
# Resources dùng để expose data (giống GET handler), khác với tools ở trên vốn để "perform actions"


@mcp.resource(
    "docs://documents",
    mime_type="application/json",
)
def list_docs() -> list[str]:
    # Direct Resource — URI tĩnh "docs://documents", không có tham số
    # SDK tự serialize list[str] này thành JSON, không cần tự json.dumps()
    return list(docs.keys())


@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain",
)
def fetch_doc(doc_id: str) -> str:
    # Templated Resource — "{doc_id}" trong URI được SDK tự parse và truyền vào đây
    # dưới dạng keyword argument, giống hệt tên biến trong URI
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


# --- Prompts (lesson "Defining prompts") ---
# Prompt trả về sẵn 1 list messages đã soạn kỹ, client dùng thẳng thay vì tự viết prompt


@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format.",
)
def format_document(
    doc_id: str = Field(description="Id of the document to format")
) -> list[base.Message]:
    # prompt được soạn sẵn, có hướng dẫn cụ thể + nhắc dùng tool 'edit_document' để áp dụng thay đổi
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.

The id of the document you need to reformat is:

{doc_id}

Add in headers, bullet points, tables, etc as necessary. Feel free to add in extra formatting.
Use the 'edit_document' tool to edit the document. After the document has been reformatted...
"""

    # trả về list[base.Message] — ở đây chỉ 1 UserMessage chứa toàn bộ instructions
    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run()  # chạy server, mặc định giao tiếp qua stdio với client
