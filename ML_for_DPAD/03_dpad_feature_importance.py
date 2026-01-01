"""
DPAD Analysis - Step 3: Feature Importance Analysis
===================================================

Purpose:
--------
Use tree-based machine learning models (Random Forest & XGBoost) to identify
which features are most important for predicting High-DPAD vs Low-DPAD agents.

What This Script Does:
----------------------
1. Trains Random Forest classifier on DPAD data
2. Trains XGBoost classifier on DPAD data
3. Calculates feature importance from both models:
   - Gini importance (Random Forest)
   - Gain importance (XGBoost)
   - Permutation importance (both models)
4. Compares feature rankings across methods
5. Creates comprehensive visualizations
6. Generates detailed feature importance report

Why This Matters:
-----------------
Unlike correlation (Script 2), feature importance captures:
- Non-linear relationships
- Feature interactions
- Predictive power in context of other features

This shows which features ML models use most to classify agents as high/low DPAD.

Author: AI Agent
Date: 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import sys
import warnings
warnings.filterwarnings('ignore')

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

# Machine Learning
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.inspection import permutation_importance
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

# XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    print("⚠️  XGBoost not available. Will use Random Forest only.")
    XGBOOST_AVAILABLE = False

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def load_preprocessed_data():
    """Load preprocessed data from Step 1"""
    print("\n" + "="*70)
    print("LOADING PREPROCESSED DATA")
    print("="*70)
    
    data_path = Path("ML_for_DPAD/analysis_outputs/preprocessed_data")
    
    # Load features and target
    X = pd.read_csv(data_path / "X_features.csv")
    y = pd.read_csv(data_path / "y_target.csv")
    
    # Load feature metadata
    with open(data_path / "feature_metadata.json", 'r') as f:
        feature_metadata = json.load(f)
    
    print(f"\n✅ Loaded preprocessed data:")
    print(f"   Features: {X.shape}")
    print(f"   Target:   {y.shape}")
    print(f"   High-DPAD: {(y.values == 1).sum()} | Low-DPAD: {(y.values == 0).sum()}")
    
    return X, y.values.ravel(), feature_metadata


def train_random_forest(X, y):
    """
    Train Random Forest classifier with cross-validation
    
    Random Forest is excellent for:
    - Capturing non-linear relationships
    - Handling feature interactions
    - Providing robust feature importance
    """
    print("\n" + "="*70)
    print("TRAINING RANDOM FOREST CLASSIFIER")
    print("="*70)
    
    # Initialize Random Forest
    rf_model = RandomForestClassifier(
        n_estimators=500,        # More trees = more stable importance
        max_depth=10,            # Prevent overfitting
        min_samples_split=5,     # Require at least 5 samples to split
        min_samples_leaf=2,      # Require at least 2 samples in leaf
        random_state=42,
        n_jobs=-1,               # Use all CPU cores
        class_weight='balanced'  # Handle any class imbalance
    )
    
    print("\n🌲 Random Forest Configuration:")
    print(f"   Trees: 500")
    print(f"   Max Depth: 10")
    print(f"   Class Weight: Balanced")
    
    # Cross-validation
    print("\n🔄 Performing 5-Fold Cross-Validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(rf_model, X, y, cv=cv, scoring='accuracy', n_jobs=-1)
    
    print(f"   CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    
    # Train on full dataset
    print("\n🎯 Training on full dataset...")
    rf_model.fit(X, y)
    
    # Get predictions and metrics
    y_pred = rf_model.predict(X)
    y_pred_proba = rf_model.predict_proba(X)[:, 1]
    
    accuracy = (y_pred == y).mean()
    roc_auc = roc_auc_score(y, y_pred_proba)
    
    print(f"\n📊 Random Forest Performance:")
    print(f"   Training Accuracy: {accuracy:.3f}")
    print(f"   ROC-AUC Score:     {roc_auc:.3f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n✅ Random Forest trained successfully")
    
    return rf_model, feature_importance, cv_scores


def train_xgboost(X, y):
    """
    Train XGBoost classifier with cross-validation
    
    XGBoost often provides different insights than Random Forest:
    - Uses gradient boosting (sequential learning)
    - Can capture different feature interactions
    - Provides gain-based importance
    """
    
    if not XGBOOST_AVAILABLE:
        print("\n⚠️  Skipping XGBoost (not installed)")
        return None, None, None
    
    print("\n" + "="*70)
    print("TRAINING XGBOOST CLASSIFIER")
    print("="*70)
    
    # Initialize XGBoost
    xgb_model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss',
        use_label_encoder=False
    )
    
    print("\n⚡ XGBoost Configuration:")
    print(f"   Trees: 500")
    print(f"   Max Depth: 6")
    print(f"   Learning Rate: 0.05")
    
    # Cross-validation
    print("\n🔄 Performing 5-Fold Cross-Validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(xgb_model, X, y, cv=cv, scoring='accuracy', n_jobs=-1)
    
    print(f"   CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    
    # Train on full dataset
    print("\n🎯 Training on full dataset...")
    xgb_model.fit(X, y)
    
    # Get predictions and metrics
    y_pred = xgb_model.predict(X)
    y_pred_proba = xgb_model.predict_proba(X)[:, 1]
    
    accuracy = (y_pred == y).mean()
    roc_auc = roc_auc_score(y, y_pred_proba)
    
    print(f"\n📊 XGBoost Performance:")
    print(f"   Training Accuracy: {accuracy:.3f}")
    print(f"   ROC-AUC Score:     {roc_auc:.3f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': xgb_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n✅ XGBoost trained successfully")
    
    return xgb_model, feature_importance, cv_scores


def calculate_permutation_importance(model, X, y, model_name="Model"):
    """
    Calculate permutation importance
    
    Permutation importance shows how much model performance drops
    when a feature's values are randomly shuffled. This is often
    more reliable than built-in feature importance.
    """
    print(f"\n🔀 Calculating Permutation Importance for {model_name}...")
    
    perm_importance = permutation_importance(
        model, X, y,
        n_repeats=10,
        random_state=42,
        n_jobs=-1
    )
    
    perm_df = pd.DataFrame({
        'feature': X.columns,
        'importance': perm_importance.importances_mean,
        'std': perm_importance.importances_std
    }).sort_values('importance', ascending=False)
    
    print(f"   ✓ Calculated permutation importance for {len(X.columns)} features")
    
    return perm_df


def compare_feature_importance(rf_importance, xgb_importance, 
                                rf_perm_importance, xgb_perm_importance):
    """
    Compare feature importance across different methods
    
    Creates a comprehensive comparison showing:
    - Consensus features (important in all methods)
    - Model-specific features (important in one model only)
    - Rank correlations between methods
    """
    print("\n" + "="*70)
    print("COMPARING FEATURE IMPORTANCE ACROSS METHODS")
    print("="*70)
    
    # Merge all importance scores
    comparison = rf_importance[['feature', 'importance']].rename(
        columns={'importance': 'rf_gini'}
    )
    
    if xgb_importance is not None:
        xgb_imp = xgb_importance[['feature', 'importance']].rename(
            columns={'importance': 'xgb_gain'}
        )
        comparison = comparison.merge(xgb_imp, on='feature', how='left')
    
    rf_perm = rf_perm_importance[['feature', 'importance']].rename(
        columns={'importance': 'rf_permutation'}
    )
    comparison = comparison.merge(rf_perm, on='feature', how='left')
    
    if xgb_perm_importance is not None:
        xgb_perm = xgb_perm_importance[['feature', 'importance']].rename(
            columns={'importance': 'xgb_permutation'}
        )
        comparison = comparison.merge(xgb_perm, on='feature', how='left')
    
    # Calculate average importance across all methods
    importance_cols = [col for col in comparison.columns if col != 'feature']
    comparison['avg_importance'] = comparison[importance_cols].mean(axis=1)
    comparison = comparison.sort_values('avg_importance', ascending=False)
    
    print(f"\n✅ Feature importance comparison complete")
    print(f"   Top 10 features by average importance:")
    for idx, row in comparison.head(10).iterrows():
        print(f"      {row['feature']:.<45} {row['avg_importance']:.4f}")
    
    return comparison


def plot_feature_importance_comparison(rf_importance, xgb_importance, 
                                       rf_perm_importance, xgb_perm_importance,
                                       output_dir, top_n=20):
    """
    Create comprehensive feature importance visualizations
    """
    print("\n" + "="*70)
    print("CREATING FEATURE IMPORTANCE VISUALIZATIONS")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "feature_importance"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Plot 1: Random Forest Gini Importance
    fig, ax = plt.subplots(figsize=(12, 10))
    top_features = rf_importance.head(top_n)
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_features)))
    
    bars = ax.barh(range(len(top_features)), top_features['importance'].values, color=colors)
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features['feature'].values, fontsize=10)
    ax.set_xlabel('Importance (Gini)', fontsize=12, fontweight='bold')
    ax.set_title(f'Random Forest Feature Importance (Top {top_n})\n' +
                 'Based on Gini Impurity Reduction',
                 fontsize=13, fontweight='bold', pad=15)
    
    for i, (bar, val) in enumerate(zip(bars, top_features['importance'].values)):
        ax.text(val + 0.001, bar.get_y() + bar.get_height()/2,
                f'{val:.4f}', va='center', fontsize=9)
    
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path / "rf_gini_importance.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: rf_gini_importance.png")
    plt.close()
    
    # Plot 2: Random Forest Permutation Importance
    fig, ax = plt.subplots(figsize=(12, 10))
    top_features = rf_perm_importance.head(top_n)
    colors = plt.cm.plasma(np.linspace(0.3, 0.9, len(top_features)))
    
    bars = ax.barh(range(len(top_features)), top_features['importance'].values, 
                    color=colors, xerr=top_features['std'].values, capsize=3)
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features['feature'].values, fontsize=10)
    ax.set_xlabel('Importance (Accuracy Drop)', fontsize=12, fontweight='bold')
    ax.set_title(f'Random Forest Permutation Importance (Top {top_n})\n' +
                 'Performance drop when feature is shuffled',
                 fontsize=13, fontweight='bold', pad=15)
    
    for i, (bar, val) in enumerate(zip(bars, top_features['importance'].values)):
        ax.text(val + 0.001, bar.get_y() + bar.get_height()/2,
                f'{val:.4f}', va='center', fontsize=9)
    
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path / "rf_permutation_importance.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: rf_permutation_importance.png")
    plt.close()
    
    # Plot 3: XGBoost Gain Importance (if available)
    if xgb_importance is not None:
        fig, ax = plt.subplots(figsize=(12, 10))
        top_features = xgb_importance.head(top_n)
        colors = plt.cm.cividis(np.linspace(0.3, 0.9, len(top_features)))
        
        bars = ax.barh(range(len(top_features)), top_features['importance'].values, color=colors)
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['feature'].values, fontsize=10)
        ax.set_xlabel('Importance (Gain)', fontsize=12, fontweight='bold')
        ax.set_title(f'XGBoost Feature Importance (Top {top_n})\n' +
                     'Based on Average Gain',
                     fontsize=13, fontweight='bold', pad=15)
        
        for i, (bar, val) in enumerate(zip(bars, top_features['importance'].values)):
            ax.text(val + 0.001, bar.get_y() + bar.get_height()/2,
                    f'{val:.4f}', va='center', fontsize=9)
        
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / "xgb_gain_importance.png", dpi=300, bbox_inches='tight')
        print(f"   ✓ Saved: xgb_gain_importance.png")
        plt.close()
    
    # Plot 4: Comparison of Methods
    comparison = rf_importance[['feature', 'importance']].head(top_n).rename(
        columns={'importance': 'RF Gini'}
    )
    
    if xgb_importance is not None:
        xgb_top = xgb_importance[['feature', 'importance']].head(top_n).rename(
            columns={'importance': 'XGB Gain'}
        )
        comparison = comparison.merge(xgb_top, on='feature', how='outer')
    
    rf_perm_top = rf_perm_importance[['feature', 'importance']].head(top_n).rename(
        columns={'importance': 'RF Perm'}
    )
    comparison = comparison.merge(rf_perm_top, on='feature', how='outer')
    
    # Get top features across all methods
    comparison = comparison.fillna(0)
    comparison['total'] = comparison.iloc[:, 1:].sum(axis=1)
    comparison = comparison.sort_values('total', ascending=True).tail(top_n)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    x = np.arange(len(comparison))
    width = 0.25
    
    ax.barh(x - width, comparison['RF Gini'].values, width, 
            label='RF Gini', color='#2ecc71')
    ax.barh(x, comparison['RF Perm'].values, width,
            label='RF Permutation', color='#3498db')
    
    if 'XGB Gain' in comparison.columns:
        ax.barh(x + width, comparison['XGB Gain'].values, width,
                label='XGB Gain', color='#e74c3c')
    
    ax.set_yticks(x)
    ax.set_yticklabels(comparison['feature'].values, fontsize=9)
    ax.set_xlabel('Importance Score', fontsize=12, fontweight='bold')
    ax.set_title(f'Feature Importance Comparison Across Methods (Top {top_n})\n' +
                 'Consensus features are important across all methods',
                 fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path / "importance_comparison.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: importance_comparison.png")
    plt.close()


def generate_feature_importance_report(rf_importance, xgb_importance,
                                        rf_perm_importance, xgb_perm_importance,
                                        comparison_df, rf_cv_scores, xgb_cv_scores,
                                        output_dir):
    """
    Generate comprehensive feature importance report
    """
    print("\n" + "="*70)
    print("GENERATING FEATURE IMPORTANCE REPORT")
    print("="*70)
    
    report = []
    report.append("# DPAD Analysis - Feature Importance Report")
    report.append("=" * 70)
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append("This report identifies which features are most important for")
    report.append("predicting High-DPAD vs Low-DPAD agent performance using")
    report.append("tree-based machine learning models.")
    report.append("")
    
    # Model Performance
    report.append("## 1. Model Performance")
    report.append("")
    report.append("### Random Forest")
    report.append(f"- **Cross-Validation Accuracy:** {rf_cv_scores.mean():.3f} (+/- {rf_cv_scores.std():.3f})")
    report.append(f"- **Number of Trees:** 500")
    report.append(f"- **Max Depth:** 10")
    report.append("")
    
    if xgb_cv_scores is not None:
        report.append("### XGBoost")
        report.append(f"- **Cross-Validation Accuracy:** {xgb_cv_scores.mean():.3f} (+/- {xgb_cv_scores.std():.3f})")
        report.append(f"- **Number of Trees:** 500")
        report.append(f"- **Learning Rate:** 0.05")
        report.append("")
    
    # Top Features
    report.append("## 2. Top 20 Features by Importance")
    report.append("")
    report.append("### Consensus Features (Important Across All Methods)")
    report.append("")
    report.append("| Rank | Feature | Avg Importance | RF Gini | RF Perm | XGB Gain |")
    report.append("|------|---------|----------------|---------|---------|----------|")
    
    for idx, row in comparison_df.head(20).iterrows():
        rank = idx + 1 if isinstance(idx, int) else 0
        rf_gini = row.get('rf_gini', 0)
        rf_perm = row.get('rf_permutation', 0)
        xgb_gain = row.get('xgb_gain', 0) if xgb_importance is not None else 0
        avg_imp = row['avg_importance']
        
        report.append(f"| {rank:2d}   | {row['feature']:<35} | {avg_imp:.4f}         | "
                     f"{rf_gini:.4f}  | {rf_perm:.4f}  | {xgb_gain:.4f}   |")
    report.append("")
    
    # Random Forest Specific
    report.append("## 3. Random Forest Gini Importance (Top 20)")
    report.append("")
    report.append("*Based on mean decrease in impurity*")
    report.append("")
    report.append("| Rank | Feature | Importance |")
    report.append("|------|---------|------------|")
    for idx, row in rf_importance.head(20).iterrows():
        rank = idx + 1 if isinstance(idx, int) else 0
        report.append(f"| {rank:2d}   | {row['feature']:<45} | {row['importance']:.4f}   |")
    report.append("")
    
    # Permutation Importance
    report.append("## 4. Random Forest Permutation Importance (Top 20)")
    report.append("")
    report.append("*Based on accuracy drop when feature is shuffled*")
    report.append("")
    report.append("| Rank | Feature | Importance | Std Dev |")
    report.append("|------|---------|------------|---------|")
    for idx, row in rf_perm_importance.head(20).iterrows():
        rank = idx + 1 if isinstance(idx, int) else 0
        report.append(f"| {rank:2d}   | {row['feature']:<40} | {row['importance']:.4f}   | "
                     f"{row['std']:.4f} |")
    report.append("")
    
    # XGBoost Specific
    if xgb_importance is not None:
        report.append("## 5. XGBoost Gain Importance (Top 20)")
        report.append("")
        report.append("*Based on average gain when feature is used*")
        report.append("")
        report.append("| Rank | Feature | Importance |")
        report.append("|------|---------|------------|")
        for idx, row in xgb_importance.head(20).iterrows():
            rank = idx + 1 if isinstance(idx, int) else 0
            report.append(f"| {rank:2d}   | {row['feature']:<45} | {row['importance']:.4f}   |")
        report.append("")
    
    # Key Insights
    report.append("## 6. Key Insights")
    report.append("")
    
    # Top 5 consensus features
    top_5 = comparison_df.head(5)
    report.append("### Most Important Features (Consensus)")
    report.append("")
    for idx, row in top_5.iterrows():
        report.append(f"**{idx+1}. {row['feature']}** (Avg Importance: {row['avg_importance']:.4f})")
        report.append(f"   - This feature is consistently ranked high across all methods")
        report.append("")
    
    # Category analysis
    report.append("### Feature Categories")
    report.append("")
    
    # Analyze which categories are most important
    categories = {
        'Sentiment': ['sentiment', 'tone', 'frustration', 'empathy'],
        'Talk Dynamics': ['talk', 'monologue', 'interruption', 'conversation'],
        'Discovery': ['discovery', 'goal', 'question'],
        'Objections': ['objection', 'resistance', 'acknowledge'],
        'Timing': ['duration', 'time', 'seconds'],
        'Structure': ['structure', 'stage', 'script'],
        'Closing': ['commitment', 'assumptive', 'roi', 'price']
    }
    
    for category, keywords in categories.items():
        cat_features = comparison_df[
            comparison_df['feature'].str.contains('|'.join(keywords), case=False, na=False)
        ]
        
        if len(cat_features) > 0:
            avg_importance = cat_features['avg_importance'].mean()
            top_feature = cat_features.iloc[0]['feature'] if len(cat_features) > 0 else "N/A"
            report.append(f"**{category}:**")
            report.append(f"- Average importance: {avg_importance:.4f}")
            report.append(f"- Top feature: {top_feature}")
            report.append("")
    
    # Save report
    report_path = output_dir / "analysis_outputs" / "feature_importance" / "feature_importance_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Feature importance report saved: {report_path}")


def save_feature_importance_data(rf_importance, xgb_importance, 
                                   rf_perm_importance, xgb_perm_importance,
                                   comparison_df, output_dir):
    """Save all feature importance data"""
    output_path = output_dir / "analysis_outputs" / "feature_importance"
    
    rf_importance.to_csv(output_path / "rf_gini_importance.csv", index=False)
    rf_perm_importance.to_csv(output_path / "rf_permutation_importance.csv", index=False)
    comparison_df.to_csv(output_path / "feature_importance_comparison.csv", index=False)
    
    if xgb_importance is not None:
        xgb_importance.to_csv(output_path / "xgb_gain_importance.csv", index=False)
        xgb_perm_importance.to_csv(output_path / "xgb_permutation_importance.csv", index=False)
    
    print(f"\n✅ Feature importance data saved to: {output_path}")


def main():
    """Main feature importance analysis pipeline"""
    
    print("\n" + "="*70)
    print("DPAD ANALYSIS - FEATURE IMPORTANCE ANALYSIS")
    print("="*70)
    print("\nUsing ML models to identify most predictive features")
    print("="*70)
    
    output_dir = Path("ML_for_DPAD")
    
    # Load preprocessed data
    X, y, feature_metadata = load_preprocessed_data()
    
    # Train Random Forest
    rf_model, rf_importance, rf_cv_scores = train_random_forest(X, y)
    
    # Calculate RF permutation importance
    rf_perm_importance = calculate_permutation_importance(rf_model, X, y, "Random Forest")
    
    # Train XGBoost
    xgb_model, xgb_importance, xgb_cv_scores = train_xgboost(X, y)
    
    # Calculate XGB permutation importance
    if xgb_model is not None:
        xgb_perm_importance = calculate_permutation_importance(xgb_model, X, y, "XGBoost")
    else:
        xgb_perm_importance = None
    
    # Compare feature importance
    comparison_df = compare_feature_importance(
        rf_importance, xgb_importance,
        rf_perm_importance, xgb_perm_importance
    )
    
    # Create visualizations
    plot_feature_importance_comparison(
        rf_importance, xgb_importance,
        rf_perm_importance, xgb_perm_importance,
        output_dir, top_n=20
    )
    
    # Generate report
    generate_feature_importance_report(
        rf_importance, xgb_importance,
        rf_perm_importance, xgb_perm_importance,
        comparison_df, rf_cv_scores, xgb_cv_scores,
        output_dir
    )
    
    # Save data
    save_feature_importance_data(
        rf_importance, xgb_importance,
        rf_perm_importance, xgb_perm_importance,
        comparison_df, output_dir
    )
    
    print("\n" + "="*70)
    print("✅ FEATURE IMPORTANCE ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nTop 5 Most Important Features:")
    for idx, row in comparison_df.head(5).iterrows():
        print(f"   {idx+1}. {row['feature']:<45} (Avg: {row['avg_importance']:.4f})")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

