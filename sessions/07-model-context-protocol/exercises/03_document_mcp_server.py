"""
Exercise 03: Defining tools with MCP (Document server)
Session: Model Context Protocol
Objective: Build an MCP server that manages in-memory documents, using the
official Python MCP SDK (FastMCP + Pydantic Field) to auto-generate tool
schemas instead of hand-writing JSON schemas.
"""

from mcp.server.fastmcp import FastMCP  # SDK dựng MCP server nhanh, decorator-based
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


if __name__ == "__main__":
    mcp.run()  # chạy server, mặc định giao tiếp qua stdio với client
