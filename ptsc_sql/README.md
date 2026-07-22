# ptsc_sql — Database `ptsc_demo` (Tổng CTCP Dịch vụ Kỹ thuật Dầu khí — PTSC/PVS)

Demo **AI-for-BI** cho doanh nghiệp **dịch vụ kỹ thuật dầu khí / EPC (project-based)**.
Database MySQL 8.0 (utf8mb4) mô phỏng **21 tháng** dữ liệu (2024-01 → 2025-09),
"hiện tại" = cuối 09/2025. Grain trung tâm: **DỰ ÁN × THÁNG** (ghi nhận doanh thu theo
POC — Percentage of Completion), KHÔNG phải bán lẻ/transaction.

Schema của `01_ddl_schema.sql` khớp **y hệt** tài liệu `database-schema.md` (kèm trong thư mục này).

## Nội dung

| File | Mô tả |
|------|-------|
| `01_ddl_schema.sql` | DROP/CREATE DATABASE, 12 bảng nghiệp vụ, index, FK, COMMENT |
| `02_metadata.sql`   | `_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary` (nguồn truth) |
| `03_master_data.sql`| Dimension: calendar (21), segment (7), region (7), facility (6), client (10), contract, **project (43)**, plan năm |
| `04_transaction_data.sql` | 4 fact: financials, EAC snapshot, progress, cost breakdown (~855 dòng/fact, cost ~4.275) |
| `05_validation_queries.sql` | Kiểm tra toàn vẹn + dry-run 6 scenario (Q1..Q6) + fallback |
| `database-schema.md` | Tài liệu schema (nguồn tham chiếu cho AI engine) |
| `generate.py` | Script sinh 03 & 04 (3 lớp: base S-curve → actual + seasonality → anomaly) |

## Reproduce vào Docker container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=ptsc_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate theo thứ tự (các file đã tự SET NAMES utf8mb4)
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < 01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < 02_metadata.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < 03_master_data.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < 04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < 05_validation_queries.sql

# 5. Reset (nếu cần)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS ptsc_demo; CREATE DATABASE ptsc_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

`01_ddl_schema.sql` đã tự `DROP DATABASE IF EXISTS` + `CREATE DATABASE` + `USE`.
Từ thư mục gốc repo có thể dùng: `./populate.sh ptsc`.

## Lưu ý cho người kết nối AI engine (MCP)

- **Metadata = nguồn truth**: đọc `_meta_tables` / `_meta_columns` / `_meta_kpi` / `_meta_glossary`.
- **Data range**: 2024-01 → 2025-09 (21 tháng); "hiện tại" = 30/09/2025.
- **Doanh thu kỳ** LUÔN dùng `revenue_recognized_vnd` (KHÔNG dùng `contract_value_vnd`).
- **Biên gộp** = `SUM(gross_profit_vnd)/SUM(revenue_recognized_vnd)` (không average dòng lẻ).
- **`fact_eac_snapshot_monthly` là SNAPSHOT**: xem trạng thái `WHERE snapshot_month='2025-09-01'`;
  **KHÔNG SUM nhiều snapshot**. Margin erosion = `eac_margin_pct − bid_margin_pct`.
- **`fact_project_cost_monthly`** nhiều dòng/dự án/tháng (mỗi cost_category 1 dòng): aggregate
  trước khi JOIN với financials để tránh nhân đôi doanh thu.
- **`fact_plan_annual.segment_id IS NULL`** = kế hoạch toàn TCT (đừng gộp vào GROUP BY theo mảng).

## 6 demo scenario (đã dry-run PASS)

| # | Câu hỏi | Kết quả chính |
|---|---------|---------------|
| S1 | DT/LN Q3/2025 vs KH theo mảng | Q3 DT 5.900 tỷ (~105% KH), biên 10,9%; Khảo sát ROV hụt (82% KH) |
| S2 ⭐ | Dự án nào bào mòn biên LN cuối HĐ | **EPCI#2 Lô B**: bid 11,5% → EAC 6,2% (−5,3 điểm, ~530 tỷ); Hải Long −2,7 điểm |
| S3 | Sản lượng chậm gói nào | EPCI#2 82% KH (T9: 3.444/4.200 tấn), DT POC hụt ~140 tỷ Q3 |
| S4 | Cả năm 2025 có về đích | DT ~23.800 tỷ (vượt KH 22.500) nhưng LNST ~1.050 (< mục tiêu 1.200) |
| S5 | Điện gió: LN tương xứng DT chưa | DT 24,5% nhưng LN gộp ~10%, biên ~4,6% → **chưa tương xứng** |
| S6 | Ưu tiên loại HĐ/khu vực nào | Day-rate 19% > Unit-rate 11% > Lump-sum 8% (rủi ro, chứa 2 dự án đã flag) |

## Known limitations / simplifications

- **Grain tháng**, không có transaction-level; `fact_eac_snapshot_monthly` là snapshot.
- **Pareto theo doanh thu**: top ~20% dự án ≈ 53% doanh thu (không đạt 75-80% như brief) — do
  yêu cầu phủ đủ **7 mảng** khiến khối **Dịch vụ** (FSO/căn cứ/O&M/khảo sát/tàu) chiếm ~33%
  doanh thu ổn định, dàn trải qua nhiều dự án. Các dự án lớn (EPCI Lô B + điện gió + fabrication
  Trung Đông) vẫn là nhóm đóng góp doanh thu/backlog lớn nhất.
- **Doanh thu nước ngoài**: ~51% (đạt >50%), chủ yếu điện gió Đài Loan/Châu Âu + fabrication
  xuất khẩu Trung Đông (Aramco/QatarEnergy). Biên gộp *tổng* của nước ngoài hiện thấp hơn trong
  nước vì nước ngoài nặng điện gió (biên mỏng) — nhất quán với S5; riêng fabrication Trung Đông
  biên ~11% là điểm sáng (xem FB2).
- Số liệu là mock có chủ đích, phản ánh magnitude thực tế PTSC 2024 (DT ~24.986 tỷ) nhưng đơn
  giản hóa số dự án (43) để demo mượt.
