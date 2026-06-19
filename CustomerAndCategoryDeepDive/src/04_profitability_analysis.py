"""
Category Profitability Analysis Script
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

print("="*80)
print("CATEGORY PROFITABILITY ANALYSIS")
print("="*80)
print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load profitability datasets
print("Loading profitability datasets...")
category_prof = pd.read_csv('Data/processed/category_profitability.csv')
subcategory_prof = pd.read_csv('Data/processed/subcategory_profitability.csv')
monthly_trends = pd.read_csv('Data/processed/monthly_profitability_trends.csv')

print(f"[OK] Loaded profitability data\n")

# ============================================================================
# STEP 1: CATEGORY-LEVEL ANALYSIS
# ============================================================================
print("="*80)
print("STEP 1: CATEGORY-LEVEL PROFITABILITY")
print("="*80)

# Sort by net profit
category_prof_sorted = category_prof.sort_values('total_net_profit', ascending=False)

print("\nCategory Profitability Summary:")
print(category_prof_sorted[['category', 'total_revenue', 'total_net_profit', 
                             'avg_net_margin_pct', 'avg_discount_pct']].to_string(index=False))

print(f"\nTotal Revenue Across All Categories: ${category_prof['total_revenue'].sum():,.2f}")
print(f"Total Net Profit Across All Categories: ${category_prof['total_net_profit'].sum():,.2f}")
print(f"Overall Net Margin: {(category_prof['total_net_profit'].sum() / category_prof['total_revenue'].sum() * 100):.2f}%")

# Identify best and worst performers
best_category = category_prof_sorted.iloc[0]
worst_category = category_prof_sorted.iloc[-1]

print(f"\nBest Performing Category: {best_category['category']}")
print(f"  Revenue: ${best_category['total_revenue']:,.2f}")
print(f"  Profit: ${best_category['total_net_profit']:,.2f}")
print(f"  Margin: {best_category['avg_net_margin_pct']:.2f}%")

print(f"\nWorst Performing Category: {worst_category['category']}")
print(f"  Revenue: ${worst_category['total_revenue']:,.2f}")
print(f"  Profit: ${worst_category['total_net_profit']:,.2f}")
print(f"  Margin: {worst_category['avg_net_margin_pct']:.2f}%")

# ============================================================================
# STEP 2: SUBCATEGORY-LEVEL ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("STEP 2: SUBCATEGORY-LEVEL PROFITABILITY")
print("="*80)

# Sort by margin
subcategory_prof_sorted = subcategory_prof.sort_values('avg_net_margin_pct', ascending=False)

print("\nTop 10 Most Profitable Subcategories (by margin):")
print(subcategory_prof_sorted.head(10)[['subcategory', 'total_revenue', 
                                         'avg_net_margin_pct', 'avg_discount_pct']].to_string(index=False))

print("\nBottom 10 Least Profitable Subcategories (by margin):")
print(subcategory_prof_sorted.tail(10)[['subcategory', 'total_revenue', 
                                         'avg_net_margin_pct', 'avg_discount_pct']].to_string(index=False))

# Identify at-risk subcategories (low margin + high discount)
at_risk = subcategory_prof[(subcategory_prof['avg_net_margin_pct'] < 10) & 
                           (subcategory_prof['avg_discount_pct'] > 10)]

if len(at_risk) > 0:
    print(f"\n[WARNING] {len(at_risk)} At-Risk Subcategories (Low Margin + High Discount):")
    print(at_risk[['subcategory', 'avg_net_margin_pct', 'avg_discount_pct', 'total_revenue']].to_string(index=False))

# ============================================================================
# STEP 3: TREND ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("STEP 3: PROFITABILITY TRENDS OVER TIME")
print("="*80)

# Convert year_month to datetime
monthly_trends['year_month'] = pd.to_datetime(monthly_trends['year_month'].astype(str))

# Calculate trend for each category
print("\nProfitability Trends by Category:")

trend_summary = []
for category in monthly_trends['category'].unique():
    cat_data = monthly_trends[monthly_trends['category'] == category].sort_values('year_month')
    
    if len(cat_data) >= 2:
        # Calculate trend (comparing first half vs second half)
        mid_point = len(cat_data) // 2
        first_half_margin = cat_data.iloc[:mid_point]['margin_pct'].mean()
        second_half_margin = cat_data.iloc[mid_point:]['margin_pct'].mean()
        
        margin_change = second_half_margin - first_half_margin
        trend = 'Gaining' if margin_change > 1 else 'Losing' if margin_change < -1 else 'Stable'
        
        trend_summary.append({
            'category': category,
            'first_half_margin': first_half_margin,
            'second_half_margin': second_half_margin,
            'margin_change': margin_change,
            'trend': trend
        })

trend_df = pd.DataFrame(trend_summary).sort_values('margin_change', ascending=False)

print(trend_df.to_string(index=False))

# Identify gaining and losing categories
gaining = trend_df[trend_df['trend'] == 'Gaining']
losing = trend_df[trend_df['trend'] == 'Losing']

print(f"\n[OK] Categories Gaining Profitability: {len(gaining)}")
if len(gaining) > 0:
    print(gaining[['category', 'margin_change']].to_string(index=False))

print(f"\n[WARNING] Categories Losing Profitability: {len(losing)}")
if len(losing) > 0:
    print(losing[['category', 'margin_change']].to_string(index=False))

# ============================================================================
# STEP 4: DISCOUNT IMPACT ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("STEP 4: DISCOUNT IMPACT ANALYSIS")
print("="*80)

# Analyze relationship between discounting and profitability
print("\nDiscount vs Profitability Analysis:")

discount_analysis = subcategory_prof[['subcategory', 'avg_discount_pct', 'avg_net_margin_pct', 'total_revenue']].copy()
discount_analysis['discount_category'] = pd.cut(discount_analysis['avg_discount_pct'], 
                                                 bins=[0, 10, 20, 100], 
                                                 labels=['Low (0-10%)', 'Medium (10-20%)', 'High (20%+)'])

discount_summary = discount_analysis.groupby('discount_category').agg({
    'avg_net_margin_pct': 'mean',
    'total_revenue': 'sum',
    'subcategory': 'count'
}).round(2)

discount_summary.columns = ['Avg Margin %', 'Total Revenue', 'Subcategory Count']
print(discount_summary)

print("\nKey Insight:")
if discount_summary.loc['Low (0-10%)', 'Avg Margin %'] > discount_summary.loc['High (20%+)', 'Avg Margin %']:
    print("  -> Lower discount rates correlate with higher profit margins")
    print("  -> Consider reducing aggressive discounting strategies")
else:
    print("  -> Discount strategy appears effective for volume")

# ============================================================================
# STEP 5: RECOMMENDATIONS
# ============================================================================
print("\n" + "="*80)
print("STEP 5: STRATEGIC RECOMMENDATIONS")
print("="*80)

recommendations = []

# 1. Focus on high-margin categories
high_margin_cats = category_prof[category_prof['avg_net_margin_pct'] > 30]
if len(high_margin_cats) > 0:
    recommendations.append({
        'priority': 'HIGH',
        'area': 'Product Mix',
        'recommendation': f"Expand {', '.join(high_margin_cats['category'].tolist())} - high margin categories",
        'impact': f"Potential margin improvement: {high_margin_cats['avg_net_margin_pct'].mean():.1f}%"
    })

# 2. Address low-margin categories
low_margin_cats = category_prof[category_prof['avg_net_margin_pct'] < 10]
if len(low_margin_cats) > 0:
    recommendations.append({
        'priority': 'HIGH',
        'area': 'Cost Optimization',
        'recommendation': f"Review pricing/costs for {', '.join(low_margin_cats['category'].tolist())}",
        'impact': f"Current margin: {low_margin_cats['avg_net_margin_pct'].mean():.1f}%"
    })

# 3. Reduce discounting on high-margin products
high_discount_high_margin = subcategory_prof[(subcategory_prof['avg_discount_pct'] > 15) & 
                                              (subcategory_prof['avg_net_margin_pct'] > 30)]
if len(high_discount_high_margin) > 0:
    recommendations.append({
        'priority': 'MEDIUM',
        'area': 'Discount Strategy',
        'recommendation': f"Reduce discounts on {len(high_discount_high_margin)} high-margin subcategories",
        'impact': f"Potential profit recovery: ${high_discount_high_margin['total_discount_cost'].sum():,.2f}"
    })

# 4. Address losing categories
if len(losing) > 0:
    recommendations.append({
        'priority': 'HIGH',
        'area': 'Trend Reversal',
        'recommendation': f"Investigate declining margins in {', '.join(losing['category'].tolist())}",
        'impact': f"Margin decline: {losing['margin_change'].mean():.2f}%"
    })

# 5. Leverage gaining categories
if len(gaining) > 0:
    recommendations.append({
        'priority': 'MEDIUM',
        'area': 'Growth Opportunity',
        'recommendation': f"Invest in growing {', '.join(gaining['category'].tolist())}",
        'impact': f"Margin improvement: +{gaining['margin_change'].mean():.2f}%"
    })

print("\nStrategic Recommendations:")
for i, rec in enumerate(recommendations, 1):
    print(f"\n{i}. [{rec['priority']}] {rec['area']}")
    print(f"   Recommendation: {rec['recommendation']}")
    print(f"   Expected Impact: {rec['impact']}")

# ============================================================================
# STEP 6: SAVE ANALYSIS RESULTS
# ============================================================================
print("\n" + "="*80)
print("STEP 6: SAVING ANALYSIS RESULTS")
print("="*80)

# Save recommendations
recommendations_df = pd.DataFrame(recommendations)
recommendations_df.to_csv('models/profitability_recommendations.csv', index=False)
print("\n[OK] Saved profitability_recommendations.csv")

# Save trend analysis
trend_df.to_csv('models/category_trends.csv', index=False)
print("[OK] Saved category_trends.csv")

# Create summary report
summary_report = {
    'analysis_date': datetime.now().strftime('%Y-%m-%d'),
    'total_categories': int(len(category_prof)),
    'total_subcategories': int(len(subcategory_prof)),
    'total_revenue': float(category_prof['total_revenue'].sum()),
    'total_profit': float(category_prof['total_net_profit'].sum()),
    'overall_margin_pct': float(category_prof['total_net_profit'].sum() / category_prof['total_revenue'].sum() * 100),
    'best_category': {
        'name': str(best_category['category']),
        'margin_pct': float(best_category['avg_net_margin_pct']),
        'profit': float(best_category['total_net_profit'])
    },
    'worst_category': {
        'name': str(worst_category['category']),
        'margin_pct': float(worst_category['avg_net_margin_pct']),
        'profit': float(worst_category['total_net_profit'])
    },
    'categories_gaining': int(len(gaining)),
    'categories_losing': int(len(losing)),
    'at_risk_subcategories': int(len(at_risk)),
    'recommendations_count': len(recommendations)
}

with open('models/profitability_summary.json', 'w') as f:
    json.dump(summary_report, f, indent=2)

print("[OK] Saved profitability_summary.json")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("PROFITABILITY ANALYSIS SUMMARY")
print("="*80)

print(f"\nOverall Performance:")
print(f"  Total Revenue: ${summary_report['total_revenue']:,.2f}")
print(f"  Total Profit: ${summary_report['total_profit']:,.2f}")
print(f"  Overall Margin: {summary_report['overall_margin_pct']:.2f}%")

print(f"\nCategory Performance:")
print(f"  Best: {summary_report['best_category']['name']} ({summary_report['best_category']['margin_pct']:.2f}% margin)")
print(f"  Worst: {summary_report['worst_category']['name']} ({summary_report['worst_category']['margin_pct']:.2f}% margin)")

print(f"\nTrends:")
print(f"  Categories Gaining Profitability: {summary_report['categories_gaining']}")
print(f"  Categories Losing Profitability: {summary_report['categories_losing']}")
print(f"  At-Risk Subcategories: {summary_report['at_risk_subcategories']}")

print(f"\nRecommendations Generated: {summary_report['recommendations_count']}")

print("\n" + "="*80)
print("[OK] PROFITABILITY ANALYSIS COMPLETE!")
print("="*80)
print("\nFiles created:")
print("  - models/profitability_recommendations.csv")
print("  - models/category_trends.csv")
print("  - models/profitability_summary.json")

# Made with Bob
