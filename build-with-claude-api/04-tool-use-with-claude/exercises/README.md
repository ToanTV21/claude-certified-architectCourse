# Exercises — Tool Use with Claude

- `01_tool_functions_and_schemas.py` — Define tool functions + schemas, handle
  message blocks, send tool results back (single tool, single turn).
- `02_multi_turn_tool_conversation.py` — Implementing multiple turns with tool use
  in a loop until Claude stops requesting tools.
- `03_using_multiple_tools.py` — Give Claude more than one tool and let it choose
  (fine-grained tool calling).
- `04_batch_tool.py` — Define a virtual "batch" tool so Claude can invoke multiple
  real tools in a single message instead of sequential round-trips.
- `05_structured_data_tool.py` — Force Claude to always call one tool via
  `tool_choice` to reliably extract structured (JSON) data from free text.
- `09_sending_tool_results.py` — Focused walkthrough of "Sending tool results":
  extracting `tool_use.input`, unpacking `**kwargs`, building `tool_result` blocks
  (`tool_use_id` / `content` / `is_error`), and matching results when Claude
  requests multiple tool calls in a single message.
- `10_conversation_loop_chat_helper.py` — Refactored `chat()`/message helpers +
  `run_conversation()` while-loop to chain multiple tool calls automatically until
  `stop_reason != "tool_use"`.
- `11_web_search_tool.py` — Built-in Web Search Tool: no custom implementation
  needed, `allowed_domains` to restrict sources, and reading the 4 response block
  types (text / server_tool_use / web_search_tool_result / citations).
