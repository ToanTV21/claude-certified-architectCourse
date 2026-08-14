# Claude Code in Action — Study Notes

Workspace ghi chú + thực hành cho khóa **Claude Code in Action** (Anthropic).
Khóa này khác với khóa `build-with-claude-api/` (FPT Claude Code Developer / ôn CCA-F): thay vì học
**Claude API**, khóa này tập trung vào cách *vận hành* **Claude Code** trong công việc thật.

- **Owner:** ToanTV — Senior Android Automotive Engineer, FPT Software Japan
- **Bắt đầu:** 2026-08-14

## Progress

| # | Section folder | Section | Lessons | Status |
|---|----------------|---------|---------|--------|
| 00 | [00-course-overview](00-course-overview/notes.md) | Course Overview | Course Overview | ⬜ Todo |
| 01 | [01-steer-the-work](01-steer-the-work/notes.md) | Steer the Work | Steering Long Sessions | 🔄 In progress |
| 02 | [02-configure-claude](02-configure-claude/notes.md) | Configure Claude | A CLAUDE.md That Follows · Verification Skills · Permission Modes · Hooks | ⬜ Todo |
| 03 | [03-automate-repeat-work](03-automate-repeat-work/notes.md) | Automate Repeat Work | Routines and Headless · GitHub Actions and Code Review | ⬜ Todo |
| 04 | [04-verify-and-share](04-verify-and-share/notes.md) | Verify and Share | Trust It: Verifying Unsupervised Runs · Plugins | ⬜ Todo |
| 05 | [05-course-quiz](05-course-quiz/notes.md) | Quiz | Course Quiz | ⬜ Todo |

## Layout

Mỗi section 1 folder, cùng convention với `build-with-claude-api/` của khóa cũ:

```
claude-code-in-action/
└── NN-ten-section/
    ├── notes.md      ← ghi chú lý thuyết (tiếng Việt, keyword giữ tiếng Anh)
    ├── exercises/    ← code / config chạy thử
    └── images/       ← screenshot slide, terminal output
```

## Convention khi ghi note

Theo đúng [CLAUDE.md](../CLAUDE.md) của project:
- Note viết **tiếng Việt**, keyword kỹ thuật giữ nguyên **tiếng Anh** (`CLAUDE.md`, `hooks`,
  `permission mode`, `headless`, `plugin`...).
- Mỗi lần write/edit file → `git add` + `git commit` + `git push` ngay.
- Bài tập/config thực hành đặt trong `exercises/` của đúng section.
