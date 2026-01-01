"""
DPAD Analysis - Step 2: Correlation Analysis
============================================

Purpose:
--------
Identify which call variables have the strongest correlation with High-DPAD 
agent performance.

What This Script Does:
----------------------
1. Loads preprocessed data from Step 1
2. Calculates correlation between each feature and the high_dpad target
3. Identifies top positive correlations (features high in successful agents)
4. Identifies top negative correlations (features low in successful agents)
5. Creates visualizations:
   - Correlation heatmap
   - Top 20 positive correlations
   - Top 20 negative correlations
6. Generates detailed correlation report

Key Questions Answered:
-----------------------
- Which variables are HIGHER in high-DPAD agents?
- Which variables are LOWER in high-DPAD agents?
- What are the strongest predictors of success?

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

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

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
    print(f"   Feature types: {len(feature_metadata['numerical_features'])} numerical, "
          f"{len(feature_metadata['categorical_features'])} categorical, "
          f"{len(feature_metadata['boolean_features'])} boolean")
    
    return X, y.values.ravel(), feature_metadata


def calculate_correlations(X, y):
    """
    Calculate Pearson correlation between each feature and target
    
    Note: For categorical/boolean variables, this represents the strength
    of linear relationship. For more nuanced categorical analysis, see Step 4.
    """
    print("\n" + "="*70)
    print("CALCULATING CORRELATIONS")
    print("="*70)
    
    correlations = {}
    
    for col in X.columns:
        try:
            # Calculate Pearson correlation
            corr = np.corrcoef(X[col].values, y)[0, 1]
            correlations[col] = corr
        except:
            # Skip if calculation fails (e.g., constant column)
            correlations[col] = 0.0
    
    # Convert to DataFrame and sort
    corr_df = pd.DataFrame({
        'feature': list(correlations.keys()),
        'correlation': list(correlations.values())
    })
    
    corr_df = corr_df.sort_values('correlation', ascending=False)
    
    print(f"\n✅ Calculated correlations for {len(correlations)} features")
    print(f"   Correlation range: [{corr_df['correlation'].min():.3f}, {corr_df['correlation'].max():.3f}]")
    
    return corr_df


def identify_top_correlations(corr_df, n=20):
    """
    Identify top positive and negative correlations
    
    Positive correlation: Feature is HIGHER in high-DPAD agents
    Negative correlation: Feature is LOWER in high-DPAD agents (or HIGHER in low-DPAD)
    """
    print("\n" + "="*70)
    print("TOP CORRELATIONS WITH HIGH-DPAD PERFORMANCE")
    print("="*70)
    
    # Top positive correlations
    top_positive = corr_df.nlargest(n, 'correlation')
    
    print(f"\n📈 TOP {n} POSITIVE CORRELATIONS")
    print("   (Features HIGHER in High-DPAD agents)")
    print("-" * 70)
    for idx, row in top_positive.iterrows():
        print(f"   {row['feature']:.<50} {row['correlation']:>6.3f}")
    
    # Top negative correlations
    top_negative = corr_df.nsmallest(n, 'correlation')
    
    print(f"\n📉 TOP {n} NEGATIVE CORRELATIONS")
    print("   (Features LOWER in High-DPAD agents)")
    print("-" * 70)
    for idx, row in top_negative.iterrows():
        print(f"   {row['feature']:.<50} {row['correlation']:>6.3f}")
    
    return top_positive, top_negative


def create_correlation_heatmap(X, y, output_dir):
    """
    Create heatmap of feature correlations with target
    Shows top 30 features by absolute correlation
    """
    print("\n" + "="*70)
    print("CREATING CORRELATION HEATMAP")
    print("="*70)
    
    # Calculate correlations
    correlations = {}
    for col in X.columns:
        try:
            corr = np.corrcoef(X[col].values, y)[0, 1]
            correlations[col] = corr
        except:
            correlations[col] = 0.0
    
    # Get top 30 by absolute correlation
    corr_series = pd.Series(correlations).sort_values(key=abs, ascending=False)[:30]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Create heatmap data
    heatmap_data = corr_series.values.reshape(-1, 1)
    
    # Plot heatmap
    im = ax.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
    
    # Set ticks
    ax.set_yticks(range(len(corr_series)))
    ax.set_yticklabels(corr_series.index, fontsize=9)
    ax.set_xticks([0])
    ax.set_xticklabels(['Correlation with\nHigh-DPAD'])
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20)
    
    # Add correlation values as text
    for i, (feat, corr) in enumerate(corr_series.items()):
        color = 'white' if abs(corr) > 0.5 else 'black'
        ax.text(0, i, f'{corr:.3f}', ha='center', va='center', 
                color=color, fontsize=9, fontweight='bold')
    
    plt.title('Top 30 Features by Correlation with High-DPAD Performance\n' +
              'Green = Higher in successful agents | Red = Lower in successful agents',
              fontsize=12, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    # Save
    output_path = output_dir / "analysis_outputs" / "correlations"
    output_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path / "correlation_heatmap.png", dpi=300, bbox_inches='tight')
    print(f"✅ Saved: correlation_heatmap.png")
    
    plt.close()


def plot_top_correlations(top_positive, top_negative, output_dir, n=20):
    """
    Create bar plots for top positive and negative correlations
    """
    print("\n" + "="*70)
    print("CREATING CORRELATION BAR PLOTS")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "correlations"
    
    # Plot 1: Top Positive Correlations
    fig, ax = plt.subplots(figsize=(12, 10))
    
    colors = plt.cm.Greens(np.linspace(0.4, 0.9, len(top_positive)))
    bars = ax.barh(range(len(top_positive)), top_positive['correlation'].values, color=colors)
    
    ax.set_yticks(range(len(top_positive)))
    ax.set_yticklabels(top_positive['feature'].values, fontsize=10)
    ax.set_xlabel('Correlation with High-DPAD Performance', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {n} Features HIGHER in High-DPAD Agents\n' +
                 '(Positive Correlations = Success Indicators)',
                 fontsize=13, fontweight='bold', pad=15)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, top_positive['correlation'].values)):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{val:.3f}', va='center', fontsize=9)
    
    ax.grid(axis='x', alpha=0.3)
    ax.set_xlim(0, max(top_positive['correlation'].max() * 1.15, 0.1))
    
    plt.tight_layout()
    plt.savefig(output_path / "top_positive_correlations.png", dpi=300, bbox_inches='tight')
    print(f"✅ Saved: top_positive_correlations.png")
    plt.close()
    
    # Plot 2: Top Negative Correlations
    fig, ax = plt.subplots(figsize=(12, 10))
    
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(top_negative)))
    bars = ax.barh(range(len(top_negative)), top_negative['correlation'].values, color=colors)
    
    ax.set_yticks(range(len(top_negative)))
    ax.set_yticklabels(top_negative['feature'].values, fontsize=10)
    ax.set_xlabel('Correlation with High-DPAD Performance', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {n} Features LOWER in High-DPAD Agents\n' +
                 '(Negative Correlations = Warning Signs)',
                 fontsize=13, fontweight='bold', pad=15)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, top_negative['correlation'].values)):
        ax.text(val - 0.01, bar.get_y() + bar.get_height()/2, 
                f'{val:.3f}', va='center', ha='right', fontsize=9)
    
    ax.grid(axis='x', alpha=0.3)
    ax.set_xlim(min(top_negative['correlation'].min() * 1.15, -0.1), 0)
    
    plt.tight_layout()
    plt.savefig(output_path / "top_negative_correlations.png", dpi=300, bbox_inches='tight')
    print(f"✅ Saved: top_negative_correlations.png")
    plt.close()


def categorize_features(corr_df, feature_metadata):
    """
    Categorize features by type for more interpretable analysis
    """
    
    # Define feature categories based on domain knowledge
    categories = {
        'Discovery & Qualification': [
            'total_discovery_questions', 'goal1_questions', 'goal2_questions', 
            'goal3_questions', 'discovery_quality', 'advanced_discovery_used',
            'business_type_mentioned', 'location_mentioned', 'is_decision_maker',
            'ready_for_customers'
        ],
        'Objection Handling': [
            'total_objections', 'objections_acknowledged', 'objections_rebutted',
            'acknowledgement_rate', 'total_resistance_signals'
        ],
        'Sentiment & Rapport': [
            'customer_sentiment_lgs', 'customer_sentiment_omc', 
            'lgs_sentiment_style', 'omc_agent_sentiment_style',
            'sentiment_progression', 'sentiment_opening', 'sentiment_early_middle',
            'sentiment_late_middle', 'sentiment_closing', 'notable_sentiment_shifts',
            'rapport_elements_count', 'name_usage_count', 'personal_greeting',
            'common_ground_established', 'empathy_responses', 'empathy_response_rate'
        ],
        'Talk Dynamics': [
            'customer_talk_percentage', 'agent_talk_percentage', 'talk_ratio_classification',
            'average_monologue_length', 'longest_monologue_length', 
            'extended_monologues_count', 'short_monologues', 'medium_monologues',
            'long_monologues', 'very_long_monologues', 'total_interruptions',
            'interruption_rate', 'interruption_pattern', 'conversation_balance'
        ],
        'Call Structure & Timing': [
            'TO_OMC_Duration', 'total_call_duration', 'time_to_reason_seconds',
            'within_45_seconds', 'call_structure_framed', 'call_structure_clarity',
            'script_adherence', 'stages_skipped', 'stages_out_of_order',
            'time_in_final_stage'
        ],
        'Closing & Commitment': [
            'assumptive_language_used', 'roi_calculation_presented',
            'price_mentions_final_2min', 'timeline_mentions_final_2min',
            'contract_mentions_final_2min', 'price_timeline_contract_before_dropoff',
            'commitment_type', 'commitment_clarity', 'premature_closing_attempt',
            'full_sale_closed', 'payment_info_collected', 'followup_scheduled'
        ],
        'Call Outcome': [
            'disconnect_stage', 'hang_up_initiated_by', 'call_result_tag',
            'primary_disconnect_reason', 'customer_frustrations'
        ],
        'Buying Signals': [
            'total_buying_signals', 'signal_ratio'
        ],
        'LGS Lead Quality': [
            'Calls Count', 'Connection Made Calls', 'Dial Attempt Calls',
            'customer_availability', 'customer_knows_marketing', 
            'customer_marketing_experience', 'ready_to_transfer'
        ],
        'Context': [
            'timezone', 'season_status', 'season_month'
        ]
    }
    
    # Categorize each feature
    categorized_corr = {}
    
    for category, features in categories.items():
        cat_features = [f for f in features if f in corr_df['feature'].values]
        if cat_features:
            cat_df = corr_df[corr_df['feature'].isin(cat_features)].copy()
            cat_df = cat_df.sort_values('correlation', ascending=False)
            categorized_corr[category] = cat_df
    
    return categorized_corr


def generate_correlation_report(corr_df, top_positive, top_negative, 
                                 categorized_corr, output_dir):
    """
    Generate comprehensive correlation analysis report
    """
    print("\n" + "="*70)
    print("GENERATING CORRELATION REPORT")
    print("="*70)
    
    report = []
    report.append("# DPAD Analysis - Correlation Report")
    report.append("=" * 70)
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append("This report identifies which call variables have the strongest")
    report.append("correlation with High-DPAD (>1 deal/agent/day) performance.")
    report.append("")
    report.append("**Key Findings:**")
    report.append("")
    
    # Overall statistics
    strong_positive = len(corr_df[corr_df['correlation'] > 0.3])
    strong_negative = len(corr_df[corr_df['correlation'] < -0.3])
    
    report.append(f"- **Features analyzed:** {len(corr_df)}")
    report.append(f"- **Strong positive correlations (>0.3):** {strong_positive}")
    report.append(f"- **Strong negative correlations (<-0.3):** {strong_negative}")
    report.append(f"- **Strongest positive correlation:** {top_positive.iloc[0]['correlation']:.3f}")
    report.append(f"- **Strongest negative correlation:** {top_negative.iloc[0]['correlation']:.3f}")
    report.append("")
    
    # Top Positive Correlations
    report.append("## 1. Top Positive Correlations")
    report.append("*Features HIGHER in High-DPAD agents (Success Indicators)*")
    report.append("")
    report.append("| Rank | Feature | Correlation |")
    report.append("|------|---------|-------------|")
    for idx, (i, row) in enumerate(top_positive.iterrows(), 1):
        report.append(f"| {idx:2d}   | {row['feature']:<45} | {row['correlation']:>6.3f}      |")
    report.append("")
    
    # Top Negative Correlations
    report.append("## 2. Top Negative Correlations")
    report.append("*Features LOWER in High-DPAD agents (Warning Signs)*")
    report.append("")
    report.append("| Rank | Feature | Correlation |")
    report.append("|------|---------|-------------|")
    for idx, (i, row) in enumerate(top_negative.iterrows(), 1):
        report.append(f"| {idx:2d}   | {row['feature']:<45} | {row['correlation']:>6.3f}      |")
    report.append("")
    
    # Categorized Analysis
    report.append("## 3. Correlation Analysis by Category")
    report.append("")
    
    for category, cat_df in categorized_corr.items():
        report.append(f"### {category}")
        report.append("")
        
        if len(cat_df) > 0:
            report.append("| Feature | Correlation | Interpretation |")
            report.append("|---------|-------------|----------------|")
            
            for idx, row in cat_df.iterrows():
                corr = row['correlation']
                if corr > 0.2:
                    interp = "✓ Higher in successful agents"
                elif corr < -0.2:
                    interp = "✗ Lower in successful agents"
                else:
                    interp = "~ Weak relationship"
                
                report.append(f"| {row['feature']:<35} | {corr:>6.3f}      | {interp:<30} |")
        else:
            report.append("*No features in this category*")
        
        report.append("")
    
    # Key Insights
    report.append("## 4. Key Insights")
    report.append("")
    
    # Analyze discovery questions
    discovery_corr = corr_df[corr_df['feature'].str.contains('discovery|goal', case=False, na=False)]
    if len(discovery_corr) > 0:
        avg_discovery_corr = discovery_corr['correlation'].mean()
        report.append(f"**Discovery Questions:**")
        report.append(f"- Average correlation: {avg_discovery_corr:.3f}")
        if avg_discovery_corr > 0.1:
            report.append("- ✓ More discovery questions correlate with higher DPAD")
        else:
            report.append("- ✗ Discovery questions show weak relationship with DPAD")
        report.append("")
    
    # Analyze objection handling
    objection_corr = corr_df[corr_df['feature'].str.contains('objection', case=False, na=False)]
    if len(objection_corr) > 0:
        avg_objection_corr = objection_corr['correlation'].mean()
        report.append(f"**Objection Handling:**")
        report.append(f"- Average correlation: {avg_objection_corr:.3f}")
        if avg_objection_corr > 0.1:
            report.append("- ✓ Better objection handling correlates with higher DPAD")
        else:
            report.append("- ✗ Objection handling shows weak relationship with DPAD")
        report.append("")
    
    # Analyze sentiment
    sentiment_corr = corr_df[corr_df['feature'].str.contains('sentiment', case=False, na=False)]
    if len(sentiment_corr) > 0:
        avg_sentiment_corr = sentiment_corr['correlation'].mean()
        report.append(f"**Sentiment Management:**")
        report.append(f"- Average correlation: {avg_sentiment_corr:.3f}")
        if avg_sentiment_corr > 0.1:
            report.append("- ✓ Positive sentiment correlates with higher DPAD")
        else:
            report.append("- ✗ Sentiment shows weak relationship with DPAD")
        report.append("")
    
    # Analyze talk ratio
    talk_corr = corr_df[corr_df['feature'].str.contains('talk|monologue', case=False, na=False)]
    if len(talk_corr) > 0:
        avg_talk_corr = talk_corr['correlation'].mean()
        report.append(f"**Talk Dynamics:**")
        report.append(f"- Average correlation: {avg_talk_corr:.3f}")
        if avg_talk_corr > 0.1:
            report.append("- ✓ Talk ratio patterns correlate with higher DPAD")
        else:
            report.append("- ✗ Talk dynamics show weak relationship with DPAD")
        report.append("")
    
    # Save report
    report_path = output_dir / "analysis_outputs" / "correlations" / "correlation_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Correlation report saved: {report_path}")
    
    # Print summary to console
    print("\n" + "="*70)
    print("CORRELATION ANALYSIS SUMMARY")
    print("="*70)
    print(f"\nTop 5 Success Indicators (Positive Correlations):")
    for idx, row in top_positive.head(5).iterrows():
        print(f"  {row['feature']:.<50} {row['correlation']:>6.3f}")
    
    print(f"\nTop 5 Warning Signs (Negative Correlations):")
    for idx, row in top_negative.head(5).iterrows():
        print(f"  {row['feature']:.<50} {row['correlation']:>6.3f}")


def save_correlation_data(corr_df, output_dir):
    """Save correlation data for downstream analysis"""
    output_path = output_dir / "analysis_outputs" / "correlations"
    
    corr_df.to_csv(output_path / "all_correlations.csv", index=False)
    print(f"\n✅ Saved correlation data: all_correlations.csv")


def main():
    """Main correlation analysis pipeline"""
    
    print("\n" + "="*70)
    print("DPAD ANALYSIS - CORRELATION ANALYSIS")
    print("="*70)
    print("\nIdentifying features that differentiate High-DPAD vs Low-DPAD agents")
    print("="*70)
    
    output_dir = Path("ML_for_DPAD")
    
    # Load preprocessed data
    X, y, feature_metadata = load_preprocessed_data()
    
    # Calculate correlations
    corr_df = calculate_correlations(X, y)
    
    # Identify top correlations
    top_positive, top_negative = identify_top_correlations(corr_df, n=20)
    
    # Categorize features
    categorized_corr = categorize_features(corr_df, feature_metadata)
    
    # Create visualizations
    create_correlation_heatmap(X, y, output_dir)
    plot_top_correlations(top_positive, top_negative, output_dir, n=20)
    
    # Generate report
    generate_correlation_report(corr_df, top_positive, top_negative, 
                                 categorized_corr, output_dir)
    
    # Save correlation data
    save_correlation_data(corr_df, output_dir)
    
    print("\n" + "="*70)
    print("✅ CORRELATION ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutputs saved to: {output_dir / 'analysis_outputs' / 'correlations'}")
    print("  - correlation_heatmap.png")
    print("  - top_positive_correlations.png")
    print("  - top_negative_correlations.png")
    print("  - correlation_report.txt")
    print("  - all_correlations.csv")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

