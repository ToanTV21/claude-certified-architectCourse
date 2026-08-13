"""
Implementing the RAG flow
Session: RAG and Agentic Search
Objective: Minimal RAG pipeline — naive keyword-overlap "retrieval" (no embedding
provider required) + feed retrieved context to Claude for a grounded answer.

For real embeddings, swap `naive_retrieve` for an embedding-based cosine
similarity search (e.g. using voyageai or another embeddings API).
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test

# "Knowledge base" giả lập — trong thực tế đây sẽ là các đoạn tài liệu đã được embed sẵn
DOCUMENTS = [
    "The Model Context Protocol (MCP) standardizes how apps connect LLMs to tools and data.",
    "Claude Code is Anthropic's CLI for agentic coding tasks in the terminal.",
    "Extended thinking lets Claude reason step by step before producing a final answer.",
]


def naive_retrieve(query: str, top_k: int = 2) -> list:
    """Rank documents by word-overlap count with the query (stand-in for embeddings)."""
    # query: str — câu hỏi của user, dùng để so khớp với từng document
    # top_k: int — số document liên quan nhất muốn lấy ra
    print(f"\n[RETRIEVE] Query nhận vào: {query!r}")

    query_words = set(query.lower().split())  # tách query thành tập các từ (lowercase)
    print(f"[RETRIEVE] Query sau khi tách từ (lowercase, set): {query_words}")

    # đếm số từ trùng nhau giữa query và từng document -> điểm số càng cao càng liên quan
    scored = []
    for doc in DOCUMENTS:
        doc_words = set(doc.lower().split())
        overlap = query_words & doc_words  # tập các từ trùng nhau
        score = len(overlap)
        scored.append((score, doc))
        print(f"[RETRIEVE]   score={score} | overlap={overlap or '{}'} | doc={doc[:60]!r}...")

    scored.sort(key=lambda x: x[0], reverse=True)  # sắp xếp giảm dần theo điểm
    print(f"[RETRIEVE] Đã sort theo score giảm dần, lấy top_k={top_k}")

    top_docs = [doc for _, doc in scored[:top_k]]  # lấy top_k document điểm cao nhất
    for i, doc in enumerate(top_docs, 1):
        print(f"[RETRIEVE]   #{i}: {doc}")

    return top_docs


def main():
    query = "What is MCP used for?"
    print(f"[MAIN] Bắt đầu RAG flow với query: {query!r}")

    context_docs = naive_retrieve(query)  # bước "R" (retrieve) trong RAG
    print(f"\n[MAIN] Retrieve xong, lấy được {len(context_docs)} document(s) liên quan nhất")

    context = "\n".join(f"- {doc}" for doc in context_docs)  # gộp các doc thành 1 block context
    print(f"\n[MAIN] Context block sau khi gộp (sẽ nhét vào prompt gửi Claude):\n{context}")

    prompt_content = f"<context>\n{context}\n</context>\n\nQuestion: {query}"
    print(f"\n[MAIN] Full user message content gửi lên Claude:\n{prompt_content}")

    try:
        print(f"\n[GENERATE] Gọi Claude API với model={MODEL} ...")
        response = client.messages.create(
            model=MODEL,
            max_tokens=256,
            # ép Claude CHỈ trả lời dựa trên context đã retrieve, tránh bịa (hallucination)
            system="Answer using ONLY the provided context. If the context is insufficient, say so.",
            messages=[
                {
                    "role": "user",
                    # nhét context đã retrieve + câu hỏi gốc vào cùng 1 user message
                    "content": prompt_content,
                }
            ],
        )
        print("[GENERATE] Nhận response thành công từ Claude API")

        answer = response.content[0].text
        print(f"\n[RESULT] Câu trả lời cuối cùng (grounded trên context đã retrieve):\n{answer}")
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"[GENERATE] API error: {exc}")


if __name__ == "__main__":
    main()
