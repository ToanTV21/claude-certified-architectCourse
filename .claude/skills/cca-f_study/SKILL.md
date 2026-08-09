---
name: cca-f_study
description: Chuyển 1 đoạn nội dung bài giảng (transcript/lesson text) của khóa FPT Claude Code Developer thành giải thích tiếng Việt + code sample Python trong đúng session folder, theo format chuẩn của project CLAUDE.md. Dùng khi user paste nội dung lesson mới và yêu cầu "viết giải thích + code cho session X", "note lại bài học này", hoặc "làm bài tập cho phần Y".
---

# CCA-F Study — Lesson-to-Notes-and-Code

Skill này đóng gói lại quy trình: user paste 1 đoạn nội dung bài học (lesson content/transcript,
thường kèm code mẫu) → Claude Code note lại kiến thức + viết bài tập minh họa, đúng theo
convention đã định nghĩa trong `CLAUDE.md` của project `fpt-claude-study`.

## Khi nào dùng skill này

- User paste nội dung 1 lesson/section trong khóa học (có thể kèm code Python mẫu từ course)
  và yêu cầu note lại hoặc viết bài tập cho session tương ứng
- User nói "note session NN", "làm bài tập cho phần...", "viết giải thích + code sample cho..."
- User yêu cầu tạo skill/tái sử dụng quy trình ghi chú bài học (chính là yêu cầu đã tạo ra skill này)

## Input cần xác định trước khi làm

1. **Session đích** — folder `sessions/NN-ten-session/` nào? Nếu user không nói rõ, suy ra từ nội dung
   lesson (vd nội dung về "generate test dataset" → thuộc `02-prompt-evaluation`) hoặc hỏi lại nếu không chắc.
2. **Tên lesson/chủ đề** — dùng để đặt tên file bài tập theo pattern
   `<NN>_<ten_lesson_snake_case>_exercise.py` trong `exercises/`, `NN` là số thứ tự tiếp theo
   (xem file đã có trong folder `exercises/` để không trùng số).

## Quy trình thực hiện

### Bước 1 — Đọc context project trước
Đọc `CLAUDE.md` ở root project (nếu chưa có trong context) để nắm đúng convention hiện hành —
đặc biệt là phần "AI Behavior in This Project", "Note-Taking Template", "Exercise Template".
Đọc `sessions/NN-ten-session/notes.md` hiện có để biết đã note tới đâu, tránh ghi trùng.

### Bước 2 — Cập nhật `notes.md` của session
Thêm 1 section mới (hoặc mở rộng section có sẵn) vào đúng vị trí trong `notes.md`, theo cấu trúc
Note-Taking Template trong CLAUDE.md:
- Giải thích khái niệm bằng **tiếng Việt**, giữ nguyên **tiếng Anh** cho keyword/thuật ngữ kỹ thuật
  (tên API, param, method, class...) — không dịch các từ này
- Nếu lesson có ví dụ cụ thể (vd 1 use case end-to-end), viết lại thành 1 sub-section riêng, có thể
  kèm snippet code ngắn minh họa trực tiếp trong notes.md (không thay thế cho file bài tập đầy đủ)
- Tick checkbox tương ứng trong phần "Lessons trong section này" ở đầu file (nếu có)
- Cập nhật bảng "Important APIs / Parameters" và "Gotchas" nếu lesson giới thiệu API/param/gotcha mới

### Bước 3 — Viết file bài tập Python riêng
Tạo file mới trong `sessions/NN-ten-session/exercises/`, theo đúng Exercise Template trong CLAUDE.md:
- Header docstring: `Exercise <NN>: <Tên bài tập>`, `Session: <Tên session>`, `Objective: <mục tiêu>`
- Dùng `from dotenv import load_dotenv` + `anthropic.Anthropic()` — không hardcode API key
- Model: ưu tiên `claude-haiku-4-5` cho dev/test (đúng rule 1 trong CLAUDE.md), trừ khi lesson gốc
  yêu cầu rõ model khác
- **Mọi đoạn code, mọi hàm, mọi parameter đều phải có comment giải thích** (rule 3 — bắt buộc,
  vì đây là môi trường học, không được để code trơ trụi)
- Nếu lesson gốc đã cho sẵn code mẫu (như trong transcript khóa học), giữ đúng logic/luồng chạy đó,
  chỉ bổ sung comment + điều chỉnh nhỏ cho khớp convention project (vd đổi model sang `claude-haiku-4-5`,
  thêm docstring, thêm xử lý lỗi cơ bản nếu hợp lý) — không tự ý đổi kiến trúc bài tập gốc
- Kết thúc bằng `if __name__ == "__main__": main()`

### Bước 4 — Đối chiếu với kiến thức Claude API hiện hành
Trước khi chốt code, đối chiếu nhanh với skill `claude-api` (model ID, tham số API còn hợp lệ hay
đã deprecated) — đặc biệt nếu lesson gốc dùng model/param cũ. Ưu tiên giữ đúng những gì lesson dạy
(vì đây là nội dung khóa học), nhưng nếu phát hiện param/model đã bị loại bỏ hoàn toàn (lỗi 400 chắc
chắn xảy ra), ghi chú lại trong `notes.md` phần Gotchas thay vì âm thầm sửa sai lệch với bài giảng gốc.

### Bước 5 — Git commit + push (bắt buộc theo rule 6b)
Sau khi write/edit xong `notes.md` và file bài tập:
```bash
git add sessions/<NN-ten-session>/notes.md sessions/<NN-ten-session>/exercises/<file>.py
git commit -m "<mô tả ngắn gọn>"
git push
```
Không gộp nhiều lesson khác nhau vào 1 commit.

## Không làm

- Không tạo file note/bài tập ngoài đúng `sessions/NN-ten-session/` tương ứng
- Không viết code thiếu comment (vi phạm rule 3 — bắt buộc với mọi bài tập trong project này)
- Không tự ý dùng model khác `claude-haiku-4-5` cho bài tập dev/test trừ khi có lý do rõ ràng
- Không qua bước cập nhật CLAUDE.md status table nếu session đó chưa hoàn thành toàn bộ — chỉ tick
  checkbox trong `notes.md` của session, để trạng thái tổng ở CLAUDE.md do user tự cập nhật khi xong cả session
