-- ====================================================================
-- E-commerce Return Rate Reduction Analysis: Database Schema
-- Compatible with SQLite, PostgreSQL, MySQL, and Snowflake
-- ====================================================================

-- 1. Suppliers Dimension
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(20) PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    defect_rate DECIMAL(5, 4),
    quality_score DECIMAL(3, 1)
);

-- 2. Products Dimension
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50) NOT NULL,
    supplier_id VARCHAR(20) REFERENCES suppliers(supplier_id),
    unit_price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL,
    sizing_sensitive INT DEFAULT 0,
    base_return_risk DECIMAL(5, 4)
);

-- 3. Customers Dimension
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_segment VARCHAR(50) NOT NULL,
    customer_tenure_months INT,
    state VARCHAR(50),
    state_code VARCHAR(10),
    region VARCHAR(30),
    delivery_lag_bias INT DEFAULT 0,
    prior_orders_count INT DEFAULT 0,
    prior_returns_count INT DEFAULT 0,
    historical_return_rate DECIMAL(5, 4)
);

-- 4. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(30) PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_id VARCHAR(20) REFERENCES customers(customer_id),
    product_id VARCHAR(20) REFERENCES products(product_id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_percent DECIMAL(5, 4) DEFAULT 0.0,
    discount_amount DECIMAL(10, 2) DEFAULT 0.0,
    net_amount DECIMAL(10, 2) NOT NULL,
    marketing_channel VARCHAR(50),
    payment_method VARCHAR(50),
    shipping_type VARCHAR(50),
    promised_delivery_days INT,
    actual_delivery_days INT,
    delivery_delay_days INT,
    is_delayed INT DEFAULT 0,
    is_returned INT DEFAULT 0
);

-- 5. Returns Table
CREATE TABLE IF NOT EXISTS returns (
    return_id VARCHAR(30) PRIMARY KEY,
    order_id VARCHAR(30) REFERENCES orders(order_id),
    return_date DATE NOT NULL,
    return_reason VARCHAR(150),
    return_status VARCHAR(50),
    refund_amount DECIMAL(10, 2),
    item_condition VARCHAR(100)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_ord_cust ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_ord_prod ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_ret_ord ON returns(order_id);
CREATE INDEX IF NOT EXISTS idx_prod_supp ON products(supplier_id);
