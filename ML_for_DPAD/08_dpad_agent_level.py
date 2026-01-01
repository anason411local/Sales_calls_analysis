"""
DPAD Analysis - Step 8: Agent-Level Analysis
============================================

Purpose:
--------
Aggregate call-level data to agent-level insights to understand individual
agent performance patterns and characteristics.

What This Script Does:
----------------------
1. Loads preprocessed data with agent identifiers
2. Aggregates metrics by agent:
   - Mean values for numerical features
   - Mode/distribution for categorical features
   - Call counts per agent
3. Creates agent performance profiles
4. Compares High-DPAD vs Low-DPAD agent groups
5. Identifies best practices from top performers
6. Generates agent-level visualizations and rankings

Why Agent-Level Analysis Matters:
----------------------------------
- Identifies specific agents who excel or need support
- Reveals consistent patterns across multiple calls per agent
- Enables targeted coaching and training
- Shows which behaviors are agent-specific vs situational
- Supports performance management decisions

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

# Set plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("notebook", font_scale=1.0)
sns.set_palette("husl")

COLORS = {
    'high_dpad': '#2ecc71',  # Green
    'low_dpad': '#e74c3c',   # Red
}


def load_data_with_agents():
    """Load preprocessed data and original data with agent identifiers"""
    print("\n" + "="*70)
    print("LOADING DATA WITH AGENT IDENTIFIERS")
    print("="*70)
    
    # Load preprocessed data
    data_path = Path("ML_for_DPAD/analysis_outputs/preprocessed_data")
    X = pd.read_csv(data_path / "X_features.csv")
    y = pd.read_csv(data_path / "y_target.csv").values.ravel()
    
    # Load original data to get agent IDs
    high_dpad = pd.read_csv("output_data/dpad_gretaer_than_1_temp.csv")
    low_dpad = pd.read_csv("output_data/dpad_less_than_1_temp.csv")
    
    # Combine and add DPAD flag
    high_dpad['high_dpad'] = 1
    low_dpad['high_dpad'] = 0
    
    full_data = pd.concat([high_dpad, low_dpad], ignore_index=True)
    
    # Extract agent column (TO_OMC_User)
    if 'TO_OMC_User' in full_data.columns:
        agent_col = 'TO_OMC_User'
    elif 'TO_OMC_User_encoded' in X.columns:
        agent_col = 'TO_OMC_User_encoded'
    else:
        print("⚠️  No agent identifier found. Using row index.")
        agent_col = None
    
    # Combine processed features with agent IDs and target
    if agent_col and agent_col in full_data.columns:
        df = X.copy()
        df['agent_id'] = full_data[agent_col].values[:len(X)]
        df['high_dpad'] = y
        df['DPAD_Group'] = df['high_dpad'].map({1: 'High-DPAD', 0: 'Low-DPAD'})
        
        print(f"\n✅ Loaded data with agent identifiers:")
        print(f"   Total calls: {len(df)}")
        print(f"   Total unique agents: {df['agent_id'].nunique()}")
        print(f"   High-DPAD agents: {df[df['high_dpad']==1]['agent_id'].nunique()}")
        print(f"   Low-DPAD agents: {df[df['high_dpad']==0]['agent_id'].nunique()}")
    else:
        print("⚠️  Could not find agent identifier column")
        df = X.copy()
        df['agent_id'] = range(len(X))  # Fallback
        df['high_dpad'] = y
        df['DPAD_Group'] = df['high_dpad'].map({1: 'High-DPAD', 0: 'Low-DPAD'})
    
    return df


def aggregate_by_agent(df):
    """
    Aggregate call-level data to agent-level metrics
    """
    print("\n" + "="*70)
    print("AGGREGATING DATA BY AGENT")
    print("="*70)
    
    # Identify numerical vs categorical features
    numerical_features = []
    categorical_features = []
    
    for col in df.columns:
        if col not in ['agent_id', 'high_dpad', 'DPAD_Group']:
            if df[col].dtype in ['float64', 'int64'] and df[col].nunique() > 10:
                numerical_features.append(col)
            else:
                categorical_features.append(col)
    
    print(f"\n📊 Aggregating {len(numerical_features)} numerical features...")
    print(f"📊 Aggregating {len(categorical_features)} categorical features...")
    
    # Numerical aggregations
    numerical_agg = df.groupby('agent_id')[numerical_features].agg(['mean', 'std', 'count'])
    
    # Flatten column names
    numerical_agg.columns = ['_'.join(col).strip() for col in numerical_agg.columns.values]
    numerical_agg = numerical_agg.reset_index()
    
    # Add agent group (High/Low DPAD)
    agent_group = df.groupby('agent_id')['high_dpad'].first().reset_index()
    agent_group['DPAD_Group'] = agent_group['high_dpad'].map({1: 'High-DPAD', 0: 'Low-DPAD'})
    
    # Merge
    agent_data = numerical_agg.merge(agent_group, on='agent_id')
    
    # Add call counts
    call_counts = df.groupby('agent_id').size().reset_index(name='total_calls')
    agent_data = agent_data.merge(call_counts, on='agent_id')
    
    print(f"\n✅ Agent-level data created:")
    print(f"   Total agents: {len(agent_data)}")
    print(f"   High-DPAD agents: {(agent_data['high_dpad']==1).sum()}")
    print(f"   Low-DPAD agents: {(agent_data['high_dpad']==0).sum()}")
    print(f"   Avg calls per agent: {agent_data['total_calls'].mean():.1f}")
    
    return agent_data, numerical_features


def create_agent_comparison_table(agent_data, numerical_features, output_dir):
    """
    Create comparison table of agent group averages
    """
    print("\n" + "="*70)
    print("CREATING AGENT GROUP COMPARISON TABLE")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "agent_level_comparison"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Select mean columns only
    mean_cols = [col for col in agent_data.columns if col.endswith('_mean')]
    
    # Calculate group averages
    comparison = []
    
    for col in mean_cols[:20]:  # Top 20 features
        feature_name = col.replace('_mean', '')
        
        low_mean = agent_data[agent_data['high_dpad']==0][col].mean()
        high_mean = agent_data[agent_data['high_dpad']==1][col].mean()
        difference = high_mean - low_mean
        
        low_std = agent_data[agent_data['high_dpad']==0][col].std()
        high_std = agent_data[agent_data['high_dpad']==1][col].std()
        
        comparison.append({
            'Feature': feature_name,
            'Low-DPAD Mean': low_mean,
            'Low-DPAD Std': low_std,
            'High-DPAD Mean': high_mean,
            'High-DPAD Std': high_std,
            'Difference': difference,
            'Abs Difference': abs(difference)
        })
    
    comparison_df = pd.DataFrame(comparison)
    comparison_df = comparison_df.sort_values('Abs Difference', ascending=False)
    
    # Save to CSV
    comparison_df.to_csv(output_path / "agent_group_comparison.csv", index=False)
    
    print(f"\n✅ Agent group comparison saved")
    print(f"\n📊 Top 5 Differences Between Agent Groups:")
    print("-" * 70)
    for idx, row in comparison_df.head(5).iterrows():
        direction = "Higher in High-DPAD" if row['Difference'] > 0 else "Higher in Low-DPAD"
        print(f"   {row['Feature']:.<45} {abs(row['Difference']):>8.3f} ({direction})")
    
    return comparison_df


def create_agent_rankings(agent_data, output_dir):
    """
    Create rankings of agents by key metrics
    """
    print("\n" + "="*70)
    print("CREATING AGENT RANKINGS")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "agent_level_comparison"
    
    # Key metrics for ranking
    key_metrics = [
        'interruption_rate_mean',
        'sentiment_progression_mean',
        'agent_talk_percentage_mean',
        'conversation_balance_mean',
        'total_interruptions_mean'
    ]
    
    rankings = {}
    
    for metric in key_metrics:
        if metric in agent_data.columns:
            # Sort (ascending for interruption, descending for sentiment)
            ascending = 'interruption' in metric or 'talk_percentage' in metric
            
            ranked = agent_data[['agent_id', 'DPAD_Group', metric, 'total_calls']].copy()
            ranked = ranked.sort_values(metric, ascending=ascending)
            ranked['rank'] = range(1, len(ranked) + 1)
            
            rankings[metric] = ranked
            
            print(f"\n📊 Top 3 Agents by {metric.replace('_mean', '')}:")
            for idx, row in ranked.head(3).iterrows():
                print(f"   #{row['rank']}: Agent {row['agent_id']} ({row['DPAD_Group']}) = {row[metric]:.3f}")
    
    # Save rankings
    for metric, ranked_df in rankings.items():
        filename = f"ranking_{metric.replace('_mean', '')}.csv"
        ranked_df.to_csv(output_path / filename, index=False)
    
    print(f"\n✅ Saved {len(rankings)} ranking files")
    
    return rankings


def create_agent_visualizations(agent_data, comparison_df, output_dir):
    """
    Create agent-level visualizations
    """
    print("\n" + "="*70)
    print("CREATING AGENT-LEVEL VISUALIZATIONS")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "agent_level_comparison"
    
    # 1. Agent Performance Heatmap
    print("\n📊 Creating agent performance heatmap...")
    
    # Select top 25 features by difference
    top_features = comparison_df.head(25)['Feature'].tolist()
    
    # Get mean columns for these features
    feature_cols = [f"{feat}_mean" for feat in top_features if f"{feat}_mean" in agent_data.columns]
    
    if len(feature_cols) > 0:
        # Create heatmap data
        heatmap_data = agent_data[['agent_id', 'DPAD_Group'] + feature_cols].copy()
        heatmap_data = heatmap_data.sort_values('DPAD_Group')
        
        # Normalize for better visualization
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        heatmap_data[feature_cols] = scaler.fit_transform(heatmap_data[feature_cols])
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(14, 18))  # Taller figure for 25 features
        
        # Prepare data for seaborn
        heatmap_plot = heatmap_data[feature_cols].T
        heatmap_plot.columns = [f"Agent {aid}\n({grp})" 
                               for aid, grp in zip(heatmap_data['agent_id'], 
                                                  heatmap_data['DPAD_Group'])]
        
        sns.heatmap(heatmap_plot, cmap='RdYlGn', center=0, 
                   annot=True, fmt='.1f', cbar_kws={'label': 'Standardized Score'},
                   linewidths=0.5, ax=ax)
        
        ax.set_title("Agent Performance Heatmap (Top 25 Features)\n" +
                     "Green = Above Average | Red = Below Average",
                     fontsize=13, fontweight='bold', pad=15)
        ax.set_ylabel("Feature", fontsize=11, fontweight='bold')
        ax.set_xlabel("Agent (sorted by DPAD Group)", fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path / "agent_performance_heatmap.png", dpi=300, bbox_inches='tight')
        print("   ✓ Saved: agent_performance_heatmap.png")
        plt.close()
    
    # 2. Agent Group Comparison Bars
    print("\n📊 Creating agent group comparison bars...")
    
    top_6_features = comparison_df.head(6)['Feature'].tolist()
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.ravel()
    
    for idx, feature in enumerate(top_6_features):
        ax = axes[idx]
        col = f"{feature}_mean"
        
        if col in agent_data.columns:
            # Bar plot
            means = agent_data.groupby('DPAD_Group')[col].mean()
            stds = agent_data.groupby('DPAD_Group')[col].std()
            
            x_pos = [0, 1]
            colors = [COLORS['low_dpad'], COLORS['high_dpad']]
            
            bars = ax.bar(x_pos, means.values, yerr=stds.values, 
                         color=colors, alpha=0.7, capsize=5, edgecolor='black')
            
            ax.set_xticks(x_pos)
            ax.set_xticklabels(['Low-DPAD', 'High-DPAD'])
            ax.set_ylabel("Mean Value", fontsize=10)
            ax.set_title(feature, fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add value labels
            for i, (bar, val) in enumerate(zip(bars, means.values)):
                ax.text(bar.get_x() + bar.get_width()/2, val, 
                       f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.suptitle("Agent-Level Mean Comparison: High-DPAD vs Low-DPAD Agents\n(Error bars show standard deviation)",
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(output_path / "agent_group_mean_comparison.png", dpi=300, bbox_inches='tight')
    print("   ✓ Saved: agent_group_mean_comparison.png")
    plt.close()
    
    # 3. Agent Scatter Plot
    print("\n📊 Creating agent scatter plot...")
    
    if 'interruption_rate_mean' in agent_data.columns and 'sentiment_progression_mean' in agent_data.columns:
        fig, ax = plt.subplots(figsize=(14, 9))  # Slightly larger for better spacing
        
        # Store all text objects for potential adjustment
        texts = []
        
        for group, color, label in [(0, COLORS['low_dpad'], 'Low-DPAD Agents'),
                                     (1, COLORS['high_dpad'], 'High-DPAD Agents')]:
            mask = agent_data['high_dpad'] == group
            ax.scatter(agent_data[mask]['interruption_rate_mean'],
                      agent_data[mask]['sentiment_progression_mean'],
                      c=color, label=label, s=250, alpha=0.7, 
                      edgecolors='black', linewidth=2, zorder=3)
            
            # Add agent labels with smart positioning
            for idx, row in agent_data[mask].iterrows():
                x = row['interruption_rate_mean']
                y = row['sentiment_progression_mean']
                agent_name = str(row['agent_id'])
                
                # Use text with offset and bbox for better visibility
                text = ax.annotate(f"A{agent_name}", 
                          xy=(x, y),
                          xytext=(8, 8),  # Offset the text by 8 points
                          textcoords='offset points',
                          fontsize=9, 
                          fontweight='bold',
                          bbox=dict(boxstyle='round,pad=0.3', 
                                   facecolor='white', 
                                   edgecolor='gray',
                                   alpha=0.8),
                          arrowprops=dict(arrowstyle='->', 
                                        connectionstyle='arc3,rad=0',
                                        color='gray',
                                        lw=1,
                                        alpha=0.6),
                          zorder=4)
                texts.append(text)
        
        # Try to use adjustText if available for automatic label positioning
        try:
            from adjustText import adjust_text
            adjust_text(texts, 
                       arrowprops=dict(arrowstyle='->', color='gray', lw=1, alpha=0.6),
                       expand_points=(1.5, 1.5),
                       expand_text=(1.2, 1.2),
                       force_points=(0.5, 0.5),
                       force_text=(0.5, 0.5))
            print("   ℹ️  Using adjustText for optimal label placement")
        except ImportError:
            print("   ℹ️  adjustText not available, using manual offsets")
            pass
        
        ax.set_xlabel("Mean Interruption Rate", fontsize=12, fontweight='bold')
        ax.set_ylabel("Mean Sentiment Progression", fontsize=12, fontweight='bold')
        ax.set_title("Agent Positioning: Interruption Rate vs Sentiment Progression\n" +
                     "Each point represents one agent's average across all their calls",
                     fontsize=13, fontweight='bold', pad=15)
        ax.legend(fontsize=11, loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / "agent_scatter_key_features.png", dpi=300, bbox_inches='tight')
        print("   ✓ Saved: agent_scatter_key_features.png")
        plt.close()
    
    # 4. Calls per Agent Distribution
    print("\n📊 Creating calls per agent distribution...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for group, color, label in [(0, COLORS['low_dpad'], 'Low-DPAD'),
                                 (1, COLORS['high_dpad'], 'High-DPAD')]:
        data = agent_data[agent_data['high_dpad'] == group]
        ax.bar(data['agent_id'], data['total_calls'], 
              color=color, alpha=0.7, label=label, edgecolor='black')
    
    ax.set_xlabel("Agent ID", fontsize=12, fontweight='bold')
    ax.set_ylabel("Number of Calls", fontsize=12, fontweight='bold')
    ax.set_title("Call Volume by Agent", fontsize=13, fontweight='bold', pad=15)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_path / "calls_per_agent.png", dpi=300, bbox_inches='tight')
    print("   ✓ Saved: calls_per_agent.png")
    plt.close()


def generate_agent_report(agent_data, comparison_df, rankings, output_dir):
    """
    Generate comprehensive agent-level report
    """
    print("\n" + "="*70)
    print("GENERATING AGENT-LEVEL REPORT")
    print("="*70)
    
    report = []
    report.append("# DPAD Analysis - Agent-Level Report")
    report.append("=" * 70)
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append("This report aggregates call-level insights to agent-level patterns,")
    report.append("revealing consistent behavioral differences between High-DPAD and")
    report.append("Low-DPAD agents.")
    report.append("")
    
    # Overall statistics
    report.append("## 1. Agent Overview")
    report.append("")
    report.append(f"**Total Agents Analyzed:** {len(agent_data)}")
    report.append(f"**High-DPAD Agents:** {(agent_data['high_dpad']==1).sum()}")
    report.append(f"**Low-DPAD Agents:** {(agent_data['high_dpad']==0).sum()}")
    report.append("")
    report.append(f"**Call Distribution:**")
    report.append(f"- Total calls: {agent_data['total_calls'].sum()}")
    report.append(f"- Avg calls per agent: {agent_data['total_calls'].mean():.1f}")
    report.append(f"- Min calls per agent: {agent_data['total_calls'].min()}")
    report.append(f"- Max calls per agent: {agent_data['total_calls'].max()}")
    report.append("")
    
    # Top differences
    report.append("## 2. Key Differences Between Agent Groups")
    report.append("")
    report.append("Features with largest mean differences (agent-level averages):")
    report.append("")
    report.append("| Rank | Feature | Low-DPAD | High-DPAD | Difference |")
    report.append("|------|---------|----------|-----------|------------|")
    
    for idx, row in comparison_df.head(15).iterrows():
        rank = idx + 1 if isinstance(idx, int) else list(comparison_df.index).index(idx) + 1
        report.append(f"| {rank:2d}   | {row['Feature']:<35} | {row['Low-DPAD Mean']:>8.3f} | "
                     f"{row['High-DPAD Mean']:>9.3f} | {row['Difference']:>10.3f} |")
    report.append("")
    
    # Best practices
    report.append("## 3. Best Practices from High-DPAD Agents")
    report.append("")
    report.append("What High-DPAD agents do differently (on average):")
    report.append("")
    
    positive_diffs = comparison_df[comparison_df['Difference'] > 0].head(5)
    negative_diffs = comparison_df[comparison_df['Difference'] < 0].head(5)
    
    if len(positive_diffs) > 0:
        report.append("### Higher Values (Good):")
        for idx, row in positive_diffs.iterrows():
            report.append(f"- **{row['Feature']}**: {row['High-DPAD Mean']:.3f} vs "
                         f"{row['Low-DPAD Mean']:.3f} (Δ +{row['Difference']:.3f})")
        report.append("")
    
    if len(negative_diffs) > 0:
        report.append("### Lower Values (Good):")
        for idx, row in negative_diffs.iterrows():
            report.append(f"- **{row['Feature']}**: {row['High-DPAD Mean']:.3f} vs "
                         f"{row['Low-DPAD Mean']:.3f} (Δ {row['Difference']:.3f})")
        report.append("")
    
    # Individual agent insights
    if 'interruption_rate_mean' in rankings:
        report.append("## 4. Individual Agent Performance")
        report.append("")
        report.append("### Top 5 Agents by Interruption Rate (Lower is Better):")
        report.append("")
        
        top_agents = rankings['interruption_rate_mean'].head(5)
        for idx, row in top_agents.iterrows():
            report.append(f"{int(row['rank'])}. **Agent {row['agent_id']}** ({row['DPAD_Group']}): "
                         f"{row['interruption_rate_mean']:.3f} - {row['total_calls']} calls")
        report.append("")
    
    # Consistency analysis
    report.append("## 5. Consistency Analysis")
    report.append("")
    report.append("Standard deviation reflects consistency across an agent's calls:")
    report.append("")
    
    std_cols = [col for col in agent_data.columns if col.endswith('_std')][:5]
    for col in std_cols:
        feature_name = col.replace('_std', '').replace('_mean', '')
        low_std = agent_data[agent_data['high_dpad']==0][col].mean()
        high_std = agent_data[agent_data['high_dpad']==1][col].mean()
        
        more_consistent = "High-DPAD" if high_std < low_std else "Low-DPAD"
        report.append(f"- **{feature_name}**: {more_consistent} agents more consistent "
                     f"(std: {high_std:.3f} vs {low_std:.3f})")
    report.append("")
    
    # Actionable insights
    report.append("## 6. Actionable Insights for Management")
    report.append("")
    report.append("### For Coaching:")
    report.append("1. Focus on agents with high interruption rates")
    report.append("2. Use top performers as peer mentors")
    report.append("3. Share behavioral patterns from High-DPAD agents")
    report.append("4. Track improvement over time using these metrics")
    report.append("")
    report.append("### For Hiring:")
    report.append("1. Test for patience and listening skills")
    report.append("2. Assess emotional intelligence (sentiment management)")
    report.append("3. Evaluate communication balance (not just talking ability)")
    report.append("")
    report.append("### For Performance Management:")
    report.append("1. Set benchmarks based on High-DPAD agent averages")
    report.append("2. Monitor agent-level trends over time")
    report.append("3. Identify agents needing additional support")
    report.append("")
    
    # Save report
    report_path = output_dir / "analysis_outputs" / "agent_level_comparison" / "agent_level_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Agent-level report saved: {report_path}")


def main():
    """Main agent-level analysis pipeline"""
    
    print("\n" + "="*70)
    print("DPAD ANALYSIS - AGENT-LEVEL AGGREGATION")
    print("="*70)
    print("\nAggregating call-level insights to agent-level patterns")
    print("="*70)
    
    output_dir = Path("ML_for_DPAD")
    
    # Load data with agent IDs
    df = load_data_with_agents()
    
    # Aggregate by agent
    agent_data, numerical_features = aggregate_by_agent(df)
    
    # Create comparison table
    comparison_df = create_agent_comparison_table(agent_data, numerical_features, output_dir)
    
    # Create agent rankings
    rankings = create_agent_rankings(agent_data, output_dir)
    
    # Create visualizations
    create_agent_visualizations(agent_data, comparison_df, output_dir)
    
    # Generate report
    generate_agent_report(agent_data, comparison_df, rankings, output_dir)
    
    # Save agent data
    output_path = output_dir / "analysis_outputs" / "agent_level_comparison"
    agent_data.to_csv(output_path / "agent_aggregated_data.csv", index=False)
    
    print("\n" + "="*70)
    print("✅ AGENT-LEVEL ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nKey Findings:")
    print(f"   Total agents: {len(agent_data)}")
    print(f"   Avg calls per agent: {agent_data['total_calls'].mean():.1f}")
    print(f"\nTop 3 Differentiating Features (agent-level):")
    for idx, row in comparison_df.head(3).iterrows():
        print(f"   {row['Feature']:.<50} Δ {abs(row['Difference']):.3f}")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

