# DATA SCHEMA — TÔN ĐÔNG Á | Lĩnh vực Doanh thu
## Database: `tondonga_demo` (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 01/01/2024 – 30/09/2026 (33 tháng) | "Hiện tại" = cuối 09/2026
## Grain trung tâm: DÒNG HOÁ ĐƠN BÁN HÀNG (`fact_sales`) | 5 chỉ số × 5 chiều dữ liệu

---

## SƠ ĐỒ QUAN HỆ

```
fact_sales (sales_key PK)                      -- 1 dòng = 1 dòng hoá đơn
  ├── date_key      ──────────► dim_date.date_key           [D01 Thời gian]
  ├── org_key       ──────────► dim_org.org_key             [D02 Công ty / Nhà máy / Site]
  ├── product_key   ──────────► dim_product.product_key     [D03 Sản phẩm]
  ├── market_key    ──────────► dim_market.market_key       [D04 Thị trường / Khu vực]
  ├── customer_key  ──────────► dim_customer.customer_key   [D05 Kênh / Đại lý]
  └── currency      ──────────► m_currency.currency_code

dim_product.sku        ──────► m_product.sku
dim_product.uom_base   (giá trị) m_uom.uom_code
dim_customer.cust_code ──────► m_customer.cust_code
m_customer.channel_code ─────► m_channel.channel_code
dim_customer.channel_group (giá trị) = m_channel.channel_name
m_product.uom_base     ──────► m_uom.uom_code
dim_org (company, bu)  (giá trị) = m_org (company, bu)
dim_market.region      (giá trị, phần nội địa) = m_region.region

m_region (province PK)   -- bảng tham chiếu tỉnh → miền, KHÔNG nối với fact_sales

_meta_tables / _meta_columns / _meta_kpi / _meta_glossary   -- mô tả bảng, trường, chỉ số, thuật ngữ
```

**Quan hệ chính:** mô hình hình sao, `fact_sales` nối thẳng tới 5 bảng chiều bằng khoá số nguyên. Không có khoá kênh trong `fact_sales`: kênh bán hàng lấy từ `dim_customer.channel_group`. Các bảng `m_*` là danh mục chuẩn đứng sau bảng chiều; truy vấn phân tích chỉ cần `fact_sales` và 5 bảng `dim_*`.

---

## DIMENSION TABLES

### 1. dim_date (1.004 dòng)
Chiều Thời gian, mỗi dòng một ngày từ 01/01/2024 đến 30/09/2026.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `date_key` | INT PK | Mã ngày dạng YYYYMMDD | 20260930 |
| `date` | DATE | Ngày dương lịch | |
| `day` | TINYINT | Ngày trong tháng | |
| `month` | TINYINT | Tháng 1–12 | |
| `quarter` | TINYINT | Quý 1–4 | |
| `year` | SMALLINT | Năm | 2024, 2025, 2026 |
| `fiscal_period` | CHAR(7) | Kỳ tài chính theo tháng, dạng `YYYY-MM` | '2026-09'; năm tài chính trùng năm dương lịch |

Tháng gần nhất có dữ liệu: `fiscal_period = '2026-09'`. Năm 2026 chỉ có 9 tháng.

### 2. dim_org (11 dòng)
Chiều Đơn vị: nhóm → công ty → nhà máy/chi nhánh → phòng ban. Mỗi dòng là một phòng kinh doanh.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `org_key` | INT PK | Mã định danh đơn vị | |
| `group_name` | VARCHAR(50) | Nhóm công ty | 'Tôn Đông Á' |
| `company` | VARCHAR(100) | Công ty thành viên | 4 giá trị, xem dưới |
| `bu` | VARCHAR(100) | Nhà máy, chi nhánh | 7 giá trị, xem dưới |
| `department` | VARCHAR(100) | Phòng ban thực hiện giao dịch | |

| org_key | company | bu | department |
|---|---|---|---|
| 1 | Công ty Cổ phần Tôn Đông Á | Nhà máy Sóng Thần | Phòng Kinh doanh Nội địa |
| 2 | Công ty Cổ phần Tôn Đông Á | Nhà máy Sóng Thần | Phòng Kinh doanh Dự án |
| 3 | Công ty Cổ phần Tôn Đông Á | Nhà máy Thủ Dầu Một | Phòng Kinh doanh Nội địa |
| 4 | Công ty Cổ phần Tôn Đông Á | Nhà máy Thủ Dầu Một | Phòng Kinh doanh Dự án |
| 5 | Công ty Cổ phần Tôn Đông Á | Nhà máy Thủ Dầu Một | Phòng Kinh doanh Xuất khẩu |
| 6 | Công ty Cổ phần Tôn Đông Á | Nhà máy Ống hộp số 5 | Phòng Kinh doanh Nội địa |
| 7 | Công ty TNHH MTV Tôn Đông Á Bắc Ninh | Chi nhánh Bắc Ninh | Phòng Kinh doanh Miền Bắc |
| 8 | Công ty TNHH MTV Tôn Đông Á Bắc Ninh | Chi nhánh Bắc Ninh | Phòng Kinh doanh Dự án |
| 9 | Công ty TNHH MTV Tôn Đông Á Đà Nẵng | Nhà máy Ống thép Đà Nẵng | Phòng Kinh doanh Miền Trung |
| 10 | Công ty TNHH MTV Tôn Đông Á Đà Nẵng | Văn phòng đại diện Bình Định | Phòng Kinh doanh Nam Trung Bộ |
| 11 | Công ty TNHH MTV Tôn Đông Á Long An | Chi nhánh Long An | Phòng Kinh doanh Miền Tây |

- "Công ty mẹ" = `company = 'Công ty Cổ phần Tôn Đông Á'`. "Công ty thành viên", "CTTV", "công ty con" = ba công ty TNHH MTV.
- "Nhà máy", "site", "chi nhánh" = `bu`.
- Nhà máy Ống hộp số 5 chỉ có giao dịch từ 01/2026.
- Toàn bộ xuất khẩu do `org_key = 5` thực hiện.

### 3. dim_product (72 dòng)
Chiều Sản phẩm: dòng → nhóm → nhãn hàng → mã sản phẩm.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `product_key` | INT PK | Mã định danh sản phẩm | |
| `sku` | VARCHAR(30) UNIQUE | Mã sản phẩm theo danh mục chuẩn | 'TL-AZ100-045', 'TK-Z120-040' |
| `product_name` | VARCHAR(120) | Tên sản phẩm | 'Tôn lạnh WINALUZIN AZ100 0.45mm' |
| `cat_l1_line` | VARCHAR(50) | Cấp 1 — dòng sản phẩm | 5 giá trị |
| `cat_l2_group` | VARCHAR(60) | Cấp 2 — nhóm hàng theo độ mạ hoặc quy cách | 16 giá trị |
| `cat_l3_brand` | VARCHAR(30) | Cấp 3 — nhãn hàng | 'KING', 'WIN', 'SVIET', 'Tôn Đông Á' |
| `uom_base` | VARCHAR(10) | Đơn vị tính cơ sở | 'TAN' cho mọi sản phẩm |

| `cat_l1_line` | `cat_l2_group` | `cat_l3_brand` | Tiền tố `sku` |
|---|---|---|---|
| Tôn lạnh | Tôn lạnh AZ150 | KING | TL-AZ150- |
| Tôn lạnh | Tôn lạnh AZ100 | WIN | TL-AZ100- |
| Tôn lạnh | Tôn lạnh AZ75 | SVIET | TL-AZ075- |
| Tôn lạnh | Tôn lạnh AZ50 | Tôn Đông Á | TL-AZ050- |
| Tôn lạnh màu | Tôn lạnh màu AZ100 | KING | TM-AZ100- |
| Tôn lạnh màu | Tôn lạnh màu AZ50 | WIN | TM-AZ050- |
| Tôn lạnh màu | Tôn lạnh màu AZ30 | SVIET | TM-AZ030- |
| Tôn kẽm | Tôn kẽm Z80 | Tôn Đông Á | TK-Z080- |
| Tôn kẽm | Tôn kẽm Z120 | Tôn Đông Á | TK-Z120- |
| Tôn kẽm | Tôn kẽm Z180 | Tôn Đông Á | TK-Z180- |
| Tôn kẽm | Tôn kẽm Z275 | Tôn Đông Á | TK-Z275- |
| Thép cán nguội | Thép cán nguội cứng (full hard) | Tôn Đông Á | CR-FH- |
| Thép cán nguội | Thép cán nguội ủ mềm | Tôn Đông Á | CR-AN- |
| Ống hộp mạ kẽm | Hộp vuông mạ kẽm | Tôn Đông Á | OH-V- |
| Ống hộp mạ kẽm | Hộp chữ nhật mạ kẽm | Tôn Đông Á | OH-CN- |
| Ống hộp mạ kẽm | Ống tròn mạ kẽm | Tôn Đông Á | OH-T- |

- "Dòng sản phẩm", "ngành hàng" = `cat_l1_line`. "Nhóm hàng", "nhóm sản phẩm" = `cat_l2_group`. "Mã sản phẩm", "SKU" = `sku`.
- Hậu tố `sku` là độ dày (045 = 0,45 mm) hoặc quy cách ống hộp (40x40x1.4).
- Nhãn hàng 'Tôn Đông Á' là hàng không gắn nhãn KING/WIN/SVIET.

### 4. dim_market (22 dòng)
Chiều Thị trường: loại thị trường → quốc gia → vùng/khu vực.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `market_key` | INT PK | Mã định danh thị trường | |
| `market_type` | VARCHAR(20) | Loại thị trường | 'Nội địa', 'Xuất khẩu' |
| `country` | VARCHAR(50) | Quốc gia | 'Việt Nam' với nội địa |
| `region` | VARCHAR(30) | Vùng (nội địa) hoặc khu vực (xuất khẩu) | xem dưới |

| `market_type` | `region` | `country` |
|---|---|---|
| Nội địa | Miền Bắc, Miền Trung, Miền Nam | Việt Nam |
| Xuất khẩu | Đông Nam Á | Indonesia, Malaysia, Thái Lan, Campuchia, Lào, Philippines |
| Xuất khẩu | Châu Âu | Bỉ, Tây Ban Nha, Ý, Ba Lan |
| Xuất khẩu | Bắc Mỹ | Hoa Kỳ, Mexico, Canada |
| Xuất khẩu | Châu Đại Dương | Úc, New Zealand |
| Xuất khẩu | Đông Bắc Á | Hàn Quốc, Nhật Bản |
| Xuất khẩu | Trung Đông | UAE, Ả Rập Xê Út |

- Không có cấp tỉnh, thành trong chiều Thị trường.
- Khi trình bày "theo thị trường/khu vực" nên nhóm theo cặp (`market_type`, `region`): 3 miền nội địa và 6 khu vực xuất khẩu.

### 5. dim_customer (251 dòng)
Chiều Khách hàng, đồng thời mang chiều Kênh bán hàng.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `customer_key` | INT PK | Mã định danh khách hàng | |
| `cust_code` | VARCHAR(10) UNIQUE | Mã khách hàng theo danh mục chuẩn | 'KH00012' |
| `cust_name` | VARCHAR(150) | Tên khách hàng | |
| `channel_group` | VARCHAR(50) | Kênh bán hàng | 6 giá trị, xem dưới |
| `customer_type` | VARCHAR(30) | Loại khách hàng | xem dưới |
| `is_internal` | TINYINT(1) | 1 = khách hàng là công ty trong nhóm | 3 dòng có giá trị 1 |

| `channel_group` | `customer_type` | Số khách | `is_internal` |
|---|---|---|---|
| Đại lý cấp 1 | Đại lý | 110 | 0 |
| Nhà phân phối | Nhà phân phối | 24 | 0 |
| Dự án – Công trình | Khách hàng trực tiếp | 38 | 0 |
| Khách hàng công nghiệp | Khách hàng trực tiếp | 30 | 0 |
| Xuất khẩu | Nhà nhập khẩu | 46 | 0 |
| Nội bộ | Công ty thành viên | 3 | 1 |

- "Kênh" = `channel_group`. "Đại lý" khi hỏi xếp hạng = từng `cust_code` trong kênh 'Đại lý cấp 1' (mở rộng sang 'Nhà phân phối' nếu người hỏi nói chung "đại lý, nhà phân phối").
- Giá trị 'Dự án – Công trình' dùng dấu gạch ngang dài (–), có khoảng trắng hai bên.
- Ba khách nội bộ có `cust_name` trùng tên ba công ty thành viên.

---

## DANH MỤC CHUẨN (MASTER DATA)

Bảy bảng `m_*` là danh mục gốc. Bảng chiều đã mang đủ thuộc tính để phân tích, nên chỉ dùng `m_*` khi cần tra mã hoặc trả lời câu hỏi về danh mục.

### 6. m_product (72 dòng)
| Cột | Kiểu | Mô tả |
|---|---|---|
| `sku` | VARCHAR(30) PK | Mã sản phẩm |
| `product_name` | VARCHAR(120) | Tên sản phẩm |
| `cat_l1` | VARCHAR(50) | Ngành hàng (= `dim_product.cat_l1_line`) |
| `cat_l2` | VARCHAR(60) | Nhóm hàng (= `cat_l2_group`) |
| `cat_l3` | VARCHAR(30) | Nhãn hàng (= `cat_l3_brand`) |
| `uom_base` | VARCHAR(10) FK | Đơn vị tính cơ sở → `m_uom` |

### 7. m_customer (251 dòng)
| Cột | Kiểu | Mô tả |
|---|---|---|
| `cust_code` | VARCHAR(10) PK | Mã khách hàng |
| `cust_name` | VARCHAR(150) | Tên khách hàng |
| `channel_code` | VARCHAR(10) FK | Mã kênh → `m_channel` |
| `customer_type` | VARCHAR(30) | Loại khách hàng |

### 8. m_channel (6 dòng)
| Cột | Kiểu | Mô tả |
|---|---|---|
| `channel_code` | VARCHAR(10) PK | 'DL1', 'NPP', 'DA', 'CN', 'XK', 'NB' |
| `channel_name` | VARCHAR(50) UNIQUE | Tên kênh (= `dim_customer.channel_group`) |
| `is_internal` | TINYINT(1) | 1 với 'NB' (Nội bộ) |

### 9. m_org (7 dòng)
| Cột | Kiểu | Mô tả |
|---|---|---|
| `entity_code` | VARCHAR(10) PK | 'TDA-ST', 'TDA-TDM', 'TDA-NM5', 'TDA-BN', 'TDA-DN', 'TDA-BD', 'TDA-LA' |
| `company` | VARCHAR(100) | Công ty |
| `bu` | VARCHAR(100) | Nhà máy, chi nhánh |
| `group_name` | VARCHAR(50) | 'Tôn Đông Á' |

### 10. m_uom (3 dòng)
| Cột | Kiểu | Mô tả |
|---|---|---|
| `uom_code` | VARCHAR(10) PK | 'TAN', 'KG', 'MET' |
| `uom_name` | VARCHAR(50) | Tấn, Kilôgam, Mét |
| `to_base` | DECIMAL(12,6) NULL | Hệ số quy đổi về tấn: TAN = 1; KG = 0,001; MET = NULL (quy đổi theo quy cách từng mã) |

### 11. m_currency (3 dòng)
| Cột | Kiểu | Mô tả |
|---|---|---|
| `currency_code` | VARCHAR(3) PK | 'VND', 'USD', 'EUR' |
| `name` | VARCHAR(50) | Tên loại tiền tệ |
| `is_base` | TINYINT(1) | 1 với VND |

### 12. m_region (34 dòng)
| Cột | Kiểu | Mô tả |
|---|---|---|
| `province` | VARCHAR(50) PK | Tỉnh, thành phố (34 đơn vị) |
| `region` | VARCHAR(20) | 'Miền Bắc', 'Miền Trung', 'Miền Nam' |

Bảng tham chiếu. `fact_sales` và `dim_customer` không có trường tỉnh, nên không phân tích doanh thu theo tỉnh được.

---

## FACT TABLES

### 13. fact_sales ⭐ (FACT DUY NHẤT — 159.473 dòng)
Giao dịch bán hàng, 1 dòng = 1 dòng hoá đơn. Gồm cả bán ra ngoài và bán nội bộ từ công ty mẹ cho công ty thành viên.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `sales_key` | BIGINT PK | Mã định danh dòng giao dịch | |
| `date_key` | INT FK | Ngày phát sinh → `dim_date` | |
| `product_key` | INT FK | Sản phẩm → `dim_product` | |
| `customer_key` | INT FK | Khách hàng → `dim_customer` | |
| `market_key` | INT FK | Thị trường → `dim_market` | |
| `org_key` | INT FK | Đơn vị thực hiện giao dịch → `dim_org` | |
| `doc_no` | VARCHAR(30) | Số hoá đơn; một hoá đơn có thể có nhiều dòng | 'HD2609-ST-00012' |
| `gross_amount` | DECIMAL(18,0) | Doanh thu gộp trước giảm trừ | VND |
| `discount_amt` | DECIMAL(18,0) | Chiết khấu | VND |
| `returns_amt` | DECIMAL(18,0) | Hàng bán bị trả lại | VND |
| `net_revenue` | DECIMAL(18,0) | Doanh thu thuần = gộp − chiết khấu − trả lại (K01) | VND |
| `cogs_amount` | DECIMAL(18,0) | Giá vốn hàng bán của dòng giao dịch | VND |
| `quantity_base` | DECIMAL(14,3) | Sản lượng tiêu thụ theo đơn vị cơ sở (K02) | tấn |
| `currency` | VARCHAR(3) FK | Loại tiền của chứng từ gốc → `m_currency` | 'VND', 'USD', 'EUR' |
| `src_system` | VARCHAR(20) | Hệ thống nguồn của dòng dữ liệu | 'ERP_TDA', 'ERP_BACNINH', 'ERP_DANANG', 'ERP_LONGAN' |

⚠️ **Doanh thu luôn dùng `net_revenue`.** Không tự tính lại từ `gross_amount`; ba trường gộp, chiết khấu, trả lại dùng để giải thích.

⚠️ **Số toàn nhóm phải lọc `dim_customer.is_internal = 0`.** Không lọc thì doanh thu bị cộng thêm phần công ty mẹ bán cho công ty thành viên (khoảng 18% với 9 tháng 2026).

⚠️ **Mọi trường giá trị đã là VND.** `currency` chỉ cho biết chứng từ gốc lập bằng tiền gì; không nhân tỷ giá.

⚠️ **ASP và biên gộp tính bằng tỷ số của hai tổng** trên cùng bộ lọc, không lấy trung bình của từng dòng.

Giá vốn của công ty thành viên với hàng mua từ công ty mẹ là giá mua nội bộ, nên biên gộp của công ty thành viên thấp hơn công ty mẹ trên cùng dòng sản phẩm.

---

## SQL TEMPLATES

Quy ước chung: kỳ hiện tại 09/2026; lũy kế = tháng 1–9; so cùng kỳ = cùng các tháng của năm trước; mọi câu đều nối `dim_customer` để lọc `is_internal = 0`.

### T1. Một chỉ số theo ba kỳ: tháng gần nhất, tháng trước, cùng kỳ (UAT 1, 9, 18)
```sql
SELECT d.fiscal_period AS ky,
       ROUND(SUM(f.net_revenue) / 1e9, 1) AS doanh_thu_thuan_ty,
       ROUND(SUM(f.quantity_base), 0) AS san_luong_tan,
       ROUND(SUM(f.net_revenue) / NULLIF(SUM(f.quantity_base), 0) / 1e6, 2) AS asp_trieu_tan
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_market m ON m.market_key = f.market_key
JOIN dim_org o ON o.org_key = f.org_key
WHERE c.is_internal = 0 AND ((d.year = 2026 AND d.month IN (8, 9)) OR (d.year = 2025 AND d.month = 9))
GROUP BY d.fiscal_period ORDER BY d.fiscal_period;
```
Thêm `ROUND(100.0 * SUM(f.net_revenue - f.cogs_amount) / NULLIF(SUM(f.net_revenue), 0), 2)` để ra biên gộp ba kỳ.

### T2. Lũy kế từ đầu năm, so cùng kỳ (UAT 2)
```sql
SELECT d.year AS nam,
       ROUND(SUM(f.net_revenue) / 1e9, 1) AS dt_luy_ke_9t_ty,
       ROUND(SUM(f.quantity_base), 0) AS san_luong_tan
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_market m ON m.market_key = f.market_key
JOIN dim_org o ON o.org_key = f.org_key
WHERE c.is_internal = 0 AND d.month BETWEEN 1 AND 9
GROUP BY d.year ORDER BY d.year;
```

### T3. Doanh thu hai kỳ theo một chiều: giá trị, chênh lệch, % tăng trưởng, tỷ trọng (UAT 3, 4, 5, 6, 13, 14, 15)
```sql
SELECT p.cat_l1_line AS dong_san_pham,
       ROUND(SUM(CASE WHEN d.year = 2026 THEN f.net_revenue ELSE 0 END) / 1e9, 1) AS dt_9t2026_ty,
       ROUND(SUM(CASE WHEN d.year = 2025 THEN f.net_revenue ELSE 0 END) / 1e9, 1) AS dt_9t2025_ty,
       ROUND(SUM(CASE WHEN d.year = 2026 THEN f.net_revenue ELSE -f.net_revenue END) / 1e9, 1) AS chenh_lech_ty,
       ROUND(100.0 * SUM(CASE WHEN d.year = 2026 THEN f.net_revenue ELSE -f.net_revenue END)
             / NULLIF(SUM(CASE WHEN d.year = 2025 THEN f.net_revenue ELSE 0 END), 0), 1) AS tang_truong_pct,
       ROUND(100.0 * SUM(CASE WHEN d.year = 2026 THEN f.net_revenue ELSE 0 END)
             / SUM(SUM(CASE WHEN d.year = 2026 THEN f.net_revenue ELSE 0 END)) OVER (), 1) AS ty_trong_2026_pct,
       ROUND(100.0 * SUM(CASE WHEN d.year = 2025 THEN f.net_revenue ELSE 0 END)
             / SUM(SUM(CASE WHEN d.year = 2025 THEN f.net_revenue ELSE 0 END)) OVER (), 1) AS ty_trong_2025_pct
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_market m ON m.market_key = f.market_key
JOIN dim_org o ON o.org_key = f.org_key
WHERE c.is_internal = 0 AND d.year IN (2025, 2026) AND d.month BETWEEN 1 AND 9
GROUP BY p.cat_l1_line
ORDER BY dt_9t2026_ty DESC;
```
Đổi chiều bằng cách thay biểu thức nhóm:
- Thị trường: `CONCAT(m.market_type, ' - ', m.region)`
- Kênh: `c.channel_group`
- Công ty / nhà máy: `CONCAT(o.company, ' | ', o.bu)` hoặc `o.company`
- Nhóm hàng, mã sản phẩm: `p.cat_l2_group`, `p.sku`

Xếp theo `chenh_lech_ty` để tìm nơi đóng góp âm/dương lớn nhất; theo `tang_truong_pct DESC` để tìm nơi tăng nhanh nhất. Kỳ gốc bằng 0 thì `tang_truong_pct` là NULL.

### T4. ASP hai kỳ theo một chiều (UAT 10, 11)
```sql
SELECT CONCAT(m.market_type, ' - ', m.region) AS thi_truong,
       ROUND(SUM(CASE WHEN d.year = 2026 THEN f.net_revenue ELSE 0 END) / NULLIF(SUM(CASE WHEN d.year = 2026 THEN f.quantity_base ELSE 0 END), 0) / 1e6, 2) AS asp_9t2026_trieu,
       ROUND(SUM(CASE WHEN d.year = 2025 THEN f.net_revenue ELSE 0 END) / NULLIF(SUM(CASE WHEN d.year = 2025 THEN f.quantity_base ELSE 0 END), 0) / 1e6, 2) AS asp_9t2025_trieu,
       ROUND(100.0 * (SUM(CASE WHEN d.year = 2026 THEN f.net_revenue ELSE 0 END) / NULLIF(SUM(CASE WHEN d.year = 2026 THEN f.quantity_base ELSE 0 END), 0))
             / NULLIF(SUM(CASE WHEN d.year = 2025 THEN f.net_revenue ELSE 0 END) / NULLIF(SUM(CASE WHEN d.year = 2025 THEN f.quantity_base ELSE 0 END), 0), 0) - 100, 1) AS thay_doi_pct,
       ROUND(SUM(CASE WHEN d.year = 2026 THEN f.net_revenue ELSE 0 END) / 1e9, 1) AS dt_9t2026_ty,
       ROUND(SUM(CASE WHEN d.year = 2026 THEN f.quantity_base ELSE 0 END), 0) AS sl_9t2026_tan
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_market m ON m.market_key = f.market_key
JOIN dim_org o ON o.org_key = f.org_key
WHERE c.is_internal = 0 AND d.year IN (2025, 2026) AND d.month BETWEEN 1 AND 9
GROUP BY CONCAT(m.market_type, ' - ', m.region)
ORDER BY thay_doi_pct;
```

### T5. ASP từng kênh so với bình quân toàn hệ thống, kèm tỷ lệ chiết khấu (UAT 12)
```sql
SELECT c.channel_group AS kenh,
       ROUND(SUM(f.net_revenue) / NULLIF(SUM(f.quantity_base), 0) / 1e6, 2) AS asp_trieu_tan,
       ROUND(SUM(SUM(f.net_revenue)) OVER () / SUM(SUM(f.quantity_base)) OVER () / 1e6, 2) AS asp_binh_quan_chung,
       ROUND((SUM(f.net_revenue) / NULLIF(SUM(f.quantity_base), 0) - SUM(SUM(f.net_revenue)) OVER () / SUM(SUM(f.quantity_base)) OVER ()) / 1e6, 2) AS chenh_lech,
       ROUND(100.0 * SUM(f.discount_amt) / NULLIF(SUM(f.gross_amount), 0), 2) AS ty_le_chiet_khau_pct
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_market m ON m.market_key = f.market_key
JOIN dim_org o ON o.org_key = f.org_key
WHERE c.is_internal = 0 AND d.year = 2026 AND d.month BETWEEN 1 AND 9
GROUP BY c.channel_group ORDER BY asp_trieu_tan;
```
Cùng cách làm cho từng đại lý: nhóm theo `c.cust_code, c.cust_name`, lọc `c.channel_group = 'Đại lý cấp 1'` ở truy vấn ngoài để bình quân chung vẫn tính trên toàn hệ thống.

### T6. Xếp hạng đại lý và tỷ trọng lũy kế của nhóm dẫn đầu (UAT 5)
```sql
SELECT x.xep_hang, x.cust_code, x.cust_name, ROUND(x.dt_ty, 1) AS dt_ty,
       ROUND(100.0 * x.dt_ty / x.tong_ty, 1) AS ty_trong_pct,
       ROUND(100.0 * x.luy_ke_ty / x.tong_ty, 1) AS ty_trong_luy_ke_pct
FROM (
  SELECT c.cust_code, c.cust_name, SUM(f.net_revenue) / 1e9 AS dt_ty,
         RANK() OVER (ORDER BY SUM(f.net_revenue) DESC) AS xep_hang,
         SUM(SUM(f.net_revenue)) OVER (ORDER BY SUM(f.net_revenue) DESC) / 1e9 AS luy_ke_ty,
         SUM(SUM(f.net_revenue)) OVER () / 1e9 AS tong_ty
  FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_market m ON m.market_key = f.market_key
JOIN dim_org o ON o.org_key = f.org_key
WHERE c.is_internal = 0 AND d.year = 2026 AND d.month BETWEEN 1 AND 9 AND c.channel_group = 'Đại lý cấp 1'
  GROUP BY c.cust_code, c.cust_name
) x
WHERE x.xep_hang <= 10 ORDER BY x.xep_hang;
```

### T7. Sản lượng theo tháng, 12 tháng gần nhất (UAT 7)
```sql
SELECT d.fiscal_period AS thang, ROUND(SUM(f.quantity_base), 0) AS san_luong_tan
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_market m ON m.market_key = f.market_key
JOIN dim_org o ON o.org_key = f.org_key
WHERE c.is_internal = 0 AND d.date_key BETWEEN 20251001 AND 20260930
GROUP BY d.fiscal_period ORDER BY d.fiscal_period;
```

### T8. Biên lợi nhuận gộp hai kỳ theo một chiều, dùng để truy dòng → nhóm → mã (UAT 16, 17)
```sql
SELECT p.cat_l2_group AS nhom_hang,
       ROUND(100.0 * SUM(CASE WHEN d.year = 2026 THEN f.net_revenue - f.cogs_amount ELSE 0 END) / NULLIF(SUM(CASE WHEN d.year = 2026 THEN f.net_revenue ELSE 0 END), 0), 2) AS bien_gop_9t2026_pct,
       ROUND(100.0 * SUM(CASE WHEN d.year = 2025 THEN f.net_revenue - f.cogs_amount ELSE 0 END) / NULLIF(SUM(CASE WHEN d.year = 2025 THEN f.net_revenue ELSE 0 END), 0), 2) AS bien_gop_9t2025_pct,
       ROUND(100.0 * SUM(CASE WHEN d.year = 2026 THEN f.net_revenue - f.cogs_amount ELSE 0 END) / NULLIF(SUM(CASE WHEN d.year = 2026 THEN f.net_revenue ELSE 0 END), 0)
           - 100.0 * SUM(CASE WHEN d.year = 2025 THEN f.net_revenue - f.cogs_amount ELSE 0 END) / NULLIF(SUM(CASE WHEN d.year = 2025 THEN f.net_revenue ELSE 0 END), 0), 2) AS thay_doi_diem,
       ROUND(SUM(CASE WHEN d.year = 2026 THEN f.net_revenue ELSE 0 END) / 1e9, 1) AS dt_9t2026_ty,
       ROUND(SUM(CASE WHEN d.year = 2026 THEN f.net_revenue - f.cogs_amount ELSE 0 END) / 1e9, 1) AS ln_gop_9t2026_ty,
       ROUND(SUM(CASE WHEN d.year = 2025 THEN f.net_revenue - f.cogs_amount ELSE 0 END) / 1e9, 1) AS ln_gop_9t2025_ty
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_market m ON m.market_key = f.market_key
JOIN dim_org o ON o.org_key = f.org_key
WHERE c.is_internal = 0 AND d.year IN (2025, 2026) AND d.month BETWEEN 1 AND 9 AND p.cat_l1_line = 'Tôn kẽm'
GROUP BY p.cat_l2_group
ORDER BY thay_doi_diem;
```
Truy xuống từng cấp: bỏ điều kiện dòng để xem theo `p.cat_l1_line`; thay bằng `p.cat_l2_group = '...'` và nhóm theo `p.sku` để xem theo mã; thêm `m.region` để xem một mã theo thị trường.

### T9. Phân rã thay đổi biên gộp theo dòng sản phẩm (UAT 18)
Phần biên gộp của một dòng = lợi nhuận gộp của dòng / doanh thu toàn bộ của kỳ. Tổng các phần bằng biên gộp chung, nên chênh lệch từng phần giữa hai kỳ là mức đóng góp của dòng đó vào thay đổi biên gộp.
```sql
WITH k AS (
  SELECT p.cat_l1_line AS dong, d.fiscal_period AS ky,
         SUM(f.net_revenue) AS dt, SUM(f.net_revenue - f.cogs_amount) AS lng
  FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_market m ON m.market_key = f.market_key
JOIN dim_org o ON o.org_key = f.org_key
WHERE c.is_internal = 0 AND ((d.year = 2026 AND d.month IN (8, 9)) OR (d.year = 2025 AND d.month = 9))
  GROUP BY p.cat_l1_line, d.fiscal_period
), t AS (
  SELECT ky, SUM(dt) AS tong FROM k GROUP BY ky
)
SELECT k.dong AS dong_san_pham,
       ROUND(SUM(CASE WHEN k.ky = '2026-09' THEN 100.0 * k.lng / t.tong ELSE 0 END), 2) AS phan_bien_gop_t9_2026,
       ROUND(SUM(CASE WHEN k.ky = '2026-08' THEN 100.0 * k.lng / t.tong ELSE 0 END), 2) AS phan_bien_gop_t8_2026,
       ROUND(SUM(CASE WHEN k.ky = '2025-09' THEN 100.0 * k.lng / t.tong ELSE 0 END), 2) AS phan_bien_gop_t9_2025,
       ROUND(SUM(CASE WHEN k.ky = '2026-09' THEN 100.0 * k.lng / t.tong WHEN k.ky = '2026-08' THEN -100.0 * k.lng / t.tong ELSE 0 END), 2) AS dong_gop_so_thang_truoc_diem,
       ROUND(SUM(CASE WHEN k.ky = '2026-09' THEN 100.0 * k.lng / t.tong WHEN k.ky = '2025-09' THEN -100.0 * k.lng / t.tong ELSE 0 END), 2) AS dong_gop_so_cung_ky_diem
FROM k JOIN t ON t.ky = k.ky
GROUP BY k.dong ORDER BY dong_gop_so_cung_ky_diem;
```

### T10. Doanh thu toàn nhóm: cộng gộp, nội bộ, sau loại trừ (câu hỏi theo công ty thành viên)
```sql
SELECT
       ROUND(SUM(f.net_revenue) / 1e9, 1) AS dt_cong_gop_ty,
       ROUND(SUM(CASE WHEN c.is_internal = 1 THEN f.net_revenue ELSE 0 END) / 1e9, 1) AS dt_noi_bo_ty,
       ROUND(SUM(CASE WHEN c.is_internal = 0 THEN f.net_revenue ELSE 0 END) / 1e9, 1) AS dt_sau_loai_tru_ty,
       ROUND(100.0 * SUM(CASE WHEN c.is_internal = 1 THEN f.net_revenue ELSE 0 END) / SUM(f.net_revenue), 1) AS ty_trong_noi_bo_pct
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_customer c ON c.customer_key = f.customer_key
WHERE d.year = 2026 AND d.month BETWEEN 1 AND 9;
```

---

## JOIN WARNINGS

1. **`fact_sales` ↔ `dim_customer` — giao dịch nội bộ.** Mọi câu hỏi về số toàn nhóm, so sánh giữa các công ty, theo sản phẩm, thị trường, kênh đều lọc `c.is_internal = 0`. Chỉ bỏ lọc khi người hỏi nói rõ muốn xem doanh thu nội bộ hoặc doanh thu cộng gộp. Lọc `c.channel_group <> 'Nội bộ'` cho kết quả tương đương.
2. **Kênh không nằm trong fact.** Muốn phân tích theo kênh phải nối `dim_customer`. Không có bảng `dim_channel`; `m_channel` chỉ là danh mục.
3. **`m_region` không nối được với `fact_sales`.** Vùng miền nội địa lấy từ `dim_market.region`. Câu hỏi theo tỉnh: trả lời là dữ liệu không có cấp tỉnh.
4. **`dim_market`: lọc nội địa bằng `market_type = 'Nội địa'`**, không bằng `country`. Nhóm theo `region` đơn lẻ vẫn an toàn vì tên vùng nội địa và khu vực xuất khẩu không trùng nhau.
5. **`dim_org` có nhiều dòng cho một công ty.** Nhóm theo `o.company` hoặc `o.bu`, không nhóm theo `org_key` khi người hỏi nói "công ty" hay "nhà máy". Nối `dim_org` với `m_org` qua (`company`, `bu`) sẽ không nhân dòng, nhưng không cần cho phân tích.
6. **`dim_product` ↔ `m_product`, `dim_customer` ↔ `m_customer`: quan hệ 1–1.** Nối thêm không sai nhưng thừa.
7. **`doc_no` không duy nhất.** Một hoá đơn có nhiều dòng; đếm hoá đơn dùng `COUNT(DISTINCT doc_no)`.
8. **So sánh kỳ:** năm 2026 mới có 9 tháng. So "cả năm" 2026 với 2025 phải giới hạn cùng số tháng (`d.month BETWEEN 1 AND 9`) hoặc nói rõ 2026 chưa đủ năm.
9. **Đơn vị không có cùng kỳ.** Nhà máy Ống hộp số 5 không có số liệu trước 2026; Hoa Kỳ và Mexico không có số liệu từ 10/2024. Dùng `NULLIF(..., 0)` cho mẫu số và trình bày là "không có kỳ so sánh".
10. **Chia số nguyên.** Các trường giá trị là DECIMAL(18,0); nhân `100.0` hoặc chia `1e9` trước khi làm tròn để giữ phần thập phân.
11. **Tên cột trùng từ khoá.** `date`, `day`, `month`, `quarter`, `year` trong `dim_date` nên viết kèm bí danh bảng (`d.year`) hoặc bọc backtick.

---

## ĐƠN VỊ TIỀN TỆ & ĐO LƯỜNG

| Bảng | Cột | Đơn vị |
|---|---|---|
| fact_sales | gross_amount, discount_amt, returns_amt, net_revenue, cogs_amount | VND |
| fact_sales | quantity_base | tấn |
| (tính) | ASP = net_revenue / quantity_base | VND/tấn, trình bày triệu VND/tấn |
| (tính) | Biên lợi nhuận gộp, tăng trưởng, tỷ trọng | % |

Cách trình bày:
- Từ 1.000 tỷ trở lên: "10.100 tỷ". Từ 1 đến dưới 1.000 tỷ: "334,2 tỷ". Dưới 1 tỷ: "850 triệu".
- Sản lượng: tấn, không lấy số lẻ ("58.884 tấn").
- ASP: triệu VND/tấn, hai chữ số thập phân ("19,53 triệu/tấn").
- Phần trăm: một chữ số thập phân; biên gộp hai chữ số thập phân; chênh lệch giữa hai tỷ lệ gọi là "điểm %".
- Dấu phân cách theo kiểu Việt Nam: chấm cho hàng nghìn, phẩy cho thập phân.

---

## MỐC SANITY CHECK

Dùng để phát hiện truy vấn bị nhân dòng hoặc quên lọc nội bộ. Số ngoài nhóm (`is_internal = 0`):

| Kỳ | Doanh thu thuần | Sản lượng | ASP | Biên gộp |
|---|---|---|---|---|
| 2024 (12 tháng) | 19.100 tỷ | 849.407 tấn | 22,49 triệu/tấn | 8,54% |
| 2025 (12 tháng) | 15.000 tỷ | 746.207 tấn | 20,10 triệu/tấn | 7,46% |
| 2026 (9 tháng) | 10.100 tỷ | 519.922 tấn | 19,43 triệu/tấn | 6,56% |

- Doanh thu một tháng nằm trong khoảng 880–1.860 tỷ; sản lượng một tháng 45.000–82.000 tấn.
- ASP theo dòng sản phẩm nằm trong khoảng 16–27 triệu/tấn; biên gộp theo dòng trong khoảng 3–12%.
- Doanh thu nội bộ 9 tháng 2026: 2.285,9 tỷ. Nếu tổng 9 tháng 2026 ra 12.385,9 tỷ là đã quên lọc `is_internal = 0`.
- Tổng theo bất kỳ chiều nào (dòng, thị trường, kênh, công ty) phải bằng tổng chung của cùng kỳ.
- `net_revenue = gross_amount - discount_amt - returns_amt` đúng trên mọi dòng.
