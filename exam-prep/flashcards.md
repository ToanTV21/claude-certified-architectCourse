# CCA-F Flashcards

> Đọc câu hỏi, tự trả lời trước khi xem đáp án bên dưới.

## Bộ 1 — 20 câu cơ bản

1. **Q:** Giá trị `temperature` mặc định của Messages API là bao nhiêu?
   **A:** `1.0`.

2. **Q:** `system` prompt được truyền như thế nào trong Messages API?
   **A:** Là một tham số top-level (`system=...`), không phải một message với `role="system"`.

3. **Q:** Trong response streaming, text nội dung nằm trong loại event nào?
   **A:** `content_block_delta`.

4. **Q:** Cú pháp đúng để ép Claude gọi một tool cụ thể là gì?
   **A:** `tool_choice={"type": "tool", "name": "<tool_name>"}`.

5. **Q:** `tool_choice={"type": "auto"}` nghĩa là gì?
   **A:** Claude tự quyết định có gọi tool hay không, và gọi tool nào.

6. **Q:** `tool_choice={"type": "any"}` khác gì `auto`?
   **A:** Bắt buộc Claude phải gọi một trong các tool đã cung cấp (không được trả lời text thuần).

7. **Q:** MCP có 3 primitive chính là gì?
   **A:** Resources, Tools, Prompts.

8. **Q:** Ai kiểm soát việc kích hoạt Resources trong MCP?
   **A:** Application (app quyết định khi nào nạp dữ liệu).

9. **Q:** Ai kiểm soát việc kích hoạt Tools trong MCP?
   **A:** Model (Claude tự quyết định khi nào gọi).

10. **Q:** Ai kiểm soát việc kích hoạt Prompts trong MCP?
    **A:** User (thường qua slash command hoặc UI action).

11. **Q:** Khác biệt chính giữa Rules (CLAUDE.md) và Skills trong Claude Code?
    **A:** Rules luôn nạp vào context; Skills chỉ nạp có điều kiện khi được trigger.

12. **Q:** Batch API phù hợp với use case nào?
    **A:** Xử lý khối lượng lớn request không cần real-time — mô hình fire-and-forget, submit rồi poll kết quả sau.

13. **Q:** Khi nào nên dùng few-shot examples thay vì mô tả tiêu chí rõ ràng (explicit criteria)?
    **A:** Khi task khó diễn đạt bằng quy tắc tường minh — pattern matching qua ví dụ hiệu quả hơn.

14. **Q:** Nguyên tắc "root-cause resolution" trong thiết kế agent nghĩa là gì?
    **A:** Agent nên tìm và sửa nguyên nhân gốc của vấn đề, không chỉ patch triệu chứng bề mặt.

15. **Q:** Messages API có tự lưu trạng thái hội thoại (stateful) không?
    **A:** Không — API stateless, client phải tự gửi lại toàn bộ lịch sử `messages` mỗi lần gọi.

16. **Q:** Transport phổ biến cho MCP server chạy local là gì?
    **A:** `stdio`.

17. **Q:** Transport phổ biến cho MCP server remote là gì?
    **A:** HTTP / SSE.

18. **Q:** Điều gì xảy ra nếu truyền `system=None` tường minh?
    **A:** Có thể gây validation error — nên bỏ hẳn tham số nếu không dùng system prompt.

19. **Q:** Domain nào chiếm trọng số lớn nhất trong đề thi CCA-F?
    **A:** Agentic Architecture & Orchestration (27%).

20. **Q:** `max_tokens` có phải tham số bắt buộc trong Messages API không?
    **A:** Có — bắt buộc cùng với `model` và `messages`.

> ⚠️ Sửa từ bộ cũ: câu 16/17 (transport `stdio`/HTTP-SSE) không nằm trong nội dung guide chính
> thức đã đọc — giữ lại vì đúng về mặt kỹ thuật MCP nhưng KHÔNG phải trọng tâm thi CCA-F
> (hosting/transport MCP server nằm trong danh sách "chủ đề ngoài phạm vi thi", xem `references.md`).

## Bộ 2 — 25 câu từ nội dung guide đầy đủ (dựa trên 76 câu hỏi mẫu)

21. **Q:** Tool result được gửi trong `messages` với `role` nào?
    **A:** `role: "user"` chứa content block `{"type": "tool_result", "tool_use_id": ..., "content": ...}` — KHÔNG có `role: "tool"` riêng.

22. **Q:** Trường nào trong response điều khiển agentic loop (tiếp tục hay dừng)?
    **A:** `stop_reason` — `"tool_use"` thì chạy tool và lặp lại; `"end_turn"` thì dừng. Không parse text, không dùng max_iterations tùy ý làm điều kiện dừng chính.

23. **Q:** Khác biệt cốt lõi giữa Hooks và chỉ dẫn trong system prompt?
    **A:** Hooks đảm bảo deterministic (100%); prompt chỉ đạt xác suất (>90%, không phải 100%). Dùng hook khi hậu quả tài chính/pháp lý/an toàn (vd chặn refund > $500).

24. **Q:** Subagent được sinh ra bằng tool nào trong Claude Agent SDK, và điều kiện gì bắt buộc?
    **A:** Tool `Task`; `allowed_tools` của coordinator phải chứa `"Task"`. Subagent có context TÁCH BIỆT, không tự kế thừa lịch sử coordinator — phải truyền context tường minh.

25. **Q:** Message Batches API tiết kiệm bao nhiêu %, và giới hạn lớn nhất khi dùng cho agentic tool-calling là gì?
    **A:** Tiết kiệm 50%; KHÔNG hỗ trợ tool calling nhiều lượt trong 1 request (không thể chặn giữa chừng để chạy tool rồi tiếp tục) — bất tương thích với workflow gọi tool lặp.

26. **Q:** Batch API có SLA về latency không? Cửa sổ xử lý tối đa là bao lâu?
    **A:** Không có SLA; có thể mất tới 24 giờ. Vì vậy không bao giờ dùng cho bước chặn merge PR hay cần phản hồi ngay.

27. **Q:** 3 cấp phân cấp của CLAUDE.md là gì, và lỗi thường gặp nhất liên quan đến chúng?
    **A:** User (`~/.claude/CLAUDE.md`), Project (`.claude/CLAUDE.md` hoặc root), Directory (trong thư mục con). Lỗi thường gặp: hướng dẫn chỉ đặt ở cấp User nên thành viên mới clone repo không nhận được — phải đặt ở cấp Project.

28. **Q:** `.claude/rules/` với `paths` glob dùng khi nào, thay vì CLAUDE.md cấp thư mục?
    **A:** Khi quy ước trải rộng nhiều thư mục không liên tục (vd file test nằm rải rác khắp codebase) — quy tắc chỉ nạp khi file đang sửa khớp mẫu glob, tiết kiệm context.

29. **Q:** `context: fork` trong frontmatter của Skill dùng để làm gì?
    **A:** Chạy skill trong một subagent context tách biệt, để output dài dòng không làm ô nhiễm/cạn kiệt session chính.

30. **Q:** Vì sao đặt tên skill cá nhân trùng tên skill của nhóm là rủi ro?
    **A:** Skill cá nhân (`~/.claude/skills/`) cùng tên sẽ ÂM THẦM che khuất skill project — người dùng mất các cập nhật của nhóm mà không hay biết. Nên đặt tên khác (vd `/my-commit`).

31. **Q:** Khi nào nên dùng Planning mode thay vì thực thi trực tiếp?
    **A:** Thay đổi lớn (hàng chục file+), nhiều cách tiếp cận khả thi, quyết định kiến trúc, codebase chưa quen thuộc — không phải cho sửa lỗi đơn giản 1 file.

32. **Q:** Cờ CLI nào là cách ĐÚNG DUY NHẤT để chạy Claude Code non-interactive trong CI/CD?
    **A:** `-p` (hoặc `--print`). Không có `--batch`, không có biến `CLAUDE_HEADLESS` — đây là các đáp án bẫy.

33. **Q:** Vì sao nên dùng một Claude Code instance ĐỘC LẬP để review code, thay vì để chính session đã sinh code tự review?
    **A:** Session đã sinh code giữ lại context lý luận của chính nó nên ít có khả năng phản biện các quyết định của mình — một "cặp mắt mới" phát hiện vấn đề tinh vi tốt hơn.

34. **Q:** Review 14 file trong 1 lượt duy nhất thường gây ra vấn đề gì, và cách sửa chuẩn là gì?
    **A:** Attention dilution — phân tích sâu 1 số file, hời hợt các file khác, nhận xét mâu thuẫn. Sửa bằng: pass per-file riêng (vấn đề cục bộ) + 1 pass integration riêng (vấn đề liên file) — KHÔNG phải chuyển sang model to hơn/context lớn hơn.

35. **Q:** Khi 2 tool có mô tả gần giống nhau khiến agent định tuyến sai, cách sửa hiệu quả nhất là gì?
    **A:** Đổi TÊN và MÔ TẢ tool để loại bỏ chồng lấn ngữ nghĩa (vd `analyze_content` → `extract_web_results` với mô tả rõ ràng gắn với web/URL) — hiệu quả hơn thêm layer routing hay bộ classifier riêng.

36. **Q:** 4 loại lỗi trong hệ thống multi-agent, và loại nào KHÔNG nên retry?
    **A:** Transient (retry được, backoff), Validation (sửa input rồi retry), Business (không retry, giải thích + phương án khác), Permission (không retry, escalation).

37. **Q:** Lỗi subagent có cấu trúc nên chứa những trường gì để coordinator ra quyết định tốt?
    **A:** `status`, `failure_type`, `attempted_query`, `partial_results`, `alternative_approaches`, `coverage_impact` — KHÔNG phải một trạng thái chung chung như "search unavailable".

38. **Q:** Tín hiệu escalation nào KHÔNG đáng tin cậy, dù trông có vẻ hợp lý?
    **A:** Phân tích cảm xúc (tâm trạng không tương quan độ phức tạp), model tự đánh giá confidence 1-10 (có thể sai một cách tự tin), bộ classifier riêng huấn luyện thêm (overengineering).

39. **Q:** Khi nào nên escalate ngay lập tức, và khi nào nên "ghi nhận → đề xuất giải pháp → chỉ escalate nếu khách hàng nhắc lại"?
    **A:** Escalate ngay khi khách hàng yêu cầu tường minh ("gặp quản lý"). Với sự không hài lòng chung chung (chưa yêu cầu người thật), nên ghi nhận cảm xúc, đề xuất giải pháp cụ thể, và chỉ escalate nếu họ nhắc lại mong muốn gặp người thật.

40. **Q:** Khi hai nguồn dữ liệu đáng tin cậy đưa ra số liệu mâu thuẫn, agent phân tích tài liệu nên làm gì?
    **A:** Hoàn thành phân tích với CẢ HAI giá trị, chú thích rõ mâu thuẫn kèm trích dẫn nguồn, và để coordinator (có bối cảnh rộng hơn) quyết định cách dung hòa — không tự chọn 1 giá trị, không dừng lại chờ ngay lập tức.

41. **Q:** Cách hiệu quả nhất để giảm context token khi kết quả từ nhiều subagent quá lớn cho bước tổng hợp?
    **A:** Sửa các AGENT THƯỢNG NGUỒN để trả về dữ liệu có cấu trúc (facts, citations, relevance score) thay vì nội dung/lập luận dài dòng — sửa tại nguồn hiệu quả hơn thêm agent tóm tắt trung gian hay vector DB.

42. **Q:** Vì sao model "quên" thông tin đầu cuộc hội thoại 40 lượt dù chưa vượt context window?
    **A:** Claude API hoàn toàn stateless — không có bộ nhớ phía server. Nếu app không gửi lại toàn bộ lịch sử `messages` trong mỗi request, model không biết gì về các lượt trước.

43. **Q:** Cách tốt nhất để xử lý yêu cầu mơ hồ của người dùng (vd "đặt chỗ cho bữa tiệc") mà không gây tỷ lệ bỏ cuộc cao?
    **A:** Nêu giả định hợp lý một cách TƯỜNG MINH rồi tiến hành, mời người dùng đính chính — tốt hơn hỏi dồn nhiều câu làm rõ hoặc âm thầm dùng giá trị mặc định.

44. **Q:** Nguyên tắc thiết kế JSON schema nào giúp tránh việc model bịa giá trị khi thiếu dữ liệu?
    **A:** Chỉ đánh dấu `required` khi thông tin luôn có sẵn; dùng `"type": ["string", "null"]` cho trường có thể vắng mặt thay vì bắt buộc.

45. **Q:** `tool_use` + JSON Schema đảm bảo điều gì và KHÔNG đảm bảo điều gì?
    **A:** Đảm bảo JSON hợp lệ về CÚ PHÁP (đúng cấu trúc, đủ trường bắt buộc). KHÔNG đảm bảo tính đúng NGỮ NGHĨA (giá trị vẫn có thể sai/hallucinate) — cần validation + retry riêng cho việc đó.
