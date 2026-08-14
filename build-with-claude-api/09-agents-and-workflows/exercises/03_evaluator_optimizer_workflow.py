"""
Evaluator-Optimizer workflow
Session: Agents and Workflows
Objective: Producer sinh 1 đoạn Python docstring, Evaluator chấm điểm và cho feedback,
lặp lại (feedback loop) cho tới khi evaluator chấp nhận hoặc hết số lần thử.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API
import json  # parse JSON trả về từ evaluator (accepted/feedback)

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test
MAX_ITERATIONS = 3  # số vòng lặp tối đa, tránh loop vô hạn nếu evaluator không bao giờ accept


def produce(function_code: str, feedback: str | None = None) -> str:
    """Producer: sinh docstring cho function_code. Nếu có feedback từ vòng trước thì sửa theo đó."""
    # function_code: str — đoạn code Python cần viết docstring
    # feedback: str | None — nhận xét từ evaluator ở vòng lặp trước (None nếu là lần đầu)
    prompt = f"Write a concise docstring for this Python function:\n{function_code}"
    if feedback:
        # nếu có feedback, yêu cầu Claude sửa lại theo đúng góp ý thay vì viết mới từ đầu
        prompt += f"\n\nPrevious attempt was rejected. Feedback to address: {feedback}"
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def evaluate(function_code: str, docstring: str) -> dict:
    """Evaluator (Grader): chấm docstring theo tiêu chí, trả về dict {accepted, feedback}."""
    # function_code: str — code gốc, dùng để evaluator đối chiếu docstring có đúng/đủ không
    # docstring: str — docstring vừa được producer sinh ra, cần được chấm điểm
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=(
            "You grade Python docstrings. Criteria: must mention all params, the return "
            "value, and be under 5 lines. Reply ONLY with JSON: "
            '{"accepted": true/false, "feedback": "..."}'
        ),
        messages=[
            {
                "role": "user",
                "content": f"Function:\n{function_code}\n\nDocstring:\n{docstring}",
            }
        ],
    )
    # parse JSON trả về; nếu Claude trả sai định dạng thì coi như reject để vòng lặp tiếp tục
    try:
        return json.loads(response.content[0].text.strip())
    except json.JSONDecodeError:
        return {"accepted": False, "feedback": "Evaluator returned invalid JSON, retry."}


def evaluator_optimizer_loop(function_code: str) -> str:
    """Vòng lặp chính: producer -> evaluator -> feedback, lặp tới khi accepted hoặc hết lượt."""
    # function_code: str — code cần sinh docstring, dùng xuyên suốt các vòng lặp
    feedback = None  # feedback từ vòng trước, None ở vòng đầu tiên
    docstring = ""  # kết quả tốt nhất hiện có, trả về dù chưa được accept nếu hết lượt
    for i in range(MAX_ITERATIONS):
        docstring = produce(function_code, feedback)  # bước Producer
        verdict = evaluate(function_code, docstring)  # bước Evaluator
        print(f"-- Iteration {i + 1} --\n{docstring}\nVerdict: {verdict}\n")
        if verdict.get("accepted"):
            break  # grader đã chấp nhận -> dừng loop sớm
        feedback = verdict.get("feedback")  # đưa feedback vào vòng lặp tiếp theo
    return docstring


def main():
    # hàm mẫu chưa có docstring, dùng làm input cho workflow
    function_code = """def calculate_discount(price: float, percent: float) -> float:
    return price - (price * percent / 100)"""

    try:
        final_docstring = evaluator_optimizer_loop(function_code)
        print("-- Final accepted (or best-effort) docstring --")
        print(final_docstring)
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
