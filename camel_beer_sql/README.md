# camel_beer_demo — Database demo BI ngành Bia (Camel Beer)

Bộ dữ liệu mô phỏng cho demo BI của **Bia Camel** (thương hiệu bia giá phổ thông, xuất khẩu mạnh).
Đối tượng demo: **CCO / Giám đốc Kinh doanh**, mục đích **pitching cho board**.
Kết nối tới AI engine (Claude) qua MCP để hỏi đáp tiếng Việt + sinh chart.

## Tổng quan

- **14 bảng**: 7 dimension + 3 fact + 4 metadata.
- **~188.800 rows** (ràng buộc cứng ≤ 300.000).
- **Phạm vi thời gian**: 2025-01-01 → 2026-04-30 (16 tháng). "Hiện tại" = cuối T4/2026 (sau Tết, thấp điểm).
- **Doanh thu** (fact_sell_in.net_revenue_vnd): 16 tháng ≈ 1.410 tỷ VND; cả năm 2025 ≈ 1.045 tỷ.
- **Cơ cấu**: Nội địa 64% / Xuất khẩu 36%.
- Tên bảng/cột: tiếng Anh snake_case. Giá trị master data: tiếng Việt. Encoding utf8mb4.

## Cấu trúc file

| File | Nội dung | Thứ tự |
|---|---|---|
| `01_ddl_schema.sql` | CREATE DATABASE + 14 CREATE TABLE + index + FK + COMMENT | 1 |
| `02_metadata.sql` | INSERT `_meta_tables/_meta_columns/_meta_kpi/_meta_glossary` | 2 |
| `03_master_data.sql` | INSERT 7 dimension tables | 3 |
| `04_transaction_data.sql` | INSERT 3 fact tables (batch ≤ 1000 rows/statement) | 4 |
| `05_validation_queries.sql` | SELECT kiểm chứng 6 demo scenarios | sau cùng |

## Reproduce trên máy mới (Docker)

```bash
# 1. Khởi tạo MySQL container
docker run --name camel_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=camel_beer_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec camel_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i camel_database mysql -uroot -proot < 01_ddl_schema.sql
docker exec -i camel_database mysql -uroot -proot < 02_metadata.sql
docker exec -i camel_database mysql -uroot -proot < 03_master_data.sql
docker exec -i camel_database mysql -uroot -proot < 04_transaction_data.sql

# 4. Verify
docker exec -i camel_database mysql -uroot -proot < 05_validation_queries.sql

# 5. Reset (nếu cần làm lại) — 01 đã tự DROP DATABASE, chỉ cần chạy lại từ bước 3
docker exec -i camel_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS camel_beer_demo; CREATE DATABASE camel_beer_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

> Lưu ý: `01_ddl_schema.sql` mở đầu bằng `DROP DATABASE IF EXISTS camel_beer_demo` rồi `CREATE DATABASE`,
> nên chạy lại bước 3 là đủ để reset toàn bộ. Mỗi file đều `USE camel_beer_demo;` và độc lập.

## Schema tóm tắt

**Dimension**: `dim_calendar` (485 ngày, cờ Tết/hè), `dim_region` (Bắc/Trung/Nam), `dim_channel`
(9 sub-channel on/off-trade), `dim_product` (25 SKU, 6 dòng), `dim_distributor` (18 NPP),
`dim_outlet` (324 điểm bán), `dim_export_market` (9 quốc gia).

**Fact**: `fact_sell_in` (⭐ Camel→distributor/importer; trade_type=domestic/export),
`fact_sell_out` (distributor→outlet, chỉ nội địa), `fact_inventory_snapshot` (tồn kho cuối tháng + days_of_inventory).

**Metadata** (`_meta_*`): nguồn truth cho AI engine — mô tả bảng/cột (đơn vị, ví dụ), công thức KPI, glossary
(on/off-trade, sell-in/out, days of inventory, ASP, GT/MT, TTĐB, ABV, NĐ168...).

## 6 Demo Scenarios (đã calibrate & validate)

| | Câu hỏi | Insight chính |
|---|---|---|
| **A** | DT tháng này vs cùng kỳ? Nội địa/XK? | Apr2026 ~76 tỷ, +8,8% YoY; nội địa 64% (+4%), **XK 36% (+16%) gánh tăng trưởng** |
| **B** | Kênh nào kéo tụt nội địa? | **On-trade −9,3%** (Quán nhậu/Bia hơi −14%), off-trade +14%, **E-com +25%**; Miền Bắc nặng nhất → Nghị định 168 |
| **C** | Distributor nhập nhiều bán chậm? | **Minh Phát (Hải Phòng)**: days_of_inventory 12→**34** ở Camel Premium Đỏ 500ml; sell-in ≫ sell-out → rủi ro ôm hàng |
| **D** | Thị trường XK nào có vấn đề? | Tổng XK +14% nhưng **Hàn Quốc −21%** 🔴 (Lager Xanh 330ml); bù lại Iran +43%, Mỹ +18% |
| **E** | SKU tăng/giảm 6 tháng? | **Camel Zero (0.0%) +36%**, Lager 500ml +12%; Special Vàng 330ml −9%; Pareto top 6 SKU ≈ 77% |
| **F** | Nếu TTĐB đẩy giá +10%? | Nhạy giá nhất = on-trade + phổ thông; an toàn = off-trade + Zero (không cồn) + XK |

## Known limitations

- **Xuất khẩu KHÔNG có** sell-out & inventory (chỉ sell-in tới importer).
- "Hiện tại" = cuối T4/2026 là tháng **sau Tết, thấp điểm** (mùa thấp nhất) — khi so sánh nên dùng YoY, không so với tháng Tết liền trước.
- **YoY tháng-với-tháng chỉ so sạch cho T1–T4** (có ở cả 2025 & 2026). Các tháng T5–T12/2025 không có cùng kỳ 2024.
- Đỉnh Tết ~118 tỷ (kịch bản gốc gợi ý 130–145): do XK ~phẳng theo mùa làm dịu đỉnh tổng; ưu tiên giữ Apr2026 đúng dải 76–82 tỷ.
- Số liệu Camel là **ước lượng** (DN chưa niêm yết) — đúng magnitude/trend ngành bia VN, không phải số thực.
