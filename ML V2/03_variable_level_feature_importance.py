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
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score, f1_score, log_loss, confusion_matrix
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

# Remove constant/near-constant variables (auto-detection)
print("\nChecking for constant/near-constant variables...")
to_remove = []
for col in X.columns:
    nunique = X[col].nunique()
    if nunique <= 1:
        to_remove.append(col)
        print(f"  [WARNING] {col}: Only {nunique} unique value(s) - removing")

if to_remove:
    X = X.drop(columns=to_remove)
    feature_cols = [c for c in feature_cols if c not in to_remove]
    print(f"\n[OK] Removed {len(to_remove)} constant variables")

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

print(f"\n[OK] Final features: {len(feature_cols)} variables")
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
y_pred_rf_train = rf_model.predict(X_train)
y_proba_rf_train = rf_model.predict_proba(X_train)[:, 1]

# Comprehensive metrics
roc_auc_rf_test = roc_auc_score(y_test, y_proba_rf)
roc_auc_rf_train = roc_auc_score(y_train, y_proba_rf_train)
acc_rf_test = accuracy_score(y_test, y_pred_rf)
acc_rf_train = accuracy_score(y_train, y_pred_rf_train)
f1_rf_test = f1_score(y_test, y_pred_rf)
f1_rf_train = f1_score(y_train, y_pred_rf_train)
logloss_rf_test = log_loss(y_test, y_proba_rf)
logloss_rf_train = log_loss(y_train, y_proba_rf_train)

# Cross-validation
cv_scores_rf = cross_val_score(rf_model, X, y, cv=5, scoring='roc_auc', n_jobs=-1)

print(f"\n[OK] Random Forest trained")
print(f"\n   TEST SET METRICS:")
print(f"   - ROC-AUC: {roc_auc_rf_test:.4f}")
print(f"   - Accuracy: {acc_rf_test:.4f}")
print(f"   - F1-Score: {f1_rf_test:.4f}")
print(f"   - Log Loss: {logloss_rf_test:.4f}")
print(f"\n   TRAIN SET METRICS:")
print(f"   - ROC-AUC: {roc_auc_rf_train:.4f}")
print(f"   - Accuracy: {acc_rf_train:.4f}")
print(f"   - F1-Score: {f1_rf_train:.4f}")
print(f"   - Log Loss: {logloss_rf_train:.4f}")
print(f"\n   CROSS-VALIDATION (5-fold):")
print(f"   - Mean ROC-AUC: {cv_scores_rf.mean():.4f} (+/- {cv_scores_rf.std() * 2:.4f})")
print(f"\n   OVERFITTING CHECK:")
overfit_roc = roc_auc_rf_train - roc_auc_rf_test
if overfit_roc > 0.10:
    print(f"   - [WARNING] HIGH OVERFITTING: Train-Test gap = {overfit_roc:.4f}")
elif overfit_roc > 0.05:
    print(f"   - [CAUTION] Moderate overfitting: Train-Test gap = {overfit_roc:.4f}")
else:
    print(f"   - [OK] Good generalization: Train-Test gap = {overfit_roc:.4f}")

# Feature importance
rf_importance = pd.DataFrame({
    'Variable': feature_cols,
    'RF_Importance': rf_model.feature_importances_
}).sort_values('RF_Importance', ascending=False)

print(f"\nTop 10 features:")
for idx, row in rf_importance.head(10).iterrows():
    print(f"  {row['Variable']}: {row['RF_Importance']:.4f}")

# ==============================================================================
# XGBOOST MODEL
# ==============================================================================

print("\n" + "="*100)
print("TRAINING XGBOOST MODEL")
print("="*100)

xgb_model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    min_child_weight=10,
    random_state=42,
    eval_metric='logloss',
    use_label_encoder=False
)

print("Training...")
xgb_model.fit(X_train, y_train)

# Predictions
y_pred_xgb = xgb_model.predict(X_test)
y_proba_xgb = xgb_model.predict_proba(X_test)[:, 1]
y_pred_xgb_train = xgb_model.predict(X_train)
y_proba_xgb_train = xgb_model.predict_proba(X_train)[:, 1]

# Comprehensive metrics
roc_auc_xgb_test = roc_auc_score(y_test, y_proba_xgb)
roc_auc_xgb_train = roc_auc_score(y_train, y_proba_xgb_train)
acc_xgb_test = accuracy_score(y_test, y_pred_xgb)
acc_xgb_train = accuracy_score(y_train, y_pred_xgb_train)
f1_xgb_test = f1_score(y_test, y_pred_xgb)
f1_xgb_train = f1_score(y_train, y_pred_xgb_train)
logloss_xgb_test = log_loss(y_test, y_proba_xgb)
logloss_xgb_train = log_loss(y_train, y_proba_xgb_train)

# Cross-validation
cv_scores_xgb = cross_val_score(xgb_model, X, y, cv=5, scoring='roc_auc')

print(f"\n[OK] XGBoost trained")
print(f"\n   TEST SET METRICS:")
print(f"   - ROC-AUC: {roc_auc_xgb_test:.4f}")
print(f"   - Accuracy: {acc_xgb_test:.4f}")
print(f"   - F1-Score: {f1_xgb_test:.4f}")
print(f"   - Log Loss: {logloss_xgb_test:.4f}")
print(f"\n   TRAIN SET METRICS:")
print(f"   - ROC-AUC: {roc_auc_xgb_train:.4f}")
print(f"   - Accuracy: {acc_xgb_train:.4f}")
print(f"   - F1-Score: {f1_xgb_train:.4f}")
print(f"   - Log Loss: {logloss_xgb_train:.4f}")
print(f"\n   CROSS-VALIDATION (5-fold):")
print(f"   - Mean ROC-AUC: {cv_scores_xgb.mean():.4f} (+/- {cv_scores_xgb.std() * 2:.4f})")
print(f"\n   OVERFITTING CHECK:")
overfit_roc = roc_auc_xgb_train - roc_auc_xgb_test
if overfit_roc > 0.10:
    print(f"   - [WARNING] HIGH OVERFITTING: Train-Test gap = {overfit_roc:.4f}")
elif overfit_roc > 0.05:
    print(f"   - [CAUTION] Moderate overfitting: Train-Test gap = {overfit_roc:.4f}")
else:
    print(f"   - [OK] Good generalization: Train-Test gap = {overfit_roc:.4f}")

# Feature importance
xgb_importance = pd.DataFrame({
    'Variable': feature_cols,
    'XGB_Importance': xgb_model.feature_importances_
}).sort_values('XGB_Importance', ascending=False)

print(f"\nTop 10 features:")
for idx, row in xgb_importance.head(10).iterrows():
    print(f"  {row['Variable']}: {row['XGB_Importance']:.4f}")

# ==============================================================================
# COMBINE IMPORTANCE SCORES
# ==============================================================================

print("\n" + "="*100)
print("COMBINING IMPORTANCE SCORES")
print("="*100)

# Merge all importance scores
df_combined = rf_importance.merge(xgb_importance, on='Variable')
df_combined = df_combined.merge(df_target_corr[['Variable', 'Abs_Correlation']], on='Variable')

# Normalize scores
for col in ['RF_Importance', 'XGB_Importance', 'Abs_Correlation']:
    max_val = df_combined[col].max()
    df_combined[f'{col}_Norm'] = df_combined[col] / max_val if max_val > 0 else 0

# Combined score (weighted average)
df_combined['Combined_Score'] = (
    df_combined['RF_Importance_Norm'] * 0.35 +
    df_combined['XGB_Importance_Norm'] * 0.35 +
    df_combined['Abs_Correlation_Norm'] * 0.30
)

df_combined = df_combined.sort_values('Combined_Score', ascending=False)

print("\nTOP 20 VARIABLES BY COMBINED IMPORTANCE:")
print("-" * 100)
for idx, row in df_combined.head(20).iterrows():
    print(f"  {idx+1}. {row['Variable']}: {row['Combined_Score']:.4f} " +
          f"(RF={row['RF_Importance']:.3f}, XGB={row['XGB_Importance']:.3f}, Corr={row['Abs_Correlation']:.3f})")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

print("\n" + "="*100)
print("SAVING RESULTS")
print("="*100)

# Save importance scores
rf_importance.to_csv('analysis_outputs/level1_variable/03_importance_random_forest.csv', index=False)
xgb_importance.to_csv('analysis_outputs/level1_variable/03_importance_xgboost.csv', index=False)
df_combined.to_csv('analysis_outputs/level1_variable/03_importance_combined.csv', index=False)

print("\n[OK] Saved CSV files:")
print("  - 03_importance_random_forest.csv")
print("  - 03_importance_xgboost.csv")
print("  - 03_importance_combined.csv")

# Save models
import joblib
joblib.dump(rf_model, 'analysis_outputs/level1_variable/03_model_random_forest.pkl')
joblib.dump(xgb_model, 'analysis_outputs/level1_variable/03_model_xgboost.pkl')

print("  - 03_model_random_forest.pkl")
print("  - 03_model_xgboost.pkl")

# Save metrics
metrics = {
    'random_forest_roc_auc_test': float(roc_auc_rf_test),
    'random_forest_roc_auc_train': float(roc_auc_rf_train),
    'random_forest_accuracy_test': float(acc_rf_test),
    'random_forest_f1_test': float(f1_rf_test),
    'random_forest_cv_mean': float(cv_scores_rf.mean()),
    'random_forest_cv_std': float(cv_scores_rf.std()),
    'random_forest_overfitting_gap': float(roc_auc_rf_train - roc_auc_rf_test),
    'xgboost_roc_auc_test': float(roc_auc_xgb_test),
    'xgboost_roc_auc_train': float(roc_auc_xgb_train),
    'xgboost_accuracy_test': float(acc_xgb_test),
    'xgboost_f1_test': float(f1_xgb_test),
    'xgboost_cv_mean': float(cv_scores_xgb.mean()),
    'xgboost_cv_std': float(cv_scores_xgb.std()),
    'xgboost_overfitting_gap': float(roc_auc_xgb_train - roc_auc_xgb_test),
    'n_features': len(feature_cols),
    'n_train': int(len(X_train)),
    'n_test': int(len(X_test)),
    'removed_variables': ['TO_OMC_Duration'] + to_remove if to_remove else ['TO_OMC_Duration']
}

import json
with open('analysis_outputs/level1_variable/03_model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("  - 03_model_metrics.json")

# ==============================================================================
# MODEL EVALUATION VISUALIZATIONS
# ==============================================================================

print("\n" + "="*100)
print("CREATING MODEL EVALUATION VISUALIZATIONS")
print("="*100)

from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import learning_curve

# ==============================
# VIZ 1: CONFUSION MATRICES
# ==============================

print("\nCreating confusion matrices...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# RF Confusion Matrix
cm_rf = confusion_matrix(y_test, y_pred_rf)
sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Blues', ax=axes[0],
            xticklabels=['Short', 'Long'], yticklabels=['Short', 'Long'],
            cbar_kws={'label': 'Count'})
axes[0].set_title(f'Random Forest Confusion Matrix\nTest ROC-AUC: {roc_auc_rf_test:.4f}',
                  fontsize=12, fontweight='bold')
axes[0].set_xlabel('Predicted', fontsize=11, fontweight='bold')
axes[0].set_ylabel('Actual', fontsize=11, fontweight='bold')

# XGBoost Confusion Matrix
cm_xgb = confusion_matrix(y_test, y_pred_xgb)
sns.heatmap(cm_xgb, annot=True, fmt='d', cmap='Greens', ax=axes[1],
            xticklabels=['Short', 'Long'], yticklabels=['Short', 'Long'],
            cbar_kws={'label': 'Count'})
axes[1].set_title(f'XGBoost Confusion Matrix\nTest ROC-AUC: {roc_auc_xgb_test:.4f}',
                  fontsize=12, fontweight='bold')
axes[1].set_xlabel('Predicted', fontsize=11, fontweight='bold')
axes[1].set_ylabel('Actual', fontsize=11, fontweight='bold')

plt.suptitle('LEVEL 1: MODEL CONFUSION MATRICES\nDiagonal = Correct Predictions | Off-diagonal = Errors',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/03_eval_confusion_matrices.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 03_eval_confusion_matrices.png")
plt.close()

# ==============================
# VIZ 2: ROC CURVES
# ==============================

print("Creating ROC curves...")
fig, ax = plt.subplots(figsize=(10, 8))

# RF ROC Curve
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_proba_rf)
ax.plot(fpr_rf, tpr_rf, label=f'Random Forest (AUC = {roc_auc_rf_test:.4f})',
        linewidth=2.5, color='#4ECDC4')

# XGBoost ROC Curve  
fpr_xgb, tpr_xgb, _ = roc_curve(y_test, y_proba_xgb)
ax.plot(fpr_xgb, tpr_xgb, label=f'XGBoost (AUC = {roc_auc_xgb_test:.4f})',
        linewidth=2.5, color='#FF6B6B')

# Diagonal (random classifier)
ax.plot([0, 1], [0, 1], 'k--', linewidth=1.5, label='Random Classifier (AUC = 0.50)')

ax.set_xlabel('False Positive Rate', fontsize=12, fontweight='bold')
ax.set_ylabel('True Positive Rate', fontsize=12, fontweight='bold')
ax.set_title('LEVEL 1: ROC CURVES - Model Comparison\nHigher curve = Better performance',
             fontsize=14, fontweight='bold', pad=20)
ax.legend(fontsize=11, loc='lower right')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/03_eval_roc_curves.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 03_eval_roc_curves.png")
plt.close()

# ==============================
# VIZ 3: LEARNING CURVES
# ==============================

print("Creating learning curves...")
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# RF Learning Curve
train_sizes, train_scores_rf, val_scores_rf = learning_curve(
    rf_model, X, y, cv=5, n_jobs=-1,
    train_sizes=np.linspace(0.1, 1.0, 10),
    scoring='roc_auc', random_state=42
)

train_mean_rf = train_scores_rf.mean(axis=1)
train_std_rf = train_scores_rf.std(axis=1)
val_mean_rf = val_scores_rf.mean(axis=1)
val_std_rf = val_scores_rf.std(axis=1)

axes[0].plot(train_sizes, train_mean_rf, label='Training Score', 
            linewidth=2.5, color='#4ECDC4', marker='o')
axes[0].fill_between(train_sizes, train_mean_rf - train_std_rf, 
                     train_mean_rf + train_std_rf, alpha=0.2, color='#4ECDC4')
axes[0].plot(train_sizes, val_mean_rf, label='Cross-Validation Score',
            linewidth=2.5, color='#FF6B6B', marker='o')
axes[0].fill_between(train_sizes, val_mean_rf - val_std_rf,
                     val_mean_rf + val_std_rf, alpha=0.2, color='#FF6B6B')

axes[0].set_xlabel('Training Set Size', fontsize=11, fontweight='bold')
axes[0].set_ylabel('ROC-AUC Score', fontsize=11, fontweight='bold')
axes[0].set_title('Random Forest Learning Curve\nChecking overfitting and convergence',
                  fontsize=12, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].grid(alpha=0.3)

# XGBoost Learning Curve
train_sizes, train_scores_xgb, val_scores_xgb = learning_curve(
    xgb_model, X, y, cv=5,
    train_sizes=np.linspace(0.1, 1.0, 10),
    scoring='roc_auc', random_state=42
)

train_mean_xgb = train_scores_xgb.mean(axis=1)
train_std_xgb = train_scores_xgb.std(axis=1)
val_mean_xgb = val_scores_xgb.mean(axis=1)
val_std_xgb = val_scores_xgb.std(axis=1)

axes[1].plot(train_sizes, train_mean_xgb, label='Training Score',
            linewidth=2.5, color='#45B7D1', marker='o')
axes[1].fill_between(train_sizes, train_mean_xgb - train_std_xgb,
                     train_mean_xgb + train_std_xgb, alpha=0.2, color='#45B7D1')
axes[1].plot(train_sizes, val_mean_xgb, label='Cross-Validation Score',
            linewidth=2.5, color='#F7DC6F', marker='o')
axes[1].fill_between(train_sizes, val_mean_xgb - val_std_xgb,
                     val_mean_xgb + val_std_xgb, alpha=0.2, color='#F7DC6F')

axes[1].set_xlabel('Training Set Size', fontsize=11, fontweight='bold')
axes[1].set_ylabel('ROC-AUC Score', fontsize=11, fontweight='bold')
axes[1].set_title('XGBoost Learning Curve\nChecking overfitting and convergence',
                  fontsize=12, fontweight='bold')
axes[1].legend(fontsize=10)
axes[1].grid(alpha=0.3)

plt.suptitle('LEVEL 1: LEARNING CURVES\nGap between training and validation = Overfitting level',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/03_eval_learning_curves.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 03_eval_learning_curves.png")
plt.close()

# ==============================
# VIZ 4: MODEL METRICS COMPARISON
# ==============================

print("Creating metrics comparison...")
fig, ax = plt.subplots(figsize=(12, 8))

metrics_comparison = {
    'ROC-AUC (Test)': [roc_auc_rf_test, roc_auc_xgb_test],
    'Accuracy (Test)': [acc_rf_test, acc_xgb_test],
    'F1-Score (Test)': [f1_rf_test, f1_xgb_test],
    'CV Mean': [cv_scores_rf.mean(), cv_scores_xgb.mean()]
}

x = np.arange(len(metrics_comparison))
width = 0.35

bars1 = ax.bar(x - width/2, [metrics_comparison[k][0] for k in metrics_comparison.keys()],
               width, label='Random Forest', color='#98D8C8', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x + width/2, [metrics_comparison[k][1] for k in metrics_comparison.keys()],
               width, label='XGBoost', color='#F7DC6F', alpha=0.8, edgecolor='black', linewidth=1.5)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xlabel('Metric', fontsize=13, fontweight='bold')
ax.set_ylabel('Score', fontsize=13, fontweight='bold')
ax.set_title('LEVEL 1: MODEL PERFORMANCE COMPARISON\nHigher is better for all metrics',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(metrics_comparison.keys(), fontsize=11)
ax.legend(fontsize=12)
ax.set_ylim([0, 1.05])
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/03_eval_metrics_comparison.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 03_eval_metrics_comparison.png")
plt.close()

print("\n[OK] Created 4 model evaluation visualizations")

print("\n" + "="*100)
print("LEVEL 1 FEATURE IMPORTANCE COMPLETE")
print("="*100)
print(f"\n[OK] Trained 2 ML models")
print(f"   RF  - Test: {roc_auc_rf_test:.4f} | Train: {roc_auc_rf_train:.4f} | CV: {cv_scores_rf.mean():.4f}")
print(f"   XGB - Test: {roc_auc_xgb_test:.4f} | Train: {roc_auc_xgb_train:.4f} | CV: {cv_scores_xgb.mean():.4f}")
print(f"[OK] Top variable: {df_combined.iloc[0]['Variable']}")
print(f"[OK] Combined importance ranking created")

