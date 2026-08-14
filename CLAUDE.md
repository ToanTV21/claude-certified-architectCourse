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
├── build-with-claude-api/       ← COURSE 1: Build with Claude API (FPT / ôn CCA-F)
│   │                             1 folder / session (major course section)
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
├── claude-code-in-action/      ← COURSE 2: Claude Code in Action (Anthropic)
│   ├── README.md               ← index + progress table của khóa này
│   ├── 00-course-overview/
│   ├── 01-steer-the-work/
│   ├── 02-configure-claude/
│   ├── 03-automate-repeat-work/
│   ├── 04-verify-and-share/
│   └── 05-course-quiz/
│       (mỗi NN-ten-section/ có notes.md + exercises/ + images/ riêng)
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
## Curriculum Progress
Workspace này chứa **2 khóa học**, mỗi khóa 1 folder riêng ở top level:

| Khóa | Folder | Progress table |
|------|--------|----------------|
| Build with Claude API (FPT Claude Code Developer → thi CCA-F) | `build-with-claude-api/` | [README.md](README.md) |
| Claude Code in Action (Anthropic) | `claude-code-in-action/` | [claude-code-in-action/README.md](claude-code-in-action/README.md) |

Tiến độ từng session/section (status, nội dung chính) ghi trong progress table tương ứng ở trên, không ghi ở đây.
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
python build-with-claude-api/01-accessing-claude-api/exercises/01_chat_exercise.py
# Start Claude Code interactive session
claude
# Run Claude Code on specific task
claude "review my MCP server implementation in build-with-claude-api/07-model-context-protocol/exercises/"
# Continue last session
claude --continue
```
---
## AI Behavior in This Project
Khi làm việc trong project này, Claude Code nên:
1. **Ưu tiên dùng `claude-haiku-4-5`** cho các bài tập dev/test để tiết kiệm cost
2. **Luôn dùng `python-dotenv`** để load API key, không bao giờ hardcode
3. **Viết code có comments giải thích** vì đây là môi trường học — mỗi đoạn code, mỗi hàm, và mỗi parameter bên trong đều phải có comment giải thích rõ nó làm gì / dùng để làm gì, không để code trơ trụi không chú thích
4. **Khi tạo file note mới** dùng template trong `build-with-claude-api/_session-template.md`
5. **Khi tạo bài tập mới** đặt trong đúng `NN-ten-session/exercises/` folder của khóa tương ứng
5b. **Chọn đúng khóa** — note/bài tập về **Claude API** (SDK, prompt, tool use, RAG, MCP server code) → `build-with-claude-api/`; note về **cách vận hành Claude Code** (CLAUDE.md, skills, permission modes, hooks, headless, routines, plugins, GitHub Actions) → `claude-code-in-action/`
6. **Sau khi làm xong bài tập** cập nhật status trong progress table của khóa đó (`README.md` hoặc `claude-code-in-action/README.md`), không phải CLAUDE.md
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
Mỗi `notes.md` trong `build-with-claude-api/NN-ten-session/` theo cấu trúc:
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
Mỗi file trong `build-with-claude-api/NN-ten-session/exercises/` theo cấu trúc:
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
