"""
Machine Learning Model Training Pipeline:
Trains a penalized Logistic Regression model to predict the probability of return.
Evaluates Odds Ratios, ROC-AUC, PR-AUC, Confusion Matrix, and compares against benchmark.
Saves model artifacts and performance charts.
"""

import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    average_precision_score,
    classification_report,
    confusion_matrix,
    brier_score_loss,
    accuracy_score
)

def train_return_prediction_model(
    data_path="data/processed/cleaned_ecommerce_returns.csv",
    model_dir="models",
    figures_dir="reports/figures"
):
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    print("Loading data for modeling...")
    df = pd.read_csv(data_path)
    
    # Feature Definition
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
    
    target = "is_returned"
    
    X = df[numeric_features + categorical_features].copy()
    y = df[target].copy()
    
    # Train / Test Split (Stratified 80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    print(f"Dataset split: Train={len(X_train)} samples, Test={len(X_test)} samples")
    print(f"Target distribution: Train Mean = {y_train.mean():.3f}, Test Mean = {y_test.mean():.3f}")
    
    # Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), categorical_features)
        ]
    )
    
    # Logistic Regression Pipeline (with balanced weights or default penalty)
    log_reg = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs", random_state=42)
    pipeline_lr = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", log_reg)
    ])
    
    print("\nTraining Logistic Regression model...")
    pipeline_lr.fit(X_train, y_train)
    
    # Predictions
    y_pred_lr = pipeline_lr.predict(X_test)
    y_prob_lr = pipeline_lr.predict_proba(X_test)[:, 1]
    
    # Metrics
    auc_lr = roc_auc_score(y_test, y_prob_lr)
    pr_auc_lr = average_precision_score(y_test, y_prob_lr)
    acc_lr = accuracy_score(y_test, y_pred_lr)
    brier_lr = brier_score_loss(y_test, y_prob_lr)
    
    print("\n" + "=" * 60)
    print("LOGISTIC REGRESSION MODEL PERFORMANCE")
    print("=" * 60)
    print(f"ROC-AUC Score:             {auc_lr:.4f}")
    print(f"PR-AUC (Avg Precision):    {pr_auc_lr:.4f}")
    print(f"Accuracy:                  {acc_lr:.4f}")
    print(f"Brier Score Loss:          {brier_lr:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_lr, digits=4))
    
    # Benchmark with Gradient Boosting
    print("\nTraining Benchmark Gradient Boosting Classifier for comparison...")
    pipeline_gb = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42))
    ])
    pipeline_gb.fit(X_train, y_train)
    y_prob_gb = pipeline_gb.predict_proba(X_test)[:, 1]
    auc_gb = roc_auc_score(y_test, y_prob_gb)
    pr_auc_gb = average_precision_score(y_test, y_prob_gb)
    print(f"Gradient Boosting ROC-AUC: {auc_gb:.4f} | PR-AUC: {pr_auc_gb:.4f}")
    
    # Extract Feature Names & Logistic Regression Coefficients / Odds Ratios
    cat_encoder = pipeline_lr.named_steps["preprocessor"].named_transformers_["cat"]
    encoded_cat_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
    all_feature_names = numeric_features + encoded_cat_names
    
    coefs = pipeline_lr.named_steps["classifier"].coef_[0]
    odds_ratios = np.exp(coefs)
    
    df_coefficients = pd.DataFrame({
        "feature": all_feature_names,
        "coefficient": coefs,
        "odds_ratio": odds_ratios,
        "abs_importance": np.abs(coefs)
    }).sort_values(by="abs_importance", ascending=False)
    
    df_coefficients.to_csv(os.path.join(model_dir, "logistic_regression_coefficients.csv"), index=False)
    print(f"\nTop 10 Most Influential Features (Odds Ratios):")
    print(df_coefficients.head(10)[["feature", "coefficient", "odds_ratio"]].to_string(index=False))
    
    # Save Pipeline Model
    model_path = os.path.join(model_dir, "logistic_regression_pipeline.joblib")
    joblib.dump(pipeline_lr, model_path)
    print(f"\nTrained pipeline saved to: {model_path}")
    
    # -------------------------------------------------------------
    # Visualizations: ROC Curve, Confusion Matrix, Odds Ratio Plot
    # -------------------------------------------------------------
    sns.set_theme(style="whitegrid")
    
    # 1. ROC Curves
    fpr_lr, tpr_lr, _ = roc_curve(y_test, y_prob_lr)
    fpr_gb, tpr_gb, _ = roc_curve(y_test, y_prob_gb)
    
    plt.figure(figsize=(8, 6), dpi=300)
    plt.plot(fpr_lr, tpr_lr, color="#2563eb", lw=2.5, label=f"Logistic Regression (AUC = {auc_lr:.3f})")
    plt.plot(fpr_gb, tpr_gb, color="#10b981", lw=2, linestyle="--", label=f"Gradient Boosting (AUC = {auc_gb:.3f})")
    plt.plot([0, 1], [0, 1], color="#94a3b8", linestyle=":", lw=1.5)
    plt.xlabel("False Positive Rate", fontsize=12, labelpad=10)
    plt.ylabel("True Positive Rate (Recall)", fontsize=12, labelpad=10)
    plt.title("Model ROC Curve - E-commerce Return Prediction", fontsize=14, fontweight="bold", pad=15)
    plt.legend(loc="lower right", frameon=True, facecolor="white")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "roc_curve.png"))
    plt.close()
    
    # 2. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred_lr)
    plt.figure(figsize=(7, 5.5), dpi=300)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["Retained (0)", "Returned (1)"],
                yticklabels=["Retained (0)", "Returned (1)"],
                annot_kws={"size": 14, "weight": "bold"})
    plt.xlabel("Predicted Label", fontsize=12, labelpad=10)
    plt.ylabel("Actual True Label", fontsize=12, labelpad=10)
    plt.title("Confusion Matrix - Logistic Regression", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "confusion_matrix.png"))
    plt.close()
    
    # 3. Top 15 Odds Ratios Barplot
    top_features = df_coefficients.head(15).copy().sort_values(by="odds_ratio", ascending=True)
    plt.figure(figsize=(10, 7), dpi=300)
    colors = ["#ef4444" if o > 1.0 else "#10b981" for o in top_features["odds_ratio"]]
    plt.barh(top_features["feature"], top_features["odds_ratio"], color=colors, height=0.65)
    plt.axvline(1.0, color="#1e293b", linestyle="--", lw=1.5, label="Baseline Odds = 1.0")
    plt.xlabel("Odds Ratio (exp(coef))", fontsize=12, labelpad=10)
    plt.title("Key Predictors of Product Return (Odds Ratios)", fontsize=14, fontweight="bold", pad=15)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "odds_ratios_top15.png"))
    plt.close()
    
    print(f"Model evaluation figures saved to: {figures_dir}")
    
    return pipeline_lr, df_coefficients

if __name__ == "__main__":
    train_return_prediction_model()
