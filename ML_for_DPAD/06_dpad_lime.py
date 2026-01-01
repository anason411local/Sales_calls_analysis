"""
DPAD Analysis - Step 6: LIME Analysis
======================================

Purpose:
--------
Use LIME (Local Interpretable Model-agnostic Explanations) to explain
individual predictions in a human-interpretable way.

What This Script Does:
----------------------
1. Loads trained Random Forest model from Step 3
2. Creates LIME explainer for tabular data
3. Generates local explanations for sample predictions:
   - High-DPAD calls correctly classified
   - Low-DPAD calls correctly classified
   - Edge cases (if any misclassifications)
4. Visualizes feature contributions for each example
5. Compares LIME explanations with SHAP (optional)
6. Generates interpretability report

Why LIME Matters:
-----------------
LIME complements SHAP by:
- Providing simpler, more interpretable explanations
- Working with any model (model-agnostic)
- Explaining individual predictions locally
- Using an interpretable linear model as proxy

While SHAP gives global importance, LIME answers:
"Why was THIS specific call classified as High/Low DPAD?"

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

# LIME
try:
    import lime
    import lime.lime_tabular
    LIME_AVAILABLE = True
    print("✓ LIME library loaded successfully")
except ImportError:
    LIME_AVAILABLE = False
    print("⚠️  LIME not available. Installing LIME is recommended:")
    print("   pip install lime")

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def load_data_and_model():
    """Load preprocessed data and train model"""
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
    
    # Train Random Forest
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
    
    # Get predictions
    predictions = rf_model.predict(X)
    accuracy = (predictions == y).mean()
    
    print(f"   Model accuracy: {accuracy:.3f}")
    print(f"   Correct predictions: {(predictions == y).sum()}/{len(y)}")
    
    return X, y, rf_model, predictions, feature_metadata


def create_lime_explainer(X, feature_names, class_names):
    """
    Create LIME explainer for tabular data
    
    LIME uses a linear model to approximate the model's behavior
    locally around each prediction
    """
    if not LIME_AVAILABLE:
        return None
    
    print("\n" + "="*70)
    print("CREATING LIME EXPLAINER")
    print("="*70)
    
    print("\n🔬 Initializing LIME TabularExplainer...")
    
    # Create explainer
    explainer = lime.lime_tabular.LimeTabularExplainer(
        training_data=X.values,
        feature_names=feature_names,
        class_names=class_names,
        mode='classification',
        random_state=42
    )
    
    print("✅ LIME explainer created successfully")
    
    return explainer


def select_diverse_examples(X, y, predictions, n_examples=6):
    """
    Select diverse examples for LIME explanation:
    - Correctly classified High-DPAD
    - Correctly classified Low-DPAD
    - Misclassified (if any)
    """
    print("\n" + "="*70)
    print("SELECTING EXAMPLE CALLS FOR EXPLANATION")
    print("="*70)
    
    examples = []
    descriptions = []
    
    # Correctly classified High-DPAD
    high_correct = np.where((y == 1) & (predictions == 1))[0]
    if len(high_correct) > 0:
        # Pick first and a middle one
        examples.append(high_correct[0])
        descriptions.append("High-DPAD (Correctly Classified) - Example 1")
        if len(high_correct) > 1:
            examples.append(high_correct[len(high_correct)//2])
            descriptions.append("High-DPAD (Correctly Classified) - Example 2")
    
    # Correctly classified Low-DPAD
    low_correct = np.where((y == 0) & (predictions == 0))[0]
    if len(low_correct) > 0:
        # Pick first and a middle one
        examples.append(low_correct[0])
        descriptions.append("Low-DPAD (Correctly Classified) - Example 1")
        if len(low_correct) > 1:
            examples.append(low_correct[len(low_correct)//2])
            descriptions.append("Low-DPAD (Correctly Classified) - Example 2")
    
    # Misclassified High-DPAD (predicted as Low)
    high_wrong = np.where((y == 1) & (predictions == 0))[0]
    if len(high_wrong) > 0:
        examples.append(high_wrong[0])
        descriptions.append("High-DPAD MISCLASSIFIED as Low-DPAD")
    
    # Misclassified Low-DPAD (predicted as High)
    low_wrong = np.where((y == 0) & (predictions == 1))[0]
    if len(low_wrong) > 0:
        examples.append(low_wrong[0])
        descriptions.append("Low-DPAD MISCLASSIFIED as High-DPAD")
    
    # Limit to n_examples
    examples = examples[:n_examples]
    descriptions = descriptions[:n_examples]
    
    print(f"\n✅ Selected {len(examples)} diverse examples:")
    for idx, desc in zip(examples, descriptions):
        print(f"   Call #{idx}: {desc}")
    
    return examples, descriptions


def generate_lime_explanations(explainer, model, X, examples, descriptions, output_dir):
    """
    Generate LIME explanations for selected examples
    """
    print("\n" + "="*70)
    print("GENERATING LIME EXPLANATIONS")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "lime_analysis"
    output_path.mkdir(parents=True, exist_ok=True)
    
    explanations = []
    
    for idx, (example_idx, description) in enumerate(zip(examples, descriptions)):
        print(f"\n   Explaining Call #{example_idx}: {description}")
        
        # Get LIME explanation
        exp = explainer.explain_instance(
            data_row=X.iloc[example_idx].values,
            predict_fn=model.predict_proba,
            num_features=15,  # Show top 15 features
            num_samples=5000  # Number of samples for local approximation
        )
        
        explanations.append({
            'index': example_idx,
            'description': description,
            'explanation': exp
        })
        
        # Save visualization
        fig = exp.as_pyplot_figure()
        fig.suptitle(f"LIME Explanation: Call #{example_idx}\n{description}",
                    fontsize=11, fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig(output_path / f"lime_explanation_call_{example_idx}.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"      ✓ Saved visualization")
    
    print(f"\n✅ Generated {len(explanations)} LIME explanations")
    
    return explanations


def create_lime_comparison_plot(explanations, output_dir):
    """
    Create comparison plot of feature importances across examples
    """
    print("\n" + "="*70)
    print("CREATING LIME COMPARISON VISUALIZATION")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "lime_analysis"
    
    # Extract feature importances from each explanation
    all_features = set()
    importance_dict = {}
    
    for exp_data in explanations:
        exp = exp_data['explanation']
        desc = exp_data['description']
        
        # Get feature contributions (for High-DPAD class)
        exp_list = exp.as_list()
        
        importance_dict[desc] = {}
        for feature_desc, weight in exp_list:
            # Extract feature name (before comparison operator)
            feature_name = feature_desc.split('<=')[0].split('>')[0].split('<')[0].split('=')[0].strip()
            all_features.add(feature_name)
            importance_dict[desc][feature_name] = weight
    
    # Create DataFrame
    comparison_df = pd.DataFrame(importance_dict).T
    comparison_df = comparison_df.fillna(0)
    
    # Select top features by absolute importance
    top_features = comparison_df.abs().sum(axis=0).nlargest(15).index
    comparison_df_top = comparison_df[top_features]
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(14, 8))
    
    sns.heatmap(comparison_df_top.T, cmap='RdBu_r', center=0, 
                annot=True, fmt='.3f', cbar_kws={'label': 'LIME Weight'},
                linewidths=0.5, ax=ax)
    
    ax.set_title("LIME Feature Importance Comparison Across Examples\n" +
                 "Red = Pushes toward High-DPAD | Blue = Pushes toward Low-DPAD",
                 fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Example Call", fontsize=11, fontweight='bold')
    ax.set_ylabel("Feature", fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path / "lime_comparison_heatmap.png", dpi=300, bbox_inches='tight')
    print("   ✓ Saved: lime_comparison_heatmap.png")
    plt.close()


def extract_lime_insights(explanations):
    """
    Extract key insights from LIME explanations
    """
    print("\n" + "="*70)
    print("EXTRACTING LIME INSIGHTS")
    print("="*70)
    
    # Aggregate feature importance across all explanations
    all_features = {}
    
    for exp_data in explanations:
        exp = exp_data['explanation']
        exp_list = exp.as_list()
        
        for feature_desc, weight in exp_list:
            # Extract feature name
            feature_name = feature_desc.split('<=')[0].split('>')[0].split('<')[0].split('=')[0].strip()
            
            if feature_name not in all_features:
                all_features[feature_name] = []
            all_features[feature_name].append(weight)
    
    # Calculate statistics
    feature_stats = []
    for feature, weights in all_features.items():
        feature_stats.append({
            'feature': feature,
            'mean_weight': np.mean(weights),
            'abs_mean_weight': np.mean(np.abs(weights)),
            'frequency': len(weights)
        })
    
    feature_stats_df = pd.DataFrame(feature_stats)
    feature_stats_df = feature_stats_df.sort_values('abs_mean_weight', ascending=False)
    
    print(f"\n📊 Top 10 Most Important Features (by mean |LIME weight|):")
    print("-" * 70)
    for idx, row in feature_stats_df.head(10).iterrows():
        print(f"   {row['feature']:.<45} {row['abs_mean_weight']:.4f} "
              f"(appeared in {row['frequency']}/{len(explanations)} examples)")
    
    return feature_stats_df


def generate_lime_report(explanations, feature_stats, output_dir):
    """
    Generate comprehensive LIME analysis report
    """
    print("\n" + "="*70)
    print("GENERATING LIME REPORT")
    print("="*70)
    
    report = []
    report.append("# DPAD Analysis - LIME Interpretability Report")
    report.append("=" * 70)
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append("This report uses LIME (Local Interpretable Model-agnostic Explanations)")
    report.append("to explain individual predictions in a human-readable way.")
    report.append("")
    report.append("LIME creates a simple linear model locally around each prediction")
    report.append("to explain which features pushed that specific call toward High or Low DPAD.")
    report.append("")
    
    # Overall statistics
    report.append("## 1. Analysis Overview")
    report.append("")
    report.append(f"**Calls Explained:** {len(explanations)}")
    report.append(f"**Features Analyzed:** {len(feature_stats)}")
    report.append("")
    
    # Top features
    report.append("## 2. Most Influential Features Across All Examples")
    report.append("")
    report.append("Features ranked by average absolute LIME weight:")
    report.append("")
    report.append("| Rank | Feature | Avg |Weight| | Frequency | Interpretation |")
    report.append("|------|---------|------------|-----------|----------------|")
    
    for idx, row in feature_stats.head(20).iterrows():
        rank = idx + 1 if isinstance(idx, int) else list(feature_stats.index).index(idx) + 1
        report.append(f"| {rank:2d}   | {row['feature']:<35} | {row['abs_mean_weight']:.4f}   | "
                     f"{row['frequency']}/{len(explanations)}      | "
                     f"High impact |")
    report.append("")
    
    # Individual example insights
    report.append("## 3. Individual Call Explanations")
    report.append("")
    
    for exp_data in explanations:
        idx = exp_data['index']
        desc = exp_data['description']
        exp = exp_data['explanation']
        
        report.append(f"### Call #{idx}: {desc}")
        report.append("")
        
        # Get top contributing features
        exp_list = exp.as_list()
        
        report.append("**Top Contributing Features:**")
        report.append("")
        report.append("| Feature Condition | Weight | Direction |")
        report.append("|-------------------|--------|-----------|")
        
        for feature_desc, weight in exp_list[:10]:
            direction = "→ High-DPAD" if weight > 0 else "→ Low-DPAD"
            report.append(f"| {feature_desc:<50} | {weight:>7.3f} | {direction:<15} |")
        
        report.append("")
    
    # Key insights
    report.append("## 4. Key Insights from LIME Analysis")
    report.append("")
    
    # Positive contributors
    positive_features = feature_stats[feature_stats['mean_weight'] > 0].nlargest(5, 'mean_weight')
    if len(positive_features) > 0:
        report.append("### Features that Push Toward High-DPAD")
        report.append("")
        for idx, row in positive_features.iterrows():
            report.append(f"- **{row['feature']}**: Avg weight = {row['mean_weight']:.4f}")
        report.append("")
    
    # Negative contributors
    negative_features = feature_stats[feature_stats['mean_weight'] < 0].nsmallest(5, 'mean_weight')
    if len(negative_features) > 0:
        report.append("### Features that Push Toward Low-DPAD")
        report.append("")
        for idx, row in negative_features.iterrows():
            report.append(f"- **{row['feature']}**: Avg weight = {row['mean_weight']:.4f}")
        report.append("")
    
    # Interpretation guide
    report.append("## 5. How to Interpret LIME Explanations")
    report.append("")
    report.append("**LIME Weight Interpretation:**")
    report.append("- Positive weight: Feature pushes prediction toward High-DPAD")
    report.append("- Negative weight: Feature pushes prediction toward Low-DPAD")
    report.append("- Larger magnitude: Stronger influence")
    report.append("")
    report.append("**Feature Conditions:**")
    report.append("- LIME shows feature values as conditions (e.g., 'x <= 0.5')")
    report.append("- This indicates the feature value range for that prediction")
    report.append("- Multiple features combine linearly to reach final prediction")
    report.append("")
    
    # Save report
    report_path = output_dir / "analysis_outputs" / "lime_analysis" / "lime_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ LIME report saved: {report_path}")


def save_lime_data(feature_stats, explanations, output_dir):
    """Save LIME feature statistics"""
    output_path = output_dir / "analysis_outputs" / "lime_analysis"
    
    # Save feature statistics
    feature_stats.to_csv(output_path / "lime_feature_importance.csv", index=False)
    
    # Save explanation details
    exp_details = []
    for exp_data in explanations:
        idx = exp_data['index']
        desc = exp_data['description']
        exp = exp_data['explanation']
        
        for feature_desc, weight in exp.as_list():
            exp_details.append({
                'call_index': idx,
                'description': desc,
                'feature_condition': feature_desc,
                'weight': weight
            })
    
    exp_df = pd.DataFrame(exp_details)
    exp_df.to_csv(output_path / "lime_explanations_detailed.csv", index=False)
    
    print(f"\n✅ LIME data saved to: {output_path}")


def main():
    """Main LIME analysis pipeline"""
    
    if not LIME_AVAILABLE:
        print("\n" + "="*70)
        print("⚠️  LIME LIBRARY NOT AVAILABLE")
        print("="*70)
        print("\nPlease install LIME to run this analysis:")
        print("  pip install lime")
        print("\nSkipping LIME analysis...")
        return
    
    print("\n" + "="*70)
    print("DPAD ANALYSIS - LIME INTERPRETABILITY")
    print("="*70)
    print("\nExplaining individual predictions with LIME")
    print("="*70)
    
    output_dir = Path("ML_for_DPAD")
    
    # Load data and model
    X, y, model, predictions, feature_metadata = load_data_and_model()
    
    # Create LIME explainer
    class_names = ['Low-DPAD', 'High-DPAD']
    explainer = create_lime_explainer(X, X.columns.tolist(), class_names)
    
    if explainer is None:
        print("\n⚠️  Could not create LIME explainer")
        return
    
    # Select diverse examples
    examples, descriptions = select_diverse_examples(X, y, predictions, n_examples=6)
    
    # Generate LIME explanations
    explanations = generate_lime_explanations(
        explainer, model, X, examples, descriptions, output_dir
    )
    
    # Create comparison plot
    create_lime_comparison_plot(explanations, output_dir)
    
    # Extract insights
    feature_stats = extract_lime_insights(explanations)
    
    # Generate report
    generate_lime_report(explanations, feature_stats, output_dir)
    
    # Save data
    save_lime_data(feature_stats, explanations, output_dir)
    
    print("\n" + "="*70)
    print("✅ LIME ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nTop 5 Most Important Features (by avg |LIME weight|):")
    for idx, row in feature_stats.head(5).iterrows():
        print(f"   {row['feature']:.<50} {row['abs_mean_weight']:.4f}")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

