-- =====================================================================
-- VRI Group Khối Dịch vụ — Metadata
-- Populate _meta_tables, _meta_columns, _meta_kpi, _meta_glossary
-- =====================================================================

USE vri_services_demo;
SET NAMES utf8mb4;

-- ------------------------------------------------------------------
-- _meta_tables
-- ------------------------------------------------------------------
INSERT INTO _meta_tables (table_name, table_type, description_vi, description_en, business_context, grain) VALUES
('dim_calendar', 'dimension', 'Bảng lịch 18 tháng (06/2024–11/2025) kèm cờ ngày lễ VN, mùa hospitality.', 'Calendar 18 months with Vietnam holiday flags, hospitality season.', 'Dùng để join với mọi fact daily. Hospitality_period giúp nhận diện cao điểm Tết, Hè, mùa quốc tế.', 'Day'),
('dim_business_unit', 'dimension', 'Hai mảng song song: Hotels và Cosmos.', 'Two parallel BUs: Hotels and Cosmos.', 'Hotels = 6 khách sạn (~1.850 tỷ/năm). Cosmos = thi sắc đẹp + membership (~280 tỷ/năm).', NULL),
('dim_region', 'dimension', 'Vùng miền địa lý VN.', 'Vietnam geographic regions.', 'Dùng cho fact_weather_daily và analytics theo vùng.', NULL),
('dim_property', 'dimension', '6 khách sạn của VRI Group.', '6 hotels of VRI Group.', 'Bao gồm 5★ Beach (Royal Beach NT), 5★ City Luxury (Diamond Stars BT), 5★ Golf (Royal Golf LA), 4★ Hill (Royal Đà Lạt), 4★ City Business (Royal Boutique SG), 4★ Heritage (Royal Heritage ĐN). Cột ota_dependency_baseline ghi tỷ trọng OTA chuẩn của property (dùng cho scenario channel reduction).', NULL),
('dim_room_type', 'dimension', 'Loại phòng theo từng property (4-6 loại).', 'Room types per property.', 'Standard/Deluxe/Suite/Villa/Presidential. Mỗi property có cơ cấu khác nhau. ADR baseline đã embed.', NULL),
('dim_channel', 'dimension', '7 kênh đặt phòng kèm hoa hồng mặc định.', '7 booking channels with default commission.', 'Direct (0%), Booking.com (20%), Agoda (22%), Traveloka (17%), Expedia (22%), Travel Agent (15%), MICE Corporate (5%). OTA = Booking+Agoda+Traveloka+Expedia.', NULL),
('dim_source_market', 'dimension', '10 nguồn khách quốc tế + nội địa.', '10 source markets.', 'VN (nội địa), CN, KR, JP, RU, US, UK, DE, AU, OTH. Beach resort phụ thuộc CN/KR/RU. City hotels phụ thuộc VN/JP/KR. Hill resort chủ yếu VN.', NULL),
('dim_guest_segment', 'dimension', 'Phân khúc khách: Leisure/Business/Group/MICE.', 'Guest segments.', 'Leisure dominant cho beach/hill. Business cho city hotel. MICE cho golf + city.', NULL),
('dim_event_type', 'dimension', 'Loại sự kiện Cosmos.', 'Cosmos event types.', 'Pageant National (MCV), Pageant International (MCO), Press Conference, Gala Tour, Crowning Tour.', NULL),
('dim_event', 'dimension', '4 sự kiện Cosmos lịch sử + hiện tại.', '4 Cosmos events.', 'MCV2023 (Đà Lạt), MCO2024 (TP.HCM, peak 10/2024), MCV2025 (Nha Trang, 6/2025), MCO2025 (TP.HCM, 10/2025). Đây là dim bởi mỗi event là 1 entity với metadata cố định.', NULL),
('dim_sponsor_tier', 'dimension', 'Hạng tài trợ Cosmos (Title/Kim cương/Vàng/Bạc/Đồng).', 'Sponsorship tiers.', 'Title (50-80 tỷ), Diamond/Kim cương (30-50 tỷ), Gold/Vàng (15-30 tỷ), Silver/Bạc (5-15 tỷ), Bronze/Đồng (1-5 tỷ).', NULL),
('dim_sponsor', 'dimension', 'Pool sponsor Cosmos (~35).', 'Cosmos sponsor pool.', 'Mix VN brands + global brands. Industry: Banking, Real Estate, F&B, Cosmetics, Aviation, Auto, Telecom.', NULL),

-- Facts
('fact_room_revenue_daily', 'fact', 'Hotels main fact: doanh thu phòng line grain.', 'Hotels main fact: room revenue line grain.', 'Mỗi dòng = 1 booking line ngày × property × room_type × channel × source × segment. Cho phép decompose Revenue = ADR × Occupancy × Rooms và drill 4 chiều cho diagnostic.', 'Day × Property × RoomType × Channel × SourceMarket × Segment'),
('fact_fnb_revenue_daily', 'fact', 'Doanh thu F&B daily theo meal period.', 'F&B revenue daily by meal period.', 'Breakfast/Lunch/Dinner/Beverages/Banquet. Tỷ trọng F&B chuẩn ngành: 18-22% tổng doanh thu hospitality.', 'Day × Property × MealPeriod'),
('fact_other_revenue_daily', 'fact', 'Doanh thu khác (spa, golf, sự kiện, tour).', 'Other revenue daily.', 'Spa, Golf, Events, Tour, Transport, Other. Tỷ trọng 10-12%. Royal Golf Long An có doanh thu Golf vượt trội.', 'Day × Property × Category'),
('fact_occupancy_daily', 'fact', 'Snapshot occupancy daily theo room_type.', 'Daily occupancy snapshot per room type.', 'Tách riêng từ revenue fact để compute occupancy độc lập (rooms_available × rooms_sold). Tránh ambiguity.', 'Day × RoomType'),
('fact_cost_monthly', 'fact', 'Chi phí monthly per property per category.', 'Monthly costs per property per category.', 'Labor, F&B Cost, Energy, OTA Commission, Marketing, Maintenance, Depreciation, Other. Hỗ trợ tính GOP và margin.', 'Month × Property × CostCategory'),
('fact_weather_daily', 'fact', 'Thời tiết daily theo vùng.', 'Daily weather by region.', 'sunny/cloudy/rain/heavy_rain/storm. Anomaly Royal Beach NT 11/2025: 8 ngày heavy_rain (vs trung bình 4).', 'Day × Region'),
('fact_cosmos_revenue_monthly', 'fact', 'Cosmos main fact: doanh thu monthly theo stream.', 'Cosmos main fact.', 'Sponsorship (50-65%), Broadcasting (10-15%), Ticket (5-10%), Merchandise/Licensing (10%), Membership (5%), Voting (5%). Uneven theo lịch event.', 'Month × Stream × Event'),
('fact_cosmos_sponsorship', 'fact', 'Chi tiết hợp đồng sponsorship.', 'Sponsorship contract details.', 'Per event × sponsor × installment. Payment status: pending/paid/overdue/cancelled. Anomaly: NCA Diamond không gia hạn 2025, Highlands Coffee chậm thanh toán đợt 2.', 'Event × Sponsor × Installment'),
('fact_cosmos_ticket_sales', 'fact', 'Vé sự kiện Cosmos.', 'Event ticket sales.', 'VIP (2-5 tr), A (1-2 tr), B (800k-1.5tr), C (500-800k).', 'Event × Tier'),
('fact_cosmos_cost', 'fact', 'Chi phí sự kiện Cosmos.', 'Event costs.', 'Production 40%, Marketing 15%, Talent 15%, Venue 10%, Logistics 10%, Other 10%.', 'Event × Category'),
('fact_cosmos_event_attendance', 'fact', 'Daily attendance + PR reach per event.', 'Daily attendance and PR reach.', 'Phục vụ phân tích cross-business synergy (event tổ chức tại property VRI).', 'Event × Day');

-- ------------------------------------------------------------------
-- _meta_columns (chọn lọc các cột trọng yếu)
-- ------------------------------------------------------------------
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
-- dim_calendar
('dim_calendar', 'date', 'DATE', 'Ngày', 'Date', NULL, '2025-11-15'),
('dim_calendar', 'is_holiday', 'TINYINT(1)', 'Cờ ngày lễ VN', 'VN holiday flag', '0/1', '0,1'),
('dim_calendar', 'hospitality_period', 'VARCHAR(40)', 'Mùa hospitality (Tết/30-4/Hè peak/Quốc tế/Off-peak/Bình thường)', 'Hospitality season', NULL, 'Tết Nguyên Đán, Hè peak, Off-peak, Bình thường'),
-- dim_property
('dim_property', 'property_name', 'VARCHAR(120)', 'Tên khách sạn', 'Property name', NULL, 'Royal Beach Resort Nha Trang'),
('dim_property', 'category_vi', 'VARCHAR(50)', 'Loại khách sạn', 'Category', NULL, 'Beach Resort, Hill Resort, City Luxury, Golf Resort, Heritage, City Business'),
('dim_property', 'total_rooms', 'SMALLINT', 'Tổng số phòng', 'Total rooms', 'phòng', '138, 256, 80, 200, 120, 150'),
('dim_property', 'ota_dependency_baseline', 'DECIMAL(5,4)', 'Tỷ trọng OTA baseline', 'OTA dependency baseline', '%', '0.30 - 0.58'),
-- dim_channel
('dim_channel', 'commission_rate_default', 'DECIMAL(5,4)', 'Hoa hồng kênh mặc định', 'Default commission', '%', '0.00 (Direct), 0.20 (Booking), 0.22 (Agoda)'),
('dim_channel', 'channel_category', 'VARCHAR(20)', 'Phân loại kênh', 'Channel category', NULL, 'Direct, OTA, Wholesale, Corporate'),
-- fact_room_revenue_daily
('fact_room_revenue_daily', 'rooms_sold', 'INT', 'Số phòng bán cho line này', 'Rooms sold', 'phòng', '0-50'),
('fact_room_revenue_daily', 'adr', 'DECIMAL(15,0)', 'Giá phòng trung bình (Average Daily Rate)', 'Average Daily Rate', 'VND', '1500000-12000000'),
('fact_room_revenue_daily', 'room_revenue', 'DECIMAL(18,0)', 'Doanh thu phòng', 'Room revenue', 'VND', NULL),
('fact_room_revenue_daily', 'commission_amount', 'DECIMAL(15,0)', 'Hoa hồng kênh phải trả', 'Commission amount', 'VND', NULL),
('fact_room_revenue_daily', 'is_cancelled', 'TINYINT(1)', 'Cờ huỷ booking', 'Cancellation flag', '0/1', '0,1'),
-- fact_cosmos_revenue_monthly
('fact_cosmos_revenue_monthly', 'revenue_stream', 'VARCHAR(30)', 'Loại doanh thu', 'Revenue stream', NULL, 'sponsorship, broadcasting, ticket, merchandise, licensing, membership, voting'),
('fact_cosmos_revenue_monthly', 'amount', 'DECIMAL(18,0)', 'Số tiền', 'Amount', 'VND', NULL),
-- fact_cosmos_sponsorship
('fact_cosmos_sponsorship', 'payment_status', 'VARCHAR(20)', 'Trạng thái thanh toán', 'Payment status', NULL, 'pending, paid, overdue, cancelled'),
('fact_cosmos_sponsorship', 'contract_amount', 'DECIMAL(18,0)', 'Giá trị hợp đồng', 'Contract amount', 'VND', NULL),
-- fact_weather_daily
('fact_weather_daily', 'weather_indicator', 'VARCHAR(20)', 'Chỉ báo thời tiết', 'Weather indicator', NULL, 'sunny, cloudy, rain, heavy_rain, storm');

-- ------------------------------------------------------------------
-- _meta_kpi
-- ------------------------------------------------------------------
INSERT INTO _meta_kpi (kpi_name_vi, kpi_name_en, formula_sql, description_vi, related_questions) VALUES
('Doanh thu phòng', 'Room Revenue',
 'SELECT SUM(room_revenue) FROM fact_room_revenue_daily WHERE date BETWEEN ? AND ? AND is_cancelled=0',
 'Tổng doanh thu phòng trong kỳ. Tính chỉ những booking không huỷ.',
 'Doanh thu phòng tháng 11/2025; YoY phòng theo property'),
('Tổng doanh thu Hotels', 'Total Hotels Revenue',
 'SELECT SUM(room_revenue)+SUM(fnb_revenue)+SUM(other_revenue) FROM ... daily summed',
 'Tổng doanh thu Hotels = Room + F&B + Other. Cấu trúc chuẩn ngành: 70-72% phòng, 18-22% F&B, 10-12% other.',
 'Tình hình kinh doanh Hotels tháng X'),
('ADR (Giá phòng trung bình)', 'Average Daily Rate (ADR)',
 'SELECT SUM(room_revenue)/SUM(rooms_sold) FROM fact_room_revenue_daily WHERE is_cancelled=0',
 'Giá phòng trung bình = doanh thu phòng / số phòng bán. ADR là 1 trong 2 lever chính của Revenue.',
 'ADR Royal Beach NT giảm; ADR theo channel/source'),
('Occupancy Rate (Công suất phòng)', 'Occupancy Rate',
 'SELECT SUM(rooms_sold)/SUM(rooms_available) FROM fact_occupancy_daily',
 'Công suất phòng = phòng bán / phòng có sẵn. Lever thứ 2 của Revenue.',
 'Occupancy 11/2025 vs 11/2024'),
('RevPAR', 'Revenue per Available Room',
 'ADR × Occupancy Rate, hoặc SUM(room_revenue)/SUM(rooms_available)',
 'Doanh thu trên mỗi phòng có sẵn. KPI tổng hợp ADR và Occupancy.',
 'RevPAR Royal Beach NT giảm 15%'),
('TRevPAR', 'Total Revenue per Available Room',
 '(SUM(room_revenue)+SUM(fnb_revenue)+SUM(other_revenue)) / SUM(rooms_available)',
 'Tổng doanh thu trên mỗi phòng có sẵn — bao gồm cả F&B và other.',
 'TRevPAR theo property'),
('GOP (Gross Operating Profit)', 'Gross Operating Profit',
 'Total Revenue − (Labor + F&B Cost + Energy + Commission + Marketing + Maintenance)',
 'Lợi nhuận gộp vận hành. Mục tiêu 30-40% cho 5★, 25-35% cho 4★.',
 'GOP margin portfolio'),
('GOPPAR', 'GOP per Available Room',
 'GOP / SUM(rooms_available)',
 'GOP trên mỗi phòng có sẵn — chỉ số sinh lời cuối cùng.',
 'GOPPAR YoY'),
('ALOS (Thời gian lưu trú TB)', 'Average Length of Stay',
 'AVG(stay_nights) trên fact_room_revenue_daily',
 'Thời gian lưu trú trung bình. Ngành VN: VN ~2.0 đêm, KR ~3.5, EU ~5+.',
 'ALOS theo source market'),
('OTA Share', 'OTA Share',
 'SUM(room_revenue WHERE channel_category=OTA) / SUM(room_revenue)',
 'Tỷ trọng doanh thu từ kênh trực tuyến (Booking/Agoda/Traveloka/Expedia). Baseline ~50% portfolio, từ 30% (Royal Golf) đến 58% (Royal Beach NT post-anomaly).',
 'OTA dependency theo property; scenario giảm OTA'),
('F&B Contribution', 'F&B Contribution',
 'SUM(fnb_revenue) / (SUM(room_revenue)+SUM(fnb_revenue)+SUM(other_revenue))',
 'Tỷ trọng F&B trong tổng doanh thu. Chuẩn 18-22%.',
 'F&B contribution by property'),
('Cosmos Sponsorship Concentration', 'Sponsor Concentration',
 'Top 5 sponsors share of total sponsorship per event',
 'Tỷ trọng top 5 sponsor. Risk nếu >70% (concentration risk).',
 'Sponsor risk Cosmos; YoY sponsor mix');

-- ------------------------------------------------------------------
-- _meta_glossary
-- ------------------------------------------------------------------
INSERT INTO _meta_glossary (term_vi, term_en, definition_vi) VALUES
('ADR', 'Average Daily Rate', 'Giá phòng trung bình = Doanh thu phòng / Số phòng đã bán. Đơn vị VND.'),
('Công suất phòng', 'Occupancy Rate', 'Tỷ lệ phòng đã bán so với phòng có sẵn. Đơn vị %.'),
('RevPAR', 'Revenue per Available Room', 'Doanh thu trên mỗi phòng có sẵn = ADR × Occupancy.'),
('TRevPAR', 'Total Revenue per Available Room', 'Tổng doanh thu (phòng + F&B + khác) trên mỗi phòng có sẵn.'),
('GOP', 'Gross Operating Profit', 'Lợi nhuận gộp vận hành = Doanh thu − Chi phí vận hành (lao động, F&B cost, hoa hồng, năng lượng, marketing, bảo trì).'),
('GOPPAR', 'GOP per Available Room', 'GOP / phòng có sẵn.'),
('ALOS', 'Average Length of Stay', 'Thời gian lưu trú trung bình của khách (số đêm/lượt).'),
('OTA', 'Online Travel Agent', 'Đại lý đặt phòng trực tuyến. Booking.com, Agoda, Traveloka, Expedia. Hoa hồng 17-22%.'),
('GSS', 'Guest Satisfaction Score', 'Điểm hài lòng khách (thường thang 1-5 hoặc 1-10).'),
('Channel Mix', 'Channel Mix', 'Tỷ trọng các kênh đặt phòng (Direct/OTA/Travel Agent/Corporate).'),
('Source Market', 'Source Market', 'Quốc gia/vùng nguồn khách (VN, CN, KR, JP, RU, US, ...).'),
('MICE', 'Meetings, Incentives, Conferences, Exhibitions', 'Khách đoàn hội nghị/sự kiện công ty.'),
('Title Sponsor', 'Title Sponsor', 'Nhà tài trợ chính của sự kiện — xuất hiện trong tên sự kiện. Mức 50-80 tỷ.'),
('Cosmoxperience', 'Cosmoxperience', 'Chương trình membership của Cosmos: 5-50 triệu/năm tuỳ tier (Diamond, Gold, Silver).'),
('Khối Dịch vụ', 'Services Division', 'Khối kinh doanh của VRI Group, gồm 2 mảng: Hotels (6 khách sạn) và Cosmos (cuộc thi sắc đẹp + membership).');
