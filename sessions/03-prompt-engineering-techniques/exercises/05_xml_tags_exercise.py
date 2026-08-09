"""
Exercise 05: Structure with XML Tags — bọc input athlete trong XML tag
Session: Prompt Engineering Techniques
Objective: Áp dụng kỹ thuật "Structure with XML Tags" lên trên bản prompt
"Being Specific" của Exercise 04 (bài toán meal plan cho vận động viên), bằng
cách bọc phần dữ liệu athlete trong tag <athlete_information> để tách rõ ranh
giới giữa "instruction" và "data", rồi so sánh output với các bài tập trước.
"""

from dotenv import load_dotenv  # nạp biến môi trường từ file .env (ANTHROPIC_API_KEY)
import anthropic  # SDK chính thức của Anthropic để gọi Claude API

load_dotenv()  # đọc .env vào os.environ, để client tự lấy API key
client = anthropic.Anthropic()  # khởi tạo client, tự đọc ANTHROPIC_API_KEY từ env

MODEL = "claude-haiku-4-5"  # dùng haiku cho dev/test — rẻ, phù hợp lúc đang thử nghiệm kỹ thuật

# Bộ input mẫu — giữ nguyên như các Exercise trước để so sánh công bằng.
sample_athlete = {
    "height": "180cm",
    "weight": "75kg",
    "goal": "tăng cơ (muscle gain)",
    "dietary_restrictions": "không ăn hải sản (no seafood)",
}

# BEING_SPECIFIC_PROMPT: bản v3 từ Exercise 04, giữ lại để in ra so sánh song song.
# Chú ý: ở bản v3, dữ liệu athlete (height, weight...) vẫn nằm xen giữa văn bản
# hướng dẫn dưới dạng danh sách gạch đầu dòng thô — chưa có ranh giới rõ ràng.
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

# XML_TAGS_PROMPT: bản v4 — áp dụng "Structure with XML Tags" trên nền v3.
# Điểm khác biệt so với v3:
#   - Toàn bộ dữ liệu athlete được bọc trong <athlete_information>...</athlete_information>,
#     tách biệt rõ ràng khỏi phần instruction/guideline phía trên và dưới.
#   - Tên tag được đặt cụ thể ("athlete_information"), không dùng tên chung chung
#     như "data", giúp model hiểu ngay đây là input bên ngoài cần xử lý.
XML_TAGS_PROMPT = """\
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
        max_tokens=700,  # giữ như v3 vì cấu trúc output kỳ vọng tương tự
        messages=[{"role": "user", "content": prompt}],  # 1 lượt hội thoại đơn giản
    )
    return response.content[0].text  # lấy text từ block đầu tiên trong content


def main():
    v3_prompt = build_prompt(BEING_SPECIFIC_PROMPT, sample_athlete)  # prompt v3 (Exercise 04)
    v4_prompt = build_prompt(XML_TAGS_PROMPT, sample_athlete)  # prompt v4 (bài tập này)

    print("=== [v3] Being Specific prompt (Exercise 04) ===")
    print(v3_prompt)

    print("\n=== [v4] Structure with XML Tags prompt ===")
    print(v4_prompt)

    try:
        result_v4 = ask_claude(v4_prompt)  # chỉ gọi API cho bản v4 để tiết kiệm chi phí
        print("\n=== Output của Claude (v4 — XML Tags) ===")
        print(result_v4)
        print(
            "\n(XML tag không đổi nội dung task, chỉ làm rõ ranh giới đâu là dữ liệu "
            "đầu vào (<athlete_information>) và đâu là hướng dẫn xử lý — giúp giảm "
            "nhầm lẫn khi prompt có nhiều phần nội dung khác nhau, đặc biệt hữu ích "
            "khi prompt dài hơn hoặc có thêm nhiều khối input khác trong tương lai.)"
        )
    except anthropic.APIError as exc:
        # bắt lỗi gọi API (vd rate limit, key sai) để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
