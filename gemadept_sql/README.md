# Gemadept Seaport Demo Database

## Thông tin
- **Database:** `seaport_demo`
- **Mục đích:** Demo AI engine (Claude + MCP) cho Tập đoàn Gemadept (GMD)
- **Data range:** 2024-01 → 2025-06 (18 tháng)
- **Tables:** 8 dimension + 8 fact + 4 metadata = 20 tables
- **Records:** ~8,500+ rows

## Cách populate

### 1. Khởi tạo MySQL container
```bash
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=seaport_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

### 2. Chờ MySQL sẵn sàng
```bash
docker exec mock_database mysqladmin ping -uroot -proot --wait=30
```

### 3. Populate data theo thứ tự
```bash
docker exec -i mock_database mysql -uroot -proot < gemadept_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < gemadept_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < gemadept_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < gemadept_sql/04_transaction_data.sql
```

### 4. Verify
```bash
docker exec -i mock_database mysql -uroot -proot < gemadept_sql/05_validation_queries.sql
```

### 5. Reset (nếu cần làm lại)
```bash
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS seaport_demo; CREATE DATABASE seaport_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3
```

## Cấu trúc files
| File | Nội dung | Rows ước tính |
|------|----------|---------------|
| 01_ddl_schema.sql | CREATE DATABASE, CREATE TABLE, indexes, constraints | 20 tables |
| 02_metadata.sql | _meta_tables, _meta_columns, _meta_kpi, _meta_glossary | ~180 rows |
| 03_master_data.sql | Dimension tables (ports, shipping_lines, equipment...) | ~110 rows |
| 04_transaction_data.sql | Fact tables (revenue, costs, vessel_calls...) | ~8,400 rows |
| 05_validation_queries.sql | SELECT queries để verify data | — |

## Demo Scenarios
| # | Câu hỏi | Anomaly/Pattern |
|---|---------|-----------------|
| 1 | Tổng quan KD 6 tháng | No anomaly — aggregate view |
| 2 | Tại sao margin NDV giảm? | Maintenance spike + bulk mix + energy cost |
| 3 | So sánh NDV vs Gemalink | Structural differences (pricing, productivity) |
| 4 | Hãng tàu giảm sản lượng? | Maersk -18% at NDV (Apr-Jun 2025) |
| 5 | Dự báo margin 2 quý tới | Uses historical trend |
| 6 | Breakeven Gemalink 2A | investment_projects + benchmark data |

## Known Anomalies
- **NDV maintenance spike (May-Jun 2025):** STS Crane #3 and #4 major overhaul → operating_costs.maintenance ×2.5-2.8
- **NDV bulk mix increase (May-Jun 2025):** Xi Măng Hải Phòng clinker export → bulk volume ×1.6-1.85
- **Energy cost step change (Apr 2025+):** All ports energy ×1.12 (EVN price adjustment)
- **Maersk decline at NDV (Apr-Jun 2025):** Volume ×0.82-0.90, vessel calls 8→6

## Cho AI Engine
- Query `_meta_tables` và `_meta_kpi` đầu tiên để hiểu database
- Data range: 2024-01 → 2025-06
- "Hiện tại" = tháng 6/2025
- NDV May-Jun 2025 có anomaly rõ ràng — AI nên detect được
