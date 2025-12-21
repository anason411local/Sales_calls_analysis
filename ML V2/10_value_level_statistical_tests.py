"""
==============================================================================
LEVEL 2: VALUE-LEVEL STATISTICAL TESTS
==============================================================================

Purpose: Statistical tests for specific values
- Chi-square for each value vs others
- Proportions comparison
- Already done in script 07, this consolidates and adds effect sizes

==============================================================================
"""

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("LEVEL 2: VALUE-LEVEL STATISTICAL TESTS")
print("="*100)

# Load results from categorical analysis
df_values = pd.read_csv('analysis_outputs/level2_value/07_categorical_value_analysis.csv')
df_binning = pd.read_csv('analysis_outputs/level2_value/08_numerical_binning_analysis.csv')

print(f"\nCategorical values: {len(df_values)}")
print(f"Numerical bins: {len(df_binning)}")

# ==============================================================================
# ENHANCED STATISTICAL ANALYSIS
# ==============================================================================

print("\n" + "="*100)
print("STATISTICAL SUMMARY")
print("="*100)

# Significant values
sig_cat = df_values[df_values['Significant'] == 'Yes']
print(f"\nStatistically significant categorical values: {len(sig_cat)}/{len(df_values)}")

# Large effects (>20% deviation from 50-50)
large_effect = df_values[df_values['Importance_Score'] > 20]
print(f"Values with large effect (>20% deviation): {len(large_effect)}")

# By direction
long_favoring = df_values[df_values['Direction'] == 'Favors Long Calls']
short_favoring = df_values[df_values['Direction'] == 'Favors Short Calls']

print(f"\nValues favoring LONG calls: {len(long_favoring)}")
print(f"Values favoring SHORT calls: {len(short_favoring)}")

# ==============================================================================
# TOP STATISTICALLY SIGNIFICANT VALUES
# ==============================================================================

print("\n" + "="*100)
print("TOP SIGNIFICANT VALUES")
print("="*100)

sig_values = df_values[df_values['Significant'] == 'Yes'].sort_values('Importance_Score', ascending=False)

print(f"\nTop 20 significant values:")
for idx, row in sig_values.head(20).iterrows():
    print(f"  {row['Variable']} = {row['Value']}")
    print(f"    {row['Pct_Long']:.1f}% long | p={row['P_Value']:.4f}")

# ==============================================================================
# SAVE SUMMARY
# ==============================================================================

summary = {
    'total_categorical_values': len(df_values),
    'total_numerical_bins': len(df_binning),
    'significant_values': len(sig_cat),
    'large_effect_values': len(large_effect),
    'long_favoring': len(long_favoring),
    'short_favoring': len(short_favoring)
}

import json
with open('analysis_outputs/level2_value/10_statistical_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

# Save significant values only
sig_values.to_csv('analysis_outputs/level2_value/10_significant_values.csv', index=False)

print("\n[OK] Saved: 10_statistical_summary.json")
print("[OK] Saved: 10_significant_values.csv")

print("\n" + "="*100)
print("LEVEL 2 STATISTICAL TESTS COMPLETE")
print("="*100)

