"""
Exercise 05: BM25 lexical search
Session: RAG and Agentic Search
Objective: Tu cai dat thuat toan BM25 (Best Match 25) tu dau — tokenize, tinh
IDF (term hiem duoc weight cao hon), tinh BM25 score cho tung document — de
lam lexical search, bo sung cho semantic search (VectorIndex o bai 04) khi
can tim EXACT term match nhu ma incident ID.

Khong can API key ben ngoai cho phan BM25 (chi la text-matching thuan toan
hoc), chi dung Claude API o buoc cuoi de sinh cau tra loi tu context tim duoc.
"""

import math  # dung log() de tinh IDF
import re  # dung regex de tokenize text

from dotenv import load_dotenv  # load bien moi truong tu file .env
import anthropic  # SDK chinh thuc de goi Claude API

load_dotenv()  # doc ANTHROPIC_API_KEY tu .env
client = anthropic.Anthropic()  # client goi Claude

MODEL = "claude-haiku-4-5"  # model re, dung cho dev/test

# BM25 tham so chuan (gia tri pho bien trong cac thu vien nhu Elasticsearch)
K1 = 1.5  # kiem soat do bao hoa cua term frequency (term xuat hien qua nhieu lan van khong tang score vo han)
B = 0.75  # kiem soat muc do "phat" document dai (document dai de co term frequency cao hon mot cach khong cong bang)


# ============================================================
# Sample "report" — mo phong cac section co chua ma incident cu the
# ============================================================
CHUNKS = [
    {
        "title": "Financial Analysis",
        "content": (
            "Revenue grew by twelve percent this quarter. Operating costs "
            "remained stable across all business divisions."
        ),
    },
    {
        "title": "Software Engineering",
        "content": (
            "The engineering team resolved incident INC-2023-Q4-011 within "
            "four hours, restoring service to the deployment pipeline."
        ),
    },
    {
        "title": "Cybersecurity",
        "content": (
            "A follow-up review of INC-2023-Q4-011 confirmed no data was "
            "exfiltrated during the outage caused by the failed deployment."
        ),
    },
]


def tokenize(text: str) -> list:
    """Tach text thanh list token (lowercase, chi giu chu/so/dau gach ngang)."""
    # \w bao gom chu+so+underscore, them '-' de khong tach roi ma nhu INC-2023-Q4-011
    return re.findall(r"[\w-]+", text.lower())


class BM25Index:
    """Lexical search index tu viet, cai dat thuat toan BM25 tu dau."""

    def __init__(self, k1: float = K1, b: float = B):
        self.k1 = k1  # luu tham so bao hoa term frequency
        self.b = b  # luu tham so phat document dai
        self._documents = []  # list metadata goc, vd [{"content": ...}, ...]
        self._doc_tokens = []  # list token da tokenize tuong ung tung document
        self._doc_lengths = []  # so luong token cua tung document
        self._avg_doc_length = 0.0  # do dai trung binh cua tat ca document (tinh lai moi lan add)

    def add_document(self, metadata: dict) -> None:
        """Them 1 document (dict co key 'content') vao index."""
        tokens = tokenize(metadata["content"])
        self._documents.append(metadata)
        self._doc_tokens.append(tokens)
        self._doc_lengths.append(len(tokens))
        # cap nhat lai do dai trung binh sau moi lan them document
        self._avg_doc_length = sum(self._doc_lengths) / len(self._doc_lengths)
        print(
            f"  [add_document] '{metadata['title']}' -> {len(tokens)} token, "
            f"avg_doc_length={self._avg_doc_length:.2f}"
        )

    def _idf(self, term: str) -> float:
        """Inverse Document Frequency: term xuat hien o CANG IT document thi CANG quan trong."""
        # n_docs_with_term: so document co chua term nay it nhat 1 lan
        n_docs_with_term = sum(1 for tokens in self._doc_tokens if term in tokens)
        n_total = len(self._documents)
        # cong thuc IDF chuan cua BM25 (co +1 o tu va mau de tranh chia cho 0 / log(0))
        idf = math.log(
            (n_total - n_docs_with_term + 0.5) / (n_docs_with_term + 0.5) + 1
        )
        print(
            f"      [idf] term={term!r} xuat hien trong {n_docs_with_term}/{n_total} doc "
            f"-> idf={idf:.4f}"
        )
        return idf

    def _bm25_score(self, query_tokens: list, doc_index: int) -> float:
        """Tinh BM25 score cua 1 document doi voi list token cua query."""
        doc_tokens = self._doc_tokens[doc_index]
        doc_length = self._doc_lengths[doc_index]
        score = 0.0
        title = self._documents[doc_index]["title"]
        print(f"    [_bm25_score] doc='{title}' doc_length={doc_length}")

        for term in query_tokens:
            term_frequency = doc_tokens.count(term)  # so lan term xuat hien trong document nay
            if term_frequency == 0:
                print(f"      [term] {term!r} tf=0 -> bo qua")
                continue  # term khong xuat hien trong doc nay -> khong dong gop score

            idf = self._idf(term)
            # cong thuc BM25: IDF * (tf * (k1+1)) / (tf + k1 * (1 - b + b * doc_len/avg_len))
            numerator = term_frequency * (self.k1 + 1)
            denominator = term_frequency + self.k1 * (
                1 - self.b + self.b * doc_length / self._avg_doc_length
            )
            term_score = idf * (numerator / denominator)
            score += term_score
            print(
                f"      [term] {term!r} tf={term_frequency} -> term_score={term_score:.4f} "
                f"(running total={score:.4f})"
            )

        print(f"    [_bm25_score] doc='{title}' final score={score:.4f}")
        return score

    def search(self, query: str, k: int = 3) -> list:
        """Tra ve k document co BM25 score cao nhat, dang (doc, distance).

        Dung '-score' lam 'distance' de giu interface giong VectorIndex.search()
        o bai 04 (sort tang dan = lien quan nhat len dau) — xem Gotchas trong
        notes.md ve su khac biet giua BM25 score (cao=tot) va cosine distance
        (thap=tot).
        """
        query_tokens = tokenize(query)
        print(f"  [search] query={query!r} -> tokens={query_tokens}")
        scored = [
            (self._documents[i], -self._bm25_score(query_tokens, i))
            for i in range(len(self._documents))
        ]
        scored.sort(key=lambda pair: pair[1])  # score cao nhat (distance am nhat) len dau
        print(f"  [search] da sort {len(scored)} document, tra ve top {k}")
        return scored[:k]


def main():
    print("=" * 60)
    print("BUOC 1: Build BM25 index tu CHUNKS")
    print("=" * 60)
    # 1. Chunk text theo section (o day da chunk san trong CHUNKS)
    # 2. Tao BM25 store va them tung document
    store = BM25Index()
    for chunk in CHUNKS:
        store.add_document(chunk)

    print("\n" + "=" * 60)
    print("BUOC 2: Search query bang BM25")
    print("=" * 60)
    # 3. Search voi 1 query chua ma incident cu the — dung case BM25 toa sang
    query = "What happened with INC-2023-Q4-011?"
    results = store.search(query, k=3)

    print("\n" + "=" * 60)
    print("BUOC 3: Ket qua xep hang")
    print("=" * 60)
    print(f"Query: {query!r}\n")
    for doc, distance in results:
        score = -distance  # dao lai de in ra BM25 score that (cang cao cang lien quan)
        print(f"[{doc['title']}] BM25 score={score:.3f}\n  {doc['content']}\n")

    print("=" * 60)
    print("BUOC 4: Goi Claude sinh cau tra loi tu chunk lien quan nhat")
    print("=" * 60)
    # Ghep chunk lien quan nhat vao prompt, goi Claude sinh cau tra loi
    best_doc, _ = results[0]
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
