# asiafoods_sales_demo — Mock Database

Mock data cho demo BI mảng kinh doanh **Asia Foods Corporation** (Mì Gấu Đỏ) — doanh thu ~5,000 tỷ/năm, 200 NPP, ~3,500 điểm bán, 18 tháng giao dịch (T11/2024 → T4/2026).

## Cấu trúc

| File | Mục đích | Kích thước ước |
|---|---|---|
| `01_ddl_schema.sql` | CREATE DATABASE + 24 tables (13 dim + 7 fact + 4 meta) + indexes/FK | ~30 KB |
| `02_metadata.sql` | Populate _meta_tables / _meta_columns / _meta_kpi / _meta_glossary | ~30 KB |
| `03_master_data.sql` | 13 dim tables: ~4,500 rows | ~700 KB |
| `04_transaction_data.sql` | 7 fact tables: ~297K orders + 1.45M lines | **~180 MB** |
| `05_validation_queries.sql` | SELECT queries để verify data + dry-run 5 scenarios | ~10 KB |

## Setup từ đầu trên một Docker container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name asiafoods_db \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=asiafoods_sales_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng (~30s)
docker exec asiafoods_db mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự (file 04 sẽ mất 2-3 phút do dung lượng)
docker exec -i asiafoods_db mysql -uroot -proot < 01_ddl_schema.sql
docker exec -i asiafoods_db mysql -uroot -proot < 02_metadata.sql
docker exec -i asiafoods_db mysql -uroot -proot < 03_master_data.sql
docker exec -i asiafoods_db mysql -uroot -proot < 04_transaction_data.sql

# 4. Verify
docker exec -i asiafoods_db mysql -uroot -proot --default-character-set=utf8mb4 < 05_validation_queries.sql

# 5. Reset (chạy lại từ đầu)
docker exec -i asiafoods_db mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS asiafoods_sales_demo; \
   CREATE DATABASE asiafoods_sales_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Cấu trúc business

```
Asia Foods (HQ) → NPP (200) → Tuyến (200) → Điểm bán (3,500) → Người tiêu dùng
                       ↓
                  DSR (Distributor Salesman Rep)
                  viếng thăm theo F4/F8/F12 (lần/tuần)
```

**Kênh phân phối:**
- GT (General Trade — tạp hóa): ~75% DT
- MT (Modern Trade — siêu thị/CVS): ~20% DT
- HoReCa / Online / Canteen: ~5% DT

**Tier khách hàng trọng điểm:**
- Kim cương (5%): doanh số >50 triệu VND/tháng, F12
- Vàng (15%): 15-50 triệu VND/tháng, F8
- Bạc (30%): 5-15 triệu VND/tháng, F4
- Thường (50%): <5 triệu VND/tháng, F2

## 5 Demo Scenarios (đã cài anomaly)

### Scenario 1 — Opener
*"Tháng 4 vừa rồi doanh số toàn công ty thế nào? Có gì bất thường?"*

AI phát hiện:
- T4/2026: ~273 tỷ VND, %TH overall ~62%
- MT3 **vượt 161% CT** (anomaly cài chủ đích)
- Mì Trứng Vàng chỉ **10% CT** (anomaly)
- Cháo Dinh Dưỡng chỉ **7.8% CT** (anomaly)
- Cháo Ly Asim đột biến **148% CT**

### Scenario 2 — MTV Root Cause
*"Mì Trứng Vàng chỉ 10% CT — vì sao?"*

AI drill 4 lớp:
- Theo miền: cả 4 miền đều thấp → không phải region issue
- Theo lịch sử YoY: T4/2025 MTV đạt bình thường → shift mới
- **12 KH Vàng đã chuyển từ MTV sang Mì Gấu Cay (launch T11/2025)**
- Verdict: **cannibalization** chứ không phải churn

### Scenario 3 — MT3 vs MT1 Growth Quality
*"MT3 vượt 161% CT, MT1 chỉ 92% — chuyện gì?"*

AI phân biệt:
- **MT3 161%:**
  - ~89 KH mới mở Q1/2026 (vs target 60)
  - 8 chuỗi BHX (Bách Hóa Xanh) tăng đơn +25-30% từ T3/2026
  - 1 đơn đột xuất Co.opXtra Long Biên 28-30/4/2026 (~540K packs)
- **MT1 92%:** MCP mới chỉ 28 (vs target 60) — team yếu khâu mở mới

### Scenario 4 — Tết Campaign ROI
*"Campaign Tết 2026 vs Khai Xuân 2025 ROI ra sao?"*

- Tết 2026: budget 12 tỷ, sales 945 tỷ
- Khai Xuân 2025: budget 9.8 tỷ, sales 842 tỷ
- AI tính ROI + YoY + lift by tier

### Scenario 5 — Kim cương Rớt Phong Độ (WOW NHẤT)
*"Có KH Kim cương nào đang 'rớt phong độ' không?"*

7 KH Kim cương declining (volume drop >50% trong 6 tháng):
- Co.opmart Đà Nẵng (MT2) — volume_drop_all pattern
- Lotte Mart Đồng Nai (MT3) — frequency_decline (đặt giãn)
- Bách Hóa Xanh Long An — drop_categories (bỏ 2 mì cao cấp)
- WinMart Huế (MT2) — volume_drop_all
- WinMart Nha Trang (MT2) — volume_drop_all
- Aeon Mall Tân Phú (MT3) — sku_diversity_drop (SKU/đơn 12→8)
- Citimart Quận 7 (MT3) — frequency_decline

Cluster MT2: 4/7 (gồm bonus Co.opmart Huế) → pattern khu vực, không tactical.

> **Lưu ý cho AI engine:** Khi câu hỏi về "KH Kim cương" trong Scenario 5, filter thêm `dim_channel.channel_code='MT'` để loại random GT-Kim cương khỏi top.

## Tóm tắt số liệu

| Bảng | Rows |
|---|---|
| dim_customer | 3,500 |
| dim_product_sku | 38 |
| dim_route | 200 |
| dim_distributor | 200 |
| fact_sales_orders | ~297,000 |
| fact_sales_lines | ~1,454,000 |
| fact_targets | 888 |
| fact_aso_daily | 1,872 |
| fact_mcp_new | 182 |
| fact_visits | ~115,000 |
| fact_customer_tier_history | 50 |

## Magnitude check

| Period | Actual | Spec target |
|---|---|---|
| T11/2024 → T10/2025 (12M) | ~4,917 tỷ | ~5,300 tỷ |
| T1-T4/2026 | ~1,728 tỷ | ~1,850 tỷ |
| T4/2026 | ~273 tỷ | ~510 tỷ (spec) |

> T4/2026 thấp vì cả anomaly Mì Trứng Vàng (-90%) + Cháo Dinh Dưỡng (-92%) cùng kéo xuống. Các %TH ratios khớp spec exactly.

## Charset / Encoding

Toàn bộ database dùng `utf8mb4` + `utf8mb4_unicode_ci` để hỗ trợ tiếng Việt có dấu. Khi connect MySQL CLI để query, dùng:
```bash
mysql -uroot -proot --default-character-set=utf8mb4 asiafoods_sales_demo
```
