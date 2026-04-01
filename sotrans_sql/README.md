# SOTRANS Demo Database — Setup Guide

## Quick Start

### 1. Khởi tạo MySQL container
```bash
docker run --name sotrans_mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=sotrans_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

### 2. Chờ MySQL sẵn sàng
```bash
docker exec sotrans_mysql mysqladmin ping -uroot -proot --wait=30
```

### 3. Populate data (theo thứ tự)
```bash
docker exec -i sotrans_mysql mysql -uroot -proot < sql_export/01_ddl_schema.sql
docker exec -i sotrans_mysql mysql -uroot -proot < sql_export/02_metadata.sql
docker exec -i sotrans_mysql mysql -uroot -proot < sql_export/03_master_data.sql
docker exec -i sotrans_mysql mysql -uroot -proot < sql_export/04_transaction_data.sql
```

### 4. Verify
```bash
docker exec -i sotrans_mysql mysql -uroot -proot < sql_export/05_validation_queries.sql
```

### 5. Reset nếu cần
```bash
docker exec -i sotrans_mysql mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS sotrans_demo; CREATE DATABASE sotrans_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Files
| File | Nội dung |
|------|----------|
| `01_ddl_schema.sql` | CREATE DATABASE + tất cả CREATE TABLE |
| `02_metadata.sql` | Metadata tables (_meta_tables, _meta_kpi, _meta_glossary) |
| `03_master_data.sql` | Dimension tables (service_types, warehouses, customers, routes...) |
| `04_transaction_data.sql` | Fact tables (18 tháng transaction data với anomalies) |
| `05_validation_queries.sql` | Validation + demo scenario queries |

## Demo Scenarios
- **S1**: Báo cáo tổng quan — freight giảm T7-T9/2024
- **S2**: Margin erode HCM-NRT — Texhong, cost tăng 22%, margin từ 11% → 3.2%
- **S3**: Kho Long An utilization giảm từ 83% → 52% — Uni-President rút dần
- **S4**: Pace analysis — FF YTD 67% kế hoạch, dự báo miss target
- **S5**: Customer profitability — Texhong revenue cao nhưng margin thấp nhất
