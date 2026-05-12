# GS25 Việt Nam — CVS Mini Demo Database

Phiên bản rút gọn của [gs25_sql](../gs25_sql/) — same schema, ít data hơn, fit trong GitHub 100MB/file limit (không cần git-lfs).

- **Database:** `gs25_mini_demo`
- **Charset:** utf8mb4 / utf8mb4_unicode_ci
- **Total size:** ~318MB (vs full ~1GB)
- **"Today" cho AI:** `2026-03-31`

## Khác biệt vs bản full

| Aspect | Full (`gs25_sql`) | Mini (`gs25_mini_sql`) |
|---|---|---|
| Time range fact_sales | 2024-10-01 → 2026-03-31 (548 days liên tục) | 2 windows: Oct'24-Mar'25 + Oct'25-Mar'26 (12 tháng) |
| fact_sales grain | Daily-level với hour, segment, channel | **Weekly** (Monday of week), hour=12, all segment='SEG_WI', all channel='walk-in' |
| fact_sales rows | 8.6M | 2.5M |
| fact_inventory | 30 ngày snapshots × 442 stores | Chỉ 2026-03-31 |
| fact_store_traffic | Hourly last 90d + daily older | Daily only |
| fact_waste | 18 tháng | 12 tháng (2 windows) |
| Schema | Identical | Identical |
| Dim tables | Full | Full (same data) |
| 5 demo scenarios | All ✅ | All ✅ (giảm độ chi tiết peak-hour, segment, channel) |

## Cấu trúc

```
gs25_mini_sql/
├── 01_ddl_schema.sql           — DDL (database: gs25_mini_demo)
├── 02_metadata.sql             — _meta_* tables
├── 03_master_data.sql          — 10 dim_* tables (full master data)
├── 04_a_sales_1.sql            — fact_sales chunk 1 (82MB)
├── 04_a_sales_2.sql            — fact_sales chunk 2 (82MB)
├── 04_a_sales_3.sql            — fact_sales chunk 3 (78MB)
├── 04_b_inventory.sql          — fact_inventory_snapshot
├── 04_c_waste.sql              — fact_waste
├── 04_d_traffic.sql            — fact_store_traffic (daily)
├── 04_e_pnl.sql                — fact_store_pnl
├── 04_f_purchase_order.sql     — fact_purchase_order
└── README.md
```

## Populate

```bash
./populate.sh gs25_mini
```

Hoặc thủ công:
```bash
docker exec -i mock_database mysql -uroot -proot < gs25_mini_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < gs25_mini_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < gs25_mini_sql/03_master_data.sql
for f in gs25_mini_sql/04_*.sql; do
  docker exec -i mock_database mysql -uroot -proot < "$f"
done
```

## Khi nào dùng bản nào?

- **gs25_sql (full):** dùng cho production demo, AI engine analysis với full hour/segment/channel detail
- **gs25_mini_sql:** dùng cho dev/testing, CI smoke test, share qua git mà không cần LFS

## Scenarios vẫn cover được

Q1 6-month overview · Q2 chronic underperformers + cohort · Q3 KR exposure + 25 Tier 1 critical · Q4 waste anomaly week (cần group theo week thay vì 2026-03-23..28 cụ thể) · Q5 synthesis.

**Lưu ý cho Q4:** Vì fact_sales aggregate weekly (Monday-anchor), tuần anomaly `2026-03-23..28` được represent bởi row `date='2026-03-23'` (Monday). Query waste rate: filter `fact_waste.waste_date BETWEEN '2026-03-23' AND '2026-03-28'` (vẫn daily grain) chia cho `fact_sales` với `date='2026-03-23'`.
