"""
==============================================================================
LEVEL 1: VARIABLE-LEVEL STATISTICAL TESTS
==============================================================================

Purpose: Perform statistical tests at the variable level
- Compare 49 variables between Short vs Long calls
- T-tests / Mann-Whitney U tests for numerical variables
- Chi-square tests for categorical variables
- Effect sizes (Cohen's D, Cramer's V)
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
        
        # Cramer's V (effect size)
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
    print(f"    Short: {row['Short_Mean']:.2f} +/- {row['Short_Std']:.2f}")
    print(f"    Long:  {row['Long_Mean']:.2f} +/- {row['Long_Std']:.2f}")

# Top categorical variables
print("\nTOP 10 CATEGORICAL VARIABLES (by effect size):")
print("-" * 100)
for idx, row in df_categorical_tests.head(10).iterrows():
    sig = "***" if row['Significant'] == 'Yes' else ""
    print(f"  {row['Variable']}: Cramer's V = {row['Cramers_V']:.3f} ({row['Effect_Size']}) {sig}")
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

# ==============================================================================
# STATISTICAL VISUALIZATIONS
# ==============================================================================

print("\n" + "="*100)
print("CREATING STATISTICAL VISUALIZATIONS")
print("="*100)

import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ==============================
# VIZ 1: P-VALUE DISTRIBUTION
# ==============================

print("\nCreating p-value distributions...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Numerical p-values
axes[0].hist(df_numerical_tests['Mann_Whitney_PValue'], bins=20, 
             color='#4ECDC4', alpha=0.7, edgecolor='black', linewidth=1.5)
axes[0].axvline(0.05, color='red', linestyle='--', linewidth=2, label='p=0.05 threshold')
axes[0].set_xlabel('P-Value (Mann-Whitney U Test)', fontsize=11, fontweight='bold')
axes[0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
axes[0].set_title(f'Numerical Variables P-Value Distribution\n{n_sig_numerical}/{len(df_numerical_tests)} Significant',
                  fontsize=12, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].grid(alpha=0.3)

# Categorical p-values
axes[1].hist(df_categorical_tests['Chi_Square_PValue'], bins=20,
             color='#FF6B6B', alpha=0.7, edgecolor='black', linewidth=1.5)
axes[1].axvline(0.05, color='red', linestyle='--', linewidth=2, label='p=0.05 threshold')
axes[1].set_xlabel('P-Value (Chi-Square Test)', fontsize=11, fontweight='bold')
axes[1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
axes[1].set_title(f'Categorical Variables P-Value Distribution\n{n_sig_categorical}/{len(df_categorical_tests)} Significant',
                  fontsize=12, fontweight='bold')
axes[1].legend(fontsize=10)
axes[1].grid(alpha=0.3)

plt.suptitle('LEVEL 1: P-VALUE DISTRIBUTIONS\nValues below red line = Statistically significant',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/04_stat_pvalue_distributions.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 04_stat_pvalue_distributions.png")
plt.close()

# ==============================
# VIZ 2: EFFECT SIZE VS P-VALUE
# ==============================

print("Creating effect size vs p-value scatter...")
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Numerical
axes[0].scatter(df_numerical_tests['Abs_Cohens_D'], 
                -np.log10(df_numerical_tests['Mann_Whitney_PValue']),
                s=100, alpha=0.6, c=df_numerical_tests['Abs_Cohens_D'],
                cmap='viridis', edgecolors='black', linewidth=1)
axes[0].axhline(-np.log10(0.05), color='red', linestyle='--', linewidth=2, label='p=0.05')
axes[0].set_xlabel('Effect Size (|Cohen\'s D|)', fontsize=11, fontweight='bold')
axes[0].set_ylabel('-log10(p-value)', fontsize=11, fontweight='bold')
axes[0].set_title('Numerical Variables: Effect Size vs Significance\nTop-right = Large effect + Significant',
                  fontsize=12, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].grid(alpha=0.3)

# Categorical
axes[1].scatter(df_categorical_tests['Cramers_V'],
                -np.log10(df_categorical_tests['Chi_Square_PValue']),
                s=100, alpha=0.6, c=df_categorical_tests['Cramers_V'],
                cmap='plasma', edgecolors='black', linewidth=1)
axes[1].axhline(-np.log10(0.05), color='red', linestyle='--', linewidth=2, label='p=0.05')
axes[1].set_xlabel('Effect Size (Cramer\'s V)', fontsize=11, fontweight='bold')
axes[1].set_ylabel('-log10(p-value)', fontsize=11, fontweight='bold')
axes[1].set_title('Categorical Variables: Effect Size vs Significance\nTop-right = Large effect + Significant',
                  fontsize=12, fontweight='bold')
axes[1].legend(fontsize=10)
axes[1].grid(alpha=0.3)

plt.suptitle('LEVEL 1: EFFECT SIZE vs STATISTICAL SIGNIFICANCE\nBest variables are in top-right (large effect + low p-value)',
             fontsize=14, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/04_stat_effect_vs_pvalue.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 04_stat_effect_vs_pvalue.png")
plt.close()

# ==============================
# VIZ 3: MEAN DIFFERENCES (NUMERICAL)
# ==============================

print("Creating mean differences plot...")
fig, ax = plt.subplots(figsize=(12, 10))

df_num_sorted = df_numerical_tests.sort_values('Mean_Diff', ascending=False).head(20)

colors = ['#4ECDC4' if sig == 'Yes' else '#FF6B6B' for sig in df_num_sorted['Significant_MW']]
bars = ax.barh(range(len(df_num_sorted)), df_num_sorted['Mean_Diff'],
               color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_yticks(range(len(df_num_sorted)))
ax.set_yticklabels(df_num_sorted['Variable'], fontsize=10)
ax.set_xlabel('Mean Difference (Long - Short calls)', fontsize=12, fontweight='bold')
ax.set_title('LEVEL 1: TOP 20 NUMERICAL VARIABLES BY MEAN DIFFERENCE\n' +
             'POSITIVE = Higher in Long Calls | NEGATIVE = Higher in Short Calls\n' +
             'TEAL = Significant | RED = Not Significant',
             fontsize=13, fontweight='bold', pad=20)
ax.invert_yaxis()
ax.axvline(0, color='black', linestyle='-', linewidth=1)
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, df_num_sorted['Mean_Diff'])):
    x_pos = val + (abs(val) * 0.05 if val > 0 else -abs(val) * 0.05)
    ax.text(x_pos, i, f'{val:.2f}',
            va='center', ha='left' if val > 0 else 'right',
            fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/04_stat_mean_differences.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 04_stat_mean_differences.png")
plt.close()

# ==============================
# VIZ 4: SIGNIFICANCE SUMMARY
# ==============================

print("Creating significance summary...")
fig, ax = plt.subplots(figsize=(10, 8))

summary_data = {
    'Numerical\nVariables': [n_sig_numerical, len(df_numerical_tests) - n_sig_numerical],
    'Categorical\nVariables': [n_sig_categorical, len(df_categorical_tests) - n_sig_categorical]
}

x = np.arange(len(summary_data))
width = 0.6

bottoms = [0] * len(summary_data)
colors_sig = ['#4ECDC4', '#45B7D1']
colors_nonsig = ['#FF6B6B', '#F7DC6F']

sig_counts = [summary_data[k][0] for k in summary_data.keys()]
nonsig_counts = [summary_data[k][1] for k in summary_data.keys()]

bars1 = ax.bar(x, sig_counts, width, label='Significant (p<0.05)',
               color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x, nonsig_counts, width, bottom=sig_counts, label='Not Significant',
               color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)

# Add value labels
for i, (sig, nonsig, total) in enumerate(zip(sig_counts, nonsig_counts, 
                                              [sig_counts[j] + nonsig_counts[j] for j in range(len(sig_counts))])):
    ax.text(i, sig/2, f'{sig}\n({sig/total*100:.1f}%)',
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    ax.text(i, sig + nonsig/2, f'{nonsig}\n({nonsig/total*100:.1f}%)',
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')

ax.set_ylabel('Number of Variables', fontsize=12, fontweight='bold')
ax.set_title('LEVEL 1: STATISTICAL SIGNIFICANCE SUMMARY\nHow many variables show significant differences?',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(summary_data.keys(), fontsize=11, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/04_stat_significance_summary.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 04_stat_significance_summary.png")
plt.close()

print("\n[OK] Created 4 statistical visualizations")

print("\n" + "="*100)
print("LEVEL 1 STATISTICAL TESTS COMPLETE")
print("="*100)
print(f"\n[OK] Tested {len(feature_cols)} variables")
print(f"[OK] Significant: {n_sig_numerical + n_sig_categorical}/{len(feature_cols)}")
print(f"[OK] Large effect sizes: {((df_numerical_tests['Effect_Size'] == 'Large').sum() + (df_categorical_tests['Effect_Size'] == 'Large').sum())}")

