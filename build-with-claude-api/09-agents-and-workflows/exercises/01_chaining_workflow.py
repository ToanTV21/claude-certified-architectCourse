"""
Chaining workflows
Session: Agents and Workflows
Objective: Chain 2 Claude calls — draft an answer, then critique-and-revise it.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test


def call(prompt: str) -> str:
    """Gọi Claude 1 lần với 1 prompt độc lập (không giữ history), trả về text."""
    # prompt: str — nội dung gửi cho Claude ở bước hiện tại trong chain
    response = client.messages.create(
        model=MODEL, max_tokens=300, messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def main():
    topic = "Explain why prompt caching reduces cost for repeated system prompts."

    try:
        # Bước 1 (draft): yêu cầu Claude viết câu trả lời ngắn ban đầu
        draft = call(f"Write a short, 3-sentence answer to: {topic}")
        print("-- Draft --")
        print(draft)

        # Bước 2 (critique + revise): đưa draft ở bước 1 làm input, yêu cầu Claude tự phê bình rồi viết lại
        revised = call(
            f"Here is a draft answer:\n{draft}\n\n"
            "Critique it for accuracy and clarity, then rewrite an improved "
            "3-sentence version. Output ONLY the improved version."
        )
        print("\n-- Revised --")
        print(revised)
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
