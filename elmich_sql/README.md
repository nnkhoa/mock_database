# `elmich_houseware_demo` — Elmich (gia dụng / houseware Việt Nam)

Mock BI database cho demo AI-for-BI dành cho **CEO Elmich Việt Nam**, pitching Hội đồng Quản trị.
Phạm vi dữ liệu **01/09/2024 → 31/08/2026** (24 tháng · 730 ngày). "Hiện tại" = cuối tháng 8/2026.

Schema trong thư mục này **khớp y hệt `database-schema.md`** (kèm bên cạnh): đúng 22 bảng
nghiệp vụ (11 dimension + 11 fact) với đúng tên cột, đúng kiểu — cộng 4 bảng metadata
(`_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary`, lấy trực tiếp từ COMMENT
trong DDL để tránh trùng lặp tư liệu).

Nguồn thiết kế: `ELMICH_claude-code-instruction.md` + `ELMICH_database-schema.md` (brief gốc,
đã brainstorm sẵn 6 câu hỏi demo và 4 anomaly có chủ đích, 2 anomaly nối chuỗi nhân quả).

---

## 1. Nạp dữ liệu

### Cách nhanh nhất (container `mock_database` đang chạy)

```bash
./populate.sh elmich          # chạy từ thư mục gốc của repo
```

### Từ đầu, container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=elmich_houseware_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate theo đúng thứ tự
docker exec -i mock_database mysql -uroot -proot < elmich_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < elmich_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < elmich_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < elmich_sql/04_a_transaction_data_sales.sql
docker exec -i mock_database mysql -uroot -proot < elmich_sql/04_b_transaction_data_rest.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < elmich_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS elmich_houseware_demo; CREATE DATABASE elmich_houseware_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3-4
```

**Lưu ý:** `04_transaction_data.sql` được tách thành `04a` (fact_sales_out, ~99 MB — fact chính,
~836K dòng) và `04b` (10 bảng fact còn lại, ~16 MB) vì tổng dung lượng gần ngưỡng 200MB khuyến
nghị trong quy trình sinh dữ liệu.

---

## 2. Số liệu tổng quan

| Bảng | Số dòng |
|---|---|
| `dim_calendar` | 730 |
| `dim_region` | 3 |
| `dim_province` | 34 |
| `dim_channel` | 4 |
| `dim_retail_chain` | 6 |
| `dim_distributor` | 48 |
| `dim_showroom` | 42 |
| `dim_ecom_platform` | 4 |
| `dim_category` | 18 |
| `dim_product` | 420 |
| `dim_trade_program` | 40 |
| `fact_sales_out` ⭐ | 836.167 |
| `fact_sales_in` | 75.497 |
| `fact_distributor_inventory` | 1.152 |
| `fact_receivables` | 1.152 |
| `fact_trade_spend` | 2.357 |
| `fact_showroom_traffic` | 30.660 |
| `fact_price_tracking` | 88.200 |
| `fact_production` | 19.232 |
| `fact_inventory_snapshot` | 44.100 |
| `fact_stockout` | 5.040 |
| `fact_monthly_financials` | 264 |
| `_meta_tables` / `_meta_columns` / `_meta_kpi` / `_meta_glossary` | 22 / 172 / 11 / 14 |

**Mốc neo tài chính đã khớp (validate.py: 25/25 PASS):**
- FY2025 doanh thu thuần = 1.449,0 tỷ (mốc 1.450 ±0,5%)
- Tổng 24 tháng = 3.029,8 tỷ (mốc ≈3.031)
- ASP toàn công ty = 766.054đ (mốc 760.000–810.000đ)
- Biên gộp toàn công ty = 38,2% (mốc 37,5–39,0%)
- Pareto: top 84 SKU (20%) chiếm 81,9% doanh thu (mốc 78–82%)
- Kênh 8T-2025/2026 (tỷ): GT 378,1/402,1 · MT 273/312 · Online 170,2/224,3 · Showroom 128,2/123,9

---

## 3. Bốn anomaly có chủ đích

| # | Tên | Bằng chứng trong data | Đã verify |
|---|---|---|---|
| **A1** | Xói mòn biên lợi nhuận kênh MT | `fact_trade_spend` (phí quầy kệ Chuỗi ĐM A tăng, "Mua 2 tặng 1 – Chảo Royal" Chuỗi ĐM B) | CM kênh MT: 12,1% (T1/26) → 8,7% (T8/26) ✅ |
| **A2** | Nhồi hàng kênh GT miền Trung | `fact_sales_in` vs `fact_sales_out`, `fact_distributor_inventory`, `fact_receivables` — neo vào 3 NPP: NPP Hoàng Gia–Đà Nẵng, NPP Minh Long–Nghệ An, NPP Tân Phát–Gia Lai | Chênh sell-in/out: Bắc 0,2% · **Trung 16,0%** · Nam −1,4% ✅ |
| **A3** | Online ăn thịt showroom | `fact_showroom_traffic`, `fact_price_tracking`, `fact_sales_out` — 18 SKU trong `anomaly_a3_skus.txt` | Conversion showroom: 24,1% (T1/26) → 16,8% (T8/26) ✅ |
| **A4** | Lệch pha nhà máy–thị trường | `fact_production.plan_source='Sell-in GT (T-6)'`, `fact_inventory_snapshot`, `fact_stockout` — 96 SKU tồn dư (`Trend`, Bộ nồi/Nồi đơn), 12 SKU hết hàng (top popularity nội bộ) | Tồn kho 218,0 tỷ, tồn >180 ngày = 74,1 tỷ (34,0%); mất ~27,1 tỷ do stockout ✅ |

**Chuỗi nhân quả A2 → A4:** `fact_production.plan_source` ghi rõ "Sell-in GT (T-6)" — kế hoạch
sản xuất neo vào tín hiệu sell-in kênh GT đã bị nhồi hàng ở A2, khiến 96 SKU nhóm Trend/Bộ nồi
tồn kho tăng vọt trong khi 12 SKU bán chạy nhất lại hết hàng.

Xem `anomaly_a3_skus.txt` (kèm trong thư mục này) để biết chính xác 18 SKU dùng cho A3.

---

## 4. Đơn giản hóa đã ghi nhận (documented simplification)

1. **`fact_trade_spend` 2.357 dòng** (brief ước tính ~5.200): GT trade spend gộp ở mức
   vùng/toàn quốc thay vì per-NPP; MT/ONL vẫn đủ chi tiết theo chuỗi/sàn × chương trình × nhóm hàng.
2. **`fact_stockout` 5.040 dòng** (brief ước tính ~34.000): giảm mật độ nhiễu nền (stockout
   ngẫu nhiên ngoài anomaly), giữ nguyên đúng magnitude của A4 (12 SKU top, ~24-27 tỷ, ~6-9
   ngày/tháng).
3. **`fact_sales_in` 75.497 dòng** (brief ước tính ~95.000): mỗi NPP có 3-6 đợt giao hàng/tháng
   thay vì nhiều hơn.
4. **Tỷ lệ trade spend/doanh thu kênh MT thực tế ~28-31%** (brief minh họa 17,2%→23,8%): vì
   biên gộp SKU thực tế của Elmich trong bộ dữ liệu này (~38% bình quân) cao hơn giả định ngầm
   trong brief (~29%). **Chỉ số được ưu tiên giữ đúng là CM (biên đóng góp) 12,1%→8,7%** — đây
   là con số thực sự được trích dẫn trong kịch bản demo Scenario 2.
5. **`dim_product.standard_cost_vnd`** = `list_price × (1 − gross_margin_pct) × 0,90` — hệ số
   0,90 phản ánh biên gộp `gross_margin_pct` được đo tại giá bán thực (net, sau chiết khấu bình
   quân ~10%), không phải tại giá niêm yết. Cần thiết để `SUM(gross_profit_vnd)/SUM(net_revenue_vnd)`
   trên `fact_sales_out` khớp đúng mốc 37,5-39%.
6. **Trọng số doanh thu SKU dùng exponent 1,08** (không phải 0,92 thô trong brief) — công thức
   `rank^-0.92` áp dụng thuần túy (không qua bước chọn K SKU active/ngày) chỉ cho ra Pareto ~71%,
   không đạt dải PASS 78-82% theo checklist validation D.2. Xác suất "chọn SKU nào active mỗi
   ngày" dùng exponent phẳng hơn (0,12) để tránh khuếch đại kép (SKU đuôi dài gần như không bao
   giờ được chọn).
7. **Tỷ trọng doanh thu theo NHÓM sản phẩm** (Đồ nấu 38%/Gia dụng điện 24%/Bảo quản & bàn ăn
   19%/Dao thớt & phụ kiện 12%/Gia dụng khác 7%) được ép cứng vào trọng số sinh doanh thu — cần
   thiết để ASP toàn công ty rơi đúng vào dải 760.000-810.000đ (nếu chỉ dùng popularity_rank độc
   lập, ASP lệch mạnh do quan hệ ngẫu nhiên giữa rank và giá bán).

---

## 5. Lưu ý khi kết nối AI engine (MCP)

- Data range: 01/09/2024 → 31/08/2026. "Hiện tại" = cuối tháng 8/2026.
- Metadata tables (`_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary`) là nguồn
  truth cho mô tả schema — AI engine nên query các bảng này trước khi viết SQL phức tạp.
- **Join warnings quan trọng** (xem đầy đủ trong `database-schema.md`):
  1. `fact_sales_in` (sell-in) và `fact_sales_out` (sell-out) KHÔNG BAO GIỜ cộng chung.
  2. `fact_trade_spend` grain THÁNG, `fact_sales_out` grain NGÀY — phải aggregate trước khi JOIN.
  3. `fact_distributor_inventory`, `fact_receivables`, `fact_inventory_snapshot` là bảng
     SNAPSHOT — không SUM qua nhiều `snapshot_date`.
  4. `fact_sales_out` có 4 cột điểm bán loại trừ nhau (`distributor_id`/`chain_id`/
     `showroom_id`/`platform_id`) — luôn lọc bằng `channel_id`, dùng LEFT JOIN.
- Known limitations: không có data đối thủ; không có data xuất khẩu OEM; `fact_monthly_financials`
  chỉ ở mức tháng × hạng mục, không tách được theo kênh/vùng/SKU.

---

## 6. Sinh lại dữ liệu

Scripts nằm ở `elmich_scripts/` (không được git theo dõi vì `.gitignore` loại `*.py`):

```bash
python3 elmich_scripts/gen_master.py      # → 03_master_data.sql (+ _master.pkl cho gen_facts.py)
python3 elmich_scripts/gen_facts.py       # → 04a/04b_transaction_data_*.sql
python3 elmich_scripts/gen_metadata.py    # → 02_metadata.sql (đọc COMMENT từ DB đang chạy)
python3 elmich_scripts/validate.py        # báo cáo 25 check PASS/FAIL
```

Yêu cầu: Python 3.10+ với `numpy`. Seed cố định (`SEED = 20260908`) nên kết quả tái lập được.
Thứ tự bắt buộc: `gen_master.py` → load `01+03` vào DB → `gen_facts.py` → load `04a+04b` →
`gen_metadata.py` (cần DB đã có dữ liệu để lấy COMMENT + row count) → load lại `02` → `validate.py`.
