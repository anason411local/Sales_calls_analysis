"""
2ND LEVEL ANALYSIS - NUMERICAL BINNING/BUCKETING ANALYSIS
Analyzing which ranges/buckets of important numerical variables contribute most to longer calls
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("2ND LEVEL ANALYSIS - NUMERICAL BINNING & BUCKETING")
print("="*100)

# Load data
df_combined = pd.read_csv('analysis_outputs/enhanced_combined_data.csv')
df_numeric_results = pd.read_csv('analysis_outputs/enhanced_numeric_variables_tests.csv')

# Get top 20 most important numeric variables
top_numeric = df_numeric_results.nsmallest(20, 'P_Value')['Variable'].tolist()

print(f"\nAnalyzing {len(top_numeric)} most important numerical variables")
print("-" * 100)

# ==================================================================================
# BIN EACH NUMERICAL VARIABLE AND ANALYZE
# ==================================================================================

binning_results = []

for var in top_numeric:
    print(f"\nAnalyzing: {var}")
    
    if var not in df_combined.columns:
        continue
    
    # Get the variable data
    data = df_combined[[var, 'call_duration_group']].dropna()
    
    if len(data) < 10:
        continue
    
    # Determine binning strategy based on distribution
    var_data = data[var]
    
    # Calculate statistics
    var_min = var_data.min()
    var_max = var_data.max()
    var_mean = var_data.mean()
    var_median = var_data.median()
    var_std = var_data.std()
    
    # Create bins
    # Use quantile-based binning for better distribution
    try:
        if len(var_data.unique()) <= 10:
            # For discrete variables with few values, use actual values
            bins = sorted(var_data.unique())
            if len(bins) > 1:
                bins = [-np.inf] + list(bins) + [np.inf]
                labels = [f"{bins[i]:.1f}" for i in range(len(bins)-1)]
            else:
                continue
        else:
            # For continuous variables, use quantiles
            bins = [var_data.quantile(q) for q in [0, 0.25, 0.5, 0.75, 1.0]]
            bins = sorted(set(bins))  # Remove duplicates
            
            if len(bins) <= 2:
                # If not enough unique bins, use fixed number
                bins = 5
                labels = [f'Q{i+1}' for i in range(5)]
            else:
                labels = []
                for i in range(len(bins)-1):
                    labels.append(f"{bins[i]:.1f}-{bins[i+1]:.1f}")
        
        # Create bins
        if isinstance(bins, int):
            data['bin'] = pd.cut(data[var], bins=bins, labels=labels if 'labels' in locals() else None, include_lowest=True)
        else:
            data['bin'] = pd.cut(data[var], bins=bins, labels=labels, include_lowest=True, duplicates='drop')
        
        # Analyze each bin
        for bin_label in data['bin'].unique():
            if pd.isna(bin_label):
                continue
            
            bin_data = data[data['bin'] == bin_label]
            
            count_short = (bin_data['call_duration_group'] == 0).sum()
            count_long = (bin_data['call_duration_group'] == 1).sum()
            total_count = len(bin_data)
            
            if total_count > 0:
                pct_long = (count_long / total_count) * 100
                pct_short = (count_short / total_count) * 100
                
                # Importance score
                importance_score = abs(pct_long - 50)
                
                # Direction
                if pct_long > pct_short:
                    direction = 'Favors Long Calls'
                elif pct_short > pct_long:
                    direction = 'Favors Short Calls'
                else:
                    direction = 'Neutral'
                
                binning_results.append({
                    'Variable': var,
                    'Bin_Range': str(bin_label),
                    'Count_Short': count_short,
                    'Count_Long': count_long,
                    'Total_Count': total_count,
                    'Pct_Short': pct_short,
                    'Pct_Long': pct_long,
                    'Importance_Score': importance_score,
                    'Direction': direction,
                    'Bin_Mean': bin_data[var].mean()
                })
        
        print(f"  Created {len(data['bin'].unique())} bins")
    
    except Exception as e:
        print(f"  Error binning {var}: {e}")
        continue

# Create DataFrame
df_binning = pd.DataFrame(binning_results)

# Sort by importance score
df_binning = df_binning.sort_values('Importance_Score', ascending=False)

# Save results
df_binning.to_csv('analysis_outputs/numerical_binning_analysis.csv', index=False)

print("\n" + "="*100)
print("TOP 30 MOST IMPORTANT NUMERICAL BINS/RANGES")
print("="*100)

display_cols = ['Variable', 'Bin_Range', 'Count_Short', 'Count_Long', 'Pct_Long', 'Direction']
print(df_binning[display_cols].head(30).to_string(index=False))

# ==================================================================================
# CREATE VISUALIZATIONS FOR TOP VARIABLES
# ==================================================================================
print("\n" + "="*100)
print("CREATING BINNING VISUALIZATIONS")
print("="*100)

# Get top 6 variables for visualization
top_6_vars_for_viz = []
seen_vars = set()
for idx, row in df_binning.iterrows():
    if row['Variable'] not in seen_vars:
        top_6_vars_for_viz.append(row['Variable'])
        seen_vars.add(row['Variable'])
    if len(top_6_vars_for_viz) == 6:
        break

fig, axes = plt.subplots(3, 2, figsize=(16, 18))
axes = axes.flatten()

for idx, var in enumerate(top_6_vars_for_viz):
    ax = axes[idx]
    
    # Get binning data for this variable
    var_bins = df_binning[df_binning['Variable'] == var].copy()
    var_bins = var_bins.sort_values('Bin_Mean')
    
    # Create stacked bar chart
    x = np.arange(len(var_bins))
    
    bars1 = ax.bar(x, var_bins['Count_Short'], label='Short Calls', 
                  color='#FF6B6B', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x, var_bins['Count_Long'], bottom=var_bins['Count_Short'], 
                  label='Long Calls', color='#4ECDC4', alpha=0.8, edgecolor='black')
    
    ax.set_xticks(x)
    ax.set_xticklabels([str(br)[:15] for br in var_bins['Bin_Range']], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Count', fontsize=10, fontweight='bold')
    ax.set_title(f'{var}\nDistribution by Bins', fontsize=11, fontweight='bold', pad=10)
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

plt.suptitle('Numerical Variable Binning Analysis: Short vs Long Calls', 
            fontsize=15, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('analysis_outputs/num_viz_01_binning_distribution.png', dpi=300, bbox_inches='tight')
print("\n[OK] Saved: num_viz_01_binning_distribution.png")
plt.close()

# Create percentage visualization
fig, axes = plt.subplots(3, 2, figsize=(16, 18))
axes = axes.flatten()

for idx, var in enumerate(top_6_vars_for_viz):
    ax = axes[idx]
    
    # Get binning data for this variable
    var_bins = df_binning[df_binning['Variable'] == var].copy()
    var_bins = var_bins.sort_values('Bin_Mean')
    
    # Create percentage plot
    x = np.arange(len(var_bins))
    
    ax.plot(x, var_bins['Pct_Long'], marker='o', linewidth=2.5, markersize=10,
           color='#4ECDC4', label='% Long Calls')
    ax.axhline(y=50, color='gray', linestyle='--', linewidth=2, label='50% Threshold')
    
    ax.set_xticks(x)
    ax.set_xticklabels([str(br)[:15] for br in var_bins['Bin_Range']], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('% Long Calls', fontsize=10, fontweight='bold')
    ax.set_title(f'{var}\n% Long Calls by Bin', fontsize=11, fontweight='bold', pad=10)
    ax.set_ylim([0, 100])
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    
    # Shade areas above 50%
    ax.fill_between(x, 50, var_bins['Pct_Long'], where=(var_bins['Pct_Long'] >= 50),
                   alpha=0.3, color='green', label='Favors Long')
    ax.fill_between(x, var_bins['Pct_Long'], 50, where=(var_bins['Pct_Long'] < 50),
                   alpha=0.3, color='red', label='Favors Short')

plt.suptitle('Numerical Variable Binning Analysis: % Long Calls Trend', 
            fontsize=15, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('analysis_outputs/num_viz_02_binning_percentage_trend.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: num_viz_02_binning_percentage_trend.png")
plt.close()

print("\n" + "="*100)
print("NUMERICAL BINNING ANALYSIS COMPLETE")
print("="*100)
print(f"\n[OK] Saved: numerical_binning_analysis.csv")
print(f"Total bins analyzed: {len(df_binning)}")

