"""
==============================================================================
PHASE 3: COMBINED ANALYSIS REPORT
==============================================================================

Purpose: Generate comprehensive report combining both levels
- Executive summary
- Level 1 (Variable-level) key findings
- Level 2 (Value-level) key findings
- Actionable insights
- Recommendations

==============================================================================
"""

import pandas as pd
import json
from datetime import datetime

print("="*100)
print("GENERATING COMBINED ANALYSIS REPORT")
print("="*100)

# ==============================================================================
# LOAD ALL RESULTS
# ==============================================================================

print("\nLoading analysis results...")

# Level 1
df_l1_importance = pd.read_csv('analysis_outputs/level1_variable/03_importance_combined.csv')
df_l1_corr = pd.read_csv('analysis_outputs/level1_variable/02_correlation_with_target.csv')
df_l1_shap = pd.read_csv('analysis_outputs/level1_variable/05_shap_importance.csv')

# Level 2
df_l2_values = pd.read_csv('analysis_outputs/level2_value/07_categorical_value_analysis.csv')
df_l2_importance = pd.read_csv('analysis_outputs/level2_value/09_importance_combined_values.csv')

print("[OK] All results loaded")

# ==============================================================================
# GENERATE REPORT
# ==============================================================================

report_lines = []

report_lines.append("="*100)
report_lines.append("COMPLETE TWO-LEVEL ANALYSIS REPORT")
report_lines.append("Sales Call Duration Analysis: Why Not All OMC Calls Go Above 4.88 Minutes")
report_lines.append("="*100)
report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append(f"Analysis Framework: Two-Level Approach (Variable-Level + Value-Level)")

# EXECUTIVE SUMMARY
report_lines.append("\n" + "="*100)
report_lines.append("EXECUTIVE SUMMARY")
report_lines.append("="*100)

report_lines.append("\nThis analysis answers 'Why not all OMC calls go above 4.88 minutes' using a")
report_lines.append("TWO-LEVEL approach:")
report_lines.append("")
report_lines.append("LEVEL 1 (VARIABLE-LEVEL): Which of the 49 variables matter most?")
report_lines.append("LEVEL 2 (VALUE-LEVEL): Which specific values within those variables matter?")
report_lines.append("")
report_lines.append(f"Total Variables Analyzed: 49 (from Sections 1-6.6)")
report_lines.append(f"Total Specific Values Analyzed: {len(df_l2_values)}")
report_lines.append(f"Significant Values Found: {(df_l2_values['Significant'] == 'Yes').sum()}")

# LEVEL 1 FINDINGS
report_lines.append("\n" + "="*100)
report_lines.append("LEVEL 1: VARIABLE-LEVEL KEY FINDINGS")
report_lines.append("="*100)

report_lines.append("\nTOP 10 MOST IMPORTANT VARIABLES:")
report_lines.append("-" * 100)
for idx, row in df_l1_importance.head(10).iterrows():
    report_lines.append(f"  {idx+1}. {row['Variable']}")
    report_lines.append(f"     Combined Score: {row['Combined_Score']:.4f}")
    report_lines.append(f"     RF Importance: {row['RF_Importance']:.4f} | GB Importance: {row['GB_Importance']:.4f}")

# LEVEL 2 FINDINGS
report_lines.append("\n" + "="*100)
report_lines.append("LEVEL 2: VALUE-LEVEL KEY FINDINGS")
report_lines.append("="*100)

report_lines.append("\nTOP 20 SPECIFIC VALUES ASSOCIATED WITH LONG CALLS:")
report_lines.append("-" * 100)
long_values = df_l2_values[df_l2_values['Direction'] == 'Favors Long Calls'].head(20)
for idx, row in long_values.iterrows():
    report_lines.append(f"  {row['Variable']} = {row['Value']}")
    report_lines.append(f"     {row['Pct_Long']:.1f}% Long Calls | {row['Total_Count']} calls | p={row['P_Value']:.4f}")

report_lines.append("\nTOP 20 SPECIFIC VALUES ASSOCIATED WITH SHORT CALLS:")
report_lines.append("-" * 100)
short_values = df_l2_values[df_l2_values['Direction'] == 'Favors Short Calls'].head(20)
for idx, row in short_values.iterrows():
    report_lines.append(f"  {row['Variable']} = {row['Value']}")
    report_lines.append(f"     {row['Pct_Short']:.1f}% Short Calls | {row['Total_Count']} calls | p={row['P_Value']:.4f}")

# KEY QUESTIONS ANSWERED
report_lines.append("\n" + "="*100)
report_lines.append("ANSWERS TO KEY QUESTIONS")
report_lines.append("="*100)

# Timezone
if 'timezone' in df_l2_values['Variable'].values:
    report_lines.append("\n1. WHICH TIMEZONE LEADS TO LONGER CALLS?")
    report_lines.append("-" * 100)
    tz_data = df_l2_values[df_l2_values['Variable'] == 'timezone'].sort_values('Pct_Long', ascending=False)
    for idx, row in tz_data.iterrows():
        report_lines.append(f"  {row['Value']}: {row['Pct_Long']:.1f}% Long Calls")

# Month
if 'season_month' in df_l2_values['Variable'].values:
    report_lines.append("\n2. WHICH MONTH HAS HIGHEST % OF LONG CALLS?")
    report_lines.append("-" * 100)
    month_data = df_l2_values[df_l2_values['Variable'] == 'season_month'].sort_values('Pct_Long', ascending=False)
    for idx, row in month_data.iterrows():
        report_lines.append(f"  {row['Value']}: {row['Pct_Long']:.1f}% Long Calls")

# Sentiment
if 'customer_sentiment_omc' in df_l2_values['Variable'].values:
    report_lines.append("\n3. WHICH CUSTOMER SENTIMENT (OMC) LEADS TO LONGER CALLS?")
    report_lines.append("-" * 100)
    sent_data = df_l2_values[df_l2_values['Variable'] == 'customer_sentiment_omc'].sort_values('Pct_Long', ascending=False).head(10)
    for idx, row in sent_data.iterrows():
        report_lines.append(f"  {row['Value']}: {row['Pct_Long']:.1f}% Long Calls")

# ACTIONABLE INSIGHTS
report_lines.append("\n" + "="*100)
report_lines.append("ACTIONABLE INSIGHTS")
report_lines.append("="*100)

report_lines.append("\n1. FOCUS ON HIGH-IMPACT VARIABLES:")
top_3_vars = df_l1_importance.head(3)['Variable'].tolist()
report_lines.append(f"   Top 3: {', '.join(top_3_vars)}")
report_lines.append("   These variables have the strongest relationship with call duration.")

report_lines.append("\n2. OPTIMIZE FOR HIGH-PERFORMING VALUES:")
top_value = long_values.iloc[0]
report_lines.append(f"   Best value: {top_value['Variable']} = {top_value['Value']}")
report_lines.append(f"   Achieves {top_value['Pct_Long']:.1f}% long calls")

report_lines.append("\n3. AVOID LOW-PERFORMING VALUES:")
worst_value = short_values.iloc[0]
report_lines.append(f"   Worst value: {worst_value['Variable']} = {worst_value['Value']}")
report_lines.append(f"   Only {worst_value['Pct_Long']:.1f}% long calls")

# METHODOLOGY
report_lines.append("\n" + "="*100)
report_lines.append("METHODOLOGY")
report_lines.append("="*100)

report_lines.append("\nLEVEL 1 (VARIABLE-LEVEL):")
report_lines.append("  - 49x49 Spearman correlation matrices")
report_lines.append("  - Random Forest & Gradient Boosting models")
report_lines.append("  - SHAP analysis (all chart types)")
report_lines.append("  - Statistical tests (t-test, Mann-Whitney, Chi-square)")

report_lines.append("\nLEVEL 2 (VALUE-LEVEL):")
report_lines.append("  - Categorical value analysis (specific values)")
report_lines.append("  - Numerical binning (range analysis)")
report_lines.append("  - ML models on one-hot encoded values")
report_lines.append("  - Value-specific SHAP analysis")

report_lines.append("\n" + "="*100)
report_lines.append("END OF REPORT")
report_lines.append("="*100)

# ==============================================================================
# SAVE REPORT
# ==============================================================================

report_text = "\n".join(report_lines)

with open('analysis_outputs/COMPLETE_ANALYSIS_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write(report_text)

print("\n[OK] Saved: COMPLETE_ANALYSIS_REPORT.txt")

# Save summary metrics
summary = {
    'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'total_variables': 49,
    'total_values_analyzed': len(df_l2_values),
    'significant_values': int((df_l2_values['Significant'] == 'Yes').sum()),
    'top_variable': df_l1_importance.iloc[0]['Variable'],
    'top_value': f"{long_values.iloc[0]['Variable']} = {long_values.iloc[0]['Value']}"
}

with open('analysis_outputs/ANALYSIS_SUMMARY.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("[OK] Saved: ANALYSIS_SUMMARY.json")

print("\n" + "="*100)
print("COMPLETE ANALYSIS REPORT GENERATED")
print("="*100)
print(f"\nReport location: analysis_outputs/COMPLETE_ANALYSIS_REPORT.txt")
print(f"Summary location: analysis_outputs/ANALYSIS_SUMMARY.json")

