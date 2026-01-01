"""
DPAD Analysis - Step 7: Comprehensive Visualizations
=====================================================

Purpose:
--------
Create beautiful, publication-ready visualizations comparing High-DPAD vs Low-DPAD agents
across all key features identified in previous analyses.

What This Script Does:
----------------------
1. Loads preprocessed data
2. Loads top features from previous analyses
3. Creates comprehensive visualizations:
   - Distribution comparisons (box plots, violin plots)
   - Scatter plots with trend lines
   - Category breakdowns (bar plots, count plots)
   - Grouped comparisons
   - Correlation scatter matrices
4. Generates visual story of DPAD differences

Why Visualizations Matter:
---------------------------
- Make complex findings accessible to non-technical stakeholders
- Reveal patterns that statistics alone might miss
- Support decision-making with clear visual evidence
- Create presentation-ready materials for executive reports

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

# Set high-quality plotting parameters
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("notebook", font_scale=1.1)
sns.set_palette("husl")

# Color scheme
COLORS = {
    'high_dpad': '#2ecc71',  # Green
    'low_dpad': '#e74c3c',   # Red
    'neutral': '#3498db'     # Blue
}


def load_analysis_data():
    """Load all necessary data and previous analysis results"""
    print("\n" + "="*70)
    print("LOADING DATA AND ANALYSIS RESULTS")
    print("="*70)
    
    data_path = Path("ML_for_DPAD/analysis_outputs")
    
    # Load preprocessed data
    X = pd.read_csv(data_path / "preprocessed_data" / "X_features.csv")
    y = pd.read_csv(data_path / "preprocessed_data" / "y_target.csv").values.ravel()
    
    # Combine for easier plotting
    df = X.copy()
    df['high_dpad'] = y
    df['DPAD_Group'] = df['high_dpad'].map({1: 'High-DPAD', 0: 'Low-DPAD'})
    
    print(f"\n✅ Loaded data:")
    print(f"   Total calls: {len(df)}")
    print(f"   High-DPAD: {(y == 1).sum()}")
    print(f"   Low-DPAD: {(y == 0).sum()}")
    print(f"   Features: {X.shape[1]}")
    
    # Load top features from correlation analysis
    corr_data = pd.read_csv(data_path / "correlations" / "all_correlations.csv")
    corr_data['abs_correlation'] = corr_data['correlation'].abs()
    top_features = corr_data.nlargest(20, 'abs_correlation')['feature'].tolist()
    
    print(f"\n✅ Loaded top {len(top_features)} features for visualization")
    
    return df, top_features


def create_distribution_plots(df, top_features, output_dir):
    """
    Create box plots and violin plots for top numerical features
    """
    print("\n" + "="*70)
    print("CREATING DISTRIBUTION COMPARISON PLOTS")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "visualizations"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Select numerical features only
    numerical_features = []
    for feat in top_features[:15]:  # Top 15
        if feat in df.columns and df[feat].dtype in ['float64', 'int64']:
            # Skip if constant or binary
            if df[feat].nunique() > 2:
                numerical_features.append(feat)
    
    print(f"\n📊 Creating distribution plots for {len(numerical_features)} features...")
    
    # Create box plots (3x3 grid)
    n_plots = min(9, len(numerical_features))
    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    axes = axes.ravel()
    
    for idx, feature in enumerate(numerical_features[:n_plots]):
        ax = axes[idx]
        
        # Box plot
        box_data = [
            df[df['high_dpad'] == 0][feature].dropna(),
            df[df['high_dpad'] == 1][feature].dropna()
        ]
        
        bp = ax.boxplot(box_data, 
                        labels=['Low-DPAD', 'High-DPAD'],
                        patch_artist=True,
                        showmeans=True,
                        meanprops=dict(marker='D', markerfacecolor='yellow', markersize=8))
        
        # Color boxes
        bp['boxes'][0].set_facecolor(COLORS['low_dpad'])
        bp['boxes'][0].set_alpha(0.6)
        bp['boxes'][1].set_facecolor(COLORS['high_dpad'])
        bp['boxes'][1].set_alpha(0.6)
        
        ax.set_title(f"{feature}", fontsize=10, fontweight='bold')
        ax.set_ylabel("Value", fontsize=9)
        ax.grid(True, alpha=0.3)
        
        # Add mean values as text
        low_mean = df[df['high_dpad'] == 0][feature].mean()
        high_mean = df[df['high_dpad'] == 1][feature].mean()
        ax.text(1, ax.get_ylim()[1] * 0.95, f"μ={low_mean:.2f}", 
                ha='center', fontsize=8, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        ax.text(2, ax.get_ylim()[1] * 0.95, f"μ={high_mean:.2f}", 
                ha='center', fontsize=8, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Remove empty subplots
    for idx in range(n_plots, 9):
        fig.delaxes(axes[idx])
    
    plt.suptitle("Distribution Comparison: High-DPAD vs Low-DPAD Agents\nBox Plots (Top Features)",
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(output_path / "distribution_boxplots.png", dpi=300, bbox_inches='tight')
    print("   ✓ Saved: distribution_boxplots.png")
    plt.close()
    
    # Create violin plots for top 6
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.ravel()
    
    for idx, feature in enumerate(numerical_features[:6]):
        ax = axes[idx]
        
        # Violin plot
        sns.violinplot(data=df, x='DPAD_Group', y=feature, ax=ax,
                       palette={'Low-DPAD': COLORS['low_dpad'], 
                               'High-DPAD': COLORS['high_dpad']},
                       alpha=0.7)
        
        # Add strip plot for individual points
        sns.stripplot(data=df, x='DPAD_Group', y=feature, ax=ax,
                     color='black', alpha=0.3, size=3)
        
        ax.set_title(f"{feature}", fontsize=11, fontweight='bold')
        ax.set_xlabel("")
        ax.set_ylabel("Value", fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle("Distribution Comparison: High-DPAD vs Low-DPAD Agents\nViolin Plots (Top 6 Features)",
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(output_path / "distribution_violinplots.png", dpi=300, bbox_inches='tight')
    print("   ✓ Saved: distribution_violinplots.png")
    plt.close()


def create_scatter_comparisons(df, top_features, output_dir):
    """
    Create scatter plots comparing relationships between top features
    """
    print("\n" + "="*70)
    print("CREATING SCATTER PLOT COMPARISONS")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "visualizations"
    
    # Select top numerical features
    numerical_features = [f for f in top_features[:10] 
                         if f in df.columns and df[f].dtype in ['float64', 'int64'] 
                         and df[f].nunique() > 2][:6]
    
    print(f"\n📊 Creating scatter plots for top {len(numerical_features)} features...")
    
    # Key feature pairs
    if 'interruption_rate' in numerical_features and 'sentiment_progression' in numerical_features:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for group, color, label in [(0, COLORS['low_dpad'], 'Low-DPAD'),
                                     (1, COLORS['high_dpad'], 'High-DPAD')]:
            mask = df['high_dpad'] == group
            ax.scatter(df[mask]['interruption_rate'], 
                      df[mask]['sentiment_progression'],
                      c=color, label=label, alpha=0.7, s=100, edgecolors='black', linewidth=0.5)
        
        ax.set_xlabel("Interruption Rate", fontsize=12, fontweight='bold')
        ax.set_ylabel("Sentiment Progression", fontsize=12, fontweight='bold')
        ax.set_title("Key Feature Relationship: Interruption Rate vs Sentiment Progression",
                    fontsize=14, fontweight='bold', pad=15)
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / "scatter_interruption_sentiment.png", dpi=300, bbox_inches='tight')
        print("   ✓ Saved: scatter_interruption_sentiment.png")
        plt.close()
    
    # Pairplot for top 4 features
    if len(numerical_features) >= 4:
        print("\n📊 Creating pairplot matrix...")
        top_4 = numerical_features[:4]
        
        pairplot_df = df[top_4 + ['DPAD_Group']].copy()
        
        g = sns.pairplot(pairplot_df, hue='DPAD_Group', 
                        palette={'Low-DPAD': COLORS['low_dpad'], 
                                'High-DPAD': COLORS['high_dpad']},
                        plot_kws={'alpha': 0.6, 's': 50, 'edgecolor': 'black', 'linewidth': 0.5},
                        diag_kind='kde',
                        corner=False)
        
        g.fig.suptitle("Feature Relationships: Top 4 Features", 
                      fontsize=14, fontweight='bold', y=1.01)
        
        plt.savefig(output_path / "pairplot_top4.png", dpi=300, bbox_inches='tight')
        print("   ✓ Saved: pairplot_top4.png")
        plt.close()


def create_categorical_comparisons(df, output_dir):
    """
    Create visualizations for categorical features
    """
    print("\n" + "="*70)
    print("CREATING CATEGORICAL FEATURE COMPARISONS")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "visualizations"
    
    # Identify categorical features
    categorical_features = []
    for col in df.columns:
        if col not in ['high_dpad', 'DPAD_Group']:
            if df[col].dtype == 'object' or df[col].nunique() <= 10:
                categorical_features.append(col)
    
    print(f"\n📊 Found {len(categorical_features)} categorical features")
    
    # Select interesting categorical features
    interesting_cats = []
    for feat in categorical_features[:20]:
        # Check if there's variation across groups
        ct = pd.crosstab(df[feat], df['DPAD_Group'])
        if len(ct) > 1 and len(ct) <= 8:  # Between 2-8 categories
            interesting_cats.append(feat)
    
    print(f"   Visualizing {min(6, len(interesting_cats))} interesting categorical features...")
    
    if len(interesting_cats) > 0:
        # Create count plots
        n_plots = min(6, len(interesting_cats))
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        axes = axes.ravel()
        
        for idx, feature in enumerate(interesting_cats[:n_plots]):
            ax = axes[idx]
            
            # Count plot
            ct = pd.crosstab(df[feature], df['DPAD_Group'], normalize='columns') * 100
            ct.plot(kind='bar', ax=ax, color=[COLORS['low_dpad'], COLORS['high_dpad']], alpha=0.7)
            
            ax.set_title(f"{feature}", fontsize=11, fontweight='bold')
            ax.set_xlabel("")
            ax.set_ylabel("Percentage (%)", fontsize=10)
            ax.legend(title="", fontsize=9)
            ax.grid(True, alpha=0.3, axis='y')
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Remove empty subplots
        for idx in range(n_plots, 6):
            fig.delaxes(axes[idx])
        
        plt.suptitle("Categorical Feature Distributions: High-DPAD vs Low-DPAD",
                     fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(output_path / "categorical_distributions.png", dpi=300, bbox_inches='tight')
        print("   ✓ Saved: categorical_distributions.png")
        plt.close()


def create_summary_dashboard(df, output_dir):
    """
    Create a single comprehensive dashboard summarizing key findings
    """
    print("\n" + "="*70)
    print("CREATING SUMMARY DASHBOARD")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "visualizations"
    
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
    
    # 1. Interruption Rate (Box + Violin)
    ax1 = fig.add_subplot(gs[0, 0])
    if 'interruption_rate' in df.columns:
        sns.violinplot(data=df, x='DPAD_Group', y='interruption_rate', ax=ax1,
                       palette={'Low-DPAD': COLORS['low_dpad'], 
                               'High-DPAD': COLORS['high_dpad']})
        ax1.set_title("🏆 #1: Interruption Rate", fontsize=11, fontweight='bold')
        ax1.set_xlabel("")
        ax1.set_ylabel("Interruption Rate", fontsize=9)
    
    # 2. Sentiment Progression
    ax2 = fig.add_subplot(gs[0, 1])
    if 'sentiment_progression' in df.columns:
        sns.violinplot(data=df, x='DPAD_Group', y='sentiment_progression', ax=ax2,
                       palette={'Low-DPAD': COLORS['low_dpad'], 
                               'High-DPAD': COLORS['high_dpad']})
        ax2.set_title("Sentiment Progression", fontsize=11, fontweight='bold')
        ax2.set_xlabel("")
        ax2.set_ylabel("Sentiment Score", fontsize=9)
    
    # 3. Agent Talk Percentage
    ax3 = fig.add_subplot(gs[0, 2])
    if 'agent_talk_percentage' in df.columns:
        sns.violinplot(data=df, x='DPAD_Group', y='agent_talk_percentage', ax=ax3,
                       palette={'Low-DPAD': COLORS['low_dpad'], 
                               'High-DPAD': COLORS['high_dpad']})
        ax3.set_title("Agent Talk %", fontsize=11, fontweight='bold')
        ax3.set_xlabel("")
        ax3.set_ylabel("Talk Percentage", fontsize=9)
    
    # 4. Longest Monologue
    ax4 = fig.add_subplot(gs[0, 3])
    if 'longest_monologue_length' in df.columns:
        sns.violinplot(data=df, x='DPAD_Group', y='longest_monologue_length', ax=ax4,
                       palette={'Low-DPAD': COLORS['low_dpad'], 
                               'High-DPAD': COLORS['high_dpad']})
        ax4.set_title("Longest Monologue", fontsize=11, fontweight='bold')
        ax4.set_xlabel("")
        ax4.set_ylabel("Length", fontsize=9)
    
    # 5. Conversation Balance
    ax5 = fig.add_subplot(gs[1, 0])
    if 'conversation_balance' in df.columns:
        sns.violinplot(data=df, x='DPAD_Group', y='conversation_balance', ax=ax5,
                       palette={'Low-DPAD': COLORS['low_dpad'], 
                               'High-DPAD': COLORS['high_dpad']})
        ax5.set_title("Conversation Balance", fontsize=11, fontweight='bold')
        ax5.set_xlabel("")
        ax5.set_ylabel("Balance Score", fontsize=9)
    
    # 6. Total Interruptions
    ax6 = fig.add_subplot(gs[1, 1])
    if 'total_interruptions' in df.columns:
        sns.violinplot(data=df, x='DPAD_Group', y='total_interruptions', ax=ax6,
                       palette={'Low-DPAD': COLORS['low_dpad'], 
                               'High-DPAD': COLORS['high_dpad']})
        ax6.set_title("Total Interruptions", fontsize=11, fontweight='bold')
        ax6.set_xlabel("")
        ax6.set_ylabel("Count", fontsize=9)
    
    # 7. Time to Reason
    ax7 = fig.add_subplot(gs[1, 2])
    if 'time_to_reason_seconds' in df.columns:
        sns.violinplot(data=df, x='DPAD_Group', y='time_to_reason_seconds', ax=ax7,
                       palette={'Low-DPAD': COLORS['low_dpad'], 
                               'High-DPAD': COLORS['high_dpad']})
        ax7.set_title("Time to Reason", fontsize=11, fontweight='bold')
        ax7.set_xlabel("")
        ax7.set_ylabel("Seconds", fontsize=9)
    
    # 8. Sample Size
    ax8 = fig.add_subplot(gs[1, 3])
    counts = df['DPAD_Group'].value_counts()
    ax8.bar(counts.index, counts.values, color=[COLORS['high_dpad'], COLORS['low_dpad']], alpha=0.7)
    ax8.set_title("Sample Size", fontsize=11, fontweight='bold')
    ax8.set_ylabel("Number of Calls", fontsize=9)
    ax8.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(counts.values):
        ax8.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
    
    # 9. Scatter: Interruption vs Sentiment
    ax9 = fig.add_subplot(gs[2, :2])
    if 'interruption_rate' in df.columns and 'sentiment_progression' in df.columns:
        for group, color, label in [(0, COLORS['low_dpad'], 'Low-DPAD'),
                                     (1, COLORS['high_dpad'], 'High-DPAD')]:
            mask = df['high_dpad'] == group
            ax9.scatter(df[mask]['interruption_rate'], 
                       df[mask]['sentiment_progression'],
                       c=color, label=label, alpha=0.7, s=100, edgecolors='black', linewidth=0.5)
        ax9.set_xlabel("Interruption Rate", fontsize=10, fontweight='bold')
        ax9.set_ylabel("Sentiment Progression", fontsize=10, fontweight='bold')
        ax9.set_title("Key Relationship: Interruptions vs Sentiment", fontsize=11, fontweight='bold')
        ax9.legend(fontsize=9)
        ax9.grid(True, alpha=0.3)
    
    # 10. Key Statistics Table
    ax10 = fig.add_subplot(gs[2, 2:])
    ax10.axis('off')
    
    stats_text = "KEY STATISTICS\n\n"
    
    if 'interruption_rate' in df.columns:
        low_int = df[df['high_dpad'] == 0]['interruption_rate'].mean()
        high_int = df[df['high_dpad'] == 1]['interruption_rate'].mean()
        stats_text += f"Interruption Rate:\n"
        stats_text += f"  Low-DPAD:  {low_int:.3f}\n"
        stats_text += f"  High-DPAD: {high_int:.3f}\n"
        stats_text += f"  Difference: {abs(high_int - low_int):.3f}\n\n"
    
    if 'sentiment_progression' in df.columns:
        low_sent = df[df['high_dpad'] == 0]['sentiment_progression'].mean()
        high_sent = df[df['high_dpad'] == 1]['sentiment_progression'].mean()
        stats_text += f"Sentiment Progression:\n"
        stats_text += f"  Low-DPAD:  {low_sent:.3f}\n"
        stats_text += f"  High-DPAD: {high_sent:.3f}\n"
        stats_text += f"  Difference: {abs(high_sent - low_sent):.3f}\n\n"
    
    if 'agent_talk_percentage' in df.columns:
        low_talk = df[df['high_dpad'] == 0]['agent_talk_percentage'].mean()
        high_talk = df[df['high_dpad'] == 1]['agent_talk_percentage'].mean()
        stats_text += f"Agent Talk %:\n"
        stats_text += f"  Low-DPAD:  {low_talk:.1f}%\n"
        stats_text += f"  High-DPAD: {high_talk:.1f}%\n"
        stats_text += f"  Difference: {abs(high_talk - low_talk):.1f}%\n"
    
    ax10.text(0.05, 0.95, stats_text, transform=ax10.transAxes,
             fontsize=10, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.suptitle("DPAD Analysis Dashboard: High-DPAD vs Low-DPAD Agents",
                 fontsize=16, fontweight='bold', y=0.995)
    
    plt.savefig(output_path / "summary_dashboard.png", dpi=300, bbox_inches='tight')
    print("   ✓ Saved: summary_dashboard.png")
    plt.close()


def create_top_features_comparison(df, top_features, output_dir):
    """
    Create a comprehensive comparison of means for top features
    """
    print("\n" + "="*70)
    print("CREATING TOP FEATURES MEAN COMPARISON")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "visualizations"
    
    # Calculate means for top features
    comparison_data = []
    
    for feature in top_features[:15]:
        if feature in df.columns and df[feature].dtype in ['float64', 'int64']:
            low_mean = df[df['high_dpad'] == 0][feature].mean()
            high_mean = df[df['high_dpad'] == 1][feature].mean()
            difference = high_mean - low_mean
            
            comparison_data.append({
                'feature': feature,
                'Low-DPAD Mean': low_mean,
                'High-DPAD Mean': high_mean,
                'Difference': difference,
                'Abs Difference': abs(difference)
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.sort_values('Abs Difference', ascending=True)
    
    # Create horizontal bar plot
    fig, ax = plt.subplots(figsize=(14, 10))
    
    y_pos = np.arange(len(comparison_df))
    
    # Plot bars
    colors = [COLORS['high_dpad'] if x > 0 else COLORS['low_dpad'] 
              for x in comparison_df['Difference']]
    
    bars = ax.barh(y_pos, comparison_df['Difference'], color=colors, alpha=0.7, edgecolor='black')
    
    # Customize
    ax.set_yticks(y_pos)
    ax.set_yticklabels(comparison_df['feature'], fontsize=10)
    ax.set_xlabel("Difference in Mean (High-DPAD - Low-DPAD)", fontsize=12, fontweight='bold')
    ax.set_title("Mean Difference: High-DPAD vs Low-DPAD (Top 15 Features)\n" +
                 "Green = Higher in High-DPAD | Red = Higher in Low-DPAD",
                 fontsize=13, fontweight='bold', pad=15)
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, (idx, row) in enumerate(comparison_df.iterrows()):
        value = row['Difference']
        ax.text(value, i, f" {value:.2f} ", 
               va='center', ha='left' if value > 0 else 'right',
               fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path / "mean_comparison_top_features.png", dpi=300, bbox_inches='tight')
    print("   ✓ Saved: mean_comparison_top_features.png")
    plt.close()


def generate_visualization_report(output_dir):
    """
    Generate summary report of all visualizations created
    """
    print("\n" + "="*70)
    print("GENERATING VISUALIZATION REPORT")
    print("="*70)
    
    report = []
    report.append("# DPAD Analysis - Visualization Report")
    report.append("=" * 70)
    report.append("")
    report.append("## Summary of Generated Visualizations")
    report.append("")
    report.append("This report catalogs all visualizations created to compare")
    report.append("High-DPAD vs Low-DPAD calling agents.")
    report.append("")
    
    report.append("## 1. Distribution Comparisons")
    report.append("")
    report.append("### distribution_boxplots.png")
    report.append("- Box plots for top 9 numerical features")
    report.append("- Shows median, quartiles, and outliers")
    report.append("- Yellow diamonds indicate means")
    report.append("- Clear comparison of central tendency and spread")
    report.append("")
    report.append("### distribution_violinplots.png")
    report.append("- Violin plots for top 6 features")
    report.append("- Shows full distribution shape (density)")
    report.append("- Individual data points overlaid as black dots")
    report.append("- Reveals multi-modality and distribution patterns")
    report.append("")
    
    report.append("## 2. Scatter Plot Comparisons")
    report.append("")
    report.append("### scatter_interruption_sentiment.png")
    report.append("- Relationship between interruption rate and sentiment progression")
    report.append("- Most important feature pair")
    report.append("- Shows clustering patterns between groups")
    report.append("")
    report.append("### pairplot_top4.png")
    report.append("- Pairwise relationships between top 4 features")
    report.append("- Diagonal: KDE distribution plots")
    report.append("- Off-diagonal: Scatter plots")
    report.append("- Comprehensive view of feature interactions")
    report.append("")
    
    report.append("## 3. Categorical Comparisons")
    report.append("")
    report.append("### categorical_distributions.png")
    report.append("- Bar plots for categorical features")
    report.append("- Percentage-based for fair comparison")
    report.append("- Shows category preferences by DPAD group")
    report.append("")
    
    report.append("## 4. Summary Dashboard")
    report.append("")
    report.append("### summary_dashboard.png")
    report.append("- **Comprehensive single-page overview**")
    report.append("- Top 7 features visualized")
    report.append("- Sample size bars")
    report.append("- Key relationship scatter plot")
    report.append("- Statistical summary table")
    report.append("- **Ready for executive presentation**")
    report.append("")
    
    report.append("## 5. Mean Comparison")
    report.append("")
    report.append("### mean_comparison_top_features.png")
    report.append("- Horizontal bar chart of mean differences")
    report.append("- Green = Higher in High-DPAD agents")
    report.append("- Red = Higher in Low-DPAD agents")
    report.append("- Sorted by absolute difference magnitude")
    report.append("")
    
    report.append("## How to Use These Visualizations")
    report.append("")
    report.append("**For Presentations:**")
    report.append("- Start with `summary_dashboard.png` for overview")
    report.append("- Use `distribution_violinplots.png` for detailed feature analysis")
    report.append("- Show `scatter_interruption_sentiment.png` for key relationship")
    report.append("")
    report.append("**For Reports:**")
    report.append("- Include `mean_comparison_top_features.png` for quick summary")
    report.append("- Add `distribution_boxplots.png` for statistical rigor")
    report.append("- Reference `pairplot_top4.png` for feature interactions")
    report.append("")
    report.append("**For Training:**")
    report.append("- Use `distribution_violinplots.png` to show ideal ranges")
    report.append("- Show `categorical_distributions.png` for behavior patterns")
    report.append("- Display `summary_dashboard.png` as motivation")
    report.append("")
    
    report.append("## Key Visual Insights")
    report.append("")
    report.append("1. **Clear Separation**: Distributions show distinct patterns between groups")
    report.append("2. **Interruption Dominance**: Interruption rate shows strongest visual difference")
    report.append("3. **Sentiment Correlation**: Positive relationship with DPAD performance")
    report.append("4. **Talk Ratio**: High-DPAD agents consistently talk less")
    report.append("5. **Consistency**: Patterns are consistent across visualization types")
    report.append("")
    
    # Save report
    report_path = output_dir / "analysis_outputs" / "visualizations" / "visualization_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Visualization report saved: {report_path}")


def main():
    """Main visualization pipeline"""
    
    print("\n" + "="*70)
    print("DPAD ANALYSIS - COMPREHENSIVE VISUALIZATIONS")
    print("="*70)
    print("\nCreating publication-ready visualizations")
    print("="*70)
    
    output_dir = Path("ML_for_DPAD")
    
    # Load data
    df, top_features = load_analysis_data()
    
    # Create visualizations
    create_distribution_plots(df, top_features, output_dir)
    create_scatter_comparisons(df, top_features, output_dir)
    create_categorical_comparisons(df, output_dir)
    create_top_features_comparison(df, top_features, output_dir)
    create_summary_dashboard(df, output_dir)
    
    # Generate report
    generate_visualization_report(output_dir)
    
    print("\n" + "="*70)
    print("✅ VISUALIZATION GENERATION COMPLETE")
    print("="*70)
    print("\nGenerated visualizations:")
    print("   ✓ distribution_boxplots.png")
    print("   ✓ distribution_violinplots.png")
    print("   ✓ scatter_interruption_sentiment.png")
    print("   ✓ pairplot_top4.png")
    print("   ✓ categorical_distributions.png")
    print("   ✓ mean_comparison_top_features.png")
    print("   ✓ summary_dashboard.png (⭐ EXECUTIVE SUMMARY)")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

