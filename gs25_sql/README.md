# GS25 Việt Nam — CVS Demo Database

Mock database cho demo CEO + Board GS25 Việt Nam — AI-for-BI pitch.

- **Database:** `gs25_demo`
- **Charset:** utf8mb4 / utf8mb4_unicode_ci
- **Time range:** 2024-10-01 → 2026-03-31 (548 ngày + 9 tháng prior cho YoY)
- **"Today" cho AI:** `2026-03-31`
- **Currency:** VND, DECIMAL(10-15, 0)

## Cấu trúc

```
gs25_sql/
├── 01_ddl_schema.sql           — 10 dim + 6 fact + 4 metadata tables
├── 02_metadata.sql             — _meta_tables / _meta_columns / _meta_kpi / _meta_glossary
├── 03_master_data.sql          — 442 stores, 1247 SKUs, 40 suppliers, 80 managers
├── 04_a_sales.sql              — fact_sales (~8.6M rows, ~850MB)
├── 04_b_inventory.sql          — fact_inventory_snapshot (~1M rows)
├── 04_c_waste.sql              — fact_waste (~840K rows)
├── 04_d_traffic.sql            — fact_store_traffic (~1.1M rows)
├── 04_e_pnl.sql                — fact_store_pnl (~7K rows)
├── 04_f_purchase_order.sql     — fact_purchase_order (~3K rows)
├── 05_validation_queries.sql   — Scenario dry-run queries
└── README.md                   — File này
```

## Populate vào Docker container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=gs25_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i mock_database mysql -uroot -proot < gs25_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < gs25_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < gs25_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < gs25_sql/04_a_sales.sql
docker exec -i mock_database mysql -uroot -proot < gs25_sql/04_b_inventory.sql
docker exec -i mock_database mysql -uroot -proot < gs25_sql/04_c_waste.sql
docker exec -i mock_database mysql -uroot -proot < gs25_sql/04_d_traffic.sql
docker exec -i mock_database mysql -uroot -proot < gs25_sql/04_e_pnl.sql
docker exec -i mock_database mysql -uroot -proot < gs25_sql/04_f_purchase_order.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < gs25_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS gs25_demo; CREATE DATABASE gs25_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Tổng quan dữ liệu

### Stores — 442 cửa hàng
| Region | Stores | % |
|---|---|---|
| TPHCM CBD (Q1, Q3, Q5) | 85 | 19% |
| TPHCM Inner | 145 | 33% |
| TPHCM Outer | 78 | 18% |
| Đông Nam Bộ | 40 | 9% |
| Hà Nội Inner | 28 | 6% |
| Hà Nội Outer | 19 | 4% |
| Khác | 47 | 11% |

### Cohorts
- Mature 2018-2020: 58 stores
- Growth 2021-2023: 185 stores
- Recent 2024: 91 stores
- New 2025+: 109 stores (HN expansion 3/2025 + HCMC fill-in)

### Products — 1,247 SKUs
| Group | SKUs | Notes |
|---|---|---|
| Snack | 300 | incl. Orion, Lotte Hàn 24+18 SKU |
| Beverage | 274 | incl. Lotte Milkis 12, Korean coffee 8 |
| Ready-to-eat | 224 | Kimbap, cơm hộp, sandwich, tokbokki |
| Instant | 150 | incl. Samyang 8 SKU, Nongshim 6 |
| Household | 137 | Personal care, household |
| Cosmetics | 73 | Innisfree, Nature Republic, The Saem |
| Fresh | 62 | Trái cây, rau |
| Other | 27 | Thuốc lá, văn phòng phẩm |

**Korean import:** 385 SKUs (30.9%) flagged `is_imported=1, origin_country='KR'`.
- High shipping sensitivity (≥7): 134 SKUs
- **Tier 1 critical (sens≥8 AND transit≥21d AND DoS≤21d on 2026-03-31): 25 SKUs**

## 5 Demo Scenarios

### Scenario 1 — Q1: Tổng quan 6 tháng
> *"Tổng quan 6 tháng vừa rồi: doanh thu toàn chuỗi GS25 thế nào? Cửa hàng nào tốt nhất, kém nhất? Trend ra sao?"*

- Revenue 6T (T10/25-T3/26): **1,718 tỷ VND**
- Active stores: 442
- Top 5: Saigon Centre Q1, Bitexco, Điện Biên Phủ, Q7 TĐN, Q4 Cantavil
- **HCMC CBD slowdown** Jan-Mar 2026 clearly visible (YoY +22.6% vs region avg +45%)

### Scenario 2 — Q2: Mở/đóng cửa hàng
> *"Nên mở thêm cửa hàng mới ở đâu? Có cửa hàng nào nên đóng?"*

- 4 chronic underperformers (lỗ 6T liên tiếp):
  - Bình Chánh Outlet 3 (0.71 tỷ/6T)
  - Vũng Tàu Bà Rịa (0.77)
  - Đồng Nai Long Khánh (1.03)
  - Bình Dương Dĩ An 2 (mới mở 6/2025)
- Cannibalization: GS25 Dĩ An 1 (12-15% dưới peer Bình Dương)
- Cohort HN 2025 ramp nhanh hơn HCMC cohort 2022

### Scenario 3 — Q3: Mỹ-Iran impact
> *"Căng thẳng Mỹ-Iran, giá dầu có thể tăng. SKU nào cần ưu tiên nhập sớm?"*

- 385 KR SKUs, KR revenue share ~14%
- **25 SKU Tier 1 CRITICAL** (sens≥8, transit≥21, DoS≤21) cần emergency order
- 72 candidate Tier 1 trước filter DoS
- Lead time KR suppliers: 14-21 ngày

### Scenario 4 — Q4: Waste fresh food anomaly
> *"Cửa hàng nào đang có waste fresh food cao bất thường tuần này?"*

Week 2026-03-23 → 2026-03-28:

| Store | Waste Rate | Root cause |
|---|---|---|
| GS25 Phú Nhuận PĐP | **11.29%** | Manager change 2026-03-14 (Lê Minh Tuấn → Phạm Quốc Việt) |
| GS25 Tân Bình CT Plaza | **10.85%** | FamilyMart mở cách 150m từ 2026-03-07 |
| GS25 HN Đào Duy Anh | **9.50%** | HCMC ordering template áp HN (HN ít ăn cơm hộp) |
| GS25 Q7 Lawrence S. Ting | **9.28%** | Spring break trường QT 2026-03-15..04-05 |
| GS25 Vũng Tàu Bãi Sau | **8.55%** | Mưa lớn weekend 2026-03-26..28 |

Baseline chain waste rate: ~4.1%

### Scenario 5 — Q5: 3 hành động ưu tiên CEO
Synthesis of Q1-Q4 → ranked recommendations với owner + deadline + cost + expected impact.

## Anomalies inject (7 nhóm)

1. **HCMC CBD slowdown** từ Jan 2026 (additional -15% on top of -4%/month gradual)
2. **HN 2025 cohort ramp-up** (60→95% in 8.5 months vs HCMC 50→95% in 11 months)
3. **4 chronic underperformers** at 55% baseline volume
4. **Cannibalization** Dĩ An 1 (-15% từ Dĩ An 2 opening 2025-06-15)
5. **5 waste anomaly stores** in week 2026-03-23..28 with specific root causes
6. **25 Tier 1 critical Korean SKUs** at DoS 13-21 days on 2026-03-31
7. **Gross margin compression** 24.8% → 22.1% over 18 months (linear)

## KPI sẵn có (xem `_meta_kpi`)

Revenue / YoY / SSSG / Gross Margin / Net Profit / Break-even months / Waste Rate / Days of Supply / KR Revenue Share / Tier 1 Critical SKU / AOV / UPT / Conversion Rate / Footfall.

## Magnitude check

- Total 18M revenue: 4,640 tỷ VND
- 6M revenue (T10/25-T3/26): 1,718 tỷ VND (target ~1,580)
- Store/month avg: 666 triệu VND (target 550-700)
- Top store/6M: ~22.7 tỷ (Saigon Centre Q1)
- Bottom store/6M: 0.71 tỷ (Bình Chánh Outlet 3, chronic)
- Gross margin: 24.8% (Oct'24) → 22.1% (Mar'26) ✅ exact target

## Notes for AI Engine

- Use `_meta_tables` / `_meta_columns` to introspect schema
- "Current date" = `'2026-03-31'`
- Currency: all `*_vnd` columns in VND
- Korean imports: `WHERE origin_country='KR'`
- SSSG: stores `WHERE opening_date < (current_date - INTERVAL 12 MONTH)`
- Waste rate Q4: `SUM(waste_value_vnd) / SUM(net_amount_vnd)` JOIN store-week

## Known limitations

- `fact_store_traffic` hourly grain only for last 90 days (2026-01-01 onwards); daily summary for older periods
- `fact_inventory_snapshot` only Mar 2026 (30-day window)
- `fact_purchase_order` ~3K POs (representative sample, not exhaustive)
- Pareto distribution slightly steeper than 80/20 (~98% top-20%) — realistic for CVS top SKU dominance
- Customer-level data not included (privacy / out of scope)
