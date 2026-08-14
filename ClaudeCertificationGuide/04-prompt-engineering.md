# Domain 4: Prompt Engineering & Structured Output (20%)

> Nguồn: https://claudecertificationguide.com/learn/4-prompt-engineering/

---

## 4.1 System Prompts với Explicit Criteria

### Vấn đề chính
"Sai lầm lớn nhất trong prompt engineering production là dựa vào instruction mơ hồ." Các cụm từ như "Be conservative", "Only report high-confidence findings", "Use your best judgement" bị coi là lỗi nền tảng vì không cung cấp ranh giới quyết định khả thi cho LLM.

### So sánh cách tiếp cận

**Sai**:
```
Review this code. Be conservative. Only report high-confidence findings.
```
Vì sao fail: thuật ngữ mơ hồ thiếu ý nghĩa cụ thể qua các context khác nhau.

**Đúng**:
```
Flag comments only when claimed behaviour contradicts actual code behaviour.
Report bugs and security vulnerabilities.
Skip minor style preferences and local patterns.
```
Vì sao đúng: cung cấp category cụ thể định nghĩa cái gì report, cái gì skip, trigger cụ thể.

### Vấn đề False Positive phá vỡ niềm tin
**Insight quan trọng**: "Tỷ lệ false positive cao ở 1 category phá hủy niềm tin dev vào **mọi** category." Khi 1 category review lỗi thường xuyên (vd 40% false positive về documentation mismatch), dev ngừng tin toàn bộ output category — kể cả category có 98% chính xác.

**Chiến lược khôi phục niềm tin**: giải pháp phản trực giác là tạm thời disable category có vấn đề trong khi refine prompt của nó. Điều này khôi phục niềm tin toàn hệ thống trước khi re-enable category đã cải thiện.

### Phương pháp Calibrate mức độ nghiêm trọng

**Không đủ — mô tả prose**:
```
Critical: Issues that could cause system failures or data loss
Minor: Issues that affect code readability but not functionality
```
Vấn đề: buộc model diễn giải khái niệm chủ quan.

**Đúng — ví dụ code cụ thể**:
```
Critical — Unsanitised user input in SQL query:
  query = f"SELECT * FROM users WHERE id = {user_input}"

Minor — Inconsistent variable naming:
  userName vs user_name in the same module
```
Lợi thế: loại bỏ mơ hồ; cho ra classification nhất quán qua các lần invoke.

### Vì sao Confidence-Based Filtering thất bại
Tài liệu thiết lập hierarchy quan trọng: "Explicit criteria trước, confidence-based routing sau."

**Giới hạn chính**: "Confidence tự báo cáo của LLM được calibrate kém. Model thường chắc chắn về finding sai và do dự về finding đúng."

Confidence-based filtering có tác dụng cho routing (gửi item confidence thấp cho human review) nhưng không thể thay thế explicit categorical criteria định nghĩa cái gì là finding hợp lệ.

### Exam traps
1. **Chọn cải thiện mơ hồ** — chọn "be conservative" hoặc "only report high-confidence findings" như cải thiện prompt hợp lệ. Các cụm từ này không cung cấp framework diễn giải nào cho model.
2. **Giả định confidence threshold giải quyết false positive** — confidence score tự báo cáo được calibrate kém, không bao giờ nên thay thế explicit criteria kèm ví dụ cụ thể.
3. **Giữ mọi category active trong lúc iterate** — giữ category false-positive cao active trong khi fix chúng làm hại niềm tin hệ thống. Tạm thời disable là chiến lược đúng.

### Practice scenario
Pipeline CI/CD cho thấy 40% false positive rate ở documentation mismatch, khiến dev bỏ qua mọi review category kể cả finding security chính xác. **Đáp án đúng**: tạm thời disable category documentation mismatch trong khi refine prompt với explicit criteria và ví dụ code. **Vì sao hoạt động**: khôi phục niềm tin dev vào category chính xác còn lại ngay lập tức, rồi cải thiện category có vấn đề qua refinement lặp trước khi re-enable.

### Build exercise — 5 bước
1. Baseline với instruction mơ hồ — test prompt mơ hồ với 5 code snippet chứa bug, security issue, style nitpick. Kỳ vọng: classification không nhất quán, kết quả khác nhau qua các lần chạy.
2. Viết lại với criteria phân loại rõ ràng — định nghĩa chính xác issue nào report (bug, security vulnerability) và skip (style preference, local pattern).
3. Thêm ví dụ code cụ thể — cung cấp pattern code thực tế ở mỗi mức severity thay vì mô tả prose.
4. So sánh tỷ lệ false positive — định lượng cải thiện giữa approach mơ hồ và explicit trên cùng test set.
5. Disable category false-positive cao — tạm tắt category vượt 25% false positive rate, document refinement cần thiết để re-enable.

### Key takeaways
- Explicit categorical criteria luôn vượt trội instruction mơ hồ.
- Mức độ nghiêm trọng cần ví dụ code cụ thể, không phải mô tả prose.
- Confidence-based filtering không thể thay thế explicit criteria.
- False positive cao ở 1 category phá hủy niềm tin xuyên suốt mọi category.
- Tạm thời disable category có vấn đề khôi phục niềm tin toàn hệ thống.
- Hierarchy: explicit criteria → confidence-based routing → human review.

---

## 4.2 Few-Shot Prompting

### Nguyên tắc cốt lõi
"Few-shot example là kỹ thuật hiệu quả nhất để đạt output nhất quán, format tốt từ Claude. Không phải thêm instruction. Không phải confidence threshold. Không phải điều chỉnh temperature."

### 3 trigger cụ thể cho Few-Shot Examples

**1. Formatting không nhất quán dù instruction chi tiết**: khi spec prompt kỹ nhưng output vẫn thay đổi cấu trúc (bulleted list, table, hay prose qua các lần invoke), thêm instruction không giải quyết được. Cần ví dụ thể hiện chính xác format mong muốn.

**2. Judgement call không nhất quán trên case mơ hồ**: code review tool flag variable shadowing là "critical" ở file này, "minor" ở file khác; agent chọn tool route request giống hệt tới tool khác nhau tùy cách diễn đạt. Cần ví dụ kèm reasoning thể hiện judgement đúng cho case mơ hồ.

**3. Extraction task với field rỗng/null cho data đã tồn tại**: thông tin có mặt nhưng format ngoài kỳ vọng — embed trong narrative text thay vì table có cấu trúc, chia nhỏ qua nhiều đoạn văn. Few-shot example thể hiện extraction từ cấu trúc document đa dạng giải quyết được.

### Xây dựng ví dụ hiệu quả

**Hướng dẫn định lượng**: dùng **2-4 ví dụ có mục tiêu**: ít hơn 2 không thiết lập được pattern; nhiều hơn 4 lãng phí token không tăng tương xứng. Trỏ ví dụ vào scenario mơ hồ cụ thể gây vấn đề.

**Yêu cầu chất lượng**: mỗi ví dụ phải thể hiện reasoning giải thích vì sao chọn action này thay vì alternative hợp lý khác. Điều này dạy model generalize sang pattern mới thay vì literal pattern-matching.

**Cấu trúc ví dụ**:
```
Input: "check my order #12345"
Selected tool: lookup_order
Reasoning: The user provides an order number (#12345), indicating
they want order-specific information. Even though this could be
interpreted as a general customer query, the specific order
identifier makes lookup_order the correct choice over get_customer.
```
Không có reasoning, model học association bề mặt. Có reasoning, model học nguyên tắc quyết định tổng quát.

**Chiến lược coverage**: ví dụ phải nhắm đúng scenario đang fail cụ thể — nếu extraction hoạt động trên table nhưng fail trên narrative text, ví dụ nên thể hiện extraction đúng từ narrative text.

### Hiệu ứng giảm Hallucination
Few-shot example cắt giảm hallucination trong task extraction bằng cách phơi bày model với sự đa dạng cấu trúc. Khi ví dụ thể hiện extraction đúng từ inline citation vs bibliography, narrative description vs table có cấu trúc, header vs embedded text — model học xử lý sự đa dạng cấu trúc mà không bịa data.

### Giảm False Positive
Ví dụ thể hiện cả cái cần flag lẫn cái cần bỏ qua, tách biệt pattern code chấp nhận được khỏi issue thật:
```
Code: function process(items) {
  const result = items.map(item => {
    const result = transform(item);  // shadows outer 'result'
    return result;
  });
  return result;
}
Severity: minor
Reasoning: The inner 'result' shadows the outer variable but
within a limited scope (arrow function). The code is still readable
and the shadow does not cause a bug. This is a style preference,
not a defect. Flag as minor only if style consistency is in scope.
```

### Few-Shot vs kỹ thuật khác

| Vấn đề | Kỹ thuật đúng |
|---|---|
| Output formatting không nhất quán | Few-shot example |
| JSON output malformed | Tool use với JSON schema |
| Field bịa giá trị khi thiếu | Optional/nullable schema field |
| Chọn tool sai | Description tool tốt hơn (trước tiên), rồi few-shot |
| Model bỏ sót thông tin narrative | Few-shot example thể hiện extraction narrative |
| Extraction sum mismatch với total | Validation-retry loop |

### Exam traps
1. **Thêm nhiều instruction hơn** — "Nếu instruction chi tiết đã tồn tại và output vẫn không nhất quán, thêm instruction không sửa được vấn đề." Few-shot example mới là biện pháp phù hợp.
2. **Đánh giá thấp khả năng generalize** — ví dụ có reasoning cho quyết định dạy model generalize sang pattern mới — chúng học nguyên tắc quyết định, không chỉ case cụ thể.
3. **Confidence threshold** — confidence threshold được calibrate kém, không giải quyết root cause. Few-shot example dạy trực tiếp quyết định nhất quán cho case mơ hồ.

### Key concept summary
"Few-shot example là kỹ thuật hiệu quả nhất cho consistency. Dùng 2-4 ví dụ có mục tiêu kèm reasoning cho quyết định, không chỉ cặp input-output. Deploy khi instruction đơn thuần cho kết quả không nhất quán, judgement mơ hồ, hoặc field extraction rỗng cho data đã tồn tại."

### Practice scenario
Pipeline extraction xác định đúng data research trong table có cấu trúc nhưng trả field rỗng khi cùng thông tin xuất hiện trong đoạn văn narrative, dù instruction chi tiết đã chỉ định mọi field và format bắt buộc. **Đáp án đúng**: thêm few-shot example thể hiện extraction đúng từ cả table có cấu trúc và đoạn văn narrative — trực tiếp giải quyết trigger thứ 3 (field rỗng cho data đã tồn tại ở format bất ngờ) và nhắm đúng scenario đang fail (đoạn văn narrative).

---

## 4.3 Structured Output với Tool Use

### Khái niệm cốt lõi
Lesson thiết lập "reliability hierarchy rõ ràng" cho sinh output tuân thủ schema:
1. **`tool_use` với JSON schema** — ngăn lỗi cú pháp JSON hoàn toàn
2. **Prompt-based JSON** — không đảm bảo cấu trúc gì, rủi ro output không parse được

Phân biệt quan trọng: tool use ràng buộc shape response qua JSON schema của tool, loại bỏ vấn đề như thiếu dấu ngoặc, dấu phẩy thừa, hay key không có quote. Prompt-based extraction để model tự do sinh output không parse được trong môi trường production.

### Tham số `tool_choice` — 3 mode

**Mode 1: `"auto"` (mặc định)** — model tự quyết định gọi tool hay trả text. Không đảm bảo structured output. Use case: khi model thật sự cần lựa chọn trả lời hội thoại.

**Mode 2: `"any"`** — model PHẢI gọi tool nhưng tự chọn tool nào. Đảm bảo structured output với lựa chọn tool linh hoạt. Use case: nhiều schema extraction khi loại document chưa biết (vd `extract_invoice`, `extract_receipt`, `extract_contract`).

**Mode 3: `{"type": "tool", "name": "extract_metadata"}`** — model PHẢI gọi đúng tool được chỉ định. Kiểm soát tối đa, không linh hoạt. Use case: đảm bảo bước metadata extraction chạy trước bước enrichment.

```typescript
// Force guaranteed structured output (unknown document type)
const response = await client.messages.create({
  model: "claude-sonnet-5",
  max_tokens: 4096,
  tool_choice: { type: "any" },
  tools: [extractInvoiceTool, extractReceiptTool, extractContractTool],
  messages: [{ role: "user", content: documentText }]
});

// Force specific extraction step
const response = await client.messages.create({
  model: "claude-sonnet-5",
  max_tokens: 4096,
  tool_choice: { type: "tool", name: "extract_metadata" },
  tools: [extractMetadataTool],
  messages: [{ role: "user", content: documentText }]
});
```

### `tool_use` KHÔNG ngăn được gì
Lesson nhấn mạnh đây là "chỗ đề thi hay đánh lừa". Tool use loại bỏ lỗi **cú pháp (syntax)** nhưng KHÔNG loại bỏ lỗi **ngữ nghĩa (semantic)**:
- **Sum discrepancy**: line item không cộng đúng bằng total nêu ra
- **Field placement error**: giá trị đặt sai field (vd date vào field amount vì cả 2 đều string)
- **Fabrication**: model bịa giá trị cho field bắt buộc khi source document thiếu thông tin

**Nguyên tắc chính**: "Schema đảm bảo cấu trúc. Nó không đảm bảo tính đúng đắn."

### Thiết kế Schema cho Production

**Chiến lược 1 — Optional/Nullable Fields**: "biện pháp phòng thủ chính chống fabrication." Khi document nguồn có thể thiếu thông tin nhất định, làm field đó optional hoặc nullable thay vì required. Field bắt buộc gây áp lực khiến model sinh giá trị dù không có trong source.
```json
{
  "type": "object",
  "properties": {
    "invoice_number": { "type": "string" },
    "vendor_name": { "type": "string" },
    "payment_terms": { "type": ["string", "null"] },
    "purchase_order": { "type": ["string", "null"] }
  },
  "required": ["invoice_number", "vendor_name"]
}
```

**Chiến lược 2 — Giá trị enum "unclear"**: cho case mơ hồ khi source thực sự không rõ, thêm option `"unclear"` tường minh vào enum field. Ngăn model ép classification khi bằng chứng mơ hồ.

**Chiến lược 3 — "Other" + chuỗi detail**: cho categorization mở rộng được, include giá trị enum `"other"` kèm field chuỗi freeform để capture edge case.
```json
{
  "category": {
    "type": "string",
    "enum": ["invoice", "receipt", "contract", "unclear", "other"]
  },
  "category_detail": {
    "type": ["string", "null"],
    "description": "Freeform detail when category is 'other'"
  }
}
```

**Chiến lược 4 — Format Normalisation Rules**: include instruction chuẩn hóa format trong prompt cùng schema. Schema enforce cấu trúc; prompt enforce consistency format (vd "Mọi ngày dùng ISO 8601", "Mọi số tiền dạng decimal không kèm ký hiệu tiền tệ").

### Key concept summary
"tool_use với JSON schema loại bỏ lỗi cú pháp nhưng không loại bỏ lỗi ngữ nghĩa. Làm field optional/nullable khi document nguồn có thể thiếu thông tin — ngăn model bịa giá trị. Dùng tool_choice 'any' cho structured output đảm bảo khi loại document chưa biết."

### Exam traps
1. **Đánh giá quá cao khả năng tool_use ngăn được** — niềm tin sai: tool_use với JSON schema ngăn mọi lỗi extraction. Thực tế: chỉ loại bỏ lỗi cú pháp JSON. Lỗi ngữ nghĩa (sum sai, data đặt sai chỗ, giá trị bịa) vẫn xảy ra và cần validation riêng.
2. **Nhầm lẫn mode tool_choice** — niềm tin sai: `'auto'` và `'any'` hoán đổi được. Thực tế: `'auto'` cho phép trả text, không đảm bảo structured output. `'any'` đảm bảo tool call nhưng để model chọn tool nào.
3. **Schema quá nhiều field required** — niềm tin sai: làm mọi field schema required đảm bảo tính đầy đủ data. Thực tế: field bắt buộc tạo áp lực khiến model bịa giá trị khi thông tin vắng mặt từ source. Field optional/nullable cho phép trả null trung thực, luôn tốt hơn data bịa trông có vẻ hợp lý.

### Practice scenario
Hệ thống extraction dùng tool_use với mọi field schema required báo cáo rằng model bịa ngày tháng và số tiền có vẻ hợp lý khi xử lý document thiếu thông tin này. **Đáp án đúng**: làm field optional hoặc nullable khi document nguồn có thể không chứa thông tin — ngăn áp lực bịa giá trị khi thông tin nguồn vắng mặt.

---

## 4.4 Validation, Retry & Feedback Loops

### Khái niệm cốt lõi: Retry-with-Error-Feedback
Pattern validated retry cần 3 thành phần thiết yếu:
1. **Document gốc** — cung cấp source material để xem xét lại
2. **Extraction fail** — thể hiện model đã sinh ra gì
3. **Validation error cụ thể** — xác định chính xác cái gì sai

```typescript
// Retry with error feedback
const retryMessages = [
  {
    role: "user",
    content: `Original document:\n${originalDocument}\n\n` +
      `Your extraction:\n${JSON.stringify(failedExtraction)}\n\n` +
      `Validation error: Line items sum to £450 but stated_total is £500. ` +
      `Please re-extract, ensuring all line items are captured.`
  }
];
```

**Phân biệt quan trọng**: retry ngây thơ không kèm error feedback cụ thể thường tái tạo y hệt lỗi cũ. Error messaging có mục tiêu cho phép model tập trung nỗ lực tự sửa vào vấn đề đã xác định.

### Ranh giới hiệu quả của Retry
Đây là điểm test chính trên đề thi. Retry có ranh giới áp dụng rõ ràng:

**Retry HIỆU QUẢ cho**: format mismatch (định dạng date, ký hiệu tiền tệ không nhất quán); structural output error (giá trị đặt sai field, nesting sai); giá trị đặt lệch chỗ (data tồn tại trong document nhưng extract sai vị trí); lỗi toán học (bỏ sót line item ảnh hưởng total).

**Retry KHÔNG hiệu quả cho**: thông tin thực sự vắng mặt trong source document; data cần document ngoài không được cung cấp cho model; field cần kiến thức mà model không có.

**Nguyên tắc chính**: nếu document nguồn thiếu thông tin bắt buộc, flag cho human review thay vì retry. Trả null (nếu schema cho phép) là phù hợp.

### Thiết kế Schema tự sửa lỗi

**Pattern Calculated vs Stated Totals**:
```json
{
  "line_items": [
    { "description": "Widget A", "amount": 150.00 },
    { "description": "Widget B", "amount": 300.00 }
  ],
  "calculated_total": 450.00,
  "stated_total": 500.00,
  "total_discrepancy": true
}
```
Cách này extract cả sum tính toán lẫn total nêu trong document, tự động flag discrepancy mà không cần logic bên ngoài.

**Conflict Detection Fields**: cho thông tin nguồn mâu thuẫn nhau, dùng boolean marker:
```json
{
  "field_a": "30 days payment",
  "field_b": "net 60 terms",
  "conflict_detected": true
}
```
Thay vì âm thầm chọn 1 giá trị, extract cả 2 và flag mâu thuẫn cho xử lý downstream.

**Detected Pattern Fields**: cho pipeline code review và security analysis, track construct cụ thể nào trigger mỗi finding:
```json
{
  "finding": "Potential SQL injection vulnerability",
  "severity": "critical",
  "detected_pattern": "string concatenation in SQL query",
  "file": "user_service.py",
  "line": 42
}
```
**Vòng lặp cải thiện có hệ thống**: track giá trị `detected_pattern` nào dev dismiss nhiều nhất — pattern dismiss cao chỉ ra khu vực cần refine prompt.

### Schema Syntax Errors vs Semantic Validation Errors

| Loại lỗi | Định nghĩa | Giải pháp |
|---|---|---|
| **Schema syntax error** | JSON malformed, thiếu field bắt buộc, sai kiểu dữ liệu | `tool_use` với JSON schema loại bỏ (Task 4.3) |
| **Semantic validation error** | Cấu trúc JSON đúng nhưng giá trị sai — sum lệch, field sai chỗ, ngày tháng sai thứ tự | Cần validation logic bên ngoài và retry loop |

Sự chồng lấn giữa các task là cố ý: `tool_use` giải quyết vấn đề cấu trúc, retry loop xử lý vấn đề giá trị.

### Pydantic — Validation Layer
Pydantic đóng vai trò validation layer biến "validation failed" chung chung thành error message cụ thể, actionable cho retry loop.

**2 chức năng Pydantic**: 1) Parsing — enforce cấu trúc (type, field bắt buộc, enum); 2) Validation — enforce business rule (cross-field arithmetic, thứ tự ngày tháng, custom constraint). Cả 2 loại fail đều lộ ra qua `ValidationError` duy nhất với message machine-readable, field-specific.

```python
import json
from pydantic import BaseModel, ValidationError, model_validator

class LineItem(BaseModel):
    description: str
    amount: float

class Invoice(BaseModel):
    line_items: list[LineItem]
    stated_total: float

    @model_validator(mode="after")
    def totals_must_match(self):
        calculated = round(sum(i.amount for i in self.line_items), 2)
        if abs(calculated - self.stated_total) > 0.01:
            raise ValueError(
                f"line items sum to {calculated} but stated_total is {self.stated_total}"
            )
        return self

try:
    invoice = Invoice.model_validate(tool_input)
except ValidationError as e:
    errors = "\n".join(
        f"{'.'.join(map(str, err['loc'])) or 'invoice'}: {err['msg']}" for err in e.errors()
    )
    retry_message = (
        f"Original document:\n{original_document}\n\n"
        f"Your extraction:\n{json.dumps(tool_input)}\n\n"
        f"Validation errors:\n{errors}\n\n"
        f"Please re-extract, fixing the identified errors."
    )
```
Nhánh `except` triển khai pattern retry-with-error-feedback — Pydantic cung cấp thành phần error cụ thể. Ranh giới hiệu quả retry không đổi: validator fail do thiếu thông tin nguồn vẫn cần human review, không phải retry.

### Trạng thái SDK hiện tại (July 2026)
- SDK Python `client.messages.parse(..., output_format=Invoice)` trả về instance Pydantic đã validate qua `parsed_output`.
- `strict: true` trên tool definition đảm bảo input tuân thủ schema ở phía server.
- Không cái nào loại bỏ semantic validation: platform enforce schema syntax, validator enforce business rule, retry loop tiêu thụ cái nào fail.

### Exam traps
1. **Giả định retry luôn hoạt động** — "Retry fix format mismatch, structural error, và giá trị đặt lệch chỗ" nhưng không thể tạo ra thông tin thực sự vắng mặt trong source document.
2. **Implement retry không kèm error message cụ thể** — retry ngây thơ thường tái tạo y hệt lỗi. Model cần "mô tả lỗi chính xác" để tự sửa có mục tiêu.
3. **Chỉ dựa vào schema validation** — schema validation qua `tool_use` bắt lỗi cú pháp. Lỗi ngữ nghĩa cần validation logic bổ sung và retry loop.
4. **Coi Pydantic là dư thừa sau tool_use** — schema loại bỏ lỗi cú pháp nhưng không thể diễn đạt rule cross-field như "sum phải khớp" hay "ngày phải đúng thứ tự".

### Practice scenario
Pipeline extraction validate sum line item với total nêu ra. Document A: tính toán £450 vs nêu £500. Document B: field 'department' thiếu từ source. **Đáp án đúng**: retry Document A với error discrepancy; flag Document B cho human review vì thông tin vắng mặt từ source. Đây phản ánh ranh giới hiệu quả retry: lỗi structural/toán học sửa được cần retry; thông tin vắng mặt cần can thiệp con người.

---

## 4.5 Batch Processing Strategies

### Khái niệm cốt lõi
Lesson này bao phủ Message Batches API như công cụ tối ưu cost trong Domain 4, Task 4.5.

### Ràng buộc cố định của Message Batches API
- **Giảm 50% cost** so với call đồng bộ
- **Xử lý tới 24 giờ** — thời gian trả kết quả biến động rộng
- **Không đảm bảo SLA latency** — không thể giả định hoàn thành nhanh
- **Không hỗ trợ multi-turn tool calling** trong 1 batch request
- **Field `custom_id`** để match request với response

### Quy tắc Matching nền tảng
Đây là khái niệm được test nặng nhất từ task này:

| Loại workflow | API chọn | Lý do |
|---|---|---|
| Đồng bộ (Synchronous) | Real-time call | Ai đó/cái gì đó đang chờ kết quả tích cực |
| Batch-eligible | Message Batches API | Kết quả tiêu thụ bất đồng bộ sau |

**Workflow blocking** (pre-merge check, real-time code review) cần xử lý đồng bộ vì dev không thể tiếp tục cho tới khi hoàn thành. **Workflow chịu được latency** (report overnight, audit hàng tuần, test generation ban đêm) phù hợp batch processing vì tiêu thụ kết quả sau khi xử lý xong.

### Framework tính toán SLA
Tính ngược từ deadline requirement:
```
Total SLA requirement: 30 hours
Maximum batch processing: 24 hours
Available buffer: 6 hours (for request collection, validation, delays)

Submission strategy: Submit batches every 4-6 hours
Last batch must submit: 24 hours before deadline
```
Đề thi có thể test câu hỏi scheduling yêu cầu tính ngược từ SLA deadline.

### Pattern xử lý Batch Failure — 3 bước đúng

**Bước 1: Xác định failure qua `custom_id`** — mỗi request mang định danh unique. Parse result để tìm giá trị `custom_id` failed.

**Bước 2: Resubmit chỉ failure với modification có mục tiêu** — không bao giờ resubmit toàn bộ batch. Modification có thể gồm: chunk document vượt giới hạn context, đơn giản hóa prompt extraction cho cấu trúc bất thường, thêm few-shot example theo format.

**Bước 3: Refine prompt trên sample set trước khi chạy full batch** — test với 5-10 document đại diện phủ đa dạng format và edge case trước khi submit toàn batch. Tối đa hóa first-pass success và giảm chi phí resubmission.

```typescript
// Parse batch results and identify failures
const results = await client.batches.results(batchId);
const failures = results.filter(r => r.result.type === "errored");
const failedIds = failures.map(f => f.custom_id);

// Resubmit only failures with modifications
const retryRequests = failedIds.map(id => {
  const originalDoc = documentsById[id];
  return {
    custom_id: `${id}-retry-1`,
    params: {
      model: "claude-sonnet-5",
      max_tokens: 8192,  // increased for oversized docs
      messages: [{
        role: "user",
        content: chunkIfNeeded(originalDoc)
      }]
    }
  };
});
```

### Ảnh hưởng cost của tỷ lệ First-Pass Success
- **First-pass 90%** trên 1,000 document = 100 lần retry
- **First-pass 60%** trên 1,000 document = 400 lần retry

Chênh lệch cost minh chứng vì sao refine prompt trước khi submit batch tiết kiệm đáng kể.

### Giới hạn Multi-Turn Tool Calling
Batch API tường minh cấm: định nghĩa tool với thực thi mid-request, xử lý tool result và tiếp tục trong cùng item batch, chạy agentic loop trong 1 batch request. Workflow cần tool execution trong lúc processing phải dùng synchronous API. Giới hạn này được test trực tiếp trên đề thi.

### So sánh Synchronous vs Batch
```typescript
// Synchronous — developer is waiting for this
const preMergeReview = await client.messages.create({
  model: "claude-sonnet-5",
  max_tokens: 4096,
  messages: [{ role: "user", content: prDiffContent }]
});

// Batch — results consumed tomorrow morning
const batchRequest = await client.batches.create({
  requests: technicalDebtDocuments.map((doc, i) => ({
    custom_id: `debt-report-${i}`,
    params: {
      model: "claude-sonnet-5",
      max_tokens: 4096,
      messages: [{ role: "user", content: doc }]
    }
  }))
});
```

### Quy trình tối ưu Prompt
Chiến lược batch cost-effective nhất theo trình tự này:
1. **Test sample set** — 5-10 document đại diện phủ range format và edge case
2. **Refine lặp** — cải thiện prompt extraction, thêm few-shot example, điều chỉnh schema
3. **Submit full batch** — prompt refined cho first-pass success cao hơn
4. **Xử lý failure có mục tiêu** — resubmit chỉ document fail với modification

### Exam traps
1. **Chuyển mọi workflow sang batch** — workflow blocking (pre-merge check, real-time review) không chịu được cửa sổ xử lý "tới 24 giờ". Chỉ workflow chịu latency mới nên migrate sang batch.
2. **Giả định batch result nhanh** — dù kết quả thường tới nhanh, API không đảm bảo latency SLA. Thiết kế workflow quanh 24 giờ tối đa, không phải timing tốt nhất.
3. **Batch API cho multi-turn tool calling** — API thiếu hỗ trợ multi-turn tool calling. Workflow cần tool execution giữa chừng phải dùng synchronous call.

### Practice scenario
Manager đề xuất chuyển cả pre-merge check lẫn technical debt report overnight sang Batch API để tiết kiệm cost. **Đáp án đúng (Option A)**: "Dùng batch processing chỉ cho technical debt report; giữ real-time call cho pre-merge check". Lý do: pre-merge check block dev; technical debt report tiêu thụ kết quả bất đồng bộ sáng hôm sau.

### Key takeaway
"Message Batches API cung cấp 50% cost saving với cửa sổ xử lý tới 24 giờ" nhưng đòi hỏi phân loại workflow cẩn thận. Xử lý đồng bộ vẫn bắt buộc cho operation blocking dù có chênh lệch cost.

---

## 4.6 Multi-Instance & Multi-Pass Review

### Khái niệm cốt lõi
"Khi Claude review chính output của nó, nó bắt đầu ở thế bất lợi: nó vẫn mang theo reasoning nó dùng để sinh ra output đó."

### Giới hạn Self-Review
**Vấn đề**: model review output trong cùng session giữ nguyên reasoning chain gốc. Nó đã hiểu vì sao nó đưa ra mỗi quyết định và chống lại việc chất vấn lựa chọn đó.

**Giải pháp**: 1 instance độc lập — invocation Claude riêng không có reasoning context trước — tiếp cận output mới mẻ, đánh giá dựa trên cái xuất hiện mà không bị bias bởi quyết định trước.

**Phân biệt chính**: self-review cùng session — model giữ reasoning, xác nhận thay vì thách thức. Independent review — instance mới, đánh giá không bias, bắt lỗi tinh vi tốt hơn.

**Anti-pattern**:
```typescript
// Self-review in same session (ineffective)
const generation = await client.messages.create({
  messages: [
    { role: "user", content: "Write a function to process orders" },
    { role: "assistant", content: generatedCode },
    { role: "user", content: "Now review your code for bugs" }
  ]
});
```

**Pattern đúng**:
```typescript
// Independent review instance
const review = await client.messages.create({
  messages: [
    {
      role: "user",
      content: `Review this code for bugs, security issues, and edge cases:\n\n${generatedCode}`
    }
  ]
});
```

### Kiến trúc Multi-Pass Review

**Vấn đề Attention Dilution**: review lớn (multi-file PR, pipeline extraction phức tạp) chịu attention dilution gây: feedback chi tiết ở vài file, comment hời hợt ở file khác; bug rõ ràng bị bỏ sót ở phần giữa; finding mâu thuẫn (pattern giống hệt bị flag ở file này, approve ở file khác).

**Giải pháp 2-pass**:

**Pass 1 — Per-File Local Analysis**: phân tích mỗi file riêng với prompt review tập trung. Đảm bảo độ sâu nhất quán qua mọi file. Mỗi invocation chỉ xem xét 1 file.

**Pass 2 — Cross-File Integration**: nhận mọi finding per-file. Check issue cross-file: data flow giữa module, consistency API, conflict dependency, finding mâu thuẫn.

```typescript
// Pass 1: Per-file analysis
const perFileFindings = await Promise.all(
  files.map(file =>
    client.messages.create({
      messages: [{
        role: "user",
        content: `Review this file for local issues (bugs, security, logic errors):\n\n${file.content}`
      }]
    })
  )
);

// Pass 2: Cross-file integration
const integrationReview = await client.messages.create({
  messages: [{
    role: "user",
    content: `Given these per-file findings, identify cross-file issues:\n` +
      `- Data flow inconsistencies between modules\n` +
      `- Contradictory patterns flagged in different files\n` +
      `- API contract violations across service boundaries\n\n` +
      `Findings:\n${JSON.stringify(perFileFindings)}`
  }]
});
```

### Ngộ nhận về Context Window
**Exam trap**: "Chuyển sang model tier cao hơn với context window lớn hơn." Thực tế: "Vấn đề không phải context size. Nó là attention quality." Context window lớn hơn không ngăn được phân bổ attention không đều giữa các file. Chỉ per-file pass tập trung mới đảm bảo độ sâu nhất quán.

### Confidence-Based Routing
**Chiến lược routing**: finding confidence cao → report trực tiếp cho dev; finding confidence thấp → route human review để verify; calibrate threshold — dùng labeled validation set để tương quan confidence score với accuracy thực tế.

```json
{
  "finding": "Potential race condition in order processing",
  "severity": "major",
  "confidence": 0.65,
  "reasoning": "Lock acquisition pattern appears correct but unlock timing depends on async callback whose ordering cannot be fully verified.",
  "route": "human_review"
}
```

**Phân biệt quan trọng**: Confidence không calibrate — score tự báo cáo không validate, không đáng tin cho quyết định tự động (anti-pattern). Confidence đã calibrate — threshold validate qua labeled validation set, phù hợp cho quyết định routing.

### Kiến trúc Production hoàn chỉnh
1. **Generation**: instance đầu sinh code/extraction/analysis
2. **Per-file review**: instance độc lập review từng đơn vị output riêng
3. **Integration review**: instance riêng check consistency cross-unit
4. **Confidence routing**: finding confidence thấp route human review
5. **Calibration loop**: labeled validation set tinh chỉnh liên tục threshold confidence

**Trade-off**: đắt hơn single-pass review nhưng đáng giá khi chất lượng ảnh hưởng trực tiếp reliability (CI/CD, extraction tài chính, compliance).

### Exam traps

| Trap | Lỗi | Cách đúng |
|---|---|---|
| Self-review cùng session | Model giữ reasoning, khó chất vấn quyết định | Dùng instance độc lập không context trước |
| Single-pass multi-file review | Độ sâu không nhất quán, bỏ sót bug, mâu thuẫn | Chia: per-file local pass + cross-file integration pass |
| Model context window lớn hơn | Không giải quyết vấn đề attention quality | Implement per-file pass tập trung |
| Confidence scoring không calibrate | Được calibrate kém, không đáng tin cho routing | Calibrate dùng labeled validation set |

### Practice scenario
PR 14 file với review không nhất quán — feedback chi tiết ở vài file, hời hợt ở file khác, bỏ sót bug rõ ràng, finding mâu thuẫn. **Đáp án đúng (Option B)**: "Chia thành per-file local analysis pass cho độ sâu nhất quán, rồi chạy cross-file integration pass riêng cho issue data flow."
