# Lam Sơn Invest — Construction & Real Estate Demo Database

## Thông tin
- **Database:** `construction_re_demo`
- **Mục đích:** Demo AI engine (Claude + MCP) cho Công ty CP Lam Sơn Invest
- **Ngành:** Xây dựng & Bất động sản (Thái Bình)
- **Data range:** 10/2023 → 03/2025 (18 tháng)
- **Tables:** 7 dimension + 12 fact + 4 metadata = 23 tables
- **Records:** ~1,700+ rows
- **Đối tượng demo:** CEO / Tổng Giám đốc

## Cách populate

### 1. Khởi tạo MySQL container
```bash
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=construction_re_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

### 2. Chờ MySQL sẵn sàng
```bash
docker exec mock_database mysqladmin ping -uroot -proot --wait=30
```

### 3. Populate data theo thứ tự
```bash
docker exec -i mock_database mysql -uroot -proot < lam_son_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < lam_son_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < lam_son_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < lam_son_sql/04_transaction_data.sql
```

### 4. Verify
```bash
docker exec -i mock_database mysql -uroot -proot < lam_son_sql/05_validation_queries.sql
```

### 5. Reset (nếu cần làm lại)
```bash
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS construction_re_demo; CREATE DATABASE construction_re_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3
```

## Cấu trúc files
| File | Nội dung | Rows ước tính |
|------|----------|---------------|
| 01_ddl_schema.sql | CREATE DATABASE, CREATE TABLE, indexes, constraints | 23 tables |
| 02_metadata.sql | _meta_tables, _meta_columns, _meta_kpi, _meta_glossary | ~150 rows |
| 03_master_data.sql | Dimension tables (regions, materials, projects...) | ~50 rows |
| 04_transaction_data.sql | Fact tables (cost_items, financials, RE units...) | ~1,500 rows |
| 05_validation_queries.sql | SELECT queries to verify data integrity | ~30 queries |

## Demo Scenarios (5 câu hỏi)

| # | Câu hỏi | Anomaly chính |
|---|---------|---------------|
| 1 | Tổng quan dự án — dự án nào có vấn đề? | TC-003 chậm -23%, vượt chi phí 17%. BDS-001 chỉ bán 35% |
| 2 | Dự án đường Đông Hưng vượt chi phí — nguyên nhân? | NVL +28%, thầu phụ +15%, mua thép đúng đỉnh giá |
| 3 | Biên lợi nhuận thi công 12 tháng — mảng nào giảm? | Giao thông: 12.3% → 7.4%. 3 gói thầu bid ratio < 0.88 |
| 4 | Dòng tiền 3 tháng tới — rủi ro? | T+2: khoản thu 8.5 tỷ từ TC-003 không chắc, phải trả 6.2 tỷ |
| 5 | Tồn kho BĐS — ưu tiên bán gì? | Shophouse Lý Bôn: 8 căn tồn 27 tháng, chi phí vốn ~2.7 tỷ |

## Lưu ý cho AI engine
- Query `_meta_tables` và `_meta_kpi` để hiểu schema
- Monetary unit: triệu VND (1 tỷ = 1.000 triệu)
- Date range: 10/2023 – 03/2025
- Current month for projection: 03/2025
- Anomaly KHÔNG được tiết lộ — AI phải tự phát hiện
