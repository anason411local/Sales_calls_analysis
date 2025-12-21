"""
STEP 5: SHAP (SHapley Additive exPlanations) ANALYSIS
Understanding feature interactions and non-linear contributions to call duration

SHAP provides:
- Individual feature contribution to each prediction
- Feature interaction effects
- Directional impact (positive/negative)
- Non-linear relationship insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import shap
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("SHAP ANALYSIS - FEATURE CONTRIBUTION & INTERACTIONS")
print("="*100)

# Load data
df_combined = pd.read_csv('analysis_outputs/02_combined_encoded.csv')
df_combined_ranking = pd.read_csv('analysis_outputs/04_combined_feature_ranking.csv')

print(f"\nData loaded: {df_combined.shape}")

# Prepare data
X = df_combined.drop('call_duration_group', axis=1)
y = (df_combined['call_duration_group'] == 'Long (>4.88 min)').astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

print(f"Training: {X_train.shape[0]}, Test: {X_test.shape[0]}")

# Get top 50 features for SHAP (analyzing all 150 would be too slow)
top_50_features = df_combined_ranking.head(50)['Feature'].tolist()
X_train_top50 = X_train[top_50_features]
X_test_top50 = X_test[top_50_features]

print(f"\nUsing top 50 features for SHAP analysis")

# ==================================================================================
# SHAP ANALYSIS - RANDOM FOREST
# ==================================================================================

print("\n" + "="*100)
print("SHAP ANALYSIS - RANDOM FOREST")
print("="*100)

print("\nTraining Random Forest model...")
rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=20,
                                  min_samples_leaf=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train_top50, y_train)

test_acc = rf_model.score(X_test_top50, y_test)
print(f"Test Accuracy: {test_acc:.4f}")

print("\nCalculating SHAP values (this may take a few minutes)...")
explainer_rf = shap.TreeExplainer(rf_model)

# Sample for faster computation
sample_size = min(300, len(X_test_top50))
X_test_sample = X_test_top50.sample(sample_size, random_state=42)
shap_values_rf = explainer_rf.shap_values(X_test_sample)

# Handle binary classification output
if isinstance(shap_values_rf, list):
    shap_values_rf_class1 = shap_values_rf[1]  # Class 1 = Long calls
else:
    shap_values_rf_class1 = shap_values_rf

print(f"[OK] SHAP values calculated for {sample_size} samples")

# Calculate mean absolute SHAP values (feature importance)
if len(shap_values_rf_class1.shape) == 2:
    mean_abs_shap_rf = np.abs(shap_values_rf_class1).mean(axis=0)
elif len(shap_values_rf_class1.shape) == 3:
    mean_abs_shap_rf = np.abs(shap_values_rf_class1[:, :, 0]).mean(axis=0)
else:
    mean_abs_shap_rf = np.abs(shap_values_rf_class1).flatten()

shap_importance_rf = pd.DataFrame({
    'Feature': X_test_sample.columns.tolist(),
    'Mean_Abs_SHAP': mean_abs_shap_rf.flatten() if hasattr(mean_abs_shap_rf, 'flatten') else mean_abs_shap_rf
}).sort_values('Mean_Abs_SHAP', ascending=False)

shap_importance_rf.to_csv('analysis_outputs/05_shap_importance_random_forest.csv', index=False)
print("\n[OK] Saved: 05_shap_importance_random_forest.csv")

print("\nTop 20 Features by SHAP Importance:")
print("-" * 80)
print(shap_importance_rf.head(20).to_string(index=False))

# ==================================================================================
# SHAP ANALYSIS - GRADIENT BOOSTING
# ==================================================================================

print("\n" + "="*100)
print("SHAP ANALYSIS - GRADIENT BOOSTING")
print("="*100)

print("\nTraining Gradient Boosting model...")
gb_model = GradientBoostingClassifier(n_estimators=100, max_depth=5, learning_rate=0.1,
                                      min_samples_split=20, min_samples_leaf=10, random_state=42)
gb_model.fit(X_train_top50, y_train)

test_acc_gb = gb_model.score(X_test_top50, y_test)
print(f"Test Accuracy: {test_acc_gb:.4f}")

print("\nCalculating SHAP values...")
explainer_gb = shap.TreeExplainer(gb_model)
shap_values_gb = explainer_gb.shap_values(X_test_sample)

# Handle GB output (usually single array for binary)
if isinstance(shap_values_gb, list):
    shap_values_gb_class1 = shap_values_gb[1]
else:
    shap_values_gb_class1 = shap_values_gb

print(f"[OK] SHAP values calculated")

# Calculate mean absolute SHAP values
if len(shap_values_gb_class1.shape) == 3:
    mean_abs_shap_gb = np.abs(shap_values_gb_class1[:, :, 0]).mean(axis=0)
elif len(shap_values_gb_class1.shape) == 2:
    mean_abs_shap_gb = np.abs(shap_values_gb_class1).mean(axis=0)
else:
    mean_abs_shap_gb = np.abs(shap_values_gb_class1).flatten()

shap_importance_gb = pd.DataFrame({
    'Feature': X_test_sample.columns.tolist(),
    'Mean_Abs_SHAP': mean_abs_shap_gb.flatten() if hasattr(mean_abs_shap_gb, 'flatten') else mean_abs_shap_gb
}).sort_values('Mean_Abs_SHAP', ascending=False)

shap_importance_gb.to_csv('analysis_outputs/05_shap_importance_gradient_boosting.csv', index=False)
print("\n[OK] Saved: 05_shap_importance_gradient_boosting.csv")

print("\nTop 20 Features by SHAP Importance:")
print("-" * 80)
print(shap_importance_gb.head(20).to_string(index=False))

# ==================================================================================
# COMBINED SHAP IMPORTANCE
# ==================================================================================

print("\n" + "="*100)
print("COMBINED SHAP IMPORTANCE")
print("="*100)

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

combined_shap.to_csv('analysis_outputs/05_shap_combined_importance.csv', index=False)
print("\n[OK] Saved: 05_shap_combined_importance.csv")

print("\nTop 25 Features by Combined SHAP:")
print("-" * 80)
print(combined_shap[['Feature', 'Mean_Abs_SHAP_RF', 'Mean_Abs_SHAP_GB', 'Combined_SHAP_Score']].head(25).to_string(index=False))

# ==================================================================================
# CREATE SHAP VISUALIZATIONS
# ==================================================================================

print("\n" + "="*100)
print("CREATING SHAP VISUALIZATIONS")
print("="*100)

# VIZ 1: SHAP Summary Plot - Random Forest
print("\n1. Creating SHAP summary plot (Random Forest)...")
fig, ax = plt.subplots(figsize=(12, 16))
shap.summary_plot(shap_values_rf_class1, X_test_sample, plot_type="dot",
                  show=False, max_display=30)
plt.title('SHAP Summary Plot - Random Forest (Top 30 Features)\nPredicting Long Calls (>4.88 min)', 
         fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('analysis_outputs/shap_viz_01_summary_random_forest.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: shap_viz_01_summary_random_forest.png")
plt.close()

# VIZ 2: SHAP Summary Plot - Gradient Boosting
print("\n2. Creating SHAP summary plot (Gradient Boosting)...")
fig, ax = plt.subplots(figsize=(12, 16))
shap.summary_plot(shap_values_gb_class1, X_test_sample, plot_type="dot",
                  show=False, max_display=30)
plt.title('SHAP Summary Plot - Gradient Boosting (Top 30 Features)\nPredicting Long Calls (>4.88 min)', 
         fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('analysis_outputs/shap_viz_02_summary_gradient_boosting.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: shap_viz_02_summary_gradient_boosting.png")
plt.close()

# VIZ 3: SHAP Bar Plot Comparison
print("\n3. Creating SHAP importance bar plots...")
fig, axes = plt.subplots(1, 2, figsize=(18, 10))

# RF Bar Plot
ax1 = axes[0]
top_20_rf = shap_importance_rf.head(20)
bars1 = ax1.barh(range(len(top_20_rf)), top_20_rf['Mean_Abs_SHAP'],
                color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
ax1.set_yticks(range(len(top_20_rf)))
ax1.set_yticklabels([f.replace('_target_enc', '').replace('_freq_enc', '')[:35] 
                     for f in top_20_rf['Feature']], fontsize=10)
ax1.set_xlabel('Mean |SHAP Value|', fontsize=12, fontweight='bold')
ax1.set_title('Random Forest\nTop 20 Features by SHAP Importance', 
             fontsize=13, fontweight='bold', pad=15)
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)

# GB Bar Plot
ax2 = axes[1]
top_20_gb = shap_importance_gb.head(20)
bars2 = ax2.barh(range(len(top_20_gb)), top_20_gb['Mean_Abs_SHAP'],
                color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.set_yticks(range(len(top_20_gb)))
ax2.set_yticklabels([f.replace('_target_enc', '').replace('_freq_enc', '')[:35]
                     for f in top_20_gb['Feature']], fontsize=10)
ax2.set_xlabel('Mean |SHAP Value|', fontsize=12, fontweight='bold')
ax2.set_title('Gradient Boosting\nTop 20 Features by SHAP Importance', 
             fontsize=13, fontweight='bold', pad=15)
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)

plt.suptitle('SHAP Feature Importance Comparison', fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('analysis_outputs/shap_viz_03_importance_comparison.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: shap_viz_03_importance_comparison.png")
plt.close()

# VIZ 4: SHAP Waterfall Plot for a sample prediction
print("\n4. Creating SHAP waterfall plot (example prediction)...")
# Pick an interesting sample (a long call with high prediction confidence)
# Get the actual y_test values for the sampled indices - use reset_index to align
y_test_reset = y_test.reset_index(drop=True)
X_test_top50_reset = X_test_top50.reset_index(drop=True)
X_test_sample_reset = X_test_sample.reset_index(drop=True)

# Find which indices in X_test_sample correspond to long calls
long_call_mask = []
for idx in X_test_sample.index:
    # Find position in original X_test_top50
    pos = X_test_top50.index.get_loc(idx)
    long_call_mask.append(y_test.iloc[pos] == 1)

long_call_indices = [i for i, is_long in enumerate(long_call_mask) if is_long]

if len(long_call_indices) > 0:
    long_call_idx = long_call_indices[0]

    fig, ax = plt.subplots(figsize=(10, 12))
    shap.waterfall_plot(
        shap.Explanation(
            values=shap_values_rf_class1[long_call_idx],
            base_values=explainer_rf.expected_value[1] if isinstance(explainer_rf.expected_value, np.ndarray) else explainer_rf.expected_value,
            data=X_test_sample_reset.iloc[long_call_idx].values,
            feature_names=[f.replace('_target_enc', '').replace('_freq_enc', '')[:30] for f in X_test_sample_reset.columns]
        ),
        show=False,
        max_display=20
    )
    plt.title('SHAP Waterfall Plot - Example Long Call Prediction\nTop 20 Contributing Features', 
             fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig('analysis_outputs/shap_viz_04_waterfall_example.png', dpi=300, bbox_inches='tight')
    print("   [OK] Saved: shap_viz_04_waterfall_example.png")
    plt.close()
else:
    print("   [SKIPPED] No long call samples found in test set for waterfall plot")

print("\n" + "="*100)
print("SHAP ANALYSIS COMPLETE")
print("="*100)

print("\nKEY SHAP INSIGHTS:")
print("- SHAP values show actual impact of each feature on predictions")
print("- Positive SHAP = pushes toward LONG calls")
print("- Negative SHAP = pushes toward SHORT calls")
print("- Color in summary plots = feature value (red=high, blue=low)")
print("- SHAP captures non-linear effects and feature interactions")

print("\nFILES CREATED:")
print("  - 05_shap_importance_random_forest.csv")
print("  - 05_shap_importance_gradient_boosting.csv")
print("  - 05_shap_combined_importance.csv")
print("  - shap_viz_01_summary_random_forest.png")
print("  - shap_viz_02_summary_gradient_boosting.png")
print("  - shap_viz_03_importance_comparison.png")
print("  - shap_viz_04_waterfall_example.png")

