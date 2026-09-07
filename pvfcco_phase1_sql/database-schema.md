# DATA SCHEMA — PVFCCo | AI4BI GIAI ĐOẠN 1
## Database: `pvfcco_phase1_demo` (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: kế hoạch 2024-01 → 2026-12 · thực hiện 2024-01 → 2026-08 | "Hiện tại" = tháng 8/2026
## Tổng: 11 bảng dữ liệu + 4 bảng metadata + 6 view · 7.696 dòng fact

> **Quy ước chung**
> - `fiscal_period` là `VARCHAR(7)` định dạng `'YYYY-MM'`, có mặt ở **mọi** bảng fact. So sánh chuỗi hoạt động đúng: `BETWEEN '2026-01' AND '2026-08'`.
> - Mọi cột sản lượng có hậu tố `_ton`, đơn vị **tấn**.
> - Mọi cột tiền tệ có hậu tố `_vnd_bn`, đơn vị **tỷ đồng** (billion VND) — khớp với đơn vị đo khai báo trong file phạm vi. Không lưu VND thô.
> - Giá trị master data bằng **tiếng Việt**; tên bảng và cột bằng **tiếng Anh**.
> - Toàn bộ database ở **grain tháng** — không có bảng nào cấp ngày.
> - Phạm vi bị khoá theo `20260904_AI4BI_PVFCCo_Chisochieudulieu_V9.xlsx`: đúng 13 chỉ số và 05 chiều, không hơn.

---

## SƠ ĐỒ QUAN HỆ

```
dim_calendar (fiscal_period PK)
  ├── fact_sales.fiscal_period
  ├── fact_production.fiscal_period
  ├── fact_inventory.fiscal_period
  ├── fact_gross_profit.fiscal_period
  └── fact_opex.fiscal_period

dim_org_unit (org_unit_id PK)
  ├── fact_sales.org_unit_id
  ├── fact_inventory.org_unit_id
  ├── fact_gross_profit.org_unit_id
  ├── fact_opex.org_unit_id
  ├── fact_production.org_unit_id   (luôn = 3, KHÔNG dùng làm chiều)
  └── self-reference: dim_org_unit.parent_org_unit_id → dim_org_unit.org_unit_id

dim_product (product_id PK)
  ├── fact_sales.product_id
  ├── fact_production.product_id     (chỉ 4 mặt hàng is_manufactured = 1)
  └── fact_inventory.product_id

dim_sales_region (region_id PK)
  └── fact_sales.region_id           (CHỈ fact_sales)

dim_cost_item (cost_item_id PK)
  └── fact_opex.cost_item_id         (CHỈ fact_opex)

dim_scenario (scenario_id PK)
  ├── fact_sales.scenario_id
  └── fact_production.scenario_id    (CHỈ hai bảng này có kịch bản)
```

## MA TRẬN CHỈ SỐ × CHIỀU (bản hợp đồng phạm vi)

Ô có ✓ nghĩa là mô hình hỗ trợ phân rã; ô trống nghĩa là **không hỗ trợ và đó là đúng thiết kế**.

| # | Chỉ số | Bảng / View | Thời gian | Đơn vị | Sản phẩm | Khu vực | Khoản mục |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | Sản lượng kinh doanh (TH/KH) | `vw_sales` | ✓ | ✓ | ✓ | ✓ | |
| 2 | Doanh thu bán hàng (TH/KH) | `vw_sales` | ✓ | ✓ | ✓ | ✓ | |
| 3 | Tồn kho thành phẩm | `vw_inventory` | ✓ | ✓ | ✓ | | |
| 4 | Sản lượng sản xuất (TH/KH) | `vw_production` | ✓ | | ✓ | | |
| 5 | Giá vốn hàng bán | `vw_gross_profit` | ✓ | ✓ | | | |
| 6 | Lợi nhuận gộp | `vw_gross_profit` | ✓ | ✓ | | | |
| 7 | Chi phí bán hàng | `vw_opex` | ✓ | ✓ | | | ✓ |
| 8 | Chi phí quản lý | `vw_opex` | ✓ | ✓ | | | ✓ |
| 9 | Tỷ lệ HTKH sản lượng kinh doanh | `vw_sales` | ✓ | ✓ | ✓ | ✓ | |
| 10 | Tỷ lệ tăng/giảm SLKD so cùng kỳ | `vw_sales` | ✓ | ✓ | ✓ | ✓ | |
| 11 | Tỷ lệ HTKH doanh thu | `vw_sales` | ✓ | ✓ | ✓ | ✓ | |
| 12 | Tỷ lệ HTKH sản lượng sản xuất | `vw_production` | ✓ | | ✓ | | |
| 13 | Tỷ lệ tăng/giảm SLSX so cùng kỳ | `vw_production` | ✓ | | ✓ | | |

Bảng này khớp 65/65 ô với ma trận trong file phạm vi V9 (kiểm bằng `conformance.py`).

---

## BẢNG DIMENSION

### `dim_calendar` — 36 dòng | chiều **Thời gian**

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `fiscal_period` | VARCHAR(7) **PK** | Kỳ báo cáo `'YYYY-MM'`. Khóa nối duy nhất với mọi fact |
| `year` | SMALLINT | 2024 / 2025 / 2026 |
| `quarter` | TINYINT | 1–4 |
| `month` | TINYINT | 1–12 |
| `month_name_vi` | VARCHAR(20) | `"Tháng 8/2026"` — chỉ để hiển thị |
| `quarter_name_vi` | VARCHAR(20) | `"Quý 3/2026"` |
| `period_start_date` / `period_end_date` | DATE | Ngày đầu / cuối tháng |
| `prior_year_period` | VARCHAR(7) NULL | Cùng kỳ năm trước. Dùng cột này thay vì tự tính số học |
| `prior_period` | VARCHAR(7) NULL | Kỳ liền trước |
| `is_current_period` | TINYINT(1) | Đúng 1 dòng = 1 → `'2026-08'` |

Hai cột `prior_*` tồn tại để lớp AI không phải tự làm số học trên khóa kỳ — đúng với lịch dương nhưng sai ngay khi lịch tài chính lệch năm dương lịch.

### `dim_org_unit` — 7 dòng | chiều **Đơn vị / phạm vi báo cáo**

| id | code | Tên rút gọn | Cấp | KD | SX |
|---|---|---|---|---|---|
| 1 | TCT | PVFCCo | 1 | | |
| 2 | VPTCT | Cơ quan TCT | 2 | ✓ | |
| 3 | NMPM | NM Đạm Phú Mỹ | 2 | | ✓ |
| 4 | PMB | PVFCCo Miền Bắc | 2 | ✓ | |
| 5 | PCE | PVFCCo Miền Trung | 2 | ✓ | |
| 6 | PSE | PVFCCo Đông Nam Bộ | 2 | ✓ | |
| 7 | PSW | PVFCCo Tây Nam Bộ | 2 | ✓ | |

⚠️ Bảng fact chỉ chứa **cấp lá** (`org_level = 2`). `org_unit_id = 1` không có dòng fact nào.
Cột `has_sales_activity` / `has_production_activity` là cờ kỹ thuật phục vụ kiểm tra toàn vẹn, **không dùng để nhóm**.

### `dim_product` — 8 dòng | chiều **Sản phẩm / Mặt hàng**

| id | code | Tên | Tự sản xuất |
|---|---|---|---|
| 1 | SP01 | Đạm Phú Mỹ (Urê) | ✓ |
| 2 | SP02 | NPK Phú Mỹ | ✓ |
| 3 | SP03 | NH3 (Amoniac) | ✓ |
| 4 | SP04 | UAN | ✓ |
| 5 | SP05 | Kali Phú Mỹ | |
| 6 | SP06 | DAP Phú Mỹ | |
| 7 | SP07 | SA Phú Mỹ | |
| 8 | SP08 | Urê nhập khẩu | |

⚠️ "Đạm Phú Mỹ (Urê)" và "Urê nhập khẩu" là hai mặt hàng khác nhau. Khi người dùng chỉ nói "urê" thì phải hỏi lại, không tự chọn.
`product_group_id` luôn `NULL` ở Giai đoạn 1 — là điểm cắm cho chiều Nhóm sản phẩm của giai đoạn sau.

### `dim_sales_region` — 6 dòng | chiều **Khu vực kinh doanh**

| id | code | Tên |
|---|---|---|
| 1 | KV01 | Miền Bắc |
| 2 | KV02 | Miền Trung |
| 3 | KV03 | Tây Nguyên |
| 4 | KV04 | Đông Nam Bộ |
| 5 | KV05 | Tây Nam Bộ |
| 6 | KV06 | Xuất khẩu |

⚠️ Khu vực **không** suy ra được từ đơn vị. Một đơn vị bán ở nhiều khu vực và một khu vực có nhiều đơn vị cùng bán — Tây Nguyên có cả PVFCCo Miền Trung và PVFCCo Đông Nam Bộ. Chỉ áp dụng cho `fact_sales`.

### `dim_cost_item` — 14 dòng | chiều **Khoản mục**

| Nhóm | Khoản mục |
|---|---|
| CPBH | Chi phí nhân viên bán hàng · Chi phí vận chuyển, bốc xếp · Chi phí bao bì, đóng gói · Chi phí kho bãi, lưu kho · Chi phí quảng cáo, khuyến mại, hỗ trợ đại lý · Chi phí hội nghị khách hàng, hội thảo đầu bờ · Chi phí bán hàng khác |
| CPQL | Chi phí nhân viên quản lý · Chi phí vật liệu, đồ dùng văn phòng · Chi phí khấu hao tài sản cố định · Thuế, phí và lệ phí · Chi phí dịch vụ mua ngoài · Chi phí dự phòng · Chi phí quản lý khác |

⚠️ Chi phí bán hàng và Chi phí quản lý là **hai lát cắt của cùng một bảng** `fact_opex`, lọc bằng `cost_group_code`. Không dùng `UNION`.

### `dim_scenario` — 2 dòng

| id | code | Tên |
|---|---|---|
| 1 | TH | Thực hiện |
| 2 | KH | Kế hoạch |

Chỉ áp dụng cho `fact_sales` và `fact_production`. Giai đoạn sau bổ sung Ước thực hiện / Dự báo bằng cách thêm dòng, không đổi cấu trúc bảng fact.

---

## BẢNG FACT

### `fact_sales` — 3.808 dòng ⭐

Grain: `fiscal_period × org_unit_id × product_id × region_id × scenario_id`

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `volume_ton` | DECIMAL(18,2) | **Chỉ số 1** — Sản lượng kinh doanh, tấn |
| `revenue_vnd_bn` | DECIMAL(18,4) | **Chỉ số 2** — Doanh thu bán hàng, tỷ đồng |

TH có đến `'2026-08'`, KH có đến `'2026-12'`.

### `fact_production` — 272 dòng

Grain: `fiscal_period × product_id × scenario_id`

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `org_unit_id` | INT | Luôn = 3 (Nhà máy Đạm Phú Mỹ). ⚠️ **KHÔNG dùng làm chiều phân rã** |
| `volume_ton` | DECIMAL(18,2) | **Chỉ số 4** — Sản lượng sản xuất, tấn |

`vw_production` đã loại `org_unit_id` ra để hàng rào phạm vi được khoá ở mức cột.

### `fact_inventory` — 1.216 dòng — SNAPSHOT

Grain: `fiscal_period × org_unit_id × product_id`

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `closing_stock_ton` | DECIMAL(18,2) | **Chỉ số 3** — Tồn kho thành phẩm cuối kỳ, tấn |

⚠️⚠️ Bán cộng: cộng được theo đơn vị và sản phẩm, **tuyệt đối không cộng theo thời gian**. Không có kế hoạch, không có chiều khu vực.

Giai đoạn 1 không có chỉ số nhập/xuất kho nên đẳng thức `Tồn cuối = Tồn đầu + Sản xuất − Bán` không kiểm chứng được trong phạm vi này. Dữ liệu demo sinh tồn kho ở mức 15–25 ngày bán để hợp lý về nghiệp vụ, không áp đẳng thức cân đối.

### `fact_gross_profit` — 160 dòng

Grain: `fiscal_period × org_unit_id`

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `cogs_vnd_bn` | DECIMAL(18,4) | **Chỉ số 5** — Giá vốn hàng bán, tỷ đồng |
| `gross_profit_vnd_bn` | DECIMAL(18,4) | **Chỉ số 6** — Lợi nhuận gộp, tỷ đồng |

⚠️ Không phân rã theo sản phẩm hay khu vực. Trong bộ demo `gross_profit = doanh thu TH − cogs` (lệch 0,0000 tỷ ở mức lũy kế) để buổi UAT đối soát chéo được; **khi triển khai thật cả hai số nạp nguyên trạng từ nguồn kế toán, không tính lại**.

### `fact_opex` — 2.240 dòng

Grain: `fiscal_period × org_unit_id × cost_item_id`

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `amount_vnd_bn` | DECIMAL(18,4) | **Chỉ số 7 hoặc 8** — giá trị chi phí, tỷ đồng |

Không có số kế hoạch.

---

## VIEW NGỮ NGHĨA

Repo `mock_database` mặc định không dùng view; bộ này có 6 view vì hai lý do:

1. **Xoay kịch bản TH/KH thành cột.** `%HTKH` trở thành một phép chia trên cùng dòng thay vì self-join — đây là nguồn sai số lớn nhất khi để mô hình ngôn ngữ tự sinh SQL.
2. **Khoá hàng rào phạm vi ở mức cột.** Cột không có trong view thì không thể `GROUP BY`. Dặn trong system prompt thì mô hình tuân thủ *phần lớn* thời gian — "phần lớn" không phải thứ mang ra nghiệm thu được.

| View | Cột đo | Chiều phơi ra |
|---|---|---|
| `vw_sales` | `volume_act_ton`, `volume_plan_ton`, `revenue_act_vnd_bn`, `revenue_plan_vnd_bn` | Thời gian, Đơn vị, Sản phẩm, Khu vực |
| `vw_production` | `volume_act_ton`, `volume_plan_ton` | Thời gian, Sản phẩm |
| `vw_inventory` | `closing_stock_ton` | Thời gian, Đơn vị, Sản phẩm |
| `vw_gross_profit` | `cogs_vnd_bn`, `gross_profit_vnd_bn` | Thời gian, Đơn vị |
| `vw_opex` | `amount_vnd_bn` | Thời gian, Đơn vị, Khoản mục |
| `vw_executive_summary` | 3 chỉ tiêu điều hành TH/KH theo tháng, cấp Tổng công ty | Thời gian |

`vw_executive_summary` tồn tại riêng cho ba câu hỏi điều hành tổng hợp (C1–C3), vốn phải so **ba chỉ tiêu khác hạt** với nhau — bước dễ sai nhất trong cả bộ 30 câu.

**Cột thuộc tính cố ý KHÔNG phơi ra view:** `has_sales_activity`, `has_production_activity`, `is_manufactured`, `product_group_id`, `org_level` (chỉ có ở view có chiều đơn vị, dùng để lọc chứ không để nhóm). Ba thuộc tính từng cân nhắc rồi loại hẳn khỏi cả bảng dimension vì chúng là **cấp nhóm không có trong phạm vi**: `Tự sản xuất / Kinh doanh` (tương đương chiều Nhóm sản phẩm), `Nội địa / Xuất khẩu` (một cấp trên Khu vực), và phân loại đơn vị theo loại hình.

---

## MẪU TRUY VẤN CHUẨN

```sql
-- Lũy kế từ đầu năm đến kỳ hiện tại
SELECT SUM(volume_act_ton)  AS slkd_th,
       SUM(volume_plan_ton) AS slkd_kh,
       SUM(volume_act_ton) / NULLIF(SUM(volume_plan_ton), 0) AS pct_htkh
FROM vw_sales
WHERE (year, month) <= (SELECT year, month FROM dim_calendar WHERE is_current_period = 1)
  AND year = (SELECT year FROM dim_calendar WHERE is_current_period = 1);

-- So cùng kỳ ở mức lũy kế (khớp số tháng)
SELECT SUM(CASE WHEN year = 2026 THEN volume_act_ton END)  AS ky_nay,
       SUM(CASE WHEN year = 2025 THEN volume_act_ton END)  AS cung_ky
FROM vw_sales
WHERE year IN (2025, 2026)
  AND month <= (SELECT month FROM dim_calendar WHERE is_current_period = 1);

-- So kỳ liền trước (mức tháng)
SELECT cost_item_name_vi,
       SUM(CASE WHEN fiscal_period = '2026-08' THEN amount_vnd_bn END) AS ky_nay,
       SUM(CASE WHEN fiscal_period = '2026-07' THEN amount_vnd_bn END) AS ky_truoc
FROM vw_opex
WHERE fiscal_period IN ('2026-08', '2026-07')
GROUP BY cost_item_name_vi;

-- Tồn kho tại kỳ hiện tại (KHÔNG cộng theo thời gian)
SELECT product_name_vi, SUM(closing_stock_ton) AS ton_kho_tan
FROM vw_inventory
WHERE is_current_period = 1
GROUP BY product_name_vi
ORDER BY ton_kho_tan DESC;
```
