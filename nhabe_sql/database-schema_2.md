# DATA SCHEMA – MAY NHÀ BÈ (NBC) | BI KIỂM SOÁT BIÊN LỢI NHUẬN
## Database: `nhabe_bi_demo` (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 2025-01-01 → 2026-06-30 (18 tháng) | "Hiện tại" = cuối 30/06/2026 | Tỷ giá: 1 USD = 26.000 VND

Tài liệu này là **nguồn tham chiếu schema** cho AI engine. Mọi tên bảng/cột khớp chính xác với DDL đã tạo. Enum/master values bằng tiếng Việt; tên bảng/cột bằng tiếng Anh.

---

## SƠ ĐỒ QUAN HỆ

```
dim_calendar (date PK)
  └── fact_pnl.month_date
  └── fact_gcn.month_date
  └── fact_sample_cost.created_date

dim_sales_team (team_id PK, 1..6)
  └── fact_pnl.team_id
  └── fact_gcn.team_id
  └── fact_sample_cost.team_id

dim_customer (customer_id PK)
  └── fact_pnl.customer_id
  └── fact_gcn.customer_id
  └── fact_sample_cost.customer_id
  └── fact_customer_yearly.customer_id

dim_product_category (category_id PK)
  └── fact_gcn.category_id
  └── fact_sample_cost.category_id

dim_factory (factory_id PK)
  └── fact_gcn.factory_id

fact_pnl              ⭐ FACT CHÍNH (P&L tháng × team × khách × hình thức)
fact_gcn              (đơn gia công ngoài)
fact_sample_cost      (mẫu — phòng mẫu)
fact_customer_yearly  (P&L khách theo năm — trend đa năm)
```

**Cấp độ chi tiết (grain):**
- `fact_pnl`: 1 dòng = 1 tháng × 1 team × 1 khách × 1 hình thức hợp đồng.
- `fact_gcn`: 1 dòng = 1 đơn gia công ngoài.
- `fact_sample_cost`: 1 dòng = 1 mẫu.
- `fact_customer_yearly`: 1 dòng = 1 khách × 1 năm.

---

## DIMENSION TABLES

### 1. dim_calendar (~546 rows, 2025-01-01 → 2026-06-30)
Bảng thời gian, phục vụ trend & seasonality.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `date` | DATE PK | Ngày | |
| `year` | INT | Năm (2025, 2026) | |
| `quarter` | INT | Quý 1–4 | |
| `month` | INT | Tháng 1–12 | |
| `month_date` | DATE | Ngày đầu tháng (khóa join tháng) | dùng cho fact_pnl/fact_gcn |
| `week_of_year` | INT | Tuần trong năm | |
| `day_of_week` | INT | 0=Thứ 2 … 6=Chủ nhật | |
| `is_weekend` | TINYINT | 1 nếu T7/CN | |
| `is_tet_season` | TINYINT | 1 nếu rơi vào cao điểm Tết (T1–T2) | |
| `season_phase` | ENUM | 'thap' / 'tang' / 'dinh' / 'ha_nhiet' | Đáy=T2; đỉnh=T5,T7 |

### 2. dim_sales_team (6 rows)
6 nhóm kinh doanh.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `team_id` | INT PK | 1–6 | |
| `team_name` | VARCHAR | 'Sale 1' … 'Sale 6' | |
| `team_leader_name` | VARCHAR | Tên trưởng nhóm (tiếng Việt) | |

### 3. dim_customer (~30 rows)
Khách hàng (thương hiệu quốc tế).

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `customer_id` | INT PK | | |
| `customer_name` | VARCHAR | Tên brand (FABIAN, MANGO, RIVER ISLAND…) | |
| `country` | VARCHAR | Quốc gia khách | |
| `default_contract_type` | ENUM | 'FOB'/'CM'/'GC'/'ODM' | hình thức chủ đạo |
| `classification` | ENUM | 'uu_tien'/'giu_co_dieu_kien'/'canh_bao'/'rui_ro' | phân loại theo biên net (Rule 2) |
| `is_active` | TINYINT | 1 đang phục vụ | |
| `note` | VARCHAR | Ghi chú (VD: "lỗ 3 năm liền") | |

### 4. dim_product_category (~10 rows)
Chủng loại sản phẩm.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `category_id` | INT PK | | |
| `category_name` | VARCHAR | Quần tây nam/nữ, Veston nam/nữ, Ghile, Jacket, Sơ mi, Quần short, Đầm/Váy, Áo khoác | |
| `gender` | ENUM | 'MEN'/'LADY'/'OTHERS' | |
| `season_bias` | ENUM | 'xuan_he'/'thu_dong'/'quanh_nam' | quần short/đầm–xuân hè; veston/áo khoác–thu đông |

### 5. dim_factory (~15 rows)
Nhà máy: nội bộ + vệ tinh gia công ngoài.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `factory_id` | INT PK | | |
| `factory_name` | VARCHAR | XN NBT, Khu A XN1/XN2, Phú Tài Linh, Mai Lan Anh, Phương Anh, Tây Đô, Hòa Thọ, D'Sago, Kontum… | |
| `province` | VARCHAR | Tỉnh/TP | |
| `region` | ENUM | 'Bac'/'Trung'/'Nam' | |
| `is_internal` | TINYINT | 1 = nội bộ; 0 = gia công ngoài | |
| `distance_tier` | ENUM | 'gan'/'trung_binh'/'xa' | Kontum, Ninh Thuận, Phan Rang = 'xa' |

---

## FACT TABLES

### 6. fact_pnl ⭐ (FACT CHÍNH — ~4–6K rows)
P&L chi tiết theo tháng × team × khách × hình thức. Nền cho phân hệ phân loại khách + hiệu quả team.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `pnl_id` | INT PK | | |
| `month_date` | DATE FK | → dim_calendar.month_date | |
| `team_id` | INT FK | → dim_sales_team | |
| `customer_id` | INT FK | → dim_customer | |
| `contract_type` | ENUM | 'FOB'/'CM'/'GC'/'ODM' | |
| `revenue_vnd` | DECIMAL(18,0) | Doanh thu thuần | VND |
| `cogs_vnd` | DECIMAL(18,0) | Giá vốn | VND |
| `gross_profit_vnd` | DECIMAL(18,0) | Lãi gộp = revenue − cogs | VND |
| `indirect_cost_vnd` | DECIMAL(18,0) | Chi phí gián tiếp phân bổ | VND |
| `net_profit_vnd` | DECIMAL(18,0) | Lãi net = gross − indirect | VND |
| `gross_margin_pct` | DECIMAL(6,4) | Tỷ lệ lãi gộp | tỷ lệ (0–1) |
| `net_margin_pct` | DECIMAL(6,4) | Tỷ lệ lãi net | tỷ lệ (0–1) |

⚠️ **Luôn dùng `revenue_vnd` cho doanh thu, `net_profit_vnd` cho lãi net. Không tự recompute nếu cột đã có.**
⚠️ **Grain = tháng×team×khách×hình thức → coi chừng nhân đôi khi JOIN sang bảng khác grain.**

### 7. fact_gcn (~200–400 rows)
Đơn gia công ngoài — kiểm soát chênh giá ký vs giá GCN.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `gcn_id` | INT PK | | |
| `month_date` | DATE FK | → dim_calendar | |
| `team_id` | INT FK | | |
| `customer_id` | INT FK | | |
| `factory_id` | INT FK | → dim_factory (nhà máy GCN) | |
| `category_id` | INT FK | | |
| `qty` | INT | Số lượng (pcs) | pcs |
| `signed_price_usd` | DECIMAL(10,2) | **Giá ký FOB với khách** | USD/pc |
| `gcn_price_usd` | DECIMAL(10,2) | **Giá trả nhà máy gia công** | USD/pc |
| `fob_revenue_vnd` | DECIMAL(18,0) | DT quy đổi (qty×signed×26.000) | VND |
| `gcn_cost_vnd` | DECIMAL(18,0) | Chi phí GCN (qty×gcn×26.000) | VND |
| `gcn_margin_vnd` | DECIMAL(18,0) | Biên GCN = fob_revenue − gcn_cost | VND |
| `gcn_margin_pct` | DECIMAL(6,4) | Biên GCN / fob_revenue | tỷ lệ |
| `is_loss_risk` | TINYINT | 1 nếu gcn_price > signed_price | |

⚠️ **Đừng nhầm `signed_price_usd` (giá bán khách) với `gcn_price_usd` (giá mua từ nhà máy). Lỗ biên khi gcn_price > signed_price.**

### 8. fact_sample_cost (~2K rows)
Mẫu do phòng mẫu thực hiện — kiểm soát chi phí may mẫu & mẫu-không-ra-đơn.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `sample_id` | INT PK | | |
| `created_date` | DATE FK | → dim_calendar | |
| `delivered_date` | DATE | Ngày giao mẫu | |
| `team_id` | INT FK | | |
| `customer_id` | INT FK | | |
| `category_id` | INT FK | | |
| `sample_stage` | ENUM | 'DEV'/'FIT'/'PROTO'/'PP'/'SIZE_SET'/'MARKETING' | |
| `qty` | INT | Số mẫu | pcs |
| `cost_vnd` | DECIMAL(18,0) | Chi phí may mẫu | VND |
| `resulted_in_order` | TINYINT | 1 nếu mẫu này dẫn tới đơn hàng | |
| `lead_time_days` | INT | Số ngày từ tạo → giao mẫu | ngày |

⚠️ **`resulted_in_order = 0` = mẫu chào rồi không ra đơn → chi phí "đốt". Cảnh báo khi team có tỷ lệ này cao.**

### 9. fact_customer_yearly (~90 rows)
P&L khách theo năm — phát hiện lỗ nhiều năm liền.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `id` | INT PK | | |
| `customer_id` | INT FK | | |
| `year` | VARCHAR | '2024' / '2025' / '2026H1' | |
| `revenue_vnd` | DECIMAL(18,0) | DT năm | VND |
| `gross_profit_vnd` | DECIMAL(18,0) | Lãi gộp năm | VND |
| `net_profit_vnd` | DECIMAL(18,0) | Lãi net năm (âm = lỗ) | VND |
| `net_margin_pct` | DECIMAL(6,4) | Tỷ lệ lãi net năm | tỷ lệ |

⚠️ **`year='2026H1'` chỉ 6 tháng → KHÔNG so trực tiếp giá trị tuyệt đối với năm đầy đủ; so tỷ lệ hoặc annualize.**

---

## SQL TEMPLATES

### T1 — Tổng quan P&L 6 tháng 2026 (Scenario 1)
```sql
SELECT SUM(revenue_vnd) AS doanh_thu,
       SUM(gross_profit_vnd) AS lai_gop,
       SUM(gross_profit_vnd)/SUM(revenue_vnd) AS ty_le_lai_gop,
       SUM(net_profit_vnd) AS lai_net,
       SUM(net_profit_vnd)/SUM(revenue_vnd) AS ty_le_lai_net
FROM fact_pnl
WHERE month_date BETWEEN '2026-01-01' AND '2026-06-30';
```

### T2 — Hiệu quả theo team (Scenario 2) — Sale 5 thấp nhất
```sql
SELECT t.team_name,
       SUM(p.revenue_vnd) AS doanh_thu,
       SUM(p.net_profit_vnd) AS lai_net,
       SUM(p.net_profit_vnd)/SUM(p.revenue_vnd) AS ty_le_net
FROM fact_pnl p JOIN dim_sales_team t USING(team_id)
WHERE p.month_date >= '2026-01-01'
GROUP BY t.team_id ORDER BY ty_le_net ASC;
```

### T3 — Phân loại khách theo biên net (Scenario 3)
```sql
SELECT c.customer_name, c.classification,
       SUM(p.revenue_vnd) AS doanh_thu,
       SUM(p.net_profit_vnd) AS lai_net,
       SUM(p.net_profit_vnd)/SUM(p.revenue_vnd) AS ty_le_net
FROM fact_pnl p JOIN dim_customer c USING(customer_id)
WHERE p.month_date >= '2026-01-01'
GROUP BY c.customer_id
ORDER BY ty_le_net ASC;   -- MANGO ~1,5% (DT lớn), BESTSELLER âm sẽ nổi lên đầu
```

### T3b — Trend lỗ đa năm 1 khách (Scenario 3 follow-up)
```sql
SELECT y.year, y.revenue_vnd, y.net_profit_vnd, y.net_margin_pct
FROM fact_customer_yearly y JOIN dim_customer c USING(customer_id)
WHERE c.customer_name = 'BESTSELLER' ORDER BY y.year;
```

### T4 — Đơn GCN nguy cơ lỗ (Scenario 4)
```sql
SELECT c.customer_name, f.factory_name, f.province, f.distance_tier,
       g.qty, g.signed_price_usd, g.gcn_price_usd,
       g.gcn_margin_vnd
FROM fact_gcn g
JOIN dim_customer c USING(customer_id)
JOIN dim_factory f USING(factory_id)
WHERE g.gcn_margin_vnd < 0
ORDER BY g.gcn_margin_vnd ASC;   -- tổng ~ −2,8 tỷ
```

### T4b — Tỷ lệ giữ nội bộ vs gia công ngoài theo team
```sql
SELECT t.team_name,
       SUM(CASE WHEN f.is_internal=1 THEN g.qty ELSE 0 END) AS noi_bo,
       SUM(CASE WHEN f.is_internal=0 THEN g.qty ELSE 0 END) AS gia_cong_ngoai
FROM fact_gcn g JOIN dim_factory f USING(factory_id)
JOIN dim_sales_team t USING(team_id)
WHERE g.month_date >= '2026-01-01'
GROUP BY t.team_id;
```

### T5 — Chi phí may mẫu theo team + tỷ lệ ra đơn (Scenario 5)
```sql
SELECT t.team_name,
       SUM(s.cost_vnd) AS chi_phi_may_mau,
       AVG(s.resulted_in_order) AS ty_le_ra_don,
       SUM(CASE WHEN s.resulted_in_order=0 THEN s.cost_vnd ELSE 0 END) AS mau_khong_ra_don
FROM fact_sample_cost s JOIN dim_sales_team t USING(team_id)
WHERE s.created_date >= '2026-01-01'
GROUP BY t.team_id ORDER BY chi_phi_may_mau DESC;   -- Sale 6 ~1,8 tỷ đứng đầu
```

### T5b — Tỷ lệ may mẫu / lãi gộp theo team
```sql
SELECT t.team_name,
       sm.sample_cost, pl.gross,
       sm.sample_cost/pl.gross AS ty_le_may_mau_tren_lai_gop
FROM (SELECT team_id, SUM(cost_vnd) sample_cost FROM fact_sample_cost
      WHERE created_date>='2026-01-01' GROUP BY team_id) sm
JOIN (SELECT team_id, SUM(gross_profit_vnd) gross FROM fact_pnl
      WHERE month_date>='2026-01-01' GROUP BY team_id) pl USING(team_id)
JOIN dim_sales_team t USING(team_id)
ORDER BY ty_le_may_mau_tren_lai_gop DESC;   -- Sale 6 chạm ~40%
```

### T6 — Goal-seek: gap tới net 5% (Scenario 6 — CLIMAX)
```sql
SELECT SUM(revenue_vnd) AS dt,
       SUM(net_profit_vnd) AS net_hien_tai,
       0.05*SUM(revenue_vnd) AS net_muc_tieu,
       0.05*SUM(revenue_vnd) - SUM(net_profit_vnd) AS gap_can_bu
FROM fact_pnl WHERE month_date >= '2026-01-01';   -- gap ~20 tỷ
```

### T6b — Định lượng đòn bẩy: tổng lỗ nhóm rủi ro (đòn 1)
```sql
SELECT SUM(p.net_profit_vnd) AS tong_lo_nhom_rui_ro
FROM fact_pnl p JOIN dim_customer c USING(customer_id)
WHERE c.classification = 'rui_ro' AND p.month_date >= '2026-01-01'
  AND p.net_profit_vnd < 0;   -- ~ −9 tỷ (cắt lỗ → +9 tỷ)
```

---

## JOIN WARNINGS

1. **fact_pnl × fact_sample_cost:** khác grain (P&L theo tháng×team×khách×hình thức; sample theo từng mẫu). **Aggregate riêng từng bảng rồi mới JOIN theo team_id/customer_id** (xem T5b), đừng JOIN thẳng dòng-với-dòng → nhân đôi.
2. **fact_pnl × fact_gcn:** fact_gcn là tập con đơn GCN, KHÔNG bằng toàn bộ doanh thu; đừng cộng `fob_revenue_vnd` vào `revenue_vnd`. Dùng fact_gcn chỉ để soi biên gia công.
3. **fact_customer_yearly year='2026H1':** chỉ 6 tháng → không so tuyệt đối với '2024'/'2025' (12 tháng). So `net_margin_pct` hoặc nhân đôi.
4. **dim_factory.is_internal:** khi hỏi "gia công ngoài" chỉ lấy `is_internal=0`; nội bộ là `=1`.
5. **contract_type NULL / GC vs GCN:** 'GC' trong `contract_type` = hợp đồng gia công; đơn giao nhà máy ngoài nằm ở `fact_gcn`. Đừng lẫn hai khái niệm.
6. **month_date vs date:** fact tables join qua `month_date` (ngày đầu tháng). Muốn lọc theo ngày cụ thể phải dùng `dim_calendar.date`.
7. **Nhân đôi khi team×khách:** một khách nhiều team → GROUP BY đúng chiều đang phân tích (Rule 6), nếu không SUM sẽ đếm trùng.

---

## ĐƠN VỊ TIỀN TỆ

| Bảng | Cột | Đơn vị |
|---|---|---|
| fact_pnl | revenue_vnd, cogs_vnd, gross_profit_vnd, indirect_cost_vnd, net_profit_vnd | VND |
| fact_gcn | fob_revenue_vnd, gcn_cost_vnd, gcn_margin_vnd | VND |
| fact_gcn | signed_price_usd, gcn_price_usd | USD/pc |
| fact_sample_cost | cost_vnd | VND |
| fact_customer_yearly | revenue_vnd, gross_profit_vnd, net_profit_vnd | VND |

**Tỷ giá quy đổi:** 1 USD = 26.000 VND.

**Format hiển thị cho board:**
- > 1 tỷ: "X,X tỷ" (VD "138 tỷ", "1,27 nghìn tỷ")
- < 1 tỷ: "XXX triệu"
- Phần trăm: 1 chữ số thập phân ("3,4%")
