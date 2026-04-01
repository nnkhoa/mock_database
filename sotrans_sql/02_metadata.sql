-- SOTRANS Demo Database — Metadata

USE `sotrans_demo`;
SET FOREIGN_KEY_CHECKS=0;


-- _meta_tables
TRUNCATE TABLE `_meta_tables`;
INSERT INTO `_meta_tables` (`table_name`,`description_vi`,`description_en`,`business_context`,`grain`,`row_count_approx`) VALUES
('annual_targets','Kế hoạch doanh thu và lợi nhuận theo năm và mảng dịch vụ','Annual revenue and gross profit targets by service','Dùng để so sánh thực tế vs kế hoạch (pace analysis).','1 dòng = 1 năm × 1 mảng dịch vụ',10),
('customer_contracts','Hợp đồng dịch vụ và rate thỏa thuận với khách hàng','Customer service contracts and agreed rates','Nguồn gốc rate tính doanh thu và margin. Route freight hay kho bãi đều có contract.','1 dòng = 1 hợp đồng',50),
('customers','Danh sách khách hàng — 20 khách lớn + others','Customer master data','tier phân loại: platinum/gold/silver/bronze theo đóng góp doanh thu.','1 dòng = 1 khách hàng',21),
('freight_routes','Tuyến vận tải quốc tế — sea, air, multimodal','International freight routes','route_code như HCM-NRT-SEA = SGN→Narita Sea freight.','1 dòng = 1 tuyến',8),
('freight_shipments','Lô hàng freight forwarding theo ngày và khách hàng','Individual freight shipment records','Fact table chính cho Freight Forwarding. Revenue, cost, margin tính tự động.','1 dòng = 1 lô hàng',3000),
('icd_teu_throughput','Sản lượng container (TEU) qua cảng/ICD hàng tháng','Monthly TEU throughput at ICD and ports','Fact table cho mảng Cảng/ICD. TEU = Twenty-foot Equivalent Unit.','1 dòng = 1 cảng × 1 loại hàng × 1 tháng',100),
('inland_waterway_trips','Chuyến vận tải đường thủy nội địa (SOWATCO)','Inland waterway freight trips','Fact table cho mảng IWT. Vận chuyển hàng hóa bằng sà lan trên sông Mekong/Đồng Nai.','1 dòng = 1 chuyến tàu',3200),
('ports_depots','Cảng và depot của Sotrans — ICD Thủ Đức, SOWATCO, v.v.','SOTRANS ports and depots','ICD_STG là cảng lớn nhất, 6.000 TEU/tháng công suất.','1 dòng = 1 cảng/depot',4),
('regions','Phân vùng địa lý hoạt động của Sotrans','Geographic regions','Miền Nam (HCM, Bình Dương, Long An, Cần Thơ) và Miền Bắc (HN).','1 dòng = 1 tỉnh/vùng',5),
('service_types','Danh mục 5 mảng dịch vụ của Sotrans','SOTRANS service catalog','5 service lines: FF, WH, ICD, IWT, CL','1 dòng = 1 mảng dịch vụ',5),
('shipping_rate_market','Giá cước vận tải biển thị trường theo tuyến và tháng','Market freight rates by route and month','Dùng để so sánh với contract rate trong customer_contracts → phát hiện margin squeeze.','1 dòng = 1 tuyến × 1 tháng',144),
('warehouse_occupancy','Tình trạng sử dụng kho theo tháng, kho, khách hàng','Monthly warehouse utilization by customer and warehouse','Fact table cho mảng Kho bãi. Dùng để tính utilization = occupied/capacity.','1 dòng = 1 khách × 1 kho × 1 tháng',600),
('warehouses','Danh sách kho của Sotrans — 230.000m² toàn quốc','SOTRANS warehouse master data','Master table. capacity_sqm là mẫu số để tính warehouse utilization.','1 dòng = 1 kho',7);

-- _meta_kpi
TRUNCATE TABLE `_meta_kpi`;
INSERT INTO `_meta_kpi` (`kpi_id`,`kpi_name`,`kpi_name_vi`,`formula_sql`,`description_vi`,`related_questions`) VALUES
(1,'Freight Gross Margin %','Biên lợi nhuận gộp Freight','SELECT ROUND(SUM(gross_profit_vnd)*100.0/SUM(revenue_vnd),2) FROM freight_shipments WHERE ...','Phần trăm lợi nhuận gộp sau khi trừ cước tàu và handling. Target 11%. Nếu <8% cần điều tra.','T2, T5'),
(2,'Warehouse Utilization %','Tỷ lệ lấp đầy kho','SELECT SUM(o.occupied_sqm)*100.0/SUM(w.capacity_sqm) FROM warehouse_occupancy o JOIN warehouses w ON ...','Tỷ lệ diện tích kho đang sử dụng / tổng diện tích. Target 80-85%. <70% là warning.','T1, T3'),
(3,'Revenue Pace %','Tiến độ doanh thu so với kế hoạch năm','SELECT SUM(revenue_vnd)*100.0/(SELECT target_revenue_vnd FROM annual_targets WHERE ...) FROM ...','YTD actual / annual target × 100. Sau 9 tháng nên đạt 70-75% để dự báo đạt kế hoạch.','T4'),
(4,'TEU Throughput','Sản lượng container qua cảng','SELECT SUM(teu_count) FROM icd_teu_throughput WHERE port_id=1 AND ...','Đơn vị đo lường hoạt động cảng ICD. 1 TEU = 1 container 20ft. Target ~6.000 TEU/tháng.','T1'),
(5,'Customer Total Margin %','Biên lợi nhuận tổng hợp theo khách hàng','SELECT (SUM(ff.gp)+SUM(wh.gp))/(SUM(ff.rev)+SUM(wh.rev))*100 FROM (freight_shipments + warehouse_occupancy) ...','Margin tổng hợp tất cả dịch vụ cho 1 khách hàng. Dùng để xếp hạng profitability.','T5'),
(6,'YoY Revenue Growth %','Tăng trưởng doanh thu so với cùng kỳ năm trước','SELECT (this_yr - last_yr)/last_yr*100 FROM (SELECT SUM revenue by year) ...','Thường được tính theo tháng để phát hiện decline trend như Scenario 1.','T1, T4');

-- _meta_glossary
TRUNCATE TABLE `_meta_glossary`;
INSERT INTO `_meta_glossary` (`term_id`,`term_vi`,`term_en`,`abbreviation`,`definition`,`related_table`,`related_column`) VALUES
(1,'Lô hàng','Shipment','N/A','Một đơn vị vận chuyển hàng hóa từ người gửi đến người nhận, thường bao gồm nhiều container hoặc kiện hàng.','freight_shipments','shipment_id'),
(2,'TEU','Twenty-foot Equivalent Unit','TEU','Đơn vị đo kích thước container tiêu chuẩn. 1 TEU = 1 container 20 feet. Container 40 feet = 2 TEU.','icd_teu_throughput','teu_count'),
(3,'CBM','Cubic Meter','CBM','Đơn vị đo thể tích hàng hóa: mét khối. Dùng để tính cước vận tải biển.','freight_shipments','cbm'),
(4,'ICD','Inland Container Depot','ICD','Cảng nội địa — kho chứa container trong đất liền, có chức năng thông quan như cảng biển.','ports_depots','port_type'),
(5,'Freight Forwarding','Giao nhận vận tải','FF','Dịch vụ tổ chức vận chuyển hàng hóa quốc tế thay mặt chủ hàng — booking tàu, làm thủ tục HQ, giao nhận.','service_types','service_code'),
(6,'Margin','Biên lợi nhuận gộp','N/A','(Revenue - Cost) / Revenue × 100%. Đo hiệu quả sinh lời trên từng dịch vụ.','freight_shipments','gross_margin_pct'),
(7,'Utilization','Tỷ lệ lấp đầy kho','N/A','Diện tích đang sử dụng / Tổng diện tích × 100%. Target 80-85%.','warehouse_occupancy','occupied_sqm'),
(8,'Contract Rate','Giá hợp đồng','N/A','Mức giá cước thỏa thuận trong hợp đồng dài hạn với khách hàng. Thường thấp hơn giá thị trường spot.','customer_contracts','rate_usd_per_cbm'),
(9,'Market Rate','Giá thị trường','N/A','Giá cước vận tải trên thị trường giao ngay (spot market). Biến động theo cung-cầu toàn cầu.','shipping_rate_market','market_rate_usd_per_cbm'),
(10,'SOWATCO','South Waterway Transport Co','N/A','Công ty con của Sotrans chuyên vận tải đường thủy nội địa trên hệ thống sông Đông Nam Bộ và ĐBSCL.','inland_waterway_trips',NULL),
(11,'Platinum/Gold/Silver/Bronze','Phân hạng khách hàng','N/A','Platinum: doanh thu >100 tỷ/năm. Gold: 50-100 tỷ. Silver: 20-50 tỷ. Bronze: <20 tỷ.','customers','tier'),
(12,'YoY','Year-over-Year','YoY','So sánh cùng kỳ năm trước. VD: doanh thu T9/2024 vs T9/2023.',NULL,NULL),
(13,'YTD','Year-to-Date','YTD','Lũy kế từ đầu năm đến hiện tại. Dùng trong pace analysis.',NULL,NULL),
(14,'Peak Season','Mùa cao điểm','N/A','Q4 (T10-T12): xuất khẩu dệt may, điện tử tăng vọt cho thị trường Mỹ/EU chuẩn bị Giáng sinh. Freight +20-30%.',NULL,NULL);
