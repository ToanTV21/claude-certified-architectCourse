# CCA-F Study Plan — Chiến lược tổng hợp kiến thức & luyện đề

> Chưa biết đọc file nào trước? Xem [README.md](README.md) — bản đồ thứ tự đọc của cả folder.

> Ngày lập: 2026-08-14 · Mục tiêu: đạt **720/1000** trước 2026-09-30 (cuối Q3).
> Quỹ thời gian còn lại: **~6.5 tuần** → plan chia 4 tuần chính + 2 tuần buffer/ôn nước rút.

---

## 0. Nguyên tắc chiến lược (đọc trước khi làm bất cứ gì)

1. **Không học lại course từ đầu.** Course FPT dạy *cách dùng* Claude API (RAG, embeddings,
   streaming, vision...) — nhưng đề CCA-F là **scenario-based về thiết kế hệ thống agent**.
   Phần giao nhau chỉ khoảng 40%. Nguồn học chính giai đoạn này là
   [references.md](references.md), KHÔNG phải `sessions/*/notes.md`.
2. **Loại trừ trước khi học thêm.** Danh sách "chủ đề CHẮC CHẮN KHÔNG thi" ở cuối
   [references.md](references.md) (fine-tuning, vector DB, streaming/SSE, vision, tokenization,
   rate limit, hosting MCP server...) — gặp trong course thì đọc lướt, không đào sâu.
3. **Học theo trọng số domain, không học theo thứ tự session.** Domain 1 (27%) + Domain 3 (20%)
   + Domain 4 (20%) = **67% điểm số**. Sai lệch effort ở đây tốn điểm nhiều nhất.
4. **Luyện đề là hoạt động học, không phải hoạt động kiểm tra.** Mỗi câu sai phải kết thúc bằng
   1 entry trong [wrong-answers.md](wrong-answers.md) — đây là thứ quyết định điểm thi thật.
5. **Học meta-pattern, không học fact rời rạc.** 18 meta-pattern ở PHẦN III của
   [references.md](references.md) là công cụ mạnh nhất để xử lý câu hỏi lạ. Thuộc 18 pattern này
   giá trị hơn thuộc 100 flashcard.

---

## 1. Bản đồ trọng số → phân bổ effort

| Domain | Trọng số | Số câu/60 | Effort đề xuất | Nguồn ôn chính |
|--------|----------|-----------|----------------|----------------|
| 1. Agentic Architecture & Orchestration | 27% | **16** | 30% | references.md Ch.3, 8, 9, 10 + Lĩnh vực 1 |
| 2. Tool Design & MCP Integration | 18% | **11** | 18% | Ch.2, 4, 13 + Lĩnh vực 2 |
| 3. Claude Code Configuration & Workflows | 20% | **12** | 22% | Ch.5 + Lĩnh vực 3 |
| 4. Prompt Engineering & Structured Output | 20% | **12** | 20% | Ch.6, 7 + Lĩnh vực 4 |
| 5. Context Management & Reliability | 15% | **9** | 10% | Ch.11, 12 + Lĩnh vực 5 |

**Cách dùng bảng này:** mọi mock exam tự sinh trong project đều phải theo đúng phân bổ
16/11/12/12/9. Chấm điểm cũng tách theo domain — biết mình yếu domain nào quan trọng hơn biết
tổng điểm bao nhiêu.

### Ước lượng điểm quy đổi
Thang 100–1000, pass 720 → cần đúng khoảng **~72%** ≈ **43–44/60 câu**.
Ngưỡng an toàn tự đặt: **48/60 (80%)** ở mock exam mới nên đi thi thật.

---

## 2. Lộ trình 4 tuần

### Tuần 1 — Tổng hợp & vá lỗ hổng kiến thức (consolidation)

| Ngày | Việc | Output |
|------|------|--------|
| D1 | Đọc lại toàn bộ [references.md](references.md) PHẦN I (Ch.1–13), gạch chân điểm chưa chắc | danh sách "điểm mù" |
| D2 | Đọc PHẦN II (5 lĩnh vực) + PHẦN III (18 meta-pattern). Học thuộc 18 pattern | tự viết lại 18 pattern không nhìn tài liệu |
| D3 | Diagnostic test: làm **Mock Set 1** (60 câu) trong 120 phút, không tra cứu | điểm baseline theo domain |
| D4 | Phân tích bài D3: mọi câu sai → entry trong wrong-answers.md, ghi rõ *vì sao bẫy hoạt động* | wrong-answers.md có entry thật |
| D5 | Vá lỗ hổng: 2 domain điểm thấp nhất → đọc lại chương tương ứng + tự viết tóm tắt bằng lời của mình | bổ sung cheat-sheet.md |
| D6 | Luyện web ngoài: [claudecertificationguide.com](https://claudecertificationguide.com/) — học theo module, không phải làm quiz | ghi khái niệm mới vào references.md |
| D7 | Ôn flashcards toàn bộ (45 câu) + review wrong-answers tuần này | — |

> **Lưu ý các session còn dở** (`00`, `04`, `05`, `06`, `08` theo [README](../README.md)):
> chỉ có `04` (Tool Use) và `08` (Claude Code) là **có trọng số thi cao** → hoàn thành 2 cái này.
> `05` (RAG/embeddings) và `06` (vision/prompt caching/citations) nằm gần như trọn trong danh sách
> "không thi" → hạ ưu tiên xuống cuối, làm nếu còn thời gian ở tuần buffer.

### Tuần 2 — Đào sâu Domain 1 + 3 (47% điểm số)

| Ngày | Việc |
|------|------|
| D8–D9 | **Domain 1**: agentic loop (`stop_reason`), hub-and-spoke, subagent context isolation, `Task` tool, hooks deterministic vs prompt probabilistic, fixed pipeline vs dynamic decomposition. Tự vẽ 1 sơ đồ coordinator/subagent + luồng lỗi |
| D10 | Drill **20 câu chỉ Domain 1** (tự sinh) — mục tiêu ≥85% |
| D11–D12 | **Domain 3**: phân cấp CLAUDE.md, `@path` import, `.claude/rules/` + `paths` glob, skill vs command, `context: fork`, planning mode, `-p`/`--print` CI, `--resume`/`fork_session`. **Thực hành trong chính repo này** — tạo thử 1 `.claude/rules/*.md` có `paths` glob và quan sát khi nào nó nạp |
| D13 | Drill **20 câu chỉ Domain 3** — mục tiêu ≥85% |
| D14 | **Mock Set 2** (60 câu, 120 phút) + phân tích sai |

### Tuần 3 — Domain 2 + 4 + 5, và luyện web ngoài

| Ngày | Việc |
|------|------|
| D15–D16 | **Domain 4**: few-shot vs explicit criteria (bẫy hay gặp), `tool_use`+JSON Schema (cú pháp ≠ ngữ nghĩa), nullable/enum "other"/"unclear", validation + retry-with-feedback, Batch API (50%, ≤24h, không tool multi-turn, `custom_id`) |
| D17 | **Domain 2**: mô tả tool = cơ chế lựa chọn chính, đổi tên tool để khử chồng lấn, lỗi MCP có cấu trúc (`isError`, `isRetryable`, 4 nhóm lỗi), `.mcp.json` vs `~/.claude.json`, built-in tools |
| D18 | **Domain 5**: case-facts block, cắt gọn tool result qua `PostToolUse`, primacy/recency, scratchpad file, escalation signals đáng tin vs không đáng tin, provenance & conflicting data |
| D19 | Chạy 2 web thi thử: [guided.maithienan.com](https://guided.maithienan.com/certifications/ccar-f) và [thangldw.github.io](https://thangldw.github.io/apps/cert/ccar-f/) |
| D20 | Chạy web thứ 3: [ccar-architect-foundations.vercel.app](https://ccar-architect-foundations.vercel.app/) |
| D21 | **Mock Set 3** + phân tích. So sánh điểm domain giữa Set 1/2/3 |

### Tuần 4 — Nước rút & mô phỏng điều kiện thi

| Ngày | Việc |
|------|------|
| D22 | Đọc lại TOÀN BỘ wrong-answers.md — đây là buổi ôn giá trị nhất |
| D23 | Làm lại các câu đã sai (chỉ câu sai) từ Set 1–3 → câu nào vẫn sai lần 2 = lỗ hổng khái niệm thật, phải đọc lại chương gốc |
| D24 | **Mock Set 4** — điều kiện thi thật: 120 phút, không tra cứu, không nghỉ giữa chừng |
| D25 | Phân tích + drill riêng domain yếu nhất còn lại |
| D26 | Đọc lướt cheat-sheet + 18 meta-pattern + flashcards (nhanh, không sâu) |
| D27 | **Mock Set 5** — kiểm tra ngưỡng ≥48/60. Chưa đạt → dùng tuần buffer |
| D28 | Nghỉ nhẹ, chỉ đọc lại 18 meta-pattern + wrong-answers |

### Tuần 5–6 (buffer)
- Chưa đạt 48/60 → lặp lại chu kỳ "drill domain yếu → mock → phân tích" cho tới khi đạt.
- Đạt rồi → đăng ký thi, giữ nhịp 1 mock/tuần để không nguội.

---

## 3. Quy trình luyện đề chuẩn (áp dụng cho MỌI mock exam)

```
1. LÀM MÙ    — 120 phút, không tra cứu, không dừng giữa chừng, ghi đáp án ra giấy/file riêng
2. TỰ CHẤM   — chấm cả bài, tính điểm TỔNG và điểm TỪNG DOMAIN
3. GHI LOG   — cập nhật mock-exam-log.md (điểm 5 domain + tổng)
4. PHÂN TÍCH — mỗi câu sai → 1 entry wrong-answers.md, bắt buộc trả lời 3 câu:
                 · Đáp án đúng đúng ở chỗ nào?
                 · Đáp án tôi chọn sai ở chỗ nào? (bẫy nào đã hiệu quả với tôi?)
                 · Nó thuộc meta-pattern nào trong 18 pattern của references.md PHẦN III?
5. VÁ       — nếu 1 domain < 70% → đọc lại chương gốc + drill riêng domain đó trước mock kế tiếp
```

**Chống học vẹt đáp án:** không làm lại nguyên 1 mock set trong vòng 10 ngày. Làm lại sớm chỉ
luyện trí nhớ vị trí đáp án, không luyện lý luận.

**Cách đọc câu hỏi trong lúc thi (checklist 4 bước):**
1. Xác định câu này thuộc domain nào → gọi meta-pattern tương ứng.
2. Loại ngay đáp án **overengineering** (thêm classifier riêng, thêm layer routing, thêm vector DB,
   train model mới) — đây là mẫu sai phổ biến nhất trong guide.
3. Loại đáp án dùng **prompt/dặn dò** khi câu hỏi yêu cầu **đảm bảo tuyệt đối** (tiền, thứ tự, an toàn)
   → đáp án đúng là code/hook/thiết kế tool.
4. Còn 2 đáp án → chọn cái **sửa tại nguồn** (upstream) thay vì **xử lý hậu kỳ** (downstream).

---

## 4. Nguồn luyện đề

### Nguồn nội bộ (tự sinh trong repo này)
| File | Nội dung | Trạng thái |
|------|----------|-----------|
| [practice-questions.md](practice-questions.md) | 10 câu warm-up mức định nghĩa | ✅ có sẵn |
| `mock-exams/set-01.md` … `set-05.md` | 5 bộ đề đầy đủ 60 câu, đúng phân bổ 16/11/12/12/9 | ⬜ sinh dần theo lịch |
| [mock-exam-log.md](mock-exam-log.md) | Bảng theo dõi điểm theo domain qua từng lần thi | ✅ có sẵn |
| [wrong-answers.md](wrong-answers.md) | Log câu sai — tài sản ôn thi quan trọng nhất | ✅ có sẵn |

> Sinh 1 bộ đề mới bằng cách yêu cầu: *"sinh Mock Set N vào exam-prep/mock-exams/, 60 câu
> scenario-based, phân bổ 16/11/12/12/9 theo domain, đáp án + giải thích ẩn trong `<details>`"*.

### Nguồn ngoài
| Site | Dùng để làm gì | Khi nào |
|------|----------------|---------|
| [claudecertificationguide.com](https://claudecertificationguide.com/learn/2-tool-design-mcp/2-1-tool-schema-design) | **Học theo module** (có cấu trúc theo đúng 5 domain) — dùng để vá lỗ hổng, không phải để luyện tốc độ | Tuần 1–3, khi cần đào sâu 1 domain |
| [guided.maithienan.com](https://guided.maithienan.com/certifications/ccar-f) | Bộ câu hỏi có hướng dẫn | D19 |
| [thangldw.github.io](https://thangldw.github.io/apps/cert/ccar-f/) | Quiz app, luyện phản xạ | D19 |
| [ccar-architect-foundations.vercel.app](https://ccar-architect-foundations.vercel.app/) | Mock exam mô phỏng | D20 |
| [Guide gốc (VN)](https://github.com/ToanTV21/claude-certified-architect/blob/main/guide_vi.md) + `practical_test_en.html` trong repo đó | 60 câu bổ sung + bài luyện dạng HTML giống thi thật | Tuần 3–4 |

⚠️ **Nguồn ngoài là nguồn cộng đồng, không phải đề chính thức.** Gặp mâu thuẫn với
[references.md](references.md) → tin references.md (bám guide gốc). Nếu nguồn ngoài đúng và
references.md thiếu → bổ sung vào references.md rồi commit.

---

## 5. Chỉ số theo dõi (định nghĩa "sẵn sàng thi")

Đủ **cả 4** điều kiện sau mới đăng ký thi:

- [ ] Mock exam gần nhất ≥ **48/60 (80%)**
- [ ] **Không domain nào** < **70%** ở 2 mock liên tiếp
- [ ] Viết lại được **18 meta-pattern** (PHẦN III references.md) không cần nhìn tài liệu
- [ ] Các câu trong wrong-answers.md làm lại đúng **≥90%**

---

## 6. Bẫy đã biết — kiểm tra kỹ khi gặp trong đề

Rút gọn từ PHẦN III references.md, xếp theo tần suất xuất hiện:

| # | Bẫy | Đáp án đúng luôn là |
|---|-----|---------------------|
| 1 | Cần đảm bảo tuyệt đối (tiền/thứ tự/an toàn) | Hook / precondition bằng code / thiết kế tool 2 bước — **KHÔNG** phải "cải thiện prompt" |
| 2 | Agent chọn nhầm tool | Sửa **tên + mô tả tool** — không thêm routing layer/classifier |
| 3 | Batch API | Chỉ cho tác vụ **không chặn**; không bao giờ cho PR-blocking |
| 4 | Claude Code trong CI | `-p` / `--print` — `--batch`, `CLAUDE_HEADLESS` là bẫy không tồn tại |
| 5 | Thành viên mới không thấy hướng dẫn | CLAUDE.md đặt nhầm ở cấp **user**, phải là **project** |
| 6 | Quy ước trải rộng nhiều thư mục | `.claude/rules/` + `paths` glob — không phải CLAUDE.md cấp thư mục |
| 7 | Escalation | Tiêu chí tường minh + few-shot — **không** dùng sentiment / self-rated confidence |
| 8 | Review 10+ file 1 lượt kém nhất quán | Per-file pass + integration pass — không phải model to hơn |
| 9 | Lỗi trong multi-agent | Trả **context lỗi có cấu trúc** — không im lặng nuốt lỗi, không hủy cả workflow |
| 10 | Dữ liệu 2 nguồn mâu thuẫn | Giữ **CẢ HAI** + gắn cờ `conflict_detected` — không tự chọn 1 giá trị |
| 11 | Model "quên" đầu hội thoại | API **stateless**, app phải gửi lại toàn bộ `messages` |
| 12 | Skill cá nhân trùng tên skill nhóm | Âm thầm che khuất bản của nhóm → đặt tên khác |
| 13 | Context quá lớn ở bước tổng hợp | Sửa **agent thượng nguồn** trả structured data — không thêm agent tóm tắt |
| 14 | Yêu cầu người dùng mơ hồ | Nêu giả định tường minh rồi tiến hành + mời đính chính |
| 15 | Skill output dài dòng làm nhiễu session | `context: fork` |

---

## 7. Ghi chú vận hành

- Mọi thay đổi trong `exam-prep/` → `git add` + `commit` + `push` ngay (theo CLAUDE.md rule 6b).
- Kiến thức mới học được từ nguồn ngoài → bổ sung vào [references.md](references.md), không tạo file rời.
- Fact nhỏ dễ quên → [flashcards.md](flashcards.md); cú pháp/tham số → [cheat-sheet.md](cheat-sheet.md).
