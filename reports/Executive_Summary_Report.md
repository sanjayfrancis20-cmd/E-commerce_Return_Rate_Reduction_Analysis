# Executive Analytics Report: E-Commerce Return Rate Reduction

## Executive Summary
This project provides an end-to-end data science and business intelligence framework to identify why customers return products and how return rates vary by category, geography, marketing channel, and supplier.

Across **25,000 transaction orders** evaluated in 2025:
- **Total Orders Analyzed:** 25,000
- **Total Returned Orders:** 8,287
- **Global Return Rate:** 33.15%
- **Gross Sales Amount:** $3,398,500.00
- **Total Refunded Amount:** $1,135,673.00 (33.42% of total revenue)
- **High-Risk SKUs Identified:** 41 products with predicted return risks between 40% and 62%
- **Machine Learning Model:** Penalized Logistic Regression (ROC-AUC = 0.6980, Accuracy = 70.28%) with odds ratio interpretability

---

## 1. Key Dimensions Analysis

### 1.1 Category Performance
| Product Category | Total Orders | Returns | Return Rate (%) | Gross Sales ($) | Refunded Sales ($) | Revenue Lost (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Apparel & Fashion** | 4,256 | 2,290 | **53.81%** | $438,281.85 | $231,874.06 | 52.91% |
| **Footwear** | 4,085 | 1,759 | **43.06%** | $640,844.20 | $271,644.65 | 42.39% |
| **Electronics** | 4,114 | 1,315 | **31.96%** | $809,516.37 | $257,180.07 | 31.77% |
| **Home & Furniture** | 4,234 | 1,229 | **29.03%** | $698,858.66 | $196,781.31 | 28.16% |
| **Sports & Outdoors** | 4,217 | 1,064 | **25.23%** | $559,608.55 | $138,980.19 | 24.84% |
| **Beauty & Personal Care** | 4,094 | 630 | **15.39%** | $254,210.26 | $39,212.33 | 15.43% |

*Insight:* Apparel and Footwear account for **$503,518.71 (44.3%)** of all refunded dollars. Their primary return drivers are fit, sizing tightness, and fabric feel mismatch.

---

### 1.2 Supplier Breakdown
| Supplier | Country | Quality Score | Declared Defect % | Total Orders | Return Rate (%) | Total Refunded ($) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Apex Fashion Mills** | Vietnam | 7.1 | 8.0% | 2,295 | **58.56%** | $145,582.61 |
| **Stride Footwear Co** | Indonesia | 7.4 | 7.0% | 1,849 | **48.73%** | $131,837.65 |
| **Nordic Weave Textiles** | Portugal | 9.2 | 3.0% | 1,961 | **48.24%** | $86,291.45 |
| **Heritage Leathercraft** | Italy | 9.5 | 2.0% | 2,236 | **38.37%** | $139,807.00 |
| **Nova Tech Gadgets** | China | 6.8 | 9.0% | 1,647 | **37.22%** | $121,672.33 |
| **Terra Home & Decor** | India | 8.3 | 5.0% | 4,234 | **29.03%** | $196,781.31 |
| **Zenith Electronic Works** | Taiwan | 8.9 | 4.0% | 2,467 | **28.46%** | $135,507.74 |
| **Summit Outdoor Gear** | Cambodia | 8.1 | 5.0% | 4,217 | **25.23%** | $138,980.19 |
| **Aura Cosmetics Lab** | South Korea | 9.4 | 2.0% | 1,424 | **15.45%** | $12,241.14 |
| **PureGlow Botanicals** | USA | 9.8 | 1.0% | 2,670 | **15.36%** | $26,971.19 |

*Insight:* Apex Fashion Mills and Stride Footwear suffer from elevated defect rates and sizing inconsistencies, generating return rates nearly 4x higher than cosmetics vendors.

---

### 1.3 Marketing Acquisition Channels
| Channel | Orders | Returns | Return Rate (%) | Avg Discount % | AOV ($) | Refund Amount ($) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Paid Social** | 7,033 | 2,692 | **38.28%** | 9.86% | $138.79 | $387,561.08 |
| **Affiliate / Influencer** | 2,474 | 905 | **36.58%** | 10.02% | $131.65 | $120,308.14 |
| **Paid Search** | 5,969 | 1,941 | **32.52%** | 9.87% | $134.51 | $255,515.31 |
| **Organic Search** | 4,516 | 1,375 | **30.45%** | 10.25% | $137.89 | $189,259.97 |
| **Email Marketing** | 2,997 | 863 | **28.80%** | 10.28% | $134.66 | $115,214.60 |
| **Direct** | 2,011 | 511 | **25.41%** | 9.51% | $134.44 | $67,813.51 |

*Insight:* Paid Social and Influencer traffic demonstrate high impulse buying with lower intent, driving over $507K in returns.

---

### 1.4 Geography & Logistics Lag
| Region | Orders | Returns | Return Rate (%) | Avg Delivery (Days) | Avg Delay (Days) | Delayed Orders (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **West** | 9,348 | 3,412 | **36.50%** | 5.17 | +1.83 | **71.22%** |
| **Northeast** | 5,631 | 1,834 | **32.57%** | 4.37 | +1.05 | **50.22%** |
| **South** | 6,778 | 2,057 | **30.35%** | 4.03 | +0.72 | **40.01%** |
| **Midwest** | 3,243 | 984 | **30.34%** | 4.01 | +0.72 | **39.56%** |

*Insight:* Transit bottlenecks in the West (including Alaska, Washington, and Montana) increase delivery delays by nearly 2 days, causing a direct 6.2 percentage point spike in return rates.

---

## 2. Machine Learning Predictive Model

### 2.1 Model Architecture & Evaluation
- **Algorithm:** L2-regularized Logistic Regression (with Standard Scaler & One-Hot Encoding)
- **Train / Test Split:** 80% / 20% Stratified (20,000 train / 5,000 test)
- **Evaluation Metrics:**
  - **ROC-AUC Score:** `0.6980`
  - **Precision-Recall AUC:** `0.5379`
  - **Overall Accuracy:** `70.28%`
  - **Brier Score Calibration Loss:** `0.1970`
  - **Benchmark Gradient Boosting ROC-AUC:** `0.6954` (Logistic Regression offers comparable predictive performance with superior interpretability).

### 2.2 Top Predictors & Odds Ratios
| Feature | Coefficient | Odds Ratio | Impact on Return Probability |
| :--- | :---: | :---: | :--- |
| `category_Beauty & Personal Care` | -1.904 | **0.149** | -85% lower odds of return vs Apparel |
| `category_Sports & Outdoors` | -1.276 | **0.279** | -72% lower odds of return vs Apparel |
| `category_Home & Furniture` | -1.055 | **0.348** | -65% lower odds of return vs Apparel |
| `category_Electronics` | -0.962 | **0.382** | -62% lower odds of return vs Apparel |
| `marketing_channel_Direct` | -0.540 | **0.583** | -42% lower odds vs Paid Social |
| `payment_method_Klarna / BNPL` | +0.434 | **1.543** | **+54.3% increase in return odds** |
| `delivery_delay_days` | +0.266 | **1.304** | **+30.4% increase per standard delay unit** |
| `customer_historical_return_rate`| +0.211 | **1.235** | **+23.5% return odds multiplier** |

---

## 3. High-Risk Products Catalog & CSV Deliverable
The prediction pipeline identified **41 high-risk SKUs** having expected return risks $\ge 40\%$. The top 5 highest risk products are:

1. **`PRD-1009` (T-Shirts & Tops Model A)**: 50.52% actual return rate | 54.80% predicted risk | Primary Reason: *Fit - Too Small*
2. **`PRD-1001` (Dresses Model A)**: 61.21% actual return rate | 54.70% predicted risk | Primary Reason: *Fit - Too Large*
3. **`PRD-1007` (Jeans & Denim Model C)**: 59.13% actual return rate | 54.60% predicted risk | Primary Reason: *Fit - Too Small*
4. **`PRD-1006` (Jeans & Denim Model B)**: 48.86% actual return rate | 54.52% predicted risk | Primary Reason: *Fit - Too Large*
5. **`PRD-1002` (Dresses Model B)**: 60.44% actual return rate | 54.52% predicted risk | Primary Reason: *Fit - Too Small*

Full export is available in `deliverables/high_risk_products.csv`.

---

## 4. Deliverables Checklist
- [x] **Python Codebase for Prediction:**
  - `src/data_generator.py` (relational e-commerce dataset generator)
  - `src/data_cleaner.py` (ETL, SQLite database, and Star Schema builder)
  - `src/sql_analytics.py` (SQL execution engine)
  - `src/model_training.py` (Logistic Regression ML training & evaluation)
  - `src/predict_risk.py` (Inference pipeline & risk scoring)
  - `src/eda_visualizations.py` (Figure generation)
  - `run_pipeline.py` (One-click master runner)
- [x] **CSV of High-Risk Products:**
  - `deliverables/high_risk_products.csv`
  - `deliverables/order_return_risk_scores.csv`
- [x] **Interactive Dashboard with Drill-Through Filters:**
  - Live Web Dashboard (`dashboard/index.html`, `style.css`, `app.js`) with dynamic recalculation, search, sort, and modal inspection.
  - Power BI Star Schema datasets (`data/processed/powerbi_star_schema/`)
  - Power BI DAX Measures (`powerbi/powerbi_measures.dax`)
  - Power BI Design & Modeling Guide (`powerbi/README_POWERBI_SETUP.md`)
