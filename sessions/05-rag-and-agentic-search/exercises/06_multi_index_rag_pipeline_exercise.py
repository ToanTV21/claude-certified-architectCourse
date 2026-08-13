"""
Exercise 06: A Multi-Index RAG pipeline
Session: RAG and Agentic Search
Objective: Ghep VectorIndex (semantic search) va BM25Index (lexical search) lai
thanh 1 pipeline hybrid duy nhat qua class Retriever, dung thuat toan
Reciprocal Rank Fusion (RRF) de merge ket qua tu ca 2 index mot cach cong
bang (khong can normalize score, chi dua vao rank).

Dung mock embedding (khong can VOYAGE_API_KEY that) de tap trung minh hoa kien
truc Retriever + RRF — xem 04_implementing_rag_flow_exercise.py de biet cach
dung embedding that qua VoyageAI.
"""

import math  # tinh IDF cho BM25
import re  # tokenize text cho BM25

from dotenv import load_dotenv  # load bien moi truong tu file .env
import anthropic  # SDK chinh thuc de goi Claude API

load_dotenv()  # doc ANTHROPIC_API_KEY tu .env
client = anthropic.Anthropic()  # client goi Claude

MODEL = "claude-haiku-4-5"  # model re, dung cho dev/test


# ============================================================
# Sample "report" — mo phong cac section, co 1 section chua ma incident
# ============================================================
CHUNKS = [
    {
        "title": "Financial Analysis",
        "content": (
            "Revenue grew by twelve percent this quarter. Operating costs "
            "remained stable across all business divisions this year."
        ),
        # mock embedding 3 chieu: [medical, software_eng, legal] — chi de demo,
        # embedding that co hang tram/nghin chieu va duoc model tu hoc
        "mock_embedding": [0.10, 0.30, 0.20],
    },
    {
        "title": "Software Engineering",
        "content": (
            "The engineering team resolved incident INC-2023-Q4-011 within "
            "four hours, restoring service to the deployment pipeline."
        ),
        "mock_embedding": [0.05, 0.95, 0.10],
    },
    {
        "title": "Cybersecurity",
        "content": (
            "A follow-up review of INC-2023-Q4-011 confirmed no data was "
            "exfiltrated during the outage caused by the failed deployment."
        ),
        "mock_embedding": [0.20, 0.85, 0.15],
    },
    {
        "title": "Legal Developments",
        "content": (
            "Legal counsel reviewed disclosure obligations following the "
            "recent outage and confirmed no regulatory filing was required."
        ),
        "mock_embedding": [0.15, 0.40, 0.90],
    },
]


def normalize(vector: list) -> list:
    """Scale vector ve magnitude = 1.0 (chuan hoa)."""
    magnitude = math.sqrt(sum(v * v for v in vector))
    return [v / magnitude for v in vector]


def cosine_distance(vec_a: list, vec_b: list) -> float:
    """distance = 1 - cosine_similarity -> cang thap cang lien quan."""
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    return 1 - (dot_product / (norm_a * norm_b))


def tokenize(text: str) -> list:
    """Tach text thanh list token lowercase (giu ca ky tu '-' trong ma nhu INC-2023-Q4-011)."""
    return re.findall(r"[\w-]+", text.lower())


class VectorIndex:
    """Semantic search index — dua vao mock embedding co san trong metadata."""

    def __init__(self):
        self._entries = []  # list (embedding, metadata)

    def add_document(self, metadata: dict) -> None:
        # o day embedding lay san tu metadata["mock_embedding"] thay vi goi API that
        embedding = normalize(metadata["mock_embedding"])
        self._entries.append((embedding, metadata))
        print(f"    [VectorIndex.add_document] '{metadata['title']}' -> embedding={embedding}")

    def search(self, query_text: str, k: int = 3, query_embedding: list = None) -> list:
        """query_embedding duoc truyen san (da mock) vi khong co embedding model that o day."""
        scored = [
            (metadata, cosine_distance(query_embedding, embedding))
            for embedding, metadata in self._entries
        ]
        scored.sort(key=lambda pair: pair[1])  # distance thap nhat (lien quan nhat) len dau
        print(f"  [VectorIndex.search] query_embedding={query_embedding}")
        for metadata, distance in scored:
            print(f"    -> '{metadata['title']}' distance={distance:.4f}")
        return scored[:k]


class BM25Index:
    """Lexical search index — thuat toan BM25 (tai su dung tu bai 05)."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self._documents = []
        self._doc_tokens = []
        self._doc_lengths = []
        self._avg_doc_length = 0.0

    def add_document(self, metadata: dict) -> None:
        tokens = tokenize(metadata["content"])
        self._documents.append(metadata)
        self._doc_tokens.append(tokens)
        self._doc_lengths.append(len(tokens))
        self._avg_doc_length = sum(self._doc_lengths) / len(self._doc_lengths)
        print(
            f"    [BM25Index.add_document] '{metadata['title']}' -> {len(tokens)} token, "
            f"avg_doc_length={self._avg_doc_length:.2f}"
        )

    def _idf(self, term: str) -> float:
        n_docs_with_term = sum(1 for tokens in self._doc_tokens if term in tokens)
        n_total = len(self._documents)
        return math.log((n_total - n_docs_with_term + 0.5) / (n_docs_with_term + 0.5) + 1)

    def _bm25_score(self, query_tokens: list, doc_index: int) -> float:
        doc_tokens = self._doc_tokens[doc_index]
        doc_length = self._doc_lengths[doc_index]
        score = 0.0
        for term in query_tokens:
            term_frequency = doc_tokens.count(term)
            if term_frequency == 0:
                continue
            idf = self._idf(term)
            numerator = term_frequency * (self.k1 + 1)
            denominator = term_frequency + self.k1 * (
                1 - self.b + self.b * doc_length / self._avg_doc_length
            )
            score += idf * (numerator / denominator)
        return score

    def search(self, query_text: str, k: int = 3, query_embedding: list = None) -> list:
        query_tokens = tokenize(query_text)
        print(f"  [BM25Index.search] query_tokens={query_tokens}")
        scored = [
            (self._documents[i], self._bm25_score(query_tokens, i))
            for i in range(len(self._documents))
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)  # score cao nhat len dau
        for doc, score in scored:
            print(f"    -> '{doc['title']}' bm25_score={score:.4f}")
        return scored[:k]


class Retriever:
    """Coordinator: forward query toi nhieu index, merge ket qua bang Reciprocal Rank Fusion."""

    def __init__(self, *indexes):
        # *indexes: nhan bao nhieu index tuy y (VectorIndex, BM25Index, hoac index tu viet khac),
        # mien la co chung interface add_document()/search() -> "SearchIndex protocol"
        if len(indexes) == 0:
            raise ValueError("At least one index must be provided")
        self._indexes = list(indexes)

    def add_document(self, document: dict) -> None:
        """Forward 1 document toi TAT CA index da dang ky."""
        print(f"  [Retriever.add_document] forward '{document['title']}' toi {len(self._indexes)} index")
        for index in self._indexes:
            index.add_document(document)

    def search(self, query_text: str, k: int = 3, k_rrf: int = 60, query_embedding: list = None) -> list:
        """Search song song tren moi index, merge ket qua bang RRF.

        RRF_score(d) = sum(1 / (k_rrf + rank_i(d))) qua tat ca index i ma d xuat hien.
        Chi dua vao RANK (thu hang), khong dung score goc -> khong can lo BM25 score
        va cosine distance khac thang do nhau.
        """
        # rrf_scores: map "title cua doc" -> RRF score cong don tu tat ca index
        # (dung title lam key vi don gian, thuc te nen dung 1 id duy nhat cho moi chunk)
        rrf_scores = {}
        doc_lookup = {}  # map title -> metadata goc, de lay lai sau khi tinh xong RRF

        for index in self._indexes:
            # moi index co the can query_embedding (VectorIndex) hoac khong (BM25Index) —
            # ca 2 deu chap nhan tham so nay qua **-style interface thong nhat
            print(f"  [Retriever.search] goi search() tren {type(index).__name__}")
            results = index.search(query_text, k=len(CHUNKS), query_embedding=query_embedding)
            for rank, (doc, _score) in enumerate(results, start=1):  # rank bat dau tu 1, khong phai 0
                title = doc["title"]
                doc_lookup[title] = doc
                # cong don 1/(k_rrf + rank) vao RRF score hien co (mac dinh 0 neu chua co)
                contribution = 1.0 / (k_rrf + rank)
                rrf_scores[title] = rrf_scores.get(title, 0.0) + contribution
                print(
                    f"    [RRF] {type(index).__name__} rank={rank} '{title}' "
                    f"+{contribution:.4f} -> running_rrf={rrf_scores[title]:.4f}"
                )

        # sort theo RRF score GIAM dan (cao hon = lien quan hon, khac voi cosine distance)
        ranked_titles = sorted(rrf_scores, key=lambda t: rrf_scores[t], reverse=True)
        print(f"  [Retriever.search] xep hang cuoi cung: {ranked_titles}")
        return [(doc_lookup[t], rrf_scores[t]) for t in ranked_titles[:k]]


def main():
    print("=" * 60)
    print("BUOC 1: Khoi tao VectorIndex + BM25Index, bo chung vao Retriever")
    print("=" * 60)
    # Khoi tao ca 2 index rieng le va bo chung vao 1 Retriever
    vector_index = VectorIndex()
    bm25_index = BM25Index()
    retriever = Retriever(vector_index, bm25_index)

    print("\n" + "=" * 60)
    print("BUOC 2: Add document -> Retriever forward toi ca 2 index")
    print("=" * 60)
    # add_document mot lan -> Retriever tu dong forward toi ca 2 index
    for chunk in CHUNKS:
        retriever.add_document(chunk)

    query = "What happened with INC-2023-Q4-011?"
    # mock embedding cho query: gan giong huong "Software Engineering"/"Cybersecurity"
    query_embedding = normalize([0.10, 0.90, 0.10])

    print(f"\nQuery: {query!r}")
    print(f"Query embedding (mock, normalized): {query_embedding}\n")

    print("=" * 60)
    print("BUOC 3: Search rieng le tren tung index (de doi chieu)")
    print("=" * 60)
    print("--- VectorIndex rieng le (semantic only) ---")
    for doc, distance in vector_index.search(query, k=4, query_embedding=query_embedding):
        print(f"  [{doc['title']}] distance={distance:.3f}")

    print("\n--- BM25Index rieng le (lexical only) ---")
    for doc, score in bm25_index.search(query, k=4):
        print(f"  [{doc['title']}] bm25_score={score:.3f}")

    print("\n" + "=" * 60)
    print("BUOC 4: Retriever hybrid — search song song + merge bang RRF")
    print("=" * 60)
    hybrid_results = retriever.search(query, k=3, k_rrf=60, query_embedding=query_embedding)
    print("\nKet qua hybrid sau RRF:")
    for doc, rrf_score in hybrid_results:
        print(f"  [{doc['title']}] rrf_score={rrf_score:.4f}")

    print("\n" + "=" * 60)
    print("BUOC 5: Goi Claude sinh cau tra loi tu chunk top-1 sau RRF")
    print("=" * 60)
    # Ghep chunk lien quan nhat (top-1 sau RRF) vao prompt, goi Claude sinh cau tra loi
    best_doc, _ = hybrid_results[0]
    print(f"  -> Dung context tu section: '{best_doc['title']}'")
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=256,
            system="Answer the user's question using ONLY the provided context.",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"<user_question>\n{query}\n</user_question>\n\n"
                        f"<report_section>\n{best_doc['content']}\n</report_section>"
                    ),
                }
            ],
        )
        print(f"\nCau tra loi cua Claude:\n{response.content[0].text}")
    except anthropic.APIError as exc:
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
