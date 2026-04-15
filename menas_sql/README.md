# Menas Group Demo Database (`menas_demo`)

## Overview
Multi-business retail & hospitality demo database for Menas Group (Sovico ecosystem).

- **5 Business Units**: Mall (TTTM), Supermarket, F&B, Duty Free, Beauty
- **15 Locations** across HCM and Nha Trang
- **~500 SKU** supermarket products
- **45 Tenants** across 2 malls
- **18 months** of data: 2024-10 to 2026-03

## SQL Files

| File | Description |
|------|-------------|
| `01_ddl_schema.sql` | Schema definition (all tables) |
| `02_metadata.sql` | Metadata tables for AI context |
| `03_master_data.sql` | Dimension/master data |
| `04_a_monthly_revenue.sql` | Monthly revenue by BU/location |
| `04_b_supermarket_sales.sql` | Daily supermarket sales (~78,294 rows) |
| `04_c_fb_data.sql` | F&B revenue and cost data |
| `04_d_tenant_data.sql` | Tenant monthly revenue |
| `04_e_footfall_airport.sql` | Daily footfall data |
| `04_f_shrinkage_promos_events.sql` | Shrinkage data |
| `04_g_employees.sql` | Employee headcount summary |
| `05_validation_queries.sql` | Validation and sanity check queries |

## Embedded Anomalies

1. **Duty Free revenue dip** (Mar 2026): LOC13 revenue x0.95
2. **Supermarket margin compression** (Q1/2026): Cost ratio shifts from 0.78 to 0.787
3. **Imported product mix shift** (Oct 2025 - Mar 2026): Imported share rises from ~30% to ~38%
4. **Tet promo margin erosion** (Jan-Feb 2026): 12% discount on all supermarket items
5. **LOC04 high shrinkage**: Fresh food 3.5%, cosmetics 2.1% vs LOC03 ~1.3%
6. **Thai Siam over-staffing**: Labor cost at 38% of revenue (vs industry 24-28%)
7. **Yum Kim Long declining** (Jan-Mar 2026): Revenue drops 8-15% while costs stay flat
8. **Fashion Line low margin**: Operating margin only 2%, declining revenue 40% YoY
9. **Skechers & TWG Tea surge**: New tenants outperforming at 1.2x base
10. **Thai Siam marketing inefficiency**: Marketing spend up 29% in Feb-Mar 2026 with low ROI
11. **Steakhouse marketing independence**: Marketing cut 20% but revenue unaffected
12. **Kiosk low margins**: KOI (8%), Banh Trang (9%) despite high rent/sqm
13. **Footfall dip** (10-16 Mar 2026): Local segment LOC01 -15% due to B1 renovation
14. **Airport passenger dip** (Mar 2026): TSN traffic -8% post-Tết, drives Duty Free decline

## Usage
```bash
./populate.sh menas
```
