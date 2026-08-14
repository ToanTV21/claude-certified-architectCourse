"""
Exercise 05: Code execution and the Files API
Session: Features of Claude
Objective: Upload 1 file CSV qua Files API, dùng container_upload block để đưa
file vào môi trường code execution, rồi yêu cầu Claude tự viết + chạy code phân tích.
"""

import io  # tạo file CSV trong bộ nhớ (không cần ghi ra đĩa) để upload demo

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test

# Dữ liệu CSV mẫu nhỏ để bài tập chạy độc lập, không cần file ngoài project.
SAMPLE_CSV = (
    "user_id,tier,monthly_hours_watched,churned\n"
    "1,basic,5,1\n"
    "2,premium,40,0\n"
    "3,basic,2,1\n"
    "4,premium,55,0\n"
    "5,standard,20,0\n"
    "6,basic,3,1\n"
)


def upload_csv(csv_text: str, filename: str = "streaming.csv"):
    """Upload nội dung CSV qua Files API, trả về file metadata (chứa file_id)."""
    # csv_text: str -- nội dung CSV dạng text, sẽ được encode ra bytes để upload
    file_bytes = io.BytesIO(csv_text.encode("utf-8"))  # wrap bytes thành file-like object
    return client.beta.files.upload(
        file=(filename, file_bytes, "text/csv"),
    )


def analyze_with_code_execution(file_id: str):
    """Yêu cầu Claude phân tích file đã upload bằng code execution tool.

    Container thực thi code KHÔNG có network access -- Files API là cách duy nhất
    để đưa data vào và lấy output (vd file plot) ra khỏi container.
    """
    return client.beta.messages.create(
        model=MODEL,
        max_tokens=2000,
        betas=["code-execution-2025-05-22"],  # beta header bắt buộc để dùng code execution
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Run a short analysis on this churn dataset: compute the churn "
                            "rate per subscription tier and report which tier churns most."
                        ),
                    },
                    # container_upload: đưa file đã upload (qua file_id) vào môi trường
                    # Docker container để code execution tool đọc được.
                    {"type": "container_upload", "file_id": file_id},
                ],
            }
        ],
        tools=[
            {
                # Server tool -- không cần tự implement logic, Claude tự chạy Python trong sandbox.
                "type": "code_execution_20250522",
                "name": "code_execution",
            }
        ],
    )


def print_response(response) -> None:
    """In ra từng loại block trong response: text, code Claude chạy, và kết quả chạy code."""
    for block in response.content:
        if block.type == "text":
            print("--- TEXT ---")
            print(block.text)
        elif block.type == "server_tool_use":
            # block chứa code Claude quyết định chạy
            print("--- CODE CLAUDE CHẠY ---")
            print(block.input.get("code", ""))
        elif block.type == "code_execution_tool_result":
            # kết quả trả về sau khi code được chạy trong container
            print("--- KẾT QUẢ CHẠY CODE ---")
            print(block.content)


def main():
    try:
        file_metadata = upload_csv(SAMPLE_CSV)
        print(f"Đã upload file, file_id = {file_metadata.id}")

        response = analyze_with_code_execution(file_metadata.id)
        print_response(response)
    except anthropic.APIError as exc:
        # bắt lỗi API (vd beta feature chưa bật cho account, sai file_id...) để không crash
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
