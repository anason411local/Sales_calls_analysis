"""
SHAP VALUES ANALYSIS
Interpreting ML model predictions using SHAP (SHapley Additive exPlanations)
Analyzing top 50 most important features
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import shap
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("SHAP VALUES ANALYSIS - TOP 50 FEATURES")
print("="*100)

# Load data and feature importance
df_combined = pd.read_csv('analysis_outputs/enhanced_combined_data.csv')
feature_importance = pd.read_csv('analysis_outputs/combined_feature_importance.csv')

# Get top 50 features
top_50_features = feature_importance.head(50)['Variable'].tolist()

print(f"\nAnalyzing top 50 features out of {len(feature_importance)}")
print(f"These features account for majority of predictive power")

# Prepare data
df_ml = df_combined.copy()

# Handle missing values
for col in df_ml.select_dtypes(include=[np.number]).columns:
    if col != 'call_duration_group':
        df_ml[col].fillna(df_ml[col].median(), inplace=True)

# Encode categorical
label_encoders = {}
for col in df_ml.select_dtypes(include=['object', 'bool']).columns:
    if col != 'call_duration_group':
        le = LabelEncoder()
        df_ml[col] = df_ml[col].astype(str)
        df_ml[col] = le.fit_transform(df_ml[col])
        label_encoders[col] = le

# Prepare features and target - FILTER TO TOP 50
X_full = df_ml.drop('call_duration_group', axis=1)
y = df_ml['call_duration_group']

# Filter to top 50 features only
available_features = [f for f in top_50_features if f in X_full.columns]
X = X_full[available_features]

print(f"\nUsing {len(available_features)} features for SHAP analysis")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

print(f"Training set: {X_train.shape}")
print(f"Test set: {X_test.shape}")

# ==================================================================================
# RANDOM FOREST SHAP ANALYSIS
# ==================================================================================
print("\n" + "="*100)
print("SHAP ANALYSIS - RANDOM FOREST")
print("="*100)

print("\nTraining Random Forest model...")
rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=20,
                                  min_samples_leaf=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

print("Calculating SHAP values (this may take a few minutes)...")

# Use TreeExplainer for tree-based models (much faster)
explainer_rf = shap.TreeExplainer(rf_model)

# Calculate SHAP values on a sample of test data (for speed)
sample_size = min(300, len(X_test))
X_test_sample = X_test.sample(sample_size, random_state=42)
shap_values_rf = explainer_rf.shap_values(X_test_sample)

# For binary classification, shap_values is a list of 2 arrays
# We use the positive class (Long Calls = 1)
if isinstance(shap_values_rf, list):
    shap_values_rf_class1 = shap_values_rf[1]
else:
    shap_values_rf_class1 = shap_values_rf

print(f"[OK] SHAP values calculated for {sample_size} test samples")
print(f"Debug - SHAP values shape: {shap_values_rf_class1.shape if hasattr(shap_values_rf_class1, 'shape') else 'N/A'}")

# Create SHAP summary plot
print("\nCreating SHAP summary plot for Random Forest...")
fig, ax = plt.subplots(figsize=(12, 16))
shap.summary_plot(shap_values_rf_class1, X_test_sample, plot_type="dot", 
                  show=False, max_display=30)
plt.title('SHAP Summary Plot - Random Forest (Top 30 Features)\nPredicting Long Calls (>4.88 min)', 
         fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('analysis_outputs/shap_01_summary_random_forest.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_01_summary_random_forest.png")
plt.close()

# SHAP Feature Importance (mean absolute SHAP value)
# The shape might be (n_samples, n_features) or (n_samples, n_features, 2) for binary classification
if len(shap_values_rf_class1.shape) == 3:
    # If 3D, take one class (already done above, but double-check)
    mean_abs_shap_rf = np.abs(shap_values_rf_class1[:, :, 0]).mean(axis=0)
elif len(shap_values_rf_class1.shape) == 2:
    # Standard 2D case
    mean_abs_shap_rf = np.abs(shap_values_rf_class1).mean(axis=0)
else:
    raise ValueError(f"Unexpected SHAP values shape: {shap_values_rf_class1.shape}")

print(f"Debug - mean_abs_shap_rf shape after processing: {mean_abs_shap_rf.shape}")

shap_importance_rf = pd.DataFrame({
    'Feature': X_test_sample.columns.tolist(),
    'Mean_Abs_SHAP': mean_abs_shap_rf
}).sort_values('Mean_Abs_SHAP', ascending=False)

shap_importance_rf.to_csv('analysis_outputs/shap_feature_importance_rf.csv', index=False)
print("[OK] Saved: shap_feature_importance_rf.csv")

print("\nTop 20 Features by SHAP Importance (Random Forest):")
print("-" * 80)
print(shap_importance_rf.head(20).to_string(index=False))

# ==================================================================================
# GRADIENT BOOSTING SHAP ANALYSIS
# ==================================================================================
print("\n" + "="*100)
print("SHAP ANALYSIS - GRADIENT BOOSTING")
print("="*100)

print("\nTraining Gradient Boosting model...")
gb_model = GradientBoostingClassifier(n_estimators=100, max_depth=5, learning_rate=0.1,
                                      min_samples_split=20, min_samples_leaf=10, random_state=42)
gb_model.fit(X_train, y_train)

print("Calculating SHAP values...")
explainer_gb = shap.TreeExplainer(gb_model)
shap_values_gb = explainer_gb.shap_values(X_test_sample)

# For binary classification with GB, use the appropriate array
if isinstance(shap_values_gb, list):
    shap_values_gb_class1 = shap_values_gb[1]
else:
    # Gradient Boosting returns single array for binary
    shap_values_gb_class1 = shap_values_gb

print(f"[OK] SHAP values calculated")

# Create SHAP summary plot
print("\nCreating SHAP summary plot for Gradient Boosting...")
fig, ax = plt.subplots(figsize=(12, 16))
shap.summary_plot(shap_values_gb_class1, X_test_sample, plot_type="dot", 
                  show=False, max_display=30)
plt.title('SHAP Summary Plot - Gradient Boosting (Top 30 Features)\nPredicting Long Calls (>4.88 min)', 
         fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('analysis_outputs/shap_02_summary_gradient_boosting.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_02_summary_gradient_boosting.png")
plt.close()

# SHAP Feature Importance
# Handle potential 3D or 2D arrays
if len(shap_values_gb_class1.shape) == 3:
    mean_abs_shap_gb = np.abs(shap_values_gb_class1[:, :, 0]).mean(axis=0)
elif len(shap_values_gb_class1.shape) == 2:
    mean_abs_shap_gb = np.abs(shap_values_gb_class1).mean(axis=0)
else:
    raise ValueError(f"Unexpected SHAP values shape: {shap_values_gb_class1.shape}")

shap_importance_gb = pd.DataFrame({
    'Feature': X_test_sample.columns.tolist(),
    'Mean_Abs_SHAP': mean_abs_shap_gb
}).sort_values('Mean_Abs_SHAP', ascending=False)

shap_importance_gb.to_csv('analysis_outputs/shap_feature_importance_gb.csv', index=False)
print("[OK] Saved: shap_feature_importance_gb.csv")

print("\nTop 20 Features by SHAP Importance (Gradient Boosting):")
print("-" * 80)
print(shap_importance_gb.head(20).to_string(index=False))

# ==================================================================================
# CREATE SHAP BAR PLOTS
# ==================================================================================
print("\n" + "="*100)
print("CREATING SHAP BAR PLOTS")
print("="*100)

fig, axes = plt.subplots(1, 2, figsize=(18, 10))

# RF Bar Plot
ax1 = axes[0]
top_20_rf = shap_importance_rf.head(20)
ax1.barh(range(len(top_20_rf)), top_20_rf['Mean_Abs_SHAP'], 
        color='#3498db', alpha=0.8, edgecolor='black')
ax1.set_yticks(range(len(top_20_rf)))
ax1.set_yticklabels(top_20_rf['Feature'], fontsize=10)
ax1.set_xlabel('Mean |SHAP Value|', fontsize=12, fontweight='bold')
ax1.set_title('Random Forest\nTop 20 Features by SHAP Importance', 
             fontsize=13, fontweight='bold', pad=15)
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)

# GB Bar Plot
ax2 = axes[1]
top_20_gb = shap_importance_gb.head(20)
ax2.barh(range(len(top_20_gb)), top_20_gb['Mean_Abs_SHAP'], 
        color='#2ecc71', alpha=0.8, edgecolor='black')
ax2.set_yticks(range(len(top_20_gb)))
ax2.set_yticklabels(top_20_gb['Feature'], fontsize=10)
ax2.set_xlabel('Mean |SHAP Value|', fontsize=12, fontweight='bold')
ax2.set_title('Gradient Boosting\nTop 20 Features by SHAP Importance', 
             fontsize=13, fontweight='bold', pad=15)
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)

plt.suptitle('SHAP Feature Importance Comparison', fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('analysis_outputs/shap_03_feature_importance_comparison.png', dpi=300, bbox_inches='tight')
print("\n[OK] Saved: shap_03_feature_importance_comparison.png")
plt.close()

# ==================================================================================
# COMBINED SHAP IMPORTANCE
# ==================================================================================
print("\n" + "="*100)
print("COMBINED SHAP IMPORTANCE RANKING")
print("="*100)

# Merge both SHAP importance rankings
combined_shap = shap_importance_rf.merge(
    shap_importance_gb, on='Feature', how='outer', 
    suffixes=('_RF', '_GB')
)

combined_shap['Mean_Abs_SHAP_RF'] = combined_shap['Mean_Abs_SHAP_RF'].fillna(0)
combined_shap['Mean_Abs_SHAP_GB'] = combined_shap['Mean_Abs_SHAP_GB'].fillna(0)

# Normalize and combine
max_rf = combined_shap['Mean_Abs_SHAP_RF'].max()
max_gb = combined_shap['Mean_Abs_SHAP_GB'].max()

combined_shap['RF_Norm'] = combined_shap['Mean_Abs_SHAP_RF'] / max_rf if max_rf > 0 else 0
combined_shap['GB_Norm'] = combined_shap['Mean_Abs_SHAP_GB'] / max_gb if max_gb > 0 else 0

combined_shap['Combined_SHAP_Score'] = (combined_shap['RF_Norm'] + combined_shap['GB_Norm']) / 2

combined_shap = combined_shap.sort_values('Combined_SHAP_Score', ascending=False)

combined_shap.to_csv('analysis_outputs/shap_combined_importance.csv', index=False)
print("\n[OK] Saved: shap_combined_importance.csv")

print("\nTop 25 Features by Combined SHAP Importance:")
print("-" * 100)
display_cols = ['Feature', 'Mean_Abs_SHAP_RF', 'Mean_Abs_SHAP_GB', 'Combined_SHAP_Score']
print(combined_shap[display_cols].head(25).to_string(index=False))

print("\n" + "="*100)
print("SHAP ANALYSIS COMPLETE")
print("="*100)
print("\nKEY INSIGHTS:")
print("- SHAP values show the actual impact of each feature on predictions")
print("- Positive SHAP = pushes prediction toward LONG calls")
print("- Negative SHAP = pushes prediction toward SHORT calls")
print("- Feature importance + SHAP gives complete picture of variable impact")

