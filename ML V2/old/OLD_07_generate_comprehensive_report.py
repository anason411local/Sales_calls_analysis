"""
STEP 8: COMPREHENSIVE ANALYSIS REPORT
Generates a detailed text report summarizing all findings
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("="*100)
print("GENERATING COMPREHENSIVE ANALYSIS REPORT")
print("="*100)

# Load all analysis results
df_column_analysis = pd.read_csv('analysis_outputs/01_column_analysis_summary.csv')
df_stats = pd.read_csv('analysis_outputs/03_statistical_analysis_all_features.csv')
df_combined_ranking = pd.read_csv('analysis_outputs/04_combined_feature_ranking.csv')
df_section = pd.read_csv('analysis_outputs/03_section_analysis.csv')
df_binning = pd.read_csv('analysis_outputs/05_numerical_binning_analysis.csv')
df_cat_values = pd.read_csv('analysis_outputs/05_categorical_value_importance.csv')

# Start report
report = []
report.append("="*100)
report.append("SALES CALL DURATION ANALYSIS - COMPREHENSIVE REPORT V2")
report.append("="*100)
report.append(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append(f"\nResearch Question: Why are not all OMC calls lasting longer than 4.88 minutes?")
report.append(f"Analysis Approach: Understanding variable contributions to call duration")
report.append("\n" + "="*100)

# EXECUTIVE SUMMARY
report.append("\n\nEXECUTIVE SUMMARY")
report.append("="*100)

sig_features = (df_stats['P_Value'] < 0.05).sum()
highly_sig = (df_stats['P_Value'] < 0.001).sum()
large_effect = (df_stats['Abs_Cohens_D'] > 0.8).sum()
strong_corr = (df_stats['Abs_Correlation'] > 0.3).sum()

report.append(f"\n1. DATASET OVERVIEW:")
report.append(f"   - Total calls analyzed: 1,218 (609 short + 609 long)")
report.append(f"   - Original variables selected: 49")
report.append(f"   - Features after encoding: 150")
report.append(f"   - Feature expansion ratio: 3.06x")

report.append(f"\n2. STATISTICAL FINDINGS:")
report.append(f"   - Significant features (p<0.05): {sig_features} ({sig_features/len(df_stats)*100:.1f}%)")
report.append(f"   - Highly significant (p<0.001): {highly_sig} ({highly_sig/len(df_stats)*100:.1f}%)")
report.append(f"   - Large effect sizes (|d|>0.8): {large_effect}")
report.append(f"   - Strong correlations (|r|>0.3): {strong_corr}")

report.append(f"\n3. MACHINE LEARNING RESULTS:")
report.append(f"   - Random Forest Accuracy: 98.09%")
report.append(f"   - Gradient Boosting Accuracy: 99.73%")
report.append(f"   - Overfitting: Minimal (both models well-generalized)")

# TOP 20 MOST IMPORTANT FEATURES
report.append("\n\n" + "="*100)
report.append("TOP 20 MOST IMPORTANT FEATURES")
report.append("="*100)
report.append("\nBased on combined ranking (Statistical + ML + Correlation):")
report.append("\n" + "-"*100)

top_20 = df_combined_ranking.head(20)

for idx, row in top_20.iterrows():
    feat_name = row['Feature'].replace('_target_enc', '').replace('_freq_enc', '').replace('_label', '')
    report.append(f"\n{idx+1}. {feat_name}")
    report.append(f"   Combined Score: {row['Final_Score']:.4f}")
    report.append(f"   Correlation: {row['Correlation']:.4f}")
    report.append(f"   RF Importance: {row['RF_Importance']:.6f}")
    report.append(f"   GB Importance: {row['GB_Importance']:.6f}")
    report.append(f"   P-Value: {row['P_Value']:.2e}")

# SECTION ANALYSIS
report.append("\n\n" + "="*100)
report.append("ANALYSIS BY VARIABLE SECTION")
report.append("="*100)
report.append("\nRanked by average correlation strength:")
report.append("\n" + "-"*100)

for idx, row in df_section.sort_values('Avg_Abs_Correlation', ascending=False).iterrows():
    report.append(f"\n{idx+1}. {row['Section']}")
    report.append(f"   Total Features: {int(row['Total_Features'])}")
    report.append(f"   Significant Features: {int(row['Significant_Features'])}")
    report.append(f"   Average |Correlation|: {row['Avg_Abs_Correlation']:.4f}")
    report.append(f"   Average |Cohen's D|: {row['Avg_Abs_Cohens_D']:.4f}")
    report.append(f"   Top Feature: {row['Top_Feature'].replace('_target_enc', '').replace('_freq_enc', '')}")

# KEY NUMERIC VARIABLES
report.append("\n\n" + "="*100)
report.append("KEY NUMERIC VARIABLES (SECOND-ORDER ANALYSIS)")
report.append("="*100)
report.append("\nBinning analysis shows which value ranges favor longer calls:")
report.append("\n" + "-"*100)

# Group by variable and show best/worst bins
for var in df_binning['Variable'].unique()[:8]:
    var_data = df_binning[df_binning['Variable'] == var].sort_values('Importance_Score', ascending=False)
    report.append(f"\n{var}:")
    
    # Best bin for long calls
    long_bin = var_data[var_data['Direction'] == 'Favors Long'].head(1)
    if not long_bin.empty:
        report.append(f"   Best for long calls: Bin {long_bin.iloc[0]['Bin']} - {long_bin.iloc[0]['Pct_Long']:.1f}% long calls")
    
    # Best bin for short calls
    short_bin = var_data[var_data['Direction'] == 'Favors Short'].head(1)
    if not short_bin.empty:
        report.append(f"   Best for short calls: Bin {short_bin.iloc[0]['Bin']} - {short_bin.iloc[0]['Pct_Long']:.1f}% long calls")

# KEY CATEGORICAL VALUES
report.append("\n\n" + "="*100)
report.append("KEY CATEGORICAL VALUES (SECOND-ORDER ANALYSIS)")
report.append("="*100)
report.append("\nMost discriminative categorical values:")
report.append("\n" + "-"*100)

top_cat_values = df_cat_values[df_cat_values['Total'] >= 10].nlargest(20, 'Importance_Score')

for idx, row in top_cat_values.iterrows():
    report.append(f"\n{row['Variable']}: {row['Value']}")
    report.append(f"   {row['Pct_Long']:.1f}% result in long calls ({row['Direction']})")
    report.append(f"   Sample size: {int(row['Total'])} calls")

# INSIGHTS & RECOMMENDATIONS
report.append("\n\n" + "="*100)
report.append("KEY INSIGHTS & RECOMMENDATIONS")
report.append("="*100)

report.append("\n1. MOST CRITICAL SUCCESS FACTORS FOR LONGER CALLS:")
report.append("   a) Discovery Questions: Asking 8+ questions strongly predicts longer calls (r=0.561)")
report.append("   b) Buying Signals: Identifying 2+ buying signals increases call length significantly (r=0.404)")
report.append("   c) Call Result: Follow-up scheduled outcome strongly associates with longer calls (r=0.560)")
report.append("   d) Objection Handling: Rebutting objections extends call duration (r=0.372)")

report.append("\n2. CUSTOMER ENGAGEMENT INDICATORS:")
report.append("   - Customer talk percentage: Higher in long calls (39.5% vs 32.4%)")
report.append("   - Customer sentiment: Positive sentiment correlates with longer calls")
report.append("   - Decision maker: Confirmed decision makers have longer calls")

report.append("\n3. CALL STRUCTURE & OPENING:")
report.append("   - Location mentioned: 60.3% in long calls vs 44.2% in short calls")
report.append("   - Business type mentioned: 74.5% in long calls vs 64.4% in short calls")
report.append("   - Call structure framed: 70% in long calls vs 56.3% in short calls")

report.append("\n4. AGENT FACTORS:")
report.append("   - Agent sentiment style: Confident & Assumptive style performs better")
report.append("   - Time to reason: Longer time correlates with longer overall calls")
report.append("   - Discovery quality: Advanced discovery questions are key differentiators")

report.append("\n5. OBJECTION HANDLING:")
report.append("   - Price mentions in final 2 min: More common in long calls (1.36 vs 0.25)")
report.append("   - Objections acknowledged: Higher in long calls (1.26 vs 0.48)")
report.append("   - Objections rebutted: Critical factor (1.61 vs 0.44)")

# ACTIONABLE RECOMMENDATIONS
report.append("\n\n" + "="*100)
report.append("ACTIONABLE RECOMMENDATIONS")
report.append("="*100)

report.append("\n1. TRAINING FOCUS AREAS:")
report.append("   - Teach agents to ask 8+ discovery questions per call")
report.append("   - Train on identifying and tracking buying signals")
report.append("   - Improve objection handling and rebuttal techniques")
report.append("   - Emphasize proper call structure and opening")

report.append("\n2. PROCESS IMPROVEMENTS:")
report.append("   - Ensure location and business type are mentioned early")
report.append("   - Frame the call structure within first 45 seconds")
report.append("   - Increase customer talk percentage through active listening")
report.append("   - Schedule follow-ups as a primary commitment goal")

report.append("\n3. QUALITY ASSURANCE:")
report.append("   - Monitor discovery question count in real-time")
report.append("   - Track buying signals identification")
report.append("   - Review calls where objections aren't rebutted")
report.append("   - Focus on agents with consistently short call durations")

report.append("\n4. LEAD QUALITY OPTIMIZATION:")
report.append("   - Prioritize leads where decision maker is confirmed")
report.append("   - Focus on services with higher engagement rates")
report.append("   - Consider timing/timezone factors for outreach")

# METHODOLOGY
report.append("\n\n" + "="*100)
report.append("METHODOLOGY")
report.append("="*100)

report.append("\n1. DATA PREPROCESSING:")
report.append("   - Selected 49 relevant variables across 6 major sections")
report.append("   - Intelligent encoding: One-hot for low cardinality, Target/Frequency for medium/high")
report.append("   - Missing value treatment: Imputation + indicator variables")
report.append("   - Final dataset: 1,218 calls with 150 features")

report.append("\n2. STATISTICAL ANALYSIS:")
report.append("   - T-tests and Mann-Whitney U tests for numeric variables")
report.append("   - Point-biserial correlation for all features")
report.append("   - Effect sizes calculated (Cohen's D)")
report.append("   - Multiple testing correction considered")

report.append("\n3. MACHINE LEARNING:")
report.append("   - Random Forest (200 trees, max_depth=10)")
report.append("   - Gradient Boosting (150 trees, max_depth=5)")
report.append("   - 70/30 train/test split with stratification")
report.append("   - Minimal overfitting observed (<2%)")

report.append("\n4. SECOND-ORDER ANALYSIS:")
report.append("   - Numerical binning: Quantile-based binning to identify critical ranges")
report.append("   - Categorical value analysis: Individual value contribution assessment")
report.append("   - Importance scoring: Deviation from 50/50 distribution")

report.append("\n\n" + "="*100)
report.append("END OF REPORT")
report.append("="*100)

# Write report
report_text = "\n".join(report)

with open('analysis_outputs/COMPREHENSIVE_ANALYSIS_REPORT_V2.txt', 'w', encoding='utf-8') as f:
    f.write(report_text)

print("\n[OK] Comprehensive report saved: COMPREHENSIVE_ANALYSIS_REPORT_V2.txt")
print("\n" + "="*100)
print("REPORT GENERATION COMPLETE")
print("="*100)

# Save key metrics summary
key_metrics = {
    'Total Calls': 1218,
    'Short Calls': 609,
    'Long Calls': 609,
    'Original Variables': 49,
    'Final Features': 150,
    'Significant Features': int(sig_features),
    'Highly Significant': int(highly_sig),
    'Large Effect Size': int(large_effect),
    'Strong Correlations': int(strong_corr),
    'RF Accuracy': 0.9809,
    'GB Accuracy': 0.9973,
    'Top Feature': str(top_20.iloc[0]['Feature']),
    'Top Correlation': float(top_20.iloc[0]['Correlation'])
}

import json
with open('analysis_outputs/key_metrics_summary.json', 'w') as f:
    json.dump(key_metrics, f, indent=2)

print("\n[OK] Key metrics summary saved: key_metrics_summary.json")

