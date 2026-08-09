"""
Exercise 04: Being Specific — thêm guideline Type A (attributes) và Type B (steps)
Session: Prompt Engineering Techniques
Objective: Áp dụng kỹ thuật "Being Specific" lên trên bản prompt "Clear and
Direct" của Exercise 03 (bài toán meal plan cho vận động viên), bằng cách thêm
guideline về thuộc tính output (Type A) và các bước suy luận (Type B), rồi so
sánh output với 2 bài tập trước.
"""

from dotenv import load_dotenv  # nạp biến môi trường từ file .env (ANTHROPIC_API_KEY)
import anthropic  # SDK chính thức của Anthropic để gọi Claude API

load_dotenv()  # đọc .env vào os.environ, để client tự lấy API key
client = anthropic.Anthropic()  # khởi tạo client, tự đọc ANTHROPIC_API_KEY từ env

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test — rẻ, phù hợp lúc đang thử nghiệm kỹ thuật

# Bộ input mẫu — giữ nguyên như Exercise 02/03 để so sánh công bằng giữa các bản prompt.
sample_athlete = {
    "height": "180cm",
    "weight": "75kg",
    "goal": "tăng cơ (muscle gain)",
    "dietary_restrictions": "không ăn hải sản (no seafood)",
}

# CLEAR_AND_DIRECT_PROMPT: bản v2 từ Exercise 03, giữ lại để in ra so sánh song song.
CLEAR_AND_DIRECT_PROMPT = """\
Generate a one-day meal plan for an athlete that meets their dietary restrictions.

Athlete information:
- Height: {height}
- Weight: {weight}
- Physical goal: {goal}
- Dietary restrictions: {dietary_restrictions}
"""

# BEING_SPECIFIC_PROMPT: bản v3 — áp dụng "Being Specific" trên nền v2.
# Điểm khác biệt so với v2:
#   - Type A (attributes): mô tả rõ output phải có 3 bữa (sáng/trưa/tối), mỗi bữa
#     gồm tên món + nguyên liệu chính + lượng calo ước tính, trình bày dạng danh sách.
#   - Type B (steps): yêu cầu model suy luận theo từng bước — tính nhu cầu calo
#     hàng ngày trước, rồi mới phân bổ vào từng bữa và chọn món phù hợp — thay vì
#     để model "nhảy thẳng" vào liệt kê món ăn ngẫu nhiên.
BEING_SPECIFIC_PROMPT = """\
Generate a one-day meal plan for an athlete that meets their dietary restrictions.

Athlete information:
- Height: {height}
- Weight: {weight}
- Physical goal: {goal}
- Dietary restrictions: {dietary_restrictions}

Follow these steps when building the plan:
1. Estimate the athlete's daily calorie needs based on their height, weight, and
   physical goal.
2. Distribute the total calories across three meals: breakfast, lunch, dinner.
3. Choose specific dishes for each meal that respect the dietary restrictions.

Format the output as a list with exactly three meals (breakfast, lunch, dinner).
For each meal include: the dish name, its main ingredients, and an estimated
calorie count.
"""


def build_prompt(template: str, athlete: dict) -> str:
    """Chèn thông tin athlete vào 1 prompt template bất kỳ."""
    # template: str — prompt string có placeholder kiểu {height}, {weight}...
    # athlete: dict — chứa các key khớp với placeholder trong template
    return template.format(**athlete)  # ** unpack dict thành keyword arguments cho .format()


def ask_claude(prompt: str) -> str:
    """Gửi prompt cho Claude, trả về text của response."""
    # prompt: str — nội dung đầy đủ gửi cho model
    response = client.messages.create(
        model=MODEL,  # model dùng để generate
        max_tokens=700,  # tăng nhẹ so với v1/v2 vì output v3 có cấu trúc chi tiết hơn
        messages=[{"role": "user", "content": prompt}],  # 1 lượt hội thoại đơn giản
    )
    return response.content[0].text  # lấy text từ block đầu tiên trong content


def main():
    v2_prompt = build_prompt(CLEAR_AND_DIRECT_PROMPT, sample_athlete)  # prompt v2 (Exercise 03)
    v3_prompt = build_prompt(BEING_SPECIFIC_PROMPT, sample_athlete)  # prompt v3 (bài tập này)

    print("=== [v2] Clear and Direct prompt (Exercise 03) ===")
    print(v2_prompt)

    print("\n=== [v3] Being Specific prompt (Type A + Type B) ===")
    print(v3_prompt)

    try:
        result_v3 = ask_claude(v3_prompt)  # chỉ gọi API cho bản v3 để tiết kiệm chi phí
        print("\n=== Output của Claude (v3 — Being Specific) ===")
        print(result_v3)
        print(
            "\n(So với v2, output v3 nên có cấu trúc rõ ràng hơn: đúng 3 bữa, mỗi "
            "bữa có tên món/nguyên liệu/calo, và logic tính calo hợp lý hơn nhờ "
            "guideline Type B (steps). Trong khóa học, kỹ thuật này giúp điểm eval "
            "tăng từ 3.92 → 7.86 — mức cải thiện lớn nhất trong 2 kỹ thuật đã học.)"
        )
    except anthropic.APIError as exc:
        # bắt lỗi gọi API (vd rate limit, key sai) để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
