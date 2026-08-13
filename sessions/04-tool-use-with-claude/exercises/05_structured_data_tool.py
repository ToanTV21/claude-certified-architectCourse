"""
Exercise 05: Tools for Structured Data
Session: Tool Use with Claude
Objective: Dùng tool + tool_choice ép buộc để lấy dữ liệu có cấu trúc (JSON) đáng tin cậy
    từ 1 đoạn text tự do, thay vì dùng kỹ thuật pre-fill + stop sequence. Khác với luồng
    tool use thông thường, KHÔNG cần gửi tool_result quay lại vì mục đích chỉ là extract.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env, không hardcode API key
import anthropic  # SDK chính thức để gọi Claude API
from anthropic.types import ToolParam  # wrap dict schema để bắt lỗi type sớm ở dev-time

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client dùng chung cho cả file

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test


def add_user_message(messages: list, content) -> None:
    """Thêm 1 user message vào messages list. content ở đây luôn là str (đoạn text cần extract)."""
    messages.append({"role": "user", "content": content})


# input_schema ở đây chính là "hình dạng" dữ liệu muốn Claude trả về, không phải mô tả
# tham số cho 1 hành động thực thi như các tool thông thường -> tên gọi theo convention
# "<ten_tool>_schema" vẫn giữ nguyên để nhất quán với các exercise khác
extract_contact_info_schema = ToolParam(
    {
        "name": "extract_contact_info",
        "description": (
            "Extract structured contact information (name, email, phone, company) from "
            "a piece of unstructured text such as an email signature."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Full name of the contact."},
                "email": {"type": "string", "description": "Email address, empty if not present."},
                "phone": {"type": "string", "description": "Phone number, empty if not present."},
                "company": {"type": "string", "description": "Company name, empty if not present."},
            },
            "required": ["name", "email", "phone", "company"],
        },
    }
)


def extract_contact(raw_text: str) -> dict:
    """Gọi Claude, ép nó luôn trả về dữ liệu qua tool extract_contact_info."""
    messages = []
    add_user_message(messages, raw_text)

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=messages,
        tools=[extract_contact_info_schema],
        # ép Claude LUÔN gọi đúng tool này, không được trả lời bằng text thường
        # và không được tự chọn tool khác (khác với tool_choice mặc định "auto")
        tool_choice={"type": "tool", "name": "extract_contact_info"},
    )

    # vì tool_choice ép buộc nên block đầu tiên chắc chắn là tool_use — lấy thẳng dữ liệu
    # có cấu trúc từ "input", KHÔNG cần gửi tool_result quay lại như luồng tool use thường
    tool_use_block = response.content[0]
    return tool_use_block.input


def main():
    # vài đoạn text thô, định dạng không đồng nhất, để kiểm tra độ tin cậy của extraction
    samples = [
        "Hi, I'm John Tran, Senior Engineer at FPT Software. "
        "Reach me at john.tran@fpt.com or call 090-123-4567.",
        "Contact: Sarah Nguyen (sarah.nguyen@example.co.jp) - Marketing Lead, ABC Corp.",
    ]

    for text in samples:
        try:
            data = extract_contact(text)
            print(f"Input: {text[:50]}...")
            print(f"Extracted: {data}\n")
        except anthropic.APIError as exc:
            # bắt lỗi API riêng cho từng sample, không dừng cả vòng lặp
            print(f"API error: {exc}")


if __name__ == "__main__":
    main()
