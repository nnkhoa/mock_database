-- SOTRANS Demo Database — DDL Schema
-- Run this file first

SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS `sotrans_demo` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `sotrans_demo`;

CREATE TABLE IF NOT EXISTS service_types (
      service_type_id   TINYINT UNSIGNED NOT NULL,
      service_code      VARCHAR(20) NOT NULL COMMENT 'Mã dịch vụ: FF, WH, ICD, IWT, CL',
      service_name_vi   VARCHAR(100) NOT NULL COMMENT 'Tên tiếng Việt',
      service_name_en   VARCHAR(100) NOT NULL,
      margin_target_pct DECIMAL(5,2) COMMENT 'Biên lợi nhuận mục tiêu %',
      PRIMARY KEY (service_type_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Danh mục 5 mảng dịch vụ của Sotrans';

CREATE TABLE IF NOT EXISTS regions (
      region_id   TINYINT UNSIGNED NOT NULL,
      region_name VARCHAR(50) NOT NULL COMMENT 'Tên vùng: Miền Nam, Miền Bắc, Miền Trung',
      province    VARCHAR(50) COMMENT 'Tỉnh/thành phố',
      PRIMARY KEY (region_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Phân vùng địa lý hoạt động';

CREATE TABLE IF NOT EXISTS warehouses (
      warehouse_id               SMALLINT UNSIGNED NOT NULL,
      warehouse_code             VARCHAR(10) NOT NULL COMMENT 'Mã kho: WH_PHM, WH_TDC...',
      warehouse_name             VARCHAR(100) NOT NULL COMMENT 'Tên kho đầy đủ',
      location                   VARCHAR(150) COMMENT 'Địa chỉ',
      region_id                  TINYINT UNSIGNED NOT NULL,
      capacity_sqm               INT UNSIGNED NOT NULL COMMENT 'Diện tích m²',
      warehouse_type             ENUM('kho_ngoai_quan','kho_thuong_mai','kho_lanh','kho_da_chuc_nang') NOT NULL,
      monthly_fixed_cost_vnd     BIGINT COMMENT 'Chi phí cố định hàng tháng VND',
      utilization_target_pct     DECIMAL(5,2) DEFAULT 85.00 COMMENT 'Mục tiêu công suất %',
      is_active                  BOOLEAN DEFAULT TRUE,
      PRIMARY KEY (warehouse_id),
      CONSTRAINT fk_wh_region FOREIGN KEY (region_id) REFERENCES regions(region_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Hệ thống kho bãi Sotrans - 230.000m² toàn quốc';

CREATE TABLE IF NOT EXISTS ports_depots (
      port_id              SMALLINT UNSIGNED NOT NULL,
      port_code            VARCHAR(10) NOT NULL,
      port_name            VARCHAR(100) NOT NULL,
      port_type            ENUM('ICD','depot','cang_song') NOT NULL,
      location             VARCHAR(150),
      region_id            TINYINT UNSIGNED NOT NULL,
      area_sqm             INT UNSIGNED COMMENT 'Diện tích m²',
      capacity_teu_month   INT UNSIGNED COMMENT 'Công suất TEU/tháng',
      PRIMARY KEY (port_id),
      CONSTRAINT fk_port_region FOREIGN KEY (region_id) REFERENCES regions(region_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Hệ thống cảng và depot của Sotrans';

CREATE TABLE IF NOT EXISTS freight_routes (
      route_id             SMALLINT UNSIGNED NOT NULL,
      route_code           VARCHAR(20) NOT NULL COMMENT 'Ví dụ: HCM-NRT-SEA',
      origin_port          VARCHAR(10) NOT NULL COMMENT 'Cảng xuất',
      destination_port     VARCHAR(10) NOT NULL COMMENT 'Cảng đến',
      destination_country  VARCHAR(50) NOT NULL,
      transport_mode       ENUM('sea','air','multimodal') NOT NULL,
      transit_days         SMALLINT UNSIGNED COMMENT 'Số ngày transit',
      is_active            BOOLEAN DEFAULT TRUE,
      PRIMARY KEY (route_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Các tuyến vận tải quốc tế của Sotrans';

CREATE TABLE IF NOT EXISTS customers (
      customer_id        SMALLINT UNSIGNED NOT NULL,
      customer_code      VARCHAR(20) NOT NULL,
      customer_name      VARCHAR(150) NOT NULL COMMENT 'Tên công ty tiếng Việt/Anh',
      industry           VARCHAR(50) COMMENT 'Ngành: FMCG, Dệt may, Điện tử, Xây dựng...',
      country_origin     VARCHAR(50) COMMENT 'Quốc gia công ty mẹ',
      tier               ENUM('platinum','gold','silver','bronze') NOT NULL COMMENT 'Phân hạng khách hàng',
      account_manager    VARCHAR(100),
      contract_start_date DATE,
      is_active          BOOLEAN DEFAULT TRUE,
      PRIMARY KEY (customer_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Danh sách khách hàng Sotrans - 20 khách hàng lớn + others';

CREATE TABLE IF NOT EXISTS customer_contracts (
      contract_id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
      customer_id            SMALLINT UNSIGNED NOT NULL,
      service_type_id        TINYINT UNSIGNED NOT NULL,
      route_id               SMALLINT UNSIGNED COMMENT 'NULL nếu không phải freight',
      warehouse_id           SMALLINT UNSIGNED COMMENT 'NULL nếu không phải kho',
      contract_code          VARCHAR(30) NOT NULL,
      rate_usd_per_cbm       DECIMAL(10,2) COMMENT 'Giá freight USD/CBM (sea)',
      rate_usd_per_kg        DECIMAL(10,4) COMMENT 'Giá freight USD/kg (air)',
      rate_vnd_per_sqm_month DECIMAL(12,2) COMMENT 'Giá thuê kho VND/m²/tháng',
      start_date             DATE NOT NULL,
      end_date               DATE COMMENT 'NULL = open-ended',
      status                 ENUM('active','expired','terminated') DEFAULT 'active',
      PRIMARY KEY (contract_id),
      CONSTRAINT fk_cc_customer  FOREIGN KEY (customer_id)     REFERENCES customers(customer_id),
      CONSTRAINT fk_cc_svc       FOREIGN KEY (service_type_id) REFERENCES service_types(service_type_id),
      CONSTRAINT fk_cc_route     FOREIGN KEY (route_id)        REFERENCES freight_routes(route_id),
      CONSTRAINT fk_cc_warehouse FOREIGN KEY (warehouse_id)    REFERENCES warehouses(warehouse_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Hợp đồng dịch vụ với khách hàng - nguồn gốc rate tính margin';

CREATE TABLE IF NOT EXISTS freight_shipments (
      shipment_id       INT UNSIGNED NOT NULL AUTO_INCREMENT,
      shipment_date     DATE NOT NULL COMMENT 'Ngày xác nhận lô hàng',
      customer_id       SMALLINT UNSIGNED NOT NULL,
      route_id          SMALLINT UNSIGNED NOT NULL,
      contract_id       INT UNSIGNED COMMENT 'Hợp đồng áp dụng',
      cbm               DECIMAL(10,2) COMMENT 'Thể tích m³ (sea)',
      weight_kg         DECIMAL(12,2) COMMENT 'Trọng lượng kg (air)',
      num_containers    SMALLINT UNSIGNED COMMENT 'Số container (sea)',
      revenue_vnd       BIGINT NOT NULL COMMENT 'Doanh thu từ khách hàng VND',
      cost_vnd          BIGINT NOT NULL COMMENT 'Chi phí thực tế (cước tàu + handling) VND',
      gross_profit_vnd  BIGINT GENERATED ALWAYS AS (revenue_vnd - cost_vnd) STORED,
      gross_margin_pct  DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN revenue_vnd > 0 THEN ROUND((revenue_vnd - cost_vnd) * 100.0 / revenue_vnd, 2) ELSE NULL END
      ) STORED,
      cargo_type        VARCHAR(50) COMMENT 'Loại hàng: dệt may, điện tử, FMCG...',
      PRIMARY KEY (shipment_id),
      CONSTRAINT fk_fs_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
      CONSTRAINT fk_fs_route    FOREIGN KEY (route_id)    REFERENCES freight_routes(route_id),
      CONSTRAINT fk_fs_contract FOREIGN KEY (contract_id) REFERENCES customer_contracts(contract_id),
      INDEX idx_date             (shipment_date),
      INDEX idx_customer_route   (customer_id, route_id),
      INDEX idx_date_route       (shipment_date, route_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Lô hàng freight forwarding - grain: 1 dòng = 1 lô hàng';

CREATE TABLE IF NOT EXISTS shipping_rate_market (
      rate_id                  INT UNSIGNED NOT NULL AUTO_INCREMENT,
      route_id                 SMALLINT UNSIGNED NOT NULL,
      rate_month               DATE NOT NULL COMMENT 'Ngày đầu tháng (YYYY-MM-01)',
      market_rate_usd_per_cbm  DECIMAL(10,2) COMMENT 'Giá thị trường USD/CBM',
      market_rate_index        DECIMAL(6,2) COMMENT 'Index so với baseline (100=Apr2023)',
      source                   VARCHAR(50) DEFAULT 'Freightos Baltic Index estimate',
      PRIMARY KEY (rate_id),
      CONSTRAINT fk_srm_route FOREIGN KEY (route_id) REFERENCES freight_routes(route_id),
      INDEX idx_route_month (route_id, rate_month)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Giá cước thị trường theo tuyến và tháng - để so sánh với contract rate';

CREATE TABLE IF NOT EXISTS warehouse_occupancy (
      occupancy_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
      occupancy_month DATE NOT NULL COMMENT 'Ngày đầu tháng (YYYY-MM-01)',
      warehouse_id    SMALLINT UNSIGNED NOT NULL,
      customer_id     SMALLINT UNSIGNED NOT NULL,
      occupied_sqm    INT UNSIGNED NOT NULL COMMENT 'Diện tích thực tế sử dụng m²',
      revenue_vnd     BIGINT NOT NULL COMMENT 'Doanh thu từ khách hàng trong tháng',
      cost_vnd        BIGINT NOT NULL COMMENT 'Chi phí vận hành phân bổ',
      cargo_category  VARCHAR(50) COMMENT 'Loại hàng lưu trữ',
      PRIMARY KEY (occupancy_id),
      CONSTRAINT fk_wo_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
      CONSTRAINT fk_wo_customer  FOREIGN KEY (customer_id)  REFERENCES customers(customer_id),
      INDEX idx_month_wh       (occupancy_month, warehouse_id),
      INDEX idx_customer_month (customer_id, occupancy_month)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Sử dụng kho theo khách hàng và tháng - grain: 1 dòng = 1 khách/1 kho/1 tháng';

CREATE TABLE IF NOT EXISTS icd_teu_throughput (
      throughput_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
      throughput_month DATE NOT NULL COMMENT 'Ngày đầu tháng',
      port_id          SMALLINT UNSIGNED NOT NULL,
      teu_count        INT UNSIGNED NOT NULL COMMENT 'Số TEU thông qua',
      revenue_vnd      BIGINT NOT NULL COMMENT 'Doanh thu khai thác cảng',
      cost_vnd         BIGINT NOT NULL,
      handling_type    ENUM('import','export','transshipment') NOT NULL,
      PRIMARY KEY (throughput_id),
      CONSTRAINT fk_icd_port FOREIGN KEY (port_id) REFERENCES ports_depots(port_id),
      INDEX idx_month_port (throughput_month, port_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Sản lượng TEU thông qua cảng ICD hàng tháng';

CREATE TABLE IF NOT EXISTS inland_waterway_trips (
      trip_id                  INT UNSIGNED NOT NULL AUTO_INCREMENT,
      trip_date                DATE NOT NULL,
      customer_id              SMALLINT UNSIGNED NOT NULL,
      origin_region_id         TINYINT UNSIGNED COMMENT 'Điểm xuất phát',
      destination_region_id    TINYINT UNSIGNED COMMENT 'Điểm đến',
      cargo_tons               DECIMAL(10,2) COMMENT 'Tấn hàng',
      revenue_vnd              BIGINT NOT NULL,
      cost_vnd                 BIGINT NOT NULL,
      PRIMARY KEY (trip_id),
      CONSTRAINT fk_iwt_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
      INDEX idx_date (trip_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Chuyến vận tải đường thủy nội địa SOWATCO';

CREATE TABLE IF NOT EXISTS annual_targets (
      target_id               SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
      fiscal_year             SMALLINT UNSIGNED NOT NULL,
      service_type_id         TINYINT UNSIGNED NOT NULL,
      target_revenue_vnd      BIGINT NOT NULL COMMENT 'Kế hoạch doanh thu VND',
      target_gross_profit_vnd BIGINT NOT NULL COMMENT 'Kế hoạch lợi nhuận gộp VND',
      PRIMARY KEY (target_id),
      CONSTRAINT fk_at_svc FOREIGN KEY (service_type_id) REFERENCES service_types(service_type_id),
      UNIQUE KEY uk_year_service (fiscal_year, service_type_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Kế hoạch năm theo mảng dịch vụ';

CREATE TABLE IF NOT EXISTS _meta_tables (
      table_name       VARCHAR(100) NOT NULL,
      description_vi   TEXT,
      description_en   TEXT,
      business_context TEXT,
      grain            VARCHAR(200) COMMENT '1 dòng = ?',
      row_count_approx INT,
      PRIMARY KEY (table_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Mô tả nghiệp vụ của từng bảng';

CREATE TABLE IF NOT EXISTS _meta_columns (
      id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
      table_name    VARCHAR(100),
      column_name   VARCHAR(100),
      data_type     VARCHAR(50),
      description_vi TEXT,
      description_en TEXT,
      unit          VARCHAR(50),
      example_values VARCHAR(200),
      PRIMARY KEY (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Mô tả chi tiết từng cột';

CREATE TABLE IF NOT EXISTS _meta_kpi (
      kpi_id           SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
      kpi_name         VARCHAR(100) NOT NULL,
      kpi_name_vi      VARCHAR(100),
      formula_sql      TEXT NOT NULL,
      description_vi   TEXT,
      related_questions VARCHAR(300),
      PRIMARY KEY (kpi_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Công thức tính các KPI trọng tâm';

CREATE TABLE IF NOT EXISTS _meta_glossary (
      term_id       SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
      term_vi       VARCHAR(100),
      term_en       VARCHAR(100),
      abbreviation  VARCHAR(20),
      definition    TEXT,
      related_table VARCHAR(100),
      related_column VARCHAR(100),
      PRIMARY KEY (term_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='Từ điển thuật ngữ logistics';

