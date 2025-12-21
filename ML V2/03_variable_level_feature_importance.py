"""
==============================================================================
LEVEL 1: VARIABLE-LEVEL FEATURE IMPORTANCE
==============================================================================

Purpose: Determine which of the 49 variables are most important
- Train ML models (Random Forest, Gradient Boosting)
- Extract feature importance scores
- Compare importance across models
- Combine with correlation for final ranking

Note: Encoding happens HERE for ML models only
==============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*100)
print("LEVEL 1: VARIABLE-LEVEL FEATURE IMPORTANCE")
print("="*100)

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("\nLoading data...")
df = pd.read_csv('analysis_outputs/level1_variable/01_combined_original.csv')
df_target_corr = pd.read_csv('analysis_outputs/level1_variable/02_correlation_with_target.csv')

print(f"Data: {df.shape}")
print(f"Target distribution: {df['target'].value_counts().to_dict()}")

# ==============================================================================
# ENCODE FOR ML MODELS
# ==============================================================================

print("\n" + "="*100)
print("ENCODING VARIABLES FOR ML MODELS")
print("="*100)

# Get feature columns
feature_cols = [c for c in df.columns if c not in ['target', 'call_duration_group']]

X = df[feature_cols].copy()
y = df['target'].values

# Encode categorical variables
label_encoders = {}
for col in X.columns:
    if X[col].dtype == 'object' or X[col].dtype == 'bool':
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le

# Handle missing values
for col in X.columns:
    if X[col].isna().any():
        X[col].fillna(X[col].median(), inplace=True)

print(f"\n[OK] Encoded {len(feature_cols)} variables for ML models")
print(f"[OK] Label encoded: {len(label_encoders)} categorical variables")

# ==============================================================================
# TRAIN/TEST SPLIT
# ==============================================================================

print("\n" + "="*100)
print("TRAIN/TEST SPLIT")
print("="*100)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print(f"\nTrain set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")
print(f"  Train positive rate: {y_train.mean():.1%}")
print(f"  Test positive rate: {y_test.mean():.1%}")

# ==============================================================================
# RANDOM FOREST MODEL
# ==============================================================================

print("\n" + "="*100)
print("TRAINING RANDOM FOREST MODEL")
print("="*100)

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=20,
    min_samples_leaf=10,
    random_state=42,
    n_jobs=-1
)

print("Training...")
rf_model.fit(X_train, y_train)

# Predictions
y_pred_rf = rf_model.predict(X_test)
y_proba_rf = rf_model.predict_proba(X_test)[:, 1]

# Metrics
roc_auc_rf = roc_auc_score(y_test, y_proba_rf)
print(f"\n[OK] Random Forest trained")
print(f"   ROC-AUC: {roc_auc_rf:.4f}")

# Feature importance
rf_importance = pd.DataFrame({
    'Variable': feature_cols,
    'RF_Importance': rf_model.feature_importances_
}).sort_values('RF_Importance', ascending=False)

print(f"\nTop 10 features:")
for idx, row in rf_importance.head(10).iterrows():
    print(f"  {row['Variable']}: {row['RF_Importance']:.4f}")

# ==============================================================================
# GRADIENT BOOSTING MODEL
# ==============================================================================

print("\n" + "="*100)
print("TRAINING GRADIENT BOOSTING MODEL")
print("="*100)

gb_model = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    min_samples_split=20,
    min_samples_leaf=10,
    random_state=42
)

print("Training...")
gb_model.fit(X_train, y_train)

# Predictions
y_pred_gb = gb_model.predict(X_test)
y_proba_gb = gb_model.predict_proba(X_test)[:, 1]

# Metrics
roc_auc_gb = roc_auc_score(y_test, y_proba_gb)
print(f"\n[OK] Gradient Boosting trained")
print(f"   ROC-AUC: {roc_auc_gb:.4f}")

# Feature importance
gb_importance = pd.DataFrame({
    'Variable': feature_cols,
    'GB_Importance': gb_model.feature_importances_
}).sort_values('GB_Importance', ascending=False)

print(f"\nTop 10 features:")
for idx, row in gb_importance.head(10).iterrows():
    print(f"  {row['Variable']}: {row['GB_Importance']:.4f}")

# ==============================================================================
# COMBINE IMPORTANCE SCORES
# ==============================================================================

print("\n" + "="*100)
print("COMBINING IMPORTANCE SCORES")
print("="*100)

# Merge all importance scores
df_combined = rf_importance.merge(gb_importance, on='Variable')
df_combined = df_combined.merge(df_target_corr[['Variable', 'Abs_Correlation']], on='Variable')

# Normalize scores
for col in ['RF_Importance', 'GB_Importance', 'Abs_Correlation']:
    max_val = df_combined[col].max()
    df_combined[f'{col}_Norm'] = df_combined[col] / max_val if max_val > 0 else 0

# Combined score (weighted average)
df_combined['Combined_Score'] = (
    df_combined['RF_Importance_Norm'] * 0.35 +
    df_combined['GB_Importance_Norm'] * 0.35 +
    df_combined['Abs_Correlation_Norm'] * 0.30
)

df_combined = df_combined.sort_values('Combined_Score', ascending=False)

print("\nTOP 20 VARIABLES BY COMBINED IMPORTANCE:")
print("-" * 100)
for idx, row in df_combined.head(20).iterrows():
    print(f"  {idx+1}. {row['Variable']}: {row['Combined_Score']:.4f} " +
          f"(RF={row['RF_Importance']:.3f}, GB={row['GB_Importance']:.3f}, Corr={row['Abs_Correlation']:.3f})")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

print("\n" + "="*100)
print("SAVING RESULTS")
print("="*100)

# Save importance scores
rf_importance.to_csv('analysis_outputs/level1_variable/03_importance_random_forest.csv', index=False)
gb_importance.to_csv('analysis_outputs/level1_variable/03_importance_gradient_boosting.csv', index=False)
df_combined.to_csv('analysis_outputs/level1_variable/03_importance_combined.csv', index=False)

print("\n[OK] Saved CSV files:")
print("  - 03_importance_random_forest.csv")
print("  - 03_importance_gradient_boosting.csv")
print("  - 03_importance_combined.csv")

# Save models
import joblib
joblib.dump(rf_model, 'analysis_outputs/level1_variable/03_model_random_forest.pkl')
joblib.dump(gb_model, 'analysis_outputs/level1_variable/03_model_gradient_boosting.pkl')

print("  - 03_model_random_forest.pkl")
print("  - 03_model_gradient_boosting.pkl")

# Save metrics
metrics = {
    'random_forest_roc_auc': float(roc_auc_rf),
    'gradient_boosting_roc_auc': float(roc_auc_gb),
    'n_features': len(feature_cols),
    'n_train': int(len(X_train)),
    'n_test': int(len(X_test))
}

import json
with open('analysis_outputs/level1_variable/03_model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("  - 03_model_metrics.json")

print("\n" + "="*100)
print("LEVEL 1 FEATURE IMPORTANCE COMPLETE")
print("="*100)
print(f"\n[OK] Trained 2 ML models (RF: {roc_auc_rf:.4f}, GB: {roc_auc_gb:.4f})")
print(f"[OK] Top variable: {df_combined.iloc[0]['Variable']}")
print(f"[OK] Combined importance ranking created")

