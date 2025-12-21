"""
STEP 3: COMPREHENSIVE STATISTICAL ANALYSIS
Determining which variables contribute to longer OMC call durations

Tests performed:
- Numeric variables: T-test (parametric) or Mann-Whitney U (non-parametric)
- Categorical variables (via encoded features): Point-biserial correlation
- Effect sizes: Cohen's D for numeric, Correlation strength for categorical
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import mannwhitneyu, ttest_ind, pearsonr, pointbiserialr
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("COMPREHENSIVE STATISTICAL ANALYSIS")
print("="*100)

# Load encoded data
df_short = pd.read_csv('analysis_outputs/02_short_calls_encoded.csv')
df_long = pd.read_csv('analysis_outputs/02_long_calls_encoded.csv')
df_combined = pd.read_csv('analysis_outputs/02_combined_encoded.csv')

print(f"\nLoaded encoded data:")
print(f"  Short: {df_short.shape}")
print(f"  Long: {df_long.shape}")
print(f"  Combined: {df_combined.shape}")

# Create binary target
df_combined['target'] = (df_combined['call_duration_group'] == 'Long (>4.88 min)').astype(int)

# Get all numeric columns (everything except label now)
all_features = [col for col in df_combined.columns if col not in ['call_duration_group', 'target']]

print(f"\nTotal features for analysis: {len(all_features)}")

# ==================================================================================
# STATISTICAL TESTS FOR ALL FEATURES
# ==================================================================================

print("\n" + "="*100)
print("STATISTICAL TESTING - ALL FEATURES")
print("="*100)

statistical_results = []

for col in all_features:
    short_vals = df_short[col].dropna()
    long_vals = df_long[col].dropna()
    
    if len(short_vals) < 3 or len(long_vals) < 3:
        continue
    
    # Descriptive statistics
    short_mean = short_vals.mean()
    long_mean = long_vals.mean()
    short_median = short_vals.median()
    long_median = long_vals.median()
    short_std = short_vals.std()
    long_std = long_vals.std()
    
    # Test for normality (Shapiro-Wilk on sample)
    sample_size = min(100, len(short_vals), len(long_vals))
    try:
        short_sample = short_vals.sample(min(sample_size, len(short_vals)), random_state=42)
        long_sample = long_vals.sample(min(sample_size, len(long_vals)), random_state=42)
        
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
    
    # Effect size (Cohen's D)
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
    
    # Point-biserial correlation with target
    valid_data = df_combined[[col, 'target']].dropna()
    if len(valid_data) >= 30:
        try:
            correlation, corr_p_value = pointbiserialr(valid_data['target'], valid_data[col])
        except:
            correlation = 0
            corr_p_value = 1.0
    else:
        correlation = 0
        corr_p_value = 1.0
    
    statistical_results.append({
        'Feature': col,
        'Short_Mean': short_mean,
        'Long_Mean': long_mean,
        'Short_Median': short_median,
        'Long_Median': long_median,
        'Short_Std': short_std,
        'Long_Std': long_std,
        'Mean_Difference': long_mean - short_mean,
        'Pct_Difference': pct_diff,
        'P_Value': p_value,
        'Test_Used': test_used,
        'Cohens_D': cohens_d,
        'Abs_Cohens_D': abs(cohens_d),
        'Effect_Size': 'Large' if abs(cohens_d) > 0.8 else ('Medium' if abs(cohens_d) > 0.5 else ('Small' if abs(cohens_d) > 0.2 else 'Negligible')),
        'Correlation': correlation,
        'Abs_Correlation': abs(correlation),
        'Correlation_P_Value': corr_p_value,
        'Significant': 'Yes' if p_value < 0.05 else 'No',
        'Highly_Significant': 'Yes' if p_value < 0.001 else 'No',
        'N_Short': len(short_vals),
        'N_Long': len(long_vals)
    })
    
    if len(statistical_results) % 50 == 0:
        print(f"  Processed {len(statistical_results)} features...")

df_stats = pd.DataFrame(statistical_results)

# Sort by multiple criteria for comprehensive ranking
df_stats['Combined_Score'] = (
    (1 - df_stats['P_Value']) * 0.3 +  # Significance
    df_stats['Abs_Cohens_D'] * 0.35 +  # Effect size
    df_stats['Abs_Correlation'] * 0.35  # Correlation strength
)

df_stats = df_stats.sort_values('Combined_Score', ascending=False)

# Save results
df_stats.to_csv('analysis_outputs/03_statistical_analysis_all_features.csv', index=False)

print(f"\n[OK] Statistical analysis complete: {len(df_stats)} features analyzed")
print(f"[OK] Saved: 03_statistical_analysis_all_features.csv")

# ==================================================================================
# SUMMARY STATISTICS
# ==================================================================================

print("\n" + "="*100)
print("STATISTICAL SUMMARY")
print("="*100)

sig_count = (df_stats['P_Value'] < 0.05).sum()
highly_sig_count = (df_stats['P_Value'] < 0.001).sum()
large_effect_count = (df_stats['Abs_Cohens_D'] > 0.8).sum()
medium_effect_count = ((df_stats['Abs_Cohens_D'] > 0.5) & (df_stats['Abs_Cohens_D'] <= 0.8)).sum()

print(f"\nStatistical Significance:")
print(f"  Significant (p<0.05): {sig_count} ({sig_count/len(df_stats)*100:.1f}%)")
print(f"  Highly Significant (p<0.001): {highly_sig_count} ({highly_sig_count/len(df_stats)*100:.1f}%)")

print(f"\nEffect Sizes:")
print(f"  Large effect (|d|>0.8): {large_effect_count}")
print(f"  Medium effect (0.5<|d|<=0.8): {medium_effect_count}")

strong_corr_count = (df_stats['Abs_Correlation'] > 0.3).sum()
moderate_corr_count = ((df_stats['Abs_Correlation'] > 0.1) & (df_stats['Abs_Correlation'] <= 0.3)).sum()

print(f"\nCorrelations:")
print(f"  Strong (|r|>0.3): {strong_corr_count}")
print(f"  Moderate (0.1<|r|<=0.3): {moderate_corr_count}")

# ==================================================================================
# TOP 50 MOST IMPORTANT FEATURES
# ==================================================================================

print("\n" + "="*100)
print("TOP 50 MOST IMPORTANT FEATURES (by Combined Score)")
print("="*100)

top_50 = df_stats.head(50)

print("\n" + "-"*100)
display_cols = ['Feature', 'Short_Mean', 'Long_Mean', 'Pct_Difference', 'P_Value', 'Cohens_D', 'Correlation', 'Effect_Size', 'Significant']
print(top_50[display_cols].to_string(index=False))

# Save top features
top_50.to_csv('analysis_outputs/03_top_50_features.csv', index=False)
print(f"\n[OK] Saved: 03_top_50_features.csv")

# ==================================================================================
# FEATURE CATEGORIES ANALYSIS
# ==================================================================================

print("\n" + "="*100)
print("FEATURE CATEGORIES BREAKDOWN")
print("="*100)

# Categorize features
original_numeric = []
one_hot_encoded = []
target_encoded = []
frequency_encoded = []
missing_indicators = []
label_encoded = []

for feature in df_stats['Feature']:
    if '_is_missing' in feature:
        missing_indicators.append(feature)
    elif '_target_enc' in feature:
        target_encoded.append(feature)
    elif '_freq_enc' in feature:
        frequency_encoded.append(feature)
    elif '_label' in feature:
        label_encoded.append(feature)
    elif '_' in feature and any(feature.startswith(prefix) for prefix in [
        'timezone_', 'season_', 'lgs_agent_gender_', 'is_decision_maker_',
        'ready_for_customers_', 'forbidden_industry_', 'ready_to_transfer_',
        'customer_language_', 'customer_knows_marketing_', 'customer_availability_',
        'who_said_hello_first_lgs_', 'omc_who_said_hello_first_',
        'location_mentioned_', 'business_type_mentioned_', 'within_45_seconds_',
        'call_structure_framed_'
    ]):
        one_hot_encoded.append(feature)
    else:
        original_numeric.append(feature)

print(f"\nFeature type breakdown:")
print(f"  Original numeric: {len(original_numeric)}")
print(f"  One-hot encoded: {len(one_hot_encoded)}")
print(f"  Target encoded: {len(target_encoded)}")
print(f"  Frequency encoded: {len(frequency_encoded)}")
print(f"  Missing indicators: {len(missing_indicators)}")
print(f"  Label encoded: {len(label_encoded)}")

# Top features by category
print(f"\nTop 10 Original Numeric Features:")
top_numeric = df_stats[df_stats['Feature'].isin(original_numeric)].head(10)
for idx, row in top_numeric.iterrows():
    print(f"  {row['Feature']}: p={row['P_Value']:.6f}, d={row['Cohens_D']:.3f}, r={row['Correlation']:.3f}")

print(f"\nTop 10 Target Encoded Features:")
top_target = df_stats[df_stats['Feature'].isin(target_encoded)].head(10)
for idx, row in top_target.iterrows():
    orig_name = row['Feature'].replace('_target_enc', '')
    print(f"  {orig_name}: p={row['P_Value']:.6f}, d={row['Cohens_D']:.3f}, r={row['Correlation']:.3f}")

print(f"\nTop 10 One-Hot Encoded Features:")
top_onehot = df_stats[df_stats['Feature'].isin(one_hot_encoded)].head(10)
for idx, row in top_onehot.iterrows():
    print(f"  {row['Feature']}: p={row['P_Value']:.6f}, d={row['Cohens_D']:.3f}, r={row['Correlation']:.3f}")

# ==================================================================================
# VARIABLE SECTION ANALYSIS
# ==================================================================================

print("\n" + "="*100)
print("ANALYSIS BY VARIABLE SECTION")
print("="*100)

# Define sections based on user's categorization
sections = {
    'Lead Quality': ['LQ_', 'Calls Count', 'Connection Made Calls'],
    'Timings': ['TO_Event_O', 'timezone', 'season'],
    'LGS Department': ['TO_User_M', 'lgs_', 'TO_length_in_sec', 'is_decision_maker', 
                        'ready_for_customers', 'forbidden_industry', 'ready_to_transfer'],
    'Customer': ['customer_sentiment', 'customer_language', 'customer_knows_marketing',
                 'customer_availability', 'who_said_hello_first_lgs', 'customer_marketing_experience'],
    'Technical Quality': ['technical_quality'],
    'OMC Department': ['TO_OMC_User', 'TO_OMC_Disposiion', 'TO_OMC_Duration', 'omc_agent_sentiment', 'omc_who_said_hello'],
    'OMC Engagement': ['customer_talk_percentage', 'total_discovery_questions', 'total_buying_signals'],
    'OMC Opening': ['time_to_reason', 'location_mentioned', 'business_type_mentioned', 
                     'within_45_seconds', 'call_structure_framed'],
    'OMC Objections': ['total_objections', 'objections_acknowledged', 'price_mentions', 
                        'timeline_mentions', 'contract_mentions', 'objections_rebutted'],
    'OMC Pace': ['total_interruptions'],
    'OMC Outcome': ['commitment_type', 'call_result_tag']
}

section_analysis = []

for section_name, keywords in sections.items():
    # Find features matching this section
    section_features = []
    for feature in df_stats['Feature']:
        if any(keyword in feature for keyword in keywords):
            section_features.append(feature)
    
    if len(section_features) > 0:
        section_df = df_stats[df_stats['Feature'].isin(section_features)]
        
        analysis = {
            'Section': section_name,
            'Total_Features': len(section_features),
            'Significant_Features': (section_df['P_Value'] < 0.05).sum(),
            'Avg_P_Value': section_df['P_Value'].mean(),
            'Avg_Abs_Cohens_D': section_df['Abs_Cohens_D'].mean(),
            'Avg_Abs_Correlation': section_df['Abs_Correlation'].mean(),
            'Top_Feature': section_df.iloc[0]['Feature'],
            'Top_Feature_Score': section_df.iloc[0]['Combined_Score']
        }
        section_analysis.append(analysis)

df_section_analysis = pd.DataFrame(section_analysis)
df_section_analysis = df_section_analysis.sort_values('Avg_Abs_Correlation', ascending=False)

print("\n" + "-"*100)
print(df_section_analysis.to_string(index=False))

df_section_analysis.to_csv('analysis_outputs/03_section_analysis.csv', index=False)
print(f"\n[OK] Saved: 03_section_analysis.csv")

print("\n" + "="*100)
print("COMPREHENSIVE STATISTICAL ANALYSIS COMPLETE")
print("="*100)
print("\nKey findings:")
print(f"  - {sig_count} features show significant differences (p<0.05)")
print(f"  - {large_effect_count} features have large effect sizes (|d|>0.8)")
print(f"  - {strong_corr_count} features have strong correlations (|r|>0.3)")
print(f"\nMost important section: {df_section_analysis.iloc[0]['Section']}")
print(f"  with average |r| = {df_section_analysis.iloc[0]['Avg_Abs_Correlation']:.3f}")

