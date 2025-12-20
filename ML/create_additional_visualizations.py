"""
ADDITIONAL DETAILED VISUALIZATIONS
Creates additional insightful visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("CREATING ADDITIONAL DETAILED VISUALIZATIONS")
print("="*100)

# Load data
df_short = pd.read_csv('Less_than_4.88_mnt..csv')
df_long = pd.read_csv('greater_than_4.88_mnt..csv')

df_short['call_duration_group'] = 'Short (<4.88 min)'
df_long['call_duration_group'] = 'Long (>4.88 min)'

df_combined = pd.concat([df_short, df_long], ignore_index=True)

# Load analysis results
df_numeric_results = pd.read_csv('analysis_outputs/numeric_variables_tests.csv')
combined_importance = pd.read_csv('analysis_outputs/combined_feature_importance.csv')

# ==================================================================================
# VISUALIZATION 5: Distribution Comparison for Top Variables
# ==================================================================================
print("\n5. Creating visualization: Distribution Comparisons...")

# Get top 6 most important numeric variables
top_vars_for_dist = combined_importance.head(12)
top_numeric_vars = []

for var in top_vars_for_dist['Variable']:
    if var in df_combined.select_dtypes(include=[np.number]).columns:
        top_numeric_vars.append(var)
    if len(top_numeric_vars) == 6:
        break

if len(top_numeric_vars) > 0:
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    colors = ['#FF6B6B', '#4ECDC4']
    
    for idx, var in enumerate(top_numeric_vars):
        ax = axes[idx]
        
        # Create violin plot with box plot overlay
        parts = ax.violinplot([df_short[var].dropna(), df_long[var].dropna()],
                              positions=[0, 1], showmeans=True, showmedians=True)
        
        # Color the violins
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(colors[i])
            pc.set_alpha(0.7)
        
        # Add box plots
        bp = ax.boxplot([df_short[var].dropna(), df_long[var].dropna()],
                       positions=[0, 1], widths=0.15, patch_artist=True,
                       boxprops=dict(facecolor='white', alpha=0.8),
                       medianprops=dict(color='red', linewidth=2))
        
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Short', 'Long'], fontsize=11)
        ax.set_ylabel('Value', fontsize=10, fontweight='bold')
        ax.set_title(f'{var}', fontsize=11, fontweight='bold', pad=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add mean values as text
        short_mean = df_short[var].mean()
        long_mean = df_long[var].mean()
        ax.text(0, ax.get_ylim()[1] * 0.95, f'μ={short_mean:.2f}', 
               ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.text(1, ax.get_ylim()[1] * 0.95, f'μ={long_mean:.2f}', 
               ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    plt.suptitle('Distribution Comparison: Top 6 Numeric Variables (Short vs Long Calls)', 
                fontsize=15, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('analysis_outputs/viz_05_distribution_comparison.png', dpi=300, bbox_inches='tight')
    print("   [OK] Saved: viz_05_distribution_comparison.png")
    plt.close()

# ==================================================================================
# VISUALIZATION 6: Percentage Differences Heatmap
# ==================================================================================
print("\n6. Creating visualization: Percentage Differences Heatmap...")

# Get top 30 significant variables
top_30_numeric = df_numeric_results.nsmallest(30, 'P_Value')

fig, ax = plt.subplots(figsize=(14, 12))

# Prepare data for heatmap
heatmap_data = top_30_numeric[['Variable', 'Short_Mean', 'Long_Mean', 'Pct_Difference']].copy()
heatmap_data = heatmap_data.set_index('Variable')

# Create custom colormap
cmap = sns.diverging_palette(10, 130, as_cmap=True)

# Create heatmap
sns.heatmap(heatmap_data[['Pct_Difference']].T, annot=False, fmt='.1f', 
           cmap=cmap, center=0, cbar_kws={'label': 'Percentage Difference (%)'}, 
           linewidths=0.5, ax=ax, vmin=-100, vmax=100)

ax.set_xlabel('Variables', fontsize=12, fontweight='bold')
ax.set_ylabel('', fontsize=12)
ax.set_title('Percentage Differences: Long vs Short Calls (Top 30 Variables)', 
            fontsize=14, fontweight='bold', pad=20)

# Rotate x labels
plt.xticks(rotation=90, ha='right', fontsize=10)
plt.yticks(rotation=0, fontsize=11)

plt.tight_layout()
plt.savefig('analysis_outputs/viz_06_percentage_differences.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: viz_06_percentage_differences.png")
plt.close()

# ==================================================================================
# VISUALIZATION 7: Statistical Significance Overview
# ==================================================================================
print("\n7. Creating visualization: Statistical Significance Overview...")

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Count significant variables by p-value threshold
p_thresholds = [0.001, 0.01, 0.05, 0.1]
numeric_sig_counts = []
categorical_sig_counts = []

for threshold in p_thresholds:
    numeric_sig_counts.append((df_numeric_results['P_Value'] < threshold).sum())
    try:
        df_cat = pd.read_csv('analysis_outputs/categorical_variables_tests.csv')
        categorical_sig_counts.append((df_cat['P_Value'] < threshold).sum())
    except:
        categorical_sig_counts.append(0)

# Plot 1: Significance counts
ax1 = axes[0]
x = np.arange(len(p_thresholds))
width = 0.35

bars1 = ax1.bar(x - width/2, numeric_sig_counts, width, label='Numeric Variables',
               color='#45B7D1', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax1.bar(x + width/2, categorical_sig_counts, width, label='Categorical Variables',
               color='#98D8C8', alpha=0.8, edgecolor='black', linewidth=1.5)

ax1.set_xlabel('P-Value Threshold', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of Significant Variables', fontsize=12, fontweight='bold')
ax1.set_title('Statistical Significance by Threshold', fontsize=13, fontweight='bold', pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(['p < 0.001', 'p < 0.01', 'p < 0.05', 'p < 0.1'], fontsize=11)
ax1.legend(fontsize=11)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Plot 2: Effect size distribution
ax2 = axes[1]
effect_sizes = df_numeric_results['Cohens_D'].abs()
bins = [0, 0.2, 0.5, 0.8, effect_sizes.max() + 0.1]
labels = ['Negligible\n(<0.2)', 'Small\n(0.2-0.5)', 'Medium\n(0.5-0.8)', 'Large\n(>0.8)']
effect_counts = pd.cut(effect_sizes, bins=bins, labels=labels).value_counts().sort_index()

colors_effect = ['#F7DC6F', '#98D8C8', '#45B7D1', '#FF6B6B']
bars3 = ax2.bar(range(len(effect_counts)), effect_counts.values, color=colors_effect,
               alpha=0.8, edgecolor='black', linewidth=1.5)

ax2.set_xlabel('Effect Size Category', fontsize=12, fontweight='bold')
ax2.set_ylabel('Number of Variables', fontsize=12, fontweight='bold')
ax2.set_title("Effect Size Distribution (Cohen's D)", fontsize=13, fontweight='bold', pad=15)
ax2.set_xticks(range(len(effect_counts)))
ax2.set_xticklabels(labels, fontsize=11)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# Add value labels
for bar in bars3:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.suptitle('Statistical Analysis Overview', fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('analysis_outputs/viz_07_statistical_overview.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: viz_07_statistical_overview.png")
plt.close()

# ==================================================================================
# VISUALIZATION 8: Top 10 Variables - Detailed Comparison
# ==================================================================================
print("\n8. Creating visualization: Top 10 Variables Detailed Comparison...")

top_10_vars = combined_importance.head(10)['Variable'].tolist()

# Filter to get only numeric variables that exist
top_10_numeric = [v for v in top_10_vars if v in df_combined.select_dtypes(include=[np.number]).columns][:10]

if len(top_10_numeric) > 0:
    fig, axes = plt.subplots(5, 2, figsize=(16, 20))
    axes = axes.flatten()
    
    for idx, var in enumerate(top_10_numeric):
        ax = axes[idx]
        
        # Get data
        short_data = df_short[var].dropna()
        long_data = df_long[var].dropna()
        
        # Create histogram with KDE
        ax.hist(short_data, bins=30, alpha=0.6, label='Short Calls', 
               color='#FF6B6B', edgecolor='black', density=True)
        ax.hist(long_data, bins=30, alpha=0.6, label='Long Calls', 
               color='#4ECDC4', edgecolor='black', density=True)
        
        # Add KDE
        try:
            from scipy.stats import gaussian_kde
            if len(short_data) > 1:
                kde_short = gaussian_kde(short_data)
                x_short = np.linspace(short_data.min(), short_data.max(), 100)
                ax.plot(x_short, kde_short(x_short), 'r-', linewidth=2, alpha=0.8)
            
            if len(long_data) > 1:
                kde_long = gaussian_kde(long_data)
                x_long = np.linspace(long_data.min(), long_data.max(), 100)
                ax.plot(x_long, kde_long(x_long), 'b-', linewidth=2, alpha=0.8)
        except:
            pass
        
        ax.set_xlabel('Value', fontsize=10, fontweight='bold')
        ax.set_ylabel('Density', fontsize=10, fontweight='bold')
        ax.set_title(f'{var}', fontsize=11, fontweight='bold', pad=10)
        ax.legend(fontsize=9, loc='upper right')
        ax.grid(alpha=0.3, linestyle='--')
        
        # Add statistics text
        stats_text = f"Short: μ={short_data.mean():.2f}, σ={short_data.std():.2f}\n"
        stats_text += f"Long: μ={long_data.mean():.2f}, σ={long_data.std():.2f}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=8,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('Distribution Analysis: Top 10 Most Important Variables', 
                fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('analysis_outputs/viz_08_top10_detailed_distributions.png', dpi=300, bbox_inches='tight')
    print("   [OK] Saved: viz_08_top10_detailed_distributions.png")
    plt.close()

print("\n" + "="*100)
print("ADDITIONAL VISUALIZATIONS COMPLETE")
print("="*100)

