"""
Exercise 02: Text chunking strategies
Session: RAG and Agentic Search
Objective: Cai dat 3 chien luoc chunking (size-based, structure-based,
sentence-based) tren cung 1 doan van ban mau, roi so sanh ket qua de thay
tradeoff giua cac cach chunk khac nhau.
"""

import re  # dung regex de split text theo pattern (header, dau cau...)


# Van ban mau co structure ro rang (Markdown-style headers) de test ca 3 chien luoc
SAMPLE_DOCUMENT = """## Introduction
Retrieval Augmented Generation helps Claude answer questions about large documents.
It works by breaking documents into smaller chunks first.

## Risk Factors
The company faces significant competition in the software engineering market.
Regulatory changes could also impact operations in the coming year.

## Financial Summary
Revenue grew by twelve percent this quarter. Operating costs remained stable.
"""


def chunk_by_char(text: str, chunk_size: int = 150, chunk_overlap: int = 20) -> list:
    """Size-based chunking: chia text thanh cac doan co do dai (so ky tu) bang nhau."""
    # text: str — van ban goc can chunk
    # chunk_size: int — so ky tu toi da cho moi chunk
    # chunk_overlap: int — so ky tu lap lai giua 2 chunk lien ke, giup giu context
    print(f"[chunk_by_char] Bat dau: text dai {len(text)} ky tu, chunk_size={chunk_size}, overlap={chunk_overlap}")

    chunks = []  # list chua cac chunk ket qua
    start_idx = 0  # vi tri bat dau cua chunk hien tai trong text
    step = 0

    while start_idx < len(text):
        step += 1
        # end_idx khong duoc vuot qua do dai text
        end_idx = min(start_idx + chunk_size, len(text))
        chunk_text = text[start_idx:end_idx]  # cat chuoi con tu start_idx den end_idx
        chunks.append(chunk_text)
        print(f"[chunk_by_char] Step {step}: start_idx={start_idx}, end_idx={end_idx}, do dai chunk={len(chunk_text)}")

        # chunk tiep theo bat dau lui lai chunk_overlap ky tu de tao overlap,
        # tru khi da cham het van ban (end_idx == len(text)) thi dung luon
        next_start = end_idx - chunk_overlap if end_idx < len(text) else len(text)
        print(f"[chunk_by_char]   -> next start_idx = {next_start} (lui lai {chunk_overlap} ky tu de overlap)" if end_idx < len(text) else f"[chunk_by_char]   -> da het text, dung vong lap")
        start_idx = next_start

    print(f"[chunk_by_char] Hoan tat: tong {len(chunks)} chunk(s)")
    return chunks


def chunk_by_section(document_text: str) -> list:
    """Structure-based chunking: chia theo header Markdown (dong bat dau bang '## ')."""
    # document_text: str — van ban co dinh dang Markdown voi cac header "## "
    print(f"[chunk_by_section] Bat dau: text dai {len(document_text)} ky tu, tim pattern header '\\n## '")
    pattern = r"\n## "  # pattern nhan dien 1 header moi: xuong dong + "## "
    sections = re.split(pattern, document_text)  # tach thanh list cac section
    print(f"[chunk_by_section] Tim thay {len(sections)} section(s) sau khi split")
    for i, s in enumerate(sections):
        print(f"[chunk_by_section]   Section {i}: {len(s)} ky tu, bat dau bang {s.strip()[:40]!r}...")
    return sections


def chunk_by_sentence(
    text: str, max_sentences_per_chunk: int = 5, overlap_sentences: int = 1
) -> list:
    """Sentence-based chunking: gom nhom N cau/chunk, co overlap vai cau giua cac chunk."""
    # text: str — van ban can chunk
    # max_sentences_per_chunk: int — so cau toi da trong 1 chunk
    # overlap_sentences: int — so cau lap lai giua 2 chunk lien ke
    # regex (?<=[.!?])\s+ la lookbehind: split ngay SAU dau cau (.  ! ?) va khoang trang,
    # giu nguyen dau cau o cuoi moi sentence thay vi bi cat mat
    sentences = re.split(r"(?<=[.!?])\s+", text)
    print(f"[chunk_by_sentence] Bat dau: tach duoc {len(sentences)} cau, max_sentences_per_chunk={max_sentences_per_chunk}, overlap_sentences={overlap_sentences}")
    for i, s in enumerate(sentences):
        print(f"[chunk_by_sentence]   Cau {i}: {s.strip()!r}")

    chunks = []
    start_idx = 0
    step = 0

    while start_idx < len(sentences):
        step += 1
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))
        current_chunk = sentences[start_idx:end_idx]  # slice danh sach cau
        chunks.append(" ".join(current_chunk))  # noi cac cau lai thanh 1 chunk text
        print(f"[chunk_by_sentence] Step {step}: lay cau [{start_idx}:{end_idx}] -> {len(current_chunk)} cau")

        start_idx += max_sentences_per_chunk - overlap_sentences  # lui lai de tao overlap
        if start_idx < 0:
            start_idx = 0  # phong truong hop overlap_sentences > max_sentences_per_chunk
        print(f"[chunk_by_sentence]   -> next start_idx = {start_idx}")

    print(f"[chunk_by_sentence] Hoan tat: tong {len(chunks)} chunk(s)")
    return chunks


def main():
    print("=== Size-based chunking (chunk_size=150, overlap=20) ===")
    for i, c in enumerate(chunk_by_char(SAMPLE_DOCUMENT, chunk_size=150, chunk_overlap=20)):
        print(f"[Chunk {i}] {c!r}\n")

    print("=== Structure-based chunking (split theo '## ' header) ===")
    for i, c in enumerate(chunk_by_section(SAMPLE_DOCUMENT)):
        print(f"[Chunk {i}] {c.strip()!r}\n")

    print("=== Sentence-based chunking (5 cau/chunk, overlap 1 cau) ===")
    for i, c in enumerate(chunk_by_sentence(SAMPLE_DOCUMENT, max_sentences_per_chunk=2, overlap_sentences=1)):
        print(f"[Chunk {i}] {c!r}\n")


if __name__ == "__main__":
    main()
