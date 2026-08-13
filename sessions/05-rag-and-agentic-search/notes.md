# Session 05: RAG and Agentic Search

## Lessons trong section này
- [x] Introducing Retrieval Augmented Generation
- [x] Text chunking strategies
- [x] Text embeddings
- [ ] The full RAG flow
- [ ] Implementing the RAG flow
- [ ] BM25 lexical search
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

## Important APIs / Parameters
| Name | Type | Default | Notes |
|------|------|---------|-------|
| `re.split(pattern, text)` | function | — | Structure-based chunking: split theo header pattern (vd `r"\n## "`) |
| `re.split(r"(?<=[.!?])\s+", text)` | function | — | Sentence-based chunking: split câu bằng lookbehind trên dấu câu kết thúc |
| `voyageai.Client()` | class | — | Client cho VoyageAI embedding API, đọc `VOYAGE_API_KEY` từ env |
| `client.embed(texts, model, input_type)` | method | model="voyage-3-large" | `texts`: list[str]; `input_type`: "query" hoặc "document"; trả về `.embeddings` (list các vector) |

## Gotchas
- [ ] Anthropic KHÔNG có embedding API riêng — bắt buộc phải dùng provider ngoài (VoyageAI được recommend chính thức)
- [ ] `VOYAGE_API_KEY` là biến env RIÊNG, khác `ANTHROPIC_API_KEY` — cần add cả 2 vào `.env`
- [ ] Size-based chunking KHÔNG overlap sẽ cắt ngang câu/từ — luôn cân nhắc `chunk_overlap > 0`
- [ ] `input_type` khi embed câu hỏi user nên là `"query"`, khi embed document/chunk nên là `"document"` — 2 loại có thể được model tối ưu khác nhau

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
