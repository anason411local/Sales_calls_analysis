"""
==============================================================================
LEVEL 1: VARIABLE-LEVEL STATISTICAL TESTS (FIXED VERSION WITH LABELS)
==============================================================================

Purpose: Perform statistical tests at the variable level
- Compare 49 variables between Short vs Long calls
- T-tests / Mann-Whitney U tests for numerical variables
- Chi-square tests for categorical variables
- Effect sizes (Cohen's D, Cramer's V)
- Point-biserial correlation with target

FIXED: Added variable labels to the Effect Size vs P-Value scatter plot

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
    if df_combined[col].dtype in ['object', 'bool'] or df_combined[col].nunique() < 20:
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
    
    # Mann-Whitney U test (non-parametric)
    stat_mw, p_mw = mannwhitneyu(short_vals, long_vals, alternative='two-sided')
    
    # Cohen's D effect size
    mean_short = short_vals.mean()
    mean_long = long_vals.mean()
    std_short = short_vals.std()
    std_long = long_vals.std()
    
    pooled_std = np.sqrt(((len(short_vals)-1)*std_short**2 + (len(long_vals)-1)*std_long**2) / 
                          (len(short_vals) + len(long_vals) - 2))
    
    cohens_d = (mean_long - mean_short) / pooled_std if pooled_std > 0 else 0
    
    # Effect size interpretation
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        effect_size = "Negligible"
    elif abs_d < 0.5:
        effect_size = "Small"
    elif abs_d < 0.8:
        effect_size = "Medium"
    else:
        effect_size = "Large"
    
    numerical_results.append({
        'Variable': var,
        'Type': 'Numerical',
        'Short_Mean': mean_short,
        'Short_Std': std_short,
        'Long_Mean': mean_long,
        'Long_Std': std_long,
        'Mean_Diff': mean_long - mean_short,
        'Mann_Whitney_Stat': stat_mw,
        'Mann_Whitney_PValue': p_mw,
        'Significant_MW': 'Yes' if p_mw < 0.05 else 'No',
        'Cohens_D': cohens_d,
        'Abs_Cohens_D': abs_d,
        'Effect_Size': effect_size
    })

df_numerical_tests = pd.DataFrame(numerical_results).sort_values('Abs_Cohens_D', ascending=False)

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
    contingency = pd.crosstab(df_combined[var].fillna('Missing'), 
                               df_combined['call_duration_group'])
    
    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        continue
    
    # Chi-square test
    chi2, p_chi, dof, expected = chi2_contingency(contingency)
    
    # Cramer's V effect size
    n = contingency.sum().sum()
    min_dim = min(contingency.shape[0], contingency.shape[1]) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
    
    # Effect size interpretation
    if cramers_v < 0.1:
        effect_size = "Negligible"
    elif cramers_v < 0.3:
        effect_size = "Small"
    elif cramers_v < 0.5:
        effect_size = "Medium"
    else:
        effect_size = "Large"
    
    # Get mode for each group
    short_mode = df_short[var].mode()[0] if len(df_short[var].mode()) > 0 else 'N/A'
    long_mode = df_long[var].mode()[0] if len(df_long[var].mode()) > 0 else 'N/A'
    
    categorical_results.append({
        'Variable': var,
        'Type': 'Categorical',
        'Short_Mode': short_mode,
        'Long_Mode': long_mode,
        'Chi_Square_Stat': chi2,
        'Chi_Square_PValue': p_chi,
        'Degrees_of_Freedom': dof,
        'Significant': 'Yes' if p_chi < 0.05 else 'No',
        'Cramers_V': cramers_v,
        'Effect_Size': effect_size
    })

df_categorical_tests = pd.DataFrame(categorical_results).sort_values('Cramers_V', ascending=False)

print(f"\n[OK] Tested {len(categorical_results)} categorical variables")

# ==============================================================================
# SUMMARY
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
# STATISTICAL VISUALIZATIONS (FIXED WITH LABELS)
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
# VIZ 2: EFFECT SIZE VS P-VALUE (FIXED WITH LABELS)
# ==============================

print("Creating effect size vs p-value scatter...")
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# NUMERICAL VARIABLES
ax = axes[0]
x_num = df_numerical_tests['Abs_Cohens_D']
y_num = -np.log10(df_numerical_tests['Mann_Whitney_PValue'])

scatter = ax.scatter(x_num, y_num,
                     s=120, alpha=0.6, c=x_num,
                     cmap='viridis', edgecolors='black', linewidth=1.5)

ax.axhline(-np.log10(0.05), color='red', linestyle='--', linewidth=2, label='p=0.05')
ax.set_xlabel('Effect Size (|Cohen\'s D|)', fontsize=12, fontweight='bold')
ax.set_ylabel('-log10(p-value)', fontsize=12, fontweight='bold')
ax.set_title('Numerical Variables: Effect Size vs Significance\nTop-right = Large effect + Significant',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(alpha=0.3)

# Add labels for significant variables with large effect sizes
labeled_count = 0
for idx, row in df_numerical_tests.iterrows():
    x_val = row['Abs_Cohens_D']
    y_val = -np.log10(row['Mann_Whitney_PValue'])
    
    # Label if: significant (p<0.05) OR large effect size (>0.3)
    if y_val > -np.log10(0.05) or x_val > 0.3:
        var_name = row['Variable']
        # Shorten long variable names
        if len(var_name) > 25:
            var_name = var_name[:22] + '...'
        
        # Offset label slightly to avoid overlapping with point
        offset_x = 0.01
        offset_y = 0.05 + (labeled_count % 3) * 0.02  # Stagger labels vertically
        
        ax.annotate(var_name, 
                   xy=(x_val, y_val),
                   xytext=(x_val + offset_x, y_val + offset_y),
                   fontsize=7, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7, edgecolor='black', linewidth=0.5),
                   arrowprops=dict(arrowstyle='->', color='black', lw=0.5, alpha=0.7))
        labeled_count += 1

# CATEGORICAL VARIABLES
ax = axes[1]
x_cat = df_categorical_tests['Cramers_V']
y_cat = -np.log10(df_categorical_tests['Chi_Square_PValue'])

scatter = ax.scatter(x_cat, y_cat,
                     s=120, alpha=0.6, c=x_cat,
                     cmap='plasma', edgecolors='black', linewidth=1.5)

ax.axhline(-np.log10(0.05), color='red', linestyle='--', linewidth=2, label='p=0.05')
ax.set_xlabel('Effect Size (Cramer\'s V)', fontsize=12, fontweight='bold')
ax.set_ylabel('-log10(p-value)', fontsize=12, fontweight='bold')
ax.set_title('Categorical Variables: Effect Size vs Significance\nTop-right = Large effect + Significant',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(alpha=0.3)

# Add labels for significant variables with large effect sizes
labeled_count = 0
for idx, row in df_categorical_tests.iterrows():
    x_val = row['Cramers_V']
    y_val = -np.log10(row['Chi_Square_PValue'])
    
    # Label if: significant (p<0.05) AND medium/large effect (>0.3) OR very large effect (>0.5)
    if (y_val > -np.log10(0.05) and x_val > 0.3) or x_val > 0.5:
        var_name = row['Variable']
        # Shorten long variable names
        if len(var_name) > 25:
            var_name = var_name[:22] + '...'
        
        # Offset label slightly to avoid overlapping with point
        offset_x = 0.02
        offset_y = 0.1 + (labeled_count % 4) * 0.15  # Stagger labels vertically
        
        ax.annotate(var_name,
                   xy=(x_val, y_val),
                   xytext=(x_val + offset_x, y_val + offset_y),
                   fontsize=7, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7, edgecolor='black', linewidth=0.5),
                   arrowprops=dict(arrowstyle='->', color='black', lw=0.5, alpha=0.7))
        labeled_count += 1

plt.suptitle('LEVEL 1: EFFECT SIZE vs STATISTICAL SIGNIFICANCE\nBest variables are in top-right (large effect + low p-value)',
             fontsize=15, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/04_stat_effect_vs_pvalue.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 04_stat_effect_vs_pvalue.png (WITH LABELS)")
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
fig, ax = plt.subplots(figsize=(12, 8))

# Combine top variables from both types
top_vars = pd.concat([
    df_numerical_tests.head(15)[['Variable', 'Abs_Cohens_D', 'Significant_MW']].rename(
        columns={'Abs_Cohens_D': 'Effect_Size', 'Significant_MW': 'Significant'}),
    df_categorical_tests.head(15)[['Variable', 'Cramers_V', 'Significant']].rename(
        columns={'Cramers_V': 'Effect_Size'})
]).sort_values('Effect_Size', ascending=True).tail(25)

colors = ['#4ECDC4' if sig == 'Yes' else '#FF6B6B' for sig in top_vars['Significant']]
bars = ax.barh(range(len(top_vars)), top_vars['Effect_Size'],
               color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_yticks(range(len(top_vars)))
ax.set_yticklabels(top_vars['Variable'], fontsize=9)
ax.set_xlabel('Effect Size (Cohen\'s D or Cramer\'s V)', fontsize=12, fontweight='bold')
ax.set_title('LEVEL 1: TOP 25 VARIABLES BY EFFECT SIZE\n' +
             'TEAL = Statistically Significant (p<0.05) | RED = Not Significant',
             fontsize=13, fontweight='bold', pad=20)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, top_vars['Effect_Size'])):
    ax.text(val + 0.01, i, f'{val:.3f}',
            va='center', ha='left',
            fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/04_stat_significance_summary.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: 04_stat_significance_summary.png")
plt.close()

print("\n[OK] Created 4 statistical visualizations")

# ==============================================================================
# COMPLETION
# ==============================================================================

print("\n" + "="*100)
print("LEVEL 1 STATISTICAL TESTS COMPLETE")
print("="*100)

print(f"\n[OK] Tested {len(feature_cols)} variables")
print(f"[OK] Significant: {n_sig_numerical + n_sig_categorical}/{len(feature_cols)}")

# Count large effect sizes
n_large_num = (df_numerical_tests['Effect_Size'].isin(['Medium', 'Large'])).sum()
n_large_cat = (df_categorical_tests['Effect_Size'].isin(['Medium', 'Large'])).sum()
print(f"[OK] Large effect sizes: {n_large_num + n_large_cat}")

