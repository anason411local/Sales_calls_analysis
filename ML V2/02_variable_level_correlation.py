"""
==============================================================================
LEVEL 1: VARIABLE-LEVEL CORRELATION ANALYSIS
==============================================================================

Purpose: Analyze correlations between the 49 original variables
- Clean 49x49 correlation matrix
- Spearman correlation (handles non-linear relationships)
- Correlation with target (call duration)
- Heatmaps with clear annotations

==============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*100)
print("LEVEL 1: VARIABLE-LEVEL CORRELATION ANALYSIS")
print("="*100)

# ==============================================================================
# LOAD PREPROCESSED DATA
# ==============================================================================

print("\nLoading preprocessed data...")
df_short = pd.read_csv('analysis_outputs/level1_variable/01_short_calls_original.csv')
df_long = pd.read_csv('analysis_outputs/level1_variable/01_long_calls_original.csv')
df_combined = pd.read_csv('analysis_outputs/level1_variable/01_combined_original.csv')

print(f"Short calls: {df_short.shape}")
print(f"Long calls: {df_long.shape}")
print(f"Combined: {df_combined.shape}")

# ==============================================================================
# PREPARE FOR CORRELATION
# ==============================================================================

print("\n" + "="*100)
print("PREPARING VARIABLES FOR CORRELATION")
print("="*100)

def prepare_for_correlation(df):
    """
    Convert all variables to numeric for correlation
    - Categorical: Target-ordered label encoding
    - Numerical: Keep as-is
    - Missing values: Median imputation
    """
    # Get analysis columns (exclude target and call_duration_group)
    analysis_cols = [c for c in df.columns if c not in ['target', 'call_duration_group']]
    
    df_corr = df[analysis_cols].copy()
    
    # Convert categorical to numeric
    for col in df_corr.columns:
        if df_corr[col].dtype == 'object' or df_corr[col].dtype == 'bool':
            # Target-ordered label encoding
            if 'target' in df.columns:
                target_means = df.groupby(col)['target'].mean()
                mapping = {val: rank for rank, val in enumerate(target_means.sort_values().index)}
                df_corr[col] = df[col].map(mapping)
            else:
                # Fallback: factorize
                df_corr[col] = pd.factorize(df[col])[0]
        
        # Impute missing values with median
        if df_corr[col].isna().any():
            median_val = df_corr[col].median()
            df_corr[col].fillna(median_val, inplace=True)
    
    return df_corr

print("Converting categorical variables to numeric...")
print("  Method: Target-ordered label encoding (preserves relationship with outcome)")

df_short_corr = prepare_for_correlation(df_short)
df_long_corr = prepare_for_correlation(df_long)
df_combined_corr = prepare_for_correlation(df_combined)

print(f"\nPrepared {len(df_combined_corr.columns)} variables for correlation")

# ==============================================================================
# CALCULATE SPEARMAN CORRELATIONS
# ==============================================================================

print("\n" + "="*100)
print("CALCULATING SPEARMAN CORRELATIONS")
print("="*100)

print("\nCalculating SHORT CALLS correlation matrix...")
corr_short = df_short_corr.corr(method='spearman')

print("Calculating LONG CALLS correlation matrix...")
corr_long = df_long_corr.corr(method='spearman')

print("Calculating COMBINED correlation matrix...")
corr_combined = df_combined_corr.corr(method='spearman')

print("Calculating DIFFERENCE matrix...")
corr_diff = corr_long - corr_short

print(f"\n[OK] Calculated 4 correlation matrices ({len(corr_combined)}x{len(corr_combined)} each)")

# ==============================================================================
# CORRELATION WITH TARGET
# ==============================================================================

print("\n" + "="*100)
print("CORRELATION WITH TARGET (Call Duration)")
print("="*100)

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

df_target_corr = pd.DataFrame(target_corr_results)
df_target_corr = df_target_corr.sort_values('Abs_Correlation', ascending=False)

print("\nTOP 20 VARIABLES CORRELATED WITH CALL DURATION:")
print("-" * 100)
for idx, row in df_target_corr.head(20).iterrows():
    direction = "+" if row['Direction'] == 'Positive' else "-"
    sig = "***" if row['Significant'] == 'Yes' else ""
    print(f"  {row['Variable']}: {direction}{row['Abs_Correlation']:.3f} ({row['Strength']}) {sig}")

# ==============================================================================
# SAVE CORRELATION MATRICES
# ==============================================================================

print("\n" + "="*100)
print("SAVING CORRELATION MATRICES")
print("="*100)

corr_short.to_csv('analysis_outputs/level1_variable/02_correlation_short_calls.csv')
corr_long.to_csv('analysis_outputs/level1_variable/02_correlation_long_calls.csv')
corr_combined.to_csv('analysis_outputs/level1_variable/02_correlation_combined.csv')
corr_diff.to_csv('analysis_outputs/level1_variable/02_correlation_difference.csv')
df_target_corr.to_csv('analysis_outputs/level1_variable/02_correlation_with_target.csv', index=False)

print("\n[OK] Saved 5 CSV files:")
print("  - 02_correlation_short_calls.csv")
print("  - 02_correlation_long_calls.csv")
print("  - 02_correlation_combined.csv")
print("  - 02_correlation_difference.csv")
print("  - 02_correlation_with_target.csv")

# ==============================================================================
# CREATE HEATMAP: SHORT CALLS
# ==============================================================================

print("\n" + "="*100)
print("CREATING HEATMAP 1/4: SHORT CALLS")
print("="*100)

fig, ax = plt.subplots(figsize=(28, 24))

sns.heatmap(corr_short,
            annot=True,
            fmt='.2f',
            annot_kws={'size': 8},  # Increased font size to 8
            cmap='RdBu_r',
            vmin=-1, vmax=1,
            center=0,
            square=True,
            linewidths=0.1,
            cbar_kws={'label': 'Spearman Correlation Coefficient', 'shrink': 0.8},
            ax=ax)

ax.set_title('LEVEL 1: VARIABLE-LEVEL CORRELATION HEATMAP\n' +
             'SHORT CALLS (<4.88 minutes)\n' +
             f'Method: SPEARMAN (Non-Linear) | Variables: {len(corr_short)} Original | Calls: {len(df_short):,}\n' +
             'RED = Positive Correlation | BLUE = Negative Correlation | WHITE = No Correlation\n' +
             'Analyzing relationships between 49 variables from Sections 1-6.6',
             fontsize=18, fontweight='bold', pad=30)

plt.xticks(rotation=90, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/heatmap_02_short_calls.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_02_short_calls.png")
plt.close()

# ==============================================================================
# CREATE HEATMAP: LONG CALLS
# ==============================================================================

print("\nCREATING HEATMAP 2/4: LONG CALLS")

fig, ax = plt.subplots(figsize=(28, 24))

sns.heatmap(corr_long,
            annot=True,
            fmt='.2f',
            annot_kws={'size': 8},  # Increased font size to 8
            cmap='RdBu_r',
            vmin=-1, vmax=1,
            center=0,
            square=True,
            linewidths=0.1,
            cbar_kws={'label': 'Spearman Correlation Coefficient', 'shrink': 0.8},
            ax=ax)

ax.set_title('LEVEL 1: VARIABLE-LEVEL CORRELATION HEATMAP\n' +
             'LONG CALLS (>4.88 minutes)\n' +
             f'Method: SPEARMAN (Non-Linear) | Variables: {len(corr_long)} Original | Calls: {len(df_long):,}\n' +
             'RED = Positive Correlation | BLUE = Negative Correlation | WHITE = No Correlation\n' +
             'Analyzing relationships between 49 variables from Sections 1-6.6',
             fontsize=18, fontweight='bold', pad=30)

plt.xticks(rotation=90, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/heatmap_02_long_calls.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_02_long_calls.png")
plt.close()

# ==============================================================================
# CREATE HEATMAP: COMBINED
# ==============================================================================

print("\nCREATING HEATMAP 3/4: COMBINED")

fig, ax = plt.subplots(figsize=(28, 24))

sns.heatmap(corr_combined,
            annot=True,
            fmt='.2f',
            annot_kws={'size': 8},  # Increased font size to 8
            cmap='RdBu_r',
            vmin=-1, vmax=1,
            center=0,
            square=True,
            linewidths=0.1,
            cbar_kws={'label': 'Spearman Correlation Coefficient', 'shrink': 0.8},
            ax=ax)

ax.set_title('LEVEL 1: VARIABLE-LEVEL CORRELATION HEATMAP\n' +
             'ALL CALLS (Combined Dataset)\n' +
             f'Method: SPEARMAN (Non-Linear) | Variables: {len(corr_combined)} Original | Calls: {len(df_combined):,}\n' +
             'RED = Positive Correlation | BLUE = Negative Correlation | WHITE = No Correlation\n' +
             'Analyzing relationships between 49 variables from Sections 1-6.6',
             fontsize=18, fontweight='bold', pad=30)

plt.xticks(rotation=90, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/heatmap_02_combined.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_02_combined.png")
plt.close()

# ==============================================================================
# CREATE HEATMAP: DIFFERENCE
# ==============================================================================

print("\nCREATING HEATMAP 4/4: DIFFERENCE")

fig, ax = plt.subplots(figsize=(28, 24))

sns.heatmap(corr_diff,
            annot=True,
            fmt='.2f',
            annot_kws={'size': 8},  # Increased font size to 8
            cmap='RdBu_r',
            vmin=-1, vmax=1,
            center=0,
            square=True,
            linewidths=0.1,
            cbar_kws={'label': 'Correlation Difference', 'shrink': 0.8},
            ax=ax)

ax.set_title('LEVEL 1: CORRELATION DIFFERENCE HEATMAP\n' +
             'LONG CALLS - SHORT CALLS\n' +
             f'Method: SPEARMAN (Non-Linear) | Variables: {len(corr_diff)} Original\n' +
             'RED = Stronger in Long Calls | BLUE = Stronger in Short Calls | WHITE = No Change\n' +
             'Shows how variable relationships change between successful vs unsuccessful calls',
             fontsize=18, fontweight='bold', pad=30)

plt.xticks(rotation=90, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/heatmap_02_difference.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_02_difference.png")
plt.close()

print("\n" + "="*100)
print("LEVEL 1 CORRELATION ANALYSIS COMPLETE")
print("="*100)
print("\n[OK] Created 49x49 correlation matrices (clean, original variables)")
print("[OK] Used Spearman correlation (non-linear)")
print("[OK] Generated 4 heatmaps with clear annotations")
print(f"[OK] Top variable: {df_target_corr.iloc[0]['Variable']} (r={df_target_corr.iloc[0]['Correlation']:.3f})")

