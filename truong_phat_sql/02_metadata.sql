-- ============================================================
-- 02_*.sql  |  wood_export_demo  |  Gỗ Trường Phát (demo)
-- Database: wood_export_demo
-- METADATA — INSERT _meta_tables / _meta_columns / _meta_kpi / _meta_glossary.
-- Encode: UTF-8 (utf8mb4). Chạy theo thứ tự 01→05.
-- ============================================================

/*!40101 SET NAMES utf8mb4 */;
SET NAMES utf8mb4;

USE `wood_export_demo`;

INSERT INTO `_meta_tables` (`table_name`, `description_vi`, `description_en`, `business_context`) VALUES
('dim_calendar','Bảng lịch ngày, phủ kín 2024-06-01..2026-05-31. Dùng cho mọi phân tích theo thời gian, YoY, seasonality.','Date dimension covering 2024-06-01..2026-05-31. Used for all time-based analysis, YoY, seasonality.','Join với fact_sales.order_date. is_tet_season giải thích dip sản xuất đầu năm.'),
('dim_market','Thị trường tiêu thụ (6 thị trường).','Sales markets (6 markets).','Mỹ ~48% tổng DT; 88% DT là xuất khẩu. \'Nội địa\' xuất hiện cả ở channel lẫn market.'),
('dim_customer','Khách hàng (nhà nhập khẩu / chuỗi bán lẻ / dự án). ~24 khách.','Customers (importer / retail chain / project). ~24 rows.','Top 3 (Westwood 22%, Coastal 15%, Nordic 11%) ≈ 48% DT → rủi ro tập trung.'),
('dim_product','Danh mục sản phẩm, hierarchy category → subcategory → SKU (~40 SKU).','Product catalog, category → subcategory → SKU hierarchy (~40 SKUs).','5 category. Chỉ \'Sofa khung gỗ\' & \'Tủ bếp\' chịu rủi ro thuế Mỹ Section 232.'),
('dim_factory','Nhà máy sản xuất (6 nhà máy tại Bình Dương + Bình Định).','Factories (6, in Bình Dương + Bình Định).','Bình Định 2 sẽ quá tải (~94%) mùa cao điểm; Bình Dương 3 dư công suất (~71%).'),
('dim_fx_monthly','Tỷ giá bình quân theo tháng. Bảng tra cứu chính cho phân tích FX margin.','Monthly average FX rates. Main lookup for FX margin analysis.','USD/VND tăng nhanh 2026-01..05 (26.050→26.400) — một phần nguyên nhân margin erosion.'),
('fact_sales','FACT CHÍNH — doanh thu bán hàng, grain = transaction line item (1 dòng = 1 line item của 1 đơn).','MAIN FACT — sales revenue at transaction line-item grain.','Luôn dùng net_revenue_vnd cho DT; biên gộp = SUM(gross_profit)/SUM(net_revenue). cogs_total đã quy đổi VND.'),
('fact_production','Sản xuất & công suất, grain = factory × month × category. SNAPSHOT theo tháng.','Production & capacity, grain = factory × month × category. Monthly snapshot.','Không SUM utilization_pct nhiều tháng. Lấy \'hiện tại\' = WHERE month>=\'2026-03-01\' rồi AVG.');

INSERT INTO `_meta_columns` (`table_name`, `column_name`, `data_type`, `description_vi`, `description_en`, `unit`, `example_values`) VALUES
('dim_calendar','date','DATE','Ngày','Calendar date','date','2025-08-15'),
('dim_calendar','year','INT','Năm','Year','year','2024;2025;2026'),
('dim_calendar','quarter','INT','Quý (1-4)','Quarter','quarter','1;2;3;4'),
('dim_calendar','month','INT','Tháng (1-12)','Month number','month','1;8;12'),
('dim_calendar','month_name_vi','VARCHAR(20)','Tên tháng tiếng Việt','Vietnamese month name','','Tháng 8'),
('dim_calendar','week','INT','Tuần ISO trong năm','ISO week of year','week','1;33;52'),
('dim_calendar','day_of_week','INT','Thứ (1=T2 .. 7=CN)','Day of week (1=Mon..7=Sun)','','1;6;7'),
('dim_calendar','day_of_month','INT','Ngày trong tháng','Day of month','','1;15;31'),
('dim_calendar','is_weekend','TINYINT','1 nếu T7/CN','1 if Sat/Sun','bool','0;1'),
('dim_calendar','is_tet_season','TINYINT','1 nếu tháng 1-2 (mùa Tết, SX chậm)','1 if Jan/Feb (Tet season)','bool','0;1'),
('dim_market','market_id','INT','ID thị trường','Market id','','1;6'),
('dim_market','market_name','VARCHAR(30)','Tên thị trường','Market name','','Mỹ;EU;Nhật Bản;Nội địa'),
('dim_market','region_type','VARCHAR(20)','Loại: Xuất khẩu / Nội địa','Export / Domestic','','Xuất khẩu;Nội địa'),
('dim_market','currency_code','VARCHAR(5)','Tiền tệ gốc đơn hàng','Order base currency','','USD;EUR;JPY;KRW;VND'),
('dim_market','default_tariff_note','VARCHAR(255)','Ghi chú thuế','Tariff note','','Section 232...'),
('dim_customer','customer_id','INT','ID khách','Customer id','','1;24'),
('dim_customer','customer_name','VARCHAR(80)','Tên khách','Customer name','','Westwood Living'),
('dim_customer','market_id','INT','Thị trường (FK dim_market)','Market (FK)','','1;2'),
('dim_customer','customer_type','VARCHAR(30)','Nhà nhập khẩu/Chuỗi bán lẻ/Dự án','Customer type','','Nhà nhập khẩu;Dự án'),
('dim_customer','country','VARCHAR(40)','Quốc gia','Country','','Mỹ;Đức;Việt Nam'),
('dim_customer','is_key_account','TINYINT','1 nếu key account','1 if key account','bool','0;1'),
('dim_customer','onboard_date','DATE','Ngày bắt đầu hợp tác','Onboard date','date','2019-03-15'),
('dim_product','product_id','INT','ID sản phẩm','Product id','','1;40'),
('dim_product','sku_code','VARCHAR(20)','Mã SKU','SKU code','','CAB-001'),
('dim_product','product_name','VARCHAR(120)','Tên sản phẩm (tiếng Việt)','Product name (VI)','','Tủ bếp trên gỗ sồi'),
('dim_product','product_category','VARCHAR(40)','Nhóm chính (5 nhóm)','Main category','','Tủ bếp;Sofa khung gỗ'),
('dim_product','product_subcategory','VARCHAR(40)','Nhóm con','Subcategory','','Tủ bếp trên;Sofa băng'),
('dim_product','wood_species','VARCHAR(20)','Loại gỗ (Sồi/Óc chó = nhập)','Wood species (Sồi/Óc chó imported)','','Sồi;Cao su;Acacia/Tràm'),
('dim_product','is_section232_affected','TINYINT','1 nếu chịu rủi ro thuế Mỹ 232','1 if Section 232 affected','bool','0;1'),
('dim_product','section232_tariff_type','ENUM(\'none\',\'sofa_30pct\',\'cabinet_50pct\')','Mức thuế dự kiến từ 1/1/2027','Planned 2027 tariff type','','none;sofa_30pct;cabinet_50pct'),
('dim_product','base_asp_vnd','DECIMAL(15,2)','Giá bán bình quân tham chiếu','Reference ASP','VND','7500000.00'),
('dim_product','popularity_weight','DECIMAL(9,6)','Trọng số Pareto (top 20% ~ 80% volume)','Pareto popularity weight','','0.547531'),
('dim_factory','factory_id','INT','ID nhà máy','Factory id','','1;6'),
('dim_factory','factory_name','VARCHAR(60)','Tên nhà máy','Factory name','','Nhà máy Bình Định 2'),
('dim_factory','location','VARCHAR(20)','Địa điểm','Location','','Bình Dương;Bình Định'),
('dim_factory','primary_category','VARCHAR(40)','Nhóm SP chính','Primary category','','Tủ bếp + phòng ngủ'),
('dim_factory','monthly_capacity_units','INT','Công suất tháng (sản phẩm)','Monthly capacity (units)','sản phẩm/tháng','5500'),
('dim_factory','opened_date','DATE','Ngày vận hành','Opened date','date','2019-11-01'),
('dim_fx_monthly','month','DATE','Đầu tháng (YYYY-MM-01)','Month start','date','2026-01-01'),
('dim_fx_monthly','usd_vnd_avg','DECIMAL(10,2)','Tỷ giá USD/VND bình quân tháng','USD/VND avg','VND/USD','26400.00'),
('dim_fx_monthly','eur_vnd_avg','DECIMAL(10,2)','Tỷ giá EUR/VND bình quân tháng','EUR/VND avg','VND/EUR','28300.00'),
('dim_fx_monthly','note','VARCHAR(255)','Ghi chú','Note','','USD/VND tăng nhanh...'),
('fact_sales','sale_id','BIGINT','ID dòng bán','Sale line id','','1;50000'),
('fact_sales','order_id','BIGINT','ID đơn hàng (gom nhiều line)','Order id','','1;20000'),
('fact_sales','order_date','DATE','Ngày đặt (FK dim_calendar)','Order date (FK)','date','2026-05-12'),
('fact_sales','customer_id','INT','Khách (FK dim_customer)','Customer (FK)','','1'),
('fact_sales','product_id','INT','Sản phẩm (FK dim_product)','Product (FK)','','31'),
('fact_sales','market_id','INT','Thị trường (FK dim_market)','Market (FK)','','1'),
('fact_sales','factory_id','INT','Nhà máy SX (FK dim_factory)','Factory (FK)','','5'),
('fact_sales','channel','VARCHAR(20)','Xuất khẩu / Nội địa','Channel','','Xuất khẩu;Nội địa'),
('fact_sales','quantity','INT','Số lượng','Quantity','sản phẩm','12'),
('fact_sales','unit_price_vnd','DECIMAL(15,2)','Đơn giá (ASP)','Unit price (ASP)','VND','7480000.00'),
('fact_sales','net_revenue_vnd','DECIMAL(18,2)','Doanh thu thuần dòng','Net revenue line','VND','89760000.00'),
('fact_sales','cogs_material_imported_vnd','DECIMAL(18,2)','Giá vốn gỗ nhập (chịu FX)','COGS imported material (FX)','VND','30000000.00'),
('fact_sales','cogs_material_domestic_vnd','DECIMAL(18,2)','Giá vốn gỗ nội địa','COGS domestic material','VND','7000000.00'),
('fact_sales','cogs_labor_vnd','DECIMAL(18,2)','Giá vốn nhân công','COGS labor','VND','18000000.00'),
('fact_sales','cogs_overhead_vnd','DECIMAL(18,2)','Chi phí SX chung','COGS overhead','VND','11000000.00'),
('fact_sales','cogs_total_vnd','DECIMAL(18,2)','Tổng giá vốn (= 4 thành phần)','Total COGS','VND','66000000.00'),
('fact_sales','gross_profit_vnd','DECIMAL(18,2)','Lợi nhuận gộp (= net_revenue - cogs_total)','Gross profit','VND','23760000.00'),
('fact_production','production_id','INT','ID dòng sản xuất','Production row id','','1;192'),
('fact_production','factory_id','INT','Nhà máy (FK dim_factory)','Factory (FK)','','5'),
('fact_production','month','DATE','Đầu tháng (YYYY-MM-01)','Month start','date','2026-05-01'),
('fact_production','product_category','VARCHAR(40)','Nhóm SP sản xuất','Produced category','','Tủ bếp'),
('fact_production','units_produced','INT','Số SP sản xuất trong tháng','Units produced','sản phẩm','3290'),
('fact_production','capacity_units','INT','Công suất khả dụng tháng (theo category)','Available capacity','sản phẩm','3500'),
('fact_production','utilization_pct','DECIMAL(6,2)','units_produced / capacity_units × 100','Utilization %','%','94.00');

INSERT INTO `_meta_kpi` (`kpi_name`, `formula_sql`, `description_vi`, `related_questions`) VALUES
('Doanh thu thuần','SUM(net_revenue_vnd)','Tổng doanh thu thuần. Drill theo market/customer/product_category/channel/time/factory.','Câu 1,3,4,5,6'),
('Biên lợi nhuận gộp (%)','SUM(gross_profit_vnd)/SUM(net_revenue_vnd)*100','Biên gộp toàn cục — KHÔNG average biên dòng lẻ.','Câu 2,5,6'),
('Tỷ trọng COGS nhập (%)','SUM(cogs_material_imported_vnd)/SUM(net_revenue_vnd)*100','Tỷ lệ giá vốn gỗ nhập (chịu FX) trên doanh thu — root cause margin erosion.','Câu 2'),
('Exposure thuế Section 232','SUM(net_revenue_vnd) WHERE is_section232_affected=1 AND market_name=\'Mỹ\'','Doanh thu nhóm SP chịu rủi ro thuế Mỹ (sofa+tủ bếp) bán sang Mỹ (~18% tổng DT).','Câu 1'),
('Tăng trưởng DT YoY (%)','(DT kỳ này - DT cùng kỳ năm trước)/DT cùng kỳ*100','Tăng trưởng so cùng kỳ (~+11%). Cần >=24 tháng dữ liệu.','Câu 4,5'),
('Mức tập trung khách hàng','Top-N SUM(net_revenue_vnd)/Tổng DT*100','Tỷ trọng doanh thu của top-N khách (top 3 ≈ 48%).','Câu 3'),
('Công suất nhà máy (%)','AVG(utilization_pct) GROUP BY factory_id WHERE month>=\'2026-03-01\'','Utilization bình quân tháng gần nhất theo nhà máy (Bình Định 2 ~94%).','Câu 6'),
('ASP bình quân','SUM(net_revenue_vnd)/SUM(quantity)','Giá bán bình quân thực tế (ASP) — dùng kiểm tra anomaly A (ASP đứng yên).','Câu 2'),
('Biên gộp theo thị trường (%)','SUM(gross_profit_vnd)/SUM(net_revenue_vnd)*100 GROUP BY market_name','So sánh biên theo thị trường (EU cao hơn Mỹ ~3 điểm).','Câu 5'),
('Tỷ trọng kênh XK/Nội địa (%)','SUM(net_revenue_vnd) GROUP BY channel / Tổng DT','Cơ cấu xuất khẩu (88%) vs nội địa (12%).','Câu 4');

INSERT INTO `_meta_glossary` (`term_vi`, `term_en`, `definition`) VALUES
('Biên gộp','Gross margin','Lợi nhuận gộp / doanh thu thuần. Tính bằng SUM(gross_profit)/SUM(net_revenue), không average dòng lẻ.'),
('Section 232','Section 232 tariff','Thuế nhập khẩu Mỹ; kế hoạch 30% sofa bọc nệm & 50% tủ bếp từ 1/1/2027 (đã hoãn từ 2026).'),
('Exposure thuế','Tariff exposure','Doanh thu rơi vào nhóm SP & thị trường chịu rủi ro tăng thuế (sofa+tủ bếp × Mỹ).'),
('ASP','Average Selling Price','Giá bán bình quân = doanh thu / số lượng.'),
('COGS nhập','Imported COGS','Giá vốn nguyên liệu gỗ nhập khẩu, chịu rủi ro tỷ giá USD/VND.'),
('Margin erosion','Margin erosion','Biên gộp bị bào mòn dù doanh thu tăng — do giá gỗ nhập + tỷ giá tăng, ASP đứng yên.'),
('Key account','Key account','Khách hàng chủ chốt đóng góp tỷ trọng doanh thu lớn.'),
('Rủi ro tập trung','Concentration risk','Phụ thuộc quá nhiều vào ít khách (top 3 ≈ 48% DT) — bài học Noble House.'),
('Utilization','Capacity utilization','Tỷ lệ công suất sử dụng = units_produced / capacity_units × 100.'),
('Seasonality','Seasonality','Tính mùa vụ: cao điểm XK tháng 8-10, thấp mùa Tết (tháng 1-2).'),
('YoY','Year over Year','So sánh cùng kỳ năm trước.'),
('Pareto 80/20','Pareto principle','Top 20% SKU tạo ~80% doanh thu/volume.'),
('EUDR','EU Deforestation Regulation','Quy định EU yêu cầu truy xuất nguồn gốc gỗ không phá rừng.'),
('Grain','Grain','Độ mịn của bảng fact. fact_sales = line-item; fact_production = factory×month×category.');

