"""
Exercise 02: Model based grading (LLM-as-judge)
Session: Prompt Evaluation
Objective: Chấm điểm output bằng chính Claude thay vì logic code thuần,
áp dụng cho tiêu chí "mềm" (chủ quan) mà code-based grading không check được.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API
import json  # parse JSON response trả về từ grader

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model dùng để chạy prompt under test
GRADER_MODEL = "claude-haiku-4-5"  # model dùng làm giám khảo, rẻ vẫn đủ chấm tốt

# Prompt under test: 1 system prompt yêu cầu Claude trả lời như nhân viên hỗ trợ khách hàng,
# giọng điệu lịch sự, đồng cảm, không được cộc lốc.
SYSTEM_PROMPT = """
You are a customer support agent. Always respond with empathy,
acknowledge the customer's frustration if any, and keep the tone polite and helpful.
"""

# Test dataset: mỗi case là 1 tình huống khách hàng + tiêu chí chấm điểm (criteria) --
# đây là tiêu chí CHỦ QUAN (giọng điệu, sự đồng cảm), không thể check bằng substring/regex
# như code-based grading -> phải dùng model-based grading.
TEST_CASES = [
    {
        "question": "My order arrived broken and I'm really upset!",
        "criteria": "Response must acknowledge the customer's frustration/apologize, "
                     "and offer a next step (refund/replacement/support). Tone must be polite, not robotic.",
    },
    {
        "question": "How long does shipping usually take?",
        "criteria": "Response must be polite and directly answer or explain typical shipping time expectations.",
    },
]


def run_case(question: str) -> str:
    """Gửi 1 câu hỏi cho Claude dưới prompt under test, trả về text response."""
    # question: str — câu hỏi/khiếu nại của khách hàng lấy từ TEST_CASES
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=SYSTEM_PROMPT,  # system prompt định hình tone hỗ trợ khách hàng
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


def model_based_grade(question: str, output: str, criteria: str) -> dict:
    """Dùng Claude làm giám khảo (LLM-as-judge) để chấm output theo criteria chủ quan."""
    # question: str — câu hỏi gốc, để grader hiểu ngữ cảnh
    # output: str — response cần chấm điểm (do run_case() sinh ra)
    # criteria: str — tiêu chí đúng/sai mà grader phải dựa vào để chấm
    grading_prompt = f"""
    Question: {question}
    Response to grade: {output}
    Grading criteria: {criteria}

    Grade the response above against the criteria.
    Return ONLY a JSON object with fields:
    "pass" (true or false) and "reason" (one short sentence explaining why).
    """

    messages = [
        {"role": "user", "content": grading_prompt},
        {"role": "assistant", "content": "```json"},  # prefill: ép Claude viết thẳng JSON, bỏ qua câu dẫn
    ]

    response = client.messages.create(
        model=GRADER_MODEL,
        max_tokens=200,
        messages=messages,
        stop_sequences=["```"],  # dừng generation ngay khi Claude định đóng code block
    )

    # Claude có thể để lại newline thừa ở đầu/cuối -> strip() trước khi parse
    return json.loads(response.content[0].text.strip())


def main():
    passed = 0  # đếm số test case pass
    for case in TEST_CASES:
        question = case["question"]
        criteria = case["criteria"]

        try:
            output = run_case(question)  # chạy prompt under test
            grade = model_based_grade(question, output, criteria)  # chấm bằng LLM-as-judge
        except anthropic.APIError as exc:
            # lỗi API cho 1 case thì log rồi bỏ qua, không dừng cả vòng lặp
            print(f"API error on '{question}': {exc}")
            continue

        ok = grade["pass"]
        passed += ok  # True được cộng như 1
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] Q: {question}")
        print(f"  -> Response: {output.strip()}")
        print(f"  -> Grader reason: {grade['reason']}\n")

    print(f"{passed}/{len(TEST_CASES)} passed")


if __name__ == "__main__":
    main()
