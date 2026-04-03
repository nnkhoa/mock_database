-- ============================================================
-- KN Holdings - Bất Động Sản Demo Database
-- 01_ddl.sql - Schema Definition
-- Database: kn_realestate_demo
-- ============================================================

CREATE DATABASE IF NOT EXISTS kn_realestate_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE kn_realestate_demo;

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

-- 1. Dự án
CREATE TABLE projects (
    project_id       VARCHAR(10) NOT NULL COMMENT 'Mã dự án (VD: PRJ-CW)',
    project_name     VARCHAR(100) NOT NULL COMMENT 'Tên dự án',
    project_type     ENUM('resort_township','residential','land','mixed') NOT NULL COMMENT 'Loại dự án',
    location_province VARCHAR(50) NOT NULL COMMENT 'Tỉnh/Thành phố',
    location_district VARCHAR(50) NOT NULL COMMENT 'Quận/Huyện',
    total_area_ha    DECIMAL(10,2) COMMENT 'Tổng diện tích (ha)',
    total_units      INT NOT NULL COMMENT 'Tổng số sản phẩm',
    launch_date      DATE COMMENT 'Ngày mở bán',
    expected_completion DATE COMMENT 'Dự kiến hoàn thành',
    status           ENUM('active_selling','mostly_sold','completed') NOT NULL COMMENT 'Trạng thái dự án',
    partner          VARCHAR(100) COMMENT 'Đối tác phát triển',
    total_investment_billion_vnd DECIMAL(12,2) COMMENT 'Tổng vốn đầu tư (tỷ VND)',
    PRIMARY KEY (project_id)
) ENGINE=InnoDB COMMENT='Danh sách dự án BĐS của KN Holdings';

-- 2. Phân khu
CREATE TABLE sub_zones (
    sub_zone_id      VARCHAR(15) NOT NULL COMMENT 'Mã phân khu (VD: SZ-ST)',
    project_id       VARCHAR(10) NOT NULL COMMENT 'Mã dự án',
    sub_zone_name    VARCHAR(100) NOT NULL COMMENT 'Tên phân khu',
    area_ha          DECIMAL(10,2) COMMENT 'Diện tích (ha)',
    total_units      INT NOT NULL COMMENT 'Tổng số sản phẩm',
    architectural_style VARCHAR(100) COMMENT 'Phong cách kiến trúc',
    distance_to_beach_m INT COMMENT 'Khoảng cách đến biển (m) - quan trọng cho phân tích Para Grus',
    launch_date      DATE COMMENT 'Ngày mở bán phân khu',
    min_price_billion DECIMAL(8,2) COMMENT 'Giá thấp nhất (tỷ VND)',
    max_price_billion DECIMAL(8,2) COMMENT 'Giá cao nhất (tỷ VND)',
    avg_price_per_sqm_million DECIMAL(8,2) COMMENT 'Giá trung bình trên m² (triệu VND) - quan trọng cho so sánh giá',
    PRIMARY KEY (sub_zone_id),
    CONSTRAINT fk_subzone_project FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='Phân khu trong từng dự án';

-- 3. Loại sản phẩm
CREATE TABLE product_types (
    product_type_id  VARCHAR(10) NOT NULL COMMENT 'Mã loại SP',
    product_type_name VARCHAR(50) NOT NULL COMMENT 'Tên loại SP',
    description      VARCHAR(200) COMMENT 'Mô tả',
    PRIMARY KEY (product_type_id)
) ENGINE=InnoDB COMMENT='Danh mục loại sản phẩm BĐS';

-- 4. Sản phẩm (đơn vị bán)
CREATE TABLE products (
    product_id       VARCHAR(20) NOT NULL COMMENT 'Mã sản phẩm (VD: CW-ST-0001)',
    sub_zone_id      VARCHAR(15) NOT NULL COMMENT 'Mã phân khu',
    product_type_id  VARCHAR(10) NOT NULL COMMENT 'Mã loại SP',
    block_or_lot     VARCHAR(20) COMMENT 'Block/Lô',
    floor_or_row     VARCHAR(10) COMMENT 'Tầng/Dãy',
    area_sqm         DECIMAL(8,2) NOT NULL COMMENT 'Diện tích (m²)',
    bedrooms         TINYINT COMMENT 'Số phòng ngủ',
    listed_price_billion DECIMAL(10,3) NOT NULL COMMENT 'Giá niêm yết (tỷ VND)',
    construction_cost_billion DECIMAL(10,3) COMMENT 'Chi phí xây dựng (tỷ VND)',
    land_cost_billion DECIMAL(10,3) COMMENT 'Chi phí đất (tỷ VND)',
    status           ENUM('available','booked','deposited','contracted','handed_over','cancelled') NOT NULL DEFAULT 'available' COMMENT 'Trạng thái SP',
    has_sea_view     BOOLEAN DEFAULT FALSE COMMENT 'Có view biển',
    has_golf_view    BOOLEAN DEFAULT FALSE COMMENT 'Có view golf',
    PRIMARY KEY (product_id),
    CONSTRAINT fk_product_subzone FOREIGN KEY (sub_zone_id) REFERENCES sub_zones(sub_zone_id) ON DELETE RESTRICT,
    CONSTRAINT fk_product_type FOREIGN KEY (product_type_id) REFERENCES product_types(product_type_id) ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='Danh sách sản phẩm BĐS (đơn vị bán)';

-- 5. Kênh bán hàng
CREATE TABLE sales_channels (
    channel_id       VARCHAR(10) NOT NULL COMMENT 'Mã kênh',
    channel_name     VARCHAR(50) NOT NULL COMMENT 'Tên kênh',
    channel_type     ENUM('online','agent','direct') NOT NULL COMMENT 'Loại kênh',
    PRIMARY KEY (channel_id)
) ENGINE=InnoDB COMMENT='Kênh bán hàng';

-- 6. Nhân viên/Đại lý bán hàng
CREATE TABLE sales_agents (
    agent_id         VARCHAR(10) NOT NULL COMMENT 'Mã đại lý/NV',
    agent_name       VARCHAR(100) NOT NULL COMMENT 'Tên đại lý/NV',
    agent_type       ENUM('agency','online','direct') NOT NULL COMMENT 'Loại đại lý',
    company          VARCHAR(100) COMMENT 'Công ty đại lý',
    commission_rate  DECIMAL(5,2) COMMENT 'Tỷ lệ hoa hồng (%)',
    PRIMARY KEY (agent_id)
) ENGINE=InnoDB COMMENT='Đại lý và nhân viên bán hàng';

-- 7. Khách hàng
CREATE TABLE customers (
    customer_id      VARCHAR(15) NOT NULL COMMENT 'Mã khách hàng',
    customer_name    VARCHAR(100) NOT NULL COMMENT 'Tên khách hàng',
    customer_type    ENUM('individual','company','overseas_vn') NOT NULL COMMENT 'Loại KH',
    province         VARCHAR(50) COMMENT 'Tỉnh/TP',
    age_group        VARCHAR(20) COMMENT 'Nhóm tuổi',
    purchase_purpose ENUM('investment','vacation','residence','business') COMMENT 'Mục đích mua',
    PRIMARY KEY (customer_id)
) ENGINE=InnoDB COMMENT='Thông tin khách hàng';

-- 8. Chính sách thanh toán
CREATE TABLE payment_policies (
    policy_id        INT NOT NULL COMMENT 'Mã chính sách',
    policy_name      VARCHAR(100) NOT NULL COMMENT 'Tên chính sách',
    installment_months INT NOT NULL COMMENT 'Số tháng trả góp',
    interest_support_percent DECIMAL(5,2) DEFAULT 0 COMMENT 'Lãi suất hỗ trợ (%)',
    rental_commitment_percent DECIMAL(5,2) DEFAULT 0 COMMENT 'Cam kết cho thuê (%/năm)',
    early_payment_discount_percent DECIMAL(5,2) DEFAULT 0 COMMENT 'Chiết khấu thanh toán nhanh (%)',
    applicable_sub_zones VARCHAR(200) COMMENT 'Phân khu áp dụng',
    effective_from   DATE COMMENT 'Ngày hiệu lực',
    PRIMARY KEY (policy_id)
) ENGINE=InnoDB COMMENT='Chính sách thanh toán';

-- ============================================================
-- FACT TABLES
-- ============================================================

-- 9. Giao dịch bán hàng
CREATE TABLE sales_transactions (
    transaction_id   VARCHAR(20) NOT NULL COMMENT 'Mã giao dịch',
    product_id       VARCHAR(20) NOT NULL COMMENT 'Mã sản phẩm',
    customer_id      VARCHAR(15) NOT NULL COMMENT 'Mã khách hàng',
    agent_id         VARCHAR(10) NOT NULL COMMENT 'Mã đại lý/NV',
    channel_id       VARCHAR(10) NOT NULL COMMENT 'Mã kênh',
    policy_id        INT NOT NULL COMMENT 'Mã chính sách TT',
    booking_date     DATE COMMENT 'Ngày giữ chỗ',
    deposit_date     DATE COMMENT 'Ngày đặt cọc',
    contract_date    DATE COMMENT 'Ngày ký hợp đồng',
    handover_date    DATE COMMENT 'Ngày bàn giao',
    cancellation_date DATE COMMENT 'Ngày hủy',
    listed_price_billion DECIMAL(10,3) NOT NULL COMMENT 'Giá niêm yết (tỷ VND)',
    actual_price_billion DECIMAL(10,3) NOT NULL COMMENT 'Giá thực bán (tỷ VND)',
    discount_percent DECIMAL(5,2) DEFAULT 0 COMMENT 'Chiết khấu (%)',
    deposit_amount_billion DECIMAL(10,3) COMMENT 'Tiền đặt cọc (tỷ VND)',
    total_paid_billion DECIMAL(10,3) COMMENT 'Tổng đã thanh toán (tỷ VND)',
    payment_installments INT COMMENT 'Số kỳ trả góp',
    transaction_status ENUM('booking','deposited','contracted','handed_over','cancelled') NOT NULL COMMENT 'Trạng thái GD',
    cancellation_reason VARCHAR(200) COMMENT 'Lý do hủy',
    PRIMARY KEY (transaction_id),
    CONSTRAINT fk_trans_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    CONSTRAINT fk_trans_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
    CONSTRAINT fk_trans_agent FOREIGN KEY (agent_id) REFERENCES sales_agents(agent_id) ON DELETE RESTRICT,
    CONSTRAINT fk_trans_channel FOREIGN KEY (channel_id) REFERENCES sales_channels(channel_id) ON DELETE RESTRICT,
    CONSTRAINT fk_trans_policy FOREIGN KEY (policy_id) REFERENCES payment_policies(policy_id) ON DELETE RESTRICT,
    INDEX idx_trans_project_date (product_id, contract_date),
    INDEX idx_trans_booking_date (booking_date),
    INDEX idx_trans_status (transaction_status)
) ENGINE=InnoDB COMMENT='Giao dịch bán hàng BĐS';

-- 10. Pipeline khách hàng tiềm năng
CREATE TABLE leads_pipeline (
    lead_id          VARCHAR(20) NOT NULL COMMENT 'Mã lead',
    customer_id      VARCHAR(15) COMMENT 'Mã KH (nullable - chưa xác định)',
    project_id       VARCHAR(10) NOT NULL COMMENT 'Mã dự án',
    sub_zone_id      VARCHAR(15) COMMENT 'Mã phân khu (nullable)',
    channel_id       VARCHAR(10) NOT NULL COMMENT 'Mã kênh',
    agent_id         VARCHAR(10) COMMENT 'Mã đại lý (nullable)',
    lead_date        DATE NOT NULL COMMENT 'Ngày tiếp nhận lead',
    lead_source      ENUM('Facebook Ads','Google Ads','Website','Referral','Event','Walk-in','Zalo') NOT NULL COMMENT 'Nguồn lead',
    visit_date       DATE COMMENT 'Ngày tham quan',
    booking_date     DATE COMMENT 'Ngày giữ chỗ',
    deposit_date     DATE COMMENT 'Ngày đặt cọc',
    contract_date    DATE COMMENT 'Ngày ký HĐ',
    current_stage    ENUM('lead','visited','booked','deposited','contracted','lost') NOT NULL COMMENT 'Giai đoạn hiện tại',
    lost_reason      VARCHAR(200) COMMENT 'Lý do mất lead',
    lead_score       TINYINT COMMENT 'Điểm lead (1-100)',
    PRIMARY KEY (lead_id),
    CONSTRAINT fk_lead_project FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
    CONSTRAINT fk_lead_subzone FOREIGN KEY (sub_zone_id) REFERENCES sub_zones(sub_zone_id) ON DELETE RESTRICT,
    CONSTRAINT fk_lead_channel FOREIGN KEY (channel_id) REFERENCES sales_channels(channel_id) ON DELETE RESTRICT,
    INDEX idx_lead_channel_date (channel_id, lead_date),
    INDEX idx_lead_subzone (sub_zone_id, current_stage)
) ENGINE=InnoDB COMMENT='Pipeline khách hàng tiềm năng (leads funnel)';

-- 11. Lịch sử giá
CREATE TABLE pricing_history (
    pricing_id       INT AUTO_INCREMENT COMMENT 'ID tự tăng',
    sub_zone_id      VARCHAR(15) NOT NULL COMMENT 'Mã phân khu',
    product_type_id  VARCHAR(10) COMMENT 'Mã loại SP',
    effective_date   DATE NOT NULL COMMENT 'Ngày hiệu lực',
    old_avg_price_per_sqm DECIMAL(8,2) COMMENT 'Giá cũ (triệu/m²)',
    new_avg_price_per_sqm DECIMAL(8,2) COMMENT 'Giá mới (triệu/m²)',
    price_change_percent DECIMAL(5,2) COMMENT 'Thay đổi giá (%)',
    old_payment_months INT COMMENT 'Kỳ hạn TT cũ (tháng)',
    new_payment_months INT COMMENT 'Kỳ hạn TT mới (tháng)',
    reason           VARCHAR(200) COMMENT 'Lý do điều chỉnh',
    approved_by      VARCHAR(100) COMMENT 'Người phê duyệt',
    PRIMARY KEY (pricing_id),
    CONSTRAINT fk_pricing_subzone FOREIGN KEY (sub_zone_id) REFERENCES sub_zones(sub_zone_id) ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='Lịch sử thay đổi giá bán';

-- 12. Snapshot tồn kho
CREATE TABLE inventory_snapshots (
    snapshot_id      INT AUTO_INCREMENT COMMENT 'ID tự tăng',
    snapshot_date    DATE NOT NULL COMMENT 'Ngày chụp snapshot',
    sub_zone_id      VARCHAR(15) NOT NULL COMMENT 'Mã phân khu',
    total_units      INT NOT NULL COMMENT 'Tổng SP',
    available_units  INT NOT NULL COMMENT 'SP còn bán',
    booked_units     INT NOT NULL DEFAULT 0 COMMENT 'SP đang giữ chỗ',
    deposited_units  INT NOT NULL DEFAULT 0 COMMENT 'SP đã đặt cọc',
    contracted_units INT NOT NULL DEFAULT 0 COMMENT 'SP đã ký HĐ',
    handed_over_units INT NOT NULL DEFAULT 0 COMMENT 'SP đã bàn giao',
    cancelled_units  INT NOT NULL DEFAULT 0 COMMENT 'SP đã hủy',
    absorption_rate  DECIMAL(5,2) COMMENT 'Tỷ lệ hấp thụ (%)',
    monthly_sell_rate DECIMAL(8,2) COMMENT 'Tốc độ bán/tháng (SP)',
    months_of_inventory DECIMAL(8,1) COMMENT 'Số tháng tồn kho',
    PRIMARY KEY (snapshot_id),
    CONSTRAINT fk_inv_subzone FOREIGN KEY (sub_zone_id) REFERENCES sub_zones(sub_zone_id) ON DELETE RESTRICT,
    INDEX idx_inv_subzone_date (sub_zone_id, snapshot_date)
) ENGINE=InnoDB COMMENT='Snapshot tồn kho hàng tháng';

-- 13. Chi phí marketing
CREATE TABLE marketing_spend (
    spend_id         INT AUTO_INCREMENT COMMENT 'ID tự tăng',
    month_date       DATE NOT NULL COMMENT 'Tháng (ngày 1)',
    project_id       VARCHAR(10) NOT NULL COMMENT 'Mã dự án',
    sub_zone_id      VARCHAR(15) COMMENT 'Mã phân khu (nullable)',
    channel_id       VARCHAR(10) NOT NULL COMMENT 'Mã kênh',
    spend_amount_million DECIMAL(10,2) NOT NULL COMMENT 'Chi phí (triệu VND)',
    leads_generated  INT COMMENT 'Số leads tạo được',
    cost_per_lead_million DECIMAL(8,3) COMMENT 'CPL (triệu VND)',
    PRIMARY KEY (spend_id),
    CONSTRAINT fk_mkt_project FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
    CONSTRAINT fk_mkt_channel FOREIGN KEY (channel_id) REFERENCES sales_channels(channel_id) ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='Chi phí marketing theo tháng/kênh';

-- 14. Mục tiêu doanh thu
CREATE TABLE revenue_targets (
    target_id        INT AUTO_INCREMENT COMMENT 'ID tự tăng',
    project_id       VARCHAR(10) NOT NULL COMMENT 'Mã dự án',
    year             SMALLINT NOT NULL COMMENT 'Năm',
    quarter          TINYINT NOT NULL COMMENT 'Quý (1-4)',
    target_revenue_billion DECIMAL(10,2) NOT NULL COMMENT 'Mục tiêu doanh thu (tỷ VND)',
    target_units     INT COMMENT 'Mục tiêu số lượng SP',
    PRIMARY KEY (target_id),
    CONSTRAINT fk_target_project FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='Mục tiêu doanh thu theo quý';

-- ============================================================
-- METADATA TABLES
-- ============================================================

-- 15. Mô tả bảng
CREATE TABLE _meta_tables (
    table_name       VARCHAR(50) NOT NULL COMMENT 'Tên bảng',
    table_description VARCHAR(500) NOT NULL COMMENT 'Mô tả bảng (tiếng Việt)',
    table_type       ENUM('dimension','fact','metadata') NOT NULL COMMENT 'Loại bảng',
    row_count_approx INT COMMENT 'Số dòng ước lượng',
    PRIMARY KEY (table_name)
) ENGINE=InnoDB COMMENT='Metadata - mô tả các bảng trong database';

-- 16. Mô tả cột
CREATE TABLE _meta_columns (
    table_name       VARCHAR(50) NOT NULL COMMENT 'Tên bảng',
    column_name      VARCHAR(50) NOT NULL COMMENT 'Tên cột',
    column_description VARCHAR(500) NOT NULL COMMENT 'Mô tả cột (tiếng Việt)',
    data_type        VARCHAR(50) COMMENT 'Kiểu dữ liệu',
    unit             VARCHAR(50) COMMENT 'Đơn vị (VD: tỷ VND, m², %)',
    is_key           BOOLEAN DEFAULT FALSE COMMENT 'Là khóa chính/ngoại',
    example_value    VARCHAR(100) COMMENT 'Giá trị ví dụ',
    PRIMARY KEY (table_name, column_name)
) ENGINE=InnoDB COMMENT='Metadata - mô tả các cột trong database';

-- 17. KPI definitions
CREATE TABLE _meta_kpi (
    kpi_id           VARCHAR(20) NOT NULL COMMENT 'Mã KPI',
    kpi_name         VARCHAR(100) NOT NULL COMMENT 'Tên KPI (tiếng Việt)',
    formula          VARCHAR(500) COMMENT 'Công thức tính',
    unit             VARCHAR(50) COMMENT 'Đơn vị',
    description      VARCHAR(500) COMMENT 'Mô tả chi tiết',
    related_tables   VARCHAR(200) COMMENT 'Bảng liên quan',
    PRIMARY KEY (kpi_id)
) ENGINE=InnoDB COMMENT='Metadata - định nghĩa KPI';

-- 18. Glossary
CREATE TABLE _meta_glossary (
    term             VARCHAR(100) NOT NULL COMMENT 'Thuật ngữ',
    definition_vi    VARCHAR(500) NOT NULL COMMENT 'Định nghĩa tiếng Việt',
    definition_en    VARCHAR(500) COMMENT 'Định nghĩa tiếng Anh',
    context          VARCHAR(200) COMMENT 'Ngữ cảnh sử dụng',
    PRIMARY KEY (term)
) ENGINE=InnoDB COMMENT='Metadata - từ điển thuật ngữ BĐS';
