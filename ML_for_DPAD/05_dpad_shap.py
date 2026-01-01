"""
DPAD Analysis - Step 5: SHAP Analysis
======================================

Purpose:
--------
Use SHAP (SHapley Additive exPlanations) to explain model predictions
and understand how features contribute to classifying agents as High vs Low DPAD.

What This Script Does:
----------------------
1. Loads trained Random Forest model from Step 3
2. Calculates SHAP values for all predictions
3. Creates comprehensive SHAP visualizations:
   - Summary plot (global feature importance)
   - Bar plot (mean absolute SHAP values)
   - Dependence plots (feature interactions)
   - Waterfall plots (individual predictions)
   - Force plots (how features push predictions)
4. Identifies key feature interactions
5. Generates interpretability report

Why SHAP Matters:
-----------------
SHAP provides:
- Feature attribution: How much each feature contributes to each prediction
- Direction: Does a feature push toward High-DPAD or Low-DPAD?
- Interactions: How features work together
- Individual explanations: Why was THIS specific call classified as high/low?

Unlike simple feature importance, SHAP shows the complete story of
HOW your model makes decisions.

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
import pickle

# SHAP
try:
    import shap
    SHAP_AVAILABLE = True
    print("✓ SHAP library loaded successfully")
except ImportError:
    SHAP_AVAILABLE = False
    print("⚠️  SHAP not available. Installing SHAP is recommended:")
    print("   pip install shap")

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def load_data_and_model():
    """Load preprocessed data and trained model"""
    print("\n" + "="*70)
    print("LOADING DATA AND MODEL")
    print("="*70)
    
    data_path = Path("ML_for_DPAD/analysis_outputs/preprocessed_data")
    
    # Load features and target
    X = pd.read_csv(data_path / "X_features.csv")
    y = pd.read_csv(data_path / "y_target.csv").values.ravel()
    
    # Load feature metadata
    with open(data_path / "feature_metadata.json", 'r') as f:
        feature_metadata = json.load(f)
    
    print(f"\n✅ Loaded data:")
    print(f"   Features: {X.shape}")
    print(f"   Target:   {y.shape}")
    
    # Train Random Forest (or load if exists)
    print(f"\n🌲 Training Random Forest model...")
    rf_model = RandomForestClassifier(
        n_estimators=500,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    rf_model.fit(X, y)
    
    accuracy = (rf_model.predict(X) == y).mean()
    print(f"   Model accuracy: {accuracy:.3f}")
    
    return X, y, rf_model, feature_metadata


def calculate_shap_values(model, X, sample_size=None):
    """
    Calculate SHAP values using TreeExplainer (optimized for tree-based models)
    
    For Random Forest, TreeExplainer is exact and fast
    """
    if not SHAP_AVAILABLE:
        print("\n⚠️  SHAP not available. Skipping SHAP analysis.")
        return None, None
    
    print("\n" + "="*70)
    print("CALCULATING SHAP VALUES")
    print("="*70)
    
    # For small datasets, use all data. For large datasets, sample.
    if sample_size and len(X) > sample_size:
        print(f"\n📊 Sampling {sample_size} instances for SHAP calculation...")
        indices = np.random.choice(len(X), sample_size, replace=False)
        X_sample = X.iloc[indices]
    else:
        X_sample = X
        print(f"\n📊 Using all {len(X)} instances for SHAP calculation...")
    
    # Create TreeExplainer
    print("   Creating SHAP TreeExplainer...")
    explainer = shap.TreeExplainer(model)
    
    # Calculate SHAP values
    print("   Calculating SHAP values (this may take a moment)...")
    shap_values = explainer.shap_values(X_sample)
    
    # For binary classification, shap_values is a list [class_0_shap, class_1_shap]
    # We want class 1 (High-DPAD) SHAP values
    if isinstance(shap_values, list):
        shap_values = shap_values[1]  # High-DPAD class
        base_value = explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value
    elif len(shap_values.shape) == 3:
        # Shape is (n_samples, n_features, n_classes)
        shap_values = shap_values[:, :, 1]  # High-DPAD class
        base_value = explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value
    else:
        base_value = explainer.expected_value
    
    print(f"\n✅ SHAP values calculated!")
    print(f"   Shape: {shap_values.shape}")
    print(f"   Base value (expected): {base_value}")
    
    return shap_values, explainer


def create_shap_summary_plot(shap_values, X, output_dir):
    """
    Create SHAP summary plot showing global feature importance
    
    This plot shows:
    - Which features are most important (y-axis ranking)
    - Distribution of SHAP values (spread on x-axis)
    - Feature values (color: red=high, blue=low)
    - Direction of effect (positive SHAP = pushes toward High-DPAD)
    """
    print("\n" + "="*70)
    print("CREATING SHAP VISUALIZATIONS")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "shap_analysis"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Summary plot
    print("\n   Creating SHAP summary plot...")
    plt.figure(figsize=(14, 12))
    shap.summary_plot(shap_values, X, show=False, max_display=20)
    plt.title("SHAP Summary Plot: Feature Impact on High-DPAD Classification\n" +
              "Red = High feature value | Blue = Low feature value\n" +
              "Right = Pushes toward High-DPAD | Left = Pushes toward Low-DPAD",
              fontsize=12, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_path / "shap_summary_plot.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: shap_summary_plot.png")
    plt.close()


def create_shap_bar_plot(shap_values, X, output_dir):
    """
    Create SHAP bar plot showing mean absolute SHAP values
    
    This is similar to feature importance but based on SHAP values
    """
    print("\n   Creating SHAP bar plot...")
    
    output_path = output_dir / "analysis_outputs" / "shap_analysis"
    
    plt.figure(figsize=(12, 10))
    shap.summary_plot(shap_values, X, plot_type="bar", show=False, max_display=20)
    plt.title("SHAP Feature Importance (Mean Absolute SHAP Value)\n" +
              "Higher = More impact on predictions",
              fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(output_path / "shap_bar_plot.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: shap_bar_plot.png")
    plt.close()


def create_shap_dependence_plots(shap_values, X, output_dir, top_n=6):
    """
    Create SHAP dependence plots for top features
    
    Dependence plots show:
    - How a feature's value affects its SHAP value
    - Interactions with other features (shown in color)
    """
    print(f"\n   Creating SHAP dependence plots for top {top_n} features...")
    
    output_path = output_dir / "analysis_outputs" / "shap_analysis"
    
    # Calculate mean absolute SHAP for feature ranking
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_features_idx = np.argsort(mean_abs_shap)[-top_n:][::-1]
    top_features = [X.columns[i] for i in top_features_idx]
    
    # Create dependence plots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for i, feature in enumerate(top_features):
        if i >= len(axes):
            break
        
        ax = axes[i]
        
        # Create dependence plot
        shap.dependence_plot(
            feature, shap_values, X,
            interaction_index="auto",
            ax=ax, show=False
        )
        ax.set_title(f"{feature}\n(SHAP Dependence)", fontsize=10, fontweight='bold')
    
    plt.suptitle("SHAP Dependence Plots: Top Features\n" +
                 "X-axis: Feature value | Y-axis: SHAP value (impact)\n" +
                 "Color: Interaction with another feature",
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path / "shap_dependence_plots.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: shap_dependence_plots.png")
    plt.close()


def create_shap_waterfall_plots(shap_values, X, y, explainer, output_dir, n_examples=4):
    """
    Create SHAP waterfall plots for individual predictions
    
    Shows how features combine to push a prediction from base value
    to final prediction for specific examples
    """
    print(f"\n   Creating SHAP waterfall plots for {n_examples} examples...")
    
    output_path = output_dir / "analysis_outputs" / "shap_analysis"
    
    # Select diverse examples
    high_dpad_idx = np.where(y == 1)[0]
    low_dpad_idx = np.where(y == 0)[0]
    
    # Pick one high-DPAD and one low-DPAD example
    examples = []
    if len(high_dpad_idx) > 0:
        examples.append(high_dpad_idx[0])  # First high-DPAD
        if len(high_dpad_idx) > 1:
            examples.append(high_dpad_idx[len(high_dpad_idx)//2])  # Middle high-DPAD
    if len(low_dpad_idx) > 0:
        examples.append(low_dpad_idx[0])  # First low-DPAD
        if len(low_dpad_idx) > 1:
            examples.append(low_dpad_idx[len(low_dpad_idx)//2])  # Middle low-DPAD
    
    examples = examples[:n_examples]
    
    for idx in examples:
        plt.figure(figsize=(12, 8))
        
        # Create explanation object
        base_val = explainer.expected_value
        if isinstance(base_val, list):
            base_val = base_val[1]
        elif isinstance(base_val, np.ndarray):
            base_val = base_val[1]
        
        explanation = shap.Explanation(
            values=shap_values[idx],
            base_values=base_val,
            data=X.iloc[idx].values,
            feature_names=X.columns.tolist()
        )
        
        # Waterfall plot
        shap.plots.waterfall(explanation, max_display=15, show=False)
        
        actual_class = "High-DPAD" if y[idx] == 1 else "Low-DPAD"
        plt.title(f"SHAP Waterfall Plot: Call #{idx} (Actual: {actual_class})\n" +
                  "Shows how features push prediction from base value to final output",
                  fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path / f"shap_waterfall_call_{idx}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"   ✓ Saved: {len(examples)} waterfall plots")


def analyze_feature_interactions(shap_values, X, top_n=10):
    """
    Analyze and report top feature interactions from SHAP values
    """
    print("\n" + "="*70)
    print("ANALYZING FEATURE INTERACTIONS")
    print("="*70)
    
    # Calculate mean absolute SHAP for ranking
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'mean_abs_shap': mean_abs_shap
    }).sort_values('mean_abs_shap', ascending=False)
    
    print(f"\n📊 Top {top_n} Features by Mean Absolute SHAP Value:")
    print("-" * 70)
    for idx, row in feature_importance.head(top_n).iterrows():
        print(f"   {row['feature']:.<50} {row['mean_abs_shap']:.4f}")
    
    return feature_importance


def generate_shap_report(shap_values, X, y, feature_importance, output_dir):
    """
    Generate comprehensive SHAP analysis report
    """
    print("\n" + "="*70)
    print("GENERATING SHAP REPORT")
    print("="*70)
    
    report = []
    report.append("# DPAD Analysis - SHAP Interpretability Report")
    report.append("=" * 70)
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append("This report explains HOW the Random Forest model classifies calls")
    report.append("as High-DPAD vs Low-DPAD using SHAP (SHapley Additive exPlanations).")
    report.append("")
    report.append("SHAP values show the contribution of each feature to each prediction:")
    report.append("- Positive SHAP: Feature pushes prediction toward High-DPAD")
    report.append("- Negative SHAP: Feature pushes prediction toward Low-DPAD")
    report.append("- Magnitude: How strong the push is")
    report.append("")
    
    # Top features by SHAP
    report.append("## 1. Global Feature Importance (SHAP-based)")
    report.append("")
    report.append("Features ranked by mean absolute SHAP value:")
    report.append("")
    report.append("| Rank | Feature | Mean |SHAP| | Interpretation |")
    report.append("|------|---------|------------|----------------|")
    
    for idx, row in feature_importance.head(20).iterrows():
        rank = idx + 1 if isinstance(idx, int) else list(feature_importance.index).index(idx) + 1
        report.append(f"| {rank:2d}   | {row['feature']:<45} | {row['mean_abs_shap']:.4f}   | "
                     f"High impact on predictions |")
    report.append("")
    
    # SHAP value statistics
    report.append("## 2. SHAP Value Statistics")
    report.append("")
    
    # Calculate overall statistics
    high_dpad_mask = y == 1
    low_dpad_mask = y == 0
    
    high_dpad_shap = shap_values[high_dpad_mask].mean(axis=0)
    low_dpad_shap = shap_values[low_dpad_mask].mean(axis=0)
    
    report.append("### Average SHAP Values by Group")
    report.append("")
    report.append("| Feature | High-DPAD Avg | Low-DPAD Avg | Difference |")
    report.append("|---------|---------------|--------------|------------|")
    
    # Top features by SHAP difference
    shap_diff = high_dpad_shap - low_dpad_shap
    diff_ranking = np.argsort(np.abs(shap_diff))[-10:][::-1]
    
    for idx in diff_ranking:
        feature = X.columns[idx]
        report.append(f"| {feature:<40} | {high_dpad_shap[idx]:>8.4f}      | "
                     f"{low_dpad_shap[idx]:>8.4f}     | {shap_diff[idx]:>7.4f}   |")
    report.append("")
    
    # Key insights
    report.append("## 3. Key Insights from SHAP Analysis")
    report.append("")
    
    # Most positive average SHAP (pushes toward High-DPAD)
    most_positive = np.argsort(shap_values.mean(axis=0))[-5:][::-1]
    report.append("### Features that Push Toward High-DPAD Classification")
    report.append("")
    for idx in most_positive:
        feature = X.columns[idx]
        avg_shap = shap_values[:, idx].mean()
        report.append(f"- **{feature}**: Avg SHAP = {avg_shap:.4f}")
    report.append("")
    
    # Most negative average SHAP (pushes toward Low-DPAD)
    most_negative = np.argsort(shap_values.mean(axis=0))[:5]
    report.append("### Features that Push Toward Low-DPAD Classification")
    report.append("")
    for idx in most_negative:
        feature = X.columns[idx]
        avg_shap = shap_values[:, idx].mean()
        report.append(f"- **{feature}**: Avg SHAP = {avg_shap:.4f}")
    report.append("")
    
    # Interpretation guide
    report.append("## 4. How to Interpret SHAP Plots")
    report.append("")
    report.append("### Summary Plot")
    report.append("- **Y-axis**: Features ranked by importance")
    report.append("- **X-axis**: SHAP value (impact on prediction)")
    report.append("- **Color**: Feature value (red=high, blue=low)")
    report.append("- **Position**: Right of zero = pushes toward High-DPAD")
    report.append("")
    report.append("### Dependence Plot")
    report.append("- **X-axis**: Feature value")
    report.append("- **Y-axis**: SHAP value for that feature")
    report.append("- **Color**: Value of interacting feature")
    report.append("- **Pattern**: Shows relationship and interactions")
    report.append("")
    report.append("### Waterfall Plot")
    report.append("- Shows step-by-step how features combine")
    report.append("- Starts from base value (expected)")
    report.append("- Each bar adds/subtracts to reach final prediction")
    report.append("- Red bars push up, blue bars push down")
    report.append("")
    
    # Save report
    report_path = output_dir / "analysis_outputs" / "shap_analysis" / "shap_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ SHAP report saved: {report_path}")


def save_shap_data(shap_values, X, feature_importance, output_dir):
    """Save SHAP values and feature importance"""
    output_path = output_dir / "analysis_outputs" / "shap_analysis"
    
    # Save SHAP values
    shap_df = pd.DataFrame(shap_values, columns=X.columns)
    shap_df.to_csv(output_path / "shap_values.csv", index=False)
    
    # Save feature importance
    feature_importance.to_csv(output_path / "shap_feature_importance.csv", index=False)
    
    print(f"\n✅ SHAP data saved to: {output_path}")


def create_shap_comparison_with_xgboost(X, y, output_dir):
    """
    Train XGBoost model and create SHAP comparison between RF and XGBoost
    Similar to ML V2 format
    """
    print("\n" + "="*70)
    print("CREATING RF vs XGBOost SHAP COMPARISON")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "shap_analysis"
    
    try:
        import xgboost as xgb
        
        # Train XGBoost model
        print("\n🌲 Training XGBoost model...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
            scale_pos_weight=len(y[y==0])/len(y[y==1])  # Handle imbalance
        )
        xgb_model.fit(X, y)
        
        accuracy = (xgb_model.predict(X) == y).mean()
        print(f"   XGBoost accuracy: {accuracy:.3f}")
        
        # Calculate SHAP for XGBoost
        print("   Calculating SHAP values for XGBoost...")
        explainer_xgb = shap.TreeExplainer(xgb_model)
        shap_values_xgb = explainer_xgb.shap_values(X)
        
        # Handle XGBoost SHAP format
        if isinstance(shap_values_xgb, list):
            shap_values_xgb = shap_values_xgb[1]  # High-DPAD class
        
        # Calculate mean absolute SHAP for XGBoost
        mean_abs_shap_xgb = np.abs(shap_values_xgb).mean(axis=0)
        
        # Also recalculate for RF
        print("   Recalculating SHAP values for Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=500,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        rf_model.fit(X, y)
        
        explainer_rf = shap.TreeExplainer(rf_model)
        shap_values_rf = explainer_rf.shap_values(X)
        
        if isinstance(shap_values_rf, list):
            shap_values_rf = shap_values_rf[1]
        elif len(shap_values_rf.shape) == 3:
            shap_values_rf = shap_values_rf[:, :, 1]
        
        mean_abs_shap_rf = np.abs(shap_values_rf).mean(axis=0)
        
        # Create comparison DataFrame (ML V2 format)
        shap_comparison = pd.DataFrame({
            'Variable': X.columns,
            'SHAP_RF': mean_abs_shap_rf,
            'SHAP_XGB': mean_abs_shap_xgb,
            'SHAP_Avg': (mean_abs_shap_rf + mean_abs_shap_xgb) / 2
        }).sort_values('SHAP_Avg', ascending=False)
        
        # Save comparison
        shap_comparison.to_csv(output_path / "05_shap_importance.csv", index=False)
        print(f"\n   ✓ Saved: 05_shap_importance.csv")
        
        # Create comparison visualization
        fig, ax = plt.subplots(figsize=(14, 10))
        
        top_n = 20
        top_vars = shap_comparison.head(top_n)
        
        x = np.arange(len(top_vars))
        width = 0.35
        
        bars1 = ax.barh(x - width/2, top_vars['SHAP_RF'], width, 
                       label='Random Forest', color='#4ECDC4', alpha=0.8, edgecolor='black')
        bars2 = ax.barh(x + width/2, top_vars['SHAP_XGB'], width,
                       label='XGBoost', color='#FFD700', alpha=0.8, edgecolor='black')
        
        ax.set_yticks(x)
        ax.set_yticklabels(top_vars['Variable'], fontsize=10)
        ax.set_xlabel('Mean |SHAP value| (average impact on model output magnitude)', 
                     fontsize=11, fontweight='bold')
        ax.set_title('LEVEL 1: VARIABLE IMPORTANCE (Random Forest vs XGBoost SHAP)\n' +
                    'Mean |SHAP value| shows average impact on predictions',
                    fontsize=13, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='lower right')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                width_val = bar.get_width()
                ax.text(width_val + 0.001, bar.get_y() + bar.get_height()/2,
                       f'{width_val:.3f}',
                       va='center', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(output_path / "05_shap_comparison_rf_vs_xgb.png", dpi=300, bbox_inches='tight')
        print(f"   ✓ Saved: 05_shap_comparison_rf_vs_xgb.png")
        plt.close()
        
        print(f"\n✅ SHAP comparison complete!")
        print(f"   Top 3 variables by average SHAP:")
        for idx, row in shap_comparison.head(3).iterrows():
            print(f"      {row['Variable']:.<45} {row['SHAP_Avg']:.4f}")
        
        return shap_values_rf, shap_values_xgb, shap_comparison
        
    except ImportError:
        print("\n⚠️  XGBoost not available. Skipping RF vs XGB comparison.")
        print("   Install with: pip install xgboost")
        return None, None, None


def main():
    """Main SHAP analysis pipeline"""
    
    if not SHAP_AVAILABLE:
        print("\n" + "="*70)
        print("⚠️  SHAP LIBRARY NOT AVAILABLE")
        print("="*70)
        print("\nPlease install SHAP to run this analysis:")
        print("  pip install shap")
        print("\nSkipping SHAP analysis...")
        return
    
    print("\n" + "="*70)
    print("DPAD ANALYSIS - SHAP INTERPRETABILITY")
    print("="*70)
    print("\nExplaining model predictions with SHAP values")
    print("="*70)
    
    output_dir = Path("ML_for_DPAD")
    
    # Load data and model
    X, y, model, feature_metadata = load_data_and_model()
    
    # Create RF vs XGBoost SHAP comparison (ML V2 style)
    shap_values_rf, shap_values_xgb, shap_comparison = create_shap_comparison_with_xgboost(X, y, output_dir)
    
    # Use RF SHAP values for detailed analysis
    if shap_values_rf is not None:
        shap_values = shap_values_rf
        explainer = shap.TreeExplainer(model)
    else:
        # Fallback to original single-model approach
        shap_values, explainer = calculate_shap_values(model, X)
        shap_comparison = None
    
    if shap_values is None:
        print("\n⚠️  Could not calculate SHAP values")
        return
    
    # Create visualizations
    create_shap_summary_plot(shap_values, X, output_dir)
    create_shap_bar_plot(shap_values, X, output_dir)
    create_shap_dependence_plots(shap_values, X, output_dir, top_n=6)
    create_shap_waterfall_plots(shap_values, X, y, explainer, output_dir, n_examples=6)  # Increased to 6
    
    # Analyze interactions
    if shap_comparison is not None:
        feature_importance = shap_comparison[['Variable', 'SHAP_Avg']].rename(
            columns={'Variable': 'feature', 'SHAP_Avg': 'mean_abs_shap'}
        )
    else:
        feature_importance = analyze_feature_interactions(shap_values, X, top_n=10)
    
    # Generate report
    generate_shap_report(shap_values, X, y, feature_importance, output_dir)
    
    # Save data
    save_shap_data(shap_values, X, feature_importance, output_dir)
    
    print("\n" + "="*70)
    print("✅ SHAP ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nTop 5 Most Important Features (by mean |SHAP|):")
    for idx, row in feature_importance.head(5).iterrows():
        feat_name = row['feature'] if 'feature' in row else row.get('Variable', 'Unknown')
        shap_val = row['mean_abs_shap'] if 'mean_abs_shap' in row else row.get('SHAP_Avg', 0)
        print(f"   {feat_name:.<50} {shap_val:.4f}")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

