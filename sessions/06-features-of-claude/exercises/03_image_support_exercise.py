"""
Exercise 03: Image support
Session: Features of Claude
Objective: Gửi 1 ảnh local kèm câu hỏi cho Claude, áp dụng kỹ thuật step-by-step
methodology (thay vì hỏi trực tiếp) để tăng độ chính xác khi phân tích ảnh.
"""

import base64  # encode file ảnh sang base64 để gửi qua API
from pathlib import Path  # xử lý đường dẫn file an toàn, portable giữa các OS

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test

# Ảnh mẫu có sẵn trong repo (biểu đồ temperature) -- dùng để demo, không phải ảnh vật thể đếm được,
# nhưng vẫn minh hoạ được luồng gửi ảnh + methodology phân tích từng bước.
IMAGE_PATH = Path(__file__).resolve().parents[2] / "01-accessing-claude-api" / "temperature.png"


def encode_image(path: Path) -> str:
    """Đọc file ảnh và encode sang base64 string (yêu cầu bắt buộc của Messages API)."""
    # path: Path -- đường dẫn tới file ảnh cần gửi
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def analyze_image(image_path: Path, question: str):
    """Gửi ảnh kèm prompt có methodology từng bước (step-by-step) để tăng độ chính xác.

    Theo lesson: prompt đơn giản kiểu "Ảnh này có gì?" thường cho kết quả kém chính xác hơn
    prompt có hướng dẫn phân tích cụ thể từng bước.
    """
    image_bytes = encode_image(image_path)  # base64 string của ảnh

    return client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        # Image content block -- luôn đứng cùng cấp với text block trong 1 message
                        "type": "image",
                        "source": {
                            "type": "base64",  # gửi ảnh dạng base64 (thay vì URL)
                            "media_type": "image/png",  # phải khớp định dạng file thật
                            "data": image_bytes,
                        },
                    },
                    {"type": "text", "text": question},
                ],
            }
        ],
    )


def main():
    if not IMAGE_PATH.exists():
        print(f"Không tìm thấy ảnh mẫu tại: {IMAGE_PATH}")
        return

    # Prompt áp dụng step-by-step methodology thay vì hỏi trực tiếp 1 câu ngắn
    question = (
        "Analyze this chart image using this methodology:\n"
        "1. Identify the chart type (line, bar, scatter, etc.) and its axes.\n"
        "2. Describe the overall trend shown in the data.\n"
        "3. Note any notable peaks, dips, or outliers.\n\n"
        "Provide your final answer as a short structured summary covering all 3 points."
    )

    try:
        response = analyze_image(IMAGE_PATH, question)
        print(response.content[0].text)
    except anthropic.APIError as exc:
        # bắt lỗi API (vd ảnh quá lớn, sai media_type...) để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
