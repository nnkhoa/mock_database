# DATA SCHEMA — ELMICH | GIA DỤNG / HOUSEWARE BI
## Database: `elmich_houseware_demo` (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 2024-09-01 → 2026-08-31 (24 tháng, 730 ngày) | "Hiện tại" = cuối tháng 8/2026

Nguồn thiết kế: `ELMICH_claude-code-instruction.md` + `ELMICH_database-schema.md` (tài liệu gốc do
người dùng cung cấp). Tài liệu này là bản sao giữ nguyên trong thư mục `elmich_sql/` để làm
nguồn truth cho DDL — mọi bảng/cột/kiểu trong `01_ddl_schema.sql` được sinh trực tiếp từ đây.

Tham khảo bản đầy đủ (sơ đồ quan hệ, SQL templates, join warnings, sanity check) trong tài liệu
gốc `ELMICH_database-schema.md` đã cung cấp cho Claude Code khi khởi tạo dự án này.

---

## DIMENSION TABLES (11)

1. `dim_calendar` (730) — `date` PK, `year`, `quarter`, `month`, `month_name_vi`, `week_of_year`,
   `day_of_week` (1=T2), `day_name_vi`, `is_weekend`, `is_holiday`, `holiday_name_vi`,
   `days_to_tet`, `tet_phase`, `is_ecom_mega_sale`, `ecom_sale_name`.
2. `dim_region` (3) — `region_id` PK, `region_name`, `revenue_share_target_pct`.
3. `dim_province` (34) — `province_id` PK, `province_name`, `region_id` FK, `population_thousand`,
   `urban_tier`, `is_key_market`.
4. `dim_channel` (4) — `channel_id` PK, `channel_code`, `channel_name_vi`, `description_vi`,
   `benchmark_contribution_margin_pct`.
5. `dim_retail_chain` (6) — `chain_id` PK, `chain_name`, `chain_type`, `store_count`,
   `revenue_share_of_mt_pct`.
6. `dim_distributor` (48) — `distributor_id` PK, `distributor_name`, `province_id` FK,
   `region_id` FK, `tier`, `credit_limit_vnd`, `payment_term_days`, `onboard_date`.
7. `dim_showroom` (42) — `showroom_id` PK, `showroom_name`, `province_id` FK, `location_type`,
   `floor_area_sqm`, `monthly_rent_vnd`, `capex_vnd`, `opening_date`, `staff_count`.
8. `dim_ecom_platform` (4) — `platform_id` PK, `platform_name`, `commission_pct`,
   `revenue_share_of_online_pct`.
9. `dim_category` (18) — `category_id` PK, `group_name_vi`, `category_name_vi`,
   `seasonality_profile`.
10. `dim_product` (420) — `product_id` PK, `sku_code`, `product_name_vi`, `category_id` FK,
    `product_line`, `material_vi`, `spec_vi`, `list_price_vnd`, `standard_cost_vnd`,
    `gross_margin_pct`, `sourcing_type`, `popularity_rank`, `launch_date`, `is_active`.
11. `dim_trade_program` (~64) — `program_id` PK, `program_name_vi`, `program_type`, `channel_id` FK,
    `chain_id` FK NULL, `platform_id` FK NULL, `target_category_id` FK NULL,
    `target_product_line` NULL, `start_date`, `end_date`, `description_vi`.

## FACT TABLES (11)

12. `fact_sales_out` (~850K) — grain: ngày × SKU × điểm bán/kênh. `sale_id` PK, `sale_date` FK,
    `channel_id`, `province_id`, `product_id`, `distributor_id` NULL, `chain_id` NULL,
    `showroom_id` NULL, `platform_id` NULL, `quantity`, `list_price_vnd`,
    `actual_unit_price_vnd`, `gross_revenue_vnd`, `discount_vnd`, `net_revenue_vnd`, `cogs_vnd`,
    `gross_profit_vnd`.
13. `fact_sales_in` (~95K) — sell-in kênh GT. `shipment_id` PK, `ship_date` FK, `distributor_id`,
    `product_id`, `quantity`, `unit_price_vnd`, `net_amount_vnd`, `cogs_vnd`, `payment_due_date`.
14. `fact_distributor_inventory` (1.152, SNAPSHOT cuối tháng) — `snapshot_date`, `distributor_id`,
    `inventory_units`, `inventory_value_vnd`, `days_on_hand`, `aging_over_90d_value_vnd`.
15. `fact_receivables` (1.152, SNAPSHOT cuối tháng) — `snapshot_date`, `distributor_id`,
    `total_ar_vnd`, `current_vnd`, `overdue_1_30_vnd`, `overdue_31_60_vnd`, `overdue_over_60_vnd`,
    `dso_days`.
16. `fact_trade_spend` (~5.200) — grain tháng × kênh × chuỗi/sàn/NPP × chương trình × nhóm hàng.
    `spend_id` PK, `spend_month`, `channel_id`, `chain_id` NULL, `platform_id` NULL,
    `distributor_id` NULL, `program_id`, `category_id` NULL, `amount_vnd`.
17. `fact_showroom_traffic` (30.660) — grain ngày × showroom. `traffic_date`, `showroom_id`,
    `visitor_count`, `transaction_count`, `conversion_pct`, `avg_basket_vnd`.
18. `fact_price_tracking` (87.360) — grain tuần (thứ Hai) × SKU × 2 kênh (SR, ONL). `track_date`,
    `product_id`, `channel_id`, `listed_price_vnd`, `effective_price_vnd`,
    `voucher_discount_pct`, `price_gap_vs_showroom_pct`.
19. `fact_production` (~19K) — grain tuần × SKU sản xuất nội bộ. `production_week`, `product_id`,
    `line_code`, `planned_quantity`, `actual_quantity`, `oee_pct`, `plan_source`.
20. `fact_inventory_snapshot` (43.680, SNAPSHOT cuối tuần) — `snapshot_date`, `product_id`,
    `warehouse_code`, `quantity_on_hand`, `inventory_value_vnd`, `days_on_hand`, `age_bucket`.
21. `fact_stockout` (~34K) — grain ngày × SKU × kênh, chỉ ghi khi có OOS. `stockout_date`,
    `product_id`, `channel_id`, `location_ref`, `stockout_days_in_month`, `estimated_lost_qty`,
    `estimated_lost_revenue_vnd`.
22. `fact_monthly_financials` (264) — grain tháng × hạng mục chi phí. `month_date`,
    `cost_category_vi`, `amount_vnd`.

## METADATA TABLES (4)

`_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary`.

---

Xem tài liệu gốc `ELMICH_claude-code-instruction.md` (đính kèm cho Claude Code khi khởi tạo dự
án) để biết đầy đủ: sơ đồ quan hệ FK, SQL templates mẫu, join warnings, 6 demo scenario và 4
anomaly (A1 xói mòn biên MT, A2 nhồi hàng GT miền Trung, A3 online ăn thịt showroom, A4 lệch pha
nhà máy–thị trường), cùng các mốc neo tài chính bắt buộc.
