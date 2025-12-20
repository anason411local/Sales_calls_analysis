"""
ENHANCED STATISTICAL ANALYSIS - Including TO_OMC_Duration
Comprehensive analysis with all required variables
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import chi2_contingency, mannwhitneyu, ttest_ind, pearsonr
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("ENHANCED STATISTICAL ANALYSIS - WITH TO_OMC_DURATION")
print("="*100)

# Load data
df_short = pd.read_csv('Less_than_4.88_mnt..csv')
df_long = pd.read_csv('greater_than_4.88_mnt..csv')

df_short['call_duration_group'] = 0
df_long['call_duration_group'] = 1

# Updated column removal list (KEEP TO_OMC_Duration this time!)
cols_to_remove = [
    'TO_Lead_ID', 'TO_Phone', 'TO_Status', 'TO_Campaing_ID', 'TO_Recording_Link',
    'TO_Transcription_VICI(0-32000) Words', 'TO_Transcription_VICI(32001-64000) Words',
    'TO_Transcription_VICI(64000+ Words)', 'TO_OMC_Campaign_ID', 'TO_OMC_Recording_Link',
    'TO_OMC_User_Group', 'TO_OMC_Transcription_VICI', 
    'TO_OMC_Transcription_VICI(32000-64000)Words', 
    'TO_OMC_Transcription_VICI(64000+ Words)', 'customer_name', 'customer_address',
    'lgs_error_message'
]

df_short = df_short.drop(columns=[col for col in cols_to_remove if col in df_short.columns])
df_long = df_long.drop(columns=[col for col in cols_to_remove if col in df_long.columns])

print(f"\nShort calls: {df_short.shape}")
print(f"Long calls: {df_long.shape}")

# Verify TO_OMC_Duration is present
if 'TO_OMC_Duration' in df_short.columns:
    print("\n[OK] TO_OMC_Duration is included in analysis")
    print(f"Short calls - TO_OMC_Duration range: {df_short['TO_OMC_Duration'].min():.1f} to {df_short['TO_OMC_Duration'].max():.1f} seconds")
    print(f"Long calls - TO_OMC_Duration range: {df_long['TO_OMC_Duration'].min():.1f} to {df_long['TO_OMC_Duration'].max():.1f} seconds")
else:
    print("\n[WARNING] TO_OMC_Duration not found in dataset!")

# Combine
df_combined = pd.concat([df_short, df_long], ignore_index=True)

# Save for later use
df_short.to_csv('analysis_outputs/enhanced_short_calls_data.csv', index=False)
df_long.to_csv('analysis_outputs/enhanced_long_calls_data.csv', index=False)
df_combined.to_csv('analysis_outputs/enhanced_combined_data.csv', index=False)

print(f"\nCombined dataset: {df_combined.shape}")

# Separate numeric and categorical
numeric_cols = df_combined.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df_combined.select_dtypes(include=['object', 'bool']).columns.tolist()

if 'call_duration_group' in numeric_cols:
    numeric_cols.remove('call_duration_group')
if 'call_duration_group' in categorical_cols:
    categorical_cols.remove('call_duration_group')

print(f"\nNumeric columns: {len(numeric_cols)}")
print(f"Categorical columns: {len(categorical_cols)}")

# ==================================================================================
# NUMERIC VARIABLES ANALYSIS
# ==================================================================================
print("\n" + "="*100)
print("NUMERIC VARIABLES ANALYSIS (INCLUDING TO_OMC_DURATION)")
print("="*100)

numeric_results = []

for col in numeric_cols:
    short_vals = df_short[col].dropna()
    long_vals = df_long[col].dropna()
    
    if len(short_vals) < 3 or len(long_vals) < 3:
        continue
    
    # Descriptive stats
    short_mean = short_vals.mean()
    long_mean = long_vals.mean()
    short_median = short_vals.median()
    long_median = long_vals.median()
    short_std = short_vals.std()
    long_std = long_vals.std()
    
    # Test for normality
    sample_size = min(100, len(short_vals), len(long_vals))
    short_sample = short_vals.sample(min(sample_size, len(short_vals)), random_state=42)
    long_sample = long_vals.sample(min(sample_size, len(long_vals)), random_state=42)
    
    try:
        _, short_p_norm = stats.shapiro(short_sample)
        _, long_p_norm = stats.shapiro(long_sample)
        is_normal = (short_p_norm > 0.05) and (long_p_norm > 0.05)
    except:
        is_normal = False
    
    # Choose appropriate test
    if is_normal:
        statistic, p_value = ttest_ind(short_vals, long_vals, equal_var=False)
        test_used = 't-test'
    else:
        statistic, p_value = mannwhitneyu(short_vals, long_vals, alternative='two-sided')
        test_used = 'Mann-Whitney U'
    
    # Effect size (Cohen's d)
    pooled_std = np.sqrt((short_std**2 + long_std**2) / 2)
    if pooled_std > 0:
        cohens_d = (long_mean - short_mean) / pooled_std
    else:
        cohens_d = 0
    
    # Percentage difference
    if short_mean != 0:
        pct_diff = ((long_mean - short_mean) / abs(short_mean)) * 100
    else:
        pct_diff = 0
    
    numeric_results.append({
        'Variable': col,
        'Short_Mean': short_mean,
        'Long_Mean': long_mean,
        'Short_Median': short_median,
        'Long_Median': long_median,
        'Short_Std': short_std,
        'Long_Std': long_std,
        'Difference': long_mean - short_mean,
        'Pct_Difference': pct_diff,
        'P_Value': p_value,
        'Test': test_used,
        'Cohens_D': cohens_d,
        'Effect_Size': 'Large' if abs(cohens_d) > 0.8 else ('Medium' if abs(cohens_d) > 0.5 else 'Small'),
        'Significant': 'Yes' if p_value < 0.05 else 'No',
        'N_Short': len(short_vals),
        'N_Long': len(long_vals)
    })

df_numeric_results = pd.DataFrame(numeric_results).sort_values('P_Value')
df_numeric_results.to_csv('analysis_outputs/enhanced_numeric_variables_tests.csv', index=False)

print(f"\n[OK] Enhanced numeric tests saved: analysis_outputs/enhanced_numeric_variables_tests.csv")
print(f"\nTop 20 Most Significant Variables:")
print("-" * 100)
display_cols = ['Variable', 'Short_Mean', 'Long_Mean', 'Difference', 'Pct_Difference', 'P_Value', 'Cohens_D']
print(df_numeric_results[display_cols].head(20).to_string(index=False))

# ==================================================================================
# CATEGORICAL VARIABLES ANALYSIS
# ==================================================================================
print("\n" + "="*100)
print("CATEGORICAL VARIABLES ANALYSIS")
print("="*100)

categorical_results = []

for col in categorical_cols:
    try:
        contingency_table = pd.crosstab(df_combined[col].fillna('Missing'), 
                                        df_combined['call_duration_group'])
        
        if contingency_table.shape[0] > 1 and contingency_table.shape[1] > 1:
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
            
            n = contingency_table.sum().sum()
            min_dim = min(contingency_table.shape[0] - 1, contingency_table.shape[1] - 1)
            cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
            
            short_mode = df_short[col].mode()[0] if len(df_short[col].mode()) > 0 else 'N/A'
            long_mode = df_long[col].mode()[0] if len(df_long[col].mode()) > 0 else 'N/A'
            
            categorical_results.append({
                'Variable': col,
                'Short_Most_Common': short_mode,
                'Long_Most_Common': long_mode,
                'Chi_Square': chi2,
                'P_Value': p_value,
                'Cramers_V': cramers_v,
                'Effect_Size': 'Large' if cramers_v > 0.25 else ('Medium' if cramers_v > 0.15 else 'Small'),
                'Significant': 'Yes' if p_value < 0.05 else 'No',
                'N_Categories': contingency_table.shape[0]
            })
    except Exception as e:
        continue

df_categorical_results = pd.DataFrame(categorical_results).sort_values('P_Value')
df_categorical_results.to_csv('analysis_outputs/enhanced_categorical_variables_tests.csv', index=False)

print(f"\n[OK] Enhanced categorical tests saved: analysis_outputs/enhanced_categorical_variables_tests.csv")
print(f"\nTop 20 Most Significant Categorical Variables:")
print("-" * 100)
display_cols_cat = ['Variable', 'Short_Most_Common', 'Long_Most_Common', 'P_Value', 'Cramers_V']
print(df_categorical_results[display_cols_cat].head(20).to_string(index=False))

print("\n" + "="*100)
print("ENHANCED STATISTICAL ANALYSIS COMPLETE")
print("="*100)

