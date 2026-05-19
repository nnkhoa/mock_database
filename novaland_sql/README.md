# Novaland Demo Database

Mock database for Novaland (NVL) Real Estate - Bất động sản Phát triển Dự án

## Overview

- **Database**: `novaland_demo`
- **Target**: CEO/Board of Novaland during restructuring
- **Focus**: Cost/margin optimization, operational efficiency, debt coverage
- **Data Range**: January 2023 - December 2025 (historical + forecast)

## Quick Start

### 1. Using existing MySQL container

```bash
# Database already running in mock_database container
# Just connect and query:
docker exec -it mock_database mysql -uroot -proot novaland_demo
```

### 2. From scratch (new container)

```bash
# Create MySQL container
docker run --name novaland_mock \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=novaland_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# Wait for MySQL to be ready
docker exec novaland_mock mysqladmin ping -uroot -proot --wait=30

# Populate data in order
docker exec -i novaland_mock mysql -uroot -proot < 01_ddl_schema.sql
docker exec -i novaland_mock mysql -uroot -proot < 02_metadata.sql
docker exec -i novaland_mock mysql -uroot -proot < 03_master_data.sql
docker exec -i novaland_mock mysql -uroot -proot < 04_transaction_data.sql
```

### 3. Verify installation

```bash
docker exec -i novaland_mock mysql -uroot -proot < 05_validation_queries.sql
```

## Database Structure

### Dimension Tables (8)
- `dim_projects` - 8 projects (Aqua City, NovaWorld PT, NovaWorld HT, etc.)
- `dim_products` - 22 product types by project
- `dim_cost_types` - 7 cost categories (COGS + OPEX)
- `dim_delay_reasons` - 5 delay reasons (legal, construction, financial)
- `dim_lenders` - 6 lenders (3 banks + 2 bonds + 1 foreign)
- `dim_land_bank` - 8 undeveloped land parcels (~2,400ha)
- `dim_market_demand` - Market demand by region and product
- `dim_calendar` - Calendar 2023-2025 with special flags

### Fact Tables (9)
- `fact_project_costs` - Monthly costs by project and type
- `fact_capitalized_interest` - Monthly capitalized interest
- `fact_deliveries` - Delivery batches with delays
- `fact_delivery_pipeline` - 12-month forecast
- `dim_debt_schedule` - Debt obligations by month
- `dim_contracts` - Customer contracts (~3,500)
- `fact_payment_schedule` - Payment schedules
- `fact_collections` - Actual collections with overdue tracking
- `fact_irr_estimates` - IRR estimates for land bank

### Metadata Tables (4)
- `_meta_tables` - Table descriptions
- `_meta_columns` - Column descriptions
- `_meta_kpi` - KPI definitions and formulas
- `_meta_glossary` - Real estate terminology

## Demo Scenarios

The database includes 5 intentional anomalies for demo:

1. **Aqua City margin erosion**: Plan 28% → Actual 19% (-9pp)
   - Cause: 15% interest rate increase from July 2024 + delays

2. **Aqua City Phase 2 delay**: 7 months behind schedule
   - Cost: ~3.2T VND/month

3. **NovaWorld PT overdue spike**: 82.7% contracts overdue >30 days
   - Triggered by Phase 3 delay announcement (Aug 2024)

4. **Bond maturity spikes**: Sep & Dec 2025 cashflow gaps
   - Sep: -1,313T, Dec: -779T

5. **Lakeview City stalled**: 906.7T costs, zero revenue
   - Legal issues blocking all deliveries

## KPI Tree

```
Gross Margin (%) = (Revenue − COGS) / Revenue
├── Revenue (By Project, Product Type, Quarter)
├── COGS
│   ├── Land cost (20-40%)
│   ├── Construction cost (40-50%)
│   ├── Capitalized interest (8-15%)
│   └── Infrastructure & QLDA (8-12%)
├── Delay Cost = interest × delay_months
├── AR Quality = overdue / total_receivable
└── Debt Coverage = revenue_12m / debt_obligation_12m
```

## Sample Queries

### Check margin by project
```sql
SELECT p.project_name,
       p.planned_gross_margin_pct AS plan,
       ROUND((SUM(d.revenue_recognized_vnd) - SUM(d.cogs_recognized_vnd)) /
             SUM(d.revenue_recognized_vnd) * 100, 2) AS actual
FROM dim_projects p
LEFT JOIN fact_deliveries d ON p.project_id = d.project_id
GROUP BY p.project_id, p.project_name, p.planned_gross_margin_pct;
```

### Monthly capitalized interest
```sql
SELECT interest_month,
       SUM(monthly_interest_vnd)/1e9 AS monthly_ty,
       SUM(cumulative_interest_vnd)/1e9 AS cumulative_ty
FROM fact_capitalized_interest
GROUP BY interest_month
ORDER BY interest_month;
```

## Data Summary

- **Total rows**: 51,539 (excluding metadata)
- **Historical period**: Jan 2023 - Dec 2024 (24 months)
- **Forecast period**: Jan 2025 - Dec 2025 (12 months)
- **Projects**: 8 (3 active, 2 stalled, 2 delivering, 1 completed)
- **Contracts**: 3,470
- **Deliveries**: 24 batches
- **Land bank**: 8 parcels (~2,400ha)

## Connection Info

```
Host: localhost
Port: 3306
User: root
Password: root
Database: novaland_demo
Charset: utf8mb4
```

## Reset Database

```bash
# Drop and recreate
docker exec novaland_mock mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS novaland_demo; CREATE DATABASE novaland_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Re-populate
docker exec -i novaland_mock mysql -uroot -proot < 01_ddl_schema.sql
# ... etc
```

## File Structure

```
novaland_sql/
├── 01_ddl_schema.sql       -- CREATE TABLE statements
├── 02_metadata.sql          -- Metadata tables data
├── 03_master_data.sql       -- Dimension tables data
├── 04_transaction_data.sql  -- Fact tables data
├── 05_validation_queries.sql -- Validation queries
└── README.md                -- This file
```

---

Generated: 2026-05-19 11:21:15
Database: novaland_demo
Total Tables: 21
Total Rows: ~51,500
