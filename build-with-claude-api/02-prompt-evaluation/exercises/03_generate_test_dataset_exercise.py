"""
Exercise 03: Generating test datasets
Session: Prompt Evaluation
Objective: Dùng chính Claude (model rẻ - Haiku) để tự động sinh ra 1 eval dataset
cho prompt "viết code AWS" (Python function / JSON config / Regex), thay vì phải
tự tay nghĩ ra từng test case. Dataset sinh ra sẽ được lưu ra file JSON để tái
sử dụng ở bước "Running the eval" (không cần generate lại mỗi lần chạy eval).
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API
import json  # parse JSON trả về từ Claude + ghi dataset ra file

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung

# Dùng Haiku để generate dataset: đây chỉ là bước sinh dữ liệu test, không phải
# prompt-under-test, nên ưu tiên model rẻ + nhanh (theo quy ước MODEL_DEV trong CLAUDE.md)
MODEL = "claude-haiku-4-5"

DATASET_FILE = "dataset.json"  # nơi lưu lại dataset đã generate, dùng lại cho bước eval


def add_user_message(messages: list, text: str) -> None:
    """Thêm 1 message role=user vào lịch sử hội thoại."""
    # messages: list — mảng messages đang xây dựng (giống format client.messages.create)
    # text: str — nội dung message của user
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages: list, text: str) -> None:
    """Thêm 1 message role=assistant vào lịch sử hội thoại (dùng để prefill)."""
    # text: str — nội dung message giả lập Claude đã nói, dùng để ép format output
    messages.append({"role": "assistant", "content": text})


def chat(messages: list, system: str = None, temperature: float = 1.0, stop_sequences: list = None) -> str:
    """Helper gọi Claude dùng chung cho cả session này (giống pattern ở bài 01/02)."""
    # messages: list — toàn bộ lịch sử hội thoại cần gửi
    # system: str | None — system prompt tùy chọn (None thì bỏ qua, không gửi field rỗng)
    # temperature: float — độ ngẫu nhiên, mặc định 1.0 theo đúng default của API
    #   (KHÔNG tự ý đổi thành 0.7 — đây là gotcha đã ghi trong CLAUDE.md)
    # stop_sequences: list[str] | None — chuỗi dừng generation, dùng để ép output JSON sạch
    if stop_sequences is None:
        stop_sequences = []

    params = {
        "model": MODEL,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
    }
    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    response = client.messages.create(**params)
    return response.content[0].text


def generate_dataset(num_cases: int = 3) -> list[dict]:
    """Yêu cầu Claude tự sinh ra 1 danh sách task AWS-related dùng làm eval dataset.

    Mỗi task mô tả 1 việc mà prompt-under-test phải giải quyết bằng cách viết ra
    Python function / JSON object / Regex — đúng 3 loại output mà prompt gốc hỗ trợ.
    """
    # num_cases: int — số lượng test case muốn Claude sinh ra
    prompt = f"""
Generate an evaluation dataset for a prompt evaluation. The dataset will be used
to evaluate prompts that generate Python, JSON, or Regex specifically for
AWS-related tasks. Generate an array of JSON objects, each representing a task
that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
  {{
    "task": "Description of task"
  }},
  ...additional
]
```

- Focus on tasks that can be solved by writing a single Python function,
  a single JSON object, or a single regex
- Focus on tasks that do not require writing much code

Please generate {num_cases} objects.
"""

    messages = []
    add_user_message(messages, prompt)
    # Prefill "```json" để Claude viết thẳng vào JSON array, bỏ qua câu dẫn kiểu
    # "Here is the dataset:" -- kỹ thuật structured output đã học ở Session 01.
    add_assistant_message(messages, "```json")

    # stop_sequences=["```"] để dừng ngay khi Claude định đóng code block,
    # tránh phải cắt bỏ phần markdown thừa bằng tay.
    text = chat(messages, stop_sequences=["```"])

    return json.loads(text)


def save_dataset(dataset: list[dict], path: str = DATASET_FILE) -> None:
    """Lưu dataset ra file JSON để dùng lại ở bước eval, không cần generate lại mỗi lần chạy."""
    # dataset: list[dict] — danh sách task vừa generate được
    # path: str — đường dẫn file JSON đích
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)  # ensure_ascii=False để giữ nguyên ký tự có dấu nếu có


def main():
    dataset = generate_dataset(num_cases=3)

    print(f"Generated {len(dataset)} test cases:\n")
    for i, item in enumerate(dataset, start=1):
        print(f"{i}. {item['task']}")

    save_dataset(dataset)
    print(f"\nSaved dataset to {DATASET_FILE}")


if __name__ == "__main__":
    main()
