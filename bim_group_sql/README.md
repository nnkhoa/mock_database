# BIM Group - Real Estate & Construction Demo Database

Database mock data cho demo AI engine (Claude + MCP) cho BIM Group.
Focus: Bất động sản nghỉ dưỡng & Quản lý dự án xây dựng.

## Database Info

- **Database:** `bim_realestate_demo`
- **Engine:** MySQL 8.0 (utf8mb4)
- **Data period:** T1/2023 - T6/2024 (18 tháng)
- **Total records:** ~4.700

## Quick Start

```bash
# 1. Khoi tao MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=bim_realestate_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Cho MySQL san sang
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thu tu
docker exec -i mock_database mysql -uroot -proot < bim_group_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < bim_group_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < bim_group_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < bim_group_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < bim_group_sql/05_validation_queries.sql

# 5. Reset (neu can lam lai)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS bim_realestate_demo; CREATE DATABASE bim_realestate_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Roi chay lai buoc 3-4
```

## File Structure

```
bim_group_sql/
├── 01_ddl_schema.sql           # CREATE DATABASE, tables, indexes, constraints
├── 02_metadata.sql             # _meta_tables, _meta_columns, _meta_kpi, _meta_glossary
├── 03_master_data.sql          # Dimension tables (clusters, projects, properties...)
├── 04_transaction_data.sql     # Fact tables (budget, construction, hospitality...)
├── 05_validation_queries.sql   # Validation & demo scenario dry-run
├── generate_transactions.py    # Python script tao 04_transaction_data.sql
└── README.md
```

## Schema Overview

### Dimension Tables
- `clusters` (4) - Cum du an: Ha Long, Phu Quoc, Ha Noi, Vientiane
- `projects` (8) - Du an BDS dang trien khai
- `properties` (6) - Resort/hotel dang van hanh
- `work_packages` (8) - Hang muc xay dung
- `contractors` (18) - Nha thau
- `materials` (6) - Vat lieu xay dung

### Fact Tables
- `budget_disbursements` (84) - Ngan sach giai ngan monthly
- `construction_costs` (377) - Chi phi XD chi tiet
- `change_orders` (23) - Phat sinh thay doi
- `material_prices` (108) - Gia vat lieu monthly
- `project_milestones` (55) - Moc tien do
- `project_financials` (8) - Chi so tai chinh
- `project_commitments` (5) - Cam ket ban giao
- `financing` (8) - Khoan vay
- `hospitality_revenue` (108) - Doanh thu van hanh
- `hospitality_costs` (648) - Chi phi van hanh
- `occupancy_daily` (3282) - Du lieu phong hang ngay

### Metadata Tables
- `_meta_tables` - Mo ta bang
- `_meta_columns` - Mo ta cot
- `_meta_kpi` - Cong thuc KPI
- `_meta_glossary` - Thuat ngu nganh

## Demo Scenarios & Anomalies

1. **Tong quan portfolio** - PJ-HL01 (InterContinental HL): disbursement 71% vs progress 58% (gap 13 diem %)
2. **Vuot du toan Ha Long** - M&E, Noi that, Ket cau vuot manh. 6 change orders, 3 do brand compliance IHG
3. **Van hanh resort** - Citadines HL: GOP 12% (staff 42%), Crowne Plaza: GOP 8% (occupancy thap)
4. **So sanh cluster** - PQ chi phi/m2 cao hon HL 23% nhung margin cao hon
5. **Cat giam ngan sach** - PJ-HL04 (Chuan bi) co the defer, 4 du an co cam ket ban giao
