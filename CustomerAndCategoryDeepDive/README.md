# Customer Churn & Category Profitability Analysis

A comprehensive machine learning solution for predicting customer churn and analyzing product category profitability, featuring an interactive Gradio web application.

## 🎯 Project Overview

This project delivers actionable insights for business optimization through:

1. **Customer Churn Prediction**: ML model to identify at-risk customers with 99.77% ROC-AUC
2. **Category Profitability Analysis**: Deep dive into product category performance and margins
3. **Trend Analysis**: Identification of categories gaining or losing profitability
4. **Interactive Dashboard**: User-friendly Gradio application for real-time predictions and insights

## 📊 Key Results

### Churn Prediction Model Performance
- **Model**: Gradient Boosting Classifier
- **Accuracy**: 99.06%
- **Precision**: 100.00% (no false positives)
- **Recall**: 96.34% (catches 96.3% of churners)
- **F1-Score**: 98.14%
- **ROC-AUC**: 99.77%

### Profitability Insights
- **Total Revenue Analyzed**: $33.9M
- **Overall Net Margin**: 16.31%
- **Best Category**: Apparel (34.95% margin)
- **At-Risk Categories**: 10 subcategories with low margins + high discounts
- **Declining Category**: Electronics (margin declining by 4.94%)

### Top Churn Risk Factors
1. **Customer Activity Status** (51.95% importance)
2. **Days Since Last Purchase** (47.81% importance)
3. **Cart Abandonment Rate** (0.13% importance)

## 🗂️ Project Structure

```
CustomerAndCategoryDeepDive/
├── Data/
│   ├── customers.csv              # Customer demographics and churn labels
│   ├── transactions.csv           # Purchase history
│   ├── products.csv               # Product catalog
│   ├── web_sessions.csv           # Digital engagement data
│   ├── stores.csv                 # Store information
│   ├── marketing_spend.csv        # Marketing investment data
│   └── processed/                 # Processed datasets
│       ├── master_customer_features.csv
│       ├── churn_modeling_dataset.csv
│       ├── category_profitability.csv
│       ├── subcategory_profitability.csv
│       └── monthly_profitability_trends.csv
├── src/
│   ├── 01_data_exploration.py     # Data quality assessment
│   ├── 02_data_preparation.py     # Feature engineering
│   ├── 03_churn_model_training.py # Model training & evaluation
│   └── 04_profitability_analysis.py # Profitability analysis
├── models/
│   ├── churn_model.pkl            # Trained churn prediction model
│   ├── feature_scaler.pkl         # Feature scaling transformer
│   ├── model_metadata.json        # Model performance metrics
│   ├── feature_importance.csv     # Feature importance rankings
│   ├── profitability_summary.json # Profitability analysis results
│   └── category_trends.csv        # Profitability trends
├── notebooks/                     # Jupyter notebooks (optional)
├── app.py                         # Gradio web application
├── requirements.txt               # Python dependencies
├── PROJECT_PLAN.md               # Detailed project plan
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd CustomerAndCategoryDeepDive
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the complete pipeline** (optional - models are pre-trained)
```bash
# Step 1: Data Exploration
python src/01_data_exploration.py

# Step 2: Data Preparation & Feature Engineering
python src/02_data_preparation.py

# Step 3: Train Churn Prediction Model
python src/03_churn_model_training.py

# Step 4: Profitability Analysis
python src/04_profitability_analysis.py
```

4. **Launch the Gradio application**
```bash
python app.py
```

The application will be available at `http://localhost:7860`

## 📱 Using the Application

### Tab 1: Churn Prediction
- Enter customer metrics (purchase behavior, web engagement, demographics)
- Click "Predict Churn Risk" to get:
  - Churn probability (0-100%)
  - Risk level (Low/Medium/High)
  - Personalized retention recommendations
  - Visual risk gauge

### Tab 2: Category Profitability
- View profitability metrics for all product categories
- Compare net margins and total profits
- Identify best and worst performing categories

### Tab 3: Subcategory Analysis
- Detailed subcategory performance
- Sort by margin percentage or total profit
- Identify top performers and at-risk subcategories

### Tab 4: Profitability Trends
- Analyze margin changes over time
- Identify categories gaining or losing profitability
- View trend indicators (Gaining/Losing/Stable)

### Tab 5: Strategic Recommendations
- Data-driven business recommendations
- Prioritized by impact (High/Medium/Low)
- Actionable insights for optimization

### Tab 6: Model Performance
- Detailed model evaluation metrics
- Confusion matrix
- Feature importance rankings

## 🔬 Methodology

### Data Preparation
1. **Data Cleaning**: Handled missing values, removed invalid records
2. **Feature Engineering**: Created 24 features including:
   - RFM Analysis (Recency, Frequency, Monetary)
   - Web engagement metrics
   - Customer behavior indicators
   - Derived scores (engagement, customer value)

### Churn Prediction Model
1. **Algorithm**: Gradient Boosting Classifier
2. **Class Imbalance**: Handled using class weights (25.84% churn rate)
3. **Feature Scaling**: StandardScaler for normalization
4. **Train/Test Split**: 80/20 with stratification
5. **Hyperparameter Tuning**: GridSearchCV with 5-fold cross-validation
6. **Validation**: Comprehensive metrics on held-out test set

### Profitability Analysis
1. **Metrics Calculated**:
   - Gross profit and margin
   - Net profit after discounts
   - Discount impact analysis
   - Category-level aggregations
2. **Trend Analysis**: Comparing first half vs second half performance
3. **Risk Identification**: Low margin + high discount combinations

## 📈 Key Findings

### Customer Churn Insights
- **25.84% overall churn rate** - requires attention
- **Bronze tier customers** have highest churn (33.96%)
- **45-54 age group** shows highest churn rate
- **Inactive customers** (90+ days since purchase) are primary risk

### Profitability Insights
- **Apparel category** is most profitable (34.95% margin, $1.8M profit)
- **Electronics category** is declining (-4.94% margin change)
- **10 at-risk subcategories** with margins below 10%
- **Grocery & Essentials** has lowest margin (2.95%)

### Strategic Recommendations
1. **HIGH PRIORITY**: Expand Apparel and Health & Beauty categories
2. **HIGH PRIORITY**: Review pricing/costs for Electronics and Grocery
3. **HIGH PRIORITY**: Investigate declining Electronics margins
4. **MEDIUM PRIORITY**: Reduce discounts on high-margin products

## 🛠️ Technical Details

### Technologies Used
- **Python 3.8+**: Core programming language
- **pandas & numpy**: Data manipulation
- **scikit-learn**: Machine learning algorithms
- **Gradio**: Interactive web application
- **plotly**: Interactive visualizations
- **matplotlib & seaborn**: Static visualizations

### Model Features (24 total)
1. days_since_last_purchase
2. total_transactions
3. total_revenue
4. avg_order_value
5. total_items_purchased
6. avg_discount_received
7. unique_products
8. unique_categories
9. unique_subcategories
10. customer_lifespan_days
11. purchase_frequency
12. total_sessions
13. total_pages_viewed
14. avg_pages_per_session
15. total_cart_abandonments
16. cart_abandonment_rate
17. engagement_score
18. customer_value_score
19. discount_dependency
20. is_active
21. is_dormant
22. customer_tenure_days
23. loyalty_tier_encoded
24. age_band_encoded

## 📊 Data Overview

### Datasets
- **Customers**: 18,000 records
- **Transactions**: 256,762 records
- **Products**: 1,200 records
- **Web Sessions**: 90,000 records
- **Stores**: 12 locations
- **Date Range**: February 2024 - January 2026

### Data Quality
- Minimal missing values (<1% in most fields)
- Strong referential integrity
- Validated transaction calculations
- Comprehensive feature coverage

## 🎓 Business Impact

### Churn Reduction Opportunities
- **Proactive Retention**: Identify at-risk customers before they churn
- **Personalized Interventions**: Tailored recommendations per customer
- **Resource Optimization**: Focus retention efforts on high-value customers
- **Expected Impact**: 20-30% reduction in churn rate

### Profitability Optimization
- **Category Mix Optimization**: Expand high-margin categories
- **Discount Strategy**: Reduce unnecessary discounting
- **Cost Management**: Address low-margin categories
- **Expected Impact**: 2-5% margin improvement

## 🔮 Future Enhancements

1. **Real-time Predictions**: API integration for live scoring
2. **Automated Alerts**: Proactive notifications for high-risk customers
3. **A/B Testing Framework**: Test retention strategies
4. **Customer Segmentation**: Advanced clustering analysis
5. **Time Series Forecasting**: Predict future profitability trends
6. **Deep Learning Models**: Explore neural networks for improved accuracy

## 📝 Documentation

- **PROJECT_PLAN.md**: Detailed project methodology and approach
- **data_cleaning_log.md**: All data cleaning decisions documented
- **models/model_metadata.json**: Complete model specifications
- **models/profitability_summary.json**: Profitability analysis results

## 🤝 Contributing

This is a portfolio project demonstrating end-to-end ML capabilities. Suggestions and feedback are welcome!

## 📧 Contact

For questions or collaboration opportunities, please reach out through GitHub.

## 📄 License

This project is for educational and portfolio purposes.

---

**Built with ❤️ using Python, scikit-learn, and Gradio**

*Last Updated: June 2026*