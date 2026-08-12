# CLAUDE.md — FPT Claude Code Developer Study Project
## Project Purpose
Đây là workspace học + ghi chú + làm bài tập cho khóa **FPT Claude Code Developer**
và chuẩn bị thi **CCA-F (Claude Certified Associate – Foundations)**.
**Owner:** ToanTV — Senior Android Automotive Engineer, FPT Software Japan  
**Target:** Pass CCA-F (720/1000) by end of Q3 2026  
**Stack:** Python 3.10+, `anthropic` SDK, `python-dotenv`
---
## Directory Layout
```
fpt-claude-study/
├── CLAUDE.md                   ← You are here (project context)
├── .env                        ← API key (gitignored)
├── .env.example
├── .gitignore
├── requirements.txt
│
├── sessions/                   ← 1 folder / session (major course section)
│   ├── _session-template.md
│   ├── 00-course-overview/
│   │   └── notes.md
│   ├── 01-accessing-claude-api/
│   │   ├── notes.md
│   │   └── exercises/
│   ├── 02-prompt-evaluation/
│   ├── 03-prompt-engineering-techniques/
│   ├── 04-tool-use-with-claude/
│   ├── 05-rag-and-agentic-search/
│   ├── 06-features-of-claude/
│   ├── 07-model-context-protocol/
│   ├── 08-anthropic-apps-claude-code/
│   ├── 09-agents-and-workflows/
│   ├── 10-final-assessment/
│   └── 11-wrapping-up/
│       (mỗi session-NN/ có notes.md + exercises/ riêng)
│
├── exam-prep/                  ← Ôn thi CCA-F
│   ├── flashcards.md           ← Q&A nhanh
│   ├── practice-questions.md   ← Mock exam questions
│   ├── cheat-sheet.md          ← Quick reference
│   └── wrong-answers.md        ← Ghi lại câu sai để ôn lại
│
└── src/                        ← Shared utilities
    ├── __init__.py
    └── client.py               ← Khởi tạo Anthropic client dùng chung
```
---
## Curriculum Map
| # | Session folder | Section | Status |
|---|-----------------|---------|--------|
| 00 | `sessions/00-course-overview/` | Course Overview | ⬜ Todo |
| 01 | `sessions/01-accessing-claude-api/` | Accessing Claude with the API | ✅ Done |
| 02 | `sessions/02-prompt-evaluation/` | Prompt Evaluation | ✅ Done |
| 03 | `sessions/03-prompt-engineering-techniques/` | Prompt Engineering Techniques | ✅ Done |
| 04 | `sessions/04-tool-use-with-claude/` | Tool Use with Claude | 🔄 In progress |
| 05 | `sessions/05-rag-and-agentic-search/` | RAG and Agentic Search | ⬜ Todo |
| 06 | `sessions/06-features-of-claude/` | Features of Claude | ⬜ Todo |
| 07 | `sessions/07-model-context-protocol/` | Model Context Protocol | ⬜ Todo |
| 08 | `sessions/08-anthropic-apps-claude-code/` | Anthropic Apps — Claude Code & Computer Use | ⬜ Todo |
| 09 | `sessions/09-agents-and-workflows/` | Agents and Workflows | ⬜ Todo |
| 10 | `sessions/10-final-assessment/` | Final Assessment | ⬜ Todo |
| 11 | `sessions/11-wrapping-up/` | Wrapping Up | ⬜ Todo |
Update status khi hoàn thành mỗi session.
---
## CCA-F Exam Overview
- **Format:** 60 câu, 120 phút, passing score 720/1000
- **Domains:**
| Domain | Weight |
|--------|--------|
| Agentic Architecture & Orchestration | 27% |
| Claude Code Configuration & Workflows | 20% |
| Prompt Engineering & Structured Output | 20% |
| Tool Design & MCP Integration | 18% |
| Context Management & Reliability | 15% |
- **Official study guide (VN):** https://github.com/ToanTV21/claude-certified-architect/blob/main/guide_vi.md
  — xem tóm tắt trong `exam-prep/references.md`.
- **High-risk topics cần chú ý:**
  - `tool_choice` mechanics và deterministic pipeline patterns
  - Claude Code: rules vs skills distinction
  - Batch API fire-and-forget architecture
  - Few-shot vs explicit criteria selection
  - Root-cause resolution design principles
---
## Coding Conventions
### Python Setup
```python
# Mọi script đều dùng pattern này
from dotenv import load_dotenv
import anthropic
import os
load_dotenv()
client = anthropic.Anthropic()  # tự đọc ANTHROPIC_API_KEY từ .env
# Dev: dùng haiku để tiết kiệm cost
# Prod/test: dùng sonnet
MODEL_DEV  = "claude-haiku-4-5"
MODEL_MAIN = "claude-sonnet-4-6"
```
### Key Gotchas (luôn nhớ)
| Gotcha | Đúng | Sai |
|--------|------|-----|
| Temperature default | `1.0` | `0.7` |
| `system` field | top-level param, không nằm trong `messages` | `messages[0]["role"] = "system"` |
| `system=None` | → validation error | bỏ qua |
| Streaming text | chỉ trong `ContentBlockDelta` events | các event khác |
| `tool_choice` force | `{"type": "tool", "name": "..."}` | `{"type": "auto"}` |
---
## Common Commands
```bash
# Setup
pip install -r requirements.txt
# Run an exercise
python sessions/01-accessing-claude-api/exercises/01_chat_exercise.py
# Start Claude Code interactive session
claude
# Run Claude Code on specific task
claude "review my MCP server implementation in sessions/07-model-context-protocol/exercises/"
# Continue last session
claude --continue
```
---
## AI Behavior in This Project
Khi làm việc trong project này, Claude Code nên:
1. **Ưu tiên dùng `claude-haiku-4-5`** cho các bài tập dev/test để tiết kiệm cost
2. **Luôn dùng `python-dotenv`** để load API key, không bao giờ hardcode
3. **Viết code có comments giải thích** vì đây là môi trường học — mỗi đoạn code, mỗi hàm, và mỗi parameter bên trong đều phải có comment giải thích rõ nó làm gì / dùng để làm gì, không để code trơ trụi không chú thích
4. **Khi tạo file note mới** dùng template trong `sessions/_session-template.md`
5. **Khi tạo bài tập mới** đặt trong đúng `sessions/NN-ten-session/exercises/` folder
6. **Sau khi làm xong bài tập** cập nhật status trong CLAUDE.md
6b. **Sau mỗi lần write/edit file** phải `git add` + `git commit` (message ngắn gọn mô tả thay đổi) rồi `git push` lên remote GitHub ngay, không gộp nhiều thay đổi rồi mới commit 1 lần
7. **Ngôn ngữ:**
   - **Khi chat trực tiếp với user** (trả lời câu hỏi, giải thích, thảo luận trong conversation): luôn dùng **tiếng Anh**.
   - **Khi ghi note vào file** (notes.md, file `.md` giải thích code, comment trong file...): luôn viết phần giải thích bằng **tiếng Việt**. Các keyword/thuật ngữ kỹ thuật (tên API, param, class, method, tên field, tên sự kiện...) giữ nguyên **tiếng Anh**, không dịch. Vd: "**Tokenization** là bước cắt input text thành các **token** nhỏ" — không viết "Token hoá" hay dịch "token" sang tiếng Việt.
8. **Khi user yêu cầu "giải thích chi tiết code"** (vd bài tập vừa viết, đoạn code Python trong exercises/), áp dụng đúng format sau:
   - Explain theo **từng đoạn code ngắn** (1 block nhỏ mỗi lần — vd 1 dòng khai báo hàm, 1 vòng lặp, 1 câu lệnh điều kiện), không giải thích dồn cả hàm/file trong 1 đoạn văn dài
   - Với mỗi đoạn: trích lại code block đó trước, rồi giải thích ý nghĩa từng phần/cú pháp bên dưới
   - **User là Senior Android Automotive Engineer, code chính là Java** — nên khi giải thích cú pháp Python lạ (type hints, dict unpacking `**kwargs`, list comprehension, decorator, context manager, `async/await`...), nếu có khái niệm tương đương hoặc gần giống trong **Java/Android/Android Automotive (AAOS)** thì nên đối chiếu ngắn gọn để dễ liên tưởng (vd: Python dict ~ Java `HashMap`/JSON object; Python `**kwargs` unpack ~ Java Builder pattern hoặc varargs; Python `None` ~ Java `null`; Python list ~ Java `List`/`ArrayList`). Không bắt buộc ví dụ Java cho mọi dòng — chỉ dùng khi thực sự giúp hiểu nhanh hơn, tránh gượng ép
   - Kết thúc bằng phần **"Tóm tắt luồng chạy"** ngắn gọn, liệt kê các bước theo thứ tự
   - Nếu file đích là 1 bài tập trong `exercises/`, lưu toàn bộ phần giải thích này vào file `.md` riêng cùng cấp, đặt tên theo pattern `<tên_file_exercise>_notes.md` (vd `02_system_prompts_exercise.py` → `02_system_prompts_exercise_notes.md`), rồi git add/commit/push theo rule 6b
---
## Note-Taking Template
Mỗi `notes.md` trong `sessions/NN-ten-session/` theo cấu trúc:
```markdown
# Module X: [Tên Module]
## Key Concepts
- Concept 1: ...
- Concept 2: ...
## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
## Gotchas
- [ ] Gotcha 1
- [ ] Gotcha 2
## CCA-F Exam Tips
- ...
## Code Snippets
\`\`\`python
# snippet
\`\`\`
## Questions / Unclear Points
- ?
```
---
## Exercise Template
Mỗi file trong `sessions/NN-ten-session/exercises/` theo cấu trúc:
```python
"""
Exercise XX-YY: [Tên bài tập]
Module: [Tên module]
Objective: [Mục tiêu]
"""
from dotenv import load_dotenv
import anthropic
load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5"  # dùng haiku cho dev
def main():
    # TODO: implement
    pass
if __name__ == "__main__":
    main()
```
