# Báo cáo đánh giá lại — guided.maithienan.com CCA-F Pre-test

> **Nguồn:** https://guided.maithienan.com/certifications/ccar-f
> **Ngày làm bài:** 2026-08-15 (PRE-TEST — baseline trước khi bắt đầu 4-tuần study-plan)
> **Báo cáo tạo lúc:** 2026-08-15 17:34
> **Mục đích:** đối chiếu lại điểm + key đáp án của site bằng hiểu biết về guidance chính thức
> của Anthropic (Building Effective Agents, Claude Code docs, MCP spec, tool-use guide), không
> chỉ tin kết quả site tự chấm — site này là **nguồn cộng đồng, không phải đề chính thức**.
> File này gộp TOÀN BỘ nội dung (tổng quan + chi tiết đầy đủ 27 câu sai) — là bản lưu duy nhất
> cho lần thi thử này, không còn tách rời trong wrong-answers.md nữa (xem ghi chú cuối file).

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
nhãn site) — kết quả sau khi gắn lại, dùng cho toàn bộ phần còn lại của báo cáo này:

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

## 5. Bài học nổi bật (rút gọn — xem chi tiết đầy đủ ở mục 6)

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

## 6. Chi tiết đầy đủ 27 câu sai

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q1 `[D4]`
**Câu hỏi:** System prompt tuân thủ tốt turn 1–15, trôi dần đến turn 25–30 dù hội thoại mới 30K/200K token (chưa chạm context limit).
**Đáp án tôi chọn:** Implement post-response validation that regenerates each response until it conforms to the specified guidelines.
**Đáp án đúng:** Chèn user-message nhắc lại guideline quan trọng tại các breakpoint tự nhiên, đặc biệt trước request phức tạp.
**Vì sao sai / bài học rút ra:** Regenerate-until-conform tốn latency/cost gấp nhiều lần mỗi turn và không sửa nguyên nhân gốc. Meta-pattern #16: trôi hướng dẫn qua nhiều lượt hội thoại → sửa bằng chèn lại lời nhắc định kỳ, không phải bắt đầu lại hay validate-regenerate tốn kém.
**Link liên quan:** references.md PHẦN III #16

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q2 `[D2]`
**Câu hỏi:** 1 tool refund/cancel/reship dùng chung `order_id` nhưng khác tham số bắt buộc — agent hay thiếu/thừa tham số.
**Đáp án tôi chọn:** Keep one unified tool with all parameters marked optional, but add few-shot examples showing correct combinations.
**Đáp án đúng:** Tách thành 3 tool riêng, mỗi tool chỉ định nghĩa đúng tham số của operation đó.
**Vì sao sai / bài học rút ra:** Few-shot chỉ giảm chứ không loại bỏ lỗi khi cấu trúc schema vẫn mơ hồ (tất cả optional). Sửa tại schema (ranh giới tool rõ ràng) đáng tin hơn dặn dò qua prompt — mở rộng của meta-pattern #2 (sửa thiết kế tool trước, không vá bằng few-shot).
**Link liên quan:** references.md PHẦN III #2

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q3 `[D3]`
**Câu hỏi:** 55% test do Claude sinh ra là low-value (trivial assertion, trùng coverage, sai fixture convention của team).
**Đáp án tôi chọn:** Add post-generation coverage analysis that automatically filters out any generated test that doesn't increase line coverage.
**Đáp án đúng:** Ghi rõ testing standard, fixture convention, ví dụ phân biệt test có giá trị vs trivial vào CLAUDE.md.
**Vì sao sai / bài học rút ra:** Đề hỏi "reduce rate... being generated in the first place" — tức phải sửa ở nguồn (Claude thiếu context về tiêu chuẩn team), lọc hậu kỳ theo coverage không giải quyết gốc và có thể loại nhầm test tốt không tăng coverage. Gần meta-pattern #14 (sửa tại nguồn, không xử lý hậu kỳ).
**Link liên quan:** references.md PHẦN III #14

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q8 `[D3]`
**Câu hỏi:** Tìm hết caller của 1 hàm trước khi xoá, hàm bị wrapper module đổi tên khi export (calculateTax → computeOrderTax).
**Đáp án tôi chọn:** Use Grep to find all files that import from the library or wrapper modules, then read each file to check usage.
**Đáp án đúng:** Đọc library + wrapper modules để liệt kê hết các tên (alias) mà hàm được export ra, rồi Grep từng tên đó trên toàn repo.
**Vì sao sai / bài học rút ra:** Đọc từng file import thủ công không scale và dễ bỏ sót ở codebase lớn; chỉ Grep tên gốc bỏ sót hết các alias. Bài học: khi 1 symbol có nhiều tên do re-export, phải liệt kê hết tên trước rồi mới search — không có sẵn trong 18 meta-pattern, ghi nhận thêm.
**Link liên quan:** (insight mới — chưa có trong references.md PHẦN III)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q10 `[D2]`
**Câu hỏi:** MCP tool `check_availability`: (1) thiếu param bắt buộc, (2) API trả 404 user không tồn tại, (3) API trả 503 tạm ngưng.
**Đáp án tôi chọn:** Report all three as JSON-RPC protocol errors.
**Đáp án đúng:** Lỗi (1) thiếu param bắt buộc → JSON-RPC protocol error (invalid params); lỗi (2) và (3) → tool result với `isError: true`.
**Vì sao sai / bài học rút ra:** Protocol error dành cho lỗi ở tầng gọi (schema/params sai) — agent không sửa được nội dung, chỉ có thể sửa cách gọi. Lỗi business/execution (user không tồn tại, service down) phải trả trong content với `isError:true` để agent còn ngữ cảnh mà quyết định retry hay báo user. Gần meta-pattern #5 (lỗi cần trả context có cấu trúc).
**Link liên quan:** references.md PHẦN III #5

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q12 `[D4]`
**Câu hỏi:** Schema review có `pros`/`cons` (array) + `overall_sentiment` (enum). Review ngắn ("Great product!") bị bịa pros/cons; review mỉa mai bị gán sentiment tùy tiện vì thiếu lựa chọn "ambiguous".
**Đáp án tôi chọn:** Make pros and cons optional fields, and add "neutral" and "unclear" to the sentiment enum.
**Đáp án đúng:** Cho phép mảng rỗng (empty array) là output hợp lệ cho pros/cons, và chỉ thêm "unclear" vào enum sentiment.
**Vì sao sai / bài học rút ra:** Optional (có thể bỏ hẳn field) khác empty-array-hợp-lệ (field luôn có, chỉ có thể rỗng) — cách sau giữ schema nhất quán cho downstream mà vẫn tránh bịa dữ liệu. Thêm "neutral" là thừa vì bài toán là "không xác định được" (ambiguous/sarcasm), không phải "trung tính thật sự" — 2 khái niệm khác nhau, chỉ "unclear" mới đúng nguyên nhân.
**Link liên quan:** (insight mới — null/empty handling cho structured extraction)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q16 `[D5]`
**Câu hỏi:** Khách bực bội "muốn nói chuyện với người thật", nhưng return đã được xác nhận đủ điều kiện xử lý ngay.
**Đáp án tôi chọn:** Call escalate_to_human immediately to honor the customer's request.
**Đáp án đúng:** Ghi nhận cảm xúc, thông báo có thể giải quyết ngay, rồi mời khách chọn xử lý luôn hoặc escalate.
**Vì sao sai / bài học rút ra:** Escalate ngay theo cảm xúc khách trong khi việc HOÀN TOÀN giải quyết được ngay chỉ làm khách chờ lâu hơn — phản tác dụng first-contact-resolution. Đúng nguyên tắc meta-pattern #3: escalation phải dựa trên tiêu chí tường minh (có giải quyết được không), không dựa cảm xúc/tín hiệu ngầm.
**Link liên quan:** references.md PHẦN III #3

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q17 `[D4]`
**Câu hỏi:** Invoice extraction: 18% case tổng line item không khớp grand total (do OCR lỗi hoặc model trích sai).
**Đáp án tôi chọn:** Implement post-processing logic that automatically adjusts line item amounts proportionally when sums don't match.
**Đáp án đúng:** Thêm field `calculated_total` (model tự cộng line items) song song `stated_total`; khi 2 giá trị lệch nhau thì flag cho human review.
**Vì sao sai / bài học rút ra:** Tự động "điều chỉnh tỷ lệ" số liệu tài chính là silently fabricate dữ liệu kế toán — cực kỳ rủi ro khi nguyên nhân có thể là lỗi OCR nguồn, không phải lỗi cộng. Biến sự khác biệt thành 1 field tường minh để downstream tự quyết định mới an toàn.
**Link liên quan:** (insight mới, họ hàng với meta-pattern #1 — không tự "sửa" số liệu quan trọng bằng code ngầm)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q18 `[D1]`
**Câu hỏi:** Coordinator gọi web-search subagent rồi ĐỢI xong mới gọi document-analysis subagent, dù 2 việc độc lập nhau.
**Đáp án tôi chọn:** Create an async orchestration layer outside the agent that spawns parallel threads, each running a separate coordinator.
**Đáp án đúng:** Để coordinator phát ra CẢ HAI lời gọi Task tool trong CÙNG 1 response message.
**Vì sao sai / bài học rút ra:** Không cần hạ tầng async ngoài — cơ chế Claude Code/Agent SDK vốn đã chạy song song mọi tool_use block nằm trong CÙNG 1 message; tách ra nhiều message riêng mới là nguyên nhân chạy tuần tự. Đây là cơ chế nền tảng cần nhớ chính xác cho domain 1.
**Link liên quan:** (insight mới — cơ chế parallel tool_use trong 1 message)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q22 `[D3]`
**Câu hỏi:** LLM code review flag được hàm hoàn toàn thiếu test, nhưng bỏ sót nhánh điều kiện/error-path thiếu test bên trong hàm đã có test.
**Đáp án tôi chọn:** Implement a multi-pass pipeline: 1 LLM call tách hết conditional branch, 1 call khác đối chiếu với test assertion.
**Đáp án đúng:** Thêm few-shot: code có nhánh chưa test kèm review comment chỉ đích danh test case còn thiếu.
**Vì sao sai / bài học rút ra:** Đề nói rõ "without overcomplicating the pipeline" — multi-pass pipeline chính là overengineering bị loại. Few-shot dạy hành vi cụ thể (nhận diện nhánh thiếu test) rẻ và trực tiếp hơn.
**Link liên quan:** references.md PHẦN III #16 (gần đúng — few-shot dạy hành vi cụ thể)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q25 `[D2]`
**Câu hỏi:** `log_workout` tool nhận `measurement` tự do → agent hay gán sai đơn vị (vd "reps" cho chạy bộ). 23% tool call sai combo.
**Đáp án tôi chọn:** Add explicit examples to the tool description showing valid combinations, with constraints per exercise category.
**Đáp án đúng:** Tách thành `log_cardio_workout` (duration/distance) và `log_strength_workout` (reps/sets) — 2 tool riêng.
**Vì sao sai / bài học rút ra:** Description dù chi tiết vẫn chỉ là gợi ý, không chặn được combination sai ở tầng schema. Tách tool theo category loại bỏ khả năng sai ngay từ cấu trúc — cùng nguyên tắc với Q2. Mở rộng meta-pattern #2: sửa schema/ranh giới tool trước, không vá bằng mô tả.
**Link liên quan:** references.md PHẦN III #2

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q26 `[D1]`
**Câu hỏi:** Phân phối câu hỏi cho subagent, độ phức tạp query lệch nhau và đang evolving.
**Đáp án tôi chọn:** Have the coordinator analyze each query dynamically and selectively route subagents based on complexity.
**Đáp án đúng (theo key site):** Tạo fast-track path cố định cho câu factual, bypass toàn bộ subagent.
**Vì sao sai / bài học rút ra:** ⚠️ Xem mục 4 ở trên — đáp án bạn chọn ở đây CHÍNH LÀ đáp án được site chấm ĐÚNG ở câu 15 với kịch bản gần như giống hệt. Nghi ngờ site tự mâu thuẫn/lỗi sinh đề, KHÔNG coi đây là lỗ hổng kiến thức. Bài học thật: học cả 2 pattern (routing cố định khi phân loại rẻ+chính xác cho 2 nhóm rõ ràng; coordinator quyết định động khi độ phức tạp nhiều mức/không dự đoán trước), đọc kỹ chi tiết đề thi thật để chọn đúng pattern.
**Link liên quan:** so sánh Q15 cùng bộ, references.md Ch.9-10

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q29 `[D3]`
**Câu hỏi:** Trùng Q3 — dev từ chối nhiều bộ test do Claude Code sinh vì trivial/coverage-maximizing, không phản ánh behavior thật.
**Đáp án tôi chọn:** Implement a two-phase generation: 1 Claude call thứ 2 chấm điểm chất lượng, lọc test điểm thấp.
**Đáp án đúng:** Ghi testing standard + fixture convention + ví dụ phân biệt test có giá trị vào CLAUDE.md.
**Vì sao sai / bài học rút ra:** Đề yêu cầu "without introducing high latency", 2-phase generation tốn gấp đôi API call mỗi lần sinh test — vi phạm ràng buộc latency ngay trong đề. Giống hệt bài học Q3: sửa tại nguồn (context/tiêu chuẩn) rẻ và hiệu quả hơn lọc hậu kỳ.
**Link liên quan:** references.md PHẦN III #14

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q33 `[D4]`
**Câu hỏi:** Invoice extraction: 12% fail semantic validation (line item không khớp total, vendor ID sai format) dù JSON syntax luôn đúng.
**Đáp án tôi chọn:** Implement post-processing logic that automatically corrects common errors, such as recalculating totals from line items.
**Đáp án đúng:** Khi validation fail, gửi follow-up request kèm document gốc + kết quả extract + lỗi validation, để model tự sửa.
**Vì sao sai / bài học rút ra:** Auto-correct âm thầm là fabricate dữ liệu (không biết lỗi do OCR hay do model, tự "sửa" có thể sai theo hướng khác). Retry-with-error-feedback cho model cơ hội tự sửa có căn cứ, đúng pattern retry chuẩn cho structured output.
**Link liên quan:** (insight mới — retry-with-validation-feedback, khác auto-correct im lặng)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q34 `[D4]`
**Câu hỏi:** Persona "expert contractor" tuân thủ tốt turn 1–4, generic dần từ turn 7, hội thoại chỉ 2500 token.
**Đáp án tôi chọn:** The model's attention on system prompt instructions naturally weakens as turns accumulate.
**Đáp án đúng (theo key site):** The assistant's accumulated responses are diluting the system prompt's influence.
**Vì sao sai / bài học rút ra:** ⚠️ Xem mục 4 ở trên — 2 lựa chọn diễn đạt gần như cùng ý, không có tài liệu chính thức phân biệt rạch ròi. Không cần dằn vặt nếu chọn lại vẫn sai; ghi nhận ý chính: hội thoại ngắn (2500 token) loại trừ nguyên nhân context-limit, nguyên nhân khả dĩ nhất là model tiếp tục theo pattern do chính output trước đó của nó tạo ra.
**Link liên quan:** references.md PHẦN III #16 (liên quan lỏng)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q35 `[D1]`
**Câu hỏi:** Agent điều tra API 500 lỗi ngắt quãng, codebase 200+ file, dev không biết component nào liên quan.
**Đáp án tôi chọn:** Have the agent first create a comprehensive plan mapping all code paths before beginning any exploration.
**Đáp án đúng:** Để agent tự sinh subtask điều tra dựa trên phát hiện ở mỗi bước, điều chỉnh kế hoạch khi có thông tin mới.
**Vì sao sai / bài học rút ra:** Lập plan đầy đủ trước khi đọc bất kỳ file nào là bất khả thi khi chưa biết bug nằm đâu — mỗi file đọc được thay đổi bước tiếp theo hữu ích nhất. Debug về bản chất là adaptive, không phải fixed-plan-first.
**Link liên quan:** (insight mới — debug = adaptive exploration, không lập plan cứng trước)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q36 `[D5]`
**Câu hỏi:** Khách hỏi 3 vấn đề riêng biệt qua 45 turn (refund/subscription/payment), turn 48 hỏi lại vấn đề refund cũ, gần chạm context limit.
**Đáp án tôi chọn:** Extract and persist structured issue data (order IDs, amounts, statuses) into a separate context layer.
**Đáp án đúng:** Tóm tắt các turn cũ thành narrative, chỉ giữ nguyên văn full history cho vấn đề đang active.
**Vì sao sai / bài học rút ra:** Ban đầu tưởng structured-state (giống Q13) đúng hơn, nhưng đây là 2 bài toán khác nhau: Q13 là tracking 1 state MUTABLE (giá trị mới ghi đè giá trị cũ — dùng structured state object); Q36 là RECALL nhiều chủ đề đã đóng trong quá khứ — dùng progressive summarization (giữ verbatim gần đây, tóm tắt phần cũ) mới đúng pattern. Site áp dụng nhất quán pattern này ở cả Q47, Q55.
**Link liên quan:** references.md PHẦN III #13/#14 (liên quan lỏng), so sánh với Q13

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q37 `[D3]`
**Câu hỏi:** Review PR tự động bỏ sót bug cross-file (đổi tên tham số hàm, caller ở file KHÔNG thay đổi không được review tới).
**Đáp án tôi chọn:** Run parallel review passes per changed file with direct dependents included, aggregate + dedupe via summarization call.
**Đáp án đúng:** Redesign review thành agentic task có turn limit, model tự đọc file + search codebase, follow reference để verify cross-file.
**Vì sao sai / bài học rút ra:** File caller nằm ở file KHÔNG đổi — static prompt/static dependency-graph 2-hop đều không "thấy" được nếu graph không đủ sâu hoặc reference dynamic. Cho model tools để tự search (agentic search) mới linh hoạt đủ, đúng nguyên tắc "agentic retrieval hơn static context stuffing" của Anthropic.
**Link liên quan:** (insight mới — agentic search cho cross-file review, khác #6 per-file+integration pass)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q39 `[D4]`
**Câu hỏi:** System prompt fitness coach có nhiều nhánh if-else theo từ khóa; agent không nhận ra tín hiệu ngầm (thuật ngữ kỹ thuật) khi user không khai báo rõ trình độ.
**Đáp án tôi chọn:** Implement a pre-conversation intake asking users to rate experience level, inject rating into system prompt.
**Đáp án đúng:** Thay phần lớn nhánh if-else bằng nguyên tắc chung ("match giải thích theo trình độ, theo dõi thuật ngữ user dùng"), chỉ giữ lại nhánh an toàn/y tế bắt buộc.
**Vì sao sai / bài học rút ra:** Intake form cứng nhắc, thêm ma sát UX và không tận dụng được tín hiệu ngầm mà đề hỏi (dùng thuật ngữ kỹ thuật). Nguyên tắc chung cho phép model tự suy luận theo ngữ cảnh — if-else brittle không generalize tốt cho case chưa liệt kê.
**Link liên quan:** (insight mới — general principle > brittle conditional list, trừ case an toàn bắt buộc)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q40 `[D4]`
**Câu hỏi:** Extract event metadata (date/location/organizer/attendee_count) nullable — model hay bịa số liệu hợp lý khi bài báo không nói (vd "500" người tham dự).
**Đáp án tôi chọn:** Make all schema fields required (non-nullable) with strict validation rules.
**Đáp án đúng:** Thêm chỉ dẫn prompt: trả `null` cho field nào không được nêu trực tiếp trong nguồn.
**Vì sao sai / bài học rút ra:** Bắt buộc field non-nullable ép model LUÔN phải đưa ra giá trị dù không có — làm tăng hallucination chứ không giảm. Đây là lỗi ngược hoàn toàn với mục tiêu đề bài.
**Link liên quan:** (fact cơ bản — nullable field + instruction rõ ràng để chặn hallucination)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q49 `[D5]`
**Câu hỏi:** Webhook báo đơn hàng đã ship giữa lúc user đang chat, muốn assistant tự nhiên đề cập ở response kế tiếp.
**Đáp án tôi chọn:** Immediately send an API request with the update as a synthetic user message, generating an unsolicited assistant response.
**Đáp án đúng:** Thêm shipping status hiện tại vào system prompt trước lượt gọi API kế tiếp (khi user thực sự nhắn tiếp).
**Vì sao sai / bài học rút ra:** Gửi message giả danh user để ép model trả lời ngay tạo ra 1 message KHÔNG được user yêu cầu, xen ngang tự nhiên của chat UI. Đưa fact vào system prompt để model dùng "khi cần" tại lượt kế tiếp tự nhiên hơn nhiều — quản lý context chủ động thay vì tạo turn giả.
**Link liên quan:** references.md PHẦN III #13 (liên quan — inject context trước, không tạo turn giả)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q51 `[D2]`
**Câu hỏi:** Tool cấp phát resource chỉ trả ACK đơn giản → user approve xong mới hỏi lại "tốn bao nhiêu?", "project nào?" — tức approve mà không hiểu.
**Đáp án tôi chọn:** (không xác định rõ trong dữ liệu gốc — site không hiển thị lựa chọn ✗ cho câu này)
**Đáp án đúng:** Trả structured data (cost estimate, target project, resource spec, impact summary) ngay trong tool response.
**Vì sao sai / bài học rút ra:** User không hiểu vì tool response quá nghèo thông tin, không phải vì thiếu bước xác nhận — thêm flag `user_acknowledged` hay hold 60s không tự tạo ra thông tin, chỉ trả structured data đủ chi tiết mới giải quyết đúng nguyên nhân.
**Link liên quan:** (insight mới — tool response phải mang đủ thông tin để user "confirm" có ý nghĩa)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q52 `[D4]`
**Câu hỏi:** Trùng chủ đề Q11 nhưng thêm bẫy: `extract_metadata` phải chạy trước `lookup_citations`/`verify_doi`.
**Đáp án tôi chọn:** Set tool_choice to {"type":"tool","name":"extract_metadata"} for EVERY API call in the pipeline.
**Đáp án đúng:** Ép `tool_choice` vào `extract_metadata` ở lượt ĐẦU TIÊN, rồi các lượt enrichment tiếp theo xử lý bình thường (auto).
**Vì sao sai / bài học rút ra:** Ép `tool_choice` cố định cho MỌI lượt gọi sẽ chặn luôn Claude gọi `lookup_citations`/`verify_doi` ở các lượt sau (vì tool_choice buộc luôn phải gọi đúng tool được chỉ định). Forcing chỉ nên áp dụng đúng 1 lượt cần đảm bảo thứ tự, không phải toàn pipeline.
**Link liên quan:** (insight mới — phạm vi áp dụng của tool_choice là per-call, không phải global)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q53 `[D2]`
**Câu hỏi:** MCP tool tăng từ 4 lên 10, tool selection accuracy tụt còn 71% do tool chồng lấn ngữ nghĩa (`issue_credit` vs `process_refund`, `check_delivery_status` vs `lookup_order`).
**Đáp án tôi chọn:** Split the tools across two sub-agents (financial resolution vs delivery) with a coordinator routing between them.
**Đáp án đúng:** Gộp các tool chồng lấn ngữ nghĩa thành 1 tool (`resolve_compensation` với flag `include_tracking`) thay vì tách nhiều tool tương tự.
**Vì sao sai / bài học rút ra:** Tách sub-agent không loại bỏ sự chồng lấn — 2 tool tương tự vẫn tồn tại song song, chỉ chuyển vấn đề sang sub-agent tài chính. Đề hỏi rõ "structurally eliminates" — chỉ có gộp tool mới thực sự xoá overlap tại nguồn. Ngược hướng với Q2/Q25 (tách tool khi PARAMS khác nhau) nhưng cùng nguyên tắc: ranh giới tool phải map 1:1 với năng lực, không chồng lấn.
**Link liên quan:** references.md PHẦN III #2

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q55 `[D5]`
**Câu hỏi:** Sliding window (25 message pairs gần nhất) làm mất context chủ đề/preference cũ trong hội thoại dài.
**Đáp án tôi chọn:** Add a separate API call each turn to summarize messages being dropped, prepending this running summary.
**Đáp án đúng:** Thay sliding window bằng hybrid: tóm tắt phần cũ, giữ nguyên văn phần gần đây.
**Vì sao sai / bài học rút ra:** ⚠️ 2 lựa chọn khá giống nhau (cùng là dạng progressive summarization); khác biệt chính có thể là gọi API tóm tắt MỖI TURN tốn kém/dư thừa so với tóm tắt theo ngưỡng/định kỳ. Câu hỏi chất lượng thấp, không cần quá lo nếu chọn lại vẫn phân vân — nắm ý chính "hybrid: cũ tóm tắt, gần đây verbatim" là đủ.
**Link liên quan:** references.md PHẦN III #13, so sánh Q47/Q36

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q56 `[D4]`
**Câu hỏi:** Sau 3 tuần chạy production, 23% correction là do đo lường phi chính thức ("a handful", "a splash") bị model tự quy đổi con số cụ thể hoặc bỏ trống.
**Đáp án tôi chọn:** Implement a post-processing layer that uses pattern matching to detect informal measurement phrases and auto-populate.
**Đáp án đúng:** Thêm few-shot minh hoạ xử lý đúng đo lường phi chính thức — trích nguyên văn ("a handful"), không quy đổi/không bỏ trống.
**Vì sao sai / bài học rút ra:** Pattern-matching hậu kỳ phải đoán giá trị cụ thể từ cụm mơ hồ — chính là việc model đang làm sai, chuyển vấn đề sang layer khác không giải quyết gốc. Few-shot dạy model hành vi mong muốn (giữ nguyên văn) trực tiếp và rẻ hơn.
**Link liên quan:** references.md PHẦN III #16 (gần đúng — dạy hành vi cụ thể bằng few-shot)

### [2026-08-15] Nguồn: guided.maithienan.com pre-test — Q60 `[D2]`
**Câu hỏi:** Agent nối 3 MCP server (issue tracker/wiki/DB), câu hỏi liên hệ thống ("bảng DB nào bị ảnh hưởng bởi refactor PROJ-1234?") tốn 8-10 tool call dò dẫm, cạn context trước khi xong.
**Đáp án tôi chọn:** Consolidate all three servers into a unified MCP server with cross-referencing capabilities.
**Đáp án đúng:** Expose content catalog của mỗi server qua MCP **Resources** (issue summary, doc hierarchy, DB schema) — không phải qua Tools.
**Vì sao sai / bài học rút ra:** Gộp 3 server thành 1 phá vỡ thiết kế composable của MCP và không giải quyết đúng vấn đề (thiếu visibility, không phải thiếu server). MCP có primitive **Resources** riêng biệt với **Tools** — dành đúng cho nội dung browsable/application-controlled, đọc được không cần tool-call round-trip. Đây là kiến thức MCP-spec quan trọng cho domain 2, cần nhớ Resources vs Tools là 2 khái niệm khác nhau.
**Link liên quan:** references.md Ch.4/13 (MCP), bổ sung khái niệm Resources nếu chưa có

---

## 7. Việc cần làm tiếp theo

- [ ] Đẩy sớm lịch ôn Domain 4 (Prompt Engineering & Structured Output) — hiện đang yếu nhất (31%)
- [ ] Đọc lại toàn bộ mục 6 (27 câu sai) trước mock kế tiếp
- [ ] Không dùng lại nguyên site guided.maithienan.com để đo domain yếu/mạnh — dùng
      `mock-exams/set-NN.md` tự sinh đúng tỷ trọng 16/11/12/12/9 cho việc này
- [ ] Ghi điểm mock tiếp theo vào [mock-exam-log.md](mock-exam-log.md) để so sánh tiến bộ

---

> **Ghi chú:** nội dung pre-test này trước đó nằm chung trong `wrong-answers.md`, nay đã chuyển
> toàn bộ về file riêng này để dễ tracking theo từng lần thi thử. `wrong-answers.md` chỉ còn giữ
> 1 dòng trỏ tới file này.
