-- =============================================================================
-- Phú Mỹ Hưng Development — Metadata Tables
-- Populates: _meta_tables, _meta_columns, _meta_kpi, _meta_glossary
-- =============================================================================

USE phu_my_hung_demo;

-- =============================================================================
-- _meta_tables — Mô tả bảng
-- =============================================================================
INSERT INTO _meta_tables (table_name, description_vi, description_en, business_context, grain) VALUES
('projects', 'Danh mục 6 dự án phát triển chính của Phú Mỹ Hưng', 'Master list of 6 PMH development projects', 'Truy vấn khi cần thông tin dự án: tên, vị trí, phân khúc, trạng thái, quy mô', '1 dòng = 1 dự án'),
('project_phases', 'Các giai đoạn thi công trong từng dự án', 'Sub-phases within each project', 'Truy vấn khi cần chi tiết tiến độ theo giai đoạn, đặc biệt Hồng Hạc City', '1 dòng = 1 giai đoạn'),
('contractors', 'Danh mục 12 nhà thầu thi công — lớn, trung bình, chuyên biệt', '12 construction contractors — large, mid-size, specialized', 'Truy vấn khi phân tích hiệu suất nhà thầu, chi phí, tiến độ', '1 dòng = 1 nhà thầu'),
('unit_types', 'Phân loại sản phẩm BĐS: căn hộ, biệt thự, shophouse, văn phòng', 'Property product types: apartment, villa, shop, office', 'Truy vấn khi phân tích giá bán, diện tích theo loại sản phẩm', '1 dòng = 1 loại sản phẩm'),
('cost_categories', 'Phân loại 8 hạng mục chi phí xây dựng', '8 construction cost categories', 'Truy vấn khi phân tích chi phí xây dựng theo hạng mục', '1 dòng = 1 hạng mục'),
('management_zones', '8 khu vực quản lý trong khu đô thị PMH tại Quận 7', '8 property management zones in PMH township, District 7', 'Truy vấn khi phân tích chi phí/doanh thu quản lý theo khu, đặc biệt Cảnh Đồi', '1 dòng = 1 khu vực'),
('commercial_tenants', 'Khách thuê mặt bằng thương mại tại Crescent Mall và khu CBD', 'Commercial tenants in Crescent Mall and CBD area', 'Truy vấn khi phân tích doanh thu cho thuê, tỷ lệ lấp đầy', '1 dòng = 1 khách thuê'),
('project_financials', 'Báo cáo tài chính hàng tháng theo dự án — doanh thu, chi phí, lợi nhuận', 'Monthly project P&L — revenue, cost, gross profit', 'BẢNG CHÍNH cho Q1: phân tích hiệu suất tài chính portfolio. Join với projects để lấy tên/phân khúc', '1 dòng = 1 dự án × 1 tháng'),
('project_budgets', 'Ngân sách dự toán theo dự án × hạng mục — baseline so sánh', 'Baseline budget by project × cost category', 'Truy vấn khi so sánh thực tế vs ngân sách (Q2: cost overrun)', '1 dòng = 1 dự án × 1 hạng mục'),
('unit_sales', 'Giao dịch bán từng căn — giá, diện tích, ngày bán', 'Individual unit sale records', 'Truy vấn khi phân tích sell-through, doanh thu bán hàng, ASP', '1 dòng = 1 căn hộ/lô đã bán'),
('payment_schedules', 'Lịch thanh toán theo đợt cho từng căn đã bán', 'Installment payment plan per sold unit', 'Truy vấn khi dự báo dòng tiền từ khách mua (Q4)', '1 dòng = 1 đợt thanh toán'),
('payment_collections', 'Thực thu từng khoản — ngày thu, số tiền, phương thức', 'Actual payments received from buyers', 'Truy vấn khi phân tích collection rate, dòng tiền vào (Q4)', '1 dòng = 1 khoản thu'),
('revenue_recognition', 'Ghi nhận doanh thu theo tiến độ thi công hàng tháng', 'Monthly revenue recognition by construction progress', 'Truy vấn khi phân tích chênh lệch sell-through vs recognized (Q1: L''Arcade gap)', '1 dòng = 1 dự án × 1 tháng'),
('construction_costs', 'Chi phí xây dựng chi tiết — dự án × nhà thầu × hạng mục × tháng', 'Detailed construction costs line items', 'BẢNG CHÍNH cho Q2: phân tích cost overrun. Join với project_budgets để so sánh', '1 dòng = 1 mục chi phí'),
('contractor_invoices', 'Hóa đơn từng nhà thầu — giá trị, trạng thái', 'Individual contractor invoices', 'Truy vấn khi phân tích chi phí nhà thầu, phát sinh (Q2)', '1 dòng = 1 hóa đơn'),
('contract_milestones', 'Mốc tiến độ nhà thầu — kế hoạch vs thực tế', 'Contractor milestones — planned vs actual dates', 'BẢNG CHÍNH cho Q3: tính OTD rate theo nhà thầu', '1 dòng = 1 mốc tiến độ'),
('project_assignments', 'Phân công nhà thầu theo dự án — vai trò, phạm vi, giá trị HĐ', 'Contractor-project assignments', 'Truy vấn khi xem nhà thầu nào đang làm dự án nào (Q3: Delta on Hồng Hạc)', '1 dòng = 1 phân công'),
('change_orders', 'Phát sinh thay đổi thiết kế — chi phí ảnh hưởng', 'Design/scope change orders with cost impact', 'Truy vấn khi phân tích nguyên nhân vượt ngân sách (Q2)', '1 dòng = 1 lệnh thay đổi'),
('material_prices', 'Chỉ số giá vật tư xây dựng hàng tháng — 6 loại vật tư', 'Monthly material price index — 6 material types', 'Truy vấn khi phân tích tác động giá vật tư lên chi phí (Q2: steel spike)', '1 dòng = 1 vật tư × 1 tháng'),
('debt_schedule', 'Danh mục nợ — trái phiếu USD, vay ngân hàng VND', 'Debt instruments — USD bonds, VND bank loans', 'BẢNG CHÍNH cho Q5: phân tích rủi ro đáo hạn nợ', '1 dòng = 1 khoản nợ'),
('debt_payments', 'Chi tiết thanh toán nợ — lãi + gốc hàng tháng', 'Debt payment details — interest + principal', 'Truy vấn khi dự báo dòng tiền ra cho trả nợ (Q4, Q5)', '1 dòng = 1 khoản thanh toán'),
('unsold_inventory', 'Hàng tồn kho chưa bán — 14 shop Scenic Valley 2', 'Unsold units — primarily 14 shops in Scenic Valley 2', 'Truy vấn khi phân tích rủi ro tồn kho, tuổi tồn kho (Q5)', '1 dòng = 1 căn chưa bán'),
('project_permits', 'Theo dõi giấy phép dự án — xây dựng, mở bán, PCCC', 'Project permit tracking', 'Truy vấn khi đánh giá rủi ro giấy phép (Q5: Hồng Hạc pre-sale pending)', '1 dòng = 1 giấy phép'),
('construction_payment_schedule', 'Kế hoạch giải ngân xây dựng — dự báo dòng tiền ra', 'Planned construction payment outflows', 'BẢNG CHÍNH cho Q4: dự báo dòng tiền ra. Hồng Hạc front-loading tháng 13-16', '1 dòng = 1 dự án × 1 tháng × 1 hạng mục'),
('management_costs', 'Chi phí quản lý BĐS hàng tháng — 8 khu × 8 hạng mục', 'Monthly property management costs by zone and category', 'BẢNG CHÍNH cho Q6: phân tích chi phí quản lý. Cảnh Đồi có chi phí tăng nhanh', '1 dòng = 1 khu × 1 hạng mục × 1 tháng'),
('management_revenue', 'Doanh thu phí quản lý BĐS hàng tháng theo khu', 'Monthly PM fee revenue by zone', 'Truy vấn khi so sánh doanh thu vs chi phí quản lý (Q6)', '1 dòng = 1 khu × 1 tháng'),
('maintenance_tickets', 'Phiếu yêu cầu bảo trì — sự cố, chi phí, thời gian xử lý', 'Maintenance work orders', 'Truy vấn khi phân tích xu hướng bảo trì, dự báo capex (Q6: elevator trend)', '1 dòng = 1 phiếu'),
('lease_income', 'Doanh thu cho thuê mặt bằng thương mại hàng tháng', 'Monthly commercial lease income', 'Truy vấn khi phân tích doanh thu cho thuê, tỷ lệ lấp đầy', '1 dòng = 1 khách thuê × 1 tháng'),
('management_fees_monthly', 'Tổng hợp phí quản lý cho phân tích dòng tiền', 'Aggregated monthly management fees for cash flow', 'Truy vấn khi cần tổng dòng tiền từ quản lý BĐS', '1 dòng = 1 tháng');

-- =============================================================================
-- _meta_kpi — Công thức KPI
-- =============================================================================
INSERT INTO _meta_kpi (kpi_name, kpi_name_vi, formula_sql, description_vi, description_en, related_tables, related_questions) VALUES
('Gross Margin %', 'Biên lợi nhuận gộp', '(SUM(pf.revenue_vnd) - SUM(pf.cost_vnd)) / NULLIF(SUM(pf.revenue_vnd), 0) * 100 FROM project_financials pf', 'Tỷ lệ lợi nhuận gộp trên doanh thu, tính theo dự án hoặc toàn portfolio', 'Gross margin by project or portfolio', 'project_financials, projects', 'Q1: Portfolio performance'),
('Sell-through Rate', 'Tỷ lệ bán hàng', 'COUNT(CASE WHEN us.status IN (''contracted'',''paying'',''handed_over'') THEN 1 END) / p.total_units * 100 FROM unit_sales us JOIN projects p ON us.project_id = p.project_id', 'Tỷ lệ % căn đã bán trên tổng căn, theo dự án', 'Percentage of units sold per project', 'unit_sales, projects', 'Q1, Q4: Sales velocity'),
('Revenue Recognition Rate', 'Tỷ lệ ghi nhận doanh thu', 'SUM(rr.recognized_revenue_vnd) / NULLIF(SUM(rr.total_contract_value_vnd), 0) * 100 FROM revenue_recognition rr', 'Tỷ lệ doanh thu đã ghi nhận / tổng giá trị HĐ — phát hiện gap L''Arcade', 'Recognized revenue vs total contract value', 'revenue_recognition', 'Q1: L''Arcade recognition gap'),
('Contractor OTD Rate', 'Tỷ lệ giao hàng đúng hạn', 'SUM(CASE WHEN cm.actual_date <= cm.planned_date THEN 1 ELSE 0 END) / COUNT(*) * 100 FROM contract_milestones cm', 'Tỷ lệ mốc hoàn thành đúng hoặc trước hạn', 'Percentage of milestones completed on or before planned date', 'contract_milestones, contractors', 'Q3: Contractor performance'),
('Cost Variance %', 'Độ lệch chi phí', '(SUM(cc.actual_cost_vnd) - SUM(cc.budgeted_cost_vnd)) / NULLIF(SUM(cc.budgeted_cost_vnd), 0) * 100 FROM construction_costs cc', 'Chênh lệch thực tế vs ngân sách, dương = vượt', 'Actual vs budgeted cost, positive = overrun', 'construction_costs, project_budgets', 'Q2: Cost overrun, Q3: Contractor cost variance'),
('Collection Rate', 'Tỷ lệ thu tiền', 'SUM(pc.amount_vnd) / NULLIF(SUM(ps.amount_vnd), 0) * 100 FROM payment_collections pc JOIN payment_schedules ps ON pc.schedule_id = ps.schedule_id', 'Tỷ lệ thu tiền thực tế / kế hoạch — phản ánh dòng tiền vào', 'Collected vs scheduled amount', 'payment_collections, payment_schedules', 'Q4: Cash flow projection'),
('Management Cost per Unit', 'Chi phí quản lý/căn', 'SUM(mc.cost_vnd) / mz.total_units FROM management_costs mc JOIN management_zones mz ON mc.zone_id = mz.zone_id', 'Chi phí quản lý trung bình mỗi căn mỗi tháng', 'Average monthly PM cost per managed unit', 'management_costs, management_zones', 'Q6: PM cost analysis'),
('Inventory Aging Days', 'Tuổi tồn kho', 'DATEDIFF(CURDATE(), ui.listing_date) FROM unsold_inventory ui', 'Số ngày kể từ khi đăng bán mà chưa có giao dịch', 'Days since listing without sale', 'unsold_inventory', 'Q5: Inventory risk'),
('Debt-to-Equity Ratio', 'Tỷ lệ nợ/vốn chủ sở hữu', 'SUM(ds.principal_amount_vnd) / 18500000000000 FROM debt_schedule ds WHERE ds.status = ''active''', 'Tổng nợ / Vốn chủ sở hữu (equity ước tính 18,500 tỷ)', 'Total active debt / Equity (est. 18,500B VND)', 'debt_schedule', 'Q5: Financial risk'),
('Cash Runway Months', 'Số tháng dòng tiền', '(Tổng tiền mặt hiện có) / (Tổng chi phí trung bình hàng tháng) — cần tính từ nhiều bảng', 'Ước tính số tháng hoạt động với dòng tiền hiện tại', 'Estimated months of operation with current cash flow', 'payment_collections, construction_payment_schedule, debt_payments', 'Q4, Q5: Liquidity risk'),
('Net Cash Flow', 'Dòng tiền ròng', 'SUM(inflows) - SUM(outflows) — cần join nhiều bảng: payment_collections + lease_income + management_revenue - construction_payment_schedule - debt_payments - management_costs', 'Dòng tiền ròng hàng tháng = tổng thu - tổng chi', 'Monthly net cash flow from all sources', 'payment_collections, lease_income, management_revenue, construction_payment_schedule, debt_payments, management_costs', 'Q4: Cash flow projection'),
('Average Selling Price', 'Giá bán trung bình', 'SUM(us.total_price_vnd) / NULLIF(SUM(us.area_sqm), 0) FROM unit_sales us', 'Giá bán trung bình trên mỗi m² theo dự án hoặc loại sản phẩm', 'Average selling price per sqm', 'unit_sales', 'Q1: Revenue analysis');

-- =============================================================================
-- _meta_glossary — Từ điển thuật ngữ
-- =============================================================================
INSERT INTO _meta_glossary (term_vi, term_en, definition) VALUES
('Doanh thu thuần', 'Net Revenue', 'Doanh thu sau khi trừ chiết khấu, giảm giá, hoàn trả'),
('Biên lợi nhuận gộp', 'Gross Margin', '(Doanh thu - Giá vốn) / Doanh thu × 100%. Phản ánh hiệu quả kinh doanh cốt lõi'),
('Tỷ lệ bán hàng', 'Sell-through Rate', 'Số căn đã bán / Tổng số căn × 100%. Đo lường tốc độ tiêu thụ'),
('Ghi nhận doanh thu', 'Revenue Recognition', 'Doanh thu được ghi sổ kế toán dựa trên tiến độ xây dựng và bàn giao — theo chuẩn mực VAS/IFRS'),
('Tỷ lệ giao hàng đúng hạn', 'On-time Delivery (OTD)', 'Mốc tiến độ nhà thầu hoàn thành đúng hoặc trước ngày kế hoạch — đo hiệu suất nhà thầu'),
('Độ lệch chi phí', 'Cost Variance', 'Chi phí thực tế vs ngân sách, tính theo %: (Thực tế - Ngân sách) / Ngân sách × 100%'),
('Tỷ lệ thu tiền', 'Collection Rate', 'Số tiền thực thu / Số tiền phải thu theo lịch × 100% — phản ánh chất lượng dòng tiền'),
('Hàng tồn kho chưa bán', 'Unsold Inventory', 'Sản phẩm BĐS đã hoàn thiện hoặc đang bán nhưng chưa có hợp đồng mua bán'),
('Tuổi tồn kho', 'Inventory Aging', 'Số ngày kể từ ngày đăng bán — tồn kho >12 tháng cần lưu ý'),
('Tỷ lệ nợ/vốn chủ sở hữu', 'Debt-to-Equity Ratio', 'Tổng nợ phải trả / Vốn chủ sở hữu — đo mức độ đòn bẩy tài chính'),
('Giá bán trung bình', 'Average Selling Price (ASP)', 'Tổng giá trị bán / Tổng diện tích bán — tính theo VND/m²'),
('Chi phí quản lý/căn hộ', 'Management Cost per Unit', 'Tổng chi phí quản lý BĐS / Số căn quản lý — tính hàng tháng'),
('Dòng tiền ròng', 'Net Cash Flow', 'Tổng tiền thu vào - Tổng tiền chi ra trong kỳ'),
('Trái phiếu quốc tế', 'International Bond', 'Trái phiếu phát hành bằng ngoại tệ (USD) trên thị trường quốc tế'),
('Lệnh thay đổi thiết kế', 'Change Order', 'Yêu cầu thay đổi thiết kế/phạm vi thi công — thường làm tăng chi phí'),
('Phí quản lý', 'Management Fee', 'Phí dịch vụ quản lý BĐS thu hàng tháng từ cư dân/chủ sở hữu'),
('Khu đô thị', 'Township', 'Khu phát triển đô thị tích hợp: nhà ở, thương mại, hạ tầng, dịch vụ'),
('Bàn giao', 'Handover', 'Chuyển giao căn hộ/sản phẩm cho khách mua sau khi hoàn thiện xây dựng'),
('Đặt cọc', 'Deposit', 'Khoản thanh toán đầu tiên khi ký hợp đồng mua bán — thường 10-30% giá trị'),
('Chi phí giữ hàng', 'Carrying Cost', 'Chi phí duy trì hàng tồn kho chưa bán: thuế đất, bảo trì, phí chung'),
('Giấy phép mở bán', 'Pre-sale Permit', 'Giấy phép cho phép chủ đầu tư mở bán sản phẩm hình thành trong tương lai — bắt buộc theo Luật KDBĐS');

-- =============================================================================
-- _meta_columns — Mô tả cột (key columns for AI engine)
-- =============================================================================
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
-- projects
('projects', 'project_id', 'VARCHAR(20)', 'Mã dự án', 'Project ID', NULL, 'PRJ-001, PRJ-002'),
('projects', 'name', 'VARCHAR(200)', 'Tên dự án tiếng Anh', 'English project name', NULL, 'Phu My Hung The Aurora, Cardinal Court'),
('projects', 'segment', 'ENUM', 'Phân khúc: ultra_luxury, luxury, premium, mid_high, commercial', 'Market segment', NULL, 'premium, luxury, ultra_luxury'),
('projects', 'status', 'ENUM', 'Trạng thái: planning, infrastructure, construction, selling, delivered, completed', 'Current status', NULL, 'selling, delivered, construction'),
('projects', 'total_units', 'INT', 'Tổng số sản phẩm trong dự án', 'Total units in project', 'căn/lô', '95, 37, 200, 476, 300, 45'),
-- project_financials
('project_financials', 'revenue_vnd', 'BIGINT', 'Doanh thu tháng của dự án', 'Monthly project revenue', 'VND', '85000000000, 45000000000'),
('project_financials', 'cost_vnd', 'BIGINT', 'Chi phí tháng (giá vốn)', 'Monthly COGS', 'VND', '46750000000'),
('project_financials', 'month_date', 'DATE', 'Tháng báo cáo — ngày 1 của tháng', 'Report month — 1st of month', NULL, '2024-01-01, 2025-06-01'),
-- unit_sales
('unit_sales', 'total_price_vnd', 'BIGINT', 'Tổng giá trị hợp đồng mua bán', 'Total contract value', 'VND', '8500000000, 15000000000'),
('unit_sales', 'price_per_sqm', 'BIGINT', 'Đơn giá trên mỗi m²', 'Price per square meter', 'VND/m²', '95000000, 130000000'),
('unit_sales', 'status', 'ENUM', 'Trạng thái: reserved, contracted, paying, handed_over, cancelled', 'Sale status', NULL, 'contracted, handed_over'),
-- payment_collections
('payment_collections', 'amount_vnd', 'BIGINT', 'Số tiền thực thu', 'Actual amount collected', 'VND', '850000000, 2000000000'),
('payment_collections', 'payment_date', 'DATE', 'Ngày thực nhận tiền', 'Actual payment receipt date', NULL, '2024-03-15'),
-- revenue_recognition
('revenue_recognition', 'recognized_pct', 'DECIMAL(5,2)', 'Tỷ lệ doanh thu đã ghi nhận lũy kế', 'Cumulative recognized revenue %', '%', '62.00, 85.50'),
('revenue_recognition', 'sell_through_pct', 'DECIMAL(5,2)', 'Tỷ lệ đã bán', 'Sell-through percentage', '%', '100.00, 72.00'),
-- construction_costs
('construction_costs', 'category', 'VARCHAR(50)', 'Hạng mục: foundation, structure, mep, finishing, facade, landscaping, infrastructure, contingency', 'Cost category', NULL, 'structure, mep, foundation'),
('construction_costs', 'actual_cost_vnd', 'BIGINT', 'Chi phí thực tế phát sinh', 'Actual cost incurred', 'VND', '5000000000'),
('construction_costs', 'budgeted_cost_vnd', 'BIGINT', 'Chi phí dự toán', 'Budgeted cost', 'VND', '4500000000'),
-- contract_milestones
('contract_milestones', 'planned_date', 'DATE', 'Ngày hoàn thành kế hoạch', 'Planned completion date', NULL, '2024-06-30'),
('contract_milestones', 'actual_date', 'DATE', 'Ngày hoàn thành thực tế — NULL nếu chưa xong', 'Actual completion date — NULL if pending', NULL, '2024-07-15'),
-- material_prices
('material_prices', 'material_type', 'VARCHAR(50)', 'Loại vật tư', 'Material type', NULL, 'steel_rebar, cement, glass_aluminum'),
('material_prices', 'price_index', 'DECIMAL(8,2)', 'Chỉ số giá — 100 = tháng gốc (01/2024)', 'Price index — 100 = base month (Jan 2024)', 'index', '100.00, 118.00, 112.00'),
-- debt_schedule
('debt_schedule', 'principal_amount', 'BIGINT', 'Giá trị gốc theo đồng tiền phát hành', 'Principal in original currency', 'VND hoặc USD', '100000000 (USD), 2000000000000 (VND)'),
('debt_schedule', 'maturity_date', 'DATE', 'Ngày đáo hạn', 'Maturity date', NULL, '2025-04-01, 2025-08-01'),
-- unsold_inventory
('unsold_inventory', 'listing_date', 'DATE', 'Ngày đăng bán', 'Date unit listed for sale', NULL, '2024-01-15'),
('unsold_inventory', 'monthly_carrying_cost_vnd', 'BIGINT', 'Chi phí giữ hàng hàng tháng: thuế đất + bảo trì', 'Monthly carrying cost: land tax + maintenance', 'VND', '41800000'),
-- management_costs
('management_costs', 'cost_category', 'VARCHAR(50)', 'Hạng mục: staff, security, elevator_maintenance, waterproofing_repairs, landscaping, utilities, cleaning, other', 'Cost category', NULL, 'elevator_maintenance, staff'),
('management_costs', 'cost_vnd', 'BIGINT', 'Chi phí hàng tháng', 'Monthly cost', 'VND', '180000000, 320000000'),
-- maintenance_tickets
('maintenance_tickets', 'category', 'VARCHAR(50)', 'Loại: elevator, waterproofing, electrical, plumbing, hvac, general, landscaping', 'Ticket category', NULL, 'elevator, waterproofing'),
('maintenance_tickets', 'cost_vnd', 'BIGINT', 'Chi phí xử lý sự cố', 'Repair/resolution cost', 'VND', '22000000, 35000000'),
-- management_zones
('management_zones', 'total_units', 'INT', 'Tổng số căn/đơn vị quản lý trong khu', 'Total managed units in zone', 'căn', '1200, 2800'),
('management_zones', 'year_established', 'INT', 'Năm hình thành — khu cũ hơn = hạ tầng cũ hơn', 'Year established — older = aging infrastructure', NULL, '1997, 2017'),
-- debt_payments
('debt_payments', 'payment_amount_vnd', 'BIGINT', 'Tổng thanh toán = lãi + gốc', 'Total payment = interest + principal', 'VND', '12000000000'),
-- lease_income
('lease_income', 'monthly_rent_vnd', 'BIGINT', 'Tiền thuê phải thu', 'Rent due', 'VND', '150000000'),
('lease_income', 'collected_vnd', 'BIGINT', 'Tiền thuê thực thu', 'Rent collected', 'VND', '150000000');
