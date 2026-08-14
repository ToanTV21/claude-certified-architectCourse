"""
Experiment: TradingView Chart Analyzer
Objective: Dùng Playwright điều khiển browser mở TradingView, chuyển cặp tiền/timeframe,
chụp screenshot vùng chart, rồi gửi ảnh cho Claude API (vision) để phân tích price action.

Lưu ý: Đây là script thử nghiệm (không thuộc build-with-claude-api/ curriculum) — kiểm tra khả năng
Claude "nhìn" chart qua screenshot thay vì đọc dữ liệu OHLC thô.

Cách chạy:
    pip install playwright
    playwright install chromium
    python chart_analyzer.py --symbol FX:EURUSD --timeframe 60
"""

import argparse  # parse tham số dòng lệnh (--symbol, --timeframe)
import base64  # encode ảnh screenshot sang base64 để gửi cho Claude API
import sys  # thoát chương trình với exit code khi lỗi
from pathlib import Path  # xử lý đường dẫn file screenshot theo kiểu OS-independent

from playwright.sync_api import sync_playwright  # API đồng bộ của Playwright, dễ dùng cho script ngắn

# import client dùng chung từ src/client.py (đã load .env, khởi tạo Anthropic client)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from client import MODEL_MAIN, client  # noqa: E402 (import sau khi chỉnh sys.path)

# Map timeframe do user nhập (phút) sang phím tắt TradingView tương ứng trên toolbar
# TradingView dùng phím tắt số cho các khung thời gian phổ biến khi chart đang được focus
TIMEFRAME_SHORTCUTS = {
    1: "1",
    5: "5",
    15: "15",
    30: "30",
    60: "h",  # H1: TradingView dùng phím "h" cho khung 1 giờ mặc định
    240: "4",  # sẽ cần kết hợp thao tác UI nếu phím tắt không khớp version hiện tại
    1440: "d",  # D1
}


def capture_chart_screenshot(symbol: str, timeframe_minutes: int, output_path: Path) -> Path:
    """Mở TradingView, chuyển symbol/timeframe, chụp screenshot vùng chart."""
    with sync_playwright() as p:
        # headless=False để có thể quan sát trực tiếp lúc test; đổi True khi chạy tự động
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1600, "height": 900})

        # TradingView cho phép truyền symbol qua query param của URL chart
        url = f"https://www.tradingview.com/chart/?symbol={symbol}"
        page.goto(url, wait_until="networkidle", timeout=60000)

        # đợi chart container render xong trước khi thao tác tiếp
        page.wait_for_selector("div.chart-container", timeout=30000)

        # click vào giữa chart để focus, cần thiết để phím tắt timeframe hoạt động
        chart_box = page.locator("div.chart-container").bounding_box()
        page.mouse.click(
            chart_box["x"] + chart_box["width"] / 2,
            chart_box["y"] + chart_box["height"] / 2,
        )

        shortcut = TIMEFRAME_SHORTCUTS.get(timeframe_minutes)
        if shortcut:
            page.keyboard.press(shortcut)
            page.wait_for_timeout(1500)  # đợi chart render lại theo timeframe mới
        else:
            print(
                f"Cảnh báo: không có phím tắt cho {timeframe_minutes} phút, "
                "giữ nguyên timeframe mặc định."
            )

        # chụp screenshot đúng vùng chart container thay vì cả trang (tránh chụp sidebar/toolbar)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        page.locator("div.chart-container").screenshot(path=str(output_path))

        browser.close()
        return output_path


def analyze_chart_with_claude(image_path: Path, symbol: str, timeframe_minutes: int) -> str:
    """Gửi ảnh chart cho Claude API (vision) để phân tích price action."""
    image_bytes = image_path.read_bytes()
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    prompt = (
        f"Đây là biểu đồ giá {symbol}, khung thời gian {timeframe_minutes} phút. "
        "Hãy phân tích: xu hướng hiện tại, vùng support/resistance rõ ràng, "
        "và bất kỳ mô hình nến đáng chú ý nào. Trả lời ngắn gọn, có cấu trúc."
    )

    response = client.messages.create(
        model=MODEL_MAIN,  # dùng model mạnh vì đây là tác vụ phân tích hình ảnh cần độ chính xác cao
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )
    return response.content[0].text


def main() -> None:
    parser = argparse.ArgumentParser(description="Chụp TradingView chart và phân tích bằng Claude API")
    parser.add_argument("--symbol", default="FX:EURUSD", help="Symbol TradingView, vd FX:EURUSD, BINANCE:BTCUSDT")
    parser.add_argument("--timeframe", type=int, default=60, help="Timeframe tính bằng phút (1, 5, 15, 30, 60, 240, 1440)")
    parser.add_argument(
        "--output",
        default="screenshot.png",
        help="Đường dẫn lưu screenshot (mặc định lưu trong cùng folder script)",
    )
    args = parser.parse_args()

    output_path = Path(__file__).parent / args.output

    print(f"Đang mở TradingView cho {args.symbol}, timeframe {args.timeframe} phút...")
    screenshot_path = capture_chart_screenshot(args.symbol, args.timeframe, output_path)
    print(f"Đã lưu screenshot: {screenshot_path}")

    print("Đang gửi ảnh cho Claude API để phân tích...")
    analysis = analyze_chart_with_claude(screenshot_path, args.symbol, args.timeframe)
    print("\n=== Kết quả phân tích ===")
    print(analysis)


if __name__ == "__main__":
    main()
