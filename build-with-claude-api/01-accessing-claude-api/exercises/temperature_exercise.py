"""
Exercise 01-03: Temperature
Module: Accessing Claude with the API
Objective: Quan sát ảnh hưởng của param `temperature` lên độ đa dạng của câu trả lời,
           bằng cách gọi Claude nhiều lần ở temperature=0.0 (deterministic) và
           temperature=1.0 (sáng tạo) với cùng 1 prompt, rồi so sánh kết quả.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client, tự đọc API key từ env

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test để tiết kiệm cost
PROMPT = "Generate a one-sentence idea for a movie."  # prompt cố định để so sánh
NUM_CALLS = 3  # số lần gọi lặp lại ở mỗi mức temperature, để thấy rõ mức độ lặp/đa dạng


def chat(messages: list, system: str | None = None, temperature: float = 1.0) -> str:
    """Gọi Claude với messages, có thể tùy chỉnh system prompt và temperature.

    messages: list[dict] — lịch sử hội thoại, mỗi phần tử {"role": ..., "content": ...}
    system: str | None — nếu có, set persona/hành vi cho Claude (top-level param, không nhét vào messages)
    temperature: float — 0.0 (gần như deterministic) đến 1.0 (đa dạng/sáng tạo hơn).
      Default 1.0 theo đúng default của Claude API (KHÔNG phải 0.7 như OpenAI).
    """
    params = {
        "model": MODEL,
        "max_tokens": 200,
        "messages": messages,
        "temperature": temperature,
    }

    # API không chấp nhận system=None -> chỉ thêm field system khi thực sự có giá trị
    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text  # lấy text từ content block đầu tiên


def run_trials(temperature: float, num_calls: int) -> None:
    """Gọi chat() lặp lại `num_calls` lần ở 1 mức temperature cố định, in ra từng kết quả
    để dễ so sánh mức độ giống/khác nhau giữa các lần gọi.
    """
    messages = [{"role": "user", "content": PROMPT}]  # tạo mới mỗi lần gọi run_trials

    for i in range(1, num_calls + 1):
        answer = chat(messages, temperature=temperature)
        print(f"  [{i}] {answer.strip()}")


def main():
    try:
        print(f"-- Temperature = 0.0 (deterministic, {NUM_CALLS} lần) --")
        # temperature thấp -> Claude gần như luôn chọn token xác suất cao nhất
        # => các câu trả lời thường giống hệt hoặc rất giống nhau
        run_trials(temperature=0.0, num_calls=NUM_CALLS)

        print(f"\n-- Temperature = 1.0 (sáng tạo, {NUM_CALLS} lần) --")
        # temperature cao -> xác suất trải đều hơn giữa các token khả dĩ
        # => các câu trả lời thường khác biệt rõ rệt về theme/nhân vật/cốt truyện
        run_trials(temperature=1.0, num_calls=NUM_CALLS)
    except anthropic.APIError as exc:
        # bắt lỗi API để in ra thay vì crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
