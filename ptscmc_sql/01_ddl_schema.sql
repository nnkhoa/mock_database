-- ============================================================
-- PTSC M&C Demo Database — DDL Schema
-- Database: ptsc_mc_demo
-- Encoding: UTF-8 (utf8mb4)
-- ============================================================

CREATE DATABASE IF NOT EXISTS ptsc_mc_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ptsc_mc_demo;

-- ============================================================
-- DIMENSION TABLES (Master Data)
-- ============================================================

-- Clients (Chủ đầu tư)
CREATE TABLE IF NOT EXISTS clients (
    client_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã chủ đầu tư',
    client_name VARCHAR(200) NOT NULL COMMENT 'Tên chủ đầu tư',
    country VARCHAR(50) NOT NULL COMMENT 'Quốc gia',
    sector VARCHAR(50) COMMENT 'Lĩnh vực (O&G, Renewables, v.v.)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Danh sách chủ đầu tư (clients/operators)';

-- Projects (5 dự án giả lập)
CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(10) PRIMARY KEY COMMENT 'Mã dự án (PJ-001..PJ-005)',
    project_name VARCHAR(200) NOT NULL COMMENT 'Tên dự án đầy đủ',
    project_code VARCHAR(20) NOT NULL COMMENT 'Mã viết tắt',
    project_type ENUM('O&G', 'Renewables') NOT NULL COMMENT 'Loại dự án: O&G hoặc Năng lượng tái tạo',
    client_id VARCHAR(20) NOT NULL COMMENT 'FK tới clients',
    contract_value_usd DECIMAL(15,2) NOT NULL COMMENT 'Giá trị hợp đồng (triệu USD)',
    start_date DATE NOT NULL COMMENT 'Ngày bắt đầu dự án',
    planned_end_date DATE NOT NULL COMMENT 'Ngày kết thúc dự kiến',
    duration_months INT NOT NULL COMMENT 'Thời gian dự kiến (tháng)',
    location VARCHAR(100) NOT NULL COMMENT 'Địa điểm thi công (VN/Qatar/...)',
    contract_type ENUM('Lump Sum', 'Reimbursable') NOT NULL COMMENT 'Loại hợp đồng',
    description TEXT COMMENT 'Mô tả ngắn dự án',
    status VARCHAR(50) DEFAULT 'Active' COMMENT 'Trạng thái dự án',
    FOREIGN KEY (client_id) REFERENCES clients(client_id),
    INDEX idx_project_type (project_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='5 dự án EPC/EPCIC giả lập của PTSC M&C';

-- Disciplines (7 chuyên ngành)
CREATE TABLE IF NOT EXISTS disciplines (
    discipline_id VARCHAR(10) PRIMARY KEY COMMENT 'Mã chuyên ngành',
    discipline_name VARCHAR(50) NOT NULL COMMENT 'Tên chuyên ngành (tiếng Anh)',
    description TEXT COMMENT 'Mô tả công việc chuyên ngành',
    sequence_order INT COMMENT 'Thứ tự trong quy trình thi công (1=đầu tiên)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Các chuyên ngành thi công: Structural, Piping, Electrical, ...';

-- Cost Categories (10 loại chi phí)
CREATE TABLE IF NOT EXISTS cost_categories (
    cost_category_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã loại chi phí',
    category_name VARCHAR(100) NOT NULL COMMENT 'Tên loại chi phí',
    parent_category VARCHAR(20) COMMENT 'Nhóm cha (LABOR, MATERIAL, SUBCONTRACTOR, OVERHEAD)',
    description TEXT COMMENT 'Mô tả chi tiết'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Phân loại chi phí dự án: nhân công, vật tư, thầu phụ, overhead';

-- Suppliers (10 nhà cung cấp)
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã nhà cung cấp',
    supplier_name VARCHAR(200) NOT NULL COMMENT 'Tên nhà cung cấp',
    country VARCHAR(50) NOT NULL COMMENT 'Quốc gia',
    specialization VARCHAR(200) COMMENT 'Chuyên môn / sản phẩm chính'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Nhà cung cấp vật tư (thép, ống, thiết bị)';

-- Work Areas (khu vực thi công per project)
CREATE TABLE IF NOT EXISTS work_areas (
    area_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã khu vực',
    project_id VARCHAR(10) NOT NULL COMMENT 'FK tới projects',
    area_name VARCHAR(200) NOT NULL COMMENT 'Tên khu vực thi công',
    description TEXT COMMENT 'Mô tả khu vực',
    scope_weight DECIMAL(5,2) DEFAULT 0.25 COMMENT 'Tỷ trọng khối lượng công việc (0-1)',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    INDEX idx_wa_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Khu vực thi công trong yard cho mỗi dự án (Module, Bay, Phase)';

-- Workforce (200 nhân sự mẫu)
CREATE TABLE IF NOT EXISTS workforce (
    worker_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã nhân viên',
    worker_name VARCHAR(100) NOT NULL COMMENT 'Họ tên (tiếng Việt)',
    skill_type VARCHAR(50) NOT NULL COMMENT 'Loại kỹ năng chính (Welder, Pipefitter, ...)',
    certification VARCHAR(200) COMMENT 'Chứng chỉ nghề (6G SMAW, Duplex SS, ...)',
    current_project_id VARCHAR(10) COMMENT 'Dự án đang được phân bổ',
    hire_date DATE COMMENT 'Ngày vào làm',
    FOREIGN KEY (current_project_id) REFERENCES projects(project_id),
    INDEX idx_wf_skill (skill_type),
    INDEX idx_wf_project (current_project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Danh sách nhân sự (200 workers): thợ hàn, thợ ống, kỹ sư, QC, ...';

-- ============================================================
-- FACT TABLES (Transaction Data)
-- ============================================================

-- Project Progress (monthly snapshots)
CREATE TABLE IF NOT EXISTS project_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10) NOT NULL COMMENT 'FK tới projects',
    report_month DATE NOT NULL COMMENT 'Tháng báo cáo (ngày 1 của tháng)',
    planned_pct DECIMAL(5,2) NOT NULL COMMENT 'Tiến độ kế hoạch lũy kế (%)',
    actual_pct DECIMAL(5,2) NOT NULL COMMENT 'Tiến độ thực tế lũy kế (%)',
    planned_value_usd DECIMAL(15,2) COMMENT 'Planned Value — EVM (USD)',
    earned_value_usd DECIMAL(15,2) COMMENT 'Earned Value — EVM (USD)',
    notes TEXT COMMENT 'Ghi chú tiến độ tháng',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    UNIQUE KEY uk_pp (project_id, report_month),
    INDEX idx_pp_month (report_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Tiến độ tổng thể dự án theo tháng (planned vs actual %)';

-- Discipline Progress (monthly by discipline)
CREATE TABLE IF NOT EXISTS discipline_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10) NOT NULL COMMENT 'FK tới projects',
    discipline_id VARCHAR(10) NOT NULL COMMENT 'FK tới disciplines',
    report_month DATE NOT NULL COMMENT 'Tháng báo cáo',
    planned_pct DECIMAL(5,2) NOT NULL COMMENT 'Tiến độ kế hoạch lũy kế discipline (%)',
    actual_pct DECIMAL(5,2) NOT NULL COMMENT 'Tiến độ thực tế lũy kế discipline (%)',
    planned_mh DECIMAL(12,2) COMMENT 'Manhour kế hoạch tháng này',
    earned_mh DECIMAL(12,2) COMMENT 'Manhour earned (theo tiến độ thực tế)',
    actual_mh DECIMAL(12,2) COMMENT 'Manhour thực tế sử dụng',
    weight_in_project DECIMAL(5,2) COMMENT 'Tỷ trọng discipline trong dự án (%)',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (discipline_id) REFERENCES disciplines(discipline_id),
    UNIQUE KEY uk_dp (project_id, discipline_id, report_month),
    INDEX idx_dp_month (report_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Tiến độ theo chuyên ngành mỗi tháng (planned/actual % + manhour)';

-- Manhour Logs (monthly by project x discipline x work_area)
CREATE TABLE IF NOT EXISTS manhour_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10) NOT NULL COMMENT 'FK tới projects',
    discipline_id VARCHAR(10) NOT NULL COMMENT 'FK tới disciplines',
    work_area_id VARCHAR(20) NOT NULL COMMENT 'FK tới work_areas',
    report_month DATE NOT NULL COMMENT 'Tháng báo cáo',
    planned_mh DECIMAL(12,2) NOT NULL COMMENT 'Manhour kế hoạch (giờ)',
    actual_mh DECIMAL(12,2) NOT NULL COMMENT 'Manhour thực tế (giờ)',
    overtime_mh DECIMAL(12,2) DEFAULT 0 COMMENT 'Manhour ngoài giờ (giờ)',
    earned_mh DECIMAL(12,2) NOT NULL COMMENT 'Manhour earned theo tiến độ (giờ)',
    headcount INT COMMENT 'Số lượng công nhân trung bình trong tháng',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (discipline_id) REFERENCES disciplines(discipline_id),
    FOREIGN KEY (work_area_id) REFERENCES work_areas(area_id),
    UNIQUE KEY uk_mh (project_id, discipline_id, work_area_id, report_month),
    INDEX idx_mh_month (report_month),
    INDEX idx_mh_project_month (project_id, report_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chi tiết manhour theo dự án x chuyên ngành x khu vực x tháng';

-- Project Costs (monthly by project x cost_category)
CREATE TABLE IF NOT EXISTS project_costs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10) NOT NULL COMMENT 'FK tới projects',
    cost_category_id VARCHAR(20) NOT NULL COMMENT 'FK tới cost_categories',
    report_month DATE NOT NULL COMMENT 'Tháng báo cáo',
    budgeted_amount DECIMAL(15,2) NOT NULL COMMENT 'Ngân sách tháng (USD)',
    actual_amount DECIMAL(15,2) NOT NULL COMMENT 'Chi phí thực tế tháng (USD)',
    committed_amount DECIMAL(15,2) DEFAULT 0 COMMENT 'Chi phí đã cam kết (PO đã phát hành, USD)',
    forecast_amount DECIMAL(15,2) COMMENT 'Dự báo chi phí tháng (USD)',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (cost_category_id) REFERENCES cost_categories(cost_category_id),
    UNIQUE KEY uk_pc (project_id, cost_category_id, report_month),
    INDEX idx_pc_month (report_month),
    INDEX idx_pc_project_month (project_id, report_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chi phí dự án theo loại x tháng (budget vs actual vs committed)';

-- Material Deliveries (PO-level)
CREATE TABLE IF NOT EXISTS material_deliveries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    po_number VARCHAR(30) NOT NULL COMMENT 'Số Purchase Order',
    project_id VARCHAR(10) NOT NULL COMMENT 'FK tới projects',
    material_type VARCHAR(100) NOT NULL COMMENT 'Loại vật tư (Duplex SS Pipe, Carbon Steel, ...)',
    supplier_id VARCHAR(20) NOT NULL COMMENT 'FK tới suppliers',
    quantity DECIMAL(12,2) NOT NULL COMMENT 'Số lượng (tấn hoặc mét)',
    unit VARCHAR(20) DEFAULT 'ton' COMMENT 'Đơn vị tính',
    budgeted_unit_price DECIMAL(12,2) COMMENT 'Đơn giá dự toán (USD)',
    actual_unit_price DECIMAL(12,2) COMMENT 'Đơn giá thực tế (USD)',
    total_value_usd DECIMAL(15,2) COMMENT 'Tổng giá trị PO (USD)',
    planned_delivery_date DATE NOT NULL COMMENT 'Ngày giao hàng dự kiến',
    actual_delivery_date DATE COMMENT 'Ngày giao hàng thực tế',
    status VARCHAR(30) DEFAULT 'Ordered' COMMENT 'Trạng thái PO (Ordered/In Transit/Delivered/Delivered Late)',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    UNIQUE KEY uk_po (po_number),
    INDEX idx_md_project (project_id),
    INDEX idx_md_supplier (supplier_id),
    INDEX idx_md_material (material_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Theo dõi mua sắm vật tư theo PO (supplier, ngày giao, giá)';

-- Quality Records (monthly by project x discipline)
CREATE TABLE IF NOT EXISTS quality_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10) NOT NULL COMMENT 'FK tới projects',
    discipline_id VARCHAR(10) NOT NULL COMMENT 'FK tới disciplines',
    report_month DATE NOT NULL COMMENT 'Tháng báo cáo',
    total_welds INT DEFAULT 0 COMMENT 'Tổng số mối hàn kiểm tra',
    rejected_welds INT DEFAULT 0 COMMENT 'Số mối hàn bị reject',
    rejection_rate DECIMAL(5,2) COMMENT 'Tỷ lệ reject (%) = rejected/total x 100',
    rework_manhours DECIMAL(10,2) DEFAULT 0 COMMENT 'Manhour sửa chữa/làm lại (giờ)',
    ndt_inspections INT DEFAULT 0 COMMENT 'Số lần kiểm tra NDT (Non-Destructive Testing)',
    ncr_count INT DEFAULT 0 COMMENT 'Số Non-Conformance Reports phát hành',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (discipline_id) REFERENCES disciplines(discipline_id),
    UNIQUE KEY uk_qr (project_id, discipline_id, report_month),
    INDEX idx_qr_month (report_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chất lượng hàn & kiểm tra theo dự án x chuyên ngành x tháng';

-- Safety Incidents (individual records)
CREATE TABLE IF NOT EXISTS safety_incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(10) NOT NULL COMMENT 'FK tới projects',
    incident_date DATE NOT NULL COMMENT 'Ngày xảy ra sự cố',
    incident_type VARCHAR(50) NOT NULL COMMENT 'Loại sự cố (Near Miss, First Aid, Medical Treatment, Lost Time, Fatality)',
    severity VARCHAR(20) NOT NULL COMMENT 'Mức độ nghiêm trọng (Near Miss, Minor, Major, Critical)',
    description TEXT COMMENT 'Mô tả sự cố',
    area_id VARCHAR(20) COMMENT 'FK tới work_areas (nơi xảy ra)',
    discipline_id VARCHAR(10) COMMENT 'Chuyên ngành liên quan',
    manhours_lost DECIMAL(10,2) DEFAULT 0 COMMENT 'Số giờ công mất do sự cố',
    corrective_action TEXT COMMENT 'Hành động khắc phục',
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (area_id) REFERENCES work_areas(area_id),
    FOREIGN KEY (discipline_id) REFERENCES disciplines(discipline_id),
    INDEX idx_si_project (project_id),
    INDEX idx_si_date (incident_date),
    INDEX idx_si_type (incident_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Sự cố an toàn lao động (HSE) — từng sự kiện riêng lẻ';

-- ============================================================
-- METADATA TABLES (cho AI engine)
-- ============================================================

CREATE TABLE IF NOT EXISTS _meta_tables (
    table_name VARCHAR(64) PRIMARY KEY COMMENT 'Tên bảng',
    description_vi TEXT COMMENT 'Mô tả bảng (tiếng Việt)',
    description_en TEXT COMMENT 'Mô tả bảng (tiếng Anh)',
    business_context TEXT COMMENT 'Ngữ cảnh sử dụng trong phân tích BI',
    row_count INT COMMENT 'Số dòng ước tính'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Metadata: mô tả các bảng trong database — dùng cho AI engine';

CREATE TABLE IF NOT EXISTS _meta_columns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(64) NOT NULL COMMENT 'Tên bảng',
    column_name VARCHAR(64) NOT NULL COMMENT 'Tên cột',
    data_type VARCHAR(50) COMMENT 'Kiểu dữ liệu',
    description_vi TEXT COMMENT 'Mô tả cột (tiếng Việt)',
    description_en TEXT COMMENT 'Mô tả cột (tiếng Anh)',
    unit VARCHAR(30) COMMENT 'Đơn vị (%, USD, giờ, ngày, ...)',
    example_values TEXT COMMENT 'Giá trị mẫu',
    UNIQUE KEY uk_mc (table_name, column_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Metadata: mô tả các cột — dùng cho AI engine hiểu ý nghĩa dữ liệu';

CREATE TABLE IF NOT EXISTS _meta_kpi (
    kpi_id VARCHAR(30) PRIMARY KEY COMMENT 'Mã KPI',
    kpi_name VARCHAR(100) NOT NULL COMMENT 'Tên KPI',
    formula_sql TEXT COMMENT 'Công thức SQL để tính KPI',
    description_vi TEXT COMMENT 'Mô tả KPI (tiếng Việt)',
    description_en TEXT COMMENT 'Mô tả KPI (tiếng Anh)',
    related_tables TEXT COMMENT 'Các bảng liên quan',
    related_questions TEXT COMMENT 'Câu hỏi liên quan trong Question Catalog'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Metadata: công thức KPI — dùng cho AI engine tính toán chính xác';

CREATE TABLE IF NOT EXISTS _meta_glossary (
    term_id INT AUTO_INCREMENT PRIMARY KEY,
    term_vi VARCHAR(100) COMMENT 'Thuật ngữ tiếng Việt',
    term_en VARCHAR(100) COMMENT 'Thuật ngữ tiếng Anh',
    abbreviation VARCHAR(20) COMMENT 'Viết tắt',
    definition TEXT COMMENT 'Giải thích chi tiết',
    UNIQUE KEY uk_glossary (term_en)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Metadata: thuật ngữ ngành EPC/offshore — dùng cho AI engine hiểu context';
