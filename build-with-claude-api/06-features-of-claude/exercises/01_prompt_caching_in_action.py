"""
Prompt caching in action
Session: Features of Claude
Objective: Mark a large static system block with cache_control and observe
cache_creation vs. cache_read token usage across nhiều lần gọi, kèm log chi tiết
(thời gian phản hồi, số token, chi phí ước tính) để thấy rõ hiệu quả của cache.
"""

import sys  # dùng để reconfigure stdout encoding, tránh lỗi UnicodeEncodeError trên console Windows (cp1252)
import time  # đo thời gian phản hồi của mỗi call để so sánh nhanh/chậm

from dotenv import load_dotenv  # load biến môi trường từ file .env
import anthropic  # SDK chính thức để gọi Claude API

sys.stdout.reconfigure(encoding="utf-8")  # ép stdout dùng UTF-8 để in được tiếng Việt trên terminal Windows

load_dotenv()  # đọc ANTHROPIC_API_KEY từ .env
client = anthropic.Anthropic()  # khởi tạo client

MODEL = "claude-haiku-4-5"  # model rẻ, dùng cho dev/test

# Giá token của claude-haiku-4-5 (USD / 1M token) — dùng để ước tính tiền tiết kiệm được nhờ cache.
# Cache write đắt hơn input thường (~1.25x), cache read rẻ hơn nhiều (~0.1x).
PRICE_PER_MTOK = {
    "input": 1.00,          # input token bình thường (không cache)
    "cache_write": 1.25,    # token ghi vào cache (cache_creation_input_tokens)
    "cache_read": 0.10,     # token đọc từ cache (cache_read_input_tokens)
    "output": 5.00,         # output token
}

# A cache block phải đủ lớn mới được cache: model Haiku yêu cầu tối thiểu ~2048 token,
# Sonnet/Opus yêu cầu tối thiểu ~1024 token. Nhân chuỗi lên 200 lần (~6000+ token) để
# chắc chắn vượt ngưỡng tối thiểu của Haiku và cache thực sự kích hoạt.
LARGE_STATIC_CONTEXT = (
    "You are a support agent for a fictional product called Acme Widgets. "
    "Product policy: refunds within 30 days, no questions asked. "
) * 200


def ask(question: str):
    """Gửi 1 câu hỏi kèm system block được đánh dấu cache_control.

    Trả về tuple (response, elapsed_seconds) để log thời gian phản hồi.
    """
    # question: str — câu hỏi cụ thể của user, phần này KHÔNG được cache (đổi mỗi lần gọi)
    start = time.perf_counter()  # mốc thời gian bắt đầu request
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=[
            {
                "type": "text",
                "text": LARGE_STATIC_CONTEXT,  # phần context tĩnh, lặp lại giữa các request
                "cache_control": {"type": "ephemeral"},  # đánh dấu block này để Anthropic cache lại
            }
        ],
        messages=[{"role": "user", "content": question}],
    )
    elapsed = time.perf_counter() - start  # tổng thời gian round-trip (network + xử lý)
    return response, elapsed


def cost_usd(usage) -> float:
    """Tính chi phí ước tính (USD) của 1 lần call dựa trên usage trả về từ API."""
    # getattr với default 0 vì cache_creation/cache_read chỉ xuất hiện khi liên quan đến cache
    input_tok = getattr(usage, "input_tokens", 0) or 0
    cache_write_tok = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cache_read_tok = getattr(usage, "cache_read_input_tokens", 0) or 0
    output_tok = getattr(usage, "output_tokens", 0) or 0

    return (
        input_tok * PRICE_PER_MTOK["input"]
        + cache_write_tok * PRICE_PER_MTOK["cache_write"]
        + cache_read_tok * PRICE_PER_MTOK["cache_read"]
        + output_tok * PRICE_PER_MTOK["output"]
    ) / 1_000_000  # giá niêm yết theo per-1M-token nên chia lại về per-token thực tế


def log_call(label: str, usage, elapsed: float) -> float:
    """In log chi tiết cho 1 call và trả về chi phí ước tính (USD) để tổng hợp cuối cùng."""
    price = cost_usd(usage)
    print(f"\n--- {label} ---")
    print(f"  elapsed_time        : {elapsed:.3f}s")
    print(f"  input_tokens        : {usage.input_tokens}")
    print(f"  cache_creation_tokens: {getattr(usage, 'cache_creation_input_tokens', 0)}")
    print(f"  cache_read_tokens   : {getattr(usage, 'cache_read_input_tokens', 0)}")
    print(f"  output_tokens       : {usage.output_tokens}")
    print(f"  estimated_cost      : ${price:.6f}")
    return price


def main():
    try:
        # Gọi 3 lần liên tiếp với cùng 1 system block (LARGE_STATIC_CONTEXT) nhưng câu hỏi khác nhau:
        # - Call 1: chưa có cache -> tạo cache mới (cache_creation_input_tokens > 0)
        # - Call 2, 3: system block trùng khớp -> phục vụ từ cache (cache_read_input_tokens > 0)
        questions = [
            "What's the refund policy?",
            "Can I get a refund after 20 days?",
            "Do you offer refunds for digital products too?",
        ]

        total_cost_with_cache = 0.0
        no_cache_baseline_cost = 0.0  # chi phí giả định NẾU không dùng cache (mọi call đều input_tokens thường)

        for i, q in enumerate(questions, start=1):
            response, elapsed = ask(q)
            price = log_call(f"Call {i}: \"{q}\"", response.usage, elapsed)
            total_cost_with_cache += price

            # Baseline giả định: nếu không cache, toàn bộ system + question sẽ tính theo giá input thường
            equivalent_input_tokens = (
                response.usage.input_tokens
                + getattr(response.usage, "cache_creation_input_tokens", 0)
                + getattr(response.usage, "cache_read_input_tokens", 0)
            )
            no_cache_baseline_cost += (
                equivalent_input_tokens * PRICE_PER_MTOK["input"]
                + response.usage.output_tokens * PRICE_PER_MTOK["output"]
            ) / 1_000_000

        # Tổng kết so sánh có cache vs không cache
        savings = no_cache_baseline_cost - total_cost_with_cache
        savings_pct = (savings / no_cache_baseline_cost * 100) if no_cache_baseline_cost > 0 else 0

        print("\n=== SUMMARY ===")
        print(f"  total cost WITH cache    : ${total_cost_with_cache:.6f}")
        print(f"  estimated cost W/O cache : ${no_cache_baseline_cost:.6f}")
        print(f"  savings                 : ${savings:.6f} ({savings_pct:.1f}%)")
        print(
            "\nGhi chú: cache_read_input_tokens ở Call 2, 3 cho thấy phần system block "
            "được phục vụ từ cache thay vì xử lý lại từ đầu -> rẻ hơn và thường nhanh hơn "
            "so với Call 1 (nơi phải tốn cache_creation_input_tokens để tạo cache)."
        )
    except anthropic.APIError as exc:
        # bắt lỗi API để không crash chương trình
        print(f"API error: {exc}")


if __name__ == "__main__":
    main()
