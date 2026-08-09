# Session 03: Prompt Engineering Techniques

## Lessons trong section này
- [x] Prompt engineering
- [ ] Being clear and direct
- [ ] Being specific
- [ ] Structure with XML tags
- [ ] Providing examples
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

## CCA-F Exam Tips
- Phân biệt rõ **Prompt Evaluation** (đo/objective scoring) vs **Prompt Engineering** (kỹ thuật sửa
  prompt) — đề thi có thể hỏi thuật ngữ nào ứng với hành động nào.
- Quy trình chuẩn của module: viết prompt → chạy eval → áp 1 kỹ thuật → chạy lại eval → so sánh điểm
  — đây chính là 1 vòng lặp cụ thể hoá "A Typical Eval Workflow" đã học ở session 02.

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
