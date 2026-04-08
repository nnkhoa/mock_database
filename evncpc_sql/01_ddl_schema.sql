-- =============================================
-- EVNCPC Demo Database — DDL Schema
-- Tổng Công ty Điện lực miền Trung
-- Database: evncpc_demo
-- =============================================

DROP DATABASE IF EXISTS `evncpc_demo`;
CREATE DATABASE IF NOT EXISTS `evncpc_demo`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `evncpc_demo`;

-- =============================================
-- DIMENSION TABLES
-- =============================================

CREATE TABLE IF NOT EXISTS power_companies (
  pc_id VARCHAR(4) PRIMARY KEY COMMENT 'Mã công ty điện lực (PC01-PC08)',
  pc_name VARCHAR(100) NOT NULL COMMENT 'Tên công ty điện lực',
  pc_short_name VARCHAR(50) COMMENT 'Tên viết tắt',
  provinces_covered TEXT COMMENT 'Danh sách tỉnh/TP quản lý',
  headquarters_city VARCHAR(50) COMMENT 'Thành phố trụ sở',
  num_employees INT COMMENT 'Số CBCNV',
  num_customers INT COMMENT 'Số khách hàng sử dụng điện',
  total_line_length_km DECIMAL(10,1) COMMENT 'Tổng chiều dài đường dây quản lý (km)',
  num_substations_110kv INT COMMENT 'Số trạm 110kV',
  num_distribution_substations INT COMMENT 'Số trạm biến áp phân phối',
  is_joint_stock BOOLEAN DEFAULT FALSE COMMENT 'Là công ty cổ phần (TRUE) hay TNHH MTV (FALSE)',
  established_date DATE COMMENT 'Ngày thành lập/sáp nhập',
  notes TEXT COMMENT 'Ghi chú đặc thù'
) COMMENT = 'Danh sách 8 công ty điện lực thành viên EVNCPC (cơ cấu mới từ 1/7/2025)';

CREATE TABLE IF NOT EXISTS provinces (
  province_id VARCHAR(4) PRIMARY KEY COMMENT 'Mã tỉnh/TP',
  province_name VARCHAR(50) NOT NULL COMMENT 'Tên tỉnh/TP',
  pc_id VARCHAR(4) NOT NULL COMMENT 'FK → power_companies',
  region VARCHAR(20) COMMENT 'Vùng: Duyên hải / Tây Nguyên',
  area_km2 DECIMAL(10,1) COMMENT 'Diện tích (km²)',
  population INT COMMENT 'Dân số ước tính',
  num_districts INT COMMENT 'Số huyện/quận/TX/TP',
  terrain_type VARCHAR(30) COMMENT 'Địa hình chính: Đồng bằng / Đồi núi / Ven biển / Hỗn hợp',
  storm_risk_level VARCHAR(10) COMMENT 'Mức rủi ro bão: Cao / Trung bình / Thấp',
  FOREIGN KEY (pc_id) REFERENCES power_companies(pc_id)
) COMMENT = '13 tỉnh/TP thuộc EVNCPC quản lý';

CREATE TABLE IF NOT EXISTS districts (
  district_id VARCHAR(6) PRIMARY KEY COMMENT 'Mã huyện/quận',
  district_name VARCHAR(50) NOT NULL COMMENT 'Tên huyện/quận/TX/TP',
  province_id VARCHAR(4) NOT NULL COMMENT 'FK → provinces',
  pc_id VARCHAR(4) NOT NULL COMMENT 'FK → power_companies (denormalized cho query nhanh)',
  district_type VARCHAR(20) COMMENT 'Loại: Thành phố / Thị xã / Huyện',
  area_km2 DECIMAL(8,1) COMMENT 'Diện tích (km²)',
  num_customers INT COMMENT 'Số khách hàng sử dụng điện',
  is_urban BOOLEAN COMMENT 'Khu vực đô thị (TRUE) / nông thôn (FALSE)',
  FOREIGN KEY (province_id) REFERENCES provinces(province_id),
  FOREIGN KEY (pc_id) REFERENCES power_companies(pc_id)
) COMMENT = 'Quận/huyện — mức chi tiết nhất cho phân tích tổn thất và sự cố';

CREATE TABLE IF NOT EXISTS substations (
  substation_id VARCHAR(10) PRIMARY KEY COMMENT 'Mã trạm biến áp',
  substation_name VARCHAR(100) COMMENT 'Tên trạm',
  pc_id VARCHAR(4) NOT NULL COMMENT 'FK → power_companies',
  district_id VARCHAR(6) NOT NULL COMMENT 'FK → districts',
  voltage_level VARCHAR(10) NOT NULL COMMENT 'Cấp điện áp: 110kV / 22kV / 0.4kV',
  substation_type VARCHAR(30) COMMENT 'Loại: Trạm 110kV / Trạm treo / Trạm giàn / Trạm hợp bộ',
  capacity_kva INT COMMENT 'Công suất định mức (kVA)',
  installed_year INT COMMENT 'Năm lắp đặt',
  manufacturer VARCHAR(50) COMMENT 'Nhà sản xuất',
  load_rate_pct DECIMAL(5,2) COMMENT 'Tỷ lệ mang tải hiện tại (%) — tải thực tế / công suất định mức × 100',
  condition_rating VARCHAR(20) COMMENT 'Tình trạng: Tốt / Trung bình / Kém / Cần thay thế',
  last_maintenance_date DATE COMMENT 'Ngày bảo trì gần nhất',
  FOREIGN KEY (pc_id) REFERENCES power_companies(pc_id),
  FOREIGN KEY (district_id) REFERENCES districts(district_id),
  INDEX idx_sub_pc (pc_id),
  INDEX idx_sub_district (district_id),
  INDEX idx_sub_voltage (voltage_level),
  INDEX idx_sub_year (installed_year)
) COMMENT = 'Trạm biến áp — representative sample phục vụ phân tích tổn thất và đầu tư';

CREATE TABLE IF NOT EXISTS grid_assets (
  asset_id VARCHAR(10) PRIMARY KEY COMMENT 'Mã tài sản',
  asset_type VARCHAR(30) NOT NULL COMMENT 'Loại: MBA phân phối / Recloser / Đường dây trung thế / Đường dây hạ thế / Tụ bù',
  pc_id VARCHAR(4) NOT NULL COMMENT 'FK → power_companies',
  district_id VARCHAR(6) COMMENT 'FK → districts',
  installed_year INT COMMENT 'Năm lắp đặt',
  capacity_or_length DECIMAL(10,2) COMMENT 'Công suất (kVA) hoặc chiều dài (km) tùy loại',
  unit VARCHAR(10) COMMENT 'Đơn vị: kVA / km',
  condition_rating VARCHAR(10) COMMENT 'Tình trạng: Tốt / Trung bình / Kém',
  replacement_cost_million_vnd DECIMAL(10,1) COMMENT 'Chi phí thay thế ước tính (triệu VND)',
  FOREIGN KEY (pc_id) REFERENCES power_companies(pc_id),
  FOREIGN KEY (district_id) REFERENCES districts(district_id),
  INDEX idx_asset_pc (pc_id),
  INDEX idx_asset_type (asset_type)
) COMMENT = 'Tài sản lưới điện — phục vụ phân tích đầu tư cải tạo';

CREATE TABLE IF NOT EXISTS customer_segments (
  segment_id INT AUTO_INCREMENT PRIMARY KEY,
  pc_id VARCHAR(4) NOT NULL COMMENT 'FK → power_companies',
  segment_name VARCHAR(50) NOT NULL COMMENT 'Nhóm KH: Công nghiệp-Xây dựng / Quản lý-Tiêu dùng / Thương nghiệp-Dịch vụ / Nông lâm ngư nghiệp / Khác',
  num_customers INT COMMENT 'Số khách hàng trong nhóm',
  proportion_pct DECIMAL(5,2) COMMENT 'Tỷ trọng sản lượng (%)',
  avg_price_vnd_per_kwh DECIMAL(8,2) COMMENT 'Giá bán bình quân nhóm (VND/kWh)',
  FOREIGN KEY (pc_id) REFERENCES power_companies(pc_id)
) COMMENT = 'Cơ cấu khách hàng theo nhóm biểu giá, theo PC';

CREATE TABLE IF NOT EXISTS loss_targets (
  target_id INT AUTO_INCREMENT PRIMARY KEY,
  pc_id VARCHAR(4) NOT NULL COMMENT 'FK → power_companies',
  year INT NOT NULL COMMENT 'Năm áp dụng',
  target_loss_rate_pct DECIMAL(5,2) NOT NULL COMMENT 'Chỉ tiêu tổn thất EVN giao (%)',
  target_saidi_minutes DECIMAL(6,1) COMMENT 'Chỉ tiêu SAIDI (phút/KH/năm)',
  target_saifi_times DECIMAL(4,1) COMMENT 'Chỉ tiêu SAIFI (lần/KH/năm)',
  FOREIGN KEY (pc_id) REFERENCES power_companies(pc_id),
  UNIQUE KEY uk_target (pc_id, year)
) COMMENT = 'Chỉ tiêu EVN giao cho từng PC theo năm';

CREATE TABLE IF NOT EXISTS weather_events (
  event_id INT AUTO_INCREMENT PRIMARY KEY,
  event_name VARCHAR(100) COMMENT 'Tên bão/áp thấp (ví dụ: Bão số 4 - Noru)',
  event_type VARCHAR(30) NOT NULL COMMENT 'Loại: Bão / Áp thấp nhiệt đới / Mưa lớn / Lũ lụt / Sạt lở',
  start_date DATE NOT NULL COMMENT 'Ngày bắt đầu ảnh hưởng',
  end_date DATE COMMENT 'Ngày kết thúc ảnh hưởng',
  severity VARCHAR(20) COMMENT 'Mức độ: Nhẹ / Trung bình / Nặng / Rất nặng',
  affected_provinces TEXT COMMENT 'Danh sách tỉnh bị ảnh hưởng (comma-separated province_id)',
  max_wind_speed_kmh INT COMMENT 'Tốc độ gió cực đại (km/h)',
  rainfall_mm INT COMMENT 'Lượng mưa tích lũy (mm)',
  notes TEXT COMMENT 'Ghi chú thêm'
) COMMENT = 'Sự kiện thời tiết ảnh hưởng đến vận hành lưới điện';

-- =============================================
-- FACT TABLES
-- =============================================

CREATE TABLE IF NOT EXISTS monthly_kpi_summary (
  kpi_id INT AUTO_INCREMENT PRIMARY KEY,
  pc_id VARCHAR(4) NOT NULL COMMENT 'FK → power_companies',
  report_month DATE NOT NULL COMMENT 'Tháng báo cáo (ngày 1 của tháng)',
  -- Sản lượng & Doanh thu
  power_received_gwh DECIMAL(10,3) COMMENT 'Điện nhận (GWh)',
  commercial_power_gwh DECIMAL(10,3) COMMENT 'Điện thương phẩm (GWh)',
  revenue_billion_vnd DECIMAL(10,2) COMMENT 'Doanh thu phân phối điện (tỷ VND)',
  avg_selling_price_vnd DECIMAL(8,2) COMMENT 'Giá bán bình quân (VND/kWh)',
  -- Tổn thất
  loss_rate_pct DECIMAL(5,2) COMMENT 'Tỷ lệ tổn thất điện năng tổng (%)',
  technical_loss_mv_pct DECIMAL(5,2) COMMENT 'Tổn thất kỹ thuật trung thế (%)',
  technical_loss_lv_pct DECIMAL(5,2) COMMENT 'Tổn thất kỹ thuật hạ thế (%)',
  commercial_loss_pct DECIMAL(5,2) COMMENT 'Tổn thất thương mại (%)',
  -- Độ tin cậy
  saidi_minutes DECIMAL(8,2) COMMENT 'SAIDI tháng (phút/KH)',
  saifi_times DECIMAL(6,2) COMMENT 'SAIFI tháng (lần/KH)',
  maifi_times DECIMAL(6,2) COMMENT 'MAIFI tháng (lần/KH)',
  -- Sự cố
  num_incidents_110kv INT COMMENT 'Số sự cố lưới 110kV',
  num_incidents_medium_voltage INT COMMENT 'Số sự cố lưới trung thế',
  num_incidents_total INT COMMENT 'Tổng số sự cố',
  -- Vận hành
  peak_load_mw DECIMAL(8,1) COMMENT 'Công suất đỉnh tháng (MW)',
  num_overloaded_substations INT COMMENT 'Số MBA quá tải (>80% công suất)',
  collection_rate_pct DECIMAL(5,2) COMMENT 'Tỷ lệ thu nộp tiền điện (%)',
  -- Nhân sự
  num_employees INT COMMENT 'Số CBCNV cuối tháng',
  productivity_kwh_per_employee DECIMAL(10,1) COMMENT 'Năng suất lao động (kWh thương phẩm/LĐ/tháng)',
  FOREIGN KEY (pc_id) REFERENCES power_companies(pc_id),
  UNIQUE KEY uk_kpi (pc_id, report_month),
  INDEX idx_kpi_month (report_month),
  INDEX idx_kpi_pc_month (pc_id, report_month)
) COMMENT = 'KPI vận hành tổng hợp theo công ty điện lực × tháng — fact table chính';

CREATE TABLE IF NOT EXISTS power_loss_detail (
  loss_id INT AUTO_INCREMENT PRIMARY KEY,
  district_id VARCHAR(6) NOT NULL COMMENT 'FK → districts',
  pc_id VARCHAR(4) NOT NULL COMMENT 'FK → power_companies (denormalized)',
  report_month DATE NOT NULL COMMENT 'Tháng báo cáo',
  power_received_mwh DECIMAL(12,2) COMMENT 'Điện nhận tại huyện (MWh)',
  commercial_power_mwh DECIMAL(12,2) COMMENT 'Điện thương phẩm tại huyện (MWh)',
  total_loss_rate_pct DECIMAL(5,2) COMMENT 'Tổn thất tổng huyện (%)',
  technical_loss_mv_pct DECIMAL(5,2) COMMENT 'Tổn thất kỹ thuật trung thế (%)',
  technical_loss_lv_pct DECIMAL(5,2) COMMENT 'Tổn thất kỹ thuật hạ thế (%)',
  commercial_loss_pct DECIMAL(5,2) COMMENT 'Tổn thất thương mại (%)',
  num_substations_overloaded INT COMMENT 'Số MBA quá tải trong huyện',
  FOREIGN KEY (district_id) REFERENCES districts(district_id),
  FOREIGN KEY (pc_id) REFERENCES power_companies(pc_id),
  UNIQUE KEY uk_loss (district_id, report_month),
  INDEX idx_loss_pc_month (pc_id, report_month)
) COMMENT = 'Tổn thất điện năng chi tiết theo huyện × tháng — phục vụ drill-down root cause';

CREATE TABLE IF NOT EXISTS grid_incidents (
  incident_id INT AUTO_INCREMENT PRIMARY KEY,
  pc_id VARCHAR(4) NOT NULL COMMENT 'FK → power_companies',
  district_id VARCHAR(6) COMMENT 'FK → districts',
  incident_date DATE NOT NULL COMMENT 'Ngày xảy ra sự cố',
  incident_time TIME COMMENT 'Giờ xảy ra',
  voltage_level VARCHAR(10) COMMENT 'Cấp điện áp: 110kV / Trung thế / Hạ thế',
  cause_category VARCHAR(30) NOT NULL COMMENT 'Nguyên nhân: Bão-Áp thấp / Cây đổ / Ngập / Sét / Thiết bị hỏng / Quá tải / Thi công bên thứ 3 / Khác',
  cause_detail TEXT COMMENT 'Mô tả chi tiết nguyên nhân',
  affected_customers INT COMMENT 'Số khách hàng bị ảnh hưởng',
  outage_duration_hours DECIMAL(6,2) COMMENT 'Thời gian mất điện (giờ)',
  restoration_time_hours DECIMAL(6,2) COMMENT 'Thời gian phục hồi cấp điện (giờ)',
  repair_cost_million_vnd DECIMAL(10,1) COMMENT 'Chi phí sửa chữa/khắc phục (triệu VND)',
  weather_event_id INT COMMENT 'FK → weather_events (NULL nếu không liên quan thời tiết)',
  equipment_damaged TEXT COMMENT 'Thiết bị hư hỏng (cột, dây, MBA...)',
  FOREIGN KEY (pc_id) REFERENCES power_companies(pc_id),
  FOREIGN KEY (district_id) REFERENCES districts(district_id),
  FOREIGN KEY (weather_event_id) REFERENCES weather_events(event_id),
  INDEX idx_inc_pc (pc_id),
  INDEX idx_inc_date (incident_date),
  INDEX idx_inc_cause (cause_category),
  INDEX idx_inc_pc_date (pc_id, incident_date)
) COMMENT = 'Sự cố lưới điện từng vụ — chi tiết nhất, phục vụ phân tích rủi ro thiên tai';

CREATE TABLE IF NOT EXISTS investment_history (
  project_id INT AUTO_INCREMENT PRIMARY KEY,
  pc_id VARCHAR(4) NOT NULL COMMENT 'FK → power_companies',
  district_id VARCHAR(6) COMMENT 'FK → districts (NULL nếu dự án toàn PC)',
  project_name VARCHAR(200) COMMENT 'Tên dự án',
  project_type VARCHAR(50) COMMENT 'Loại: Cải tạo lưới trung thế / Cải tạo lưới hạ thế / Thay MBA / Lắp recloser / Xây TBA 110kV / Kéo dây mới',
  start_year INT COMMENT 'Năm bắt đầu',
  completion_year INT COMMENT 'Năm hoàn thành',
  investment_billion_vnd DECIMAL(10,2) COMMENT 'Giá trị đầu tư (tỷ VND)',
  expected_loss_reduction_pct DECIMAL(5,2) COMMENT 'Dự kiến giảm tổn thất (điểm %)',
  actual_loss_reduction_pct DECIMAL(5,2) COMMENT 'Thực tế giảm tổn thất (điểm %) — NULL nếu chưa đánh giá',
  expected_saidi_reduction_pct DECIMAL(5,2) COMMENT 'Dự kiến giảm SAIDI (%)',
  status VARCHAR(20) COMMENT 'Trạng thái: Đang triển khai / Hoàn thành / Chậm tiến độ',
  FOREIGN KEY (pc_id) REFERENCES power_companies(pc_id),
  FOREIGN KEY (district_id) REFERENCES districts(district_id),
  INDEX idx_inv_pc (pc_id),
  INDEX idx_inv_type (project_type)
) COMMENT = 'Lịch sử đầu tư xây dựng — phục vụ phân tích ROI và tối ưu phân bổ ngân sách';

CREATE TABLE IF NOT EXISTS operating_costs (
  cost_id INT AUTO_INCREMENT PRIMARY KEY,
  pc_id VARCHAR(4) NOT NULL COMMENT 'FK → power_companies',
  report_month DATE NOT NULL COMMENT 'Tháng báo cáo',
  cost_category VARCHAR(50) NOT NULL COMMENT 'Loại chi phí: Sửa chữa thường xuyên / Sửa chữa lớn / Nhân công / Khấu hao / Khắc phục thiên tai / Vật tư / Điện tự dùng / Khác',
  amount_million_vnd DECIMAL(12,1) NOT NULL COMMENT 'Số tiền (triệu VND)',
  notes TEXT COMMENT 'Ghi chú',
  FOREIGN KEY (pc_id) REFERENCES power_companies(pc_id),
  UNIQUE KEY uk_cost (pc_id, report_month, cost_category),
  INDEX idx_cost_pc_month (pc_id, report_month)
) COMMENT = 'Chi phí vận hành theo PC × tháng × loại chi phí';

-- =============================================
-- METADATA TABLES
-- =============================================

CREATE TABLE IF NOT EXISTS _meta_tables (
  table_name VARCHAR(50) PRIMARY KEY,
  description_vi TEXT,
  description_en TEXT,
  business_context TEXT,
  row_count_estimate INT
) COMMENT = 'Metadata: mô tả các bảng trong database';

CREATE TABLE IF NOT EXISTS _meta_columns (
  id INT AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(50),
  column_name VARCHAR(50),
  data_type VARCHAR(30),
  description_vi TEXT,
  description_en TEXT,
  unit VARCHAR(20),
  example_values TEXT
) COMMENT = 'Metadata: mô tả chi tiết từng cột';

CREATE TABLE IF NOT EXISTS _meta_kpi (
  kpi_name VARCHAR(50) PRIMARY KEY,
  formula_sql TEXT,
  description_vi TEXT,
  related_questions TEXT,
  benchmark_good VARCHAR(50),
  benchmark_warning VARCHAR(50),
  benchmark_alert VARCHAR(50)
) COMMENT = 'Metadata: công thức SQL cho các KPI';

CREATE TABLE IF NOT EXISTS _meta_glossary (
  term_vi VARCHAR(100) PRIMARY KEY,
  term_en VARCHAR(100),
  abbreviation VARCHAR(20),
  definition TEXT,
  related_table VARCHAR(50),
  related_column VARCHAR(50)
) COMMENT = 'Metadata: thuật ngữ ngành điện lực VN ↔ EN';
