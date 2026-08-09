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
    query_words = set(query.lower().split())  # tách query thành tập các từ (lowercase)
    # đếm số từ trùng nhau giữa query và từng document -> điểm số càng cao càng liên quan
    scored = [
        (len(query_words & set(doc.lower().split())), doc) for doc in DOCUMENTS
    ]
    scored.sort(key=lambda x: x[0], reverse=True)  # sắp xếp giảm dần theo điểm
    return [doc for _, doc in scored[:top_k]]  # lấy top_k document điểm cao nhất


def main():
    query = "What is MCP used for?"
    context_docs = naive_retrieve(query)  # bước "R" (retrieve) trong RAG
    context = "\n".join(f"- {doc}" for doc in context_docs)  # gộp các doc thành 1 block context

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=256,
            # ép Claude CHỈ trả lời dựa trên context đã retrieve, tránh bịa (hallucination)
            system="Answer using ONLY the provided context. If the context is insufficient, say so.",
            messages=[
                {
                    "role": "user",
                    # nhét context đã retrieve + câu hỏi gốc vào cùng 1 user message
                    "content": f"<context>\n{context}\n</context>\n\nQuestion: {query}",
                }
            ],
        )
        print(response.content[0].text)
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
