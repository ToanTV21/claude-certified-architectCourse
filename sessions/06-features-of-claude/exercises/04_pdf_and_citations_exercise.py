"""
Exercise 04: PDF support + Citations
Session: Features of Claude
Objective: Gửi 1 document dạng plain text (thay PDF, không cần file mẫu) kèm
citations enabled, rồi in ra câu trả lời cùng đoạn text được Claude trích dẫn.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test

# Dùng document dạng "text" thay vì upload file PDF thật, để bài tập chạy được ngay
# không cần file mẫu -- cơ chế citations hoạt động giống hệt với PDF, chỉ khác source.type
# và trả về character position thay vì page_number.
ARTICLE_TEXT = (
    "Earth's atmosphere formed roughly 4.5 billion years ago through volcanic "
    "outgassing, releasing water vapor, carbon dioxide, and nitrogen from the "
    "planet's interior. Early photosynthetic organisms called cyanobacteria "
    "began producing oxygen around 2.4 billion years ago, in an event known as "
    "the Great Oxidation Event, which fundamentally transformed the "
    "atmosphere's composition."
)


def ask_with_citations(question: str):
    """Gửi document dạng text kèm citations enabled, hỏi 1 câu về nội dung đó."""
    # question: str -- câu hỏi cụ thể muốn Claude trả lời dựa trên ARTICLE_TEXT
    return client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        # Document content block -- dùng cho cả PDF và plain text.
                        # Với PDF: source.type = "base64", media_type = "application/pdf".
                        # Với text: source.type = "text", media_type = "text/plain" (như dưới đây).
                        "type": "document",
                        "source": {
                            "type": "text",
                            "media_type": "text/plain",
                            "data": ARTICLE_TEXT,
                        },
                        "title": "earth_atmosphere_article",  # tên hiển thị trong citation
                        "citations": {"enabled": True},  # bật tracking nguồn trích dẫn
                    },
                    {"type": "text", "text": question},
                ],
            }
        ],
    )


def print_citations(response) -> None:
    """Duyệt qua các content block, in text + citation đi kèm (nếu có)."""
    for block in response.content:
        if block.type != "text":
            continue
        print(block.text)
        # Khi citations được bật, mỗi text block có thể kèm 1 list `citations`
        # gồm các đoạn text gốc trong document đã hỗ trợ cho câu trả lời này.
        citations = getattr(block, "citations", None) or []
        for citation in citations:
            # citation.cited_text: đoạn text chính xác trong document nguồn
            # citation.start_char_index / end_char_index: vị trí ký tự (thay vì page_number với PDF)
            print(f"  [nguồn]: \"{citation.cited_text}\"")


def main():
    question = "When did the Great Oxidation Event happen and what caused it?"
    try:
        response = ask_with_citations(question)
        print_citations(response)
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
