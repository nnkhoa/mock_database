# vnuhcm_finance_demo — Tài chính Giáo dục Đại học | ĐHQG-HCM (demo)

Mock database phục vụ BI/AI engine (MySQL 8.0 + MCP) cho **Ban Kế hoạch - Tài chính ĐHQG-HCM**.

> ⚠️ Cấu trúc tổ chức (13 đơn vị, tên trường) là **THẬT**. Toàn bộ **số liệu tài chính là MOCK**, grounded trên benchmark ngành giáo dục ĐH công lập VN — KHÔNG phải số thật của ĐHQG-HCM.

- **Database:** `vnuhcm_finance_demo` (utf8mb4_unicode_ci)
- **Phạm vi:** 2024-07-01 → 2026-06-30 (24 tháng), grain tháng. "Hiện tại" = cuối 2026-06.
- **Năm nay** (dùng cho YoY/scenario) = 2025-07-01 → 2026-06-30.

## Cấu trúc file (chạy tuần tự 01 → 05)

| File | Nội dung |
|---|---|
| `01_ddl_schema.sql` | CREATE DATABASE, 11 bảng dữ liệu + 4 bảng metadata, index, FK, COMMENT |
| `02_metadata.sql` | INSERT `_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary` |
| `03_master_data.sql` | INSERT dimension: calendar, unit, revenue_source, cost_category, asset, capital_project |
| `04_transaction_data.sql` | INSERT fact: revenue, expense, enrollment, capital_project, asset_utilization |
| `05_validation_queries.sql` | Kiểm tra kỹ thuật + dry-run 5 demo scenario (S1..S5) + fallback |

## Reproduce trên máy mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=vnuhcm_finance_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i mock_database mysql -uroot -proot < 01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < 02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < 03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < 04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < 05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS vnuhcm_finance_demo; CREATE DATABASE vnuhcm_finance_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```
> `01_ddl_schema.sql` đã tự `DROP DATABASE IF EXISTS` + `CREATE`, nên chạy lại từ 01 là reset sạch.

## Schema (11 bảng dữ liệu)

**Dimension:** `dim_calendar` (24), `dim_unit` (13), `dim_revenue_source` (4), `dim_cost_category` (7), `dim_asset` (19), `dim_capital_project` (5).
**Fact:** `fact_finance_revenue` ⭐ (1.248 = 13×4×24), `fact_finance_expense` ⭐ (2.184 = 13×7×24), `fact_enrollment` (66), `fact_capital_project` (30), `fact_asset_utilization` (114).

### Lưu ý JOIN quan trọng
1. **Không JOIN trực tiếp** revenue ↔ expense để tính kết dư — aggregate riêng rồi trừ.
2. `fact_enrollment` grain theo **KỲ** vs finance theo **THÁNG** — aggregate finance về kỳ/năm trước khi chia SV (tránh nhân trùng).
3. `fact_capital_project` = **LŨY KẾ** — dùng `cumulative_disbursed_vnd` tháng gần nhất, KHÔNG SUM.
4. `fact_asset_utilization` = **SNAPSHOT** — lọc `snapshot_month='2026-06-01'`, KHÔNG SUM.
5. **DORM & VPQG** không có trong `fact_enrollment` (không đào tạo) — nhớ gồm đủ 13 đơn vị khi tính tổng thu.

## 5 Demo Scenario (đã dry-run PASS)

| # | Scenario | Con số chính |
|---|---|---|
| S1 | Cơ cấu nguồn thu hợp nhất | Tổng ~6.130 tỷ; HP 54.6% / NSNN 20.9% / KH&CN 13.6% / DV 10.9%; YoY tổng +8.9%, HP +14.2%, NSNN −3.2% |
| S2 | Rủi ro tập trung nguồn thu | Lệ thuộc HP: UIT 82% · UEL 78% · IU 74% · MED 68%. Lệ thuộc NSNN: SPA 60% · BTC 48% · AGU 45% · USSH 39% |
| S3 | Chi phí đào tạo/SV | IU/MED cao (mô hình đào tạo đắt — hợp lý); USSH/AGU thấp. Anomaly: **UIT chi vận hành +22.5% YoY** (cần tối ưu) |
| S4 | Giải ngân & tài sản | KTX Khu B GĐ2 = 17.9%, Thư viện = 8.7%; tổng 372/1.200 = 31%. Tài sản dưới công suất: Kính hiển vi 27.5%, Tòa liên ngành 48%, KTX A 71.5%; KTX B quá tải 98.5% |
| S5 | What-if NSNN −10% | Hụt ~128 tỷ hệ thống; đơn vị chịu nặng theo % tổng thu: AGU/USSH/VPQG/SPA. Nối insight tài sản nhàn rỗi từ S4 |

## Kết nối AI engine
- **Metadata tables** (`_meta_*`) là nguồn truth để AI hiểu schema, KPI, thuật ngữ.
- **Data range:** 2024-07 → 2026-06 (24 tháng) — đủ cho trend ≥6 tháng, YoY, what-if.
- **Đơn vị tiền:** cột `*_vnd` = VND. Hiển thị board: >1 tỷ → "X,X tỷ" (÷1e9); <1 tỷ → "XXX triệu" (÷1e6).
- **Known limitations:** (1) Chi phí/SV hệ thống ~60 triệu (không phải ~38 như benchmark) — hệ quả toán học của tổng thu 6.180 tỷ ÷ ~90k SV; thứ hạng tương đối vẫn đúng cho S3. (2) DORM/VPQG có khoản thu học phí/NCKH token rất nhỏ để phủ đủ lưới 13×4 nguồn (fallback).
