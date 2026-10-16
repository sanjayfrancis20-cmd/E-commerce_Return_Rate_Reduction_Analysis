"""
SQL Analytics Runner: Executes core queries against SQLite database and generates analytical summary tables.
"""

import os
import sqlite3
import pandas as pd

def run_sql_analytics(db_path="data/ecommerce.db", output_dir="reports"):
    os.makedirs(output_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    print("=" * 70)
    print("E-COMMERCE RETURN RATE REDUCTION ANALYSIS: SQL QUERY RESULTS")
    print("=" * 70)
    
    # 1. Category
    q_cat = """
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
    """
    df_cat = pd.read_sql_query(q_cat, conn)
    print("\n[1] Return Rate by Product Category:")
    print(df_cat.to_string(index=False))
    
    # 2. Supplier
    q_supp = """
    SELECT 
        s.supplier_id,
        s.supplier_name,
        s.country,
        s.quality_score,
        ROUND(s.defect_rate * 100, 2) AS declared_defect_pct,
        COUNT(o.order_id) AS total_orders,
        SUM(o.is_returned) AS returned_orders,
        ROUND(100.0 * SUM(o.is_returned) / COUNT(o.order_id), 2) AS return_rate_pct,
        ROUND(SUM(CASE WHEN o.is_returned = 1 THEN o.net_amount ELSE 0 END), 2) AS total_refunded_value
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    JOIN suppliers s ON p.supplier_id = s.supplier_id
    GROUP BY s.supplier_id, s.supplier_name, s.country, s.quality_score, s.defect_rate
    ORDER BY return_rate_pct DESC;
    """
    df_supp = pd.read_sql_query(q_supp, conn)
    print("\n[2] Return Rate by Supplier:")
    print(df_supp.to_string(index=False))
    
    # 3. Marketing Channel
    q_chan = """
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
    """
    df_chan = pd.read_sql_query(q_chan, conn)
    print("\n[3] Return Rate by Marketing Channel:")
    print(df_chan.to_string(index=False))
    
    # 4. Geography
    q_geo = """
    SELECT 
        c.region,
        COUNT(o.order_id) AS total_orders,
        SUM(o.is_returned) AS total_returns,
        ROUND(100.0 * SUM(o.is_returned) / COUNT(o.order_id), 2) AS return_rate_pct,
        ROUND(AVG(o.actual_delivery_days), 2) AS avg_delivery_days,
        ROUND(AVG(o.delivery_delay_days), 2) AS avg_delay_days,
        ROUND(100.0 * SUM(o.is_delayed) / COUNT(o.order_id), 2) AS pct_delayed
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY c.region
    ORDER BY return_rate_pct DESC;
    """
    df_geo = pd.read_sql_query(q_geo, conn)
    print("\n[4] Return Rate by Geography / Region:")
    print(df_geo.to_string(index=False))
    
    # Save SQL aggregation outputs
    df_cat.to_csv(os.path.join(output_dir, "sql_summary_category.csv"), index=False)
    df_supp.to_csv(os.path.join(output_dir, "sql_summary_supplier.csv"), index=False)
    df_chan.to_csv(os.path.join(output_dir, "sql_summary_channel.csv"), index=False)
    df_geo.to_csv(os.path.join(output_dir, "sql_summary_geography.csv"), index=False)
    
    conn.close()
    print("\nSQL Analytics executed successfully. Aggregation tables saved to reports/")

if __name__ == "__main__":
    run_sql_analytics()
