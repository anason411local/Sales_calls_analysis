"""
ENHANCED ML MODEL EVALUATION
Comprehensive model evaluation with confusion matrix, learning curves, and overfitting analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, learning_curve, cross_val_score
from sklearn.metrics import (confusion_matrix, classification_report, roc_curve, roc_auc_score,
                             precision_recall_curve, f1_score, accuracy_score)
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("ENHANCED ML MODEL EVALUATION")
print("="*100)

# Load data
df_combined = pd.read_csv('analysis_outputs/enhanced_combined_data.csv')

print(f"\nDataset shape: {df_combined.shape}")

# Prepare data
df_ml = df_combined.copy()

# Handle missing values
for col in df_ml.select_dtypes(include=[np.number]).columns:
    if col != 'call_duration_group':
        df_ml[col].fillna(df_ml[col].median(), inplace=True)

# Encode categorical variables
label_encoders = {}
for col in df_ml.select_dtypes(include=['object', 'bool']).columns:
    if col != 'call_duration_group':
        le = LabelEncoder()
        df_ml[col] = df_ml[col].astype(str)
        df_ml[col] = le.fit_transform(df_ml[col])
        label_encoders[col] = le

# Prepare features and target
X = df_ml.drop('call_duration_group', axis=1)
y = df_ml['call_duration_group']

print(f"Features: {X.shape[1]}")
print(f"Target distribution:\n{y.value_counts()}")

# Split data with stratification
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

print(f"\nTraining set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")

# ==================================================================================
# MODEL 1: RANDOM FOREST
# ==================================================================================
print("\n" + "="*100)
print("RANDOM FOREST CLASSIFIER - DETAILED EVALUATION")
print("="*100)

rf_model = RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_split=20,
                                  min_samples_leaf=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

# Predictions
y_train_pred_rf = rf_model.predict(X_train)
y_test_pred_rf = rf_model.predict(X_test)
y_test_proba_rf = rf_model.predict_proba(X_test)[:, 1]

# Metrics
train_acc_rf = accuracy_score(y_train, y_train_pred_rf)
test_acc_rf = accuracy_score(y_test, y_test_pred_rf)
train_f1_rf = f1_score(y_train, y_train_pred_rf)
test_f1_rf = f1_score(y_test, y_test_pred_rf)
auc_rf = roc_auc_score(y_test, y_test_proba_rf)

print(f"\nPerformance Metrics:")
print(f"  Training Accuracy: {train_acc_rf:.4f}")
print(f"  Test Accuracy: {test_acc_rf:.4f}")
print(f"  Training F1-Score: {train_f1_rf:.4f}")
print(f"  Test F1-Score: {test_f1_rf:.4f}")
print(f"  Test AUC-ROC: {auc_rf:.4f}")
print(f"  Overfitting Gap (Accuracy): {(train_acc_rf - test_acc_rf):.4f}")

# Confusion Matrix
cm_rf = confusion_matrix(y_test, y_test_pred_rf)
print(f"\nConfusion Matrix:")
print(cm_rf)

# Classification Report
print(f"\nClassification Report:")
print(classification_report(y_test, y_test_pred_rf, target_names=['Short Calls', 'Long Calls']))

# Cross-validation
cv_scores_rf = cross_val_score(rf_model, X_train, y_train, cv=5, scoring='accuracy')
print(f"\n5-Fold Cross-Validation Scores: {cv_scores_rf}")
print(f"Mean CV Accuracy: {cv_scores_rf.mean():.4f} (+/- {cv_scores_rf.std() * 2:.4f})")

# ==================================================================================
# MODEL 2: GRADIENT BOOSTING
# ==================================================================================
print("\n" + "="*100)
print("GRADIENT BOOSTING CLASSIFIER - DETAILED EVALUATION")
print("="*100)

gb_model = GradientBoostingClassifier(n_estimators=150, max_depth=5, learning_rate=0.1,
                                      min_samples_split=20, min_samples_leaf=10, random_state=42)
gb_model.fit(X_train, y_train)

# Predictions
y_train_pred_gb = gb_model.predict(X_train)
y_test_pred_gb = gb_model.predict(X_test)
y_test_proba_gb = gb_model.predict_proba(X_test)[:, 1]

# Metrics
train_acc_gb = accuracy_score(y_train, y_train_pred_gb)
test_acc_gb = accuracy_score(y_test, y_test_pred_gb)
train_f1_gb = f1_score(y_train, y_train_pred_gb)
test_f1_gb = f1_score(y_test, y_test_pred_gb)
auc_gb = roc_auc_score(y_test, y_test_proba_gb)

print(f"\nPerformance Metrics:")
print(f"  Training Accuracy: {train_acc_gb:.4f}")
print(f"  Test Accuracy: {test_acc_gb:.4f}")
print(f"  Training F1-Score: {train_f1_gb:.4f}")
print(f"  Test F1-Score: {test_f1_gb:.4f}")
print(f"  Test AUC-ROC: {auc_gb:.4f}")
print(f"  Overfitting Gap (Accuracy): {(train_acc_gb - test_acc_gb):.4f}")

# Confusion Matrix
cm_gb = confusion_matrix(y_test, y_test_pred_gb)
print(f"\nConfusion Matrix:")
print(cm_gb)

# Classification Report
print(f"\nClassification Report:")
print(classification_report(y_test, y_test_pred_gb, target_names=['Short Calls', 'Long Calls']))

# Cross-validation
cv_scores_gb = cross_val_score(gb_model, X_train, y_train, cv=5, scoring='accuracy')
print(f"\n5-Fold Cross-Validation Scores: {cv_scores_gb}")
print(f"Mean CV Accuracy: {cv_scores_gb.mean():.4f} (+/- {cv_scores_gb.std() * 2:.4f})")

# ==================================================================================
# SAVE EVALUATION METRICS
# ==================================================================================
print("\n" + "="*100)
print("SAVING EVALUATION RESULTS")
print("="*100)

# Save metrics summary
metrics_summary = pd.DataFrame({
    'Model': ['Random Forest', 'Gradient Boosting'],
    'Train_Accuracy': [train_acc_rf, train_acc_gb],
    'Test_Accuracy': [test_acc_rf, test_acc_gb],
    'Train_F1': [train_f1_rf, train_f1_gb],
    'Test_F1': [test_f1_rf, test_f1_gb],
    'AUC_ROC': [auc_rf, auc_gb],
    'Overfitting_Gap': [train_acc_rf - test_acc_rf, train_acc_gb - test_acc_gb],
    'CV_Mean': [cv_scores_rf.mean(), cv_scores_gb.mean()],
    'CV_Std': [cv_scores_rf.std(), cv_scores_gb.std()]
})

metrics_summary.to_csv('analysis_outputs/ml_model_metrics_summary.csv', index=False)
print("\n[OK] Saved: ml_model_metrics_summary.csv")

# Save confusion matrices
cm_df_rf = pd.DataFrame(cm_rf, columns=['Pred_Short', 'Pred_Long'], index=['True_Short', 'True_Long'])
cm_df_rf.to_csv('analysis_outputs/confusion_matrix_random_forest.csv')

cm_df_gb = pd.DataFrame(cm_gb, columns=['Pred_Short', 'Pred_Long'], index=['True_Short', 'True_Long'])
cm_df_gb.to_csv('analysis_outputs/confusion_matrix_gradient_boosting.csv')

print("[OK] Saved: confusion_matrix_random_forest.csv")
print("[OK] Saved: confusion_matrix_gradient_boosting.csv")

# ==================================================================================
# CREATE VISUALIZATIONS
# ==================================================================================
print("\n" + "="*100)
print("CREATING ML EVALUATION VISUALIZATIONS")
print("="*100)

# Figure 1: Confusion Matrices
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# RF Confusion Matrix
sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Blues', ax=axes[0],
            xticklabels=['Short', 'Long'], yticklabels=['Short', 'Long'])
axes[0].set_title(f'Random Forest - Confusion Matrix\nAccuracy: {test_acc_rf:.4f}', 
                 fontsize=13, fontweight='bold', pad=15)
axes[0].set_ylabel('True Label', fontsize=11, fontweight='bold')
axes[0].set_xlabel('Predicted Label', fontsize=11, fontweight='bold')

# GB Confusion Matrix
sns.heatmap(cm_gb, annot=True, fmt='d', cmap='Greens', ax=axes[1],
            xticklabels=['Short', 'Long'], yticklabels=['Short', 'Long'])
axes[1].set_title(f'Gradient Boosting - Confusion Matrix\nAccuracy: {test_acc_gb:.4f}', 
                 fontsize=13, fontweight='bold', pad=15)
axes[1].set_ylabel('True Label', fontsize=11, fontweight='bold')
axes[1].set_xlabel('Predicted Label', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('analysis_outputs/ml_viz_01_confusion_matrices.png', dpi=300, bbox_inches='tight')
print("\n[OK] Saved: ml_viz_01_confusion_matrices.png")
plt.close()

# Figure 2: ROC Curves
fig, ax = plt.subplots(figsize=(10, 8))

fpr_rf, tpr_rf, _ = roc_curve(y_test, y_test_proba_rf)
fpr_gb, tpr_gb, _ = roc_curve(y_test, y_test_proba_gb)

ax.plot(fpr_rf, tpr_rf, color='#2E86DE', linewidth=2.5, 
        label=f'Random Forest (AUC = {auc_rf:.4f})')
ax.plot(fpr_gb, tpr_gb, color='#10AC84', linewidth=2.5, 
        label=f'Gradient Boosting (AUC = {auc_gb:.4f})')
ax.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Random Classifier')

ax.set_xlabel('False Positive Rate', fontsize=12, fontweight='bold')
ax.set_ylabel('True Positive Rate', fontsize=12, fontweight='bold')
ax.set_title('ROC Curves - Model Comparison', fontsize=14, fontweight='bold', pad=15)
ax.legend(loc='lower right', fontsize=11)
ax.grid(alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('analysis_outputs/ml_viz_02_roc_curves.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: ml_viz_02_roc_curves.png")
plt.close()

# Figure 3: Model Comparison
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# Accuracy comparison
ax1 = axes[0, 0]
models = ['Random Forest', 'Gradient Boosting']
train_scores = [train_acc_rf, train_acc_gb]
test_scores = [test_acc_rf, test_acc_gb]

x = np.arange(len(models))
width = 0.35

bars1 = ax1.bar(x - width/2, train_scores, width, label='Train', color='#3498db', alpha=0.8, edgecolor='black')
bars2 = ax1.bar(x + width/2, test_scores, width, label='Test', color='#e74c3c', alpha=0.8, edgecolor='black')

ax1.set_ylabel('Accuracy', fontsize=11, fontweight='bold')
ax1.set_title('Accuracy: Train vs Test', fontsize=12, fontweight='bold', pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(models)
ax1.legend(fontsize=10)
ax1.grid(axis='y', alpha=0.3)
ax1.set_ylim([0.9, 1.0])

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# F1-Score comparison
ax2 = axes[0, 1]
f1_train = [train_f1_rf, train_f1_gb]
f1_test = [test_f1_rf, test_f1_gb]

bars3 = ax2.bar(x - width/2, f1_train, width, label='Train', color='#9b59b6', alpha=0.8, edgecolor='black')
bars4 = ax2.bar(x + width/2, f1_test, width, label='Test', color='#f39c12', alpha=0.8, edgecolor='black')

ax2.set_ylabel('F1-Score', fontsize=11, fontweight='bold')
ax2.set_title('F1-Score: Train vs Test', fontsize=12, fontweight='bold', pad=10)
ax2.set_xticks(x)
ax2.set_xticklabels(models)
ax2.legend(fontsize=10)
ax2.grid(axis='y', alpha=0.3)
ax2.set_ylim([0.9, 1.0])

for bars in [bars3, bars4]:
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Overfitting analysis
ax3 = axes[1, 0]
overfit_gaps = [train_acc_rf - test_acc_rf, train_acc_gb - test_acc_gb]
colors = ['#e74c3c' if gap > 0.05 else '#2ecc71' for gap in overfit_gaps]

bars5 = ax3.bar(models, overfit_gaps, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax3.set_ylabel('Overfitting Gap (Train - Test)', fontsize=11, fontweight='bold')
ax3.set_title('Overfitting Analysis', fontsize=12, fontweight='bold', pad=10)
ax3.axhline(y=0.05, color='orange', linestyle='--', linewidth=2, label='Acceptable Threshold (5%)')
ax3.legend(fontsize=9)
ax3.grid(axis='y', alpha=0.3)

for bar, gap in zip(bars5, overfit_gaps):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
            f'{gap:.4f}\n({gap*100:.2f}%)', ha='center', va='bottom' if gap > 0 else 'top', 
            fontsize=10, fontweight='bold')

# Cross-validation scores
ax4 = axes[1, 1]
cv_means = [cv_scores_rf.mean(), cv_scores_gb.mean()]
cv_stds = [cv_scores_rf.std(), cv_scores_gb.std()]

bars6 = ax4.bar(models, cv_means, yerr=cv_stds, capsize=10, 
               color='#16a085', alpha=0.8, edgecolor='black', linewidth=1.5)

ax4.set_ylabel('Cross-Validation Accuracy', fontsize=11, fontweight='bold')
ax4.set_title('5-Fold Cross-Validation Performance', fontsize=12, fontweight='bold', pad=10)
ax4.grid(axis='y', alpha=0.3)
ax4.set_ylim([0.9, 1.0])

for bar, mean, std in zip(bars6, cv_means, cv_stds):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
            f'{mean:.4f}\n±{std:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.suptitle('Machine Learning Model Evaluation - Comprehensive Analysis', 
            fontsize=15, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('analysis_outputs/ml_viz_03_model_comparison.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: ml_viz_03_model_comparison.png")
plt.close()

print("\n" + "="*100)
print("ENHANCED ML MODEL EVALUATION COMPLETE")
print("="*100)
print(f"\nOVERFITTING ASSESSMENT:")
print(f"  Random Forest: {'MINIMAL OVERFITTING' if (train_acc_rf - test_acc_rf) < 0.05 else 'SOME OVERFITTING'}")
print(f"  Gradient Boosting: {'MINIMAL OVERFITTING' if (train_acc_gb - test_acc_gb) < 0.05 else 'SOME OVERFITTING'}")
print(f"\nRECOMMENDATION: {'Both models are well-generalized!' if max(train_acc_rf - test_acc_rf, train_acc_gb - test_acc_gb) < 0.05 else 'Consider regularization for better generalization.'}")

