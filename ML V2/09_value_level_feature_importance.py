"""
==============================================================================
LEVEL 2: VALUE-LEVEL FEATURE IMPORTANCE
==============================================================================

Purpose: Train ML models on SPECIFIC VALUES (not variables)
- One-hot encode top categorical values
- Create features from specific values: timezone_Eastern, timezone_Central, etc.
- Combined approach: top N most discriminative values as features
- Separate ML models for value-level analysis

==============================================================================
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("LEVEL 2: VALUE-LEVEL FEATURE IMPORTANCE")
print("="*100)

# ==============================================================================
# LOAD DATA AND VALUE ANALYSIS
# ==============================================================================

print("\nLoading data...")
df = pd.read_csv('analysis_outputs/level1_variable/01_combined_original.csv')
df_value_analysis = pd.read_csv('analysis_outputs/level2_value/07_categorical_value_analysis.csv')

print(f"Data: {df.shape}")
print(f"Value analysis: {len(df_value_analysis)} values")

# ==============================================================================
# SELECT TOP VALUES FOR MODELING
# ==============================================================================

print("\n" + "="*100)
print("SELECTING TOP DISCRIMINATIVE VALUES")
print("="*100)

# Take top N most discriminative values
top_n = 100
top_values = df_value_analysis.nlargest(top_n, 'Importance_Score')

print(f"\nSelected top {len(top_values)} values for modeling")
print("Criteria: Highest importance score (deviation from 50-50)")

# ==============================================================================
# CREATE VALUE-LEVEL FEATURES
# ==============================================================================

print("\n" + "="*100)
print("CREATING VALUE-LEVEL FEATURES")
print("="*100)

X = pd.DataFrame()
y = df['target'].values

print("\nCreating binary features for each top value...")

for idx, row in top_values.iterrows():
    var = row['Variable']
    value = row['Value']
    
    # Create binary feature: 1 if this value, 0 otherwise
    feature_name = f"{var}_{value}"[:50]  # Limit length
    X[feature_name] = (df[var].astype(str) == value).astype(int)

print(f"\n[OK] Created {len(X.columns)} value-level features")

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

# ==============================================================================
# RANDOM FOREST MODEL
# ==============================================================================

print("\n" + "="*100)
print("TRAINING RANDOM FOREST (VALUE-LEVEL)")
print("="*100)

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=20,
    min_samples_leaf=10,
    random_state=42,
    n_jobs=-1
)

print("Training...")
rf_model.fit(X_train, y_train)

y_proba_rf = rf_model.predict_proba(X_test)[:, 1]
roc_auc_rf = roc_auc_score(y_test, y_proba_rf)

print(f"\n[OK] Random Forest trained")
print(f"   ROC-AUC: {roc_auc_rf:.4f}")

# Feature importance
rf_importance = pd.DataFrame({
    'Value_Feature': X.columns,
    'RF_Importance': rf_model.feature_importances_
}).sort_values('RF_Importance', ascending=False)

print(f"\nTop 10 value features:")
for idx, row in rf_importance.head(10).iterrows():
    print(f"  {row['Value_Feature']}: {row['RF_Importance']:.4f}")

# ==============================================================================
# GRADIENT BOOSTING MODEL
# ==============================================================================

print("\n" + "="*100)
print("TRAINING GRADIENT BOOSTING (VALUE-LEVEL)")
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

y_proba_gb = gb_model.predict_proba(X_test)[:, 1]
roc_auc_gb = roc_auc_score(y_test, y_proba_gb)

print(f"\n[OK] Gradient Boosting trained")
print(f"   ROC-AUC: {roc_auc_gb:.4f}")

# Feature importance
gb_importance = pd.DataFrame({
    'Value_Feature': X.columns,
    'GB_Importance': gb_model.feature_importances_
}).sort_values('GB_Importance', ascending=False)

print(f"\nTop 10 value features:")
for idx, row in gb_importance.head(10).iterrows():
    print(f"  {row['Value_Feature']}: {row['GB_Importance']:.4f}")

# ==============================================================================
# COMBINE IMPORTANCE SCORES
# ==============================================================================

print("\n" + "="*100)
print("COMBINING IMPORTANCE SCORES")
print("="*100)

df_combined = rf_importance.merge(gb_importance, on='Value_Feature')

# Normalize
df_combined['RF_Norm'] = df_combined['RF_Importance'] / df_combined['RF_Importance'].max()
df_combined['GB_Norm'] = df_combined['GB_Importance'] / df_combined['GB_Importance'].max()

# Combined score
df_combined['Combined_Score'] = (
    df_combined['RF_Norm'] * 0.5 +
    df_combined['GB_Norm'] * 0.5
)

df_combined = df_combined.sort_values('Combined_Score', ascending=False)

print("\nTOP 20 VALUE FEATURES BY COMBINED IMPORTANCE:")
print("-" * 100)
for idx, row in df_combined.head(20).iterrows():
    print(f"  {row['Value_Feature']}: {row['Combined_Score']:.4f}")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

print("\n" + "="*100)
print("SAVING RESULTS")
print("="*100)

rf_importance.to_csv('analysis_outputs/level2_value/09_importance_rf_values.csv', index=False)
gb_importance.to_csv('analysis_outputs/level2_value/09_importance_gb_values.csv', index=False)
df_combined.to_csv('analysis_outputs/level2_value/09_importance_combined_values.csv', index=False)

print("\n[OK] Saved CSV files:")
print("  - 09_importance_rf_values.csv")
print("  - 09_importance_gb_values.csv")
print("  - 09_importance_combined_values.csv")

# Save models
import joblib
joblib.dump(rf_model, 'analysis_outputs/level2_value/09_model_rf_values.pkl')
joblib.dump(gb_model, 'analysis_outputs/level2_value/09_model_gb_values.pkl')

print("  - 09_model_rf_values.pkl")
print("  - 09_model_gb_values.pkl")

# Save metrics
metrics = {
    'rf_roc_auc': float(roc_auc_rf),
    'gb_roc_auc': float(roc_auc_gb),
    'n_value_features': len(X.columns),
    'n_train': int(len(X_train)),
    'n_test': int(len(X_test))
}

import json
with open('analysis_outputs/level2_value/09_model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("  - 09_model_metrics.json")

print("\n" + "="*100)
print("LEVEL 2 FEATURE IMPORTANCE COMPLETE")
print("="*100)
print(f"\n[OK] Trained 2 ML models on {len(X.columns)} value features")
print(f"[OK] RF ROC-AUC: {roc_auc_rf:.4f} | GB ROC-AUC: {roc_auc_gb:.4f}")
print(f"[OK] Top value feature: {df_combined.iloc[0]['Value_Feature']}")

