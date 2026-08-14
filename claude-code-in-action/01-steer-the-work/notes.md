# Section 01: Steer the Work

> Chủ đề: điều khiển (**steer**) Claude Code trong các session dài — làm sao giữ context
> đúng hướng, không để agent đi lệch mục tiêu qua nhiều lượt.

## Lessons trong section này
- [x] Steering Long Sessions

## Key Concepts

Task ngắn (quick task) thì dễ: hỏi → Claude làm → check kết quả. Nhưng task dài (refactor
nhiều file, build feature mới) có thể chạy hàng giờ, và càng phải **steer** (chỉnh hướng)
Claude nhiều lần thì càng tốn thời gian. Chốt lại 2 thói quen cốt lõi:

1. **Scope trước khi Claude chạy** — dùng **plan mode**.
2. **Steer trong lúc Claude đang chạy** — dùng compact, rewind, goal, loop, worktrees.

### 1. Scope the work first — Plan Mode

Trước khi Claude viết dòng code đầu tiên, bắt nó lập **plan**. Ở plan mode, Claude chỉ
research (đọc code) ở chế độ **read-only** — không sửa gì cả. Nó đọc code, xác định cần
thay đổi gì, rồi đưa ra 1 plan để user review.

Khi nhận plan, **đọc kỹ, đừng skim**. Plan càng chi tiết thì càng ít bất ngờ khi Claude bắt
đầu execute. Nếu thiếu/sai gì, yêu cầu Claude bổ sung ngay trong plan — **iterate trên plan
nhanh hơn nhiều** so với để Claude chạy tự do rồi mới dọn dẹp hậu quả.

### 2. Steer while Claude works

#### Compact
`/compact` tóm tắt (summarize) conversation hiện tại, dùng summary đó làm context mới, và
xoá message cũ đi → giải phóng context window để Claude chạy tiếp. Rủi ro: thứ quan trọng
có thể bị rớt khỏi summary → Claude bị lệch hướng (drift).

→ **Đừng chạy `/compact` trơ trụi.** Thêm instruction ngay sau lệnh để chỉ Claude nên giữ
gì khi tóm tắt. Vd nếu vừa debug xong và giờ chỉ quan tâm API changes:
```
/compact Focus on the --version flag implementation
```
Bất cứ gì viết sau `/compact` sẽ định hình summary giữ lại cái gì — đây chính là "steering
wheel" cho context.

#### Rewind
Khi Claude đi sai hướng, không cần prompt để kéo nó quay lại — dùng **rewind** để về lại
checkpoint gần nhất. Mỗi user prompt tự động tạo 1 checkpoint có thể revert. Mở rewind menu
bằng cách **double tap Esc** khi prompt đang trống.

Các option trong rewind menu:
- **Restore code and conversation** — rollback cả code lẫn conversation cùng lúc
- **Restore conversation** — chỉ rollback chat
- **Restore code** — chỉ rollback file
- **Summarize from here** — tóm tắt mọi thứ *sau* checkpoint (hữu ích nếu có 1 đoạn side
  conversation lạc đề, muốn giải phóng context)
- **Summarize up to here** — tóm tắt mọi thứ *trước* checkpoint (hữu ích khi có 1 giai đoạn
  setup dài muốn nén lại, nhưng vẫn giữ nguyên phần implementation phía sau)

#### Goal
Khác với việc luôn ngồi canh và sửa từng bước (hands-on), `/goal` cho Claude chạy **tự chủ
hơn**: user mô tả điều kiện "done" là gì, Claude tự chạy qua nhiều turn cho đến khi 1 fast
evaluator xác nhận điều kiện đó đã đạt — không dừng ngay lần đầu *tưởng* là xong.

Vd:
```
/goal all tests in src/billing pass, and the type checker reports zero errors
```
Huỷ goal bằng `/goal clear`.

**Constraint quan trọng:** evaluator **chỉ đọc transcript**, nên điều kiện goal phải
**checkable từ output** mà Claude thực sự tạo ra (vd kết quả chạy test), không thể là điều
kiện mơ hồ không quan sát được qua output.

#### Loop
`/loop` chạy 1 prompt lặp lại theo interval giữa các turn — có thể **fixed interval** hoặc
**self-paced**. Dùng để poll trạng thái bên ngoài (external state) như CI run hay deploy,
rồi hành động khi trạng thái đó thay đổi. Dừng loop bằng cách nhấn **Esc**.

### 3. Run parallel work with Worktrees

Ẩn dụ "steering" ở trên giả định 1 steering wheel trong 1 xe. Nhưng khi chạy **nhiều agent
song song** trên cùng 1 codebase, không thể để 2 steering wheel trong 1 xe — 2 Claude
session cùng sửa chung file sẽ dẫn tới conflict.

→ Dùng **worktree**: mỗi session được cấp 1 **file tree độc lập riêng**, nên các session
không thể ghi đè (clobber) thay đổi của nhau. Khi 1 session kết thúc, worktree sạch (clean)
của nó tự động bị xoá.

File đáng chú ý: **`.worktreeinclude`** ở root repo — liệt kê các file bị git-ignore nhưng
cần copy vào mỗi worktree (vd file env variable, local config cần có ở mọi worktree nhưng
không muốn commit vào version control).

## Important Config / Files / Commands
| Name | Loại | Scope | Notes |
|------|------|-------|-------|
| `/compact <hint>` | slash command | session | Tóm tắt conversation + xoá history cũ; hint sau command định hướng nội dung được giữ lại |
| Rewind menu (double-tap Esc) | UI action | session | Revert code/conversation về checkpoint (mỗi user prompt = 1 checkpoint) |
| `/goal <condition>` | slash command | session | Set completion condition; Claude tự chạy nhiều turn tới khi fast evaluator xác nhận đạt |
| `/goal clear` | slash command | session | Huỷ goal đang set |
| `/loop <interval> <prompt>` | slash command | session | Chạy lại prompt/slash command theo interval (fixed hoặc self-paced); Esc để dừng |
| `.worktreeinclude` | file | repo root | Liệt kê git-ignored file cần copy vào mỗi worktree mới (vd `.env`, local config) |
| Worktree | Claude Code feature | per-session | Cấp file tree riêng cho mỗi session để chạy song song không đụng file nhau |

## Gotchas
- [ ] `/compact` không kèm hint → dễ mất context quan trọng, Claude drift khỏi mục tiêu ban đầu
- [ ] `/goal` evaluator **chỉ đọc transcript** — điều kiện goal phải checkable từ output thực tế (vd kết quả test run), không thể là tiêu chí không thể quan sát qua output
- [ ] Chạy nhiều agent song song **không dùng worktree** → risk conflict do 2 session cùng sửa 1 file
- [ ] Plan mode chỉ có giá trị nếu user **đọc kỹ** plan trước khi execute — skim qua sẽ mất tác dụng "ít bất ngờ hơn"

## CCA-F Exam Tips
- Phân biệt rõ **Compact** (nén context, có thể mất thông tin) vs **Rewind** (revert về checkpoint, không mất — chỉ quay lại trạng thái cũ) vs **Goal** (set completion condition, chạy tự động nhiều turn) vs **Loop** (chạy lặp theo interval, dùng cho polling external state)
- `/goal` evaluator chỉ nhìn transcript — đây là điểm hay bị hỏi dạng "tại sao goal condition X không hoạt động đúng" (vì X không thể verify được từ output Claude tạo ra)
- Worktree = cơ chế an toàn cho **parallel agent execution**, tránh race condition khi nhiều session sửa cùng codebase

## Code / Config Snippets
```bash
# Compact có định hướng nội dung giữ lại
/compact Focus on the --version flag implementation

# Set 1 goal có thể verify được từ test output
/goal all tests in src/billing pass, and the type checker reports zero errors

# Huỷ goal đang set
/goal clear
```

## Questions / Unclear Points
- ?
