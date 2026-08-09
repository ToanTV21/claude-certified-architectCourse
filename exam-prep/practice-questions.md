# CCA-F Practice Questions — Mock Exam (10 câu)

> Trả lời trước, sau đó xem đáp án + giải thích ở cuối mỗi câu.

---

**1.** Giá trị mặc định của `temperature` trong Messages API là gì?
A. 0.0  B. 0.7  C. 1.0  D. Không có giá trị mặc định

<details><summary>Đáp án</summary>
**C. 1.0** — đây là gotcha hay bị nhầm với 0.7 (giá trị phổ biến ở các API khác).
</details>

---

**2.** Cách đúng để truyền system prompt trong Messages API là gì?
A. `messages=[{"role": "system", "content": "..."}, ...]`
B. `system="..."` (tham số top-level)
C. `client.system("...")`
D. Đặt trong `metadata={"system": "..."}`

<details><summary>Đáp án</summary>
**B** — `system` là tham số top-level riêng biệt, không phải một message trong list `messages`.
</details>

---

**3.** Để bắt buộc Claude gọi đúng tool tên `search_docs`, `tool_choice` nên là gì?
A. `{"type": "auto"}`
B. `{"type": "any"}`
C. `{"type": "tool", "name": "search_docs"}`
D. `{"force": "search_docs"}`

<details><summary>Đáp án</summary>
**C** — `{"type": "tool", "name": "..."}` ép gọi đúng 1 tool cụ thể. `auto` để Claude tự chọn, `any` chỉ ép phải chọn 1 trong các tool (không chỉ định tên).
</details>

---

**4.** Trong MCP, primitive nào là "model-controlled" (Claude tự quyết định kích hoạt)?
A. Resources  B. Tools  C. Prompts  D. Sampling

<details><summary>Đáp án</summary>
**B. Tools** — Resources là application-controlled, Prompts là user-controlled.
</details>

---

**5.** Khi streaming response, đoạn text thực sự của model nằm trong loại event nào?
A. `message_start`  B. `content_block_start`  C. `content_block_delta`  D. `message_stop`

<details><summary>Đáp án</summary>
**C. content_block_delta** — các event khác chỉ đánh dấu vòng đời của message/block, không chứa nội dung text.
</details>

---

**6.** Sự khác biệt chính giữa "Rules" (CLAUDE.md) và "Skills" trong Claude Code là gì?
A. Rules chỉ dùng cho Python, Skills dùng cho mọi ngôn ngữ
B. Rules luôn nằm trong context, Skills chỉ nạp khi được trigger
C. Skills là tính năng cũ hơn Rules
D. Không có khác biệt, dùng thay thế nhau được

<details><summary>Đáp án</summary>
**B** — đây là điểm thiết kế cốt lõi: Rules tốn context liên tục, Skills lazy-load theo tình huống, giúp tiết kiệm token.
</details>

---

**7.** Batch API phù hợp nhất với use case nào?
A. Chatbot cần phản hồi real-time cho người dùng
B. Xử lý hàng loạt request không cần kết quả ngay lập tức
C. Streaming video call
D. Gọi 1 request duy nhất

<details><summary>Đáp án</summary>
**B** — Batch API là mô hình fire-and-forget: submit batch, poll trạng thái, lấy kết quả sau, tối ưu cho khối lượng lớn không cần real-time.
</details>

---

**8.** Khi nào nên ưu tiên few-shot examples thay vì liệt kê explicit criteria trong prompt?
A. Khi task có logic rất rõ ràng, dễ liệt kê quy tắc
B. Khi task khó diễn đạt bằng luật tường minh, pattern matching qua ví dụ hiệu quả hơn
C. Luôn luôn ưu tiên few-shot trong mọi trường hợp
D. Few-shot chỉ dùng được với tool use

<details><summary>Đáp án</summary>
**B** — few-shot mạnh khi mô tả bằng lời khó bao quát hết case, ví dụ cụ thể giúp model nắm pattern tốt hơn.
</details>

---

**9.** Nguyên tắc "root-cause resolution" trong thiết kế agent nhấn mạnh điều gì?
A. Agent nên sửa nhanh triệu chứng để tiết kiệm thời gian
B. Agent nên tìm và giải quyết nguyên nhân gốc của vấn đề, không chỉ patch bề mặt
C. Agent không cần quan tâm nguyên nhân, chỉ cần output đúng
D. Root cause chỉ áp dụng cho debugging code, không áp dụng cho thiết kế agent

<details><summary>Đáp án</summary>
**B** — thiết kế agent tốt hướng tới xử lý triệt để nguyên nhân, tránh các bản vá tạm bợ gây lỗi lặp lại.
</details>

---

**10.** Messages API có tự động lưu lịch sử hội thoại giữa các lần gọi không?
A. Có, server tự lưu session
B. Không, API stateless — client phải tự gửi lại toàn bộ `messages` mỗi lần gọi
C. Chỉ lưu nếu bật `stream=True`
D. Chỉ lưu nếu dùng MCP

<details><summary>Đáp án</summary>
**B** — Messages API là stateless theo thiết kế; ứng dụng chịu trách nhiệm quản lý và gửi lại lịch sử hội thoại.
</details>
