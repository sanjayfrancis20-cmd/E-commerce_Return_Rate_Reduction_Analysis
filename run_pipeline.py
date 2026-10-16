"""
Master End-to-End Orchestrator Pipeline:
Executes the full workflow:
1. Data Generation (Multi-table raw relational e-commerce data)
2. Data Cleaning & Star Schema Transformation
3. SQL Database Ingestion & Analytics
4. Logistic Regression Machine Learning Training & Evaluation
5. Prediction & Risk Scoring (Generates CSV deliverables)
6. EDA Visualizations & Figures Export
7. Dashboard Data Export
"""

import sys
import time
from src.data_generator import generate_ecommerce_data
from src.data_cleaner import clean_and_prepare_data
from src.sql_analytics import run_sql_analytics
from src.model_training import train_return_prediction_model
from src.predict_risk import generate_risk_predictions
from src.eda_visualizations import generate_eda_figures
from src.export_dashboard_data import export_dashboard_json

def main():
    start_time = time.time()
    print("=" * 80)
    print("STARTING E-COMMERCE RETURN RATE REDUCTION ANALYSIS PIPELINE")
    print("=" * 80)
    
    # Step 1: Data Generation
    print("\n[STEP 1/7] Generating synthetic raw relational e-commerce dataset...")
    generate_ecommerce_data(num_orders=25000)
    
    # Step 2: Data Cleaning & Star Schema
    print("\n[STEP 2/7] Cleaning data, populating SQLite DB, and creating Star Schema...")
    clean_and_prepare_data()
    
    # Step 3: SQL Analytics
    print("\n[STEP 3/7] Running core SQL analytics queries...")
    run_sql_analytics()
    
    # Step 4: Model Training
    print("\n[STEP 4/7] Training Logistic Regression prediction model...")
    train_return_prediction_model()
    
    # Step 5: Risk Scoring & Deliverables
    print("\n[STEP 5/7] Scoring orders and generating high-risk products CSV deliverables...")
    generate_risk_predictions()
    
    # Step 6: EDA Visualizations
    print("\n[STEP 6/7] Exporting high-resolution analytics figures...")
    generate_eda_figures()
    
    # Step 7: Dashboard Export
    print("\n[STEP 7/7] Exporting web dashboard payload...")
    export_dashboard_json()
    
    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 80)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed} SECONDS!")
    print("=" * 80)

if __name__ == "__main__":
    main()
