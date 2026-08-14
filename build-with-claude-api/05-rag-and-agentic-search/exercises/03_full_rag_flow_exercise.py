"""
Exercise 03: The full RAG flow
Session: RAG and Agentic Search
Objective: Minh hoa toan bo pipeline RAG end-to-end — chunk -> embed (mock 2D
embedding de de hinh dung, khong can VoyageAI key that) -> luu vao "vector DB"
gia lap -> nhan query -> tinh cosine similarity -> lay chunk lien quan nhat ->
ghep prompt -> goi Claude sinh cau tra loi.

Embedding o day la MOCK (tu tinh tay 2 chieu: "medical score" va "software
engineering score") de bam sat vi du minh hoa trong bai giang — trong thuc te
se thay bang embedding model that (vd VoyageAI voyage-3-large, xem
02_chunking_strategies... va notes.md phan Text embeddings).
"""

import math  # dung sqrt() de tinh vector norm khi normalize

from dotenv import load_dotenv  # load bien moi truong tu file .env
import anthropic  # SDK chinh thuc de goi Claude API

load_dotenv()  # doc ANTHROPIC_API_KEY tu .env
client = anthropic.Anthropic()  # khoi tao client

MODEL = "claude-haiku-4-5"  # model re, dung cho dev/test


# ============================================================
# BUOC 1 — Chunk source text (o day da chunk san theo section)
# ============================================================
CHUNKS = [
    {
        "title": "Medical Research",
        "text": (
            "This year saw significant strides in our understanding of "
            "XDR-47, a 'bug' we have not seen before."
        ),
    },
    {
        "title": "Software Engineering",
        "text": (
            "This division dedicated significant effort to studying various "
            "infection vectors in our distributed systems"
        ),
    },
]


def mock_embed(medical_score: float, software_score: float) -> list:
    """Gia lap 1 embedding model 2 chieu: [do lien quan y khoa, do lien quan SE].

    Trong thuc te, embedding that co hang tram/nghin chieu va duoc model tu
    hoc, khong ai "gan tay" gia tri nhu the nay — ham nay chi de minh hoa
    khai niem, khop voi vi du trong bai giang.
    """
    return [medical_score, software_score]


def normalize(vector: list) -> list:
    """BUOC 2b — Normalization: scale vector ve magnitude (do dai) = 1.0."""
    # vector: list[float] — embedding vector chua normalize
    magnitude = math.sqrt(sum(v * v for v in vector))  # tinh do dai vector (Euclidean norm)
    return [v / magnitude for v in vector]  # chia tung phan tu cho magnitude


def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """Do tuong dong giua 2 vector bang cosin cua goc giua chung.

    Range: -1 (rat khac nhau) den 1 (rat giong nhau), 0 = vuong goc (khong lien quan).
    Neu ca 2 vector da normalize (magnitude=1) thi cong thuc rut gon thanh dot product.
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))  # tich vo huong (dot product)
    norm_a = math.sqrt(sum(a * a for a in vec_a))  # do dai vector a
    norm_b = math.sqrt(sum(b * b for b in vec_b))  # do dai vector b
    return dot_product / (norm_a * norm_b)  # cong thuc cosine similarity day du


# ============================================================
# BUOC 2 + 3 — Generate embeddings cho tung chunk + "luu vao vector DB"
# ============================================================
# vector_db: list cac dict {chunk, embedding} — dong vai tro vector database don gian
vector_db = []
for chunk, raw_embedding in zip(
    CHUNKS,
    [mock_embed(0.97, 0.34), mock_embed(0.30, 0.97)],  # embedding tho, chua normalize
):
    vector_db.append(
        {
            "chunk": chunk,
            "embedding": normalize(raw_embedding),  # luu ban da normalize
        }
    )


def retrieve_most_relevant_chunk(query_embedding: list) -> dict:
    """BUOC 5 — Tim chunk co cosine similarity cao nhat voi query embedding."""
    # query_embedding: list[float] — embedding cua cau hoi user, da normalize
    best_entry = None
    best_score = -1.0  # cosine similarity thap nhat co the la -1

    for entry in vector_db:
        score = cosine_similarity(query_embedding, entry["embedding"])
        print(f"  - similarity voi '{entry['chunk']['title']}': {score:.3f}")
        if score > best_score:
            best_score = score
            best_entry = entry

    return best_entry


def main():
    # BUOC 4 — Process user query: embed cau hoi bang CUNG embedding "model"
    # (o day la mock_embed) da dung cho chunks
    user_question = (
        "I'm curious about the company. In particular, what did the "
        "software engineering dept do this year?"
    )
    query_embedding = normalize(mock_embed(0.1, 0.89))

    print("Dang tim chunk lien quan nhat...")
    best = retrieve_most_relevant_chunk(query_embedding)
    print(f"-> Chunk duoc chon: '{best['chunk']['title']}'\n")

    # BUOC 6 — Create the final prompt: ghep question + chunk relevant nhat
    context = f"## Section: {best['chunk']['title']}\n{best['chunk']['text']}"

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=256,
            system="Answer the user's question using ONLY the provided context.",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"<user_question>\n{user_question}\n</user_question>\n\n"
                        f"<report>\n{context}\n</report>"
                    ),
                }
            ],
        )
        print(response.content[0].text)
    except anthropic.APIError as exc:
        # bat loi API de khong crash chuong trinh
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
