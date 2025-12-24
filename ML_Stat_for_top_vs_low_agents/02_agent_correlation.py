"""
==============================================================================
AGENT-LEVEL ANALYSIS: CORRELATION
==============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
import sys
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Get agent type from command line
AGENT_TYPE = sys.argv[2] if len(sys.argv) >= 3 else 'top_agent'
AGENT_NAME = sys.argv[1] if len(sys.argv) >= 2 else 'Unknown'

print("="*100)
print(f"AGENT-LEVEL CORRELATION ANALYSIS: {AGENT_NAME}")
print("="*100)

# Load data
df_short = pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/01_short_calls_original.csv')
df_long = pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/01_long_calls_original.csv')
df_combined = pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/01_combined_original.csv')

print(f"Short calls: {df_short.shape}")
print(f"Long calls: {df_long.shape}")
print(f"Combined: {df_combined.shape}")

# Prepare for correlation
def prepare_for_correlation(df):
    analysis_cols = [c for c in df.columns if c not in ['target', 'call_duration_group']]
    df_corr = df[analysis_cols].copy()
    
    for col in df_corr.columns:
        if df_corr[col].dtype == 'object' or df_corr[col].dtype == 'bool':
            if 'target' in df.columns:
                target_means = df.groupby(col)['target'].mean()
                mapping = {val: rank for rank, val in enumerate(target_means.sort_values().index)}
                df_corr[col] = df[col].map(mapping)
            else:
                df_corr[col] = pd.factorize(df[col])[0]
        
        if df_corr[col].isna().any():
            median_val = df_corr[col].median()
            df_corr[col].fillna(median_val, inplace=True)
    
    return df_corr

print("\nCalculating correlations...")
df_short_corr = prepare_for_correlation(df_short)
df_long_corr = prepare_for_correlation(df_long)
df_combined_corr = prepare_for_correlation(df_combined)

corr_short = df_short_corr.corr(method='spearman')
corr_long = df_long_corr.corr(method='spearman')
corr_combined = df_combined_corr.corr(method='spearman')

# Correlation with target
target_corr_results = []
for col in df_combined_corr.columns:
    corr, pval = spearmanr(df_combined_corr[col], df_combined['target'], nan_policy='omit')
    target_corr_results.append({
        'Variable': col,
        'Correlation': corr,
        'Abs_Correlation': abs(corr),
        'P_Value': pval,
        'Significant': 'Yes' if pval < 0.05 else 'No',
        'Direction': 'Positive' if corr > 0 else 'Negative',
        'Strength': 'Strong' if abs(corr) > 0.5 else ('Moderate' if abs(corr) > 0.3 else 'Weak')
    })

df_target_corr = pd.DataFrame(target_corr_results).sort_values('Abs_Correlation', ascending=False)

print(f"\nTOP 20 VARIABLES CORRELATED WITH CALL DURATION FOR {AGENT_NAME}:")
print("-" * 100)
for idx, row in df_target_corr.head(20).iterrows():
    direction = "+" if row['Direction'] == 'Positive' else "-"
    sig = "***" if row['Significant'] == 'Yes' else ""
    print(f"  {row['Variable']}: {direction}{row['Abs_Correlation']:.3f} ({row['Strength']}) {sig}")

# Save results
output_dir = f'analysis_outputs/{AGENT_TYPE}'
corr_short.to_csv(f'{output_dir}/02_correlation_short_calls.csv')
corr_long.to_csv(f'{output_dir}/02_correlation_long_calls.csv')
corr_combined.to_csv(f'{output_dir}/02_correlation_combined.csv')
df_target_corr.to_csv(f'{output_dir}/02_correlation_with_target.csv', index=False)

# Create heatmaps
fig, ax = plt.subplots(figsize=(28, 24))
sns.heatmap(corr_short, annot=True, fmt='.2f', annot_kws={'size': 8}, cmap='RdBu_r',
            vmin=-1, vmax=1, center=0, square=True, linewidths=0.1,
            cbar_kws={'label': 'Spearman Correlation', 'shrink': 0.8}, ax=ax)
ax.set_title(f'AGENT-LEVEL CORRELATION HEATMAP: {AGENT_NAME}\nSHORT CALLS (<4.88 minutes)\n' +
             f'Method: SPEARMAN | Variables: {len(corr_short)} | Calls: {len(df_short):,}',
             fontsize=18, fontweight='bold', pad=30)
plt.xticks(rotation=90, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig(f'{output_dir}/heatmap_02_short_calls.png', dpi=300, bbox_inches='tight')
plt.close()

fig, ax = plt.subplots(figsize=(28, 24))
sns.heatmap(corr_long, annot=True, fmt='.2f', annot_kws={'size': 8}, cmap='RdBu_r',
            vmin=-1, vmax=1, center=0, square=True, linewidths=0.1,
            cbar_kws={'label': 'Spearman Correlation', 'shrink': 0.8}, ax=ax)
ax.set_title(f'AGENT-LEVEL CORRELATION HEATMAP: {AGENT_NAME}\nLONG CALLS (>4.88 minutes)\n' +
             f'Method: SPEARMAN | Variables: {len(corr_long)} | Calls: {len(df_long):,}',
             fontsize=18, fontweight='bold', pad=30)
plt.xticks(rotation=90, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig(f'{output_dir}/heatmap_02_long_calls.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n[OK] Correlation analysis complete")
print(f"[OK] Saved heatmaps and correlation data to {output_dir}")
