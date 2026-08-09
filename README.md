# FPT Claude Code Developer — Study Project

Workspace học + ghi chú + làm bài tập cho khóa **FPT Claude Code Developer**,
chuẩn bị thi **CCA-F (Claude Certified Associate – Foundations)**.

- **Owner:** ToanTV — Senior Android Automotive Engineer, FPT Software Japan
- **Target:** Pass CCA-F (720/1000) by end of Q3 2026
- **Stack:** Python 3.10+, `anthropic` SDK, `python-dotenv`

Chi tiết layout, conventions, và AI behavior khi làm việc trong project này:
xem [CLAUDE.md](CLAUDE.md).

## Quick Start

```bash
git clone <repo-url>
cd buildwithClaudeAPI
pip install -r requirements.txt
cp .env.example .env   # rồi điền ANTHROPIC_API_KEY của bạn
python src/client.py   # health check — in ra response mẫu từ Claude
```

## Curriculum Progress

Mỗi session của khóa học nằm trong 1 folder riêng dưới `sessions/`, gồm
`notes.md` (ghi chú lý thuyết) + `exercises/` (code chạy thử).

| # | Session folder | Section | Status |
|---|-----------------|---------|--------|
| 00 | [sessions/00-course-overview](sessions/00-course-overview/notes.md) | Course Overview | ⬜ Todo |
| 01 | [sessions/01-accessing-claude-api](sessions/01-accessing-claude-api/notes.md) | Accessing Claude with the API | ✅ Done |
| 02 | [sessions/02-prompt-evaluation](sessions/02-prompt-evaluation/notes.md) | Prompt Evaluation | 🔄 In progress |
| 03 | [sessions/03-prompt-engineering-techniques](sessions/03-prompt-engineering-techniques/notes.md) | Prompt Engineering Techniques | ⬜ Todo |
| 04 | [sessions/04-tool-use-with-claude](sessions/04-tool-use-with-claude/notes.md) | Tool Use with Claude | ⬜ Todo |
| 05 | [sessions/05-rag-and-agentic-search](sessions/05-rag-and-agentic-search/notes.md) | RAG and Agentic Search | ⬜ Todo |
| 06 | [sessions/06-features-of-claude](sessions/06-features-of-claude/notes.md) | Features of Claude | ⬜ Todo |
| 07 | [sessions/07-model-context-protocol](sessions/07-model-context-protocol/notes.md) | Model Context Protocol | ⬜ Todo |
| 08 | [sessions/08-anthropic-apps-claude-code](sessions/08-anthropic-apps-claude-code/notes.md) | Anthropic Apps — Claude Code & Computer Use | ⬜ Todo |
| 09 | [sessions/09-agents-and-workflows](sessions/09-agents-and-workflows/notes.md) | Agents and Workflows | ⬜ Todo |
| 10 | [sessions/10-final-assessment](sessions/10-final-assessment/notes.md) | Final Assessment | ⬜ Todo |
| 11 | [sessions/11-wrapping-up](sessions/11-wrapping-up/notes.md) | Wrapping Up | ⬜ Todo |

## Layout

- `sessions/` — 1 folder / session: `notes.md` + `exercises/`
- `exam-prep/` — ôn thi CCA-F ([flashcards](exam-prep/flashcards.md),
  [cheat-sheet](exam-prep/cheat-sheet.md),
  [practice questions](exam-prep/practice-questions.md),
  [wrong answers log](exam-prep/wrong-answers.md),
  [official guide references](exam-prep/references.md))
- `src/` — shared utilities (Anthropic client)
