# taseco_land_demo — Mock Database

Mock data cho demo BI mảng kinh doanh **Taseco Land** (CTCP Đầu tư Bất động sản Taseco, mã CK **TAL**) — doanh thu kế hoạch 6.000 tỷ năm 2026, 8 dự án core, ~3.000 căn, **28 tháng giao dịch (01/2024 → 04/2026)**. "Hiện tại" cho demo = **30/04/2026**.

## Cấu trúc

| File | Mục đích | Kích thước |
|---|---|---|
| `01_ddl_schema.sql` | CREATE DATABASE + 23 tables (9 dim + 10 fact + 4 meta) + indexes/FK | ~25 KB |
| `02_metadata.sql` | INSERT INTO _meta_tables / _meta_columns / _meta_kpi / _meta_glossary | ~22 KB |
| `03_master_data.sql` | 9 dim tables (~3.910 rows) | ~364 KB |
| `04_transaction_data.sql` | 10 fact tables (~38K rows + ~20K events) | ~1.8 MB |
| `05_validation_queries.sql` | SELECT queries verify data + dry-run 5 scenarios | ~10 KB |

## Setup từ đầu trên một Docker container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=taseco_land_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng (~30s)
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i mock_database mysql -uroot -proot < 01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < 02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < 03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < 04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < 05_validation_queries.sql

# 5. Reset (chạy lại từ đầu)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS taseco_land_demo; \
   CREATE DATABASE taseco_land_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Cấu trúc business

```
Taseco Land (HQ - CTCP TAL)
  → 8 dự án core
     → Sàn F1 (8 đại lý) — chiếm 50-65% doanh số
     → Sàn F2 (16 môi giới) — F2 lướt sóng = rủi ro hủy cọc
     → Internal Sales Teams (4 team / 33 nhân viên)
     → Online (FB Lead Ads, Zalo OA, Google Ads, batdongsan.com.vn)
     → Referral, Event, B2B (FDI)
```

**Funnel BĐS Việt Nam (6 giai đoạn):**
Lead → Site Visit / Booking giữ chỗ (50-100tr) → Đặt cọc 10-15% → HĐMB → Thanh toán 5-7 đợt → Bàn giao

**5 Phân khúc khách:**
- end_user (~50%)
- investor_individual (~30%)
- F2_speculator lướt sóng (~8%) — driver anomaly hủy cọc
- FDI_expat (~5%) — đặc biệt ở Thái Nguyên
- luxury_gift (~7%) — mua làm quà

**Seasonality BĐS Hà Nội (cài trong dim_calendar):**
- Q1 thấp điểm (Tết)
- Q2 cao điểm xuân-hè
- Q4 cao điểm chốt số cuối năm
- T8 dương lịch (tháng 7 ÂL — **cô hồn**) giảm 30-40% (vào năm 2024 và 2025)

## 8 dự án core

| Mã | Tên | Loại | Tỉnh | Mở bán | Total units | Plan 2026 |
|---|---|---|---|---|---|---|
| LBC | Long Biên Central | Apartment_Luxury | Hà Nội | 07/2025 | 458 | 1.600 tỷ |
| TTV | Taseco Trung Văn | Mixed | Hà Nội | 08/2025 | 762 | 1.500 tỷ |
| DNG | Đoàn Ngoại giao Đợt cuối | Premium | Hà Nội | 05/2023 | 180 | 700 tỷ |
| NAK | Nam An Khánh thấp tầng | Townhouse | HN/Hoài Đức | 03/2024 | 96 | 450 tỷ |
| NMS | NOXH Mê Linh | Social_Housing | HN/Mê Linh | 01/2026 | 400 | 280 tỷ |
| TNS | Thái Nguyên Central Square | Urban_Township | Thái Nguyên | 05/2024 | 420 | 950 tỷ |
| BNT | Bắc Ninh Từ Sơn | Urban_Township | Bắc Ninh | 12/2026 (pre-launch) | 430 | 200 tỷ |
| DNR | Đà Nẵng Resort | Resort | Đà Nẵng | 03/2027 (teaser) | 208 | 320 tỷ |

## 5 Demo Scenarios (đã cài anomaly)

### Scenario 1 — Bức tranh tổng 4T2026
*"Doanh số 4 tháng đầu năm 2026 thế nào? Có đạt kế hoạch không?"*

AI phát hiện:
- Tổng 1.498 tỷ / 6.000 tỷ = 25% kế hoạch năm 2026 (pro-rata 4 tháng ≈ 33% → on pace nhưng lệch theo dự án)
- 🟢 Đầu tàu: Trung Văn (479 tỷ — 32% KH), Nam An Khánh (37,6% KH — vượt pro-rata)
- 🟡 Theo dõi: Long Biên Central (388 tỷ — chỉ 24% KH), Thái Nguyên (22,6% KH)
- 🔴 Báo động: NOXH Mê Linh (17,2% KH — chậm thủ tục)

### Scenario 2 — Long Biên Central vs Trung Văn
*"Vì sao Long Biên chậm hơn Trung Văn?"*

3 nguyên nhân được AI cross-reference:
- **Kênh F1:** Đất Vàng Land drop 42% từ 02/2026 (sàn lớn nhất Long Biên, share đỉnh 28% → còn ~8%)
- **1PN Long Biên:** Lead time ~118 ngày (vs 70 ngày của 3PN) → pricing không match phân khúc 1PN
- **Policy:** Long Biên chỉ HTLS 18 tháng. Trung Văn có thêm chiết khấu 2% từ 11/2025 → conversion jump

### Scenario 3 — AI tự flag anomaly
*"Có dấu hiệu bất thường gì gần đây?"*

3 anomalies tự phát hiện:
- 🚨 **TTV Shophouse cancellation surge** 15/3-30/4/2026: 28 ca hủy (14 từ An Phú Realty — F2 lướt sóng)
- 🚨 **Đất Vàng Land drop**: Sàn F1 lớn nhất LBC giảm 42% YoY trong 3 tháng gần (Feb-Mar-Apr 2026)
- 🚨 **LBC 1PN lead time**: ~118 ngày (vs 70 cho 3PN) — pricing không match phân khúc

### Scenario 4 — Forecast Long Biên Central
*"Khi nào Long Biên Central bán hết? Có cần điều chỉnh chính sách?"*

AI dùng elasticity từ TTV policy (11/2025: velocity tăng từ 45 → 60 contracts = +33%) để project Long Biên scenarios A/B/C.

### Scenario 5 — Budget Q2/2026 (Climax)
*"Nên ưu tiên dự án/kênh/phân khúc nào để max doanh thu Q2/2026?"*

ROI matrix 4T2026 cho thấy:
- 🟢 **SCALE UP:** TNS Referral, TTV Referral, TNS B2B/FDI, NMS Referral
- 🟢 **Mid:** LBC Online_Paid, TTV Online_Paid
- 🔴 **CẮT:** **TTV Internal_Sales (telesales shophouse) ROI ~1.1x** ≈ break-even — cắt 70%, chuyển sang Referral
- 🔴 **CẮT:** Đà Nẵng Resort marketing rộng — còn ~11 tháng mới mở bán quy mô

## Tóm tắt số liệu

| Bảng | Rows |
|---|---|
| dim_calendar | 851 |
| dim_project | 8 |
| dim_unit | 2.954 |
| dim_broker | 28 |
| dim_employee | 33 |
| fact_lead | 8.036 |
| fact_lead_event | 20.182 |
| fact_booking | 1.285 |
| fact_deposit | 736 |
| fact_sales_contract | 736 |
| fact_cancellation | 555 |
| fact_payment_installment | 4.962 |
| fact_marketing_spend | 717 |
| fact_referral | 8 |
| fact_unit_inventory_snapshot | 224 |
| _meta_* (4 tables) | 86 |

## Magnitude check

| Period | Actual | Spec target | % |
|---|---|---|---|
| 2024 | 1.566 tỷ | 1.684 tỷ | 93% |
| 2025 | 3.923 tỷ | 4.332 tỷ | 91% |
| 4T2026 (01-04) | 1.498 tỷ | ~1.500 tỷ (pro-rata 25% KH) | **100%** |

## Charset / Encoding

Toàn bộ database dùng `utf8mb4` + `utf8mb4_unicode_ci` để hỗ trợ tiếng Việt có dấu. Khi connect MySQL CLI:
```bash
mysql -uroot -proot --default-character-set=utf8mb4 taseco_land_demo
```

## Lưu ý cho AI engine MCP

- **Metadata tables `_meta_*`** chứa schema documentation (Tiếng Việt + English), KPI formulas, glossary BĐS VN. AI nên đọc trước khi query.
- **Data range:** 2024-01-01 → 2026-04-30. "Hiện tại" cho cuộc demo = **30/04/2026**.
- **Đơn vị tiền:** VND (BIGINT). Chia 1e9 để có tỷ VND.
- **Tháng cô hồn 2024/2025** (`dim_calendar.is_thang_co_hon=TRUE`) — kiêng kỵ mua nhà, doanh số dip 30-40%.
- **Tết Bính Ngọ 2026** (`is_le_tet=TRUE`, 10-24/2/2026) — gần như không có HĐMB trong window này.
- Khi câu hỏi về "AN PHÚ REALTY" + "hủy cọc shophouse" → ám chỉ Scenario 3A (15/3-30/4/2026).
- Khi câu hỏi về "Long Biên Central 1PN" → ám chỉ Scenario 2B (lead time 118 ngày, conversion thấp).
- Khi câu hỏi về "TTV telesales" hoặc "Internal_Sales TTV shophouse" → ám chỉ Scenario 5 (ROI break-even).
