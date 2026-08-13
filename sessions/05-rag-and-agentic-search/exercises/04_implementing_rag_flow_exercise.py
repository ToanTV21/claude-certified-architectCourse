"""
Exercise 04: Implementing the RAG flow
Session: RAG and Agentic Search
Objective: Trien khai day du 5 buoc RAG bang code that — chunk document theo
section, batch-generate embedding that qua VoyageAI, luu vao 1 vector store
tu viet (VectorIndex), roi search chunk lien quan nhat cho cau hoi user va
dua vao prompt cho Claude.

Yeu cau: can VOYAGE_API_KEY trong .env (xem notes.md phan "Text embeddings").
Neu chua co key, script se in loi ro rang thay vi crash mo ho.
"""

import math  # tinh cosine distance
import os  # doc duong dan file report mau
import re  # dung cho chunk_by_section (split theo header Markdown)

from dotenv import load_dotenv  # load bien moi truong tu file .env
import anthropic  # SDK chinh thuc de goi Claude API
import voyageai  # SDK cua VoyageAI, dung de generate embedding that

load_dotenv()  # doc ANTHROPIC_API_KEY va VOYAGE_API_KEY tu .env
client = anthropic.Anthropic()  # client goi Claude
voyage_client = voyageai.Client()  # client goi VoyageAI embedding model

MODEL = "claude-haiku-4-5"  # model re, dung cho dev/test
EMBED_MODEL = "voyage-3-large"  # embedding model duoc VoyageAI recommend

# duong dan file report mau, dat cung thu muc voi file exercise nay
REPORT_PATH = os.path.join(os.path.dirname(__file__), "_04_sample_report.md")


# ============================================================
# BUOC 1 — Chunk text theo section (tai su dung structure-based chunking)
# ============================================================
def chunk_by_section(document_text: str) -> list:
    """Split document theo header Markdown '## ' — moi chunk la 1 section."""
    pattern = r"\n## "  # pattern nhan dien 1 header moi
    return re.split(pattern, document_text)


# ============================================================
# BUOC 2 — Generate embeddings, ho tro ca 1 string don le lan 1 list string
# ============================================================
def generate_embedding(texts, model: str = EMBED_MODEL, input_type: str = "document"):
    """Tra ve embedding cho 1 string hoac 1 list string (batch processing).

    texts: str hoac list[str] — noi dung can embed
    input_type: "document" khi embed chunk, "query" khi embed cau hoi user
    """
    is_single = isinstance(texts, str)  # kiem tra dau vao la 1 string don le
    text_list = [texts] if is_single else texts  # luon goi API voi 1 list

    result = voyage_client.embed(text_list, model=model, input_type=input_type)

    # neu dau vao la 1 string thi tra ve 1 embedding, khong phai list-cua-list
    return result.embeddings[0] if is_single else result.embeddings


# ============================================================
# BUOC 3 — Vector store don gian, luu ca embedding lan text goc
# ============================================================
class VectorIndex:
    """Vector database toi gian, luu trong bo nho (khong ben vung qua session)."""

    def __init__(self):
        # moi phan tu la tuple (embedding, metadata) — metadata luu text goc
        self._entries = []

    def add_vector(self, embedding: list, metadata: dict) -> None:
        """Them 1 embedding + metadata (vd {'content': chunk_text}) vao store."""
        self._entries.append((embedding, metadata))

    def _cosine_distance(self, vec_a: list, vec_b: list) -> float:
        """distance = 1 - cosine_similarity -> cang thap cang lien quan."""
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        similarity = dot_product / (norm_a * norm_b)
        return 1 - similarity

    def search(self, query_embedding: list, k: int = 2) -> list:
        """Tra ve k ket qua (metadata, distance) gan nhat, sort distance tang dan."""
        scored = [
            (metadata, self._cosine_distance(query_embedding, embedding))
            for embedding, metadata in self._entries
        ]
        scored.sort(key=lambda pair: pair[1])  # distance thap nhat len dau
        return scored[:k]


def main():
    # BUOC 1 — doc file report mau va chunk theo section
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    chunks = chunk_by_section(text)
    print(f"Da chunk thanh {len(chunks)} sections.\n")

    try:
        # BUOC 2 — embed toan bo chunks trong 1 lan goi (batch)
        embeddings = generate_embedding(chunks, input_type="document")

        # BUOC 3 — tao vector store, add tung cap (embedding, chunk text)
        store = VectorIndex()
        for embedding, chunk in zip(embeddings, chunks):
            store.add_vector(embedding, {"content": chunk})

        # BUOC 4 — embed cau hoi cua user
        user_question = "What did the software engineering dept do last year?"
        user_embedding = generate_embedding(user_question, input_type="query")

        # BUOC 5 — search 2 chunk lien quan nhat (distance thap nhat)
        results = store.search(user_embedding, k=2)
        print("Ket qua search (distance cang thap cang lien quan):")
        for doc, distance in results:
            print(f"  distance={distance:.3f} | {doc['content'][:80].strip()}...")

        # Ghep chunk lien quan nhat vao prompt, goi Claude sinh cau tra loi
        best_doc, _ = results[0]
        response = client.messages.create(
            model=MODEL,
            max_tokens=256,
            system="Answer the user's question using ONLY the provided context.",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"<user_question>\n{user_question}\n</user_question>\n\n"
                        f"<report>\n{best_doc['content']}\n</report>"
                    ),
                }
            ],
        )
        print(f"\nCau tra loi cua Claude:\n{response.content[0].text}")

    except voyageai.error.AuthenticationError:
        # bat loi rieng khi thieu/sai VOYAGE_API_KEY de user biet chinh xac phai sua gi
        print("Loi: VOYAGE_API_KEY khong hop le hoac chua duoc set trong .env")
    except anthropic.APIError as exc:
        print(f"API error tu Claude: {exc}")


if __name__ == "__main__":
    main()
