"""
Exploratory Data Analysis & Presentation-Ready Visualizations
Saves high-resolution figures to reports/figures/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def generate_eda_figures(
    data_path="data/processed/cleaned_ecommerce_returns.csv",
    predictions_path="deliverables/order_return_risk_scores.csv",
    output_dir="reports/figures"
):
    os.makedirs(output_dir, exist_ok=True)
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    
    df = pd.read_csv(data_path)
    df_pred = pd.read_csv(predictions_path)
    
    # 1. Return % by Category Bar Chart
    cat_summary = df.groupby("category").agg(
        orders=("order_id", "count"),
        returns=("is_returned", "sum")
    ).reset_index()
    cat_summary["return_rate"] = cat_summary["returns"] / cat_summary["orders"] * 100
    cat_summary = cat_summary.sort_values(by="return_rate", ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    bars = ax.bar(cat_summary["category"], cat_summary["return_rate"], color="#3b82f6", width=0.55, edgecolor="#1e40af")
    ax.axhline(df["is_returned"].mean() * 100, color="#ef4444", linestyle="--", linewidth=1.5, 
               label=f"Overall Avg Return Rate ({df['is_returned'].mean()*100:.1f}%)")
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=11, fontweight="bold", color="#1e293b")
    ax.set_title("Return Rate (%) by Product Category", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Return Rate (%)", fontsize=11)
    ax.set_ylim(0, max(cat_summary["return_rate"]) + 10)
    ax.legend(frameon=True, facecolor="white")
    plt.xticks(rotation=15, ha="right", fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "return_rate_by_category.png"))
    plt.close()
    
    # 2. Return Rate by Supplier (with quality score)
    supp_summary = df.groupby(["supplier_name", "quality_score"]).agg(
        orders=("order_id", "count"),
        returns=("is_returned", "sum")
    ).reset_index()
    supp_summary["return_rate"] = supp_summary["returns"] / supp_summary["orders"] * 100
    supp_summary = supp_summary.sort_values(by="return_rate", ascending=True)
    
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    colors = ["#ef4444" if r > 35 else "#f59e0b" if r > 25 else "#10b981" for r in supp_summary["return_rate"]]
    bars = ax.barh(supp_summary["supplier_name"], supp_summary["return_rate"], color=colors, height=0.6)
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{w:.1f}%",
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(6, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=10, fontweight="bold")
    ax.set_title("Return Rate (%) by Supplier", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Return Rate (%)", fontsize=11)
    ax.set_xlim(0, max(supp_summary["return_rate"]) + 10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "return_rate_by_supplier.png"))
    plt.close()
    
    # 3. Return % by Marketing Channel
    chan_summary = df.groupby("marketing_channel").agg(
        orders=("order_id", "count"),
        returns=("is_returned", "sum")
    ).reset_index()
    chan_summary["return_rate"] = chan_summary["returns"] / chan_summary["orders"] * 100
    chan_summary = chan_summary.sort_values(by="return_rate", ascending=False)
    
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    bars = ax.bar(chan_summary["marketing_channel"], chan_summary["return_rate"], color="#6366f1", width=0.5)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_title("Return Rate (%) by Customer Acquisition Marketing Channel", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("Return Rate (%)", fontsize=11)
    ax.set_ylim(0, max(chan_summary["return_rate"]) + 8)
    plt.xticks(rotation=20, ha="right", fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "return_rate_by_channel.png"))
    plt.close()
    
    # 4. Return Rate by Delivery Delay Days
    delay_summary = df.groupby("delivery_delay_days").agg(
        orders=("order_id", "count"),
        returns=("is_returned", "sum")
    ).reset_index()
    delay_summary = delay_summary[delay_summary["orders"] >= 50]
    delay_summary["return_rate"] = delay_summary["returns"] / delay_summary["orders"] * 100
    
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)
    ax.plot(delay_summary["delivery_delay_days"], delay_summary["return_rate"], marker="o", color="#dc2626", linewidth=2.5, markersize=8)
    for _, row in delay_summary.iterrows():
        ax.annotate(f"{row['return_rate']:.1f}%",
                    xy=(row["delivery_delay_days"], row["return_rate"]),
                    xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=9, fontweight="bold")
    ax.set_title("Impact of Delivery Delays on Product Return Probability", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Days Delayed Beyond Promised Delivery Date", fontsize=11)
    ax.set_ylabel("Return Rate (%)", fontsize=11)
    ax.set_ylim(0, max(delay_summary["return_rate"]) + 10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "return_rate_by_delivery_delay.png"))
    plt.close()
    
    # 5. Risk Tier Distribution from Model Predictions
    tier_summary = df_pred["risk_tier"].value_counts(normalize=True).reset_index()
    tier_summary.columns = ["risk_tier", "percentage"]
    tier_summary["percentage"] *= 100
    
    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    tier_colors = {"Low Risk": "#10b981", "Medium Risk": "#f59e0b", "High Risk": "#ef4444"}
    bars = ax.bar(tier_summary["risk_tier"], tier_summary["percentage"], 
                  color=[tier_colors.get(t, "#64748b") for t in tier_summary["risk_tier"]], width=0.45)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_title("Predicted Return Risk Tier Distribution (Orders)", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("Share of Orders (%)", fontsize=11)
    ax.set_ylim(0, max(tier_summary["percentage"]) + 10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "predicted_risk_tier_distribution.png"))
    plt.close()
    
    print(f"All EDA and Risk visualizations generated in {output_dir}")

if __name__ == "__main__":
    generate_eda_figures()
