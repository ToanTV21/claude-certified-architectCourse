"""
Exercise 03: Being Clear and Direct — thêm action verb + task rõ ràng ở dòng đầu
Session: Prompt Engineering Techniques
Objective: Áp dụng kỹ thuật "Being Clear and Direct" lên baseline prompt của
Exercise 02 (bài toán meal plan cho vận động viên), so sánh output với baseline
để thấy sự khác biệt khi dòng đầu tiên có action verb + mô tả task rõ ràng.
"""

from dotenv import load_dotenv  # nạp biến môi trường từ file .env (ANTHROPIC_API_KEY)
import anthropic  # SDK chính thức của Anthropic để gọi Claude API

load_dotenv()  # đọc .env vào os.environ, để client tự lấy API key
client = anthropic.Anthropic()  # khởi tạo client, tự đọc ANTHROPIC_API_KEY từ env

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test — rẻ, phù hợp lúc đang thử nghiệm kỹ thuật

# Bộ input mẫu — giữ nguyên như Exercise 02 để so sánh công bằng (cùng input,
# chỉ khác prompt) giữa baseline và bản đã áp dụng "clear and direct".
sample_athlete = {
    "height": "180cm",
    "weight": "75kg",
    "goal": "tăng cơ (muscle gain)",
    "dietary_restrictions": "không ăn hải sản (no seafood)",
}

# BASELINE_PROMPT: giữ lại y nguyên bản v1 (Exercise 02) để in ra so sánh song song.
BASELINE_PROMPT = """\
Here is some information about an athlete: height {height}, weight {weight},
goal {goal}, dietary restrictions {dietary_restrictions}. Help with a meal plan.
"""

# CLEAR_AND_DIRECT_PROMPT: bản v2 — áp dụng "Being Clear and Direct".
# Điểm khác biệt so với baseline:
#   1. Dòng đầu tiên bắt đầu bằng action verb "Generate" thay vì mô tả bối cảnh
#      lan man trước.
#   2. Task được nêu rõ ràng ngay từ đầu: "a one-day meal plan for an athlete".
#   3. Nêu rõ yêu cầu output ngay trong câu đầu: phải đáp ứng dietary restrictions.
CLEAR_AND_DIRECT_PROMPT = """\
Generate a one-day meal plan for an athlete that meets their dietary restrictions.

Athlete information:
- Height: {height}
- Weight: {weight}
- Physical goal: {goal}
- Dietary restrictions: {dietary_restrictions}
"""


def build_prompt(template: str, athlete: dict) -> str:
    """Chèn thông tin athlete vào 1 prompt template bất kỳ (baseline hoặc v2)."""
    # template: str — prompt string có placeholder kiểu {height}, {weight}...
    # athlete: dict — chứa các key khớp với placeholder trong template
    return template.format(**athlete)  # ** unpack dict thành keyword arguments cho .format()


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
    baseline_prompt = build_prompt(BASELINE_PROMPT, sample_athlete)  # prompt v1
    v2_prompt = build_prompt(CLEAR_AND_DIRECT_PROMPT, sample_athlete)  # prompt v2

    print("=== [v1] Baseline prompt (Exercise 02) ===")
    print(baseline_prompt)

    print("\n=== [v2] Clear and Direct prompt ===")
    print(v2_prompt)

    try:
        result_v2 = ask_claude(v2_prompt)  # chỉ gọi API cho bản v2 để tiết kiệm chi phí
        print("\n=== Output của Claude (v2 — Clear and Direct) ===")
        print(result_v2)
        print(
            "\n(So với output v1 mơ hồ ở Exercise 02, output v2 thường có cấu trúc "
            "rõ ràng hơn — do dòng đầu tiên đã nêu chính xác action + task cần làm. "
            "Trong khóa học, riêng kỹ thuật này giúp điểm eval tăng từ 2.32 → 3.92.)"
        )
    except anthropic.APIError as exc:
        # bắt lỗi gọi API (vd rate limit, key sai) để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
