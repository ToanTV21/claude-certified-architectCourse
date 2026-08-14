# Claude Certification Guide — Study Notes

## Nguồn
Toàn bộ note trong folder này được scrape và tổng hợp từ **https://claudecertificationguide.com/** — một trang học liệu **miễn phí, độc lập** (không phải của FPT hay Anthropic chính thức) chuyên ôn thi **CCAR-F (Claude Certified Architect – Foundations)**. Trang có kèm **mock exam** (câu hỏi trắc nghiệm mô phỏng đề thi thật) cho từng domain.

> Lưu ý: Folder này **tách biệt hoàn toàn** với 2 khóa học chính của workspace (`build-with-claude-api/` — khóa FPT Claude Code Developer, và `claude-code-in-action/` — khóa Claude Code in Action của Anthropic). Đây là tài liệu tham khảo bổ sung từ nguồn thứ ba, dùng để ôn thi chéo/đối chiếu thêm góc nhìn khi luyện CCA-F.

## 5 Domain & Trọng số thi

| Domain | Tên | Trọng số |
|---|---|---|
| 1 | Agentic Architecture & Orchestration | 27% |
| 2 | Tool Design & MCP Integration | 18% |
| 3 | Claude Code Configuration & Workflows | 20% |
| 4 | Prompt Engineering & Structured Output | 20% |
| 5 | Context Management & Reliability | 15% |

## Index — Note theo từng Domain

- [01-agentic-architecture.md](01-agentic-architecture.md) — Domain 1: Agentic Architecture & Orchestration (27%)
  - 1.1 Agentic Loops
  - 1.2 Orchestration Patterns
  - 1.3 Subagent Invocation & Context Passing
  - 1.4 Workflow Enforcement & Handoff
  - 1.5 Agent SDK Hooks
  - 1.6 Task Decomposition
  - 1.7 Session State & Resumption

- [02-tool-design-mcp.md](02-tool-design-mcp.md) — Domain 2: Tool Design & MCP Integration (18%)
  - 2.1 Tool Schema / Interface Design
  - 2.2 Structured Error Responses
  - 2.3 Tool Distribution & Tool Choice
  - 2.4 MCP Server Integration
  - 2.5 Built-in Tools (Read/Write/Edit/Bash/Grep/Glob)

- [03-claude-code-config.md](03-claude-code-config.md) — Domain 3: Claude Code Configuration & Workflows (20%)
  - 3.1 CLAUDE.md Hierarchy
  - 3.2 Slash Commands & Skills
  - 3.3 Path-Specific Rules
  - 3.4 Plan Mode vs Direct Execution
  - 3.5 Iterative Refinement
  - 3.6 CI/CD Integration

- [04-prompt-engineering.md](04-prompt-engineering.md) — Domain 4: Prompt Engineering & Structured Output (20%)
  - 4.1 System Prompts với Explicit Criteria
  - 4.2 Few-Shot Prompting
  - 4.3 Structured Output với Tool Use
  - 4.4 Validation, Retry & Feedback Loops
  - 4.5 Batch Processing Strategies
  - 4.6 Multi-Instance & Multi-Pass Review

- [05-context-management.md](05-context-management.md) — Domain 5: Context Management & Reliability (15%)
  - 5.1 Context Window Management
  - 5.2 Escalation & Ambiguity Resolution
  - 5.3 Error Propagation (Multi-Agent)
  - 5.4 Codebase Exploration & Context Degradation
  - 5.5 Human Review & Confidence Calibration
  - 5.6 Information Provenance & Multi-Source Synthesis

## Quy ước
- Prose giải thích viết bằng **tiếng Việt**, giữ nguyên **tiếng Anh** cho các keyword/thuật ngữ kỹ thuật (tên API, param, field, tool, event...) — theo đúng convention của `CLAUDE.md` ở repo root.
- Mỗi lesson gồm: khái niệm cốt lõi, bảng/so sánh, code example, anti-pattern, exam trap, và practice scenario (nếu trang gốc có).
