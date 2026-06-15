-- =====================================================================
-- 02_metadata.sql — _meta_tables/_meta_columns/_meta_kpi/_meta_glossary
-- Nguồn truth để AI engine (MCP) hiểu schema bằng tiếng Việt.
-- =====================================================================
USE tondonga_demo;

INSERT INTO _meta_tables (table_name, description_vi, description_en, business_context) VALUES
('dim_calendar','Bảng lịch theo ngày','Date dimension (one row per day)','Phục vụ phân tích thời gian, seasonality, YoY. 18 tháng (2024-01..2025-06).'),
('dim_region','Vùng địa lý','Geographic region dimension','Nội địa: 3 miền Bắc/Trung/Nam -> tỉnh. Xuất khẩu: quốc gia (EU/ASEAN/Đông Á/Bắc Mỹ).'),
('dim_channel','Kênh bán hàng','Sales channel dimension','Nội địa (Đại lý cấp 1, Nhà phân phối vùng, Dự án/Công trình) + Xuất khẩu trực tiếp.'),
('dim_product','Danh mục sản phẩm','Product catalog dimension','Hierarchy nhóm -> SKU. Tôn màu ASP/margin cao nhất, thép hộp thấp nhất.'),
('dim_customer','Khách hàng/đại lý','Customer dimension','~50 đại lý/khách. Phân bổ Nam>Bắc>Trung; XK theo quốc gia.'),
('dim_hrc_price','Giá HRC nguyên liệu theo tháng','Monthly HRC raw material price','USD/tấn + tỷ giá + quy đổi VND. 3 tháng cuối +7% (margin erosion). Join theo YYYY-MM.'),
('dim_target','Kế hoạch sản lượng/doanh thu theo tháng','Monthly plan/target','Phân bổ mục tiêu năm 780.000 tấn / 18.000 tỷ theo seasonality. Standalone, join theo period.'),
('fact_sales','FACT chính - bán hàng transaction-level','Main sales fact (transaction grain)','1 dòng = 1 line item (ngày x khách x SP x kênh). LUÔN dùng net_revenue_vnd cho doanh thu.'),
('fact_cogs','Giá vốn hàng bán (1-1 với fact_sales)','Cost of goods sold fact (1-1)','Tách HRC/other/conversion. hrc_cost_vnd đã nằm trong total_cogs_vnd - KHÔNG cộng thêm.');

INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
('dim_calendar','date','DATE','Ngày (PK)','Day','','2024-01-15'),
('dim_calendar','year','INT','Năm','Year','','2024;2025'),
('dim_calendar','quarter','INT','Quý','Quarter','','1;2;3;4'),
('dim_calendar','month','INT','Tháng','Month','','1..12'),
('dim_calendar','season','VARCHAR','Mùa','Season','','Mùa khô;Mùa mưa'),
('dim_calendar','is_holiday','TINYINT','Ngày lễ/Tết','Holiday flag','','0;1'),
('dim_region','region_id','INT','Mã vùng (PK)','Region id','','1;15;26'),
('dim_region','region_name','VARCHAR','Tên tỉnh/quốc gia','Region name','','TP.HCM;Đà Nẵng;Bỉ'),
('dim_region','macro_area','VARCHAR','Khu vực lớn','Macro area','','Bắc;Trung;Nam;Nước ngoài'),
('dim_region','region_type','VARCHAR','Loại vùng','Region type','','Nội địa;Xuất khẩu'),
('dim_region','country','VARCHAR','Quốc gia','Country','','Việt Nam;Hoa Kỳ'),
('dim_channel','channel_name','VARCHAR','Kênh chính','Channel','','Nội địa;Xuất khẩu'),
('dim_channel','sub_channel','VARCHAR','Kênh con','Sub-channel','','Đại lý cấp 1;Dự án/Công trình'),
('dim_product','product_group','VARCHAR','Nhóm SP','Product group','','Tôn màu;Tôn lạnh;CRC'),
('dim_product','thickness_mm','DECIMAL','Độ dày','Thickness','mm','0.40;1.20'),
('dim_product','asp_benchmark_vnd_per_ton','DECIMAL','ASP tham chiếu','Benchmark ASP','VND/tấn','27300000'),
('dim_product','margin_tier','VARCHAR','Hạng margin','Margin tier','','Cao;Trung;Thấp'),
('dim_product','popularity_weight','DECIMAL','Trọng số Pareto','Pareto weight','','6.0;0.3'),
('dim_customer','customer_tier','VARCHAR','Quy mô KH','Customer size','','Lớn;Vừa;Nhỏ'),
('dim_hrc_price','price_month','VARCHAR','Tháng (PK)','Month','','2025-06'),
('dim_hrc_price','hrc_usd_per_ton','DECIMAL','Giá HRC','HRC price','USD/tấn','519'),
('dim_hrc_price','usd_vnd_rate','DECIMAL','Tỷ giá','FX rate','VND/USD','25400'),
('dim_hrc_price','hrc_vnd_per_ton','DECIMAL','Giá HRC quy đổi','HRC price VND','VND/tấn','13180000'),
('dim_target','period','VARCHAR','Tháng (PK)','Period','','2025-06'),
('dim_target','target_volume_ton','DECIMAL','Mục tiêu sản lượng','Target volume','tấn','78000'),
('dim_target','target_revenue_vnd','DECIMAL','Mục tiêu doanh thu','Target revenue','VND','1800000000000'),
('fact_sales','sale_id','BIGINT','Mã giao dịch (PK)','Sale id','','1'),
('fact_sales','sale_date','DATE','Ngày bán','Sale date','','2025-06-10'),
('fact_sales','quantity_ton','DECIMAL','Khối lượng','Quantity','tấn','6.250'),
('fact_sales','asp_vnd_per_ton','DECIMAL','Giá bán net','Net ASP','VND/tấn','24700000'),
('fact_sales','net_revenue_vnd','DECIMAL','Doanh thu thuần','Net revenue','VND','154375000'),
('fact_cogs','hrc_cost_vnd','DECIMAL','Chi phí HRC','HRC cost','VND','~70% total_cogs'),
('fact_cogs','other_material_cost_vnd','DECIMAL','Vật liệu khác (kẽm/sơn)','Other material','VND',''),
('fact_cogs','conversion_cost_vnd','DECIMAL','Gia công (NL/nhân công)','Conversion cost','VND',''),
('fact_cogs','total_cogs_vnd','DECIMAL','Tổng giá vốn','Total COGS','VND','= HRC+other+conversion');

INSERT INTO _meta_kpi (kpi_name, formula_sql, description_vi, related_questions) VALUES
('net_revenue','SUM(fact_sales.net_revenue_vnd)','Doanh thu thuần (VND)','Q1,Q2,Q4,Q5'),
('volume_ton','SUM(fact_sales.quantity_ton)','Sản lượng (tấn)','Q1,Q5'),
('asp','SUM(net_revenue_vnd)/SUM(quantity_ton)','Giá bán bình quân (VND/tấn)','Q1,Q4'),
('gross_margin','(SUM(net_revenue_vnd)-SUM(total_cogs_vnd))/SUM(net_revenue_vnd)','Biên lợi nhuận gộp (%)','Q3,Q6'),
('hrc_share_of_cogs','SUM(hrc_cost_vnd)/SUM(total_cogs_vnd)','Tỷ trọng HRC trong COGS (%)','Q3,Q6'),
('cogs_to_revenue','SUM(total_cogs_vnd)/SUM(net_revenue_vnd)','Tỷ lệ giá vốn/doanh thu (%)','Q3,Q6'),
('yoy_growth','(period_t - period_t_minus_1y)/period_t_minus_1y','Tăng trưởng cùng kỳ (%)','Q1,Q2,Q4'),
('achievement_rate','SUM(quantity_ton)/dim_target.target_volume_ton','Tỷ lệ hoàn thành kế hoạch (%)','Q5'),
('product_mix','SUM(net_revenue_vnd) per group / total revenue','Cơ cấu nhóm sản phẩm (%)','Q4'),
('channel_mix','SUM(net_revenue_vnd) per channel / total revenue','Cơ cấu kênh (%)','Q2'),
('hrc_whatif_margin_impact','hrc_share_of_cogs * cogs_to_revenue * delta_hrc_pct','Tác động margin khi HRC thay đổi','Q6');

INSERT INTO _meta_glossary (term_vi, term_en, definition) VALUES
('HRC','Hot Rolled Coil','Thép cuộn cán nóng - nguyên liệu chính (~65-72% COGS), tính giá USD.'),
('ASP','Average Selling Price','Giá bán bình quân = doanh thu / sản lượng (VND/tấn).'),
('COGS','Cost of Goods Sold','Giá vốn hàng bán = HRC + vật liệu khác + chi phí gia công.'),
('Gross margin','Gross margin','Biên lợi nhuận gộp = (Doanh thu - COGS)/Doanh thu. Ngành tôn mạ ~9-12%.'),
('Net revenue','Net revenue','Doanh thu thuần đã trừ chiết khấu. Dùng cột net_revenue_vnd.'),
('Tôn lạnh','Aluzinc/AZ steel','Tôn mạ hợp kim nhôm-kẽm, chống ăn mòn tốt, ASP trung-cao.'),
('Tôn màu','Pre-painted steel','Tôn mạ phủ sơn màu, giá trị & biên lợi nhuận cao nhất (cao cấp hoá).'),
('Tôn kẽm','Galvanized steel','Tôn mạ kẽm phổ thông, volume lớn, margin trung bình.'),
('CRC','Cold Rolled Coil','Thép cán nguội, bán thành phẩm, ASP/margin thấp-trung.'),
('Thép hộp mạ kẽm','Galvanized steel pipe','Ống/hộp thép mạ kẽm, margin thấp, trend giảm nhẹ.'),
('Tôn mạ','Coated steel sheet','Ngành midstream: mua HRC -> cán/mạ/sơn -> bán đại lý/dự án/XK.'),
('CBPG','Anti-dumping duty','Thuế chống bán phá giá. QĐ 460/QĐ-BCT áp HRC TQ/Ấn 19,38-27,83%.'),
('Lag truyền dẫn giá','Price pass-through lag','Khi HRC tăng, giá tôn bán ra tăng chậm hơn ~1-2 tháng -> bóp margin.'),
('Cao cấp hoá','Premiumization','Dịch cơ cấu sang sản phẩm giá trị cao (tôn màu) để nâng ASP & margin.'),
('Mùa khô','Dry season','Cao điểm xây dựng (T10-12, T3-4) -> sản lượng cao.'),
('Mùa mưa','Wet season','Thấp điểm xây dựng (T5-9) -> sản lượng giảm.'),
('GDA','Ton Dong A Corp','Mã CK Công ty CP Tôn Đông Á (UPCoM). Top 3 tôn mạ VN.');
