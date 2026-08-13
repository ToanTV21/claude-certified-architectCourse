# Session 05: RAG and Agentic Search

## Lessons trong section này
- [x] Introducing Retrieval Augmented Generation
- [x] Text chunking strategies
- [x] Text embeddings
- [x] The full RAG flow
- [x] Implementing the RAG flow
- [x] BM25 lexical search
- [ ] A Multi-Index RAG pipeline

## Key Concepts

### 1. Introducing Retrieval Augmented Generation (RAG)
**RAG** giải quyết bài toán: document quá lớn (vd 800 trang) không thể nhét hết vào 1 prompt.

- **Option 1 — Stuff toàn bộ document vào prompt:** đơn giản nhưng có giới hạn:
  - Có hard limit về độ dài prompt (context window)
  - Prompt càng dài, Claude càng kém hiệu quả
  - Tốn chi phí hơn (nhiều input token)
  - Xử lý chậm hơn
- **Option 2 — RAG (chunk + retrieve):** preprocessing bước chunk document thành các
  mảnh nhỏ (**chunks**), khi user hỏi thì tìm các chunk **liên quan nhất** (relevant)
  rồi mới nhét vào prompt, thay vì nhét cả document.
  - **Benefit:** Claude tập trung vào nội dung liên quan; scale được với document rất lớn;
    làm việc được với nhiều document cùng lúc; prompt nhỏ hơn → rẻ hơn, nhanh hơn.
  - **Challenge:** cần bước preprocessing để chunk; cần cơ chế search để tìm chunk
    "relevant"; chunk được chọn có thể thiếu context cần thiết; có nhiều cách chunk khác
    nhau — cách nào là tốt nhất còn tùy use case.
- **Khi nào dùng RAG:** RAG tốn công triển khai hơn "stuff hết vào prompt" — chỉ nên dùng
  khi document rất lớn, có nhiều document, hoặc cần tối ưu cost/performance. RAG đánh đổi
  simplicity lấy scalability + efficiency.

### 2. Text chunking strategies
Chunking là bước **critical** trong RAG pipeline — chunk sai làm nhiễu context, dẫn tới
câu trả lời sai hoàn toàn (vd chunk lẫn 2 chủ đề khác nhau, từ "bug" trong context y khoa
bị lẫn với "bug" trong context software engineering).

- **Size-based chunking:** chia text thành các đoạn có độ dài (số ký tự) bằng nhau —
  đơn giản nhất, hoạt động với mọi loại document (kể cả code). Nhược điểm: cắt ngang
  câu/từ, mất context xung quanh, section header có thể bị tách khỏi nội dung của nó.
  Khắc phục bằng **chunk overlap** — mỗi chunk lấy thêm 1 đoạn ký tự từ chunk liền kề
  để giữ context + câu hoàn chỉnh hơn. Đây thường là lựa chọn mặc định trong production
  vì đơn giản, đáng tin cậy, hoạt động với mọi loại nội dung.
- **Structure-based chunking:** chia theo cấu trúc tự nhiên của document (headers,
  paragraphs, sections) — vd split theo `## ` header trong Markdown. Cho chunk "sạch"
  và có ý nghĩa nhất (mỗi chunk = 1 section hoàn chỉnh), nhưng chỉ dùng được khi document
  có cấu trúc rõ ràng, đảm bảo (nhiều document thực tế là plain text/PDF không có structure
  markers).
- **Semantic-based chunking:** chia text thành từng câu, rồi dùng NLP để đo độ liên quan
  giữa các câu liên tiếp, gom nhóm câu liên quan thành 1 chunk. Cho chunk relevant nhất
  nhưng tốn compute và phức tạp nhất để triển khai.
- **Sentence-based chunking:** giải pháp trung gian thực tế — split text thành câu bằng
  regex, gom N câu/chunk với overlap vài câu giữa các chunk liền kề.
- **Chọn strategy nào:** structure-based cho kết quả tốt nhất khi bạn kiểm soát được
  format document (vd internal report công ty); sentence-based là trung gian tốt cho hầu
  hết text document; size-based là fallback đáng tin cậy nhất, hoạt động với mọi loại nội
  dung kể cả code. Không có strategy "tốt nhất" tuyệt đối — phụ thuộc vào document, use
  case, và trade-off giữa độ phức tạp triển khai vs chất lượng chunk.

### 3. Text embeddings
Sau khi có chunks, bước tiếp theo là tìm chunk nào **relevant** nhất với câu hỏi của
user — đây là bài toán **search**.

- **Semantic search:** khác keyword search (tìm khớp từ chính xác), semantic search dùng
  **text embeddings** để hiểu ý nghĩa (meaning) và ngữ cảnh (context) của cả query lẫn
  từng chunk.
- **Text embedding** là 1 numerical representation (danh sách số thực) biểu diễn ý nghĩa
  của 1 đoạn text. Luồng hoạt động:
  - Đưa text vào **embedding model**
  - Model trả về 1 list số (embedding vector), mỗi số nằm trong khoảng -1 đến +1
  - Các số này đại diện cho các "đặc trưng" (features/qualities) khác nhau của input text
  - **Lưu ý quan trọng:** mỗi số trong embedding KHÔNG có ý nghĩa cụ thể mà con người
    diễn giải trực tiếp được (không phải "số này = độ vui vẻ của câu") — ý nghĩa của mỗi
    dimension được model tự học trong quá trình training, không interpretable trực tiếp.
- **Anthropic hiện KHÔNG cung cấp embedding model** — provider được recommend là
  **VoyageAI** (cần tạo account riêng, lấy API key riêng, free để bắt đầu).
- Setup: thêm `VOYAGE_API_KEY` vào `.env`, cài `voyageai` package, dùng
  `voyageai.Client()` (đọc key từ env tự động như `anthropic.Anthropic()`), gọi
  `client.embed([text], model="voyage-3-large", input_type="query")` để lấy embedding.
- Bước tiếp theo (chưa học ở lesson này): so sánh các embedding vector để tính độ tương
  đồng (similarity) — đây là core của semantic search.

### 4. The full RAG flow
Đây là bức tranh tổng thể, ghép toàn bộ các mảnh đã học (chunking, embedding) thành 1
pipeline hoàn chỉnh, chia làm 2 giai đoạn: **preprocessing** (làm trước, offline) và
**query-time** (chạy mỗi khi user hỏi).

**Giai đoạn preprocessing (làm 1 lần, trước khi có user nào hỏi):**
1. **Chunk source text** — chia document gốc thành các chunk nhỏ (vd theo section:
   "Medical Research" section, "Software Engineering" section).
2. **Generate embeddings** — đưa từng chunk qua embedding model, ra 1 vector số. Ví dụ
   minh họa (embedding model tưởng tượng, chỉ 2 chiều: chiều 1 = "độ liên quan y khoa",
   chiều 2 = "độ liên quan software engineering"):
   - Chunk "Medical Research" (có chứa từ `'bug'`) → `[0.97, 0.34]`
   - Chunk "Software Engineering" (có chứa `'infection vectors'`) → `[0.30, 0.97]`
   - Lưu ý: cả 2 vector đều có phần "lệch" sang chiều còn lại vì có từ ngữ mập mờ
     (`'bug'` trong y khoa dễ gây nhiễu với software, `'infection vectors'` ngược lại)
     — đây chính là lý do semantic search (hiểu ý nghĩa) tốt hơn keyword search (khớp từ).
   - **Normalization**: embedding API thường tự động scale vector về magnitude = 1.0
     (nằm trên unit circle/unit sphere) — không cần tự tính toán, model lo việc này.
     Vd `[0.97, 0.34]` → normalized `[0.944, 0.331]`.
3. **Store in vector database** — lưu các embedding đã chunk vào **vector database**,
   1 loại database chuyên dụng để lưu trữ, so sánh, và search trên các vector số dài.
   → Đến đây pipeline **dừng lại và chờ** user gửi query — toàn bộ bước trên là
   preprocessing, làm trước (offline), không phụ thuộc vào câu hỏi cụ thể nào.

**Giai đoạn query-time (chạy mỗi khi có user hỏi):**
4. **Process user query** — embed câu hỏi của user bằng **CÙNG 1 embedding model** đã
   dùng để embed chunks (bắt buộc dùng chung model để vector nằm cùng "không gian ý
   nghĩa", so sánh được với nhau). Vd query "what did software engineering dept do this
   year?" → `[0.1, 0.89]` → normalized `[0.112, 0.993]`.
5. **Find similar embeddings** — gửi query embedding vào vector database, database trả
   về (các) chunk embedding gần nhất — chính là chunk "liên quan nhất" tới câu hỏi.
   - **Cosine similarity**: đo độ tương đồng bằng cosin của góc giữa 2 vector.
     - Range: **-1 đến 1**
     - Gần **1** → rất giống nhau (giống hướng)
     - Gần **-1** → rất khác nhau (ngược hướng)
     - **0** → vuông góc, không liên quan gì nhau
     - Ví dụ: query vs chunk "Software Engineering" → similarity `0.983` (rất cao,
       được chọn); query vs chunk "Medical Research" → chỉ `0.398` (thấp, bị loại)
   - **Cosine distance** = `1 - cosine_similarity` — hay gặp trong docs của vector
     database. Ngược lại với similarity: gần **0** = giống nhau, càng lớn = càng khác.
6. **Create the final prompt** — ghép câu hỏi gốc của user + chunk relevant nhất vừa
   tìm được vào 1 prompt (dùng pattern `<user_question>` / `<report>` hoặc tương tự),
   gửi cho Claude để sinh câu trả lời cuối cùng — đây chính là bước "Generation" (G)
   trong RAG, dựa trên context đã "Retrieve" (R) được ở bước 5.

**Tóm tắt luồng chạy đầy đủ:**
`Chunk → Embed chunks → Store in vector DB` (preprocessing, offline)
`→ (chờ query) → Embed query (cùng model) → Cosine similarity search trong vector DB
→ Lấy chunk gần nhất → Ghép prompt (question + chunk) → Gửi Claude → Trả lời` (query-time)

### 5. Implementing the RAG flow (code thật, dùng VoyageAI)
Đây là lesson biến sơ đồ 5 bước ở mục 4 thành code cụ thể, dùng embedding model
**thật** (VoyageAI) thay vì mock 2D như bài trước, và giới thiệu 1 class
**`VectorIndex`** đóng vai trò vector database đơn giản (in-memory).

**5 bước implement (khớp với luồng ở mục 4):**
1. **Chunk text theo section** — đọc file document, dùng lại `chunk_by_section()`
   (đã học ở mục 2) để tách thành các chunk theo header.
2. **Generate embeddings cho tất cả chunk** — gọi `generate_embedding()` 1 lần với
   **cả list chunks** thay vì gọi từng chunk riêng lẻ → **batch processing**,
   hiệu quả hơn (ít round-trip API hơn). Hàm `generate_embedding` cần được viết lại
   để nhận cả `str` đơn lẻ lẫn `list[str]`.
3. **Tạo vector store, add từng embedding vào** — `VectorIndex()` là 1 class tự
   viết, đóng vai trò vector database tối giản. Mỗi lần `add_vector(embedding, metadata)`
   lưu **CẢ embedding LẪN nội dung text gốc** (metadata, vd `{"content": chunk}`).
   - **Vì sao phải lưu cả text gốc?** Khi search xong, vector DB chỉ biết trả về
     embedding nào gần nhất — nhưng thứ mình CẦN dùng lại là **text gốc** để nhét vào
     prompt cho Claude, không phải dãy số. Nên phải lưu kèm text (hoặc reference tới
     text) ngay từ lúc `add_vector`.
4. **Embed câu hỏi user** — gọi `generate_embedding(query)` với model **giống hệt**
   model đã dùng để embed chunks (nhắc lại gotcha từ mục 4).
5. **Search trong vector store** — `store.search(user_embedding, k)` trả về `k` kết
   quả gần nhất, mỗi kết quả là tuple `(doc, distance)` — `doc` là metadata đã lưu ở
   bước 3 (chứa `content`), `distance` là **cosine distance** (không phải similarity).
   - **Distance càng THẤP → càng liên quan** (ngược logic với similarity).
   - Ví dụ trong bài giảng: query "What did the software engineering dept do last
     year?" → `Section 2: Software Engineering` distance `0.71` (gần nhất),
     `Methodology` distance `0.72` (gần nhì) — được chọn vì distance thấp hơn các
     section khác.

**Tóm tắt luồng chạy:**
`Đọc file → chunk_by_section() → generate_embedding(chunks) (batch)
→ VectorIndex().add_vector(embedding, {"content": chunk}) cho từng chunk
→ generate_embedding(user_query) → store.search(user_embedding, k)
→ nhận list (doc, distance) → lấy doc["content"] làm context cho prompt Claude`

**Lưu ý:** lesson này nói "vẫn còn case chưa xử lý tốt" — sẽ được cải thiện ở các
lesson sau (BM25, Multi-Index pipeline).

### 6. BM25 lexical search
**Vấn đề của semantic search đơn thuần:** semantic search (dựa trên embedding) rất giỏi
hiểu ý nghĩa/context, nhưng có thể **miss exact term match**. Ví dụ: user search 1 mã
incident cụ thể như `"INC-2023-Q4-011"` — semantic search có thể trả về section
"Cybersecurity" (đúng, có chứa mã này) LẪN section "Financial Analysis" (SAI, không hề
nhắc tới mã này) — vì semantic search quan tâm "conceptual similarity" chứ không quan
tâm việc term đó có thực sự xuất hiện trong text hay không.

**Giải pháp — Hybrid search:** chạy song song 2 loại search rồi merge kết quả:
- **Semantic search** — tìm nội dung liên quan về mặt ý nghĩa (dùng embeddings)
- **Lexical search** — tìm exact term match (dùng classic text search, vd BM25)
- **Merged results** — kết hợp cả 2 để có kết quả chính xác hơn (lesson sau sẽ học
  cách merge — "A Multi-Index RAG pipeline")

**BM25 (Best Match 25)** là thuật toán phổ biến nhất cho lexical search trong RAG. Cách
hoạt động khi xử lý 1 query:
1. **Tokenize query** — tách câu hỏi thành từng term riêng lẻ. Vd `"a INC-2023-Q4-011"`
   → `["a", "INC-2023-Q4-011"]`.
2. **Đếm term frequency** — đếm mỗi term xuất hiện bao nhiêu lần trong TOÀN BỘ tập
   documents. Từ phổ biến như `"a"` có thể xuất hiện 5 lần, trong khi term đặc thù như
   `"INC-2023-Q4-011"` chỉ xuất hiện 1 lần.
3. **Weight term theo độ quan trọng** — term xuất hiện CÀNG ÍT thì được coi CÀNG quan
   trọng (importance score cao). `"a"` có importance thấp (quá phổ biến, không mang
   nhiều thông tin phân biệt); `"INC-2023-Q4-011"` có importance cao (hiếm, đặc thù).
   → Đây chính là ý tưởng **IDF (Inverse Document Frequency)**: term hiếm → giá trị cao.
4. **Tìm best match** — trả về document chứa NHIỀU instance của các term có weight cao
   nhất.

**Điểm mạnh của BM25:**
- Weight cao hơn cho term hiếm, đặc thù
- Bỏ qua (ít quan tâm) các từ phổ biến không mang giá trị phân biệt
- Tập trung vào **term frequency**, không quan tâm "ý nghĩa" ngữ cảnh
- Đặc biệt hiệu quả với technical terms, ID, mã số, cụm từ cụ thể — đúng những case mà
  semantic search hay bỏ sót

**Insight chính:** semantic search và lexical search (BM25) có điểm mạnh BỔ SUNG cho
nhau (complementary) — semantic hiểu context/ý nghĩa, lexical đảm bảo không bỏ sót exact
match. Kết hợp cả 2 tạo ra hệ thống search robust hơn, xử lý tốt cả câu hỏi mang tính khái
niệm (conceptual) lẫn tra cứu cụ thể (specific lookup).

**Interface `BM25Index` (tương tự `VectorIndex` ở mục 5, để dễ hoán đổi/merge sau này):**
```python
chunks = chunk_by_section(text)          # 1. chunk text theo section (tai su dung)
store = BM25Index()                      # 2. tao BM25 store
for chunk in chunks:
    store.add_document({"content": chunk})
results = store.search("What happened with INC-2023-Q4-011?", 3)   # 3. search top-3
for doc, distance in results:
    print(distance, "\n", doc["content"][:200], "\n----\n")
```

## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
| `BM25Index.add_document(metadata)` | method (tự viết) | — | Thêm 1 document (dict có `content`) vào BM25 index — index sẽ tự tokenize nội dung |
| `BM25Index.search(query, k)` | method (tự viết) | — | Trả về `k` document có BM25 score cao nhất, dạng `(doc, distance)` giống interface `VectorIndex` |
| `re.split(pattern, text)` | function | — | Structure-based chunking: split theo header pattern (vd `r"\n## "`) |
| `re.split(r"(?<=[.!?])\s+", text)` | function | — | Sentence-based chunking: split câu bằng lookbehind trên dấu câu kết thúc |
| `voyageai.Client()` | class | — | Client cho VoyageAI embedding API, đọc `VOYAGE_API_KEY` từ env |
| `client.embed(texts, model, input_type)` | method | model="voyage-3-large" | `texts`: list[str]; `input_type`: "query" hoặc "document"; trả về `.embeddings` (list các vector) |
| Cosine similarity | công thức | — | `dot(a, b) / (norm(a) * norm(b))` — nếu a, b đã normalize (magnitude=1) thì đơn giản còn `dot(a, b)` |
| Cosine distance | công thức | — | `1 - cosine_similarity` — dùng phổ biến trong vector DB (0 = giống nhau, lớn hơn = khác nhau) |
| `VectorIndex.add_vector(embedding, metadata)` | method (tự viết) | — | Lưu 1 embedding + metadata (vd `{"content": chunk}`) vào in-memory vector store |
| `VectorIndex.search(query_embedding, k)` | method (tự viết) | — | Trả về `k` kết quả `(metadata, distance)` gần nhất, sort theo cosine distance tăng dần |

## Gotchas
- [ ] Anthropic KHÔNG có embedding API riêng — bắt buộc phải dùng provider ngoài (VoyageAI được recommend chính thức)
- [ ] `VOYAGE_API_KEY` là biến env RIÊNG, khác `ANTHROPIC_API_KEY` — cần add cả 2 vào `.env`
- [ ] Size-based chunking KHÔNG overlap sẽ cắt ngang câu/từ — luôn cân nhắc `chunk_overlap > 0`
- [ ] `input_type` khi embed câu hỏi user nên là `"query"`, khi embed document/chunk nên là `"document"` — 2 loại có thể được model tối ưu khác nhau
- [ ] Query và chunks BẮT BUỘC phải embed bằng CÙNG 1 model — embedding từ 2 model khác nhau không nằm cùng không gian vector, so sánh (cosine similarity) sẽ vô nghĩa
- [ ] Cosine similarity range là [-1, 1], KHÔNG phải [0, 1] — dễ nhầm với các loại similarity score khác (vd Jaccard)
- [ ] `VectorIndex.search()` trả về **cosine distance**, không phải similarity — logic NGƯỢC lại (distance thấp = liên quan cao), dễ đọc nhầm khi debug
- [ ] Luôn lưu text gốc (metadata) kèm embedding trong vector store — chỉ có embedding number thì không dùng lại được để build prompt cho Claude
- [ ] BM25 score gốc là "cao hơn = liên quan hơn" (ngược với cosine distance) — nếu muốn interface giống `VectorIndex.search()` (sort tăng dần theo "distance") thì phải tự đảo dấu (vd trả về `-score`), lesson dùng chung tên biến `distance` cho cả 2 nhưng bản chất công thức khác nhau, dễ nhầm
- [ ] BM25 chỉ match token CHÍNH XÁC (sau khi tokenize) — không hiểu synonym/ý nghĩa, nên vẫn cần semantic search song song cho câu hỏi mang tính khái niệm

## Code Snippets
```python
# Size-based chunking với overlap
def chunk_by_char(text, chunk_size=150, chunk_overlap=20):
    chunks = []
    start_idx = 0
    while start_idx < len(text):
        end_idx = min(start_idx + chunk_size, len(text))
        chunks.append(text[start_idx:end_idx])
        start_idx = end_idx - chunk_overlap if end_idx < len(text) else len(text)
    return chunks

# Structure-based chunking (Markdown headers)
def chunk_by_section(document_text):
    return re.split(r"\n## ", document_text)

# Sentence-based chunking với overlap
def chunk_by_sentence(text, max_sentences_per_chunk=5, overlap_sentences=1):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    start_idx = 0
    while start_idx < len(sentences):
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))
        chunks.append(" ".join(sentences[start_idx:end_idx]))
        start_idx += max_sentences_per_chunk - overlap_sentences
        if start_idx < 0:
            start_idx = 0
    return chunks

# Generate embedding với VoyageAI
def generate_embedding(text, model="voyage-3-large", input_type="query"):
    result = client.embed([text], model=model, input_type=input_type)
    return result.embeddings[0]
```

## Questions / Unclear Points
- ?
