"""
Data Preparation & Feature Engineering Script
Customer Churn & Category Profitability Analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("DATA PREPARATION & FEATURE ENGINEERING")
print("="*80)
print(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load all datasets
print("Loading datasets...")
customers = pd.read_csv('Data/customers.csv')
transactions = pd.read_csv('Data/transactions.csv')
products = pd.read_csv('Data/products.csv')
web_sessions = pd.read_csv('Data/web_sessions.csv')
stores = pd.read_csv('Data/stores.csv')

# Convert dates
customers['signup_date'] = pd.to_datetime(customers['signup_date'])
transactions['date'] = pd.to_datetime(transactions['date'])
products['launch_date'] = pd.to_datetime(products['launch_date'])
web_sessions['date'] = pd.to_datetime(web_sessions['date'])

print("[OK] Datasets loaded\n")

# ============================================================================
# STEP 1: DATA CLEANING
# ============================================================================
print("="*80)
print("STEP 1: DATA CLEANING")
print("="*80)

# Set reference date (latest transaction date)
reference_date = transactions['date'].max()
print(f"\nReference Date: {reference_date}")

# Clean customers dataset
print("\nCleaning customers dataset...")
# Handle missing age_band - fill with 'Unknown'
customers['age_band'] = customers['age_band'].fillna('Unknown')
print(f"  - Filled {customers['age_band'].isna().sum()} missing age_band values")

# Clean transactions dataset
print("\nCleaning transactions dataset...")
# Remove transactions with missing customer_id
txn_before = len(transactions)
transactions = transactions[transactions['customer_id'].notna()]
print(f"  - Removed {txn_before - len(transactions)} transactions with missing customer_id")

# Clean web_sessions dataset
print("\nCleaning web_sessions dataset...")
# Remove sessions with missing customer_id
web_before = len(web_sessions)
web_sessions = web_sessions[web_sessions['customer_id'].notna()]
print(f"  - Removed {web_before - len(web_sessions)} sessions with missing customer_id")

print("\n[OK] Data cleaning complete")

# ============================================================================
# STEP 2: MERGE DATASETS & CREATE MASTER DATASET
# ============================================================================
print("\n" + "="*80)
print("STEP 2: CREATING MASTER DATASET")
print("="*80)

# Merge transactions with products
print("\nMerging transactions with products...")
transactions_enriched = transactions.merge(
    products[['product_id', 'category', 'subcategory']],
    on='product_id',
    how='left'
)
print(f"  - Merged {len(transactions_enriched):,} transactions")

# ============================================================================
# STEP 3: CUSTOMER-LEVEL FEATURE ENGINEERING
# ============================================================================
print("\n" + "="*80)
print("STEP 3: CUSTOMER-LEVEL FEATURE ENGINEERING")
print("="*80)

print("\nCalculating RFM metrics...")

# Recency, Frequency, Monetary (RFM) Analysis
customer_rfm = transactions_enriched.groupby('customer_id').agg({
    'date': ['max', 'min', 'count'],
    'net_amount': ['sum', 'mean'],
    'qty': 'sum',
    'discount_pct': 'mean',
    'product_id': 'nunique',
    'category': 'nunique',
    'subcategory': 'nunique'
}).reset_index()

# Flatten column names
customer_rfm.columns = ['customer_id', 'last_purchase_date', 'first_purchase_date', 
                        'total_transactions', 'total_revenue', 'avg_order_value',
                        'total_items_purchased', 'avg_discount_received',
                        'unique_products', 'unique_categories', 'unique_subcategories']

# Calculate recency (days since last purchase)
customer_rfm['days_since_last_purchase'] = (reference_date - customer_rfm['last_purchase_date']).dt.days

# Calculate customer lifespan
customer_rfm['customer_lifespan_days'] = (customer_rfm['last_purchase_date'] - customer_rfm['first_purchase_date']).dt.days

# Calculate purchase frequency (transactions per month)
customer_rfm['purchase_frequency'] = customer_rfm['total_transactions'] / (customer_rfm['customer_lifespan_days'] / 30 + 1)

print(f"  - Created RFM features for {len(customer_rfm):,} customers")

# Payment method preferences
print("\nCalculating payment preferences...")
payment_prefs = transactions_enriched.groupby('customer_id')['payment_method'].agg(
    lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown'
).reset_index()
payment_prefs.columns = ['customer_id', 'preferred_payment_method']

# Category preferences
print("\nCalculating category preferences...")
category_prefs = transactions_enriched.groupby('customer_id')['category'].agg(
    lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown'
).reset_index()
category_prefs.columns = ['customer_id', 'preferred_category']

# Web engagement metrics
print("\nCalculating web engagement metrics...")
web_engagement = web_sessions.groupby('customer_id').agg({
    'session_id': 'count',
    'pages_viewed': ['sum', 'mean'],
    'cart_abandoned': ['sum', 'mean']
}).reset_index()

web_engagement.columns = ['customer_id', 'total_sessions', 'total_pages_viewed',
                          'avg_pages_per_session', 'total_cart_abandonments',
                          'cart_abandonment_rate']

# Channel preferences
channel_prefs = web_sessions.groupby('customer_id')['channel'].agg(
    lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown'
).reset_index()
channel_prefs.columns = ['customer_id', 'preferred_channel']

print(f"  - Created web engagement features for {len(web_engagement):,} customers")

# ============================================================================
# STEP 4: MERGE ALL CUSTOMER FEATURES
# ============================================================================
print("\n" + "="*80)
print("STEP 4: MERGING ALL FEATURES")
print("="*80)

# Start with customers base
master_df = customers.copy()

# Calculate customer tenure
master_df['customer_tenure_days'] = (reference_date - master_df['signup_date']).dt.days

# Merge RFM features
master_df = master_df.merge(customer_rfm, on='customer_id', how='left')

# Merge payment preferences
master_df = master_df.merge(payment_prefs, on='customer_id', how='left')

# Merge category preferences
master_df = master_df.merge(category_prefs, on='customer_id', how='left')

# Merge web engagement
master_df = master_df.merge(web_engagement, on='customer_id', how='left')

# Merge channel preferences
master_df = master_df.merge(channel_prefs, on='customer_id', how='left')

print(f"\n[OK] Master dataset created with {len(master_df):,} customers and {len(master_df.columns)} features")

# ============================================================================
# STEP 5: HANDLE MISSING VALUES IN FEATURES
# ============================================================================
print("\n" + "="*80)
print("STEP 5: HANDLING MISSING VALUES")
print("="*80)

# Fill missing values for customers with no transactions
transaction_features = ['total_transactions', 'total_revenue', 'avg_order_value',
                        'total_items_purchased', 'avg_discount_received',
                        'unique_products', 'unique_categories', 'unique_subcategories',
                        'customer_lifespan_days', 'purchase_frequency']

for col in transaction_features:
    if col in master_df.columns:
        master_df[col] = master_df[col].fillna(0)

# Fill days_since_last_purchase with max value for customers with no purchases
if 'days_since_last_purchase' in master_df.columns:
    max_days = master_df['days_since_last_purchase'].max()
    master_df['days_since_last_purchase'] = master_df['days_since_last_purchase'].fillna(max_days)

# Fill missing web engagement features
web_features = ['total_sessions', 'total_pages_viewed', 'avg_pages_per_session',
                'total_cart_abandonments', 'cart_abandonment_rate']

for col in web_features:
    if col in master_df.columns:
        master_df[col] = master_df[col].fillna(0)

# Fill missing categorical features
master_df['preferred_payment_method'] = master_df['preferred_payment_method'].fillna('None')
master_df['preferred_category'] = master_df['preferred_category'].fillna('None')
master_df['preferred_channel'] = master_df['preferred_channel'].fillna('None')

print(f"\n[OK] Missing values handled")
print(f"Remaining missing values: {master_df.isnull().sum().sum()}")

# ============================================================================
# STEP 6: CREATE DERIVED FEATURES
# ============================================================================
print("\n" + "="*80)
print("STEP 6: CREATING DERIVED FEATURES")
print("="*80)

# Engagement score (composite metric)
master_df['engagement_score'] = (
    (master_df['total_transactions'] / master_df['total_transactions'].max()) * 0.3 +
    (master_df['total_sessions'] / master_df['total_sessions'].max()) * 0.3 +
    (master_df['avg_pages_per_session'] / master_df['avg_pages_per_session'].max()) * 0.2 +
    (1 - master_df['cart_abandonment_rate']) * 0.2
)

# Customer value score
master_df['customer_value_score'] = (
    (master_df['total_revenue'] / master_df['total_revenue'].max()) * 0.5 +
    (master_df['purchase_frequency'] / master_df['purchase_frequency'].max()) * 0.3 +
    (master_df['unique_products'] / master_df['unique_products'].max()) * 0.2
)

# Discount dependency
master_df['discount_dependency'] = master_df['avg_discount_received'] / (master_df['avg_discount_received'].max() + 1)

# Activity trend (recent vs historical)
master_df['is_active'] = (master_df['days_since_last_purchase'] <= 90).astype(int)
master_df['is_dormant'] = (master_df['days_since_last_purchase'] > 180).astype(int)

# Loyalty tier encoding (ordinal)
loyalty_mapping = {'Bronze': 0, 'Silver': 1, 'Gold': 2, 'Platinum': 3}
master_df['loyalty_tier_encoded'] = master_df['loyalty_tier'].map(loyalty_mapping)

# Age band encoding (ordinal)
age_mapping = {'18-24': 0, '25-34': 1, '35-44': 2, '45-54': 3, '55-64': 4, '65+': 5, 'Unknown': -1}
master_df['age_band_encoded'] = master_df['age_band'].map(age_mapping)

print(f"\n[OK] Created {6} derived features")

# ============================================================================
# STEP 7: SAVE PROCESSED DATA
# ============================================================================
print("\n" + "="*80)
print("STEP 7: SAVING PROCESSED DATA")
print("="*80)

# Save master dataset
master_df.to_csv('Data/processed/master_customer_features.csv', index=False)
print(f"\n[OK] Saved master_customer_features.csv ({len(master_df):,} rows, {len(master_df.columns)} columns)")

# Save transactions with enriched data
transactions_enriched.to_csv('Data/processed/transactions_enriched.csv', index=False)
print(f"[OK] Saved transactions_enriched.csv ({len(transactions_enriched):,} rows)")

# Create feature list for modeling
feature_columns = [
    # RFM features
    'days_since_last_purchase', 'total_transactions', 'total_revenue',
    'avg_order_value', 'total_items_purchased', 'avg_discount_received',
    'unique_products', 'unique_categories', 'unique_subcategories',
    'customer_lifespan_days', 'purchase_frequency',
    # Web engagement
    'total_sessions', 'total_pages_viewed', 'avg_pages_per_session',
    'total_cart_abandonments', 'cart_abandonment_rate',
    # Derived features
    'engagement_score', 'customer_value_score', 'discount_dependency',
    'is_active', 'is_dormant', 'customer_tenure_days',
    # Encoded features
    'loyalty_tier_encoded', 'age_band_encoded'
]

# Create modeling dataset
modeling_df = master_df[['customer_id', 'churn_flag'] + feature_columns].copy()

# Remove any remaining NaN values
modeling_df = modeling_df.fillna(0)

modeling_df.to_csv('Data/processed/churn_modeling_dataset.csv', index=False)
print(f"[OK] Saved churn_modeling_dataset.csv ({len(modeling_df):,} rows, {len(feature_columns)} features)")

# ============================================================================
# STEP 8: PROFITABILITY ANALYSIS DATA PREPARATION
# ============================================================================
print("\n" + "="*80)
print("STEP 8: PROFITABILITY ANALYSIS PREPARATION")
print("="*80)

# Calculate profitability metrics at transaction level
transactions_enriched['gross_profit'] = (transactions_enriched['unit_price'] - transactions_enriched['unit_cost']) * transactions_enriched['qty']
transactions_enriched['net_profit'] = transactions_enriched['net_amount'] - (transactions_enriched['unit_cost'] * transactions_enriched['qty'])
transactions_enriched['gross_margin_pct'] = (transactions_enriched['gross_profit'] / transactions_enriched['gross_amount']) * 100
transactions_enriched['net_margin_pct'] = (transactions_enriched['net_profit'] / transactions_enriched['net_amount']) * 100
transactions_enriched['discount_cost'] = transactions_enriched['gross_amount'] - transactions_enriched['net_amount']

# Add time features for trend analysis
transactions_enriched['year'] = transactions_enriched['date'].dt.year
transactions_enriched['month'] = transactions_enriched['date'].dt.month
transactions_enriched['quarter'] = transactions_enriched['date'].dt.quarter
transactions_enriched['year_month'] = transactions_enriched['date'].dt.to_period('M')

# Category-level profitability aggregation
category_profitability = transactions_enriched.groupby('category').agg({
    'txn_id': 'count',
    'net_amount': 'sum',
    'gross_profit': 'sum',
    'net_profit': 'sum',
    'discount_cost': 'sum',
    'gross_margin_pct': 'mean',
    'net_margin_pct': 'mean',
    'discount_pct': 'mean',
    'qty': 'sum'
}).reset_index()

category_profitability.columns = ['category', 'total_transactions', 'total_revenue',
                                   'total_gross_profit', 'total_net_profit', 'total_discount_cost',
                                   'avg_gross_margin_pct', 'avg_net_margin_pct', 'avg_discount_pct',
                                   'total_units_sold']

# Subcategory-level profitability
subcategory_profitability = transactions_enriched.groupby('subcategory').agg({
    'txn_id': 'count',
    'net_amount': 'sum',
    'gross_profit': 'sum',
    'net_profit': 'sum',
    'discount_cost': 'sum',
    'gross_margin_pct': 'mean',
    'net_margin_pct': 'mean',
    'discount_pct': 'mean',
    'qty': 'sum'
}).reset_index()

subcategory_profitability.columns = ['subcategory', 'total_transactions', 'total_revenue',
                                      'total_gross_profit', 'total_net_profit', 'total_discount_cost',
                                      'avg_gross_margin_pct', 'avg_net_margin_pct', 'avg_discount_pct',
                                      'total_units_sold']

# Time-based profitability trends
monthly_profitability = transactions_enriched.groupby(['year_month', 'category']).agg({
    'net_amount': 'sum',
    'net_profit': 'sum',
    'net_margin_pct': 'mean',
    'discount_pct': 'mean'
}).reset_index()

monthly_profitability.columns = ['year_month', 'category', 'revenue', 'profit', 'margin_pct', 'discount_pct']

# Save profitability datasets
category_profitability.to_csv('Data/processed/category_profitability.csv', index=False)
print(f"\n[OK] Saved category_profitability.csv ({len(category_profitability)} categories)")

subcategory_profitability.to_csv('Data/processed/subcategory_profitability.csv', index=False)
print(f"[OK] Saved subcategory_profitability.csv ({len(subcategory_profitability)} subcategories)")

monthly_profitability.to_csv('Data/processed/monthly_profitability_trends.csv', index=False)
print(f"[OK] Saved monthly_profitability_trends.csv ({len(monthly_profitability)} records)")

# Save updated transactions with profitability metrics
transactions_enriched.to_csv('Data/processed/transactions_with_profitability.csv', index=False)
print(f"[OK] Saved transactions_with_profitability.csv")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("DATA PREPARATION SUMMARY")
print("="*80)

print(f"\nCustomer Features:")
print(f"  - Total customers: {len(master_df):,}")
print(f"  - Total features: {len(master_df.columns)}")
print(f"  - Churn rate: {master_df['churn_flag'].mean()*100:.2f}%")

print(f"\nModeling Dataset:")
print(f"  - Samples: {len(modeling_df):,}")
print(f"  - Features: {len(feature_columns)}")
print(f"  - Target variable: churn_flag")

print(f"\nProfitability Analysis:")
print(f"  - Categories analyzed: {len(category_profitability)}")
print(f"  - Subcategories analyzed: {len(subcategory_profitability)}")
print(f"  - Time periods: {monthly_profitability['year_month'].nunique()}")

print(f"\nTop 5 Most Profitable Categories:")
print(category_profitability.nlargest(5, 'total_net_profit')[['category', 'total_net_profit', 'avg_net_margin_pct']])

print(f"\nTop 5 Least Profitable Subcategories:")
print(subcategory_profitability.nsmallest(5, 'avg_net_margin_pct')[['subcategory', 'avg_net_margin_pct', 'total_revenue']])

print("\n" + "="*80)
print("[OK] DATA PREPARATION COMPLETE!")
print("="*80)
print("\nNext steps:")
print("  1. Run churn prediction model training")
print("  2. Analyze profitability trends")
print("  3. Build Gradio application")

# Made with Bob
