"""
Chat exercise
Session: Accessing Claude with the API
Objective: Build a simple multi-turn chat loop, manually tracking `messages` history.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env vào os.environ
client = anthropic.Anthropic()  # khởi tạo client, tự lấy API key từ env

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test


def add_user_message(messages, text):
    """Append 1 message role="user" vào list messages (mutate tại chỗ, không return)."""
    # messages: list[dict] — lịch sử hội thoại đang giữ ở phía client
    # text: str — nội dung user gõ vào
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    """Append 1 message role="assistant" vào list messages — lưu lại response của Claude."""
    # messages: list[dict] — cùng list history với add_user_message
    # text: str — text Claude vừa generate ra, cần lưu để lần gọi sau Claude "nhớ" được
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def chat(messages):
    """Gửi toàn bộ messages history lên Claude API và trả về text response."""
    # messages: list[dict] — bắt buộc gửi FULL history vì API stateless,
    # Claude không tự nhớ các lượt hỏi/đáp trước đó
    message = client.messages.create(
        model=MODEL,  # model dùng để generate
        max_tokens=1000,  # giới hạn an toàn số token output, không phải target
        messages=messages,  # toàn bộ lịch sử hội thoại (user + assistant messages)
    )
    return message.content[0].text  # phần text thật sự nằm ở content block đầu tiên


def main():
    messages = []  # list rỗng ban đầu, sẽ được build dần qua từng lượt chat
    print("Type 'quit' to exit.")
    while True:
        user_input = input("You: ")  # đọc input từ user qua terminal
        if user_input.strip().lower() == "quit":
            break  # thoát vòng lặp khi user gõ "quit"

        add_user_message(messages, user_input)  # thêm câu hỏi mới vào history

        try:
            answer = chat(messages)  # gọi API với full history, lấy response
        except anthropic.APIError as exc:
            # bắt lỗi API (vd hết quota, network...) để không crash chương trình
            print(f"API error: {exc}")
            break

        add_assistant_message(messages, answer)  # lưu response của Claude vào history
        print(f"Claude: {answer}")


if __name__ == "__main__":
    main()
