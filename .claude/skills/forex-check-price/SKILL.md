---
name: forex-check-price
description: Check toàn bộ (hoặc 1 phần) watchlist forex/vàng trên TradingView (chart layout riêng của user, đã login sẵn qua Claude in Chrome) theo multi-timeframe D1/H4/H1, dùng phương pháp price-action + S/D của skill forex-priceaction-sd, rồi xuất mỗi cặp thành 1 file markdown report riêng có nhúng ảnh chụp từng khung thời gian làm evidence. Dùng khi user nói "check giá", "check watchlist", "check các cặp tiền", "chạy forex-check-price", hoặc yêu cầu quét toàn bộ watchlist EURUSD/GBPUSD/USDJPY/USDCAD/AUDUSD/XAUUSD.
---

# Forex Check Price — Multi-pair Multi-timeframe Report

Skill này đóng gói quy trình đã làm thủ công: dùng **Claude in Chrome** để điều khiển
đúng Chrome thật của user (đã login sẵn TradingView), mở chart layout riêng của user
(đã có custom indicator EMA34_v2 / RSI_PB / BOS system), lần lượt đổi symbol + timeframe,
chụp ảnh, rồi phân tích theo phương pháp trong skill `forex-priceaction-sd`. Kết quả: mỗi
cặp tiền/vàng ra 1 file `.md` report riêng, có nhúng ảnh D1/H4/H1 làm evidence.

## Khi nào dùng

- User gọi thẳng skill này, hoặc nói "check giá", "check watchlist", "quét các cặp tiền",
  "phân tích toàn bộ watchlist"
- Không có yêu cầu subset cụ thể → mặc định check đủ **6 mục trong watchlist**:
  `EURUSD, GBPUSD, USDJPY, USDCAD, AUDUSD, XAUUSD`
- User có thể giới hạn subset (vd "check EURUSD với XAUUSD thôi") → chỉ chạy đúng các
  symbol được nêu, giữ nguyên toàn bộ quy trình còn lại

## Input cố định (đã xác nhận với user trong phiên trước)

- **Chart layout TradingView của user:** `https://www.tradingview.com/chart/4G6oI0C4/`
  (layout riêng, cần user đã đăng nhập sẵn trong Chrome thật — layout chứa indicator
  EMA34_v2, RSI_PB_v5, hệ thống BOS/Bias/Entry Filter riêng của user)
- **Broker nguồn ưu tiên khi search symbol:** `OANDA` (khớp với watchlist hiện có của user).
  Nếu 1 symbol không có nguồn OANDA (vd một số cross hiếm), chọn kết quả `forex` đầu tiên
  hợp lý gần nhất.
- **3 khung thời gian bắt buộc mỗi symbol:** D1 → H4 → H1 (đúng thứ tự, đúng quy trình MTA
  trong skill `forex-priceaction-sd`)

## Quy trình thực hiện

### Bước 0 — Kết nối Chrome thật của user

1. `ToolSearch` load các tool `claude-in-chrome` cần dùng (tabs_context_mcp, tabs_create_mcp,
   navigate, computer, read_page, find, browser_batch) nếu chưa có trong context.
2. `list_connected_browsers` để xác nhận có Chrome nào đang kết nối (`isLocal: true`).
3. `tabs_context_mcp {createIfEmpty: true}` để lấy tab trong nhóm MCP. Nếu không có tab nào
   phù hợp, `tabs_create_mcp` tạo tab mới rồi `navigate` tab đó đến chart URL ở trên.
4. Chụp thử 1 screenshot — nếu TradingView báo "We can't open this chart layout for you"
   (chưa login) → dừng lại, báo user cần đăng nhập TradingView trong tab đó trước, KHÔNG
   tự động nhập thông tin đăng nhập.

### Bước 1 — Hỏi trạng thái account (CHỈ 1 LẦN cho cả phiên, không hỏi lại mỗi cặp)

Theo quy tắc bắt buộc của `forex-priceaction-sd` (Bước 2 trong quy trình phân tích của skill
đó): phải biết account đang mở bao nhiêu lệnh, loại tài khoản (cá nhân/FTMO), P&L/drawdown
hiện tại trước khi đưa bất kỳ trade recommendation nào. Hỏi 1 lần bằng `AskUserQuestion` ngay
đầu phiên chạy skill này, áp dụng chung cho tất cả các cặp sẽ check trong lượt chạy.

### Bước 2 — Chuẩn bị thư mục output

Thư mục gốc report: `experiments/tradingview-chart-analyzer/reports/<YYYY-MM-DD>/`
(dùng ngày hiện tại theo context `currentDate`). Trong đó:
- `images/` — chứa ảnh chụp, đặt tên `<PAIR>_<TF>.png` (vd `EURUSD_D1.png`, `EURUSD_H4.png`,
  `EURUSD_H1.png`)
- `<PAIR>.md` — 1 file report riêng cho mỗi symbol

Tạo thư mục bằng lệnh shell trước khi bắt đầu vòng lặp symbol đầu tiên.

### Bước 3 — Vòng lặp cho từng symbol trong danh sách

Với mỗi symbol (theo đúng thứ tự trong watchlist trừ khi user giới hạn subset):

1. **Đổi symbol:** `find` nút "Symbol search" trên toolbar (hoặc dùng lại ref đã biết nếu
   còn hợp lệ), click, `type` tên symbol, đợi dropdown, click đúng kết quả `forex` nguồn
   OANDA đầu tiên khớp tên (không click nhầm CFD/futures của broker khác).
2. **Lấy lại danh sách ref mới:** sau mỗi lần đổi symbol, ref của các nút timeframe có thể
   đổi số — luôn `read_page {filter: "interactive"}` lại để lấy đúng ref của radio "1 day",
   "4 hours", "1 hour" trước khi click, KHÔNG tái sử dụng ref từ symbol trước.
3. **Với từng timeframe theo thứ tự D1 → H4 → H1:**
   - Click đúng ref timeframe tương ứng
   - `wait` ~1.5s cho chart render lại
   - `computer {action: "screenshot", save_to_disk: true}` để chụp và lưu ảnh ra file thật
     (không dùng screenshot thường vì ảnh đó chỉ trả về inline, không có file trên đĩa để
     nhúng vào markdown)
   - Đọc path file mà tool trả về trong output text, dùng lệnh shell di chuyển/copy file đó
     vào đúng `images/<PAIR>_<TF>.png` trong thư mục report của ngày hôm nay
   - Nếu `save_to_disk` không trả về path rõ ràng trong output, thử lại 1 lần; nếu vẫn không
     có, ghi chú rõ trong report là "thiếu evidence ảnh cho khung X" thay vì bỏ qua âm thầm
4. **Phân tích:** áp dụng đúng quy trình 6 bước trong skill `forex-priceaction-sd`
   (Price Action → S/D Zone → Entry Trigger H1 → Grade Setup), dựa trên nội dung nhìn thấy
   trong 3 ảnh vừa chụp (đọc cả các label/panel chỉ số custom của user trên chart: EMA34_v2,
   RSI_PB, Overall Bias, Entry Filter, BOS Bull/Bear Lvl...).
5. **Ghi file report** `<PAIR>.md` theo template ở dưới.

### Bước 4 — Git commit (theo rule 6b của CLAUDE.md)

Sau khi ghi xong report + ảnh cho 1 symbol, `git add` đúng file report + ảnh của symbol đó,
commit riêng (không gộp nhiều symbol vào 1 commit), rồi `git push`. Message ngắn gọn dạng
`Add forex check report: <PAIR> <YYYY-MM-DD>`.

### Bước 5 — Tóm tắt cuối phiên trong chat

Sau khi chạy xong toàn bộ symbol, tóm tắt ngắn gọn (không lặp lại full nội dung từng report):
liệt kê symbol nào có setup Grade A/B (actionable) kèm entry zone, symbol nào Grade C
(chỉ watch) kèm watch level chính. Dẫn link tới từng file report bằng markdown link.

## Template file report `<PAIR>.md`

```markdown
# Forex Check — <PAIR> — <YYYY-MM-DD HH:mm> (UTC+9)

## MULTI-TF ANALYSIS

**D1:** [Trend + cấu trúc + EMA + ADX + Overall Bias / Entry Filter đọc từ panel]
**H4:** [Zone + BOS levels + trạng thái range/trend]
**H1:** [Regime + entry trigger nếu có]

![D1](images/<PAIR>_D1.png)
![H4](images/<PAIR>_H4.png)
![H1](images/<PAIR>_H1.png)

## S/D ZONE ASSESSMENT

| Zone | Vị trí | Ghi chú |
|------|--------|---------|
| ... | ... | ... |

Score: X/8

## TRADE PLAN

[Grade A/B: entry/SL/TP/size theo Kelly ½K — hoặc Grade C: watch levels + điều kiện xác nhận]

## RISK NOTES

[Correlation với các cặp khác trong watchlist, tin tức, FTMO/personal limit nếu áp dụng]
```

## Không làm

- Không đưa trade recommendation cho bất kỳ cặp nào mà chưa hỏi account status trong phiên
- Không tự nhập thông tin đăng nhập TradingView giúp user
- Không gộp nhiều symbol vào 1 commit git
- Không bỏ qua bước lấy lại `read_page` ref mới sau mỗi lần đổi symbol (ref cũ có thể trỏ
  sai timeframe do TradingView re-render DOM)
- Không tạo report nếu thiếu ảnh evidence mà không ghi chú rõ lý do thiếu
