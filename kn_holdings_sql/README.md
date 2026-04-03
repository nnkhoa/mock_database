# KN Holdings - Database BDS Demo

Database mock cho demo AI+MCP trong linh vuc Bat Dong San.

## Database: `kn_realestate_demo`

| File | Mo ta |
|---|---|
| 01_ddl.sql | Schema 18 tables (8 dimension + 6 fact + 4 metadata) |
| 02_metadata.sql | Meta tables, KPI, glossary |
| 03_master_data.sql | Du an, phan khu, san pham, khach hang, dai ly |
| 04_transaction_data.sql | Giao dich, leads, ton kho, marketing, targets |
| 05_validation.sql | Validation queries + demo dry-run |

## Thong so

- **Data range:** T7/2023 - T12/2024 (18 thang)
- **Products:** 8,459 (5,753 available for active sale)
- **Customers:** 3,200
- **Sales Agents:** 50 (Pareto: top 20% ~ 52% revenue)
- **Sales Transactions:** 4,211 (3,600 non-cancelled)
- **Leads Pipeline:** 12,891
- **Inventory Snapshots:** 150 (monthly x sub-zones)

## Du an

| ID | Ten | Loai | Trang thai |
|---|---|---|---|
| PRJ-CW | CaraWorld Cam Ranh | Resort township | Active - TRONG TAM |
| PRJ-BH | Bien Hoa New City | Dat nen | Active |
| PRJ-DEF | Define | Can ho | Active |
| PRJ-FEV | Feliz En Vista | Can ho | ~90% ban giao |
| PRJ-VV | Vista Verde | Can ho | ~95% ban giao |
| PRJ-VA | The Vista An Phu | Can ho | 100% ban giao |

## 5 Demo Scenarios

1. **S1 - Descriptive:** Q4/2024 tong quan - CW ~83% revenue
2. **S2 - Diagnostic:** Para Grus absorption thap (6.3%) - gia cao + xa bien + mua mua + online conv thap
3. **S3 - Predictive:** Inventory forecast - PG 581 units con, 52.8 thang ton kho
4. **S4 - Simulation:** Song Town price cut T6/2024 - sales tang manh (Before 349 vs After 876)
5. **S5 - Goal-seeking:** Q4/2024 CW overachieve +14% vs target (8,649 vs 7,587 ty)

## Cach su dung

```bash
# Load vao MySQL
mysql -uroot -proot < 01_ddl.sql
mysql -uroot -proot < 02_metadata.sql
mysql -uroot -proot < 03_master_data.sql
mysql -uroot -proot < 04_transaction_data.sql

# Validate
mysql -uroot -proot kn_realestate_demo < 05_validation.sql
```

## Regenerate data

```bash
python3 generate_kn_holdings_data.py
```
