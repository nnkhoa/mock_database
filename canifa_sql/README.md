# CANIFA Retail Fashion — Demo Database

## Thông tin
- **Database:** canifa_retail_demo
- **Engine:** MySQL 8.0 (utf8mb4)
- **Data range:** 07/2023 – 03/2025 (21 tháng)
- **Stores:** 110 cửa hàng toàn quốc
- **Products:** ~500 SKU
- **Channels:** 5 (Cửa hàng, Website, Shopee, TikTok, Lazada)

## Populate

```bash
# 1. Khởi tạo MySQL container
docker run --name canifa_demo \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=canifa_retail_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec canifa_demo mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/01_ddl_schema.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/02_metadata.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/03_master_data.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/04a_sales_1.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/04a_sales_2.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/04b_returns.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/04c_inventory.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/04d_store_costs.sql

# 4. Verify
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/05_validation_queries.sql

# 5. Reset (nếu cần)
docker exec -i canifa_demo mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS canifa_retail_demo; CREATE DATABASE canifa_retail_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Demo Scenarios
1. Top 10 sản phẩm bán chạy — Dry-Tech surge
2. Hiệu quả khuyến mại — Flash Sale 12/12 ROI âm
3. Tồn kho cuối mùa đông — 2 cửa hàng overstock
4. Inventory days tăng dần — len/sợi 105 ngày
5. Margin erosion Q1/2025 — 3 yếu tố
6. Hiệu quả cửa hàng — Star/Underperformer clusters
