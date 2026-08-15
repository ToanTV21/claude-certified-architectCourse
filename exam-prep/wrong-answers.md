# Wrong Answers Log

> Mỗi khi làm sai 1 câu (mock exam, quiz module, hoặc final assessment),
> ghi lại vào đây để ôn lại trước ngày thi thật.

## Template
```
### [YYYY-MM-DD] Nguồn: (mock exam / quiz module X / final assessment)
**Câu hỏi:** ...
**Đáp án tôi chọn:** ...
**Đáp án đúng:** ...
**Vì sao sai / bài học rút ra:** ...
**Link liên quan:** notes/xx-....md
```

---

<!-- Thêm entry mới bên dưới dòng này -->

### [2026-08-15] Nguồn: mock exam (screenshot, domain 04 · Prompt Engineering & Structured Output)
**Câu hỏi:** QA testing thấy Claude tuân thủ system prompt guideline tốt trong 10-15 lượt đầu, nhưng
đến lượt 25-30 bắt đầu lệch (dùng tone informal khi yêu cầu formal, bỏ format bắt buộc, lộ loại
thông tin bị hạn chế). Conversation length vẫn trong giới hạn context (~30K/200K token). Cách hiệu
quả nhất để giữ hành vi nhất quán xuyên suốt hội thoại dài?
**Đáp án tôi chọn:** Implement post-response validation that regenerates each response until it
conforms to the specified guidelines.
**Đáp án đúng:** Insert user-role messages that reinforce critical guidelines at natural
conversation breakpoints, especially before complex requests.
**Vì sao sai / bài học rút ra:** Chọn "validate-and-regenerate" là bẫy overengineering/downstream
fix — tốn thêm 1 lượt gọi model mỗi response, không giải quyết gốc rễ (guideline bị "trôi" ra khỏi
vùng attention hiệu quả khi hội thoại dài, dù còn dư context window). Đáp án đúng sửa TẠI NGUỒN
bằng cách chủ động bơm lại guideline quan trọng vào lịch sử hội thoại đúng thời điểm (breakpoint tự
nhiên, trước request phức tạp) — quản lý context có chủ đích thay vì phụ thuộc vào long-history
recall vốn không đáng tin cậy. 2 đáp án loại khác cũng sai: dời guideline vào first user message
(vẫn bị "trôi" theo cùng cơ chế), hay tự động reset conversation sau 20 lượt (tốn kém, làm gián đoạn
UX, không giải quyết nguyên nhân).
**Meta-pattern áp dụng:** #16 — Trôi hướng dẫn qua nhiều lượt hội thoại: sửa bằng few-shot cụ thể
hoặc chèn lại lời nhắc định kỳ, KHÔNG phải bắt đầu lại toàn bộ hội thoại hay validate-and-regenerate
tốn kém.
**Link liên quan:** [references.md#L418](references.md) (PHẦN III, mục 16)

---

## 📍 PRE-TEST (baseline) — 2026-08-15 — guided.maithienan.com/certifications/ccar-f

> Toàn bộ nội dung (tổng quan + chi tiết đầy đủ 27 câu sai) đã chuyển sang file riêng:
> [maithienan_website_test_2026-08-15_1734.md](maithienan_website_test_2026-08-15_1734.md).
> Điểm baseline: 32–33/60 (~53–55%). Domain yếu nhất: D4 Prompt Engineering & Structured Output
> (4/13, 31%). Có 1 nghi vấn key đáp án của site tự mâu thuẫn (Q26 vs Q15) — xem chi tiết trong
> file trên.
