"""
VALUE-LEVEL ANALYSIS
Analyzes specific values within each variable to answer questions like:
- Which timezone (Eastern/Central/Pacific) leads to longer calls?
- Which month has the highest % of long calls?
- Which sentiment leads to longer calls?
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*100)
print("VALUE-LEVEL ANALYSIS - ANALYZING SPECIFIC VALUES WITHIN EACH VARIABLE")
print("="*100)

# ==================================================================================
# LOAD ORIGINAL DATA (BEFORE ENCODING)
# ==================================================================================

print("\nLoading original data (49 variables + target)...")
df = pd.read_csv('analysis_outputs/01_combined_data.csv')

print(f"Data shape: {df.shape}")
print(f"Total variables: {df.shape[1] - 1} (excluding target)")

# Create binary target
df['target'] = (df['call_duration_group'] == 'Long (>4.88 min)').astype(int)

# ==================================================================================
# IDENTIFY VARIABLE TYPES
# ==================================================================================

print("\n" + "="*100)
print("IDENTIFYING VARIABLE TYPES")
print("="*100)

# Exclude target and ID columns
analysis_columns = [col for col in df.columns if col not in ['call_duration_group', 'target']]

categorical_vars = []
numerical_vars = []

for col in analysis_columns:
    if df[col].dtype in ['object', 'bool'] or df[col].nunique() < 50:
        categorical_vars.append(col)
    else:
        numerical_vars.append(col)

print(f"\nCategorical variables: {len(categorical_vars)}")
print(f"Numerical variables: {len(numerical_vars)}")

# ==================================================================================
# VALUE-LEVEL ANALYSIS FOR CATEGORICAL VARIABLES
# ==================================================================================

print("\n" + "="*100)
print("VALUE-LEVEL ANALYSIS: CATEGORICAL VARIABLES")
print("="*100)

value_level_results = []

for var in categorical_vars:
    print(f"\nAnalyzing: {var}")
    
    # Get value counts for short and long calls
    short_counts = df[df['target'] == 0][var].value_counts()
    long_counts = df[df['target'] == 1][var].value_counts()
    
    # Get all unique values
    all_values = sorted(df[var].dropna().unique())
    
    for value in all_values:
        # Count occurrences
        count_short = short_counts.get(value, 0)
        count_long = long_counts.get(value, 0)
        total = count_short + count_long
        
        if total < 5:  # Skip rare values
            continue
        
        # Calculate percentages
        pct_short = (count_short / total * 100) if total > 0 else 0
        pct_long = (count_long / total * 100) if total > 0 else 0
        
        # Calculate chi-square for this value vs all others
        try:
            # Create contingency table
            value_is_this = df[var] == value
            contingency = pd.crosstab(value_is_this, df['target'])
            chi2, p_value, dof, expected = chi2_contingency(contingency)
        except:
            chi2 = 0
            p_value = 1.0
        
        # Determine direction
        if pct_long > 55:
            direction = "Favors Long Calls"
        elif pct_short > 55:
            direction = "Favors Short Calls"
        else:
            direction = "Neutral"
        
        # Calculate importance score (deviation from 50-50)
        importance = abs(pct_long - 50)
        
        value_level_results.append({
            'Variable': var,
            'Value': str(value),
            'Count_Short': int(count_short),
            'Count_Long': int(count_long),
            'Total_Count': int(total),
            'Pct_Short': round(pct_short, 2),
            'Pct_Long': round(pct_long, 2),
            'Pct_Difference': round(pct_long - pct_short, 2),
            'Chi_Square': round(chi2, 4),
            'P_Value': round(p_value, 4),
            'Significant': 'Yes' if p_value < 0.05 else 'No',
            'Direction': direction,
            'Importance_Score': round(importance, 2)
        })

# Create DataFrame
df_value_analysis = pd.DataFrame(value_level_results)
df_value_analysis = df_value_analysis.sort_values('Importance_Score', ascending=False)

# Save full results
df_value_analysis.to_csv('analysis_outputs/08_value_level_analysis_all.csv', index=False)
print(f"\n[OK] Saved: 08_value_level_analysis_all.csv ({len(df_value_analysis)} rows)")

# ==================================================================================
# VALUE-LEVEL ANALYSIS FOR NUMERICAL VARIABLES
# ==================================================================================

print("\n" + "="*100)
print("VALUE-LEVEL ANALYSIS: NUMERICAL VARIABLES (BINNING)")
print("="*100)

numerical_value_results = []

for var in numerical_vars:
    print(f"\nAnalyzing: {var}")
    
    # Skip if too many missing values
    if df[var].isna().sum() / len(df) > 0.5:
        print(f"  Skipping (>50% missing)")
        continue
    
    # Create bins
    try:
        df[f'{var}_bin'] = pd.qcut(df[var], q=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'], duplicates='drop')
    except:
        try:
            df[f'{var}_bin'] = pd.cut(df[var], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
        except:
            print(f"  Skipping (cannot bin)")
            continue
    
    # Analyze each bin
    short_counts = df[df['target'] == 0][f'{var}_bin'].value_counts()
    long_counts = df[df['target'] == 1][f'{var}_bin'].value_counts()
    
    for bin_value in ['Very Low', 'Low', 'Medium', 'High', 'Very High']:
        count_short = short_counts.get(bin_value, 0)
        count_long = long_counts.get(bin_value, 0)
        total = count_short + count_long
        
        if total < 5:
            continue
        
        pct_short = (count_short / total * 100) if total > 0 else 0
        pct_long = (count_long / total * 100) if total > 0 else 0
        
        if pct_long > 55:
            direction = "Favors Long Calls"
        elif pct_short > 55:
            direction = "Favors Short Calls"
        else:
            direction = "Neutral"
        
        importance = abs(pct_long - 50)
        
        numerical_value_results.append({
            'Variable': var,
            'Bin': bin_value,
            'Count_Short': int(count_short),
            'Count_Long': int(count_long),
            'Total_Count': int(total),
            'Pct_Short': round(pct_short, 2),
            'Pct_Long': round(pct_long, 2),
            'Pct_Difference': round(pct_long - pct_short, 2),
            'Direction': direction,
            'Importance_Score': round(importance, 2)
        })

# Create DataFrame
df_numerical_value_analysis = pd.DataFrame(numerical_value_results)
df_numerical_value_analysis = df_numerical_value_analysis.sort_values('Importance_Score', ascending=False)

# Save results
df_numerical_value_analysis.to_csv('analysis_outputs/08_value_level_analysis_numerical.csv', index=False)
print(f"\n[OK] Saved: 08_value_level_analysis_numerical.csv ({len(df_numerical_value_analysis)} rows)")

# ==================================================================================
# CREATE TOP INSIGHTS SUMMARY
# ==================================================================================

print("\n" + "="*100)
print("TOP VALUE-LEVEL INSIGHTS")
print("="*100)

# Top values favoring LONG calls
print("\nTOP 20 VALUES MOST ASSOCIATED WITH LONG CALLS:")
print("-" * 100)
top_long = df_value_analysis[df_value_analysis['Direction'] == 'Favors Long Calls'].head(20)
for idx, row in top_long.iterrows():
    print(f"  {row['Variable']}: {row['Value']}")
    print(f"    -> {row['Pct_Long']:.1f}% Long Calls | {row['Total_Count']} total calls | p={row['P_Value']:.4f}")

# Top values favoring SHORT calls
print("\nTOP 20 VALUES MOST ASSOCIATED WITH SHORT CALLS:")
print("-" * 100)
top_short = df_value_analysis[df_value_analysis['Direction'] == 'Favors Short Calls'].head(20)
for idx, row in top_short.iterrows():
    print(f"  {row['Variable']}: {row['Value']}")
    print(f"    -> {row['Pct_Short']:.1f}% Short Calls | {row['Total_Count']} total calls | p={row['P_Value']:.4f}")

# ==================================================================================
# ANSWER SPECIFIC QUESTIONS
# ==================================================================================

print("\n" + "="*100)
print("ANSWERING KEY QUESTIONS")
print("="*100)

# Question 1: Which timezone leads to longer calls?
if 'timezone' in categorical_vars:
    print("\n1. WHICH TIMEZONE LEADS TO LONGER CALLS?")
    print("-" * 100)
    timezone_data = df_value_analysis[df_value_analysis['Variable'] == 'timezone'].sort_values('Pct_Long', ascending=False)
    for idx, row in timezone_data.iterrows():
        print(f"  {row['Value']}: {row['Pct_Long']:.1f}% Long Calls ({row['Count_Long']}/{row['Total_Count']} calls)")

# Question 2: Which month has highest % of long calls?
if 'season_month' in categorical_vars:
    print("\n2. WHICH MONTH HAS HIGHEST % OF LONG CALLS?")
    print("-" * 100)
    month_data = df_value_analysis[df_value_analysis['Variable'] == 'season_month'].sort_values('Pct_Long', ascending=False)
    for idx, row in month_data.iterrows():
        print(f"  {row['Value']}: {row['Pct_Long']:.1f}% Long Calls ({row['Count_Long']}/{row['Total_Count']} calls)")

# Question 3: Which sentiment leads to longer calls?
sentiment_vars = ['customer_sentiment_lgs', 'customer_sentiment_omc', 'lgs_sentiment_style', 'omc_agent_sentiment_style']
for sent_var in sentiment_vars:
    if sent_var in categorical_vars:
        print(f"\n3. WHICH {sent_var.upper()} LEADS TO LONGER CALLS?")
        print("-" * 100)
        sent_data = df_value_analysis[df_value_analysis['Variable'] == sent_var].sort_values('Pct_Long', ascending=False)
        for idx, row in sent_data.iterrows():
            print(f"  {row['Value']}: {row['Pct_Long']:.1f}% Long Calls ({row['Count_Long']}/{row['Total_Count']} calls)")

print("\n" + "="*100)
print("VALUE-LEVEL ANALYSIS COMPLETE")
print("="*100)
print("\nGenerated Files:")
print("  - 08_value_level_analysis_all.csv (all categorical values)")
print("  - 08_value_level_analysis_numerical.csv (numerical bins)")

