-- ============================================================
-- 02_metadata.sql
-- Database: menas_demo
-- Menas Group — Metadata
-- ============================================================

USE menas_demo;

-- Metadata: Tables
CREATE TABLE IF NOT EXISTS _meta_tables (
  table_name VARCHAR(100) PRIMARY KEY,
  description VARCHAR(500),
  notes TEXT,
  approx_rows INT
) COMMENT='Mô tả các bảng dữ liệu';

INSERT INTO `_meta_tables` (table_name, description, notes, approx_rows) VALUES
('business_units', 'Các mảng kinh doanh', 'Menas Group có 5 mảng: TTTM, Siêu thị, F&B, Duty Free, Beauty', 5.00),
('locations', 'Tất cả địa điểm kinh doanh', '15 địa điểm trải khắp HCM và Nha Trang', 15.00),
('product_categories', 'Nhóm hàng siêu thị', '6 nhóm hàng chính trong siêu thị Mena Gourmet', 6.00),
('products', 'Danh mục sản phẩm', '~500 SKU siêu thị với phân bố Pareto', 500.00),
('fb_outlets', 'Chi tiết outlet F&B', '9 outlet F&B thuộc Menas Group', 9.00),
('tenants', 'Tenant thuê mặt bằng', '~45 tenant tại 2 TTTM', 45.00),
('planned_locations', 'Địa điểm dự kiến', '5 vị trí mở rộng tiềm năng', 5.00),
('employees_summary', 'Nhân sự theo tháng', 'Headcount và chi phí nhân sự', 270.00),
('monthly_revenue', 'Doanh thu tổng hợp', 'Doanh thu, chi phí, lợi nhuận theo mảng/tháng', 270.00),
('supermarket_daily_sales', 'Bán hàng siêu thị', '~160K dòng bán hàng chi tiết theo ngày', 160000.00),
('supermarket_shrinkage', 'Hao hụt hàng hóa', 'Hao hụt theo nhóm hàng/tháng', 216.00),
('fb_monthly_revenue', 'Doanh thu F&B', 'Doanh thu, covers, avg check theo outlet/tháng', 162.00),
('fb_monthly_costs', 'Chi phí F&B', 'Chi phí theo loại: food/labor/rent/utilities/marketing', 810.00),
('tenant_monthly_revenue', 'Doanh thu tenant', 'Doanh thu gộp tenant theo tháng', 810.00),
('promotions', 'Chương trình khuyến mãi', 'Khuyến mãi siêu thị và F&B', 20.00),
('mall_events', 'Sự kiện TTTM', 'Sự kiện tại các TTTM bao gồm bảo trì', 16.00),
('mall_daily_footfall', 'Lượt khách TTTM', 'Lượt khách hàng ngày theo phân khúc airport/local', 2200.00),
('airport_daily_passengers', 'Khách sân bay TSN', 'Lượng khách sân bay Tân Sơn Nhất hàng ngày', 549.00);

-- Metadata: Key Columns
CREATE TABLE IF NOT EXISTS _meta_columns (
  id INT AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(100),
  column_name VARCHAR(100),
  description VARCHAR(500),
  aggregation_hint VARCHAR(100),
  notes TEXT
) COMMENT='Mô tả các cột quan trọng';

INSERT INTO `_meta_columns` (table_name, column_name, description, aggregation_hint, notes) VALUES
('monthly_revenue', 'revenue_vnd', 'Doanh thu tháng (VND)', 'SUM, AVG', 'Tổng doanh thu theo mảng kinh doanh'),
('monthly_revenue', 'cost_vnd', 'Chi phí tháng (VND)', 'SUM, AVG', 'Tổng chi phí vận hành'),
('monthly_revenue', 'profit_vnd', 'Lợi nhuận tháng (VND)', 'SUM', 'Doanh thu - Chi phí'),
('supermarket_daily_sales', 'quantity', 'Số lượng bán', 'SUM, AVG', 'Số lượng sản phẩm bán theo ngày'),
('supermarket_daily_sales', 'selling_price_vnd', 'Giá bán (VND)', 'AVG', 'Giá bán thực tế (có thể khác base)'),
('supermarket_daily_sales', 'discount_amount_vnd', 'Giảm giá (VND)', 'SUM', 'Tổng giảm giá trong chương trình KM'),
('supermarket_shrinkage', 'shrinkage_rate_pct', 'Tỷ lệ hao hụt (%)', 'AVG', 'Tỷ lệ hao hụt trên doanh thu nhóm hàng'),
('fb_monthly_revenue', 'covers', 'Số lượt khách', 'SUM, AVG', 'Tổng lượt khách F&B trong tháng'),
('fb_monthly_revenue', 'avg_check_vnd', 'Giá trị trung bình/lượt', 'AVG', 'Doanh thu / số lượt khách'),
('fb_monthly_costs', 'amount_vnd', 'Chi phí (VND)', 'SUM', 'Chi phí theo loại: food/labor/rent/utilities/marketing'),
('tenant_monthly_revenue', 'gross_revenue_vnd', 'Doanh thu gộp tenant', 'SUM, AVG', 'Doanh thu tenant để tính revenue share'),
('mall_daily_footfall', 'total_count', 'Lượt khách', 'SUM, AVG', 'Lượt khách TTTM hàng ngày theo phân khúc airport/local'),
('mall_daily_footfall', 'segment', 'Phân khúc khách', 'GROUP BY', 'airport = khách sân bay, local = khách địa phương'),
('airport_daily_passengers', 'total_passengers', 'Tổng lượt khách sân bay', 'SUM, AVG', 'Lượng khách TSN hàng ngày');

-- Metadata: KPIs
CREATE TABLE IF NOT EXISTS _meta_kpi (
  kpi_code VARCHAR(50) PRIMARY KEY,
  kpi_name VARCHAR(200),
  formula TEXT,
  benchmark TEXT
) COMMENT='Các KPI chính';

INSERT INTO `_meta_kpi` (kpi_code, kpi_name, formula, benchmark) VALUES
('gross_margin_pct', 'Biên lợi nhuận gộp (%)', '(Revenue - Cost) / Revenue × 100', 'Siêu thị target ≥22%, F&B target ≥30%'),
('revenue_per_sqm', 'Doanh thu/m²', 'Revenue / Diện tích', 'So sánh hiệu quả sử dụng mặt bằng'),
('shrinkage_rate', 'Tỷ lệ hao hụt (%)', 'Shrinkage / Revenue × 100', 'Target <1.5%, cảnh báo >2%'),
('food_cost_ratio', 'Tỷ lệ food cost (%)', 'Food Cost / F&B Revenue × 100', 'Target <35%'),
('labor_cost_ratio', 'Tỷ lệ chi phí nhân sự (%)', 'Labor Cost / Revenue × 100', 'Target <28%, cảnh báo >32%'),
('avg_check', 'Giá trị trung bình/lượt (VND)', 'Revenue / Covers', 'Theo dõi xu hướng giá trị đơn hàng'),
('occupancy_rate', 'Tỷ lệ lấp đầy (%)', 'Diện tích cho thuê / Tổng diện tích thuê × 100', 'Target >90%'),
('tenant_rev_per_sqm', 'Doanh thu tenant/m²', 'Tenant Revenue / SQM thuê', 'Đánh giá hiệu quả tenant'),
('marketing_roi', 'ROI Marketing', 'Revenue Uplift / Marketing Spend', 'Đánh giá hiệu quả marketing'),
('yoy_growth', 'Tăng trưởng YoY (%)', '(Revenue_current - Revenue_prior) / Revenue_prior × 100', 'Target 15% YoY');

-- Metadata: Glossary
CREATE TABLE IF NOT EXISTS _meta_glossary (
  term VARCHAR(100) PRIMARY KEY,
  definition_vi VARCHAR(500),
  definition_en VARCHAR(500)
) COMMENT='Bảng thuật ngữ';

INSERT INTO `_meta_glossary` (term, definition_vi, definition_en) VALUES
('TTTM', 'Trung tâm thương mại', 'Shopping mall / Commercial center'),
('BU', 'Business Unit', 'Mảng kinh doanh'),
('SKU', 'Stock Keeping Unit', 'Đơn vị quản lý kho'),
('Covers', 'Lượt khách F&B', 'Số lượt khách phục vụ tại nhà hàng'),
('Avg Check', 'Giá trị trung bình/lượt', 'Average check per customer'),
('Shrinkage', 'Hao hụt', 'Tổn thất hàng hóa do hư hỏng, mất cắp, hết hạn'),
('Revenue Share', 'Chia sẻ doanh thu', 'Tỷ lệ doanh thu tenant chia cho TTTM'),
('Footfall', 'Lượt khách', 'Số lượt khách đến TTTM/cửa hàng'),
('Gross Margin', 'Biên lợi nhuận gộp', '(Doanh thu - Giá vốn) / Doanh thu'),
('Food Cost', 'Chi phí nguyên liệu', 'Chi phí nguyên liệu thực phẩm F&B'),
('Duty Free', 'Miễn thuế', 'Cửa hàng bán hàng miễn thuế tại sân bay'),
('Ramp-up', 'Giai đoạn khởi động', 'Thời gian location mới đạt công suất tối đa');

