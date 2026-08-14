"""
Parallelization workflow
Session: Agents and Workflows
Objective: Đánh giá 1 part text-description theo 3 loại vật liệu (metal, polymer, wood)
bằng 3 request Claude chạy song song, mỗi request 1 bộ tiêu chí riêng, rồi aggregate
kết quả thành 1 khuyến nghị cuối cùng.
"""

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API
from concurrent.futures import ThreadPoolExecutor  # chạy nhiều Claude call song song (I/O-bound)

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test

# Mỗi material có 1 bộ tiêu chí riêng biệt -> mỗi request chỉ tập trung 1 khía cạnh
MATERIAL_CRITERIA = {
    "metal": "Evaluate suitability for metal: strength, load-bearing, heat resistance.",
    "polymer": "Evaluate suitability for polymer/plastic: weight, cost, moldability.",
    "wood": "Evaluate suitability for wood: aesthetics, sustainability, ease of shaping.",
}


def evaluate_material(part_description: str, material: str) -> tuple[str, str]:
    """Sub-task: đánh giá part theo tiêu chí của 1 material cụ thể (chạy độc lập, song song được)."""
    # part_description: str — mô tả part cần đánh giá, dùng chung cho mọi material
    # material: str — key trong MATERIAL_CRITERIA, xác định tiêu chí riêng cho sub-task này
    criteria = MATERIAL_CRITERIA[material]
    response = client.messages.create(
        model=MODEL,
        max_tokens=150,
        system=f"You are a materials engineer. {criteria} Reply in 2-3 sentences.",
        messages=[{"role": "user", "content": part_description}],
    )
    return material, response.content[0].text.strip()


def aggregate(part_description: str, analyses: dict[str, str]) -> str:
    """Bước Aggregate: đưa toàn bộ kết quả song song vào 1 request cuối để Claude chọn ra material tốt nhất."""
    # part_description: str — mô tả part gốc, giúp Claude nhớ lại ngữ cảnh khi so sánh
    # analyses: dict[str, str] — kết quả đánh giá từng material, thu thập từ các sub-task chạy song song
    summary = "\n\n".join(f"[{material}]\n{text}" for material, text in analyses.items())
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Part description: {part_description}\n\n"
                    f"Per-material analyses:\n{summary}\n\n"
                    "Based on these analyses, recommend the single best material and explain why in 2 sentences."
                ),
            }
        ],
    )
    return response.content[0].text.strip()


def main():
    part_description = (
        "A small bracket that mounts a camera to a car dashboard. "
        "Needs to be lightweight, low-cost, and produced in high volume."
    )

    try:
        # Bước 1+2 (split + run song song): gửi 1 request/material cùng lúc bằng ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=len(MATERIAL_CRITERIA)) as executor:
            futures = [
                executor.submit(evaluate_material, part_description, material)
                for material in MATERIAL_CRITERIA
            ]
            analyses = dict(future.result() for future in futures)

        for material, text in analyses.items():
            print(f"-- {material} --\n{text}\n")

        # Bước 3 (aggregate): đưa hết kết quả song song vào 1 lần gọi cuối để ra quyết định
        recommendation = aggregate(part_description, analyses)
        print("-- Final recommendation --")
        print(recommendation)
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
