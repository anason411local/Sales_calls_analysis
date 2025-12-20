"""
BEAUTIFUL VISUALIZATIONS
Creates comprehensive visual analysis of the data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# Set beautiful style
plt.style.use('seaborn-v0_8-darkgrid')
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
sns.set_palette(colors)

print("="*100)
print("CREATING VISUALIZATIONS")
print("="*100)

# Load results
df_numeric_results = pd.read_csv('analysis_outputs/numeric_variables_tests.csv')
df_categorical_results = pd.read_csv('analysis_outputs/categorical_variables_tests.csv')
df_correlation = pd.read_csv('analysis_outputs/correlation_analysis.csv')
feature_importance_rf = pd.read_csv('analysis_outputs/feature_importance_random_forest.csv')
feature_importance_gb = pd.read_csv('analysis_outputs/feature_importance_gradient_boosting.csv')
combined_importance = pd.read_csv('analysis_outputs/combined_feature_importance.csv')

# ==================================================================================
# VISUALIZATION 1: Top Significant Numeric Variables
# ==================================================================================
print("\n1. Creating visualization: Top Significant Numeric Variables...")

fig, axes = plt.subplots(2, 1, figsize=(16, 12))

# Top 20 by p-value
top_numeric = df_numeric_results.nsmallest(20, 'P_Value')

# Plot 1: Mean differences
ax1 = axes[0]
x_pos = np.arange(len(top_numeric))
colors_bars = ['#4ECDC4' if diff > 0 else '#FF6B6B' for diff in top_numeric['Difference']]

bars = ax1.barh(x_pos, top_numeric['Difference'], color=colors_bars, alpha=0.8, edgecolor='black')
ax1.set_yticks(x_pos)
ax1.set_yticklabels(top_numeric['Variable'], fontsize=10)
ax1.set_xlabel('Mean Difference (Long - Short)', fontsize=12, fontweight='bold')
ax1.set_title('Top 20 Numeric Variables: Mean Differences Between Long and Short Calls', 
              fontsize=14, fontweight='bold', pad=20)
ax1.axvline(x=0, color='black', linestyle='--', linewidth=1)
ax1.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, top_numeric['Difference'])):
    ax1.text(val + (0.02 if val > 0 else -0.02), i, f'{val:.2f}', 
             va='center', ha='left' if val > 0 else 'right', fontsize=9)

# Plot 2: Effect sizes (Cohen's D)
ax2 = axes[1]
top_effect = df_numeric_results.nlargest(20, 'Cohens_D', keep='all')
top_effect = top_effect.iloc[:20]  # Limit to 20

x_pos2 = np.arange(len(top_effect))
colors_effect = ['#45B7D1' if d > 0 else '#FFA07A' for d in top_effect['Cohens_D']]

bars2 = ax2.barh(x_pos2, top_effect['Cohens_D'], color=colors_effect, alpha=0.8, edgecolor='black')
ax2.set_yticks(x_pos2)
ax2.set_yticklabels(top_effect['Variable'], fontsize=10)
ax2.set_xlabel("Cohen's D (Effect Size)", fontsize=12, fontweight='bold')
ax2.set_title("Top 20 Numeric Variables by Effect Size (Cohen's D)", 
              fontsize=14, fontweight='bold', pad=20)
ax2.axvline(x=0, color='black', linestyle='--', linewidth=1)
ax2.axvline(x=0.5, color='orange', linestyle=':', linewidth=1, alpha=0.5, label='Medium Effect')
ax2.axvline(x=0.8, color='red', linestyle=':', linewidth=1, alpha=0.5, label='Large Effect')
ax2.axvline(x=-0.5, color='orange', linestyle=':', linewidth=1, alpha=0.5)
ax2.axvline(x=-0.8, color='red', linestyle=':', linewidth=1, alpha=0.5)
ax2.legend(loc='lower right')
ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_outputs/viz_01_numeric_variables_significance.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: viz_01_numeric_variables_significance.png")
plt.close()

# ==================================================================================
# VISUALIZATION 2: Correlation Heatmap
# ==================================================================================
print("\n2. Creating visualization: Correlation Analysis...")

fig = plt.figure(figsize=(16, 10))

# Top 30 correlations
top_corr = df_correlation.nlargest(30, 'Abs_Correlation')

# Create bar plot with dual information
x_pos = np.arange(len(top_corr))
colors_corr = ['#4ECDC4' if corr > 0 else '#FF6B6B' for corr in top_corr['Correlation']]

plt.barh(x_pos, top_corr['Correlation'], color=colors_corr, alpha=0.8, edgecolor='black', linewidth=1.5)
plt.yticks(x_pos, top_corr['Variable'], fontsize=11)
plt.xlabel('Point-Biserial Correlation with Call Duration Group', fontsize=13, fontweight='bold')
plt.title('Top 30 Variables: Correlation with Call Duration (>4.88 min vs <4.88 min)', 
          fontsize=15, fontweight='bold', pad=20)
plt.axvline(x=0, color='black', linestyle='-', linewidth=2)
plt.grid(axis='x', alpha=0.4, linestyle='--')

# Add significance markers
for i, (corr, p_val) in enumerate(zip(top_corr['Correlation'], top_corr['P_Value'])):
    marker = '***' if p_val < 0.001 else ('**' if p_val < 0.01 else ('*' if p_val < 0.05 else ''))
    if marker:
        plt.text(corr + (0.01 if corr > 0 else -0.01), i, marker,
                va='center', ha='left' if corr > 0 else 'right', fontsize=12, fontweight='bold')

# Add legend
plt.text(0.98, 0.02, '*** p<0.001  ** p<0.01  * p<0.05', 
         transform=plt.gca().transAxes, fontsize=10,
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
         verticalalignment='bottom', horizontalalignment='right')

plt.tight_layout()
plt.savefig('analysis_outputs/viz_02_correlation_analysis.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: viz_02_correlation_analysis.png")
plt.close()

# ==================================================================================
# VISUALIZATION 3: Feature Importance Comparison
# ==================================================================================
print("\n3. Creating visualization: Feature Importance Methods Comparison...")

fig, axes = plt.subplots(1, 3, figsize=(20, 10))

# Random Forest
ax1 = axes[0]
top_rf = feature_importance_rf.head(20)
ax1.barh(np.arange(len(top_rf)), top_rf['Importance'], color='#45B7D1', alpha=0.8, edgecolor='black')
ax1.set_yticks(np.arange(len(top_rf)))
ax1.set_yticklabels(top_rf['Variable'], fontsize=10)
ax1.set_xlabel('Importance Score', fontsize=11, fontweight='bold')
ax1.set_title('Random Forest\nFeature Importance', fontsize=13, fontweight='bold', pad=15)
ax1.grid(axis='x', alpha=0.3)
ax1.invert_yaxis()

# Gradient Boosting
ax2 = axes[1]
top_gb = feature_importance_gb.head(20)
ax2.barh(np.arange(len(top_gb)), top_gb['Importance'], color='#98D8C8', alpha=0.8, edgecolor='black')
ax2.set_yticks(np.arange(len(top_gb)))
ax2.set_yticklabels(top_gb['Variable'], fontsize=10)
ax2.set_xlabel('Importance Score', fontsize=11, fontweight='bold')
ax2.set_title('Gradient Boosting\nFeature Importance', fontsize=13, fontweight='bold', pad=15)
ax2.grid(axis='x', alpha=0.3)
ax2.invert_yaxis()

# Combined Score
ax3 = axes[2]
top_combined = combined_importance.head(20)
ax3.barh(np.arange(len(top_combined)), top_combined['Combined_Score'], 
         color='#F7DC6F', alpha=0.8, edgecolor='black')
ax3.set_yticks(np.arange(len(top_combined)))
ax3.set_yticklabels(top_combined['Variable'], fontsize=10)
ax3.set_xlabel('Combined Score', fontsize=11, fontweight='bold')
ax3.set_title('Combined Ranking\n(RF + GB + Correlation)', fontsize=13, fontweight='bold', pad=15)
ax3.grid(axis='x', alpha=0.3)
ax3.invert_yaxis()

plt.suptitle('Feature Importance: Comparison of Methods (Top 20)', 
             fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('analysis_outputs/viz_03_feature_importance_comparison.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: viz_03_feature_importance_comparison.png")
plt.close()

# ==================================================================================
# VISUALIZATION 4: Top Variables Combined Analysis
# ==================================================================================
print("\n4. Creating visualization: Top Variables Combined Analysis...")

fig = plt.figure(figsize=(18, 12))
gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

# Get top 15 from combined ranking
top_vars = combined_importance.head(15)

# Plot 1: Combined scores
ax1 = fig.add_subplot(gs[0, :])
x_pos = np.arange(len(top_vars))
bars = ax1.bar(x_pos, top_vars['Combined_Score'], color='#FF6B6B', alpha=0.8, 
               edgecolor='black', linewidth=1.5)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(top_vars['Variable'], rotation=45, ha='right', fontsize=11)
ax1.set_ylabel('Combined Importance Score', fontsize=12, fontweight='bold')
ax1.set_title('Top 15 Most Important Variables (Combined Ranking)', 
              fontsize=14, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.4, linestyle='--')

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 2: Method comparison for top variables
ax2 = fig.add_subplot(gs[1, 0])
top_10 = combined_importance.head(10)
x = np.arange(len(top_10))
width = 0.25

ax2.barh(x - width, top_10['RF_Importance_Norm'], width, label='Random Forest', 
         color='#45B7D1', alpha=0.8, edgecolor='black')
ax2.barh(x, top_10['GB_Importance_Norm'], width, label='Gradient Boosting',
         color='#98D8C8', alpha=0.8, edgecolor='black')
ax2.barh(x + width, top_10['Correlation_Norm'], width, label='Correlation',
         color='#F7DC6F', alpha=0.8, edgecolor='black')

ax2.set_yticks(x)
ax2.set_yticklabels(top_10['Variable'], fontsize=10)
ax2.set_xlabel('Normalized Score', fontsize=11, fontweight='bold')
ax2.set_title('Top 10 Variables: Method Comparison', fontsize=12, fontweight='bold', pad=10)
ax2.legend(loc='lower right', fontsize=10)
ax2.grid(axis='x', alpha=0.3)
ax2.invert_yaxis()

# Plot 3: Correlation direction for top variables
ax3 = fig.add_subplot(gs[1, 1])

# Get correlation values for top 10 variables
top_10_vars_list = top_10['Variable'].tolist()
corr_values = []
for var in top_10_vars_list:
    corr_row = df_correlation[df_correlation['Variable'] == var]
    if not corr_row.empty:
        corr_values.append(corr_row['Correlation'].iloc[0])
    else:
        corr_values.append(0)

colors_dir = ['#4ECDC4' if c > 0 else '#FF6B6B' for c in corr_values]

bars3 = ax3.barh(np.arange(len(top_10)), corr_values, 
                 color=colors_dir, alpha=0.8, edgecolor='black')
ax3.set_yticks(np.arange(len(top_10)))
ax3.set_yticklabels(top_10['Variable'], fontsize=10)
ax3.set_xlabel('Correlation Coefficient', fontsize=11, fontweight='bold')
ax3.set_title('Top 10 Variables: Correlation Direction', fontsize=12, fontweight='bold', pad=10)
ax3.axvline(x=0, color='black', linestyle='-', linewidth=2)
ax3.grid(axis='x', alpha=0.3)
ax3.invert_yaxis()

plt.suptitle('Comprehensive Analysis: Top Important Variables', 
             fontsize=16, fontweight='bold', y=0.99)
plt.savefig('analysis_outputs/viz_04_top_variables_combined.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: viz_04_top_variables_combined.png")
plt.close()

print("\n" + "="*100)
print("VISUALIZATION COMPLETE - All files saved to analysis_outputs/")
print("="*100)

