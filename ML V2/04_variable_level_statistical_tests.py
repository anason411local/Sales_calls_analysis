"""
==============================================================================
LEVEL 1: VARIABLE-LEVEL STATISTICAL TESTS
==============================================================================

Purpose: Perform statistical tests at the variable level
- Compare 49 variables between Short vs Long calls
- T-tests / Mann-Whitney U tests for numerical variables
- Chi-square tests for categorical variables
- Effect sizes (Cohen's D, Cramér's V)
- Point-biserial correlation with target

==============================================================================
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import mannwhitneyu, chi2_contingency, pointbiserialr
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("LEVEL 1: VARIABLE-LEVEL STATISTICAL TESTS")
print("="*100)

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("\nLoading data...")
df_short = pd.read_csv('analysis_outputs/level1_variable/01_short_calls_original.csv')
df_long = pd.read_csv('analysis_outputs/level1_variable/01_long_calls_original.csv')
df_combined = pd.read_csv('analysis_outputs/level1_variable/01_combined_original.csv')

print(f"Short calls: {len(df_short)}")
print(f"Long calls: {len(df_long)}")

# Get feature columns
feature_cols = [c for c in df_combined.columns if c not in ['target', 'call_duration_group']]

# ==============================================================================
# IDENTIFY VARIABLE TYPES
# ==============================================================================

print("\n" + "="*100)
print("IDENTIFYING VARIABLE TYPES")
print("="*100)

categorical_vars = []
numerical_vars = []

for col in feature_cols:
    if df_combined[col].dtype in ['object', 'bool'] or df_combined[col].nunique() < 50:
        categorical_vars.append(col)
    else:
        numerical_vars.append(col)

print(f"\nCategorical variables: {len(categorical_vars)}")
print(f"Numerical variables: {len(numerical_vars)}")

# ==============================================================================
# STATISTICAL TESTS: NUMERICAL VARIABLES
# ==============================================================================

print("\n" + "="*100)
print("STATISTICAL TESTS: NUMERICAL VARIABLES")
print("="*100)

numerical_results = []

for var in numerical_vars:
    print(f"Testing: {var}")
    
    short_vals = df_short[var].dropna()
    long_vals = df_long[var].dropna()
    
    if len(short_vals) < 3 or len(long_vals) < 3:
        continue
    
    # Descriptive statistics
    short_mean = short_vals.mean()
    long_mean = long_vals.mean()
    short_median = short_vals.median()
    long_median = long_vals.median()
    short_std = short_vals.std()
    long_std = long_vals.std()
    
    # T-test (parametric)
    t_stat, t_pval = stats.ttest_ind(short_vals, long_vals, nan_policy='omit')
    
    # Mann-Whitney U test (non-parametric)
    u_stat, u_pval = mannwhitneyu(short_vals, long_vals, alternative='two-sided')
    
    # Cohen's D (effect size)
    pooled_std = np.sqrt((short_std**2 + long_std**2) / 2)
    cohens_d = (long_mean - short_mean) / pooled_std if pooled_std > 0 else 0
    
    # Point-biserial correlation
    combined_vals = df_combined[var].dropna()
    combined_target = df_combined.loc[combined_vals.index, 'target']
    
    if len(combined_vals) >= 30:
        try:
            pb_corr, pb_pval = pointbiserialr(combined_target, combined_vals)
        except:
            pb_corr, pb_pval = 0, 1.0
    else:
        pb_corr, pb_pval = 0, 1.0
    
    numerical_results.append({
        'Variable': var,
        'Type': 'Numerical',
        'Short_Mean': short_mean,
        'Long_Mean': long_mean,
        'Short_Median': short_median,
        'Long_Median': long_median,
        'Short_Std': short_std,
        'Long_Std': long_std,
        'Mean_Diff': long_mean - short_mean,
        'Median_Diff': long_median - short_median,
        'T_Statistic': t_stat,
        'T_PValue': t_pval,
        'Mann_Whitney_U': u_stat,
        'Mann_Whitney_PValue': u_pval,
        'Cohens_D': cohens_d,
        'Abs_Cohens_D': abs(cohens_d),
        'Effect_Size': 'Large' if abs(cohens_d) > 0.8 else ('Medium' if abs(cohens_d) > 0.5 else ('Small' if abs(cohens_d) > 0.2 else 'Negligible')),
        'PointBiserial_Corr': pb_corr,
        'PointBiserial_PValue': pb_pval,
        'Significant_T': 'Yes' if t_pval < 0.05 else 'No',
        'Significant_MW': 'Yes' if u_pval < 0.05 else 'No',
        'N_Short': len(short_vals),
        'N_Long': len(long_vals)
    })

df_numerical_tests = pd.DataFrame(numerical_results)
df_numerical_tests = df_numerical_tests.sort_values('Abs_Cohens_D', ascending=False)

print(f"\n[OK] Tested {len(numerical_results)} numerical variables")

# ==============================================================================
# STATISTICAL TESTS: CATEGORICAL VARIABLES
# ==============================================================================

print("\n" + "="*100)
print("STATISTICAL TESTS: CATEGORICAL VARIABLES")
print("="*100)

categorical_results = []

for var in categorical_vars:
    print(f"Testing: {var}")
    
    # Create contingency table
    contingency = pd.crosstab(df_combined[var], df_combined['target'])
    
    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        continue
    
    # Chi-square test
    try:
        chi2, chi2_pval, dof, expected = chi2_contingency(contingency)
        
        # Cramér's V (effect size)
        n = contingency.sum().sum()
        min_dim = min(contingency.shape[0] - 1, contingency.shape[1] - 1)
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if n > 0 and min_dim > 0 else 0
    except:
        chi2, chi2_pval, cramers_v = 0, 1.0, 0
    
    # Mode for each group
    short_mode = df_short[var].mode()[0] if len(df_short[var].mode()) > 0 else None
    long_mode = df_long[var].mode()[0] if len(df_long[var].mode()) > 0 else None
    
    categorical_results.append({
        'Variable': var,
        'Type': 'Categorical',
        'Short_Mode': str(short_mode),
        'Long_Mode': str(long_mode),
        'Unique_Values': df_combined[var].nunique(),
        'Chi_Square': chi2,
        'Chi_Square_PValue': chi2_pval,
        'Degrees_of_Freedom': dof if 'dof' in locals() else 0,
        'Cramers_V': cramers_v,
        'Effect_Size': 'Large' if cramers_v > 0.5 else ('Medium' if cramers_v > 0.3 else ('Small' if cramers_v > 0.1 else 'Negligible')),
        'Significant': 'Yes' if chi2_pval < 0.05 else 'No',
        'N_Short': len(df_short[var].dropna()),
        'N_Long': len(df_long[var].dropna())
    })

df_categorical_tests = pd.DataFrame(categorical_results)
df_categorical_tests = df_categorical_tests.sort_values('Cramers_V', ascending=False)

print(f"\n[OK] Tested {len(categorical_results)} categorical variables")

# ==============================================================================
# COMBINE AND SUMMARIZE
# ==============================================================================

print("\n" + "="*100)
print("SUMMARY OF STATISTICAL TESTS")
print("="*100)

# Top numerical variables
print("\nTOP 10 NUMERICAL VARIABLES (by effect size):")
print("-" * 100)
for idx, row in df_numerical_tests.head(10).iterrows():
    sig = "***" if row['Significant_MW'] == 'Yes' else ""
    print(f"  {row['Variable']}: Cohen's D = {row['Cohens_D']:.3f} ({row['Effect_Size']}) {sig}")
    print(f"    Short: {row['Short_Mean']:.2f} ± {row['Short_Std']:.2f}")
    print(f"    Long:  {row['Long_Mean']:.2f} ± {row['Long_Std']:.2f}")

# Top categorical variables
print("\nTOP 10 CATEGORICAL VARIABLES (by effect size):")
print("-" * 100)
for idx, row in df_categorical_tests.head(10).iterrows():
    sig = "***" if row['Significant'] == 'Yes' else ""
    print(f"  {row['Variable']}: Cramér's V = {row['Cramers_V']:.3f} ({row['Effect_Size']}) {sig}")
    print(f"    Short mode: {row['Short_Mode']}")
    print(f"    Long mode:  {row['Long_Mode']}")

# Overall statistics
n_sig_numerical = (df_numerical_tests['Significant_MW'] == 'Yes').sum()
n_sig_categorical = (df_categorical_tests['Significant'] == 'Yes').sum()

print(f"\n[OK] Significant numerical variables: {n_sig_numerical}/{len(df_numerical_tests)}")
print(f"[OK] Significant categorical variables: {n_sig_categorical}/{len(df_categorical_tests)}")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

print("\n" + "="*100)
print("SAVING RESULTS")
print("="*100)

df_numerical_tests.to_csv('analysis_outputs/level1_variable/04_statistical_tests_numerical.csv', index=False)
df_categorical_tests.to_csv('analysis_outputs/level1_variable/04_statistical_tests_categorical.csv', index=False)

# Combined summary
df_combined_tests = pd.concat([
    df_numerical_tests[['Variable', 'Type', 'Significant_MW', 'Abs_Cohens_D']].rename(columns={'Significant_MW': 'Significant', 'Abs_Cohens_D': 'Effect_Size_Value'}),
    df_categorical_tests[['Variable', 'Type', 'Significant', 'Cramers_V']].rename(columns={'Cramers_V': 'Effect_Size_Value'})
], ignore_index=True)

df_combined_tests = df_combined_tests.sort_values('Effect_Size_Value', ascending=False)
df_combined_tests.to_csv('analysis_outputs/level1_variable/04_statistical_tests_combined.csv', index=False)

print("\n[OK] Saved CSV files:")
print("  - 04_statistical_tests_numerical.csv")
print("  - 04_statistical_tests_categorical.csv")
print("  - 04_statistical_tests_combined.csv")

print("\n" + "="*100)
print("LEVEL 1 STATISTICAL TESTS COMPLETE")
print("="*100)
print(f"\n[OK] Tested {len(feature_cols)} variables")
print(f"[OK] Significant: {n_sig_numerical + n_sig_categorical}/{len(feature_cols)}")
print(f"[OK] Large effect sizes: {((df_numerical_tests['Effect_Size'] == 'Large').sum() + (df_categorical_tests['Effect_Size'] == 'Large').sum())}")

