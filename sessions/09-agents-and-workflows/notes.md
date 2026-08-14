# Session 09: Agents and Workflows

## Lessons trong section này
- [x] Agents and workflows
- [x] Parallelization workflows
- [x] Chaining workflows
- [x] Routing workflows
- [ ] Agents and tools
- [ ] Environment inspection
- [ ] Workflows vs agents
- [ ] Quiz on Agents and Workflows

## Key Concepts

### 1. Agents vs Workflows — phân biệt cốt lõi
Cả 2 đều là chiến lược xử lý task mà Claude không thể xong trong 1 request duy nhất. Điểm
khác biệt nằm ở việc ta hiểu rõ task đến đâu:

- **Workflow** — 1 chuỗi lệnh gọi Claude được thiết kế sẵn (predetermined) để giải quyết 1
  vấn đề cụ thể qua các bước cố định. Dùng khi ta **hình dung được chính xác flow/step**
  Claude cần đi qua, hoặc khi UX của app giới hạn user vào 1 tập task cố định.
- **Agent** — cho Claude 1 goal + 1 bộ tool, để Claude **tự quyết định** cách hoàn thành goal
  đó qua nhiều bước. Dùng khi ta **không chắc trước** sẽ giao task/tham số gì cho Claude
  (task quá đa dạng, không thể liệt kê hết thành steps cố định).

→ Lưu ý: chỉ *nhận diện* được pattern (workflow/agent) không tự làm gì cả — vẫn phải viết
code thực sự để implement nó.

### 2. Ví dụ workflow thực tế — Image to CAD
Bài toán: user upload ảnh 1 metal part, app tự sinh ra file STEP (chuẩn công nghiệp cho 3D
model). Vì đã biết rõ từng bước cần làm khi có ảnh input → đây là ứng viên hoàn hảo cho
**workflow** (không cần agent tự quyết định gì cả):

1. Đưa ảnh vào Claude, yêu cầu mô tả object trong ảnh
2. Dựa trên mô tả, yêu cầu Claude dùng thư viện `CadQuery` để model lại object đó
3. Tạo bản rendering từ model vừa tạo
4. Yêu cầu Claude **chấm điểm** rendering so với ảnh gốc — nếu có vấn đề, quay lại sửa

### 3. Evaluator-Optimizer pattern
Workflow "Image to CAD" ở trên chính là 1 ví dụ điển hình của pattern **Evaluator-Optimizer**
— 1 recipe có thể tái sử dụng cho nhiều bài toán khác nhau:

- **Producer** — nhận input, tạo ra output (vd Claude dùng CadQuery để model + render)
- **Grader (Evaluator)** — chấm điểm output đó theo tiêu chí cho trước
- **Feedback loop** — nếu grader không chấp nhận, feedback được đưa ngược lại cho producer
  để cải thiện
- **Iteration** — lặp lại chu trình này cho tới khi grader chấp nhận output

→ Pattern này hữu ích bất cứ khi nào có 1 bước "tạo ra" và 1 bước "đánh giá" độc lập được với
nhau — vd sinh code rồi chạy test, viết bài rồi self-critique (xem `01_chaining_workflow.py`
— chaining là dạng đơn giản của evaluator-optimizer, chỉ chạy 1 vòng không lặp lại).

### 4. Parallelization workflows
**Vấn đề với single complex prompt:** khi task cần Claude đánh giá 1 input theo nhiều tiêu
chí khác nhau cùng lúc (vd chọn vật liệu phù hợp nhất cho 1 part trong 6 loại: metal,
polymer, ceramic, composite, elastomer, wood), nhồi hết tiêu chí của cả 6 loại vào 1 prompt
duy nhất khiến Claude phải cân nhắc quá nhiều consideration cùng lúc → kết quả kém tin cậy
hơn, dễ nhầm lẫn giữa các tiêu chí.

**Giải pháp — Parallelization:** thay vì 1 request khổng lồ, tách thành nhiều request chạy
song song, mỗi request chỉ tập trung đánh giá theo **1 tiêu chí chuyên biệt**:

1. **Split** — chia 1 task phức tạp thành nhiều sub-task độc lập, tập trung (vd 1 request/
   loại vật liệu, mỗi request có criteria riêng cho loại đó)
2. **Run song song** — gửi tất cả sub-task cùng lúc (cùng input, khác prompt/criteria) để
   xử lý nhanh hơn
3. **Aggregate** — thu kết quả từ tất cả sub-task, đưa lại cho Claude 1 lần nữa để so sánh
   và ra quyết định cuối cùng

Lưu ý: các sub-task **không cần giống hệt nhau** — mỗi cái có thể có prompt riêng, tool
riêng, hoặc tiêu chí đánh giá riêng.

**Lợi ích:**
- **Focused attention** — Claude tập trung vào đúng 1 khía cạnh mỗi lần, không phải cân bằng
  nhiều tiêu chí cạnh tranh nhau cùng lúc → phân tích sâu và chính xác hơn
- **Dễ optimize từng phần** — có thể cải thiện/test riêng prompt cho từng sub-task mà không
  ảnh hưởng các sub-task khác (vd sửa riêng prompt đánh giá metal mà không đụng tới polymer)
- **Dễ scale** — thêm 1 tiêu chí/loại đánh giá mới chỉ cần thêm 1 request song song, không
  phải viết lại các prompt đã có hay lo chúng xung đột với tiêu chí mới
- **Reliability cao hơn** — giảm cognitive load cho model nhờ chia nhỏ task → kết quả ổn
  định, nhất quán hơn

**Khi nào dùng:** phù hợp với quyết định phức tạp có thể tách thành nhiều đánh giá **độc
lập** — task cần Claude cân nhắc nhiều tiêu chí, so sánh nhiều lựa chọn, hoặc quyết định
đụng tới nhiều domain chuyên môn khác nhau. Điều kiện quan trọng: mỗi sub-task phải hoạt
động độc lập được và đóng góp 1 phần phân tích riêng biệt cho quyết định cuối.

## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
| `CadQuery` | Python library | — | Dùng để model 3D object bằng code trong workflow Image-to-CAD |
| `concurrent.futures.ThreadPoolExecutor` | Python stdlib | — | Cách phổ biến để chạy nhiều Claude call song song trong parallelization workflow |

## Gotchas
- [ ] Nhận diện được pattern (workflow/agent) chưa làm gì cả — vẫn phải tự viết code để
  implement nó, đây không phải thứ "tự động có sẵn"
- [ ] Evaluator-Optimizer cần điều kiện dừng rõ ràng (max iteration hoặc grader threshold)
  — nếu không dễ bị loop vô hạn khi grader không bao giờ "chấp nhận" được output
- [ ] Parallelization chỉ hiệu quả khi các sub-task **thực sự độc lập** — nếu sub-task B cần
  kết quả của sub-task A thì phải dùng chaining, không dùng parallelization được

## Code Snippets
```python
# Evaluator-Optimizer — vòng lặp producer -> grader -> feedback cho tới khi đạt
draft = produce(input_data)
for _ in range(MAX_ITERATIONS):
    verdict = evaluate(draft, criteria)
    if verdict.accepted:
        break
    draft = produce(input_data, feedback=verdict.feedback)

# Parallelization — chạy nhiều Claude call song song rồi aggregate
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    results = list(executor.map(evaluate_criterion, criteria_list))
final_decision = aggregate(results)
```

## Questions / Unclear Points
- ?
