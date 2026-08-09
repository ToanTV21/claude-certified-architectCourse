"""
Exercise 05: Tools for Structured Data
Session: Tool Use with Claude
Objective: Dung tool + tool_choice ep buoc de lay du lieu co cau truc (JSON)
dang tin cay tu 1 doan text tu do, thay vi dung ky thuat pre-fill + stop sequence.
"""

from dotenv import load_dotenv  # doc ANTHROPIC_API_KEY tu file .env
import anthropic  # SDK chinh thuc cua Anthropic

load_dotenv()  # nap bien moi truong tu .env
client = anthropic.Anthropic()  # tao client, tu doc key tu env

MODEL = "claude-haiku-4-5"  # dung haiku cho bai tap dev/test

# input_schema o day chinh la "hinh dang" du lieu ma minh muon Claude tra ve,
# khong phai mo ta tham so cho 1 hanh dong thuc thi nhu cac tool thong thuong
EXTRACT_CONTACT_SCHEMA = {
    "name": "extract_contact_info",
    "description": (
        "Extract structured contact information (name, email, phone, company) "
        "from a piece of unstructured text such as an email signature."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Ho ten day du cua nguoi lien he"},
            "email": {"type": "string", "description": "Dia chi email, rong neu khong co"},
            "phone": {"type": "string", "description": "So dien thoai, rong neu khong co"},
            "company": {"type": "string", "description": "Ten cong ty, rong neu khong co"},
        },
        "required": ["name", "email", "phone", "company"],
    },
}


def extract_contact(raw_text: str) -> dict:
    """Goi Claude, ep no luon tra ve du lieu qua tool extract_contact_info."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        tools=[EXTRACT_CONTACT_SCHEMA],
        # ep Claude LUON goi dung tool nay, khong duoc tra loi bang text thuong
        # va khong duoc tu chon tool khac (khac voi tool_choice mac dinh "auto")
        tool_choice={"type": "tool", "name": "extract_contact_info"},
        messages=[{"role": "user", "content": raw_text}],
    )

    # vi tool_choice ep buoc nen block dau tien chac chan la tool_use,
    # lay thang du lieu co cau truc tu "input" - khong can gui tool_result quay lai
    tool_use_block = response.content[0]
    return tool_use_block.input


def main():
    # vai doan text tho, dinh dang khong dong nhat, de kiem tra do tin cay cua extraction
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
            # bat loi API rieng cho tung sample, khong dung ca vong lap
            print(f"API error: {exc}")


if __name__ == "__main__":
    main()
