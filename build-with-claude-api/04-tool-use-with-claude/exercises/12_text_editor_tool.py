"""
Exercise 12: The Text Editor Tool
Session: Tool Use with Claude
Objective: Dung built-in Text Editor Tool cua Claude -- chi co san schema (type + name),
    phan thuc thi (doc/ghi file that) phai tu code hoan toan. Minh hoa dung Claude 4.x
    schema (text_editor_20250728 / str_replace_based_edit_tool) va implement 4 command:
    view, create, str_replace, insert -- kem sandbox path validation de chan path
    traversal, vi `path` la input do model sinh ra, khong dang tin cay.
"""

import os  # dung de resolve path an toan (tranh path traversal)
import sys  # ep stdout in UTF-8, tranh loi UnicodeEncodeError tren terminal Windows (cp1252)
from dotenv import load_dotenv  # load bien moi truong tu file .env, khong hardcode API key
import anthropic  # SDK chinh thuc de goi Claude API

sys.stdout.reconfigure(encoding="utf-8")  # cho phep print() tieng Viet co dau an toan

load_dotenv()  # doc ANTHROPIC_API_KEY tu .env
client = anthropic.Anthropic()  # khoi tao client dung chung cho ca file

MODEL = "claude-haiku-4-5"  # model re, dung cho dev/test

# Schema stub cua Text Editor Tool tren Claude 4.x -- CA type LAN name deu phai dung
# ban 4.x, khong duoc tron voi ban 3.x (text_editor_20250124 / str_replace_editor)
TEXT_EDITOR_TOOL = {
    "type": "text_editor_20250728",
    "name": "str_replace_based_edit_tool",
}

# Sandbox root -- moi thao tac file bi gioi han trong thu muc nay, khong cho ra ngoai
SANDBOX_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "_text_editor_sandbox")
)
os.makedirs(SANDBOX_ROOT, exist_ok=True)


def _safe_path(raw_path: str) -> str:
    """Resolve `path` do Claude sinh ra ve dang canonical, kiem tra van nam trong
    SANDBOX_ROOT truoc khi cho phep doc/ghi -- chan path traversal (vd '../../secret').

    `path` la model output nen khong dang tin cay, giong nhu khong duoc dung thang
    user input de tao 1 java.io.File() ma khong validate.
    """
    # noi path tuong doi vao sandbox root, roi resolve het ../ va symlink
    candidate = os.path.abspath(os.path.join(SANDBOX_ROOT, raw_path.lstrip("/\\")))
    if os.path.commonpath([SANDBOX_ROOT, candidate]) != SANDBOX_ROOT:
        raise ValueError(f"Path '{raw_path}' escapes sandbox root -- rejected.")
    return candidate


def view(path: str, view_range: list = None) -> str:
    """Xem noi dung file (co danh so dong) hoac liet ke thu muc."""
    full_path = _safe_path(path)
    if os.path.isdir(full_path):
        entries = sorted(os.listdir(full_path))
        return "\n".join(entries) if entries else "(empty directory)"

    with open(full_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start, end = 1, len(lines)  # mac dinh xem toan bo file
    if view_range:
        start, end = view_range[0], view_range[1] if view_range[1] != -1 else len(lines)

    numbered = [f"{i}: {lines[i - 1].rstrip()}" for i in range(start, end + 1)]
    return "\n".join(numbered)


def create(path: str, file_text: str) -> str:
    """Tao moi (hoac ghi de) 1 file voi noi dung file_text."""
    full_path = _safe_path(path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(file_text)
    return f"File created at {path}"


def str_replace(path: str, old_str: str, new_str: str) -> str:
    """Thay dung 1 cho khop old_str -> new_str. Loi neu khop 0 hoac >1 lan
    (giong tinh chat unique-match cua String.replace nhung phai tu kiem tra so lan khop)."""
    full_path = _safe_path(path)
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    count = content.count(old_str)
    if count == 0:
        raise ValueError("old_str not found in file.")
    if count > 1:
        raise ValueError(f"old_str is not unique -- found {count} matches.")

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.replace(old_str, new_str))
    return f"Replaced 1 occurrence in {path}"


def insert(path: str, insert_line: int, insert_text: str) -> str:
    """Chen insert_text ngay sau dong insert_line (0 = dau file)."""
    full_path = _safe_path(path)
    with open(full_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    lines.insert(insert_line, insert_text if insert_text.endswith("\n") else insert_text + "\n")

    with open(full_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return f"Inserted text after line {insert_line} in {path}"


def run_text_editor_command(tool_input: dict) -> str:
    """Dispatcher: doc command tu tool_input, goi ham thuc thi tuong ung.
    Luu y: khong xu ly command 'undo_edit' -- da bi bo tren Claude 4.x."""
    command = tool_input["command"]
    if command == "view":
        return view(tool_input["path"], tool_input.get("view_range"))
    if command == "create":
        return create(tool_input["path"], tool_input["file_text"])
    if command == "str_replace":
        return str_replace(tool_input["path"], tool_input["old_str"], tool_input["new_str"])
    if command == "insert":
        return insert(tool_input["path"], tool_input["insert_line"], tool_input["insert_text"])
    raise ValueError(f"Unsupported command: {command}")


def run_conversation(messages: list, max_turns: int = 6):
    """Vong lap tool-use tieu chuan: gui request -> neu Claude goi text editor tool
    thi thuc thi roi gui lai tool_result -> lap toi khi stop_reason != 'tool_use'."""
    response = None
    for turn in range(max_turns):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            tools=[TEXT_EDITOR_TOOL],
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"  -> {block.name} command={block.input.get('command')} path={block.input.get('path')}")
            try:
                result = run_text_editor_command(block.input)
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )
            except Exception as exc:
                # loi tu ham thuc thi (path escape, khong tim thay old_str...) -- van tra
                # tool_result nhung danh dau is_error=True de Claude tu dieu chinh
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(exc),
                        "is_error": True,
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    return response


def main():
    messages = [
        {
            "role": "user",
            "content": (
                "Create a file called notes.txt with the text 'Hello from the text editor tool.' "
                "Then view the file to confirm its contents."
            ),
        }
    ]

    try:
        final_response = run_conversation(messages)
        final_text = "\n".join(b.text for b in final_response.content if b.type == "text")
        print(f"\nFinal answer: {final_text}")
    except anthropic.APIError as exc:
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
