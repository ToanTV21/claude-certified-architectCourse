# Tài liệu tham khảo chính thức cho CCA-F

## Nguồn chính
- **CCA-F Study Guide (tiếng Việt):**
  https://github.com/ToanTV21/claude-certified-architect/blob/main/guide_vi.md
  (fork từ `paullarionov/claude-certified-architect`)
- File này (`references.md`) là bản tổng hợp đầy đủ nội dung guide, tổ chức lại
  để tra cứu nhanh. Các điểm quan trọng nhất đã được đưa thêm vào
  [cheat-sheet.md](cheat-sheet.md) và [flashcards.md](flashcards.md).
- Lộ trình ôn + quy trình luyện đề: [study-plan.md](study-plan.md).

## Nguồn luyện đề cộng đồng (KHÔNG phải đề chính thức)
| Site | Dùng để |
|------|---------|
| https://claudecertificationguide.com/ | Học theo module, cấu trúc bám đúng 5 domain — dùng để vá lỗ hổng kiến thức |
| https://guided.maithienan.com/certifications/ccar-f | Bộ câu hỏi có hướng dẫn |
| https://thangldw.github.io/apps/cert/ccar-f/ | Quiz app, luyện phản xạ |
| https://ccar-architect-foundations.vercel.app/ | Mock exam mô phỏng |

⚠️ Khi nguồn ngoài mâu thuẫn với file này → tin file này (bám guide gốc). Nếu nguồn ngoài đúng
mà file này thiếu → bổ sung vào đây rồi commit.

## Định dạng bài thi
| Tham số | Giá trị |
|---------|---------|
| Loại câu hỏi | Trắc nghiệm, 1/4 đáp án đúng |
| Thang điểm | 100–1000, điểm đạt 720 |
| Phạt khi đoán | Không |
| Số kịch bản | 4 trong 8 kịch bản (chọn ngẫu nhiên) |

## 5 Lĩnh vực thi
| Lĩnh vực | Trọng số |
|----------|----------|
| 1. Kiến trúc agent và điều phối | 27% |
| 2. Thiết kế tool và tích hợp MCP | 18% |
| 3. Cấu hình và quy trình làm việc Claude Code | 20% |
| 4. Prompt engineering và structured output | 20% |
| 5. Quản lý context và độ tin cậy | 15% |

## 8 Kịch bản thi
1. Agent Hỗ trợ Khách hàng (Claude Agent SDK + MCP tools: `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`; mục tiêu 80%+ giải quyết ngay lần đầu)
2. Sinh mã với Claude Code (slash commands, CLAUDE.md, planning mode)
3. Hệ thống Nghiên cứu Multi-Agent (coordinator + subagents: web-search, document-analysis, synthesis)
4. Công cụ Nâng cao Năng suất Lập trình viên (Read/Write/Bash/Grep/Glob + MCP)
5. Claude Code cho CI/CD (code review tự động, giảm false positive)
6. Trích xuất Dữ liệu Có cấu trúc (JSON schema validation)
7. Các Mẫu Kiến trúc AI Hội thoại (context window, memory, tool safety, ambiguity)
8. Công cụ Agentic AI (nội dung chưa đầy đủ trong guide gốc)

## Tài liệu chính thức
| Tài nguyên | URL |
|------------|-----|
| Claude API — Messages | https://platform.claude.com/docs/en/api/messages |
| Claude API — Tool Use | https://platform.claude.com/docs/en/build-with-claude/tool-use |
| Claude API — Message Batches | https://platform.claude.com/docs/en/build-with-claude/message-batches |
| Claude Agent SDK — Overview | https://platform.claude.com/docs/en/agent-sdk/overview |
| Claude Agent SDK — Hooks | https://platform.claude.com/docs/en/agent-sdk/hooks |
| Claude Agent SDK — Subagents | https://platform.claude.com/docs/en/agent-sdk/subagents |
| Claude Agent SDK — Sessions | https://platform.claude.com/docs/en/agent-sdk/sessions |
| Model Context Protocol | https://modelcontextprotocol.io/ |
| MCP — Tools | https://modelcontextprotocol.io/docs/concepts/tools |
| MCP — Resources | https://modelcontextprotocol.io/docs/concepts/resources |
| MCP — Servers | https://modelcontextprotocol.io/docs/concepts/servers |
| Claude Code — Documentation | https://code.claude.com/docs/en/overview |
| Claude Code — CLAUDE.md and Memory | https://code.claude.com/docs/en/memory |
| Claude Code — Skills | https://code.claude.com/docs/en/skills |
| Claude Code — Hooks | https://code.claude.com/docs/en/hooks |
| Claude Code — Sub-agents | https://code.claude.com/docs/en/sub-agents |
| Claude Code — MCP Integration | https://code.claude.com/docs/en/mcp |
| Claude Code — GitHub Actions CI/CD | https://code.claude.com/docs/en/github-actions |
| Claude Code — GitLab CI/CD | https://code.claude.com/docs/en/gitlab-ci-cd |
| Claude Code — Headless mode | https://code.claude.com/docs/en/headless |
| Prompt Engineering Guide | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview |
| Extended Thinking | https://platform.claude.com/docs/en/build-with-claude/extended-thinking |
| Anthropic Cookbook | https://github.com/anthropics/anthropic-cookbook |

---

# PHẦN I: NỀN TẢNG LÝ THUYẾT (tóm tắt 13 chương)

## Chương 1 — Claude API: cấu trúc request/response
- Request gồm: `model`, `max_tokens` (bắt buộc), `system`, `messages`, `tools`, `tool_choice`.
- 3 "vai trò": `user`, `assistant`, và `system` (có thể ở top-level HOẶC chèn thẳng vào `messages`).
- **Tool result KHÔNG dùng `role: "tool"`** — luôn là `role: "user"` chứa content block
  `{"type": "tool_result", "tool_use_id": ..., "content": ...}`.
- `system` chèn giữa `messages` (không chỉ top-level) — dùng để thêm chỉ dẫn giữa hội thoại mà
  không phá cache prefix. Quy tắc vị trí nghiêm ngặt:
  - Phải theo ngay sau lượt `user` (kể cả có `tool_result`) hoặc lượt `assistant` kết thúc bằng server tool.
  - Phải đứng trước lượt `assistant` hoặc là phần tử cuối mảng.
  - KHÔNG được nằm giữa `tool_use` và `tool_result` tương ứng → lỗi 400.
  - `system` xuất hiện sau ưu tiên hơn `system` trước đó và hơn cả tham số `system` top-level.
- API stateless tuyệt đối — mỗi request phải gửi lại **toàn bộ lịch sử**.
- `stop_reason`: `end_turn` (xong), `tool_use` (cần chạy tool), `max_tokens` (bị cắt), `stop_sequence`.
  → `tool_use`/`end_turn` là 2 giá trị điều khiển agentic loop.
- System prompt có ưu tiên cao hơn user message; cách diễn đạt có thể tạo liên tưởng tool
  ngoài ý muốn (vd "luôn xác minh khách hàng" → lạm dụng `get_customer`).
- Context window gồm: system + toàn bộ messages + tool definitions + tool results.
  - **Lost-in-the-middle**: model xử lý tốt đầu/cuối input dài, dễ bỏ sót ở giữa.
  - **Tool result accumulation**: tool trả 40+ field nhưng chỉ cần 5 → lãng phí context.
  - **Tóm tắt lũy tiến**: số liệu/% /ngày tháng dễ bị mất, biến thành "khoảng", "một vài".

## Chương 2 — Tools và `tool_use`
- Model không tự chạy code — nó sinh yêu cầu tool có cấu trúc, code của bạn thực thi và trả kết quả.
- **Mô tả tool là cơ chế lựa chọn chính** của LLM — mô tả sơ sài gây nhầm giữa các tool chồng lấn.
  Mô tả tốt cần: tool làm gì/trả về gì, định dạng input + ví dụ, edge case, khi nào dùng tool này
  so với phương án khác.
- Built-in tool (Read, Grep...) có thể lấn át MCP tool tương tự → cần mô tả MCP tool mạnh hơn,
  nêu rõ ưu thế/dữ liệu độc nhất.
- `tool_choice`:
  | Giá trị | Hành vi |
  |---|---|
  | `{"type": "auto"}` | Model tự quyết định gọi tool hay trả lời text (mặc định) |
  | `{"type": "any"}` | Bắt buộc gọi 1 tool nào đó (đảm bảo structured output, không ép tên) |
  | `{"type": "tool", "name": "X"}` | Bắt buộc gọi đúng tool `X` (ép thứ tự/bước đầu tiên) |
- JSON schema qua `tool_use` là cách đáng tin cậy nhất cho structured output: đảm bảo **cú pháp**
  hợp lệ, KHÔNG đảm bảo **ngữ nghĩa** đúng (giá trị vẫn có thể sai/hallucinate).
- Thiết kế schema:
  - Chỉ đánh dấu `required` khi thông tin luôn có sẵn — required ép model bịa giá trị khi thiếu dữ liệu.
  - Dùng `"type": ["string", "null"]` cho trường có thể vắng mặt.
  - Enum nên có `"other"` + trường chi tiết để không mất dữ liệu ngoài danh mục.
  - Enum nên có `"unclear"` cho các case model không tự tin phân loại.
- Lỗi cú pháp (JSON sai định dạng) vs lỗi ngữ nghĩa (tổng không khớp, giá trị sai vị trí,
  hallucination) — `tool_use`+schema chỉ giải quyết cú pháp; ngữ nghĩa cần validation + retry.

## Chương 3 — Claude Agent SDK
- **Agentic loop**: gửi request → check `stop_reason` → nếu `tool_use`: chạy tool, nối kết quả vào
  history, lặp lại; nếu `end_turn`: xong. Đây là ra quyết định **do model điều khiển**, không phải
  cây quyết định hard-code.
- Anti-pattern: parse text để đoán "đã xong", dùng giới hạn số vòng lặp tùy ý làm điều kiện dừng
  chính, coi việc model sinh text là tín hiệu hoàn thành. **Chỉ tin `stop_reason == "end_turn"`.**
- `AgentDefinition`: `name`, `description`, `system_prompt`, `allowed_tools` (least privilege).
- **Hub-and-spoke**: coordinator phân rã task, chọn subagent (động), ủy thác, tổng hợp, xử lý lỗi,
  giao tiếp với người dùng. Toàn bộ giao tiếp đi qua coordinator (observability).
- **Subagent có context TÁCH BIỆT** — không tự kế thừa lịch sử coordinator; mọi context cần thiết
  phải được truyền tường minh vào prompt của subagent.
- Tool `Task` để spawn subagent — `allowed_tools` của coordinator phải chứa `"Task"`.
- Có thể spawn nhiều `Task` song song trong 1 response của coordinator.
- **Hooks**: chặn tại các điểm trong vòng đời agent.
  - `PostToolUse`: chuẩn hóa/cắt gọn tool result trước khi model tiêu thụ.
  - `PreToolUse`/hook chặn lời gọi đi ra: enforce policy cứng (vd chặn refund > $500).
  - **Hooks = deterministic (100%)**; **prompt instructions = xác suất (>90%, không phải 100%)**.
    Quy tắc: hậu quả tài chính/pháp lý/an toàn → dùng hook, không dùng prompt.

## Chương 4 — Model Context Protocol
- 3 primitive: **Tools** (hành động, model gọi), **Resources** (dữ liệu đọc, "bản đồ" giúp agent
  không cần tool thăm dò), **Prompts** (template dựng sẵn).
- Cấu hình:
  - `.mcp.json` ở project root — dùng chung cho nhóm, commit vào VCS, secret qua biến môi trường
    (`${GITHUB_TOKEN}`), không commit token thật.
  - `~/.claude.json` — cấp người dùng, không chia sẻ VCS, dùng cho thử nghiệm cá nhân.
  - Ưu tiên MCP server cộng đồng có sẵn cho tích hợp chuẩn (Jira, GitHub, Slack); chỉ tự viết
    server cho workflow đặc thù riêng của nhóm.
- `isError: true` báo lỗi MCP tool. Lỗi có cấu trúc (tốt) gồm `errorCategory`
  (transient/validation/permission...), `isRetryable`, `message`, `partial_results` — cho phép
  agent quyết định retry/đổi truy vấn/escalation. Lỗi chung chung ("Operation failed") vô dụng.

## Chương 5 — Claude Code: cấu hình & workflow
- Phân cấp CLAUDE.md 3 mức: **user** (`~/.claude/CLAUDE.md`, không VCS), **project**
  (`.claude/CLAUDE.md` hoặc root `CLAUDE.md`, có VCS, áp dụng mọi người), **directory**
  (CLAUDE.md trong thư mục con, chỉ áp dụng khi làm việc ở đó).
  - Lỗi thường gặp: thành viên mới không nhận hướng dẫn vì nó nằm ở cấp user thay vì project.
- `@path` import file vào CLAUDE.md — không có khoảng trắng sau `@`, hỗ trợ path tương đối/tuyệt
  đối (tương đối theo file chứa import), độ sâu lồng tối đa 5.
- `.claude/rules/*.md` — quy tắc theo chủ đề, thay thế CLAUDE.md đơn khối. YAML frontmatter
  `paths: ["src/api/**/*"]` để nạp **có điều kiện** theo glob — chỉ nạp khi sửa file khớp mẫu,
  tiết kiệm token. Dùng khi quy ước trải rộng nhiều thư mục (test, migration); dùng CLAUDE.md
  cấp thư mục khi quy ước gắn với 1 thư mục cụ thể.
- Slash command/skill: `.claude/commands/` (cũ) và `.claude/skills/` (hiện tại, `SKILL.md` +
  frontmatter) đều tạo lệnh `/name`. Project-level (`.claude/...`) = VCS, chia sẻ nhóm;
  user-level (`~/.claude/...`) = cá nhân, không chia sẻ. **Skill cùng tên ở user-level sẽ ÂM
  THẦM che khuất skill project cùng tên** — nên đặt tên khác (vd `/my-commit`) để không mất
  update từ skill nhóm.
- Skill frontmatter: `context: fork` (chạy trong subagent tách biệt, không làm nhiễu session
  chính — dùng khi skill có output dài dòng), `allowed-tools` (giới hạn tool, bảo mật),
  `argument-hint` (gợi ý đối số bắt buộc).
- Planning mode (chỉ điều tra, Read/Grep/Glob, không có side effect, tạo plan để duyệt) vs
  thực thi trực tiếp (task đơn giản, đã hiểu rõ, 1 file). Dùng planning mode cho: thay đổi lớn
  (hàng chục file), nhiều cách tiếp cận khả thi, quyết định kiến trúc, codebase lạ, migration
  45+ file. Cách kết hợp: plan để điều tra/thiết kế → duyệt → thực thi trực tiếp để triển khai.
  Subagent **Explore** cô lập output khám phá dài dòng, chỉ trả về tóm tắt, tránh cạn context.
- `/compact` — nén context, rủi ro mất số liệu chính xác trong tóm tắt.
- `/memory` — mở CLAUDE.md để sửa, giữ lại qua các session.
- CI/CD: cờ `-p`/`--print` = non-interactive, xử lý prompt → in stdout → thoát (**cách duy nhất
  đúng** để chạy trong pipeline). `--output-format json` + `--json-schema` cho structured output
  parse được để đăng comment inline trên PR. **Session sinh code thì kém hiệu quả khi tự review
  chính nó** (giữ context lý luận, ít phản biện) — nên dùng instance độc lập để review.
  Khi review lại sau commit mới: đưa review trước vào context, chỉ báo cáo vấn đề mới/chưa sửa.
- `--resume <session-name>` tiếp tục session có tên; rủi ro nếu file đã đổi thì tool result cũ
  lỗi thời. `fork_session` tạo nhánh độc lập từ context chung để so sánh phương án song song.
  Nên bắt đầu session mới (với tóm tắt ngắn) thay vì resume khi: tool result lỗi thời, context
  đã suy giảm nhiều.

## Chương 6 — Prompt engineering nâng cao
- Few-shot (2–4 ví dụ input/output) hiệu quả hơn mô tả bằng lời cho: kịch bản mơ hồ (kèm lý do),
  định dạng output, phân biệt code chấp nhận được/có vấn đề, trích xuất từ định dạng tài liệu
  khác nhau, đo lường không chính thức ("khoảng 2 nắm gạo" → "~100g").
- Tiêu chí rõ ràng > chỉ dẫn mơ hồ: định nghĩa chính xác "flag khi nào", "không flag khi nào",
  định nghĩa mức độ nghiêm trọng kèm ví dụ cụ thể cho từng mức.
- Prompt chaining: chia task lớn thành các bước tập trung (per-file → integration pass) để
  tránh **attention dilution** (pha loãng chú ý khi xử lý nhiều file/nhiều thứ cùng lúc).
  Prompt chaining cho task lặp lại/dự đoán được; dynamic decomposition cho điều tra mở.
- Mẫu "phỏng vấn": Claude đặt câu hỏi làm rõ trước khi triển khai — hữu ích cho lĩnh vực lạ,
  hệ quả không hiển nhiên, nhiều cách tiếp cận khả thi.
- Validation + retry-with-feedback: đưa document gốc + bản trích xuất sai + lỗi cụ thể vào retry.
  Retry hiệu quả cho lỗi định dạng/cấu trúc/số học; KHÔNG hiệu quả khi thông tin không có trong
  nguồn. Pydantic: validation cấu trúc (kiểu, required, enum) + validator tùy chỉnh cho logic
  nghiệp vụ (semantic) + sinh JSON Schema làm single source of truth cho `tool_use`.
- Tự sửa lỗi: trích xuất cả `stated_total` và `calculated_total`, có cờ `conflict_detected`.

## Chương 7 — Message Batches API
| Thuộc tính | Giá trị |
|---|---|
| Tiết kiệm | **50%** so với đồng bộ |
| Cửa sổ xử lý | Lên đến **24 giờ**, KHÔNG có SLA latency |
| Tool calling nhiều lượt | **KHÔNG hỗ trợ** (1 request = 1 response, không thể chặn giữa chừng
  để chạy tool rồi tiếp tục — bất tương thích với các quy trình gọi tool lặp) |
| Tương quan | `custom_id` liên kết request/response |
- Dùng Batch cho: không chặn, không cần real-time (báo cáo qua đêm, audit hàng tuần, xử lý
  hàng loạt tài liệu). Dùng Synchronous cho: chặn merge PR, review tương tác, cần phản hồi ngay.
- Xử lý thất bại: định danh bằng `custom_id`, chỉ gửi lại phần lỗi.
- Lập kế hoạch SLA: nếu cần kết quả trong 30h và batch mất tới 24h → cửa sổ gửi = 6h; nên chia
  thành các cửa sổ đều đặn (vd 4h) cho việc gửi thường xuyên.

## Chương 8 — Chiến lược phân rã tác vụ
- **Pipeline cố định** (prompt chaining): các bước định trước, dùng khi task có cấu trúc dự
  đoán được, cần ổn định/tái lập.
- **Phân rã thích ứng động**: task con sinh ra dựa trên kết quả trung gian, dùng cho điều tra
  mở, phạm vi chưa biết trước.
- Code review nhiều lượt cho PR 10+ file: pass 1 per-file (local issues) + pass 2 integration
  (cross-file). 1 lượt duy nhất cho nhiều file → attention dilution, nhận xét không nhất quán,
  bỏ sót lỗi.

## Chương 9 — Escalation và human-in-the-loop
- Tác nhân escalation đáng tin cậy: yêu cầu tường minh của khách hàng ("gặp quản lý" → escalate
  ngay, KHÔNG cố giải quyết trước), chính sách không bao quát yêu cầu (lỗ hổng chính sách), agent
  không tiến triển được, thao tác tài chính vượt ngưỡng (nên qua hook, không phải prompt), nhiều
  kết quả khớp khi tìm khách hàng (hỏi thêm định danh, không đoán).
- **KHÔNG đáng tin cậy**: phân tích cảm xúc (tâm trạng ≠ độ phức tạp vụ việc), model tự đánh giá
  độ tin cậy 1–10 (có thể sai một cách tự tin, hiệu chỉnh kém), bộ phân loại tự động riêng
  (overengineering).
- Mẫu escalation: ghi nhận cảm xúc → đề xuất giải pháp cụ thể → chỉ escalate nếu khách hàng
  **nhắc lại** mong muốn gặp người thật (không escalate ngay lần đầu không hài lòng).
- Structured handoff: `customer_id`, `issue_summary`, `order_id`, `root_cause`, `actions_taken`,
  `recommended_action`, `escalation_reason` — vì người vận hành không thấy toàn bộ hội thoại.
- Hiệu chỉnh độ tin cậy: điểm tin cậy cấp trường + calibration trên tập validation đã gán nhãn +
  routing (tin cậy cao → tự động, thấp/nguồn mơ hồ → người review). **Lấy mẫu ngẫu nhiên phân
  tầng** để kiểm toán ngay cả các case tin cậy cao — độ chính xác tổng 97% có thể che giấu 40%
  lỗi ở 1 loại tài liệu cụ thể.

## Chương 10 — Xử lý lỗi trong hệ thống đa agent
| Nhóm lỗi | Ví dụ | Retry? | Hành động |
|---|---|---|---|
| Transient | timeout, 503 | Có | exponential backoff |
| Validation | input sai định dạng | Không (sửa input) | điều chỉnh + retry |
| Business | vi phạm policy | Không | giải thích + phương án thay thế |
| Permission | từ chối truy cập | Không | escalation |
- Anti-pattern: trạng thái lỗi chung chung ("search unavailable"), ém lỗi âm thầm (kết quả rỗng
  = coi như thành công), hủy toàn bộ workflow vì 1 lỗi, retry vô hạn trong subagent (lãng phí).
- Lỗi subagent có cấu trúc: `status`, `failure_type`, `attempted_query`, `partial_results`,
  `alternative_approaches`, `coverage_impact` — cho coordinator đủ thông tin quyết định.
- Chú thích độ phủ trong báo cáo cuối: đánh dấu rõ phần nào "BAO PHỦ ĐẦY ĐỦ" vs "MỘT PHẦN"
  kèm lý do (vd timeout).

## Chương 11 — Quản lý context trong production
- Trích "case facts" (customer ID, order ID, amount, status...) vào 1 block riêng, đưa vào MỌI
  prompt bất kể lịch sử đã tóm tắt thế nào — tránh mất số liệu qua các lần nén.
- Cắt gọn tool result: hook `PostToolUse` chỉ giữ field liên quan (40+ field → 5 field cần).
- Đầu vào nhận biết vị trí: đặt key findings ở ĐẦU, action items ở CUỐI (tận dụng
  primacy/recency, giảm lost-in-the-middle).
- File scratchpad: agent ghi phát hiện quan trọng ra file để tham khảo lại khi context suy giảm
  hoặc session mới, thay vì chạy lại khám phá.
- Ủy quyền subagent để bảo vệ context chính: subagent đọc 15 file → main agent chỉ giữ 1 dòng
  tóm tắt thay vì 15 file đầy đủ. Coordinator = lớp context riêng biệt, ngăn "rò rỉ context".
  Ngân sách context subagent: gửi context tối thiểu, yêu cầu output có cấu trúc, giới hạn
  `allowedTools` (ít tool = ít phân tâm = ít context).
- Lưu trạng thái có cấu trúc theo agent (`agent-state/*.json`) + manifest tổng để phục hồi khi
  crash/resume.

## Chương 12 — Bảo toàn provenance
- Mỗi claim cần giữ: `source_url`/`source_name`, `publication_date`, `confidence` — tránh mất
  quy kết nguồn khi tổng hợp nhiều nguồn.
- Dữ liệu xung đột: giữ CẢ HAI giá trị kèm nguồn + `conflict_detected` + `possible_explanation`,
  KHÔNG tùy tiện chọn 1 giá trị — để coordinator/người dùng quyết định.
- Luôn kèm ngày tháng để tránh hiểu nhầm chênh lệch thời gian thành mâu thuẫn thực sự.
- Trình bày theo loại nội dung: dữ liệu tài chính → bảng, tin tức → văn xuôi, phát hiện kỹ
  thuật → danh sách có cấu trúc, chuỗi thời gian → sắp theo trình tự.

## Chương 13 — Built-in tools của Claude Code
| Tác vụ | Tool |
|---|---|
| Tìm file theo tên/mẫu | Glob |
| Tìm kiếm nội dung trong file | Grep |
| Đọc toàn bộ 1 file | Read |
| Ghi file mới | Write |
| Sửa chính xác 1 file có sẵn (khớp text duy nhất) | Edit |
| Chạy lệnh shell | Bash |
- Chiến lược điều tra tăng dần: Grep tìm entry point → Read file tìm được → Grep tìm usage →
  Read file dùng → lặp lại. Không đọc hết mọi file cùng lúc.
- Khi Edit thất bại do khớp không duy nhất: fallback Read (đọc full) → sửa trong code → Write.

---

# PHẦN II: GHI CHÚ THEO 5 LĨNH VỰC THI (bản đầy đủ)

## Lĩnh vực 1 — Kiến trúc và Điều phối Agent (27%)
1. **Agentic loop tự chủ**: điều khiển bằng `stop_reason` (`tool_use` vs `end_turn`), KHÔNG
   parse text hay dùng max_iterations làm cơ chế dừng chính.
2. **Điều phối multi-agent hub-and-spoke**: coordinator sở hữu toàn bộ giao tiếp, xử lý lỗi,
   định tuyến; subagent context tách biệt; rủi ro coordinator phân rã task quá hẹp (bỏ sót phạm vi).
3. **Cấu hình subagent/truyền context**: tool `Task`, `allowedTools` phải có `"Task"`, context
   PHẢI truyền tường minh, `AgentDefinition`, `fork_session` để thử phương án song song.
4. **Workflow nhiều bước + bàn giao**: thực thi theo lập trình (deterministic) vs hướng dẫn
   prompt (xác suất) — dùng điều kiện tiên quyết bằng code khi cần đảm bảo tuyệt đối (vd chặn
   `process_refund` cho tới khi có ID đã xác minh từ `get_customer`).
5. **Hooks**: `PostToolUse` để chuẩn hóa dữ liệu, hook chặn để enforce compliance —
   deterministic > prompt khi có hậu quả nghiêm trọng.
6. **Chiến lược phân rã task**: pipeline cố định vs phân rã thích ứng động.
7. **Session state**: `--resume`, `fork_session`, biết khi nào nên bắt đầu session mới.

## Lĩnh vực 2 — Thiết kế Tool và Tích hợp MCP (18%)
1. Mô tả tool rõ ràng = cơ chế lựa chọn chính; đổi tên tool để loại bỏ chồng lấn (vd
   `analyze_content` → `extract_web_results`) thay vì chỉ thêm ví dụ/prompt.
2. Lỗi MCP có cấu trúc: `isError`, phân biệt transient/validation/business/permission,
   `isRetryable`; phục hồi cục bộ trong subagent cho lỗi tạm thời, chỉ lan truyền lỗi không tự
   giải quyết được.
3. Phân bổ tool: quá nhiều tool/agent giảm độ tin cậy chọn tool — giới hạn theo vai trò
   (least privilege); `tool_choice: "any"` đảm bảo có structured output; ép tool cụ thể để đảm
   bảo thứ tự.
4. MCP server: `.mcp.json` (project, VCS, env var cho secret) vs `~/.claude.json` (user,
   cá nhân); ưu tiên server cộng đồng cho tích hợp chuẩn.
5. Built-in tools: Grep (nội dung), Glob (tên/mẫu file), Read/Write (toàn bộ file), Edit (sửa
   chính xác, fallback Read+Write khi khớp không duy nhất).

## Lĩnh vực 3 — Cấu hình Claude Code và Workflow (20%)
1. Phân cấp CLAUDE.md (user/project/directory) + `@path` import + `.claude/rules/` với `paths` glob.
2. Slash command/skill: project (`.claude/commands|skills/`, VCS) vs user (`~/.claude/...`,
   cá nhân); `context: fork`, `allowed-tools`, `argument-hint`.
3. Quy tắc theo đường dẫn (`.claude/rules/` + `paths` glob) ưu tiên hơn CLAUDE.md cấp thư mục
   khi quy ước trải rộng nhiều thư mục (test files rải rác).
4. Planning mode (thay đổi lớn, nhiều phương án, quyết định kiến trúc) vs thực thi trực tiếp
   (đơn giản, rõ ràng); subagent Explore cô lập khám phá dài dòng.
5. Tinh chỉnh lặp lại: ví dụ input/output cụ thể, test-driven iteration, mẫu "phỏng vấn".
6. CI/CD: `-p`/`--print` (bắt buộc cho non-interactive), `--output-format json` +
   `--json-schema`, cô lập session review khỏi session sinh code, đưa review trước vào context
   khi chạy lại để tránh comment trùng lặp.

## Lĩnh vực 4 — Prompt Engineering và Structured Output (20%)
1. Tiêu chí tường minh > hướng dẫn mơ hồ — định nghĩa rõ báo cáo gì/bỏ qua gì, mức độ nghiêm
   trọng kèm ví dụ.
2. Few-shot cải thiện tính nhất quán — đặc biệt cho kịch bản mơ hồ, định dạng output, phân biệt
   pattern chấp nhận được/có vấn đề.
3. `tool_use` + JSON Schema = cách đáng tin cậy nhất cho structured output (đảm bảo cú pháp,
   không đảm bảo ngữ nghĩa); `tool_choice` auto/any/forced; trường nullable/optional để tránh
   bịa giá trị; enum có "other"/"unclear".
4. Validation + retry-with-feedback: đưa lỗi cụ thể vào retry; nhận diện khi nào retry vô ích
   (thông tin không có trong nguồn); trường `detected_pattern` để phân tích false positive.
5. Batch processing: 50% tiết kiệm, ≤24h không SLA, không hỗ trợ tool calling nhiều lượt,
   `custom_id` để tương quan và retry có chọn lọc.
6. Review đa instance/đa lượt: instance độc lập (không có context sinh ra) review tốt hơn tự
   review; per-file + integration pass để tránh attention dilution.

## Lĩnh vực 5 — Quản lý Context và Độ tin cậy (15%)
1. Trích "case facts" ra khối riêng bền vững; cắt gọn tool output; đặt phát hiện quan trọng ở
   đầu; subagent trả metadata (nguồn, ngày) có cấu trúc.
2. Escalation: tiêu chí tường minh + few-shot; escalate ngay khi yêu cầu tường minh; escalate
   khi chính sách mơ hồ/im lặng; hỏi thêm định danh khi nhiều kết quả khớp — KHÔNG dùng cảm xúc
   hay self-reported confidence làm tín hiệu.
3. Lan truyền lỗi multi-agent: context lỗi có cấu trúc; phân biệt lỗi truy cập vs kết quả rỗng
   hợp lệ; phục hồi cục bộ cho lỗi tạm thời; chú thích độ phủ trong tổng hợp.
4. Quản lý context khi điều tra codebase lớn: scratchpad file, ủy thác subagent, lưu trạng thái
   có cấu trúc để crash-recovery, `/compact` cho session dài.
5. Giám sát con người + hiệu chỉnh độ tin cậy: lấy mẫu phân tầng, phân tích độ chính xác theo
   loại tài liệu/trường (không chỉ tổng thể), routing theo ngưỡng tin cậy.
6. Bảo toàn provenance: ánh xạ claim→source, giữ dữ liệu mâu thuẫn kèm chú thích (không tự chọn
   1 giá trị), ngày xuất bản để diễn giải đúng thời gian, trình bày theo loại nội dung.

---

# PHẦN III: Bài học rút ra từ các câu hỏi mẫu (76 câu, đã đọc toàn bộ guide)

Các nguyên tắc lặp lại nhiều lần nhất trong đáp án đúng — đây là "meta-pattern" hữu ích khi gặp
câu hỏi lạ trong bài thi thật:

1. **Khi cần đảm bảo tuyệt đối (tài chính/thứ tự/an toàn) → chọn giải pháp CODE/HOOK/kiến trúc
   tool, KHÔNG chọn "cải thiện prompt" hay "thêm few-shot".** (Q1, Q61 — dùng precondition
   theo lập trình hoặc thiết kế tool 2 bước dry-run+token thay vì dặn dò trong prompt.)
2. **Khi vấn đề là chọn nhầm tool → sửa MÔ TẢ/TÊN tool trước tiên**, không phải thêm layer
   routing hay bộ phân loại riêng (Q2, Q7, Q46, Q57 — overengineering là đáp án sai phổ biến).
3. **Escalation nên dựa trên tiêu chí tường minh + few-shot, KHÔNG dựa trên cảm xúc/self-rated
   confidence/bộ classifier riêng** (Q3, Q49 — đây là bẫy lặp lại nhiều lần).
4. **Coordinator luôn là trung tâm điều phối** — subagent không nói chuyện trực tiếp với nhau
   (Q2, Q8 phần multi-agent).
5. **Lỗi cần trả về context có cấu trúc (loại lỗi, đã thử gì, kết quả một phần, phương án thay
   thế), không phải trạng thái chung chung hay im lặng nuốt lỗi** (Q8, Q9, Q12, Q59 nhiều biến
   thể — đây là chủ đề bị hỏi nhiều nhất trong nhóm multi-agent).
6. **"14 file review 1 lượt kém nhất quán" luôn được sửa bằng per-file pass + 1 integration
   pass riêng**, KHÔNG phải bằng model to hơn/context lớn hơn (Q12, Q27 — lặp lại y hệt).
7. **Batch API: chỉ dùng cho tác vụ KHÔNG chặn** (báo cáo qua đêm/hàng tuần); KHÔNG BAO GIỜ dùng
   cho bước chặn merge/PR-blocking vì không có SLA latency và không hỗ trợ tool nhiều lượt
   (Q11, Q19, Q21, Q30 — xuất hiện 4 lần, luôn cùng 1 đáp án).
8. **`-p`/`--print` là CÁCH DUY NHẤT đúng để chạy Claude Code trong CI** — các phương án
   "CLAUDE_HEADLESS=true", "--batch", redirect stdin đều là bẫy/không tồn tại (Q10, Q26).
9. **CLAUDE.md project-level = `.claude/CLAUDE.md` hoặc root, KHÔNG phải `~/.claude/CLAUDE.md`**
   — lỗi "thành viên mới không thấy hướng dẫn" luôn do đặt nhầm cấp user (Q4, Q37, Q41).
10. **`.claude/rules/` + `paths` glob dùng khi quy ước trải rộng nhiều thư mục** (test files nằm
    rải rác) — CLAUDE.md cấp thư mục không giải quyết được việc này (Q6, Q33, Q40, Q42).
11. **Skill `context: fork`** dùng khi output dài dòng làm nhiễu context chính (Q35, Q43 —
    lặp lại chính xác cùng 1 pattern).
12. **Đặt tên skill cá nhân KHÁC tên skill nhóm** để không âm thầm che khuất bản cập nhật của
    nhóm (Q36 — bẫy tinh vi, dễ chọn nhầm "cùng tên tại `~/.claude/skills/`").
13. **Context window: đặt thông tin quan trọng ở ĐẦU và/hoặc CUỐI**, dùng tiêu đề mục rõ ràng để
    giảm lost-in-the-middle — KHÔNG phải tóm tắt mọi thứ xuống dưới ngưỡng token hay đảo thứ tự
    ngẫu nhiên (Q13, Q65, Q68).
14. **Giảm token context bằng cách sửa AGENT THƯỢNG NGUỒN trả dữ liệu có cấu trúc** thay vì thêm
    agent tóm tắt trung gian hay vector DB (Q14 — sửa tại nguồn > xử lý hậu kỳ).
15. **`system` không có bộ nhớ phía server — luôn phải gửi lại toàn bộ `messages`** (Q64, Q67 —
    lặp lại y hệt, hay bị nhầm là do context window hoặc thiếu `session_id`).
16. **Trôi hướng dẫn qua nhiều lượt hội thoại**: sửa bằng few-shot cụ thể hoặc chèn lại lời nhắc
    định kỳ, KHÔNG phải bắt đầu lại toàn bộ hội thoại hay validate-and-regenerate tốn kém
    (Q69, Q70, Q75).
17. **Câu hỏi mơ hồ từ người dùng**: nêu giả định tường minh rồi tiến hành + mời đính chính —
    tốt hơn hỏi dồn dập nhiều câu hoặc âm thầm đoán (Q74, Q76 — lặp lại y hệt).
18. **Dữ liệu mâu thuẫn giữa các nguồn**: giữ CẢ HAI kèm trích dẫn, KHÔNG tự chọn 1 giá trị,
    KHÔNG dừng lại chờ coordinator quyết định ngay (agent phân tích vẫn hoàn thành việc, chỉ gắn
    cờ mâu thuẫn) (Q1 phần multi-agent, Chương 12).

## Bài kiểm tra thực hành
- Guide có 1 bộ 60 câu bổ sung (không paste đầy đủ vào đây) + 1 file HTML luyện tập giống bài
  thi thật. TODO: nếu cần luyện thêm, mở trực tiếp `practical_test_en.html` trong repo guide gốc
  trên GitHub.

## Chủ đề CHẮC CHẮN KHÔNG xuất hiện trong bài thi (loại trừ để không học lệch)
- Fine-tuning/huấn luyện model tùy chỉnh; xác thực/billing API; chi tiết framework/ngôn ngữ cụ
  thể; hosting/deploy MCP server; kiến trúc nội bộ Claude/RLHF; embedding model/vector DB nội
  bộ; computer use (browser/desktop automation); Vision; streaming API/SSE; rate limit/quota/chi
  phí chi tiết; OAuth/API key rotation; cấu hình cloud provider cụ thể; benchmark hiệu năng model;
  chi tiết triển khai prompt caching; thuật toán tokenization.
