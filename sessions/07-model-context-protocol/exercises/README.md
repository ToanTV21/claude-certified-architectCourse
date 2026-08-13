# Exercises — Model Context Protocol

Requires: `pip install mcp`

- `01_mcp_server.py` — Defining tools, resources, and prompts with MCP (FastMCP).
- `02_mcp_client.py` — Implementing a client that connects to `01_mcp_server.py`
  over stdio and calls its tool/resource/prompt.
- `03_document_mcp_server.py` — Defining tools with MCP: in-memory document
  server (`read_doc_contents` / `edit_document`) using Pydantic `Field` for
  auto-generated tool schemas.

## Chạy thử với MCP Inspector
```bash
mcp dev sessions/07-model-context-protocol/exercises/01_mcp_server.py
mcp dev sessions/07-model-context-protocol/exercises/03_document_mcp_server.py
```
