# VRI Group — Khối Dịch vụ (Hotels + Cosmos) — Mock Database

Mock database cho demo COO Khối Dịch vụ pitching Hội đồng Quản trị VRI Group.
Bao gồm 6 khách sạn (Hotels) + hệ sinh thái Miss Cosmo (Cosmos).

- **Database name:** `vri_services_demo`
- **Time range:** 1/6/2024 → 30/11/2025 (18 tháng)
- **Charset:** utf8mb4 / utf8mb4_unicode_ci
- **Currency:** VND, DECIMAL(15-18, 0)

## Cấu trúc

```
vri_services_sql/
├── 01_ddl_schema.sql           — DDL: 12 dim + 11 fact + 4 metadata tables
├── 02_metadata.sql             — _meta_tables / _meta_columns / _meta_kpi / _meta_glossary
├── 03_master_data.sql          — Master data 12 dimension tables
├── 04_transaction_data.sql     — Fact data 11 fact tables (~250k rows total)
├── 05_validation_queries.sql   — Sanity / scenario / fallback queries
└── README.md                   — File này
```

## Populate vào Docker container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=vri_services_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i mock_database mysql -uroot -proot < vri_services_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < vri_services_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < vri_services_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < vri_services_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < vri_services_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS vri_services_demo; CREATE DATABASE vri_services_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Tổng quan dữ liệu

### Hotels — 6 khách sạn (944 phòng)

| Property | Class | Loại | Phòng | Vị trí | OTA baseline |
|---|---|---|---|---|---|
| Diamond Stars Bến Tre | 5★ | City Luxury | 138 | Bến Tre | 48% |
| Royal Hotel & Villas Đà Lạt | 4★ | Hill Resort | 256 | Đà Lạt | 38% |
| Royal Golf Club Long An | 5★ | Golf Resort | 80 | Long An | 30% |
| Royal Beach Resort Nha Trang | 5★ | Beach Resort | 200 | Nha Trang | 42% (anomaly 11/2025: 58%) |
| Royal Boutique Sài Gòn | 4★ | City Business | 120 | TP.HCM | 35% |
| Royal Heritage Đà Nẵng | 4★ | Heritage | 150 | Đà Nẵng | 55% |

### Cosmos — Hệ sinh thái Miss Cosmo

- **4 events:** MCV2023 Đà Lạt | MCO2024 TP.HCM | MCV2025 Nha Trang | MCO2025 TP.HCM
- **35 sponsors** với 5 tier (Title/Diamond/Gold/Silver/Bronze)
- **Revenue streams:** sponsorship, broadcasting, ticket, merchandise, licensing, membership, voting

## 3 Demo Scenarios

### Scenario 1 — Tổng quan Khối Dịch vụ
> *"Tình hình kinh doanh Khối Dịch vụ tháng 11/2025 thế nào? So với cùng kỳ năm ngoái?"*

- Khối DV 11/2025: ~182 tỷ
- Hotels 11/2025: ~160 tỷ (+11% YoY)
- Cosmos 11/2025: 22.6 tỷ (post-event tail sau MCO2025)

### Scenario 2 — Royal Beach NT diagnostic
> *"Tại sao Royal Beach Resort Nha Trang doanh thu giảm tháng 11/2025?"*

**Anomaly đã inject (Oct 15 - Nov 30, 2025):**
- Revenue YoY: -14.6% ✅
- ADR YoY: -17.2% ✅
- Channel mix shift: OTA 42% → 59% ✅
- Source market: Trung Quốc -32%, Hàn Quốc -8%, Việt Nam +19%
- Weather: 9 ngày heavy_rain Nov 2025 NTB

### Scenario 3 — What-if giảm OTA xuống 30%
> *"Nếu giảm phụ thuộc kênh đặt phòng trực tuyến xuống 30%, doanh thu và lợi nhuận thay đổi thế nào?"*

OTA share theo property (12T qua):
- Royal Golf 40% < Boutique 41% < Đà Lạt 42% < Beach 47% < Diamond 55% < Heritage 60%

Property nào dễ giảm OTA nhất (Golf, Boutique) vs khó nhất (Heritage, Beach NT).

## Anomalies inject

1. **Royal Beach NT 11/2025**: Channel shift + ADR drop + Source market shift + Weather (4 chiều)
2. **Sponsor anomalies**:
   - NCA Diamond & Jewelry: Gold 2024 nhưng không gia hạn 2025 (0 contracts trong MCV2025/MCO2025)
   - Highlands Coffee: Silver MCO2025, đợt 2 `payment_status='overdue'`
3. **Royal Heritage ĐN**: OTA dependency cao (60%) — anomaly cấu trúc, hỗ trợ Scenario 3

## KPI sẵn có (xem `_meta_kpi`)

ADR, Occupancy, RevPAR, TRevPAR, GOP, GOPPAR, ALOS, OTA Share, F&B Contribution, Cosmos Sponsor Concentration

## Magnitude check

- Hotels 12T: 1.849 tỷ (target ~1.850 ✅)
- Cosmos 12T: 332 tỷ (theo monthly pattern spec)
- Khối DV total: 2.181 tỷ (target ~2.130 ✅)
- Tỷ lệ Hotels Room 67% / F&B 22% / Other 11% ✅

## Generators (Python)

- `generate_vri_services.py` — master data (chạy sau 01_ddl)
- `generate_vri_transactions.py` — transaction data + 04 SQL export
- `validate_vri_services.py` — validation report
