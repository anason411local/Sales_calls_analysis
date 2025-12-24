"""
==============================================================================
COMPREHENSIVE AGENT COMPARISON: TOP vs WORST PERFORMER
==============================================================================

This script creates beautiful, interactive, and data-based visualizations
comparing the TOP agent (DARWINSANCHEZ24) vs WORST agent (ARTURODELEON).

Generates:
1. Executive Summary Dashboard
2. Performance Metrics Comparison
3. Variable Importance Differences
4. Call Pattern Analysis
5. Model Performance Comparison
6. Statistical Significance Comparison
7. SHAP Value Comparison
8. Actionable Insights Report

==============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*100)
print("COMPREHENSIVE AGENT COMPARISON ANALYSIS")
print("="*100)

# ==============================================================================
# LOAD ALL DATA FOR BOTH AGENTS
# ==============================================================================

print("\nLoading data for both agents...")

# Paths
top_path = Path('analysis_outputs/top_agent')
worst_path = Path('analysis_outputs/worst_agent')
output_path = Path('analysis_outputs/comparison')
output_path.mkdir(exist_ok=True)

# Load metadata
with open(top_path / '01_metadata.json', 'r') as f:
    top_meta = json.load(f)
with open(worst_path / '01_metadata.json', 'r') as f:
    worst_meta = json.load(f)

# Load importance data
top_imp = pd.read_csv(top_path / '03_importance_combined.csv')
worst_imp = pd.read_csv(worst_path / '03_importance_combined.csv')

# Load correlation data
top_corr = pd.read_csv(top_path / '02_correlation_with_target.csv')
worst_corr = pd.read_csv(worst_path / '02_correlation_with_target.csv')

# Load statistical tests
top_stats = pd.read_csv(top_path / '04_statistical_tests_combined.csv')
worst_stats = pd.read_csv(worst_path / '04_statistical_tests_combined.csv')

# Load SHAP importance
top_shap = pd.read_csv(top_path / '05_shap_importance.csv')
worst_shap = pd.read_csv(worst_path / '05_shap_importance.csv')

# Load model metrics
with open(top_path / '03_model_metrics.json', 'r') as f:
    top_model_metrics = json.load(f)
with open(worst_path / '03_model_metrics.json', 'r') as f:
    worst_model_metrics = json.load(f)

# Load raw data
top_data = pd.read_csv(top_path / '01_combined_original.csv')
worst_data = pd.read_csv(worst_path / '01_combined_original.csv')

print(f"[OK] Loaded data for {top_meta['agent_name']} ({top_meta['total_records']} calls)")
print(f"[OK] Loaded data for {worst_meta['agent_name']} ({worst_meta['total_records']} calls)")

# ==============================================================================
# VIZ 1: EXECUTIVE SUMMARY DASHBOARD
# ==============================================================================

print("\n" + "="*100)
print("CREATING EXECUTIVE SUMMARY DASHBOARD")
print("="*100)

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)

# Title
fig.suptitle('AGENT PERFORMANCE COMPARISON: TOP vs WORST PERFORMER\n' +
             f'{top_meta["agent_name"]} vs {worst_meta["agent_name"]}',
             fontsize=20, fontweight='bold', y=0.98)

# --- ROW 1: KEY METRICS ---

# 1.1: Call Volume & Success Rate
ax1 = fig.add_subplot(gs[0, 0])
agents = ['TOP\n' + top_meta['agent_name'], 'WORST\n' + worst_meta['agent_name']]
total_calls = [top_meta['total_records'], worst_meta['total_records']]
long_call_pct = [
    top_meta['long_calls'] / top_meta['total_records'] * 100,
    worst_meta['long_calls'] / worst_meta['total_records'] * 100
]

x = np.arange(len(agents))
width = 0.35
bars1 = ax1.bar(x - width/2, total_calls, width, label='Total Calls', color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=2)
ax2 = ax1.twinx()
bars2 = ax2.bar(x + width/2, long_call_pct, width, label='Long Call %', color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=2)

ax1.set_ylabel('Total Calls', fontsize=11, fontweight='bold')
ax2.set_ylabel('Long Call %', fontsize=11, fontweight='bold')
ax1.set_title('Call Volume & Success Rate', fontsize=12, fontweight='bold', pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(agents, fontsize=9, fontweight='bold')
ax1.legend(loc='upper left', fontsize=9)
ax2.legend(loc='upper right', fontsize=9)
ax1.grid(alpha=0.3, axis='y')

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')
for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 1.2: Model Performance (ROC-AUC)
ax2 = fig.add_subplot(gs[0, 1])
models = ['Random\nForest', 'XGBoost']
top_roc = [
    top_model_metrics['random_forest_roc_auc_test'],
    top_model_metrics['xgboost_roc_auc_test']
]
worst_roc = [
    worst_model_metrics['random_forest_roc_auc_test'],
    worst_model_metrics['xgboost_roc_auc_test']
]

x = np.arange(len(models))
width = 0.35
bars1 = ax2.bar(x - width/2, top_roc, width, label='TOP Agent', color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=2)
bars2 = ax2.bar(x + width/2, worst_roc, width, label='WORST Agent', color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=2)

ax2.set_ylabel('ROC-AUC Score', fontsize=11, fontweight='bold')
ax2.set_title('Model Performance Comparison', fontsize=12, fontweight='bold', pad=10)
ax2.set_xticks(x)
ax2.set_xticklabels(models, fontsize=9, fontweight='bold')
ax2.legend(fontsize=9)
ax2.set_ylim([0.7, 1.0])
ax2.axhline(y=0.85, color='green', linestyle='--', linewidth=1, alpha=0.5, label='Good (0.85)')
ax2.grid(alpha=0.3, axis='y')

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# 1.3: Top 5 Variable Importance Comparison
ax3 = fig.add_subplot(gs[0, 2:])
top_vars = top_imp.head(5)
worst_vars = worst_imp.head(5)

# Get common variables
all_vars = list(set(top_vars['Variable'].tolist() + worst_vars['Variable'].tolist()))[:8]
top_scores = []
worst_scores = []

for var in all_vars:
    top_score = top_imp[top_imp['Variable'] == var]['Combined_Score'].values
    worst_score = worst_imp[worst_imp['Variable'] == var]['Combined_Score'].values
    top_scores.append(top_score[0] if len(top_score) > 0 else 0)
    worst_scores.append(worst_score[0] if len(worst_score) > 0 else 0)

y = np.arange(len(all_vars))
height = 0.35
bars1 = ax3.barh(y + height/2, top_scores, height, label='TOP Agent', color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax3.barh(y - height/2, worst_scores, height, label='WORST Agent', color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)

ax3.set_yticks(y)
ax3.set_yticklabels(all_vars, fontsize=9)
ax3.set_xlabel('Combined Importance Score', fontsize=11, fontweight='bold')
ax3.set_title('Top Variables: Importance Comparison', fontsize=12, fontweight='bold', pad=10)
ax3.legend(fontsize=9)
ax3.invert_yaxis()
ax3.grid(alpha=0.3, axis='x')

# Add value labels
for bar in bars1:
    width_val = bar.get_width()
    if width_val > 0:
        ax3.text(width_val, bar.get_y() + bar.get_height()/2.,
                f'{width_val:.3f}', ha='left', va='center', fontsize=8, fontweight='bold')
for bar in bars2:
    width_val = bar.get_width()
    if width_val > 0:
        ax3.text(width_val, bar.get_y() + bar.get_height()/2.,
                f'{width_val:.3f}', ha='left', va='center', fontsize=8, fontweight='bold')

# --- ROW 2: DETAILED COMPARISONS ---

# 2.1: Call Duration Distribution
ax4 = fig.add_subplot(gs[1, 0])
ax4.hist([top_data[top_data['target']==0]['TO_length_in_sec'], 
          top_data[top_data['target']==1]['TO_length_in_sec']],
         bins=20, label=['Short Calls', 'Long Calls'], color=['#FF6B6B', '#4ECDC4'],
         alpha=0.7, edgecolor='black', linewidth=1.5)
ax4.set_xlabel('Call Duration (seconds)', fontsize=10, fontweight='bold')
ax4.set_ylabel('Frequency', fontsize=10, fontweight='bold')
ax4.set_title(f'TOP Agent: Call Duration Distribution\n{top_meta["agent_name"]}',
             fontsize=11, fontweight='bold', pad=10)
ax4.legend(fontsize=8)
ax4.axvline(x=292.8, color='red', linestyle='--', linewidth=2, label='4.88 min threshold')
ax4.grid(alpha=0.3)

# 2.2: Call Duration Distribution (Worst)
ax5 = fig.add_subplot(gs[1, 1])
ax5.hist([worst_data[worst_data['target']==0]['TO_length_in_sec'],
          worst_data[worst_data['target']==1]['TO_length_in_sec']],
         bins=20, label=['Short Calls', 'Long Calls'], color=['#FF6B6B', '#4ECDC4'],
         alpha=0.7, edgecolor='black', linewidth=1.5)
ax5.set_xlabel('Call Duration (seconds)', fontsize=10, fontweight='bold')
ax5.set_ylabel('Frequency', fontsize=10, fontweight='bold')
ax5.set_title(f'WORST Agent: Call Duration Distribution\n{worst_meta["agent_name"]}',
             fontsize=11, fontweight='bold', pad=10)
ax5.legend(fontsize=8)
ax5.axvline(x=292.8, color='red', linestyle='--', linewidth=2, label='4.88 min threshold')
ax5.grid(alpha=0.3)

# 2.3: Correlation Strength Comparison
ax6 = fig.add_subplot(gs[1, 2:])
top_corr_top10 = top_corr.head(10)
worst_corr_top10 = worst_corr.head(10)

# Get common variables
all_corr_vars = list(set(top_corr_top10['Variable'].tolist() + worst_corr_top10['Variable'].tolist()))[:10]
top_corr_vals = []
worst_corr_vals = []

for var in all_corr_vars:
    top_val = top_corr[top_corr['Variable'] == var]['Abs_Correlation'].values
    worst_val = worst_corr[worst_corr['Variable'] == var]['Abs_Correlation'].values
    top_corr_vals.append(top_val[0] if len(top_val) > 0 else 0)
    worst_corr_vals.append(worst_val[0] if len(worst_val) > 0 else 0)

y = np.arange(len(all_corr_vars))
height = 0.35
bars1 = ax6.barh(y + height/2, top_corr_vals, height, label='TOP Agent', color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax6.barh(y - height/2, worst_corr_vals, height, label='WORST Agent', color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)

ax6.set_yticks(y)
ax6.set_yticklabels(all_corr_vars, fontsize=8)
ax6.set_xlabel('Absolute Correlation with Target', fontsize=10, fontweight='bold')
ax6.set_title('Correlation Strength Comparison', fontsize=11, fontweight='bold', pad=10)
ax6.legend(fontsize=8)
ax6.invert_yaxis()
ax6.grid(alpha=0.3, axis='x')

# --- ROW 3: KEY INSIGHTS ---

# 3.1: Statistical Significance
ax7 = fig.add_subplot(gs[2, 0])
sig_data = [
    [top_stats[top_stats['Significant'] == 'Yes'].shape[0], 
     worst_stats[worst_stats['Significant'] == 'Yes'].shape[0]],
    [top_stats[top_stats['Significant'] == 'No'].shape[0],
     worst_stats[worst_stats['Significant'] == 'No'].shape[0]]
]

x = np.arange(2)
width = 0.35
bars1 = ax7.bar(x - width/2, [sig_data[0][0], sig_data[1][0]], width, 
               label='TOP Agent', color=['#4ECDC4', '#FF6B6B'], alpha=0.8, edgecolor='black', linewidth=2)
bars2 = ax7.bar(x + width/2, [sig_data[0][1], sig_data[1][1]], width,
               label='WORST Agent', color=['#4ECDC4', '#FF6B6B'], alpha=0.6, edgecolor='black', linewidth=2)

ax7.set_ylabel('Number of Variables', fontsize=10, fontweight='bold')
ax7.set_title('Statistical Significance', fontsize=11, fontweight='bold', pad=10)
ax7.set_xticks(x)
ax7.set_xticklabels(['Significant\n(p<0.05)', 'Not Significant'], fontsize=9, fontweight='bold')
ax7.legend(['TOP Agent', 'WORST Agent'], fontsize=8)
ax7.grid(alpha=0.3, axis='y')

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax7.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# 3.2: SHAP Importance Top 5
ax8 = fig.add_subplot(gs[2, 1])
top_shap_top5 = top_shap.head(5)
worst_shap_top5 = worst_shap.head(5)

vars_shap = top_shap_top5['Variable'].tolist()
top_shap_vals = top_shap_top5['SHAP_Avg'].tolist()
worst_shap_vals = [worst_shap[worst_shap['Variable'] == var]['SHAP_Avg'].values[0] 
                   if var in worst_shap['Variable'].values else 0 for var in vars_shap]

y = np.arange(len(vars_shap))
height = 0.35
bars1 = ax8.barh(y + height/2, top_shap_vals, height, label='TOP', color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax8.barh(y - height/2, worst_shap_vals, height, label='WORST', color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)

ax8.set_yticks(y)
ax8.set_yticklabels(vars_shap, fontsize=8)
ax8.set_xlabel('SHAP Importance', fontsize=10, fontweight='bold')
ax8.set_title('SHAP: Top 5 Variables', fontsize=11, fontweight='bold', pad=10)
ax8.legend(fontsize=8)
ax8.invert_yaxis()
ax8.grid(alpha=0.3, axis='x')

# 3.3: Key Differences Summary (Text Box)
ax9 = fig.add_subplot(gs[2, 2:])
ax9.axis('off')

# Calculate key differences
long_call_diff = long_call_pct[0] - long_call_pct[1]
roc_diff = top_roc[0] - worst_roc[0]
top_discovery = top_data['total_discovery_questions'].mean()
worst_discovery = worst_data['total_discovery_questions'].mean()
discovery_diff = top_discovery - worst_discovery

summary_text = f"""
KEY DIFFERENCES: WHY TOP AGENT OUTPERFORMS

1. SUCCESS RATE
   • TOP Agent: {long_call_pct[0]:.1f}% long calls
   • WORST Agent: {long_call_pct[1]:.1f}% long calls
   • Difference: +{long_call_diff:.1f}% (TOP is better)

2. MODEL PREDICTABILITY
   • TOP Agent: {top_roc[0]:.3f} ROC-AUC
   • WORST Agent: {worst_roc[0]:.3f} ROC-AUC
   • Difference: +{roc_diff:.3f} (more predictable patterns)

3. DISCOVERY QUESTIONS
   • TOP Agent: {top_discovery:.1f} questions/call
   • WORST Agent: {worst_discovery:.1f} questions/call
   • Difference: +{discovery_diff:.1f} questions (TOP asks more)

4. VARIABLE IMPORTANCE
   • TOP Agent: {top_imp.iloc[0]['Variable']} (score: {top_imp.iloc[0]['Combined_Score']:.3f})
   • WORST Agent: {worst_imp.iloc[0]['Variable']} (score: {worst_imp.iloc[0]['Combined_Score']:.3f})

5. STATISTICAL SIGNIFICANCE
   • TOP Agent: {sig_data[0][0]} significant variables
   • WORST Agent: {sig_data[0][1]} significant variables
"""

ax9.text(0.05, 0.95, summary_text, transform=ax9.transAxes,
        fontsize=9, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8, edgecolor='black', linewidth=2))

plt.tight_layout()
plt.savefig(output_path / '08_executive_summary_dashboard.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: 08_executive_summary_dashboard.png")
plt.close()

# ==============================================================================
# VIZ 2: DETAILED VARIABLE IMPORTANCE COMPARISON
# ==============================================================================

print("\nCreating detailed variable importance comparison...")

fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('DETAILED VARIABLE IMPORTANCE COMPARISON\nTOP vs WORST Agent',
             fontsize=16, fontweight='bold')

# 2.1: Top 20 Variables - Side by Side
ax = axes[0, 0]
top20_vars = top_imp.head(20)['Variable'].tolist()
top20_scores_top = top_imp.head(20)['Combined_Score'].tolist()
top20_scores_worst = [worst_imp[worst_imp['Variable'] == var]['Combined_Score'].values[0]
                      if var in worst_imp['Variable'].values else 0 for var in top20_vars]

y = np.arange(len(top20_vars))
height = 0.4
bars1 = ax.barh(y + height/2, top20_scores_top, height, label='TOP Agent',
               color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1)
bars2 = ax.barh(y - height/2, top20_scores_worst, height, label='WORST Agent',
               color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1)

ax.set_yticks(y)
ax.set_yticklabels(top20_vars, fontsize=8)
ax.set_xlabel('Combined Importance Score', fontsize=10, fontweight='bold')
ax.set_title('Top 20 Variables by Importance (TOP Agent)', fontsize=11, fontweight='bold')
ax.legend(fontsize=9)
ax.invert_yaxis()
ax.grid(alpha=0.3, axis='x')

# 2.2: Importance Difference (Top - Worst)
ax = axes[0, 1]
importance_diff = [top20_scores_top[i] - top20_scores_worst[i] for i in range(len(top20_vars))]
colors = ['#4ECDC4' if diff > 0 else '#FF6B6B' for diff in importance_diff]

bars = ax.barh(y, importance_diff, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
ax.set_yticks(y)
ax.set_yticklabels(top20_vars, fontsize=8)
ax.set_xlabel('Importance Difference (TOP - WORST)', fontsize=10, fontweight='bold')
ax.set_title('Where TOP Agent Excels (Positive = Better)', fontsize=11, fontweight='bold')
ax.axvline(x=0, color='black', linestyle='-', linewidth=2)
ax.invert_yaxis()
ax.grid(alpha=0.3, axis='x')

# Add value labels
for i, (bar, val) in enumerate(zip(bars, importance_diff)):
    x_pos = val + (0.01 if val > 0 else -0.01)
    ax.text(x_pos, i, f'{val:+.3f}',
           va='center', ha='left' if val > 0 else 'right',
           fontsize=7, fontweight='bold')

# 2.3: Correlation Comparison
ax = axes[1, 0]
top_corr_sorted = top_corr.sort_values('Abs_Correlation', ascending=False).head(15)
vars_corr = top_corr_sorted['Variable'].tolist()
top_corr_vals = top_corr_sorted['Abs_Correlation'].tolist()
worst_corr_vals = [worst_corr[worst_corr['Variable'] == var]['Abs_Correlation'].values[0]
                   if var in worst_corr['Variable'].values else 0 for var in vars_corr]

y = np.arange(len(vars_corr))
height = 0.4
bars1 = ax.barh(y + height/2, top_corr_vals, height, label='TOP Agent',
               color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1)
bars2 = ax.barh(y - height/2, worst_corr_vals, height, label='WORST Agent',
               color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1)

ax.set_yticks(y)
ax.set_yticklabels(vars_corr, fontsize=8)
ax.set_xlabel('Absolute Correlation with Target', fontsize=10, fontweight='bold')
ax.set_title('Top 15 Correlations Comparison', fontsize=11, fontweight='bold')
ax.legend(fontsize=9)
ax.invert_yaxis()
ax.grid(alpha=0.3, axis='x')

# 2.4: SHAP Importance Comparison
ax = axes[1, 1]
top_shap_sorted = top_shap.sort_values('SHAP_Avg', ascending=False).head(15)
vars_shap = top_shap_sorted['Variable'].tolist()
top_shap_vals = top_shap_sorted['SHAP_Avg'].tolist()
worst_shap_vals = [worst_shap[worst_shap['Variable'] == var]['SHAP_Avg'].values[0]
                   if var in worst_shap['Variable'].values else 0 for var in vars_shap]

y = np.arange(len(vars_shap))
height = 0.4
bars1 = ax.barh(y + height/2, top_shap_vals, height, label='TOP Agent',
               color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1)
bars2 = ax.barh(y - height/2, worst_shap_vals, height, label='WORST Agent',
               color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1)

ax.set_yticks(y)
ax.set_yticklabels(vars_shap, fontsize=8)
ax.set_xlabel('Average SHAP Importance', fontsize=10, fontweight='bold')
ax.set_title('Top 15 SHAP Importance Comparison', fontsize=11, fontweight='bold')
ax.legend(fontsize=9)
ax.invert_yaxis()
ax.grid(alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig(output_path / '08_detailed_importance_comparison.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: 08_detailed_importance_comparison.png")
plt.close()

# ==============================================================================
# VIZ 3: CALL PATTERN ANALYSIS
# ==============================================================================

print("\nCreating call pattern analysis...")

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('CALL PATTERN ANALYSIS: TOP vs WORST Agent',
             fontsize=16, fontweight='bold')

# 3.1: Call Duration Box Plot
ax = axes[0, 0]
data_to_plot = [
    top_data[top_data['target']==0]['TO_length_in_sec'],
    top_data[top_data['target']==1]['TO_length_in_sec'],
    worst_data[worst_data['target']==0]['TO_length_in_sec'],
    worst_data[worst_data['target']==1]['TO_length_in_sec']
]
bp = ax.boxplot(data_to_plot, labels=['TOP\nShort', 'TOP\nLong', 'WORST\nShort', 'WORST\nLong'],
               patch_artist=True, showmeans=True)

colors = ['#FF6B6B', '#4ECDC4', '#FF6B6B', '#4ECDC4']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax.set_ylabel('Call Duration (seconds)', fontsize=10, fontweight='bold')
ax.set_title('Call Duration Distribution', fontsize=11, fontweight='bold')
ax.axhline(y=292.8, color='red', linestyle='--', linewidth=2, alpha=0.5, label='4.88 min')
ax.grid(alpha=0.3, axis='y')
ax.legend(fontsize=8)

# 3.2: Discovery Questions
ax = axes[0, 1]
if 'total_discovery_questions' in top_data.columns:
    data_to_plot = [
        top_data[top_data['target']==0]['total_discovery_questions'].dropna(),
        top_data[top_data['target']==1]['total_discovery_questions'].dropna(),
        worst_data[worst_data['target']==0]['total_discovery_questions'].dropna(),
        worst_data[worst_data['target']==1]['total_discovery_questions'].dropna()
    ]
    bp = ax.boxplot(data_to_plot, labels=['TOP\nShort', 'TOP\nLong', 'WORST\nShort', 'WORST\nLong'],
                   patch_artist=True, showmeans=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Number of Discovery Questions', fontsize=10, fontweight='bold')
    ax.set_title('Discovery Questions Pattern', fontsize=11, fontweight='bold')
    ax.grid(alpha=0.3, axis='y')

# 3.3: Customer Talk Percentage
ax = axes[0, 2]
if 'customer_talk_percentage' in top_data.columns:
    data_to_plot = [
        top_data[top_data['target']==0]['customer_talk_percentage'].dropna(),
        top_data[top_data['target']==1]['customer_talk_percentage'].dropna(),
        worst_data[worst_data['target']==0]['customer_talk_percentage'].dropna(),
        worst_data[worst_data['target']==1]['customer_talk_percentage'].dropna()
    ]
    bp = ax.boxplot(data_to_plot, labels=['TOP\nShort', 'TOP\nLong', 'WORST\nShort', 'WORST\nLong'],
                   patch_artist=True, showmeans=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Customer Talk %', fontsize=10, fontweight='bold')
    ax.set_title('Customer Engagement Pattern', fontsize=11, fontweight='bold')
    ax.grid(alpha=0.3, axis='y')

# 3.4: Call Disposition Distribution (TOP)
ax = axes[1, 0]
if 'TO_OMC_Disposiion' in top_data.columns:
    top_disp = top_data['TO_OMC_Disposiion'].value_counts().head(8)
    ax.barh(range(len(top_disp)), top_disp.values, color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_yticks(range(len(top_disp)))
    ax.set_yticklabels(top_disp.index, fontsize=9)
    ax.set_xlabel('Count', fontsize=10, fontweight='bold')
    ax.set_title(f'TOP Agent: Call Dispositions\n{top_meta["agent_name"]}', fontsize=11, fontweight='bold')
    ax.invert_yaxis()
    ax.grid(alpha=0.3, axis='x')
    
    # Add value labels
    for i, v in enumerate(top_disp.values):
        ax.text(v, i, f' {v}', va='center', fontsize=9, fontweight='bold')

# 3.5: Call Disposition Distribution (WORST)
ax = axes[1, 1]
if 'TO_OMC_Disposiion' in worst_data.columns:
    worst_disp = worst_data['TO_OMC_Disposiion'].value_counts().head(8)
    ax.barh(range(len(worst_disp)), worst_disp.values, color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_yticks(range(len(worst_disp)))
    ax.set_yticklabels(worst_disp.index, fontsize=9)
    ax.set_xlabel('Count', fontsize=10, fontweight='bold')
    ax.set_title(f'WORST Agent: Call Dispositions\n{worst_meta["agent_name"]}', fontsize=11, fontweight='bold')
    ax.invert_yaxis()
    ax.grid(alpha=0.3, axis='x')
    
    # Add value labels
    for i, v in enumerate(worst_disp.values):
        ax.text(v, i, f' {v}', va='center', fontsize=9, fontweight='bold')

# 3.6: Call Result Tag Comparison
ax = axes[1, 2]
if 'call_result_tag' in top_data.columns and 'call_result_tag' in worst_data.columns:
    top_tags = top_data['call_result_tag'].value_counts().head(5)
    worst_tags = worst_data['call_result_tag'].value_counts().head(5)
    
    all_tags = list(set(top_tags.index.tolist() + worst_tags.index.tolist()))[:6]
    top_counts = [top_tags.get(tag, 0) for tag in all_tags]
    worst_counts = [worst_tags.get(tag, 0) for tag in all_tags]
    
    x = np.arange(len(all_tags))
    width = 0.35
    bars1 = ax.bar(x - width/2, top_counts, width, label='TOP', color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, worst_counts, width, label='WORST', color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel('Count', fontsize=10, fontweight='bold')
    ax.set_title('Call Result Tags Comparison', fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([tag[:20] + '...' if len(tag) > 20 else tag for tag in all_tags], 
                       rotation=45, ha='right', fontsize=8)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(output_path / '08_call_pattern_analysis.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: 08_call_pattern_analysis.png")
plt.close()

# ==============================================================================
# VIZ 4: MODEL PERFORMANCE DEEP DIVE
# ==============================================================================

print("\nCreating model performance deep dive...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('MODEL PERFORMANCE DEEP DIVE: TOP vs WORST Agent',
             fontsize=16, fontweight='bold')

# 4.1: All Metrics Comparison - Random Forest
ax = axes[0, 0]
metrics = ['ROC-AUC', 'Accuracy', 'F1-Score']
top_rf_metrics = [
    top_model_metrics['random_forest_roc_auc_test'],
    top_model_metrics['random_forest_accuracy_test'],
    top_model_metrics['random_forest_f1_test']
]
worst_rf_metrics = [
    worst_model_metrics['random_forest_roc_auc_test'],
    worst_model_metrics['random_forest_accuracy_test'],
    worst_model_metrics['random_forest_f1_test']
]

x = np.arange(len(metrics))
width = 0.35
bars1 = ax.bar(x - width/2, top_rf_metrics, width, label='TOP Agent',
              color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=2)
bars2 = ax.bar(x + width/2, worst_rf_metrics, width, label='WORST Agent',
              color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=2)

ax.set_ylabel('Score', fontsize=10, fontweight='bold')
ax.set_title('Random Forest: All Metrics', fontsize=11, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=9, fontweight='bold')
ax.legend(fontsize=9)
ax.set_ylim([0.5, 1.0])
ax.grid(alpha=0.3, axis='y')

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{height:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
for bar in bars2:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{height:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

# 4.2: All Metrics Comparison - XGBoost
ax = axes[0, 1]
top_xgb_metrics = [
    top_model_metrics['xgboost_roc_auc_test'],
    top_model_metrics['xgboost_accuracy_test'],
    top_model_metrics['xgboost_f1_test']
]
worst_xgb_metrics = [
    worst_model_metrics['xgboost_roc_auc_test'],
    worst_model_metrics['xgboost_accuracy_test'],
    worst_model_metrics['xgboost_f1_test']
]

bars1 = ax.bar(x - width/2, top_xgb_metrics, width, label='TOP Agent',
              color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=2)
bars2 = ax.bar(x + width/2, worst_xgb_metrics, width, label='WORST Agent',
              color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=2)

ax.set_ylabel('Score', fontsize=10, fontweight='bold')
ax.set_title('XGBoost: All Metrics', fontsize=11, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=9, fontweight='bold')
ax.legend(fontsize=9)
ax.set_ylim([0.5, 1.0])
ax.grid(alpha=0.3, axis='y')

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{height:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
for bar in bars2:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{height:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

# 4.3: Train vs Test Performance (Overfitting Check)
ax = axes[0, 2]
models = ['RF\nTOP', 'RF\nWORST', 'XGB\nTOP', 'XGB\nWORST']
train_scores = [
    top_model_metrics['random_forest_roc_auc_train'],
    worst_model_metrics['random_forest_roc_auc_train'],
    top_model_metrics['xgboost_roc_auc_train'],
    worst_model_metrics['xgboost_roc_auc_train']
]
test_scores = [
    top_model_metrics['random_forest_roc_auc_test'],
    worst_model_metrics['random_forest_roc_auc_test'],
    top_model_metrics['xgboost_roc_auc_test'],
    worst_model_metrics['xgboost_roc_auc_test']
]

x = np.arange(len(models))
width = 0.35
bars1 = ax.bar(x - width/2, train_scores, width, label='Train',
              color='#95E1D3', alpha=0.8, edgecolor='black', linewidth=2)
bars2 = ax.bar(x + width/2, test_scores, width, label='Test',
              color='#F38181', alpha=0.8, edgecolor='black', linewidth=2)

ax.set_ylabel('ROC-AUC Score', fontsize=10, fontweight='bold')
ax.set_title('Overfitting Check (Train vs Test)', fontsize=11, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=8, fontweight='bold')
ax.legend(fontsize=9)
ax.set_ylim([0.7, 1.0])
ax.grid(alpha=0.3, axis='y')

# Add gap labels
for i, (train, test) in enumerate(zip(train_scores, test_scores)):
    gap = train - test
    ax.text(i, max(train, test) + 0.01, f'Gap:\n{gap:.3f}',
           ha='center', va='bottom', fontsize=7, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

# 4.4: Cross-Validation Scores
ax = axes[1, 0]
cv_scores = [
    top_model_metrics['random_forest_cv_mean'],
    worst_model_metrics['random_forest_cv_mean'],
    top_model_metrics['xgboost_cv_mean'],
    worst_model_metrics['xgboost_cv_mean']
]
cv_stds = [
    top_model_metrics['random_forest_cv_std'],
    worst_model_metrics['random_forest_cv_std'],
    top_model_metrics['xgboost_cv_std'],
    worst_model_metrics['xgboost_cv_std']
]

bars = ax.bar(x, cv_scores, color=['#4ECDC4', '#FF6B6B', '#4ECDC4', '#FF6B6B'],
             alpha=0.8, edgecolor='black', linewidth=2, yerr=cv_stds, capsize=5)

ax.set_ylabel('Mean ROC-AUC (5-Fold CV)', fontsize=10, fontweight='bold')
ax.set_title('Cross-Validation Performance', fontsize=11, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=8, fontweight='bold')
ax.set_ylim([0.7, 1.0])
ax.grid(alpha=0.3, axis='y')

# Add value labels
for bar, score, std in zip(bars, cv_scores, cv_stds):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{score:.3f}\n±{std:.3f}', ha='center', va='bottom', fontsize=7, fontweight='bold')

# 4.5: Performance Difference (TOP - WORST)
ax = axes[1, 1]
metrics_all = ['RF\nROC-AUC', 'RF\nAccuracy', 'RF\nF1', 'XGB\nROC-AUC', 'XGB\nAccuracy', 'XGB\nF1']
differences = [
    top_rf_metrics[0] - worst_rf_metrics[0],
    top_rf_metrics[1] - worst_rf_metrics[1],
    top_rf_metrics[2] - worst_rf_metrics[2],
    top_xgb_metrics[0] - worst_xgb_metrics[0],
    top_xgb_metrics[1] - worst_xgb_metrics[1],
    top_xgb_metrics[2] - worst_xgb_metrics[2]
]

colors = ['#4ECDC4' if diff > 0 else '#FF6B6B' for diff in differences]
bars = ax.bar(range(len(metrics_all)), differences, color=colors, alpha=0.8, edgecolor='black', linewidth=2)

ax.set_ylabel('Performance Difference (TOP - WORST)', fontsize=10, fontweight='bold')
ax.set_title('Where TOP Agent Excels', fontsize=11, fontweight='bold')
ax.set_xticks(range(len(metrics_all)))
ax.set_xticklabels(metrics_all, fontsize=8, fontweight='bold')
ax.axhline(y=0, color='black', linestyle='-', linewidth=2)
ax.grid(alpha=0.3, axis='y')

# Add value labels
for bar, diff in zip(bars, differences):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{diff:+.3f}', ha='center', va='bottom' if diff > 0 else 'top',
           fontsize=8, fontweight='bold')

# 4.6: Model Consistency (CV Std Dev)
ax = axes[1, 2]
consistency = [1/std if std > 0 else 0 for std in cv_stds]  # Lower std = higher consistency

bars = ax.bar(x, consistency, color=['#4ECDC4', '#FF6B6B', '#4ECDC4', '#FF6B6B'],
             alpha=0.8, edgecolor='black', linewidth=2)

ax.set_ylabel('Consistency Score (1/StdDev)', fontsize=10, fontweight='bold')
ax.set_title('Model Consistency\n(Higher = More Stable)', fontsize=11, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=8, fontweight='bold')
ax.grid(alpha=0.3, axis='y')

# Add value labels
for bar, score in zip(bars, consistency):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{score:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig(output_path / '08_model_performance_deepdive.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: 08_model_performance_deepdive.png")
plt.close()

# ==============================================================================
# GENERATE TEXT REPORT
# ==============================================================================

print("\n" + "="*100)
print("GENERATING COMPREHENSIVE TEXT REPORT")
print("="*100)

report = []
report.append("="*100)
report.append("COMPREHENSIVE AGENT COMPARISON REPORT")
report.append("TOP PERFORMER vs WORST PERFORMER")
report.append("="*100)
report.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append(f"\nTOP AGENT: {top_meta['agent_name']}")
report.append(f"WORST AGENT: {worst_meta['agent_name']}")

report.append("\n" + "="*100)
report.append("1. EXECUTIVE SUMMARY")
report.append("="*100)

report.append(f"\nCALL VOLUME:")
report.append(f"  TOP Agent: {top_meta['total_records']} total calls")
report.append(f"  WORST Agent: {worst_meta['total_records']} total calls")
report.append(f"  Difference: {top_meta['total_records'] - worst_meta['total_records']:+d} calls")

report.append(f"\nSUCCESS RATE (Long Calls %):")
report.append(f"  TOP Agent: {long_call_pct[0]:.1f}% ({top_meta['long_calls']}/{top_meta['total_records']})")
report.append(f"  WORST Agent: {long_call_pct[1]:.1f}% ({worst_meta['long_calls']}/{worst_meta['total_records']})")
report.append(f"  Difference: {long_call_diff:+.1f}% (TOP is better)")

report.append(f"\nMODEL PERFORMANCE (Random Forest ROC-AUC):")
report.append(f"  TOP Agent: {top_roc[0]:.3f}")
report.append(f"  WORST Agent: {worst_roc[0]:.3f}")
report.append(f"  Difference: {roc_diff:+.3f} (TOP is more predictable)")

report.append("\n" + "="*100)
report.append("2. TOP 10 MOST IMPORTANT VARIABLES")
report.append("="*100)

report.append("\nTOP AGENT:")
for i, row in top_imp.head(10).iterrows():
    report.append(f"  {i+1}. {row['Variable']}: {row['Combined_Score']:.4f}")

report.append("\nWORST AGENT:")
for i, row in worst_imp.head(10).iterrows():
    report.append(f"  {i+1}. {row['Variable']}: {row['Combined_Score']:.4f}")

report.append("\n" + "="*100)
report.append("3. KEY DIFFERENCES ANALYSIS")
report.append("="*100)

# Calculate key differences
report.append("\nDISCOVERY QUESTIONS:")
report.append(f"  TOP Agent Average: {top_discovery:.2f} questions per call")
report.append(f"  WORST Agent Average: {worst_discovery:.2f} questions per call")
report.append(f"  Difference: {discovery_diff:+.2f} questions (TOP asks more)")

report.append("\nSTATISTICAL SIGNIFICANCE:")
report.append(f"  TOP Agent: {sig_data[0][0]} significant variables (out of {len(top_stats)})")
report.append(f"  WORST Agent: {sig_data[0][1]} significant variables (out of {len(worst_stats)})")
report.append(f"  Difference: {sig_data[0][0] - sig_data[0][1]:+d} variables")

report.append("\n" + "="*100)
report.append("4. ACTIONABLE INSIGHTS")
report.append("="*100)

report.append("\nWHAT MAKES THE TOP AGENT SUCCESSFUL:")
report.append(f"  1. Asks {discovery_diff:.1f} more discovery questions per call")
report.append(f"  2. Achieves {long_call_diff:.1f}% higher long call rate")
report.append(f"  3. Has {roc_diff:.3f} better model predictability (more consistent patterns)")
report.append(f"  4. Shows {sig_data[0][0] - sig_data[0][1]} more statistically significant variables")
report.append(f"  5. Top variable importance: {top_imp.iloc[0]['Variable']} ({top_imp.iloc[0]['Combined_Score']:.3f})")

report.append("\nRECOMMENDATIONS FOR IMPROVEMENT:")
report.append("  1. Train agents to ask more discovery questions (target: 8+ per call)")
report.append("  2. Focus on buying signals identification and response")
report.append("  3. Improve call structure and pacing (reduce interruptions)")
report.append("  4. Enhance objection handling techniques")
report.append("  5. Implement TOP agent's successful patterns in training")

report.append("\n" + "="*100)
report.append("5. DETAILED METRICS COMPARISON")
report.append("="*100)

report.append("\nRANDOM FOREST PERFORMANCE:")
report.append(f"  TOP Agent:")
report.append(f"    - Test ROC-AUC: {top_model_metrics['random_forest_roc_auc_test']:.3f}")
report.append(f"    - Test Accuracy: {top_model_metrics['random_forest_accuracy_test']:.3f}")
report.append(f"    - Test F1-Score: {top_model_metrics['random_forest_f1_test']:.3f}")
report.append(f"    - CV Mean ROC-AUC: {top_model_metrics['random_forest_cv_mean']:.3f} ± {top_model_metrics['random_forest_cv_std']:.3f}")

report.append(f"  WORST Agent:")
report.append(f"    - Test ROC-AUC: {worst_model_metrics['random_forest_roc_auc_test']:.3f}")
report.append(f"    - Test Accuracy: {worst_model_metrics['random_forest_accuracy_test']:.3f}")
report.append(f"    - Test F1-Score: {worst_model_metrics['random_forest_f1_test']:.3f}")
report.append(f"    - CV Mean ROC-AUC: {worst_model_metrics['random_forest_cv_mean']:.3f} ± {worst_model_metrics['random_forest_cv_std']:.3f}")

report.append("\nXGBOOST PERFORMANCE:")
report.append(f"  TOP Agent:")
report.append(f"    - Test ROC-AUC: {top_model_metrics['xgboost_roc_auc_test']:.3f}")
report.append(f"    - Test Accuracy: {top_model_metrics['xgboost_accuracy_test']:.3f}")
report.append(f"    - Test F1-Score: {top_model_metrics['xgboost_f1_test']:.3f}")
report.append(f"    - CV Mean ROC-AUC: {top_model_metrics['xgboost_cv_mean']:.3f} ± {top_model_metrics['xgboost_cv_std']:.3f}")

report.append(f"  WORST Agent:")
report.append(f"    - Test ROC-AUC: {worst_model_metrics['xgboost_roc_auc_test']:.3f}")
report.append(f"    - Test Accuracy: {worst_model_metrics['xgboost_accuracy_test']:.3f}")
report.append(f"    - Test F1-Score: {worst_model_metrics['xgboost_f1_test']:.3f}")
report.append(f"    - CV Mean ROC-AUC: {worst_model_metrics['xgboost_cv_mean']:.3f} ± {worst_model_metrics['xgboost_cv_std']:.3f}")

report.append("\n" + "="*100)
report.append("END OF REPORT")
report.append("="*100)

# Save report
with open(output_path / '08_comprehensive_comparison_report.txt', 'w') as f:
    f.write('\n'.join(report))

print("[OK] Saved: 08_comprehensive_comparison_report.txt")

# ==============================================================================
# COMPLETION
# ==============================================================================

print("\n" + "="*100)
print("COMPREHENSIVE AGENT COMPARISON COMPLETE")
print("="*100)

print("\n[OK] Generated 4 comprehensive visualizations:")
print("  1. 08_executive_summary_dashboard.png - High-level overview")
print("  2. 08_detailed_importance_comparison.png - Variable importance deep dive")
print("  3. 08_call_pattern_analysis.png - Call patterns and behaviors")
print("  4. 08_model_performance_deepdive.png - ML model performance")

print("\n[OK] Generated comprehensive text report:")
print("  - 08_comprehensive_comparison_report.txt")

print(f"\n[OK] All outputs saved to: {output_path}")

print("\n" + "="*100)
print("KEY FINDINGS:")
print("="*100)
print(f"1. TOP agent ({top_meta['agent_name']}) has {long_call_diff:.1f}% higher success rate")
print(f"2. TOP agent asks {discovery_diff:.1f} more discovery questions per call")
print(f"3. TOP agent has {roc_diff:.3f} better model predictability")
print(f"4. TOP agent shows {sig_data[0][0] - sig_data[0][1]} more significant variables")
print(f"5. Most important variable for TOP: {top_imp.iloc[0]['Variable']}")
print("="*100)

