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

## 3. Chi tiết 162 câu theo domain

### D1 — Agentic Architecture & Orchestration (32 câu)

**Q1.** Debug lỗi 500 ngắt quãng, codebase 200+ file, chưa biết component nào liên quan → **B**
(agent tự sinh subtask điều tra dựa trên phát hiện từng bước, điều chỉnh kế hoạch khi có thông
tin mới). Debug về bản chất là adaptive, không thể lập kế hoạch đầy đủ khi chưa biết bug nằm đâu.

**Q4.** Subagent explore 30 phút bị ngắt kết nối, đồng nghiệp đã đổi tên 2 hàm trong lúc đó → **B**
(resume từ transcript cũ NHƯNG báo cho agent biết về các hàm đã đổi tên). Giữ context tích lũy
nhưng phải cập nhật thực tế mới, không bỏ qua thay đổi cũng không restart lãng phí.

**Q10.** Đã phân tích auth module hôm qua ra 2 hướng refactor, hôm nay muốn đào sâu CẢ HAI song
song để so sánh → **C** (`fork_session` tạo 2 nhánh từ session hôm qua). Giữ nguyên context đã
tích lũy, tách nhánh thay vì lặp lại phân tích từ đầu ở 2 session riêng.

**Q11.** Tương tự Q10 nhưng cho 2 chiến lược test (end-to-end mock vs snapshot) → **A**
(`fork_session` enabled, mỗi nhánh 1 chiến lược).

**Q20.** Batch 10.000 doc, 300 doc lỗi `context_length_exceeded` → **A** (chỉ resubmit 300 doc lỗi
sau khi chunk nhỏ hơn, ghép lại kết quả). Tăng `max_tokens` không giải quyết lỗi context length
đầu vào; xử lý lại nguyên batch 10.000 doc tốn kém không cần thiết.

**Q28.** SLA 30h/99.9% reliability, batch window 24h → **D** (submit batch mỗi 4 giờ). Case xấu
nhất mỗi 6h = 6+24=30h, sát ngưỡng SLA không có margin cho 99.9% reliability; mỗi 4h = 4+24=28h,
có margin an toàn.

**Q30.** 2 loại doc cùng schema, urgent cần alert trong 30 phút → **B** (report định kỳ → Batch
API tiết kiệm 50%; report khẩn → Messages API real-time). Kiến trúc hybrid theo latency
requirement của từng loại, không gộp chung 1 pipeline.

**Q33.** Web-search agent trả data 2024, document-analysis agent trả data nội bộ 2022, synthesis
agent hiểu nhầm là mâu thuẫn → **C** (bắt buộc subagent trả kèm ngày publication/thu thập dữ liệu
trong structured output). Vấn đề gốc là thiếu metadata thời gian, không phải cần agent lọc bỏ hay
luôn ưu tiên data mới nhất.

**Q34.** Multi-agent pipeline crash giữa chừng (12/28 doc), cần resume không lặp lại việc → **C**
(mỗi agent persist structured report vào vị trí cố định; coordinator load report và inject vào
prompt khi resume). Cân bằng giữa độ trung thực thông tin và hiệu quả context — không cần vector
store phức tạp cho use case này.

**Q35.** Report cuối thiếu nhất quán cách trình bày độ tin cậy → **B** (dùng section rõ ràng tách
"confirmed findings" khỏi "contested analysis", giữ nguyên cách diễn đạt gốc của nguồn thay vì ép
về số 0.0–1.0). Chuẩn hoá xác suất giả tạo (option A) tạo cảm giác chính xác giả khi nguồn gốc vốn
đã mơ hồ.

**Q36.** Coordinator ra chỉ dẫn quá chi tiết/cứng cho subagent, gãy khi gặp tình huống ngoài kịch
bản → **B** (chỉ định goal + tiêu chí chất lượng, để subagent tự quyết cách thực thi, không phải
chỉ dẫn từng bước). Cùng nguyên tắc "general principle > brittle procedure" như Q142.

**Q37.** Nhiều loại subagent output khác nhau (JSON tài chính, prose tin tức...) nhưng synthesis
agent ép hết về bullet point, mất cấu trúc gốc → **C** (render đúng định dạng theo loại nội dung —
bảng cho tài chính, prose cho tin tức), không chuẩn hoá cưỡng ép về 1 format chung.

**Q38.** Web-search agent tìm được nguồn, document-analysis agent cần các nguồn đó → **A**
(coordinator nhận output của agent trước, đưa vào prompt khi gọi agent sau). Subagent không giao
tiếp trực tiếp với nhau — coordinator là trung gian truyền context.

**Q39.** Synthesis agent báo "không có research findings" dù 2 agent trước đã chạy xong → **C**
(coordinator quên đưa output của các agent trước vào prompt của synthesis agent). Lỗi kiến trúc
phổ biến nhất khi orchestrate nhiều agent tuần tự.

**Q40.** Report cuối thiếu citation dù các subagent đã gắn citation đúng ở output riêng → **A**
(bắt buộc mọi subagent trả structured claim-source mapping, và synthesis agent phải giữ nguyên khi
gộp). Sửa tại nguồn (structured metadata xuyên suốt pipeline), không vá bằng semantic-matching hậu
kỳ hay log-parsing.

**Q41.** Follow-up summarization request luôn mất 40s vì coordinator spawn lại synthesis subagent
với 80K+ token dù chính coordinator đã có sẵn data đó → **C** (coordinator tự xử lý summarization
đơn giản bằng context sẵn có, chỉ spawn subagent cho phân tích phức tạp thật sự).

**Q42.** Coordinator cần truyền context từ 3 agent trước (120K+15K+3K token) sang report-generation
agent → **B** (truyền synthesis draft + structured source index map claim→URL/excerpt). Cân bằng
đầy đủ thông tin trích dẫn mà không cần full raw context.

**Q43.** Case pháp lý trích dẫn 12 tiền lệ, phân tích tuần tự mất 3 phút → **C** (coordinator spawn
song song nhiều document-analysis subagent, mỗi cái xử lý 1 tập con tiền lệ, gộp kết quả trước
synthesis). Giữ khả năng coordinator giám sát/debug (khác message-queue ẩn hay recursive hierarchy).

**Q44 / Q64.** Phân phối query cho subagent không đều, độ phức tạp đang evolving theo người dùng
mới → **A** (coordinator tự phân tích từng query động, route linh hoạt theo độ phức tạp thực tế).
Không dùng classifier train sẵn hay pattern cố định vì phân phối đang thay đổi liên tục, không dự
đoán trước được.

**Q45.** Synthesis agent mất dấu nguồn nào ủng hộ kết luận nào khi gộp — root generation gaps →
**A** (yêu cầu tất cả subagent xuất structured claim-source mapping, giữ nguyên khi merge). Sửa tại
nguồn dữ liệu, không tái dựng lại bằng semantic matching hay log phân tích hậu kỳ.

**Q54.** Sau khi `lookup_order` trả order 45 ngày tuổi, agent quyết định gọi `process_refund` hay
`escalate_to_human` như thế nào? → **C** (order details đưa vào conversation, model reasoning để
chọn hành động). Đây là agentic loop chuẩn — không có decision tree/orchestration layer cứng
route thay model.

**Q66.** Document-analysis agent phát hiện gap chủ đề nhưng pipeline cứng đã qua giai đoạn search
→ **B** (analysis agent báo gap cụ thể cho coordinator, coordinator trigger search có mục tiêu rồi
re-invoke analysis). Vòng lặp phản hồi giữa các giai đoạn, khác với việc chỉ gắn confidence score
cho người đọc tự nhận biết.

**Q106.** Coordinator gọi tuần tự web-search rồi đợi xong mới gọi document-analysis dù 2 việc độc
lập → **C** (phát cả 2 lời gọi Task tool trong CÙNG 1 response message để chạy song song). Đây là
cơ chế nền tảng của Claude Code/Agent SDK — không cần hạ tầng async ngoài (giống hệt maithienan Q18).

**Q109.** Task mở "thêm test cho codebase 200 file, không rõ ưu tiên module nào" → **C** (dùng
Glob/Grep map cấu trúc, xác định module coupling cao, lập kế hoạch ưu tiên, điều chỉnh khi phát
hiện thêm dependency). Không đọc hết 200 file trước (quá chậm) cũng không làm theo alphabet.

**Q111.** Synthesis agent báo 3 câu hỏi nghiên cứu chưa trả lời được, nhưng coordinator vẫn tiến
thẳng đến report → **C** (coordinator đánh giá gap trong synthesis output, re-delegate search với
query có mục tiêu, rồi mới re-invoke synthesis). Vòng lặp hoàn thiện chủ động thay vì chỉ ghi chú
hạn chế trong report cuối.

**Q121.** CI review 50 PR/ngày, không blocking, cân nhắc Batch API để giảm 50% chi phí → **D**
(yếu tố quyết định là feedback trễ tới 24h có còn actionable không). Vì review không blocking merge
nên latency không quan trọng bằng việc feedback vẫn còn giá trị khi đến.

**Q127.** (đề bài bị lỗi soạn thảo/garbled, nhưng 4 lựa chọn trùng Q11) → **C** (`fork_session`).
Suy luận từ cấu trúc lựa chọn giống hệt Q11, không phải lỗ hổng kiến thức — chỉ là lỗi đề của site.

**Q129.** Review PR luôn theo đúng 1 quy trình 3 bước cố định (style→security→docs) cho MỌI PR →
**A** (prompt chaining — các bước tuần tự cố định). Vì workflow LUÔN giống nhau cho mọi input, đây
là prompt-chaining kinh điển, không phải orchestrator-workers (dành cho việc phân rã ĐỘNG theo
từng input khác nhau).

**Q130.** Coordinator cần cấp context cho synthesis subagent sau khi 2 agent trước xong → **C**
(đưa toàn bộ findings của 2 agent trước trực tiếp vào prompt của synthesis subagent). Không có
callback/shared-memory tự động giữa các subagent — coordinator luôn là cầu nối truyền dữ liệu.

**Q134.** 50.000 hợp đồng, deadline 2 tuần, mẫu 500 doc cho thấy 18% lỗi đa dạng → **D** (dùng
2.000 doc mẫu qua real-time API để tìm pattern lỗi và tinh chỉnh prompt, RỒI mới batch toàn bộ
50.000 với prompt đã tối ưu). Tránh vừa batch vừa sửa nhiều vòng (tốn 24h/vòng, không kịp deadline).

**Q150.** Agent hết `max_turns` giữa chừng dispute phức tạp, cần đảm bảo LUÔN kết thúc bằng
resolution hoặc escalation → **A** (code ở tầng orchestration kiểm tra outcome sau khi loop kết
thúc — nếu chưa resolve/escalate thì tự động gọi `escalate_to_human`). Đây là safety-net nằm NGOÀI
khả năng kiểm soát của model, đảm bảo tuyệt đối bất kể vì sao loop dừng.

### D2 — Tool Design & MCP Integration (41 câu)

**Q8.** MCP server có tool refactor chuyên dụng nhưng agent vẫn dùng Write/sed vì mô tả tool quá
sơ sài → **C** (mở rộng mô tả tool giải thích khi nào nên dùng, input/output kỳ vọng). Mô tả tool
là "giao diện" duy nhất model nhìn thấy — mô tả nghèo thì tool tốt cũng không được chọn.

**Q15.** MCP tool `analyze_dependencies` vẫn bị bỏ qua, agent dùng Grep thay thế → **B** (mở rộng
mô tả + output mẫu để phân biệt rõ với Grep, vd liệt kê rõ nó trả gì mà Grep không có).

**Q19 / Q95.** Cần đảm bảo `extract_metadata` LUÔN chạy trước các tool enrichment khác → **C/A**
(ép `tool_choice` vào đúng `extract_metadata` ở LƯỢT ĐẦU TIÊN, các lượt enrichment sau xử lý bình
thường/auto). Không ép `tool_choice` cho MỌI lượt gọi trong pipeline — sẽ chặn luôn các tool khác
về sau (đây là high-risk topic được CLAUDE.md của project này lưu ý riêng).

**Q31.** 1 tool `analyze_document` nhận free-text instruction, kết quả không nhất quán 35% case →
**B** (tách thành tool chuyên biệt: `extract_data_points`, `summarize_content`,
`verify_claim_against_source`, mỗi cái có input/output contract rõ ràng). Free-text instruction
không đủ ràng buộc để model hiểu đúng ý định.

**Q32 / Q63.** Coordinator "nói" sẽ delegate nhưng không thực sự gọi subagent → **B/D**
(`allowedTools` của coordinator thiếu `"Task"` nên không thể invoke, dù vẫn mô tả được ý định bằng
lời). Cấu hình permission sai, không phải vấn đề system prompt hay context.

**Q46 / Q59 / Q125.** Phân loại lỗi MCP: thiếu param bắt buộc vs lỗi business (404 not found) vs
lỗi hạ tầng (503) → **A** (lỗi thiếu param → JSON-RPC protocol error; lỗi business/execution → tool
result với `isError: true`). Protocol error dành cho lỗi tầng GỌI (agent sửa được cách gọi); lỗi
business/hạ tầng phải trả về content có `isError:true` để agent còn ngữ cảnh quyết định retry hay
báo user (kiến thức MCP-spec quan trọng, khớp hoàn toàn với maithienan Q10).

**Q53 / Q59 / Q65 / Q93 / Q116.** Lỗi transient (timeout/503) và lỗi permanent (business rule) đều
trả về message chung chung → **B** (trả structured error kèm `retryable: false/true` + mô tả thân
thiện cho Claude dùng). Agent cần đủ thông tin để tự quyết định retry hay dừng, không phải đoán từ
text message thuần.

**Q56.** Compliance bắt buộc refund >$500 phải escalate, prompt đã rõ ràng nhưng vẫn lọt 3% → **A**
(hook `PreToolUse` chặn tool call ở tầng hệ thống khi amount > $500, không phụ thuộc model tuân
thủ). Compliance cứng phải enforce bằng code/hook, không bao giờ tin tưởng hoàn toàn vào prompt dù
viết "CRITICAL"/viết hoa.

**Q67.** Cần tích hợp Jira ticket data, đang copy-paste thủ công → **C** (dùng MCP server có sẵn
cho Jira thay vì tự build custom hoặc dùng `curl` qua Bash). Ưu tiên MCP server sẵn có, chuẩn hoá
và discoverable hơn tự viết wrapper.

**Q70.** Tool `remove_team_member` có `dry_run` nhưng agent bỏ qua bước preview 15% case → **C**
(tách thành 2 tool: `preview_remove_member` trả token xác nhận dùng 1 lần; `execute_remove_member`
BẮT BUỘC token đó). Ràng buộc bằng cấu trúc tool (token binding), không phải chỉ dặn dò qua mô tả
hay few-shot.

**Q72 / Q91.** Cần schema JSON compliance tuyệt đối cho downstream reject mọi input sai định dạng
→ **C/A** (định nghĩa tool với input schema đúng cấu trúc mong muốn, lấy dữ liệu từ `tool_use`
response). Tool use ép cấu trúc ở tầng API, đáng tin hơn prompt-instruction + parse text.

**Q74.** Nhiều loại doc, nhiều tool extraction riêng theo schema, `tool_choice: "auto"` đôi khi trả
text thay vì gọi tool → **A** (gọi phân loại trước, RỒI gọi lần 2 với `tool_choice` ép vào đúng tool
đã xác định loại doc). Vì chưa biết loại doc trước, không thể ép tool ngay từ đầu.

**Q92.** Tool `lookup_order` trả lỗi generic "execution failed" khiến agent hoặc retry vô hạn hoặc
escalate ngay không thử cách khác → **A** (trả message cụ thể theo loại lỗi + gợi ý bước tiếp theo,
vd "order not found - thử get_customer tìm theo số điện thoại"). Đúng nguyên tắc chính thức của
Anthropic tool-use doc được trích trong đề: lỗi phải nói rõ "cái gì sai + nên thử gì tiếp theo".

**Q97 / Q114 / Q116.** Lỗi transient (503/timeout) từ API ngoài → **D/B/B** (retry với exponential
backoff NGAY TRONG tool implementation cho lỗi transient; lỗi business/non-transient thì trả thẳng
cho agent kèm mô tả để agent tự quyết). Phân chia trách nhiệm rõ: lỗi transient nên tự phục hồi ở
tầng tool (agent không cần biết), lỗi cần quyết định thì đưa lên cho model.

**Q98 / (maithienan Q25).** `log_workout` nhận `measurement` tự do → sai combo 23% case → **D**
(tách `log_cardio_workout` và `log_strength_workout` — 2 tool riêng theo category). Sửa tại schema/
ranh giới tool, không vá bằng ví dụ mô tả hay enum constraint (enum vẫn cho phép combo sai giữa 2
category khác nhau).

**Q107.** Review PR 30+ file dùng `report_findings` tool, response bị cắt giữa JSON vì chạm
`max_tokens` → **C** (chia review thành nhiều API call, mỗi call phân tích 1 tập con file, gộp kết
quả). Giải quyết đúng nguyên nhân gốc (quá nhiều nội dung trong 1 response), không phải chỉ tăng
`max_tokens` (có giới hạn) hay đổi format.

**Q110 (=maithienan Q60).** Agent nối 3 MCP server, câu hỏi liên hệ thống tốn 8-10 tool call dò
dẫm → **B** (expose content catalog của mỗi server qua MCP **Resources** — không phải Tools). MCP
Resources dành riêng cho nội dung browsable/application-controlled, đọc được mà không cần
tool-call round-trip — kiến thức MCP-spec quan trọng cho domain 2.

**Q112.** Tool search trả `"Found 3 documents: ..."` dạng text, cần hỗ trợ workflow nhiều bước tiếp
theo → **A** (trả structured data có document ID + metadata). Agent cần ID có cấu trúc để tham
chiếu lại ở bước sau, text thuần không đủ tin cậy để parse.

**Q113.** 50+ connector, tool selection accuracy giảm, agent hay bỏ qua bước search hoặc chọn sai
sau khi search → **D** (`search_connectors` khi tìm thấy sẽ DYNAMICALLY thêm connector khớp vào bộ
tool khả dụng của agent — connector khởi đầu ẩn, chỉ "persist" sau khi được discover). Đây là
pattern "progressive tool disclosure" — giảm decision space thay vì chỉ tăng chất lượng mô tả.

**Q115.** Race condition giữa `get_available_slots` và `book_appointment` (15% fail vì slot bị
người khác đặt trước) → **A** (gộp thành 1 tool `find_and_book_appointment` atomic — check + book
trong 1 thao tác). Loại bỏ khoảng hở race condition bằng thiết kế tool, không phải retry hay hold
tạm 60s (vẫn còn khoảng hở).

**Q117.** Confidence score cho extraction nhưng agent tự diễn giải sai ngưỡng (23% low-confidence
vẫn được dùng, 31% high-confidence bị review thừa) → **A** (trả field + `requires_review` boolean
đã TÍNH SẴN theo ngưỡng đã kiểm chứng, kèm `review_reasons`). Đừng để model tự diễn giải số
confidence thô — tính toán logic ngưỡng ở tầng tool dựa trên dữ liệu đã test.

**Q118.** `update_game_score` nhận tên đội/ngày tự do → agent hay nhầm biệt danh, format ngày, trận
đấu lại (rematch) cùng mùa → **D** (thay 3 param bằng 1 `game_id` + tool `search_games` riêng để
tra cứu ID trước). Định danh duy nhất (ID) loại bỏ hoàn toàn nhập nhằng, hiệu quả hơn enum/regex
validation (vẫn không giải quyết được vụ rematch trùng đội/ngày).

**Q119.** 4 subagent đều có quyền truy cập TOÀN BỘ 18 tool, chọn sai tool ngoài chuyên môn → **C**
(chọn từ 18 tool thay vì 4-5 tool liên quan làm tăng độ phức tạp quyết định vượt ngưỡng tin cậy).
Nguyên nhân gốc là quá nhiều lựa chọn cùng lúc, không phải vấn đề role description hay context
window. Bài học: giới hạn tool theo đúng vai trò từng subagent.

**Q123 (=maithienan Q51).** Tool cấp phát resource chỉ trả ACK đơn giản → user approve mà không
hiểu đã duyệt gì → **A** (trả structured data: cost estimate, project, resource spec, impact
summary NGAY trong tool response). Vấn đề gốc là response nghèo thông tin, không phải thiếu bước
xác nhận (hold 60s hay flag `user_acknowledged` không tự tạo ra thông tin).

**Q124.** `search_products` trả 200+ kết quả, auto-fetch hết mọi trang gây delay 15-20s → **A**
(trả trang đầu + tổng số match + cursor cho trang tiếp). Để agent/user chủ động quyết định có cần
xem thêm không, thay vì luôn tải hết hoặc giới hạn cứng số trang.

**Q126 (=maithienan Q56).** 23% correction do đo lường phi chính thức ("a handful") bị model tự
quy đổi số cụ thể hoặc bỏ trống → **A** (few-shot minh hoạ xử lý đúng — giữ nguyên văn, không quy
đổi/không bỏ trống). Dạy hành vi cụ thể bằng ví dụ trực tiếp và rẻ hơn pattern-matching hậu kỳ.

**Q132.** `archive_file` vs `delete_file` mô tả tối giản → agent gọi nhầm delete cho "old backups"
→ **C** (mở rộng mô tả tool làm rõ use case, thêm hướng dẫn "Do not use for backup files" ngay
trong description của `delete_file`). Sửa tại mô tả tool trước khi cần đến validation phía server
hay few-shot ở system prompt.

**Q133.** `delete_contact` nhầm bản ghi trùng tên gần giống nhau, 8% bị reverse trong 24h, nhưng
flow confirm hiện tại quá nhiều bước gây friction → **D** (hiển thị các bản ghi khớp kèm trường
phân biệt, yêu cầu xác nhận 1-click đúng target trước khi xoá). Giải quyết cả độ chính xác (phân
biệt rõ record) lẫn hiệu quả (1 click, không multi-step rườm rà).

**Q139 (=maithienan Q53).** Tool tăng 4→10, accuracy giảm còn 71% vì tool chồng lấn ngữ nghĩa
(`issue_credit` vs `process_refund`) → **B** (gộp tool chồng lấn thành `resolve_compensation` với
flag `include_tracking`). Đề hỏi "structurally eliminates" — chỉ gộp tool mới thực sự xoá overlap
tại nguồn, tách sub-agent (lựa chọn A) chỉ chuyển vấn đề sang nơi khác chứ không xoá overlap.

**Q140.** Biến thể của Q139 (tool 1→7, accuracy 86%→71%) → **D** (gộp `issue_credit`+
`process_refund` thành `handle_promotions` với `action` param, gộp `check_delivery_status` vào
`lookup_order` với flag `include_tracking`). Cùng nguyên tắc gộp tool chồng lấn ngữ nghĩa như Q139.

**Q141 (=maithienan Q2).** 1 tool refund/cancel/reship dùng chung `order_id` nhưng khác param bắt
buộc, agent hay thiếu/thừa param → **B** (tách 3 tool riêng, mỗi tool chỉ định nghĩa đúng param của
operation đó). Sửa tại schema/ranh giới tool đáng tin hơn dặn dò qua few-shot khi tất cả param đều
optional.

**Q145.** Threshold $500 cho reimbursement cần "tamper-proof" bất kể agent bị prompt thế nào →
**C** (tool `process_reimbursement` TỰ ENFORCE ngưỡng nội bộ — <$500 auto-disburse, >$500 tạo
pending-approval request). Logic nghiệp vụ bắt buộc phải nằm trong chính tool, không phải param
`approved_by_manager` dựa vào model tự set trung thực hay hook chỉ sửa context (agent vẫn có thể
bỏ qua flag đó).

**Q146.** So sánh JSON structured vs text tự do cho `portfolio_value` tool → **C** (agent trích
xuất giá trị cụ thể không cần parse free-text, giảm lỗi ở bước xử lý tiếp theo). Đây là lý do cốt
lõi của structured tool output — không phải về validation tự động hay tiết kiệm token.

**Q152.** 3 MCP server (git/Jira/docs) cùng cấu hình, user yêu cầu việc cần cả 2 server → **C**
(tool của TẤT CẢ MCP server được discover lúc connect và khả dụng đồng thời cho agent). Không cần
chọn server thủ công theo turn hay routing theo prefix tên tool.

**Q155.** Tool `update_user_profile` — Claude hay thiếu/sai cấu trúc `user_id` → **B** (mô tả
param rõ ràng về format kỳ vọng, vd "UUID của user cần update (required)"). Mô tả param rõ ràng là
yếu tố quan trọng nhất giúp model điền đúng giá trị — quan trọng hơn tên param dài dòng hay chỉ
dựa vào error message sau khi sai.

### D3 — Claude Code Configuration & Workflows (29 câu)

**Q2.** Edit tool fail vì `old_string` không unique (docstring/tên biến lặp lại nhiều) → **A**
(dùng Read load cả file, chèn hàm đúng vị trí, rồi Write lại toàn bộ file). Đáng tin hơn cố kéo dài
`old_string` (30+ dòng — vẫn có thể trùng) hay `replace_all` (rủi ro thay nhầm chỗ khác).

**Q3.** Cần resume đúng session cụ thể đã đặt tên "auth-deep-dive" từ hôm qua, đã làm việc trên 3
codebase khác từ đó → **A** (`--resume auth-deep-dive` — load đúng session theo TÊN). `--continue`
chỉ lấy conversation gần nhất (đã bị codebase khác ghi đè), không đúng session cần.

**Q6.** Tìm hết caller trước khi xoá hàm bị wrapper module đổi tên khi export (calculateTax →
computeOrderTax) → **A** (đọc library + wrapper để liệt kê hết TÊN (alias) hàm được export, rồi
Grep từng tên trên toàn repo). Chỉ Grep tên gốc hoặc chỉ đọc từng file import thủ công đều bỏ sót
alias hoặc không scale với codebase lớn.

**Q13.** Caching logic trải 15 file (~8.000 dòng), cần hiểu trước khi thêm cache invalidation
trigger → **B** (phân tích import/class hierarchy tìm base cache class, Read hiểu interface, rồi
trace các implementation invalidation cụ thể). Đi từ trừu tượng (interface) xuống cụ thể, hiệu quả
hơn đọc tuần tự hết 15 file hay chỉ Grep từ khoá rời rạc.

**Q14.** Auth/authorization architecture, 800+ file, engineer mới join team → **C** (Grep tìm entry
point, đọc, rồi follow import/function call để map luồng auth dần dần). Exploration tiệm tiến theo
dấu vết code thực tế, không đọc mọi file khớp từ khoá hay chỉ hỏi user liệt kê sẵn 10-15 file.

**Q68.** Bug production rõ ràng, stack trace chỉ đúng khu vực, nhưng chưa từng làm việc với module
này → **A** (direct execution — đọc stack trace, đọc code liên quan, sửa luôn khi tìm ra root
cause). Stack trace đã đủ cụ thể, không cần plan mode cho việc rõ ràng, phạm vi hẹp.

**Q87.** Migration breaking-change (auth lib v2→v3), 45 file bị ảnh hưởng across nhiều module →
**C** (plan mode — khảo sát usage across module, map code path bị ảnh hưởng, lập chiến lược trước
khi implement). Phạm vi rộng + breaking changes phức tạp cần lập kế hoạch trước khi sửa hàng loạt.

**Q88.** 3 vấn đề formatting của PDF report tương tác lẫn nhau (column width ảnh hưởng date, date
ảnh hưởng page break) → **A** (sửa TỪNG vấn đề theo thứ tự với số đo cụ thể, verify xong mới sang
vấn đề tiếp theo). Vì các vấn đề tương tác nhau, sửa tuần tự + test sau mỗi bước tránh hiệu ứng dây
chuyền khó debug hơn là sửa cả 3 cùng lúc.

**Q89.** Tích hợp module thanh toán mới cần theo đúng pattern của 3 module mẫu — chỉ là task
one-off, đã có doc ở wiki team → **B** (dùng `@references` đưa trực tiếp code 3 module mẫu vào
prompt). Vì đây là task một lần, không cần thêm vào CLAUDE.md (option C) — đưa code cụ thể qua
`@references` chính xác và tiết kiệm hơn mô tả bằng lời (option D).

**Q90.** Monorepo 15 package, 3 file chuẩn chung (security/testing/api-conventions), mỗi package
CLAUDE.md hiện duplicate cả 3 dù chỉ cần 1-2 → **A** (dùng `@imports` trong CLAUDE.md từng package,
chỉ trỏ tới đúng standard liên quan, dựa trên hiểu biết domain của maintainer package đó). Đề bài
nhấn mạnh "maintainer tự hiểu domain requirement của mình" — gợi ý rõ cơ chế phân quyền theo từng
package thay vì tập trung hoá bằng path-glob (khác với Q138 — nơi path-glob mới là lựa chọn đúng
vì bối cảnh khác: guidance theo LOẠI FILE, không theo domain nghiệp vụ do người sở hữu tự quyết).

**Q96.** Review PR tự động miss bug cross-file (rename param, caller ở file KHÔNG đổi không được
review tới) → **A** (redesign review thành agentic task có turn limit, model tự đọc file + search
codebase, follow reference để verify). Agentic search linh hoạt hơn static dependency-graph (không
đủ sâu) hay parallel per-file pass (vẫn miss file không đổi nằm ngoài phạm vi).

**Q102.** Thêm 1 điều kiện validate ngày vào 1 hàm, 1 file → **A** (direct execution). Task đơn
giản, phạm vi rõ ràng (1 hàm, 1 file) không cần plan mode.

**Q103.** CLAUDE.md có rule format code nhưng ~15-30% vẫn sai dù đã nhấn mạnh bằng chữ hoa → **B**
(hook `PostToolUse` matcher `Edit|Write` tự động chạy Prettier sau mỗi lần sửa file). Enforcement
bằng hook đảm bảo 100%, không phụ thuộc việc model có "nhớ" tuân thủ prompt hay không.

**Q104.** Cần thêm caching layer nhưng chưa chắc mọi cân nhắc cần thiết (invalidation, layer,
consistency...) → **C** (nhờ Claude phỏng vấn ngược lại user về requirement trước khi implement).
Khi chính user cũng chưa rõ hết yêu cầu, để Claude chủ động hỏi để surface các cân nhắc quan trọng
tốt hơn là bắt đầu code luôn hay viết spec với nhiều "TBD".

**Q105.** Script migration data không xử lý đúng null value ở required field → **B** (đưa test
case cụ thể — input có null + expected output — rồi yêu cầu Claude sửa). Feedback cụ thể, có thể
verify được, hiệu quả hơn mô tả vấn đề bằng lời hay chỉ thêm "think harder".

**Q108.** Log lỗi lạ "SYNC_CONFLICT..." không biết service nào trong 12 service sinh ra → **A**
(Grep tìm text đặc trưng của message lỗi trực tiếp trong codebase). Tìm bằng chuỗi cụ thể hiệu quả
hơn đoán theo tên thư mục quy ước hay đọc README trước.

**Q120.** CLAUDE.md quy định dùng `ApiError` class nhưng Claude Code đôi khi vẫn dùng try/catch
generic, không nhất quán → **A** (chạy `/memory` để kiểm tra file nào đang thực sự được load).
Bước chẩn đoán đầu tiên hiệu quả nhất là xác nhận file có được nạp đúng không, trước khi sửa nội
dung hay tạo thêm rule path-scoped.

**Q131.** Tìm hết file import package `@company/auth` trong monorepo → **B** (Grep tìm pattern câu
lệnh import trong nội dung file). Glob chỉ khớp tên file/path, không thấy nội dung import bên
trong.

**Q137.** Cài thuật toán graph traversal phức tạp có yêu cầu hiệu năng + edge case rõ ràng, cần
iterate hiệu quả → **B** (viết test suite (hành vi, edge case, hiệu năng) TRƯỚC, yêu cầu Claude
viết code pass test, rồi chia sẻ kết quả test fail ở mỗi vòng lặp tiếp theo). Test-driven feedback
là tín hiệu cụ thể, khách quan, lặp lại được — hiệu quả hơn review thủ công bằng mô tả ngôn ngữ tự
nhiên.

**Q138.** Repo IaC (Terraform/K8s/CI-CD) mỗi phần có convention riêng, root CLAUDE.md 500+ dòng nạp
thừa context không liên quan → **D** (`.claude/rules/` với YAML frontmatter `paths:` scope theo
loại file, chỉ nạp khi đang sửa đúng file khớp pattern). Khác Q90 (phân quyền theo domain nghiệp
vụ do người dùng), đây là phân loại THEO LOẠI FILE — path-scoped rules đúng là cơ chế chính thức
cho trường hợp này.

**Q143.** Tìm mọi chỗ dùng `eval()` nguy hiểm trong codebase lớn để security scan → **D** (Grep
pattern `"eval("` trên toàn bộ file). Content search chuẩn, không cần đọc từng file theo import
chain hay liệt kê file qua Glob rồi mới đọc.

**Q144 / Q160.** Test tự sinh 55% low-value (assertion tầm thường, trùng coverage, sai convention),
cần giảm NGAY TỪ GỐC (không hậu xử lý, không thêm latency) → **A** (ghi rõ testing standard,
fixture convention, ví dụ phân biệt test giá trị vs trivial vào CLAUDE.md). Đề hỏi rõ "in the first
place"/"without introducing high latency" — lọc hậu kỳ theo coverage hay 2-phase LLM scoring đều vi
phạm ràng buộc latency hoặc không sửa gốc (giống hệt maithienan Q3/Q29).

**Q148.** Team cần 1 skill workflow migrate React→Vue dùng chung, gõ `/migrate-component`, phải
đồng bộ khi team cập nhật → **B** (`.claude/skills/migrate-component/SKILL.md` ở project root,
commit vào version control). Project-scoped + version-controlled đảm bảo mọi dev cùng dùng bản mới
nhất, khác skill cá nhân ở `~/.claude/skills/` (chỉ máy của 1 người).

**Q151.** Cùng session review code do chính Claude vừa refactor bỏ sót bug mà CI review riêng biệt
bắt được → **B** (Claude giữ context lý luận trước đó trong cùng session, ít có xu hướng phản biện
lại quyết định của chính nó). Bias tự nhất quán (self-consistency bias) — CI chạy fresh session
không mang theo "niềm tin" cũ nên khách quan hơn.

**Q153.** So sánh 2 request: đổi tên hàm đơn giản (A) vs cải thiện error handling toàn module (B),
loại nào hưởng lợi từ workflow multi-phase (analyze→propose→implement→review) rõ rệt hơn → **D**
(Request B — error handling). Task mơ hồ, nhiều quyết định thiết kế (loại lỗi nào, message ra sao,
khi nào không silently corrupt) hưởng lợi từ phân tích/đề xuất trước khi code; đổi tên hàm là cơ
học, rõ ràng, không cần workflow nhiều pha.

**Q154.** Review PR lớn tốn 20 phút/$8-12/lần do agentic loop dài, cần Claude Code TỰ enforce giới
hạn turn + budget cho mỗi lần gọi → **A** (`--max-turns 10 --max-budget-usd 2.00` trong `claude -p`).
Đã xác minh `--max-budget-usd` là flag thật (print-mode only, tính cả chi phí subagent) — khớp với
phát hiện đã verify trong báo cáo maithienan trước đó.

**Q159.** Pipeline review non-interactive dùng `--system-prompt` nhưng Claude ngừng hẳn dùng
file-reading/code-navigation tool, chỉ nhìn raw diff → **A** (đổi sang `--append-system-prompt` để
custom instruction được THÊM VÀO thay vì GHI ĐÈ toàn bộ default system prompt — vốn chứa hướng dẫn
dùng tool có sẵn). `--system-prompt` overwrite hoàn toàn built-in guidance, đây là gotcha CLI quan
trọng cần nhớ.

**Q162.** Cấu hình MCP server: 1 server chung cho cả team (venue lookup), 1 server cá nhân đang thử
nghiệm (playlist) → **B** (venue server → `.mcp.json` — project-scoped, chia sẻ qua version
control; playlist server → `~/.claude.json` — user-scoped, chỉ máy cá nhân). Đúng quy ước scope
MCP server chính thức của Claude Code.

### D4 — Prompt Engineering & Structured Output (29 câu)

**Q16.** Hợp đồng có điều khoản gốc + amendment (30 ngày → 45 ngày), model trích không nhất quán
giá trị nào → **C** (redesign schema để field bị amend chứa NHIỀU giá trị, mỗi giá trị kèm vị trí
nguồn + ngày hiệu lực). Sửa tại cấu trúc schema để phản ánh đúng thực tế nghiệp vụ (có thể có nhiều
phiên bản), không ép chọn 1 giá trị bằng prompt instruction hay validation hậu kỳ.

**Q17.** 12% extraction lỗi semantic (pass schema validation nhưng sai ý nghĩa), chỉ đủ nhân lực
review 20% → **C** (model tự xuất confidence score theo field, hiệu chỉnh ngưỡng review bằng tập
validation có nhãn). Phân bổ nguồn lực review theo tín hiệu định lượng, hiệu quả hơn random sample
hay chỉ review theo heuristic bề ngoài (format bất thường).

**Q18 / Q61 (=maithienan Q17/33).** Line item không khớp grand total (OCR lỗi hoặc model trích
sai) → **D** (thêm field `calculated_total` model tự cộng, song song `stated_total`, flag khi lệch
cho human review). Không tự động "điều chỉnh tỷ lệ" số liệu tài chính — đó là silently fabricate dữ
liệu kế toán khi chưa rõ nguyên nhân lệch.

**Q21.** Field "materials" trích không nhất quán format ("cotton blend" vs "Cotton/Polyester mix")
→ **B** (few-shot 2-3 cặp input-output hoàn chỉnh minh hoạ format chuẩn hoá). Dạy hành vi cụ thể
bằng ví dụ, hiệu quả và rẻ hơn đổi model tier hay chỉ set `temperature=0` (không giải quyết vấn đề
chuẩn hoá định dạng).

**Q22.** Field nullable nhưng model hay bịa giá trị hợp lý khi nguồn không đề cập (vd attendee_count
"500") → **D** (thêm prompt instruction: trả `null` khi thông tin không được nêu trực tiếp trong
nguồn). Bắt buộc field non-nullable (option A) sẽ LÀM TĂNG hallucination — ngược hoàn toàn mục tiêu.

**Q23.** JSON hợp lệ nhưng field bắt buộc (citations, methodology) bị rỗng dù nguồn có thông tin ở
định dạng đa dạng (inline vs bibliography...) → **C** (few-shot minh hoạ trích xuất từ nhiều cấu
trúc tài liệu khác nhau). Dạy model nhận diện đa dạng định dạng nguồn, hiệu quả hơn regex hậu xử lý
hay chỉ retry logic (không đổi được cách model đọc nguồn).

**Q24.** Retry-with-error-feedback hiệu quả với hầu hết lỗi format/type, NHƯNG kém hiệu quả nhất
với loại lỗi nào? → **C** (model trích "et al." vì danh sách đồng tác giả đầy đủ chỉ tồn tại ở
NGUỒN NGOÀI, không có trong input). Retry chỉ giúp khi thông tin đúng CÓ SẴN trong input nhưng bị
format sai — không giúp được khi thông tin vốn dĩ không tồn tại trong input.

**Q25.** Menu nhà hàng format giá/dietary info không nhất quán ("$12" vs "12.00", icon vs text) →
**A** (định nghĩa schema chặt + quy tắc chuẩn hoá format ngay trong prompt). Chuẩn hoá tại nguồn
sinh dữ liệu, không tách nhiều call riêng hay chỉ sửa ở post-processing code.

**Q26.** Enum `property_type` liên tục xuất hiện loại mới ("loft", "tiny house"...) không có trong
danh sách, 8% fail validation → **A** (thêm giá trị "other" vào enum + field
`property_type_detail` string riêng để ghi cụ thể). Giải pháp dài hạn không cần liên tục mở rộng
enum (option D — tốn công bảo trì vô hạn) hay bỏ enum hoàn toàn (mất validation).

**Q27.** Confidence >90% có accuracy 97% tổng thể, cân nhắc tự động hoá review high-confidence →
**C** (phân tích accuracy theo TỪNG loại document/field để xác nhận nhất quán across mọi segment,
không chỉ tin số tổng hợp). 97% trung bình có thể ẩn chứa segment cụ thể tệ hơn nhiều — phải kiểm
tra breakdown trước khi tự động hoá diện rộng.

**Q29.** Field `skills: string[]` không nhất quán (gộp/tách compound phrase, độ dài mảng dao động
lớn) → **C** (few-shot minh hoạ xử lý compound phrase, tiêu chí "explicitly mentioned", độ chi tiết
entry phù hợp). Dạy hành vi qua ví dụ cụ thể thay vì chỉ thêm ràng buộc số lượng cứng (option B —
không giải quyết vấn đề nhất quán ngữ nghĩa) hay chuẩn hoá hậu kỳ (không sửa gốc).

**Q61.** Xem Q18 (cùng pattern, khác số liệu %).

**Q69.** Review tool precision cao nhưng recall thấp — bug production nghiêm trọng bị bỏ lọt vì
prompt yêu cầu "chỉ báo cáo khi chắc chắn" → **A** (tách thành 2 giai đoạn: giai đoạn tìm kiếm mục
tiêu là COVERAGE tối đa (gắn confidence/severity metadata cho mọi phát hiện), giai đoạn riêng để
threshold/lọc). Tách rõ "tìm" và "lọc" giải quyết trade-off precision/recall triệt để hơn cố gắng
cân bằng cả 2 trong 1 prompt.

**Q71 / Q75.** 12% extraction fail semantic validation dù JSON luôn hợp lệ → **D/B** (khi validation
fail, gửi follow-up request kèm document gốc + kết quả extract + lỗi validation để model tự sửa).
Retry-with-validation-feedback cho model cơ hội tự sửa có căn cứ — đáng tin hơn auto-correct âm
thầm (silently fabricate) hay chỉ retry không kèm lý do lỗi.

**Q73.** Document dài 175-190K token (trong giới hạn 200K), accuracy giảm còn 71%, thông tin ở
phần cuối bị bỏ sót → **D** (tool definition + system prompt + document content cộng dồn tiệm cận
giới hạn context, làm suy giảm xử lý phần cuối tài liệu). Nguyên nhân kỹ thuật cụ thể (tổng token
tiệm cận limit), không phải "attention span" mơ hồ hay số field trong schema.

**Q82.** Response luôn mở đầu bằng "Certainly!"/"I'd be happy to help!" dù đã sâu trong hội thoại →
**A** (system prompt instruction cụ thể liệt kê cụm từ cần tránh). Giải pháp trực tiếp và đơn giản
nhất cho vấn đề style/tone thuần túy.

**Q84.** System prompt 2.800 token có hướng dẫn chi tiết dạng văn bản, sau 12 turn bị bỏ qua dần →
**B** (thay hướng dẫn dài dòng bằng few-shot minh hoạ cụ thể sự khác biệt giữa các mức độ). Ví dụ
cụ thể "bám" tốt hơn hướng dẫn trừu tượng dài khi hội thoại kéo dài — khác với Q80 (nơi chèn lại
reminder định kỳ mới là giải pháp đúng, vì bối cảnh khác: system prompt ngắn hơn, vấn đề là "quên"
chứ không phải "hướng dẫn không đủ cụ thể để bám").

**Q85.** 12% extraction "high-confidence" (>85%) vẫn sai (lỗi từ bảng so sánh, phụ lục biến thể
khác nhau...) → **D** (stratified random sampling review định kỳ % cố định trên high-confidence
extraction, đo lường error rate theo thời gian). Cần đo lường LIÊN TỤC và phát hiện pattern mới,
không chỉ hạ ngưỡng confidence (tốn thêm review) hay heuristic rule cứng (chỉ bắt được loại lỗi đã
biết).

**Q91.** Xem D2 (structured tool use cho resume extraction).

**Q94.** Model bỏ sót nhánh điều kiện/error-path chưa test bên trong hàm ĐÃ có test (dù phát hiện
đúng hàm hoàn toàn chưa test) → **D** (few-shot minh hoạ cặp: code có nhánh chưa test + review
comment chỉ đích danh test case còn thiếu). Đề yêu cầu "without overcomplicating the pipeline" —
multi-pass pipeline (option A) là overengineering bị loại; few-shot dạy hành vi cụ thể rẻ và trực
tiếp hơn.

**Q126.** Xem D2 (giữ nguyên văn đo lường phi chính thức).

**Q128.** Review 1 prompt cho cả security/API/business-logic, thêm few-shot logic bug thì recall
logic tăng nhưng API design recall giảm (trade-off qua lại) → **B** (tách thành nhiều prompt tập
trung riêng biệt theo từng loại vấn đề, mỗi cái có ví dụ riêng, gộp kết quả sau). Giải quyết
nguyên nhân gốc — 1 prompt/1 bộ few-shot không thể tối ưu đồng thời nhiều mối quan tâm khác biệt.

**Q136.** Meeting transcript dài (>60 phút) accuracy giảm còn 68% dù vẫn trong context window →
**C** (chia transcript dài thành chunk, extract riêng từng chunk, gộp + dedupe kết quả). Pattern
map-reduce cho tài liệu dài với thông tin rải rác, hiệu quả hơn chỉ thêm few-shot hay tóm tắt trước
(mất chi tiết).

**Q142 (=maithienan Q39).** System prompt fitness coach nhiều nhánh if-else theo từ khoá, bỏ sót
tín hiệu ngầm (thuật ngữ kỹ thuật) khi user không khai báo rõ trình độ → **C** (thay phần lớn
nhánh if-else bằng nguyên tắc chung "match độ sâu giải thích theo thuật ngữ user dùng", chỉ giữ
nhánh an toàn/y tế bắt buộc). Nguyên tắc chung tổng quát hoá tốt hơn danh sách if-else brittle
không bao quát hết case chưa liệt kê.

**Q149 (=maithienan Q12, đã SỬA LẠI).** Schema `pros`/`cons` (array) + `overall_sentiment` (enum)
— review ngắn bị bịa pros/cons; review mỉa mai bị gán sentiment tuỳ tiện → **D** (cho phép MẢNG
RỖNG hợp lệ cho pros/cons — không phải optional/nullable — và chỉ thêm "unclear" vào enum, KHÔNG
thêm "neutral"). Site này đồng thuận với phân tích đã tự sửa trong báo cáo maithienan trước đó:
empty-array (field luôn có, có thể rỗng) khác optional (có thể bỏ hẳn field); "neutral" là thừa vì
bài toán là "không xác định được" (ambiguous/sarcasm) chứ không phải "trung tính thật sự".

**Q158.** 35% finding của automated review là false positive theo pattern nhất quán (vi phạm
convention riêng của team) → **D** (few-shot ví dụ code đã annotate phân biệt pattern chấp nhận
được vs lỗi thật trong từng category). Ví dụ cụ thể giúp model TỔNG QUÁT HOÁ phán đoán cho pattern
mới chưa gặp — hiệu quả hơn viết spec đầy đủ dài dòng (không scale) hay lọc keyword hậu kỳ (brittle).

**Q161.** Cần duy trì tone/hành vi nhất quán XUYÊN SUỐT mọi tương tác (không riêng 1 hội thoại) →
**D** (định nghĩa trong `system` prompt — top-level param). Đây là kiến thức nền tảng API: system
prompt không nằm trong `messages` và không nên đặt ở message đầu tiên hay biến môi trường.

### D5 — Context Management & Reliability (31 câu)

**Q5.** Agent explore rendering 25 phút, bắt đầu trả lời chung chung "typical rendering patterns"
thay vì tên class cụ thể đã khám phá (dấu hiệu context drift), giờ cần chuyển sang chủ đề physics
liên quan → **B** (tóm tắt findings về rendering, spawn subagent MỚI cho physics kèm summary đó
làm initial context). Không `/clear` xoá sạch (mất liên kết rendering↔physics cần thiết) cũng
không tiếp tục trong context đã suy giảm.

**Q7.** Session explore 30+ phút, agent trả lời không nhất quán về structure đã bàn trước đó →
**C** (agent duy trì file scratchpad ghi finding chính, tham chiếu lại cho câu hỏi sau). Giải pháp
đơn giản, trực tiếp — không cần clear context định kỳ (mất thông tin hữu ích) hay đổi model tier
(không giải quyết vấn đề context accumulation).

**Q9.** Investigation 15-file payment module, sau 8 file response kém chính xác dần → **B** (spawn
subagent explore các file còn lại, có summary pattern đã phát hiện làm context ban đầu). Subagent
mới có context "sạch" + đủ thông tin cần thiết, hiệu quả hơn chỉ Grep thêm hay clear+restart.

**Q12.** Session resume hợp lệ nhưng 3/12 file đã bị merge thay đổi qua đêm → **C** (resume session
và báo CỤ THỂ cho agent những file nào đã đổi để re-analyze có mục tiêu). Cân bằng hiệu quả (không
đọc lại cả 12 file) và độ chính xác (không bỏ qua thay đổi thực tế).

**Q47.** Dispute 25+ turn, cần escalate nhưng human agent KHÔNG có quyền truy cập transcript →
**D** (structured summary: customer ID, root cause, refund amount, recommended action). Không gửi
transcript đầy đủ (human không truy cập được/quá dài để đọc nhanh) — nén thành thông tin actionable.

**Q48.** `lookup_order` trả 40+ field mỗi lần, tool output chiếm phần lớn context, còn 2 order nữa
cần tra → **D** (trích riêng field liên quan đến return — items, purchase date, return window,
status — bỏ chi tiết dư thừa từ response đã có). Chủ động dọn context TRƯỚC khi lookup thêm, không
đợi context đầy mới xử lý.

**Q49.** Customer bực bội, đã "giải thích 2 lần", đòi gặp người thật NGAY, agent CHƯA điều tra gì →
**A** (escalate ngay lập tức). Khách đã tự báo cáo 2 lần thử không
thành + yêu cầu tường minh gặp người thật → thoả tiêu chí escalation rõ ràng (khách yêu cầu +
agent chưa có gì để giải quyết ngay). Khác Q55 — nơi investigation ĐÃ xác nhận vấn đề đơn giản/giải
quyết được ngay, nên ưu tiên đề nghị giải quyết trước khi escalate.

**Q50.** 4 cách trigger escalation khác nhau → **A** (escalate khi: khách yêu cầu người thật, HOẶC
cần policy exception, HOẶC agent không tiến triển được). Tiêu chí tường minh/hành vi cụ thể, không
phải đếm số lần tool fail (option B — không phản ánh đúng bản chất vấn đề) hay sentiment analysis
(option D — dựa cảm xúc, không đáng tin bằng tiêu chí khách quan).

**Q51.** Agent phát hiện giữa chừng cần approval vượt quyền hạn → **B** (soạn structured handoff —
customer info, order info, vấn đề đã xác định — TRƯỚC khi gọi `escalate_to_human`). Cung cấp đủ
ngữ cảnh actionable cho human, không chỉ forward message gốc của khách hay toàn bộ history thô.

**Q52.** Đã đủ thông tin xác nhận refund eligible nhưng `process_refund` timeout ở backend → **D**
(giải thích billing + xác nhận eligible + thừa nhận lỗi hệ thống + đề nghị escalate hoặc thử lại
sau). Cân bằng first-contact-resolution với minh bạch về lỗi thật — không giả vờ đã xử lý xong
(option C) hay escalate ngay khi vẫn còn cách xử lý khác (option A).

**Q55.** Customer mệt mỏi đòi gặp người thật, NHƯNG `lookup_order` đã xác nhận return đơn giản/đủ
điều kiện xử lý NGAY → **C** (ghi nhận cảm xúc, thông báo có thể giải quyết ngay, mời chọn xử lý
luôn hoặc escalate). Đối lập với Q49 — ở đây agent ĐÃ có đủ thông tin để giải quyết ngay, escalate
vội sẽ phản tác dụng first-contact-resolution.

**Q57.** 3 vấn đề riêng biệt qua 45 turn, khách hỏi lại vấn đề cũ ở turn 48, gần chạm context limit
→ **A** (extract + persist structured issue data — order ID, amount, status — vào context layer
riêng). Structured state cho dữ liệu CÓ CẤU TRÚC, RÕ RÀNG cần truy xuất chính xác — khác pattern
progressive-summarization (dùng khi cần RECALL nội dung tự do/narrative, xem Q76/Q79).

**Q58.** Xác minh danh tính nhiều bước, sau câu hỏi thứ 3 agent hỏi lại tên như chưa từng hỏi →
**D** (conversation history KHÔNG được gửi lại trong các request tiếp theo). Nguyên nhân kỹ thuật
gốc — API stateless, phải gửi đủ history mỗi lần gọi.

**Q60.** Khách quay lại sau 4 giờ, session cũ 32 turn có "Status: Pending Refund" → **A** (bắt đầu
session MỚI, inject structured summary của tương tác trước — loại vấn đề, bước đã xử lý, trạng thái
hiện tại — rồi tool call mới khi cần). Session mới + context cô đọng hiệu quả hơn resume nguyên
32-turn history (dư thừa) hay chỉ dựa vào tool để re-fetch mà không có tóm tắt định hướng.

**Q62.** Investigation 45-file module, sau 8 file response kém chính xác → **B** (spawn subagent
điều tra câu hỏi cụ thể trong khi main agent điều phối và giữ hiểu biết tổng quan). Cùng pattern
với Q9 — phân rã việc explore sâu ra subagent, giữ main agent "sạch" để tổng hợp.

**Q76.** Conversation history 85.000 token qua nhiều buổi thảo luận sách, hỏi lại kết luận cũ bị
trả lời chung chung → **D** (progressive summarization — block cũ thay bằng tóm tắt trích rõ kết
luận/quyết định/chủ đề lặp lại, giữ nguyên văn phần gần đây). Pattern chuẩn cho RECALL nhiều chủ đề
đã đóng trong hội thoại rất dài.

**Q77 / Q99.** Claude không nhớ thông tin đã nói ở turn trước dù hội thoại ngắn → **A** (app không
gửi lại các message trước đó trong `messages` array — API stateless không tự lưu history). Nguyên
nhân kỹ thuật cơ bản nhất, không phải do context window đầy hay cần session_id đặc biệt.

**Q78.** ⚠️ Xem mục 1 (Tổng quan) — persona compliance giảm từ turn 7, hội thoại chỉ ~2000 token →
**C** (system prompt chỉ được gửi ở request ĐẦU TIÊN — lỗi implementation, không gửi lại mỗi lần
gọi). **Đã sửa lại so với kết luận cũ ở báo cáo maithienan** (từng chọn D "accumulated responses
diluting" — cách diễn đạt mơ hồ, không kiểm chứng được). Nhất quán với Q77/Q99 cùng site: nguyên
nhân gốc luôn là vi phạm tính stateless của API.

**Q79 (=maithienan Q55).** Sliding window 25 message pairs làm mất context chủ đề/preference cũ →
**D** (thay sliding window bằng hybrid: tóm tắt phần cũ, giữ verbatim phần gần đây).

**Q80 (=maithienan Q1).** Guideline tuân thủ tốt turn 1-15, trôi dần turn 25-30, hội thoại chỉ
30K/200K token (chưa chạm limit) → **B** (chèn user-message nhắc lại guideline quan trọng tại
breakpoint tự nhiên, đặc biệt trước request phức tạp). Regenerate-until-conform (option D) tốn
latency/cost gấp nhiều lần và không sửa nguyên nhân gốc.

**Q81 (=maithienan Q49).** Webhook báo ship giữa lúc user đang chat, muốn assistant tự nhiên đề
cập ở response kế tiếp → **D** (thêm shipping status vào system prompt TRƯỚC lượt gọi API kế tiếp,
khi user thực sự nhắn tiếp). Không tạo message giả danh user (option A) — xen ngang tự nhiên chat
UI.

**Q83.** Request mơ hồ ("book a venue for the party"), hỏi trung bình 4.2 câu clarify khiến 35% bỏ
cuộc, nhưng giảm hỏi thì recommendation sai preference → **A** (nêu rõ giả định dựa trên history,
tiến hành recommendation kèm mời sửa, CHỈ hỏi clarify cho hành động không thể đảo ngược như xác
nhận booking). Cân bằng tốc độ và độ chính xác bằng cách phân biệt rõ hành động reversible vs
irreversible.

**Q86.** Hội thoại phân tích paper academic >60K token, câu hỏi cần số liệu chính xác (sample size,
p-value) bị trả lời hedge/sai sau khi đã tóm tắt → **D** (duy trì database có cấu trúc các fact
quan trọng từ mỗi paper — số liệu, phương pháp — retrieve khi câu hỏi cần độ chính xác cao). Dữ
liệu numeric quan trọng cần lưu structured, không tin vào tóm tắt tự do (dù có "instruct kỹ hơn").

**Q99.** Xem Q77 (cùng pattern).

**Q100.** Câu đầu tiên mơ hồ ("Set up my focus music") có 3 nghĩa khả dĩ → **A** (hỏi 1 câu clarify
về loại hành động: play ngay hay config sau). Với action-type hoàn toàn không rõ (khác mức độ chi
tiết), 1 câu hỏi trực tiếp về loại hành động là cần thiết trước khi làm bất cứ gì.

**Q101.** Assistant hỏi dồn 3 câu clarify 1 lúc → 40% bỏ cuộc → **C** (system prompt hướng dẫn nêu
giả định rõ ràng từ context sẵn có, đề nghị điều chỉnh nếu sai). Giảm friction bằng cách chủ động
giả định + minh bạch, khác với chỉ giới hạn 1 câu hỏi/turn (option A — vẫn có thể tích luỹ nhiều
turn hỏi liên tục) hay preprocessing classifier riêng (phức tạp không cần thiết).

**Q122.** Session dinner-party 78.000 token có cả dữ kiện quan trọng (dị ứng hải sản, khẩu phần, ý
nghĩa thuật ngữ riêng của user) lẫn thảo luận chung chung → **D** (trích structured data quan trọng
riêng — dị ứng, khẩu phần, thuật ngữ tự định nghĩa — tóm tắt phần thảo luận chung, giữ nguyên văn
phần gần đây). Kết hợp cả 2 kỹ thuật (structured extraction cho fact cứng + progressive
summarization cho phần mềm) — phù hợp khi có CẢ HAI loại thông tin cùng lúc.

**Q135.** Deploy system prompt mới, user hội thoại đa phiên nhiều tuần thấy assistant mâu thuẫn với
phát biểu cũ + đổi tone → **D** (version hoá system prompt, gắn mỗi hội thoại với version tại thời
điểm bắt đầu; chỉ áp dụng update cho hội thoại MỚI). Giữ nhất quán trong 1 hội thoại xuyên suốt
vòng đời của nó — không hồi tố thay đổi vào hội thoại đang diễn ra.

**Q147.** Context bị chiếm bởi RAG result tích luỹ từ mọi query trước, đẩy lùi conversation history
→ **B** (sliding window RIÊNG cho RAG result — chỉ giữ 2-3 query gần nhất — trong khi bảo toàn toàn
bộ conversation history). Phân biệt rõ 2 loại nội dung khác bản chất (RAG context có thể "hết hạn"
theo query mới, conversation history thì cần giữ liên tục).

**Q156.** Story elements bền vững (nhân vật, plot, world rules) và brainstorming ephemeral trộn lẫn,
sau 40+ turn assistant "quên" đặc điểm nhân vật đã thiết lập → **A** (tách riêng "story bible" giữ
cố định ở đầu context, chỉ trim/summarize phần brainstorming). Phân loại nội dung theo độ bền vững
để áp dụng chiến lược retention khác nhau cho từng loại.

**Q157 (họ hàng maithienan Q13).** User liên tục refine preference giữa hội thoại ("giờ đổi
condo thay vì house"), assistant đôi khi vẫn dùng preference CŨ dù update đã có trong history (dù
context mới dùng 35% capacity — không phải vấn đề context đầy) → **D** (structured state object
lưu preference hiện tại, cập nhật khi có thay đổi, đưa vào MỌI request). Giá trị MUTABLE cần ghi đè
rõ ràng bằng structured state — không tin vào việc model tự "nhặt" đúng bản cập nhật mới nhất từ
history dài dù vẫn nằm trong context.
