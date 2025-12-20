"""
CORRELATION HEATMAPS - 3 Versions (Short, Long, Combined)
Beautiful correlation matrices for numerical variables
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

# Load enhanced data
df_short = pd.read_csv('analysis_outputs/enhanced_short_calls_data.csv')
df_long = pd.read_csv('analysis_outputs/enhanced_long_calls_data.csv')
df_combined = pd.read_csv('analysis_outputs/enhanced_combined_data.csv')

# Get numeric columns only
numeric_cols_short = df_short.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols_long = df_long.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols_combined = df_combined.select_dtypes(include=[np.number]).columns.tolist()

print(f"\nNumeric columns in short dataset: {len(numeric_cols_short)}")
print(f"Numeric columns in long dataset: {len(numeric_cols_long)}")
print(f"Numeric columns in combined dataset: {len(numeric_cols_combined)}")

# ==================================================================================
# HEATMAP 1: SHORT CALLS CORRELATION
# ==================================================================================
print("\n1. Creating correlation heatmap for SHORT CALLS...")

df_short_numeric = df_short[numeric_cols_short].dropna(axis=1, how='all')
corr_short = df_short_numeric.corr()

# Create figure
fig, ax = plt.subplots(figsize=(20, 18))

# Create mask for upper triangle
mask = np.triu(np.ones_like(corr_short, dtype=bool))

# Create heatmap
sns.heatmap(corr_short, mask=mask, annot=False, cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax)

ax.set_title('Correlation Heatmap: SHORT CALLS (<4.88 minutes)\n' + 
             f'{len(corr_short)} Numeric Variables', 
             fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_01_short_calls_correlation.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: heatmap_01_short_calls_correlation.png")
plt.close()

# ==================================================================================
# HEATMAP 2: LONG CALLS CORRELATION
# ==================================================================================
print("\n2. Creating correlation heatmap for LONG CALLS...")

df_long_numeric = df_long[numeric_cols_long].dropna(axis=1, how='all')
corr_long = df_long_numeric.corr()

fig, ax = plt.subplots(figsize=(20, 18))
mask = np.triu(np.ones_like(corr_long, dtype=bool))

sns.heatmap(corr_long, mask=mask, annot=False, cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax)

ax.set_title('Correlation Heatmap: LONG CALLS (>4.88 minutes)\n' + 
             f'{len(corr_long)} Numeric Variables', 
             fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_02_long_calls_correlation.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: heatmap_02_long_calls_correlation.png")
plt.close()

# ==================================================================================
# HEATMAP 3: COMBINED CORRELATION
# ==================================================================================
print("\n3. Creating correlation heatmap for COMBINED DATA...")

df_combined_numeric = df_combined[numeric_cols_combined].dropna(axis=1, how='all')
corr_combined = df_combined_numeric.corr()

fig, ax = plt.subplots(figsize=(20, 18))
mask = np.triu(np.ones_like(corr_combined, dtype=bool))

sns.heatmap(corr_combined, mask=mask, annot=False, cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax)

ax.set_title('Correlation Heatmap: COMBINED DATA (All Calls)\n' + 
             f'{len(corr_combined)} Numeric Variables', 
             fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_03_combined_correlation.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: heatmap_03_combined_correlation.png")
plt.close()

# ==================================================================================
# SAVE CORRELATION MATRICES AS CSV
# ==================================================================================
print("\n4. Saving correlation matrices as CSV files...")

corr_short.to_csv('analysis_outputs/correlation_matrix_short_calls.csv')
corr_long.to_csv('analysis_outputs/correlation_matrix_long_calls.csv')
corr_combined.to_csv('analysis_outputs/correlation_matrix_combined.csv')

print("   [OK] Saved: correlation_matrix_short_calls.csv")
print("   [OK] Saved: correlation_matrix_long_calls.csv")
print("   [OK] Saved: correlation_matrix_combined.csv")

# ==================================================================================
# CREATE TOP CORRELATIONS SUMMARY
# ==================================================================================
print("\n5. Creating top correlations summary...")

# For each dataset, find top positive and negative correlations with TO_OMC_Duration
summaries = []

for name, corr_matrix in [('Short', corr_short), ('Long', corr_long), ('Combined', corr_combined)]:
    if 'TO_OMC_Duration' in corr_matrix.columns:
        omc_corr = corr_matrix['TO_OMC_Duration'].drop('TO_OMC_Duration').sort_values(ascending=False)
        
        summary = {
            'Dataset': name,
            'Top_Positive_Variable': omc_corr.index[0],
            'Top_Positive_Correlation': omc_corr.iloc[0],
            'Top_Negative_Variable': omc_corr.index[-1],
            'Top_Negative_Correlation': omc_corr.iloc[-1],
            'Avg_Abs_Correlation': omc_corr.abs().mean()
        }
        summaries.append(summary)

df_summary = pd.DataFrame(summaries)
df_summary.to_csv('analysis_outputs/correlation_with_duration_summary.csv', index=False)

print("\nTop Correlations with TO_OMC_Duration:")
print("-" * 100)
print(df_summary.to_string(index=False))

print("\n" + "="*100)
print("CORRELATION HEATMAPS COMPLETE")
print("="*100)

