"""
Exercise 06: Providing Examples — thêm one-shot example minh hoạ output lý tưởng
Session: Prompt Engineering Techniques
Objective: Áp dụng kỹ thuật "Providing Examples" (one-shot prompting) lên trên
bản prompt "XML Tags" của Exercise 05 (bài toán meal plan cho vận động viên),
bằng cách thêm 1 ví dụ input/output mẫu kèm giải thích lý do output đó lý
tưởng — đây là kỹ thuật cuối cùng trong chuỗi 4 kỹ thuật của module (Clear &
Direct → Specific → XML Tags → Examples).
"""

from dotenv import load_dotenv  # nạp biến môi trường từ file .env (ANTHROPIC_API_KEY)
import anthropic  # SDK chính thức của Anthropic để gọi Claude API

load_dotenv()  # đọc .env vào os.environ, để client tự lấy API key
client = anthropic.Anthropic()  # khởi tạo client, tự đọc ANTHROPIC_API_KEY từ env

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test — rẻ, phù hợp lúc đang thử nghiệm kỹ thuật

# Bộ input mẫu để test prompt cuối cùng — khác với athlete dùng trong ví dụ mẫu
# bên dưới, để tránh Claude "học vẹt" y hệt ví dụ thay vì áp dụng đúng logic.
sample_athlete = {
    "height": "180cm",
    "weight": "75kg",
    "goal": "tăng cơ (muscle gain)",
    "dietary_restrictions": "không ăn hải sản (no seafood)",
}

# EXAMPLES_PROMPT: bản v5 — áp dụng "Providing Examples" trên nền v4 (XML Tags).
# Cấu trúc:
#   1. Instruction + guideline (Type A/B) + <athlete_information> — giữ nguyên
#      logic đã xây dựng ở Exercise 04/05.
#   2. Khối <example> đặt SAU phần instruction chính (đúng best practice: ví dụ
#      luôn đặt sau, không đặt trước) — chứa input mẫu + output mẫu + phần
#      reasoning giải thích tại sao output đó lý tưởng, giúp model "thấy" hình
#      mẫu cụ thể thay vì chỉ đọc mô tả bằng lời.
EXAMPLES_PROMPT = """\
Generate a one-day meal plan for an athlete that meets their dietary restrictions.

<athlete_information>
- Height: {height}
- Weight: {weight}
- Physical goal: {goal}
- Dietary restrictions: {dietary_restrictions}
</athlete_information>

Follow these steps when building the plan:
1. Estimate the athlete's daily calorie needs based on the information in
   <athlete_information>.
2. Distribute the total calories across three meals: breakfast, lunch, dinner.
3. Choose specific dishes for each meal that respect the dietary restrictions.

Format the output as a list with exactly three meals (breakfast, lunch, dinner).
For each meal include: the dish name, its main ingredients, and an estimated
calorie count.

<example>
<input>
Height: 165cm, Weight: 60kg, Goal: weight loss, Dietary restrictions: vegetarian
</input>
<ideal_output>
1. Breakfast — Oat and berry bowl: rolled oats, low-fat milk, mixed berries,
   chia seeds. ~350 kcal.
2. Lunch — Chickpea salad: chickpeas, cucumber, tomato, olive oil, lemon
   dressing. ~450 kcal.
3. Dinner — Tofu stir-fry: tofu, broccoli, bell pepper, brown rice. ~500 kcal.
</ideal_output>
<why_this_is_ideal>
Output tuân thủ đúng dietary restriction (vegetarian, không có thịt/cá), tổng
calo (~1300 kcal) hợp lý cho mục tiêu weight loss, và mỗi bữa đều có đủ 3
thông tin bắt buộc: tên món, nguyên liệu chính, lượng calo ước tính — đúng
format Type A đã yêu cầu ở phần guideline phía trên.
</why_this_is_ideal>
</example>
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
        max_tokens=700,  # giữ như các bản trước vì cấu trúc output kỳ vọng tương tự
        messages=[{"role": "user", "content": prompt}],  # 1 lượt hội thoại đơn giản
    )
    return response.content[0].text  # lấy text từ block đầu tiên trong content


def main():
    v5_prompt = build_prompt(EXAMPLES_PROMPT, sample_athlete)  # prompt v5 (bài tập này)

    print("=== [v5] Providing Examples prompt (final version) ===")
    print(v5_prompt)

    try:
        result_v5 = ask_claude(v5_prompt)  # gọi Claude với prompt v5 hoàn chỉnh
        print("\n=== Output của Claude (v5 — Providing Examples) ===")
        print(result_v5)
        print(
            "\n(Đây là bản prompt hoàn chỉnh sau khi áp dụng đủ 4 kỹ thuật: Clear & "
            "Direct (Ex.03) -> Specific (Ex.04) -> XML Tags (Ex.05) -> Examples "
            "(bài này). So với baseline ở Exercise 02, output kỳ vọng có cấu trúc "
            "ổn định, đúng format 3 bữa, và bám sát dietary restrictions hơn hẳn.)"
        )
    except anthropic.APIError as exc:
        # bắt lỗi gọi API (vd rate limit, key sai) để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
