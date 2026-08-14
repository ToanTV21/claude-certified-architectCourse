"""
Agent SDK overview
Session: Agents and Workflows
Objective: Minh hoa cach dung Claude Agent SDK (khac voi Messages API/Client SDK dung o
    cac exercise truoc) de chay 1 agent tim va sua bug trong code, tai su dung san agent
    loop + tool + context management cua Claude Code -- khong phai tu viet tool loop nhu
    khi goi truc tiep anthropic.Anthropic().messages.create().

    Luu y: file nay can package rieng `claude-agent-sdk` (khong phai `anthropic`), cai bang:
        pip install claude-agent-sdk
    va can co Claude Code CLI da cai san tren may (Agent SDK chay ben duoi bang Claude Code).
"""

import asyncio  # Agent SDK dung API bat dong bo (async/await)

from dotenv import load_dotenv  # load ANTHROPIC_API_KEY tu .env, khong hardcode

# claude_agent_sdk: package rieng cua Agent SDK, KHONG phai `anthropic`
# - query(): ham chinh, gui 1 prompt va nhan ve stream message tu agent loop
# - ClaudeAgentOptions: cau hinh agent (model, tool duoc phep dung, system prompt...)
from claude_agent_sdk import ClaudeAgentOptions, query

load_dotenv()  # doc ANTHROPIC_API_KEY tu .env

# Model dung cho dev/test theo convention cua project -- Agent SDK cung nhan model id
# giong Messages API (vd "claude-haiku-4-5")
MODEL = "claude-haiku-4-5"


def build_options() -> ClaudeAgentOptions:
    """Cau hinh agent: gioi han tool duoc dung va them system prompt rieng.

    allowed_tools chi liet ke tool GENERIC (Read, Edit, Bash) dung theo dung nguyen tac
    "tool nen du tru tuong" da hoc o muc 8 (Agents and tools) -- khong can tool rieng
    kieu "fix_bug" hay "find_bug".
    """
    return ClaudeAgentOptions(
        model=MODEL,
        # allowed_tools: list[str] -- ten tool built-in duoc phep dung, giong tool set
        # cua chinh Claude Code (Read/Edit/Bash...), KHONG phai tool tu dinh nghia schema
        # nhu o cac exercise truoc (04_parallelization_workflow.py, 06_agents_and_tools_exercise.py)
        allowed_tools=["Read", "Edit", "Bash"],
        # system_prompt: str -- huong dan them cho agent, giong system prompt cua Messages API
        system_prompt=(
            "You are a careful Python debugging agent. Always read a file before editing "
            "it, explain the bug you found, then apply the minimal fix."
        ),
        # permission_mode: "acceptEdits" de agent tu ap dung edit khong hoi lai tung buoc
        # (phu hop demo tu dong; production nen dung mode chat che hon hoac permission hook)
        permission_mode="acceptEdits",
    )


async def run_bugfix_agent(prompt: str) -> None:
    """Chay agent qua ham query() -- day chinh la agent loop co san cua Claude Code,
    khong phai tu viet vong lap goi tool nhu run_agent() o 06_agents_and_tools_exercise.py.

    query() tra ve 1 async generator, moi phan tu la 1 message trong qua trinh agent chay
    (assistant text, tool call, tool result...) -- can iterate qua het de xem toan bo qua
    trinh agent "suy nghi" va hanh dong.
    """
    # prompt: str -- goal cho agent, giong tinh chat "Goal" trong so do kien truc Agents
    # o muc 8 (Goal + Tools -> Claude -> Plan)
    options = build_options()

    async for message in query(prompt=prompt, options=options):
        # Moi message co the la text tu agent, thong bao goi tool, hoac ket qua tool
        # -- in ra de theo doi qua trinh agent tu quyet dinh doc file, sua file nao
        print(message)


def main():
    # Vi du: tao san 1 file co bug ro rang, roi giao cho agent tu tim + sua -- khong chi
    # dinh truoc buoc nao (khac han workflow da lam o 01-04, day la agent thuc su)
    buggy_file = "buggy_math.py"
    with open(buggy_file, "w", encoding="utf-8") as f:
        f.write(
            "def add(a, b):\n"
            "    return a - b  # BUG: dang tru thay vi cong\n"
        )

    prompt = f"Read {buggy_file}, find the bug in the add() function, and fix it."

    try:
        asyncio.run(run_bugfix_agent(prompt))
    except Exception as exc:
        # Bat loi chung (vd chua cai claude-agent-sdk, hoac chua login Claude Code CLI)
        print(f"Agent run failed: {exc}")


if __name__ == "__main__":
    main()
