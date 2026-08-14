"""
Exercise 02: Prompt Engineering — baseline prompt (chưa áp dụng kỹ thuật gì)
Session: Prompt Engineering Techniques
Objective: Tạo prompt sơ khai (chưa clear/specific/XML/examples) cho bài toán
"one-day meal plan cho vận động viên", làm baseline để so sánh điểm số sau khi
áp dụng từng kỹ thuật prompt engineering ở các bài tập tiếp theo (Being clear
and direct, Being specific, XML tags, Providing examples).
"""

from dotenv import load_dotenv  # nạp biến môi trường từ file .env (ANTHROPIC_API_KEY)
import anthropic  # SDK chính thức của Anthropic để gọi Claude API

load_dotenv()  # đọc .env vào os.environ, để client tự lấy API key
client = anthropic.Anthropic()  # khởi tạo client, tự đọc ANTHROPIC_API_KEY từ env

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test — rẻ, phù hợp lúc đang thử baseline

# prompt_input_spec: khai báo các input mà prompt cần, dùng để sau này tự sinh
# dataset test case (giống eval pipeline đã học ở session 02). Ở bài tập baseline
# này ta chỉ dùng 1 bộ input mẫu, chưa cần generate hàng loạt.
prompt_input_spec = {
    "height": "chiều cao vận động viên (cm)",
    "weight": "cân nặng vận động viên (kg)",
    "goal": "mục tiêu thể chất",
    "dietary_restrictions": "hạn chế ăn uống",
}

# Bộ input mẫu cho 1 vận động viên cụ thể — dùng để thử prompt baseline
sample_athlete = {
    "height": "180cm",
    "weight": "75kg",
    "goal": "tăng cơ (muscle gain)",
    "dietary_restrictions": "không ăn hải sản (no seafood)",
}

# BASELINE_PROMPT: prompt sơ khai, cố tình viết chung chung, không có action verb
# rõ ràng ở đầu câu, không nêu guideline/step, không dùng XML tag để tách input,
# không có ví dụ minh hoạ. Đây chính là kiểu prompt "v1" mà khóa học dùng để đo
# điểm baseline (~2.32/10) trước khi áp dụng các kỹ thuật prompt engineering.
BASELINE_PROMPT = """\
Here is some information about an athlete: height {height}, weight {weight},
goal {goal}, dietary restrictions {dietary_restrictions}. Help with a meal plan.
"""


def build_prompt(athlete: dict) -> str:
    """Chèn thông tin athlete vào BASELINE_PROMPT (giống string interpolation)."""
    # athlete: dict — chứa các key khớp với placeholder trong BASELINE_PROMPT
    return BASELINE_PROMPT.format(**athlete)  # ** unpack dict thành keyword arguments cho .format()


def ask_claude(prompt: str) -> str:
    """Gửi prompt cho Claude, trả về text của response."""
    # prompt: str — nội dung đầy đủ gửi cho model
    response = client.messages.create(
        model=MODEL,  # model dùng để generate
        max_tokens=500,  # giới hạn an toàn, đủ cho 1 meal plan ngắn
        messages=[{"role": "user", "content": prompt}],  # 1 lượt hội thoại đơn giản
    )
    return response.content[0].text  # lấy text từ block đầu tiên trong content


def main():
    prompt = build_prompt(sample_athlete)  # tạo prompt baseline từ input mẫu
    print("=== Baseline prompt (chưa áp dụng kỹ thuật gì) ===")
    print(prompt)

    try:
        result = ask_claude(prompt)  # gọi Claude với prompt baseline
        print("\n=== Output của Claude ===")
        print(result)
        print(
            "\n(Baseline này thường cho output mơ hồ/thiếu chi tiết — sẽ dùng làm điểm "
            "so sánh khi áp dụng Being clear and direct, Being specific, XML tags, "
            "Providing examples ở các bài tập tiếp theo.)"
        )
    except anthropic.APIError as exc:
        # bắt lỗi gọi API (vd rate limit, key sai) để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
