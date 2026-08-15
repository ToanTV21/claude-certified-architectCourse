# Báo cáo đánh giá lại — guided.maithienan.com CCA-F Pre-test

> **Nguồn:** https://guided.maithienan.com/certifications/ccar-f
> **Ngày làm bài:** 2026-08-15 (PRE-TEST — baseline trước khi bắt đầu 4-tuần study-plan)
> **Báo cáo tạo lúc:** 2026-08-15 17:34
> **Mục đích:** đối chiếu lại điểm + key đáp án của site bằng hiểu biết về guidance chính thức
> của Anthropic (Building Effective Agents, Claude Code docs, MCP spec, tool-use guide), không
> chỉ tin kết quả site tự chấm — site này là **nguồn cộng đồng, không phải đề chính thức**.
> Chi tiết từng câu sai (27 câu, đầy đủ 5 mục: câu hỏi / đáp án đã chọn / đáp án đúng / bài học /
> link tham chiếu) nằm trong [wrong-answers.md](wrong-answers.md) — file này là bản tóm tắt để
> track nhanh qua các lần thi thử sau.

---

## 1. Điểm số

| | Site tự chấm | Tự đếm lại theo nhãn Đúng/Sai từng câu |
|---|---|---|
| Tổng | 32/60 (53%) | 33/60 (55%) |

Lệch 1 câu — nhiều khả năng là lỗi đếm nhỏ của site, không phải lỗi đọc đề. Dùng **32–33/60
(~53–55%)** làm điểm baseline.

- Ngưỡng pass thật: 43–44/60 (72%) → **còn thiếu ~11 câu**
- Ngưỡng an toàn tự đặt trước khi đăng ký thi: 48/60 (80%) → **còn thiếu ~15 câu**
- Đây là bài test ĐẦU TIÊN trước khi học nghiêm túc theo study-plan.md — kết quả này là baseline
  bình thường, không phải tín hiệu xấu, miễn là các mock set sau cải thiện đều đặn.

---

## 2. Nhãn domain của site KHÔNG đáng tin

Đếm theo nhãn domain (01–05) mà chính site gắn cho từng câu:

| Domain | Site gắn nhãn | Tỷ trọng chính thức (60 câu) |
|---|---|---|
| D1 — Agentic Architecture & Orchestration | 9 | **16** |
| D2 — Tool Design & MCP Integration | 9 | 11 |
| D3 — Claude Code Configuration & Workflows | 9 | 12 |
| D4 — Prompt Engineering & Structured Output | 14 | 12 |
| D5 — Context Management & Reliability | 19 | 9 |

Site **thiếu gần một nửa** số câu Domain 1 lẽ ra phải có (domain nặng nhất, 27% đề thi thật) và
**thừa hơn gấp đôi** số câu Domain 5. Đã tự gắn lại domain theo NỘI DUNG từng câu hỏi (không theo
nhãn site) — kết quả sau khi gắn lại:

| Domain | Sau khi gắn lại theo nội dung |
|---|---|
| D1 | 9 |
| D2 | 14 |
| D3 | 15 |
| D4 | 13 |
| D5 | 9 |

Vẫn không khớp tỷ trọng chính thức → **kết luận: bộ đề này của site KHÔNG đại diện đúng cấu trúc
đề thi thật**, đặc biệt thiếu hẳn câu Domain 1. Chỉ dùng để luyện phản xạ đọc câu hỏi kiểu
scenario-based, không dùng bộ đề này để tự đánh giá domain nào yếu domain nào mạnh cho đề thi thật.

---

## 3. Điểm theo domain (gắn lại theo nội dung, N/tổng-câu-trong-set-này)

| Domain | Đúng/Tổng | % | Đánh giá |
|---|---|---|---|
| D1 — Agentic Architecture & Orchestration | 6/9 | 67% | Trên ngưỡng báo động (70%) một chút — cần củng cố |
| D2 — Tool Design & MCP Integration | 8/14 | 57% | Dưới ngưỡng báo động |
| D3 — Claude Code Configuration & Workflows | 10/15 | 67% | Trên ngưỡng báo động một chút |
| **D4 — Prompt Engineering & Structured Output** | **4/13** | **31%** | **⚠️ Yếu nhất rõ rệt — xa ngưỡng báo động** |
| D5 — Context Management & Reliability | 5/9 | 56% | Dưới ngưỡng báo động |

**Khuyến nghị:** Domain 4 (20% trọng số đề thi thật) đang là điểm yếu rõ rệt nhất, không phải yếu
đều các domain. Nên đẩy lịch ôn Domain 4 (study-plan.md D15–D16, hiện xếp tuần 3) lên sớm hơn thay
vì chờ đúng lịch, vì đây là domain có gap lớn nhất và trọng số cao thứ nhì.

---

## 4. Vấn đề chất lượng đề phát hiện được khi đối chiếu

### ⚠️ Q26 — key đáp án của site tự mâu thuẫn với Q15
Q15 và Q26 là gần như cùng 1 kịch bản: phân phối câu hỏi cho hệ nhiều subagent, độ phức tạp
"evolving as users discover new applications". Nhưng đáp án đúng theo key của site **ngược nhau**:

- Q15 → đúng là "coordinator tự đánh giá và quyết định động (dynamic)"
- Q26 → đúng là "tạo fast-track cố định cho câu factual", và đánh dấu SAI chính đáp án "coordinator
  quyết định động" — vốn là đáp án ĐÚNG ở Q15!

Nhiều khả năng là lỗi sinh đề trùng lặp/gán nhầm key của site, **không tính là lỗ hổng kiến thức
thật**. Bài học: cả 2 pattern đều đúng tùy ngữ cảnh — routing cố định khi phân loại rẻ + chính xác
cho 2 nhóm rõ ràng; coordinator quyết định động khi độ phức tạp nhiều mức không dự đoán trước được.

### Q34, Q55 — 2 lựa chọn diễn đạt gần giống hệt nhau
Không có tài liệu chính thức nào phân biệt rạch ròi 2 cách diễn đạt được đưa ra làm đáp án đúng/sai
ở 2 câu này → chất lượng câu hỏi thấp của nguồn cộng đồng, nếu chọn lại vẫn sai thì không cần lo.

### ✅ Đã verify: `--max-budget-usd` (Q19) là flag THẬT
Tra cứu trực tiếp `code.claude.com/docs/en/cli-reference`: `--max-budget-usd` là flag thật của
`claude -p` (print mode only, giới hạn USD spend/invocation, tính cả chi phí subagent) — không
phải bẫy hư cấu, học thuộc yên tâm cùng `--max-turns`.

### Ngoài các mục trên
Tất cả 24 câu sai còn lại đối chiếu đúng với key của site — không phát hiện thêm lỗi nào khác
trong 60 câu.

---

## 5. Bài học nổi bật (rút gọn từ 27 câu sai — chi tiết đầy đủ trong wrong-answers.md)

1. **Tách tool khi tham số bắt buộc khác nhau theo operation** (Q2, Q25) — few-shot/description
   không thay được việc sửa schema.
2. **Gộp tool khi 2 tool chồng lấn ngữ nghĩa** (Q53) — hướng ngược Q2/Q25 nhưng cùng nguyên tắc:
   ranh giới tool phải map 1:1 với năng lực.
3. **Sửa tại nguồn (context/tiêu chuẩn) thay vì lọc/sửa hậu kỳ** (Q3, Q29, Q17, Q33, Q56) — lặp
   lại nhiều lần nhất trong các câu sai của bạn, đáng chú ý nhất.
4. **Escalation dựa trên tiêu chí tường minh (giải quyết được hay không), không dựa cảm xúc** (Q16).
5. **MCP: lỗi tầng gọi (params sai) → protocol error; lỗi tầng thực thi (business/service) → tool
   result isError:true** (Q10). MCP có primitive **Resources** tách biệt với **Tools**, dùng để
   expose catalog/schema không cần tool-call round-trip (Q60).
6. **`tool_choice` ép buộc chỉ nên áp dụng đúng 1 lượt cần đảm bảo thứ tự, không áp dụng toàn
   pipeline** (Q52) — nếu không sẽ chặn luôn các tool khác về sau.
7. **Debug là quá trình adaptive** — không lập plan đầy đủ trước khi đọc bất kỳ file nào (Q35);
   review đa file cần agentic tool (đọc + search theo dấu vết) chứ không phải static context
   nhồi thêm file (Q37).
8. **Progressive summarization** (tóm tắt phần cũ, giữ verbatim phần gần đây) dùng khi cần RECALL
   nhiều chủ đề đã đóng trong hội thoại dài (Q36, so sánh Q13 — structured state object chỉ dùng
   khi tracking 1 giá trị MUTABLE bị ghi đè, không phải để recall lịch sử).
9. **Ưu tiên nguyên tắc chung hơn danh sách if-else brittle**, chỉ giữ conditional cho case an
   toàn/compliance bắt buộc (Q39).
10. **Task tool calls trong CÙNG 1 response message = chạy song song**; tách nhiều message riêng
    mới chạy tuần tự — không cần hạ tầng async ngoài (Q18).

---

## 6. Việc cần làm tiếp theo

- [ ] Đẩy sớm lịch ôn Domain 4 (Prompt Engineering & Structured Output) — hiện đang yếu nhất (31%)
- [ ] Đọc lại toàn bộ 27 entry trong [wrong-answers.md](wrong-answers.md) trước mock kế tiếp
- [ ] Không dùng lại nguyên site guided.maithienan.com để đo domain yếu/mạnh — dùng
      `mock-exams/set-NN.md` tự sinh đúng tỷ trọng 16/11/12/12/9 cho việc này
- [ ] Ghi điểm mock tiếp theo vào [mock-exam-log.md](mock-exam-log.md) để so sánh tiến bộ
