"""
STEP 1: DATA EXPLORATION AND PREPROCESSING
Understanding why not all OMC calls are going above 4.88 minutes

This script:
1. Loads and explores the specified columns only
2. Analyzes data distribution, missing values, and patterns
3. Preprocesses categorical variables intelligently
4. Saves cleaned data for further analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*100)
print("DATA EXPLORATION AND PREPROCESSING - V2 ANALYSIS")
print("="*100)

# ==================================================================================
# DEFINE COLUMNS TO ANALYZE (AS SPECIFIED BY USER)
# ==================================================================================

COLUMNS_TO_ANALYZE = {
    # Section 1: Lead Quality
    'lead_quality': [
        'LQ_Company_Name', 'LQ_Company_Address', 'LQ_Service', 'LQ_Customer_Name',
        'Calls Count', 'Connection Made Calls'
    ],
    
    # Section 2: Timings
    'timings': [
        'TO_Event_O', 'timezone', 'season_status', 'season_month'
    ],
    
    # Section 3: LGS Department
    'lgs_department': [
        'TO_User_M', 'lgs_sentiment_style', 'lgs_agent_gender', 'TO_length_in_sec',
        'is_decision_maker', 'ready_for_customers', 'forbidden_industry', 'ready_to_transfer'
    ],
    
    # Section 4: Customer
    'customer': [
        'customer_sentiment_lgs', 'customer_sentiment_omc', 'customer_language',
        'customer_knows_marketing', 'customer_availability', 'who_said_hello_first_lgs',
        'customer_marketing_experience'
    ],
    
    # Section 5: Technical Quality
    'technical_quality': [
        'technical_quality_score', 'technical_quality_issues'
    ],
    
    # Section 6.1: OMC Department
    'omc_department': [
        'TO_OMC_User', 'TO_OMC_Disposiion', 'TO_OMC_Duration', 'omc_agent_sentiment_style',
        'omc_who_said_hello_first'
    ],
    
    # Section 6.2: OMC Customer Engagement
    'omc_engagement': [
        'customer_talk_percentage', 'total_discovery_questions', 'total_buying_signals'
    ],
    
    # Section 6.3: OMC Call Opening
    'omc_opening': [
        'time_to_reason_seconds', 'location_mentioned', 'business_type_mentioned',
        'within_45_seconds', 'call_structure_framed'
    ],
    
    # Section 6.4: OMC Objections
    'omc_objections': [
        'total_objections', 'objections_acknowledged', 'price_mentions_final_2min',
        'timeline_mentions_final_2min', 'contract_mentions_final_2min', 'objections_rebutted'
    ],
    
    # Section 6.5: Pace & Control
    'omc_pace': [
        'total_interruptions'
    ],
    
    # Section 6.6: Outcome
    'omc_outcome': [
        'commitment_type', 'call_result_tag'
    ]
}

# Flatten all columns
ALL_SELECTED_COLUMNS = []
for section, cols in COLUMNS_TO_ANALYZE.items():
    ALL_SELECTED_COLUMNS.extend(cols)

print(f"\nTotal columns selected for analysis: {len(ALL_SELECTED_COLUMNS)}")
for section, cols in COLUMNS_TO_ANALYZE.items():
    print(f"  - {section}: {len(cols)} columns")

# ==================================================================================
# LOAD DATA
# ==================================================================================

print("\n" + "="*100)
print("LOADING DATA")
print("="*100)

df_short = pd.read_csv('../ML/Less_than_4.88_mnt..csv')
df_long = pd.read_csv('../ML/greater_than_4.88_mnt..csv')

print(f"\nOriginal data:")
print(f"  Short calls (<4.88 min): {df_short.shape[0]} rows, {df_short.shape[1]} columns")
print(f"  Long calls (>4.88 min): {df_long.shape[0]} rows, {df_long.shape[1]} columns")

# Add duration group label
df_short['call_duration_group'] = 'Short (<4.88 min)'
df_long['call_duration_group'] = 'Long (>4.88 min)'

# Select only specified columns (+ label)
available_cols_short = [col for col in ALL_SELECTED_COLUMNS if col in df_short.columns]
available_cols_long = [col for col in ALL_SELECTED_COLUMNS if col in df_long.columns]

missing_cols = set(ALL_SELECTED_COLUMNS) - set(available_cols_short)
if missing_cols:
    print(f"\n[WARNING] Missing columns in dataset: {missing_cols}")

# Select columns
df_short_filtered = df_short[available_cols_short + ['call_duration_group']].copy()
df_long_filtered = df_long[available_cols_long + ['call_duration_group']].copy()

print(f"\nFiltered data:")
print(f"  Short calls: {df_short_filtered.shape[0]} rows, {df_short_filtered.shape[1]} columns")
print(f"  Long calls: {df_long_filtered.shape[0]} rows, {df_long_filtered.shape[1]} columns")

# Combine datasets
df_combined = pd.concat([df_short_filtered, df_long_filtered], ignore_index=True)
print(f"  Combined: {df_combined.shape[0]} rows, {df_combined.shape[1]} columns")

# ==================================================================================
# DATA EXPLORATION
# ==================================================================================

print("\n" + "="*100)
print("DATA EXPLORATION - UNDERSTANDING EACH VARIABLE")
print("="*100)

# Create output directory
import os
os.makedirs('analysis_outputs', exist_ok=True)

# Separate numeric and categorical columns
numeric_cols = df_combined.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df_combined.select_dtypes(include=['object', 'bool']).columns.tolist()

# Remove label
if 'call_duration_group' in numeric_cols:
    numeric_cols.remove('call_duration_group')
if 'call_duration_group' in categorical_cols:
    categorical_cols.remove('call_duration_group')

print(f"\nVariable types:")
print(f"  Numeric variables: {len(numeric_cols)}")
print(f"  Categorical variables: {len(categorical_cols)}")

# ==================================================================================
# DETAILED COLUMN ANALYSIS
# ==================================================================================

print("\n" + "="*100)
print("DETAILED COLUMN-BY-COLUMN ANALYSIS")
print("="*100)

column_analysis = []

for col in df_combined.columns:
    if col == 'call_duration_group':
        continue
    
    analysis = {
        'Column': col,
        'Data_Type': str(df_combined[col].dtype),
        'Total_Count': len(df_combined),
        'Missing_Count': df_combined[col].isnull().sum(),
        'Missing_Pct': (df_combined[col].isnull().sum() / len(df_combined)) * 100,
        'Unique_Values': df_combined[col].nunique()
    }
    
    if col in numeric_cols:
        analysis['Min'] = df_combined[col].min()
        analysis['Max'] = df_combined[col].max()
        analysis['Mean'] = df_combined[col].mean()
        analysis['Median'] = df_combined[col].median()
        analysis['Std'] = df_combined[col].std()
    else:
        # Categorical
        value_counts = df_combined[col].value_counts()
        if len(value_counts) > 0:
            analysis['Most_Common'] = value_counts.index[0]
            analysis['Most_Common_Count'] = value_counts.iloc[0]
            analysis['Most_Common_Pct'] = (value_counts.iloc[0] / len(df_combined)) * 100
        else:
            analysis['Most_Common'] = 'N/A'
            analysis['Most_Common_Count'] = 0
            analysis['Most_Common_Pct'] = 0
    
    column_analysis.append(analysis)

df_column_analysis = pd.DataFrame(column_analysis)
df_column_analysis.to_csv('analysis_outputs/01_column_analysis_summary.csv', index=False)

print("\nColumn Analysis Summary (Top 20 by Missing %):")
print("-" * 100)
print(df_column_analysis.nlargest(20, 'Missing_Pct')[
    ['Column', 'Data_Type', 'Missing_Pct', 'Unique_Values']
].to_string(index=False))

# ==================================================================================
# CATEGORICAL VARIABLE ANALYSIS - UNDERSTANDING DISTRIBUTIONS
# ==================================================================================

print("\n" + "="*100)
print("CATEGORICAL VARIABLE ANALYSIS - VALUE DISTRIBUTIONS")
print("="*100)

categorical_distribution_analysis = []

for col in categorical_cols:
    print(f"\nAnalyzing: {col}")
    print("-" * 80)
    
    # Get value counts for each group
    short_values = df_short_filtered[col].value_counts()
    long_values = df_long_filtered[col].value_counts()
    
    # Get all unique values
    all_values = set(short_values.index) | set(long_values.index)
    
    print(f"  Unique values: {len(all_values)}")
    print(f"  Missing: {df_combined[col].isnull().sum()} ({(df_combined[col].isnull().sum()/len(df_combined)*100):.1f}%)")
    
    # Show top 10 values
    combined_values = df_combined[col].value_counts().head(10)
    print(f"  Top 10 values:")
    for val, count in combined_values.items():
        pct = (count / len(df_combined)) * 100
        print(f"    {val}: {count} ({pct:.1f}%)")
    
    # Analyze each unique value
    for value in all_values:
        if pd.isna(value):
            continue
        
        count_short = (df_short_filtered[col] == value).sum()
        count_long = (df_long_filtered[col] == value).sum()
        total = count_short + count_long
        
        if total > 0:
            pct_long = (count_long / total) * 100
            categorical_distribution_analysis.append({
                'Column': col,
                'Value': str(value),
                'Count_Short': count_short,
                'Count_Long': count_long,
                'Total_Count': total,
                'Pct_Long': pct_long,
                'Favor_Direction': 'Long' if pct_long > 50 else 'Short',
                'Importance_Score': abs(pct_long - 50)
            })

df_cat_dist = pd.DataFrame(categorical_distribution_analysis)
df_cat_dist = df_cat_dist.sort_values('Importance_Score', ascending=False)
df_cat_dist.to_csv('analysis_outputs/01_categorical_distributions.csv', index=False)

print("\n" + "="*100)
print("TOP 30 MOST DISCRIMINATIVE CATEGORICAL VALUES")
print("="*100)
print(df_cat_dist[['Column', 'Value', 'Count_Short', 'Count_Long', 'Pct_Long', 'Favor_Direction']].head(30).to_string(index=False))

# ==================================================================================
# NUMERIC VARIABLE ANALYSIS
# ==================================================================================

print("\n" + "="*100)
print("NUMERIC VARIABLE ANALYSIS - DISTRIBUTIONS")
print("="*100)

numeric_distribution_analysis = []

for col in numeric_cols:
    short_vals = df_short_filtered[col].dropna()
    long_vals = df_long_filtered[col].dropna()
    
    if len(short_vals) == 0 or len(long_vals) == 0:
        continue
    
    analysis = {
        'Column': col,
        'Short_Mean': short_vals.mean(),
        'Long_Mean': long_vals.mean(),
        'Short_Median': short_vals.median(),
        'Long_Median': long_vals.median(),
        'Short_Std': short_vals.std(),
        'Long_Std': long_vals.std(),
        'Mean_Difference': long_vals.mean() - short_vals.mean(),
        'Median_Difference': long_vals.median() - short_vals.median()
    }
    
    if short_vals.mean() != 0:
        analysis['Pct_Difference'] = ((long_vals.mean() - short_vals.mean()) / abs(short_vals.mean())) * 100
    else:
        analysis['Pct_Difference'] = 0
    
    numeric_distribution_analysis.append(analysis)
    
    print(f"\n{col}:")
    print(f"  Short calls: Mean={short_vals.mean():.2f}, Median={short_vals.median():.2f}, Std={short_vals.std():.2f}")
    print(f"  Long calls:  Mean={long_vals.mean():.2f}, Median={long_vals.median():.2f}, Std={long_vals.std():.2f}")
    print(f"  Difference:  {analysis['Mean_Difference']:.2f} ({analysis['Pct_Difference']:.1f}%)")

df_numeric_dist = pd.DataFrame(numeric_distribution_analysis)
df_numeric_dist = df_numeric_dist.sort_values('Mean_Difference', key=abs, ascending=False)
df_numeric_dist.to_csv('analysis_outputs/01_numeric_distributions.csv', index=False)

# ==================================================================================
# SAVE PROCESSED DATA
# ==================================================================================

print("\n" + "="*100)
print("SAVING PROCESSED DATA")
print("="*100)

df_short_filtered.to_csv('analysis_outputs/01_short_calls_data.csv', index=False)
df_long_filtered.to_csv('analysis_outputs/01_long_calls_data.csv', index=False)
df_combined.to_csv('analysis_outputs/01_combined_data.csv', index=False)

print(f"\n[OK] Saved: 01_short_calls_data.csv ({df_short_filtered.shape})")
print(f"[OK] Saved: 01_long_calls_data.csv ({df_long_filtered.shape})")
print(f"[OK] Saved: 01_combined_data.csv ({df_combined.shape})")

# ==================================================================================
# PREPROCESSING RECOMMENDATIONS
# ==================================================================================

print("\n" + "="*100)
print("PREPROCESSING RECOMMENDATIONS")
print("="*100)

print("\n1. HIGH CARDINALITY CATEGORICAL VARIABLES (>50 unique values):")
high_card_cols = df_column_analysis[
    (df_column_analysis['Data_Type'] == 'object') & 
    (df_column_analysis['Unique_Values'] > 50)
]['Column'].tolist()

if high_card_cols:
    for col in high_card_cols:
        print(f"   - {col}: {df_combined[col].nunique()} unique values")
    print(f"   Recommendation: Use Target Encoding or Group Rare Categories")
else:
    print("   None found")

print("\n2. LOW CARDINALITY CATEGORICAL VARIABLES (2-10 unique values):")
low_card_cols = df_column_analysis[
    (df_column_analysis['Data_Type'] == 'object') & 
    (df_column_analysis['Unique_Values'] >= 2) &
    (df_column_analysis['Unique_Values'] <= 10)
]['Column'].tolist()

if low_card_cols:
    for col in low_card_cols:
        print(f"   - {col}: {df_combined[col].nunique()} unique values")
    print(f"   Recommendation: Use One-Hot Encoding")
else:
    print("   None found")

print("\n3. MEDIUM CARDINALITY CATEGORICAL VARIABLES (11-50 unique values):")
med_card_cols = df_column_analysis[
    (df_column_analysis['Data_Type'] == 'object') & 
    (df_column_analysis['Unique_Values'] > 10) &
    (df_column_analysis['Unique_Values'] <= 50)
]['Column'].tolist()

if med_card_cols:
    for col in med_card_cols:
        print(f"   - {col}: {df_combined[col].nunique()} unique values")
    print(f"   Recommendation: Use Frequency Encoding or Target Encoding")
else:
    print("   None found")

print("\n4. HIGH MISSING VALUE COLUMNS (>30% missing):")
high_missing_cols = df_column_analysis[df_column_analysis['Missing_Pct'] > 30]['Column'].tolist()

if high_missing_cols:
    for col in high_missing_cols:
        pct = df_column_analysis[df_column_analysis['Column'] == col]['Missing_Pct'].values[0]
        print(f"   - {col}: {pct:.1f}% missing")
    print(f"   Recommendation: Consider creating 'Missing' indicator or imputation strategy")
else:
    print("   None found")

# Save recommendations
recommendations = {
    'High Cardinality (>50)': high_card_cols,
    'Medium Cardinality (11-50)': med_card_cols,
    'Low Cardinality (2-10)': low_card_cols,
    'High Missing (>30%)': high_missing_cols
}

with open('analysis_outputs/01_preprocessing_recommendations.txt', 'w') as f:
    f.write("PREPROCESSING RECOMMENDATIONS\n")
    f.write("="*80 + "\n\n")
    for category, cols in recommendations.items():
        f.write(f"{category}:\n")
        if cols:
            for col in cols:
                f.write(f"  - {col}\n")
        else:
            f.write("  None\n")
        f.write("\n")

print("\n" + "="*100)
print("DATA EXPLORATION AND PREPROCESSING COMPLETE")
print("="*100)
print("\nNext steps:")
print("  1. Review the column analysis and distribution files")
print("  2. Proceed to intelligent encoding and correlation analysis")
print("  3. Build comprehensive statistical analysis")

