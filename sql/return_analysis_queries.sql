-- ====================================================================
-- E-commerce Return Rate Reduction Analysis: Production SQL Queries
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Return % and Financial Impact by Product Category
-- --------------------------------------------------------------------
SELECT 
    p.category,
    COUNT(o.order_id) AS total_orders,
    SUM(o.is_returned) AS total_returns,
    ROUND(100.0 * SUM(o.is_returned) / COUNT(o.order_id), 2) AS return_rate_pct,
    ROUND(SUM(o.net_amount), 2) AS gross_sales_amount,
    ROUND(SUM(CASE WHEN o.is_returned = 1 THEN o.net_amount ELSE 0 END), 2) AS returned_sales_amount,
    ROUND(100.0 * SUM(CASE WHEN o.is_returned = 1 THEN o.net_amount ELSE 0 END) / SUM(o.net_amount), 2) AS revenue_lost_pct
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;


-- --------------------------------------------------------------------
-- QUERY 2: Return % and Quality Metrics by Supplier
-- --------------------------------------------------------------------
SELECT 
    s.supplier_id,
    s.supplier_name,
    s.country,
    s.quality_score,
    ROUND(s.defect_rate * 100, 2) AS declared_defect_rate_pct,
    COUNT(o.order_id) AS total_orders,
    SUM(o.is_returned) AS returned_orders,
    ROUND(100.0 * SUM(o.is_returned) / COUNT(o.order_id), 2) AS actual_return_rate_pct,
    ROUND(SUM(CASE WHEN o.is_returned = 1 THEN o.net_amount ELSE 0 END), 2) AS total_refunded_value
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.country, s.quality_score, s.defect_rate
ORDER BY actual_return_rate_pct DESC;


-- --------------------------------------------------------------------
-- QUERY 3: Return % by Marketing Channel & Discount Sensitivity
-- --------------------------------------------------------------------
SELECT 
    o.marketing_channel,
    COUNT(o.order_id) AS total_orders,
    SUM(o.is_returned) AS total_returns,
    ROUND(100.0 * SUM(o.is_returned) / COUNT(o.order_id), 2) AS return_rate_pct,
    ROUND(AVG(o.discount_percent) * 100, 2) AS avg_discount_pct,
    ROUND(AVG(o.net_amount), 2) AS avg_order_value,
    ROUND(SUM(CASE WHEN o.is_returned = 1 THEN o.net_amount ELSE 0 END), 2) AS total_refunded_amount
FROM orders o
GROUP BY o.marketing_channel
ORDER BY return_rate_pct DESC;


-- --------------------------------------------------------------------
-- QUERY 4: Return % by Geographic Region & Delivery Delay Impact
-- --------------------------------------------------------------------
SELECT 
    c.region,
    c.state,
    COUNT(o.order_id) AS total_orders,
    SUM(o.is_returned) AS total_returns,
    ROUND(100.0 * SUM(o.is_returned) / COUNT(o.order_id), 2) AS return_rate_pct,
    ROUND(AVG(o.actual_delivery_days), 2) AS avg_delivery_days,
    ROUND(AVG(o.delivery_delay_days), 2) AS avg_delay_days,
    ROUND(100.0 * SUM(o.is_delayed) / COUNT(o.order_id), 2) AS pct_orders_delayed
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.region, c.state
ORDER BY return_rate_pct DESC;


-- --------------------------------------------------------------------
-- QUERY 5: Top Return Reasons Breakdown per Category
-- --------------------------------------------------------------------
SELECT 
    p.category,
    r.return_reason,
    COUNT(r.return_id) AS return_reason_count,
    ROUND(100.0 * COUNT(r.return_id) / SUM(COUNT(r.return_id)) OVER(PARTITION BY p.category), 2) AS category_reason_share_pct
FROM returns r
JOIN orders o ON r.order_id = o.order_id
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category, r.return_reason
ORDER BY p.category, return_reason_count DESC;


-- --------------------------------------------------------------------
-- QUERY 6: Top 15 Highest Risk Products (High Volume & Return Rate)
-- --------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    s.supplier_name,
    COUNT(o.order_id) AS total_sold,
    SUM(o.is_returned) AS total_returns,
    ROUND(100.0 * SUM(o.is_returned) / COUNT(o.order_id), 2) AS return_rate_pct,
    ROUND(SUM(CASE WHEN o.is_returned = 1 THEN o.net_amount ELSE 0 END), 2) AS total_refunded_amount
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
GROUP BY p.product_id, p.product_name, p.category, s.supplier_name
HAVING COUNT(o.order_id) >= 50
ORDER BY return_rate_pct DESC, total_refunded_amount DESC
LIMIT 15;


-- --------------------------------------------------------------------
-- QUERY 7: Impact of Payment Method (e.g. BNPL / Klarna vs Credit Card)
-- --------------------------------------------------------------------
SELECT 
    o.payment_method,
    COUNT(o.order_id) AS total_orders,
    SUM(o.is_returned) AS total_returns,
    ROUND(100.0 * SUM(o.is_returned) / COUNT(o.order_id), 2) AS return_rate_pct,
    ROUND(AVG(o.net_amount), 2) AS avg_order_value
FROM orders o
GROUP BY o.payment_method
ORDER BY return_rate_pct DESC;
