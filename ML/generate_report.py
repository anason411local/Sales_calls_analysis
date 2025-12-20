"""
COMPREHENSIVE ANALYSIS SUMMARY REPORT
Generates a detailed text report with all findings
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("="*100)
print("GENERATING COMPREHENSIVE ANALYSIS REPORT")
print("="*100)

# Load all results
df_numeric_results = pd.read_csv('analysis_outputs/numeric_variables_tests.csv')
df_categorical_results = pd.read_csv('analysis_outputs/categorical_variables_tests.csv')
df_correlation = pd.read_csv('analysis_outputs/correlation_analysis.csv')
feature_importance_rf = pd.read_csv('analysis_outputs/feature_importance_random_forest.csv')
feature_importance_gb = pd.read_csv('analysis_outputs/feature_importance_gradient_boosting.csv')
combined_importance = pd.read_csv('analysis_outputs/combined_feature_importance.csv')

# Start building report
report = []
report.append("="*100)
report.append("SALES CALL DURATION ANALYSIS - COMPREHENSIVE RESEARCH REPORT")
report.append("="*100)
report.append(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append(f"\nAnalysis Focus: Understanding factors that contribute to longer call durations")
report.append(f"Comparison: Calls >4.88 minutes (293 seconds) vs <4.88 minutes")
report.append("\n" + "="*100)

# ==================================================================================
# EXECUTIVE SUMMARY
# ==================================================================================
report.append("\n\nEXECUTIVE SUMMARY")
report.append("="*100)

# Key statistics
total_numeric_vars = len(df_numeric_results)
sig_numeric_vars = (df_numeric_results['P_Value'] < 0.05).sum()
high_effect_numeric = (df_numeric_results['Cohens_D'].abs() > 0.5).sum()

total_categorical_vars = len(df_categorical_results)
sig_categorical_vars = (df_categorical_results['P_Value'] < 0.05).sum()

strong_correlations = (df_correlation['Abs_Correlation'] > 0.2).sum()

report.append(f"\n1. SCALE OF ANALYSIS:")
report.append(f"   • Total Variables Analyzed: {total_numeric_vars + total_categorical_vars}")
report.append(f"   • Numeric Variables: {total_numeric_vars}")
report.append(f"   • Categorical Variables: {total_categorical_vars}")

report.append(f"\n2. STATISTICAL SIGNIFICANCE:")
report.append(f"   • Significant Numeric Variables (p<0.05): {sig_numeric_vars} ({sig_numeric_vars/total_numeric_vars*100:.1f}%)")
report.append(f"   • Significant Categorical Variables (p<0.05): {sig_categorical_vars} ({sig_categorical_vars/total_categorical_vars*100:.1f}%)")
report.append(f"   • Variables with Medium-to-Large Effect Size: {high_effect_numeric}")
report.append(f"   • Variables with Strong Correlation (|r|>0.2): {strong_correlations}")

# ==================================================================================
# TOP 15 MOST IMPORTANT VARIABLES
# ==================================================================================
report.append("\n\n" + "="*100)
report.append("TOP 15 MOST IMPORTANT VARIABLES (Combined Ranking)")
report.append("="*100)
report.append("\nThese variables have the highest combined importance across all analysis methods")
report.append("(Random Forest, Gradient Boosting, and Correlation Analysis)")
report.append("\n" + "-"*100)

top_15 = combined_importance.head(15)

for idx, row in top_15.iterrows():
    var_name = row['Variable']
    combined_score = row['Combined_Score']
    rf_imp = row['RF_Importance']
    gb_imp = row['GB_Importance']
    correlation = row['Correlation']
    
    report.append(f"\n{idx+1}. {var_name}")
    report.append(f"   Combined Score: {combined_score:.4f}")
    report.append(f"   Random Forest Importance: {rf_imp:.4f}")
    report.append(f"   Gradient Boosting Importance: {gb_imp:.4f}")
    report.append(f"   Correlation: {correlation:.4f}")
    
    # Add statistical info if available
    numeric_info = df_numeric_results[df_numeric_results['Variable'] == var_name]
    if not numeric_info.empty:
        row_info = numeric_info.iloc[0]
        report.append(f"   Short Calls Mean: {row_info['Short_Mean']:.2f}")
        report.append(f"   Long Calls Mean: {row_info['Long_Mean']:.2f}")
        report.append(f"   Difference: {row_info['Difference']:.2f} ({row_info['Pct_Difference']:.1f}%)")
        report.append(f"   P-Value: {row_info['P_Value']:.4f} {'***' if row_info['P_Value'] < 0.001 else '**' if row_info['P_Value'] < 0.01 else '*' if row_info['P_Value'] < 0.05 else ''}")
        report.append(f"   Effect Size (Cohen's D): {row_info['Cohens_D']:.3f}")

# ==================================================================================
# TOP NUMERIC VARIABLES BY STATISTICAL SIGNIFICANCE
# ==================================================================================
report.append("\n\n" + "="*100)
report.append("TOP 20 NUMERIC VARIABLES BY STATISTICAL SIGNIFICANCE")
report.append("="*100)
report.append("\nVariables showing the most significant differences between short and long calls")
report.append("\n" + "-"*100)

top_20_numeric = df_numeric_results.nsmallest(20, 'P_Value')

for idx, row in top_20_numeric.iterrows():
    report.append(f"\n{row.name+1}. {row['Variable']}")
    report.append(f"   Short Calls: Mean={row['Short_Mean']:.2f}, Median={row['Short_Median']:.2f}, N={int(row['N_Short'])}")
    report.append(f"   Long Calls:  Mean={row['Long_Mean']:.2f}, Median={row['Long_Median']:.2f}, N={int(row['N_Long'])}")
    report.append(f"   Difference: {row['Difference']:.2f} ({'+' if row['Difference'] > 0 else ''}{row['Pct_Difference']:.1f}%)")
    report.append(f"   P-Value: {row['P_Value']:.6f} {'***' if row['P_Value'] < 0.001 else '**' if row['P_Value'] < 0.01 else '*'}")
    report.append(f"   Effect Size: {row['Cohens_D']:.3f} ({row['Effect_Size']})")
    report.append(f"   Test Used: {row['Test']}")

# ==================================================================================
# TOP CORRELATIONS
# ==================================================================================
report.append("\n\n" + "="*100)
report.append("TOP 20 VARIABLES BY CORRELATION STRENGTH")
report.append("="*100)
report.append("\nVariables with the strongest correlation to call duration group")
report.append("(Positive = favors longer calls, Negative = favors shorter calls)")
report.append("\n" + "-"*100)

top_20_corr = df_correlation.nlargest(20, 'Abs_Correlation')

for idx, row in top_20_corr.iterrows():
    report.append(f"\n{idx+1}. {row['Variable']}")
    report.append(f"   Correlation: {row['Correlation']:.4f} ({row['Direction']})")
    report.append(f"   Strength: {row['Strength']}")
    report.append(f"   P-Value: {row['P_Value']:.6f}")
    report.append(f"   Sample Size: {int(row['N'])}")

# ==================================================================================
# KEY INSIGHTS & PATTERNS
# ==================================================================================
report.append("\n\n" + "="*100)
report.append("KEY INSIGHTS & PATTERNS")
report.append("="*100)

# Identify patterns in top variables
report.append("\n1. VARIABLES STRONGLY ASSOCIATED WITH LONGER CALLS:")
positive_correlations = df_correlation[df_correlation['Correlation'] > 0.15].nlargest(10, 'Correlation')
for idx, row in positive_correlations.iterrows():
    report.append(f"   • {row['Variable']}: r={row['Correlation']:.3f}")

report.append("\n2. VARIABLES STRONGLY ASSOCIATED WITH SHORTER CALLS:")
negative_correlations = df_correlation[df_correlation['Correlation'] < -0.15].nsmallest(10, 'Correlation')
for idx, row in negative_correlations.iterrows():
    report.append(f"   • {row['Variable']}: r={row['Correlation']:.3f}")

report.append("\n3. VARIABLES WITH LARGEST PRACTICAL DIFFERENCES:")
largest_differences = df_numeric_results.nlargest(10, 'Difference')
for idx, row in largest_differences.iterrows():
    report.append(f"   • {row['Variable']}: +{row['Difference']:.2f} ({'+' if row['Pct_Difference'] > 0 else ''}{row['Pct_Difference']:.1f}%)")

# ==================================================================================
# CATEGORICAL VARIABLES
# ==================================================================================
if len(df_categorical_results) > 0:
    report.append("\n\n" + "="*100)
    report.append("TOP 15 CATEGORICAL VARIABLES BY SIGNIFICANCE")
    report.append("="*100)
    report.append("\n" + "-"*100)
    
    top_15_cat = df_categorical_results.nsmallest(15, 'P_Value')
    
    for idx, row in top_15_cat.iterrows():
        report.append(f"\n{idx+1}. {row['Variable']}")
        report.append(f"   Most Common in Short Calls: {row['Short_Most_Common']}")
        report.append(f"   Most Common in Long Calls: {row['Long_Most_Common']}")
        report.append(f"   P-Value: {row['P_Value']:.6f}")
        report.append(f"   Effect Size (Cramér's V): {row['Cramers_V']:.3f} ({row['Effect_Size']})")
        report.append(f"   Number of Categories: {int(row['N_Categories'])}")

# ==================================================================================
# METHODOLOGY
# ==================================================================================
report.append("\n\n" + "="*100)
report.append("METHODOLOGY")
report.append("="*100)

report.append("\n1. DATA PREPROCESSING:")
report.append("   • Removed identifying information and transcription columns")
report.append("   • Separated analysis by call duration: <4.88 min vs >4.88 min (293 seconds)")
report.append("   • Handled missing values appropriately for each analysis method")

report.append("\n2. STATISTICAL TESTS:")
report.append("   • Numeric Variables: T-tests (parametric) or Mann-Whitney U tests (non-parametric)")
report.append("   • Categorical Variables: Chi-square tests of independence")
report.append("   • Effect Sizes: Cohen's D for numeric, Cramér's V for categorical")

report.append("\n3. CORRELATION ANALYSIS:")
report.append("   • Point-biserial correlation for numeric variables with binary target")
report.append("   • Significance testing at α=0.05 level")

report.append("\n4. FEATURE IMPORTANCE:")
report.append("   • Random Forest Classifier (200 trees, max_depth=10)")
report.append("   • Gradient Boosting Classifier (150 trees, max_depth=5)")
report.append("   • Combined ranking: weighted average of normalized scores")

report.append("\n5. SIGNIFICANCE LEVELS:")
report.append("   • *** p < 0.001 (highly significant)")
report.append("   • **  p < 0.01 (very significant)")
report.append("   • *   p < 0.05 (significant)")

# ==================================================================================
# WRITE REPORT
# ==================================================================================
report_text = "\n".join(report)

with open('analysis_outputs/COMPREHENSIVE_ANALYSIS_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write(report_text)

print("\n✓ Comprehensive report saved: analysis_outputs/COMPREHENSIVE_ANALYSIS_REPORT.txt")
print("\n" + "="*100)
print("REPORT GENERATION COMPLETE")
print("="*100)

