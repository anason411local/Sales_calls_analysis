"""
==============================================================================
LEVEL 2: VALUE-LEVEL SHAP ANALYSIS
==============================================================================

Purpose: SHAP analysis for value-level features
- Explain which SPECIFIC VALUES matter most
- ALL SHAP chart types with reading guides
- Uses value-level ML models from script 09

==============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
import joblib
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')

print("="*100)
print("LEVEL 2: VALUE-LEVEL SHAP ANALYSIS")
print("="*100)

# ==============================================================================
# LOAD MODELS AND DATA
# ==============================================================================

print("\nLoading models...")
rf_model = joblib.load('analysis_outputs/level2_value/09_model_rf_values.pkl')
gb_model = joblib.load('analysis_outputs/level2_value/09_model_gb_values.pkl')

# Reconstruct X from top values
df = pd.read_csv('analysis_outputs/level1_variable/01_combined_original.csv')
df_value_analysis = pd.read_csv('analysis_outputs/level2_value/07_categorical_value_analysis.csv')

top_values = df_value_analysis.nlargest(100, 'Importance_Score')

X = pd.DataFrame()
for idx, row in top_values.iterrows():
    var = row['Variable']
    value = row['Value']
    feature_name = f"{var}_{value}"[:50]
    X[feature_name] = (df[var].astype(str) == value).astype(int)

print(f"Features: {X.shape}")

# Sample for SHAP
sample_size = min(300, len(X))
np.random.seed(42)
X_sample = X.sample(sample_size, random_state=42)

print(f"SHAP sample: {len(X_sample)}")

# ==============================================================================
# SHAP: RANDOM FOREST
# ==============================================================================

print("\n" + "="*100)
print("SHAP ANALYSIS: RANDOM FOREST (VALUE-LEVEL)")
print("="*100)

explainer_rf = shap.TreeExplainer(rf_model)
shap_values_rf = explainer_rf.shap_values(X_sample)

# Handle binary classification
if isinstance(shap_values_rf, np.ndarray) and len(shap_values_rf.shape) == 3:
    shap_values_rf = shap_values_rf[:, :, 1]
elif isinstance(shap_values_rf, list):
    shap_values_rf = shap_values_rf[1]

print(f"[OK] SHAP values: {shap_values_rf.shape}")

# ==============================================================================
# SHAP CHART 1: SUMMARY PLOT
# ==============================================================================

print("\nCreating Summary Plot...")

fig, ax = plt.subplots(figsize=(14, 12))

shap.summary_plot(shap_values_rf, X_sample,
                  max_display=30,
                  show=False)

guide = """
HOW TO READ (VALUE-LEVEL):
━━━━━━━━━━━━━━━━━━━━━━━━
• Y-axis: Specific VALUES (not variables)
• Shows which timezone value, 
  sentiment value, etc. matters
• Example: "timezone_Mountain" vs
  "timezone_Eastern"
"""

plt.text(1.02, 0.5, guide, transform=ax.transAxes,
         fontsize=9, verticalalignment='center',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
         family='monospace')

plt.title('LEVEL 2: VALUE-LEVEL SHAP SUMMARY (Random Forest)\n' +
          'Shows which SPECIFIC VALUES push calls toward Short vs Long\n' +
          f'Based on {len(X_sample)} sample calls | Top 100 discriminative values',
          fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('analysis_outputs/level2_value/shap_11_rf_summary_values.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_11_rf_summary_values.png")
plt.close()

# ==============================================================================
# SHAP CHART 2: BAR PLOT
# ==============================================================================

print("Creating Bar Plot...")

fig, ax = plt.subplots(figsize=(12, 10))

shap.summary_plot(shap_values_rf, X_sample,
                  plot_type='bar',
                  max_display=30,
                  show=False)

plt.title('LEVEL 2: VALUE IMPORTANCE (Random Forest SHAP)\n' +
          'Shows which specific values matter most for predictions\n' +
          f'Top 30 of {len(X.columns)} value features',
          fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('analysis_outputs/level2_value/shap_11_rf_importance_bar_values.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_11_rf_importance_bar_values.png")
plt.close()

# ==============================================================================
# SAVE SHAP IMPORTANCE
# ==============================================================================

print("\nSaving SHAP importance values...")

mean_abs_shap = np.abs(shap_values_rf).mean(axis=0)

shap_importance = pd.DataFrame({
    'Value_Feature': X.columns,
    'SHAP_Importance': mean_abs_shap
}).sort_values('SHAP_Importance', ascending=False)

shap_importance.to_csv('analysis_outputs/level2_value/11_shap_importance_values.csv', index=False)
print("[OK] Saved: 11_shap_importance_values.csv")

print("\nTop 20 value features by SHAP:")
for idx, row in shap_importance.head(20).iterrows():
    print(f"  {row['Value_Feature']}: {row['SHAP_Importance']:.4f}")

print("\n" + "="*100)
print("LEVEL 2 SHAP ANALYSIS COMPLETE")
print("="*100)
print(f"\n[OK] Analyzed {len(X.columns)} value features")
print(f"[OK] Created 2 SHAP visualizations with reading guides")
print(f"[OK] Top value: {shap_importance.iloc[0]['Value_Feature']}")

