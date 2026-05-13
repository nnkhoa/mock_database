# Mitsubishi Motors Vietnam Demo Database (`mmv_auto_demo`)

**Database for Mitsubishi Motors Vietnam (MMV) board-level demo.**

- **Audience:** MMC global board (Tokyo) + MMV leadership (HCMC/Hanoi)
- **Language:** All master data values in **Japanese (日本語)**; table/column names in English snake_case
- **Charset:** `utf8mb4 / utf8mb4_unicode_ci` (REQUIRED for Japanese 4-byte characters)
- **Size:** ~18 MB DB, ~225,000 rows

## Tables (24 total)

- **12 dimension tables:** calendar, model (8), dealer (45), region (31), customer_segment (4), channel (4), competitor_brand (12), competitor_model (30), fx_rate (1096 daily), fuel_price (53 weekly), brent_oil_price (1096 daily), promotion (6)
- **8 fact tables:** sales_out (~50k), sales_target (~3.6k), production_ckd (~260), inventory (~16k), test_drive (~150k), competitor_sales (~360), market_total (~108), cogs (100 = 15 months × 8 models)
- **4 metadata tables:** _meta_tables, _meta_columns, _meta_kpi, _meta_glossary

## Demo Scenarios Built In

1. **Performance overview (T6/2026):** ~4,200 units, +38% YoY (real MMV Q1/2026 was +50%)
2. **Margin compression Q1/2026 vs Q1/2025:** OP margin compressed from 6.8% → 3.7%
3. **Geopolitical fuel shock (May-Jun 2026):** Brent $78→$94, RON95 24,500→27,800; Pajero Sport -26%, Triton -32%
4. **Dealer underperformers (Q1/2026):** D-MEK-CTH (internal sales), D-VTI-VIN (Nghệ An flood), D-TDO-DLK (ramp-up)
5. **Destinator launch cannibalization (Dec 2025):** Pajero Sport -39%, Xforce -38%, CX-5 -345/mo lost to MMV

## Setup Instructions

```bash
# 1. Start MySQL container
docker run --name mmv_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=mmv_auto_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Wait for MySQL ready
docker exec mmv_database mysqladmin ping -uroot -proot --wait=30

# 3. Load data in order
docker exec -i mmv_database mysql -uroot -proot < 01_ddl_schema.sql
docker exec -i mmv_database mysql -uroot -proot < 02_metadata.sql
docker exec -i mmv_database mysql -uroot -proot < 03_master_data.sql
docker exec -i mmv_database mysql -uroot -proot < 04_transaction_data.sql

# 4. Verify (runs scenario queries)
docker exec -i mmv_database mysql -uroot -proot < 05_validation_queries.sql

# 5. Reset database (if needed)
docker exec -i mmv_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS mmv_auto_demo; \
   CREATE DATABASE mmv_auto_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Verifying Japanese Display

```bash
docker exec mmv_database mysql --default-character-set=utf8mb4 \
  -uroot -proot mmv_auto_demo \
  -e "SELECT model_id, model_name_jp FROM dim_model LIMIT 3;"
```

Should display: `エクスパンダー`, `エクスパンダー・クロス`, `エクスフォース`

## Key Special Records

| dealer_id | dealer_name_jp | scenario |
|---|---|---|
| `D-MEK-CTH` | ミツビシ・アンカン・カントー | Q1/2026 internal sales weakness, 18% conversion |
| `D-VTI-VIN` | ミツビシ・ベトティエン・ヴィン | Sept 2025 Nghệ An flood impact, Triton -65% |
| `D-TDO-DLK` | ミツビシ・タイドー・ダクラク | New dealer (opened 6/2024), still ramping |

| model_id | model_name_jp | special date |
|---|---|---|
| `M07` | アウトランダー | EOL 2025-11-30 (volume = 0 from Dec 2025) |
| `M08` | デスティネーター | Launch 2025-12-01 |
| `M02` | エクスパンダー・クロス | Launch 2025-09-22 |
