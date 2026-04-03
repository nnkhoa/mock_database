# SASCO Demo Database

Mock database cho demo AI for BI tai Cong ty Co phan Dich vu Hang khong San bay Tan Son Nhat (SASCO).

## Thong tin ket noi

- **Database:** `sasco_demo`
- **Host:** localhost:3306
- **User:** root / root
- **Charset:** utf8mb4

## Cau truc thu muc

```
sasco_sql/
├── 01_ddl_schema.sql           # CREATE DATABASE, CREATE TABLE, indexes, constraints
├── 02_metadata.sql             # INSERT _meta_tables, _meta_columns, _meta_kpi, _meta_glossary
├── 03_master_data.sql          # INSERT dimension tables (terminals, lounges, products...)
├── 04_transaction_data.sql     # INSERT fact tables (sales, lounge_visits, passenger_traffic)
├── 05_validation_queries.sql   # SELECT queries de verify data
└── README.md                   # Huong dan nay
```

## Huong dan populate tren may moi

```bash
# 1. Khoi tao MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=sasco_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Cho MySQL san sang
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thu tu
docker exec -i mock_database mysql -uroot -proot < sasco_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < sasco_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < sasco_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < sasco_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < sasco_sql/05_validation_queries.sql

# 5. Reset (neu can lam lai)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS sasco_demo; CREATE DATABASE sasco_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Roi chay lai buoc 3-4
```

## Tong quan data

### Dimension tables (7)

| Table | Records | Mo ta |
|-------|---------|-------|
| terminals | 5 | T1 (Noi dia), T2 (Quoc te), T3 (Hon hop, mo 04/2025), Cam Ranh, Phu Quoc |
| business_lines | 4 | Phong cho, Mien thue, F&B, Dich vu khac |
| locations | 37 | Diem kinh doanh: 15 phong cho, 5 DF, 12 F&B, 5 dich vu |
| lounges | 15 | Chi tiet phong cho (extend locations) |
| nationality_groups | 13 | 0=Noi dia + 12 nhom quoc te |
| product_categories | 30 | Hierarchy 2 cap |
| products | 394 | SKU thuc te voi Pareto weights |

### Fact tables (3)

| Table | Records | Grain | Date range |
|-------|---------|-------|------------|
| passenger_traffic | ~18K | 1 ngay x 1 terminal x 1 nationality | 01/2024-06/2025 |
| lounge_visits | ~168K | 1 phong cho x 1 ngay x 1 gio | 01/2024-06/2025 |
| sales_transactions | ~5.4M | 1 line item | 01/2024-06/2025 |

### Metadata tables (4)

| Table | Mo ta |
|-------|-------|
| _meta_tables | Mo ta cac bang - AI engine dung de hieu database |
| _meta_columns | Mo ta cac cot - AI engine dung de hieu y nghia |
| _meta_kpi | Cong thuc KPI - AI engine dung de tinh toan |
| _meta_glossary | Thuat ngu nganh - AI engine dung de hieu cau hoi tieng Viet |

### Revenue overview (2024)

| Mang kinh doanh | Revenue (ty VND) | Ty trong |
|------------------|-------------------|----------|
| Phong cho thuong gia | ~895 | 29.9% |
| Cua hang mien thue | ~1,042 | 34.8% |
| F&B & Ban le | ~753 | 25.2% |
| Dich vu khac | ~302 | 10.1% |
| **Tong** | **~2,992** | **100%** |

### Demo scenarios

1. **Buc tranh tong quan:** Revenue + margin theo 4 mang, YoY comparison
2. **Nghich ly mien thue:** PAX tang ma DF tang cham - root cause: nationality mix shift
3. **Hieu suat phong cho:** Heatmap utilization theo gio/ngay - peak/trough pattern
4. **T3 ramp-up:** Weekly revenue curve tu khi T3 mo (04/2025)
5. **Spend per nationality:** Category preferences theo quoc tich

### Anomalies co chu dich

- **Nationality mix shift:** Tu 01/2025, Ấn Do va Campuchia tang ty trong, Han Quoc giam
- **Lounge T1 skew:** Phong cho noi dia T1 peak 6-9h (95-104%), trung 12-15h (19-25%)
- **T3 ramp-up:** Revenue tang tu 2.67 ty/tuan len ~11 ty/tuan trong 10 tuan
- **DF slow growth:** Mien thue chi tang ~15% YoY vs tong 18.6%

### Luu y cho AI engine

- Data range: 01/2024 - 06/2025 (18 thang)
- T3 data bat dau tu 01/04/2025
- Phu Quoc data bat dau tu 01/11/2024
- Metadata tables co day du mo ta schema, KPI formulas, glossary tieng Viet
- ENUM values dung ASCII (Quoc te, Noi dia, Hon hop)
