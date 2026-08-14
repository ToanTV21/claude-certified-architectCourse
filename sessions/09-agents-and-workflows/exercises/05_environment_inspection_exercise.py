"""
Environment inspection
Session: Agents and Workflows
Objective: Minh hoa pattern "read before write" -- truoc khi yeu cau Claude sua 1 file,
    phai doc noi dung hien tai va dua vao context, de Claude "quan sat" duoc structure
    hien co truoc khi de xuat thay doi, thay vi sua mu quang.
"""

from pathlib import Path  # thao tac path/file de doc lai noi dung file muc tieu

from dotenv import load_dotenv  # load bien moi truong tu file .env
import anthropic  # SDK chinh thuc de goi Claude API

load_dotenv()  # doc ANTHROPIC_API_KEY tu .env
client = anthropic.Anthropic()  # khoi tao client

MODEL = "claude-haiku-4-5"  # model re, dung cho dev/test

# File "target" gia lap -- 1 module Flask co san vai route, dong vai tro environment
# de agent "inspect" (doc) truoc khi de xuat them route moi
SAMPLE_MODULE = '''\
from flask import Flask

app = Flask(__name__)


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/users/<int:user_id>")
def get_user(user_id):
    return {"id": user_id, "name": "placeholder"}
'''


def inspect_environment(target_path: Path) -> str:
    """Buoc environment inspection: doc noi dung file HIEN TAI truoc khi lam gi khac.

    Day la buoc bat buoc phai lam truoc -- neu bo qua, Claude se de xuat code
    khong khop convention/structure co san (vd sai style route, trung ten route).
    """
    # target_path: Path -- duong dan file can inspect truoc khi sua
    return target_path.read_text(encoding="utf-8")


def propose_change(current_content: str, request: str) -> str:
    """Dua noi dung da inspect duoc lam context, roi moi yeu cau Claude de xuat thay doi.

    Vi Claude da "thay" duoc code hien co (qua current_content), no co the giu dung
    convention (vd cung kieu @app.route decorator, cung format return dict) thay vi
    doan mo hinh chung chung.
    """
    # current_content: str -- noi dung file vua doc duoc o buoc inspect_environment
    # request: str -- yeu cau thay doi cu the tu user
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": (
                    "Here is the current content of a Flask module:\n\n"
                    f"<current_file>\n{current_content}\n</current_file>\n\n"
                    f"Request: {request}\n\n"
                    "Only output the NEW route function to add (matching the existing "
                    "style/convention in current_file). Do not repeat existing code."
                ),
            }
        ],
    )
    return response.content[0].text.strip()


def main():
    # Ghi sample module ra 1 file tam trong cung thu muc de mo phong "doc file that"
    target_path = Path(__file__).parent / "_sample_flask_module.py"
    target_path.write_text(SAMPLE_MODULE, encoding="utf-8")

    try:
        # Buoc 1 (inspect): PHAI doc file truoc, khong duoc doan mo cau truc
        current_content = inspect_environment(target_path)
        print("-- Da inspect environment (noi dung file hien tai) --")
        print(current_content)

        # Buoc 2 (act dua tren ket qua inspect): de xuat route moi, dua vao context da doc
        request = "Add a new route that deletes a user by id (DELETE /users/<int:user_id>)."
        new_route = propose_change(current_content, request)
        print("\n-- De xuat thay doi (dua tren environment da inspect) --")
        print(new_route)
    except anthropic.APIError as exc:
        # bat loi API de khong crash chuong trinh
        print(f"API error: {exc}")
    finally:
        # don dep file tam sau khi chay xong
        target_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
