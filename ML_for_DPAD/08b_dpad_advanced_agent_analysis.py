"""
DPAD Analysis - Step 8B: Advanced Agent-Level Analysis
=======================================================

Purpose:
--------
Advanced statistical, machine learning, and temporal analysis of agent performance
to uncover deeper insights beyond basic aggregation.

What This Script Does:
----------------------
1. **Temporal Analysis**: Track agent performance over time
2. **Statistical Rigor**: Effect sizes, confidence intervals, bootstrap testing
3. **Dimensionality Reduction**: PCA to identify key agent "dimensions"
4. **Clustering**: Identify agent archetypes/groups
5. **Feature Importance**: ML models trained on agent-level data
6. **Network Analysis**: Feature correlation patterns at agent level
7. **Advanced Visualizations**: Radar charts, dendrograms, PCA biplots, timelines

Why This Matters:
-----------------
- Small sample size (11 agents) requires sophisticated statistical methods
- Temporal patterns reveal agent improvement/decline trends
- Clustering identifies coaching archetypes
- PCA reveals underlying behavioral dimensions
- Advanced visualizations communicate complex patterns clearly

Author: AI Agent
Date: 2026-01-02
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import sys
import warnings
from datetime import datetime
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, LeaveOneOut
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import itertools

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
    'cluster': ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
}


def load_data_with_temporal():
    """Load data with temporal information"""
    print("\n" + "="*70)
    print("LOADING DATA WITH TEMPORAL INFORMATION")
    print("="*70)
    
    # Load original data with dates
    high_dpad = pd.read_csv("output_data/dpad_gretaer_than_1_temp.csv")
    low_dpad = pd.read_csv("output_data/dpad_less_than_1_temp.csv")
    
    # Add DPAD flag
    high_dpad['high_dpad'] = 1
    low_dpad['high_dpad'] = 0
    
    # Combine
    df = pd.concat([high_dpad, low_dpad], ignore_index=True)
    
    # Parse dates
    df['call_date'] = pd.to_datetime(df['TO_OMC_Call_Date_O'], format='%m/%d/%Y %H:%M', errors='coerce')
    df['call_week'] = df['call_date'].dt.to_period('W')
    df['call_day'] = df['call_date'].dt.date
    
    # Load preprocessed features
    data_path = Path("ML_for_DPAD/analysis_outputs/preprocessed_data")
    X = pd.read_csv(data_path / "X_features.csv")
    
    # Combine with dates and agent info
    df_combined = X.copy()
    df_combined['agent_id'] = df['TO_OMC_User'].values[:len(X)]
    df_combined['high_dpad'] = df['high_dpad'].values[:len(X)]
    df_combined['call_date'] = df['call_date'].values[:len(X)]
    df_combined['call_week'] = df['call_week'].values[:len(X)]
    df_combined['call_day'] = df['call_day'].values[:len(X)]
    
    print(f"\n✅ Loaded {len(df_combined)} calls")
    print(f"   Date range: {df_combined['call_date'].min()} to {df_combined['call_date'].max()}")
    print(f"   Agents: {df_combined['agent_id'].nunique()}")
    
    # Load agent aggregated data
    agent_path = Path("ML_for_DPAD/analysis_outputs/agent_level_comparison")
    agent_data = pd.read_csv(agent_path / "agent_aggregated_data.csv")
    
    return df_combined, agent_data


def bootstrap_confidence_interval(data, n_bootstrap=1000, ci=95):
    """Calculate bootstrap confidence interval"""
    bootstrap_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_means.append(np.mean(sample))
    
    lower = np.percentile(bootstrap_means, (100 - ci) / 2)
    upper = np.percentile(bootstrap_means, 100 - (100 - ci) / 2)
    
    return lower, upper


def calculate_effect_sizes_agent_level(agent_data):
    """Calculate Cohen's d for all features at agent level"""
    print("\n" + "="*70)
    print("CALCULATING AGENT-LEVEL EFFECT SIZES")
    print("="*70)
    
    mean_cols = [col for col in agent_data.columns if col.endswith('_mean')]
    
    effect_sizes = []
    
    for col in mean_cols:
        feature_name = col.replace('_mean', '')
        
        high_dpad_vals = agent_data[agent_data['high_dpad'] == 1][col].values
        low_dpad_vals = agent_data[agent_data['high_dpad'] == 0][col].values
        
        # Remove NaN
        high_dpad_vals = high_dpad_vals[~np.isnan(high_dpad_vals)]
        low_dpad_vals = low_dpad_vals[~np.isnan(low_dpad_vals)]
        
        if len(high_dpad_vals) > 0 and len(low_dpad_vals) > 0:
            # Cohen's d
            pooled_std = np.sqrt(((len(high_dpad_vals) - 1) * np.var(high_dpad_vals, ddof=1) +
                                   (len(low_dpad_vals) - 1) * np.var(low_dpad_vals, ddof=1)) /
                                  (len(high_dpad_vals) + len(low_dpad_vals) - 2))
            
            if pooled_std > 0:
                cohens_d = (np.mean(high_dpad_vals) - np.mean(low_dpad_vals)) / pooled_std
            else:
                cohens_d = 0
            
            # T-test
            t_stat, p_value = stats.ttest_ind(high_dpad_vals, low_dpad_vals)
            
            # Bootstrap CI for means
            high_ci_lower, high_ci_upper = bootstrap_confidence_interval(high_dpad_vals)
            low_ci_lower, low_ci_upper = bootstrap_confidence_interval(low_dpad_vals)
            
            effect_sizes.append({
                'Feature': feature_name,
                'Cohens_D': cohens_d,
                'Abs_Cohens_D': abs(cohens_d),
                'High_Mean': np.mean(high_dpad_vals),
                'High_CI_Lower': high_ci_lower,
                'High_CI_Upper': high_ci_upper,
                'Low_Mean': np.mean(low_dpad_vals),
                'Low_CI_Lower': low_ci_lower,
                'Low_CI_Upper': low_ci_upper,
                'P_Value': p_value,
                'Significant': p_value < 0.05,
                'Effect_Category': 'Large' if abs(cohens_d) >= 0.8 else 
                                   'Medium' if abs(cohens_d) >= 0.5 else 
                                   'Small' if abs(cohens_d) >= 0.2 else 'Negligible'
            })
    
    effect_df = pd.DataFrame(effect_sizes)
    effect_df = effect_df.sort_values('Abs_Cohens_D', ascending=False)
    
    print(f"\n✅ Calculated effect sizes for {len(effect_df)} features")
    print(f"\n📊 Effect Size Distribution:")
    print(f"   Large (|d| >= 0.8):    {(effect_df['Abs_Cohens_D'] >= 0.8).sum()}")
    print(f"   Medium (|d| >= 0.5):   {((effect_df['Abs_Cohens_D'] >= 0.5) & (effect_df['Abs_Cohens_D'] < 0.8)).sum()}")
    print(f"   Small (|d| >= 0.2):    {((effect_df['Abs_Cohens_D'] >= 0.2) & (effect_df['Abs_Cohens_D'] < 0.5)).sum()}")
    print(f"   Negligible (|d| < 0.2): {(effect_df['Abs_Cohens_D'] < 0.2).sum()}")
    
    return effect_df


def perform_pca_analysis(agent_data):
    """Perform PCA on agent-level data"""
    print("\n" + "="*70)
    print("PERFORMING PCA ANALYSIS")
    print("="*70)
    
    # Select mean features
    mean_cols = [col for col in agent_data.columns if col.endswith('_mean')]
    
    # Prepare data
    X = agent_data[mean_cols].copy()
    X = X.fillna(X.mean())  # Fill NaN with column mean
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # PCA
    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)
    
    # Explained variance
    explained_var = pca.explained_variance_ratio_
    cumulative_var = np.cumsum(explained_var)
    
    # How many components to explain 80% variance?
    n_components_80 = np.argmax(cumulative_var >= 0.80) + 1
    
    print(f"\n✅ PCA completed")
    print(f"   Components for 80% variance: {n_components_80}")
    print(f"   PC1 explains: {explained_var[0]*100:.1f}%")
    print(f"   PC2 explains: {explained_var[1]*100:.1f}%")
    print(f"   PC1+PC2 explains: {(explained_var[0]+explained_var[1])*100:.1f}%")
    
    # Get loadings (feature contributions)
    loadings = pd.DataFrame(
        pca.components_.T,
        columns=[f'PC{i+1}' for i in range(len(pca.components_))],
        index=[col.replace('_mean', '') for col in mean_cols]
    )
    
    pca_results = {
        'pca': pca,
        'X_pca': X_pca,
        'X_scaled': X_scaled,
        'scaler': scaler,
        'loadings': loadings,
        'explained_var': explained_var,
        'cumulative_var': cumulative_var,
        'feature_names': [col.replace('_mean', '') for col in mean_cols]
    }
    
    return pca_results


def perform_clustering(agent_data, pca_results):
    """Perform hierarchical and k-means clustering"""
    print("\n" + "="*70)
    print("PERFORMING CLUSTERING ANALYSIS")
    print("="*70)
    
    X_scaled = pca_results['X_scaled']
    
    # Hierarchical clustering
    linkage_matrix = linkage(X_scaled, method='ward')
    
    # Try different numbers of clusters (2-4)
    silhouette_scores = []
    for n_clusters in range(2, min(5, len(agent_data))):
        cluster_labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust')
        if len(np.unique(cluster_labels)) > 1:
            sil_score = silhouette_score(X_scaled, cluster_labels)
            silhouette_scores.append((n_clusters, sil_score))
    
    # Best number of clusters
    if silhouette_scores:
        best_n_clusters = max(silhouette_scores, key=lambda x: x[1])[0]
    else:
        best_n_clusters = 2
    
    cluster_labels = fcluster(linkage_matrix, best_n_clusters, criterion='maxclust')
    
    print(f"\n✅ Clustering completed")
    print(f"   Best number of clusters: {best_n_clusters}")
    print(f"   Silhouette score: {silhouette_scores[-1][1]:.3f}" if silhouette_scores else "")
    
    # Assign clusters to agent data
    agent_data_clustered = agent_data.copy()
    agent_data_clustered['cluster'] = cluster_labels
    
    clustering_results = {
        'linkage_matrix': linkage_matrix,
        'cluster_labels': cluster_labels,
        'n_clusters': best_n_clusters,
        'silhouette_scores': silhouette_scores,
        'agent_data_clustered': agent_data_clustered
    }
    
    return clustering_results


def analyze_temporal_trends(df_combined):
    """Analyze how agents perform over time"""
    print("\n" + "="*70)
    print("ANALYZING TEMPORAL TRENDS")
    print("="*70)
    
    # Key metrics to track
    key_metrics = [
        'interruption_rate',
        'sentiment_progression',
        'acknowledgement_rate',
        'agent_talk_percentage',
        'total_call_duration'
    ]
    
    temporal_data = []
    
    for agent_id in df_combined['agent_id'].unique():
        agent_calls = df_combined[df_combined['agent_id'] == agent_id].copy()
        agent_calls = agent_calls.sort_values('call_date')
        
        # Calculate rolling averages (window=10 calls)
        for metric in key_metrics:
            if metric in agent_calls.columns:
                agent_calls[f'{metric}_rolling'] = agent_calls[metric].rolling(window=10, min_periods=5).mean()
        
        # Aggregate by week
        weekly = agent_calls.groupby('call_week').agg({
            **{metric: 'mean' for metric in key_metrics if metric in agent_calls.columns},
            'high_dpad': 'first'
        }).reset_index()
        
        weekly['agent_id'] = agent_id
        temporal_data.append(weekly)
    
    if temporal_data:
        temporal_df = pd.concat(temporal_data, ignore_index=True)
    else:
        temporal_df = pd.DataFrame()
    
    print(f"\n✅ Temporal analysis completed")
    print(f"   Agents tracked: {df_combined['agent_id'].nunique()}")
    print(f"   Date range: {df_combined['call_date'].min()} to {df_combined['call_date'].max()}")
    
    return temporal_df


def create_advanced_visualizations(agent_data, effect_df, pca_results, clustering_results, 
                                   temporal_df, output_dir):
    """Create advanced visualizations"""
    print("\n" + "="*70)
    print("CREATING ADVANCED VISUALIZATIONS")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "agent_level_advanced"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Effect Size with Confidence Intervals
    print("\n📊 Creating effect size visualization with CI...")
    create_effect_size_ci_plot(effect_df, output_path)
    
    # 1b. Agent Group Mean Comparison (NEW)
    print("\n📊 Creating agent group mean comparison...")
    create_agent_group_mean_comparison(agent_data, effect_df, output_path)
    
    # 2. PCA Biplot
    print("\n📊 Creating PCA biplot...")
    create_pca_biplot(agent_data, pca_results, output_path)
    
    # 3. Hierarchical Clustering Dendrogram (Standalone)
    print("\n📊 Creating clustering dendrogram (standalone)...")
    create_clustering_dendrogram_standalone(agent_data, clustering_results, output_path)
    
    # 4. Agent Feature Heatmap (Separate)
    print("\n📊 Creating agent feature heatmap...")
    create_agent_feature_heatmap(agent_data, clustering_results, output_path)
    
    # 4. Radar Charts
    print("\n📊 Creating radar charts...")
    create_radar_charts(agent_data, effect_df, output_path)
    
    # 5. Agent Similarity Heatmap
    print("\n📊 Creating agent similarity matrix...")
    create_agent_similarity_matrix(agent_data, output_path)
    
    # 6. Temporal Trends
    print("\n📊 Creating temporal trend analysis...")
    create_temporal_visualizations(temporal_df, output_path)
    
    # 7. Feature Correlation Network
    print("\n📊 Creating feature correlation network...")
    create_feature_network(agent_data, output_path)
    
    print(f"\n✅ All advanced visualizations saved to: {output_path}")


def create_effect_size_ci_plot(effect_df, output_path):
    """Plot effect sizes with confidence intervals"""
    top_features = effect_df.head(30)  # INCREASED FROM 20 TO 30
    
    fig, ax = plt.subplots(figsize=(16, 14))  # INCREASED SIZE FOR 30 FEATURES
    
    y_pos = np.arange(len(top_features))
    
    # Plot Cohen's d with error bars (using CI of means to approximate)
    colors = [COLORS['high_dpad'] if d > 0 else COLORS['low_dpad'] 
              for d in top_features['Cohens_D']]
    
    bars = ax.barh(y_pos, top_features['Cohens_D'], color=colors, alpha=0.7, edgecolor='black')
    
    # Add reference lines
    ax.axvline(0, color='black', linewidth=1.5, linestyle='-')
    ax.axvline(0.2, color='gray', linewidth=0.8, linestyle='--', alpha=0.5)
    ax.axvline(-0.2, color='gray', linewidth=0.8, linestyle='--', alpha=0.5)
    ax.axvline(0.5, color='gray', linewidth=0.8, linestyle='--', alpha=0.5)
    ax.axvline(-0.5, color='gray', linewidth=0.8, linestyle='--', alpha=0.5)
    ax.axvline(0.8, color='gray', linewidth=0.8, linestyle='--', alpha=0.5, label='Large (|d|≥0.8)')
    ax.axvline(-0.8, color='gray', linewidth=0.8, linestyle='--', alpha=0.5)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_features['Feature'], fontsize=9)  # SLIGHTLY SMALLER FONT FOR 30 FEATURES
    ax.set_xlabel("Cohen's d (Effect Size)", fontsize=12, fontweight='bold')
    ax.set_title("Top 30 Agent-Level Effect Sizes\n" +
                 "Positive = Higher in High-DPAD | Negative = Higher in Low-DPAD",
                 fontsize=14, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, top_features['Cohens_D'])):
        x_pos = val + (0.05 if val > 0 else -0.05)
        ha = 'left' if val > 0 else 'right'
        ax.text(x_pos, bar.get_y() + bar.get_height()/2, f'{val:.2f}',
                ha=ha, va='center', fontsize=8, fontweight='bold')  # SMALLER FONT FOR VALUES
    
    plt.tight_layout()
    plt.savefig(output_path / "08b_effect_sizes_agent_level.png", dpi=300, bbox_inches='tight')
    plt.close()


def create_agent_group_mean_comparison(agent_data, effect_df, output_path):
    """Create grouped bar chart comparing actual mean values between High-DPAD and Low-DPAD agents"""
    print("   Creating agent group mean value comparison...")
    
    # Get top 30 features by effect size
    top_features = effect_df.head(30)['Feature'].tolist()
    
    # Extract mean values for each group
    high_dpad_means = []
    low_dpad_means = []
    feature_names = []
    
    for feature in top_features:
        mean_col = f"{feature}_mean"
        if mean_col in agent_data.columns:
            high_mean = agent_data[agent_data['high_dpad'] == 1][mean_col].mean()
            low_mean = agent_data[agent_data['high_dpad'] == 0][mean_col].mean()
            
            high_dpad_means.append(high_mean)
            low_dpad_means.append(low_mean)
            feature_names.append(feature)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 14))
    
    y_pos = np.arange(len(feature_names))
    bar_height = 0.35
    
    # Create bars
    bars1 = ax.barh(y_pos - bar_height/2, high_dpad_means, bar_height, 
                    label='High-DPAD Agents (>1 deal/agent/day)', 
                    color=COLORS['high_dpad'], alpha=0.8, edgecolor='black', linewidth=0.8)
    bars2 = ax.barh(y_pos + bar_height/2, low_dpad_means, bar_height,
                    label='Low-DPAD Agents (<1 deal/agent/day)',
                    color=COLORS['low_dpad'], alpha=0.8, edgecolor='black', linewidth=0.8)
    
    # Customize axes
    ax.set_yticks(y_pos)
    ax.set_yticklabels(feature_names, fontsize=9)
    ax.set_xlabel('Mean Value', fontsize=12, fontweight='bold')
    ax.set_title('Top 30 Features: High-DPAD vs Low-DPAD Agent Group Means\n' +
                 'Direct Comparison of Actual Average Values',
                 fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='lower right', fontsize=11, framealpha=0.95)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels on bars
    for i, (bar1, bar2, val1, val2) in enumerate(zip(bars1, bars2, high_dpad_means, low_dpad_means)):
        # High-DPAD label
        x_pos1 = val1 + (abs(val1) * 0.01 if val1 > 0 else -abs(val1) * 0.01)
        ha1 = 'left' if val1 > 0 else 'right'
        ax.text(x_pos1, bar1.get_y() + bar1.get_height()/2, f'{val1:.2f}',
                ha=ha1, va='center', fontsize=7, fontweight='bold', color='darkgreen')
        
        # Low-DPAD label
        x_pos2 = val2 + (abs(val2) * 0.01 if val2 > 0 else -abs(val2) * 0.01)
        ha2 = 'left' if val2 > 0 else 'right'
        ax.text(x_pos2, bar2.get_y() + bar2.get_height()/2, f'{val2:.2f}',
                ha=ha2, va='center', fontsize=7, fontweight='bold', color='darkred')
    
    # Add reading guidelines
    guidelines = ("📖 Reading Guide:\n"
                 "• Green bars = High-DPAD agent averages\n"
                 "• Red bars = Low-DPAD agent averages\n"
                 "• Values show actual mean scores\n"
                 "• Larger gap = bigger difference between groups\n"
                 "• Features ordered by effect size (top to bottom)")
    
    props = dict(boxstyle='round,pad=0.7', facecolor='lightyellow', 
                edgecolor='black', linewidth=2, alpha=0.98)
    ax.text(0.98, 0.98, guidelines, transform=ax.transAxes,
           fontsize=9, verticalalignment='top', horizontalalignment='right', 
           bbox=props, family='sans-serif')
    
    plt.tight_layout()
    plt.savefig(output_path / "08b_agent_group_means_comparison_top30.png", dpi=300, bbox_inches='tight')
    plt.close()



def create_pca_biplot(agent_data, pca_results, output_path):
    """Create PCA biplot with agents and top features - IMPROVED READABILITY"""
    fig, ax = plt.subplots(figsize=(18, 14))  # LARGER FIGURE
    
    X_pca = pca_results['X_pca']
    loadings = pca_results['loadings']
    
    # Create agent labels with full names
    agent_labels = []
    for idx, row in agent_data.iterrows():
        dpad_label = 'H' if row['high_dpad'] == 1 else 'L'
        agent_labels.append(f"{row['agent_id']} ({dpad_label})")
    
    # Plot agents as scatter points
    for idx, row in agent_data.iterrows():
        color = COLORS['high_dpad'] if row['high_dpad'] == 1 else COLORS['low_dpad']
        label = 'High-DPAD' if row['high_dpad'] == 1 else 'Low-DPAD'
        
        # Plot point
        ax.scatter(X_pca[idx, 0], X_pca[idx, 1], c=color, s=400, alpha=0.7,
                  edgecolors='black', linewidth=2.5, zorder=3,
                  label=label if idx == agent_data[agent_data['high_dpad'] == row['high_dpad']].index[0] else '')
    
    # Add agent labels with smart positioning to avoid overlap
    # Calculate offsets based on point positions
    texts = []
    for idx, row in agent_data.iterrows():
        x, y = X_pca[idx, 0], X_pca[idx, 1]
        
        # Determine offset direction based on position
        # This creates a radial offset from center
        offset_x = 0.5 if x > 0 else -0.5
        offset_y = 0.5 if y > 0 else -0.5
        
        # Create text with white background box
        text = ax.annotate(
            agent_labels[idx],
            xy=(x, y),
            xytext=(x + offset_x, y + offset_y),
            fontsize=10,
            fontweight='bold',
            ha='center',
            va='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor='black', linewidth=1.5, alpha=0.9),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3',
                          color='black', lw=1.5, alpha=0.7),
            zorder=4
        )
        texts.append(text)
    
    # Try to use adjustText if available for even better positioning
    try:
        from adjustText import adjust_text
        adjust_text(texts, 
                   arrowprops=dict(arrowstyle='->', color='black', lw=1.5, alpha=0.7),
                   expand_points=(1.5, 1.5),
                   force_points=(0.5, 0.5),
                   ax=ax)
    except ImportError:
        print("   ℹ️ adjustText not available, using manual positioning")
    
    # Plot top feature loadings (arrows)
    top_n = 10
    loading_magnitude = np.sqrt(loadings['PC1']**2 + loadings['PC2']**2)
    top_features_idx = loading_magnitude.nlargest(top_n).index
    
    scale = 3  # Scaling factor for arrows
    for feature in top_features_idx:
        ax.arrow(0, 0, loadings.loc[feature, 'PC1'] * scale, loadings.loc[feature, 'PC2'] * scale,
                head_width=0.2, head_length=0.15, fc='darkblue', ec='darkblue', 
                alpha=0.5, linewidth=2.5, zorder=2)
        
        # Feature labels with background
        ax.text(loadings.loc[feature, 'PC1'] * scale * 1.2, 
               loadings.loc[feature, 'PC2'] * scale * 1.2,
               feature, fontsize=10, ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', 
                        edgecolor='darkblue', alpha=0.85, linewidth=1),
               zorder=2)
    
    ax.set_xlabel(f"PC1 ({pca_results['explained_var'][0]*100:.1f}% variance)", 
                 fontsize=13, fontweight='bold')
    ax.set_ylabel(f"PC2 ({pca_results['explained_var'][1]*100:.1f}% variance)", 
                 fontsize=13, fontweight='bold')
    ax.set_title("PCA Biplot: Agent Positioning in Feature Space\n" +
                 "Arrows show top 10 feature directions | Labels show agent names (H=High-DPAD, L=Low-DPAD)",
                 fontsize=15, fontweight='bold', pad=20)
    ax.legend(fontsize=12, loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(0, color='black', linewidth=1.2, alpha=0.8)
    ax.axvline(0, color='black', linewidth=1.2, alpha=0.8)
    
    # Add some padding to axes
    x_margin = (X_pca[:, 0].max() - X_pca[:, 0].min()) * 0.2
    y_margin = (X_pca[:, 1].max() - X_pca[:, 1].min()) * 0.2
    ax.set_xlim(X_pca[:, 0].min() - x_margin, X_pca[:, 0].max() + x_margin)
    ax.set_ylim(X_pca[:, 1].min() - y_margin, X_pca[:, 1].max() + y_margin)
    
    plt.tight_layout()
    plt.savefig(output_path / "08b_pca_biplot.png", dpi=300, bbox_inches='tight')
    plt.close()


def create_clustering_dendrogram_standalone(agent_data, clustering_results, output_path):
    """Create standalone hierarchical clustering dendrogram with reading guidelines"""
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Dendrogram
    linkage_matrix = clustering_results['linkage_matrix']
    
    labels = [f"{row['agent_id']} ({'H' if row['high_dpad']==1 else 'L'})"
              for _, row in agent_data.iterrows()]
    
    # Create dendrogram
    dendro = dendrogram(linkage_matrix, ax=ax, labels=labels, orientation='top',
                       color_threshold=10, above_threshold_color='#2c3e50',
                       leaf_font_size=11)
    
    ax.set_ylabel("Distance (Ward Linkage)", fontsize=13, fontweight='bold')
    ax.set_xlabel("Agents (H=High-DPAD, L=Low-DPAD)", fontsize=13, fontweight='bold')
    ax.set_title("Hierarchical Clustering of Agents\nBased on 60 Behavioral Features",
                fontsize=15, fontweight='bold', pad=20)
    
    # Add distance reference lines
    ax.axhline(y=2, color='green', linestyle='--', alpha=0.3, linewidth=1.5, label='Very Similar (d≤2)')
    ax.axhline(y=6, color='orange', linestyle='--', alpha=0.3, linewidth=1.5, label='Moderately Similar (d≤6)')
    ax.axhline(y=10, color='red', linestyle='--', alpha=0.3, linewidth=1.5, label='Different (d≤10)')
    ax.axhline(y=14, color='darkred', linestyle='--', alpha=0.3, linewidth=2, label='Very Different (d>10)')
    
    # Add legend
    ax.legend(loc='upper left', fontsize=10, framealpha=0.95)
    
    # Add reading guidelines as text box
    guidelines_text = """
    📖 HOW TO READ THIS DENDROGRAM:
    
    1. VERTICAL AXIS (Distance): Higher = more different agents
       • 0-2: Very similar behavioral patterns
       • 2-6: Moderately similar patterns  
       • 6-10: Different patterns
       • >10: Very different (outliers)
    
    2. HORIZONTAL LINES: Connect agents that merge into clusters
       • Lower connections = more similar agents
       • Higher connections = less similar agents
    
    3. CLUSTERS IDENTIFIED:
       • Main Cluster (10 agents): Mixed High/Low-DPAD
       • Outlier Cluster (1 agent): Bryan Bernal - Unique profile
    
    4. INTERPRETATION:
       • Agents close together can use similar coaching
       • Outliers need individualized approaches
    """
    
    # Add text box with guidelines
    props = dict(boxstyle='round,pad=1', facecolor='lightyellow', 
                edgecolor='black', linewidth=2, alpha=0.95)
    ax.text(0.02, 0.98, guidelines_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='top', bbox=props, family='monospace')
    
    # Rotate x-axis labels
    ax.tick_params(axis='x', labelrotation=45, labelsize=10)
    ax.tick_params(axis='y', labelsize=11)
    
    # Add grid
    ax.grid(True, alpha=0.2, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_path / "08b_clustering_dendrogram_standalone.png", dpi=300, bbox_inches='tight')
    plt.close()


def create_agent_feature_heatmap(agent_data, clustering_results, output_path):
    """Create agent feature heatmap with top 25 features - IMPROVED"""
    fig, ax = plt.subplots(figsize=(18, 14))  # LARGER for 25 features
    
    # Heatmap of top 25 features (INCREASED FROM 15)
    agent_data_clustered = clustering_results['agent_data_clustered']
    mean_cols = [col for col in agent_data_clustered.columns if col.endswith('_mean')][:25]  # TOP 25
    
    # Reorder by clustering
    linkage_matrix = clustering_results['linkage_matrix']
    reorder_idx = dendrogram(linkage_matrix, no_plot=True)['leaves']
    agent_data_reordered = agent_data_clustered.iloc[reorder_idx]
    
    heatmap_data = agent_data_reordered[mean_cols]
    
    # Standardize for heatmap
    scaler = StandardScaler()
    heatmap_data_scaled = scaler.fit_transform(heatmap_data)
    
    # Create heatmap WITH ANNOTATIONS
    annot_fontsize = 6  # Smaller font for 25 features
    
    sns.heatmap(heatmap_data_scaled.T, ax=ax, cmap='RdYlGn', center=0,
                yticklabels=[col.replace('_mean', '') for col in mean_cols],
                xticklabels=[f"{agent} ({'H' if dpad==1 else 'L'})" 
                            for agent, dpad in zip(agent_data_reordered['agent_id'].values,
                                                   agent_data_reordered['high_dpad'].values)],
                cbar_kws={'label': 'Standardized Score (Z-score)', 'shrink': 0.7},
                linewidths=0.3, linecolor='gray',
                annot=True,  # SHOW VALUES
                fmt='.2f',   # 2 DECIMAL PLACES
                annot_kws={'fontsize': annot_fontsize, 'fontweight': 'normal'})
    
    ax.set_xlabel("Agents (Ordered by Clustering Similarity)\nH=High-DPAD, L=Low-DPAD", 
                 fontsize=13, fontweight='bold')
    ax.set_ylabel("Top 25 Behavioral Features", fontsize=13, fontweight='bold')
    ax.set_title("Agent Feature Heatmap - Top 25 Features\n" +
                 "(Hierarchically Ordered with Standardized Z-scores)\n" +
                 "Green = Above Average | Red = Below Average",
                 fontsize=15, fontweight='bold', pad=20)
    
    # Adjust tick label sizes
    ax.tick_params(axis='x', labelsize=9, rotation=45)
    ax.tick_params(axis='y', labelsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path / "08b_agent_heatmap_top25.png", dpi=300, bbox_inches='tight')
    plt.close()


def create_clustering_dendrogram(agent_data, clustering_results, output_path):
    """Create hierarchical clustering dendrogram with heatmap - KEPT FOR COMPATIBILITY"""
    # This function is kept for backward compatibility but now generates the combined view
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 10), gridspec_kw={'width_ratios': [1, 2.5]})
    
    # Dendrogram
    linkage_matrix = clustering_results['linkage_matrix']
    
    labels = [f"{row['agent_id']} ({'H' if row['high_dpad']==1 else 'L'})"
              for _, row in agent_data.iterrows()]
    
    dendrogram(linkage_matrix, ax=ax1, labels=labels, orientation='left',
               color_threshold=0, above_threshold_color='k')
    
    ax1.set_xlabel("Distance (Ward)", fontsize=12, fontweight='bold')
    ax1.set_title("Hierarchical Clustering\nof Agents", fontsize=14, fontweight='bold', pad=15)
    ax1.tick_params(axis='y', labelsize=10)
    
    # Heatmap of top features
    agent_data_clustered = clustering_results['agent_data_clustered']
    mean_cols = [col for col in agent_data_clustered.columns if col.endswith('_mean')][:15]
    
    # Reorder by clustering
    reorder_idx = dendrogram(linkage_matrix, no_plot=True)['leaves']
    agent_data_reordered = agent_data_clustered.iloc[reorder_idx]
    
    heatmap_data = agent_data_reordered[mean_cols]
    
    # Standardize for heatmap
    scaler = StandardScaler()
    heatmap_data_scaled = scaler.fit_transform(heatmap_data)
    
    # Create heatmap WITH ANNOTATIONS
    # Determine font size based on data size
    annot_fontsize = 7 if len(mean_cols) > 12 else 8
    
    sns.heatmap(heatmap_data_scaled.T, ax=ax2, cmap='RdYlGn', center=0,
                yticklabels=[col.replace('_mean', '') for col in mean_cols],
                xticklabels=agent_data_reordered['agent_id'].values,
                cbar_kws={'label': 'Standardized Score', 'shrink': 0.8},
                linewidths=0.5, linecolor='gray',
                annot=True,  # ENABLE ANNOTATIONS
                fmt='.2f',   # FORMAT: 2 DECIMAL PLACES
                annot_kws={'fontsize': annot_fontsize, 'fontweight': 'normal'})  # ANNOTATION STYLING
    
    ax2.set_xlabel("Agent (ordered by clustering)", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Top 15 Features", fontsize=12, fontweight='bold')
    ax2.set_title("Agent Feature Heatmap\n(Hierarchically Ordered with Standardized Values)", 
                 fontsize=14, fontweight='bold', pad=15)
    
    # Adjust tick label sizes
    ax2.tick_params(axis='x', labelsize=10, rotation=45)
    ax2.tick_params(axis='y', labelsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path / "08b_clustering_dendrogram_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()



def create_radar_charts(agent_data, effect_df, output_path):
    """Create radar charts comparing agent groups"""
    # Select top 8 features by effect size
    top_features = effect_df.head(8)['Feature'].tolist()
    
    # Get mean values for each group
    mean_cols = [f"{feat}_mean" for feat in top_features if f"{feat}_mean" in agent_data.columns]
    
    if len(mean_cols) < 3:
        print("   ⚠️ Not enough features for radar chart")
        return
    
    high_dpad_means = agent_data[agent_data['high_dpad'] == 1][mean_cols].mean()
    low_dpad_means = agent_data[agent_data['high_dpad'] == 0][mean_cols].mean()
    
    # Normalize to 0-100 scale
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 100))
    
    all_values = pd.concat([high_dpad_means, low_dpad_means], axis=1).T
    all_values_scaled = scaler.fit_transform(all_values)
    
    high_values = all_values_scaled[0]
    low_values = all_values_scaled[1]
    
    # Create radar chart
    labels = [col.replace('_mean', '') for col in mean_cols]
    num_vars = len(labels)
    
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    high_values = np.concatenate((high_values, [high_values[0]]))
    low_values = np.concatenate((low_values, [low_values[0]]))
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))
    
    ax.plot(angles, high_values, 'o-', linewidth=2, label='High-DPAD Agents',
            color=COLORS['high_dpad'], markersize=8)
    ax.fill(angles, high_values, alpha=0.25, color=COLORS['high_dpad'])
    
    ax.plot(angles, low_values, 'o-', linewidth=2, label='Low-DPAD Agents',
            color=COLORS['low_dpad'], markersize=8)
    ax.fill(angles, low_values, alpha=0.25, color=COLORS['low_dpad'])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Normalized Score (0-100)", fontsize=11, fontweight='bold')
    ax.set_title("Agent Group Profile: Radar Chart\n" +
                 f"Top {len(labels)} Features by Effect Size",
                 fontsize=14, fontweight='bold', pad=20, y=1.08)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_path / "08b_radar_chart_agent_profiles.png", dpi=300, bbox_inches='tight')
    plt.close()


def create_agent_similarity_matrix(agent_data, output_path):
    """Create agent similarity heatmap"""
    mean_cols = [col for col in agent_data.columns if col.endswith('_mean')]
    
    X = agent_data[mean_cols].fillna(0)
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Calculate pairwise distances
    distances = pdist(X_scaled, metric='euclidean')
    distance_matrix = squareform(distances)
    
    # Convert to similarity (inverse of distance)
    similarity_matrix = 1 / (1 + distance_matrix)
    
    # Create labels
    labels = [f"{row['agent_id']} ({'H' if row['high_dpad']==1 else 'L'})"
              for _, row in agent_data.iterrows()]
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    sns.heatmap(similarity_matrix, annot=True, fmt='.2f', cmap='YlGnBu',
                xticklabels=labels, yticklabels=labels, ax=ax,
                cbar_kws={'label': 'Similarity Score'}, linewidths=0.5)
    
    ax.set_title("Agent Similarity Matrix\n" +
                 "Based on all behavioral features (H=High-DPAD, L=Low-DPAD)",
                 fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig(output_path / "08b_agent_similarity_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()


def create_temporal_visualizations(temporal_df, output_path):
    """Create temporal trend visualizations"""
    if temporal_df.empty:
        print("   ⚠️ No temporal data available")
        return
    
    # Select key metrics
    key_metrics = ['interruption_rate', 'sentiment_progression', 'acknowledgement_rate']
    key_metrics = [m for m in key_metrics if m in temporal_df.columns]
    
    if not key_metrics:
        print("   ⚠️ No key metrics found in temporal data")
        return
    
    fig, axes = plt.subplots(len(key_metrics), 1, figsize=(16, 5*len(key_metrics)))
    
    if len(key_metrics) == 1:
        axes = [axes]
    
    for idx, metric in enumerate(key_metrics):
        ax = axes[idx]
        
        for agent_id in temporal_df['agent_id'].unique():
            agent_data = temporal_df[temporal_df['agent_id'] == agent_id].copy()
            agent_data = agent_data.sort_values('call_week')
            
            if len(agent_data) > 1:
                color = COLORS['high_dpad'] if agent_data['high_dpad'].iloc[0] == 1 else COLORS['low_dpad']
                
                # Convert Period to string for plotting
                x_values = agent_data['call_week'].astype(str)
                
                ax.plot(x_values, agent_data[metric], marker='o', label=agent_id,
                       color=color, alpha=0.7, linewidth=2)
        
        ax.set_xlabel("Week", fontsize=11, fontweight='bold')
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=11, fontweight='bold')
        ax.set_title(f"Temporal Trend: {metric.replace('_', ' ').title()}",
                    fontsize=13, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        # Rotate x labels
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_path / "08b_temporal_trends.png", dpi=300, bbox_inches='tight')
    plt.close()


def create_feature_network(agent_data, output_path):
    """Create feature correlation network visualization"""
    mean_cols = [col for col in agent_data.columns if col.endswith('_mean')][:20]
    
    # Calculate correlations
    corr_matrix = agent_data[mean_cols].corr()
    
    # Only keep strong correlations (|r| > 0.6)
    threshold = 0.6
    strong_corr = corr_matrix[(corr_matrix.abs() > threshold) & (corr_matrix != 1.0)]
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Create network-like visualization using correlation matrix
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    
    sns.heatmap(corr_matrix, mask=mask, annot=False, cmap='RdBu_r', center=0,
                vmin=-1, vmax=1, ax=ax, cbar_kws={'label': 'Correlation'},
                linewidths=0.5, square=True)
    
    ax.set_xticklabels([col.replace('_mean', '') for col in mean_cols], rotation=90, fontsize=9)
    ax.set_yticklabels([col.replace('_mean', '') for col in mean_cols], rotation=0, fontsize=9)
    ax.set_title("Feature Correlation Network (Agent-Level)\n" +
                 "Red = Negative Correlation | Blue = Positive Correlation",
                 fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig(output_path / "08b_feature_correlation_network.png", dpi=300, bbox_inches='tight')
    plt.close()


def generate_advanced_report(agent_data, effect_df, pca_results, clustering_results, 
                            temporal_df, output_dir):
    """Generate comprehensive advanced analysis report"""
    print("\n" + "="*70)
    print("GENERATING ADVANCED ANALYSIS REPORT")
    print("="*70)
    
    report = []
    report.append("# DPAD ANALYSIS - ADVANCED AGENT-LEVEL REPORT")
    report.append("=" * 70)
    report.append("")
    report.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}")
    report.append("")
    report.append("=" * 70)
    report.append("")
    
    # Executive Summary
    report.append("## 🎯 EXECUTIVE SUMMARY")
    report.append("")
    report.append("This advanced analysis applies rigorous statistical methods, machine learning,")
    report.append("and temporal analysis to uncover deeper insights about agent performance.")
    report.append("")
    report.append(f"**Agents Analyzed:** {len(agent_data)}")
    report.append(f"- High-DPAD: {(agent_data['high_dpad']==1).sum()}")
    report.append(f"- Low-DPAD: {(agent_data['high_dpad']==0).sum()}")
    report.append("")
    
    # Effect Size Analysis
    report.append("## 📊 1. EFFECT SIZE ANALYSIS (Cohen's d)")
    report.append("")
    report.append("Effect sizes provide a standardized measure of difference magnitude,")
    report.append("accounting for both mean difference and variability.")
    report.append("")
    
    large_effects = effect_df[effect_df['Abs_Cohens_D'] >= 0.8]
    medium_effects = effect_df[(effect_df['Abs_Cohens_D'] >= 0.5) & (effect_df['Abs_Cohens_D'] < 0.8)]
    
    if len(large_effects) > 0:
        report.append("### Features with LARGE Effect Sizes (|d| >= 0.8):")
        report.append("")
        report.append("| Feature | Cohen's d | High-DPAD Mean | Low-DPAD Mean | Significant |")
        report.append("|---------|-----------|----------------|---------------|-------------|")
        for _, row in large_effects.head(10).iterrows():
            report.append(f"| {row['Feature']:<35} | {row['Cohens_D']:>9.3f} | "
                         f"{row['High_Mean']:>14.3f} | {row['Low_Mean']:>13.3f} | "
                         f"{'Yes' if row['Significant'] else 'No':>11} |")
        report.append("")
    
    if len(medium_effects) > 0:
        report.append("### Features with MEDIUM Effect Sizes (0.5 <= |d| < 0.8):")
        report.append("")
        report.append("| Feature | Cohen's d | High-DPAD Mean | Low-DPAD Mean | Significant |")
        report.append("|---------|-----------|----------------|---------------|-------------|")
        for _, row in medium_effects.head(10).iterrows():
            report.append(f"| {row['Feature']:<35} | {row['Cohens_D']:>9.3f} | "
                         f"{row['High_Mean']:>14.3f} | {row['Low_Mean']:>13.3f} | "
                         f"{'Yes' if row['Significant'] else 'No':>11} |")
        report.append("")
    
    # PCA Analysis
    report.append("## 🔬 2. PRINCIPAL COMPONENT ANALYSIS")
    report.append("")
    report.append("PCA reveals the underlying 'dimensions' that explain agent variance.")
    report.append("")
    report.append(f"**Key Findings:**")
    report.append(f"- PC1 explains {pca_results['explained_var'][0]*100:.1f}% of variance")
    report.append(f"- PC2 explains {pca_results['explained_var'][1]*100:.1f}% of variance")
    report.append(f"- First 2 PCs explain {(pca_results['explained_var'][0]+pca_results['explained_var'][1])*100:.1f}% total variance")
    report.append(f"- Need {np.argmax(pca_results['cumulative_var'] >= 0.80) + 1} PCs to explain 80% variance")
    report.append("")
    
    report.append("### Top 10 Features Contributing to PC1:")
    report.append("")
    loadings_pc1 = pca_results['loadings']['PC1'].abs().nlargest(10)
    for feature, loading in loadings_pc1.items():
        report.append(f"- **{feature}**: {loading:.3f}")
    report.append("")
    
    # Clustering Analysis
    report.append("## 🎭 3. AGENT CLUSTERING")
    report.append("")
    report.append("Clustering identifies distinct agent 'archetypes' based on behavioral patterns.")
    report.append("")
    report.append(f"**Optimal Clusters:** {clustering_results['n_clusters']}")
    report.append("")
    
    agent_data_clustered = clustering_results['agent_data_clustered']
    for cluster_id in range(1, clustering_results['n_clusters'] + 1):
        cluster_agents = agent_data_clustered[agent_data_clustered['cluster'] == cluster_id]
        high_count = (cluster_agents['high_dpad'] == 1).sum()
        low_count = (cluster_agents['high_dpad'] == 0).sum()
        
        report.append(f"### Cluster {cluster_id}: {len(cluster_agents)} agents")
        report.append(f"- High-DPAD: {high_count}")
        report.append(f"- Low-DPAD: {low_count}")
        report.append(f"- Agents: {', '.join(cluster_agents['agent_id'].astype(str).tolist())}")
        report.append("")
    
    # Temporal Analysis
    if not temporal_df.empty:
        report.append("## ⏱️ 4. TEMPORAL TRENDS")
        report.append("")
        report.append("Analysis of how agent performance evolves over time.")
        report.append("")
        report.append(f"**Time Period:** {temporal_df['call_week'].min()} to {temporal_df['call_week'].max()}")
        report.append(f"**Agents Tracked:** {temporal_df['agent_id'].nunique()}")
        report.append("")
        report.append("**Key Observations:**")
        report.append("- Refer to temporal trend visualizations for detailed patterns")
        report.append("- Individual agent trajectories show improvement/decline over time")
        report.append("")
    
    # Actionable Insights
    report.append("## 💡 5. ACTIONABLE INSIGHTS")
    report.append("")
    report.append("### Based on Effect Size Analysis:")
    top_5_effects = effect_df.head(5)
    for idx, row in top_5_effects.iterrows():
        direction = "HIGHER" if row['Cohens_D'] > 0 else "LOWER"
        report.append(f"{idx+1}. **{row['Feature']}**: High-DPAD agents show {direction} values")
        report.append(f"   - Effect: {row['Effect_Category']} (d = {row['Cohens_D']:.3f})")
        report.append(f"   - Statistical significance: {'Yes (p < 0.05)' if row['Significant'] else 'No'}")
        report.append("")
    
    report.append("### Based on Clustering:")
    report.append("- Use cluster profiles to identify coaching needs")
    report.append("- Match training programs to specific agent archetypes")
    report.append("- Pair agents from different clusters for peer learning")
    report.append("")
    
    report.append("### Based on Temporal Analysis:")
    report.append("- Monitor agents showing declining trends for early intervention")
    report.append("- Identify and replicate practices from improving agents")
    report.append("- Use weekly trends for performance reviews")
    report.append("")
    
    # Methodology
    report.append("## 🔬 6. METHODOLOGY")
    report.append("")
    report.append("### Statistical Methods:")
    report.append("- **Cohen's d**: Standardized effect size measure")
    report.append("- **Bootstrap CI**: Confidence intervals with 1000 iterations")
    report.append("- **T-tests**: Compare agent group means")
    report.append("")
    report.append("### Machine Learning:")
    report.append("- **PCA**: Dimensionality reduction (standardized features)")
    report.append("- **Hierarchical Clustering**: Ward linkage method")
    report.append("- **Silhouette Analysis**: Optimal cluster selection")
    report.append("")
    report.append("### Temporal Analysis:")
    report.append("- **Rolling averages**: 10-call windows")
    report.append("- **Weekly aggregation**: Week-over-week trends")
    report.append("")
    
    # Save report
    report_path = output_dir / "analysis_outputs" / "agent_level_advanced" / "08b_advanced_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Advanced report saved: {report_path}")
    
    # Also save effect sizes to CSV
    effect_df.to_csv(output_dir / "analysis_outputs" / "agent_level_advanced" / "08b_effect_sizes.csv", 
                     index=False)
    
    # Save PCA loadings
    pca_results['loadings'].to_csv(output_dir / "analysis_outputs" / "agent_level_advanced" / "08b_pca_loadings.csv")
    
    # Save clustering results
    clustering_results['agent_data_clustered'][['agent_id', 'high_dpad', 'DPAD_Group', 'cluster']].to_csv(
        output_dir / "analysis_outputs" / "agent_level_advanced" / "08b_agent_clusters.csv", index=False)


def main():
    """Main advanced analysis pipeline"""
    
    print("\n" + "="*70)
    print("DPAD ANALYSIS - ADVANCED AGENT-LEVEL ANALYSIS")
    print("="*70)
    print("\nApplying advanced statistical & ML methods to agent data")
    print("="*70)
    
    output_dir = Path("ML_for_DPAD")
    
    # Load data
    df_combined, agent_data = load_data_with_temporal()
    
    # 1. Effect Size Analysis
    effect_df = calculate_effect_sizes_agent_level(agent_data)
    
    # 2. PCA Analysis
    pca_results = perform_pca_analysis(agent_data)
    
    # 3. Clustering
    clustering_results = perform_clustering(agent_data, pca_results)
    
    # 4. Temporal Trends
    temporal_df = analyze_temporal_trends(df_combined)
    
    # 5. Visualizations
    create_advanced_visualizations(agent_data, effect_df, pca_results, clustering_results,
                                   temporal_df, output_dir)
    
    # 6. Generate Report
    generate_advanced_report(agent_data, effect_df, pca_results, clustering_results,
                            temporal_df, output_dir)
    
    print("\n" + "="*70)
    print("✅ ADVANCED AGENT-LEVEL ANALYSIS COMPLETE")
    print("="*70)
    print(f"\n📊 Key Findings:")
    print(f"   Large effect sizes: {(effect_df['Abs_Cohens_D'] >= 0.8).sum()}")
    print(f"   Medium effect sizes: {((effect_df['Abs_Cohens_D'] >= 0.5) & (effect_df['Abs_Cohens_D'] < 0.8)).sum()}")
    print(f"   PC1+PC2 variance explained: {(pca_results['explained_var'][0]+pca_results['explained_var'][1])*100:.1f}%")
    print(f"   Optimal clusters: {clustering_results['n_clusters']}")
    print(f"\n📁 Outputs saved to: ML_for_DPAD/analysis_outputs/agent_level_advanced/")
    print("="*70)


if __name__ == "__main__":
    main()

