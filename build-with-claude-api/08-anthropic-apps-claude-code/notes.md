# Session 08: Anthropic Apps — Claude Code and Computer Use

## Lessons trong section này
- [x] Anthropic apps
- [x] Claude Code setup
- [x] Claude Code in action
- [x] Enhancements with MCP servers

## Key Concepts

### 1. Anthropic apps (overview)
Module này khảo sát 2 app do Anthropic xây dựng — **Claude Code** và **Computer Use** —
như 2 case study điển hình về AI agent trong thực tế. Hiểu cách chúng hoạt động sẽ là nền
tảng để tự xây dựng agent riêng ở các session sau (09-agents-and-workflows).

Kế hoạch của module (3 bước):
1. **Claude Code** — agentic coding assistant chạy trong terminal
2. **Computer Use** — bộ tool cho phép Claude tương tác với desktop environment
3. **Agents** — rút ra điều gì làm cho 2 app trên thành công, để áp dụng khi tự build agent

**Claude Code** có thể: edit file, fix bug, trả lời câu hỏi code, hỗ trợ dev workflow.

**Computer Use** mở rộng khả năng của Claude ra ngoài text-only — cho phép:
- Truy cập website / browse internet
- Tương tác với desktop application
- Thực hiện task cần visual interface navigation (click, type, screenshot...)

Cả 2 app đều minh hoạ các nguyên lý cốt lõi của agent:
- **Tool integration and usage** — dùng tool để hành động thay vì chỉ trả lời text
- **Multi-step task execution** — chia nhỏ task lớn thành nhiều bước
- **Environmental interaction** — đọc/ghi vào môi trường thực (file system, browser, desktop)
- **Autonomous problem-solving** — tự quyết định bước tiếp theo dựa trên kết quả bước trước

### 2. Claude Code — setup
Claude Code là coding assistant chạy trực tiếp trong terminal (dòng lệnh), cung cấp:
- **File operations** — search, read, edit file trong project
- **Terminal access** — chạy lệnh shell trực tiếp từ trong conversation
- **Web access** — search doc, fetch code example...
- **MCP Server support** — mở rộng tool bằng cách connect thêm MCP server

Chạy được trên MacOS, Windows WSL, và Linux.

**Cài đặt (3 bước):**
```bash
# 1. Cài Node.js (kiểm tra đã có chưa bằng: npm help)
# tải tại nodejs.org/en/download

# 2. Cài Claude Code (global npm package)
npm install -g @anthropic-ai/claude-code

# 3. Khởi động + login (lần đầu sẽ yêu cầu login vào tài khoản Anthropic)
claude
```

### 3. Claude Code — in action (workflow thực tế)
Claude Code không chỉ để viết code — nó đồng hành xuyên suốt vòng đời project: từ setup ban
đầu tới deploy và support, giống như "một kỹ sư nữa trong team".

**Lệnh `/init`:** quét toàn bộ codebase (structure, dependencies, coding style, architecture)
và tóm tắt lại thành file `CLAUDE.md` — file này tự động được nạp làm context cho mọi
conversation sau đó, giúp Claude "nhớ" thông tin quan trọng về project mà không cần lặp lại.

Có thể có nhiều cấp `CLAUDE.md`:
| Cấp | Mô tả |
|-----|-------|
| Project | Dùng chung cho cả team, checked into git |
| Local | Note cá nhân, không commit vào git |
| User | Áp dụng cho tất cả project của user |

Khi chạy `/init` có thể thêm hướng dẫn riêng để Claude tập trung vào phần nào đó. File
sinh ra sẽ gồm build commands, coding guideline, pattern riêng của project.

Lệnh nhanh `#` — thêm note trực tiếp vào `CLAUDE.md`. Vd gõ `# Always use descriptive
variable names` sẽ được hỏi lưu vào project / local / user memory.

**Workflow hiệu quả nhất (3 bước):**
1. **Feed context vào Claude** — trước khi yêu cầu build feature, chỉ ra các file liên quan
   trong codebase để Claude đọc trước (làm ví dụ về pattern code hiện có)
2. **Yêu cầu Claude lập plan** — bảo Claude nghĩ qua approach + step cần làm, **chưa viết code**
3. **Yêu cầu Claude implement** — dựa trên plan đã thống nhất, Claude viết code

**Test-Driven Development workflow (biến thể mạnh hơn):**
1. Feed context (như trên)
2. Yêu cầu Claude brainstorm test case sẽ validate feature mới
3. Chọn ra test case liên quan nhất, yêu cầu Claude viết test đó
4. Yêu cầu Claude viết code cho tới khi pass hết test

→ Cách này thường ra code robust hơn vì Claude có success criteria rõ ràng để nhắm tới.

**Ví dụ thực tế** — thêm tool `document_path_to_markdown`:
```
> Read the math.py and document.py files
> Plan to implement document_path_to_markdown tool: ...
> Implement the plan
```
Claude sẽ tạo function, cập nhật file liên quan, viết test, và chạy test suite để verify.

**Các lệnh hữu ích khác:**
| Lệnh | Chức năng |
|------|-----------|
| `/clear` | Xoá conversation history, reset context |
| `/init`  | Quét codebase, tạo `CLAUDE.md` |
| `#`      | Thêm note vào `CLAUDE.md` |

Claude Code cũng đảm nhiệm được các việc thường ngày: `git add`/`commit`, chạy test, quản
lý dependency — thay vì phải chuyển qua lại giữa editor và terminal.

### 4. Enhancements with MCP servers
Claude Code có **MCP client built-in**, cho phép kết nối MCP server để mở rộng khả năng
vượt ra ngoài tool có sẵn. Mỗi MCP server expose 3 loại thành phần: **Tools** (hành động),
**Prompts** (template), **Resources** (dữ liệu) — xem lại chi tiết ở session 07.

**Đăng ký MCP server:**
```bash
claude mcp add [server-name] [command-to-start-server]

# Vd server document processing khởi động bằng "uv run main.py"
claude mcp add documents uv run main.py
```
Sau khi add, Claude Code tự động connect tới server này mỗi lần khởi động.

**Ví dụ:** Server có tool `document_path_to_markdown` (đọc PDF/Word) — khi user yêu cầu
"Convert the tests/fixtures/mcp_docs.docx file to markdown", Claude tự động gọi tool này.

**Một số MCP server phổ biến trong dev workflow:**
| Server | Chức năng |
|--------|-----------|
| `sentry-mcp` | Tự động tìm và fix bug được log trong Sentry |
| `playwright-mcp` | Browser automation cho testing/troubleshooting |
| `figma-context-mcp` | Expose Figma design cho Claude |
| `mcp-atlassian` | Truy cập Confluence và Jira |
| `firecrawl-mcp-server` | Web scraping |
| `slack-mcp` | Post message / reply thread trong Slack |

→ Kết hợp nhiều MCP server phù hợp với workflow riêng (vd: Sentry để lấy lỗi production +
Jira để đọc requirement + Slack để báo team khi xong) biến Claude Code thành coding
assistant "may đo" theo đúng bộ tool/service mà team đang dùng.

## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
| `claude` | CLI command | — | Khởi động Claude Code, lần đầu sẽ yêu cầu login |
| `claude mcp add <name> <cmd>` | CLI command | — | Đăng ký 1 MCP server mới cho Claude Code |
| `/init` | slash command | — | Quét codebase, sinh/refresh `CLAUDE.md` |
| `/clear` | slash command | — | Xoá conversation history + reset context |
| `#<note>` | shortcut | — | Thêm note nhanh vào `CLAUDE.md` (project/local/user) |

## Gotchas
- [ ] `CLAUDE.md` có 3 cấp (Project / Local / User) — cấp Local không được commit vào git,
  dễ nhầm khi setup máy mới (phải tạo lại note cá nhân)
- [ ] Luôn nên qua bước **Plan** (dặn Claude "chưa viết code") trước khi để Claude implement —
  bỏ qua bước này dễ dẫn tới code sai hướng phải sửa lại nhiều lần

## Code Snippets
```bash
# Cài đặt Claude Code
npm install -g @anthropic-ai/claude-code
claude   # lần đầu sẽ yêu cầu login vào tài khoản Anthropic

# Trong project, quét codebase và sinh CLAUDE.md
> /init

# Thêm 1 MCP server (vd server document processing chạy bằng uv)
claude mcp add documents uv run main.py

# Workflow chuẩn: feed context -> plan -> implement
> Read the math.py and document.py files
> Plan to implement document_path_to_markdown tool: ... (chưa viết code)
> Implement the plan
```

## Questions / Unclear Points
- ?
