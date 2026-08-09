"""
Exercise on prompt evals
Session: Prompt Evaluation
Objective: Run a tiny eval — a test dataset, a prompt under test, and code-based grading.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test

# Test dataset: (input, expected_substring)
# Mỗi tuple là 1 test case: câu hỏi gửi cho Claude + chuỗi con kỳ vọng xuất hiện trong response
TEST_CASES = [
    ("What is 2 + 2?", "4"),
    ("What is the capital of Japan?", "Tokyo"),
    ("What is the capital of Vietnam?", "Hanoi"),
]


def run_case(question: str) -> str:
    """Gửi 1 câu hỏi cho Claude, trả về text response (đây là 'prompt under test')."""
    # question: str — nội dung câu hỏi lấy từ TEST_CASES
    response = client.messages.create(
        model=MODEL,
        max_tokens=100,  # câu trả lời ngắn nên giới hạn thấp cho nhanh/rẻ
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


def code_based_grade(output: str, expected_substring: str) -> bool:
    """Chấm điểm bằng code đơn giản: kiểm tra expected_substring có nằm trong output không."""
    # output: str — text Claude trả về
    # expected_substring: str — chuỗi con kỳ vọng có mặt trong output (so sánh không phân biệt hoa/thường)
    return expected_substring.lower() in output.lower()


def main():
    passed = 0  # đếm số test case pass
    for question, expected in TEST_CASES:
        try:
            output = run_case(question)  # gọi API lấy response cho từng câu hỏi
        except anthropic.APIError as exc:
            # lỗi API cho 1 case thì log rồi bỏ qua, không dừng cả vòng lặp
            print(f"API error on '{question}': {exc}")
            continue

        ok = code_based_grade(output, expected)  # chấm điểm bằng hàm grader ở trên
        passed += ok  # True được cộng như 1
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] Q: {question}\n  -> {output.strip()}")

    print(f"\n{passed}/{len(TEST_CASES)} passed")


if __name__ == "__main__":
    main()
