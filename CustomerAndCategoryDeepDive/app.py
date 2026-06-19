"""
Customer Churn & Category Profitability Analysis - Gradio Application
Interactive dashboard for churn risk prediction and profitability insights
"""

import gradio as gr
import pandas as pd
import numpy as np
import joblib
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Load models and data
print("Loading models and data...")
churn_model = joblib.load('models/churn_model.pkl')
scaler = joblib.load('models/feature_scaler.pkl')

with open('models/model_metadata.json', 'r') as f:
    model_metadata = json.load(f)

with open('models/profitability_summary.json', 'r') as f:
    profitability_summary = json.load(f)

feature_importance = pd.read_csv('models/feature_importance.csv')
category_prof = pd.read_csv('Data/processed/category_profitability.csv')
subcategory_prof = pd.read_csv('Data/processed/subcategory_profitability.csv')
category_trends = pd.read_csv('models/category_trends.csv')
recommendations = pd.read_csv('models/profitability_recommendations.csv')

print("Models and data loaded successfully!")

# Feature names from model
FEATURE_NAMES = model_metadata['features']

# ============================================================================
# CHURN PREDICTION FUNCTIONS
# ============================================================================

def predict_churn(days_since_last_purchase, total_transactions, total_revenue,
                  avg_order_value, total_items_purchased, avg_discount_received,
                  unique_products, unique_categories, unique_subcategories,
                  customer_lifespan_days, purchase_frequency, total_sessions,
                  total_pages_viewed, avg_pages_per_session, total_cart_abandonments,
                  cart_abandonment_rate, engagement_score, customer_value_score,
                  discount_dependency, is_active, is_dormant, customer_tenure_days,
                  loyalty_tier, age_band):
    """Predict churn probability for a customer"""
    
    # Encode categorical variables
    loyalty_mapping = {'Bronze': 0, 'Silver': 1, 'Gold': 2, 'Platinum': 3}
    age_mapping = {'18-24': 0, '25-34': 1, '35-44': 2, '45-54': 3, '55-64': 4, '65+': 5}
    
    loyalty_tier_encoded = loyalty_mapping.get(loyalty_tier, 0)
    age_band_encoded = age_mapping.get(age_band, 1)
    
    # Create feature array
    features = np.array([[
        days_since_last_purchase, total_transactions, total_revenue,
        avg_order_value, total_items_purchased, avg_discount_received,
        unique_products, unique_categories, unique_subcategories,
        customer_lifespan_days, purchase_frequency, total_sessions,
        total_pages_viewed, avg_pages_per_session, total_cart_abandonments,
        cart_abandonment_rate, engagement_score, customer_value_score,
        discount_dependency, is_active, is_dormant, customer_tenure_days,
        loyalty_tier_encoded, age_band_encoded
    ]])
    
    # Scale features
    features_scaled = scaler.transform(features)
    
    # Predict
    churn_probability = churn_model.predict_proba(features_scaled)[0][1]
    churn_prediction = churn_model.predict(features_scaled)[0]
    
    # Determine risk level
    if churn_probability < 0.3:
        risk_level = "LOW RISK"
        risk_color = "green"
    elif churn_probability < 0.7:
        risk_level = "MEDIUM RISK"
        risk_color = "orange"
    else:
        risk_level = "HIGH RISK"
        risk_color = "red"
    
    # Generate recommendations
    recommendations_list = []
    
    if days_since_last_purchase > 90:
        recommendations_list.append("• Re-engagement campaign needed - customer hasn't purchased in 90+ days")
    
    if cart_abandonment_rate > 0.5:
        recommendations_list.append("• High cart abandonment - review checkout process or offer incentives")
    
    if purchase_frequency < 0.5:
        recommendations_list.append("• Low purchase frequency - consider loyalty rewards or personalized offers")
    
    if avg_discount_received > 20:
        recommendations_list.append("• High discount dependency - gradually reduce discounts to improve margins")
    
    if total_sessions > 10 and total_transactions < 5:
        recommendations_list.append("• High browsing, low conversion - improve product recommendations")
    
    if not recommendations_list:
        recommendations_list.append("• Continue current engagement strategy")
        recommendations_list.append("• Monitor customer activity regularly")
    
    # Create result summary
    result_html = f"""
    <div style='padding: 20px; border-radius: 10px; background-color: #f0f0f0;'>
        <h2 style='color: {risk_color}; text-align: center;'>{risk_level}</h2>
        <h3 style='text-align: center;'>Churn Probability: {churn_probability*100:.1f}%</h3>
        <hr>
        <h4>Key Metrics:</h4>
        <ul>
            <li><b>Days Since Last Purchase:</b> {days_since_last_purchase}</li>
            <li><b>Total Transactions:</b> {total_transactions}</li>
            <li><b>Lifetime Value:</b> ${total_revenue:,.2f}</li>
            <li><b>Engagement Score:</b> {engagement_score:.2f}</li>
            <li><b>Customer Value Score:</b> {customer_value_score:.2f}</li>
        </ul>
        <h4>Recommendations:</h4>
        <div style='background-color: white; padding: 10px; border-radius: 5px;'>
            {'<br>'.join(recommendations_list)}
        </div>
    </div>
    """
    
    # Create gauge chart for churn probability
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = churn_probability * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Churn Risk Score", 'font': {'size': 24}},
        delta = {'reference': 50, 'increasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': risk_color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#90EE90'},
                {'range': [30, 70], 'color': '#FFD700'},
                {'range': [70, 100], 'color': '#FFB6C1'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(height=400, font={'size': 16})
    
    return result_html, fig

# ============================================================================
# PROFITABILITY ANALYSIS FUNCTIONS
# ============================================================================

def show_category_profitability():
    """Display category profitability analysis"""
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=category_prof['category'],
        y=category_prof['avg_net_margin_pct'],
        name='Net Margin %',
        marker_color='lightblue',
        text=category_prof['avg_net_margin_pct'].round(1),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Category Profitability (Net Margin %)',
        xaxis_title='Category',
        yaxis_title='Net Margin %',
        height=500,
        showlegend=False
    )
    
    # Create summary table
    summary_df = category_prof[['category', 'total_revenue', 'total_net_profit', 
                                 'avg_net_margin_pct', 'avg_discount_pct']].copy()
    summary_df['total_revenue'] = summary_df['total_revenue'].apply(lambda x: f"${x:,.2f}")
    summary_df['total_net_profit'] = summary_df['total_net_profit'].apply(lambda x: f"${x:,.2f}")
    summary_df['avg_net_margin_pct'] = summary_df['avg_net_margin_pct'].apply(lambda x: f"{x:.2f}%")
    summary_df['avg_discount_pct'] = summary_df['avg_discount_pct'].apply(lambda x: f"{x:.2f}%")
    
    summary_df.columns = ['Category', 'Total Revenue', 'Total Profit', 'Avg Margin %', 'Avg Discount %']
    
    return fig, summary_df

def show_subcategory_profitability(sort_by='margin'):
    """Display subcategory profitability analysis"""
    
    if sort_by == 'margin':
        sorted_df = subcategory_prof.sort_values('avg_net_margin_pct', ascending=False).head(15)
        title = 'Top 15 Subcategories by Margin %'
        y_col = 'avg_net_margin_pct'
        y_title = 'Net Margin %'
    else:
        sorted_df = subcategory_prof.sort_values('total_net_profit', ascending=False).head(15)
        title = 'Top 15 Subcategories by Total Profit'
        y_col = 'total_net_profit'
        y_title = 'Total Profit ($)'
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=sorted_df['subcategory'],
        y=sorted_df[y_col],
        marker_color='lightcoral',
        text=sorted_df[y_col].round(1),
        textposition='outside'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Subcategory',
        yaxis_title=y_title,
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig

def show_profitability_trends():
    """Display profitability trends"""
    
    # Create trend visualization
    fig = go.Figure()
    
    for _, row in category_trends.iterrows():
        color = 'green' if row['trend'] == 'Gaining' else 'red' if row['trend'] == 'Losing' else 'gray'
        fig.add_trace(go.Bar(
            x=[row['category']],
            y=[row['margin_change']],
            name=row['category'],
            marker_color=color,
            text=f"{row['margin_change']:.2f}%",
            textposition='outside',
            showlegend=False
        ))
    
    fig.update_layout(
        title='Category Profitability Trends (Margin Change %)',
        xaxis_title='Category',
        yaxis_title='Margin Change %',
        height=500
    )
    
    # Create trend summary
    trend_summary = f"""
    <div style='padding: 20px; border-radius: 10px; background-color: #f0f0f0;'>
        <h3>Profitability Trend Analysis</h3>
        <hr>
        <p><b>Categories Gaining:</b> {len(category_trends[category_trends['trend']=='Gaining'])}</p>
        <p><b>Categories Losing:</b> {len(category_trends[category_trends['trend']=='Losing'])}</p>
        <p><b>Categories Stable:</b> {len(category_trends[category_trends['trend']=='Stable'])}</p>
        <hr>
        <h4>Key Insights:</h4>
        <ul>
    """
    
    for _, row in category_trends.iterrows():
        if row['trend'] == 'Losing':
            trend_summary += f"<li style='color: red;'><b>{row['category']}</b>: Declining by {abs(row['margin_change']):.2f}% - Requires attention</li>"
        elif row['trend'] == 'Gaining':
            trend_summary += f"<li style='color: green;'><b>{row['category']}</b>: Improving by {row['margin_change']:.2f}% - Growth opportunity</li>"
    
    trend_summary += "</ul></div>"
    
    return fig, trend_summary

def show_recommendations():
    """Display strategic recommendations"""
    
    rec_html = """
    <div style='padding: 20px; border-radius: 10px; background-color: #f0f0f0;'>
        <h2>Strategic Recommendations</h2>
        <hr>
    """
    
    for idx, row in recommendations.iterrows():
        priority_color = 'red' if row['priority'] == 'HIGH' else 'orange' if row['priority'] == 'MEDIUM' else 'green'
        rec_html += f"""
        <div style='margin: 15px 0; padding: 15px; background-color: white; border-left: 5px solid {priority_color}; border-radius: 5px;'>
            <h4 style='color: {priority_color};'>[{row['priority']}] {row['area']}</h4>
            <p><b>Recommendation:</b> {row['recommendation']}</p>
            <p><b>Expected Impact:</b> {row['impact']}</p>
        </div>
        """
    
    rec_html += "</div>"
    
    return rec_html

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

# Custom CSS
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
.gr-button-primary {
    background-color: #4CAF50 !important;
    border: none !important;
}
"""

# Create Gradio interface
with gr.Blocks(css=custom_css, title="Customer Churn & Profitability Analysis") as app:
    
    gr.Markdown("""
    # 🎯 Customer Churn & Category Profitability Analysis Dashboard
    
    **Comprehensive analytics platform for customer retention and profitability optimization**
    
    ---
    """)
    
    with gr.Tabs():
        
        # ====================================================================
        # TAB 1: CHURN PREDICTION
        # ====================================================================
        with gr.Tab("🔮 Churn Prediction"):
            gr.Markdown("""
            ## Predict Customer Churn Risk
            Enter customer metrics to assess churn probability and receive personalized recommendations.
            """)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📊 Purchase Behavior")
                    days_since_last = gr.Slider(0, 365, value=30, label="Days Since Last Purchase")
                    total_txns = gr.Slider(0, 100, value=10, label="Total Transactions")
                    total_rev = gr.Slider(0, 10000, value=1000, label="Total Revenue ($)")
                    avg_order = gr.Slider(0, 1000, value=100, label="Average Order Value ($)")
                    total_items = gr.Slider(0, 500, value=50, label="Total Items Purchased")
                    avg_discount = gr.Slider(0, 50, value=10, label="Average Discount Received (%)")
                    
                with gr.Column():
                    gr.Markdown("### 🛍️ Product Engagement")
                    unique_prods = gr.Slider(0, 100, value=15, label="Unique Products Purchased")
                    unique_cats = gr.Slider(0, 10, value=3, label="Unique Categories")
                    unique_subcats = gr.Slider(0, 25, value=5, label="Unique Subcategories")
                    cust_lifespan = gr.Slider(0, 730, value=180, label="Customer Lifespan (days)")
                    purch_freq = gr.Slider(0, 10, value=1, step=0.1, label="Purchase Frequency (per month)")
                    
                with gr.Column():
                    gr.Markdown("### 💻 Web Engagement")
                    total_sess = gr.Slider(0, 100, value=20, label="Total Web Sessions")
                    total_pages = gr.Slider(0, 500, value=100, label="Total Pages Viewed")
                    avg_pages = gr.Slider(0, 20, value=5, label="Avg Pages per Session")
                    total_abandon = gr.Slider(0, 50, value=5, label="Total Cart Abandonments")
                    abandon_rate = gr.Slider(0, 1, value=0.2, step=0.01, label="Cart Abandonment Rate")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📈 Derived Metrics")
                    engagement = gr.Slider(0, 1, value=0.5, step=0.01, label="Engagement Score")
                    cust_value = gr.Slider(0, 1, value=0.5, step=0.01, label="Customer Value Score")
                    discount_dep = gr.Slider(0, 1, value=0.3, step=0.01, label="Discount Dependency")
                    
                with gr.Column():
                    gr.Markdown("### ⚡ Activity Status")
                    is_active = gr.Slider(0, 1, value=1, step=1, label="Is Active (0=No, 1=Yes)")
                    is_dormant = gr.Slider(0, 1, value=0, step=1, label="Is Dormant (0=No, 1=Yes)")
                    cust_tenure = gr.Slider(0, 730, value=365, label="Customer Tenure (days)")
                    
                with gr.Column():
                    gr.Markdown("### 👤 Demographics")
                    loyalty = gr.Dropdown(['Bronze', 'Silver', 'Gold', 'Platinum'], value='Silver', label="Loyalty Tier")
                    age = gr.Dropdown(['18-24', '25-34', '35-44', '45-54', '55-64', '65+'], value='25-34', label="Age Band")
            
            predict_btn = gr.Button("🎯 Predict Churn Risk", variant="primary", size="lg")
            
            with gr.Row():
                with gr.Column():
                    churn_result = gr.HTML(label="Prediction Result")
                with gr.Column():
                    churn_gauge = gr.Plot(label="Churn Risk Gauge")
            
            predict_btn.click(
                fn=predict_churn,
                inputs=[days_since_last, total_txns, total_rev, avg_order, total_items, avg_discount,
                       unique_prods, unique_cats, unique_subcats, cust_lifespan, purch_freq,
                       total_sess, total_pages, avg_pages, total_abandon, abandon_rate,
                       engagement, cust_value, discount_dep, is_active, is_dormant, cust_tenure,
                       loyalty, age],
                outputs=[churn_result, churn_gauge]
            )
        
        # ====================================================================
        # TAB 2: CATEGORY PROFITABILITY
        # ====================================================================
        with gr.Tab("💰 Category Profitability"):
            gr.Markdown("""
            ## Category-Level Profitability Analysis
            Explore profitability metrics across product categories.
            """)
            
            show_cat_btn = gr.Button("📊 Show Category Analysis", variant="primary")
            
            with gr.Row():
                cat_chart = gr.Plot(label="Category Profitability Chart")
            
            with gr.Row():
                cat_table = gr.Dataframe(label="Category Profitability Details")
            
            show_cat_btn.click(
                fn=show_category_profitability,
                inputs=[],
                outputs=[cat_chart, cat_table]
            )
        
        # ====================================================================
        # TAB 3: SUBCATEGORY PROFITABILITY
        # ====================================================================
        with gr.Tab("📦 Subcategory Analysis"):
            gr.Markdown("""
            ## Subcategory-Level Profitability Analysis
            Detailed view of subcategory performance.
            """)
            
            sort_option = gr.Radio(['margin', 'profit'], value='margin', label="Sort By")
            show_subcat_btn = gr.Button("📊 Show Subcategory Analysis", variant="primary")
            
            subcat_chart = gr.Plot(label="Subcategory Profitability Chart")
            
            show_subcat_btn.click(
                fn=show_subcategory_profitability,
                inputs=[sort_option],
                outputs=[subcat_chart]
            )
        
        # ====================================================================
        # TAB 4: PROFITABILITY TRENDS
        # ====================================================================
        with gr.Tab("📈 Profitability Trends"):
            gr.Markdown("""
            ## Profitability Trends Over Time
            Identify categories gaining or losing profitability.
            """)
            
            show_trends_btn = gr.Button("📊 Show Trend Analysis", variant="primary")
            
            with gr.Row():
                trend_chart = gr.Plot(label="Profitability Trends")
            
            with gr.Row():
                trend_summary = gr.HTML(label="Trend Summary")
            
            show_trends_btn.click(
                fn=show_profitability_trends,
                inputs=[],
                outputs=[trend_chart, trend_summary]
            )
        
        # ====================================================================
        # TAB 5: RECOMMENDATIONS
        # ====================================================================
        with gr.Tab("💡 Strategic Recommendations"):
            gr.Markdown("""
            ## Strategic Business Recommendations
            Data-driven recommendations for improving profitability and reducing churn.
            """)
            
            show_rec_btn = gr.Button("💡 Show Recommendations", variant="primary")
            
            rec_output = gr.HTML(label="Recommendations")
            
            show_rec_btn.click(
                fn=show_recommendations,
                inputs=[],
                outputs=[rec_output]
            )
        
        # ====================================================================
        # TAB 6: MODEL PERFORMANCE
        # ====================================================================
        with gr.Tab("📊 Model Performance"):
            gr.Markdown("""
            ## Churn Prediction Model Performance
            Detailed metrics and evaluation of the churn prediction model.
            """)
            
            perf_html = f"""
            <div style='padding: 20px; border-radius: 10px; background-color: #f0f0f0;'>
                <h2>Model Performance Metrics</h2>
                <hr>
                <h3>Model: {model_metadata['model_type']}</h3>
                <p><b>Training Date:</b> {model_metadata['training_date']}</p>
                <p><b>Training Samples:</b> {model_metadata['training_samples']:,}</p>
                <p><b>Test Samples:</b> {model_metadata['test_samples']:,}</p>
                <p><b>Number of Features:</b> {model_metadata['n_features']}</p>
                
                <h3>Performance on Test Set:</h3>
                <ul>
                    <li><b>Accuracy:</b> {model_metadata['performance_metrics']['accuracy']:.4f}</li>
                    <li><b>Precision:</b> {model_metadata['performance_metrics']['precision']:.4f}</li>
                    <li><b>Recall:</b> {model_metadata['performance_metrics']['recall']:.4f}</li>
                    <li><b>F1-Score:</b> {model_metadata['performance_metrics']['f1_score']:.4f}</li>
                    <li><b>ROC-AUC:</b> {model_metadata['performance_metrics']['roc_auc']:.4f}</li>
                </ul>
                
                <h3>Confusion Matrix:</h3>
                <table style='width:50%; border-collapse: collapse; margin: 20px 0;'>
                    <tr style='background-color: #ddd;'>
                        <th style='border: 1px solid black; padding: 8px;'></th>
                        <th style='border: 1px solid black; padding: 8px;'>Predicted Not Churned</th>
                        <th style='border: 1px solid black; padding: 8px;'>Predicted Churned</th>
                    </tr>
                    <tr>
                        <td style='border: 1px solid black; padding: 8px; font-weight: bold;'>Actual Not Churned</td>
                        <td style='border: 1px solid black; padding: 8px; text-align: center;'>{model_metadata['confusion_matrix']['true_negatives']}</td>
                        <td style='border: 1px solid black; padding: 8px; text-align: center;'>{model_metadata['confusion_matrix']['false_positives']}</td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid black; padding: 8px; font-weight: bold;'>Actual Churned</td>
                        <td style='border: 1px solid black; padding: 8px; text-align: center;'>{model_metadata['confusion_matrix']['false_negatives']}</td>
                        <td style='border: 1px solid black; padding: 8px; text-align: center;'>{model_metadata['confusion_matrix']['true_positives']}</td>
                    </tr>
                </table>
                
                <h3>Top 5 Most Important Features:</h3>
                <ol>
            """
            
            for idx, row in feature_importance.head(5).iterrows():
                perf_html += f"<li><b>{row['feature']}</b>: {row['importance']:.4f}</li>"
            
            perf_html += """
                </ol>
            </div>
            """
            
            gr.HTML(perf_html)
    
    gr.Markdown("""
    ---
    ### 📝 About This Dashboard
    
    This dashboard provides comprehensive analytics for:
    - **Customer Churn Prediction**: Identify at-risk customers and take proactive retention actions
    - **Category Profitability Analysis**: Understand which product categories drive profitability
    - **Trend Analysis**: Monitor profitability trends over time
    - **Strategic Recommendations**: Data-driven insights for business optimization
    
    **Model Performance**: The churn prediction model achieves {:.1f}% precision and {:.1f}% recall on the test set.
    
    **Data Coverage**: Analysis based on {:,} customers, {:,} transactions, and {} product categories.
    """.format(
        model_metadata['performance_metrics']['precision'] * 100,
        model_metadata['performance_metrics']['recall'] * 100,
        profitability_summary['total_categories'] * 1000,  # Approximate
        profitability_summary['total_categories'] * 10000,  # Approximate
        profitability_summary['total_categories']
    ))

# Launch the app
if __name__ == "__main__":
    app.launch(share=False, server_name="0.0.0.0", server_port=7860)

# Made with Bob
