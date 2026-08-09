"""
Exercise 04: Running the eval
Session: Prompt Evaluation
Objective: Xây dựng core evaluation pipeline gồm 3 hàm (run_prompt, run_test_case,
run_eval), chạy toàn bộ dataset.json (đã sinh ở exercise 03) qua prompt under test,
và thu về kết quả có cấu trúc (output + test_case + score). Grading logic thật
chưa cài ở bước này -- score đang hardcode = 10, sẽ được thay bằng grader thật
ở bài học tiếp theo (Model/Code based grading).
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API
import json  # đọc dataset.json và in kết quả dạng JSON

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test (đúng quy ước MODEL_DEV trong CLAUDE.md)

DATASET_FILE = "dataset.json"  # file dataset đã sinh ra ở exercises/03_generate_test_dataset_exercise.py


def add_user_message(messages: list, text: str) -> None:
    """Thêm 1 message role=user vào lịch sử hội thoại."""
    # messages: list — mảng messages đang xây dựng (format giống client.messages.create)
    # text: str — nội dung message của user
    messages.append({"role": "user", "content": text})


def chat(messages: list) -> str:
    """Helper gọi Claude, trả về text response — dùng chung cho toàn bộ pipeline."""
    # messages: list — toàn bộ lịch sử hội thoại cần gửi cho Claude
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=messages,
    )
    return response.content[0].text


def run_prompt(test_case: dict) -> str:
    """Merges the prompt and test case input, then returns the result.

    Đây là 'prompt under test' -- prompt này chính là thứ đang được eval,
    không phải logic pipeline. Cố tình để ĐƠN GIẢN, chưa có formatting
    instruction gì -- nên Claude sẽ trả lời khá verbose (dài dòng). Việc
    này sẽ được tinh chỉnh dần khi iterate prompt ở các bước sau.
    """
    # test_case: dict — 1 phần tử của dataset, có field "task" mô tả yêu cầu cần giải quyết
    prompt = f"""
Please solve the following task:

{test_case["task"]}
"""

    messages = []
    add_user_message(messages, prompt)
    output = chat(messages)
    return output


def run_test_case(test_case: dict) -> dict:
    """Calls run_prompt, then grades the result.

    Score đang hardcode = 10 -- grading logic thật (code-based/model-based,
    xem notes.md phần "Code based grading" / "Model based grading") sẽ được
    lắp vào sau. Để test thông suốt cả pipeline trước khi lo tới việc
    chấm điểm cho đúng.
    """
    # test_case: dict — 1 phần tử của dataset cần chạy eval
    output = run_prompt(test_case)  # chạy prompt under test cho case này

    # TODO - Grading: thay hardcode bằng grader thật ở bài tiếp theo
    score = 10

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
    }


def run_eval(dataset: list[dict]) -> list[dict]:
    """Loads the dataset and calls run_test_case with each case.

    Lặp qua toàn bộ dataset, chạy từng test case, gom kết quả vào 1 list.
    Bắt lỗi API riêng cho từng case để 1 case lỗi không làm dừng cả vòng lặp.
    """
    # dataset: list[dict] — toàn bộ tập test case đọc từ dataset.json
    results = []  # gom kết quả của tất cả test case

    for test_case in dataset:
        try:
            result = run_test_case(test_case)
        except anthropic.APIError as exc:
            # lỗi API (timeout, rate limit...) cho 1 case thì log rồi bỏ qua case đó
            print(f"API error on task '{test_case['task']}': {exc}")
            continue
        results.append(result)

    return results


def main():
    # Load dataset đã sinh ra từ exercises/03_generate_test_dataset_exercise.py
    # (chạy file 03 trước để tạo dataset.json trong cùng thư mục exercises/)
    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Loaded {len(dataset)} test case(s) from {DATASET_FILE}\n")

    # Chạy pipeline -- lần chạy đầu có thể mất ~30s dù dùng Haiku, vì gọi API
    # tuần tự cho từng case (tối ưu song song sẽ học ở phần sau)
    results = run_eval(dataset)

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
