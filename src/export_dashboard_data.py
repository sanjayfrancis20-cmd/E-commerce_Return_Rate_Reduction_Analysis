"""
Exports aggregated and granular data into dashboard/data.json for the interactive dashboard.
"""

import os
import json
import pandas as pd
import numpy as np

def export_dashboard_json():
    df_master = pd.read_csv("data/processed/cleaned_ecommerce_returns.csv")
    df_scored = pd.read_csv("deliverables/order_return_risk_scores.csv")
    df_high_risk = pd.read_csv("deliverables/high_risk_products.csv")
    
    # 1. Overall KPIs
    total_orders = int(len(df_scored))
    total_returns = int(df_scored["is_returned"].sum())
    overall_return_rate = round(float(total_returns / total_orders * 100), 2)
    total_revenue = round(float(df_scored["net_amount"].sum()), 2)
    total_refunded = round(float(df_master["refund_amount"].sum()), 2)
    revenue_at_risk = round(float(df_scored["expected_refund_loss"].sum()), 2)
    high_risk_orders_count = int((df_scored["risk_tier"] == "High Risk").sum())
    
    # 2. Category Aggregations
    cat_agg = df_scored.groupby("category").agg(
        orders=("order_id", "count"),
        returns=("is_returned", "sum"),
        revenue=("net_amount", "sum"),
        avg_risk=("predicted_return_prob", "mean")
    ).reset_index()
    cat_agg["return_rate"] = np.round(cat_agg["returns"] / cat_agg["orders"] * 100, 2)
    cat_agg["avg_risk_pct"] = np.round(cat_agg["avg_risk"] * 100, 2)
    cat_data = cat_agg.sort_values(by="return_rate", ascending=False).to_dict("records")
    
    # 3. Supplier Aggregations
    supp_agg = df_master.groupby(["supplier_id", "supplier_name", "country", "quality_score"]).agg(
        orders=("order_id", "count"),
        returns=("is_returned", "sum"),
        refunded=("refund_amount", "sum")
    ).reset_index()
    supp_agg["return_rate"] = np.round(supp_agg["returns"] / supp_agg["orders"] * 100, 2)
    supp_data = supp_agg.sort_values(by="return_rate", ascending=False).to_dict("records")
    
    # 4. Marketing Channel Aggregations
    chan_agg = df_scored.groupby("marketing_channel").agg(
        orders=("order_id", "count"),
        returns=("is_returned", "sum"),
        avg_discount=("discount_percent", "mean")
    ).reset_index()
    chan_agg["return_rate"] = np.round(chan_agg["returns"] / chan_agg["orders"] * 100, 2)
    chan_agg["avg_discount_pct"] = np.round(chan_agg["avg_discount"] * 100, 2)
    chan_data = chan_agg.sort_values(by="return_rate", ascending=False).to_dict("records")
    
    # 5. Geography Aggregations
    geo_agg = df_master.groupby("region").agg(
        orders=("order_id", "count"),
        returns=("is_returned", "sum"),
        avg_delay=("delivery_delay_days", "mean")
    ).reset_index()
    geo_agg["return_rate"] = np.round(geo_agg["returns"] / geo_agg["orders"] * 100, 2)
    geo_agg["avg_delay"] = np.round(geo_agg["avg_delay"], 2)
    geo_data = geo_agg.sort_values(by="return_rate", ascending=False).to_dict("records")
    
    # 6. Return Reasons Breakdown
    reason_agg = df_master[df_master["is_returned"] == 1]["return_reason"].value_counts().reset_index()
    reason_agg.columns = ["reason", "count"]
    reason_data = reason_agg.to_dict("records")
    
    # 7. High Risk Products List
    high_risk_list = df_high_risk.to_dict("records")
    
    # 8. All Products List (for complete drill-through)
    all_prods = df_master.groupby(["product_id", "product_name", "category", "subcategory", "supplier_name", "unit_price"]).agg(
        orders=("order_id", "count"),
        returns=("is_returned", "sum"),
        refunded=("refund_amount", "sum")
    ).reset_index()
    all_prods = all_prods.merge(df_high_risk[["product_id", "avg_predicted_risk_pct", "primary_return_reason", "recommended_mitigation_action", "risk_grade"]], on="product_id", how="left")
    all_prods["actual_return_rate_pct"] = np.round(all_prods["returns"] / all_prods["orders"] * 100, 2)
    all_prods["avg_predicted_risk_pct"] = all_prods["avg_predicted_risk_pct"].fillna(all_prods["actual_return_rate_pct"]).round(2)
    all_prods["primary_return_reason"] = all_prods["primary_return_reason"].fillna("Standard Wear / None")
    all_prods["risk_grade"] = all_prods["risk_grade"].fillna("Normal (Grade B)")
    all_prods["recommended_mitigation_action"] = all_prods["recommended_mitigation_action"].fillna("Standard catalog monitoring")
    all_prods_list = all_prods.to_dict("records")
    
    # 9. Logistic Regression Feature Importance
    df_coef = pd.read_csv("models/logistic_regression_coefficients.csv")
    features_data = df_coef.head(10).to_dict("records")
    
    # 10. Sample Granular Orders (for order-level drilldown table)
    sample_orders = df_scored.head(300).to_dict("records")
    
    dashboard_payload = {
        "kpis": {
            "total_orders": total_orders,
            "total_returns": total_returns,
            "overall_return_rate": overall_return_rate,
            "total_revenue": total_revenue,
            "total_refunded": total_refunded,
            "revenue_at_risk": revenue_at_risk,
            "high_risk_orders_count": high_risk_orders_count,
            "high_risk_orders_pct": round(high_risk_orders_count / total_orders * 100, 1)
        },
        "categories": cat_data,
        "suppliers": supp_data,
        "channels": chan_data,
        "geography": geo_data,
        "reasons": reason_data,
        "high_risk_products": high_risk_list,
        "all_products": all_prods_list,
        "top_features": features_data,
        "sample_orders": sample_orders
    }
    
    output_path = os.path.join("dashboard", "data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dashboard_payload, f, indent=2)
        
    print(f"Dashboard data exported to: {output_path}")

if __name__ == "__main__":
    export_dashboard_json()
