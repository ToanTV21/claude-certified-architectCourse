# exam-prep/ — Bản đồ ôn thi CCA-F

> Đây là trang chỉ mục. **Đọc file này trước, rồi đi theo thứ tự bên dưới.**
> Mục tiêu: 720/1000 (≈ 43–44/60 câu). Ngưỡng an toàn tự đặt: 48/60.

---

## 1. Thứ tự đọc lần đầu (nếu bạn mới quay lại folder này)

| Bước | File | Đọc để làm gì | Thời lượng |
|------|------|---------------|-----------|
| 1️⃣ | [study-plan.md](study-plan.md) | **Bắt đầu từ đây.** Chiến lược tổng thể: trọng số 5 domain, lịch 4 tuần, quy trình luyện đề, định nghĩa "sẵn sàng thi" | 20 phút |
| 2️⃣ | [references.md](references.md) | Nguồn kiến thức CHÍNH. Toàn bộ guide chính thức đã tổng hợp lại: 13 chương lý thuyết + ghi chú theo 5 domain + 18 meta-pattern | 2–3 giờ |
| 3️⃣ | [cheat-sheet.md](cheat-sheet.md) | Tra cứu nhanh cú pháp/tham số API (`temperature`, `tool_choice`, streaming events...) | 15 phút |
| 4️⃣ | [flashcards.md](flashcards.md) | 45 câu Q&A ngắn — tự kiểm tra fact rời rạc | 30 phút |
| 5️⃣ | [practice-questions.md](practice-questions.md) | 10 câu warm-up mức định nghĩa — làm nóng trước khi vào mock đầy đủ | 15 phút |
| 6️⃣ | `mock-exams/set-NN.md` | Bộ đề đầy đủ 60 câu (chưa sinh — xem mục 4 bên dưới) | 120 phút/bộ |
| 7️⃣ | [mock-exam-log.md](mock-exam-log.md) | Ghi điểm **theo từng domain** sau mỗi lần thi thử | 5 phút/lần |
| 8️⃣ | [wrong-answers.md](wrong-answers.md) | Log câu sai. **Tài sản ôn thi quan trọng nhất** — đọc lại nhiều lần | liên tục |

---

## 2. Vai trò của từng file (đọc khi nào, không phải đọc gì)

### 📌 [study-plan.md](study-plan.md) — La bàn
Mở lại **mỗi đầu tuần** để biết tuần này làm gì. Chứa:
- Bảng phân bổ effort theo trọng số domain (27/18/20/20/15)
- Lịch chi tiết 28 ngày (D1 → D28) + 2 tuần buffer
- Quy trình 5 bước cho mọi mock exam
- Checklist 4 bước đọc đề trong lúc thi
- Bảng 15 bẫy đã biết

### 📚 [references.md](references.md) — Sách giáo khoa
Nguồn **duy nhất** đáng tin khi có mâu thuẫn. Cấu trúc:
- Format bài thi + 5 lĩnh vực + 8 kịch bản
- **PHẦN I**: 13 chương lý thuyết (API → Tools → Agent SDK → MCP → Claude Code → Prompt eng → Batch → Decomposition → Escalation → Error handling → Context → Provenance → Built-in tools)
- **PHẦN II**: ghi chú gom theo đúng 5 domain thi
- **PHẦN III**: ⭐ **18 meta-pattern** — phần giá trị nhất, học thuộc phần này
- Cuối file: danh sách **chủ đề CHẮC CHẮN KHÔNG thi** (đọc để không học lệch)
- Đầu file: link 4 web thi thử cộng đồng

### ⚡ [cheat-sheet.md](cheat-sheet.md) — Tra nhanh
Dùng khi *"cú pháp cái này là gì nhỉ"*. Không dùng để học lần đầu.

### 🃏 [flashcards.md](flashcards.md) — Ôn nhanh
Dùng lúc rảnh, ngày trước khi thi. Bộ 1 = fact cơ bản, Bộ 2 = 25 câu từ guide đầy đủ.

### 📝 [practice-questions.md](practice-questions.md) — Warm-up
10 câu mức định nghĩa. **Không đại diện độ khó thi thật** (đề thật là scenario-based).

### 📊 [mock-exam-log.md](mock-exam-log.md) — Bảng điểm
Cập nhật sau **mọi** lần thi thử, kể cả web ngoài. Tách điểm theo domain để biết mình yếu ở đâu —
tổng điểm không nói lên điều đó.

### 🔴 [wrong-answers.md](wrong-answers.md) — Sổ lỗi
Mỗi câu sai → 1 entry, bắt buộc trả lời 3 câu hỏi:
1. Đáp án đúng đúng ở chỗ nào?
2. Bẫy nào đã hiệu quả với tôi?
3. Nó thuộc meta-pattern nào trong 18 pattern ở references.md PHẦN III?

---

## 3. Ba chế độ sử dụng folder này

### 🟢 Chế độ HỌC (tuần 1–3)
```
references.md (1 chương)  →  tự tóm tắt bằng lời mình  →  flashcards liên quan
                          →  bổ sung cheat-sheet nếu thiếu cú pháp
```

### 🟡 Chế độ LUYỆN ĐỀ (tuần 2–4)
```
mock-exams/set-NN.md (120 phút, làm mù)
  →  tự chấm theo domain
  →  mock-exam-log.md (ghi điểm)
  →  wrong-answers.md (mỗi câu sai 1 entry)
  →  domain < 70% ?  →  quay lại references.md chương tương ứng
```

### 🔴 Chế độ NƯỚC RÚT (3 ngày cuối)
```
wrong-answers.md (toàn bộ)  →  18 meta-pattern  →  cheat-sheet  →  flashcards
```
Không đọc references.md PHẦN I ở giai đoạn này — quá dài, không kịp hấp thụ.

---

## 4. Sinh bộ đề mới

Thư mục `mock-exams/` chứa các bộ đề đầy đủ. Sinh bộ mới bằng cách yêu cầu Claude Code:

> *"Sinh Mock Set N vào `exam-prep/mock-exams/set-0N.md`, 60 câu scenario-based,
> phân bổ theo domain 16/11/12/12/9, đáp án + giải thích ẩn trong `<details>`."*

Phân bổ chuẩn 60 câu theo trọng số chính thức:

| Domain | Trọng số | Số câu |
|--------|----------|--------|
| D1 — Agentic Architecture & Orchestration | 27% | 16 |
| D2 — Tool Design & MCP Integration | 18% | 11 |
| D3 — Claude Code Config & Workflows | 20% | 12 |
| D4 — Prompt Engineering & Structured Output | 20% | 12 |
| D5 — Context Management & Reliability | 15% | 9 |

---

## 5. Quy tắc bảo trì folder

- Kiến thức mới (từ web thi thử, từ course) → bổ sung vào **references.md**, không tạo file rời.
- Fact ngắn dễ quên → **flashcards.md**. Cú pháp/tham số → **cheat-sheet.md**.
- Mâu thuẫn giữa nguồn ngoài và references.md → **tin references.md** (bám guide gốc).
- Mọi thay đổi → `git add` + `commit` + `push` ngay (CLAUDE.md rule 6b).
