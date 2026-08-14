# TradingView Chart Analyzer (Experiment)

Script thử nghiệm: dùng Playwright mở TradingView, chuyển symbol/timeframe, chụp
screenshot vùng chart, rồi gửi ảnh cho Claude API (vision) để phân tích price action.

Đây là thử nghiệm độc lập, **không thuộc** curriculum trong `sessions/`.

## Setup

```bash
pip install playwright
playwright install chromium
```

Đảm bảo `.env` ở project root đã có `ANTHROPIC_API_KEY` (script tái sử dụng
`src/client.py` để lấy key).

## Chạy thử

```bash
python chart_analyzer.py --symbol FX:EURUSD --timeframe 60
python chart_analyzer.py --symbol BINANCE:BTCUSDT --timeframe 15
```

## Giới hạn đã biết

- Phím tắt timeframe (`TIMEFRAME_SHORTCUTS` trong `chart_analyzer.py`) có thể lệch
  theo phiên bản UI TradingView hiện tại — cần verify lại bằng cách chạy
  `headless=False` và quan sát trực tiếp.
- TradingView có thể yêu cầu đăng nhập cho một số symbol/tính năng nâng cao;
  chart cơ bản (FX, crypto) thường xem được ở chế độ ẩn danh.
- Đây là phân tích dựa trên **hình ảnh** (vision), không phải dữ liệu OHLC chính
  xác — phù hợp để thử nghiệm price action reading, không dùng cho tính toán
  entry/backtest chính xác.
