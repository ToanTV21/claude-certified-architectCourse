# Session 03: Prompt Engineering Techniques

## Lessons trong section này
- [x] Prompt engineering
- [x] Being clear and direct
- [x] Being specific
- [x] Structure with XML tags
- [x] Providing examples
- [ ] Exercise on prompting
- [ ] Quiz on prompt engineering techniques

## Key Concepts

### Prompt Engineering (overview lesson)
- **Prompt Engineering** = quá trình cải thiện prompt để có output đáng tin cậy và chất lượng cao hơn
  từ language model. Khác với **Prompt Evaluation** (session 02) — evaluation là đo lường khách quan,
  còn engineering là các *kỹ thuật* cụ thể để viết/sửa prompt nhằm cải thiện điểm số đó.
- **Cấu trúc của module này**: bắt đầu từ 1 prompt ban đầu còn kém → áp dụng từng kỹ thuật prompt
  engineering một (clear & direct → specific → XML tags → examples) → chạy lại eval pipeline sau
  mỗi bước để đo mức cải thiện → quan sát điểm số tăng dần theo thời gian.
- **Prompt Engineering Cycle** = quy trình lặp lại (cụ thể hoá "A Typical Eval Workflow" ở session 02)
  gồm 5 bước, trong đó 2 bước cuối lặp đi lặp lại tới khi hài lòng:
  1. **Set a goal** — định nghĩa rõ prompt cần đạt được điều gì
  2. **Write an initial prompt** — viết 1 bản nháp đầu tiên, đơn giản
  3. **Evaluate the prompt** — chạy eval, chấm điểm theo tiêu chí đã đặt
  4. **Apply prompt engineering techniques** — áp dụng 1 kỹ thuật cụ thể để cải thiện
  5. **Re-evaluate** — chạy lại eval, xác nhận điểm số có tăng thật hay không
  - Bước 4 và 5 lặp lại tới khi đạt kết quả mong muốn — mỗi vòng lặp phải cho thấy cải thiện
    **đo được** (measurable improvement) trong điểm eval, không chỉ "cảm giác tốt hơn".
  - Điểm mấu chốt: không áp dụng kỹ thuật rồi dừng — phải luôn re-evaluate để có bằng chứng khách
    quan rằng thay đổi thực sự có tác dụng, tránh trường hợp "tưởng tốt hơn nhưng thực ra không".
- **Ví dụ xuyên suốt module**: bài toán tạo **one-day meal plan cho vận động viên**, dựa trên input
  gồm chiều cao, cân nặng, mục tiêu thể chất, và các hạn chế ăn uống (dietary restrictions).
- **Setup kỹ thuật đi kèm**: bản eval pipeline được nâng cấp so với session 02 — dùng 1
  `PromptEvaluator` class linh hoạt hơn, hỗ trợ chạy đồng thời (concurrency, điều chỉnh
  `max_concurrent_tasks` tùy rate limit của API key).
  - `prompt_input_spec` = dict định nghĩa các input bắt buộc mà prompt cần (vd height, weight,
    goal, dietary_restrictions) — dùng để sinh test case tự động.
  - `extra_criteria` = tiêu chí đánh giá bổ sung khi dùng model-based grading (vd "phải liệt kê đủ
    3 bữa ăn", "phải tôn trọng dietary restriction").
  - `output.html` = report kết quả eval dạng HTML, hiển thị từng test case + điểm số, dễ nhìn hơn
    console output thô.
- **Kết quả kỳ vọng ban đầu**: prompt sơ khai (chỉ nói chung chung, chưa áp dụng kỹ thuật nào) cho
  điểm rất thấp — vd **2.32/10** trong ví dụ của khóa học, đặc biệt tệ hơn khi dùng model kém mạnh
  hơn (haiku so với sonnet/opus). Đây là baseline để so sánh sau khi áp dụng từng kỹ thuật.

### Being Clear and Direct
- **Being Clear and Direct** = kỹ thuật đầu tiên và cơ bản nhất trong prompt engineering: dùng ngôn
  ngữ đơn giản, trực tiếp, với **action verb** (động từ hành động: "Write", "Identify", "Generate"...)
  ngay ở **dòng đầu tiên** của prompt để nêu rõ chính xác task cần làm.
- **Tại sao dòng đầu quan trọng nhất**: dòng đầu tiên đặt nền tảng (foundation) cho toàn bộ cách model
  hiểu và tiếp cận phần còn lại của prompt. Nếu dòng đầu mơ hồ, model dễ hiểu sai ý định dù các dòng
  sau có chi tiết đến đâu.
- **Cấu trúc chuẩn**: `Action verb + mô tả task rõ ràng + yêu cầu output cụ thể`. Ví dụ:
  - "Write three paragraphs about how solar panels work"
  - "Identify three countries that use geothermal energy and for each include generation stats"
  - "Generate a one day meal plan for an athlete that meets their dietary restrictions"
- **So với baseline (Exercise 02)**: baseline chỉ liệt kê thông tin rồi nói chung chung "Help with a
  meal plan" — không có action verb rõ ràng, không nói output cần bao gồm gì. Áp dụng kỹ thuật này
  nghĩa là đổi thành: "**Generate** a one-day meal plan for an athlete based on the information below,
  ensuring it meets their dietary restrictions."
- **Kết quả trong khóa học**: chỉ riêng kỹ thuật này đã giúp điểm eval tăng từ **2.32 → 3.92** — cải
  thiện đáng kể dù chỉ sửa 1 câu đầu tiên, cho thấy tầm quan trọng của rõ ràng + trực tiếp.

### Being Specific
- **Being Specific** = kỹ thuật bổ sung **guideline** (hướng dẫn cụ thể) hoặc **step** (các bước) vào
  prompt để định hướng output theo đúng ý muốn, thay vì để model tự suy đoán.
- Có **2 loại guideline**, thường dùng kết hợp:
  - **Type A — Attributes (thuộc tính)**: liệt kê các đặc điểm/thuộc tính mong muốn của output (độ
    dài, cấu trúc, format...). Vd: "Mỗi bữa ăn phải có tên món, danh sách nguyên liệu, và lượng calo
    ước tính. Trình bày dưới dạng danh sách có 3 bữa: sáng, trưa, tối."
  - **Type B — Steps (các bước)**: đưa ra các bước cụ thể để model *suy luận* theo, giúp model cân
    nhắc góc nhìn/khía cạnh mà nó có thể bỏ sót nếu không được hướng dẫn. Vd: "Trước tiên tính nhu cầu
    calo hàng ngày dựa trên chiều cao/cân nặng/mục tiêu, sau đó phân bổ calo cho 3 bữa, cuối cùng chọn
    món ăn phù hợp với dietary restrictions."
- **Khi nào dùng loại nào**:
  - Type A (attributes) → khuyến nghị dùng cho **hầu hết mọi prompt**, vì luôn cần kiểm soát hình thức
    output.
  - Type B (steps) → chỉ cần cho **bài toán phức tạp**, khi muốn model xem xét nhiều góc độ hơn bình
    thường nó sẽ tự làm (vd tính toán dinh dưỡng nhiều bước như trên).
- **Kết quả trong khóa học**: sau khi thêm guideline (kết hợp cả Type A và Type B) vào prompt đã "clear
  and direct" từ bước trước, điểm eval nhảy từ **3.92 → 7.86** — mức cải thiện lớn nhất trong 2 kỹ
  thuật đã học, cho thấy "cụ thể hóa" tác động mạnh hơn cả việc chỉ "rõ ràng".

### Structure with XML Tags
- **Structure with XML Tags** = kỹ thuật dùng cặp thẻ XML (vd `<athlete_information>...
  </athlete_information>`) để bao bọc từng phần nội dung được **interpolate** (chèn) vào prompt,
  thay vì dán nội dung thô lẫn với phần hướng dẫn.
- **Vấn đề khi không dùng tag**: khi prompt càng dài, càng có nhiều phần nội dung khác nhau được chèn
  vào (dữ liệu athlete, guideline, ví dụ...), model dễ nhầm lẫn ranh giới giữa "đây là instruction" và
  "đây là data cần xử lý" — nhất là khi nội dung chèn vào cũng chứa văn bản tự nhiên giống câu lệnh.
- **Cách áp dụng**: bọc mỗi khối nội dung interpolate trong 1 cặp tag có tên **mô tả cụ thể**, không
  dùng tên chung chung. Vd `<athlete_information>` tốt hơn `<data>`, `<my_code>`/`<docs>` tốt hơn gộp
  chung code và tài liệu vào 1 khối văn bản.
- **Áp dụng vào ví dụ meal plan**: thay vì viết thẳng "Height: {height}, Weight: {weight}..." xen giữa
  câu hướng dẫn, bọc toàn bộ input athlete trong `<athlete_information>` để model phân biệt rõ đâu là
  dữ liệu đầu vào, đâu là chỉ dẫn xử lý dữ liệu đó.
- **Nguyên tắc dùng tag**: nên bọc tag ngay cả khi nội dung chèn vào **ngắn** — vì mục đích chính là
  làm rõ ranh giới "đây là input bên ngoài cần cân nhắc", không chỉ để xử lý nội dung dài.
- **Lợi ích**: giúp cấu trúc prompt rõ ràng hơn với model, giảm nhầm lẫn ranh giới nội dung, cải thiện
  chất lượng output ngay cả với những khối nội dung nhỏ.

### Providing Examples
- **Providing Examples (One-shot / Multi-shot prompting)** = kỹ thuật đưa **ví dụ mẫu** (input + output
  lý tưởng) vào prompt để định hướng hành vi model. **One-shot** = 1 ví dụ, **Multi-shot** = nhiều ví dụ.
- **Cách triển khai**: bọc mỗi ví dụ trong cặp XML tag riêng (vd `<example>`), bên trong có input mẫu
  và output mẫu, tách biệt rõ với phần prompt chính (instructions/guidelines) — luôn đặt ví dụ **sau**
  phần instruction/guideline chính, không đặt trước.
- **Khi nào dùng kỹ thuật này**:
  - Xử lý **corner case** (trường hợp đặc biệt) — vd cần chú ý sarcasm, edge case khó diễn tả bằng lời.
  - Định dạng output **phức tạp** — vd cấu trúc JSON cụ thể, format đặc thù khó mô tả đầy đủ bằng text.
  - Làm rõ **chất lượng/phong cách** output mong muốn khi lời văn không đủ diễn đạt.
  - Áp dụng cho bài toán meal plan: đưa 1 ví dụ athlete mẫu + meal plan mẫu đúng chuẩn Type A/B đã học,
    giúp model "thấy" trước hình mẫu output lý tưởng thay vì chỉ đọc mô tả bằng lời.
- **Best practices**:
  - Thêm ngữ cảnh cho corner case ngay trong ví dụ (vd "chú ý đặc biệt tới...").
  - Kèm **lý do (reasoning)** giải thích tại sao output trong ví dụ là lý tưởng — không chỉ đưa input/
    output trần mà không giải thích.
  - Ưu tiên dùng chính những output **đạt điểm cao nhất** từ các lần eval trước làm ví dụ mẫu.
- **Kết quả kỳ vọng**: kết hợp ví dụ + giải thích tại sao ví dụ đó tốt sẽ củng cố thêm các đặc điểm
  output mong muốn — thường là bước cải thiện cuối cùng trong chuỗi 4 kỹ thuật của module (Clear &
  Direct → Specific → XML Tags → Examples), đưa điểm eval lên mức cao nhất trong toàn bộ module.

## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
| `prompt_input_spec` | dict | — | Định nghĩa input fields cần thiết cho prompt template, dùng để auto-generate dataset |
| `extra_criteria` | list/str | — | Tiêu chí bổ sung truyền vào model-based grader ngoài tiêu chí mặc định |
| `max_concurrent_tasks` | int | tuỳ impl | Giới hạn số request chạy song song trong eval pipeline, cần chỉnh theo rate limit |

## Gotchas
- [ ] Đừng nhầm **Prompt Evaluation** (đo lường, session 02) với **Prompt Engineering** (kỹ thuật cải
  thiện, session 03) — hai khái niệm bổ trợ nhau: engineering cần eval để biết đã cải thiện hay chưa.
- [ ] Điểm số ban đầu thấp (vd 2.32) là **kỳ vọng bình thường** với prompt sơ khai — không phải dấu
  hiệu model bị lỗi. Mục tiêu của module là chứng minh từng kỹ thuật giúp tăng điểm dần dần.
- [ ] Model yếu hơn (Haiku) sẽ cho điểm thấp hơn với cùng 1 prompt so với model mạnh hơn (Sonnet/Opus)
  — cần cân nhắc chọn model phù hợp khi đánh giá "prompt đã đủ tốt chưa".
- [ ] Dòng đầu tiên (first line) của prompt quan trọng hơn phần còn lại — luôn bắt đầu bằng action verb
  rõ ràng thay vì mô tả bối cảnh lan man trước.
- [ ] Type B (steps) không phải lúc nào cũng cần — dùng thừa cho task đơn giản có thể khiến prompt dài
  dòng không cần thiết mà không cải thiện điểm số tương xứng. Chỉ dùng khi task thực sự phức tạp.
- [ ] Tên tag XML phải **mô tả cụ thể** (vd `<athlete_information>`), không dùng tên chung chung như
  `<data>` — tên mơ hồ làm giảm tác dụng làm rõ ranh giới nội dung của kỹ thuật này.
- [ ] Ví dụ (examples) luôn đặt **sau** phần instruction/guideline chính trong prompt — đặt trước dễ
  khiến model coi ví dụ là phần cần xử lý thay vì là hình mẫu tham khảo.

## CCA-F Exam Tips
- Phân biệt rõ **Prompt Evaluation** (đo/objective scoring) vs **Prompt Engineering** (kỹ thuật sửa
  prompt) — đề thi có thể hỏi thuật ngữ nào ứng với hành động nào.
- Quy trình chuẩn của module: viết prompt → chạy eval → áp 1 kỹ thuật → chạy lại eval → so sánh điểm
  — đây chính là 1 vòng lặp cụ thể hoá "A Typical Eval Workflow" đã học ở session 02.
- Thứ tự 4 kỹ thuật prompt engineering chuẩn của module: **Clear & Direct → Specific → XML Tags →
  Examples**. Đề thi có thể hỏi thứ tự áp dụng hoặc tác dụng riêng của từng kỹ thuật.
- XML tags dùng để **tổ chức cấu trúc** prompt (phân biệt input/instruction), khác với Examples dùng để
  **định hướng hành vi** model qua ví dụ cụ thể — hai kỹ thuật bổ trợ nhau, không thay thế nhau.

## Code Snippets
```python
# Ví dụ cấu trúc prompt_input_spec cho bài toán meal plan (session 03 - overview)
prompt_input_spec = {
    "height": "chiều cao vận động viên (cm)",
    "weight": "cân nặng vận động viên (kg)",
    "goal": "mục tiêu thể chất (vd tăng cơ, giảm mỡ, duy trì hiệu suất)",
    "dietary_restrictions": "hạn chế ăn uống (vd vegetarian, không gluten)",
}
```

## Questions / Unclear Points
- ?
