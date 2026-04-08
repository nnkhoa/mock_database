-- ============================================================================
-- GEMADEPT SEAPORT DEMO — DDL Schema
-- Database: seaport_demo
-- Description: Schema cho demo AI engine (Claude + MCP) cho Tập đoàn Gemadept
-- Tables: 8 dimension + 8 fact + 4 metadata = 20 tables
-- ============================================================================

CREATE DATABASE IF NOT EXISTS seaport_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE seaport_demo;

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. ports — Danh sách cảng của Gemadept
-- ----------------------------------------------------------------------------
CREATE TABLE ports (
  port_id           VARCHAR(5)    NOT NULL  COMMENT 'Mã cảng (VD: NDV, GML, PHL, DQT)',
  port_name         VARCHAR(100)  NOT NULL  COMMENT 'Tên cảng đầy đủ',
  port_name_short   VARCHAR(50)   NOT NULL  COMMENT 'Tên cảng viết tắt',
  region            VARCHAR(20)   NOT NULL  COMMENT 'Khu vực địa lý (VD: Miền Nam, Miền Trung)',
  port_type         ENUM('river_port','deep_sea_port','icd','sea_port')
                                  NOT NULL  COMMENT 'Loại cảng: cảng sông / cảng nước sâu / ICD / cảng biển',
  design_capacity_teu  INT        NULL      COMMENT 'Công suất thiết kế (TEU/năm)',
  design_capacity_tons INT        NULL      COMMENT 'Công suất thiết kế (tấn/năm)',
  quay_length_m     INT           NULL      COMMENT 'Chiều dài cầu tàu (mét)',
  water_depth_m     DECIMAL(4,1)  NULL      COMMENT 'Độ sâu luồng tàu (mét)',
  num_berths        INT           NULL      COMMENT 'Số bến tàu',
  status            ENUM('active','inactive','under_construction')
                                  NOT NULL DEFAULT 'active'
                                            COMMENT 'Trạng thái hoạt động',
  created_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                            COMMENT 'Thời điểm tạo bản ghi',
  PRIMARY KEY (port_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Danh sách các cảng thuộc Gemadept (NDV, GML, PHL, DQT)';

-- ----------------------------------------------------------------------------
-- 2. shipping_lines — Danh sách hãng tàu
-- ----------------------------------------------------------------------------
CREATE TABLE shipping_lines (
  shipping_line_id    VARCHAR(10)   NOT NULL  COMMENT 'Mã hãng tàu (VD: MSK, CMA, OOCL)',
  shipping_line_name  VARCHAR(100)  NOT NULL  COMMENT 'Tên hãng tàu đầy đủ',
  alliance            VARCHAR(50)   NULL      COMMENT 'Liên minh hãng tàu (2M, THE Alliance, Ocean Alliance)',
  country             VARCHAR(50)   NULL      COMMENT 'Quốc gia đăng ký',
  market_share_pct    DECIMAL(4,1)  NULL      COMMENT 'Thị phần tại Gemadept (%)',
  PRIMARY KEY (shipping_line_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Danh sách 15 hãng tàu hoạt động tại cảng Gemadept';

-- ----------------------------------------------------------------------------
-- 3. cost_types — Danh mục loại chi phí
-- ----------------------------------------------------------------------------
CREATE TABLE cost_types (
  cost_type_id        VARCHAR(20)   NOT NULL  COMMENT 'Mã loại chi phí (VD: LABOR, FUEL, MAINT)',
  cost_type_name_vi   VARCHAR(100)  NOT NULL  COMMENT 'Tên loại chi phí (tiếng Việt)',
  cost_type_name_en   VARCHAR(100)  NOT NULL  COMMENT 'Tên loại chi phí (tiếng Anh)',
  typical_pct_of_total DECIMAL(4,1) NULL      COMMENT 'Tỷ trọng điển hình trong tổng chi phí (%)',
  PRIMARY KEY (cost_type_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Danh mục 6 loại chi phí vận hành cảng';

-- ----------------------------------------------------------------------------
-- 4. cargo_types — Danh mục loại hàng hóa
-- ----------------------------------------------------------------------------
CREATE TABLE cargo_types (
  cargo_type_id          VARCHAR(20)   NOT NULL  COMMENT 'Mã loại hàng (VD: CONT_DRY, BULK, LIQUID)',
  cargo_type_name_vi     VARCHAR(100)  NOT NULL  COMMENT 'Tên loại hàng (tiếng Việt)',
  cargo_type_name_en     VARCHAR(100)  NOT NULL  COMMENT 'Tên loại hàng (tiếng Anh)',
  unit                   VARCHAR(10)   NOT NULL  COMMENT 'Đơn vị tính (TEU, tấn, m3)',
  avg_revenue_per_unit_vnd BIGINT      NULL      COMMENT 'Doanh thu trung bình / đơn vị (VND)',
  PRIMARY KEY (cargo_type_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Danh mục 6 loại hàng hóa qua cảng';

-- ----------------------------------------------------------------------------
-- 5. equipment — Danh sách thiết bị cảng
-- ----------------------------------------------------------------------------
CREATE TABLE equipment (
  equipment_id    VARCHAR(15)   NOT NULL  COMMENT 'Mã thiết bị (VD: QC-NDV-01, RTG-GML-03)',
  equipment_name  VARCHAR(100)  NOT NULL  COMMENT 'Tên thiết bị',
  equipment_type  VARCHAR(30)   NOT NULL  COMMENT 'Loại thiết bị (QC, RTG, Reach Stacker, Forklift...)',
  port_id         VARCHAR(5)    NOT NULL  COMMENT 'Mã cảng đặt thiết bị (FK → ports)',
  capacity_tons   DECIMAL(6,1)  NULL      COMMENT 'Sức nâng tối đa (tấn)',
  year_acquired   INT           NULL      COMMENT 'Năm mua / đưa vào sử dụng',
  status          ENUM('active','maintenance','retired')
                                NOT NULL DEFAULT 'active'
                                          COMMENT 'Trạng thái thiết bị',
  PRIMARY KEY (equipment_id),
  CONSTRAINT fk_equipment_port
    FOREIGN KEY (port_id) REFERENCES ports (port_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Danh sách ~35 thiết bị xếp dỡ tại các cảng Gemadept';

-- ----------------------------------------------------------------------------
-- 6. customers — Danh sách khách hàng
-- ----------------------------------------------------------------------------
CREATE TABLE customers (
  customer_id            VARCHAR(20)   NOT NULL  COMMENT 'Mã khách hàng',
  customer_name          VARCHAR(150)  NOT NULL  COMMENT 'Tên khách hàng',
  industry               VARCHAR(50)   NULL      COMMENT 'Ngành nghề (VD: Xuất khẩu nông sản, Điện tử, Dệt may)',
  primary_port_id        VARCHAR(5)    NULL      COMMENT 'Cảng sử dụng chính (FK → ports)',
  cargo_type_preference  VARCHAR(20)   NULL      COMMENT 'Loại hàng ưu tiên (FK → cargo_types)',
  PRIMARY KEY (customer_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Danh sách ~40 khách hàng sử dụng dịch vụ cảng Gemadept';

-- ----------------------------------------------------------------------------
-- 7. regions — Danh sách khu vực địa lý
-- ----------------------------------------------------------------------------
CREATE TABLE regions (
  region_id           VARCHAR(10)  NOT NULL  COMMENT 'Mã khu vực (VD: MN, MT, MB)',
  region_name         VARCHAR(50)  NOT NULL  COMMENT 'Tên khu vực',
  provinces_included  TEXT         NULL      COMMENT 'Danh sách tỉnh/thành phố thuộc khu vực',
  PRIMARY KEY (region_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='7 khu vực địa lý phục vụ phân tích hậu phương cảng';

-- ----------------------------------------------------------------------------
-- 8. investment_projects — Danh sách dự án đầu tư
-- ----------------------------------------------------------------------------
CREATE TABLE investment_projects (
  project_id              VARCHAR(10)   NOT NULL  COMMENT 'Mã dự án đầu tư',
  project_name            VARCHAR(200)  NOT NULL  COMMENT 'Tên dự án',
  port_id                 VARCHAR(5)    NOT NULL  COMMENT 'Cảng liên quan (FK → ports)',
  total_investment_usd    BIGINT        NULL      COMMENT 'Tổng vốn đầu tư (USD)',
  total_investment_vnd    BIGINT        NULL      COMMENT 'Tổng vốn đầu tư (VND)',
  additional_capacity_teu INT           NULL      COMMENT 'Công suất tăng thêm (TEU/năm)',
  depreciation_years      INT           NULL      COMMENT 'Số năm khấu hao',
  annual_depreciation_vnd BIGINT        NULL      COMMENT 'Khấu hao hàng năm (VND)',
  estimated_annual_opex_vnd BIGINT      NULL      COMMENT 'Chi phí vận hành ước tính/năm (VND)',
  construction_start      DATE          NULL      COMMENT 'Ngày khởi công',
  expected_completion     DATE          NULL      COMMENT 'Ngày dự kiến hoàn thành',
  status                  ENUM('planning','under_construction','completed')
                                        NOT NULL DEFAULT 'planning'
                                                  COMMENT 'Trạng thái dự án',
  PRIMARY KEY (project_id),
  CONSTRAINT fk_investment_port
    FOREIGN KEY (port_id) REFERENCES ports (port_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Danh sách dự án đầu tư mở rộng cảng Gemadept';


-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 9. port_revenue — Doanh thu theo cảng, tháng, loại hàng
-- ----------------------------------------------------------------------------
CREATE TABLE port_revenue (
  id                  INT           NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính tự tăng',
  port_id             VARCHAR(5)    NOT NULL  COMMENT 'Mã cảng (FK → ports)',
  month               DATE          NOT NULL  COMMENT 'Tháng báo cáo (ngày 1 của tháng)',
  cargo_type_id       VARCHAR(20)   NOT NULL  COMMENT 'Mã loại hàng (FK → cargo_types)',
  volume_teu          INT           NULL      COMMENT 'Sản lượng (TEU)',
  volume_tons         INT           NULL      COMMENT 'Sản lượng (tấn)',
  revenue_per_unit_vnd BIGINT       NULL      COMMENT 'Đơn giá doanh thu / đơn vị (VND)',
  total_revenue_vnd   BIGINT        NULL      COMMENT 'Tổng doanh thu (VND)',
  PRIMARY KEY (id),
  INDEX idx_port_revenue_port_month (port_id, month),
  CONSTRAINT fk_port_revenue_port
    FOREIGN KEY (port_id) REFERENCES ports (port_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_port_revenue_cargo
    FOREIGN KEY (cargo_type_id) REFERENCES cargo_types (cargo_type_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Doanh thu cảng theo tháng và loại hàng hóa';

-- ----------------------------------------------------------------------------
-- 10. container_throughput — Sản lượng container qua cảng
-- ----------------------------------------------------------------------------
CREATE TABLE container_throughput (
  id              INT           NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính tự tăng',
  port_id         VARCHAR(5)    NOT NULL  COMMENT 'Mã cảng (FK → ports)',
  month           DATE          NOT NULL  COMMENT 'Tháng báo cáo (ngày 1 của tháng)',
  cargo_type_id   VARCHAR(20)   NOT NULL  COMMENT 'Mã loại hàng (FK → cargo_types)',
  volume_teu      INT           NULL      COMMENT 'Sản lượng (TEU)',
  volume_tons     INT           NULL      COMMENT 'Sản lượng (tấn)',
  PRIMARY KEY (id),
  INDEX idx_throughput_port_month (port_id, month),
  CONSTRAINT fk_throughput_port
    FOREIGN KEY (port_id) REFERENCES ports (port_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_throughput_cargo
    FOREIGN KEY (cargo_type_id) REFERENCES cargo_types (cargo_type_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Sản lượng container qua cảng theo tháng và loại hàng';

-- ----------------------------------------------------------------------------
-- 11. operating_costs — Chi phí vận hành theo cảng, tháng, loại chi phí
-- ----------------------------------------------------------------------------
CREATE TABLE operating_costs (
  id              INT           NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính tự tăng',
  port_id         VARCHAR(5)    NOT NULL  COMMENT 'Mã cảng (FK → ports)',
  month           DATE          NOT NULL  COMMENT 'Tháng báo cáo (ngày 1 của tháng)',
  cost_type_id    VARCHAR(20)   NOT NULL  COMMENT 'Mã loại chi phí (FK → cost_types)',
  cost_amount_vnd BIGINT        NULL      COMMENT 'Số tiền chi phí (VND)',
  PRIMARY KEY (id),
  INDEX idx_opcost_port_month (port_id, month),
  CONSTRAINT fk_opcost_port
    FOREIGN KEY (port_id) REFERENCES ports (port_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_opcost_costtype
    FOREIGN KEY (cost_type_id) REFERENCES cost_types (cost_type_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Chi phí vận hành cảng theo tháng và loại chi phí';

-- ----------------------------------------------------------------------------
-- 12. shipping_line_revenue — Doanh thu theo hãng tàu
-- ----------------------------------------------------------------------------
CREATE TABLE shipping_line_revenue (
  id                INT           NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính tự tăng',
  port_id           VARCHAR(5)    NOT NULL  COMMENT 'Mã cảng (FK → ports)',
  month             DATE          NOT NULL  COMMENT 'Tháng báo cáo (ngày 1 của tháng)',
  shipping_line_id  VARCHAR(10)   NOT NULL  COMMENT 'Mã hãng tàu (FK → shipping_lines)',
  volume_teu        INT           NULL      COMMENT 'Sản lượng (TEU)',
  revenue_vnd       BIGINT        NULL      COMMENT 'Doanh thu (VND)',
  num_vessel_calls  INT           NULL      COMMENT 'Số chuyến tàu cập cảng',
  PRIMARY KEY (id),
  INDEX idx_slrev_port_month (port_id, month),
  INDEX idx_slrev_shipping_line (shipping_line_id),
  CONSTRAINT fk_slrev_port
    FOREIGN KEY (port_id) REFERENCES ports (port_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_slrev_shipping_line
    FOREIGN KEY (shipping_line_id) REFERENCES shipping_lines (shipping_line_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Doanh thu cảng theo hãng tàu và tháng';

-- ----------------------------------------------------------------------------
-- 13. vessel_calls — Chi tiết chuyến tàu cập cảng
-- ----------------------------------------------------------------------------
CREATE TABLE vessel_calls (
  id                    INT           NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính tự tăng',
  port_id               VARCHAR(5)    NOT NULL  COMMENT 'Mã cảng (FK → ports)',
  shipping_line_id      VARCHAR(10)   NOT NULL  COMMENT 'Mã hãng tàu (FK → shipping_lines)',
  vessel_name           VARCHAR(100)  NOT NULL  COMMENT 'Tên tàu',
  vessel_capacity_teu   INT           NULL      COMMENT 'Sức chứa tàu (TEU)',
  actual_volume_teu     INT           NULL      COMMENT 'Sản lượng thực tế xếp dỡ (TEU)',
  arrival_time          DATETIME      NOT NULL  COMMENT 'Thời gian tàu cập cảng',
  departure_time        DATETIME      NULL      COMMENT 'Thời gian tàu rời cảng',
  turnaround_hours      DECIMAL(5,1)  NULL      COMMENT 'Thời gian quay vòng tàu (giờ)',
  cargo_types_handled   VARCHAR(200)  NULL      COMMENT 'Danh sách loại hàng xử lý (phân cách bằng dấu phẩy)',
  PRIMARY KEY (id),
  CONSTRAINT fk_vcall_port
    FOREIGN KEY (port_id) REFERENCES ports (port_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_vcall_shipping_line
    FOREIGN KEY (shipping_line_id) REFERENCES shipping_lines (shipping_line_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Chi tiết từng chuyến tàu cập cảng Gemadept';

-- ----------------------------------------------------------------------------
-- 14. equipment_utilization — Hiệu suất sử dụng thiết bị theo tháng
-- ----------------------------------------------------------------------------
CREATE TABLE equipment_utilization (
  id                          INT           NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính tự tăng',
  equipment_id                VARCHAR(15)   NOT NULL  COMMENT 'Mã thiết bị (FK → equipment)',
  port_id                     VARCHAR(5)    NOT NULL  COMMENT 'Mã cảng (FK → ports)',
  month                       DATE          NOT NULL  COMMENT 'Tháng báo cáo (ngày 1 của tháng)',
  total_hours                 INT           NOT NULL DEFAULT 720
                                                      COMMENT 'Tổng số giờ trong tháng (mặc định 720)',
  operating_hours             INT           NULL      COMMENT 'Số giờ vận hành thực tế',
  idle_hours                  INT           NULL      COMMENT 'Số giờ chờ / không tải',
  maintenance_hours           INT           NULL      COMMENT 'Số giờ bảo trì',
  moves_count                 INT           NULL      COMMENT 'Số lượt nâng hạ / di chuyển',
  availability_pct            DECIMAL(5,2)  NULL      COMMENT 'Tỷ lệ sẵn sàng (%)',
  productivity_moves_per_hour DECIMAL(5,1)  NULL      COMMENT 'Năng suất (lượt/giờ vận hành)',
  PRIMARY KEY (id),
  INDEX idx_equip_util_port_month (port_id, month),
  CONSTRAINT fk_equip_util_equipment
    FOREIGN KEY (equipment_id) REFERENCES equipment (equipment_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_equip_util_port
    FOREIGN KEY (port_id) REFERENCES ports (port_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Hiệu suất sử dụng thiết bị xếp dỡ theo tháng';

-- ----------------------------------------------------------------------------
-- 15. equipment_maintenance — Lịch sử bảo trì thiết bị
-- ----------------------------------------------------------------------------
CREATE TABLE equipment_maintenance (
  id                INT           NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính tự tăng',
  equipment_id      VARCHAR(15)   NOT NULL  COMMENT 'Mã thiết bị (FK → equipment)',
  port_id           VARCHAR(5)    NOT NULL  COMMENT 'Mã cảng (FK → ports)',
  maintenance_type  ENUM('routine','major_overhaul','emergency','inspection')
                                  NOT NULL  COMMENT 'Loại bảo trì: định kỳ / đại tu / khẩn cấp / kiểm tra',
  start_date        DATE          NOT NULL  COMMENT 'Ngày bắt đầu bảo trì',
  end_date          DATE          NULL      COMMENT 'Ngày kết thúc bảo trì',
  cost_vnd          BIGINT        NULL      COMMENT 'Chi phí bảo trì (VND)',
  description       TEXT          NULL      COMMENT 'Mô tả công việc bảo trì',
  PRIMARY KEY (id),
  CONSTRAINT fk_equip_maint_equipment
    FOREIGN KEY (equipment_id) REFERENCES equipment (equipment_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_equip_maint_port
    FOREIGN KEY (port_id) REFERENCES ports (port_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Lịch sử bảo trì và sửa chữa thiết bị cảng';

-- ----------------------------------------------------------------------------
-- 16. customer_revenue — Doanh thu theo khách hàng
-- ----------------------------------------------------------------------------
CREATE TABLE customer_revenue (
  id              INT           NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính tự tăng',
  port_id         VARCHAR(5)    NOT NULL  COMMENT 'Mã cảng (FK → ports)',
  month           DATE          NOT NULL  COMMENT 'Tháng báo cáo (ngày 1 của tháng)',
  customer_id     VARCHAR(20)   NOT NULL  COMMENT 'Mã khách hàng (FK → customers)',
  cargo_type_id   VARCHAR(20)   NOT NULL  COMMENT 'Mã loại hàng (FK → cargo_types)',
  volume_teu      INT           NULL      COMMENT 'Sản lượng (TEU)',
  volume_tons     INT           NULL      COMMENT 'Sản lượng (tấn)',
  revenue_vnd     BIGINT        NULL      COMMENT 'Doanh thu (VND)',
  PRIMARY KEY (id),
  INDEX idx_custrev_port_month (port_id, month),
  CONSTRAINT fk_custrev_port
    FOREIGN KEY (port_id) REFERENCES ports (port_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_custrev_customer
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_custrev_cargo
    FOREIGN KEY (cargo_type_id) REFERENCES cargo_types (cargo_type_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Doanh thu cảng theo khách hàng, loại hàng và tháng';


-- ============================================================================
-- METADATA TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 17. _meta_tables — Mô tả các bảng trong database
-- ----------------------------------------------------------------------------
CREATE TABLE _meta_tables (
  table_name        VARCHAR(50)   NOT NULL  COMMENT 'Tên bảng trong database',
  description_vi    TEXT          NULL      COMMENT 'Mô tả bảng (tiếng Việt)',
  description_en    TEXT          NULL      COMMENT 'Mô tả bảng (tiếng Anh)',
  business_context  TEXT          NULL      COMMENT 'Ngữ cảnh nghiệp vụ cho AI engine',
  PRIMARY KEY (table_name)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Metadata: mô tả các bảng trong seaport_demo cho AI engine';

-- ----------------------------------------------------------------------------
-- 18. _meta_columns — Mô tả các cột trong database
-- ----------------------------------------------------------------------------
CREATE TABLE _meta_columns (
  id              INT           NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính tự tăng',
  table_name      VARCHAR(50)   NOT NULL  COMMENT 'Tên bảng chứa cột',
  column_name     VARCHAR(50)   NOT NULL  COMMENT 'Tên cột',
  data_type       VARCHAR(50)   NULL      COMMENT 'Kiểu dữ liệu',
  description_vi  TEXT          NULL      COMMENT 'Mô tả cột (tiếng Việt)',
  description_en  TEXT          NULL      COMMENT 'Mô tả cột (tiếng Anh)',
  unit            VARCHAR(20)   NULL      COMMENT 'Đơn vị (VND, TEU, tấn, %, giờ...)',
  example_values  TEXT          NULL      COMMENT 'Giá trị mẫu để AI hiểu ngữ cảnh',
  PRIMARY KEY (id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Metadata: mô tả các cột trong seaport_demo cho AI engine';

-- ----------------------------------------------------------------------------
-- 19. _meta_kpi — Định nghĩa KPI nghiệp vụ
-- ----------------------------------------------------------------------------
CREATE TABLE _meta_kpi (
  kpi_id            VARCHAR(30)   NOT NULL  COMMENT 'Mã KPI (VD: throughput_growth, opex_ratio)',
  kpi_name_vi       VARCHAR(100)  NOT NULL  COMMENT 'Tên KPI (tiếng Việt)',
  kpi_name_en       VARCHAR(100)  NOT NULL  COMMENT 'Tên KPI (tiếng Anh)',
  formula_sql       TEXT          NULL      COMMENT 'Công thức SQL tính KPI',
  description_vi    TEXT          NULL      COMMENT 'Giải thích KPI (tiếng Việt)',
  related_questions TEXT          NULL      COMMENT 'Các câu hỏi mẫu liên quan đến KPI',
  PRIMARY KEY (kpi_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Metadata: định nghĩa KPI nghiệp vụ cảng cho AI engine';

-- ----------------------------------------------------------------------------
-- 20. _meta_glossary — Từ điển thuật ngữ ngành cảng
-- ----------------------------------------------------------------------------
CREATE TABLE _meta_glossary (
  term_id     VARCHAR(30)   NOT NULL  COMMENT 'Mã thuật ngữ',
  term_vi     VARCHAR(100)  NOT NULL  COMMENT 'Thuật ngữ tiếng Việt',
  term_en     VARCHAR(100)  NOT NULL  COMMENT 'Thuật ngữ tiếng Anh',
  definition  TEXT          NULL      COMMENT 'Định nghĩa / giải thích',
  PRIMARY KEY (term_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Metadata: từ điển thuật ngữ ngành cảng biển cho AI engine';

-- ============================================================================
-- END OF DDL
-- ============================================================================
