# `lavie_water_demo` — Mock BI database
### Công ty TNHH La Vie (Nestlé Waters Việt Nam) · Nước khoáng đóng chai

Bộ dữ liệu mô phỏng phục vụ demo AI‑BI: câu hỏi tiếng Việt tự nhiên → MCP → MySQL → insight.

| | |
|---|---|
| **Database** | `lavie_water_demo` (MySQL 8.0, `utf8mb4_unicode_ci`) |
| **Phạm vi** | 2024‑07‑01 → 2026‑06‑30 · 24 tháng · 730 ngày |
| **"Hiện tại"** | cuối ngày **30/06/2026** |
| **Số bảng** | 20 — 9 dimension + 7 fact + 4 metadata |
| **Số dòng** | **112.415** (ràng buộc đề bài: 100.000 – 150.000) |
| **Đối tượng demo** | Tổng Giám Đốc La Vie, dùng để pitching HĐQT / Nestlé Waters regional |

---

## 1. Populate vào Docker container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=lavie_water_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate theo đúng thứ tự
docker exec -i mock_database mysql -uroot -proot < lavie_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < lavie_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < lavie_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < lavie_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < lavie_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS lavie_water_demo; CREATE DATABASE lavie_water_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

Nếu dùng container `mock_database` sẵn có trong repo, chỉ cần: `./populate.sh lavie`
(`01_ddl_schema.sql` đã tự `DROP DATABASE` nên chạy lại là sạch).

---

## 2. Nội dung thư mục

| File | Nội dung | Kích thước |
|---|---|---|
| `01_ddl_schema.sql` | `CREATE DATABASE`, 20 `CREATE TABLE`, index, `COMMENT` từng bảng và từng cột | 26 KB |
| `02_metadata.sql` | `_meta_tables` (20) · `_meta_columns` (187) · `_meta_kpi` (15) · `_meta_glossary` (15) | 42 KB |
| `03_master_data.sql` | 9 bảng dimension — 1.276 dòng | 127 KB |
| `04_transaction_data.sql` | 7 bảng fact — 110.902 dòng, mỗi `INSERT` tối đa 1000 dòng | 12,6 MB |
| `05_validation_queries.sql` | Query kiểm tra D.1 kỹ thuật · D.2 thống kê · D.3 sáu scenario · D.4 ngoài kịch bản | 17 KB |
| `database-schema.md` | **Tài liệu schema** — mô tả từng bảng, từng cột, 13 SQL template, 10 cảnh báo JOIN | 905 dòng |

Script sinh dữ liệu nằm ở `../lavie_scripts/` (`common.py`, `gen_master.py`, `gen_facts.py`,
`finplan.py`, `gen_metadata.py`, `validate.py`, `verify_schema.py`).

---

## 3. Số dòng từng bảng

| Bảng | Grain | Dòng |
|---|---|---:|
| `dim_calendar` | ngày | 730 |
| `dim_geography` | vùng + tỉnh | 37 |
| `dim_channel` | kênh | 5 |
| `dim_customer` | đại lý / khách hàng | 380 |
| `dim_product` | SKU | 11 |
| `dim_plant` | nhà máy | 2 |
| `dim_production_line` | dây chuyền | 9 |
| `dim_warehouse` | kho / DC | 6 |
| `dim_route` | tuyến giao hàng | 96 |
| `fact_sales_out` ⭐ | tháng × khách hàng × SKU | 81.100 |
| `fact_trade_spend` | tháng × khách hàng × loại chi | 9.720 |
| `fact_production` | ngày × dây chuyền | 6.570 |
| `fact_inventory` | tuần × kho × SKU | 5.616 |
| `fact_container_cycle` | tháng × khách hàng có 19L | 5.232 |
| `fact_cost_to_serve` | tháng × tuyến | 2.304 |
| `fact_pnl_monthly` | tháng × kênh × vùng | 360 |
| `_meta_*` (4 bảng) | — | 237 |
| **TỔNG** | | **112.415** |

---

## 4. Ba anomaly có chủ đích

| | Nội dung | Đường drill‑down |
|---|---|---|
| **A** | **Miền Trung "tăng trưởng lỗ"** — doanh thu +18,4% nhưng biên đóng góp rơi 21,4% → 13,2%. Ba tỉnh Bắc Trung Bộ có CM **âm**: Hà Tĩnh −3,4%, Quảng Trị −2,1%, Huế −0,8%. Đối chứng: **Nghệ An liền kề +17,2%** vì lấy hàng từ Hưng Yên (760 đ/lít) thay vì Long An qua DC Đà Nẵng (1.180 đ/lít). | vùng → tỉnh → `dim_route` → `dim_warehouse` |
| **B** | **Rò rỉ vỏ bình 19L** — thu hồi giảm đều 6 quý 94,2% → 86,8%. 62.400 vỏ mất = **4,80 tỷ** hao hụt tài sản + **3,25 tỷ** cọc treo. Nguồn: **14 đại lý HOD `contract_type='MOI_2025'`** thu hồi 78,3% so với 93,1% của đại lý lâu năm. | toàn công ty → nhóm `onboard_date` → 14 đại lý |
| **C** | **Doanh thu ảo kênh MT** — MT gross margin thuộc nhóm cao nhất nhưng **net margin thấp nhất**, trade spend 38,4% doanh thu. **Circle K net −1,8%**, **GS25 net −0,6%** dù doanh thu +26% / +25%. Nguyên nhân sâu: mở điểm bán rất nhanh nhưng **doanh thu trên mỗi điểm bán giảm ~10%**. | kênh → khách hàng → `store_count` |

---

## 5. Mốc sanity check (đã verify trên dữ liệu thật)

| Chỉ số | Giá trị |
|---|---|
| Doanh thu FY2025 | 2.499,9 tỷ |
| Doanh thu 12T gần nhất (2025‑07 → 2026‑06) | 2.621,1 tỷ |
| Doanh thu toàn bộ 24 tháng | 5.030,4 tỷ |
| Tháng đỉnh / tháng đáy | 2026‑06 (291 tỷ) / 2025‑11 (167 tỷ) |
| Tăng trưởng H1/2026 vs H1/2025 | +9,3% |
| Sản lượng 12T | 735,4 triệu lít |
| Yield trung bình | 3.564 đ/lít |
| Biên đóng góp toàn công ty | 30,2% |
| EBIT 12T gần nhất | 372,0 tỷ (14,2%) |
| Tỷ trọng doanh thu SKU 19L FY2025 | 38,1% |
| Tỷ lệ thu hồi vỏ 2026‑Q2 | 86,8% |
| Utilization Long An / Hưng Yên (T6/2026) | 91,4% / 84,7% |
| Days of cover trung bình (T6/2026) | 8,4 ngày |
| Pareto top 20% khách hàng | 80,0% doanh thu |

Chạy `python3 ../lavie_scripts/validate.py` để in báo cáo đầy đủ (**83/83 PASS**).
Chạy `python3 ../lavie_scripts/verify_schema.py` để xác nhận schema trong MySQL **khớp y hệt** `database-schema.md`.

---

## 6. Lưu ý cho người kết nối AI engine

- **Metadata tables** — `_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary`.
  Đây là nguồn truth để AI hiểu ý nghĩa cột và thuật ngữ; query trước khi viết SQL.
- **Data range** 2024‑07‑01 → 2026‑06‑30. "Hiện tại" = cuối 2026‑06. Không có dữ liệu tương lai.
- **`net_revenue_vnd` là cột doanh thu chuẩn.** `gross_revenue_vnd` chỉ dùng khi cần tách chiết khấu.
- **10 cảnh báo JOIN** nằm cuối `database-schema.md` — đặc biệt:
  `fact_trade_spend` ↔ `fact_sales_out` khác grain (phải aggregate về `(fiscal_period, customer_id)` trước);
  `fact_inventory` là snapshot (không SUM nhiều kỳ);
  `deposit_outstanding_vnd` là cột lũy kế (dùng `MAX`);
  `dim_geography` có 2 cấp (luôn thêm `geo_level='Tỉnh'`).
- **Địa giới hành chính**: 34 tỉnh/thành **sau sáp nhập 01/07/2025**. Không tồn tại "Thừa Thiên Huế",
  "Quảng Bình", "Bình Dương", "Bà Rịa – Vũng Tàu".

### Known limitations

Đề bài gốc có một số mốc số **mâu thuẫn nội tại**; các lựa chọn xử lý đã ghi rõ trong
`../lavie_scripts/common.py` và `../lavie_scripts/finplan.py`:

1. **Biên đóng góp 29–31% và gross margin theo kênh 24,5–33%** không thể cùng đúng
   (vì `CM = gross − logistics ≤ gross`). Dữ liệu ưu tiên nhóm mốc của Anomaly A;
   `fact_pnl_monthly` lấy `cogs` thẳng từ `fact_sales_out` nên gross margin theo kênh
   cao hơn bảng trong đề bài, nhưng **thứ hạng và khoảng cách giữa các kênh giữ nguyên**
   — MT vẫn gross thuộc nhóm cao nhất và net **thấp nhất**.
2. **Trade spend kênh MT** phải đạt ~38% doanh thu thì Circle K / GS25 mới âm đúng như
   Anomaly C, cao hơn mức 26,8% ghi trong `dim_channel` (cột đó là *typical*, không phải
   giá trị thực đo). Tỷ lệ chi của 4 kênh còn lại nhân 0,80 để EBIT 12T đạt đúng 372 tỷ.
3. **`fact_container_cycle.containers_issued` = vỏ mới cấp vào lưu thông**, không phải số
   bình 19L giao mỗi tháng — đây là cách đọc duy nhất khớp được với chính các con số tiền
   của đề bài (62.400 vỏ mất → 4,80 tỷ). Vòng quay vỏ neo ở 4,1 lượt/năm.
4. **Trọng số dân số Miền Bắc** trong đề bài cộng lại 101,0%; đã hạ Hà Nội 42,0 → 41,0.
5. **Nghệ An** doanh thu ~28 tỷ/H1 theo trọng số dân số 6% của đề bài, không phải 18,4 tỷ
   như bảng Anomaly A ghi; CM +17,2% và chi phí 760 đ/lít — hai con số dùng để đối chứng
   với Hà Tĩnh — thì đúng tuyệt đối.
6. **Sản lượng sản xuất 24T** cao hơn sản lượng bán vì công suất ngày của 9 dây chuyền
   (bảng B7) lớn hơn hẳn công suất năm của 2 nhà máy; đã ưu tiên giữ đúng utilization
   91,4% / 84,7% vì đó là con số Scenario 5 đọc ra.
