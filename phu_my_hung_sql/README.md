# Phú Mỹ Hưng Development — Demo Database

**Database:** `phu_my_hung_demo`
**Tables:** 33 (7 dimension + 22 fact + 4 metadata)
**Records:** ~15,000+
**Data range:** 01/2024 – 06/2025 (18 months)

## Quick Start

```bash
# 1. Start MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=phu_my_hung_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Wait for MySQL ready
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data in order
docker exec -i mock_database mysql -uroot -proot < phu_my_hung_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < phu_my_hung_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < phu_my_hung_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < phu_my_hung_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < phu_my_hung_sql/05_validation_queries.sql

# 5. Reset (if needed)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS phu_my_hung_demo; CREATE DATABASE phu_my_hung_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Then re-run steps 3-4
```

## Demo Scenarios

| # | Question | Key Tables | Anomaly |
|---|----------|-----------|---------|
| 1 | Portfolio performance — revenue, cost, margin | `project_financials`, `projects`, `revenue_recognition` | L'Arcade: 100% sell-through but 62% recognized |
| 2 | The Horizon cost overrun drivers | `construction_costs`, `material_prices`, `change_orders`, `contractor_invoices` | Steel spike +18%, Hòa Bình delays, 3 change orders → 12% overrun |
| 3 | Contractor OTD ranking | `contract_milestones`, `contractors`, `project_assignments` | Delta Construction: ~70% OTD vs portfolio avg ~85% |
| 4 | Cash flow projection next 2 quarters | `payment_collections`, `construction_payment_schedule`, `debt_payments` | Hồng Hạc infrastructure front-loading creates Q3 deficit |
| 5 | Top financial risks for board | `debt_schedule`, `unsold_inventory`, `project_permits` | $180M bonds maturing in 4 months + 14 unsold shops aging >12mo |
| 6 | PM cost per unit rising — which zones? | `management_costs`, `management_zones`, `maintenance_tickets` | Cảnh Đồi: elevator +3.5%/mo, waterproofing +2.8%/mo compound |

## Projects

| ID | Name | City | Segment | Units | Status |
|----|------|------|---------|-------|--------|
| PRJ-001 | The Aurora | HCMC | premium | 95 | selling |
| PRJ-002 | L'Arcade | HCMC | ultra_luxury | 37 | construction |
| PRJ-003 | Cardinal Court | HCMC | luxury | 200 | delivered |
| PRJ-004 | The Horizon | HCMC | luxury | 476 | delivered |
| PRJ-005 | Hồng Hạc City Ph1 | Bắc Ninh | mid_high | 300 | infrastructure |
| PRJ-006 | Scenic Valley 2 | HCMC | premium | 45 | selling |

## Key Metadata Tables

- `_meta_tables` — Description of every table (AI reads this first)
- `_meta_columns` — Column definitions with units and examples
- `_meta_kpi` — 12 KPI formulas with SQL
- `_meta_glossary` — Vietnamese ↔ English terminology (21 terms)

## File Structure

```
phu_my_hung_sql/
├── 01_ddl_schema.sql           # Schema: 33 tables with indexes and constraints
├── 02_metadata.sql             # 4 metadata tables: _meta_tables, _meta_columns, _meta_kpi, _meta_glossary
├── 03_master_data.sql          # 7 dimension tables: projects, contractors, zones, tenants, etc.
├── 04_transaction_data.sql     # 22 fact tables: financials, sales, costs, debt, maintenance, etc.
├── 05_validation_queries.sql   # Validation queries for all 6 scenarios + off-script checks
└── README.md                   # This file
```

## Regeneration

To regenerate from scratch with the Python script:

```bash
cd "Demo Data"
python3 generate_phu_my_hung.py
```

This will:
1. Drop and recreate the database
2. Create schema, load metadata and master data
3. Generate 18 months of transaction data with anomalies
4. Export to `phu_my_hung_sql/04_transaction_data.sql`
