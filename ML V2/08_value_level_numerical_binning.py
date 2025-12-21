"""
==============================================================================
LEVEL 2: VALUE-LEVEL NUMERICAL BINNING ANALYSIS
==============================================================================

Purpose: Analyze SPECIFIC RANGES within each numerical variable
- Create bins/ranges for numerical variables
- Find which ranges favor long vs short calls
- Answer: "What range of discovery_questions leads to longer calls?"

Example: Instead of "discovery_questions is important", we find:
- "0-3 questions: 40% long calls"
- "4-7 questions: 55% long calls"  
- "8+ questions: 70% long calls"

==============================================================================
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("LEVEL 2: VALUE-LEVEL NUMERICAL BINNING ANALYSIS")
print("="*100)

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("\nLoading data...")
df = pd.read_csv('analysis_outputs/level1_variable/01_combined_original.csv')

print(f"Data: {df.shape}")

# ==============================================================================
# IDENTIFY NUMERICAL VARIABLES
# ==============================================================================

print("\n" + "="*100)
print("IDENTIFYING NUMERICAL VARIABLES")
print("="*100)

feature_cols = [c for c in df.columns if c not in ['target', 'call_duration_group']]

numerical_vars = []
for col in feature_cols:
    if df[col].dtype in ['int64', 'float64'] and df[col].nunique() >= 50:
        numerical_vars.append(col)

print(f"\nNumerical variables: {len(numerical_vars)}")
print("Variables:", numerical_vars)

# ==============================================================================
# BINNING ANALYSIS
# ==============================================================================

print("\n" + "="*100)
print("ANALYZING BINS/RANGES WITHIN EACH NUMERICAL VARIABLE")
print("="*100)

binning_results = []

for var in numerical_vars:
    print(f"\nAnalyzing variable: {var}")
    
    # Skip if too many missing values
    if df[var].isna().sum() / len(df) > 0.5:
        print(f"  Skipping (>50% missing)")
        continue
    
    # Create bins (quantile-based)
    try:
        df[f'{var}_bin'] = pd.qcut(df[var], q=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'], duplicates='drop')
        bin_labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
    except:
        try:
            df[f'{var}_bin'] = pd.cut(df[var], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
            bin_labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
        except:
            print(f"  Skipping (cannot bin)")
            continue
    
    print(f"  Created 5 bins")
    
    # Analyze each bin
    for bin_label in bin_labels:
        bin_mask = df[f'{var}_bin'] == bin_label
        total_count = bin_mask.sum()
        
        if total_count < 5:
            continue
        
        short_count = (bin_mask & (df['target'] == 0)).sum()
        long_count = (bin_mask & (df['target'] == 1)).sum()
        
        pct_short = (short_count / total_count * 100) if total_count > 0 else 0
        pct_long = (long_count / total_count * 100) if total_count > 0 else 0
        
        # Get actual value range for this bin
        bin_values = df[bin_mask][var].dropna()
        if len(bin_values) > 0:
            range_min = bin_values.min()
            range_max = bin_values.max()
            range_str = f"[{range_min:.2f}, {range_max:.2f}]"
        else:
            range_str = "N/A"
        
        # Direction
        if pct_long > 55:
            direction = "Favors Long Calls"
        elif pct_short > 55:
            direction = "Favors Short Calls"
        else:
            direction = "Neutral"
        
        importance = abs(pct_long - 50)
        
        binning_results.append({
            'Variable': var,
            'Bin': bin_label,
            'Value_Range': range_str,
            'Count_Short': int(short_count),
            'Count_Long': int(long_count),
            'Total_Count': int(total_count),
            'Pct_Short': round(pct_short, 2),
            'Pct_Long': round(pct_long, 2),
            'Pct_Difference': round(pct_long - pct_short, 2),
            'Direction': direction,
            'Importance_Score': round(importance, 2)
        })

# ==============================================================================
# CREATE RESULTS DATAFRAME
# ==============================================================================

df_binning = pd.DataFrame(binning_results)
df_binning = df_binning.sort_values('Importance_Score', ascending=False)

print(f"\n[OK] Analyzed {len(df_binning)} bins across {len(numerical_vars)} variables")

# ==============================================================================
# TOP INSIGHTS
# ==============================================================================

print("\n" + "="*100)
print("TOP NUMERICAL RANGE INSIGHTS")
print("="*100)

print("\nTOP 20 RANGES MOST ASSOCIATED WITH LONG CALLS:")
print("-" * 100)
top_long = df_binning[df_binning['Direction'] == 'Favors Long Calls'].head(20)
for idx, row in top_long.iterrows():
    print(f"  {row['Variable']} - {row['Bin']} {row['Value_Range']}")
    print(f"    -> {row['Pct_Long']:.1f}% Long | {row['Total_Count']} calls")

print("\nTOP 20 RANGES MOST ASSOCIATED WITH SHORT CALLS:")
print("-" * 100)
top_short = df_binning[df_binning['Direction'] == 'Favors Short Calls'].head(20)
for idx, row in top_short.iterrows():
    print(f"  {row['Variable']} - {row['Bin']} {row['Value_Range']}")
    print(f"    -> {row['Pct_Short']:.1f}% Short | {row['Total_Count']} calls")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

print("\n" + "="*100)
print("SAVING RESULTS")
print("="*100)

df_binning.to_csv('analysis_outputs/level2_value/08_numerical_binning_analysis.csv', index=False)
print("\n[OK] Saved: 08_numerical_binning_analysis.csv")

# Save per-variable binning
for var in numerical_vars:
    var_data = df_binning[df_binning['Variable'] == var]
    if len(var_data) > 0:
        var_data.to_csv(f'analysis_outputs/level2_value/08_bins_{var}.csv', index=False)

print(f"[OK] Saved {len(numerical_vars)} per-variable binning CSV files")

print("\n" + "="*100)
print("LEVEL 2 NUMERICAL BINNING COMPLETE")
print("="*100)
print(f"\n[OK] Analyzed {len(df_binning)} bins/ranges")
print(f"[OK] Across {len(numerical_vars)} numerical variables")
print(f"[OK] Top bin: {df_binning.iloc[0]['Variable']} - {df_binning.iloc[0]['Bin']}")

