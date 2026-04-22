-- 02_metadata.sql — Metadata tables
USE `dtg_distribution_demo`;

-- _meta_tables: 19 rows
INSERT INTO `_meta_tables` (`table_name`,`description_vi`,`description_en`,`business_context`,`row_count_approx`) VALUES
('dim_branch','7 chi nhánh DTG + monthly_opex + staff count + năm thành lập','Branch/depot master','Dùng Scenario 5 phân tích footprint',7),
('dim_calendar','Bảng lịch 730 ngày, chứa year/quarter/month/week/day_of_week, cờ is_tet_period cho mùa Tết, is_weekend, lunar_date','Calendar dimension','Dùng để join mọi fact theo date, hỗ trợ filter theo mùa và Tết',731),
('dim_channel','4 kênh: MT/HORECA/GT/Online','Channel dimension','Mix kênh khác FMCG thường (HORECA cao)',4),
('dim_currency','Tiền tệ: VND, KRW, EUR','Currency dimension','Master ngoại tệ',3),
('dim_principal','6 nhà cung cấp: Binggrae (kem, KRW), CJ Food (há cảo, KRW), Ammerland (sữa, EUR), DongWon (há cảo premium, KRW), Tashun (hải sản, VND), M.Ngon (nhãn riêng, VND)','Principal suppliers','Có imported_content_pct và source_currency để tính FX impact',6),
('dim_product','~111 SKUs với giá base, COGS base, shelf life','Product master','Quan trọng: cogs_baseline dùng làm tham chiếu tính FX impact',111),
('dim_product_category','Danh mục sản phẩm (Kem, Sữa, Bơ, Há cảo...)','Product categories','Hỗ trợ rollup doanh thu theo danh mục',16),
('dim_province','63 tỉnh thành + dân số + GDP + POS potential','Province dimension','pos_potential_count dùng để tính market coverage',63),
('dim_region','6 miền kinh tế Việt Nam','Region dimension','Rollup từ tỉnh',6),
('dim_store','~5000 điểm bán. Cột competitor_present flag Nutifood-KIDO','Store/POS master','Quan trọng cho Scenario 4 (Binggrae miền Bắc)',5000),
('dim_warehouse','21 kho: Frozen/Chilled/Ambient × 7 branches','Warehouse','Phân kho lạnh theo branch',21),
('fact_budget','Kế hoạch theo tháng × dimension × metric','Budget targets','Scenario 1 — so sánh actual vs plan',2500),
('fact_fx_rate','Tỷ giá EUR/KRW/VND theo ngày','FX rate daily','Scenario 2 — EUR spike T8-T9/2025',2193),
('fact_inventory','Tồn kho weekly snapshot với manufactured_date + expiry_date','Inventory snapshot','Scenario 6 — near-expiry alert',150000),
('fact_operating_cost','Chi phí vận hành theo tháng × chi nhánh × loại','OpEx monthly','Scenario 2 (fuel spike T9), Scenario 5 (branch CM)',1008),
('fact_route_coverage','Map branch → store với distance và cost per visit, is_primary flag','Route coverage','Scenario 5 — phát hiện overlap HN-HP',5000),
('fact_sales','Sell-in transaction level — 1 dòng = 1 line item. Có fx_rate_used denormalized','Sales sell-in','KPI gốc: net_amount_vnd, cogs_total_vnd. Scenario 1,2,3,5,7',450000),
('fact_sales_out','Sell-out POS scan theo tuần. Chênh với sell-in cho biết tồn dealer','Sell-out POS','Scenario 4 — gap sell-in/sell-out tại Binggrae miền Bắc',350000),
('fact_trade_promotion','Trade promo campaigns với planned và actual amount','Trade promo','Scenario 2 — BOGO Binggrae overspend T9/2025',500);

-- _meta_columns: 25 rows
INSERT INTO `_meta_columns` (`table_name`,`column_name`,`data_type`,`description_vi`,`unit`,`example_values`) VALUES
('dim_branch','monthly_opex_vnd','DECIMAL','Chi phí vận hành tháng','VND','170M-1.1B'),
('dim_principal','imported_content_pct','DECIMAL','Tỷ lệ nguyên liệu nhập khẩu','%','100 (Ammerland), 5 (M.Ngon)'),
('dim_principal','source_currency','CHAR(3)','Đồng tiền gốc COGS','—','EUR, KRW, VND'),
('dim_product','cogs_baseline','DECIMAL','Giá vốn base tại FX baseline','VND','—'),
('dim_product','retail_price_base','DECIMAL','Giá bán lẻ base MT','VND','—'),
('dim_product','shelf_life_days','INT','Hạn sử dụng','days','45, 180, 365'),
('dim_store','competitor_present','TINYINT(1)','1 nếu có Merino/Celano (Nutifood-KIDO) cùng tủ đông','0/1','0, 1'),
('dim_store','store_tier','CHAR(1)','Phân tầng store A/B/C theo volume','—','A, B, C'),
('fact_budget','dimension','VARCHAR','Chiều kế hoạch','—','total/principal/region/branch/channel'),
('fact_budget','metric','VARCHAR','Đại lượng kế hoạch','—','revenue/gross_profit/margin_pct/units'),
('fact_inventory','days_to_expire','INT','Số ngày đến hạn (snapshot - expiry)','days','18, 25, 90'),
('fact_operating_cost','cost_category','VARCHAR','Phân loại chi phí','—','rent/staff/fuel_logistics/utility/marketing/admin'),
('fact_route_coverage','is_primary','TINYINT(1)','1 nếu là route chính của branch → store','0/1','0, 1'),
('fact_sales','cogs_total_vnd','DECIMAL','Giá vốn tổng = qty × cogs_unit','VND','—'),
('fact_sales','cogs_unit_vnd','DECIMAL','Giá vốn/đơn vị đã áp FX tại ngày','VND','—'),
('fact_sales','date','DATE','Ngày giao dịch sell-in','date','2025-09-15'),
('fact_sales','discount_vnd','DECIMAL','Chiết khấu','VND','-'),
('fact_sales','fx_rate_used','DECIMAL','FX rate đã dùng (1 cho VND)','—','25800, 18.5, 1.0'),
('fact_sales','gross_amount_vnd','DECIMAL','Doanh thu gross = qty × unit_price','VND','-'),
('fact_sales','net_amount_vnd','DECIMAL','Doanh thu thuần = gross - discount','VND','KPI gốc'),
('fact_sales','quantity','INT','Số lượng đơn vị (cây kem, túi, hộp)','units','30, 80, 120'),
('fact_sales','sales_id','BIGINT','Primary key tự tăng','—','1,2,3…'),
('fact_sales','unit_price_vnd','DECIMAL','Đơn giá tại thời điểm, có điều chỉnh theo channel','VND','13000, 45000'),
('fact_trade_promotion','actual_amount_vnd','DECIMAL','Thực chi promo','VND','1.2B'),
('fact_trade_promotion','planned_amount_vnd','DECIMAL','Ngân sách promo đã duyệt','VND','690M');

-- _meta_kpi: 9 rows
INSERT INTO `_meta_kpi` (`kpi_name_vi`,`kpi_name_en`,`formula_sql`,`description_vi`,`related_questions`) VALUES
('Biên lợi nhuận gộp','Gross Margin %','(SUM(net_amount_vnd - cogs_total_vnd) / SUM(net_amount_vnd)) * 100','Biên LN gộp, đơn vị %','1,2,3,5,7'),
('Branch Contribution Margin','Branch CM %','(SUM(GP_from_sales) - SUM(amount_vnd from fact_operating_cost)) / SUM(net_amount_vnd) * 100','CM chi nhánh %','5,7'),
('Budget Variance','Budget Variance','actual - target (từ fact_budget)','Chênh thực tế vs kế hoạch','1,2,7'),
('Days of Inventory','DOH','SUM(total_value_vnd) / avg_daily_cogs','Số ngày tồn kho','6,7'),
('Doanh thu thuần','Net Revenue','SUM(net_amount_vnd)','Tổng doanh thu đã trừ chiết khấu','1,2,5,7'),
('FX Impact','FX Impact VND','SUM(cogs_total_vnd) - SUM(quantity * cogs_baseline)','Chênh COGS do FX','2,3,7'),
('Lợi nhuận gộp','Gross Profit','SUM(net_amount_vnd - cogs_total_vnd)','Lợi nhuận gộp VND','1,2,3,5,7'),
('Near-Expiry Value','Near-Expiry Value','SUM(total_value_vnd WHERE days_to_expire < 30)','Giá trị tồn gần date','6,7'),
('Sell-through Rate','Sell-through %','(fact_sales_out.quantity_sold / fact_sales.quantity) * 100','Tỷ lệ sell-out trên sell-in','4,6');

-- _meta_glossary: 23 rows
INSERT INTO `_meta_glossary` (`term_vi`,`term_en`,`definition`,`related_tables`) VALUES
('Biên LN gộp','Gross Margin','(Doanh thu - COGS) / Doanh thu','fact_sales'),
('BOGO','Buy One Get One','Mua 1 tặng 1 — promo type','fact_trade_promotion'),
('Cannibalization','Cannibalization','Cạnh tranh giành share giữa sản phẩm cùng kênh','dim_store.competitor_present'),
('CM','Contribution Margin','Biên đóng góp = GP - OpEx của branch','fact_sales,fact_operating_cost'),
('COGS','Cost of Goods Sold','Giá vốn hàng bán','fact_sales,dim_product'),
('Cold-chain','Cold Chain','Chuỗi cung ứng lạnh -18°C cho kem/đông lạnh','dim_warehouse,fact_operating_cost'),
('DC','Distribution Center','Kho phân phối của branch','dim_warehouse'),
('DOH','Days of Inventory','Số ngày tồn kho = total_value / daily_cogs','fact_inventory'),
('FX','Foreign Exchange','Tỷ giá ngoại tệ','fact_fx_rate'),
('GT','General Trade','Chợ đầu mối, tạp hóa truyền thống có tủ đông','dim_channel,dim_store'),
('HORECA','HORECA','Hotel/Restaurant/Catering — khách sạn, nhà hàng, bếp CN','dim_channel,dim_store'),
('MOQ','Minimum Order Quantity','Đơn đặt hàng tối thiểu với principal','—'),
('MT','Modern Trade','Kênh siêu thị, CVS chuỗi (7-Eleven, Circle K, Co.op Mart…)','dim_channel,dim_store'),
('Pareto 80/20','80/20 Rule','20% SKUs đóng góp ~80% doanh thu','dim_product,fact_sales'),
('POS','Point of Sale','Điểm bán — cửa hàng/quầy bán cuối cùng đến người tiêu dùng','dim_store'),
('Principal','Principal/Supplier','Nhà cung cấp độc quyền — DTG phân phối độc quyền tại VN','dim_principal'),
('Sell-in','Sell-in','Hàng DTG bán ra cho dealer/POS — fact_sales','fact_sales'),
('Sell-out','Sell-out','Hàng POS bán cho người tiêu dùng — fact_sales_out','fact_sales_out'),
('Shelf life','Shelf life','Hạn sử dụng','dim_product'),
('Tết','Lunar New Year','Tết Nguyên đán — peak tiêu dùng mạnh nhất năm','dim_calendar'),
('Tier','Store Tier','Phân tầng store A/B/C theo volume','dim_store'),
('TPN','Trade Promotion','Chi phí khuyến mãi kênh (BOGO, price down, display fee)','fact_trade_promotion'),
('YoY','Year-over-Year','Tăng trưởng so với cùng kỳ năm trước','fact_sales');

