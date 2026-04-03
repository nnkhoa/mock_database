-- ============================================================================
-- SASCO Demo Database - DDL Schema
-- Mo ta: Tao database, tables, indexes, constraints cho SASCO demo
-- Database: sasco_demo
-- Encoding: UTF-8 (utf8mb4)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS sasco_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sasco_demo;

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- 1. terminals - Nha ga / san bay
CREATE TABLE terminals (
    terminal_id TINYINT UNSIGNED PRIMARY KEY COMMENT 'Ma nha ga',
    terminal_name VARCHAR(100) NOT NULL COMMENT 'Ten nha ga - tieng Viet',
    terminal_code VARCHAR(10) NOT NULL COMMENT 'Ma viet tat (T1, T2, T3, CR, PQ)',
    airport_name VARCHAR(100) NOT NULL COMMENT 'Ten san bay',
    airport_code VARCHAR(5) NOT NULL COMMENT 'Ma IATA san bay (SGN, CXR, PQC)',
    terminal_type ENUM('Quoc te', 'Noi dia', 'Hon hop') NOT NULL COMMENT 'Loai nha ga: Quoc te, Noi dia, Hon hop',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Dang hoat dong',
    open_date DATE COMMENT 'Ngay bat dau khai thac'
) COMMENT = 'Nhà ga / sân bay nơi SASCO vận hành dịch vụ';

-- 2. business_lines - Mang kinh doanh
CREATE TABLE business_lines (
    business_line_id TINYINT UNSIGNED PRIMARY KEY COMMENT 'Ma mang kinh doanh',
    business_line_name VARCHAR(100) NOT NULL COMMENT 'Ten mang - tieng Viet',
    business_line_code VARCHAR(20) NOT NULL COMMENT 'Ma viet tat',
    description TEXT COMMENT 'Mo ta chi tiet mang kinh doanh'
) COMMENT = 'Các mảng kinh doanh chính của SASCO';

-- 3. locations - Diem kinh doanh cu the
CREATE TABLE locations (
    location_id SMALLINT UNSIGNED PRIMARY KEY COMMENT 'Ma diem kinh doanh',
    location_name VARCHAR(150) NOT NULL COMMENT 'Ten diem kinh doanh - tieng Viet',
    location_code VARCHAR(30) NOT NULL COMMENT 'Ma viet tat',
    terminal_id TINYINT UNSIGNED NOT NULL COMMENT 'FK -> terminals',
    business_line_id TINYINT UNSIGNED NOT NULL COMMENT 'FK -> business_lines',
    location_type VARCHAR(50) NOT NULL COMMENT 'Phan loai chi tiet (phong cho, cua hang DF, nha hang, cafe, shop ban le, dich vu)',
    floor_area_sqm DECIMAL(8,2) COMMENT 'Dien tich san (m2)',
    capacity INT COMMENT 'Suc chua (ghe cho phong cho, hoac NULL)',
    open_date DATE NOT NULL COMMENT 'Ngay bat dau hoat dong',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Dang hoat dong',
    FOREIGN KEY (terminal_id) REFERENCES terminals(terminal_id),
    FOREIGN KEY (business_line_id) REFERENCES business_lines(business_line_id)
) COMMENT = 'Các điểm kinh doanh cụ thể của SASCO (phòng chờ, cửa hàng, nhà hàng, dịch vụ)';

-- 4. lounges - Chi tiet phong cho (extend locations)
CREATE TABLE lounges (
    lounge_id SMALLINT UNSIGNED PRIMARY KEY COMMENT 'Ma phong cho = location_id',
    lounge_type ENUM('Quoc te', 'Noi dia', 'Hon hop') NOT NULL COMMENT 'Loai phong cho: Quoc te, Noi dia, Hon hop',
    brand VARCHAR(50) NOT NULL COMMENT 'Thuong hieu (Lotus Lounge, The SENS)',
    max_capacity_per_hour INT NOT NULL COMMENT 'Suc chua toi da moi gio (luot khach)',
    base_price_vnd INT NOT NULL COMMENT 'Gia phong cho chuan (VND/khach)',
    FOREIGN KEY (lounge_id) REFERENCES locations(location_id)
) COMMENT = 'Thông tin chi tiết phòng chờ thương gia - extend từ locations';

-- 5. nationality_groups - Nhom quoc tich khach
CREATE TABLE nationality_groups (
    nationality_group_id TINYINT UNSIGNED PRIMARY KEY COMMENT 'Ma nhom quoc tich',
    nationality_name VARCHAR(50) NOT NULL COMMENT 'Ten quoc tich - tieng Viet',
    nationality_name_en VARCHAR(50) NOT NULL COMMENT 'Ten quoc tich - tieng Anh',
    region VARCHAR(50) NOT NULL COMMENT 'Khu vuc (Dong Bac A, Dong Nam A, Au My, Nam A, Khac)',
    avg_spend_per_pax_vnd INT NOT NULL COMMENT 'Chi tieu trung binh/khach tai SASCO (VND) - benchmark',
    pax_share_pct DECIMAL(5,2) NOT NULL COMMENT 'Ty trong PAX tai TSN (%) - baseline dau ky'
) COMMENT = 'Nhóm quốc tịch hành khách quốc tế - phục vụ phân tích spend/PAX';

-- 6. product_categories - Danh muc san pham/dich vu
CREATE TABLE product_categories (
    category_id SMALLINT UNSIGNED PRIMARY KEY COMMENT 'Ma danh muc',
    category_name VARCHAR(100) NOT NULL COMMENT 'Ten danh muc - tieng Viet',
    business_line_id TINYINT UNSIGNED NOT NULL COMMENT 'FK -> business_lines',
    parent_category_id SMALLINT UNSIGNED COMMENT 'Danh muc cha (NULL neu top-level)',
    FOREIGN KEY (business_line_id) REFERENCES business_lines(business_line_id),
    FOREIGN KEY (parent_category_id) REFERENCES product_categories(category_id)
) COMMENT = 'Danh mục sản phẩm/dịch vụ - hierarchy 2 cấp';

-- 7. products - San pham/dich vu cu the
CREATE TABLE products (
    product_id INT UNSIGNED PRIMARY KEY COMMENT 'Ma san pham/dich vu',
    product_name VARCHAR(200) NOT NULL COMMENT 'Ten san pham - tieng Viet hoac ten thuong hieu',
    product_code VARCHAR(30) NOT NULL COMMENT 'Ma SKU',
    category_id SMALLINT UNSIGNED NOT NULL COMMENT 'FK -> product_categories',
    unit_price_vnd DECIMAL(12,0) NOT NULL COMMENT 'Gia ban (VND)',
    cost_price_vnd DECIMAL(12,0) NOT NULL COMMENT 'Gia von (VND)',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Dang kinh doanh',
    popularity_weight DECIMAL(5,4) DEFAULT 0.0020 COMMENT 'Trong so pho bien - Pareto (0-1, tong = 1 trong category)',
    nationality_preference VARCHAR(100) COMMENT 'Quoc tich ua thich (JSON array nationality_group_ids, NULL = all)',
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id)
) COMMENT = 'Danh mục sản phẩm/dịch vụ cụ thể (~300-500 SKU)';

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- 8. passenger_traffic - Luu luong hanh khach
CREATE TABLE passenger_traffic (
    traffic_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    traffic_date DATE NOT NULL COMMENT 'Ngay',
    terminal_id TINYINT UNSIGNED NOT NULL COMMENT 'FK -> terminals',
    nationality_group_id TINYINT UNSIGNED NOT NULL COMMENT 'FK -> nationality_groups (0 = noi dia)',
    passenger_type ENUM('Quoc te', 'Noi dia') NOT NULL COMMENT 'Loai hanh khach: Quoc te hoac Noi dia',
    pax_count INT NOT NULL COMMENT 'So luong hanh khach (luot)',
    FOREIGN KEY (terminal_id) REFERENCES terminals(terminal_id),
    INDEX idx_traffic_date_terminal (traffic_date, terminal_id),
    INDEX idx_traffic_date_nationality (traffic_date, nationality_group_id)
) COMMENT = 'Lưu lượng hành khách theo ngày × nhà ga × quốc tịch. Grain: 1 dòng = 1 ngày × 1 terminal × 1 nationality';

-- 9. sales_transactions - Giao dich ban hang
CREATE TABLE sales_transactions (
    transaction_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    transaction_date DATE NOT NULL COMMENT 'Ngay giao dich',
    transaction_time TIME COMMENT 'Gio giao dich (HH:MM:SS)',
    location_id SMALLINT UNSIGNED NOT NULL COMMENT 'FK -> locations',
    business_line_id TINYINT UNSIGNED NOT NULL COMMENT 'FK -> business_lines (denormalized for query speed)',
    terminal_id TINYINT UNSIGNED NOT NULL COMMENT 'FK -> terminals (denormalized)',
    product_id INT UNSIGNED NOT NULL COMMENT 'FK -> products',
    nationality_group_id TINYINT UNSIGNED COMMENT 'FK -> nationality_groups (NULL neu noi dia hoac unknown)',
    quantity INT NOT NULL DEFAULT 1 COMMENT 'So luong',
    unit_price_vnd DECIMAL(12,0) NOT NULL COMMENT 'Don gia ban thuc te (VND)',
    total_revenue_vnd DECIMAL(15,0) NOT NULL COMMENT 'Doanh thu = quantity x unit_price (VND)',
    cost_vnd DECIMAL(15,0) NOT NULL COMMENT 'Gia von (VND)',
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (business_line_id) REFERENCES business_lines(business_line_id),
    FOREIGN KEY (terminal_id) REFERENCES terminals(terminal_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_sales_date_bl (transaction_date, business_line_id),
    INDEX idx_sales_date_terminal (transaction_date, terminal_id),
    INDEX idx_sales_date_nationality (transaction_date, nationality_group_id),
    INDEX idx_sales_location (location_id, transaction_date)
) COMMENT = 'Giao dịch bán hàng chi tiết. Grain: 1 dòng = 1 line item. Bao gồm tất cả mảng KD.';

-- 10. lounge_visits - Luot su dung phong cho
CREATE TABLE lounge_visits (
    visit_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    visit_date DATE NOT NULL COMMENT 'Ngay',
    hour_slot TINYINT UNSIGNED NOT NULL COMMENT 'Khung gio (0-23)',
    lounge_id SMALLINT UNSIGNED NOT NULL COMMENT 'FK -> lounges',
    terminal_id TINYINT UNSIGNED NOT NULL COMMENT 'FK -> terminals (denormalized)',
    guest_count INT NOT NULL COMMENT 'So luot khach trong khung gio',
    capacity INT NOT NULL COMMENT 'Suc chua khung gio do (ghe)',
    utilization_rate DECIMAL(5,2) COMMENT 'guest_count / capacity x 100 (%)',
    FOREIGN KEY (lounge_id) REFERENCES lounges(lounge_id),
    FOREIGN KEY (terminal_id) REFERENCES terminals(terminal_id),
    INDEX idx_lounge_date (lounge_id, visit_date),
    INDEX idx_lounge_date_hour (lounge_id, visit_date, hour_slot)
) COMMENT = 'Lượt sử dụng phòng chờ theo giờ. Grain: 1 dòng = 1 phòng chờ × 1 ngày × 1 khung giờ.';

-- ============================================================================
-- METADATA TABLES
-- ============================================================================

-- 11. _meta_tables
CREATE TABLE _meta_tables (
    table_name VARCHAR(100) PRIMARY KEY,
    description_vi TEXT NOT NULL,
    description_en TEXT,
    business_context TEXT,
    record_count_estimate INT
) COMMENT = 'Metadata mô tả các bảng trong database';

-- 12. _meta_columns
CREATE TABLE _meta_columns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    description_vi TEXT NOT NULL,
    description_en TEXT,
    unit VARCHAR(30),
    example_values TEXT
) COMMENT = 'Metadata mô tả các cột trong từng bảng';

-- 13. _meta_kpi
CREATE TABLE _meta_kpi (
    kpi_name VARCHAR(100) PRIMARY KEY,
    formula_sql TEXT NOT NULL,
    description_vi TEXT NOT NULL,
    related_questions TEXT
) COMMENT = 'Công thức KPI cốt lõi - AI dùng để tính toán';

-- 14. _meta_glossary
CREATE TABLE _meta_glossary (
    term_vi VARCHAR(100) PRIMARY KEY,
    term_en VARCHAR(100),
    definition TEXT NOT NULL
) COMMENT = 'Thuật ngữ ngành - AI dùng để hiểu câu hỏi tiếng Việt';
