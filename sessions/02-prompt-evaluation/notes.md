# Session 02: Prompt Evaluation

## Lessons trong section này
- [x] Prompt evaluation
- [x] A typical eval workflow
- [ ] Generating test datasets
- [ ] Running the eval
- [ ] Model based grading
- [ ] Code based grading
- [ ] Exercise on prompt evals
- [ ] Quiz on prompt evaluation

## Key Concepts

### Prompt Engineering vs Prompt Evaluation — 2 khái niệm khác nhau, bổ trợ nhau
Viết được 1 prompt tốt chỉ mới là bước khởi đầu. Để xây AI application đáng tin cậy, cần hiểu rõ 2 khái niệm:

- **Prompt engineering** — bộ kỹ thuật để *viết* prompt tốt hơn: **multishot prompting** (đưa nhiều ví dụ mẫu), cấu trúc prompt bằng **XML tags**, và nhiều best practice khác (xem chi tiết ở [Session 03](../03-prompt-engineering-techniques/notes.md)). Giúp Claude hiểu chính xác mình đang yêu cầu gì và nên phản hồi theo cách nào.
- **Prompt evaluation** — không tập trung vào *cách viết*, mà là *đo lường* mức độ hiệu quả của prompt qua automated testing:
  - Test output so với đáp án kỳ vọng (expected answers)
  - So sánh nhiều version của cùng 1 prompt để chọn bản tốt hơn
  - Review output để phát hiện lỗi

→ Prompt engineering giúp viết prompt tốt hơn; prompt evaluation giúp *chứng minh* prompt đó tốt tới mức nào, bằng con số khách quan chứ không phải cảm tính.

### 3 lựa chọn sau khi viết xong 1 prompt
Sau khi soạn xong 1 prompt, thường có 3 hướng đi tiếp:

| Option | Cách làm | Rủi ro |
|--------|----------|--------|
| **1** | Test 1 lần, thấy "ổn" là chốt luôn | Rủi ro cao nhất — dễ vỡ khi lên production, gặp input người dùng thật không lường trước |
| **2** | Test vài lần, chỉnh sửa cho qua 1-2 edge case đã thấy | Đỡ hơn option 1, nhưng user thực tế vẫn tạo ra input bất ngờ hơn nhiều so với những gì mình đã thử |
| **3** | Chạy prompt qua **evaluation pipeline** để chấm điểm, rồi iterate dựa trên metric khách quan | Tốn công + chi phí hơn, nhưng cho độ tin cậy cao hơn hẳn |

**Vì sao hầu hết engineer (kể cả người có kinh nghiệm) rơi vào bẫy Option 1/2:** viết prompt cho 1 application nghiêm túc mà test chưa đủ kỹ là chuyện rất tự nhiên — con người có xu hướng **đánh giá thấp** số lượng edge case mà user thật sẽ gặp phải. Khi prompt lên production, user sẽ tương tác theo những cách mình chưa từng nghĩ tới; 1 prompt "có vẻ ổn" khi test giới hạn có thể sụp đổ ngay khi gặp đủ loại input đa dạng ngoài đời thực.

### Evaluation-first approach — vì sao nên đầu tư vào Option 3
Chạy prompt qua eval pipeline cho ra metric khách quan trên tập test case rộng hơn, giúp:
- Phát hiện điểm yếu **trước khi** nó trở thành sự cố trên production
- So sánh các version prompt khác nhau một cách khách quan (không chỉ dựa cảm giác "câu này đọc mượt hơn")
- Iterate với sự tự tin, dựa trên cải thiện đo lường được (measurable improvement)
- Xây AI application đáng tin cậy hơn

Cách tiếp cận này đòi hỏi đầu tư nhiều hơn ban đầu (thời gian + testing infrastructure), nhưng đổi lại độ tin cậy/robustness của sản phẩm cuối cùng. Mục tiêu là **bắt lỗi trong lúc phát triển**, thay vì để user là người phát hiện ra lỗi trước.

### A typical eval workflow — quy trình eval điển hình
Có nhiều cách lắp ráp workflow eval (tool mã nguồn mở, tool trả phí...), nhưng nắm được quy trình cốt lõi sẽ giúp bắt đầu nhỏ rồi scale dần lên. Một pipeline eval cơ bản gồm 5 bước, lặp lại theo vòng tròn:

**Bước 1 — Draft a Prompt (viết prompt cần đánh giá)**
Bắt đầu bằng 1 prompt baseline đơn giản, ví dụ:
```python
prompt = f"""
Please answer the user's question:

{question}
"""
```
Đây là baseline dùng để test và cải thiện dần.

**Bước 2 — Create an Eval Dataset (tạo tập dữ liệu test)**
Dataset gồm các input mẫu đại diện cho loại câu hỏi/request mà prompt sẽ gặp trong production. Các câu hỏi này sẽ được interpolate (chèn) vào prompt template. Ví dụ dataset gồm 3 câu hỏi:
- "What's 2+2?"
- "How do I make oatmeal?"
- "How far away is the Moon?"

Trong thực tế dataset có thể có hàng chục tới hàng nghìn record — tự viết tay hoặc nhờ Claude generate (xem [Generating test datasets](#generating-test-datasets--tạo-tập-dữ-liệu-test) bên dưới).

**Bước 3 — Feed Through Claude (chạy qua Claude để lấy response)**
Với mỗi câu hỏi trong dataset, ghép vào prompt template thành prompt hoàn chỉnh rồi gửi cho Claude. Ví dụ câu hỏi đầu tiên trở thành:
```
Please answer the user's question:
What's 2+2?
```
Claude trả lời "2 + 2 = 4" cho câu toán, hướng dẫn nấu oatmeal cho câu 2, và khoảng cách Mặt Trăng cho câu 3.

**Bước 4 — Feed Through a Grader (chấm điểm qua grader)**
Grader đánh giá chất lượng response bằng cách xem cả câu hỏi gốc lẫn câu trả lời của Claude, cho điểm khách quan — thường theo thang **1–10** (10 = hoàn hảo, điểm thấp = cần cải thiện). Ví dụ:
- Câu toán: 10 (trả lời hoàn hảo)
- Câu oatmeal: 4 (cần cải thiện — thiếu chi tiết)
- Câu Mặt Trăng: 9 (rất tốt)

→ Điểm trung bình: (10 + 4 + 9) ÷ 3 = **7.66**

**Bước 5 — Change Prompt and Repeat (chỉnh prompt rồi lặp lại)**
Có điểm baseline rồi, sửa prompt và chạy lại toàn bộ quy trình để xem có cải thiện không. Ví dụ thêm hướng dẫn chi tiết hơn:
```python
prompt = f"""
Please answer the user's question:

{question}

Answer the question with ample detail
"""
```
Chạy lại eval với prompt mới, điểm trung bình có thể tăng lên **8.7** — cho thấy hướng dẫn thêm vào giúp Claude trả lời tốt hơn.

**Prompt Scoring — vì sao workflow này có giá trị**
Lợi ích cốt lõi là có được **con số đo lường khách quan** cho hiệu năng prompt, từ đó:
- So sánh các version prompt khác nhau bằng số, không phải cảm tính
- Chọn version có điểm cao nhất để dùng
- Tiếp tục iterate để tìm cách tiếp cận tốt hơn nữa

→ Cách tiếp cận có hệ thống này loại bỏ việc đoán mò khỏi prompt engineering, cho mình sự tự tin rằng thay đổi đang thực sự là cải thiện, chứ không chỉ là 1 biến thể khác.

### Generating test datasets — tạo tập dữ liệu test
Test dataset là danh sách các cặp `(input, expected_output/criteria)`. Có 2 cách tạo:

- **Viết tay (manual)** — tự nghĩ ra các câu hỏi/tình huống đại diện, phù hợp khi số lượng case ít và mình hiểu rõ domain
- **Dùng chính Claude để generate** — yêu cầu Claude tạo ra N test case đa dạng (kể cả edge case: input rỗng, input dài, input mơ hồ, input sai định dạng...) theo 1 spec cho trước. Cách này giúp mở rộng độ bao phủ (coverage) nhanh hơn, phát hiện được nhiều edge case mà tự nghĩ tay dễ bỏ sót

Dataset càng đa dạng, càng phản ánh sát input thực tế mà user sẽ gửi → eval càng đáng tin cậy.

### Running the eval — chạy prompt trên toàn bộ dataset
Bước này đơn giản là 1 vòng lặp: với mỗi test case trong dataset, gọi `client.messages.create()` với prompt under test, lưu lại output để chấm điểm ở bước sau. Cần xử lý cả trường hợp API lỗi (timeout, rate limit...) cho từng case riêng lẻ, không để 1 case lỗi làm dừng cả vòng lặp.

### Code based grading — chấm điểm bằng logic code thuần
Dùng code (không cần gọi thêm LLM) để kiểm tra output có đạt tiêu chí không. Phù hợp khi tiêu chí đúng/sai rõ ràng, có thể check bằng logic:
- **Exact match** — output phải khớp y hệt chuỗi kỳ vọng
- **Substring match** — output có chứa 1 chuỗi con kỳ vọng không (vd đáp án "Tokyo" phải xuất hiện trong response)
- **Regex match** — output khớp 1 pattern cụ thể
- **Schema validation** — nếu output là JSON, parse thử bằng `json.loads()` rồi check đúng field/type theo schema mong muốn

**Ưu điểm:** nhanh, rẻ (không tốn thêm API call), kết quả deterministic (chạy lại luôn ra cùng kết quả).
**Nhược điểm:** chỉ áp dụng được khi tiêu chí đúng/sai đơn giản, rõ ràng. Không đánh giá được các tiêu chí "mềm" như văn phong, mức độ hữu ích, có đúng tone không...

### Model based grading — dùng LLM làm giám khảo (LLM-as-judge)
Khi tiêu chí đánh giá mang tính chủ quan / khó check bằng code thuần (vd: "câu trả lời có đủ lịch sự không", "bản tóm tắt có giữ đúng ý chính không", "câu trả lời có đúng tone thương hiệu không"), dùng chính Claude (hoặc 1 model khác) làm **giám khảo (grader)**:

1. Gửi cho grader: câu hỏi gốc + output cần chấm + tiêu chí chấm điểm (rubric)
2. Yêu cầu grader trả về kết quả có cấu trúc — vd `{"pass": true/false, "score": 1-5, "reason": "..."}`
3. Dùng kỹ thuật **structured output** đã học ở [Session 01](../01-accessing-claude-api/notes.md) (assistant message prefilling + `stop_sequences`) để đảm bảo grader luôn trả JSON sạch, parse được ngay bằng `json.loads()`

**Ưu điểm:** đánh giá được cả tiêu chí "mềm", linh hoạt hơn code-based nhiều.
**Nhược điểm:** tốn thêm 1 API call/case (chậm hơn, tốn chi phí hơn), và bản thân grader cũng có thể sai/không nhất quán 100% giữa các lần chạy (nên có thể cần chấm nhiều lần rồi lấy majority vote với case quan trọng).

### Chọn code-based hay model-based?
| Tiêu chí | Code-based | Model-based |
|----------|-----------|--------------|
| Đáp án rõ ràng, đúng/sai khách quan (vd số, tên riêng, format JSON) | ✅ Ưu tiên | Không cần thiết |
| Tiêu chí chủ quan (tone, độ hữu ích, mức độ tự nhiên) | ❌ Không làm được | ✅ Ưu tiên |
| Cần tốc độ nhanh, chi phí thấp, chạy dataset lớn thường xuyên (CI) | ✅ Ưu tiên | Cân nhắc chi phí |
| Cần độ chính xác cao nhất có thể | Kết hợp cả 2 | Kết hợp cả 2 |

Trong thực tế, 1 eval pipeline tốt thường **kết hợp cả 2** — dùng code-based cho các check nhanh/rõ ràng, và model-based cho các tiêu chí cần đánh giá chất lượng ngữ nghĩa.

## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
| `TEST_CASES` | list[tuple] | — | tập test dataset, mỗi phần tử là `(input, expected/criteria)` |
| `client.messages.create()` | — | — | dùng để chạy prompt under test VÀ để gọi grader (model-based) |
| `stop_sequences` | list[str] | None | dùng trong grader prompt để ép output JSON sạch (kỹ thuật prefill từ Session 01) |
| `json.loads()` | — | — | parse output JSON của cả prompt under test lẫn grader response |

## Gotchas
- [ ] Đừng chốt prompt chỉ sau 1-2 lần test thủ công (Option 1/2) — user thực tế luôn tạo input bất ngờ hơn mình nghĩ
- [ ] Code-based grading chỉ dùng được khi tiêu chí đúng/sai rõ ràng — đừng cố ép logic code check tiêu chí chủ quan (tone, style)
- [ ] Model-based grading tốn thêm API call cho mỗi test case → cân nhắc chi phí khi dataset lớn hoặc chạy thường xuyên (CI)
- [ ] Grader (model-based) cũng có thể không nhất quán giữa các lần chạy — cần structured output (prefill + stop_sequences) để parse kết quả ổn định, tránh grader trả JSON kèm giải thích thừa
- [ ] 1 test case lỗi API không nên làm dừng cả vòng lặp eval — bắt exception riêng cho từng case

## Code Snippets

### Code-based grading — check bằng logic thuần
```python
def code_based_grade(output: str, expected_substring: str) -> bool:
    # So sánh không phân biệt hoa/thường
    return expected_substring.lower() in output.lower()
```

### Model-based grading — dùng Claude làm giám khảo, ép output JSON sạch
```python
import json

GRADER_MODEL = "claude-haiku-4-5"  # grader dùng model rẻ vẫn đủ chấm điểm tốt

def model_based_grade(question: str, output: str, criteria: str) -> dict:
    grading_prompt = f"""
    Question: {question}
    Response to grade: {output}
    Grading criteria: {criteria}

    Grade the response above. Return ONLY a JSON object with fields:
    "pass" (true/false) and "reason" (short explanation).
    """

    messages = [
        {"role": "user", "content": grading_prompt},
        {"role": "assistant", "content": "```json"},  # prefill: ép Claude viết thẳng JSON
    ]

    response = client.messages.create(
        model=GRADER_MODEL,
        max_tokens=200,
        messages=messages,
        stop_sequences=["```"],  # dừng ngay khi Claude định đóng code block
    )

    return json.loads(response.content[0].text.strip())
```

## Questions / Unclear Points
- ?
