"""
DPAD Analysis - Step 4: Statistical Tests
==========================================

Purpose:
--------
Perform rigorous statistical testing to validate differences between
High-DPAD and Low-DPAD agents.

What This Script Does:
----------------------
1. Independent samples t-tests for numerical features
2. Mann-Whitney U tests (non-parametric alternative)
3. Chi-square tests for categorical features
4. Calculate effect sizes (Cohen's d, Cramér's V)
5. Multiple testing correction (Bonferroni)
6. Generate statistical significance report

Why This Matters:
-----------------
While correlations and ML feature importance show relationships,
statistical tests provide:
- P-values (is the difference statistically significant?)
- Effect sizes (how large is the difference?)
- Confidence intervals (range of likely values)
- Non-parametric tests (when data isn't normally distributed)

This gives us scientific rigor to claim: "High-DPAD agents are
SIGNIFICANTLY different in these ways."

Author: AI Agent
Date: 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import sys
import warnings
warnings.filterwarnings('ignore')

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

# Statistical tests
from scipy import stats
from scipy.stats import chi2_contingency, mannwhitneyu, ttest_ind

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def load_preprocessed_data():
    """Load preprocessed data from Step 1"""
    print("\n" + "="*70)
    print("LOADING PREPROCESSED DATA")
    print("="*70)
    
    data_path = Path("ML_for_DPAD/analysis_outputs/preprocessed_data")
    
    # Load features and target
    X = pd.read_csv(data_path / "X_features.csv")
    y = pd.read_csv(data_path / "y_target.csv").values.ravel()
    
    # Load feature metadata
    with open(data_path / "feature_metadata.json", 'r') as f:
        feature_metadata = json.load(f)
    
    # Split into high and low DPAD groups
    X_high = X[y == 1].reset_index(drop=True)
    X_low = X[y == 0].reset_index(drop=True)
    
    print(f"\n✅ Loaded preprocessed data:")
    print(f"   Total samples: {len(X)}")
    print(f"   High-DPAD group: {len(X_high)} calls")
    print(f"   Low-DPAD group:  {len(X_low)} calls")
    print(f"   Features: {X.shape[1]}")
    
    return X, y, X_high, X_low, feature_metadata


def calculate_cohens_d(group1, group2):
    """
    Calculate Cohen's d effect size
    
    Cohen's d interpretation:
    - Small effect: d = 0.2
    - Medium effect: d = 0.5
    - Large effect: d = 0.8
    
    Positive d: Higher in group1 (High-DPAD)
    Negative d: Lower in group1 (Higher in Low-DPAD)
    """
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    
    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    
    if pooled_std == 0:
        return 0
    
    # Cohen's d
    d = (np.mean(group1) - np.mean(group2)) / pooled_std
    
    return d


def perform_t_tests(X_high, X_low, feature_metadata):
    """
    Perform independent samples t-tests for numerical features
    
    Null hypothesis: No difference between High-DPAD and Low-DPAD agents
    Alternative: High-DPAD and Low-DPAD agents are different
    """
    print("\n" + "="*70)
    print("PERFORMING T-TESTS (Numerical Features)")
    print("="*70)
    
    results = []
    
    # Get numerical features
    numerical_features = feature_metadata['numerical_features']
    
    for feature in numerical_features:
        if feature not in X_high.columns:
            continue
        
        high_vals = X_high[feature].dropna()
        low_vals = X_low[feature].dropna()
        
        # Skip if too few samples
        if len(high_vals) < 3 or len(low_vals) < 3:
            continue
        
        # Perform t-test
        t_stat, p_value = ttest_ind(high_vals, low_vals, equal_var=False)  # Welch's t-test
        
        # Calculate Cohen's d
        cohens_d = calculate_cohens_d(high_vals, low_vals)
        
        # Calculate means and std
        mean_high = high_vals.mean()
        mean_low = low_vals.mean()
        std_high = high_vals.std()
        std_low = low_vals.std()
        
        results.append({
            'feature': feature,
            'test': 't-test',
            'mean_high': mean_high,
            'mean_low': mean_low,
            'std_high': std_high,
            'std_low': std_low,
            'difference': mean_high - mean_low,
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'n_high': len(high_vals),
            'n_low': len(low_vals)
        })
    
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('p_value')
    
    print(f"\n✅ Completed {len(results_df)} t-tests")
    print(f"   Significant at p<0.05: {(results_df['p_value'] < 0.05).sum()}")
    print(f"   Significant at p<0.01: {(results_df['p_value'] < 0.01).sum()}")
    
    return results_df


def perform_mann_whitney_tests(X_high, X_low, feature_metadata):
    """
    Perform Mann-Whitney U tests (non-parametric alternative to t-test)
    
    Useful when:
    - Data is not normally distributed
    - Outliers are present
    - Ordinal data
    
    Tests if distributions differ between groups
    """
    print("\n" + "="*70)
    print("PERFORMING MANN-WHITNEY U TESTS (Non-parametric)")
    print("="*70)
    
    results = []
    
    # Test all numerical and categorical features
    all_features = (feature_metadata['numerical_features'] + 
                    feature_metadata['categorical_features'])
    
    for feature in all_features:
        if feature not in X_high.columns:
            continue
        
        high_vals = X_high[feature].dropna()
        low_vals = X_low[feature].dropna()
        
        # Skip if too few samples
        if len(high_vals) < 3 or len(low_vals) < 3:
            continue
        
        # Perform Mann-Whitney U test
        u_stat, p_value = mannwhitneyu(high_vals, low_vals, alternative='two-sided')
        
        # Calculate medians
        median_high = high_vals.median()
        median_low = low_vals.median()
        
        results.append({
            'feature': feature,
            'test': 'mann-whitney',
            'median_high': median_high,
            'median_low': median_low,
            'difference': median_high - median_low,
            'u_statistic': u_stat,
            'p_value': p_value,
            'n_high': len(high_vals),
            'n_low': len(low_vals)
        })
    
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('p_value')
    
    print(f"\n✅ Completed {len(results_df)} Mann-Whitney U tests")
    print(f"   Significant at p<0.05: {(results_df['p_value'] < 0.05).sum()}")
    print(f"   Significant at p<0.01: {(results_df['p_value'] < 0.01).sum()}")
    
    return results_df


def perform_chi_square_tests(X_high, X_low, feature_metadata):
    """
    Perform Chi-square tests for categorical features
    
    Tests if the distribution of categories differs between High and Low DPAD
    
    Also calculates Cramér's V (effect size for categorical data):
    - Small: V = 0.1
    - Medium: V = 0.3
    - Large: V = 0.5
    """
    print("\n" + "="*70)
    print("PERFORMING CHI-SQUARE TESTS (Categorical Features)")
    print("="*70)
    
    results = []
    
    categorical_features = feature_metadata['categorical_features']
    
    for feature in categorical_features:
        if feature not in X_high.columns:
            continue
        
        # Create contingency table
        high_counts = X_high[feature].value_counts()
        low_counts = X_low[feature].value_counts()
        
        # Align indices
        all_categories = sorted(set(high_counts.index) | set(low_counts.index))
        high_counts = high_counts.reindex(all_categories, fill_value=0)
        low_counts = low_counts.reindex(all_categories, fill_value=0)
        
        # Create contingency table
        contingency_table = np.array([high_counts.values, low_counts.values])
        
        # Skip if too few samples or categories
        if contingency_table.shape[1] < 2 or contingency_table.sum() < 10:
            continue
        
        # Perform chi-square test
        try:
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
            
            # Calculate Cramér's V
            n = contingency_table.sum()
            min_dim = min(contingency_table.shape) - 1
            cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
            
            results.append({
                'feature': feature,
                'test': 'chi-square',
                'n_categories': len(all_categories),
                'chi2_statistic': chi2,
                'p_value': p_value,
                'degrees_of_freedom': dof,
                'cramers_v': cramers_v,
                'n_high': high_counts.sum(),
                'n_low': low_counts.sum()
            })
        except:
            # Skip if chi-square test fails
            continue
    
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('p_value')
    
    print(f"\n✅ Completed {len(results_df)} Chi-square tests")
    print(f"   Significant at p<0.05: {(results_df['p_value'] < 0.05).sum()}")
    print(f"   Significant at p<0.01: {(results_df['p_value'] < 0.01).sum()}")
    
    return results_df


def apply_bonferroni_correction(results_df):
    """
    Apply Bonferroni correction for multiple testing
    
    Problem: When testing many hypotheses, some will appear significant by chance
    Solution: Adjust p-values for number of tests performed
    
    New threshold: p < 0.05 / n_tests
    """
    n_tests = len(results_df)
    bonferroni_alpha = 0.05 / n_tests
    
    results_df['bonferroni_significant'] = results_df['p_value'] < bonferroni_alpha
    results_df['bonferroni_alpha'] = bonferroni_alpha
    
    print(f"\n🔬 Bonferroni Correction Applied:")
    print(f"   Number of tests: {n_tests}")
    print(f"   Adjusted alpha: {bonferroni_alpha:.6f}")
    print(f"   Significant after correction: {results_df['bonferroni_significant'].sum()}")
    
    return results_df


def create_combined_effect_size_visualization(t_test_results, chi_square_results, output_dir):
    """
    Create combined effect size visualization showing top 25 variables
    Similar to ML V2 output
    """
    print("\n📊 Creating combined effect size visualization...")
    
    output_path = output_dir / "analysis_outputs" / "statistical_tests"
    
    # Combine numerical and categorical results
    combined_results = []
    
    # Add numerical features (Cohen's D)
    for idx, row in t_test_results.iterrows():
        combined_results.append({
            'Variable': row['feature'],
            'Type': 'Numerical',
            'Significant': 'Yes' if row['p_value'] < 0.05 else 'No',
            'Effect_Size_Value': abs(row['cohens_d'])
        })
    
    # Add categorical features (Cramér's V)
    for idx, row in chi_square_results.iterrows():
        combined_results.append({
            'Variable': row['feature'],
            'Type': 'Categorical',
            'Significant': 'Yes' if row['p_value'] < 0.05 else 'No',
            'Effect_Size_Value': row['cramers_v']
        })
    
    combined_df = pd.DataFrame(combined_results)
    combined_df = combined_df.sort_values('Effect_Size_Value', ascending=True).tail(25)
    
    # Save combined results
    all_combined = pd.DataFrame(combined_results).sort_values('Effect_Size_Value', ascending=False)
    all_combined.to_csv(output_path / "04_statistical_tests_combined.csv", index=False)
    print(f"   ✓ Saved: 04_statistical_tests_combined.csv")
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(14, 10))
    
    colors = ['#4ECDC4' if sig == 'Yes' else '#FF6B6B' 
              for sig in combined_df['Significant']]
    
    bars = ax.barh(range(len(combined_df)), combined_df['Effect_Size_Value'], 
                   color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)
    
    ax.set_yticks(range(len(combined_df)))
    ax.set_yticklabels(combined_df['Variable'], fontsize=10)
    ax.set_xlabel("Effect Size (Cohen's D or Cramér's V)", fontsize=13, fontweight='bold')
    ax.set_title("LEVEL 1: TOP 25 VARIABLES BY EFFECT SIZE\n" +
                 "TEAL = Statistically Significant (p<0.05) | RED = Not Significant",
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels
    for bar, val in zip(bars, combined_df['Effect_Size_Value']):
        ax.text(val + 0.02, bar.get_y() + bar.get_height()/2,
               f'{val:.3f}',
               va='center', fontsize=9, fontweight='bold')
    
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path / "04_effect_size_top25.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: 04_effect_size_top25.png")
    plt.close()


def create_effect_size_vs_significance_plots(t_test_results, chi_square_results, output_dir):
    """
    Create scatter plots showing effect size vs statistical significance
    Similar to ML V2 volcano-style plots
    """
    print("\n📊 Creating effect size vs significance scatter plots...")
    
    output_path = output_dir / "analysis_outputs" / "statistical_tests"
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Plot 1: Numerical Variables (Cohen's D vs p-value)
    if len(t_test_results) > 0:
        # Calculate -log10(p-value)
        neg_log_p = -np.log10(t_test_results['p_value'].replace(0, 1e-300))
        
        # Color by significance
        colors = []
        for p in t_test_results['p_value']:
            if p < 0.05:
                colors.append('#FFD700')  # Yellow for significant
            else:
                colors.append('#4169E1')  # Blue for not significant
        
        scatter = ax1.scatter(t_test_results['cohens_d'], neg_log_p,
                            c=colors, s=120, alpha=0.7, edgecolors='black', linewidths=1.5)
        
        # Add significance line
        ax1.axhline(-np.log10(0.05), color='red', linestyle='--', 
                   label='p=0.05', linewidth=2)
        
        # Annotate top features by absolute effect size
        t_test_results['abs_cohens_d'] = t_test_results['cohens_d'].abs()
        top_features = t_test_results.nlargest(3, 'abs_cohens_d')
        for idx, row in top_features.iterrows():
            if abs(row['cohens_d']) > 0.3:  # Only annotate if meaningful effect
                ax1.annotate(row['feature'], 
                           xy=(row['cohens_d'], -np.log10(row['p_value'])),
                           xytext=(10, 10), textcoords='offset points',
                           fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        ax1.set_xlabel("Effect Size (|Cohen's D|)", fontsize=12, fontweight='bold')
        ax1.set_ylabel("-log10(p-value)", fontsize=12, fontweight='bold')
        ax1.set_title("Numerical Variables: Effect Size vs Significance\n" +
                     "Top-right = Large effect + Significant",
                     fontsize=13, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(alpha=0.3)
    
    # Plot 2: Categorical Variables (Cramér's V vs p-value)
    if len(chi_square_results) > 0:
        # Calculate -log10(p-value)
        neg_log_p = -np.log10(chi_square_results['p_value'].replace(0, 1e-300))
        
        # Color by significance
        colors = []
        for p in chi_square_results['p_value']:
            if p < 0.05:
                colors.append('#FFD700')  # Yellow for significant
            else:
                colors.append('#FF6347')  # Red for not significant
        
        scatter = ax2.scatter(chi_square_results['cramers_v'], neg_log_p,
                            c=colors, s=120, alpha=0.7, edgecolors='black', linewidths=1.5)
        
        # Add significance line
        ax2.axhline(-np.log10(0.05), color='red', linestyle='--',
                   label='p=0.05', linewidth=2)
        
        # Annotate top features
        top_features = chi_square_results.nlargest(3, 'cramers_v')
        for idx, row in top_features.iterrows():
            if row['cramers_v'] > 0.3:  # Only annotate if meaningful effect
                ax2.annotate(row['feature'],
                           xy=(row['cramers_v'], -np.log10(row['p_value'])),
                           xytext=(10, 10), textcoords='offset points',
                           fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        ax2.set_xlabel("Effect Size (Cramér's V)", fontsize=12, fontweight='bold')
        ax2.set_ylabel("-log10(p-value)", fontsize=12, fontweight='bold')
        ax2.set_title("Categorical Variables: Effect Size vs Significance\n" +
                     "Top-right = Large effect + Significant",
                     fontsize=13, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(alpha=0.3)
    
    plt.suptitle("LEVEL 1: EFFECT SIZE vs STATISTICAL SIGNIFICANCE\n" +
                 "Best variables are in top-right (large effect + low p-value)",
                 fontsize=15, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig(output_path / "04_effect_size_vs_significance.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: 04_effect_size_vs_significance.png")
    plt.close()


def save_detailed_statistical_tables(t_test_results, chi_square_results, output_dir):
    """
    Save detailed statistical tables similar to ML V2 format
    """
    print("\n💾 Saving detailed statistical tables...")
    
    output_path = output_dir / "analysis_outputs" / "statistical_tests"
    
    # Numerical features table
    numerical_table = t_test_results.copy()
    numerical_table['Type'] = 'Numerical'
    numerical_table['Significant'] = numerical_table['p_value'].apply(
        lambda p: 'Yes' if p < 0.05 else 'No'
    )
    numerical_table['Abs_Cohens_D'] = numerical_table['cohens_d'].abs()
    
    # Categorize effect size
    def categorize_effect_cohens(d):
        d = abs(d)
        if d >= 0.8:
            return 'Large'
        elif d >= 0.5:
            return 'Medium'
        elif d >= 0.2:
            return 'Small'
        else:
            return 'Negligible'
    
    numerical_table['Effect_Size'] = numerical_table['cohens_d'].apply(categorize_effect_cohens)
    
    # Rename columns to match ML V2 format
    numerical_export = numerical_table[[
        'feature', 'Type', 'mean_high', 'std_high', 'mean_low', 'std_low',
        'difference', 't_statistic', 'p_value', 'Significant',
        'cohens_d', 'Abs_Cohens_D', 'Effect_Size'
    ]].rename(columns={
        'feature': 'Variable',
        'mean_high': 'High_DPAD_Mean',
        'mean_low': 'Low_DPAD_Mean',
        'std_high': 'High_DPAD_Std',
        'std_low': 'Low_DPAD_Std',
        'difference': 'Mean_Diff',
        't_statistic': 'T_Statistic',
        'p_value': 'P_Value',
        'cohens_d': 'Cohens_D'
    })
    
    numerical_export = numerical_export.sort_values('Abs_Cohens_D', ascending=False)
    numerical_export.to_csv(output_path / "04_statistical_tests_numerical.csv", index=False)
    print(f"   ✓ Saved: 04_statistical_tests_numerical.csv")
    
    # Categorical features table
    categorical_table = chi_square_results.copy()
    categorical_table['Type'] = 'Categorical'
    categorical_table['Significant'] = categorical_table['p_value'].apply(
        lambda p: 'Yes' if p < 0.05 else 'No'
    )
    
    # Categorize effect size
    def categorize_effect_cramers(v):
        if v >= 0.5:
            return 'Large'
        elif v >= 0.3:
            return 'Medium'
        elif v >= 0.1:
            return 'Small'
        else:
            return 'Negligible'
    
    categorical_table['Effect_Size'] = categorical_table['cramers_v'].apply(categorize_effect_cramers)
    
    # Rename columns
    categorical_export = categorical_table[[
        'feature', 'Type', 'chi2_statistic', 'p_value', 
        'degrees_of_freedom', 'Significant', 'cramers_v', 'Effect_Size'
    ]].rename(columns={
        'feature': 'Variable',
        'chi2_statistic': 'Chi_Square_Stat',
        'p_value': 'P_Value',
        'degrees_of_freedom': 'Degrees_of_Freedom',
        'cramers_v': 'Cramers_V'
    })
    
    categorical_export = categorical_export.sort_values('Cramers_V', ascending=False)
    categorical_export.to_csv(output_path / "04_statistical_tests_categorical.csv", index=False)
    print(f"   ✓ Saved: 04_statistical_tests_categorical.csv")


def create_statistical_visualizations(t_test_results, mann_whitney_results, 
                                       chi_square_results, output_dir):
    """
    Create comprehensive statistical test visualizations
    """
    print("\n" + "="*70)
    print("CREATING STATISTICAL VISUALIZATIONS")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "statistical_tests"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # NEW: Create combined effect size visualization
    create_combined_effect_size_visualization(t_test_results, chi_square_results, output_dir)
    
    # NEW: Create effect size vs significance scatter plots
    create_effect_size_vs_significance_plots(t_test_results, chi_square_results, output_dir)
    
    # NEW: Save detailed statistical tables
    save_detailed_statistical_tables(t_test_results, chi_square_results, output_dir)
    
    # ORIGINAL: Plot 1: T-test Results (Effect Size vs P-value)
    if len(t_test_results) > 0:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Color by significance
        colors = ['red' if p < 0.01 else 'orange' if p < 0.05 else 'gray' 
                  for p in t_test_results['p_value']]
        
        scatter = ax.scatter(t_test_results['cohens_d'], 
                            -np.log10(t_test_results['p_value']),
                            c=colors, s=100, alpha=0.6, edgecolors='black')
        
        # Add significance line
        ax.axhline(-np.log10(0.05), color='blue', linestyle='--', 
                   label='p=0.05', linewidth=2)
        ax.axhline(-np.log10(0.01), color='darkblue', linestyle='--',
                   label='p=0.01', linewidth=2)
        
        # Add effect size lines
        ax.axvline(0.2, color='green', linestyle=':', alpha=0.5, label='Small effect')
        ax.axvline(0.5, color='orange', linestyle=':', alpha=0.5, label='Medium effect')
        ax.axvline(0.8, color='red', linestyle=':', alpha=0.5, label='Large effect')
        ax.axvline(-0.2, color='green', linestyle=':', alpha=0.5)
        ax.axvline(-0.5, color='orange', linestyle=':', alpha=0.5)
        ax.axvline(-0.8, color='red', linestyle=':', alpha=0.5)
        
        ax.set_xlabel("Cohen's d (Effect Size)", fontsize=12, fontweight='bold')
        ax.set_ylabel("-log10(p-value)", fontsize=12, fontweight='bold')
        ax.set_title("T-Test Results: Effect Size vs Statistical Significance\n" +
                     "Right = Higher in High-DPAD | Left = Higher in Low-DPAD",
                     fontsize=13, fontweight='bold', pad=15)
        
        # Annotate top significant features
        top_features = t_test_results.nsmallest(5, 'p_value')
        for idx, row in top_features.iterrows():
            ax.annotate(row['feature'], 
                       xy=(row['cohens_d'], -np.log10(row['p_value'])),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, alpha=0.7)
        
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / "t_test_volcano_plot.png", dpi=300, bbox_inches='tight')
        print(f"   ✓ Saved: t_test_volcano_plot.png")
        plt.close()
    
    # ORIGINAL: Plot 2: Top Significant Features (T-test)
    if len(t_test_results) > 0:
        sig_features = t_test_results[t_test_results['p_value'] < 0.05].head(20)
        
        if len(sig_features) > 0:
            fig, ax = plt.subplots(figsize=(12, 10))
            
            # Sort by effect size
            sig_features = sig_features.sort_values('cohens_d', ascending=True)
            
            colors = ['green' if d > 0 else 'red' for d in sig_features['cohens_d']]
            bars = ax.barh(range(len(sig_features)), sig_features['cohens_d'], color=colors, alpha=0.7)
            
            ax.set_yticks(range(len(sig_features)))
            ax.set_yticklabels(sig_features['feature'], fontsize=10)
            ax.set_xlabel("Cohen's d (Effect Size)", fontsize=12, fontweight='bold')
            ax.set_title("Top 20 Statistically Significant Features (p<0.05)\n" +
                         "Green = Higher in High-DPAD | Red = Higher in Low-DPAD",
                         fontsize=13, fontweight='bold', pad=15)
            
            # Add p-values as text
            for i, (bar, row) in enumerate(zip(bars, sig_features.iterrows())):
                idx, data = row
                ax.text(data['cohens_d'] + 0.05 if data['cohens_d'] > 0 else data['cohens_d'] - 0.05,
                       bar.get_y() + bar.get_height()/2,
                       f"p={data['p_value']:.4f}",
                       va='center', ha='left' if data['cohens_d'] > 0 else 'right',
                       fontsize=8, alpha=0.7)
            
            ax.axvline(0, color='black', linestyle='-', linewidth=1)
            ax.grid(axis='x', alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path / "significant_features_effect_sizes.png", dpi=300, bbox_inches='tight')
            print(f"   ✓ Saved: significant_features_effect_sizes.png")
            plt.close()
    
    # ORIGINAL: Plot 3: Chi-square Results
    if len(chi_square_results) > 0:
        sig_chi = chi_square_results[chi_square_results['p_value'] < 0.05].head(20)
        
        if len(sig_chi) > 0:
            fig, ax = plt.subplots(figsize=(12, 10))
            
            sig_chi = sig_chi.sort_values('cramers_v', ascending=True)
            
            colors = plt.cm.viridis(sig_chi['cramers_v'] / sig_chi['cramers_v'].max())
            bars = ax.barh(range(len(sig_chi)), sig_chi['cramers_v'], color=colors)
            
            ax.set_yticks(range(len(sig_chi)))
            ax.set_yticklabels(sig_chi['feature'], fontsize=10)
            ax.set_xlabel("Cramér's V (Effect Size)", fontsize=12, fontweight='bold')
            ax.set_title("Top 20 Categorical Features (Chi-square p<0.05)\n" +
                         "Higher Cramér's V = Stronger association",
                         fontsize=13, fontweight='bold', pad=15)
            
            ax.grid(axis='x', alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path / "chi_square_effect_sizes.png", dpi=300, bbox_inches='tight')
            print(f"   ✓ Saved: chi_square_effect_sizes.png")
            plt.close()
    
    print(f"\n✅ Created all statistical visualizations")


def generate_statistical_report(t_test_results, mann_whitney_results,
                                 chi_square_results, output_dir):
    """
    Generate comprehensive statistical testing report
    """
    print("\n" + "="*70)
    print("GENERATING STATISTICAL REPORT")
    print("="*70)
    
    report = []
    report.append("# DPAD Analysis - Statistical Tests Report")
    report.append("=" * 70)
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append("This report presents rigorous statistical tests comparing High-DPAD")
    report.append("(>1 deal/agent/day) vs Low-DPAD (<1 deal/agent/day) agents.")
    report.append("")
    
    # Overall statistics
    total_tests = len(t_test_results) + len(mann_whitney_results) + len(chi_square_results)
    sig_005 = ((t_test_results['p_value'] < 0.05).sum() +
               (mann_whitney_results['p_value'] < 0.05).sum() +
               (chi_square_results['p_value'] < 0.05).sum())
    sig_001 = ((t_test_results['p_value'] < 0.01).sum() +
               (mann_whitney_results['p_value'] < 0.01).sum() +
               (chi_square_results['p_value'] < 0.01).sum())
    
    report.append("**Testing Overview:**")
    report.append(f"- **Total tests performed:** {total_tests}")
    report.append(f"- **Significant at p<0.05:** {sig_005} ({sig_005/total_tests*100:.1f}%)")
    report.append(f"- **Significant at p<0.01:** {sig_001} ({sig_001/total_tests*100:.1f}%)")
    report.append("")
    
    # T-test Results
    report.append("## 1. T-Test Results (Numerical Features)")
    report.append("")
    report.append("*Independent samples t-test comparing means*")
    report.append("")
    
    sig_t = t_test_results[t_test_results['p_value'] < 0.05].head(20)
    if len(sig_t) > 0:
        report.append("### Top 20 Significant Differences")
        report.append("")
        report.append("| Feature | Mean High | Mean Low | Diff | Cohen's d | p-value | Interpretation |")
        report.append("|---------|-----------|----------|------|-----------|---------|----------------|")
        
        for idx, row in sig_t.iterrows():
            # Interpret Cohen's d
            d = abs(row['cohens_d'])
            if d >= 0.8:
                effect = "Large"
            elif d >= 0.5:
                effect = "Medium"
            elif d >= 0.2:
                effect = "Small"
            else:
                effect = "Negligible"
            
            direction = "↑ Higher in High-DPAD" if row['cohens_d'] > 0 else "↓ Higher in Low-DPAD"
            
            report.append(f"| {row['feature']:<35} | {row['mean_high']:.3f} | "
                         f"{row['mean_low']:.3f} | {row['difference']:.3f} | "
                         f"{row['cohens_d']:.3f} | {row['p_value']:.4f} | "
                         f"{effect} {direction} |")
    else:
        report.append("*No significant differences found at p<0.05*")
    report.append("")
    
    # Mann-Whitney Results
    report.append("## 2. Mann-Whitney U Test Results (Non-parametric)")
    report.append("")
    report.append("*Comparing distributions without assuming normality*")
    report.append("")
    
    sig_mw = mann_whitney_results[mann_whitney_results['p_value'] < 0.05].head(20)
    if len(sig_mw) > 0:
        report.append("### Top 20 Significant Differences")
        report.append("")
        report.append("| Feature | Median High | Median Low | Diff | U-statistic | p-value |")
        report.append("|---------|-------------|------------|------|-------------|---------|")
        
        for idx, row in sig_mw.iterrows():
            report.append(f"| {row['feature']:<40} | {row['median_high']:.3f} | "
                         f"{row['median_low']:.3f} | {row['difference']:.3f} | "
                         f"{row['u_statistic']:.1f} | {row['p_value']:.4f} |")
    else:
        report.append("*No significant differences found at p<0.05*")
    report.append("")
    
    # Chi-square Results
    report.append("## 3. Chi-Square Test Results (Categorical Features)")
    report.append("")
    report.append("*Testing association between categories and DPAD level*")
    report.append("")
    
    sig_chi = chi_square_results[chi_square_results['p_value'] < 0.05].head(20)
    if len(sig_chi) > 0:
        report.append("### Top 20 Significant Associations")
        report.append("")
        report.append("| Feature | Chi-square | Cramér's V | p-value | Effect Size |")
        report.append("|---------|------------|------------|---------|-------------|")
        
        for idx, row in sig_chi.iterrows():
            # Interpret Cramér's V
            v = row['cramers_v']
            if v >= 0.5:
                effect = "Large"
            elif v >= 0.3:
                effect = "Medium"
            elif v >= 0.1:
                effect = "Small"
            else:
                effect = "Negligible"
            
            report.append(f"| {row['feature']:<35} | {row['chi2_statistic']:.2f} | "
                         f"{row['cramers_v']:.3f} | {row['p_value']:.4f} | {effect} |")
    else:
        report.append("*No significant associations found at p<0.05*")
    report.append("")
    
    # Key Insights
    report.append("## 4. Key Statistical Insights")
    report.append("")
    
    # Find features significant in multiple tests
    t_sig_features = set(t_test_results[t_test_results['p_value'] < 0.05]['feature'])
    mw_sig_features = set(mann_whitney_results[mann_whitney_results['p_value'] < 0.05]['feature'])
    consensus_features = t_sig_features.intersection(mw_sig_features)
    
    if len(consensus_features) > 0:
        report.append("### Consensus Features (Significant in Both Parametric & Non-parametric Tests)")
        report.append("")
        for feat in list(consensus_features)[:10]:
            report.append(f"- **{feat}**: Robust difference across test types")
        report.append("")
    
    # Largest effect sizes
    large_effects = t_test_results[abs(t_test_results['cohens_d']) >= 0.8]
    if len(large_effects) > 0:
        report.append("### Features with Large Effect Sizes (|d| ≥ 0.8)")
        report.append("")
        for idx, row in large_effects.head(5).iterrows():
            direction = "higher" if row['cohens_d'] > 0 else "lower"
            report.append(f"- **{row['feature']}**: Cohen's d = {row['cohens_d']:.3f}")
            report.append(f"  {direction.capitalize()} in High-DPAD agents (very large practical difference)")
        report.append("")
    
    # Save report
    report_path = output_dir / "analysis_outputs" / "statistical_tests" / "statistical_tests_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Statistical report saved: {report_path}")


def save_statistical_data(t_test_results, mann_whitney_results, 
                          chi_square_results, output_dir):
    """Save all statistical test results"""
    output_path = output_dir / "analysis_outputs" / "statistical_tests"
    
    t_test_results.to_csv(output_path / "t_test_results.csv", index=False)
    mann_whitney_results.to_csv(output_path / "mann_whitney_results.csv", index=False)
    chi_square_results.to_csv(output_path / "chi_square_results.csv", index=False)
    
    print(f"\n✅ Statistical test data saved to: {output_path}")


def main():
    """Main statistical testing pipeline"""
    
    print("\n" + "="*70)
    print("DPAD ANALYSIS - STATISTICAL TESTS")
    print("="*70)
    print("\nRigorous statistical validation of differences")
    print("="*70)
    
    output_dir = Path("ML_for_DPAD")
    
    # Load data
    X, y, X_high, X_low, feature_metadata = load_preprocessed_data()
    
    # Perform t-tests
    t_test_results = perform_t_tests(X_high, X_low, feature_metadata)
    
    # Perform Mann-Whitney U tests
    mann_whitney_results = perform_mann_whitney_tests(X_high, X_low, feature_metadata)
    
    # Perform Chi-square tests
    chi_square_results = perform_chi_square_tests(X_high, X_low, feature_metadata)
    
    # Apply Bonferroni correction
    t_test_results = apply_bonferroni_correction(t_test_results)
    mann_whitney_results = apply_bonferroni_correction(mann_whitney_results)
    chi_square_results = apply_bonferroni_correction(chi_square_results)
    
    # Create visualizations
    create_statistical_visualizations(
        t_test_results, mann_whitney_results, 
        chi_square_results, output_dir
    )
    
    # Generate report
    generate_statistical_report(
        t_test_results, mann_whitney_results,
        chi_square_results, output_dir
    )
    
    # Save data
    save_statistical_data(
        t_test_results, mann_whitney_results,
        chi_square_results, output_dir
    )
    
    print("\n" + "="*70)
    print("✅ STATISTICAL TESTS COMPLETE")
    print("="*70)
    print(f"\nTop 5 Most Significant Features (by p-value):")
    
    all_results = pd.concat([
        t_test_results[['feature', 'p_value', 'test']],
        mann_whitney_results[['feature', 'p_value', 'test']],
        chi_square_results[['feature', 'p_value', 'test']]
    ])
    all_results = all_results.sort_values('p_value').head(5)
    
    for idx, row in all_results.iterrows():
        print(f"   {row['feature']:.<50} p={row['p_value']:.6f} ({row['test']})")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

