"""
Prediction & Risk Scoring Pipeline:
Loads trained model, scores orders and products, assigns Risk Tiers, and generates deliverables:
- deliverables/high_risk_products.csv
- deliverables/order_return_risk_scores.csv
"""

import os
import joblib
import pandas as pd
import numpy as np

def generate_risk_predictions(
    data_path="data/processed/cleaned_ecommerce_returns.csv",
    model_path="models/logistic_regression_pipeline.joblib",
    deliverables_dir="deliverables",
    star_schema_dir="data/processed/powerbi_star_schema"
):
    os.makedirs(deliverables_dir, exist_ok=True)
    os.makedirs(star_schema_dir, exist_ok=True)
    
    print("Loading dataset and trained model...")
    df = pd.read_csv(data_path)
    pipeline = joblib.load(model_path)
    
    numeric_features = [
        "unit_price",
        "discount_percent",
        "quantity",
        "delivery_delay_days",
        "actual_delivery_days",
        "customer_tenure_months",
        "historical_return_rate",
        "prior_orders_count"
    ]
    
    categorical_features = [
        "category",
        "marketing_channel",
        "payment_method",
        "shipping_type",
        "region",
        "customer_segment"
    ]
    
    X = df[numeric_features + categorical_features].copy()
    
    # Predict Probability
    print("Generating return risk probabilities...")
    return_probabilities = pipeline.predict_proba(X)[:, 1]
    
    df["predicted_return_prob"] = np.round(return_probabilities, 4)
    
    # Risk Tier Segmentation
    def assign_risk_tier(prob):
        if prob >= 0.45:
            return "High Risk"
        elif prob >= 0.25:
            return "Medium Risk"
        else:
            return "Low Risk"
            
    df["risk_tier"] = df["predicted_return_prob"].apply(assign_risk_tier)
    df["expected_refund_loss"] = np.round(df["net_amount"] * df["predicted_return_prob"], 2)
    
    # ---------------------------------------------------------
    # Deliverable 1: Order-Level Return Risk Scores CSV
    # ---------------------------------------------------------
    order_deliverable_cols = [
        "order_id", "order_date", "customer_id", "customer_segment",
        "product_id", "product_name", "category", "subcategory", "supplier_name",
        "net_amount", "discount_percent", "marketing_channel", "payment_method",
        "actual_delivery_days", "delivery_delay_days", "is_returned",
        "predicted_return_prob", "risk_tier", "expected_refund_loss"
    ]
    df_orders_scored = df[order_deliverable_cols].copy()
    orders_output_path = os.path.join(deliverables_dir, "order_return_risk_scores.csv")
    df_orders_scored.to_csv(orders_output_path, index=False)
    print(f"Deliverable saved: {orders_output_path} ({len(df_orders_scored)} orders)")
    
    # Also save to star schema folder for seamless Power BI consumption
    df_orders_scored.to_csv(os.path.join(star_schema_dir, "fact_orders_scored.csv"), index=False)
    
    # ---------------------------------------------------------
    # Deliverable 2: High-Risk Products CSV
    # ---------------------------------------------------------
    # Aggregate product risk metrics
    # Find top return reason per product
    returns_reasons = df[df["is_returned"] == 1].groupby(["product_id", "return_reason"]).size().reset_index(name="reason_count")
    idx_top_reason = returns_reasons.groupby("product_id")["reason_count"].idxmax()
    top_reasons_df = returns_reasons.loc[idx_top_reason, ["product_id", "return_reason"]].rename(
        columns={"return_reason": "primary_return_reason"}
    )
    
    prod_summary = df.groupby([
        "product_id", "product_name", "category", "subcategory", "supplier_name", "unit_price"
    ]).agg(
        total_orders=("order_id", "count"),
        total_returns=("is_returned", "sum"),
        actual_return_rate=("is_returned", "mean"),
        avg_predicted_return_risk=("predicted_return_prob", "mean"),
        total_revenue=("net_amount", "sum"),
        total_refund_amount=("refund_amount", "sum"),
        total_expected_refund_loss=("expected_refund_loss", "sum")
    ).reset_index()
    
    # Merge primary reason
    prod_summary = prod_summary.merge(top_reasons_df, on="product_id", how="left")
    prod_summary["primary_return_reason"] = prod_summary["primary_return_reason"].fillna("No Returns Recorded")
    
    # Format percentages and rounding
    prod_summary["actual_return_rate_pct"] = np.round(prod_summary["actual_return_rate"] * 100, 2)
    prod_summary["avg_predicted_risk_pct"] = np.round(prod_summary["avg_predicted_return_risk"] * 100, 2)
    prod_summary["total_revenue"] = np.round(prod_summary["total_revenue"], 2)
    prod_summary["total_refund_amount"] = np.round(prod_summary["total_refund_amount"], 2)
    prod_summary["total_expected_refund_loss"] = np.round(prod_summary["total_expected_refund_loss"], 2)
    
    # Filter for high-risk products (predicted risk >= 35% or actual return rate >= 35%)
    high_risk_products = prod_summary[
        (prod_summary["avg_predicted_risk_pct"] >= 35.0) | (prod_summary["actual_return_rate_pct"] >= 40.0)
    ].sort_values(by=["avg_predicted_risk_pct", "total_refund_amount"], ascending=[False, False]).copy()
    
    # Actionable Business Recommendations based on Category and Primary Reason
    def recommend_action(row):
        cat = row["category"]
        reason = str(row["primary_return_reason"])
        if "Fit" in reason or "Sizing" in reason:
            return "Implement 3D AR Size Guide, update size chart with bust/waist dimensions, and prompt fit survey at checkout"
        elif "Defective" in reason or "Quality" in reason:
            return "Issue supplier QC audit warning, withhold vendor batch payout, and inspect warehouse intake"
        elif "Damaged" in reason:
            return "Upgrade transit packaging, mandate corner foam padding with carrier, switch shipping tier"
        elif "Not Functioning" in reason or "setup" in reason:
            return "Include QR code quick-start video guide in box; offer proactive post-purchase onboarding SMS"
        elif "Fabric" in reason or "Color" in reason:
            return "Update studio photography with true-color lighting and add customer unedited review photos"
        else:
            return "Review customer feedback, evaluate price/value alignment, and restrict deep discounting"
            
    high_risk_products["recommended_mitigation_action"] = high_risk_products.apply(recommend_action, axis=1)
    
    # Assign Risk Grade
    def assign_grade(risk_pct):
        if risk_pct >= 50.0:
            return "Critical (Grade E)"
        elif risk_pct >= 40.0:
            return "Severe (Grade D)"
        else:
            return "Elevated (Grade C)"
            
    high_risk_products["risk_grade"] = high_risk_products["avg_predicted_risk_pct"].apply(assign_grade)
    
    high_risk_output_path = os.path.join(deliverables_dir, "high_risk_products.csv")
    high_risk_products.to_csv(high_risk_output_path, index=False)
    print(f"Deliverable saved: {high_risk_output_path} ({len(high_risk_products)} high risk products identified)")
    
    print("\nTop 5 Highest Risk Products Preview:")
    print(high_risk_products[[
        "product_id", "product_name", "category", "supplier_name", "actual_return_rate_pct", "avg_predicted_risk_pct", "primary_return_reason"
    ]].head(5).to_string(index=False))
    
    return high_risk_products, df_orders_scored

if __name__ == "__main__":
    generate_risk_predictions()
