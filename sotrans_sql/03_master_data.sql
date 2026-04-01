-- SOTRANS Demo Database — Master Data

USE `sotrans_demo`;


-- service_types (5 rows)
TRUNCATE TABLE `service_types`;
INSERT INTO `service_types` (`service_type_id`,`service_code`,`service_name_vi`,`service_name_en`,`margin_target_pct`) VALUES
(1,'FF','Giao nhận vận tải quốc tế','International Freight Forwarding',11.00),
(2,'WH','Dịch vụ kho bãi','Warehousing',30.00),
(3,'ICD','Khai thác cảng/ICD','Port & ICD Operations',35.00),
(4,'IWT','Vận tải đường thủy','Inland Waterway Transport',17.00),
(5,'CL','Contract Logistics','Contract Logistics',22.00);

-- regions (5 rows)
TRUNCATE TABLE `regions`;
INSERT INTO `regions` (`region_id`,`region_name`,`province`) VALUES
(1,'Miền Nam','Hồ Chí Minh'),
(2,'Miền Nam','Bình Dương'),
(3,'Miền Nam','Long An'),
(4,'Miền Nam','Cần Thơ'),
(5,'Miền Bắc','Hà Nội');

-- warehouses (7 rows)
TRUNCATE TABLE `warehouses`;
INSERT INTO `warehouses` (`warehouse_id`,`warehouse_code`,`warehouse_name`,`location`,`region_id`,`capacity_sqm`,`warehouse_type`,`monthly_fixed_cost_vnd`,`utilization_target_pct`,`is_active`) VALUES
(1,'WH_PHM','Kho Sotrans Phú Mỹ','KCN Phú Mỹ, Bà Rịa-Vũng Tàu',1,50000,'kho_da_chuc_nang',1200000000,85.00,1),
(2,'WH_TDC','Kho Sotrans Thủ Đức','Km9 QL1A, Thủ Đức, HCM',1,35000,'kho_da_chuc_nang',850000000,85.00,1),
(3,'WH_LBH','Kho Sotrans Long Bình','KCN Long Bình, Đồng Nai',2,12000,'kho_thuong_mai',320000000,85.00,1),
(4,'WH_LAN','Kho Sotrans Long An','Long An',3,9000,'kho_thuong_mai',240000000,80.00,1),
(5,'WH_CTH','Kho Sotrans Cần Thơ','27 Lê Hồng Phong, Cần Thơ',4,3000,'kho_thuong_mai',90000000,80.00,1),
(6,'WH_HNI','Kho Sotrans Hà Nội','142 Đội Cấn, Ba Đình, HN',5,8500,'kho_da_chuc_nang',220000000,80.00,1),
(7,'WH_TTU','Kho Sotrans Tân Tức','Bình Chánh, HCM',1,15000,'kho_ngoai_quan',380000000,85.00,1);

-- ports_depots (4 rows)
TRUNCATE TABLE `ports_depots`;
INSERT INTO `ports_depots` (`port_id`,`port_code`,`port_name`,`port_type`,`location`,`region_id`,`area_sqm`,`capacity_teu_month`) VALUES
(1,'ICD_STG','Cảng Sotrans ICD Thủ Đức','ICD','Km9 QL Hà Nội, Thủ Đức',1,100000,6000),
(2,'ICD_LBH','Cảng SOWATCO Long Bình','cang_song','Long Bình, Đồng Nai',2,50000,2000),
(3,'DEP_MPH','Depot Sotrans Mỹ Phước','depot','Mỹ Phước, Bình Dương',2,22000,NULL),
(4,'DEP_NTR','Depot Sotrans Nhơn Trạch','depot','Nhơn Trạch, Đồng Nai',2,8500,NULL);

-- freight_routes (8 rows)
TRUNCATE TABLE `freight_routes`;
INSERT INTO `freight_routes` (`route_id`,`route_code`,`origin_port`,`destination_port`,`destination_country`,`transport_mode`,`transit_days`,`is_active`) VALUES
(1,'HCM-NRT-SEA','SGN','NRT','Nhật Bản','sea',18,1),
(2,'HCM-ICN-SEA','SGN','ICN','Hàn Quốc','sea',10,1),
(3,'HCM-LAX-SEA','SGN','LAX','Hoa Kỳ','sea',28,1),
(4,'HCM-RTM-SEA','SGN','RTM','Châu Âu','sea',32,1),
(5,'HCM-SIN-SEA','SGN','SIN','Singapore','sea',5,1),
(6,'HCM-NRT-AIR','SGN','NRT','Nhật Bản','air',2,1),
(7,'HCM-ICN-AIR','SGN','ICN','Hàn Quốc','air',2,1),
(8,'HCM-LAX-AIR','SGN','LAX','Hoa Kỳ','air',1,1);

-- customers (21 rows)
TRUNCATE TABLE `customers`;
INSERT INTO `customers` (`customer_id`,`customer_code`,`customer_name`,`industry`,`country_origin`,`tier`,`account_manager`,`contract_start_date`,`is_active`) VALUES
(1,'CUST_CGR','Cargill Vietnam','FMCG/Nông sản','Hoa Kỳ','platinum','Nguyễn Thanh Hải','2015-03-01',1),
(2,'CUST_PEP','PepsiCo Vietnam','FMCG','Hoa Kỳ','platinum','Trần Minh Khoa','2014-06-01',1),
(3,'CUST_PNG','P&G Vietnam','FMCG','Hoa Kỳ','platinum','Lê Thu Hương','2013-01-01',1),
(4,'CUST_TXH','Texhong Vietnam','Dệt may','Trung Quốc','platinum','Phạm Đức Trung','2016-09-01',1),
(5,'CUST_SDI','Samsung SDI Vietnam','Điện tử','Hàn Quốc','gold','Nguyễn Văn Bình','2018-04-01',1),
(6,'CUST_FLC','FrieslandCampina Vietnam','FMCG/Sữa','Hà Lan','gold','Vũ Thị Mai','2017-02-01',1),
(7,'CUST_HLM','Holcim Vietnam','Vật liệu xây dựng','Thụy Sĩ','gold','Đỗ Văn Sơn','2016-05-01',1),
(8,'CUST_COL','Colgate-Palmolive Vietnam','FMCG','Hoa Kỳ','gold','Hoàng Thị Lan','2015-08-01',1),
(9,'CUST_UNP','Uni-President Vietnam','FMCG/Thực phẩm','Đài Loan','gold','Bùi Quang Huy','2017-11-01',1),
(10,'CUST_MSK','Maersk Vietnam','Vận tải biển','Đan Mạch','silver','Ngô Thị Hà','2019-03-01',1),
(11,'CUST_HPG','Hòa Phát Logistics','Thép/CN nặng','Việt Nam','silver','Đinh Văn Hùng','2018-07-01',1),
(12,'CUST_VNM','Vinamilk','FMCG/Sữa','Việt Nam','silver','Lý Thị Bích','2016-01-01',1),
(13,'CUST_MSN','Masan Consumer','FMCG','Việt Nam','silver','Phan Hữu Nghĩa','2017-04-01',1),
(14,'CUST_GVT','GreenFeed Vietnam','Chăn nuôi/Thức ăn','Việt Nam','silver','Trương Minh Tuấn','2019-06-01',1),
(15,'CUST_TGI','Thai Group International','Thực phẩm','Thái Lan','silver','Cao Thị Ngọc','2020-01-01',1),
(16,'CUST_SKN','Schaeffler Vietnam','Cơ khí/Điện tử','Đức','bronze','Lưu Văn Dũng','2020-05-01',1),
(17,'CUST_YRD','Yarn Dyeing VN (Texhong Group)','Dệt may','Trung Quốc','bronze','Phạm Thị Tuyết','2019-09-01',1),
(18,'CUST_DHL','DHL Supply Chain Vietnam','Logistics','Đức','bronze','Đặng Văn Minh','2021-02-01',1),
(19,'CUST_BSH','Bosch Vietnam','Điện tử/Công nghiệp','Đức','bronze','Nguyễn Phúc An','2021-07-01',1),
(20,'CUST_LPO','LG Electronics Vietnam','Điện tử','Hàn Quốc','bronze','Trần Thị Bảo','2020-11-01',1),
(21,'CUST_OTH','Khách hàng khác','Đa ngành','Đa quốc gia','bronze',NULL,'2013-01-01',1);

-- annual_targets (10 rows)
TRUNCATE TABLE `annual_targets`;
INSERT INTO `annual_targets` (`target_id`,`fiscal_year`,`service_type_id`,`target_revenue_vnd`,`target_gross_profit_vnd`) VALUES
(1,2023,1,966000000000,106260000000),
(2,2023,2,625600000000,187680000000),
(3,2023,3,450800000000,157780000000),
(4,2023,4,248400000000,42228000000),
(5,2023,5,73600000000,16192000000),
(6,2024,1,1050000000000,115500000000),
(7,2024,2,680000000000,204000000000),
(8,2024,3,490000000000,171500000000),
(9,2024,4,270000000000,45900000000),
(10,2024,5,80000000000,17600000000);
