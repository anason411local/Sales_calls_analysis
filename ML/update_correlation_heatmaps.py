"""
UPDATED CORRELATION HEATMAPS - With Values Displayed
Shows correlation values on ALL cells for better readability
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("CREATING CORRELATION HEATMAPS WITH VALUES")
print("="*100)

# Load enhanced data
df_short = pd.read_csv('analysis_outputs/enhanced_short_calls_data.csv')
df_long = pd.read_csv('analysis_outputs/enhanced_long_calls_data.csv')
df_combined = pd.read_csv('analysis_outputs/enhanced_combined_data.csv')

# Get numeric columns only
numeric_cols_short = df_short.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols_long = df_long.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols_combined = df_combined.select_dtypes(include=[np.number]).columns.tolist()

print(f"\nNumeric columns: {len(numeric_cols_short)}")

# ==================================================================================
# HEATMAP 1: SHORT CALLS CORRELATION (WITH VALUES)
# ==================================================================================
print("\n1. Creating SHORT CALLS correlation heatmap with values...")

df_short_numeric = df_short[numeric_cols_short].dropna(axis=1, how='all')
corr_short = df_short_numeric.corr()

fig, ax = plt.subplots(figsize=(24, 22))
mask = np.triu(np.ones_like(corr_short, dtype=bool))

sns.heatmap(corr_short, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax, annot_kws={'size': 6})

ax.set_title('Correlation Heatmap: SHORT CALLS (<4.88 minutes)\n' + 
             f'{len(corr_short)} Numeric Variables\n' +
             'Read: Red=Positive correlation, Blue=Negative correlation, White=No correlation', 
             fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_01_short_calls_correlation.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved with values: heatmap_01_short_calls_correlation.png")
plt.close()

# ==================================================================================
# HEATMAP 2: LONG CALLS CORRELATION (WITH VALUES)
# ==================================================================================
print("\n2. Creating LONG CALLS correlation heatmap with values...")

df_long_numeric = df_long[numeric_cols_long].dropna(axis=1, how='all')
corr_long = df_long_numeric.corr()

fig, ax = plt.subplots(figsize=(24, 22))
mask = np.triu(np.ones_like(corr_long, dtype=bool))

sns.heatmap(corr_long, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax, annot_kws={'size': 6})

ax.set_title('Correlation Heatmap: LONG CALLS (>4.88 minutes)\n' + 
             f'{len(corr_long)} Numeric Variables\n' +
             'Read: Red=Positive correlation, Blue=Negative correlation, White=No correlation', 
             fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_02_long_calls_correlation.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved with values: heatmap_02_long_calls_correlation.png")
plt.close()

# ==================================================================================
# HEATMAP 3: COMBINED CORRELATION (WITH VALUES)
# ==================================================================================
print("\n3. Creating COMBINED correlation heatmap with values...")

df_combined_numeric = df_combined[numeric_cols_combined].dropna(axis=1, how='all')
corr_combined = df_combined_numeric.corr()

fig, ax = plt.subplots(figsize=(24, 22))
mask = np.triu(np.ones_like(corr_combined, dtype=bool))

sns.heatmap(corr_combined, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax, annot_kws={'size': 6})

ax.set_title('Correlation Heatmap: COMBINED DATA (All Calls)\n' + 
             f'{len(corr_combined)} Numeric Variables\n' +
             'Read: Red=Positive correlation, Blue=Negative correlation, White=No correlation', 
             fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('analysis_outputs/heatmap_03_combined_correlation.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved with values: heatmap_03_combined_correlation.png")
plt.close()

print("\n" + "="*100)
print("CORRELATION HEATMAPS WITH VALUES COMPLETE")
print("="*100)
print("\nHOW TO READ CORRELATION HEATMAPS:")
print("- Values range from -1 to +1")
print("- +1 = Perfect positive correlation (variables move together)")
print("- -1 = Perfect negative correlation (variables move opposite)")
print("- 0 = No correlation")
print("- |r| > 0.7 = Strong correlation")
print("- |r| 0.3-0.7 = Moderate correlation")
print("- |r| < 0.3 = Weak correlation")

