"""
Churn Prediction Model Training & Evaluation
Customer Churn & Category Profitability Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, confusion_matrix, roc_auc_score,
                             roc_curve, precision_recall_curve, f1_score,
                             precision_score, recall_score, accuracy_score)
from sklearn.utils.class_weight import compute_class_weight
import joblib
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("CHURN PREDICTION MODEL TRAINING")
print("="*80)
print(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load modeling dataset
print("Loading modeling dataset...")
df = pd.read_csv('Data/processed/churn_modeling_dataset.csv')
print(f"[OK] Loaded {len(df):,} samples with {len(df.columns)-2} features\n")

# Separate features and target
X = df.drop(['customer_id', 'churn_flag'], axis=1)
y = df['churn_flag']

print(f"Features: {X.shape[1]}")
print(f"Target distribution:")
print(f"  Not Churned (0): {(y==0).sum():,} ({(y==0).mean()*100:.2f}%)")
print(f"  Churned (1): {(y==1).sum():,} ({(y==1).mean()*100:.2f}%)")

# ============================================================================
# STEP 1: TRAIN-TEST SPLIT
# ============================================================================
print("\n" + "="*80)
print("STEP 1: TRAIN-TEST SPLIT")
print("="*80)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set: {len(X_train):,} samples")
print(f"Test set: {len(X_test):,} samples")
print(f"Train churn rate: {y_train.mean()*100:.2f}%")
print(f"Test churn rate: {y_test.mean()*100:.2f}%")

# ============================================================================
# STEP 2: FEATURE SCALING
# ============================================================================
print("\n" + "="*80)
print("STEP 2: FEATURE SCALING")
print("="*80)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\n[OK] Features scaled using StandardScaler")

# Save scaler
joblib.dump(scaler, 'models/feature_scaler.pkl')
print("[OK] Scaler saved to models/feature_scaler.pkl")

# ============================================================================
# STEP 3: HANDLE CLASS IMBALANCE WITH CLASS WEIGHTS
# ============================================================================
print("\n" + "="*80)
print("STEP 3: HANDLING CLASS IMBALANCE")
print("="*80)

print("\nCalculating class weights to handle imbalance...")
class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
class_weight_dict = {0: class_weights[0], 1: class_weights[1]}

print(f"\nClass distribution:")
print(f"  Class 0 (Not Churned): {(y_train==0).sum():,} samples")
print(f"  Class 1 (Churned): {(y_train==1).sum():,} samples")
print(f"\nClass weights:")
print(f"  Class 0: {class_weights[0]:.4f}")
print(f"  Class 1: {class_weights[1]:.4f}")

# Use original training data (no resampling needed with class weights)
X_train_balanced = X_train_scaled
y_train_balanced = y_train

# ============================================================================
# STEP 4: MODEL TRAINING & COMPARISON
# ============================================================================
print("\n" + "="*80)
print("STEP 4: MODEL TRAINING & COMPARISON")
print("="*80)

models = {
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
    'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100, class_weight='balanced'),
    'Gradient Boosting': GradientBoostingClassifier(random_state=42, n_estimators=100)
}

results = {}

for name, model in models.items():
    print(f"\nTraining {name}...")
    
    # Train model
    model.fit(X_train_balanced, y_train_balanced)
    
    # Predictions
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    results[name] = {
        'model': model,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc_auc,
        'y_pred': y_pred,
        'y_pred_proba': y_pred_proba
    }
    
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    print(f"  ROC-AUC: {roc_auc:.4f}")

# Select best model based on ROC-AUC
best_model_name = max(results, key=lambda x: results[x]['roc_auc'])
best_model = results[best_model_name]['model']

print(f"\n[OK] Best model: {best_model_name} (ROC-AUC: {results[best_model_name]['roc_auc']:.4f})")

# ============================================================================
# STEP 5: HYPERPARAMETER TUNING FOR BEST MODEL
# ============================================================================
print("\n" + "="*80)
print("STEP 5: HYPERPARAMETER TUNING")
print("="*80)

if best_model_name == 'Random Forest':
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
elif best_model_name == 'Gradient Boosting':
    param_grid = {
        'n_estimators': [100, 200],
        'learning_rate': [0.01, 0.1],
        'max_depth': [3, 5],
        'min_samples_split': [2, 5]
    }
else:
    param_grid = {
        'C': [0.1, 1, 10],
        'penalty': ['l2'],
        'solver': ['lbfgs']
    }

print(f"\nTuning {best_model_name}...")
print(f"Parameter grid: {param_grid}")

grid_search = GridSearchCV(
    best_model, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=0
)
grid_search.fit(X_train_balanced, y_train_balanced)

print(f"\n[OK] Best parameters: {grid_search.best_params_}")
print(f"[OK] Best CV ROC-AUC: {grid_search.best_score_:.4f}")

# Use tuned model
final_model = grid_search.best_estimator_

# ============================================================================
# STEP 6: FINAL MODEL EVALUATION
# ============================================================================
print("\n" + "="*80)
print("STEP 6: FINAL MODEL EVALUATION")
print("="*80)

# Predictions
y_pred_final = final_model.predict(X_test_scaled)
y_pred_proba_final = final_model.predict_proba(X_test_scaled)[:, 1]

# Calculate all metrics
accuracy_final = accuracy_score(y_test, y_pred_final)
precision_final = precision_score(y_test, y_pred_final)
recall_final = recall_score(y_test, y_pred_final)
f1_final = f1_score(y_test, y_pred_final)
roc_auc_final = roc_auc_score(y_test, y_pred_proba_final)

print("\nFINAL MODEL PERFORMANCE:")
print(f"  Accuracy:  {accuracy_final:.4f}")
print(f"  Precision: {precision_final:.4f}")
print(f"  Recall:    {recall_final:.4f}")
print(f"  F1-Score:  {f1_final:.4f}")
print(f"  ROC-AUC:   {roc_auc_final:.4f}")

# Classification report
print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred_final, target_names=['Not Churned', 'Churned']))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred_final)
print("\nConfusion Matrix:")
print(f"                 Predicted")
print(f"                 Not Churned  Churned")
print(f"Actual Not Churned    {cm[0,0]:5d}      {cm[0,1]:5d}")
print(f"Actual Churned        {cm[1,0]:5d}      {cm[1,1]:5d}")

# ============================================================================
# STEP 7: FEATURE IMPORTANCE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("STEP 7: FEATURE IMPORTANCE ANALYSIS")
print("="*80)

if hasattr(final_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Save feature importance
    feature_importance.to_csv('models/feature_importance.csv', index=False)
    print("\n[OK] Feature importance saved to models/feature_importance.csv")
else:
    print("\n[INFO] Model does not support feature importance")
    feature_importance = None

# ============================================================================
# STEP 8: SAVE MODEL AND RESULTS
# ============================================================================
print("\n" + "="*80)
print("STEP 8: SAVING MODEL AND RESULTS")
print("="*80)

# Save final model
joblib.dump(final_model, 'models/churn_model.pkl')
print("\n[OK] Model saved to models/churn_model.pkl")

# Save model metadata
model_metadata = {
    'model_type': best_model_name,
    'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'training_samples': int(len(X_train_balanced)),
    'test_samples': int(len(X_test)),
    'features': list(X.columns),
    'n_features': int(len(X.columns)),
    'best_parameters': {k: str(v) for k, v in grid_search.best_params_.items()},
    'performance_metrics': {
        'accuracy': float(accuracy_final),
        'precision': float(precision_final),
        'recall': float(recall_final),
        'f1_score': float(f1_final),
        'roc_auc': float(roc_auc_final)
    },
    'confusion_matrix': {
        'true_negatives': int(cm[0,0]),
        'false_positives': int(cm[0,1]),
        'false_negatives': int(cm[1,0]),
        'true_positives': int(cm[1,1])
    }
}

with open('models/model_metadata.json', 'w') as f:
    json.dump(model_metadata, f, indent=2)

print("[OK] Model metadata saved to models/model_metadata.json")

# Save predictions for analysis
predictions_df = pd.DataFrame({
    'customer_id': df.loc[X_test.index, 'customer_id'],
    'actual_churn': y_test,
    'predicted_churn': y_pred_final,
    'churn_probability': y_pred_proba_final
})
predictions_df.to_csv('models/test_predictions.csv', index=False)
print("[OK] Test predictions saved to models/test_predictions.csv")

# ============================================================================
# STEP 9: VISUALIZATIONS
# ============================================================================
print("\n" + "="*80)
print("STEP 9: GENERATING VISUALIZATIONS")
print("="*80)

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Confusion Matrix Heatmap
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0, 0],
            xticklabels=['Not Churned', 'Churned'],
            yticklabels=['Not Churned', 'Churned'])
axes[0, 0].set_title('Confusion Matrix', fontsize=14, fontweight='bold')
axes[0, 0].set_ylabel('Actual')
axes[0, 0].set_xlabel('Predicted')

# 2. ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_pred_proba_final)
axes[0, 1].plot(fpr, tpr, linewidth=2, label=f'ROC (AUC = {roc_auc_final:.3f})')
axes[0, 1].plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
axes[0, 1].set_xlabel('False Positive Rate')
axes[0, 1].set_ylabel('True Positive Rate')
axes[0, 1].set_title('ROC Curve', fontsize=14, fontweight='bold')
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.3)

# 3. Precision-Recall Curve
precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_pred_proba_final)
axes[1, 0].plot(recall_curve, precision_curve, linewidth=2)
axes[1, 0].set_xlabel('Recall')
axes[1, 0].set_ylabel('Precision')
axes[1, 0].set_title('Precision-Recall Curve', fontsize=14, fontweight='bold')
axes[1, 0].grid(alpha=0.3)

# 4. Feature Importance (if available)
if feature_importance is not None:
    top_features = feature_importance.head(10)
    axes[1, 1].barh(range(len(top_features)), top_features['importance'])
    axes[1, 1].set_yticks(range(len(top_features)))
    axes[1, 1].set_yticklabels(top_features['feature'])
    axes[1, 1].set_xlabel('Importance')
    axes[1, 1].set_title('Top 10 Feature Importance', fontsize=14, fontweight='bold')
    axes[1, 1].invert_yaxis()
else:
    axes[1, 1].text(0.5, 0.5, 'Feature importance\nnot available', 
                    ha='center', va='center', fontsize=12)
    axes[1, 1].set_title('Feature Importance', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('models/model_evaluation_plots.png', dpi=300, bbox_inches='tight')
print("\n[OK] Visualizations saved to models/model_evaluation_plots.png")
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("MODEL TRAINING SUMMARY")
print("="*80)

print(f"\nBest Model: {best_model_name}")
print(f"Training Samples: {len(X_train_balanced):,} (with class weights)")
print(f"Test Samples: {len(X_test):,}")
print(f"Number of Features: {len(X.columns)}")

print(f"\nPerformance on Test Set:")
print(f"  Precision: {precision_final:.4f} - Of predicted churners, {precision_final*100:.1f}% actually churned")
print(f"  Recall:    {recall_final:.4f} - Identified {recall_final*100:.1f}% of actual churners")
print(f"  F1-Score:  {f1_final:.4f} - Harmonic mean of precision and recall")
print(f"  ROC-AUC:   {roc_auc_final:.4f} - Overall discrimination ability")

if feature_importance is not None:
    print(f"\nTop 3 Churn Risk Factors:")
    for i, row in feature_importance.head(3).iterrows():
        print(f"  {i+1}. {row['feature']}: {row['importance']:.4f}")

print("\n" + "="*80)
print("[OK] MODEL TRAINING COMPLETE!")
print("="*80)
print("\nFiles created:")
print("  - models/churn_model.pkl")
print("  - models/feature_scaler.pkl")
print("  - models/model_metadata.json")
print("  - models/feature_importance.csv")
print("  - models/test_predictions.csv")
print("  - models/model_evaluation_plots.png")

# Made with Bob
