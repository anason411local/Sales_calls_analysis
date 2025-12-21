"""
STEP 5B: CORRELATION HEATMAPS
Creates correlation heatmaps for:
1. Short calls (<4.88 min)
2. Long calls (>4.88 min)
3. Combined dataset (all calls)

Shows correlations between all numeric features
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("CREATING CORRELATION HEATMAPS")
print("="*100)

# Load encoded data (all features are now numeric)
df_short = pd.read_csv('analysis_outputs/02_short_calls_encoded.csv')
df_long = pd.read_csv('analysis_outputs/02_long_calls_encoded.csv')
df_combined = pd.read_csv('analysis_outputs/02_combined_encoded.csv')

print(f"\nLoaded data:")
print(f"  Short: {df_short.shape}")
print(f"  Long: {df_long.shape}")
print(f"  Combined: {df_combined.shape}")

# Remove the label column for correlation
df_short_num = df_short.drop('call_duration_group', axis=1)
df_long_num = df_long.drop('call_duration_group', axis=1)
df_combined_num = df_combined.drop('call_duration_group', axis=1)

print(f"\nNumeric features: {df_short_num.shape[1]}")

# ==================================================================================
# HEATMAP 1: SHORT CALLS CORRELATION
# ==================================================================================

print("\n" + "="*100)
print("CREATING HEATMAP 1: SHORT CALLS (<4.88 min)")
print("="*100)

print("\nCalculating correlation matrix using SPEARMAN method...")
print("(Spearman captures non-linear monotonic relationships)")
corr_short = df_short_num.corr(method='spearman')

print(f"Correlation matrix shape: {corr_short.shape}")

# Save correlation matrix
corr_short.to_csv('analysis_outputs/correlation_matrix_short_calls.csv')
print("[OK] Saved: correlation_matrix_short_calls.csv")

# Create heatmap
fig, ax = plt.subplots(figsize=(24, 22))

# Create mask for upper triangle
mask = np.triu(np.ones_like(corr_short, dtype=bool))

# Create heatmap with values
sns.heatmap(corr_short, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax, annot_kws={'size': 5})

ax.set_title('CORRELATION HEATMAP: SHORT CALLS (<4.88 minutes)\n' + 
             f'Method: SPEARMAN (Non-Linear) | Features: {len(corr_short)} | Calls: {df_short.shape[0]:,}\n' +
             'RED = Positive Correlation | BLUE = Negative Correlation | WHITE = No Correlation\n' +
             'Only variables from Sections 1-6.6 included', 
             fontsize=18, fontweight='bold', pad=25)

plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_01_short_calls_correlation.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_01_short_calls_correlation.png")
plt.close()

# ==================================================================================
# HEATMAP 2: LONG CALLS CORRELATION
# ==================================================================================

print("\n" + "="*100)
print("CREATING HEATMAP 2: LONG CALLS (>4.88 min)")
print("="*100)

print("\nCalculating correlation matrix using SPEARMAN method...")
print("(Spearman captures non-linear monotonic relationships)")
corr_long = df_long_num.corr(method='spearman')

print(f"Correlation matrix shape: {corr_long.shape}")

# Save correlation matrix
corr_long.to_csv('analysis_outputs/correlation_matrix_long_calls.csv')
print("[OK] Saved: correlation_matrix_long_calls.csv")

# Create heatmap
fig, ax = plt.subplots(figsize=(24, 22))

mask = np.triu(np.ones_like(corr_long, dtype=bool))

sns.heatmap(corr_long, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax, annot_kws={'size': 5})

ax.set_title('CORRELATION HEATMAP: LONG CALLS (>4.88 minutes)\n' + 
             f'Method: SPEARMAN (Non-Linear) | Features: {len(corr_long)} | Calls: {df_long.shape[0]:,}\n' +
             'RED = Positive Correlation | BLUE = Negative Correlation | WHITE = No Correlation\n' +
             'Only variables from Sections 1-6.6 included', 
             fontsize=18, fontweight='bold', pad=25)

plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_02_long_calls_correlation.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_02_long_calls_correlation.png")
plt.close()

# ==================================================================================
# HEATMAP 3: COMBINED CALLS CORRELATION
# ==================================================================================

print("\n" + "="*100)
print("CREATING HEATMAP 3: COMBINED (All Calls)")
print("="*100)

print("\nCalculating correlation matrix using SPEARMAN method...")
print("(Spearman captures non-linear monotonic relationships)")
corr_combined = df_combined_num.corr(method='spearman')

print(f"Correlation matrix shape: {corr_combined.shape}")

# Save correlation matrix
corr_combined.to_csv('analysis_outputs/correlation_matrix_combined.csv')
print("[OK] Saved: correlation_matrix_combined.csv")

# Create heatmap
fig, ax = plt.subplots(figsize=(24, 22))

mask = np.triu(np.ones_like(corr_combined, dtype=bool))

sns.heatmap(corr_combined, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax, annot_kws={'size': 5})

ax.set_title('CORRELATION HEATMAP: COMBINED DATA (All Calls)\n' + 
             f'Method: SPEARMAN (Non-Linear) | Features: {len(corr_combined)} | Calls: {df_combined.shape[0]:,}\n' +
             'RED = Positive Correlation | BLUE = Negative Correlation | WHITE = No Correlation\n' +
             'Only variables from Sections 1-6.6 included', 
             fontsize=18, fontweight='bold', pad=25)

plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_03_combined_correlation.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_03_combined_correlation.png")
plt.close()

# ==================================================================================
# CORRELATION DIFFERENCES ANALYSIS
# ==================================================================================

print("\n" + "="*100)
print("CORRELATION DIFFERENCES: Short vs Long")
print("="*100)

print("\nCalculating correlation differences...")

# Compute difference
corr_diff = corr_long - corr_short

# Find largest differences
corr_diff_flat = corr_diff.values[np.triu_indices_from(corr_diff.values, k=1)]
indices = np.triu_indices_from(corr_diff.values, k=1)

differences = []
for i, j in zip(indices[0], indices[1]):
    diff = corr_diff.iloc[i, j]
    if abs(diff) > 0.1:  # Only significant differences
        differences.append({
            'Feature_1': corr_diff.index[i],
            'Feature_2': corr_diff.columns[j],
            'Corr_Short': corr_short.iloc[i, j],
            'Corr_Long': corr_long.iloc[i, j],
            'Difference': diff,
            'Abs_Difference': abs(diff)
        })

df_diff = pd.DataFrame(differences)
df_diff = df_diff.sort_values('Abs_Difference', ascending=False)

df_diff.to_csv('analysis_outputs/correlation_differences_short_vs_long.csv', index=False)
print("[OK] Saved: correlation_differences_short_vs_long.csv")

if len(df_diff) > 0:
    print("\nTop 20 Correlation Differences (Short vs Long):")
    print("-" * 100)
    print(df_diff[['Feature_1', 'Feature_2', 'Corr_Short', 'Corr_Long', 'Difference']].head(20).to_string(index=False))
else:
    print("\nNo major correlation differences found (threshold: 0.1)")

# ==================================================================================
# STRONGEST CORRELATIONS SUMMARY
# ==================================================================================

print("\n" + "="*100)
print("STRONGEST CORRELATIONS SUMMARY")
print("="*100)

def get_top_correlations(corr_matrix, name, n=20):
    """Extract top n correlations from a correlation matrix"""
    # Get upper triangle indices
    indices = np.triu_indices_from(corr_matrix.values, k=1)
    
    correlations = []
    for i, j in zip(indices[0], indices[1]):
        correlations.append({
            'Dataset': name,
            'Feature_1': corr_matrix.index[i],
            'Feature_2': corr_matrix.columns[j],
            'Correlation': corr_matrix.iloc[i, j],
            'Abs_Correlation': abs(corr_matrix.iloc[i, j])
        })
    
    df_corr = pd.DataFrame(correlations)
    return df_corr.nlargest(n, 'Abs_Correlation')

# Get top correlations for each dataset
top_short = get_top_correlations(corr_short, 'Short Calls', 20)
top_long = get_top_correlations(corr_long, 'Long Calls', 20)
top_combined = get_top_correlations(corr_combined, 'Combined', 20)

# Combine all
all_top_corr = pd.concat([top_short, top_long, top_combined], ignore_index=True)
all_top_corr.to_csv('analysis_outputs/top_correlations_all_datasets.csv', index=False)
print("\n[OK] Saved: top_correlations_all_datasets.csv")

print("\nTop 10 Correlations - SHORT CALLS:")
print("-" * 100)
display_cols = ['Feature_1', 'Feature_2', 'Correlation']
print(top_short[display_cols].head(10).to_string(index=False))

print("\nTop 10 Correlations - LONG CALLS:")
print("-" * 100)
print(top_long[display_cols].head(10).to_string(index=False))

print("\nTop 10 Correlations - COMBINED:")
print("-" * 100)
print(top_combined[display_cols].head(10).to_string(index=False))

# ==================================================================================
# CREATE DIFFERENCE HEATMAP (Bonus Visualization)
# ==================================================================================

print("\n" + "="*100)
print("CREATING BONUS: CORRELATION DIFFERENCE HEATMAP")
print("="*100)

fig, ax = plt.subplots(figsize=(24, 22))

mask = np.triu(np.ones_like(corr_diff, dtype=bool))

sns.heatmap(corr_diff, mask=mask, annot=False, cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8, "label": "Correlation Difference"},
            vmin=-0.5, vmax=0.5, ax=ax)

ax.set_title('CORRELATION DIFFERENCE HEATMAP: Long Calls - Short Calls\n' + 
             f'Method: SPEARMAN (Non-Linear) | Features: {len(corr_diff)}\n' +
             'RED = Stronger in Long Calls | BLUE = Stronger in Short Calls | WHITE = No Difference\n' +
             'Shows behavioral changes between successful vs unsuccessful calls', 
             fontsize=18, fontweight='bold', pad=25)

plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_04_correlation_difference.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_04_correlation_difference.png")
plt.close()

print("\n" + "="*100)
print("CORRELATION HEATMAPS COMPLETE")
print("="*100)

print("\nFILES CREATED:")
print("  CSV Files:")
print("    - correlation_matrix_short_calls.csv")
print("    - correlation_matrix_long_calls.csv")
print("    - correlation_matrix_combined.csv")
print("    - correlation_differences_short_vs_long.csv")
print("    - top_correlations_all_datasets.csv")
print("\n  Heatmap Visualizations:")
print("    - heatmap_01_short_calls_correlation.png")
print("    - heatmap_02_long_calls_correlation.png")
print("    - heatmap_03_combined_correlation.png")
print("    - heatmap_04_correlation_difference.png (BONUS)")

print("\n" + "="*100)
print("HOW TO READ CORRELATION HEATMAPS:")
print("="*100)
print("\n  - Values range from -1 to +1")
print("  - +1 = Perfect positive correlation (variables move together)")
print("  - -1 = Perfect negative correlation (variables move opposite)")
print("  - 0 = No correlation")
print("  - |r| > 0.7 = Strong correlation")
print("  - |r| 0.3-0.7 = Moderate correlation")
print("  - |r| < 0.3 = Weak correlation")
print("\n  Colors:")
print("  - Red shades = Positive correlations")
print("  - Blue shades = Negative correlations")
print("  - White = No correlation (near zero)")

