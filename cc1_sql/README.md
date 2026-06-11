# CC1 Construction Demo Database

Mock database cho Tổng Công ty Xây dựng Số 1 (CC1) — pitch CEO/HĐQT về 4 trụ chiến lược:
tăng trưởng DT & backlog, biên LN, tiến độ thi công, dòng tiền & công nợ.

## Thông tin

- **Database:** `cc1_construction_demo` (MySQL 8.0, utf8mb4_unicode_ci)
- **Phạm vi:** 01/2024 – 12/2025 (24 tháng) | "Hiện tại" = cuối 12/2025
- **Đơn vị tiền tệ:** VND
- **Tables:** 8 dimension + 7 fact + 4 meta (tổng 19 tables)
- **Grain fact:** tháng × dự án (ghi nhận DT theo milestone, đặc thù EPC)

## Magnitude anchors (khớp BCTC)

| Chỉ số | 2024 | 2025 |
|--------|------|------|
| Doanh thu thuần (tỷ) | 10,160 | 11,811 (+16.3%) |
| LN gộp (tỷ) | 484 | 557 |
| Biên gộp (%) | 4.76 | 4.72 |
| LNST (tỷ) | 229 | 227 (-0.9%) |
| Backlog cuối kỳ (tỷ) | — | ~42,500 |
| Phải thu cuối kỳ (tỷ) | — | 6,800 |

**Nghịch lý cốt lõi:** DT +16.3% nhưng LNST -0.9% — margin erosion + chi phí tài chính tăng.

## 5 Demo Scenarios + 4 Anomalies

| # | Scenario | Tầng | Data anomaly |
|---|----------|------|-------------|
| ❶ | Bức tranh tổng thể 2025 vs KH & 2024 | Descriptive | — (warm-up) |
| ❷ | Tiến độ 70+ dự án & khả năng đạt KH 2026 | Predictive | **A1:** 3 dự án chậm (Vĩnh Hảo / Hạnh Phúc / Cầu Đồng Nai) |
| ❸ | Công nợ phải thu & dòng tiền | Diagnostic | **A2:** 3 chủ đầu tư 'Chậm' chiếm 35% phải thu, >180d 28% |
| ❹ | What-if giá cát/đá +15% | Strategic | **A3:** ~12 HĐ đơn giá cố định, cát+đá 18% cost |
| ❺ | DT tăng nhưng LNST đứng yên | Diagnostic | **A4:** Biên giao thông 5.1%→3.8%; chi phí lãi vay +18% |

## Reproduce (Docker MySQL 8.0)

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=cc1_construction_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate theo thứ tự
docker exec -i mock_database mysql -uroot -proot < 01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < 02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < 03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < 04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < 05_validation_queries.sql

# 5. Reset nếu cần
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS cc1_construction_demo; CREATE DATABASE cc1_construction_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Lưu ý cho AI engine

- **Metadata tables** (`_meta_*`) là nguồn truth schema cho LLM. Đọc từ đó để hiểu tables/columns/KPI.
- **Grain fact = tháng**. Không có giao dịch ngày (đặc thù EPC ghi nhận DT theo milestone).
- **fact_project_progress & fact_receivables = SNAPSHOT.** Luôn `WHERE snapshot_month` chứ không SUM nhiều snapshot.
- **fact_financial_summary là TỔNG company-level**, KHÔNG join với fact_project_revenue để tránh nhân đôi (chênh ≤5%).
- **What-if cát/đá +15%:** tính tại query time = (Σ cost cát/đá nhóm 'Đơn giá cố định') × 0.15 → trừ vào gross_profit.
- **material_id NULL** nếu cost_category ≠ NVL → dùng LEFT JOIN dim_material.

## Files

| File | Mô tả | Size ước tính |
|------|-------|--------------|
| 01_ddl_schema.sql | CREATE DATABASE + 19 tables | ~12 KB |
| 02_metadata.sql | INSERT _meta_* (tables, columns, KPI, glossary) | ~25 KB |
| 03_master_data.sql | INSERT 8 dimension tables | ~80 KB |
| 04_transaction_data.sql | INSERT 7 fact tables (batch ≤800 rows) | ~3 MB |
| 05_validation_queries.sql | SELECT verify | ~6 KB |
