# Domain 3: Claude Code Configuration & Workflows (20%)

> Nguồn: https://claudecertificationguide.com/learn/3-claude-code-config/

---

## 3.1 CLAUDE.md Hierarchy

### 3 cấp độ hierarchy

**User-Level: `~/.claude/CLAUDE.md`** — scope: cá nhân dev; storage: home directory, ngoài repository; version control: không track bởi git; use case: sở thích cá nhân, verbosity setting, output style, shortcut cá nhân. **Giới hạn quan trọng**: khi team member mới clone repo, họ KHÔNG nhận được config user-level vì nó nằm ngoài repo.

**Project-Level: `.claude/CLAUDE.md` hoặc root `CLAUDE.md`** — scope: toàn team; storage: root repository hoặc trong thư mục `.claude/`; version control: track bởi git, tự động phân phối khi clone/pull; use case: naming convention, error handling pattern, testing requirement, architecture decision, code review checklist. **Lợi thế chính**: mọi dev clone/pull đều tự động nhận instruction này.

**Directory-Level: subdirectory `CLAUDE.md`** — scope: chỉ đúng thư mục đó và nội dung bên trong; ví dụ path: `/packages/api/CLAUDE.md`; use case: convention riêng package, convention khác root, rule domain-specific không áp dụng nơi khác. **Giới hạn quan trọng**: chỉ áp dụng cho thư mục đó, không cascade qua nhiều thư mục.

### Loading Order & Conflict Handling

**Mô hình concatenation (không phải override)**: tài liệu chính thức nói rằng "Mọi file phát hiện được được concatenate vào context thay vì override lẫn nhau." Khác hoàn toàn với hệ config dựa trên precedence.

**Documented load order**:
1. File load từ scope rộng nhất tới hẹp nhất
2. Instruction project xuất hiện trong context sau instruction user
3. Nội dung sắp xếp "từ filesystem root xuống tới working directory"
4. Instruction gần working directory được đọc sau cùng
5. Trong 1 thư mục, `CLAUDE.local.md` append sau `CLAUDE.md`

**Điểm quan trọng**: đọc sau cùng trong load order KHÔNG thiết lập precedence hay đảm bảo thắng conflict.

**Xử lý conflict**: khi 2 rule mâu thuẫn nhau, "Claude có thể chọn tùy tiện." Tài liệu nói rõ: không có đảm bảo tuân thủ chặt chẽ. Coi CLAUDE.md như hướng dẫn model thường theo, không phải config layer deterministic có hard enforcement.

**Giới hạn enforcement**: cho rule PHẢI đúng mọi lần thực thi — đừng dựa vào CLAUDE.md scoping; dùng `settings.json` (client enforce bất kể Claude quyết định gì) hoặc hooks (fire tại lifecycle event cố định).

### CLAUDE.md vs settings.json

| Đặc điểm | CLAUDE.md | settings.json |
|---|---|---|
| Mô hình precedence | Concatenation; conflict có thể resolve tùy tiện | Precedence chặt: managed > local > project > user |
| Enforcement | Guidance (không deterministic) | Hard enforcement bởi client |
| Use case | Style guidance, convention, best practice | Permission, blocked tool, formatter bắt buộc |
| Version control | Có thể track hoặc không (tùy level) | Thường version-control ở project level |

### Modular Organisation với `@` Path Imports
**Mục đích**: cho CLAUDE.md dài hơn vài trăm dòng, cú pháp `@` cho phép split qua nhiều file mà vẫn giữ cấu trúc nguồn dễ đọc.

**Cú pháp**: là `@` theo sau bởi path — KHÔNG có keyword `@import` dù docs online phổ biến hay ghi sai vậy.

```markdown
# .claude/CLAUDE.md

Coding standards:

@./standards/naming-conventions.md
@./standards/error-handling.md
@./standards/testing-requirements.md
```

Mỗi dòng `@<path>` trigger inline file đó lúc load; nội dung file reference được chèn y hệt như copy-paste. CLAUDE.md riêng của mỗi package có thể import chỉ standard áp dụng, không trùng lặp giữa các package.

**Lưu ý quan trọng về context**: import load eager và đầy đủ. Split CLAUDE.md 600 dòng thành 6 import 100 dòng làm source dễ maintain hơn nhưng context window cuối cùng nhận cùng lượng nội dung. **Nếu mục tiêu là giảm context per-session, dùng `.claude/rules/` với path-scoped frontmatter thay thế** (chi tiết ở Task 3.3).

### CLAUDE.local.md — Override chỉ local
**Hành vi load**: append sau `CLAUDE.md` cùng level; đọc sau cùng ở level đó nhưng không thiết lập precedence; conflict với rule khác vẫn có thể resolve tùy tiện.

**Convention git**: thường thêm vào `.gitignore`; đánh dấu file chỉ dùng cá nhân; tránh commit nhầm tweak cá nhân.

**Mục đích dự kiến**: `CLAUDE.md` chung — rule và convention team; `CLAUDE.local.md` — sở thích cá nhân dev cho repo đó (vd scratchpad path yêu thích, giải thích verbose, debug note tạm).

**Mô hình khái niệm**: coi `CLAUDE.local.md` như phiên bản project-scoped của `~/.claude/CLAUDE.md` — cùng nguyên tắc, phạm vi hẹp hơn. Nếu dùng nó để diễn đạt rule team, nên chuyển rule đó sang `CLAUDE.md` chung.

### Thư mục `.claude/rules/`
**Cấu trúc**: thay thế cho 1 file CLAUDE.md duy nhất; chứa file rule theo topic trong `.claude/rules/`.

**Ví dụ file**: `testing.md` (naming test, assertion pattern, fixture usage); `api-conventions.md` (endpoint naming, request/response schema); `deployment.md` (checklist deploy, cấu hình môi trường).

**Hỗ trợ frontmatter**: mỗi file có thể có YAML frontmatter với path scoping (optional). Không có frontmatter → rule load cho mọi session.

**Phân biệt với `@` import**: `@` import — split 1 CLAUDE.md qua nhiều file để dễ maintain; nội dung luôn load. `.claude/rules/` — file theo topic có thể dùng path scoping để load có chọn lọc.

### Lệnh `/memory` và `/context`
**Mục đích `/memory`**: hiển thị file config nào đang được load trong session hiện tại. Đây là **diagnostic tool**, không phải trigger loading.

**Khái niệm chính**: "/memory KHÔNG load file config — nó chỉ ra file nào đã load rồi. File config load tự động dựa theo level và location. Dùng /memory để chẩn đoán, không phải để kích hoạt."

**Ghi chú implementation hiện tại**: exam guide (v1.0) coi `/memory` là lệnh hiển thị file đã load. Claude Code hiện tại chia diagnostic thành 2:
- `/memory`: liệt kê CLAUDE.md, CLAUDE.local.md, và vị trí auto-memory; mở trong editor
- `/context`: báo cáo cái gì thực sự load vào session dưới mục "Memory files"

Không lệnh nào trigger loading; cả 2 chỉ diagnostic.

**Trạng thái hiện tại**: để debug file đã load, hướng dẫn chính thức chỉ user tới `/context`: "check list dưới Memory files để verify CLAUDE.md và CLAUDE.local.md đã load."

### Persistence qua `/compact`
**Hành vi CLAUDE.md project-root**: khi `/compact` tóm tắt session dài, CLAUDE.md project-root vẫn nguyên vẹn. Không phải vì nó có đặc quyền, mà vì Claude re-read nó từ disk sau compaction và re-inject. Instruction gốc chưa bao giờ là 1 phần của conversation history, nên không có gì để summarizer nén.

**File KHÔNG tự động quay lại**: CLAUDE.md nested trong subdirectory; file `.claude/rules/` với frontmatter `paths:`. Cả 2 load on-demand, nên quay lại lần sau khi Claude đọc file matching, không phải ngay sau khi compaction xong.

**Instruction biến mất**: khi 1 instruction có vẻ mất sau `/compact`, nguyên nhân thường là: 1) nó là directory hoặc rules file có path scoping (quay lại lần đọc file matching kế tiếp), 2) nó chỉ tồn tại trong conversation history (compaction có thể tóm tắt mất).

### Kịch bản đề thi quan trọng: Team member mới không nhận được instruction
**Setup bẫy**: Developer A đã ở team nhiều tháng. Claude Code follow đúng mọi convention (API naming, cấu trúc test, error handling). Developer B tham gia, clone repo, Claude Code cho kết quả không nhất quán, bỏ qua convention.

**Root cause**: Convention lưu ở user-level config của Developer A (`~/.claude/CLAUDE.md`) thay vì project-level (`.claude/CLAUDE.md` hoặc root CLAUDE.md). Config user-level không share qua git.

**Fix**: chuyển instruction từ user-level sang project-level config.

**Chiến lược nhận diện**: thấy "team member mới" đi kèm "hành vi không nhất quán"? Kiểm tra config nằm ở đâu — gần như chắc chắn ở user-level.

### Exam traps
1. **Chia sẻ config với team member mới** — sai giả định: instruction project-level tự động tới mọi team member clone repo — chỉ đúng nếu lưu trong `.claude/CLAUDE.md` hoặc root `CLAUDE.md` (cả 2 version-controlled). `~/.claude/CLAUDE.md` user-level là cá nhân và không bao giờ share.
2. **`/memory` trigger loading** — sai giả định: chạy `/memory` kích hoạt config file vào session context. `/memory` chỉ diagnostic; config load tự động theo hierarchy location.
3. **Directory-level là giải pháp phổ quát cho convention** — sai giả định: directory-level `CLAUDE.md` giải quyết tốt nhất convention cross-directory. Thực tế: directory-level chỉ áp dụng 1 thư mục. Cho convention trải nhiều thư mục (như file test khắp codebase), dùng path-specific rule trong `.claude/rules/` với glob pattern.
4. **Precedence của scoping hierarchy** — sai giả định: scope cụ thể hơn "thắng" conflict (vd "user-level override project-level"). Thực tế: file concatenate; conflict resolve tùy tiện. Docs chính thức không bao giờ nói ai thắng.

### Practice scenario
Developer A: Claude Code follow đúng convention naming API. Developer B (tham gia tuần trước): naming không nhất quán. Cả 2 làm chung repo, chung branch. **Root cause đúng**: convention naming API lưu ở CLAUDE.md user-level của Developer A (`~/.claude/CLAUDE.md`) thay vì config project-level.

### Key takeaways
1. **3-level hierarchy** là nền tảng; user-level không bao giờ share qua git.
2. **Concatenation model** nghĩa là file load cùng nhau không có precedence chặt.
3. **Conflict resolution tùy tiện**; rule cứng phải nằm ở `settings.json` hoặc hooks.
4. **Cú pháp `@`** không có keyword `@import` — chỉ `@` cộng path.
5. **Bẫy team member mới** là bẫy ưa thích trên đề thi — tìm config user-level lưu rule chia sẻ.
6. **`/memory` là diagnostic**, không kích hoạt.
7. **Directory-level chỉ áp dụng 1 thư mục**; dùng `.claude/rules/` cho pattern cross-directory.
8. **`CLAUDE.local.md`** là config cá nhân scoped ở project, thường gitignore.
9. **Sau compaction**, CLAUDE.md project-root quay lại; file directory/rules quay lại lần đọc file matching kế tiếp.

---

## 3.2 Slash Commands & Skills

### Khái niệm cốt lõi
"Custom command và skill đã được merge thành 1 hệ thống thống nhất: **Skills system**." Cả `.claude/skills/` và `.claude/commands/` đều tạo `/command` với hành vi giống hệt, chỉ khác cấu trúc file.

**Phân biệt cấu trúc file**: Skills — thư mục chứa `SKILL.md` (vd `.claude/skills/deploy/SKILL.md`). Commands — file Markdown phẳng (vd `.claude/commands/deploy.md`). "1 file phẳng đặt trực tiếp trong `.claude/skills/` KHÔNG tạo command." Path `.claude/skills/` là canonical và khuyến nghị.

### Tính năng của Unified Skills System
Cả 2 path cho ra `/command` giống hệt. Ưu điểm path skills: có thư mục file hỗ trợ đi kèm SKILL.md; tự động discover khi skill match với intent; precedence hơn command trùng tên (skill thắng); cùng hỗ trợ YAML frontmatter như path commands.

"Cả 2 path hỗ trợ cùng YAML frontmatter (`context: fork`, `allowed-tools`, `argument-hint`) và cả 2 tạo ra cùng `/command`, nên file `.claude/commands/` hiện có vẫn hoạt động không đổi."

### 2 cấp scoping

**Project-Scoped (share qua Git)** — location: `.claude/skills/` hoặc `.claude/commands/` trong repo. "Đặt skill trong `.claude/skills/` (canonical) hoặc `.claude/commands/` (alias) trong repository. Cả 2 version-controlled và share qua git. Mọi dev clone/pull repo đều tự động có command này." Use case: `/review`, `/deploy-check`, `/lint`, `/migration-guide`.

```markdown
<!-- .claude/commands/review.md — creates /review -->
Review the staged changes against our team checklist:
1. Check error handling patterns
2. Verify test coverage for new functions
3. Confirm API naming conventions
4. Flag any hardcoded credentials or secrets
```

**User-Scoped (cá nhân)** — location: `~/.claude/skills/` hoặc `~/.claude/commands/`. "Đặt skill trong `~/.claude/skills/` (canonical) hoặc `~/.claude/commands/` (alias). Cá nhân và không version-control hay share. Dùng cho workflow năng suất cá nhân team member khác không cần."

**Pattern chính**: "Pattern scoping nhất quán xuyên suốt Claude Code: project-level (`.claude/`) share qua git; user-level (`~/.claude/`) cá nhân. Áp dụng cho CLAUDE.md, commands/skills, và rules. Ghi nhớ pattern này — xuất hiện xuyên suốt Domain 3."

### Skills Frontmatter — 3 tùy chọn quan trọng trên đề thi

**1. `context: fork`** — "Chạy skill trong context sub-agent isolated. Toàn bộ output verbose ở lại trong fork, main conversation giữ sạch." Cần thiết cho: phân tích codebase (nhiều file listing và code excerpt), brainstorming (nhiều alternative và đánh giá), bất kỳ task nào tạo output khám phá, ồn ào.

"Không có `context: fork`, output skill chảy vào main conversation và tốn token context window. Với skill verbose, điều này làm giảm chất lượng response sau đó."

```yaml
---
description: "Analyse a feature area of the codebase and report structure, patterns and risks"
context: fork
allowed-tools:
  - Read
  - Grep
  - Glob
argument-hint: "Provide a feature description or area of the codebase to analyse"
---
```

**2. `allowed-tools`** — "Pre-approve các tool được liệt kê để Claude dùng mà không cần permission prompt trong khi skill active. KHÔNG giới hạn tool nào có sẵn: mọi tool khác vẫn gọi được, permission setting bình thường vẫn govern những gì không được liệt kê."

```yaml
---
allowed-tools:
  - Read
  - Grep
  - Glob
---
```

Lưu ý: "Để _xóa_ tool khỏi pool của Claude khi skill chạy — đây mới là security boundary thực sự — liệt kê chúng trong `disallowed-tools` thay vào đó, hoặc thêm deny rule trong permission setting."

**3. `argument-hint`** — "Prompt dev nhập tham số bắt buộc khi skill invoke không kèm argument. Cải thiện trải nghiệm dev bằng cách làm rõ input thay vì dựa vào dev nhớ skill cần gì."

```yaml
---
argument-hint: "Specify the module path to analyse (e.g., src/api/auth)"
---
```

**Field frontmatter khác**: guide nhắc `description` là field impact cao nhất (không exam-tested chính thức nhưng critical thực tế): "Đây là cái Claude đọc để quyết định skill có áp dụng cho câu hỏi vừa hỏi không, nên skill không có description hữu ích chỉ chạy khi dev tự gõ `/name`." Field live khác: `disallowed-tools`, `disable-model-invocation`, `model`, `effort`, `when_to_use`, `paths`.

### Skills vs CLAUDE.md — phân biệt được test trực tiếp trên đề thi

| Đặc điểm | Skills | CLAUDE.md |
|---|---|---|
| Invocation | On-demand, workflow task-specific | Always-loaded, tiêu chuẩn phổ quát |
| Loading | Body skill đầy đủ chỉ load khi invoke (explicit `/skill-name` hoặc auto qua description match) | Áp dụng tự động mỗi session, luôn trong context |
| Scope | Quy trình task-specific | Convention phổ quát và tài liệu tham khảo |
| Auto-invocation | Có thể qua field `description` hoặc `paths` matching; tắt bằng `disable-model-invocation: true` | Không áp dụng — luôn active |

**Quy tắc**: "Đừng đặt quy trình task-specific vào CLAUDE.md. Đừng đặt tài liệu tham khảo always-on vào skill."

**Hướng dẫn thực tế**: naming convention API (áp dụng mỗi lần generate code) → CLAUDE.md hoặc `.claude/rules/`; phân tích codebase multi-step (dev chạy thi thoảng) → Skill; convention cho loại file cụ thể (vd test file) → path-scoped `.claude/rules/`.

### Tùy chỉnh Skill cá nhân
"Tạo variant cá nhân trong `~/.claude/skills/` (hoặc `~/.claude/commands/`) với tên khác để không ảnh hưởng đồng nghiệp. Nếu team có skill chuẩn `/analyse` mà bạn thích version verbose hơn, tạo skill riêng trong `~/.claude/skills/` với tên khác (vd `/deep-analyse`). Skill cá nhân không override hay conflict với version team."

### Bảng tham khảo nhanh: Đặt Command ở đâu

| Nhu cầu | Location Canonical | Cũng hoạt động | Scoping |
|---|---|---|---|
| Command team-wide | `.claude/skills/<name>/SKILL.md` | `.claude/commands/<name>.md` | Project (share qua git) |
| Command team-wide có frontmatter | `.claude/skills/<name>/SKILL.md` | `.claude/commands/<name>.md` | Project (share qua git) |
| Command cá nhân | `~/.claude/skills/<name>/SKILL.md` | `~/.claude/commands/<name>.md` | User (không share) |
| Standard phổ quát | `.claude/CLAUDE.md` hoặc root `CLAUDE.md` | — | Project (luôn load) |
| Sở thích cá nhân | `~/.claude/CLAUDE.md` | — | User (không share) |

### Exam traps

1. **Cấu trúc file trong `.claude/skills/`** — sai lầm: tạo file Markdown phẳng trực tiếp trong `.claude/skills/` (vd `.claude/skills/review.md`) mong đợi có command `/review`. Thực tế: "Skill là 1 thư mục chứa entrypoint SKILL.md (`.claude/skills/review/SKILL.md`); file .md phẳng chỉ tạo command dưới `.claude/commands/` (`.claude/commands/review.md`). File lỏng thả thẳng vào `.claude/skills/` không được nhận diện."

2. **Ranh giới scoping cho command team** — sai lầm: đặt command share cho team ở path user-scoped (`~/.claude/commands/` hoặc `~/.claude/skills/`). Thực tế: "Path user-scoped là cá nhân và không version-controlled. Command team share cho mọi người phải nằm ở path project-scoped (`.claude/skills/` hoặc `.claude/commands/`) trong repository."

3. **Skill như guidance always-on** — sai lầm: nghĩ skill hành xử như CLAUDE.md cho convention always-on. Thực tế: "Skill load on-demand như workflow kiểu task, không phải guidance always-in-context. Claude có thể auto-invoke skill khi prompt khớp description (hoặc khi skill path-scoped khớp file đang edit), nhưng skill vẫn load như 1 unit invocation-style riêng biệt thay vì shape mỗi session mặc định." Chỉ dẫn đáp án: nếu câu hỏi hỏi về convention always-on, đáp án là CLAUDE.md hoặc `.claude/rules/`, không phải skill.

4. **Hiểu sai `context: fork`** — sai lầm: không nhận ra khi nào cần `context: fork`. Thực tế: "`context: fork` isolate output verbose khỏi main conversation. Không có nó, output brainstorm hay codebase analysis làm ô nhiễm context window. Đề thi sẽ đưa scenario output verbose làm rối main conversation — fix là context: fork."

5. **Workflow task-specific trong CLAUDE.md** — sai lầm: đặt workflow task-specific trong CLAUDE.md. Thực tế: "CLAUDE.md dành cho standard phổ quát always-loaded. Quy trình task-specific (code review workflow, routine phân tích, template brainstorm) thuộc về skill invoke on-demand."

### Practice scenario
Team muốn command `/review` có sẵn cho mọi người clone repo. Dev cũng muốn skill cá nhân `/brainstorm` cho output codebase analysis verbose không làm rối main conversation. **Đáp án đúng**: `/review` trong `.claude/commands/` để share team; `/brainstorm` như `~/.claude/skills/brainstorm/SKILL.md` với frontmatter `context: fork`.

### Key takeaways
1. Skills và commands đã unify; cấu trúc file khác nhau (thư mục vs file phẳng).
2. `.claude/` là project-scoped và share; `~/.claude/` là user-scoped và cá nhân.
3. `context: fork` isolate output verbose — thiết yếu cho analysis và brainstorming.
4. `allowed-tools` pre-approve tool mà không cần permission prompt.
5. `argument-hint` cải thiện trải nghiệm dev qua prompt tham số.
6. Skills on-demand, task-specific; CLAUDE.md always-on, phổ quát.
7. Skills có thể auto-invoke qua description match; CLAUDE.md không bao giờ auto-invoke.

---

## 3.3 Path-Specific Rules

### Khái niệm cốt lõi
Path-specific rule áp dụng convention có điều kiện dựa vào file đang edit. Giải quyết khoảng trống mà cả root CLAUDE.md lẫn directory-level CLAUDE.md không xử lý tốt: convention áp dụng cho 1 loại file rải rác qua nhiều thư mục.

### Cách hoạt động
File rule nằm trong thư mục `.claude/rules/` với YAML frontmatter chứa field `paths` chỉ định glob pattern. Rule chỉ load khi edit file khớp pattern đó.

**Cấu trúc cơ bản**:
```yaml
---
paths: ["terraform/**/*"]
---
# Terraform Conventions

- Use snake_case for all resource names
- Tag every resource with environment and team labels
- Never hardcode AMI IDs — use data sources
- All modules must have variables.tf, outputs.tf, and README.md
```

Khi edit file khớp `terraform/**/*`, rule này tự động load. Edit React component hay API handler thì rule vẫn ở trạng thái không active.

### Phạm vi Glob Pattern
Glob pattern match trên toàn codebase. Pattern như `**/*.test.tsx` bắt mọi file test bất kể ở đâu. Ví dụ cấu trúc project:
```
src/
  components/
    Button.tsx
    Button.test.tsx
  api/
    auth.ts
    auth.test.ts
  utils/
    format.ts
    format.test.ts
  pages/
    dashboard/
      Dashboard.tsx
      Dashboard.test.tsx
```
1 rule path-specific với `paths: ["**/*.test.tsx", "**/*.test.ts"]` áp dụng convention test giống hệt cho mọi file test tự động, loại bỏ nhu cầu 50+ bản copy directory-level.

### Vì sao không dùng directory-level CLAUDE.md?
Directory-level CLAUDE.md chỉ áp dụng cho file trong 1 thư mục đó. Phủ file test rải rác 50+ thư mục đòi hỏi đặt CLAUDE.md ở từng thư mục, gây:
- 50+ bản copy convention trùng lặp
- Cập nhật thủ công bắt buộc ở mỗi thư mục test mới
- Convention đổi đòi hỏi cập nhật cả 50+ file
- Drift chắc chắn xảy ra khi vài bản copy bị lỗi thời

Path-specific rule với glob pattern loại bỏ hoàn toàn các vấn đề này — 1 file, 1 pattern, phủ toàn bộ.

### Vì sao không dùng root CLAUDE.md?
Root CLAUDE.md load cho mọi session bất kể đang edit file nào. Đặt convention Terraform ở root CLAUDE.md tốn token ngay cả khi đang edit React component. Đặt convention test ở đó thì nó load ngay cả khi viết API handler.

**Khái niệm chính**: "Rule path-scoped tiết kiệm token hơn root CLAUDE.md vì CHỈ load khi edit file khớp. Giảm context không liên quan, giữ model tập trung vào convention thực sự áp dụng cho công việc hiện tại. Trong project lớn nhiều category convention, mức tiết kiệm này đáng kể."

### Ví dụ rule file thực tế

**Test convention toàn codebase**:
```yaml
---
paths: ["**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts", "**/*.spec.tsx"]
---
# Test Conventions

- Use describe/it blocks with descriptive names that read as sentences
- Each test file must have at least one happy path and one error case
- Use factory functions for test data, not inline object literals
- Mock external services at the module boundary, not individual functions
- Assert behaviour, not implementation details
```

**API convention cho route handler**:
```yaml
---
paths: ["src/api/**/*", "**/routes/**/*", "**/*.controller.ts"]
---
# API Conventions

- All endpoints return { data, error, metadata } response shape
- Use Zod schemas for request validation at the handler boundary
- Log request ID on every error response
- Rate limiting configuration must be explicit, not inherited from defaults
```

**Infrastructure-as-Code convention**:
```yaml
---
paths: ["terraform/**/*", "**/*.tf", "infrastructure/**/*"]
---
# Infrastructure Conventions

- State files must reference remote backends, never local
- Use workspaces for environment separation
- Every module must be versioned with a CHANGELOG
```

### Khi nào dùng cách nào

| Tình huống | Cách tốt nhất |
|---|---|
| Standard team phổ quát cho mọi code | Root CLAUDE.md |
| Convention cho 1 thư mục package cụ thể | Directory-level CLAUDE.md |
| Convention cho loại file rải nhiều thư mục | Path-specific rule với glob pattern |
| Workflow task-specific invoke on-demand | Skills trong .claude/skills/ |

**Tập trung đề thi**: "Đề thi thường xuyên đưa scenario file test nằm cùng chỗ với source file qua nhiều thư mục. Đáp án luôn là path-specific rule với glob pattern."

### Exam traps

1. **Directory-level thay vì path-specific rule** — chọn directory-level CLAUDE.md cho convention cross-directory là sai. Khi convention phải áp dụng cho file rải 50+ thư mục (như test file cùng chỗ), path-specific rule với glob pattern là đáp án đúng. Directory-level CLAUDE.md đòi hỏi đặt file ở mọi thư mục — gánh nặng maintain khổng lồ.

2. **Convention theo loại file trong root CLAUDE.md** — đặt convention theo file type trong root CLAUDE.md gây tốn token không cần thiết. Root CLAUDE.md load cho mọi session bất kể đang edit file nào. Convention Terraform tốn token khi edit React component. Path-specific rule chỉ load khi edit file khớp, giữ token budget.

3. **Nhầm lẫn Skills với Path-Specific Rules** — cả skill và `.claude/rules/` đều auto-activate qua frontmatter `paths`, nhưng phục vụ mục đích khác nhau. Rule ở lại trong context như guidance nền — load khi Claude đọc file khớp — nên shape mỗi lần edit. Skill load on-demand như workflow kiểu task, trigger bởi intent match của model hoặc invoke tường minh. Khi câu hỏi hỏi về loading convention tự động, always-on cho 1 loại file, path-specific rule là đáp án đúng.

### Practice scenario
Codebase có file test cùng chỗ với source file qua 50+ thư mục. Team muốn mọi test follow convention giống nhau bất kể vị trí. **Đáp án đúng**: tạo 1 rule file trong `.claude/rules/` với YAML frontmatter `paths: ["**/*.test.tsx", "**/*.test.ts"]` chứa convention test.

### Build exercise
1. Tạo `.claude/rules/testing.md` với glob pattern target file test và convention test (naming, assertion, mocking)
2. Tạo `.claude/rules/api-conventions.md` với `paths` target thư mục API và convention API (response shape, validation, error handling)
3. Tạo `.claude/rules/terraform.md` với `paths` target file Terraform và convention infrastructure
4. Verify conditional loading dùng lệnh `/memory` khi edit file test (chỉ rule testing load, không phải API và Terraform)
5. Verify complementary loading khi edit API handler
6. So sánh token footprint giữa root CLAUDE.md (mọi convention luôn load) và path-specific rule (chỉ convention liên quan load)

---

## 3.4 Plan Mode vs Direct Execution

### Khái niệm mở đầu
"Quyết định không nằm ở độ khó mà ở độ mơ hồ (ambiguity). 1 bug fix khó nhưng định nghĩa rõ (stack trace rõ, 1 hàm, nguyên nhân đã biết) là direct execution." Claude Code vận hành qua 2 chiến lược thực thi khác biệt, phân biệt bởi phạm vi và độ rõ ràng của task, không phải mức độ phức tạp.

### Plan Mode — khi nào dùng
Phù hợp task phức tạp cần exploration, đánh giá, thiết kế chiến lược trước khi implement. Deploy plan mode khi:
- **Thay đổi quy mô lớn** — tái cấu trúc monolith thành microservices, tổ chức lại module system, refactor abstraction lõi
- **Nhiều approach hợp lệ tồn tại** — kiến trúc integration khác nhau với yêu cầu infrastructure khác nhau cần đánh giá
- **Quyết định kiến trúc bắt buộc** — service boundary, module dependency, API contract có hệ quả downstream
- **Sửa đổi multi-file** — migration library ảnh hưởng 45+ file cần chiến lược nhất quán
- **Cần khảo sát codebase** — dependency, data flow, cấu trúc hiện có phải map trước khi thay đổi

**Chức năng**: Plan mode cho phép khám phá an toàn. Claude đọc, phân tích, đề xuất mà không sửa file.

### Direct Execution — khi nào dùng
Phù hợp thay đổi hiểu rõ, phạm vi giới hạn. Dùng direct execution khi:
- **Thay đổi có scope tốt** — bug fix 1 file với stack trace rõ ràng
- **Approach đúng đã biết** — cái gì cần đổi, ở đâu, cách nào đã xác định
- **Scope giới hạn** — 1 hàm, 1 file, 1 sửa đổi rõ ràng

**Chức năng**: "Direct execution bỏ qua phase planning và thực hiện thay đổi ngay lập tức."

### Explore Subagent
**Mục đích**: isolate output khám phá verbose khỏi main conversation.

**Cách hoạt động**: chạy exploration isolated → tạo summary finding → trả summary về main conversation → giữ context window main sạch.

**Khi dùng**: task multi-phase mà discovery tạo output verbose nhưng implementation cần context tập trung.

### Hybrid Approach: Plan Then Execute
Chiến lược kết hợp cho investigation và implementation:

**Phase 1 — Plan**: khảo sát codebase, hiểu dependency, đánh giá approach, thiết kế chiến lược implementation.
**Phase 2 — Execute**: implement approach đã plan file-by-file với chiến lược đã quyết.

**Ví dụ scenario**: Migrate logging library qua 30 file — Plan: xác định file, map API khác biệt, thiết kế pattern, check edge case; Execute: áp dụng pattern cho từng file dùng approach đã plan.

**Insight quan trọng**: pattern là "plan THEN direct, không phải plan OR direct."

### Bảng tổng hợp quyết định

| Đặc điểm task | Mode khuyến nghị |
|---|---|
| Tái cấu trúc kiến trúc | Plan mode |
| Migration library (nhiều file) | Plan mode (sau đó direct execution) |
| Nhiều approach implementation hợp lệ | Plan mode |
| Cần khảo sát codebase | Plan mode (với Explore subagent) |
| Bug fix 1 file với stack trace rõ | Direct execution |
| Thêm validation check cho 1 hàm | Direct execution |
| Cập nhật giá trị config | Direct execution |
| Fix đã biết, vị trí đã biết, approach đã biết | Direct execution |

### Nhận diện độ phức tạp ngay từ đầu
Khi requirement nói rõ độ phức tạp (vd "restructure the monolith into microservices"), chọn plan mode ngay lập tức. Độ phức tạp được nêu trong task description, không phải suy đoán. Tránh chờ độ phức tạp lộ ra trong lúc thực thi.

### Exam traps
1. **Mặc định direct execution cho thay đổi kiến trúc multi-file** — sửa đổi multi-file với nhiều approach hợp lệ cần plan mode; direct execution có nguy cơ rework tốn kém khi dependency lộ ra muộn.
2. **Dùng plan mode cho bug fix 1 file có stack trace rõ** — vấn đề rõ, vị trí rõ, giải pháp rõ ám chỉ direct execution; plan mode thêm overhead không cần thiết.
3. **Không nhận ra pattern hybrid plan-then-execute** — đề thi test việc kết hợp plan mode investigation với direct execution implementation.
4. **Bắt đầu bằng direct execution, chuyển sang plan mode khi độ phức tạp lộ ra** — chọn mode ban đầu nên phản ánh độ phức tạp được nêu rõ trong requirement, không phải suy đoán.

### Practice scenario
3 scenario cần chọn mode:
1. Restructure monolith thành microservices
2. Fix null pointer exception ở 1 hàm với stack trace rõ
3. Migrate logging library qua 30 file

**Đáp án đúng**: Plan mode cho (1) và (3), direct execution cho (2). Lý do: (1) liên quan quyết định kiến trúc; (3) cần phối hợp multi-file; (2) rõ ràng và scope 1 chỗ.

---

## 3.5 Iterative Refinement

### Khái niệm cốt lõi
Làm việc với Claude Code cần refinement lặp lại. Output đầu tiên hiếm khi là giải pháp cuối cùng. Thành công phụ thuộc vào việc hiểu kỹ thuật refinement nào deploy trong tình huống cụ thể nào.

### Hierarchy kỹ thuật

**1. Ví dụ Input/Output cụ thể (hiệu quả nhất cho diễn giải không nhất quán)**
**Dùng khi**: prose description cho ra kết quả khác nhau qua nhiều lần chạy. **Nguyên tắc chính**: "Fix là ví dụ cụ thể" thay vì mô tả prose chi tiết hơn. **Cách triển khai**: cung cấp 2-3 ví dụ input/output chính xác; model generalize từ pattern cụ thể đáng tin cậy hơn prose; 2-3 ví dụ chọn kỹ đã đủ, tránh liệt kê case tận cùng.

```
Input:
  getUserData(userId: string): Promise<UserData>

Expected output:
  getUserData(userId: string): Promise<Result<UserData, ApiError>>
```

**Insight chính**: model áp dụng pattern cho case mới mà không cần ví dụ cho mọi scenario có thể.

**2. Test-Driven Iteration (hiệu quả nhất cho transformation phức tạp)**
**Dùng khi**: transformation phức tạp cần xử lý edge case toàn diện. **Test coverage yêu cầu**: happy path (transformation kỳ vọng chuẩn), edge case (null value, input rỗng, boundary condition), performance requirement (nếu có). **Cơ chế feedback**: chia sẻ test failure thay vì feedback prose.

```
FAIL: testMigrationHandlesNullValues
  Expected: null preserved in output JSON
  Actual: null replaced with empty string ""
```

**Lợi thế**: test output loại bỏ diễn giải mơ hồ; "Expected X, got Y" cho target sửa không mơ hồ.

**3. Interview Pattern (hiệu quả nhất cho domain lạ)**
**Dùng khi**: làm việc trong domain thiếu chuyên môn cá nhân. **Triển khai**: yêu cầu Claude hỏi câu hỏi làm rõ trước khi implement thay vì kê sẵn giải pháp.

Đối chiếu:
- Không hiệu quả: "Build me a caching layer for the API"
- Hiệu quả: "I need a caching layer. Before implementing, ask questions about requirements, edge cases, and constraints I should consider."

**Kỳ vọng đầu ra**: Claude nêu 5-10 câu hỏi có mục tiêu về những cân nhắc mà expert sẽ tự động nghĩ tới nhưng dev ít kinh nghiệm hơn có thể bỏ sót.

**Phân biệt chính**: kỹ thuật này lộ ra requirement thiếu trong domain lạ — khác với ví dụ (xử lý diễn giải không nhất quán trong domain đã biết).

### Chiến lược gửi feedback

| Tình huống | Cách tiếp cận | Lý do |
|---|---|---|
| Issue tương tác lẫn nhau | Gộp toàn bộ feedback vào 1 message | Model phải thấy mọi constraint cùng lúc để fix nhất quán |
| Issue độc lập | Lặp tuần tự (sequential) | Gộp issue độc lập gây nhầm feedback nào áp dụng chỗ nào |

**Ví dụ issue tương tác**: 3 thay đổi liên kết — error response phải có field error code, logging phải có error code dạng structured, client SDK type phải phản ánh field error code mới — cần gộp vì fix cái này ảnh hưởng cái khác.

**Ví dụ issue độc lập**: naming convention (camelCase), indentation (2 space) — xử lý tuần tự không xung đột.

### Pattern giao tiếp dựa trên ví dụ
**Trình tự tiến triển**: 1) quan sát inconsistency: prose description cho kết quả khác nhau qua nhiều lần chạy; 2) chuyển sang ví dụ: cung cấp 2-3 cặp before/after cụ thể; 3) verify generalization: test với case mới để confirm pattern áp dụng đúng; 4) thêm ví dụ edge case nếu cần: nếu case chuẩn thành công nhưng edge case fail, cung cấp ví dụ edge case có mục tiêu.

**Nguyên tắc hiệu quả**: "2-3 ví dụ chọn kỹ phủ case chuẩn và 1 edge case quan trọng là đủ."

### Bảng chọn kỹ thuật

| Tình huống | Kỹ thuật khuyến nghị |
|---|---|
| Prose description diễn giải khác nhau mỗi lần | Ví dụ input/output cụ thể |
| Transformation phức tạp nhiều edge case | Test-driven iteration |
| Làm việc domain lạ | Interview pattern |
| Nhiều issue ảnh hưởng lẫn nhau | Batch feedback (1 message) |
| Nhiều issue độc lập | Sequential feedback |

### Exam traps
1. **Refine prose thay vì chuyển sang ví dụ** — sai lầm: viết lại prose với ngôn ngữ chính xác hơn. Đúng: "Prose chính xác hơn vẫn dựa vào diễn giải. Ví dụ input/output cụ thể loại bỏ mơ hồ diễn giải."
2. **Hiểu sai batch vs sequential feedback** — issue tương tác cần feedback thống nhất; issue độc lập cần xử lý tuần tự.
3. **Nhầm Interview Pattern với kỹ thuật Ví dụ** — Interview pattern: cho domain lạ nơi dev có thể bỏ sót cân nhắc. Ví dụ: cho transformation đã biết nhưng diễn giải không nhất quán. Đây là 2 vấn đề hoàn toàn khác nhau.

### Practice scenario
Dev mô tả code transformation bằng prose, nhận kết quả không nhất quán qua nhiều lần chạy. **Đáp án đúng**: cung cấp 2-3 ví dụ input/output cụ thể thể hiện transformation before/after chính xác.

### Key takeaway
"Output đầu tiên hiếm khi là output cuối cùng." Thành công đòi hỏi khớp kỹ thuật refinement với vấn đề cụ thể: diễn giải không nhất quán cần ví dụ, transformation phức tạp cần test-driven iteration, domain lạ cần interview pattern, issue tương tác cần feedback gộp.

---

## 3.6 CI/CD Integration

### Tổng quan
Lesson này bao phủ tích hợp Claude Code vào pipeline CI/CD, biến nó từ dev tool tương tác thành engine review và generation tự động. Đề thi nhấn mạnh 5 khái niệm cốt lõi, với flag `-p` là phần được test trực tiếp nhiều nhất (Sample Question 10).

### Khái niệm chính: Flag `-p` (Non-Interactive Mode)
**Định nghĩa**: flag `-p` (hay `--print`) chuyển Claude Code sang print mode, cho phép chạy non-interactive phù hợp pipeline CI.

**Vấn đề nó giải quyết**: Claude Code mặc định là interactive mode, chờ input bàn phím. Pipeline CI không có bàn phím → job hang vô thời hạn chờ input không bao giờ tới.

```bash
# WRONG — hangs in CI
claude "Analyse this pull request for security issues"

# CORRECT — runs non-interactively
claude -p "Analyse this pull request for security issues"
```

**Ghi chú quan trọng đề thi**: "Flag `-p` là fact được test trực tiếp nhất trong Domain 3. Là Question 10 trong sample question chính thức. Khi thấy CI pipeline hang và log cho thấy Claude đang chờ input, đáp án luôn là `-p`."

**Đáp án sai phổ biến**: `CLAUDE_HEADLESS=true` (env var này không tồn tại), flag `--batch` (không tồn tại cho mục đích này), stdin redirect từ `/dev/null` (không xử lý đúng interactive mode).

### Structured Output cho CI
**Vì sao quan trọng**: "Trong CI, output của Claude Code phải machine-parseable. Không có người đọc. Hệ thống tự động xử lý nó để post inline PR comment, cập nhật dashboard, hoặc trigger downstream workflow."

**2 flag chính hoạt động cùng nhau**:

| Flag | Mục đích |
|---|---|
| `--output-format json` | Bọc run trong envelope JSON (gồm result text, session ID, cost và usage metadata) thay vì text human-readable |
| `--json-schema` | Validate output cuối của agent theo JSON Schema; chỉ hoạt động trong print mode |

```bash
claude -p \
  --output-format json \
  --json-schema '{"type":"object","properties":{"findings":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line":{"type":"integer"},"severity":{"type":"string"},"message":{"type":"string"}}}}}}' \
  "Review this PR for security issues"
```

**Trích xuất data**: "Data khớp schema nằm ở field `structured_output` của envelope — trích xuất bằng `jq '.structured_output'`, không phải từ top level."

### Session Context Isolation
**Vấn đề cốt lõi**: "Cùng 1 session Claude sinh ra code sẽ kém hiệu quả khi review chính thay đổi của nó. Đây không phải lo lắng lý thuyết; đó là hiệu ứng đo được."

**Vì sao self-review yếu hơn**: khi Claude sinh code trong 1 session, nó xây dựng reasoning context về design choice, tradeoff, alternative bị loại bỏ. Trong lúc review cùng session, prior justification này vẫn access được, làm giảm đánh giá phê phán với chính quyết định của nó.

**Giải pháp — Independent Review Instances**:
```bash
# Step 1: Generate code (session A)
claude -p "Implement the authentication middleware"

# Step 2: Review code (session B — independent, no shared context)
claude -p "Review the authentication middleware for security issues, error handling gaps, and edge cases"
```

**Nguyên tắc chính**: "Dùng 1 invocation Claude Code riêng cho review — không access reasoning context của session generation. Reviewer độc lập đánh giá code trên giá trị bản thân nó, không bị bias bởi justification trước đó."

### Incremental Review Context
**Vấn đề**: review tự động chạy mỗi push mà không có context trước sẽ re-analyze toàn bộ PR từ đầu, cho ra finding giống hệt lặp lại. Tạo noise xói mòn niềm tin dev.

**Ảnh hưởng tới dev**: "1 issue thực sự đã fix sẽ tự động biến mất, vì code đã đổi không còn trigger nó nữa. Cái vẫn tiếp tục xuất hiện lại là issue dev đã thấy và cố tình chọn không đổi; 1 lần re-scan không context không phân biệt được chúng với vấn đề mới, nên flag lại mỗi lần push."

```bash
claude -p \
  --output-format json \
  "Review this PR. Here are the findings from the previous review:
  ${PREVIOUS_FINDINGS}

  Report ONLY:
  1. New issues not in the previous findings
  2. Issues from the previous findings that are still present

  Do NOT re-report previous findings the developer has already reviewed and chosen not to act on."
```

**Vì sao quan trọng**: "Comment trùng lặp xói mòn niềm tin dev. Nếu mỗi push sinh ra 5 comment giống hệt bất kể dev đã fix hay chưa, dev ngừng đọc comment. Incremental review context giữ tỷ lệ signal-to-noise."

### CLAUDE.md cho CI Context
**Nguyên tắc**: Claude Code đọc file CLAUDE.md trong môi trường CI y hệt như interactive mode.

**Nội dung cần thiết cho CI run**: testing standard (pattern test có giá trị, cái cần tránh), fixture có sẵn (path, nội dung, cách dùng), tiêu chí review (finding critical vs minor), test coverage hiện có (đã cover gì để tránh trùng lặp).

```markdown
## Testing Standards

- Tests must use the factory pattern from test/factories/ for data creation
- Integration tests connect to the test database via test/setup/db.ts
- Do not test private implementation details — test public API contracts
- Coverage target: 80% branch coverage for new code
- Available fixtures: test/fixtures/users.json, test/fixtures/orders.json
```

### Bảng tham khảo CLI Flags

**System prompt flags**:

| Flag | Hiệu ứng |
|---|---|
| `--system-prompt "<text>"` | Thay toàn bộ default system prompt |
| `--system-prompt-file <path>` | Thay default prompt bằng nội dung file |
| `--append-system-prompt "<text>"` | Append text vào default prompt |
| `--append-system-prompt-file <path>` | Append nội dung file vào default prompt |

**Khi nào append vs replace**: Append khi Claude vẫn nên là coding assistant tuân theo rule bổ sung, giữ tool guidance, safety instruction, coding convention mặc định. Replace khi identity hoặc permission model khác default của Claude Code (vd agent không phải coding trong pipeline không giám sát).

**Headless output và limit (print mode)**:

| Flag | Hiệu ứng |
|---|---|
| `--output-format text\|json\|stream-json` | Shape output cho `-p`; format json machine-parseable |
| `--input-format text\|stream-json` | Shape input cho `-p` |
| `--json-schema '<schema>'` | Output validate theo schema cho `-p`; với `--output-format json` nằm trong field `structured_output` của envelope |
| `--max-turns <n>` | Giới hạn số turn agentic, rồi thoát |
| `--verbose` | Output đầy đủ theo từng turn |

**Permission, tool, và context**:

| Flag | Hiệu ứng |
|---|---|
| `--permission-mode <mode>` | Bắt đầu ở `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, hoặc `bypassPermissions` |
| `--allowedTools "<rules>"` | Tool chạy không cần permission prompt |
| `--disallowedTools "<rules>"` | Deny rule; bare tool name loại tool hoàn toàn |
| `--tools "Bash,Edit,Read"` | Giới hạn tool built-in nào có sẵn |
| `--add-dir <path>` | Thêm thư mục Claude được đọc/sửa |
| `--model <alias\|name>` | Set model cho session |

**Session và start-up flags**: `-c`/`--continue` — resume conversation gần nhất trong thư mục hiện tại. `-r`/`--resume <id|name>` — resume session cụ thể. `--bare` — minimal mode bỏ auto-discovery hook, skill, plugin, MCP server, auto memory, và CLAUDE.md; chỉ để lại Bash và tool read/edit file. Dùng `--bare` khi muốn run script nhanh, dự đoán được, không cần project configuration load.

### Batch API vs Real-Time cho CI Workflow

| Loại workflow | API chọn | Lý do |
|---|---|---|
| Pre-merge check (blocking) | Real-time (đồng bộ) | Dev đợi kết quả |
| Technical debt report overnight | Batch API | Không nhạy latency, tiết kiệm 50% |
| Code audit hàng tuần | Batch API | Scheduled, chịu được latency |
| Test generation ban đêm | Batch API | Chạy qua đêm, review buổi sáng sau |

**Phân biệt quan trọng**: "Message Batches API tiết kiệm 50% cost nhưng thời gian xử lý tới 24 giờ, không có SLA latency đảm bảo." Vì vậy pre-merge check là workflow blocking, Batch API không phù hợp vì không đảm bảo latency.

### Exam traps
1. **Fix sai cho pipeline hang** — triệu chứng: CI pipeline hang, log cho thấy Claude chờ input tương tác. Đáp án sai: `CLAUDE_HEADLESS=true`, flag `--batch`, stdin redirect từ `/dev/null`. Đáp án đúng: flag `-p` (hay `--print`).
2. **Giả định self-review hiệu quả** — hiểu sai: review code cùng session với generation hiệu quả tương đương. Thực tế: reasoning context trước đó làm bias reviewer chống lại việc chất vấn quyết định chính nó. Fix: dùng independent review instance không share session context.
3. **Dùng Batch API cho pre-merge check** — hiểu sai: cost saving của Batch API áp dụng cho mọi workflow CI. Thực tế: không đảm bảo latency khiến batch không phù hợp workflow blocking. Fix: dùng real-time API cho check blocking; batch API cho analysis overnight hoặc weekly.
4. **Bỏ qua incremental review context** — hiểu sai: mỗi lần review có thể chạy độc lập mà không cần finding trước. Thực tế: comment trùng lặp xuất hiện mỗi push bất kể issue đã fix hay chưa. Fix: include finding trước trong context và yêu cầu Claude chỉ report issue mới hoặc chưa xử lý.

### Build exercise
1. Non-interactive execution: viết CI script dùng flag `claude -p` chạy xong không hang
2. Structured JSON output: thêm `--output-format json` và `--json-schema` để có finding machine-parseable
3. Inline PR comment: parse JSON output và post finding tại đúng file/line
4. CLAUDE.md documentation: tạo section CI-relevant document testing standard, fixture có sẵn, tiêu chí review
5. Session isolation: cấu hình 2 invocation `claude -p` riêng — 1 cho generation, 1 cho review độc lập không share context
6. Incremental review: lưu finding trước, include vào run sau, yêu cầu Claude chỉ report issue mới hoặc chưa xử lý

**Key takeaway**: Flag `-p` là điểm ghi nhớ quan trọng nhất cho Domain 3. Hiểu session isolation, yêu cầu structured output, và pattern incremental review hoàn thiện năng lực cho Task 3.6.
