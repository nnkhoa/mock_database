-- ============================================================
-- 02_metadata.sql
-- AP Saigon Petro — Metadata for AI engine understanding
-- ============================================================
USE lubricants_demo;

-- ============================================================
-- _meta_tables
-- ============================================================

INSERT INTO _meta_tables (table_name, description_vi, description_en, business_context) VALUES
('regions', 'Khu vuc dia ly phan cap: Mien > Vung > Tinh. Bao phu 63 tinh thanh Viet Nam.',
 'Geographic regions with hierarchy: Macro-region > Region > Province. Covers all 63 provinces of Vietnam.',
 'AP Saigon Petro sells nationwide. Key markets: Dong Nam Bo (HCM area), DBSCL (Mekong Delta), and Tay Nguyen. The population_index column helps weight regional demand — HCM=1.0, smaller provinces ~0.1.'),

('channels', 'Kenh ban hang B2B va B2C cua AP Saigon Petro.',
 'Sales channels for both B2B and B2C distribution.',
 'B2B channels include industrial/fleet accounts, workshops, authorized garages. B2C includes retail shops, gas stations, online. Each channel has a typical_margin_pct reflecting standard gross margin for that channel type.'),

('distributors', 'Nha phan phoi (NPP) — khoang 100 NPP phan cap Tong dai ly, Dai ly cap 1, Dai ly cap 2.',
 'Distributors (NPP) — approximately 100 distributors tiered as Master Distributor, Tier-1 Dealer, Tier-2 Dealer.',
 'AP Saigon Petro uses a tiered distribution model. Tong dai ly (Master Distributors) handle large volumes and may sub-distribute. Credit limits and payment terms vary by tier. The status field tracks active vs inactive NPPs. Use onboarded_date to analyze distributor growth over time.'),

('products', 'Danh muc san pham dau nhon — khoang 200 SKU thuoc 4 thuong hieu: Saigon Petro, AP OIL, Sino, Polaris.',
 'Lubricant product catalog — approximately 200 active SKUs across 4 brands: Saigon Petro, AP OIL, Sino, Polaris.',
 'Product groups include: Dau xe may (motorcycle oil), Dau o to (car oil), Dau xe tai (truck/diesel oil), Dau hang hai (marine oil), Dau cong nghiep (industrial oil), Mo boi tron (grease), Dau nong nghiep (agricultural oil). Product types: mineral, semi_synthetic, full_synthetic, grease. Viscosity grades follow SAE standards (10W-40, 15W-40, etc.). The popularity_weight reflects Pareto distribution — top 20% SKUs have higher weight. unit_price_vnd is suggested retail price; cost_per_liter_vnd is base manufacturing cost.'),

('suppliers', 'Nha cung cap dau goc (base oil) va phu gia (additive) cho nha may Cat Lai.',
 'Suppliers of base oils (Group I/II/III/IV) and additives for the Cat Lai factory.',
 'Base oil is sourced from both domestic (PVN/BSR) and international suppliers (Singapore, Korea, Thailand). Material types: base_oil_group_I (cheapest, mineral), base_oil_group_II, base_oil_group_III (synthetic), base_oil_group_IV (PAO, full synthetic), additive, naphthenic_base_oil. Lead times range 7-45 days depending on origin.'),

('production_lines', 'Day chuyen san xuat nha may Cat Lai — 5 day chuyen.',
 'Production lines at the Cat Lai factory — 5 lines.',
 'Line types: blending (pha tron dau goc + phu gia), filling_small (dong goi chai nho 0.8-4L), filling_large (dong goi can 18-200L), filling_drum (dong phuy 200L), grease (day chuyen mo boi tron rieng). Target yield rate is typically 97.5%. Max capacity per month varies by line — total factory capacity approximately 5,000-8,000 tons/month.'),

('sales_orders', 'Don hang ban cho NPP — moi dong la 1 line item (1 san pham). Du lieu 18 thang tu 10/2024 den 03/2026.',
 'Sales orders to distributors — each row is one line item (single product). 18 months of data from Oct 2024 to Mar 2026.',
 'Core revenue table. Revenue = quantity_liters x unit_price_vnd. COGS is broken into 3 components: material (NVL), production (SX), transport (van chuyen). Gross profit and margin are pre-calculated. Payment tracking: invoice_date, due_date, payment_status (pending/partial/paid/overdue). JOIN with distributors for regional analysis, with products for brand/category analysis.'),

('payments', 'Thanh toan tu NPP — theo doi DSO va no qua han.',
 'Payments from distributors — tracks DSO (Days Sales Outstanding) and overdue receivables.',
 'Each payment links to a sales_order. Multiple payments can exist per order (partial payments). days_from_invoice measures collection speed. is_overdue flags late payments. Payment methods: Chuyen khoan (bank transfer), Tien mat (cash), LC (letter of credit). JOIN with sales_orders to reconcile outstanding balances.'),

('production_batches', 'Batch san xuat nha may Cat Lai — theo doi yield rate va chi phi san xuat tren moi lit.',
 'Production batches at Cat Lai factory — tracks yield rate and production cost per liter.',
 'Each batch produces one primary product on one production line. yield_rate = output/input — below 95% signals quality issues. Costs split into material (NVL), labor (nhan cong), overhead (dien, nuoc, khau hao). cost_per_liter_vnd = total_production_cost / output_quantity — key metric for monitoring production efficiency.'),

('raw_material_costs', 'Gia nguyen vat lieu (dau goc, phu gia) theo thang — theo doi xu huong bien dong gia.',
 'Monthly raw material prices (base oils, additives) — tracks price trends and volatility.',
 'month_date is always the 1st of each month. Price per liter varies significantly by material type: Group I cheapest, Group IV most expensive. Volume purchased shows procurement patterns. Total cost = price x volume. JOIN with suppliers for country-of-origin analysis. Price spikes directly impact COGS in sales_orders.');

-- ============================================================
-- _meta_columns
-- ============================================================

-- ---------- regions ----------
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
('regions', 'region_id', 'VARCHAR(10)', 'Ma khu vuc', 'Region ID (primary key)', NULL, 'RG-01, RG-02, RG-10'),
('regions', 'region_name', 'VARCHAR(100)', 'Ten vung', 'Region name', NULL, 'Dong Nam Bo, DBSCL, Tay Nguyen, Dong bang song Hong'),
('regions', 'macro_region', 'VARCHAR(50)', 'Mien (phan cap cao nhat)', 'Macro-region (top-level hierarchy)', NULL, 'Mien Nam, Mien Trung, Mien Bac'),
('regions', 'province', 'VARCHAR(100)', 'Tinh/thanh pho', 'Province or city', NULL, 'TP.HCM, Binh Duong, Can Tho, Da Nang'),
('regions', 'population_index', 'DECIMAL(5,2)', 'Chi so dan so tuong doi (HCM=1.0)', 'Relative population index (HCM=1.0)', NULL, '1.00, 0.45, 0.12');

-- ---------- channels ----------
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
('channels', 'channel_id', 'VARCHAR(10)', 'Ma kenh ban hang', 'Channel ID (primary key)', NULL, 'CH-01, CH-02'),
('channels', 'channel_name', 'VARCHAR(100)', 'Ten kenh ban hang', 'Channel name', NULL, 'Dai ly xe may, Gara o to, Cong nghiep, Tram xang, Online'),
('channels', 'channel_type', 'VARCHAR(20)', 'Loai kenh: B2B hoac B2C', 'Channel type: B2B or B2C', NULL, 'B2B, B2C'),
('channels', 'typical_margin_pct', 'DECIMAL(5,2)', 'Bien loi nhuan gop dien hinh cua kenh, %', 'Typical gross margin for this channel, %', '%', '18.50, 25.00, 15.00');

-- ---------- distributors ----------
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
('distributors', 'distributor_id', 'VARCHAR(10)', 'Ma nha phan phoi', 'Distributor ID (primary key)', NULL, 'NPP-001, NPP-050, NPP-100'),
('distributors', 'distributor_name', 'VARCHAR(200)', 'Ten nha phan phoi', 'Distributor name', NULL, 'TNHH TM Thanh Phat, DNTN Minh Tuan'),
('distributors', 'region_id', 'VARCHAR(10)', 'Khoa ngoai toi bang regions', 'Foreign key to regions table', NULL, 'RG-01, RG-05'),
('distributors', 'channel_id', 'VARCHAR(10)', 'Khoa ngoai toi bang channels (kenh chinh)', 'Foreign key to channels (primary channel)', NULL, 'CH-01, CH-03'),
('distributors', 'tier', 'VARCHAR(20)', 'Phan cap NPP', 'Distributor tier', NULL, 'Tong dai ly, Dai ly cap 1, Dai ly cap 2'),
('distributors', 'city', 'VARCHAR(100)', 'Thanh pho/tinh cu the', 'Specific city or province', NULL, 'TP.HCM, Binh Duong, Can Tho'),
('distributors', 'credit_limit_vnd', 'BIGINT', 'Han muc tin dung', 'Credit limit', 'VND', '500000000, 2000000000, 5000000000'),
('distributors', 'payment_term_days', 'INT', 'Ky han thanh toan mac dinh', 'Default payment terms', 'ngay', '15, 30, 45'),
('distributors', 'status', 'VARCHAR(20)', 'Trang thai hoat dong', 'Active status', NULL, 'active, inactive'),
('distributors', 'onboarded_date', 'DATE', 'Ngay bat dau hop tac', 'Date distributor started partnership', NULL, '2020-03-15, 2023-01-01');

-- ---------- products ----------
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
('products', 'product_id', 'VARCHAR(15)', 'Ma san pham', 'Product ID (primary key)', NULL, 'PRD-001, PRD-100, PRD-200'),
('products', 'product_name', 'VARCHAR(200)', 'Ten san pham day du', 'Full product name', NULL, 'Saigon Petro Super 4T 10W-40 1L, AP OIL Diesel CI-4 15W-40 18L'),
('products', 'brand', 'VARCHAR(50)', 'Thuong hieu', 'Brand name', NULL, 'Saigon Petro, AP OIL, Sino, Polaris'),
('products', 'product_group', 'VARCHAR(100)', 'Nhom san pham', 'Product group', NULL, 'Dau xe may, Dau o to, Dau xe tai, Dau hang hai, Dau cong nghiep, Mo boi tron, Dau nong nghiep'),
('products', 'product_category', 'VARCHAR(100)', 'Danh muc chi tiet', 'Detailed product category', NULL, 'Dau 4T, Dau 2T, Dau tay ga, Dau diesel, Dau thuy luc'),
('products', 'product_type', 'VARCHAR(30)', 'Loai dau goc', 'Base oil type', NULL, 'mineral, semi_synthetic, full_synthetic, grease'),
('products', 'viscosity_grade', 'VARCHAR(30)', 'Cap do nhot SAE', 'SAE viscosity grade', NULL, '10W-40, 15W-40, 20W-50, 5W-30, SAE 40'),
('products', 'volume_ml', 'INT', 'Dung tich dong goi', 'Package volume', 'ml', '800, 1000, 4000, 18000, 200000'),
('products', 'unit_price_vnd', 'BIGINT', 'Gia ban le de xuat moi lit', 'Suggested retail price per liter', 'VND/lit', '45000, 78000, 120000, 250000'),
('products', 'cost_per_liter_vnd', 'BIGINT', 'Gia von chuan moi lit (chua tinh van chuyen)', 'Standard cost per liter (excl. transport)', 'VND/lit', '28000, 52000, 85000, 180000'),
('products', 'popularity_weight', 'DECIMAL(5,3)', 'Trong so ban chay — top 20% SKU co weight cao', 'Sales popularity weight — Pareto: top 20% SKUs have higher weight', NULL, '0.200, 1.000, 2.500, 5.000'),
('products', 'api_grade', 'VARCHAR(20)', 'Tieu chuan API', 'API performance grade', NULL, 'SN, SL, CI-4, CH-4, GL-5'),
('products', 'status', 'VARCHAR(20)', 'Trang thai san pham', 'Product status', NULL, 'active, discontinued');

-- ---------- suppliers ----------
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
('suppliers', 'supplier_id', 'VARCHAR(10)', 'Ma nha cung cap', 'Supplier ID (primary key)', NULL, 'SUP-01, SUP-05, SUP-10'),
('suppliers', 'supplier_name', 'VARCHAR(200)', 'Ten nha cung cap', 'Supplier name', NULL, 'SK Lubricants, Shell Chemicals, BSR Binh Son'),
('suppliers', 'country', 'VARCHAR(50)', 'Quoc gia', 'Country of origin', NULL, 'Viet Nam, Singapore, Han Quoc, Thai Lan'),
('suppliers', 'material_type', 'VARCHAR(50)', 'Loai nguyen vat lieu cung cap', 'Type of raw material supplied', NULL, 'base_oil_group_I, base_oil_group_II, base_oil_group_III, base_oil_group_IV, additive, naphthenic_base_oil'),
('suppliers', 'lead_time_days', 'INT', 'Thoi gian giao hang', 'Delivery lead time', 'ngay', '7, 14, 30, 45');

-- ---------- production_lines ----------
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
('production_lines', 'line_id', 'VARCHAR(10)', 'Ma day chuyen san xuat', 'Production line ID (primary key)', NULL, 'LN-01, LN-02, LN-05'),
('production_lines', 'line_name', 'VARCHAR(100)', 'Ten day chuyen', 'Production line name', NULL, 'Day chuyen pha tron 1, Day chuyen chiet rot nho'),
('production_lines', 'line_type', 'VARCHAR(50)', 'Loai day chuyen', 'Line type', NULL, 'blending, filling_small, filling_large, filling_drum, grease'),
('production_lines', 'max_capacity_liters_per_month', 'BIGINT', 'Cong suat toi da moi thang', 'Maximum monthly capacity', 'lit', '500000, 800000, 1200000'),
('production_lines', 'target_yield_rate', 'DECIMAL(5,3)', 'Ty le thanh pham muc tieu', 'Target yield rate', NULL, '0.975, 0.970, 0.980');

-- ---------- sales_orders ----------
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
('sales_orders', 'order_id', 'VARCHAR(20)', 'Ma don hang', 'Order ID (primary key)', NULL, 'SO-2024-000001, SO-2025-005000'),
('sales_orders', 'order_date', 'DATE', 'Ngay dat hang', 'Order date', NULL, '2024-10-15, 2025-06-01, 2026-03-20'),
('sales_orders', 'distributor_id', 'VARCHAR(10)', 'Khoa ngoai toi bang distributors', 'Foreign key to distributors', NULL, 'NPP-001, NPP-050'),
('sales_orders', 'product_id', 'VARCHAR(15)', 'Khoa ngoai toi bang products', 'Foreign key to products', NULL, 'PRD-001, PRD-100'),
('sales_orders', 'quantity_liters', 'DECIMAL(12,2)', 'So luong ban', 'Quantity sold', 'lit', '500.00, 2000.00, 18000.00'),
('sales_orders', 'unit_price_vnd', 'BIGINT', 'Don gia ban thuc te moi lit', 'Actual selling price per liter', 'VND/lit', '48000, 75000, 115000'),
('sales_orders', 'total_revenue_vnd', 'BIGINT', 'Doanh thu = quantity x unit_price', 'Revenue = quantity x unit_price', 'VND', '24000000, 150000000, 2070000000'),
('sales_orders', 'cogs_material_vnd', 'BIGINT', 'Gia von nguyen vat lieu', 'COGS — raw material component', 'VND', '15000000, 95000000'),
('sales_orders', 'cogs_production_vnd', 'BIGINT', 'Chi phi san xuat', 'COGS — production/manufacturing component', 'VND', '2000000, 12000000'),
('sales_orders', 'cogs_transport_vnd', 'BIGINT', 'Chi phi van chuyen den NPP', 'COGS — transportation to distributor', 'VND', '500000, 3000000'),
('sales_orders', 'total_cogs_vnd', 'BIGINT', 'Tong COGS = material + production + transport', 'Total COGS = material + production + transport', 'VND', '17500000, 110000000'),
('sales_orders', 'gross_profit_vnd', 'BIGINT', 'Loi nhuan gop = revenue - COGS', 'Gross profit = revenue - total COGS', 'VND', '6500000, 40000000'),
('sales_orders', 'gross_margin_pct', 'DECIMAL(5,2)', 'Bien loi nhuan gop = gross_profit / revenue x 100', 'Gross margin % = gross_profit / revenue x 100', '%', '18.50, 22.00, 27.30'),
('sales_orders', 'invoice_date', 'DATE', 'Ngay xuat hoa don', 'Invoice date', NULL, '2024-10-16, 2025-06-02'),
('sales_orders', 'due_date', 'DATE', 'Ngay den han thanh toan', 'Payment due date', NULL, '2024-11-15, 2025-07-02'),
('sales_orders', 'payment_status', 'VARCHAR(20)', 'Trang thai thanh toan', 'Payment status', NULL, 'pending, partial, paid, overdue');

-- ---------- payments ----------
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
('payments', 'payment_id', 'VARCHAR(20)', 'Ma thanh toan', 'Payment ID (primary key)', NULL, 'PAY-2024-000001, PAY-2025-010000'),
('payments', 'order_id', 'VARCHAR(20)', 'Khoa ngoai toi bang sales_orders', 'Foreign key to sales_orders', NULL, 'SO-2024-000001'),
('payments', 'distributor_id', 'VARCHAR(10)', 'Khoa ngoai toi bang distributors', 'Foreign key to distributors', NULL, 'NPP-001, NPP-050'),
('payments', 'payment_date', 'DATE', 'Ngay thanh toan thuc te', 'Actual payment date', NULL, '2024-11-10, 2025-06-28'),
('payments', 'amount_vnd', 'BIGINT', 'So tien thanh toan', 'Payment amount', 'VND', '24000000, 150000000'),
('payments', 'payment_method', 'VARCHAR(30)', 'Phuong thuc thanh toan', 'Payment method', NULL, 'Chuyen khoan, Tien mat, LC'),
('payments', 'days_from_invoice', 'INT', 'So ngay ke tu invoice_date', 'Days elapsed since invoice date (for DSO calculation)', 'ngay', '15, 30, 45, 60'),
('payments', 'is_overdue', 'BOOLEAN', 'Tra sau due_date hay khong', 'Whether payment was made after due date', NULL, 'TRUE, FALSE');

-- ---------- production_batches ----------
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
('production_batches', 'batch_id', 'VARCHAR(20)', 'Ma batch san xuat', 'Production batch ID (primary key)', NULL, 'BAT-2024-000001, BAT-2025-001500'),
('production_batches', 'batch_date', 'DATE', 'Ngay san xuat', 'Production date', NULL, '2024-10-05, 2025-06-15'),
('production_batches', 'line_id', 'VARCHAR(10)', 'Khoa ngoai toi bang production_lines', 'Foreign key to production_lines', NULL, 'LN-01, LN-03'),
('production_batches', 'product_id', 'VARCHAR(15)', 'Khoa ngoai toi bang products (san pham chinh cua batch)', 'Foreign key to products (primary product of batch)', NULL, 'PRD-001, PRD-100'),
('production_batches', 'input_quantity_liters', 'DECIMAL(12,2)', 'Luong nguyen lieu dau vao', 'Input raw material quantity', 'lit', '5000.00, 20000.00'),
('production_batches', 'output_quantity_liters', 'DECIMAL(12,2)', 'Luong thanh pham dau ra', 'Finished goods output quantity', 'lit', '4875.00, 19500.00'),
('production_batches', 'yield_rate', 'DECIMAL(5,3)', 'Ty le thanh pham = output/input', 'Yield rate = output / input', NULL, '0.975, 0.960, 0.985'),
('production_batches', 'material_cost_vnd', 'BIGINT', 'Chi phi nguyen vat lieu cho batch', 'Raw material cost for this batch', 'VND', '150000000, 600000000'),
('production_batches', 'labor_cost_vnd', 'BIGINT', 'Chi phi nhan cong', 'Labor cost', 'VND', '8000000, 25000000'),
('production_batches', 'overhead_cost_vnd', 'BIGINT', 'Chi phi overhead (dien, nuoc, khau hao)', 'Overhead cost (electricity, water, depreciation)', 'VND', '12000000, 40000000'),
('production_batches', 'total_production_cost_vnd', 'BIGINT', 'Tong chi phi SX = material + labor + overhead', 'Total production cost = material + labor + overhead', 'VND', '170000000, 665000000'),
('production_batches', 'cost_per_liter_vnd', 'BIGINT', 'Chi phi SX moi lit = total_cost / output_qty', 'Production cost per liter = total_cost / output_qty', 'VND/lit', '34872, 34103');

-- ---------- raw_material_costs ----------
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
('raw_material_costs', 'id', 'INT', 'Khoa chinh tu dong tang', 'Auto-increment primary key', NULL, '1, 100, 500'),
('raw_material_costs', 'month_date', 'DATE', 'Thang bao cao (ngay 1 cua thang)', 'Reporting month (always 1st of month)', NULL, '2024-10-01, 2025-06-01'),
('raw_material_costs', 'supplier_id', 'VARCHAR(10)', 'Khoa ngoai toi bang suppliers', 'Foreign key to suppliers', NULL, 'SUP-01, SUP-05'),
('raw_material_costs', 'material_type', 'VARCHAR(50)', 'Loai nguyen vat lieu', 'Raw material type', NULL, 'base_oil_group_I, base_oil_group_II, base_oil_group_III, additive'),
('raw_material_costs', 'price_per_liter_vnd', 'BIGINT', 'Gia mua moi lit', 'Purchase price per liter', 'VND/lit', '18000, 28000, 45000, 85000'),
('raw_material_costs', 'volume_purchased_liters', 'DECIMAL(12,2)', 'Luong mua trong thang', 'Volume purchased during the month', 'lit', '50000.00, 200000.00'),
('raw_material_costs', 'total_cost_vnd', 'BIGINT', 'Tong chi phi = price x volume', 'Total cost = price x volume', 'VND', '900000000, 5600000000');

-- ============================================================
-- _meta_kpi
-- ============================================================

INSERT INTO _meta_kpi (kpi_name, formula_sql, description_vi, related_questions) VALUES
('revenue',
 'SUM(total_revenue_vnd) FROM sales_orders WHERE order_date BETWEEN @start AND @end',
 'Tong doanh thu ban hang (VND). La chi so kinh doanh co ban nhat, tinh tren bang sales_orders.',
 'Doanh thu thang nay bao nhieu?; Doanh thu theo vung/brand/kenh?; Top 10 NPP doanh thu cao nhat?'),

('cogs',
 'SUM(total_cogs_vnd) FROM sales_orders WHERE order_date BETWEEN @start AND @end',
 'Tong gia von hang ban = NVL + san xuat + van chuyen. Gom 3 thanh phan: cogs_material_vnd + cogs_production_vnd + cogs_transport_vnd.',
 'COGS thang nay la bao nhieu?; Ty trong tung thanh phan COGS?; COGS theo nhom san pham?'),

('gross_profit',
 'SUM(gross_profit_vnd) FROM sales_orders WHERE order_date BETWEEN @start AND @end',
 'Loi nhuan gop = Doanh thu - COGS. Da duoc tinh san trong cot gross_profit_vnd cua bang sales_orders.',
 'Loi nhuan gop thang nay?; Brand nao co loi nhuan gop cao nhat?; Gross profit theo vung mien?'),

('gross_margin_pct',
 'SUM(gross_profit_vnd) * 100.0 / NULLIF(SUM(total_revenue_vnd), 0) FROM sales_orders WHERE order_date BETWEEN @start AND @end',
 'Bien loi nhuan gop (%) = Tong LN gop / Tong doanh thu x 100. Benchmark nganh dau nhon VN: 18-28%. Khong dung AVG(gross_margin_pct) vi se sai — phai tinh SUM/SUM.',
 'Margin trung binh la bao nhieu?; Brand/san pham nao margin thap nhat?; Margin theo kenh ban hang?'),

('dso',
 'AVG(days_from_invoice) FROM payments WHERE payment_date BETWEEN @start AND @end',
 'Days Sales Outstanding — So ngay thu tien binh quan. Benchmark nganh: 30-45 ngay. DSO > 45 can canh bao.',
 'DSO trung binh bao nhieu ngay?; NPP nao tra cham nhat?; DSO co xu huong tang hay giam?'),

('yield_rate',
 'SUM(output_quantity_liters) / NULLIF(SUM(input_quantity_liters), 0) FROM production_batches WHERE batch_date BETWEEN @start AND @end',
 'Ty le thanh pham = luong dau ra / luong dau vao. Muc tieu: >= 97.5%. Duoi 95% la bat thuong, can kiem tra chat luong.',
 'Yield rate thang nay bao nhieu?; Day chuyen nao yield thap nhat?; Yield theo san pham?'),

('capacity_utilization',
 'SUM(pb.output_quantity_liters) / NULLIF(SUM(pl.max_capacity_liters_per_month), 0) FROM production_batches pb JOIN production_lines pl ON pb.line_id = pl.line_id WHERE YEAR(pb.batch_date)=@year AND MONTH(pb.batch_date)=@month',
 'Ty le su dung cong suat = san luong thuc te / cong suat toi da. Tren 90% la can mo rong. Duoi 60% la lang phi.',
 'Cong suat su dung thang nay la bao nhieu %?; Day chuyen nao dang qua tai?; Xu huong cong suat 6 thang qua?'),

('overdue_rate',
 'SUM(CASE WHEN payment_status = ''overdue'' THEN total_revenue_vnd ELSE 0 END) * 100.0 / NULLIF(SUM(total_revenue_vnd), 0) FROM sales_orders WHERE order_date BETWEEN @start AND @end',
 'Ty le no qua han = gia tri don hang overdue / tong doanh thu x 100. Tren 10% la muc canh bao do.',
 'Ty le no qua han hien tai?; NPP nao dang no qua han nhieu nhat?; No qua han theo vung?'),

('yoy_growth',
 '(SUM(CASE WHEN YEAR(order_date)=@year THEN total_revenue_vnd END) - SUM(CASE WHEN YEAR(order_date)=@year-1 THEN total_revenue_vnd END)) * 100.0 / NULLIF(SUM(CASE WHEN YEAR(order_date)=@year-1 THEN total_revenue_vnd END), 0) FROM sales_orders',
 'Tang truong doanh thu so voi cung ky nam truoc (%). Cong thuc: (DT nam nay - DT nam truoc) / DT nam truoc x 100.',
 'Tang truong YoY la bao nhieu %?; Brand nao tang truong nhanh nhat?; Vung nao tang truong am?'),

('revenue_per_npp',
 'SUM(total_revenue_vnd) / COUNT(DISTINCT distributor_id) FROM sales_orders WHERE order_date BETWEEN @start AND @end',
 'Doanh thu binh quan moi NPP. Dung de danh gia hieu qua kenh phan phoi va phat hien NPP yeu.',
 'Doanh thu trung binh moi NPP?; NPP nao duoi muc trung binh?'),

('material_cost_trend',
 'SELECT month_date, material_type, AVG(price_per_liter_vnd) FROM raw_material_costs GROUP BY month_date, material_type ORDER BY month_date',
 'Xu huong gia nguyen vat lieu theo thang. Gia dau goc bien dong theo gia dau tho the gioi.',
 'Gia dau goc Group II tang bao nhieu trong 6 thang?; NVL nao tang gia nhieu nhat?'),

('production_cost_per_liter',
 'SUM(total_production_cost_vnd) / NULLIF(SUM(output_quantity_liters), 0) FROM production_batches WHERE batch_date BETWEEN @start AND @end',
 'Chi phi san xuat binh quan moi lit. Gom NVL + nhan cong + overhead. Dung de theo doi hieu qua san xuat.',
 'Chi phi san xuat trung binh moi lit?; Xu huong chi phi SX 6 thang?; San pham nao chi phi SX cao nhat?');

-- ============================================================
-- _meta_glossary
-- ============================================================

INSERT INTO _meta_glossary (term_vi, term_en, definition) VALUES
('NPP', 'Distributor',
 'Nha phan phoi — doi tac mua hang tu AP Saigon Petro de ban lai. Phan cap: Tong dai ly, Dai ly cap 1, Dai ly cap 2. Bang: distributors.'),

('Dai ly', 'Dealer / Distributor',
 'Tuong tu NPP. Dai ly cap 1 mua truc tiep tu cong ty, Dai ly cap 2 mua qua Tong dai ly.'),

('Tong dai ly', 'Master Distributor',
 'NPP cap cao nhat, mua so luong lon, co the phan phoi lai cho dai ly cap 2 trong khu vuc. Tier = Tong dai ly trong bang distributors.'),

('DT', 'Revenue',
 'Doanh thu — viet tat cua Doanh thu. Cot total_revenue_vnd trong bang sales_orders. Tinh bang = quantity_liters x unit_price_vnd.'),

('Doanh thu', 'Revenue',
 'Tong tien ban hang truoc khi tru chi phi. Cot total_revenue_vnd trong bang sales_orders.'),

('COGS', 'Cost of Goods Sold',
 'Gia von hang ban. Gom 3 thanh phan: cogs_material_vnd (NVL) + cogs_production_vnd (san xuat) + cogs_transport_vnd (van chuyen). Cot total_cogs_vnd trong sales_orders.'),

('Gia von', 'COGS / Cost of Goods Sold',
 'Tuong tu COGS. Tong chi phi de san xuat va giao hang san pham toi NPP.'),

('NVL', 'Raw Materials',
 'Nguyen vat lieu — dau goc (base oil) va phu gia (additive). Bang: raw_material_costs, suppliers.'),

('Loi nhuan gop', 'Gross Profit',
 'Doanh thu tru COGS. Cot gross_profit_vnd = total_revenue_vnd - total_cogs_vnd trong bang sales_orders.'),

('Bien loi nhuan gop', 'Gross Margin %',
 'Ty le loi nhuan gop tren doanh thu. Cot gross_margin_pct trong sales_orders. Tinh toan tren tap hop: SUM(gross_profit_vnd)/SUM(total_revenue_vnd)*100. Benchmark nganh: 18-28%.'),

('Margin', 'Margin / Gross Margin',
 'Viet tat cua Bien loi nhuan gop. Tinh bang %: gross_profit / revenue x 100.'),

('DSO', 'Days Sales Outstanding',
 'So ngay thu tien binh quan. Do toc do thu hoi cong no tu NPP. Cot days_from_invoice trong bang payments. Benchmark: 30-45 ngay.'),

('Cong no', 'Accounts Receivable',
 'Tien NPP con no chua tra. Xac dinh qua payment_status = ''pending'' hoac ''overdue'' trong sales_orders, ket hop payments.'),

('No qua han', 'Overdue Receivables',
 'Don hang da qua due_date nhung chua thanh toan du. payment_status = ''overdue'' trong sales_orders. is_overdue = TRUE trong payments.'),

('Yield', 'Yield Rate',
 'Ty le thanh pham — luong san pham dau ra / luong nguyen lieu dau vao. Cot yield_rate trong production_batches. Muc tieu >= 97.5%.'),

('Ty le thanh pham', 'Yield Rate',
 'Tuong tu Yield. output_quantity_liters / input_quantity_liters. Duoi 95% la bat thuong.'),

('Cong suat', 'Capacity / Capacity Utilization',
 'Kha nang san xuat cua day chuyen. max_capacity_liters_per_month trong production_lines. So sanh voi san luong thuc te de tinh ty le su dung.'),

('Day chuyen', 'Production Line',
 'Day chuyen san xuat tai nha may Cat Lai. 5 loai: blending, filling_small, filling_large, filling_drum, grease. Bang: production_lines.'),

('Nha may Cat Lai', 'Cat Lai Factory',
 'Nha may san xuat dau nhon cua AP Saigon Petro tai Cat Lai, TP.HCM. 5 day chuyen, cong suat 5,000-8,000 tan/thang.'),

('Dau goc', 'Base Oil',
 'Nguyen lieu chinh de pha che dau nhon. Phan nhom: Group I (khoang), Group II, Group III (tong hop), Group IV (PAO). Bang: suppliers, raw_material_costs.'),

('Phu gia', 'Additive',
 'Hoa chat them vao dau goc de cai thien tinh nang: chong oxy hoa, chong ma mon, tang chi so nhot. material_type = additive.'),

('Base oil', 'Base Oil',
 'Dau goc — tuong tu Dau goc. Chiem 70-90% thanh phan dau nhon. Gia bien dong theo gia dau tho the gioi.'),

('Dau nhon', 'Lubricant / Lubricating Oil',
 'San pham chinh cua AP Saigon Petro. Gom dau dong co (xe may, o to, xe tai), dau cong nghiep, dau hang hai, mo boi tron.'),

('Do nhot', 'Viscosity / Viscosity Grade',
 'Do dac loang cua dau nhon. Theo tieu chuan SAE: so nho = loang (5W-30), so lon = dac (20W-50). Cot viscosity_grade trong products.'),

('API', 'API Grade',
 'Tieu chuan hieu nang dau nhon cua Vien Dau khi Hoa Ky. SN/SP cho xang, CI-4/CK-4 cho diesel. Cot api_grade trong products.'),

('SKU', 'Stock Keeping Unit',
 'Don vi luu kho — moi ma san pham la 1 SKU. AP Saigon Petro co khoang 200 SKU active.'),

('B2B', 'Business to Business',
 'Ban buon cho doanh nghiep: nha may, doi xe, xuong sua chua. channel_type = B2B trong channels.'),

('B2C', 'Business to Consumer',
 'Ban le cho nguoi tieu dung cuoi: cua hang, tram xang, online. channel_type = B2C trong channels.'),

('YoY', 'Year over Year',
 'So sanh cung ky nam truoc. Cong thuc: (gia tri nam nay - gia tri nam truoc) / gia tri nam truoc x 100%.'),

('MoM', 'Month over Month',
 'So sanh voi thang truoc. Cong thuc: (gia tri thang nay - gia tri thang truoc) / gia tri thang truoc x 100%.'),

('Kenh ban hang', 'Sales Channel',
 'Kenh phan phoi san pham: dai ly xe may, gara o to, cong nghiep, tram xang, online. Bang: channels.'),

('Vung mien', 'Region / Macro-region',
 'Phan chia dia ly: Mien Bac, Mien Trung, Mien Nam. Cot macro_region trong regions. De group theo vung dung cot region_name.');
