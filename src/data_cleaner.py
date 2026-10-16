"""
Data Cleaning, Merging, and Star-Schema Preparation for Power BI and Analytics.
Creates:
1. data/processed/cleaned_ecommerce_returns.csv (flat master analytical dataset)
2. data/processed/powerbi_star_schema/ (dimensional model: facts & dimensions)
3. data/ecommerce.db (SQLite database for running SQL queries)
"""

import os
import sqlite3
import pandas as pd
import numpy as np

def clean_and_prepare_data(raw_dir="data/raw", processed_dir="data/processed"):
    os.makedirs(processed_dir, exist_ok=True)
    star_schema_dir = os.path.join(processed_dir, "powerbi_star_schema")
    os.makedirs(star_schema_dir, exist_ok=True)
    
    print("Loading raw files...")
    df_orders = pd.read_csv(os.path.join(raw_dir, "orders_raw.csv"))
    df_returns = pd.read_csv(os.path.join(raw_dir, "returns_raw.csv"))
    df_products = pd.read_csv(os.path.join(raw_dir, "products_raw.csv"))
    df_customers = pd.read_csv(os.path.join(raw_dir, "customers_raw.csv"))
    df_suppliers = pd.read_csv(os.path.join(raw_dir, "suppliers_raw.csv"))
    
    # 1. Clean Orders
    df_orders["order_date"] = pd.to_datetime(df_orders["order_date"])
    df_orders["discount_percent"] = df_orders["discount_percent"].clip(0.0, 0.90)
    df_orders["quantity"] = df_orders["quantity"].astype(int)
    df_orders["net_amount"] = df_orders["net_amount"].round(2)
    
    # 2. Clean Returns
    df_returns["return_date"] = pd.to_datetime(df_returns["return_date"])
    df_returns["refund_amount"] = df_returns["refund_amount"].round(2)
    df_returns["return_reason"] = df_returns["return_reason"].fillna("Reason Not Specified")
    df_returns["return_status"] = df_returns["return_status"].fillna("Pending")
    df_returns["item_condition"] = df_returns["item_condition"].fillna("Uninspected")
    
    # 3. Merge for Unified Master Analytical Table
    # Drop unit_price from products before merging since orders already has unit_price
    products_to_merge = df_products.drop(columns=["unit_price"])
    df_master = df_orders.merge(df_returns, on="order_id", how="left")
    df_master = df_master.merge(products_to_merge, on="product_id", how="left")
    df_master = df_master.merge(df_customers, on="customer_id", how="left")
    df_master = df_master.merge(df_suppliers, on="supplier_id", how="left")
    
    # Fill return-specific nulls for non-returned items
    df_master["return_reason"] = df_master["return_reason"].fillna("Not Returned")
    df_master["return_status"] = df_master["return_status"].fillna("Not Applicable")
    df_master["item_condition"] = df_master["item_condition"].fillna("Not Applicable")
    df_master["refund_amount"] = df_master["refund_amount"].fillna(0.0)
    
    # Derived Business Metrics
    df_master["order_year"] = df_master["order_date"].dt.year
    df_master["order_month"] = df_master["order_date"].dt.strftime("%Y-%m")
    df_master["order_quarter"] = "Q" + df_master["order_date"].dt.quarter.astype(str)
    df_master["order_day_name"] = df_master["order_date"].dt.day_name()
    
    # Calculate return turnaround days
    df_master["days_to_return"] = (df_master["return_date"] - df_master["order_date"]).dt.days
    df_master["days_to_return"] = df_master["days_to_return"].fillna(-1).astype(int)
    
    # Save flat cleaned master
    master_path = os.path.join(processed_dir, "cleaned_ecommerce_returns.csv")
    df_master.to_csv(master_path, index=False)
    print(f"Master cleaned dataset saved to: {master_path} ({len(df_master)} records)")
    
    # 4. Prepare Star Schema for Power BI
    # Dim_Date
    min_date = df_orders["order_date"].min()
    max_date = pd.to_datetime("2026-01-31")
    date_range = pd.date_range(min_date, max_date, freq="D")
    df_dim_date = pd.DataFrame({"date_key": date_range.strftime("%Y-%m-%d"), "full_date": date_range})
    df_dim_date["year"] = df_dim_date["full_date"].dt.year
    df_dim_date["quarter"] = "Q" + df_dim_date["full_date"].dt.quarter.astype(str)
    df_dim_date["month_number"] = df_dim_date["full_date"].dt.month
    df_dim_date["month_name"] = df_dim_date["full_date"].dt.strftime("%B")
    df_dim_date["month_year"] = df_dim_date["full_date"].dt.strftime("%b %Y")
    df_dim_date["day_of_week"] = df_dim_date["full_date"].dt.day_name()
    df_dim_date["is_weekend"] = df_dim_date["full_date"].dt.weekday.apply(lambda x: 1 if x >= 5 else 0)
    
    # Dim_Products
    df_dim_products = df_products.copy()
    
    # Dim_Suppliers
    df_dim_suppliers = df_suppliers.copy()
    
    # Dim_Customers
    df_dim_customers = df_customers.copy()
    
    # Fact_Orders_Returns
    fact_cols = [
        "order_id", "order_date", "customer_id", "product_id", "supplier_id",
        "quantity", "unit_price", "discount_percent", "discount_amount", "net_amount",
        "marketing_channel", "payment_method", "shipping_type", "promised_delivery_days",
        "actual_delivery_days", "delivery_delay_days", "is_delayed", "is_returned",
        "return_id", "return_date", "return_reason", "return_status", "refund_amount", "item_condition"
    ]
    df_fact = df_master[fact_cols].copy()
    
    # Export Star Schema CSVs
    df_dim_date.to_csv(os.path.join(star_schema_dir, "dim_dates.csv"), index=False)
    df_dim_products.to_csv(os.path.join(star_schema_dir, "dim_products.csv"), index=False)
    df_dim_suppliers.to_csv(os.path.join(star_schema_dir, "dim_suppliers.csv"), index=False)
    df_dim_customers.to_csv(os.path.join(star_schema_dir, "dim_customers.csv"), index=False)
    df_fact.to_csv(os.path.join(star_schema_dir, "fact_orders_returns.csv"), index=False)
    
    print(f"Power BI Star Schema exported to {star_schema_dir}")
    
    # 5. Populate SQLite Database for SQL Analysis
    db_path = os.path.join("data", "ecommerce.db")
    conn = sqlite3.connect(db_path)
    
    df_suppliers.to_sql("suppliers", conn, if_exists="replace", index=False)
    df_products.to_sql("products", conn, if_exists="replace", index=False)
    df_customers.to_sql("customers", conn, if_exists="replace", index=False)
    df_orders.to_sql("orders", conn, if_exists="replace", index=False)
    df_returns.to_sql("returns", conn, if_exists="replace", index=False)
    df_fact.to_sql("fact_orders_returns", conn, if_exists="replace", index=False)
    
    # Create indexes for rapid querying
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_cust ON orders(customer_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_prod ON orders(product_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_returns_ord ON returns(order_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_supp ON products(supplier_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_cat ON fact_orders_returns(product_id, supplier_id);")
    conn.commit()
    conn.close()
    print(f"SQLite database populated with indexes at {db_path}")

if __name__ == "__main__":
    clean_and_prepare_data()
