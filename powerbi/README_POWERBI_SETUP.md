# Power BI Return Risk Score Dashboard Setup Guide

This guide walks you through building the interactive **Return Risk Score Dashboard** in Power BI Desktop using the pre-modeled Star Schema datasets.

---

## 1. Data Model Architecture (Star Schema)

The datasets are located in `data/processed/powerbi_star_schema/`:

| Table Name | File | Role | Key Join |
| :--- | :--- | :--- | :--- |
| **`fact_orders_scored`** | `fact_orders_scored.csv` | Fact Table | Primary transaction & predictive risk fact table |
| **`dim_products`** | `dim_products.csv` | Dimension | `product_id` (1-to-Many with Fact) |
| **`dim_suppliers`** | `dim_suppliers.csv` | Dimension | `supplier_id` (1-to-Many with Fact) |
| **`dim_customers`** | `dim_customers.csv` | Dimension | `customer_id` (1-to-Many with Fact) |
| **`dim_dates`** | `dim_dates.csv` | Dimension | `date_key` -> `order_date` (1-to-Many with Fact) |

### Relationship Diagram
```
   [dim_dates] (1) ------------ (*) [fact_orders_scored] (*) ------------ (1) [dim_products]
                                              |                                       |
                                              |                                       |
                                             (*)                                     (1)
                                      [dim_customers]                          [dim_suppliers]
```
*(All cross-filter directions set to Single: Dimension filters Fact).*

---

## 2. Step-by-Step Power BI Setup

### Step A: Load the Data
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Import each file from `data/processed/powerbi_star_schema/`:
   - `fact_orders_scored.csv`
   - `dim_products.csv`
   - `dim_suppliers.csv`
   - `dim_customers.csv`
   - `dim_dates.csv`
4. In Power Query, verify column data types (`order_date` as Date, numerical rates as Decimals, etc.), then click **Close & Apply**.

### Step B: Wire Relationships
1. Go to the **Model view** (left sidebar icon).
2. Create active relationships:
   - `dim_products[product_id]` -> `fact_orders_scored[product_id]`
   - `dim_suppliers[supplier_id]` -> `fact_orders_scored[supplier_id]`
   - `dim_customers[customer_id]` -> `fact_orders_scored[customer_id]`
   - `dim_dates[date_key]` -> `fact_orders_scored[order_date]`

### Step C: Create Measures
1. Right-click on `fact_orders_scored` in the Data pane -> **New measure**.
2. Copy and paste the DAX formulas from `powerbi/powerbi_measures.dax` (e.g., `Return Rate %`, `Gross Revenue`, `Avg Predicted Return Risk %`, `Total Expected Refund Loss`).

---

## 3. Recommended 3-Page Dashboard Layout

### Page 1: Executive Return Overview
- **Top KPI Cards**:
  - Total Orders (`Total Orders`)
  - Total Returns (`Total Returned Orders`)
  - Actual Return Rate (`Return Rate %`) — with dynamic red/green conditional color
  - Revenue Lost to Returns (`Total Refunded Amount`)
  - Predicted Return Risk (`Avg Predicted Return Risk %`)
- **Top Visuals**:
  - Clustered Bar Chart: `Return Rate %` by `dim_products[category]`
  - Horizontal Bar Chart: `Return Rate %` and `Declared Defect %` by `dim_suppliers[supplier_name]`
  - Donut Chart: Orders by `risk_tier` (High / Medium / Low)
  - Slicers: Date Range, Region, Marketing Channel

### Page 2: Root-Cause & Logistics Deep Dive
- Matrix / Heatmap: Category vs Return Reason count & % share.
- Scatter Plot: `Avg Delivery Delay Days` (X-axis) vs `Return Rate %` (Y-axis), bubble size = `Total Orders`.
- Stacked Column Chart: Return Rate by `marketing_channel` split by `payment_method` (showing Klarna/BNPL surge).

### Page 3: High-Risk SKU Drill-Through Table
- Configure **Drill-Through Filter**: Set `dim_products[product_id]` or `dim_products[category]` as drill-through fields.
- **Table Visual**:
  - `product_id`
  - `product_name`
  - `category`
  - `supplier_name`
  - `Return Rate %`
  - `Avg Predicted Return Risk %`
  - `Total Expected Refund Loss`
  - Primary Return Reason
  - Actionable mitigation badge
