# Exercises — RAG and Agentic Search

- `01_basic_rag_flow.py` — Implementing the RAG flow: chunk a small doc set, embed,
  retrieve top-k by cosine similarity, and feed retrieved context to Claude.

> Note: cần thêm `numpy` (và tùy chọn `voyageai` hoặc embedding provider khác)
> để chạy thử embeddings thật. `pip install numpy voyageai`.
