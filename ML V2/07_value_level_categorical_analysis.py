"""
==============================================================================
LEVEL 2: VALUE-LEVEL CATEGORICAL ANALYSIS
==============================================================================

Purpose: Analyze SPECIFIC VALUES within each categorical variable
- For each categorical variable, analyze each unique value
- Answer questions like: "Which timezone (Eastern/Central/Pacific) matters?"
- Calculate percentages, statistical significance, importance scores
- Chi-square tests for each value vs all others

Example: Instead of "timezone is important", we find:
- "Mountain timezone: 55.1% long calls"
- "Central timezone: 53.8% long calls"
- "Eastern timezone: 48.2% long calls"

==============================================================================
"""

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("LEVEL 2: VALUE-LEVEL CATEGORICAL ANALYSIS")
print("="*100)

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("\nLoading data...")
df = pd.read_csv('analysis_outputs/level1_variable/01_combined_original.csv')

print(f"Data: {df.shape}")
print(f"Target distribution:")
print(f"  Short calls: {(df['target'] == 0).sum()}")
print(f"  Long calls: {(df['target'] == 1).sum()}")

# ==============================================================================
# IDENTIFY CATEGORICAL VARIABLES
# ==============================================================================

print("\n" + "="*100)
print("IDENTIFYING CATEGORICAL VARIABLES")
print("="*100)

feature_cols = [c for c in df.columns if c not in ['target', 'call_duration_group']]

categorical_vars = []
for col in feature_cols:
    if df[col].dtype in ['object', 'bool'] or df[col].nunique() < 50:
        categorical_vars.append(col)

print(f"\nCategorical variables: {len(categorical_vars)}")
print("Variables:", categorical_vars[:10], "..." if len(categorical_vars) > 10 else "")

# ==============================================================================
# VALUE-LEVEL ANALYSIS
# ==============================================================================

print("\n" + "="*100)
print("ANALYZING SPECIFIC VALUES WITHIN EACH VARIABLE")
print("="*100)

value_results = []

for var in categorical_vars:
    print(f"\nAnalyzing variable: {var}")
    
    # Get unique values
    unique_values = df[var].dropna().unique()
    
    print(f"  Unique values: {len(unique_values)}")
    
    for value in unique_values:
        # Count occurrences
        value_mask = df[var] == value
        total_count = value_mask.sum()
        
        # Skip rare values
        if total_count < 5:
            continue
        
        short_count = ((df[var] == value) & (df['target'] == 0)).sum()
        long_count = ((df[var] == value) & (df['target'] == 1)).sum()
        
        # Calculate percentages
        pct_short = (short_count / total_count * 100) if total_count > 0 else 0
        pct_long = (long_count / total_count * 100) if total_count > 0 else 0
        
        # Chi-square test (this value vs all others)
        try:
            value_is_this = df[var] == value
            contingency = pd.crosstab(value_is_this, df['target'])
            chi2, p_value, dof, expected = chi2_contingency(contingency)
        except:
            chi2, p_value = 0, 1.0
        
        # Direction
        if pct_long > 55:
            direction = "Favors Long Calls"
        elif pct_short > 55:
            direction = "Favors Short Calls"
        else:
            direction = "Neutral"
        
        # Importance score (deviation from 50-50)
        importance = abs(pct_long - 50)
        
        value_results.append({
            'Variable': var,
            'Value': str(value),
            'Count_Short': int(short_count),
            'Count_Long': int(long_count),
            'Total_Count': int(total_count),
            'Pct_Short': round(pct_short, 2),
            'Pct_Long': round(pct_long, 2),
            'Pct_Difference': round(pct_long - pct_short, 2),
            'Chi_Square': round(chi2, 4),
            'P_Value': round(p_value, 4),
            'Significant': 'Yes' if p_value < 0.05 else 'No',
            'Direction': direction,
            'Importance_Score': round(importance, 2)
        })

# ==============================================================================
# CREATE RESULTS DATAFRAME
# ==============================================================================

df_value_analysis = pd.DataFrame(value_results)
df_value_analysis = df_value_analysis.sort_values('Importance_Score', ascending=False)

print(f"\n[OK] Analyzed {len(df_value_analysis)} specific values across {len(categorical_vars)} variables")

# ==============================================================================
# ANSWER KEY QUESTIONS
# ==============================================================================

print("\n" + "="*100)
print("ANSWERING KEY QUESTIONS")
print("="*100)

# Question 1: Which timezone?
if 'timezone' in categorical_vars:
    print("\n1. WHICH TIMEZONE LEADS TO LONGER CALLS?")
    print("-" * 100)
    timezone_data = df_value_analysis[df_value_analysis['Variable'] == 'timezone'].sort_values('Pct_Long', ascending=False)
    for idx, row in timezone_data.iterrows():
        sig = "***" if row['Significant'] == 'Yes' else ""
        print(f"  {row['Value']}: {row['Pct_Long']:.1f}% Long Calls ({row['Count_Long']}/{row['Total_Count']} calls) {sig}")

# Question 2: Which month?
if 'season_month' in categorical_vars:
    print("\n2. WHICH MONTH HAS HIGHEST % OF LONG CALLS?")
    print("-" * 100)
    month_data = df_value_analysis[df_value_analysis['Variable'] == 'season_month'].sort_values('Pct_Long', ascending=False)
    for idx, row in month_data.iterrows():
        sig = "***" if row['Significant'] == 'Yes' else ""
        print(f"  {row['Value']}: {row['Pct_Long']:.1f}% Long Calls ({row['Count_Long']}/{row['Total_Count']} calls) {sig}")

# Question 3: Which sentiments?
sentiment_vars = ['customer_sentiment_lgs', 'customer_sentiment_omc', 'lgs_sentiment_style', 'omc_agent_sentiment_style']
for sent_var in sentiment_vars:
    if sent_var in categorical_vars:
        print(f"\n3. WHICH {sent_var.upper().replace('_', ' ')} LEADS TO LONGER CALLS?")
        print("-" * 100)
        sent_data = df_value_analysis[df_value_analysis['Variable'] == sent_var].sort_values('Pct_Long', ascending=False)
        for idx, row in sent_data.head(10).iterrows():
            sig = "***" if row['Significant'] == 'Yes' else ""
            print(f"  {row['Value']}: {row['Pct_Long']:.1f}% Long Calls ({row['Count_Long']}/{row['Total_Count']} calls) {sig}")

# ==============================================================================
# TOP INSIGHTS
# ==============================================================================

print("\n" + "="*100)
print("TOP VALUE-LEVEL INSIGHTS")
print("="*100)

print("\nTOP 20 VALUES MOST ASSOCIATED WITH LONG CALLS:")
print("-" * 100)
top_long = df_value_analysis[df_value_analysis['Direction'] == 'Favors Long Calls'].head(20)
for idx, row in top_long.iterrows():
    sig = "***" if row['Significant'] == 'Yes' else ""
    print(f"  {row['Variable']}: {row['Value']}")
    print(f"    -> {row['Pct_Long']:.1f}% Long | {row['Total_Count']} calls | p={row['P_Value']:.4f} {sig}")

print("\nTOP 20 VALUES MOST ASSOCIATED WITH SHORT CALLS:")
print("-" * 100)
top_short = df_value_analysis[df_value_analysis['Direction'] == 'Favors Short Calls'].head(20)
for idx, row in top_short.iterrows():
    sig = "***" if row['Significant'] == 'Yes' else ""
    print(f"  {row['Variable']}: {row['Value']}")
    print(f"    -> {row['Pct_Short']:.1f}% Short | {row['Total_Count']} calls | p={row['P_Value']:.4f} {sig}")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

print("\n" + "="*100)
print("SAVING RESULTS")
print("="*100)

# Create output directory
import os
os.makedirs('analysis_outputs/level2_value', exist_ok=True)

# Save all value analysis
df_value_analysis.to_csv('analysis_outputs/level2_value/07_categorical_value_analysis.csv', index=False)
print("\n[OK] Saved: 07_categorical_value_analysis.csv")

# Save top long values
top_long.to_csv('analysis_outputs/level2_value/07_top_values_long_calls.csv', index=False)
print("[OK] Saved: 07_top_values_long_calls.csv")

# Save top short values
top_short.to_csv('analysis_outputs/level2_value/07_top_values_short_calls.csv', index=False)
print("[OK] Saved: 07_top_values_short_calls.csv")

# Save per-variable summaries
print("\n[OK] Creating per-variable summaries...")
for var in categorical_vars:
    var_data = df_value_analysis[df_value_analysis['Variable'] == var]
    if len(var_data) > 0:
        var_data.to_csv(f'analysis_outputs/level2_value/07_values_{var}.csv', index=False)

print(f"[OK] Saved {len(categorical_vars)} per-variable CSV files")

print("\n" + "="*100)
print("LEVEL 2 CATEGORICAL ANALYSIS COMPLETE")
print("="*100)
print(f"\n[OK] Analyzed {len(df_value_analysis)} specific values")
print(f"[OK] Across {len(categorical_vars)} categorical variables")
print(f"[OK] Significant values: {(df_value_analysis['Significant'] == 'Yes').sum()}")
print(f"[OK] Top value: {df_value_analysis.iloc[0]['Variable']} = {df_value_analysis.iloc[0]['Value']}")

