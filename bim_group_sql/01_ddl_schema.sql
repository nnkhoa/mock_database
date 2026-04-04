-- ============================================================================
-- BIM Group Real Estate & Construction Demo - DDL Schema
-- Mo ta: Tao database, tables, indexes, constraints
-- Database: bim_realestate_demo
-- Encoding: UTF-8 (utf8mb4)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS bim_realestate_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE bim_realestate_demo;

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- 1. clusters - Cum du an theo vung dia ly
CREATE TABLE clusters (
    cluster_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma cum du an (CL-HL, CL-PQ, CL-HN, CL-LA)',
    cluster_name VARCHAR(50) NOT NULL COMMENT 'Ten cum - tieng Viet',
    region VARCHAR(50) NOT NULL COMMENT 'Vung mien (Mien Bac, Mien Nam, Dong Nam A)',
    city VARCHAR(50) NOT NULL COMMENT 'Thanh pho',
    country VARCHAR(50) NOT NULL DEFAULT 'Viet Nam' COMMENT 'Quoc gia'
) COMMENT = 'Cụm dự án theo vùng địa lý: Hạ Long, Phú Quốc, Hà Nội, Viêng Chăn';

-- 2. projects - Du an BDS dang trien khai
CREATE TABLE projects (
    project_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma du an (PJ-HL01, PJ-PQ01...)',
    project_name VARCHAR(200) NOT NULL COMMENT 'Ten du an - tieng Viet',
    cluster_id VARCHAR(10) NOT NULL COMMENT 'FK -> clusters',
    project_type VARCHAR(50) NOT NULL COMMENT 'Loai du an (Resort+Residences, Biet thu, To hop, Khu do thi, Giai tri)',
    total_budget BIGINT NOT NULL COMMENT 'Tong ngan sach (VND)',
    total_gfa INT NOT NULL COMMENT 'Tong dien tich san (m2 - Gross Floor Area)',
    planned_start DATE NOT NULL COMMENT 'Ngay bat dau ke hoach',
    planned_end DATE NOT NULL COMMENT 'Ngay ket thuc ke hoach',
    actual_progress_pct DECIMAL(5,2) NOT NULL DEFAULT 0 COMMENT 'Tien do thuc te (%)',
    planned_progress_pct DECIMAL(5,2) NOT NULL DEFAULT 0 COMMENT 'Tien do ke hoach (%)',
    status VARCHAR(30) NOT NULL COMMENT 'Trang thai: Dang xay dung, Hoan thien, Chuan bi',
    brand_partner VARCHAR(50) COMMENT 'Doi tac thuong hieu quoc te (IHG, Hyatt...)',
    FOREIGN KEY (cluster_id) REFERENCES clusters(cluster_id),
    INDEX idx_projects_cluster (cluster_id),
    INDEX idx_projects_status (status)
) COMMENT = 'Dự án BĐS đang triển khai - 8 dự án tại 4 cluster';

-- 3. properties - BDS dang van hanh (resort/hotel)
CREATE TABLE properties (
    property_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma BDS van hanh (PR-PQ01...)',
    property_name VARCHAR(200) NOT NULL COMMENT 'Ten BDS - tieng Viet/Anh',
    cluster_id VARCHAR(10) NOT NULL COMMENT 'FK -> clusters',
    rooms INT NOT NULL COMMENT 'So phong/can ho',
    brand_partner VARCHAR(50) NOT NULL COMMENT 'Doi tac quan ly thuong hieu',
    opening_year INT NOT NULL COMMENT 'Nam khai truong',
    property_type VARCHAR(50) NOT NULL COMMENT 'Loai BDS (Resort 6*, Resort 5*, Can ho DV, Khach san 5*)',
    FOREIGN KEY (cluster_id) REFERENCES clusters(cluster_id),
    INDEX idx_properties_cluster (cluster_id)
) COMMENT = 'BĐS đang vận hành (resort/hotel) - 6 property tại 4 cluster';

-- 4. work_packages - Hang muc cong viec xay dung
CREATE TABLE work_packages (
    work_package_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma hang muc (WP-01...WP-08)',
    work_package_name VARCHAR(100) NOT NULL COMMENT 'Ten hang muc - tieng Anh',
    category_vi VARCHAR(100) NOT NULL COMMENT 'Ten hang muc - tieng Viet',
    budget_weight_pct DECIMAL(5,2) NOT NULL COMMENT 'Ty trong ngan sach chuan (%)'
) COMMENT = 'Hạng mục công việc xây dựng - 8 loại (móng, M&E, nội thất...)';

-- 5. contractors - Nha thau xay dung
CREATE TABLE contractors (
    contractor_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma nha thau (CT-01...CT-18)',
    contractor_name VARCHAR(100) NOT NULL COMMENT 'Ten nha thau - tieng Viet',
    specialty VARCHAR(100) NOT NULL COMMENT 'Chuyen mon chinh',
    region VARCHAR(50) NOT NULL COMMENT 'Vung hoat dong'
) COMMENT = 'Nhà thầu xây dựng - 18 nhà thầu đa chuyên ngành';

-- 6. materials - Vat lieu xay dung chinh
CREATE TABLE materials (
    material_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma vat lieu (MAT-01...MAT-06)',
    material_name VARCHAR(100) NOT NULL COMMENT 'Ten vat lieu - tieng Viet',
    unit VARCHAR(30) NOT NULL COMMENT 'Don vi do (VND/kg, VND/tan, VND/m2, VND/m3)'
) COMMENT = 'Vật liệu xây dựng chính - 6 loại theo dõi giá';

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- 7. budget_disbursements - Ngan sach giai ngan monthly
CREATE TABLE budget_disbursements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10) NOT NULL COMMENT 'FK -> projects',
    period VARCHAR(7) NOT NULL COMMENT 'Ky bao cao (YYYY-MM)',
    planned_amount BIGINT NOT NULL COMMENT 'Ngan sach ke hoach thang (VND)',
    actual_amount BIGINT NOT NULL COMMENT 'Giai ngan thuc te thang (VND)',
    cumulative_planned BIGINT NOT NULL COMMENT 'Luy ke ke hoach (VND)',
    cumulative_actual BIGINT NOT NULL COMMENT 'Luy ke thuc te (VND)',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    INDEX idx_bd_project_period (project_id, period),
    UNIQUE KEY uq_bd_project_period (project_id, period)
) COMMENT = 'Ngân sách giải ngân hàng tháng theo dự án - grain: project x month';

-- 8. construction_costs - Chi phi xay dung chi tiet
CREATE TABLE construction_costs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10) NOT NULL COMMENT 'FK -> projects',
    work_package_id VARCHAR(10) NOT NULL COMMENT 'FK -> work_packages',
    contractor_id VARCHAR(10) NOT NULL COMMENT 'FK -> contractors',
    period VARCHAR(7) NOT NULL COMMENT 'Ky bao cao (YYYY-MM)',
    budgeted_cost BIGINT NOT NULL COMMENT 'Chi phi du toan thang (VND)',
    actual_cost BIGINT NOT NULL COMMENT 'Chi phi thuc te thang (VND)',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (work_package_id) REFERENCES work_packages(work_package_id),
    FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id),
    INDEX idx_cc_project_period (project_id, period),
    INDEX idx_cc_contractor (contractor_id, project_id),
    INDEX idx_cc_wp (work_package_id, project_id)
) COMMENT = 'Chi phí xây dựng chi tiết - grain: project x work_package x contractor x month';

-- 9. change_orders - Phat sinh thay doi thiet ke
CREATE TABLE change_orders (
    change_order_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma phat sinh (CO-001...)',
    project_id VARCHAR(10) NOT NULL COMMENT 'FK -> projects',
    work_package_id VARCHAR(10) NOT NULL COMMENT 'FK -> work_packages',
    contractor_id VARCHAR(10) NOT NULL COMMENT 'FK -> contractors',
    reason VARCHAR(500) NOT NULL COMMENT 'Ly do phat sinh',
    reason_category VARCHAR(50) NOT NULL COMMENT 'Phan loai: Brand compliance, Bien dong gia, Thiet ke, Khac',
    amount BIGINT NOT NULL COMMENT 'Gia tri phat sinh (VND)',
    order_date DATE NOT NULL COMMENT 'Ngay phat sinh',
    status VARCHAR(30) NOT NULL DEFAULT 'Da duyet' COMMENT 'Trang thai: Da duyet, Cho duyet, Tu choi',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (work_package_id) REFERENCES work_packages(work_package_id),
    FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id),
    INDEX idx_co_project (project_id)
) COMMENT = 'Phát sinh thay đổi thiết kế/yêu cầu - per event';

-- 10. material_prices - Gia vat lieu monthly
CREATE TABLE material_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    material_id VARCHAR(10) NOT NULL COMMENT 'FK -> materials',
    period VARCHAR(7) NOT NULL COMMENT 'Ky bao cao (YYYY-MM)',
    price BIGINT NOT NULL COMMENT 'Gia don vi (VND theo unit cua material)',
    FOREIGN KEY (material_id) REFERENCES materials(material_id),
    UNIQUE KEY uq_mp_material_period (material_id, period)
) COMMENT = 'Giá vật liệu xây dựng hàng tháng - grain: material x month';

-- 11. project_milestones - Moc tien do
CREATE TABLE project_milestones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10) NOT NULL COMMENT 'FK -> projects',
    milestone_name VARCHAR(200) NOT NULL COMMENT 'Ten moc tien do - tieng Viet',
    planned_date DATE NOT NULL COMMENT 'Ngay ke hoach',
    actual_date DATE COMMENT 'Ngay thuc te (NULL neu chua dat)',
    status VARCHAR(30) NOT NULL COMMENT 'Trang thai: Hoan thanh, Dang thuc hien, Chua bat dau, Tre han',
    progress_pct DECIMAL(5,2) NOT NULL DEFAULT 0 COMMENT 'Tien do tuong ung khi dat moc (%)',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    INDEX idx_pm_project (project_id)
) COMMENT = 'Mốc tiến độ dự án - 5-8 milestones mỗi dự án';

-- 12. project_financials - Chi so tai chinh du an
CREATE TABLE project_financials (
    project_id VARCHAR(10) PRIMARY KEY COMMENT 'FK -> projects',
    total_investment BIGINT NOT NULL COMMENT 'Tong von dau tu (VND) - bao gom dat, XD, tai chinh',
    construction_cost_per_sqm BIGINT NOT NULL COMMENT 'Chi phi xay dung tren m2 (VND/m2)',
    expected_revenue BIGINT NOT NULL COMMENT 'Doanh thu du kien (VND)',
    expected_margin_pct DECIMAL(5,2) NOT NULL COMMENT 'Bien loi nhuan du kien (%)',
    estimated_irr_pct DECIMAL(5,2) COMMENT 'IRR uoc tinh (%)',
    payback_years DECIMAL(4,1) COMMENT 'Thoi gian hoan von (nam)',
    cost_variance_pct DECIMAL(5,2) NOT NULL DEFAULT 0 COMMENT 'Ty le vuot du toan (%)',
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
) COMMENT = 'Chỉ số tài chính tổng hợp mỗi dự án - so sánh hiệu quả đầu tư';

-- 13. project_commitments - Cam ket ban giao khach hang
CREATE TABLE project_commitments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10) NOT NULL COMMENT 'FK -> projects',
    commitment_type VARCHAR(100) NOT NULL COMMENT 'Loai cam ket (Ban giao can ho, Ban giao biet thu...)',
    units_committed INT NOT NULL COMMENT 'So don vi cam ket ban giao',
    commitment_date DATE NOT NULL COMMENT 'Han ban giao cam ket',
    has_penalty BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Co dieu khoan phat tre khong',
    penalty_rate_pct DECIMAL(5,2) COMMENT 'Ty le phat tre (%/thang)',
    notes VARCHAR(500) COMMENT 'Ghi chu them',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    INDEX idx_pc_project (project_id)
) COMMENT = 'Cam kết bàn giao khách hàng - dự án có deadline và penalty';

-- 14. financing - Khoan vay tung du an
CREATE TABLE financing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10) NOT NULL COMMENT 'FK -> projects',
    lender VARCHAR(100) NOT NULL COMMENT 'Ngan hang/to chuc cho vay',
    loan_amount BIGINT NOT NULL COMMENT 'Han muc vay (VND)',
    loan_outstanding BIGINT NOT NULL COMMENT 'Du no hien tai (VND)',
    annual_interest_rate_pct DECIMAL(5,2) NOT NULL COMMENT 'Lai suat nam (%)',
    start_date DATE NOT NULL COMMENT 'Ngay giai ngan',
    maturity_date DATE NOT NULL COMMENT 'Ngay dao han',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    INDEX idx_fin_project (project_id)
) COMMENT = 'Khoản vay từng dự án - tính chi phí tài chính khi delay';

-- 15. hospitality_revenue - Doanh thu van hanh monthly
CREATE TABLE hospitality_revenue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id VARCHAR(10) NOT NULL COMMENT 'FK -> properties',
    period VARCHAR(7) NOT NULL COMMENT 'Ky bao cao (YYYY-MM)',
    room_revenue BIGINT NOT NULL COMMENT 'Doanh thu phong (VND)',
    fnb_revenue BIGINT NOT NULL COMMENT 'Doanh thu F&B (VND)',
    other_revenue BIGINT NOT NULL COMMENT 'Doanh thu khac - spa, event... (VND)',
    total_revenue BIGINT NOT NULL COMMENT 'Tong doanh thu (VND)',
    rooms_available INT NOT NULL COMMENT 'Tong phong kha dung trong thang',
    rooms_sold INT NOT NULL COMMENT 'Tong phong ban trong thang',
    avg_daily_rate BIGINT NOT NULL COMMENT 'Gia phong trung binh/dem (VND) - ADR',
    FOREIGN KEY (property_id) REFERENCES properties(property_id),
    INDEX idx_hr_property_period (property_id, period),
    UNIQUE KEY uq_hr_property_period (property_id, period)
) COMMENT = 'Doanh thu vận hành hospitality hàng tháng - grain: property x month';

-- 16. hospitality_costs - Chi phi van hanh monthly
CREATE TABLE hospitality_costs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id VARCHAR(10) NOT NULL COMMENT 'FK -> properties',
    period VARCHAR(7) NOT NULL COMMENT 'Ky bao cao (YYYY-MM)',
    cost_category VARCHAR(50) NOT NULL COMMENT 'Loai chi phi: Nhan su, Dien nuoc, Bao tri, Marketing, Phi quan ly, Khac',
    cost_amount BIGINT NOT NULL COMMENT 'Chi phi (VND)',
    FOREIGN KEY (property_id) REFERENCES properties(property_id),
    INDEX idx_hc_property_period (property_id, period)
) COMMENT = 'Chi phí vận hành hospitality hàng tháng - grain: property x month x cost_category';

-- 17. occupancy_daily - Du lieu phong hang ngay
CREATE TABLE occupancy_daily (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id VARCHAR(10) NOT NULL COMMENT 'FK -> properties',
    date DATE NOT NULL COMMENT 'Ngay',
    rooms_available INT NOT NULL COMMENT 'Phong kha dung',
    rooms_sold INT NOT NULL COMMENT 'Phong da ban',
    avg_rate BIGINT NOT NULL COMMENT 'Gia phong trung binh ngay do (VND)',
    FOREIGN KEY (property_id) REFERENCES properties(property_id),
    INDEX idx_od_property_date (property_id, date),
    UNIQUE KEY uq_od_property_date (property_id, date)
) COMMENT = 'Dữ liệu phòng hàng ngày - grain: property x date, phục vụ phân tích seasonality';

-- ============================================================================
-- METADATA TABLES
-- ============================================================================

-- _meta_tables - Mo ta moi bang
CREATE TABLE _meta_tables (
    table_name VARCHAR(100) PRIMARY KEY COMMENT 'Ten bang',
    description_vi TEXT NOT NULL COMMENT 'Mo ta bang - tieng Viet',
    table_type VARCHAR(20) NOT NULL COMMENT 'Loai: dimension, fact, metadata',
    grain VARCHAR(200) COMMENT 'Don vi du lieu (vd: project x month)',
    row_count_estimate INT COMMENT 'So dong uoc tinh'
) COMMENT = 'Metadata: mô tả mỗi bảng trong database - nguồn truth cho AI engine';

-- _meta_columns - Mo ta moi cot
CREATE TABLE _meta_columns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL COMMENT 'Ten bang',
    column_name VARCHAR(100) NOT NULL COMMENT 'Ten cot',
    description_vi TEXT NOT NULL COMMENT 'Mo ta cot - tieng Viet',
    data_type VARCHAR(50) NOT NULL COMMENT 'Kieu du lieu',
    unit VARCHAR(30) COMMENT 'Don vi (VND, m2, %, ngay...)',
    is_key BOOLEAN DEFAULT FALSE COMMENT 'La khoa chinh hoac khoa ngoai',
    example_value VARCHAR(200) COMMENT 'Gia tri mau',
    UNIQUE KEY uq_mc_table_column (table_name, column_name)
) COMMENT = 'Metadata: mô tả mỗi cột - giúp AI engine hiểu ý nghĩa dữ liệu';

-- _meta_kpi - Cong thuc KPI
CREATE TABLE _meta_kpi (
    kpi_name VARCHAR(100) PRIMARY KEY COMMENT 'Ten KPI (tieng Anh)',
    formula_sql TEXT NOT NULL COMMENT 'Cong thuc SQL de tinh KPI',
    description_vi TEXT NOT NULL COMMENT 'Mo ta KPI - tieng Viet',
    related_tables VARCHAR(500) COMMENT 'Cac bang lien quan',
    category VARCHAR(50) COMMENT 'Nhom KPI: Ngan sach, Tien do, Hospitality, Tai chinh'
) COMMENT = 'Metadata: công thức KPI - nguồn truth để AI engine tính toán chính xác';

-- _meta_glossary - Thuat ngu nganh
CREATE TABLE _meta_glossary (
    term VARCHAR(100) PRIMARY KEY COMMENT 'Thuat ngu (tieng Anh hoac tieng Viet)',
    definition_vi TEXT NOT NULL COMMENT 'Dinh nghia - tieng Viet',
    related_kpi VARCHAR(200) COMMENT 'KPI lien quan',
    context VARCHAR(200) COMMENT 'Ngu canh su dung'
) COMMENT = 'Metadata: thuật ngữ ngành BĐS & xây dựng - giúp AI hiểu câu hỏi tiếng Việt';
