"""
Exercise 05: Model based grading + Code based grading (kết hợp)
Session: Prompt Evaluation
Objective: Lắp grading logic THẬT vào pipeline đã xây ở exercise 04 (thay cho
score = 10 hardcode). Kết hợp 2 loại grader cho prompt "viết code AWS":
  - Code-based grader: check syntax hợp lệ (Python/JSON/Regex) bằng ast/json/re
  - Model-based grader: dùng Claude chấm "task following" (có giải quyết đúng
    yêu cầu không), yêu cầu trả kèm strengths/weaknesses/reasoning để tránh
    hiện tượng model có xu hướng chấm điểm an toàn ở khoảng giữa (~6/10) khi
    chỉ hỏi mỗi "score".
Điểm cuối cùng = trung bình cộng (model_score + syntax_score) / 2.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API
import json  # parse JSON response của grader + validate JSON output
import ast  # parse thử code Python để check syntax hợp lệ
import re  # compile thử regex để check syntax hợp lệ
from statistics import mean  # tính điểm trung bình toàn dataset

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung

MODEL = "claude-haiku-4-5"  # model chạy prompt under test
GRADER_MODEL = "claude-haiku-4-5"  # model làm giám khảo, rẻ vẫn đủ chấm tốt

# Dataset rút gọn, có kèm field "format" để code grader biết dùng validator nào
# -- đúng yêu cầu "Dataset Format Requirements" trong bài học. Trong thực tế,
# field "format" này nên được sinh kèm luôn ở exercises/03_generate_test_dataset_exercise.py.
TEST_CASES = [
    {
        "task": "Write a Python function that validates an AWS IAM username "
                "(1-64 chars, letters/digits/+=,.@_- only).",
        "format": "python",
    },
    {
        "task": "Write a JSON config object for an S3 bucket with versioning enabled "
                "and a lifecycle rule that expires objects after 30 days.",
        "format": "json",
    },
    {
        "task": "Write a regex that matches a valid AWS ARN "
                "(e.g. arn:aws:s3:::my-bucket).",
        "format": "regex",
    },
]


def add_user_message(messages: list, text: str) -> None:
    """Thêm 1 message role=user vào lịch sử hội thoại."""
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages: list, text: str) -> None:
    """Thêm 1 message role=assistant vào lịch sử hội thoại (dùng để prefill)."""
    messages.append({"role": "assistant", "content": text})


def run_prompt(test_case: dict) -> str:
    """Prompt under test -- yêu cầu Claude CHỈ trả code thô, không giải thích.

    So với exercise 04, prompt đã được siết chặt thêm 2 instruction quan trọng
    (đúng phần "Improving Prompt Clarity" trong bài học) để dễ chấm bằng code
    grader hơn: không được có comment/giải thích, chỉ trả đúng 1 loại code.
    """
    # test_case: dict — 1 phần tử của TEST_CASES, có field "task"
    prompt = f"""
Please provide a solution to the following task:
{test_case["task"]}

- Respond only with Python, JSON, or a plain Regex
- Do not add any comments or commentary or explanation
"""
    messages = []
    add_user_message(messages, prompt)
    # Prefill "```code" -- không cần biết trước là Python/JSON/Regex, Claude sẽ
    # tự viết thẳng nội dung code vào trong code block này.
    add_assistant_message(messages, "```code")

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=messages,
        stop_sequences=["```"],  # dừng ngay khi Claude định đóng code block
    )
    return response.content[0].text.strip()


def validate_json(text: str) -> int:
    """Thử parse text bằng json.loads -- parse được thì syntax hợp lệ."""
    # text: str — output cần kiểm tra, kỳ vọng là 1 JSON object/array
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0


def validate_python(text: str) -> int:
    """Thử parse text bằng ast.parse -- parse được thì syntax Python hợp lệ."""
    # text: str — output cần kiểm tra, kỳ vọng là code Python
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0


def validate_regex(text: str) -> int:
    """Thử compile text bằng re.compile -- compile được thì syntax regex hợp lệ."""
    # text: str — output cần kiểm tra, kỳ vọng là 1 pattern regex
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0


def grade_syntax(output: str, test_case: dict) -> int:
    """Code grader: dispatch tới đúng validator theo field 'format' của test case."""
    # output: str — response của prompt under test
    # test_case: dict — cần field "format" để biết nên validate kiểu gì
    validators = {
        "python": validate_python,
        "json": validate_json,
        "regex": validate_regex,
    }
    validator = validators[test_case["format"]]
    return validator(output)


def grade_by_model(test_case: dict, output: str) -> dict:
    """Model grader: chấm 'task following' -- Claude có giải quyết đúng task không.

    Yêu cầu trả kèm strengths/weaknesses/reasoning trước khi cho score --
    đây là điểm mấu chốt trong bài học: nếu chỉ hỏi mỗi "score", model có xu
    hướng chấm an toàn quanh mức 6/10; buộc phải giải thích lý do trước giúp
    điểm số phản ánh đúng chất lượng thật hơn.
    """
    # test_case: dict — chứa "task" gốc để grader biết yêu cầu là gì
    # output: str — response của prompt under test cần chấm
    eval_prompt = f"""
You are an expert code reviewer. Evaluate this AI-generated solution.

Task: {test_case["task"]}
Solution: {output}

Provide your evaluation as a structured JSON object with:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your assessment
- "score": A number between 1-10
"""
    messages = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```json")  # prefill: ép Claude viết thẳng JSON

    response = client.messages.create(
        model=GRADER_MODEL,
        max_tokens=500,
        messages=messages,
        stop_sequences=["```"],  # dừng ngay khi Claude định đóng code block
    )
    return json.loads(response.content[0].text.strip())


def run_test_case(test_case: dict) -> dict:
    """Chạy prompt under test, chấm bằng cả 2 grader, gộp điểm = trung bình cộng."""
    # test_case: dict — 1 phần tử của TEST_CASES cần chạy eval
    output = run_prompt(test_case)

    model_grade = grade_by_model(test_case, output)  # grader mềm: task following
    model_score = model_grade["score"]

    syntax_score = grade_syntax(output, test_case)  # grader cứng: syntax hợp lệ

    # Trọng số bằng nhau cho cả 2 tiêu chí -- có thể điều chỉnh tuỳ use case
    # (vd ưu tiên syntax hơn nếu output sẽ chạy trực tiếp trong production).
    score = (model_score + syntax_score) / 2

    return {
        "output": output,
        "test_case": test_case,
        "model_reasoning": model_grade["reasoning"],
        "syntax_score": syntax_score,
        "model_score": model_score,
        "score": score,
    }


def run_eval(dataset: list) -> list:
    """Lặp qua dataset, chạy + chấm từng case, gom kết quả. Lỗi 1 case không dừng cả vòng lặp."""
    # dataset: list[dict] — toàn bộ tập test case (TEST_CASES)
    results = []
    for test_case in dataset:
        try:
            result = run_test_case(test_case)
        except anthropic.APIError as exc:
            print(f"API error on task '{test_case['task']}': {exc}")
            continue
        results.append(result)
    return results


def main():
    results = run_eval(TEST_CASES)

    for r in results:
        print(f"Task: {r['test_case']['task']}")
        print(f"  Output: {r['output'][:80]}...")
        print(f"  syntax_score={r['syntax_score']}  model_score={r['model_score']}  "
              f"final_score={r['score']}")
        print(f"  Reasoning: {r['model_reasoning']}\n")

    average_score = mean(r["score"] for r in results)
    print(f"Average score: {average_score}")


if __name__ == "__main__":
    main()
