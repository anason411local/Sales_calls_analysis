"""
==============================================================================
LEVEL 1: VARIABLE-LEVEL SHAP ANALYSIS
==============================================================================

Purpose: Explain ML model predictions using SHAP
- Generate ALL SHAP chart types
- Add clear reading guides on each chart
- Analyze variable contributions and interactions
- Both Random Forest and Gradient Boosting models

SHAP Charts Included:
1. Summary Plot (Beeswarm) - Overall feature impact
2. Bar Plot - Feature importance ranking
3. Waterfall Plot - Individual prediction explanation
4. Force Plot - Visual explanation
5. Dependence Plot - Feature interactions

==============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import joblib
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')

print("="*100)
print("LEVEL 1: VARIABLE-LEVEL SHAP ANALYSIS")
print("="*100)

# ==============================================================================
# LOAD MODELS AND DATA
# ==============================================================================

print("\nLoading models and data...")
rf_model = joblib.load('analysis_outputs/level1_variable/03_model_random_forest.pkl')
xgb_model = joblib.load('analysis_outputs/level1_variable/03_model_xgboost.pkl')

df = pd.read_csv('analysis_outputs/level1_variable/01_combined_original.csv')

# Get features
feature_cols = [c for c in df.columns if c not in ['target', 'call_duration_group']]

# Prepare X (encoded as in feature importance script)
from sklearn.preprocessing import LabelEncoder

X = df[feature_cols].copy()
label_encoders = {}

for col in X.columns:
    if X[col].dtype == 'object' or X[col].dtype == 'bool':
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le

for col in X.columns:
    if X[col].isna().any():
        X[col].fillna(X[col].median(), inplace=True)

print(f"Features: {X.shape[1]}")
print(f"Samples: {X.shape[0]}")

# Sample for SHAP (500 from EACH dataset for balanced representation)
np.random.seed(42)

# Get indices for each class
short_indices = np.where(df['target'] == 0)[0]
long_indices = np.where(df['target'] == 1)[0]

# Sample 500 from each
sample_size_per_class = 500
short_sample = np.random.choice(short_indices, min(sample_size_per_class, len(short_indices)), replace=False)
long_sample = np.random.choice(long_indices, min(sample_size_per_class, len(long_indices)), replace=False)

# Combine samples
sample_indices = np.concatenate([short_sample, long_sample])
np.random.shuffle(sample_indices)  # Shuffle to mix them

X_sample = X.iloc[sample_indices]

print(f"SHAP sample size: {len(X_sample)} (500 short + 500 long calls)")
print(f"  - Short calls: {sum(df.iloc[sample_indices]['target'] == 0)}")
print(f"  - Long calls: {sum(df.iloc[sample_indices]['target'] == 1)}")

# ==============================================================================
# SHAP ANALYSIS: RANDOM FOREST
# ==============================================================================

print("\n" + "="*100)
print("SHAP ANALYSIS: RANDOM FOREST")
print("="*100)

print("Creating SHAP explainer...")
explainer_rf = shap.TreeExplainer(rf_model)

print("Calculating SHAP values...")
shap_values_rf = explainer_rf.shap_values(X_sample)

# For binary classification RandomForest, SHAP returns 3D array (samples, features, classes)
# We want the positive class (Long calls = class 1)
if isinstance(shap_values_rf, np.ndarray) and len(shap_values_rf.shape) == 3:
    shap_values_rf = shap_values_rf[:, :, 1]  # Take positive class
elif isinstance(shap_values_rf, list):
    shap_values_rf = shap_values_rf[1]

print(f"[OK] SHAP values calculated: {shap_values_rf.shape}")

# ==============================================================================
# SHAP CHART 1: SUMMARY PLOT (BEESWARM)
# ==============================================================================

print("\nCreating Chart 1/5: Summary Plot (Beeswarm)...")

fig, ax = plt.subplots(figsize=(16, 16))

shap.summary_plot(shap_values_rf, X_sample, 
                  feature_names=feature_cols,
                  max_display=30,
                  show=False)

# Add values at the LEFT side (away from the Low-High scale)
# Get mean absolute SHAP for each feature
mean_abs_shap = np.abs(shap_values_rf).mean(axis=0)
feature_order = np.argsort(mean_abs_shap)[-30:][::-1]  # Top 30 features in order

# Get current axis limits
xlim = ax.get_xlim()
ylim = ax.get_ylim()

# Add value labels on the FAR LEFT side (away from variable names AND color scale)
for i, feat_idx in enumerate(feature_order):
    value = mean_abs_shap[feat_idx]
    # Position FAR left to avoid overlap with variable names
    ax.text(xlim[0] - (xlim[1] - xlim[0]) * 0.40, 30 - i - 1, f'{value:.3f}', 
            va='center', ha='right', fontsize=7, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.9, edgecolor='black', linewidth=0.5))

plt.title('LEVEL 1: VARIABLE-LEVEL SHAP SUMMARY (Random Forest)\n' +
          'Shows which variables push calls toward Short vs Long duration\n' +
          f'Based on {len(X_sample)} sample calls (500 short + 500 long)',
          fontsize=14, fontweight='bold', pad=20)

# Add reading guide at bottom with spacing
guide_text = """HOW TO READ THIS SHAP SUMMARY PLOT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Y-axis: Variables ranked by importance (top = most important) | X-axis: SHAP value (impact on prediction)
• Positive (right) = Pushes toward LONG calls | Negative (left) = Pushes toward SHORT calls
• Each dot = One call | Color: Feature value (Red = High, Blue = Low) | Values on LEFT = Mean |SHAP|
EXAMPLE: If "customer_talk_percentage" has Red dots on right = High percentage → Long calls"""

fig.text(0.5, -0.02, guide_text, ha='center', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, edgecolor='black'), family='monospace')

plt.tight_layout()
plt.subplots_adjust(bottom=0.12, left=0.25)  # More space for labels on LEFT
plt.savefig('analysis_outputs/level1_variable/shap_05_rf_summary_beeswarm.png', 
            dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_05_rf_summary_beeswarm.png")
plt.close()

# ==============================================================================
# SHAP CHART 2: BAR PLOT (FEATURE IMPORTANCE)
# ==============================================================================

print("\nCreating Chart 2/5: Bar Plot (Feature Importance)...")

fig, ax = plt.subplots(figsize=(14, 14))

shap.summary_plot(shap_values_rf, X_sample,
                  feature_names=feature_cols,
                  plot_type='bar',
                  max_display=30,
                  show=False)

# Add values at the end of bars
mean_abs_shap = np.abs(shap_values_rf).mean(axis=0)
feature_order = np.argsort(mean_abs_shap)[-30:][::-1]

xlim = ax.get_xlim()

for i, feat_idx in enumerate(feature_order):
    value = mean_abs_shap[feat_idx]
    ax.text(value + xlim[1] * 0.01, 30 - i - 1, f'{value:.3f}', 
            va='center', ha='left', fontsize=8, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.6))

plt.title('LEVEL 1: VARIABLE IMPORTANCE (Random Forest SHAP)\n' +
          'Mean |SHAP value| shows average impact on predictions\n' +
          f'Based on {len(X_sample)} sample calls (500 short + 500 long)',
          fontsize=14, fontweight='bold', pad=20)

# Add reading guide at bottom with spacing
guide_text = """HOW TO READ THIS SHAP BAR PLOT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Shows average absolute SHAP value | Higher value = More important variable
• Answers: "Which variables matter most for predicting call duration?"
• This is model-based importance (not just correlation) | Values shown at end of bars"""

fig.text(0.5, -0.02, guide_text, ha='center', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5, edgecolor='black'), family='monospace')

plt.tight_layout()
plt.subplots_adjust(bottom=0.10)  # More space for guide
plt.savefig('analysis_outputs/level1_variable/shap_05_rf_importance_bar.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_05_rf_importance_bar.png")
plt.close()

# ==============================================================================
# SHAP CHART 3: WATERFALL PLOT (INDIVIDUAL PREDICTION)
# ==============================================================================

print("\nCreating Chart 3/5: Waterfall Plot (Individual Explanation)...")

# Find interesting examples (one short, one long prediction)
y_sample = df.iloc[sample_indices]['target'].values
proba_sample = rf_model.predict_proba(X_sample)[:, 1]

# High confidence long call
long_idx = np.where((y_sample == 1) & (proba_sample > 0.7))[0]
if len(long_idx) > 0:
    example_long_idx = long_idx[0]
else:
    example_long_idx = np.argmax(proba_sample)

# High confidence short call
short_idx = np.where((y_sample == 0) & (proba_sample < 0.3))[0]
if len(short_idx) > 0:
    example_short_idx = short_idx[0]
else:
    example_short_idx = np.argmin(proba_sample)

# Create waterfall plots - INCREASED TO 25 VARIABLES
fig, axes = plt.subplots(2, 1, figsize=(16, 40))  # Increased height for 25 variables

# Get expected value
expected_value = explainer_rf.expected_value
if isinstance(expected_value, (list, np.ndarray)):
    expected_value = expected_value[1] if len(expected_value) > 1 else expected_value[0]

# Long call example
plt.sca(axes[0])
shap.waterfall_plot(
    shap.Explanation(values=shap_values_rf[example_long_idx],
                     base_values=expected_value,
                     data=X_sample.iloc[example_long_idx],
                     feature_names=feature_cols),
    max_display=25,  # CHANGED FROM 15 TO 25
    show=False
)
axes[0].set_title(f'RANDOM FOREST - LONG CALL Prediction (Actual: {"Long" if y_sample[example_long_idx] == 1 else "Short"})\n' +
                  f'Predicted Probability: {proba_sample[example_long_idx]:.1%}',
                  fontsize=11, fontweight='bold')  # Slightly smaller font

# Short call example
plt.sca(axes[1])
shap.waterfall_plot(
    shap.Explanation(values=shap_values_rf[example_short_idx],
                     base_values=expected_value,
                     data=X_sample.iloc[example_short_idx],
                     feature_names=feature_cols),
    max_display=25,  # CHANGED FROM 15 TO 25
    show=False
)
axes[1].set_title(f'RANDOM FOREST - SHORT CALL Prediction (Actual: {"Long" if y_sample[example_short_idx] == 1 else "Short"})\n' +
                  f'Predicted Probability: {proba_sample[example_short_idx]:.1%}',
                  fontsize=11, fontweight='bold')  # Slightly smaller font

# Add overall guide
fig.text(0.5, 0.01, 
         'HOW TO READ WATERFALL PLOTS:\n' +
         'Start from base value (E[f(x)]) → Each bar shows one variable\'s contribution → End at final prediction (f(x))\n' +
         'RED = Pushes toward Long calls | BLUE = Pushes toward Short calls | Bar length = Strength of effect',
         ha='center', fontsize=9,  # Slightly smaller font
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))

plt.tight_layout()
plt.subplots_adjust(bottom=0.02)  # Less bottom margin
plt.savefig('analysis_outputs/level1_variable/shap_05_rf_waterfall.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_05_rf_waterfall.png (25 variables)")
plt.close()

# ==============================================================================
# SHAP CHART 4: DEPENDENCE PLOTS (TOP 4 FEATURES)
# ==============================================================================

print("\nCreating Chart 4/5: Dependence Plots (Feature Interactions)...")

# Get top 4 features by mean |SHAP|
mean_abs_shap = np.abs(shap_values_rf).mean(axis=0)
top_4_indices = np.argsort(mean_abs_shap)[-4:][::-1]
top_4_features = [feature_cols[i] for i in top_4_indices]

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()

for idx, (feat_idx, feat_name) in enumerate(zip(top_4_indices, top_4_features)):
    ax = axes[idx]
    plt.sca(ax)
    
    shap.dependence_plot(feat_idx, shap_values_rf, X_sample,
                         feature_names=feature_cols,
                         show=False,
                         ax=ax)
    
    ax.set_title(f'{feat_name}\nShows how this variable affects predictions',
                 fontsize=11, fontweight='bold')

# Add reading guide
fig.text(0.5, 0.02,
         'HOW TO READ DEPENDENCE PLOTS:\n' +
         'X-axis: Variable value | Y-axis: SHAP value (impact on prediction) | Color: Interaction variable\n' +
         'Shows relationship between variable value and its impact. Helps identify thresholds and interactions.',
         ha='center', fontsize=10,
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

plt.suptitle('LEVEL 1: TOP 4 VARIABLE DEPENDENCE PLOTS (Random Forest)\n' +
             'Shows how variable values affect predictions and interactions',
             fontsize=14, fontweight='bold', y=0.98)

plt.tight_layout()
plt.subplots_adjust(bottom=0.08, top=0.94)
plt.savefig('analysis_outputs/level1_variable/shap_05_rf_dependence.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_05_rf_dependence.png")
plt.close()

# ==============================================================================
# SHAP ANALYSIS: XGBOOST (REPEAT)
# ==============================================================================

print("\n" + "="*100)
print("SHAP ANALYSIS: XGBOOST")
print("="*100)

print("Creating SHAP explainer...")
explainer_xgb = shap.TreeExplainer(xgb_model)

print("Calculating SHAP values...")
shap_values_xgb = explainer_xgb.shap_values(X_sample)

# Handle binary classification
if isinstance(shap_values_xgb, np.ndarray) and len(shap_values_xgb.shape) == 3:
    shap_values_xgb = shap_values_xgb[:, :, 1]
elif isinstance(shap_values_xgb, list):
    shap_values_xgb = shap_values_xgb[1]

print(f"[OK] SHAP values calculated: {shap_values_xgb.shape}")

# Create XGBoost summary plot
print("\nCreating XGBoost Summary Plot...")
fig, ax = plt.subplots(figsize=(16, 16))

shap.summary_plot(shap_values_xgb, X_sample,
                  feature_names=feature_cols,
                  max_display=30,
                  show=False)

# Add values at the LEFT side (away from color scale)
mean_abs_shap_xgb = np.abs(shap_values_xgb).mean(axis=0)
feature_order_xgb = np.argsort(mean_abs_shap_xgb)[-30:][::-1]

xlim = ax.get_xlim()

for i, feat_idx in enumerate(feature_order_xgb):
    value = mean_abs_shap_xgb[feat_idx]
    # Position FAR left to avoid overlap with variable names
    ax.text(xlim[0] - (xlim[1] - xlim[0]) * 0.40, 30 - i - 1, f'{value:.3f}', 
            va='center', ha='right', fontsize=7, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.9, edgecolor='black', linewidth=0.5))

plt.title('LEVEL 1: VARIABLE-LEVEL SHAP SUMMARY (XGBoost)\n' +
          'Shows which variables push calls toward Short vs Long duration\n' +
          f'Based on {len(X_sample)} sample calls (500 short + 500 long)',
          fontsize=14, fontweight='bold', pad=20)

# Add reading guide at bottom with spacing
guide_text = """HOW TO READ THIS SHAP SUMMARY PLOT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Y-axis: Variables ranked by importance | X-axis: SHAP value (impact on prediction)
• Positive (right) = LONG calls | Negative (left) = SHORT calls | Each dot = One call
• Color: Feature value (Red = High, Blue = Low) | Values on LEFT = Mean |SHAP|
This is from XGBoost model. Compare with Random Forest to find consistent patterns!"""

fig.text(0.5, -0.02, guide_text, ha='center', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, edgecolor='black'), family='monospace')

plt.tight_layout()
plt.subplots_adjust(bottom=0.12, left=0.25)  # More space for labels on LEFT
plt.savefig('analysis_outputs/level1_variable/shap_05_xgb_summary_beeswarm.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_05_xgb_summary_beeswarm.png")
plt.close()

# ==============================================================================
# XGBOOST BAR PLOT (FEATURE IMPORTANCE)
# ==============================================================================

print("\nCreating XGBoost Bar Plot...")
fig, ax = plt.subplots(figsize=(14, 14))

shap.summary_plot(shap_values_xgb, X_sample,
                  feature_names=feature_cols,
                  plot_type='bar',
                  max_display=30,
                  show=False)

# Add values at the end of bars
mean_abs_shap_xgb_bar = np.abs(shap_values_xgb).mean(axis=0)
feature_order_xgb_bar = np.argsort(mean_abs_shap_xgb_bar)[-30:][::-1]

xlim = ax.get_xlim()

for i, feat_idx in enumerate(feature_order_xgb_bar):
    value = mean_abs_shap_xgb_bar[feat_idx]
    ax.text(value + xlim[1] * 0.01, 30 - i - 1, f'{value:.3f}', 
            va='center', ha='left', fontsize=8, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.6))

plt.title('LEVEL 1: VARIABLE IMPORTANCE (XGBoost SHAP)\n' +
          'Mean |SHAP value| shows average impact on predictions\n' +
          f'Based on {len(X_sample)} sample calls (500 short + 500 long)',
          fontsize=14, fontweight='bold', pad=20)

# Add reading guide at bottom with spacing
guide_text = """HOW TO READ THIS SHAP BAR PLOT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Shows average absolute SHAP value | Higher value = More important variable
• Answers: "Which variables matter most for predicting call duration?"
• This is from XGBoost model | Values shown at end of bars"""

fig.text(0.5, -0.02, guide_text, ha='center', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5, edgecolor='black'), family='monospace')

plt.tight_layout()
plt.subplots_adjust(bottom=0.10)
plt.savefig('analysis_outputs/level1_variable/shap_05_xgb_importance_bar.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_05_xgb_importance_bar.png")
plt.close()

# ==============================================================================
# XGBOOST WATERFALL PLOTS (25 VARIABLES)
# ==============================================================================

print("\nCreating XGBoost Waterfall Plots (25 variables)...")

# Get predictions for XGBoost
proba_sample_xgb = xgb_model.predict_proba(X_sample)[:, 1]

# High confidence long call
long_idx_xgb = np.where((y_sample == 1) & (proba_sample_xgb > 0.7))[0]
if len(long_idx_xgb) > 0:
    example_long_idx_xgb = long_idx_xgb[0]
else:
    example_long_idx_xgb = np.argmax(proba_sample_xgb)

# High confidence short call
short_idx_xgb = np.where((y_sample == 0) & (proba_sample_xgb < 0.3))[0]
if len(short_idx_xgb) > 0:
    example_short_idx_xgb = short_idx_xgb[0]
else:
    example_short_idx_xgb = np.argmin(proba_sample_xgb)

# Create waterfall plots - 25 VARIABLES
fig, axes = plt.subplots(2, 1, figsize=(16, 40))  # Increased height for 25 variables

# Get expected value
expected_value_xgb = explainer_xgb.expected_value
if isinstance(expected_value_xgb, (list, np.ndarray)):
    expected_value_xgb = expected_value_xgb[1] if len(expected_value_xgb) > 1 else expected_value_xgb[0]

# Long call example
plt.sca(axes[0])
shap.waterfall_plot(
    shap.Explanation(values=shap_values_xgb[example_long_idx_xgb],
                     base_values=expected_value_xgb,
                     data=X_sample.iloc[example_long_idx_xgb],
                     feature_names=feature_cols),
    max_display=25,  # 25 VARIABLES
    show=False
)
axes[0].set_title(f'XGBOOST - LONG CALL Prediction (Actual: {"Long" if y_sample[example_long_idx_xgb] == 1 else "Short"})\n' +
                  f'Predicted Probability: {proba_sample_xgb[example_long_idx_xgb]:.1%}',
                  fontsize=11, fontweight='bold')

# Short call example
plt.sca(axes[1])
shap.waterfall_plot(
    shap.Explanation(values=shap_values_xgb[example_short_idx_xgb],
                     base_values=expected_value_xgb,
                     data=X_sample.iloc[example_short_idx_xgb],
                     feature_names=feature_cols),
    max_display=25,  # 25 VARIABLES
    show=False
)
axes[1].set_title(f'XGBOOST - SHORT CALL Prediction (Actual: {"Long" if y_sample[example_short_idx_xgb] == 1 else "Short"})\n' +
                  f'Predicted Probability: {proba_sample_xgb[example_short_idx_xgb]:.1%}',
                  fontsize=11, fontweight='bold')

# Add overall guide
fig.text(0.5, 0.01, 
         'HOW TO READ WATERFALL PLOTS:\n' +
         'Start from base value (E[f(x)]) → Each bar shows one variable\'s contribution → End at final prediction (f(x))\n' +
         'RED = Pushes toward Long calls | BLUE = Pushes toward Short calls | Bar length = Strength of effect',
         ha='center', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))

plt.tight_layout()
plt.subplots_adjust(bottom=0.02)
plt.savefig('analysis_outputs/level1_variable/shap_05_xgb_waterfall.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_05_xgb_waterfall.png (25 variables)")
plt.close()

# ==============================================================================
# XGBOOST DEPENDENCE PLOTS (TOP 4 FEATURES)
# ==============================================================================

print("\nCreating XGBoost Dependence Plots...")

# Get top 4 features by mean |SHAP|
mean_abs_shap_xgb_dep = np.abs(shap_values_xgb).mean(axis=0)
top_4_indices_xgb = np.argsort(mean_abs_shap_xgb_dep)[-4:][::-1]
top_4_features_xgb = [feature_cols[i] for i in top_4_indices_xgb]

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()

for idx, (feat_idx, feat_name) in enumerate(zip(top_4_indices_xgb, top_4_features_xgb)):
    ax = axes[idx]
    plt.sca(ax)
    
    shap.dependence_plot(feat_idx, shap_values_xgb, X_sample,
                         feature_names=feature_cols,
                         show=False,
                         ax=ax)
    
    ax.set_title(f'{feat_name}\nShows how this variable affects predictions',
                 fontsize=11, fontweight='bold')

# Add reading guide
fig.text(0.5, 0.02,
         'HOW TO READ DEPENDENCE PLOTS:\n' +
         'X-axis: Variable value | Y-axis: SHAP value (impact on prediction) | Color: Interaction variable\n' +
         'Shows relationship between variable value and its impact. Helps identify thresholds and interactions.',
         ha='center', fontsize=10,
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

plt.suptitle('LEVEL 1: TOP 4 VARIABLE DEPENDENCE PLOTS (XGBoost)\n' +
             'Shows how variable values affect predictions and interactions',
             fontsize=14, fontweight='bold', y=0.98)

plt.tight_layout()
plt.subplots_adjust(bottom=0.08, top=0.94)
plt.savefig('analysis_outputs/level1_variable/shap_05_xgb_dependence.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: shap_05_xgb_dependence.png")
plt.close()

# ==============================================================================
# SAVE SHAP IMPORTANCE VALUES
# ==============================================================================

print("\n" + "="*100)
print("SAVING SHAP IMPORTANCE VALUES")
print("="*100)

# Calculate mean absolute SHAP values
mean_abs_shap_rf = np.abs(shap_values_rf).mean(axis=0)
mean_abs_shap_xgb = np.abs(shap_values_xgb).mean(axis=0)

shap_importance = pd.DataFrame({
    'Variable': feature_cols,
    'SHAP_RF': mean_abs_shap_rf,
    'SHAP_XGB': mean_abs_shap_xgb,
    'SHAP_Avg': (mean_abs_shap_rf + mean_abs_shap_xgb) / 2
}).sort_values('SHAP_Avg', ascending=False)

shap_importance.to_csv('analysis_outputs/level1_variable/05_shap_importance.csv', index=False)
print("[OK] Saved: 05_shap_importance.csv")

print("\nTOP 20 VARIABLES BY SHAP IMPORTANCE:")
print("-" * 100)
for idx, row in shap_importance.head(20).iterrows():
    print(f"  {row['Variable']}: {row['SHAP_Avg']:.4f} (RF={row['SHAP_RF']:.4f}, XGB={row['SHAP_XGB']:.4f})")

print("\n" + "="*100)
print("LEVEL 1 SHAP ANALYSIS COMPLETE")
print("="*100)
print("\n[OK] Created 8 types of SHAP visualizations:")
print("   1. Summary plots (beeswarm) - RF & XGBoost")
print("   2. Bar plots (importance) - RF & XGBoost")
print("   3. Waterfall plots (25 variables) - RF & XGBoost")
print("   4. Dependence plots (interactions) - RF & XGBoost")
print("[OK] All charts include reading guides")
print(f"[OK] Top variable: {shap_importance.iloc[0]['Variable']}")

