-- =====================================================================
-- VRI Group — Khối Dịch vụ (Hotels + Cosmos) — DDL Schema
-- Database: vri_services_demo
-- Charset:  utf8mb4 / utf8mb4_unicode_ci
-- Time range: 2024-06-01 → 2025-11-30 (18 months)
-- =====================================================================

DROP DATABASE IF EXISTS vri_services_demo;
CREATE DATABASE vri_services_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE vri_services_demo;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================================
-- DIMENSION TABLES
-- =====================================================================

-- ------------------------------------------------------------------
-- 1. dim_calendar
-- ------------------------------------------------------------------
CREATE TABLE dim_calendar (
  date              DATE        PRIMARY KEY                COMMENT 'Ngày (YYYY-MM-DD)',
  day_of_week       TINYINT     NOT NULL                   COMMENT '1=Mon..7=Sun',
  day_name_vi       VARCHAR(15) NOT NULL                   COMMENT 'Thứ Hai..Chủ Nhật',
  day_of_month      TINYINT     NOT NULL,
  week_of_year      TINYINT     NOT NULL,
  `month`           TINYINT     NOT NULL                   COMMENT '1-12',
  month_name_vi     VARCHAR(15) NOT NULL                   COMMENT 'Tháng 1..Tháng 12',
  quarter           TINYINT     NOT NULL                   COMMENT '1-4',
  `year`            SMALLINT    NOT NULL,
  ym        CHAR(7)     NOT NULL                   COMMENT 'YYYY-MM',
  is_weekend        TINYINT(1)  NOT NULL DEFAULT 0,
  is_holiday        TINYINT(1)  NOT NULL DEFAULT 0         COMMENT 'Ngày lễ VN',
  holiday_name_vi   VARCHAR(60) NULL                       COMMENT 'Tên ngày lễ',
  season_vi         VARCHAR(20) NOT NULL                   COMMENT 'Xuân/Hạ/Thu/Đông',
  hospitality_period VARCHAR(40) NOT NULL                  COMMENT 'Tết/30-4/Hè peak/Quốc tế/Off-peak/Bình thường',
  INDEX idx_ym (ym),
  INDEX idx_year (`year`),
  INDEX idx_month (`month`)
) ENGINE=InnoDB COMMENT='Calendar 18 tháng, kèm cờ ngày lễ và mùa hospitality VN';

-- ------------------------------------------------------------------
-- 2. dim_business_unit
-- ------------------------------------------------------------------
CREATE TABLE dim_business_unit (
  business_unit_id    INT         PRIMARY KEY,
  business_unit_code  VARCHAR(10) NOT NULL UNIQUE,
  business_unit_name  VARCHAR(50) NOT NULL                 COMMENT 'Tên BU: Hotels / Cosmos',
  description_vi      VARCHAR(255) NOT NULL,
  ceo_name            VARCHAR(80) NULL,
  founded_year        SMALLINT    NULL
) ENGINE=InnoDB COMMENT='2 mảng song song của Khối Dịch vụ';

-- ------------------------------------------------------------------
-- 3. dim_region
-- ------------------------------------------------------------------
CREATE TABLE dim_region (
  region_id     INT         PRIMARY KEY,
  region_code   VARCHAR(10) NOT NULL UNIQUE,
  region_name_vi VARCHAR(50) NOT NULL                       COMMENT 'Vùng miền VN',
  macro_region_vi VARCHAR(30) NOT NULL                      COMMENT 'Bắc/Trung/Nam'
) ENGINE=InnoDB COMMENT='Vùng miền địa lý VN';

-- ------------------------------------------------------------------
-- 4. dim_property
-- ------------------------------------------------------------------
CREATE TABLE dim_property (
  property_id           INT         PRIMARY KEY,
  property_code         VARCHAR(10) NOT NULL UNIQUE,
  property_name         VARCHAR(120) NOT NULL              COMMENT 'Tên khách sạn (tiếng Việt)',
  business_unit_id      INT         NOT NULL,
  hotel_class           TINYINT     NOT NULL               COMMENT 'Số sao (4 hoặc 5)',
  category_vi           VARCHAR(50) NOT NULL               COMMENT 'City Luxury/Hill Resort/Beach Resort/Golf/City Business/Heritage',
  total_rooms           SMALLINT    NOT NULL,
  address               VARCHAR(255) NOT NULL,
  city                  VARCHAR(50) NOT NULL,
  region_id             INT         NOT NULL,
  opening_year          SMALLINT    NOT NULL,
  ota_dependency_baseline DECIMAL(5,4) NOT NULL            COMMENT 'Tỷ trọng OTA baseline (cho anomaly setup)',
  notes_vi              VARCHAR(255) NULL,
  INDEX idx_bu (business_unit_id),
  INDEX idx_region (region_id)
) ENGINE=InnoDB COMMENT='6 khách sạn của VRI Group';

-- ------------------------------------------------------------------
-- 5. dim_room_type
-- ------------------------------------------------------------------
CREATE TABLE dim_room_type (
  room_type_id     INT         PRIMARY KEY AUTO_INCREMENT,
  property_id      INT         NOT NULL,
  room_type_code   VARCHAR(20) NOT NULL,
  room_type_name_vi VARCHAR(60) NOT NULL                   COMMENT 'Tên loại phòng',
  tier             VARCHAR(20) NOT NULL                    COMMENT 'Standard/Deluxe/Suite/Villa/Presidential',
  rooms_count      SMALLINT    NOT NULL                    COMMENT 'Số phòng cùng loại (cộng = total_rooms property)',
  base_adr         DECIMAL(15,0) NOT NULL                  COMMENT 'ADR baseline VND',
  capacity         TINYINT     NOT NULL DEFAULT 2          COMMENT 'Sức chứa (số người)',
  UNIQUE KEY uk_property_code (property_id, room_type_code),
  INDEX idx_property (property_id)
) ENGINE=InnoDB COMMENT='Loại phòng theo từng khách sạn (4-6 loại/property)';

-- ------------------------------------------------------------------
-- 6. dim_channel
-- ------------------------------------------------------------------
CREATE TABLE dim_channel (
  channel_id              VARCHAR(10) PRIMARY KEY,
  channel_name_vi         VARCHAR(60) NOT NULL              COMMENT 'Tên kênh (tiếng Việt)',
  channel_name_en         VARCHAR(60) NOT NULL,
  channel_category        VARCHAR(20) NOT NULL              COMMENT 'Direct/OTA/Wholesale/Corporate',
  commission_rate_default DECIMAL(5,4) NOT NULL             COMMENT 'Hoa hồng mặc định',
  description_vi          VARCHAR(255) NOT NULL
) ENGINE=InnoDB COMMENT='Kênh đặt phòng — Direct, OTA, Wholesale, Corporate';

-- ------------------------------------------------------------------
-- 7. dim_source_market
-- ------------------------------------------------------------------
CREATE TABLE dim_source_market (
  source_market_id      VARCHAR(5)  PRIMARY KEY            COMMENT 'ISO-2 hoặc OTH',
  source_market_name_vi VARCHAR(40) NOT NULL,
  source_market_name_en VARCHAR(40) NOT NULL,
  geo_region_vi         VARCHAR(30) NOT NULL                COMMENT 'Đông Á/Đông Nam Á/Tây Âu/...',
  is_domestic           TINYINT(1)  NOT NULL DEFAULT 0
) ENGINE=InnoDB COMMENT='Nguồn khách (10 markets)';

-- ------------------------------------------------------------------
-- 8. dim_guest_segment
-- ------------------------------------------------------------------
CREATE TABLE dim_guest_segment (
  segment_id    INT         PRIMARY KEY,
  segment_code  VARCHAR(15) NOT NULL UNIQUE,
  segment_name_vi VARCHAR(40) NOT NULL                      COMMENT 'Leisure/Business/Group/MICE',
  description_vi VARCHAR(255) NOT NULL
) ENGINE=InnoDB COMMENT='Phân khúc khách';

-- ------------------------------------------------------------------
-- 9. dim_event_type
-- ------------------------------------------------------------------
CREATE TABLE dim_event_type (
  event_type_id    INT         PRIMARY KEY,
  event_type_code  VARCHAR(20) NOT NULL UNIQUE,
  event_type_name_vi VARCHAR(60) NOT NULL,
  scale_vi         VARCHAR(30) NOT NULL                     COMMENT 'Quốc gia/Quốc tế/Phụ trợ'
) ENGINE=InnoDB COMMENT='Loại sự kiện Cosmos';

-- ------------------------------------------------------------------
-- 10. dim_event
-- ------------------------------------------------------------------
CREATE TABLE dim_event (
  event_id            VARCHAR(20) PRIMARY KEY               COMMENT 'MCV2023/MCO2024/...',
  event_name_vi       VARCHAR(120) NOT NULL,
  event_type_id       INT         NOT NULL,
  business_unit_id    INT         NOT NULL,
  venue_name          VARCHAR(120) NOT NULL,
  venue_city          VARCHAR(50) NOT NULL,
  venue_type          VARCHAR(20) NOT NULL                   COMMENT 'Internal (VRI property) / External',
  start_date          DATE        NOT NULL,
  end_date            DATE        NOT NULL,
  final_date          DATE        NOT NULL                  COMMENT 'Ngày chung kết',
  contestants_count   SMALLINT    NOT NULL,
  broadcasting_reach  SMALLINT    NOT NULL                  COMMENT 'Số quốc gia phát sóng',
  season_year         SMALLINT    NOT NULL,
  notes_vi            VARCHAR(255) NULL,
  INDEX idx_event_type (event_type_id),
  INDEX idx_dates (start_date, end_date)
) ENGINE=InnoDB COMMENT='Cosmos events lịch sử + hiện tại';

-- ------------------------------------------------------------------
-- 11. dim_sponsor_tier
-- ------------------------------------------------------------------
CREATE TABLE dim_sponsor_tier (
  tier_id        INT         PRIMARY KEY,
  tier_code      VARCHAR(20) NOT NULL UNIQUE,
  tier_name_vi   VARCHAR(40) NOT NULL                       COMMENT 'Title/Kim cương/Vàng/Bạc/Đồng',
  rank_order     TINYINT     NOT NULL                       COMMENT '1=cao nhất',
  min_amount     DECIMAL(18,0) NOT NULL                     COMMENT 'Mức tài trợ tối thiểu VND',
  max_amount     DECIMAL(18,0) NOT NULL,
  benefits_vi    VARCHAR(500) NOT NULL
) ENGINE=InnoDB COMMENT='Hạng tài trợ Cosmos';

-- ------------------------------------------------------------------
-- 12. dim_sponsor
-- ------------------------------------------------------------------
CREATE TABLE dim_sponsor (
  sponsor_id        INT         PRIMARY KEY AUTO_INCREMENT,
  sponsor_code      VARCHAR(20) NOT NULL UNIQUE,
  sponsor_name      VARCHAR(120) NOT NULL                    COMMENT 'Tên thương hiệu/công ty',
  industry_vi       VARCHAR(60) NOT NULL                     COMMENT 'Ngành/lĩnh vực',
  country           VARCHAR(50) NOT NULL DEFAULT 'Việt Nam',
  is_long_term      TINYINT(1)  NOT NULL DEFAULT 0           COMMENT 'Đối tác đa năm',
  notes_vi          VARCHAR(255) NULL
) ENGINE=InnoDB COMMENT='Sponsor pool Cosmos';

-- =====================================================================
-- FACT TABLES
-- =====================================================================

-- ------------------------------------------------------------------
-- F1. fact_room_revenue_daily ⭐ HOTELS MAIN FACT
-- ------------------------------------------------------------------
CREATE TABLE fact_room_revenue_daily (
  fact_id           BIGINT      PRIMARY KEY AUTO_INCREMENT,
  date              DATE        NOT NULL                    COMMENT 'Ngày check-in (booking line)',
  property_id       INT         NOT NULL,
  room_type_id      INT         NOT NULL,
  channel_id        VARCHAR(10) NOT NULL,
  source_market_id  VARCHAR(5)  NOT NULL,
  segment_id        INT         NOT NULL,
  rooms_sold        INT         NOT NULL DEFAULT 0          COMMENT 'Số phòng bán cho line này',
  stay_nights       DECIMAL(5,2) NOT NULL DEFAULT 1         COMMENT 'ALOS line',
  adr               DECIMAL(15,0) NOT NULL                  COMMENT 'Avg Daily Rate VND',
  room_revenue      DECIMAL(18,0) NOT NULL                  COMMENT 'rooms_sold * adr (post-cancellation effective)',
  commission_rate   DECIMAL(5,4) NOT NULL DEFAULT 0,
  commission_amount DECIMAL(15,0) NOT NULL DEFAULT 0,
  is_cancelled      TINYINT(1)  NOT NULL DEFAULT 0          COMMENT 'Cancellation flag',
  loyalty_member_flag TINYINT(1) NOT NULL DEFAULT 0,
  INDEX idx_date_property (date, property_id),
  INDEX idx_date_channel  (date, channel_id),
  INDEX idx_date_source   (date, source_market_id),
  INDEX idx_property_date (property_id, date),
  INDEX idx_channel       (channel_id),
  INDEX idx_source        (source_market_id),
  INDEX idx_room_type     (room_type_id)
) ENGINE=InnoDB COMMENT='Hotels main fact: line grain = day×property×room_type×channel×source×segment';

-- ------------------------------------------------------------------
-- F2. fact_fnb_revenue_daily
-- ------------------------------------------------------------------
CREATE TABLE fact_fnb_revenue_daily (
  fact_id        BIGINT      PRIMARY KEY AUTO_INCREMENT,
  date           DATE        NOT NULL,
  property_id    INT         NOT NULL,
  meal_period    VARCHAR(20) NOT NULL                       COMMENT 'Breakfast/Lunch/Dinner/Beverages/Banquet',
  covers         INT         NOT NULL DEFAULT 0             COMMENT 'Số lượt khách phục vụ',
  fnb_revenue    DECIMAL(18,0) NOT NULL                     COMMENT 'Doanh thu F&B VND',
  fnb_cost       DECIMAL(18,0) NOT NULL DEFAULT 0           COMMENT 'Giá vốn F&B',
  INDEX idx_date_property (date, property_id),
  INDEX idx_property      (property_id)
) ENGINE=InnoDB COMMENT='Doanh thu F&B daily theo meal period';

-- ------------------------------------------------------------------
-- F3. fact_other_revenue_daily
-- ------------------------------------------------------------------
CREATE TABLE fact_other_revenue_daily (
  fact_id           BIGINT      PRIMARY KEY AUTO_INCREMENT,
  date              DATE        NOT NULL,
  property_id       INT         NOT NULL,
  revenue_category  VARCHAR(30) NOT NULL                     COMMENT 'Spa/Golf/Events/Tour/Transport/Other',
  units_sold        INT         NOT NULL DEFAULT 0,
  other_revenue     DECIMAL(18,0) NOT NULL,
  INDEX idx_date_property (date, property_id),
  INDEX idx_category      (revenue_category)
) ENGINE=InnoDB COMMENT='Doanh thu khác (spa, golf, sự kiện, tour) daily';

-- ------------------------------------------------------------------
-- F4. fact_occupancy_daily
-- ------------------------------------------------------------------
CREATE TABLE fact_occupancy_daily (
  fact_id           BIGINT      PRIMARY KEY AUTO_INCREMENT,
  date              DATE        NOT NULL,
  property_id       INT         NOT NULL,
  room_type_id      INT         NOT NULL,
  rooms_available   INT         NOT NULL,
  rooms_sold        INT         NOT NULL,
  occupancy_rate    DECIMAL(6,4) NOT NULL                   COMMENT 'rooms_sold/rooms_available',
  UNIQUE KEY uk_date_room (date, room_type_id),
  INDEX idx_date_property (date, property_id)
) ENGINE=InnoDB COMMENT='Snapshot occupancy daily theo room_type';

-- ------------------------------------------------------------------
-- F5. fact_cost_monthly
-- ------------------------------------------------------------------
CREATE TABLE fact_cost_monthly (
  fact_id        BIGINT      PRIMARY KEY AUTO_INCREMENT,
  ym     CHAR(7)     NOT NULL,
  property_id    INT         NOT NULL,
  cost_category  VARCHAR(30) NOT NULL                       COMMENT 'Labor/F&B Cost/Energy/OTA Commission/Marketing/Maintenance/Depreciation/Other',
  amount         DECIMAL(18,0) NOT NULL,
  UNIQUE KEY uk_ym_prop_cat (ym, property_id, cost_category),
  INDEX idx_property (property_id),
  INDEX idx_ym (ym)
) ENGINE=InnoDB COMMENT='Chi phí monthly per property per category';

-- ------------------------------------------------------------------
-- F6. fact_weather_daily
-- ------------------------------------------------------------------
CREATE TABLE fact_weather_daily (
  fact_id          BIGINT      PRIMARY KEY AUTO_INCREMENT,
  date             DATE        NOT NULL,
  region_id        INT         NOT NULL,
  weather_indicator VARCHAR(20) NOT NULL                    COMMENT 'sunny/cloudy/rain/heavy_rain/storm',
  temperature_avg  DECIMAL(4,1) NULL                        COMMENT 'Nhiệt độ TB °C',
  rainfall_mm      DECIMAL(6,1) NULL,
  notes_vi         VARCHAR(120) NULL,
  UNIQUE KEY uk_date_region (date, region_id),
  INDEX idx_date (date)
) ENGINE=InnoDB COMMENT='Thời tiết daily theo vùng (cho cross-reference scenario)';

-- ------------------------------------------------------------------
-- F7. fact_cosmos_revenue_monthly ⭐ COSMOS MAIN FACT
-- ------------------------------------------------------------------
CREATE TABLE fact_cosmos_revenue_monthly (
  fact_id         BIGINT      PRIMARY KEY AUTO_INCREMENT,
  ym      CHAR(7)     NOT NULL,
  event_id        VARCHAR(20) NULL                          COMMENT 'NULL nếu là tail/non-event revenue',
  revenue_stream  VARCHAR(30) NOT NULL                      COMMENT 'sponsorship/broadcasting/ticket/merchandise/licensing/membership/voting',
  amount          DECIMAL(18,0) NOT NULL,
  notes_vi        VARCHAR(255) NULL,
  INDEX idx_ym (ym),
  INDEX idx_event (event_id),
  INDEX idx_stream (revenue_stream)
) ENGINE=InnoDB COMMENT='Cosmos main fact: doanh thu monthly theo stream';

-- ------------------------------------------------------------------
-- F8. fact_cosmos_sponsorship
-- ------------------------------------------------------------------
CREATE TABLE fact_cosmos_sponsorship (
  fact_id         BIGINT      PRIMARY KEY AUTO_INCREMENT,
  event_id        VARCHAR(20) NOT NULL,
  sponsor_id      INT         NOT NULL,
  tier_id         INT         NOT NULL,
  installment_no  TINYINT     NOT NULL DEFAULT 1            COMMENT 'Đợt thanh toán',
  contract_amount DECIMAL(18,0) NOT NULL,
  paid_amount     DECIMAL(18,0) NOT NULL DEFAULT 0,
  payment_status  VARCHAR(20) NOT NULL DEFAULT 'pending'    COMMENT 'pending/paid/overdue/cancelled',
  payment_due_date DATE       NOT NULL,
  paid_date       DATE        NULL,
  notes_vi        VARCHAR(255) NULL,
  INDEX idx_event (event_id),
  INDEX idx_sponsor (sponsor_id),
  INDEX idx_tier (tier_id),
  INDEX idx_status (payment_status)
) ENGINE=InnoDB COMMENT='Chi tiết sponsorship contract per event x sponsor x installment';

-- ------------------------------------------------------------------
-- F9. fact_cosmos_ticket_sales
-- ------------------------------------------------------------------
CREATE TABLE fact_cosmos_ticket_sales (
  fact_id        BIGINT      PRIMARY KEY AUTO_INCREMENT,
  event_id       VARCHAR(20) NOT NULL,
  tier           VARCHAR(20) NOT NULL                       COMMENT 'VIP/A/B/C',
  quantity_sold  INT         NOT NULL,
  unit_price     DECIMAL(15,0) NOT NULL,
  total_revenue  DECIMAL(18,0) NOT NULL,
  INDEX idx_event (event_id)
) ENGINE=InnoDB COMMENT='Vé sự kiện Cosmos';

-- ------------------------------------------------------------------
-- F10. fact_cosmos_cost
-- ------------------------------------------------------------------
CREATE TABLE fact_cosmos_cost (
  fact_id       BIGINT      PRIMARY KEY AUTO_INCREMENT,
  event_id      VARCHAR(20) NOT NULL,
  cost_category VARCHAR(30) NOT NULL                        COMMENT 'Production/Marketing/Talent/Venue/Logistics/Other',
  amount        DECIMAL(18,0) NOT NULL,
  notes_vi      VARCHAR(255) NULL,
  INDEX idx_event (event_id),
  INDEX idx_cat   (cost_category)
) ENGINE=InnoDB COMMENT='Chi phí sự kiện Cosmos';

-- ------------------------------------------------------------------
-- F11. fact_cosmos_event_attendance
-- ------------------------------------------------------------------
CREATE TABLE fact_cosmos_event_attendance (
  fact_id           BIGINT      PRIMARY KEY AUTO_INCREMENT,
  event_id          VARCHAR(20) NOT NULL,
  date              DATE        NOT NULL,
  attendees_local   INT         NOT NULL DEFAULT 0,
  attendees_intl    INT         NOT NULL DEFAULT 0,
  pr_reach_estimate BIGINT      NOT NULL DEFAULT 0           COMMENT 'PR/Media reach',
  social_engagement INT         NOT NULL DEFAULT 0,
  INDEX idx_event_date (event_id, date)
) ENGINE=InnoDB COMMENT='Daily attendance + PR reach per event (cho cross-business synergy)';

-- =====================================================================
-- METADATA TABLES
-- =====================================================================

CREATE TABLE _meta_tables (
  table_name        VARCHAR(64) PRIMARY KEY,
  table_type        VARCHAR(20) NOT NULL                    COMMENT 'dimension/fact/metadata',
  description_vi    VARCHAR(500) NOT NULL,
  description_en    VARCHAR(500) NOT NULL,
  business_context  VARCHAR(800) NOT NULL,
  grain             VARCHAR(255) NULL                       COMMENT 'Chỉ áp dụng fact'
) ENGINE=InnoDB COMMENT='Metadata các tables';

CREATE TABLE _meta_columns (
  meta_id        INT         PRIMARY KEY AUTO_INCREMENT,
  table_name     VARCHAR(64) NOT NULL,
  column_name    VARCHAR(64) NOT NULL,
  data_type      VARCHAR(40) NOT NULL,
  description_vi VARCHAR(500) NOT NULL,
  description_en VARCHAR(500) NULL,
  unit           VARCHAR(40) NULL,
  example_values VARCHAR(255) NULL,
  UNIQUE KEY uk_table_col (table_name, column_name)
) ENGINE=InnoDB COMMENT='Metadata các columns';

CREATE TABLE _meta_kpi (
  kpi_id            INT         PRIMARY KEY AUTO_INCREMENT,
  kpi_name_vi       VARCHAR(80) NOT NULL,
  kpi_name_en       VARCHAR(80) NOT NULL,
  formula_sql       VARCHAR(2000) NOT NULL,
  description_vi    VARCHAR(800) NOT NULL,
  related_questions VARCHAR(800) NULL
) ENGINE=InnoDB COMMENT='KPI definitions';

CREATE TABLE _meta_glossary (
  glossary_id  INT         PRIMARY KEY AUTO_INCREMENT,
  term_vi      VARCHAR(80) NOT NULL UNIQUE,
  term_en      VARCHAR(80) NOT NULL,
  definition_vi VARCHAR(800) NOT NULL
) ENGINE=InnoDB COMMENT='Thuật ngữ ngành';

SET FOREIGN_KEY_CHECKS = 1;
