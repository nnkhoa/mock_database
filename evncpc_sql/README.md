# EVNCPC Demo Database

Database mock data cho demo AI + MCP tại Tổng Công ty Điện lực miền Trung (EVNCPC).

## Thông tin database

- **Database name:** `evncpc_demo`
- **Character set:** utf8mb4 / utf8mb4_unicode_ci
- **Thời gian dữ liệu:** 24 tháng (10/2023 - 09/2025)
- **Tháng gần nhất:** Tháng 9/2025

### Quy mô dữ liệu

| Loại | Table | Records |
|------|-------|---------|
| Dimension | power_companies | 8 |
| Dimension | provinces | 13 |
| Dimension | districts | 64 |
| Dimension | substations | 772 |
| Dimension | grid_assets | 542 |
| Dimension | customer_segments | 40 |
| Dimension | loss_targets | 16 |
| Dimension | weather_events | 28 |
| Fact | monthly_kpi_summary | 192 |
| Fact | power_loss_detail | 1,536 |
| Fact | grid_incidents | 2,284 |
| Fact | investment_history | 65 |
| Fact | operating_costs | 1,536 |
| Metadata | _meta_tables, _meta_columns, _meta_kpi, _meta_glossary | ~170 |

### 8 Công ty Điện lực

| PC_ID | Tên | Tỉnh/TP | Ghi chú |
|-------|-----|----------|---------|
| PC01 | PC Quảng Trị | Quảng Bình + Quảng Trị | Rủi ro bão cao nhất |
| PC02 | PC Huế | Thừa Thiên Huế | |
| PC03 | PC Đà Nẵng | Đà Nẵng + Quảng Nam | Lớn nhất, DMS tốt |
| PC04 | PC Quảng Ngãi | Quảng Ngãi + Kon Tum | |
| PC05 | PC Gia Lai | Gia Lai + Bình Định | Anomaly: tổn thất cao |
| PC06 | PC Đắk Lắk | Đắk Lắk + Phú Yên | Anomaly: SAIDI tăng |
| PC07 | PC Khánh Hòa | Khánh Hòa + Ninh Thuận | |
| PC08 | CP ĐL Khánh Hòa | Khánh Hòa (Nha Trang) | Công ty cổ phần |

## Hướng dẫn populate

### 1. Khởi tạo MySQL container

```bash
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=evncpc_demo \
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
docker exec -i mock_database mysql -uroot -proot < evncpc_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < evncpc_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < evncpc_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < evncpc_sql/04_transaction_data.sql
```

### 4. Verify

```bash
docker exec -i mock_database mysql -uroot -proot < evncpc_sql/05_validation_queries.sql
```

### 5. Reset (nếu cần làm lại)

```bash
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS evncpc_demo; CREATE DATABASE evncpc_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3-4
```

## Demo Scenarios

Database chứa 5 demo scenarios với anomalies có chủ đích:

1. **Tổng quan KPI 8 PC** — AI tự flag PC Gia Lai (tổn thất 4.80%) và PC Đắk Lắk (SAIDI +26% YoY)
2. **Root cause tổn thất PC Gia Lai** — MBA cũ (>15 năm) tại 4 huyện Bình Định gây tổn thất hạ thế cao
3. **Sự cố mùa bão Q3** — 287 vụ (vs 198 Q3 năm trước, +45%), PC Quảng Trị nặng nhất (115 vụ, 46 tỷ)
4. **Cảnh báo sớm tổn thất** — PC Gia Lai projected 4.95% vs target 4.40%, PC Đắk Lắk 3.88% vs 3.75%
5. **Tối ưu phân bổ 500 tỷ đầu tư** — Cross-query substations + grid_assets + investment_history

## Cấu trúc SQL files

```
evncpc_sql/
├── 01_ddl_schema.sql           # CREATE DATABASE, CREATE TABLE
├── 02_metadata.sql             # _meta_tables, _meta_columns, _meta_kpi, _meta_glossary
├── 03_master_data.sql          # Dimension tables (power_companies, provinces, ...)
├── 04_transaction_data.sql     # Fact tables (monthly_kpi_summary, grid_incidents, ...)
├── 05_validation_queries.sql   # Validation queries
└── README.md                   # File này
```

## Generator script

Để regenerate data từ đầu: `python3 generate_evncpc.py all`
