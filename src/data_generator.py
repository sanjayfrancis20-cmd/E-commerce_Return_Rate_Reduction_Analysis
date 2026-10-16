"""
Data Generator for E-commerce Return Rate Reduction Analysis.
Generates realistic multi-table relational dataset:
- Suppliers
- Products
- Customers
- Orders
- Returns
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)

def generate_ecommerce_data(num_orders=25000, start_date="2025-01-01", end_date="2025-12-31", output_dir="data/raw"):
    set_seed(42)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Suppliers
    suppliers_data = [
        {"supplier_id": "SUP-101", "supplier_name": "Apex Fashion Mills", "country": "Vietnam", "defect_rate": 0.08, "quality_score": 7.1},
        {"supplier_id": "SUP-102", "supplier_name": "Nordic Weave Textiles", "country": "Portugal", "defect_rate": 0.03, "quality_score": 9.2},
        {"supplier_id": "SUP-103", "supplier_name": "Zenith Electronic Works", "country": "Taiwan", "defect_rate": 0.04, "quality_score": 8.9},
        {"supplier_id": "SUP-104", "supplier_name": "Nova Tech Gadgets", "country": "China", "defect_rate": 0.09, "quality_score": 6.8},
        {"supplier_id": "SUP-105", "supplier_name": "Heritage Leathercraft", "country": "Italy", "defect_rate": 0.02, "quality_score": 9.5},
        {"supplier_id": "SUP-106", "supplier_name": "Stride Footwear Co", "country": "Indonesia", "defect_rate": 0.07, "quality_score": 7.4},
        {"supplier_id": "SUP-107", "supplier_name": "Terra Home & Decor", "country": "India", "defect_rate": 0.05, "quality_score": 8.3},
        {"supplier_id": "SUP-108", "supplier_name": "PureGlow Botanicals", "country": "USA", "defect_rate": 0.01, "quality_score": 9.8},
        {"supplier_id": "SUP-109", "supplier_name": "Aura Cosmetics Lab", "country": "South Korea", "defect_rate": 0.02, "quality_score": 9.4},
        {"supplier_id": "SUP-110", "supplier_name": "Summit Outdoor Gear", "country": "Cambodia", "defect_rate": 0.05, "quality_score": 8.1},
    ]
    df_suppliers = pd.DataFrame(suppliers_data)
    
    # 2. Products
    categories = {
        "Apparel & Fashion": {
            "subcategories": ["Dresses", "Jeans & Denim", "T-Shirts & Tops", "Outerwear & Jackets", "Activewear"],
            "base_return_propensity": 0.28,
            "suppliers": ["SUP-101", "SUP-102"],
            "price_range": (29.0, 180.0)
        },
        "Footwear": {
            "subcategories": ["Running Shoes", "Formal Shoes", "Boots", "Sandals", "Sneakers"],
            "base_return_propensity": 0.22,
            "suppliers": ["SUP-105", "SUP-106"],
            "price_range": (45.0, 220.0)
        },
        "Electronics": {
            "subcategories": ["Wireless Audio", "Smartwatches", "Phone Accessories", "Tablets", "Smart Home"],
            "base_return_propensity": 0.14,
            "suppliers": ["SUP-103", "SUP-104"],
            "price_range": (35.0, 450.0)
        },
        "Home & Furniture": {
            "subcategories": ["Bedding & Linens", "Accent Rugs", "Kitchen Appliances", "Lighting", "Wall Decor"],
            "base_return_propensity": 0.12,
            "suppliers": ["SUP-107"],
            "price_range": (25.0, 320.0)
        },
        "Beauty & Personal Care": {
            "subcategories": ["Skincare Sets", "Serums & Oils", "Hair Styling Tools", "Fragrances", "Makeup Palettes"],
            "base_return_propensity": 0.05,
            "suppliers": ["SUP-108", "SUP-109"],
            "price_range": (18.0, 110.0)
        },
        "Sports & Outdoors": {
            "subcategories": ["Yoga Equipment", "Camping Essentials", "Hydration Packs", "Fitness Trackers", "Cycling Gear"],
            "base_return_propensity": 0.09,
            "suppliers": ["SUP-110"],
            "price_range": (22.0, 210.0)
        }
    }
    
    products_list = []
    prod_counter = 1001
    
    for cat_name, cat_info in categories.items():
        for subcat in cat_info["subcategories"]:
            for item_idx in range(1, 5): # 4 products per subcategory = 120 products total
                p_id = f"PRD-{prod_counter}"
                prod_counter += 1
                supplier = random.choice(cat_info["suppliers"])
                price = round(random.uniform(cat_info["price_range"][0], cat_info["price_range"][1]), 2)
                cost = round(price * random.uniform(0.35, 0.55), 2)
                # Specific risk factors (e.g. sizing complexity, fragile, technical setup)
                sizing_sensitive = 1 if cat_name in ["Apparel & Fashion", "Footwear"] else 0
                products_list.append({
                    "product_id": p_id,
                    "product_name": f"{subcat} Model {chr(64 + item_idx)}",
                    "category": cat_name,
                    "subcategory": subcat,
                    "supplier_id": supplier,
                    "unit_price": price,
                    "cost_price": cost,
                    "sizing_sensitive": sizing_sensitive,
                    "base_return_risk": cat_info["base_return_propensity"]
                })
    df_products = pd.DataFrame(products_list)
    
    # 3. Customers
    us_states = [
        {"state": "California", "state_code": "CA", "region": "West", "delivery_lag_bias": 0},
        {"state": "New York", "state_code": "NY", "region": "Northeast", "delivery_lag_bias": 0},
        {"state": "Texas", "state_code": "TX", "region": "South", "delivery_lag_bias": 0},
        {"state": "Florida", "state_code": "FL", "region": "South", "delivery_lag_bias": 0},
        {"state": "Illinois", "state_code": "IL", "region": "Midwest", "delivery_lag_bias": 0},
        {"state": "Washington", "state_code": "WA", "region": "West", "delivery_lag_bias": 1},
        {"state": "Colorado", "state_code": "CO", "region": "West", "delivery_lag_bias": 1},
        {"state": "Georgia", "state_code": "GA", "region": "South", "delivery_lag_bias": 0},
        {"state": "Pennsylvania", "state_code": "PA", "region": "Northeast", "delivery_lag_bias": 0},
        {"state": "Ohio", "state_code": "OH", "region": "Midwest", "delivery_lag_bias": 0},
        {"state": "Montana", "state_code": "MT", "region": "West", "delivery_lag_bias": 3}, # Remote
        {"state": "Alaska", "state_code": "AK", "region": "West", "delivery_lag_bias": 4}, # High transit delay
        {"state": "Maine", "state_code": "ME", "region": "Northeast", "delivery_lag_bias": 2},
    ]
    
    num_customers = 5000
    customer_list = []
    segments = ["Frequent Shopper", "Occasional Buyer", "Discount Hunter", "First-Time Buyer", "VIP Member"]
    segment_weights = [0.25, 0.35, 0.20, 0.12, 0.08]
    
    for c_idx in range(1, num_customers + 1):
        st = random.choices(us_states, weights=[0.18, 0.14, 0.12, 0.10, 0.08, 0.06, 0.05, 0.05, 0.05, 0.05, 0.04, 0.04, 0.04])[0]
        seg = random.choices(segments, weights=segment_weights)[0]
        tenure_months = random.randint(1, 48)
        
        # prior returns history
        if seg == "Discount Hunter":
            prior_orders = random.randint(2, 20)
            prior_returns = int(prior_orders * random.uniform(0.20, 0.45))
        elif seg == "VIP Member":
            prior_orders = random.randint(10, 50)
            prior_returns = int(prior_orders * random.uniform(0.05, 0.15))
        elif seg == "First-Time Buyer":
            prior_orders = 1
            prior_returns = 0
        else:
            prior_orders = random.randint(2, 15)
            prior_returns = int(prior_orders * random.uniform(0.08, 0.25))
            
        customer_list.append({
            "customer_id": f"CUST-{10000 + c_idx}",
            "customer_segment": seg,
            "customer_tenure_months": tenure_months,
            "state": st["state"],
            "state_code": st["state_code"],
            "region": st["region"],
            "delivery_lag_bias": st["delivery_lag_bias"],
            "prior_orders_count": prior_orders,
            "prior_returns_count": prior_returns,
            "historical_return_rate": round(prior_returns / max(1, prior_orders), 3)
        })
    df_customers = pd.DataFrame(customer_list)
    
    # 4. Orders & Returns Generation
    channels = ["Paid Social", "Paid Search", "Organic Search", "Email Marketing", "Affiliate / Influencer", "Direct"]
    channel_weights = [0.28, 0.24, 0.18, 0.12, 0.10, 0.08]
    # Channels have varying return tendencies: Paid Social / Affiliate have higher impulse buying
    channel_risk_multiplier = {
        "Paid Social": 1.35,
        "Affiliate / Influencer": 1.25,
        "Paid Search": 1.00,
        "Organic Search": 0.90,
        "Email Marketing": 0.75,
        "Direct": 0.65
    }
    
    payment_methods = ["Credit Card", "PayPal", "Apple Pay / Google Pay", "Klarna / Buy Now Pay Later", "Debit Card"]
    payment_weights = [0.45, 0.20, 0.15, 0.12, 0.08]
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    date_range_days = (end_dt - start_dt).days
    
    orders = []
    returns = []
    return_counter = 50001
    
    # Pre-index tables for speed
    prod_dict = df_products.set_index("product_id").to_dict("index")
    cust_dict = df_customers.set_index("customer_id").to_dict("index")
    supp_dict = df_suppliers.set_index("supplier_id").to_dict("index")
    
    prod_ids = list(prod_dict.keys())
    cust_ids = list(cust_dict.keys())
    
    for i in range(1, num_orders + 1):
        order_id = f"ORD-{20250000 + i}"
        ord_date = start_dt + timedelta(days=random.randint(0, date_range_days))
        cust_id = random.choice(cust_ids)
        cust = cust_dict[cust_id]
        
        prod_id = random.choice(prod_ids)
        prod = prod_dict[prod_id]
        supp = supp_dict[prod["supplier_id"]]
        
        channel = random.choices(channels, weights=channel_weights)[0]
        payment = random.choices(payment_methods, weights=payment_weights)[0]
        
        # Discounts
        if cust["customer_segment"] == "Discount Hunter":
            discount_pct = round(random.choice([0.15, 0.20, 0.25, 0.35, 0.50]), 2)
        elif random.random() < 0.40:
            discount_pct = round(random.choice([0.05, 0.10, 0.15, 0.20]), 2)
        else:
            discount_pct = 0.0
            
        quantity = random.choices([1, 2, 3], weights=[0.82, 0.14, 0.04])[0]
        gross_amount = round(prod["unit_price"] * quantity, 2)
        discount_amount = round(gross_amount * discount_pct, 2)
        net_amount = round(gross_amount - discount_amount, 2)
        
        # Shipping and delivery
        shipping_type = random.choices(["Standard Ground", "Express 2-Day", "Next-Day Air"], weights=[0.70, 0.22, 0.08])[0]
        promised_days = 2 if shipping_type == "Express 2-Day" else (1 if shipping_type == "Next-Day Air" else 4)
        
        # Actual transit days influenced by state bias & randomness
        transit_delay = int(cust["delivery_lag_bias"] + int(np.random.choice([0, 1, 2, 3, 5], p=[0.60, 0.22, 0.10, 0.05, 0.03])))
        actual_delivery_days = int(promised_days + transit_delay)
        is_delayed = 1 if actual_delivery_days > promised_days else 0
        delivery_date = ord_date + timedelta(days=actual_delivery_days)
        
        # CALCULATE PROBABILITY OF RETURN based on authentic business factors:
        # Base probability from product category
        prob = prod["base_return_risk"]
        
        # Channel influence
        prob *= channel_risk_multiplier[channel]
        
        # Supplier quality penalty / bonus
        prob += (supp["defect_rate"] * 1.5)
        
        # Sizing sensitivity: apparel/footwear with discounts has higher return rate
        if prod["sizing_sensitive"] == 1:
            prob *= 1.15
            
        # Heavy discount impact (impulse buying and poor fit)
        if discount_pct >= 0.30:
            prob *= 1.25
        elif discount_pct > 0.15:
            prob *= 1.10
            
        # Delivery delay impact (buyer frustration, missed occasions)
        if is_delayed:
            prob += (0.04 * (actual_delivery_days - promised_days))
            
        # Customer historical return behavior
        prob += (cust["historical_return_rate"] * 0.25)
        
        # BNPL (Buy Now Pay Later / Klarna) increases returns due to zero upfront friction
        if payment == "Klarna / Buy Now Pay Later":
            prob *= 1.20
            
        # Bound probability between 0.01 and 0.85
        prob = max(0.01, min(0.85, prob))
        
        # Determine actual return status
        is_returned = 1 if random.random() < prob else 0
        
        orders.append({
            "order_id": order_id,
            "order_date": ord_date.strftime("%Y-%m-%d"),
            "customer_id": cust_id,
            "product_id": prod_id,
            "quantity": quantity,
            "unit_price": prod["unit_price"],
            "discount_percent": discount_pct,
            "discount_amount": discount_amount,
            "net_amount": net_amount,
            "marketing_channel": channel,
            "payment_method": payment,
            "shipping_type": shipping_type,
            "promised_delivery_days": promised_days,
            "actual_delivery_days": actual_delivery_days,
            "delivery_delay_days": max(0, actual_delivery_days - promised_days),
            "is_delayed": is_delayed,
            "is_returned": is_returned
        })
        
        if is_returned:
            return_id = f"RET-{return_counter}"
            return_counter += 1
            # Return date typically 3 to 18 days after delivery
            ret_date = delivery_date + timedelta(days=random.randint(2, 16))
            
            # Select root cause / reason based on category and supplier defect
            cat = prod["category"]
            if cat == "Apparel & Fashion":
                reasons = ["Fit - Too Small", "Fit - Too Large", "Style/Fabric not as pictured", "Changed Mind", "Quality Defect"]
                r_weights = [0.38, 0.32, 0.15, 0.10, 0.05]
            elif cat == "Footwear":
                reasons = ["Sizing - Too Narrow/Tight", "Sizing - Too Loose", "Uncomfortable Fit", "Color mismatch", "Quality Defect"]
                r_weights = [0.40, 0.30, 0.18, 0.07, 0.05]
            elif cat == "Electronics":
                reasons = ["Defective / Not Functioning", "Missing Accessories", "Hard to configure / setup", "Did not meet expectations", "Arrived Damaged"]
                r_weights = [0.42, 0.18, 0.15, 0.15, 0.10]
            elif cat == "Home & Furniture":
                reasons = ["Arrived Damaged in Transit", "Dimensions did not fit space", "Color/Texture mismatch", "Parts missing", "Buyer Remorse"]
                r_weights = [0.35, 0.25, 0.20, 0.12, 0.08]
            elif cat == "Beauty & Personal Care":
                reasons = ["Skin Irritation / Reaction", "Scent / Color not liked", "Damaged / Leaking bottle", "Wrong product sent", "Changed Mind"]
                r_weights = [0.35, 0.30, 0.18, 0.10, 0.07]
            else: # Sports & Outdoors
                reasons = ["Quality lower than expected", "Incorrect sizing / grip", "Defective part", "Found better price elsewhere", "Changed Mind"]
                r_weights = [0.35, 0.25, 0.15, 0.15, 0.10]
                
            return_reason = random.choices(reasons, weights=r_weights)[0]
            return_status = random.choices(["Refunded", "Replacement Sent", "Store Credit Issued"], weights=[0.75, 0.15, 0.10])[0]
            item_condition = random.choices(["Like New / Resellable", "Opened / Restockable with Discount", "Damaged / Salvage / Scrap"], weights=[0.60, 0.25, 0.15])[0]
            
            returns.append({
                "return_id": return_id,
                "order_id": order_id,
                "return_date": ret_date.strftime("%Y-%m-%d"),
                "return_reason": return_reason,
                "return_status": return_status,
                "refund_amount": net_amount,
                "item_condition": item_condition
            })

    df_orders = pd.DataFrame(orders)
    df_returns = pd.DataFrame(returns)
    
    # Save raw datasets
    df_suppliers.to_csv(os.path.join(output_dir, "suppliers_raw.csv"), index=False)
    df_products.to_csv(os.path.join(output_dir, "products_raw.csv"), index=False)
    df_customers.to_csv(os.path.join(output_dir, "customers_raw.csv"), index=False)
    df_orders.to_csv(os.path.join(output_dir, "orders_raw.csv"), index=False)
    df_returns.to_csv(os.path.join(output_dir, "returns_raw.csv"), index=False)
    
    print(f"Data Generation Completed successfully:")
    print(f" - Suppliers: {len(df_suppliers)}")
    print(f" - Products: {len(df_products)}")
    print(f" - Customers: {len(df_customers)}")
    print(f" - Orders: {len(df_orders)} (Return Rate: {df_orders['is_returned'].mean():.2%})")
    print(f" - Returns: {len(df_returns)}")

if __name__ == "__main__":
    generate_ecommerce_data()
