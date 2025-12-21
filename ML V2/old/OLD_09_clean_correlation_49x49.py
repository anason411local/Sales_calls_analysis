"""
CLEAN 49x49 CORRELATION HEATMAP
Uses original variables (before encoding) for clear, interpretable correlation analysis
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
print("CREATING CLEAN 49x49 CORRELATION HEATMAP (ORIGINAL VARIABLES)")
print("="*100)

# ==================================================================================
# LOAD ORIGINAL DATA
# ==================================================================================

print("\nLoading original data...")
df_short = pd.read_csv('analysis_outputs/01_short_calls_data.csv')
df_long = pd.read_csv('analysis_outputs/01_long_calls_data.csv')
df_combined = pd.read_csv('analysis_outputs/01_combined_data.csv')

print(f"Short calls: {df_short.shape[0]} rows, {df_short.shape[1]} columns")
print(f"Long calls: {df_long.shape[0]} rows, {df_long.shape[1]} columns")
print(f"Combined: {df_combined.shape[0]} rows, {df_combined.shape[1]} columns")

# ==================================================================================
# PREPARE DATA FOR CORRELATION
# ==================================================================================

print("\n" + "="*100)
print("PREPARING DATA FOR CORRELATION ANALYSIS")
print("="*100)

# Exclude target column
analysis_columns = [col for col in df_combined.columns if col != 'call_duration_group']

print(f"\nAnalyzing {len(analysis_columns)} variables")

# Create binary target
df_short['target'] = 0
df_long['target'] = 1
df_combined['target'] = (df_combined['call_duration_group'] == 'Long (>4.88 min)').astype(int)

def prepare_for_correlation(df, columns):
    """
    Convert all variables to numeric for correlation analysis
    - Categorical: Label encoding (ordered by target mean)
    - Numerical: Keep as is
    """
    df_corr = df[columns].copy()
    
    for col in df_corr.columns:
        if df_corr[col].dtype == 'object' or df_corr[col].dtype == 'bool':
            # Label encode based on target mean (preserves relationship with outcome)
            if col in df.columns and 'target' in df.columns:
                target_means = df.groupby(col)['target'].mean()
                mapping = {val: rank for rank, val in enumerate(target_means.sort_values().index)}
                df_corr[col] = df[col].map(mapping)
            else:
                # Fallback: simple label encoding
                df_corr[col] = pd.factorize(df[col])[0]
        
        # Fill missing values with median
        if df_corr[col].isna().any():
            df_corr[col].fillna(df_corr[col].median(), inplace=True)
    
    return df_corr

print("\nConverting categorical variables to numeric (target-ordered label encoding)...")
df_short_corr = prepare_for_correlation(df_short, analysis_columns)
df_long_corr = prepare_for_correlation(df_long, analysis_columns)
df_combined_corr = prepare_for_correlation(df_combined, analysis_columns)

print(f"Prepared for correlation: {df_combined_corr.shape}")

# ==================================================================================
# CALCULATE SPEARMAN CORRELATIONS
# ==================================================================================

print("\n" + "="*100)
print("CALCULATING SPEARMAN CORRELATIONS (49x49)")
print("="*100)

print("\nCalculating for SHORT calls...")
corr_short = df_short_corr.corr(method='spearman')

print("Calculating for LONG calls...")
corr_long = df_long_corr.corr(method='spearman')

print("Calculating for COMBINED data...")
corr_combined = df_combined_corr.corr(method='spearman')

print("\nCalculating DIFFERENCE (Long - Short)...")
corr_diff = corr_long - corr_short

# Save matrices
corr_short.to_csv('analysis_outputs/09_correlation_49x49_short_calls.csv')
corr_long.to_csv('analysis_outputs/09_correlation_49x49_long_calls.csv')
corr_combined.to_csv('analysis_outputs/09_correlation_49x49_combined.csv')
corr_diff.to_csv('analysis_outputs/09_correlation_49x49_difference.csv')

print("\n[OK] Saved correlation matrices (49x49)")

# ==================================================================================
# CREATE CLEAN HEATMAP: SHORT CALLS
# ==================================================================================

print("\n" + "="*100)
print("CREATING HEATMAP 1: SHORT CALLS")
print("="*100)

fig, ax = plt.subplots(figsize=(24, 20))

# Create heatmap
sns.heatmap(corr_short, 
            annot=False,  # No values (too cluttered with 49 vars)
            fmt='.2f',
            cmap='RdBu_r',
            vmin=-1, vmax=1,
            center=0,
            square=True,
            linewidths=0.1,
            cbar_kws={'label': 'Spearman Correlation', 'shrink': 0.8},
            ax=ax)

ax.set_title('CORRELATION HEATMAP: SHORT CALLS (<4.88 minutes)\n' + 
             f'Method: SPEARMAN (Non-Linear) | Variables: {len(corr_short)} ORIGINAL (not encoded)\n' +
             f'Calls: {df_short.shape[0]:,} | RED = Positive | BLUE = Negative | WHITE = None\n' +
             'Shows relationships between 49 variables from Sections 1-6.6', 
             fontsize=20, fontweight='bold', pad=30)

plt.xticks(rotation=90, ha='right', fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_09_clean_49x49_short_calls.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_09_clean_49x49_short_calls.png")
plt.close()

# ==================================================================================
# CREATE CLEAN HEATMAP: LONG CALLS
# ==================================================================================

print("\n" + "="*100)
print("CREATING HEATMAP 2: LONG CALLS")
print("="*100)

fig, ax = plt.subplots(figsize=(24, 20))

sns.heatmap(corr_long, 
            annot=False,
            fmt='.2f',
            cmap='RdBu_r',
            vmin=-1, vmax=1,
            center=0,
            square=True,
            linewidths=0.1,
            cbar_kws={'label': 'Spearman Correlation', 'shrink': 0.8},
            ax=ax)

ax.set_title('CORRELATION HEATMAP: LONG CALLS (>4.88 minutes)\n' + 
             f'Method: SPEARMAN (Non-Linear) | Variables: {len(corr_long)} ORIGINAL (not encoded)\n' +
             f'Calls: {df_long.shape[0]:,} | RED = Positive | BLUE = Negative | WHITE = None\n' +
             'Shows relationships between 49 variables from Sections 1-6.6', 
             fontsize=20, fontweight='bold', pad=30)

plt.xticks(rotation=90, ha='right', fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_09_clean_49x49_long_calls.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_09_clean_49x49_long_calls.png")
plt.close()

# ==================================================================================
# CREATE CLEAN HEATMAP: COMBINED
# ==================================================================================

print("\n" + "="*100)
print("CREATING HEATMAP 3: COMBINED DATA")
print("="*100)

fig, ax = plt.subplots(figsize=(24, 20))

sns.heatmap(corr_combined, 
            annot=False,
            fmt='.2f',
            cmap='RdBu_r',
            vmin=-1, vmax=1,
            center=0,
            square=True,
            linewidths=0.1,
            cbar_kws={'label': 'Spearman Correlation', 'shrink': 0.8},
            ax=ax)

ax.set_title('CORRELATION HEATMAP: ALL CALLS (Combined Dataset)\n' + 
             f'Method: SPEARMAN (Non-Linear) | Variables: {len(corr_combined)} ORIGINAL (not encoded)\n' +
             f'Calls: {df_combined.shape[0]:,} | RED = Positive | BLUE = Negative | WHITE = None\n' +
             'Shows relationships between 49 variables from Sections 1-6.6', 
             fontsize=20, fontweight='bold', pad=30)

plt.xticks(rotation=90, ha='right', fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_09_clean_49x49_combined.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_09_clean_49x49_combined.png")
plt.close()

# ==================================================================================
# CREATE CLEAN HEATMAP: DIFFERENCE
# ==================================================================================

print("\n" + "="*100)
print("CREATING HEATMAP 4: CORRELATION DIFFERENCE")
print("="*100)

fig, ax = plt.subplots(figsize=(24, 20))

sns.heatmap(corr_diff, 
            annot=False,
            fmt='.2f',
            cmap='RdBu_r',
            vmin=-1, vmax=1,
            center=0,
            square=True,
            linewidths=0.1,
            cbar_kws={'label': 'Correlation Difference', 'shrink': 0.8},
            ax=ax)

ax.set_title('CORRELATION DIFFERENCE: Long Calls - Short Calls\n' + 
             f'Method: SPEARMAN (Non-Linear) | Variables: {len(corr_diff)} ORIGINAL\n' +
             'RED = Stronger in Long Calls | BLUE = Stronger in Short Calls | WHITE = No Change\n' +
             'Shows how variable relationships change between successful vs unsuccessful calls', 
             fontsize=20, fontweight='bold', pad=30)

plt.xticks(rotation=90, ha='right', fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_09_clean_49x49_difference.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: heatmap_09_clean_49x49_difference.png")
plt.close()

# ==================================================================================
# CORRELATION WITH TARGET
# ==================================================================================

print("\n" + "="*100)
print("CORRELATION WITH TARGET (Call Duration Group)")
print("="*100)

# Calculate correlation with target for combined data
target_corr = []
for col in analysis_columns:
    corr, pval = spearmanr(df_combined_corr[col], df_combined['target'], nan_policy='omit')
    target_corr.append({
        'Variable': col,
        'Correlation_With_Target': corr,
        'P_Value': pval,
        'Abs_Correlation': abs(corr),
        'Significant': 'Yes' if pval < 0.05 else 'No'
    })

df_target_corr = pd.DataFrame(target_corr)
df_target_corr = df_target_corr.sort_values('Abs_Correlation', ascending=False)

# Save
df_target_corr.to_csv('analysis_outputs/09_correlation_with_target.csv', index=False)
print("\n[OK] Saved: 09_correlation_with_target.csv")

# Show top correlations
print("\nTOP 20 VARIABLES CORRELATED WITH CALL DURATION:")
print("-" * 100)
for idx, row in df_target_corr.head(20).iterrows():
    direction = "+" if row['Correlation_With_Target'] > 0 else "-"
    print(f"  {row['Variable']}: {direction}{row['Abs_Correlation']:.3f} (p={row['P_Value']:.4f})")

print("\n" + "="*100)
print("CLEAN 49x49 CORRELATION HEATMAPS COMPLETE")
print("="*100)
print("\nGenerated Files:")
print("  CSV Files:")
print("    - 09_correlation_49x49_short_calls.csv")
print("    - 09_correlation_49x49_long_calls.csv")
print("    - 09_correlation_49x49_combined.csv")
print("    - 09_correlation_49x49_difference.csv")
print("    - 09_correlation_with_target.csv")
print("\n  Heatmap Images:")
print("    - heatmap_09_clean_49x49_short_calls.png")
print("    - heatmap_09_clean_49x49_long_calls.png")
print("    - heatmap_09_clean_49x49_combined.png")
print("    - heatmap_09_clean_49x49_difference.png")

