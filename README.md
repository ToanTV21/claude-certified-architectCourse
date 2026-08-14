# Claude Study Workspace — ToanTV

Workspace học + ghi chú + làm bài tập cho các khóa Claude, chuẩn bị thi
**CCA-F (Claude Certified Associate – Foundations)**.

- **Owner:** ToanTV — Senior Android Automotive Engineer, FPT Software Japan
- **Target:** Pass CCA-F (720/1000) by end of Q3 2026
- **Stack:** Python 3.10+, `anthropic` SDK, `python-dotenv`

Chi tiết layout, conventions, và AI behavior khi làm việc trong project này:
xem [CLAUDE.md](CLAUDE.md).

## Khóa học trong workspace

| Khóa | Folder | Nội dung | Progress |
|------|--------|----------|----------|
| **Build with Claude API** (FPT Claude Code Developer) | [build-with-claude-api/](build-with-claude-api/) | Gọi **Claude API** bằng SDK: prompt engineering, eval, tool use, RAG, MCP, agents & workflows | [bảng dưới ↓](#build-with-claude-api--curriculum-progress) |
| **Claude Code in Action** (Anthropic) | [claude-code-in-action/](claude-code-in-action/README.md) | Vận hành **Claude Code**: steering, CLAUDE.md, skills, permission modes, hooks, headless/routines, GitHub Actions, plugins | [claude-code-in-action/README.md](claude-code-in-action/README.md) |

## Quick Start

```bash
git clone <repo-url>
cd buildwithClaudeAPI
pip install -r requirements.txt
cp .env.example .env   # rồi điền ANTHROPIC_API_KEY của bạn
python src/client.py   # health check — in ra response mẫu từ Claude
```

## Build with Claude API — Curriculum Progress

Mỗi session của khóa học nằm trong 1 folder riêng dưới `build-with-claude-api/`, gồm
`notes.md` (ghi chú lý thuyết) + `exercises/` (code chạy thử).

| # | Session folder | Section | Status | Nội dung chính |
|---|-----------------|---------|--------|----------------|
| 00 | [build-with-claude-api/00-course-overview](build-with-claude-api/00-course-overview/notes.md) | Course Overview | ⬜ Todo | Giới thiệu tổng quan khóa học và giới thiệu về Anthropic — overview các dòng **Claude models** hiện có. |
| 01 | [build-with-claude-api/01-accessing-claude-api](build-with-claude-api/01-accessing-claude-api/notes.md) | Accessing Claude with the API | ✅ Done | Cách lấy **API key** và gọi **Claude API**: single request, **multi-turn conversations**, **system prompts**, **temperature**, **response streaming**, và **structured data** (output theo format cố định). |
| 02 | [build-with-claude-api/02-prompt-evaluation](build-with-claude-api/02-prompt-evaluation/notes.md) | Prompt Evaluation | ✅ Done | Quy trình **eval** một prompt: xây dựng **test dataset**, chạy eval, và hai cách chấm điểm — **model-based grading** (dùng LLM làm giám khảo) và **code-based grading** (chấm bằng logic code). |
| 03 | [build-with-claude-api/03-prompt-engineering-techniques](build-with-claude-api/03-prompt-engineering-techniques/notes.md) | Prompt Engineering Techniques | ✅ Done | Các kỹ thuật viết prompt hiệu quả: rõ ràng & trực tiếp (**clear and direct**), càng cụ thể càng tốt (**being specific**), cấu trúc prompt bằng **XML tags**, và kỹ thuật **few-shot** (đưa ví dụ mẫu). |
| 04 | [build-with-claude-api/04-tool-use-with-claude](build-with-claude-api/04-tool-use-with-claude/notes.md) | Tool Use with Claude | 🔄 In progress | Cho Claude gọi **tool/function**: định nghĩa **tool schema**, xử lý **message blocks**, gửi lại **tool results**, các vòng **multi-turn conversation** khi có tool, dùng nhiều tool cùng lúc, **fine-grained tool calling**, và 2 tool có sẵn — **text edit tool** và **web search tool**. |
| 05 | [build-with-claude-api/05-rag-and-agentic-search](build-with-claude-api/05-rag-and-agentic-search/notes.md) | RAG and Agentic Search | ⬜ Todo | **Retrieval Augmented Generation (RAG)**: chiến lược **text chunking**, **text embeddings**, dựng full RAG flow từ đầu, kết hợp **BM25** (lexical search) và pipeline **multi-index RAG**. |
| 06 | [build-with-claude-api/06-features-of-claude](build-with-claude-api/06-features-of-claude/notes.md) | Features of Claude | ⬜ Todo | Các tính năng nâng cao của Claude: **extended thinking**, đọc **image**/**PDF**, **citations** (trích dẫn nguồn), **prompt caching** (quy tắc + áp dụng thực tế), và **code execution** kết hợp **Files API**. |
| 07 | [build-with-claude-api/07-model-context-protocol](build-with-claude-api/07-model-context-protocol/notes.md) | Model Context Protocol | ✅ Done | Giới thiệu **MCP (Model Context Protocol)**: setup project, viết **MCP client**, định nghĩa **tools** qua MCP, dùng **server inspector** để debug, định nghĩa và truy cập **resources**, định nghĩa **prompts** và dùng chúng trong client. |
| 08 | [build-with-claude-api/08-anthropic-apps-claude-code](build-with-claude-api/08-anthropic-apps-claude-code/notes.md) | Anthropic Apps — Claude Code & Computer Use | 🔄 In progress | Các app do Anthropic xây dựng: setup và thực hành **Claude Code**, mở rộng khả năng của nó bằng cách kết nối thêm **MCP servers**. |
| 09 | [build-with-claude-api/09-agents-and-workflows](build-with-claude-api/09-agents-and-workflows/notes.md) | Agents and Workflows | ✅ Done | Các pattern xây **agentic workflow**: **parallelization**, **chaining**, **routing**, kết hợp agent với tool, kỹ thuật **environment inspection**, và so sánh **workflows vs agents** — khi nào dùng cái nào. |
| 10 | [build-with-claude-api/10-final-assessment](build-with-claude-api/10-final-assessment/notes.md) | Final Assessment | ✅ Done | Bài đánh giá tổng kết cuối khóa, ôn lại toàn bộ kiến thức đã học qua các session trước. |
| 11 | [build-with-claude-api/11-wrapping-up](build-with-claude-api/11-wrapping-up/notes.md) | Wrapping Up | ✅ Done | Tổng kết khóa học, nhìn lại lộ trình đã đi qua và định hướng bước tiếp theo. |

## Layout

- `build-with-claude-api/` — khóa Build with Claude API — 1 folder / session: `notes.md` + `exercises/`
- `claude-code-in-action/` — khóa Claude Code in Action — 1 folder / section: `notes.md` + `exercises/` + `images/`
- `exam-prep/` — ôn thi CCA-F — [**bản đồ ôn thi / thứ tự đọc**](exam-prep/README.md) ← bắt đầu từ đây
  ([study plan](exam-prep/study-plan.md),
  [flashcards](exam-prep/flashcards.md),
  [cheat-sheet](exam-prep/cheat-sheet.md),
  [practice questions](exam-prep/practice-questions.md),
  [mock exam log](exam-prep/mock-exam-log.md),
  [wrong answers log](exam-prep/wrong-answers.md),
  [official guide references](exam-prep/references.md))
- `src/` — shared utilities (Anthropic client)
