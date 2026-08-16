# Báo cáo phân tích — ccar-architect-foundations.vercel.app (CCAR-F full bank, 162 câu)

> **Nguồn:** https://ccar-architect-foundations.vercel.app/ (site "ÔN TẬP" — có sẵn key đáp án +
> giải thích embedded trong dữ liệu trang, không phải site tự chấm sau khi làm bài).
> **Ngày tạo báo cáo:** 2026-08-15 21:08
> **Phương pháp:** Lấy toàn bộ 162 câu (câu hỏi + 4 lựa chọn + đáp án key) trực tiếp từ biến JS
> `DATA.topics[0].questions` nhúng trong trang (site không có backend, dữ liệu load thẳng vào
> `window`). Sau đó **tự đọc và phân tích lại từng câu bằng kiến thức Anthropic** (Building
> Effective Agents, Claude Code docs, tool-use guide, MCP spec) — KHÔNG chỉ copy phần `explain`
> có sẵn của site (phần đó là text template tự sinh, chất lượng thấp — câu bị cắt giữa chừng
> bằng "…", lý do loại các đáp án sai bị lặp y hệt "Bỏ qua yêu cầu chính…" cho mọi lựa chọn).
> Domain (D1–D5) là do tôi tự gắn theo nội dung câu hỏi, không phải nhãn chính thức của đề thi
> thật — chỉ mang tính tham khảo để cân đối ôn tập.

---

## 0. ĐỌC TRƯỚC KHI THI — Cheat sheet: common mistakes & cách chọn đáp án đúng nhanh

> Ghi lại từ pattern lặp đi lặp lại xuyên suốt cả 162 câu (không phải chỉ 1-2 câu riêng lẻ) — nếu
> chỉ còn 1-2 ngày, đọc kỹ phần 0 này trước, sau đó lướt nhanh domain còn yếu ở phần 3. Member
> confirm đề site này sát đề thật (~lệch 4 câu) → thuộc phần 0 gần như là thuộc "khung ra quyết
> định" của cả bài thi, áp dụng được cho câu chưa từng gặp.

### 0.1 — 6 nguyên tắc ra quyết định lặp lại nhiều nhất

1. **Sửa tại tầng CẤU TRÚC (schema/tool design/hook/code) luôn thắng sửa tại tầng LỜI NÓI (prompt
   instruction/few-shot/mô tả tool).** Bất cứ khi nào đề có 1 lựa chọn "tách tool/sửa schema/thêm
   hook/tool tự enforce" và 1 lựa chọn "thêm few-shot/nhấn mạnh prompt/dặn dò kỹ hơn" cho CÙNG 1
   vấn đề → chọn lựa chọn cấu trúc. Few-shot/prompt chỉ đúng khi vấn đề thật sự là "hành vi mơ hồ
   cần dạy ví dụ" (format chuẩn hoá, phân biệt trivial/meaningful...), không phải khi vấn đề là
   "ràng buộc bắt buộc/compliance/param required" (khi đó cần schema hoặc hook, few-shot chỉ là
   xác suất không phải đảm bảo). Ví dụ: Q2/Q25/Q98/Q141 (tách tool), Q56/Q103/Q145 (hook/enforce
   tại tool), Q158/Q21/Q29/Q94/Q126/Q23 (đúng chỗ dùng few-shot vì bài toán là "dạy hành vi").
2. **Không bao giờ tự động "sửa"/"điều chỉnh"/"suy đoán" số liệu quan trọng (tài chính, y tế) một
   cách âm thầm.** Thấy cụm "automatically adjusts/corrects the values" cho invoice/refund/số tiền
   → gần như luôn SAI. Đáp án đúng thường là: thêm field song song (`calculated_X` vs `stated_X`)
   + flag cho human review, HOẶC retry-with-error-feedback để model tự sửa có căn cứ. (Q17/18/33/
   61/71/75).
3. **Hội thoại NGẮN (vài nghìn token, còn xa giới hạn) mà vẫn "quên"/"trôi hướng dẫn" → nguyên
   nhân luôn là LỖI ENGINEERING CỤ THỂ (không gửi lại `messages`/`system` mỗi lần gọi — API
   stateless), KHÔNG BAO GIỜ là "attention tự nhiên suy yếu theo turn" hay "response tích luỹ làm
   loãng ảnh hưởng" (2 kiểu diễn đạt mơ hồ, không kiểm chứng được — thấy là loại ngay).
   Ngược lại, hội thoại THẬT SỰ DÀI (hàng chục nghìn token, gần chạm limit) mới áp dụng kỹ thuật
   context management thật (xem 0.3). (Q58/77/78/99 — dấu hiệu nhận biết: đề cho số token cụ thể,
   luôn so sánh với 200K).
4. **Không escalate/không action ngay chỉ vì tín hiệu cảm xúc (giận dữ, dấu chấm than, lặp câu
   hỏi).** Escalation/quyết định quan trọng phải dựa TIÊU CHÍ TƯỜNG MINH: khách hàng yêu cầu người
   thật rõ ràng, HOẶC vượt quyền hạn/policy exception, HOẶC agent không tiến triển được. Nhưng nếu
   agent ĐÃ đủ thông tin để giải quyết NGAY thì ưu tiên đề nghị giải quyết trước, không escalate
   vội (đối lập Q49 vs Q55 — đọc kỹ agent đã điều tra/có giải pháp trong tay chưa trước khi chọn).
5. **Khi khối lượng công việc/phân phối query đang "evolving"/"diverse"/không đoán trước được** →
   không chọn classifier train sẵn, không chọn rule cố định/pattern-based routing → chọn "để
   model/coordinator tự đánh giá động mỗi lần". Rule cứng chỉ đúng khi đề mô tả rõ 2 nhóm tách biệt
   ổn định, phân loại rẻ và chính xác (Q44/64 vs các câu routing cố định khác — đọc kỹ đề có nói
   "evolving"/"discover new applications" không).
6. **Tách hay gộp tool — nhìn đúng NGUYÊN NHÂN:** tham số bắt buộc khác nhau theo operation → TÁCH
   tool (Q2/25/98/141). Hai tool ngữ nghĩa chồng lấn/agent nhầm lẫn giữa 2 tool na ná nhau → GỘP
   tool (Q139/140). Đề luôn cho từ khoá "structurally eliminates" khi đáp án đúng là gộp/tách tại
   schema — không phải tách sub-agent hay thêm few-shot phân biệt.

### 0.2 — Bẫy đáp án SAI hay gặp nhất (loại ngay khi thấy, trừ khi đề có lý do đặc biệt)

- ❌ "Clear context / start fresh / restart session" khi vấn đề là cần GIỮ hiểu biết đã tích luỹ —
  hầu như luôn sai trừ khi đề nói rõ hiểu biết cũ không còn giá trị. Đáp án đúng thường là: tóm
  tắt + truyền tiếp, hoặc spawn subagent MỚI kèm summary, hoặc resume + báo cập nhật thay đổi.
- ❌ "Train a classifier / build a rules engine / decision tree" cho việc phân loại đang thay đổi
  liên tục — chọn "để model tự suy luận động" thay vào đó (xem nguyên tắc 5).
- ❌ "Consolidate/merge tất cả server hoặc tool thành 1" để giải quyết vấn đề THIẾU VISIBILITY —
  sai hướng, vấn đề là thiếu giao diện khám phá nội dung (dùng MCP **Resources**, không phải gộp
  server — Q110). Chỉ gộp tool đúng khi vấn đề là OVERLAP NGỮ NGHĨA giữa 2 tool cụ thể (Q139/140).
- ❌ "Increase context window / upgrade model tier / lower temperature" như giải pháp chính cho
  vấn đề THIẾT KẾ (schema/context-management/tool design) — đây luôn là distractor "né vấn đề
  thật" trong bộ đề này, gần như không bao giờ là đáp án đúng.
- ❌ Ép `tool_choice` cho **TOÀN BỘ pipeline/mọi lượt gọi** để đảm bảo thứ tự — sai, sẽ chặn luôn
  các tool khác về sau. Chỉ ép cho ĐÚNG 1 lượt đầu tiên cần đảm bảo thứ tự (Q19/95).
- ❌ Coi field `optional` (có thể bỏ hẳn) và **mảng rỗng hợp lệ** (field luôn có, có thể rỗng) là
  một — 2 khái niệm khác nhau, đề hay test đúng chỗ này (Q149).
- ❌ Bắt buộc field `required`/non-nullable để "ép" model luôn trả giá trị — làm TĂNG hallucination
  chứ không giảm; nullable + instruction "trả null nếu nguồn không nêu" mới đúng (Q22).
- ❌ Đưa raw confidence score/error message thô cho model tự diễn giải ngưỡng — nên TÍNH SẴN logic
  ngưỡng ở tầng tool/backend (đã test) rồi trả kết quả đã phân loại (`requires_review`,
  `retryable`, `errorCategory`...) cho model dùng trực tiếp (Q46/53/59/65/92/93/116/117/125).
- ❌ Dựa vào lời văn prompt ("CRITICAL, MUST, NEVER", viết hoa nhấn mạnh) để đảm bảo compliance
  cứng (ngưỡng tiền, threshold bắt buộc) — không bao giờ đủ tin cậy 100%; phải dùng hook
  (`PreToolUse`) hoặc tool tự enforce logic nội bộ (Q56/103/145).

### 0.3 — Bảng "thấy cụm từ này trong đề → nghĩ ngay pattern này"

| Cụm từ / tình huống trong đề | Pattern cần nhớ |
|---|---|
| "in the first place" / "without introducing latency" / "without overcomplicating the pipeline" | Loại bỏ MỌI lựa chọn hậu xử lý/multi-pass/2nd LLM call — chọn sửa tại nguồn (CLAUDE.md docs, schema, few-shot dạy hành vi) |
| Hội thoại dài, cần RECALL nhiều chủ đề/kết luận cũ đã đóng | Progressive summarization (tóm tắt cũ, giữ verbatim gần đây) |
| Hội thoại dài, cần 1 giá trị hiện tại luôn ĐÚNG/MỚI NHẤT (preference, status) hay bị GHI ĐÈ | Structured state object cập nhật mỗi lần đổi, đưa vào mọi request |
| Cần vài fact CỤ THỂ chính xác tuyệt đối xuyên suốt (dị ứng, ID, số liệu) + phần còn lại linh hoạt | Tách riêng structured "reference section"/"story bible" giữ cố định, chỉ tóm tắt phần còn lại |
| RAG/tool-output tích luỹ đè context, hội thoại thì vẫn cần giữ | Sliding window RIÊNG cho RAG/tool result, giữ nguyên conversation history |
| "structurally eliminates" | Đáp án đúng luôn ở tầng schema/tool design, không phải sub-agent/few-shot |
| MCP tool trả lỗi: thiếu param bắt buộc | JSON-RPC protocol error |
| MCP tool trả lỗi: business (404 not found, đã refund rồi...) hoặc hạ tầng (503) | Tool result với `isError: true` |
| Task 2+ subagent việc ĐỘC LẬP nhau nhưng đang chạy tuần tự/chậm | Phát nhiều Task tool call trong CÙNG 1 response message (không cần async layer ngoài) |
| Cần đảm bảo compliance/threshold tuyệt đối bất kể prompt | Hook (PreToolUse) hoặc logic enforce ngay trong tool, không phải prompt wording |
| Task đơn giản, rõ ràng, 1 file/1 hàm | Direct execution |
| Task phức tạp, nhiều file, breaking change, chưa rõ phạm vi ảnh hưởng | Plan mode trước khi implement |
| Trích xuất dữ liệu tài chính/số liệu mà tổng không khớp | Field `calculated_X` song song `stated_X` + flag review — KHÔNG tự động điều chỉnh |
| Sinh dữ liệu/test "low-value"/"trivial" cần giảm NGAY TỪ GỐC | Ghi rõ tiêu chuẩn + ví dụ vào CLAUDE.md, không lọc hậu kỳ |
| `--resume <tên>` vs `--continue` vs `--session-id` | `--resume <name>` = đúng session theo tên; `--continue` = gần nhất; `--session-id` = đúng UUID |
| `--system-prompt` vs `--append-system-prompt` | `--system-prompt` GHI ĐÈ (mất tool-use guidance mặc định); `--append-system-prompt` chỉ THÊM VÀO |

### 0.4 — Lưu ý nhanh theo domain (bổ sung phần 0.1–0.3, không lặp lại)

- **D1 (Orchestration):** Coordinator luôn là trung gian DUY NHẤT giữa các subagent — không có
  giao tiếp trực tiếp/shared-memory tự động trừ khi đề nói rõ đã cấu hình. Debug/explore luôn
  adaptive — không lập plan đầy đủ trước khi đọc file đầu tiên. `fork_session` khi cần đào sâu
  SONG SONG nhiều hướng từ 1 điểm context chung.
- **D2 (Tool/MCP):** Tool description nghèo → agent chọn sai tool dù tool đúng đã tồn tại — luôn
  cân nhắc "mở rộng mô tả" trước khi nhảy sang giải pháp phức tạp hơn. Lỗi transient (timeout/503)
  xử lý (retry) NGAY TRONG tool; lỗi business/non-transient trả thẳng cho agent kèm giải thích.
- **D3 (Claude Code):** `/memory` là bước chẩn đoán ĐẦU TIÊN khi nghi ngờ CLAUDE.md không được
  load đúng — đừng vội sửa nội dung rule trước khi xác nhận file có load hay không. Rules
  (`.claude/rules/*.md` + YAML `paths:`) dùng khi cần guidance theo LOẠI FILE tự động; `@imports`
  dùng khi maintainer/người viết tự quyết định cần include gì.
- **D4 (Structured Output):** Tool use (`tool_use`/forced schema) luôn đáng tin hơn "prompt yêu
  cầu output JSON rồi parse text". `system` prompt là top-level param, gửi lại MỖI LẦN gọi API,
  không nằm trong `messages`, không phải "gửi 1 lần lúc đầu".
- **D5 (Context/Reliability):** Luôn hỏi "hội thoại này ĐÃ dài chưa (so với 200K) hay còn ngắn?"
  trước khi chọn giữa "lỗi engineering cụ thể" (ngắn) và "kỹ thuật quản lý context" (dài) — đây là
  bẫy phổ biến nhất của domain này (xem nguyên tắc 3).

---

## 1. Tổng quan

- **162/162 câu** đã trích xuất đầy đủ + đối chiếu đáp án.
- Ngân hàng câu hỏi của site này **trùng lặp rất nhiều** với site `guided.maithienan.com` đã làm
  trước đó (xem [maithienan_website_test_2026-08-15_1734.md](maithienan_website_test_2026-08-15_1734.md))
  — nhiều câu giống hệt về nội dung/tình huống (vd Q1≈maithienan Q35, Q80≈Q1, Q79≈Q55, Q81≈Q49,
  Q106≈Q18, Q110≈Q60, Q123≈Q51, Q125≈Q10, Q126≈Q56, Q139≈Q53, Q141≈Q2, Q142≈Q39, Q144/160≈Q3/29,
  Q149≈Q12, Q154 xác nhận lại `--max-budget-usd`...). Nhiều khả năng cả 2 site cùng lấy từ 1 ngân
  hàng câu hỏi cộng đồng gốc → dùng để **đối chiếu chéo chất lượng đáp án** giữa 2 nguồn độc lập.
- **1 phát hiện đáng chú ý — sửa lại kết luận cũ:** Q78 ở site này (kịch bản giống hệt Q34 của
  maithienan: persona "expert contractor" tuân thủ tốt turn 1–4, generic dần từ turn 7, hội thoại
  chỉ ~2000–2500 token) có đáp án khác với maithienan. Site cũ chọn "accumulated responses diluting
  system prompt's influence" (D — một cách diễn đạt mơ hồ, không kiểm chứng được). Site này chọn
  **C — "The system prompt is only sent with the first API request"**. Sau khi đối chiếu lại: **C
  hợp lý hơn về mặt kỹ thuật** — Claude API là stateless, phải gửi lại `system` + toàn bộ
  `messages` ở MỌI lần gọi; nếu app chỉ gửi `system` ở request đầu tiên (lỗi implementation thật,
  không phải "attention tự nhiên suy yếu" — một khái niệm không có cơ sở kỹ thuật rõ ràng), guideline
  sẽ biến mất hoàn toàn từ turn 2 trở đi — khớp chính xác với hiện tượng mô tả. Ngữ cảnh chỉ
  2000–2500 token (rất nhỏ so với 200K) cũng loại trừ mọi giả thuyết "context dài làm loãng
  attention". Câu này cùng nhóm với Q77/Q99 của chính site này — cả hai đều nhấn mạnh nguyên nhân
  gốc "stateless API, không gửi lại đủ context mỗi lần gọi" — nên C nhất quán hơn D. **Kết luận:
  ghi nhớ lại đáp án C cho pattern này, không phải D như đã ghi trong báo cáo maithienan.**
- Ngoài phát hiện trên, đối chiếu toàn bộ 162 câu với kiến thức chính thức không phát hiện đáp án
  nào sai rõ ràng khác. 1 câu (Q127) có phần đề bài bị lỗi soạn thảo/garbled text ("Lead Data
  Scientist... something is not completely right...") — nội dung không đọc được mạch lạc, nhưng
  4 lựa chọn trùng khớp với Q11 (fork_session cho 2 hướng test song song) nên suy ra đúng là C —
  không tính là lỗ hổng kiến thức, chỉ là lỗi chất lượng đề của site.

## 2. Phân bố domain (tự gắn theo nội dung)

| Domain | Số câu | Tỷ trọng đề thi thật |
|---|---|---|
| D1 — Agentic Architecture & Orchestration | 32 | 27% |
| D2 — Tool Design & MCP Integration | 41 | 18% |
| D3 — Claude Code Configuration & Workflows | 29 | 20% |
| D4 — Prompt Engineering & Structured Output | 29 | 20% |
| D5 — Context Management & Reliability | 31 | 15% |

Bộ 162 câu này khá cân đối so với maithienan (không lệch domain nghiêm trọng), nhưng D2 hơi vượt
tỷ trọng thật (41 vs tỷ lệ 18% kỳ vọng ~29 câu/162) và D1 hơi thiếu — dùng để luyện phản xạ đọc đề
là chính, không dùng để tự đánh giá domain yếu/mạnh.

---

## 3. Chi tiết 162 câu — danh sách TUẦN TỰ Q1 → Q162

> **Đã restructure (bản cập nhật):** trước đây phần này nhóm theo domain nên số câu bị "nhảy cóc"
> (Q1 → Q4 → Q10...) và ~20 câu bị gộp chung 1 mục (`Q53 / Q59 / Q65 / Q93 / Q116 → B`) hoặc chỉ
> ghi con trỏ (`Q61. Xem Q18`) → không có đáp án riêng. Bản này liệt kê **đủ 162 câu theo đúng thứ
> tự đề gốc**, mỗi câu có **1 đáp án riêng** + phân tích ngắn. Nhãn `[D1]`–`[D5]` là domain tự gắn;
> muốn ôn theo domain thì xem **mục 4 — Index theo domain** ở cuối file.
>
> Ký hiệu: `≡ Qxx` = cùng pattern/gần trùng với câu khác trong chính bộ đề này; `=mtn Qxx` = trùng
> với câu số xx của site maithienan (đã đối chiếu chéo).

**Q1** `[D1]` — Debug lỗi 500 ngắt quãng, codebase 200+ file, chưa biết component nào liên quan →
**B**. Agent tự sinh subtask điều tra dựa trên phát hiện từng bước, điều chỉnh kế hoạch khi có
thông tin mới. Debug về bản chất là adaptive — không thể lập kế hoạch đầy đủ khi chưa biết bug nằm
đâu (loại D "lập plan toàn bộ trước khi đọc file nào"). (=mtn Q35)

**Q2** `[D3]` — Edit tool fail vì `old_string` không unique (docstring/tên biến lặp lại) → **A**.
Read load cả file → chèn hàm đúng vị trí → Write lại toàn bộ. Đáng tin hơn kéo dài `old_string` 30+
dòng (vẫn có thể trùng) hay `replace_all` (thay nhầm chỗ khác).

**Q3** `[D3]` — Resume đúng session đã đặt tên "auth-deep-dive" từ hôm qua, đã làm 3 codebase khác
từ đó → **A** (`--resume auth-deep-dive`). `--continue` chỉ lấy conversation GẦN NHẤT (đã bị
codebase khác ghi đè); `--session-id` cần UUID chứ không phải tên.

**Q4** `[D1]` — Subagent explore 30 phút bị ngắt, đồng nghiệp đã đổi tên 2 hàm trong lúc đó → **B**.
Resume từ transcript cũ NHƯNG báo cho agent biết các hàm đã đổi tên: giữ context tích luỹ nhưng cập
nhật thực tế mới — không bỏ qua thay đổi (A), không restart lãng phí (C/D). (≡ Q12)

**Q5** `[D5]` — Agent explore rendering 25 phút, bắt đầu trả lời chung chung "typical rendering
patterns" thay vì tên class cụ thể đã khám phá (context drift), giờ cần chuyển sang physics →
**B**. Tóm tắt findings rendering → spawn subagent MỚI cho physics kèm summary làm initial context.
Không `/clear` (mất liên kết rendering↔physics cần thiết), không tiếp tục trong context đã suy giảm.

**Q6** `[D3]` — Tìm hết caller trước khi xoá hàm, wrapper module đổi tên khi export (`calculateTax`
→ `computeOrderTax`) → **A**. Đọc library + wrapper để liệt kê hết TÊN (alias) được export, rồi
Grep từng tên trên toàn repo. Chỉ Grep tên gốc (B) bỏ sót alias; đọc từng file import (C) không
scale.

**Q7** `[D5]` — Session 30+ phút, agent trả lời không nhất quán về structure đã bàn → **C**. Agent
duy trì file scratchpad ghi finding chính, tham chiếu lại cho câu hỏi sau. Không clear định kỳ (mất
thông tin hữu ích), không đổi model tier (không sửa gốc vấn đề context accumulation).

**Q8** `[D2]` — MCP server có tool refactor chuyên dụng nhưng agent vẫn dùng Write/`sed` vì mô tả
tool quá sơ sài → **C**. Mở rộng mô tả tool: khi nào nên dùng, input/output kỳ vọng. Mô tả tool là
"giao diện" DUY NHẤT model nhìn thấy — mô tả nghèo thì tool tốt cũng không được chọn. (≡ Q15/Q132)

**Q9** `[D5]` — Investigation 15-file payment module, sau 8 file response kém chính xác dần → **B**.
Spawn subagent explore các file còn lại, có summary pattern đã phát hiện làm context ban đầu.
Subagent mới context "sạch" + đủ thông tin — hiệu quả hơn Grep thêm hay clear+restart. (≡ Q62)

**Q10** `[D1]` — Đã phân tích auth module hôm qua ra 2 hướng refactor, hôm nay muốn đào sâu CẢ HAI
song song để so sánh → **C** (`fork_session` tạo 2 nhánh từ session hôm qua). Giữ nguyên context đã
tích luỹ, tách nhánh thay vì lặp lại phân tích từ đầu ở 2 session riêng. (≡ Q11/Q127)

**Q11** `[D1]` — Tương tự Q10 nhưng 2 chiến lược test (end-to-end mock vs snapshot), cần phát triển
ĐỘC LẬP để so sánh trade-off → **A** (resume + `fork_session` enabled, mỗi nhánh 1 chiến lược).
⚠️ Lưu ý chữ cái khác Q10 dù cùng nội dung — đọc kỹ vị trí lựa chọn.

**Q12** `[D5]` — Session ID còn hợp lệ nhưng 3/12 file đã bị merge thay đổi qua đêm → **C**. Resume
session VÀ báo CỤ THỂ file nào đã đổi để re-analyze có mục tiêu. Cân bằng hiệu quả (không đọc lại cả
12 file — A) và độ chính xác (không bỏ qua thay đổi — D). (≡ Q4)

**Q13** `[D3]` — Caching logic trải 15 file (~8.000 dòng), cần hiểu trước khi thêm invalidation
trigger → **B**. Phân tích import/class hierarchy → tìm base cache class → Read hiểu interface →
trace implementation invalidation cụ thể. Đi từ trừu tượng xuống cụ thể, hiệu quả hơn đọc tuần tự
hết 15 file (A) hay Grep từ khoá rời rạc (C).

**Q14** `[D3]` — Auth/authorization architecture, 800+ file, engineer mới join → **C**. Grep tìm
entry point → đọc → follow import/function call map luồng auth dần dần. Exploration tiệm tiến theo
dấu vết code thật, không đọc mọi file khớp từ khoá (A) hay bắt user liệt kê sẵn 10-15 file (B).

**Q15** `[D2]` — MCP tool `analyze_dependencies` bị bỏ qua, agent vẫn dùng Grep → **B**. Mở rộng mô
tả + mô tả output để phân biệt rõ với Grep (nó trả dependency graph/cycle mà Grep không có). Không
gỡ Grep (C — cắt bỏ năng lực hợp lệ), không tách nhỏ tool (A — không sửa nguyên nhân mô tả nghèo).

**Q16** `[D4]` — Hợp đồng có điều khoản gốc + amendment (30 ngày → 45 ngày), model trích không nhất
quán giá trị nào → **C**. Redesign schema để field bị amend chứa NHIỀU giá trị, mỗi giá trị kèm vị
trí nguồn + ngày hiệu lực. Sửa tại cấu trúc schema phản ánh đúng nghiệp vụ (có nhiều phiên bản),
không ép chọn 1 giá trị bằng prompt (A) hay validation hậu kỳ (B).

**Q17** `[D4]` — 12% extraction lỗi semantic (pass schema validation nhưng sai ý nghĩa), chỉ đủ nhân
lực review 20% → **C**. Model xuất confidence score theo FIELD, hiệu chỉnh ngưỡng review bằng tập
validation có nhãn. Phân bổ review theo tín hiệu định lượng, hiệu quả hơn random sample (A) hay
heuristic bề ngoài (B).

**Q18** `[D4]` — Line item không cộng khớp grand total (8% invoice) → **D**. Thêm field
`calculated_total` (model tự cộng) song song `stated_total` + flag `is_total_consistent` cho human
review khi lệch. ❌ Tuyệt đối không "tự động điều chỉnh" số liệu tài chính (B). (≡ Q61, =mtn Q17/Q33)

**Q19** `[D2]` — Cần đảm bảo `extract_metadata` LUÔN chạy trước → **C**. Ép
`tool_choice = {"type":"tool","name":"extract_metadata"}` ở LƯỢT ĐẦU TIÊN, xử lý enrichment ở các
lượt sau. ❌ Không ép cho MỌI lượt trong pipeline (sẽ chặn luôn tool enrichment về sau) — high-risk
topic. (≡ Q95, chú ý Q95 đáp án là **A**)

**Q20** `[D1]` — Batch 10.000 doc, 300 doc lỗi `context_length_exceeded` → **A**. Chỉ resubmit 300
doc lỗi sau khi chunk nhỏ hơn, ghép lại kết quả. `max_tokens` (B) là giới hạn OUTPUT — không liên
quan lỗi context length đầu vào; chạy lại nguyên batch (C/D) tốn kém vô ích.

**Q21** `[D4]` — Field "materials" trích không nhất quán format ("cotton blend" vs "Cotton/Polyester
mix") → **B**. Few-shot 2-3 cặp input-output hoàn chỉnh minh hoạ format chuẩn hoá. Đây ĐÚNG chỗ
dùng few-shot (dạy hành vi/format), không phải đổi model tier (A) hay `temperature=0` (C — không
sửa vấn đề chuẩn hoá).

**Q22** `[D4]` — Field nullable nhưng model bịa giá trị hợp lý khi nguồn không nêu (attendee_count
"500") → **D**. Thêm instruction: trả `null` khi thông tin không được nêu TRỰC TIẾP trong nguồn.
❌ Bắt buộc field non-nullable (A) LÀM TĂNG hallucination — ngược hoàn toàn mục tiêu.

**Q23** `[D4]` — JSON hợp lệ nhưng field bắt buộc (citations, methodology) rỗng dù nguồn có thông
tin ở định dạng đa dạng (inline vs bibliography) → **C**. Few-shot minh hoạ trích xuất từ nhiều cấu
trúc tài liệu khác nhau. Dạy model nhận diện đa dạng định dạng, hơn regex hậu xử lý (A) hay retry
suông (D — không đổi cách model đọc nguồn).

**Q24** `[D4]` — Retry-with-error-feedback KÉM hiệu quả nhất với loại lỗi nào? → **C**. Model trích
"et al." vì danh sách đồng tác giả đầy đủ chỉ tồn tại ở NGUỒN NGOÀI, không có trong input. Retry
chỉ giúp khi thông tin đúng CÓ SẴN trong input nhưng bị format sai (A/B/D đều là lỗi format).

**Q25** `[D4]` — Menu nhà hàng format giá/dietary không nhất quán ("$12" vs "12.00", icon vs text) →
**A**. Schema chặt + quy tắc chuẩn hoá format ngay trong prompt. Chuẩn hoá tại nguồn sinh dữ liệu,
không tách nhiều call riêng (B) hay đẩy hết sang post-processing (C).

**Q26** `[D4]` — Enum `property_type` liên tục xuất hiện loại mới ("loft", "tiny house"), 8% fail
validation → **A**. Thêm giá trị `"other"` + field `property_type_detail` string ghi cụ thể. Giải
pháp DÀI HẠN: không phải liên tục mở rộng enum (D — bảo trì vô hạn) hay bỏ enum (C — mất validation).

**Q27** `[D4]` — Confidence >90% có accuracy 97% tổng thể, muốn tự động hoá review high-confidence →
**C**. Phân tích accuracy theo TỪNG loại document/field để xác nhận nhất quán across mọi segment.
97% trung bình có thể ẩn segment tệ hơn nhiều — phải xem breakdown trước khi tự động hoá diện rộng.

**Q28** `[D1]` — SLA 30h/99.9% reliability, batch window tối đa 24h → **D** (submit batch mỗi 4
giờ). Case xấu nhất: mỗi 6h → 6+24 = 30h, chạm đúng ngưỡng, không còn margin cho 99.9%; mỗi 4h →
4+24 = 28h, có margin an toàn.

**Q29** `[D4]` — Field `skills: string[]` không nhất quán (gộp/tách compound phrase, độ dài mảng dao
động 5–40+) → **C**. Few-shot minh hoạ xử lý compound phrase, tiêu chí "explicitly mentioned", độ
chi tiết entry phù hợp. Ràng buộc số cứng (B) không sửa vấn đề nhất quán ngữ nghĩa; chuẩn hoá hậu
kỳ (A) không sửa gốc.

**Q30** `[D1]` — 2 loại doc cùng schema, loại urgent cần alert trong 30 phút → **B**. Report định kỳ
→ Batch API (tiết kiệm 50%); report khẩn → Messages API real-time. Kiến trúc hybrid theo latency
requirement từng loại, không gộp chung 1 pipeline (A/C/D).

**Q31** `[D2]` — 1 tool `analyze_document` nhận free-text instruction, 35% kết quả phải re-request →
**B**. Tách thành tool chuyên biệt `extract_data_points` / `summarize_content` /
`verify_claim_against_source`, mỗi cái có input/output contract rõ. Free-text instruction không đủ
ràng buộc; enum param (A) vẫn chung 1 output contract mơ hồ.

**Q32** `[D2]` — Coordinator "nói" sẽ delegate nhưng không thực sự gọi subagent → **B**.
`allowedTools` của coordinator thiếu `"Task"` nên mô tả được ý định bằng lời nhưng không invoke
được. Lỗi cấu hình permission, không phải system prompt/context. (≡ Q63, đáp án Q63 là **D**)

**Q33** `[D1]` — Web-search agent trả data 2024, document-analysis trả data nội bộ 2022, synthesis
hiểu nhầm là mâu thuẫn → **C**. Bắt buộc subagent trả kèm ngày publication/thu thập trong structured
output. Vấn đề gốc là THIẾU METADATA THỜI GIAN, không phải cần lọc bỏ (B) hay luôn ưu tiên mới (A/D).

**Q34** `[D1]` — Pipeline crash giữa chừng (12/28 doc), cần resume không lặp lại việc → **C**. Mỗi
agent persist structured report vào vị trí cố định; coordinator load report và inject vào prompt khi
resume. Cân bằng trung thực thông tin ↔ hiệu quả context — không cần vector store (B) cho use case này.

**Q35** `[D1]` — Report cuối không nhất quán cách trình bày độ tin cậy → **B**. Dùng section tách
"confirmed findings" khỏi "contested analysis", GIỮ NGUYÊN cách diễn đạt gốc của nguồn. Ép về số
0.0–1.0 (A) tạo cảm giác chính xác GIẢ khi nguồn vốn đã mơ hồ.

**Q36** `[D1]` — Coordinator ra chỉ dẫn quá chi tiết/cứng cho subagent, gãy khi gặp tình huống ngoài
kịch bản → **B**. Chỉ định GOAL + tiêu chí chất lượng, để subagent tự quyết cách thực thi. Nguyên
tắc "general principle > brittle procedure" — không phải bỏ hết chỉ dẫn (A) hay thêm fallback vá
víu (C). (≡ Q142)

**Q37** `[D1]` — Subagent output khác nhau (JSON tài chính, prose tin tức, list patent) nhưng
synthesis ép hết về bullet point → **C**. Render đúng định dạng theo loại nội dung (bảng cho tài
chính, prose cho tin tức). Không chuẩn hoá cưỡng ép về 1 format chung (A/B/D — mất thông tin cấu trúc).

**Q38** `[D1]` — Web-search agent tìm được nguồn, document-analysis cần các nguồn đó → **A**.
Coordinator nhận output agent trước, đưa vào prompt khi gọi agent sau. Subagent KHÔNG giao tiếp
trực tiếp với nhau — coordinator là trung gian duy nhất. (≡ Q39/Q130)

**Q39** `[D1]` — Synthesis agent báo "không có research findings" dù 2 agent trước đã chạy xong →
**C**. Coordinator quên đưa output của agent trước vào prompt của synthesis agent. Lỗi kiến trúc
phổ biến nhất khi orchestrate nhiều agent tuần tự — không phải context window nhỏ (D).

**Q40** `[D1]` — Report cuối thiếu citation dù subagent đã gắn citation đúng ở output riêng → **A**.
Bắt buộc mọi subagent trả structured claim-source mapping, synthesis phải GIỮ NGUYÊN khi gộp. Sửa
tại nguồn, không vá bằng semantic-matching hậu kỳ (B) hay log-parsing (D). (≡ Q45)

**Q41** `[D1]` — Follow-up summarization mất 40s vì coordinator spawn lại synthesis subagent với
80K+ token dù chính nó đã có sẵn data → **C**. Coordinator TỰ xử lý summarization đơn giản bằng
context sẵn có, chỉ spawn subagent cho phân tích phức tạp thật sự.

**Q42** `[D1]` — Truyền context từ 3 agent (120K + 15K + 3K token) sang report-generation agent →
**B**. Truyền synthesis draft + structured source index map claim→URL/excerpt. Đủ thông tin trích
dẫn mà không cần full raw context (A) và không mất attribution (C/D).

**Q43** `[D1]` — Case pháp lý 12 tiền lệ, phân tích tuần tự mất 3 phút → **C**. Coordinator spawn
song song nhiều document-analysis subagent, mỗi cái 1 tập con tiền lệ, gộp kết quả trước synthesis.
Giữ khả năng coordinator giám sát/debug (khác message-queue ẩn A hay recursive hierarchy B/D).

**Q44** `[D1]` — Phân phối query không đều và ĐANG EVOLVING theo người dùng mới → **A**. Coordinator
tự phân tích từng query động, route linh hoạt. ❌ Không classifier train sẵn (C) / pattern cố định
(D) vì phân phối thay đổi liên tục. (≡ Q64)

**Q45** `[D1]` — Synthesis mất dấu nguồn nào ủng hộ kết luận nào khi gộp summary → **A**. Yêu cầu
tất cả subagent xuất structured claim-source mapping, giữ nguyên khi merge. Sửa tại nguồn dữ liệu,
không tái dựng bằng semantic matching hậu kỳ. (≡ Q40)

**Q46** `[D2]` — MCP tool `lookup_order` backend lỗi ("Order not found" / DB fail tạm thời) → **A**.
Trả error message trong tool result content với cờ `isError: true`. Lỗi THỰC THI (business/hạ tầng)
luôn về dạng tool result — không throw exception (D), không trả empty im lặng (C). (≡ Q125)

**Q47** `[D5]` — Dispute 25+ turn, escalate nhưng human agent KHÔNG truy cập được transcript → **D**.
Structured summary: customer ID, root cause, refund amount, recommended action. Không gửi transcript
đầy đủ (B — human không đọc/không truy cập được), không chỉ gửi chẩn đoán trống (C). (≡ Q51)

**Q48** `[D5]` — `lookup_order` trả 40+ field/lần, tool output chiếm phần lớn context, còn 2 order
nữa cần tra → **D**. Trích riêng field liên quan return (items, purchase date, return window,
status), bỏ chi tiết dư thừa từ response đã có. Chủ động dọn context TRƯỚC khi lookup thêm.

**Q49** `[D5]` — Khách bực bội, "đã giải thích 2 lần", đòi gặp người thật NGAY, agent CHƯA điều tra
gì → **A** (escalate ngay). Khách yêu cầu TƯỜNG MINH gặp người thật + agent chưa có gì để giải quyết
→ thoả tiêu chí escalation. ⚠️ Đối lập Q55 — ở đó agent ĐÃ có sẵn giải pháp nên không escalate vội.

**Q50** `[D5]` — Chọn cơ chế trigger escalation đáng tin nhất → **A**. Escalate khi: khách yêu cầu
người thật, HOẶC cần policy exception, HOẶC agent không tiến triển được. Tiêu chí tường minh —
không đếm số lần tool fail (B), không sentiment analysis (D — cảm xúc không đáng tin).

**Q51** `[D5]` — Agent phát hiện giữa chừng cần manager approval, vượt quyền hạn → **B**. Soạn
structured handoff (customer info, order info, vấn đề đã xác định) TRƯỚC khi gọi `escalate_to_human`.
Không thử refund liều (A), không chỉ forward message gốc (C), không chỉ đưa reference ID (D).

**Q52** `[D5]` — Đủ thông tin xác nhận refund eligible nhưng `process_refund` timeout ở backend →
**D**. Giải thích billing + xác nhận eligible + thừa nhận lỗi hệ thống + đề nghị escalate hoặc thử
lại sau. Minh bạch về lỗi thật — không giả vờ đã xử lý xong (C), không escalate ngay (A).

**Q53** `[D2]` — `lookup_order` lỗi, agent retry lãng phí 3-4 turn; tool chỉ trả plain-text error →
**C**. Trả structured error với `retryable: false` cho lỗi business + lời giải thích thân thiện để
Claude dùng lại cho khách. Agent cần metadata để QUYẾT ĐỊNH, không phải đoán từ text thuần. (≡ Q59/Q65/Q93)

**Q54** `[D1]` — Sau khi `lookup_order` trả order 45 ngày tuổi, agent quyết định gọi `process_refund`
hay `escalate_to_human` bằng cách nào? → **C**. Order details được đưa vào conversation, MODEL suy
luận chọn hành động. Đây là agentic loop chuẩn — không có decision tree (B) hay orchestration layer
(D) route thay model.

**Q55** `[D5]` — Khách mệt mỏi đòi gặp người thật NHƯNG `lookup_order` đã xác nhận return đơn giản,
xử lý được NGAY → **C**. Ghi nhận cảm xúc + thông báo giải quyết được ngay + mời chọn xử lý luôn
hoặc escalate. ⚠️ Đối lập Q49. Cũng không tự ý refund luôn không hỏi (A — bỏ qua quyền chọn của khách).

**Q56** `[D2]` — Compliance: refund > $500 PHẢI escalate, prompt đã rõ nhưng vẫn lọt 3% → **A**.
Hook `PreToolUse` chặn tool call ở tầng hệ thống khi amount > $500. Compliance CỨNG enforce bằng
code/hook — không bao giờ tin prompt dù viết "CRITICAL"/viết hoa (B). (≡ Q103/Q145)

**Q57** `[D5]` — 3 vấn đề riêng qua 45 turn, khách hỏi lại vấn đề cũ ở turn 48, gần chạm context
limit → **A**. Extract + persist structured issue data (order ID, amount, status) vào context layer
riêng. Structured state cho dữ liệu CÓ CẤU TRÚC cần truy xuất chính xác — khác progressive
summarization (dùng cho recall narrative, xem Q76/Q79).

**Q58** `[D5]` — Verify danh tính nhiều bước, sau câu hỏi thứ 3 agent hỏi lại tên như chưa từng hỏi
→ **D**. Conversation history KHÔNG được gửi lại trong request tiếp theo — API stateless. ❌ Không
phải "Claude chỉ nhớ 2 turn" (C) hay "thiếu instruction nhớ" (A). (≡ Q77/Q78/Q99)

**Q59** `[D2]` — `process_refund` có lỗi transient (5%) và lỗi business permanent (12%), agent phí
3-4 turn retry lỗi business → **B**. Trả structured error `retryable: false` cho lỗi business +
giải thích customer-friendly. Few-shot parse text (A) không đáng tin; retry-in-tool cho technical
(C) đúng một nửa nhưng không giải quyết phần customer-facing quality mà đề hỏi. (≡ Q53/Q65/Q93/Q116)

**Q60** `[D5]` — Khách quay lại sau 4 giờ, session cũ 32 turn có "Status: Pending Refund" → **A**.
Bắt đầu session MỚI, inject structured summary (loại vấn đề, bước đã xử lý, trạng thái hiện tại),
rồi tool call mới khi cần. Hiệu quả hơn resume nguyên 32-turn history dư thừa (B/D).

**Q61** `[D4]` — Biến thể Q18: 18% invoice line items không khớp grand total (OCR lỗi hoặc model
sai) → **D**. Field `calculated_total` (model tự cộng) + `stated_total`, flag cho human review khi
lệch. ❌ Không tự động điều chỉnh tỷ lệ (B) — đó là fabricate dữ liệu kế toán. (≡ Q18)

**Q62** `[D5]` — Investigation 45-file payment module, sau 8 file response kém chính xác → **B**.
Spawn subagent điều tra câu hỏi CỤ THỂ ("tìm hết test file", "trace refund flow") trong khi main
agent điều phối và giữ hiểu biết tổng quan. (≡ Q9)

**Q63** `[D2]` — Coordinator reason đúng về delegation nhưng không subagent nào chạy, log không lỗi
→ **D**. `allowedTools` thiếu `"Task"`. ⚠️ Cùng nội dung Q32 nhưng CHỮ CÁI KHÁC (Q32 = B) — đọc kỹ
vị trí lựa chọn, đừng nhớ máy móc theo chữ cái.

**Q64** `[D1]` — Query fact đơn giản vẫn đi hết 4 subagent (40s+), phân phối query diverse và
evolving → **A**. Coordinator tự đánh giá từng query và quyết định gọi subagent nào. ❌ Không
classifier train sẵn (B), không pattern-based routing cố định (D). (≡ Q44)

**Q65** `[D2]` — MCP tool trả lỗi đồng nhất `{"isError":true,"text":"Operation failed"}`, agent lúc
retry 5+ lần, lúc escalate sớm, lúc hỏi user → **B**. Bổ sung structured metadata: `errorCategory`
(transient/validation/permission), `isRetryable` boolean, mô tả nguyên nhân. (≡ Q53/Q59/Q93)

**Q66** `[D1]` — Document-analysis agent phát hiện gap chủ đề nhưng pipeline cứng đã qua giai đoạn
search → **B**. Analysis agent báo gap CỤ THỂ cho coordinator → coordinator trigger search có mục
tiêu → re-invoke analysis đến khi đủ. Vòng lặp phản hồi thật, khác chỉ gắn confidence cho người đọc
tự biết (A). (≡ Q111)

**Q67** `[D2]` — Cần agent truy cập Jira ticket data, đang copy-paste thủ công → **C**. Dùng MCP
server Jira CÓ SẴN (expose tickets/comments/metadata qua tool interface discoverable). Ưu tiên
server sẵn có hơn tự build custom (B) hay `curl` qua Bash (A — không discoverable, phải parse tay).

**Q68** `[D3]` — Bug production, stack trace chỉ rõ khu vực, nhưng chưa từng làm module này → **A**.
Direct execution: đọc stack trace → đọc code liên quan → sửa khi tìm ra root cause. Stack trace đã
đủ cụ thể — không cần plan mode cho việc rõ ràng, phạm vi hẹp. (≡ Q102; đối lập Q87)

**Q69** `[D4]` — Review tool precision cao / recall thấp vì prompt bảo "chỉ báo cáo khi chắc chắn" →
**A**. Tách 2 giai đoạn: giai đoạn TÌM tối đa coverage (gắn confidence + severity metadata cho mọi
phát hiện) + giai đoạn RIÊNG để threshold/lọc. Tách "tìm" khỏi "lọc" giải quyết trade-off triệt để
hơn cân bằng cả 2 trong 1 prompt (B/C).

**Q70** `[D2]` — Tool `remove_team_member` có `dry_run` nhưng agent bỏ qua preview 15% case → **C**.
Tách 2 tool: `preview_remove_member` trả confirmation token dùng-1-lần; `execute_remove_member` BẮT
BUỘC token đó. Ràng buộc bằng CẤU TRÚC tool (token binding), không phải dặn dò trong description (A)
hay validation theo thời gian 60s (D — vẫn bỏ qua được bước user confirm).

**Q71** `[D4]` — 12% extraction fail semantic validation dù JSON luôn hợp lệ → **D**. Khi validation
fail, gửi follow-up request kèm document gốc + kết quả extract + lỗi validation để model TỰ SỬA có
căn cứ. Đáng tin hơn auto-correct âm thầm (C) hay retry mù không kèm lý do (B). (≡ Q75)

**Q72** `[D4]` — Cần JSON tuyệt đối đúng schema (calendar invite), downstream reject mọi output sai
→ **C**. Định nghĩa TOOL với input schema đúng cấu trúc, lấy dữ liệu từ `tool_use` response. Tool
use ép cấu trúc ở tầng API — đáng tin hơn prompt yêu cầu JSON rồi parse text (A/D) hay prefill `{`
(B). (≡ Q91)

**Q73** `[D4]` — Document 175-190K token (limit 200K), accuracy tụt còn 71%, thông tin cuối bị bỏ
sót → **D**. Tool definition (~2.500 token) + system prompt + document cộng dồn TIỆM CẬN giới hạn
context → suy giảm xử lý phần cuối. Nguyên nhân kỹ thuật đo được, không phải "attention span" mơ hồ
(C) hay số field schema (A).

**Q74** `[D2]` — Nhiều loại doc, mỗi loại 1 extraction tool riêng; `tool_choice:"auto"` đôi khi trả
text → **A**. Gọi phân loại trước, RỒI gọi lần 2 với `tool_choice` ép đúng tool của loại doc đã xác
định. Vì chưa biết loại doc trước nên không thể ép ngay từ đầu; `"any"` (B) vẫn có thể chọn sai tool.

**Q75** `[D4]` — 12% fail Pydantic validation ("expected float, got '2 to 3'"), retry y nguyên vẫn
fail → **B**. Gửi follow-up request KÈM validation error để model sửa output. `temperature=0` (A)
không sửa lỗi ngữ nghĩa; đổi model tier (C) là né vấn đề. (≡ Q71)

**Q76** `[D5]` — History 85.000 token qua nhiều buổi thảo luận sách, hỏi lại kết luận cũ bị trả lời
chung chung → **D**. Progressive summarization: block cũ thay bằng tóm tắt trích rõ kết luận/quyết
định/chủ đề lặp lại, GIỮ NGUYÊN VĂN phần gần đây. Pattern chuẩn cho RECALL nhiều chủ đề đã đóng
trong hội thoại rất dài. (≡ Q79)

**Q77** `[D5]` — User nói thích jazz, 2 message sau Claude lại hỏi thích thể loại gì → **A**. App
không đưa các message trước vào `messages` array — API stateless không tự lưu history. Không phải
context window đầy (B) hay thiếu `session_id` (D — không tồn tại tham số này). (≡ Q58/Q99)

**Q78** `[D5]` — ⚠️ Persona "expert contractor" tuân thủ turn 1-4, generic dần từ turn 7, hội thoại
chỉ ~2.000 token → **C**. `system` prompt chỉ được gửi ở request ĐẦU TIÊN (lỗi implementation).
**Đã sửa lại so với báo cáo maithienan** (từng chọn D "accumulated responses diluting" — diễn đạt mơ
hồ, không kiểm chứng được). Xem chi tiết ở mục 1. (≡ Q77/Q99)

**Q79** `[D5]` — Sliding window 25 message pairs làm mất topic/preference cũ → **D**. Thay bằng
hybrid: TÓM TẮT phần cũ + giữ VERBATIM phần gần đây. Tăng window (A) chỉ trì hoãn vấn đề; vector
search (C) phá vỡ mạch hội thoại tuyến tính. (=mtn Q55)

**Q80** `[D5]` — Guideline tuân thủ turn 1-15, trôi dần turn 25-30, hội thoại 30K/200K token (chưa
chạm limit) → **B**. Chèn user-role message nhắc lại guideline quan trọng tại breakpoint tự nhiên,
đặc biệt trước request phức tạp. Regenerate-until-conform (D) tốn latency/cost và không sửa gốc.
⚠️ Khác Q84 (ở đó vấn đề là hướng dẫn quá trừu tượng → thay bằng few-shot). (=mtn Q1)

**Q81** `[D5]` — Webhook báo đã ship giữa lúc user đang chat, muốn assistant đề cập tự nhiên ở
response kế → **D**. Thêm shipping status vào system prompt TRƯỚC lượt gọi API kế tiếp. Không tạo
message giả danh user (A/B — xen ngang không tự nhiên), không ép gọi tool mọi lượt (C — lãng phí).
(=mtn Q49)

**Q82** `[D4]` — Response luôn mở đầu "Certainly!"/"I'd be happy to help!" → **A**. System prompt
liệt kê cụ thể cụm từ cần tránh. Giải pháp trực tiếp nhất cho vấn đề style/tone thuần; post-process
strip (B) brittle; hạ temperature (D) không liên quan.

**Q83** `[D5]` — Request mơ hồ ("book a venue"), hỏi trung bình 4.2 câu clarify → 35% bỏ cuộc →
**A**. Nêu rõ GIẢ ĐỊNH dựa trên history, tiến hành recommendation kèm mời sửa, CHỈ hỏi clarify cho
hành động KHÔNG THỂ ĐẢO NGƯỢC (xác nhận booking). Phân biệt reversible vs irreversible là mấu chốt.
(≡ Q101)

**Q84** `[D4]` — System prompt 2.800 token toàn hướng dẫn dạng văn xuôi, sau 12 turn bỏ qua dần
proficiency-adaptation → **B**. Thay hướng dẫn dài dòng bằng FEW-SHOT minh hoạ cụ thể sự khác biệt
giữa các mức trình độ. Ví dụ cụ thể "bám" tốt hơn hướng dẫn trừu tượng dài. ⚠️ Khác Q80 (ở đó là
"quên" → chèn reminder; ở đây là "hướng dẫn không đủ cụ thể để bám").

**Q85** `[D4]` — 12% extraction high-confidence (>85%) vẫn sai, nguồn lỗi đa dạng (bảng so sánh, phụ
lục biến thể) → **D**. Stratified random sampling review % cố định trên high-confidence hàng tuần →
ĐO ĐƯỢC error rate theo thời gian + phát hiện pattern MỚI. Hạ ngưỡng (B) tốn review; heuristic cứng
(C) chỉ bắt loại lỗi đã biết.

**Q86** `[D5]` — Hội thoại phân tích paper >60K token, câu hỏi cần số liệu chính xác (sample size,
p-value) bị trả lời hedge/sai sau khi tóm tắt → **D**. Database structured các fact quan trọng từ
mỗi paper, retrieve khi câu hỏi cần độ chính xác cao. Số liệu numeric cần lưu structured — không
tin vào tóm tắt tự do dù "instruct kỹ hơn" (B).

**Q87** `[D3]` — Migration breaking-change (auth lib v2→v3), 45 file across nhiều module → **C**.
Plan mode: khảo sát usage, map code path bị ảnh hưởng, lập chiến lược migration TRƯỚC khi implement.
Phạm vi rộng + breaking change cần plan. ⚠️ Đối lập Q68/Q102 (task hẹp, rõ → direct execution).

**Q88** `[D3]` — 3 vấn đề formatting PDF report TƯƠNG TÁC lẫn nhau (column width ↔ date ↔ page
break) → **A**. Sửa TỪNG vấn đề theo thứ tự với số đo cụ thể, verify xong mới sang vấn đề kế. Vì
các vấn đề tương tác, sửa cả 3 cùng lúc (D) tạo hiệu ứng dây chuyền khó debug.

**Q89** `[D3]` — Module thanh toán mới cần theo pattern của 3 module mẫu; task ONE-OFF, đã có doc ở
wiki team → **B**. Dùng `@references` đưa trực tiếp code 3 module vào prompt. Task một lần → không
thêm vào CLAUDE.md (C — CLAUDE.md dành cho convention lâu dài); code cụ thể chính xác hơn mô tả
bằng lời (D).

**Q90** `[D3]` — Monorepo 15 package, 3 file chuẩn chung, mỗi package CLAUDE.md duplicate cả 3 →
**A**. `@imports` trong CLAUDE.md từng package, chỉ trỏ tới standard liên quan, dựa trên hiểu biết
domain của MAINTAINER. Đề nhấn "maintainer tự hiểu domain requirement của mình". ⚠️ Khác Q138 (phân
loại theo LOẠI FILE → path-scoped rules mới đúng).

**Q91** `[D4]` — Extract resume (name/contact/skills/experience/education) phải khớp tuyệt đối JSON
schema → **A**. Định nghĩa tool với input schema đúng cấu trúc, lấy dữ liệu từ `tool_use` response.
⚠️ Cùng nội dung Q72 nhưng chữ cái khác (Q72 = C). (≡ Q72)

**Q92** `[D2]` — `lookup_order` trả generic "execution failed" → agent hoặc retry vô hạn hoặc
escalate ngay → **A**. Trả message CỤ THỂ theo loại lỗi + gợi ý bước tiếp theo ("order not found —
thử `get_customer` tìm theo số điện thoại"; "Database timeout (transient) — retry should succeed").
Đúng nguyên tắc chính thức Anthropic tool-use doc được trích trong chính đề bài. ❌ Không bỏ
`is_error` (C); không chặn lỗi trước khi Claude thấy (D).

**Q93** `[D2]` — Biến thể Q65 (MCP tool trả error đồng nhất, agent xử lý không nhất quán) → **B**.
Structured metadata: `error_category` (transient/retriable/permission), reason, mô tả nguyên nhân.
(≡ Q53/Q59/Q65/Q116)

**Q94** `[D4]` — Model bỏ sót NHÁNH điều kiện/error-path chưa test bên trong hàm ĐÃ có test → **D**.
Few-shot minh hoạ cặp: code có nhánh chưa test + review comment chỉ đích danh test case còn thiếu.
Đề yêu cầu "without overcomplicating the pipeline" → loại multi-pass pipeline (A).

**Q95** `[D2]` — `extract_metadata` phải chạy trước `lookup_citations`/`verify_doi` (cần DOI) →
**A**. Ép `tool_choice = {"type":"tool","name":"extract_metadata"}` cho lượt đầu, enrichment ở lượt
sau. ❌ Option D (ép cho MỌI API call trong pipeline) là bẫy — sẽ chặn luôn enrichment. ⚠️ Cùng nội
dung Q19 nhưng chữ cái khác (Q19 = C).

**Q96** `[D3]` — Review PR miss bug cross-file (rename param, caller ở file KHÔNG đổi) → **A**.
Redesign thành agentic task có turn limit, model tự đọc file + search codebase, follow reference để
verify. Linh hoạt hơn static dependency-graph 2 hop (C) hay parallel per-file pass (B).

**Q97** `[D2]` — `search_flights` gọi API ngoài thỉnh thoảng trả 503 Service Unavailable → **D**.
Tự retry với exponential backoff trong tool implementation trước khi trả kết quả cho agent — 503 là
lỗi TRANSIENT, nên tự phục hồi ở tầng tool. ❌ Tuyệt đối không trả empty list giả vờ thành công
(A/B). (Nếu đề nhấn "communicate to the agent" thay vì "handle" thì C là runner-up — đọc kỹ động từ
trong câu hỏi.) (≡ Q114/Q116)

**Q98** `[D2]` — `log_workout(exercise_type, value, measurement)` sai combo 23% (reps cho chạy bộ,
miles cho bench press) → **D**. Tách `log_cardio_workout` (duration_minutes/distance_miles) và
`log_strength_workout` (reps/sets). Enum constraint (C) VẪN cho phép combo sai giữa 2 category. (=mtn Q25)

**Q99** `[D5]` — Claude không nhớ từ vựng đã bàn ở turn trước → **A**. Không đưa message trước vào
mỗi API request — API stateless không giữ history. (≡ Q58/Q77/Q78)

**Q100** `[D5]` — Message ĐẦU TIÊN mơ hồ "Set up my focus music" (3 nghĩa: config / tạo playlist /
phát ngay) → **A**. Hỏi 1 câu clarify về LOẠI HÀNH ĐỘNG (play ngay hay config sau). Khi action-type
hoàn toàn không xác định (khác với chỉ thiếu chi tiết), 1 câu hỏi trực tiếp là cần thiết. ⚠️ Khác
Q83/Q101 (ở đó action-type đã rõ, chỉ thiếu tham số → giả định + mời sửa).

**Q101** `[D5]` — Assistant hỏi dồn 3 câu clarify 1 lúc → 40% bỏ cuộc → **C**. System prompt hướng
dẫn nêu giả định rõ ràng từ context sẵn có + đề nghị điều chỉnh nếu sai. Giới hạn 1 câu/turn (A) vẫn
tích luỹ nhiều turn hỏi; classifier riêng (B) phức tạp không cần thiết. (≡ Q83)

**Q102** `[D3]` — Thêm 1 điều kiện validate ngày vào 1 hàm, 1 file → **A** (direct execution). Task
đơn giản, phạm vi rõ ràng — plan mode (C/D) là overhead thừa. (≡ Q68)

**Q103** `[D3]` — CLAUDE.md có rule format nhưng 15-30% file vẫn sai dù đã viết hoa nhấn mạnh →
**B**. Hook `PostToolUse` matcher `Edit|Write` tự chạy Prettier sau mỗi lần sửa file. Enforcement
bằng hook = 100% deterministic, không phụ thuộc model "nhớ". (≡ Q56/Q145)

**Q104** `[D3]` — Cần thêm caching layer nhưng chưa rõ hết cân nhắc (invalidation, layer,
consistency, failure mode) → **C**. Nhờ Claude PHỎNG VẤN NGƯỢC user về requirement trước khi
implement. Khi chính user chưa rõ yêu cầu, để Claude surface các cân nhắc quan trọng tốt hơn code
luôn (A) hay spec đầy "TBD" (B).

**Q105** `[D3]` — Script migration không xử lý đúng null ở required field → **B**. Đưa TEST CASE cụ
thể (input có null + expected output) rồi yêu cầu Claude sửa. Feedback cụ thể, verify được — hơn mô
tả bằng lời (C) hay thêm "think harder" rồi rewrite toàn bộ (D). (≡ Q137)

**Q106** `[D1]` — Coordinator gọi tuần tự web-search rồi đợi xong mới gọi document-analysis dù 2
việc ĐỘC LẬP → **C**. Phát cả 2 lời gọi Task tool trong CÙNG 1 response message. Cơ chế nền tảng
của Claude Code/Agent SDK — không cần async layer ngoài (A). (=mtn Q18)

**Q107** `[D2]` — Review PR 30+ file dùng `report_findings`, response bị cắt giữa JSON vì chạm
`max_tokens` → **C**. Chia review thành nhiều API call, mỗi call 1 tập con file, gộp findings array.
Sửa nguyên nhân gốc (quá nhiều nội dung/1 response), không chỉ tăng `max_tokens` (B — vẫn có trần)
hay bỏ structured output (A).

**Q108** `[D3]` — Log lỗi lạ "SYNC_CONFLICT: entity version mismatch" không biết service nào trong
12 service sinh ra → **A**. Grep chuỗi đặc trưng của message lỗi trực tiếp trong codebase → Read
file khớp. Hiệu quả hơn đoán theo tên thư mục (C) hay đọc README trước (D). (≡ Q131/Q143)

**Q109** `[D1]` — "Thêm test cho codebase 200 file, không rõ ưu tiên module nào" → **C**. Glob/Grep
map cấu trúc → xác định module coupling cao → kế hoạch ưu tiên → điều chỉnh khi phát hiện dependency
mới. Không đọc hết 200 file trước (A), không làm theo alphabet (D).

**Q110** `[D2]` — Agent nối 3 MCP server, câu hỏi liên hệ thống tốn 8-10 tool call dò dẫm vì không
thấy được server nào chứa gì → **B**. Expose content catalog của mỗi server qua MCP **Resources**
(issue summaries, doc hierarchy, DB schema). Resources dành cho nội dung browsable/
application-controlled — đọc được KHÔNG cần tool-call round-trip. ❌ Gộp 3 server làm 1 (A) sai
hướng: vấn đề là thiếu VISIBILITY, không phải phân mảnh. (=mtn Q60)

**Q111** `[D1]` — Synthesis báo 3 câu hỏi nghiên cứu chưa trả lời được, coordinator vẫn tiến thẳng
tới report → **C**. Coordinator đánh giá gap trong synthesis output → re-delegate search với query
có mục tiêu → re-invoke synthesis. Vòng lặp hoàn thiện chủ động, không chỉ ghi chú hạn chế (A).
(≡ Q66)

**Q112** `[D2]` — Tool search trả `"Found 3 documents: ..."` dạng text, cần hỗ trợ workflow nhiều
bước tiếp → **A**. Trả structured data có document ID + metadata cho từng kết quả. Agent cần ID có
cấu trúc để tham chiếu ở bước sau — text thuần/URL (B)/mảng title (D) không đủ tin cậy.

**Q113** `[D2]` — 50+ connector, tool selection accuracy còn 58%; agent hay bỏ qua search hoặc chọn
sai sau khi search → **D**. `search_connectors` DYNAMICALLY thêm connector khớp vào bộ tool khả
dụng — connector khởi đầu ẩn, "persist" sau khi được discover. Pattern **progressive tool
disclosure**: giảm DECISION SPACE, không chỉ tăng chất lượng mô tả (A).

**Q114** `[D2]` — `publish_article` có cả lỗi transient (timeout/503) lẫn non-transient (403/422),
hiện trả hết cho agent → **B**. Retry transient NGAY TRONG tool; trả non-transient cho agent kèm mô
tả để agent hành động sửa. Phân chia trách nhiệm rõ ràng. (≡ Q97/Q116)

**Q115** `[D2]` — Race condition giữa `get_available_slots` và `book_appointment` (15% fail vì slot
bị người khác đặt) → **A**. Gộp thành 1 tool `find_and_book_appointment` ATOMIC (check + book trong
1 thao tác), trả booking đã xác nhận hoặc alternative. Hold 60s (B) vẫn còn khoảng hở; retry (C/D)
không loại bỏ race.

**Q116** `[D2]` — `search_catalog` fail 12%: 8% network timeout (retry là được) + 4% query syntax
error (không bao giờ được) → **B**. Retry với backoff cho timeout NGAY TRONG tool; trả syntax error
ngay lập tức kèm chi tiết validation param. (≡ Q97/Q114)

**Q117** `[D2]` — Tool extraction trả confidence score thô, agent tự diễn giải sai ngưỡng (23%
low-conf vẫn dùng, 31% high-conf review thừa) → **A**. Trả field + `requires_review` boolean ĐÃ
TÍNH SẴN theo ngưỡng đã kiểm chứng + `review_reasons` array. ❌ Đừng để model tự diễn giải số
confidence thô (C).

**Q118** `[D2]` — `update_game_score(game_date, home_team, away_team)` — agent nhầm biệt danh, sai
format ngày, chọn nhầm trận rematch cùng mùa → **D**. Thay 3 param bằng 1 `game_id` + tool
`search_games` tra ID trước. ID duy nhất loại bỏ hoàn toàn nhập nhằng — enum/regex (B) vẫn không
giải quyết được rematch trùng đội.

**Q119** `[D2]` — 4 subagent đều có TOÀN BỘ 18 tool, hay gọi tool ngoài chuyên môn → **C**. Chọn từ
18 tool thay vì 4-5 tool liên quan làm tăng độ phức tạp quyết định VƯỢT ngưỡng tin cậy. Nguyên nhân
gốc là quá nhiều lựa chọn, không phải role description (B) hay context window (D). Bài học: giới hạn
tool theo đúng vai trò từng subagent.

**Q120** `[D3]` — CLAUDE.md quy định `ApiError` nhưng Claude Code lúc theo lúc không, ngẫu nhiên
giữa các session → **A**. Chạy `/memory` kiểm tra file memory nào ĐANG được load. Bước CHẨN ĐOÁN
đầu tiên là xác nhận file có được nạp không — trước khi sửa nội dung (C) hay tạo rule path-scoped
(B).

**Q121** `[D1]` — CI review 50 PR/ngày ($150/ngày), non-blocking, cân nhắc Batch API giảm 50% chi
phí → **D**. Yếu tố quyết định: feedback trễ TỚI 24h có còn actionable không. Vì review không block
merge nên latency (C) không phải yếu tố quyết định.

**Q122** `[D5]` — Session dinner-party 78.000 token có cả fact cứng (dị ứng hải sản, khẩu phần,
thuật ngữ riêng của user) lẫn thảo luận chung → **D**. Trích structured data quan trọng riêng + tóm
tắt phần thảo luận chung + giữ nguyên văn phần gần đây. Kết hợp CẢ HAI kỹ thuật vì có CẢ HAI loại
thông tin. (≡ Q156)

**Q123** `[D2]` — Tool cấp phát resource chỉ trả ACK đơn giản → user approve mà không hiểu đã duyệt
gì → **A**. Trả structured data (cost estimate, target project, resource spec, impact summary) NGAY
trong tool response. Vấn đề gốc là RESPONSE NGHÈO THÔNG TIN — hold 60s (B) hay flag
`user_acknowledged` (C) không tự tạo ra thông tin. (=mtn Q51)

**Q124** `[D2]` — `search_products` khớp 200+ sản phẩm, auto-fetch hết mọi trang gây delay 15-20s →
**A**. Trả trang đầu + tổng số match + cursor cho trang tiếp. Để agent/user chủ động quyết định xem
thêm, thay vì luôn tải hết hay giới hạn cứng (B/D — mất dữ liệu ngầm).

**Q125** `[D2]` — 3 loại lỗi MCP: (1) thiếu param bắt buộc, (2) API trả 404 user không tồn tại, (3)
API trả 503 → **A**. Lỗi (1) = JSON-RPC **protocol error** (sai cách GỌI tool); lỗi (2) và (3) =
tool result với `isError: true` (lỗi THỰC THI, agent cần ngữ cảnh để quyết định retry hay báo user).
Kiến thức MCP-spec trọng tâm. (=mtn Q10, ≡ Q46)

**Q126** `[D4]` — 847 correction, 23% do đo lường phi chính thức ("a handful", "a splash") bị model
quy đổi số cụ thể hoặc bỏ trống → **A**. Few-shot minh hoạ xử lý đúng: trích NGUYÊN VĂN, không quy
đổi, không bỏ trống. Dạy hành vi bằng ví dụ rẻ hơn fine-tune (B) hay pattern-matching hậu kỳ (C).
(=mtn Q56)

**Q127** `[D1]` — ⚠️ Đề bài GARBLED (lỗi soạn thảo của site: "Lead Data Scientist... something is
not completely right...") nhưng 4 lựa chọn TRÙNG KHỚP Q11 → **C** (`fork_session` tạo nhánh riêng
cho từng chiến lược test). Suy ra từ cấu trúc lựa chọn — không tính là lỗ hổng kiến thức. (≡ Q10/Q11)

**Q128** `[D4]` — 1 prompt cho cả security/API design/business logic; thêm few-shot logic bug thì
logic recall tăng nhưng API recall giảm → **B**. Tách thành nhiều prompt TẬP TRUNG riêng theo loại
vấn đề, mỗi cái có ví dụ riêng, gộp kết quả sau. 1 prompt/1 bộ few-shot không thể tối ưu đồng thời
nhiều mối quan tâm khác biệt. Đổi model tier (D) là né vấn đề.

**Q129** `[D1]` — Review PR luôn theo ĐÚNG 1 quy trình 3 bước cố định (style → security → docs) cho
MỌI PR → **A** (prompt chaining). Workflow LUÔN giống nhau cho mọi input → chaining kinh điển; ❌
orchestrator-workers (C) dành cho phân rã ĐỘNG theo từng input khác nhau; routing (D) dành cho phân
loại rồi rẽ nhánh.

**Q130** `[D1]` — Coordinator cần cấp context cho synthesis subagent sau khi 2 agent trước xong →
**C**. Đưa TOÀN BỘ findings của 2 agent trực tiếp vào prompt của synthesis subagent. Không có
callback (A) hay shared-memory tự động (B) giữa các subagent. (≡ Q38/Q39)

**Q131** `[D3]` — Tìm hết file import package `@company/auth` trong monorepo → **B** (Grep pattern
câu lệnh import trong NỘI DUNG file). Glob (D) chỉ khớp tên file/path, không thấy nội dung import.
(≡ Q108/Q143)

**Q132** `[D2]` — `archive_file` vs `delete_file` mô tả tối giản → agent gọi nhầm delete cho "old
backups" → **C**. Mở rộng mô tả tool làm rõ use case + thêm "Do not use for backup files" ngay
trong description của `delete_file`. Sửa tại mô tả tool TRƯỚC khi cần server-side validation (A) hay
few-shot (B). (≡ Q8/Q15)

**Q133** `[D2]` — `delete_contact` nhầm record trùng tên gần giống, 8% bị reverse trong 24h, nhưng
flow confirm hiện tại quá nhiều bước gây friction → **D**. Hiển thị các record khớp KÈM TRƯỜNG PHÂN
BIỆT + xác nhận 1-click đúng target. Giải quyết CẢ độ chính xác lẫn friction — soft-delete (B) chỉ
sửa hậu quả, bắt nhập ID tay (A) đẩy friction sang user.

**Q134** `[D1]` — 50.000 hợp đồng, deadline 2 tuần, mẫu 500 doc cho thấy 18% lỗi ĐA DẠNG → **D**.
Chạy 2.000 doc mẫu qua REAL-TIME API để tìm pattern lỗi và tinh chỉnh prompt, RỒI batch toàn bộ
50.000 với prompt đã tối ưu. Tránh vòng lặp batch-rồi-sửa (B — mỗi vòng tốn tới 24h, không kịp deadline).

**Q135** `[D5]` — Deploy system prompt mới, user hội thoại đa phiên nhiều tuần thấy assistant mâu
thuẫn phát biểu cũ + đổi tone → **D**. VERSION hoá system prompt, gắn mỗi hội thoại với version tại
thời điểm bắt đầu, chỉ áp dụng update cho hội thoại MỚI. Không hồi tố thay đổi vào hội thoại đang
diễn ra (A/B).

**Q136** `[D4]` — Transcript họp >60 phút accuracy tụt còn 68% (thông tin rải rác) dù vẫn trong
context window → **C**. Chia transcript thành chunk → extract riêng từng chunk → gộp + dedupe.
Pattern map-reduce cho tài liệu dài rải rác, hơn few-shot (A) hay tóm tắt trước (D — mất chi tiết).

**Q137** `[D3]` — Graph traversal phức tạp có yêu cầu hiệu năng + edge case rõ ràng, cần iterate
hiệu quả → **B**. Viết TEST SUITE trước (hành vi, edge case, hiệu năng) → Claude viết code pass test
→ chia sẻ test fail ở mỗi vòng lặp. Test-driven feedback là tín hiệu khách quan, lặp lại được — hơn
review thủ công bằng mô tả (D). (≡ Q105)

**Q138** `[D3]` — Repo IaC (Terraform/K8s/CI-CD) mỗi phần convention riêng, root CLAUDE.md 500+ dòng
nạp thừa context → **D**. `.claude/rules/` với YAML frontmatter `paths:` scope theo LOẠI FILE, chỉ
nạp khi đang sửa file khớp pattern. ⚠️ Khác Q90 (ở đó là phân quyền theo domain nghiệp vụ do
maintainer tự quyết → `@imports`).

**Q139** `[D2]` — Tool 4 → 10, accuracy còn 71% vì tool CHỒNG LẤN NGỮ NGHĨA (`issue_credit` vs
`process_refund`; `check_delivery_status` vs `lookup_order`) → **B**. GỘP tool chồng lấn thành
`resolve_compensation` + flag `include_tracking`. Đề hỏi "structurally eliminates" → chỉ gộp mới
XOÁ overlap tại nguồn; tách sub-agent (A) chỉ chuyển vấn đề đi nơi khác. (=mtn Q53)

**Q140** `[D2]` — Biến thể Q139 (tool 1→7, accuracy 86%→71%) → **D**. Gộp `issue_credit` +
`process_refund` thành 1 tool với `action` param, fold `check_delivery_status` vào `lookup_order`
với flag `include_tracking`. ⚠️ Cùng nguyên tắc Q139 nhưng CHỮ CÁI KHÁC. (≡ Q139)

**Q141** `[D2]` — 1 tool dùng chung cho refund/cancel/reship — chung `order_id` nhưng KHÁC param bắt
buộc, agent hay thiếu/thừa param → **B**. Tách 3 tool riêng, mỗi tool chỉ định nghĩa đúng param của
operation đó. Nguyên tắc: **param bắt buộc khác nhau theo operation → TÁCH tool** (đối lập với
Q139/Q140: overlap ngữ nghĩa → GỘP). JSON Schema if-then-else (C) phức tạp và model không tuân thủ
tốt. (=mtn Q2)

**Q142** `[D4]` — System prompt fitness coach nhiều nhánh if-else theo từ khoá, bỏ sót tín hiệu NGẦM
(thuật ngữ kỹ thuật) khi user không khai trình độ → **C**. Thay phần lớn nhánh if-else bằng NGUYÊN
TẮC CHUNG ("match độ sâu giải thích theo thuật ngữ user dùng"), chỉ giữ nhánh an toàn/y tế bắt buộc.
Nguyên tắc chung tổng quát hoá tốt hơn danh sách if-else brittle (B). (=mtn Q39, ≡ Q36)

**Q143** `[D3]` — Tìm mọi chỗ dùng `eval()` trong codebase lớn để security scan → **D** (Grep pattern
`"eval("` trên toàn bộ file). Content search chuẩn — không dùng `ls -R | grep` (A), không Glob rồi
đọc từng file (B). (≡ Q108/Q131)

**Q144** `[D3]` — Test tự sinh 55% low-value (assertion tầm thường, trùng coverage, sai fixture
convention), cần giảm NGAY TỪ GỐC → **A**. Ghi rõ testing standard, fixture convention, ví dụ phân
biệt test giá trị vs trivial vào CLAUDE.md. Đề hỏi "in the first place" → loại mọi giải pháp lọc hậu
kỳ (B/C). (≡ Q160, =mtn Q3/Q29)

**Q145** `[D2]` — Threshold $500 reimbursement phải TAMPER-PROOF bất kể agent bị prompt thế nào →
**C**. Tool `process_reimbursement` TỰ ENFORCE ngưỡng nội bộ: <$500 auto-disburse; >$500 tạo pending
approval request. Logic nghiệp vụ bắt buộc nằm TRONG tool — không dựa param `approved_by_manager` do
model tự set (A), không dựa hook chỉ sửa context (B — tool vẫn có thể bỏ qua flag). (≡ Q56/Q103)

**Q146** `[D2]` — Structured JSON vs text tự do cho `portfolio_value` tool — ưu điểm CHÍNH của
structured output? → **C**. Agent trích xuất giá trị cụ thể không cần parse free-text → giảm lỗi ở
bước xử lý tiếp theo. ❌ Không phải validation tự động (A), không phải "model xử lý deterministic"
(B — sai về mặt kỹ thuật), không phải tiết kiệm token (D).

**Q147** `[D5]` — RAG result tích luỹ từ mọi query trước đè context, đẩy lùi conversation history,
coherence giảm sau 15+ turn → **B**. Sliding window RIÊNG cho RAG result (giữ 2-3 query gần nhất),
BẢO TOÀN toàn bộ conversation history. Phân biệt 2 loại nội dung khác bản chất: RAG context "hết
hạn" theo query mới, conversation history cần liên tục.

**Q148** `[D3]` — Team cần skill workflow migrate React→Vue dùng chung, gõ `/migrate-component`,
phải đồng bộ khi team cập nhật → **B**. `.claude/skills/migrate-component/SKILL.md` ở project root,
COMMIT vào version control. Project-scoped + version-controlled → mọi dev dùng bản mới nhất; khác
`~/.claude/skills/` (C — chỉ máy cá nhân).

**Q149** `[D4]` — Schema `pros`/`cons` (array) + `overall_sentiment` (enum); review ngắn bị bịa
pros/cons, review mỉa mai bị gán sentiment tuỳ tiện → **D**. Cho phép MẢNG RỖNG hợp lệ (không phải
optional/nullable) + thêm `"unclear"` vào enum. ⚠️ Bẫy kinh điển: `optional` (bỏ hẳn field) ≠ MẢNG
RỖNG (field luôn có, có thể rỗng); `"neutral"` là thừa vì bài toán là "không xác định được", không
phải "trung tính thật sự". (=mtn Q12, đã sửa lại)

**Q150** `[D1]` — Agent hết `max_turns` giữa chừng dispute phức tạp; cần ĐẢM BẢO mọi interaction kết
thúc bằng resolution HOẶC escalation → **A**. Code ở tầng ORCHESTRATION kiểm tra outcome sau khi
loop kết thúc — nếu chưa resolve/escalate thì tự động gọi `escalate_to_human` với context tích luỹ.
Safety-net NGOÀI tầm kiểm soát của model → đảm bảo tuyệt đối bất kể lý do loop dừng. Prompt
instruction (B) không đảm bảo được.

**Q151** `[D3]` — Cùng session review code do chính Claude vừa refactor bỏ sót bug mà CI review riêng
bắt được → **B**. Claude giữ context lý luận trước đó trong cùng session → ít có xu hướng phản biện
quyết định của chính nó (self-consistency bias). CI chạy fresh session, không mang "niềm tin" cũ.

**Q152** `[D2]` — 3 MCP server (git/Jira/docs) cùng cấu hình, user yêu cầu việc cần nhiều server →
**C**. Tool của TẤT CẢ MCP server được discover lúc connect và khả dụng ĐỒNG THỜI. Không cần chọn
server thủ công theo turn (B) hay routing theo prefix tên tool (D).

**Q153** `[D3]` — Request A (rename hàm) vs Request B (cải thiện error handling toàn module) — cái
nào hưởng lợi từ workflow multi-phase (analyze→propose→implement→review)? → **D** (Request B). Task
mơ hồ, nhiều quyết định thiết kế → cần phân tích/đề xuất trước khi code; rename là cơ học, rõ ràng,
không cần multi-phase.

**Q154** `[D3]` — Review PR lớn tốn 20 phút/$8-12/lần; cần CLAUDE CODE TỰ enforce giới hạn turn +
budget mỗi lần gọi → **A** (`--max-turns 10 --max-budget-usd 2.00` trong `claude -p`). Đã verify
`--max-budget-usd` là flag thật (print-mode only, tính cả chi phí subagent). ❌ `timeout-minutes` của
GitHub Actions (D) là job runner enforce, không phải Claude Code.

**Q155** `[D2]` — `update_user_profile` — Claude hay thiếu `user_id` hoặc sai cấu trúc → **B**. Mô
tả param RÕ RÀNG về format kỳ vọng ("user_id: UUID của user cần update (required)"). Mô tả param là
yếu tố quan trọng NHẤT giúp model điền đúng — hơn tên param dài dòng (A) hay chỉ dựa error response
sau khi sai (C). ⚠️ JSON Schema type constraint (D) chặn được type sai nhưng không dạy model biết
LẤY GIÁ TRỊ GÌ.

**Q156** `[D5]` — Story elements bền vững (nhân vật, plot, world rules) trộn lẫn brainstorming
ephemeral; sau 40+ turn assistant "quên" đặc điểm nhân vật → **A**. Tách riêng "story bible" giữ CỐ
ĐỊNH ở đầu context, chỉ trim/summarize phần brainstorming. Phân loại nội dung theo ĐỘ BỀN VỮNG để
áp chiến lược retention khác nhau. (≡ Q122)

**Q157** `[D5]` — User refine preference giữa hội thoại ("giờ đổi condo thay vì house"), assistant
đôi khi vẫn dùng preference CŨ dù update đã có trong history (context mới dùng 35%) → **D**.
Structured state object lưu preference HIỆN TẠI, cập nhật khi đổi, đưa vào MỌI request. Giá trị
MUTABLE cần ghi đè rõ ràng — không tin model tự "nhặt" bản mới nhất từ history dài. ❌ Không phải vấn
đề context đầy nên pruning (A) không đúng trọng tâm. (họ hàng =mtn Q13)

**Q158** `[D4]` — 35% finding của automated review là false positive theo pattern nhất quán (trái
convention team, an toàn trong deployment context này) → **D**. Few-shot ví dụ code ĐÃ ANNOTATE phân
biệt pattern chấp nhận được vs lỗi thật trong từng category. Đề hỏi "generalize to NOVEL patterns"
→ ví dụ cụ thể giúp TỔNG QUÁT HOÁ; spec đầy đủ (A) không scale; keyword filter (B) brittle; instruct
"be conservative" (C) làm giảm recall thật.

**Q159** `[D3]` — Pipeline review non-interactive dùng `--system-prompt`, Claude ngừng hẳn dùng
file-reading/code-navigation tool, chỉ nhìn raw diff → **A**. Đổi sang `--append-system-prompt` để
custom instruction được THÊM VÀO thay vì GHI ĐÈ default system prompt (vốn chứa hướng dẫn dùng
tool). Gotcha CLI quan trọng: `--system-prompt` = overwrite hoàn toàn.

**Q160** `[D3]` — Biến thể Q144: test tự sinh trivial, cần chất lượng cao NGAY TỪ ĐẦU, không thêm
latency, không sửa pipeline script → **A**. Document testing standard + fixture + ví dụ phân biệt
vào CLAUDE.md. Ràng buộc "without high latency / without modifying pipeline" loại B/C/D. (≡ Q144)

**Q161** `[D4]` — Cần tone/hành vi nhất quán XUYÊN SUỐT mọi tương tác (không riêng 1 hội thoại) →
**D**. Định nghĩa trong `system` prompt (top-level param). Kiến thức nền tảng API: `system` KHÔNG
nằm trong `messages`, không đặt ở message đầu tiên (A), không phải biến môi trường (B).

**Q162** `[D3]` — 1 MCP server dùng chung cả team (venue lookup) + 1 server cá nhân đang thử nghiệm
(playlist) → **B**. venue → `.mcp.json` (project scope, chia sẻ qua version control); playlist →
`~/.claude.json` (user/local scope, chỉ máy cá nhân). Đúng quy ước scope MCP của Claude Code.

---

## 4. Index theo domain (tra nhanh khi ôn theo domain yếu)

| Domain | Số câu | Danh sách câu |
|---|---|---|
| **D1** — Agentic Architecture & Orchestration | 32 | 1, 4, 10, 11, 20, 28, 30, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 54, 64, 66, 106, 109, 111, 121, 127, 129, 130, 134, 150 |
| **D2** — Tool Design & MCP Integration | 41 | 8, 15, 19, 31, 32, 46, 53, 56, 59, 63, 65, 67, 70, 74, 92, 93, 95, 97, 98, 107, 110, 112, 113, 114, 115, 116, 117, 118, 119, 123, 124, 125, 132, 133, 139, 140, 141, 145, 146, 152, 155 |
| **D3** — Claude Code Configuration & Workflows | 29 | 2, 3, 6, 13, 14, 68, 87, 88, 89, 90, 96, 102, 103, 104, 105, 108, 120, 131, 137, 138, 143, 144, 148, 151, 153, 154, 159, 160, 162 |
| **D4** — Prompt Engineering & Structured Output | 29 | 16, 17, 18, 21, 22, 23, 24, 25, 26, 27, 29, 61, 69, 71, 72, 73, 75, 82, 84, 85, 91, 94, 126, 128, 136, 142, 149, 158, 161 |
| **D5** — Context Management & Reliability | 31 | 5, 7, 9, 12, 47, 48, 49, 50, 51, 52, 55, 57, 58, 60, 62, 76, 77, 78, 79, 80, 81, 83, 86, 99, 100, 101, 122, 135, 147, 156, 157 |

## 5. Bảng đáp án nhanh (162 câu — tự chấm)

| # | Đ.A | # | Đ.A | # | Đ.A | # | Đ.A | # | Đ.A | # | Đ.A |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | B | 28 | D | 55 | C | 82 | A | 109 | C | 136 | C |
| 2 | A | 29 | C | 56 | A | 83 | A | 110 | B | 137 | B |
| 3 | A | 30 | B | 57 | A | 84 | B | 111 | C | 138 | D |
| 4 | B | 31 | B | 58 | D | 85 | D | 112 | A | 139 | B |
| 5 | B | 32 | B | 59 | B | 86 | D | 113 | D | 140 | D |
| 6 | A | 33 | C | 60 | A | 87 | C | 114 | B | 141 | B |
| 7 | C | 34 | C | 61 | D | 88 | A | 115 | A | 142 | C |
| 8 | C | 35 | B | 62 | B | 89 | B | 116 | B | 143 | D |
| 9 | B | 36 | B | 63 | D | 90 | A | 117 | A | 144 | A |
| 10 | C | 37 | C | 64 | A | 91 | A | 118 | D | 145 | C |
| 11 | A | 38 | A | 65 | B | 92 | A | 119 | C | 146 | C |
| 12 | C | 39 | C | 66 | B | 93 | B | 120 | A | 147 | B |
| 13 | B | 40 | A | 67 | C | 94 | D | 121 | D | 148 | B |
| 14 | C | 41 | C | 68 | A | 95 | A | 122 | D | 149 | D |
| 15 | B | 42 | B | 69 | A | 96 | A | 123 | A | 150 | A |
| 16 | C | 43 | C | 70 | C | 97 | D | 124 | A | 151 | B |
| 17 | C | 44 | A | 71 | D | 98 | D | 125 | A | 152 | C |
| 18 | D | 45 | A | 72 | C | 99 | A | 126 | A | 153 | D |
| 19 | C | 46 | A | 73 | D | 100 | A | 127 | C | 154 | A |
| 20 | A | 47 | D | 74 | A | 101 | C | 128 | B | 155 | B |
| 21 | B | 48 | D | 75 | B | 102 | A | 129 | A | 156 | A |
| 22 | D | 49 | A | 76 | D | 103 | B | 130 | C | 157 | D |
| 23 | C | 50 | A | 77 | A | 104 | C | 131 | B | 158 | D |
| 24 | C | 51 | B | 78 | C | 105 | B | 132 | C | 159 | A |
| 25 | A | 52 | D | 79 | D | 106 | C | 133 | D | 160 | A |
| 26 | A | 53 | C | 80 | B | 107 | C | 134 | D | 161 | D |
| 27 | C | 54 | C | 81 | D | 108 | A | 135 | D | 162 | B |

> **Cặp câu dễ nhầm CHỮ CÁI (cùng nội dung, khác vị trí lựa chọn) — đọc kỹ đáp án, đừng nhớ máy
> móc:** Q10 (C) ↔ Q11 (A) ↔ Q127 (C) · Q19 (C) ↔ Q95 (A) · Q32 (B) ↔ Q63 (D) · Q72 (C) ↔ Q91 (A) ·
> Q139 (B) ↔ Q140 (D) · Q144 (A) ↔ Q160 (A) · Q18 (D) ↔ Q61 (D) · Q9 (B) ↔ Q62 (B).
