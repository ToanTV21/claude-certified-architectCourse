"""
Exercise on prompting
Session: Prompt Engineering Techniques
Objective: Compare a vague prompt vs. a clear, specific, XML-structured prompt with examples.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test

VAGUE_PROMPT = "Summarize this."  # prompt mơ hồ — không nói rõ format, độ dài, tone

# Prompt tốt: dùng XML tag để tách rõ task / example / input, kèm 1 ví dụ mẫu (few-shot)
GOOD_PROMPT = """\
<task>
Summarize the text below in exactly 2 bullet points, focused on the main
conclusion and one supporting detail. Use plain English, no jargon.
</task>

<example>
<input>Sales grew 20% in Q2 due to the new pricing tier, though churn also rose 5%.</input>
<output>
- Q2 sales grew 20%, driven by the new pricing tier.
- Churn also rose 5% in the same period, a risk to watch.
</output>
</example>

<text>
{text}
</text>
"""

# Đoạn văn bản chung dùng để test cả 2 prompt (vague vs good)
TEXT = (
    "The team migrated the auth service to a new token format last month. "
    "Login latency dropped by 40%, but two legacy clients failed to parse the "
    "new tokens and required a hotfix."
)


def ask(prompt: str) -> str:
    """Gửi 1 prompt bất kỳ cho Claude, trả về text response."""
    # prompt: str — nội dung prompt đầy đủ (đã format sẵn text vào nếu cần)
    response = client.messages.create(
        model=MODEL,
        max_tokens=256,  # đủ cho vài câu tóm tắt
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def main():
    try:
        print("-- Vague prompt --")
        # nối vague prompt với text thô -> Claude tự đoán format, có thể không nhất quán
        print(ask(f"{VAGUE_PROMPT}\n\n{TEXT}"))

        print("\n-- Clear, structured prompt with example --")
        # .format(text=TEXT) chèn TEXT vào placeholder {text} trong GOOD_PROMPT
        print(ask(GOOD_PROMPT.format(text=TEXT)))
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
