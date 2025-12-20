"""
ENHANCED ML MODEL EVALUATION - WITH UNDERFITTING CHECK & LEARNING CURVES
Includes train/test loss plots and comprehensive model diagnostics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, learning_curve, validation_curve
from sklearn.metrics import (confusion_matrix, classification_report, roc_curve, roc_auc_score,
                             accuracy_score, log_loss)
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("ENHANCED ML EVALUATION - UNDERFITTING & LEARNING CURVES")
print("="*100)

# Load data
df_combined = pd.read_csv('analysis_outputs/enhanced_combined_data.csv')

# Prepare data
df_ml = df_combined.copy()

for col in df_ml.select_dtypes(include=[np.number]).columns:
    if col != 'call_duration_group':
        df_ml[col].fillna(df_ml[col].median(), inplace=True)

label_encoders = {}
for col in df_ml.select_dtypes(include=['object', 'bool']).columns:
    if col != 'call_duration_group':
        le = LabelEncoder()
        df_ml[col] = df_ml[col].astype(str)
        df_ml[col] = le.fit_transform(df_ml[col])
        label_encoders[col] = le

X = df_ml.drop('call_duration_group', axis=1)
y = df_ml['call_duration_group']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

print(f"\nDataset: {X.shape}")
print(f"Training: {X_train.shape[0]}, Test: {X_test.shape[0]}")

# ==================================================================================
# RANDOM FOREST - WITH LEARNING CURVES
# ==================================================================================
print("\n" + "="*100)
print("RANDOM FOREST - LEARNING CURVES & DIAGNOSTICS")
print("="*100)

rf_model = RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_split=20,
                                  min_samples_leaf=10, random_state=42, n_jobs=-1)

# Learning curve
print("\nCalculating learning curves (this may take a few minutes)...")
train_sizes, train_scores, val_scores = learning_curve(
    rf_model, X_train, y_train, cv=5, n_jobs=-1,
    train_sizes=np.linspace(0.1, 1.0, 10), scoring='accuracy'
)

train_mean = train_scores.mean(axis=1)
train_std = train_scores.std(axis=1)
val_mean = val_scores.mean(axis=1)
val_std = val_scores.std(axis=1)

# Train final model
rf_model.fit(X_train, y_train)

train_acc = rf_model.score(X_train, y_train)
test_acc = rf_model.score(X_test, y_test)

# Predictions for loss calculation
y_train_pred_proba = rf_model.predict_proba(X_train)
y_test_pred_proba = rf_model.predict_proba(X_test)

train_loss = log_loss(y_train, y_train_pred_proba)
test_loss = log_loss(y_test, y_test_pred_proba)

print(f"\nRandom Forest Performance:")
print(f"  Train Accuracy: {train_acc:.4f}")
print(f"  Test Accuracy: {test_acc:.4f}")
print(f"  Train Loss: {train_loss:.4f}")
print(f"  Test Loss: {test_loss:.4f}")
print(f"  Overfitting Gap: {(train_acc - test_acc):.4f}")

# Assess underfitting
if train_acc < 0.85:
    print(f"  [WARNING] UNDERFITTING DETECTED - Train accuracy < 85%")
elif train_acc < 0.90:
    print(f"  [WARNING] SLIGHT UNDERFITTING - Train accuracy < 90%")
else:
    print(f"  [OK] NO UNDERFITTING - Train accuracy = {train_acc:.4f}")

# ==================================================================================
# GRADIENT BOOSTING - WITH LEARNING CURVES
# ==================================================================================
print("\n" + "="*100)
print("GRADIENT BOOSTING - LEARNING CURVES & DIAGNOSTICS")
print("="*100)

gb_model = GradientBoostingClassifier(n_estimators=150, max_depth=5, learning_rate=0.1,
                                      min_samples_split=20, min_samples_leaf=10, random_state=42)

# Learning curve
print("\nCalculating learning curves...")
train_sizes_gb, train_scores_gb, val_scores_gb = learning_curve(
    gb_model, X_train, y_train, cv=5, n_jobs=-1,
    train_sizes=np.linspace(0.1, 1.0, 10), scoring='accuracy'
)

train_mean_gb = train_scores_gb.mean(axis=1)
train_std_gb = train_scores_gb.std(axis=1)
val_mean_gb = val_scores_gb.mean(axis=1)
val_std_gb = val_scores_gb.std(axis=1)

# Train final model
gb_model.fit(X_train, y_train)

train_acc_gb = gb_model.score(X_train, y_train)
test_acc_gb = gb_model.score(X_test, y_test)

y_train_pred_proba_gb = gb_model.predict_proba(X_train)
y_test_pred_proba_gb = gb_model.predict_proba(X_test)

train_loss_gb = log_loss(y_train, y_train_pred_proba_gb)
test_loss_gb = log_loss(y_test, y_test_pred_proba_gb)

print(f"\nGradient Boosting Performance:")
print(f"  Train Accuracy: {train_acc_gb:.4f}")
print(f"  Test Accuracy: {test_acc_gb:.4f}")
print(f"  Train Loss: {train_loss_gb:.4f}")
print(f"  Test Loss: {test_loss_gb:.4f}")
print(f"  Overfitting Gap: {(train_acc_gb - test_acc_gb):.4f}")

if train_acc_gb < 0.85:
    print(f"  [WARNING] UNDERFITTING DETECTED - Train accuracy < 85%")
elif train_acc_gb < 0.90:
    print(f"  [WARNING] SLIGHT UNDERFITTING - Train accuracy < 90%")
else:
    print(f"  [OK] NO UNDERFITTING - Train accuracy = {train_acc_gb:.4f}")

# ==================================================================================
# CREATE LEARNING CURVE VISUALIZATIONS
# ==================================================================================
print("\n" + "="*100)
print("CREATING LEARNING CURVE VISUALIZATIONS")
print("="*100)

fig, axes = plt.subplots(2, 2, figsize=(16, 14))

# RF Learning Curve
ax1 = axes[0, 0]
ax1.plot(train_sizes, train_mean, 'o-', color='#3498db', linewidth=2.5, markersize=8, label='Training Score')
ax1.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.2, color='#3498db')
ax1.plot(train_sizes, val_mean, 'o-', color='#e74c3c', linewidth=2.5, markersize=8, label='Validation Score')
ax1.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.2, color='#e74c3c')
ax1.set_xlabel('Training Set Size', fontsize=11, fontweight='bold')
ax1.set_ylabel('Accuracy Score', fontsize=11, fontweight='bold')
ax1.set_title('Random Forest - Learning Curve\nHow to Read: Training & validation scores should converge', 
             fontsize=12, fontweight='bold', pad=10)
ax1.legend(loc='lower right', fontsize=10)
ax1.grid(alpha=0.3)
ax1.set_ylim([0.85, 1.01])

# Add annotations
ax1.text(0.02, 0.98, f'Final Train: {train_acc:.4f}\nFinal Test: {test_acc:.4f}\nGap: {(train_acc-test_acc):.4f}',
        transform=ax1.transAxes, fontsize=9, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# GB Learning Curve
ax2 = axes[0, 1]
ax2.plot(train_sizes_gb, train_mean_gb, 'o-', color='#2ecc71', linewidth=2.5, markersize=8, label='Training Score')
ax2.fill_between(train_sizes_gb, train_mean_gb - train_std_gb, train_mean_gb + train_std_gb, alpha=0.2, color='#2ecc71')
ax2.plot(train_sizes_gb, val_mean_gb, 'o-', color='#e67e22', linewidth=2.5, markersize=8, label='Validation Score')
ax2.fill_between(train_sizes_gb, val_mean_gb - val_std_gb, val_mean_gb + val_std_gb, alpha=0.2, color='#e67e22')
ax2.set_xlabel('Training Set Size', fontsize=11, fontweight='bold')
ax2.set_ylabel('Accuracy Score', fontsize=11, fontweight='bold')
ax2.set_title('Gradient Boosting - Learning Curve\nHow to Read: Training & validation scores should converge', 
             fontsize=12, fontweight='bold', pad=10)
ax2.legend(loc='lower right', fontsize=10)
ax2.grid(alpha=0.3)
ax2.set_ylim([0.85, 1.01])

ax2.text(0.02, 0.98, f'Final Train: {train_acc_gb:.4f}\nFinal Test: {test_acc_gb:.4f}\nGap: {(train_acc_gb-test_acc_gb):.4f}',
        transform=ax2.transAxes, fontsize=9, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Train/Test Loss Comparison
ax3 = axes[1, 0]
models = ['Random Forest', 'Gradient Boosting']
train_losses = [train_loss, train_loss_gb]
test_losses = [test_loss, test_loss_gb]

x = np.arange(len(models))
width = 0.35

bars1 = ax3.bar(x - width/2, train_losses, width, label='Train Loss', color='#9b59b6', alpha=0.8, edgecolor='black')
bars2 = ax3.bar(x + width/2, test_losses, width, label='Test Loss', color='#f39c12', alpha=0.8, edgecolor='black')

ax3.set_ylabel('Log Loss (Lower is Better)', fontsize=11, fontweight='bold')
ax3.set_title('Train vs Test Loss\nHow to Read: Lower is better, similar values = good fit', 
             fontsize=12, fontweight='bold', pad=10)
ax3.set_xticks(x)
ax3.set_xticklabels(models)
ax3.legend(fontsize=10)
ax3.grid(axis='y', alpha=0.3)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Overfitting/Underfitting Assessment
ax4 = axes[1, 1]
assessment_data = {
    'Random Forest': {
        'Train Acc': train_acc,
        'Test Acc': test_acc,
        'Overfit Gap': train_acc - test_acc
    },
    'Gradient Boosting': {
        'Train Acc': train_acc_gb,
        'Test Acc': test_acc_gb,
        'Overfit Gap': train_acc_gb - test_acc_gb
    }
}

# Create assessment visualization
categories = ['Train Acc', 'Test Acc']
rf_scores = [train_acc, test_acc]
gb_scores = [train_acc_gb, test_acc_gb]

x = np.arange(len(categories))
width = 0.35

bars1 = ax4.bar(x - width/2, rf_scores, width, label='Random Forest', color='#3498db', alpha=0.8, edgecolor='black')
bars2 = ax4.bar(x + width/2, gb_scores, width, label='Gradient Boosting', color='#2ecc71', alpha=0.8, edgecolor='black')

ax4.set_ylabel('Accuracy', fontsize=11, fontweight='bold')
ax4.set_title('Overfitting/Underfitting Assessment\nHow to Read: Train~Test=Good, Train>>Test=Overfit, Both Low=Underfit', 
             fontsize=12, fontweight='bold', pad=10)
ax4.set_xticks(x)
ax4.set_xticklabels(categories)
ax4.legend(fontsize=10)
ax4.grid(axis='y', alpha=0.3)
ax4.set_ylim([0.9, 1.01])

# Add assessment text
assessment_text = f"RF: {'[OK] Good Fit' if abs(train_acc - test_acc) < 0.05 else '[WARNING] Overfit'}\n"
assessment_text += f"GB: {'[OK] Good Fit' if abs(train_acc_gb - test_acc_gb) < 0.05 else '[WARNING] Overfit'}"
ax4.text(0.98, 0.02, assessment_text, transform=ax4.transAxes, fontsize=10,
        verticalalignment='bottom', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

plt.suptitle('Machine Learning Model Diagnostics - Learning Curves & Fit Analysis', 
            fontsize=15, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('analysis_outputs/ml_viz_04_learning_curves_and_diagnostics.png', dpi=300, bbox_inches='tight')
print("\n[OK] Saved: ml_viz_04_learning_curves_and_diagnostics.png")
plt.close()

# Save metrics
metrics_detailed = pd.DataFrame({
    'Model': ['Random Forest', 'Gradient Boosting'],
    'Train_Accuracy': [train_acc, train_acc_gb],
    'Test_Accuracy': [test_acc, test_acc_gb],
    'Train_Loss': [train_loss, train_loss_gb],
    'Test_Loss': [test_loss, test_loss_gb],
    'Overfitting_Gap': [train_acc - test_acc, train_acc_gb - test_acc_gb],
    'Underfitting_Check': ['No Underfitting' if train_acc >= 0.9 else 'Check Required',
                          'No Underfitting' if train_acc_gb >= 0.9 else 'Check Required'],
    'Final_Assessment': ['Well-Generalized' if abs(train_acc - test_acc) < 0.05 else 'Some Overfitting',
                        'Well-Generalized' if abs(train_acc_gb - test_acc_gb) < 0.05 else 'Some Overfitting']
})

metrics_detailed.to_csv('analysis_outputs/ml_detailed_diagnostics.csv', index=False)
print("[OK] Saved: ml_detailed_diagnostics.csv")

print("\n" + "="*100)
print("MODEL DIAGNOSTICS COMPLETE")
print("="*100)
print("\nFINAL ASSESSMENT:")
print(f"Random Forest: {metrics_detailed.loc[0, 'Final_Assessment']}")
print(f"Gradient Boosting: {metrics_detailed.loc[1, 'Final_Assessment']}")
print("\nUNDERFITTING CHECK:")
print(f"Random Forest: {metrics_detailed.loc[0, 'Underfitting_Check']}")
print(f"Gradient Boosting: {metrics_detailed.loc[1, 'Underfitting_Check']}")

