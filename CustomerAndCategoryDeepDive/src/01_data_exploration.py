"""
Data Exploration & Profiling Script
Customer Churn & Category Profitability Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')

print("="*80)
print("DATA EXPLORATION & PROFILING")
print("="*80)
print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load all datasets
print("Loading datasets...\n")

customers = pd.read_csv('Data/customers.csv')
print(f"[OK] Customers: {customers.shape[0]:,} rows, {customers.shape[1]} columns")

transactions = pd.read_csv('Data/transactions.csv')
print(f"[OK] Transactions: {transactions.shape[0]:,} rows, {transactions.shape[1]} columns")

products = pd.read_csv('Data/products.csv')
print(f"[OK] Products: {products.shape[0]:,} rows, {products.shape[1]} columns")

web_sessions = pd.read_csv('Data/web_sessions.csv')
print(f"[OK] Web Sessions: {web_sessions.shape[0]:,} rows, {web_sessions.shape[1]} columns")

stores = pd.read_csv('Data/stores.csv')
print(f"[OK] Stores: {stores.shape[0]:,} rows, {stores.shape[1]} columns")

marketing_spend = pd.read_csv('Data/marketing_spend.csv')
print(f"[OK] Marketing Spend: {marketing_spend.shape[0]:,} rows, {marketing_spend.shape[1]} columns")

print("\n[OK] All datasets loaded successfully!\n")

# Convert date columns
customers['signup_date'] = pd.to_datetime(customers['signup_date'])
transactions['date'] = pd.to_datetime(transactions['date'])
products['launch_date'] = pd.to_datetime(products['launch_date'])
web_sessions['date'] = pd.to_datetime(web_sessions['date'])

# Data Quality Assessment
print("="*80)
print("DATA QUALITY ASSESSMENT")
print("="*80)

def check_missing_values(df, name):
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    missing_df = pd.DataFrame({
        'Missing_Count': missing,
        'Missing_Percentage': missing_pct
    })
    missing_df = missing_df[missing_df['Missing_Count'] > 0]
    
    if len(missing_df) > 0:
        print(f"\n{name} - Missing Values:")
        print(missing_df)
    else:
        print(f"\n{name}: [OK] No missing values")
    
    return missing_df

# Check all datasets
for name, df in [('Customers', customers), ('Transactions', transactions), 
                 ('Products', products), ('Web Sessions', web_sessions),
                 ('Stores', stores), ('Marketing Spend', marketing_spend)]:
    check_missing_values(df, name)

# Churn Analysis
print("\n" + "="*80)
print("CHURN ANALYSIS")
print("="*80)

churn_counts = customers['churn_flag'].value_counts()
churn_pct = customers['churn_flag'].value_counts(normalize=True) * 100

print(f"\nChurn Distribution:")
print(f"  Not Churned (0): {churn_counts[0]:,} ({churn_pct[0]:.2f}%)")
print(f"  Churned (1): {churn_counts[1]:,} ({churn_pct[1]:.2f}%)")
print(f"\nOverall Churn Rate: {churn_pct[1]:.2f}%")

if churn_pct[1] < 30:
    print("[WARNING] Class imbalance detected - will need to address in modeling")

# Churn by demographics
print("\nChurn Rate by Demographics:")

churn_by_age = customers.groupby('age_band')['churn_flag'].agg(['sum', 'count', 'mean'])
churn_by_age['churn_rate'] = churn_by_age['mean'] * 100
print("\nBy Age Band:")
print(churn_by_age[['count', 'sum', 'churn_rate']].rename(columns={'count': 'total', 'sum': 'churned'}))

churn_by_island = customers.groupby('island')['churn_flag'].agg(['sum', 'count', 'mean'])
churn_by_island['churn_rate'] = churn_by_island['mean'] * 100
print("\nBy Island:")
print(churn_by_island[['count', 'sum', 'churn_rate']].rename(columns={'count': 'total', 'sum': 'churned'}))

churn_by_loyalty = customers.groupby('loyalty_tier')['churn_flag'].agg(['sum', 'count', 'mean'])
loyalty_order = ['Bronze', 'Silver', 'Gold', 'Platinum']
churn_by_loyalty = churn_by_loyalty.reindex(loyalty_order)
churn_by_loyalty['churn_rate'] = churn_by_loyalty['mean'] * 100
print("\nBy Loyalty Tier:")
print(churn_by_loyalty[['count', 'sum', 'churn_rate']].rename(columns={'count': 'total', 'sum': 'churned'}))

# Transaction Analysis
print("\n" + "="*80)
print("TRANSACTION ANALYSIS")
print("="*80)

print(f"\nDate Range: {transactions['date'].min()} to {transactions['date'].max()}")
print(f"Total Transactions: {len(transactions):,}")
print(f"Unique Customers: {transactions['customer_id'].nunique():,}")
print(f"Unique Products: {transactions['product_id'].nunique():,}")
print(f"Total Revenue (Gross): ${transactions['gross_amount'].sum():,.2f}")
print(f"Total Revenue (Net): ${transactions['net_amount'].sum():,.2f}")
print(f"Total Discount Given: ${(transactions['gross_amount'] - transactions['net_amount']).sum():,.2f}")
print(f"Average Discount: {transactions['discount_pct'].mean():.2f}%")

print("\nPayment Method Distribution:")
print(transactions['payment_method'].value_counts())

# Product Analysis
print("\n" + "="*80)
print("PRODUCT & CATEGORY ANALYSIS")
print("="*80)

print(f"\nTotal Products: {len(products):,}")
print(f"Categories: {products['category'].nunique()}")
print(f"Subcategories: {products['subcategory'].nunique()}")

print("\nSubcategory Distribution:")
print(products['subcategory'].value_counts())

# Calculate profit margins
products['profit_margin'] = ((products['unit_price'] - products['unit_cost']) / products['unit_price']) * 100

print("\nProfit Margin Statistics:")
print(products['profit_margin'].describe())

print("\nAverage Profit Margin by Subcategory:")
margin_by_subcat = products.groupby('subcategory')['profit_margin'].mean().sort_values()
print(margin_by_subcat)

# Web Engagement Analysis
print("\n" + "="*80)
print("WEB ENGAGEMENT ANALYSIS")
print("="*80)

print(f"\nTotal Sessions: {len(web_sessions):,}")
print(f"Unique Customers: {web_sessions['customer_id'].nunique():,}")
print(f"Average Pages per Session: {web_sessions['pages_viewed'].mean():.2f}")
print(f"Cart Abandonment Rate: {(web_sessions['cart_abandoned'].mean() * 100):.2f}%")

print("\nChannel Distribution:")
print(web_sessions['channel'].value_counts())

print("\nCart Abandonment Rate by Channel:")
abandon_by_channel = web_sessions.groupby('channel')['cart_abandoned'].mean() * 100
print(abandon_by_channel.sort_values(ascending=False))

# Data Integrity Checks
print("\n" + "="*80)
print("DATA INTEGRITY CHECKS")
print("="*80)

txn_customers = set(transactions['customer_id'].unique())
cust_customers = set(customers['customer_id'].unique())
web_customers = set(web_sessions['customer_id'].unique())

print("\nCustomer ID Linkage:")
print(f"  Customers in customers.csv: {len(cust_customers):,}")
print(f"  Customers in transactions.csv: {len(txn_customers):,}")
print(f"  Customers in web_sessions.csv: {len(web_customers):,}")

txn_not_in_cust = txn_customers - cust_customers
web_not_in_cust = web_customers - cust_customers

print(f"  Transactions with missing customer records: {len(txn_not_in_cust):,}")
print(f"  Web sessions with missing customer records: {len(web_not_in_cust):,}")

txn_products = set(transactions['product_id'].unique())
prod_products = set(products['product_id'].unique())

print("\nProduct ID Linkage:")
print(f"  Products in products.csv: {len(prod_products):,}")
print(f"  Products in transactions.csv: {len(txn_products):,}")

txn_not_in_prod = txn_products - prod_products
print(f"  Transactions with missing product records: {len(txn_not_in_prod):,}")

# Validate calculations
transactions['calc_net_amount'] = transactions['gross_amount'] * (1 - transactions['discount_pct'] / 100)
amount_diff = abs(transactions['net_amount'] - transactions['calc_net_amount'])
mismatches = (amount_diff > 0.01).sum()

print("\nTransaction Calculation Validation:")
print(f"  Net amount calculation mismatches: {mismatches:,} ({(mismatches/len(transactions)*100):.2f}%)")

if mismatches == 0:
    print("  [OK] All transaction amounts are correctly calculated")

# Key Insights
print("\n" + "="*80)
print("KEY INSIGHTS")
print("="*80)

churn_rate = customers['churn_flag'].mean() * 100
avg_discount = transactions['discount_pct'].mean()
cart_abandon_rate = web_sessions['cart_abandoned'].mean() * 100

print(f"\n1. CHURN RATE: {churn_rate:.2f}% - {'High' if churn_rate > 25 else 'Moderate' if churn_rate > 15 else 'Low'}")
print(f"   -> Class imbalance: {'Yes - need SMOTE/class weights' if churn_rate < 30 else 'No'}")

highest_churn_age = churn_by_age['churn_rate'].idxmax()
print(f"\n2. DEMOGRAPHICS: Highest churn in {highest_churn_age} age group")

highest_churn_loyalty = churn_by_loyalty['churn_rate'].idxmax()
print(f"   -> {highest_churn_loyalty} tier has highest churn rate")

print(f"\n3. DISCOUNTING: Average discount is {avg_discount:.2f}%")
print(f"   -> Total discount cost: ${(transactions['gross_amount'] - transactions['net_amount']).sum():,.2f}")

lowest_margin_subcat = margin_by_subcat.idxmin()
print(f"\n4. PROFITABILITY: {lowest_margin_subcat} has lowest margin ({margin_by_subcat.min():.2f}%)")

print(f"\n5. WEB ENGAGEMENT: Cart abandonment rate is {cart_abandon_rate:.2f}%")
if cart_abandon_rate > 50:
    print("   -> High abandonment - checkout optimization needed")

print(f"\n6. DATA QUALITY: {'Excellent' if len(txn_not_in_cust) == 0 else 'Needs attention'}")

# Save exploration summary
summary = {
    'exploration_date': datetime.now().strftime('%Y-%m-%d'),
    'datasets': {
        'customers': {'rows': len(customers), 'columns': len(customers.columns)},
        'transactions': {'rows': len(transactions), 'columns': len(transactions.columns)},
        'products': {'rows': len(products), 'columns': len(products.columns)},
        'web_sessions': {'rows': len(web_sessions), 'columns': len(web_sessions.columns)},
        'stores': {'rows': len(stores), 'columns': len(stores.columns)},
        'marketing_spend': {'rows': len(marketing_spend), 'columns': len(marketing_spend.columns)}
    },
    'key_metrics': {
        'churn_rate': f"{churn_rate:.2f}%",
        'total_revenue_net': f"${transactions['net_amount'].sum():,.2f}",
        'avg_discount': f"{avg_discount:.2f}%",
        'cart_abandonment': f"{cart_abandon_rate:.2f}%",
        'unique_customers': int(customers.shape[0]),
        'unique_products': int(products.shape[0])
    },
    'data_quality': {
        'missing_customer_links': int(len(txn_not_in_cust)),
        'missing_product_links': int(len(txn_not_in_prod)),
        'calculation_mismatches': int(mismatches)
    }
}

with open('exploration_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\n" + "="*80)
print("[OK] Exploration complete! Summary saved to exploration_summary.json")
print("="*80)

# Made with Bob
