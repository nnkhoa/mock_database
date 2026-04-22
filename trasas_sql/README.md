# TRASAS Demo Database

Mock database cho **CTCP Vận Tải và Dịch Vụ Hàng Hải TRA-SAS** (mã CK: TRS).

## Thông tin

- **Database:** `trasas_demo`
- **MySQL:** 8.0, charset utf8mb4
- **Data range:** 2024-01-01 → 2025-06-30 (18 tháng)
- **Tổng doanh thu:** ~1,628 tỷ VND (18 tháng)
- **4 mảng:** FWD (41%), WHS (28%), CUS (15%), TRK (16%)

## Cách sử dụng

### Khởi tạo MySQL container

```bash
docker run --name trasas_mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=trasas_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

### Chờ MySQL sẵn sàng

```bash
docker exec trasas_mysql mysqladmin ping -uroot -proot --wait=30
```

### Populate data theo thứ tự

```bash
docker exec -i trasas_mysql mysql -uroot -proot < sql_export/01_ddl_schema.sql
docker exec -i trasas_mysql mysql -uroot -proot < sql_export/02_metadata.sql
docker exec -i trasas_mysql mysql -uroot -proot < sql_export/03_master_data.sql
docker exec -i trasas_mysql mysql -uroot -proot < sql_export/04_transaction_data.sql
```

### Verify

```bash
docker exec -i trasas_mysql mysql -uroot -proot < sql_export/05_validation_queries.sql
```

### Reset (nếu cần làm lại)

```bash
docker exec -i trasas_mysql mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS trasas_demo; CREATE DATABASE trasas_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước populate
```

## Cấu trúc files

| File | Nội dung | Kích thước |
|---|---|---|
| `01_ddl_schema.sql` | CREATE TABLE cho 17 bảng | ~15 KB |
| `02_metadata.sql` | INSERT _meta_tables, _meta_kpi, _meta_glossary, _meta_columns | ~5 KB |
| `03_master_data.sql` | INSERT dimension tables + contracts | ~28 KB |
| `04_transaction_data.sql` | INSERT fact tables (service_orders, freight_costs, warehouse_stats, delivery) | ~9 MB |
| `05_validation_queries.sql` | SELECT queries để verify data | ~5 KB |

## Tables

### Dimension (9 bảng)
- `service_types` — 4 mảng: FWD, WHS, CUS, TRK
- `customers` — 35 KH, top 10 chiếm ~70% DT
- `customer_service_map` — 82 mappings KH × mảng (cross-sell analysis)
- `warehouses` — 6 kho (WH-PT01 = kho mới hóa chất, vận hành từ 01/2025)
- `vehicles` — 45 xe (25 container, 15 tải, 5 hàng nguy hiểm)
- `trade_lanes` — 9 tuyến quốc tế (8 sea + 1 air)
- `regions` — 3 khu vực (Miền Nam 60%, Bắc 30%, Trung 10%)
- `employees` — 18 account managers
- `contracts` — 63 hợp đồng (30% FWD = FIXED rate)

### Fact (4 bảng)
- `service_orders` — ~52.000 rows, fact chính
- `freight_costs` — 162 rows (18 tháng × 9 lanes)
- `warehouse_monthly_stats` — 96 rows
- `delivery_performance` — ~52.000 rows (1:1 với orders)

### Metadata (4 bảng)
- `_meta_tables` — mô tả 13 bảng chính
- `_meta_kpi` — 10 KPI definitions
- `_meta_glossary` — 20 thuật ngữ logistics
- `_meta_columns` — 14 cột quan trọng

## 6 Demo Scenarios

| # | Scenario | Anomaly |
|---|---|---|
| S1 | Tổng quan DT 12 tháng | FWD growth chỉ +5% (vs WHS +21%) |
| S2 | Margin erosion | FWD margin 17% → 7.5% (buying +22%, selling +9%) |
| S3 | 3 Signals | Kho PT01 util 32%, OTD TRK Bắc 83%, Fonterra -35% |
| S4 | Customer concentration | Top 10 = 70%. Coca-Cola 4 mảng, Siemens 1 mảng |
| S5 | Pass-through lag | Spread thu hẹp, FIXED margin 3.8% vs SPOT 7.9% |
| S6 | What-if +50% cước | Dùng data S2+S5, AI extrapolate |

## Lưu ý cho AI engine (MCP)

- Query `_meta_tables` và `_meta_columns` để hiểu schema
- Tất cả giá trị tiền tệ đơn vị **VND**
- Anomalies embedded — AI phải tự phát hiện
- `freight_costs.buying_rate` là cước mua theo tháng × tuyến
- `service_orders.selling_rate` là cước bán theo đơn hàng
- `contracts.rate_type` = 'FIXED' nghĩa là giá bán không đổi theo HĐ
- `warehouse_monthly_stats` cho WH-PT01 chỉ có từ 2025-01
