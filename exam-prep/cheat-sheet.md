# CCA-F Cheat Sheet — Quick Reference

## Models (ví dụ, kiểm tra tên chính thức mới nhất trước khi thi)
| Model | Dùng khi |
|-------|----------|
| `claude-haiku-4-5` | Dev/test, task đơn giản, cần tốc độ + rẻ |
| `claude-sonnet-4-6` | Task chính, cần chất lượng cao hơn |
| `claude-opus-*` | Task phức tạp nhất, sẵn sàng đánh đổi chi phí/tốc độ |

## Messages API — tham số chính
```python
client.messages.create(
    model="claude-haiku-4-5",   # required
    max_tokens=1024,             # required
    system="...",                # optional, TOP-LEVEL, không nằm trong messages
    messages=[...],              # required, list of {"role", "content"}
    temperature=1.0,             # optional, default 1.0 (KHÔNG phải 0.7)
    tools=[...],                 # optional
    tool_choice={"type": "auto"},# optional
    stream=False,                # optional
)
```

## `tool_choice` syntax
| Value | Ý nghĩa |
|-------|---------|
| `{"type": "auto"}` | Claude tự quyết định gọi tool hay không (mặc định khi có `tools`) |
| `{"type": "any"}` | Bắt buộc gọi 1 trong các tool đã cung cấp |
| `{"type": "tool", "name": "X"}` | Bắt buộc gọi đúng tool tên `X` |
| `{"type": "none"}` | Cấm gọi tool, chỉ trả lời text |

## Streaming events (thứ tự)
```
message_start
  content_block_start
    content_block_delta   ← text/tool input nằm ở đây
  content_block_stop
message_delta
message_stop
```

## Vai trò trong `messages` — 3 loại
- `user` — tin nhắn người dùng **và** tool result (KHÔNG có `role: "tool"` riêng!):
  ```json
  {"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "toolu_01...", "content": "..."}
  ]}
  ```
- `assistant` — phản hồi model, gồm cả `tool_use` block.
- `system` — top-level param HOẶC chèn thẳng vào `messages` giữa hội thoại (để thêm chỉ dẫn mà
  không phá cache prefix). Quy tắc vị trí: phải theo sau lượt `user`/`tool_result`; phải đứng
  trước lượt `assistant` hoặc là phần tử cuối; KHÔNG được chen giữa `tool_use` và `tool_result`
  tương ứng (→ lỗi 400). `system` xuất hiện sau ưu tiên hơn cái trước và hơn cả top-level `system`.

## `stop_reason` — điều khiển agentic loop
| Giá trị | Ý nghĩa | Hành động |
|---|---|---|
| `end_turn` | Model xong | Hiển thị cho user, **dừng loop** |
| `tool_use` | Model muốn gọi tool | Chạy tool, nối kết quả, **lặp lại** |
| `max_tokens` | Cắt do giới hạn | Có thể cần tăng `max_tokens` |
| `stop_sequence` | Gặp stop sequence | Tùy logic app |
- Agentic loop CHỈ nên tin `stop_reason`, KHÔNG parse text để đoán "đã xong", KHÔNG dùng
  `max_iterations` tùy ý làm điều kiện dừng chính.

## MCP — 3 primitives
| Primitive | Ai kiểm soát | Giống với |
|-----------|--------------|-----------|
| Resources | Application | GET endpoint / "bản đồ" dữ liệu |
| Tools     | Model (Claude) | POST endpoint / function call |
| Prompts   | User | Slash command / template |

**MCP server config:**
- `.mcp.json` (project root) — VCS, dùng chung nhóm, secret qua env var `${VAR}` (không commit token thật).
- `~/.claude.json` (user home) — không VCS, dùng cho server cá nhân/thử nghiệm.
- `isError: true` + lỗi có cấu trúc (`errorCategory`, `isRetryable`, `message`) > lỗi chung chung.

## Claude Agent SDK — Hooks vs Prompt
| | Hooks | Chỉ dẫn trong prompt |
|---|---|---|
| Đảm bảo | **Deterministic (100%)** | Xác suất (>90%, không phải 100%) |
| Dùng khi | Quy tắc tài chính/pháp lý/an toàn (vd chặn refund > $500) | Tùy chọn chung, khuyến nghị |
- `PostToolUse` hook: chuẩn hóa/cắt gọn tool result trước khi model thấy.
- Subagent (tool `Task`) có **context TÁCH BIỆT** — không tự kế thừa lịch sử coordinator, phải
  truyền tường minh. `allowed_tools` của coordinator phải chứa `"Task"`.

## Claude Code — CLAUDE.md phân cấp
| Cấp | Path | VCS | Phạm vi |
|---|---|---|---|
| User | `~/.claude/CLAUDE.md` | Không | Chỉ 1 người dùng |
| Project | `.claude/CLAUDE.md` hoặc root `CLAUDE.md` | Có | Mọi người trong repo |
| Directory | `CLAUDE.md` trong thư mục con | Có | Chỉ khi làm việc ở thư mục đó |
- Lỗi thường gặp: hướng dẫn chỉ ở cấp User → thành viên mới clone repo không thấy được.
- `@path` import file vào CLAUDE.md (không cách sau `@`, lồng tối đa 5 cấp).
- `.claude/rules/*.md` + YAML frontmatter `paths: ["glob"]` → nạp CÓ ĐIỀU KIỆN theo file đang
  sửa — dùng khi quy ước trải rộng nhiều thư mục (vd test file nằm rải rác khắp repo).

## Claude Code — Rules vs Skills vs Commands
| | Rules (CLAUDE.md) | Skills / Commands (`/name`) |
|---|---|---|
| Nạp vào context | Luôn luôn | Chỉ khi gọi `/name` |
| Mục đích | Context/convention cố định | Workflow theo yêu cầu |
| Chi phí token | Cao hơn (luôn tốn) | Thấp hơn (lazy load) |
| Vị trí project | `.claude/CLAUDE.md` | `.claude/commands/` hoặc `.claude/skills/` |
| Vị trí cá nhân | `~/.claude/CLAUDE.md` | `~/.claude/commands/` hoặc `~/.claude/skills/` |
- Skill frontmatter: `context: fork` (chạy trong subagent tách biệt, output dài không nhiễu
  session chính), `allowed-tools` (giới hạn tool), `argument-hint`.
- ⚠️ Skill cá nhân **cùng tên** với skill project sẽ ÂM THẦM che khuất bản của nhóm — đặt tên
  khác (vd `/my-commit`) để tránh mất update.

## Planning mode vs Thực thi trực tiếp
- **Planning mode**: chỉ Read/Grep/Glob, không side-effect, tạo plan để duyệt. Dùng cho: thay
  đổi lớn (hàng chục file+), nhiều cách tiếp cận khả thi, quyết định kiến trúc, codebase lạ.
- **Thực thi trực tiếp**: task đơn giản, rõ ràng, 1 file.
- Subagent **Explore**: cô lập output khám phá dài dòng, chỉ trả tóm tắt — tránh cạn context.

## Claude Code CLI cho CI/CD
- `-p` / `--print` — **cách duy nhất đúng** để chạy non-interactive (không có `--batch`,
  không có `CLAUDE_HEADLESS`).
- `--output-format json` + `--json-schema` — structured output parse được để đăng comment PR.
- Dùng **instance độc lập** để review code (không phải chính session đã sinh ra code đó) —
  session sinh code giữ context lý luận, ít phản biện chính mình.

## Batch API
| Thuộc tính | Giá trị |
|---|---|
| Tiết kiệm | **50%** so với đồng bộ |
| Cửa sổ xử lý | Tới **24 giờ**, KHÔNG có SLA latency |
| Tool nhiều lượt | **KHÔNG hỗ trợ** (không thể chặn giữa request để chạy tool rồi tiếp tục) |
| Tương quan | `custom_id` |
- Dùng cho: KHÔNG chặn (báo cáo qua đêm, audit hàng tuần). **KHÔNG BAO GIỜ** dùng cho bước
  chặn merge PR / cần phản hồi ngay.

## Prompt Engineering
- **Few-shot**: 2–4 ví dụ input/output — tốt cho kịch bản mơ hồ, định dạng output, phân biệt
  pattern chấp nhận được/có vấn đề.
- **Explicit criteria**: liệt kê rõ "flag khi nào / không flag khi nào" — tốt hơn hướng dẫn mơ hồ
  kiểu "hãy thận trọng hơn".
- **Prompt chaining** (per-file → integration pass) tránh **attention dilution** khi review
  nhiều file cùng lúc — KHÔNG sửa bằng cách dùng model to hơn/context lớn hơn.
- JSON Schema qua `tool_use`: đảm bảo cú pháp, KHÔNG đảm bảo ngữ nghĩa (giá trị vẫn có thể sai).
  Chỉ đánh dấu `required` khi luôn có sẵn; dùng `["string","null"]` cho trường có thể vắng mặt.

## Context Management
- Trích "case facts" (số liệu/ID/ngày) ra 1 block riêng, đưa vào MỌI prompt — tránh mất khi tóm tắt.
- Đặt thông tin quan trọng ở ĐẦU/CUỐI input dài (lost-in-the-middle).
- Cắt gọn tool output xuống field liên quan (hook `PostToolUse`).
- API stateless tuyệt đối — không có bộ nhớ phía server, phải gửi lại toàn bộ `messages`.

## Escalation — tín hiệu đáng tin cậy vs KHÔNG đáng tin cậy
| Đáng tin cậy | KHÔNG đáng tin cậy |
|---|---|
| Yêu cầu tường minh ("gặp quản lý") | Phân tích cảm xúc |
| Lỗ hổng chính sách | Model tự đánh giá confidence 1-10 |
| Nhiều kết quả khớp (hỏi thêm định danh) | Bộ classifier riêng (overengineering) |

## Gotchas cần nhớ
- Temperature default = `1.0`, không phải `0.7`.
- `system` là top-level param HOẶC chèn giữa `messages` (có quy tắc vị trí nghiêm ngặt).
- `system=None` tường minh → có thể lỗi validation, nên bỏ hẳn param.
- Text streaming chỉ nằm trong `content_block_delta`.
- API là stateless — client tự quản lý lịch sử hội thoại.
- Tool result luôn là `role: "user"` + `tool_result` block — KHÔNG có `role: "tool"`.
- CLAUDE.md project-level ≠ user-level — nhầm cấp là lỗi hay gặp nhất trong đề thi.
- Batch API không hỗ trợ tool calling nhiều lượt trong 1 request.
