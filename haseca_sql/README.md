# HASECA Demo Database

Database mock cho demo AI engine (MCP) — ngành **Suất ăn công nghiệp** (Industrial Catering).

## Bối cảnh

- **Khách hàng:** Công ty Cổ phần Dịch vụ Quốc tế Hà Thành (HASECA)
- **Quy mô mock:** 200K suất ăn/ngày, 120 bếp trên 40 tỉnh, ~90 khách hàng FDI/nội địa
- **Doanh thu 12 tháng:** ~1.75 nghìn tỷ VND
- **Data range:** 2024-05-01 → 2026-04-30 (24 tháng)

## Cấu trúc files

```
haseca_sql/
├── 01_ddl_schema.sql                      # CREATE DATABASE + 20 tables (DDL only)
├── 02_metadata.sql                        # _meta_tables/columns/kpi/glossary data
├── 03_master_data.sql                     # 12 dim_* tables data (~90 KB)
├── 04_a_fact_meals_served.sql             # ~370K rows (~36 MB)
├── 04_b_fact_raw_material_purchase.sql    # ~835K rows (~44 MB)
├── 04_c_fact_menu_served.sql              # ~2.26M rows (~100 MB)
├── 04_d_fact_contract_event.sql           # 141 rows
├── 05_validation_queries.sql              # Verification queries
└── README.md                              # File này
```

Tổng dung lượng SQL: ~180 MB.

## Populate vào Docker

### Cách 1: dùng populate.sh (recommended)

Từ thư mục cha (`Demo Data/`):

```bash
./populate.sh haseca
```

Script này tự:
- Tìm folder `haseca_sql/`
- Detect database name từ `01_ddl_schema.sql`
- Reset database + chạy file 01→04 theo thứ tự

### Cách 2: chạy thủ công

```bash
# 1. Khởi tạo MySQL container (nếu chưa có)
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=haseca_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate theo thứ tự
docker exec -i mock_database mysql -uroot -proot < haseca_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < haseca_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < haseca_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < haseca_sql/04_a_fact_meals_served.sql
docker exec -i mock_database mysql -uroot -proot < haseca_sql/04_b_fact_raw_material_purchase.sql
docker exec -i mock_database mysql -uroot -proot < haseca_sql/04_c_fact_menu_served.sql
docker exec -i mock_database mysql -uroot -proot < haseca_sql/04_d_fact_contract_event.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < haseca_sql/05_validation_queries.sql

# 5. Reset (nếu cần)
docker exec mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS haseca_demo; \
   CREATE DATABASE haseca_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Cấu trúc database

**12 Dimension tables:**

| Table | Rows | Mô tả |
|---|---|---|
| dim_calendar | 730 | 24 tháng, có cờ Tết + lễ VN |
| dim_region | 3 | Miền Bắc / Trung / Nam |
| dim_province | 40 | Tỉnh KCN-heavy |
| dim_industrial_zone | 52 | KCN Yên Phong, VSIP, Amata, Thăng Long... |
| dim_kitchen | 120 | Bếp Haseca, size S/M/L/XL |
| dim_customer | 90 | KR 22, JP 20, VN 18, TW 8, US 8, EU 7, CN 7 |
| dim_customer_site | ~140 | Sites của khách hàng |
| dim_meal_tier | 5 | Basic 18k → Luxury 45k |
| dim_contract | 104 | 23 hết hạn T5-T10/2026 |
| dim_menu_category | 10 | Cơm, protein, canh, rau, tráng miệng, đồ uống |
| dim_raw_material | 80 | meat/poultry/seafood/vegetable/grain/seasoning/dairy/fruit |
| dim_supplier | 30 | Metro/MM, distributor, VietGAP farm, hải sản |

**4 Fact tables:**

| Table | Rows | Granularity |
|---|---|---|
| fact_meals_served | ~370K | date × kitchen × site × tier × shift |
| fact_raw_material_purchase | ~835K | date × kitchen × supplier × material |
| fact_menu_served | ~2.26M | date × kitchen × tier × shift × menu_category |
| fact_contract_event | 141 | contract event signed/renewed/price_change |

**4 Metadata tables:** `_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary` — source of truth cho AI engine MCP.

## 6 Demo Scenarios với anomaly có chủ đích

| # | Tầng | Câu hỏi | Anomaly |
|---|---|---|---|
| 1 | Descriptive | Tổng quan 12 tháng + bất thường | Auto-flag 3 anomaly: margin T8/2025, KR churn cluster, Yên Phong waste |
| 2 | Diagnostic | Tại sao margin T8/2025 giảm? | Pork price spike +18% (165k VND/kg vs 145k) → food cost ratio +5đ% → margin -3đ% |
| 3 | Diagnostic | Khách nào giảm volume? | Shinwon -29%, Hansol -28%, LG Display -15% (T2-T4/2026 vs T11-T1) — KR FDI cluster MB |
| 4 | Comparative | Bếp MB×L underperform? | Bếp Yên Phong waste 8.5% vs peer 4.1%, cost 18.4K vs peer 16.5K, từ T11/2025 (đổi manager) |
| 5 | Strategic | HĐ sắp hết hạn — tăng giá? | 23 hợp đồng end T5-T10/2026, segment 3 nhóm theo strategic_value |
| 6 | What-if | Heo +10% → impact? | Pork = 17% food spend → margin -1.7đ%; 36% HĐ có raw_material_adjustment auto-trigger |

## Anomaly chính trong data

1. **Pork price spike T8/2025**: `fact_raw_material_purchase.unit_price_vnd` cho thịt heo nạc vai/ba chỉ/sườn tăng từ 145k → ~165k T8/2025, sau đó hồi về 145k T9, rồi creep dần lên 158k T4/2026.
2. **Margin drop T8/2025**: từ ~17.9% xuống 15.24%, do pork spike × menu mix Miền Nam (47% protein là heo).
3. **Customer churn T2-T4/2026**: 4 khách hàng KR/JP giảm volume gradually (Shinwon, Hansol, LG Display, Nitori).
4. **Customer growth T3-T4/2026**: Ford Hải Dương + Heineken Vũng Tàu tăng volume.
5. **Yên Phong waste anomaly**: `waste_rate` tăng từ ~4% lên ~8.5% từ 2025-11-01 (trùng `manager_changed_date`).
6. **Pork at 158k VND/kg** trong T4/2026 (baseline cho Scenario 6 What-if).

## Notes cho AI Engine

- Kết nối MCP tới MySQL `haseca_demo` (host=localhost, port=3306, user=root, password=root)
- AI nên đọc `_meta_tables`, `_meta_columns`, `_meta_glossary` trước khi query
- `_meta_kpi` chứa SQL formula cho 14 KPI standard
- Tất cả tên tiếng Việt dùng utf8mb4 (collation utf8mb4_unicode_ci)
- "Hiện tại" trong data = 2026-04-30
- YoY growth: ~12% trong 12 tháng gần nhất

## Reset & re-populate

```bash
docker exec mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS haseca_demo;"
./populate.sh haseca
```
