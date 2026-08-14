"""
Exercise 11: The Web Search Tool
Session: Tool Use with Claude
Objective: Dung built-in Web Search Tool cua Claude -- khong can tu code implementation
    (khac voi tool tu dinh nghia o cac bai truoc). Chi khai bao schema, Claude tu chay
    search that va tu ghep ket qua vao response. Minh hoa cach doc ket qua tra ve gom
    4 loai block: text, tool_use (query da search), web_search_tool_result, va citation --
    dong thoi dung allowed_domains de gioi han nguon tin cay (vd chi lay tu nih.gov).
"""

import sys  # ep stdout in UTF-8, tranh loi UnicodeEncodeError tren terminal Windows (cp1252)
from dotenv import load_dotenv  # load bien moi truong tu file .env, khong hardcode API key
import anthropic  # SDK chinh thuc de goi Claude API

sys.stdout.reconfigure(encoding="utf-8")  # cho phep print() tieng Viet co dau an toan

load_dotenv()  # doc ANTHROPIC_API_KEY tu .env
client = anthropic.Anthropic()  # khoi tao client dung chung cho ca file

MODEL = "claude-haiku-4-5"  # model re, dung cho dev/test


# Schema cua Web Search Tool -- day la built-in tool, khong can dinh nghia input_schema
# vi Claude/Anthropic da tu quan ly toan bo logic search phia server cua ho.
WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",  # type co dinh cho web search tool (theo version)
    "name": "web_search",
    "max_uses": 3,  # gioi han toi da 3 lan Claude duoc phep goi search trong 1 request
    # gioi han search chi trong domain NIH.gov -- dam bao thong tin y te/suc khoe
    # co kiem chung khoa hoc thay vi lay tu web chung chung khong ro nguon
    "allowed_domains": ["nih.gov"],
}


def run_web_search_query(question: str):
    """Gui 1 cau hoi can thong tin moi/thoi su cho Claude, kem theo Web Search Tool.

    Khac voi tool tu dinh nghia (get_current_datetime, add_duration_to_datetime...):
    o day KHONG can vong lap tool_use -> tool_result thu cong. Claude tu chay search
    va tra ve response da hoan chinh trong 1 lan goi client.messages.create() duy nhat
    (co the Claude tu goi search nhieu lan ben trong, toi da theo max_uses).
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        tools=[WEB_SEARCH_TOOL],
        messages=[{"role": "user", "content": question}],
    )
    return response


def print_response_blocks(response) -> None:
    """Duyet qua response.content va phan loai tung block theo type -- minh hoa 4 loai
    block co the xuat hien khi dung Web Search Tool: text / tool_use / web_search_tool_result
    (chua cac search result con) / va citation (gan trong text block neu co)."""
    for block in response.content:
        if block.type == "text":
            print(f"[TEXT] {block.text}")
            # neu block text co citations (trich dan nguon), in ra rieng de de theo doi
            citations = getattr(block, "citations", None)
            if citations:
                for citation in citations:
                    # cac field co the khac nhau tuy loai citation, .get an toan hon getattr o day
                    title = getattr(citation, "title", None)
                    url = getattr(citation, "url", None)
                    print(f"    -> citation: {title} ({url})")

        elif block.type == "server_tool_use":
            # day la "tool_use" block nhung do server (Anthropic) tu thuc thi, khong
            # can minh chay code gi ca -- chi de log lai Claude da search query gi
            print(f"[SEARCH QUERY] {block.input.get('query')}")

        elif block.type == "web_search_tool_result":
            # ket qua tra ve tu lan search do -- moi item la 1 trang tim duoc
            print("[SEARCH RESULTS]")
            for result in block.content:
                title = getattr(result, "title", "(no title)")
                url = getattr(result, "url", "(no url)")
                print(f"    - {title} | {url}")

        else:
            print(f"[OTHER BLOCK: {block.type}]")


def main():
    question = (
        "What does NIH say about the recommended amount of weekly aerobic exercise "
        "for adults? Cite your sources."
    )

    try:
        response = run_web_search_query(question)
        print_response_blocks(response)
    except anthropic.APIError as exc:
        # bat loi API de khong crash chuong trinh (vd rate limit, network...)
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
