"""
==============================================================================
LEVEL 1: VARIABLE-LEVEL VISUALIZATIONS
==============================================================================

Purpose: Create comprehensive visualizations for variable-level analysis
- Top variables by combined importance
- Section-wise analysis
- Feature type comparison
- Statistical significance summary

==============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*100)
print("LEVEL 1: VARIABLE-LEVEL VISUALIZATIONS")
print("="*100)

# ==============================================================================
# LOAD ALL ANALYSIS RESULTS
# ==============================================================================

print("\nLoading analysis results...")

df_importance = pd.read_csv('analysis_outputs/level1_variable/03_importance_combined.csv')
df_corr_target = pd.read_csv('analysis_outputs/level1_variable/02_correlation_with_target.csv')
df_stats_num = pd.read_csv('analysis_outputs/level1_variable/04_statistical_tests_numerical.csv')
df_stats_cat = pd.read_csv('analysis_outputs/level1_variable/04_statistical_tests_categorical.csv')

# Try to load SHAP, but handle if it doesn't exist
try:
    df_shap = pd.read_csv('analysis_outputs/level1_variable/05_shap_importance.csv')
    has_shap = True
    print("[OK] All results loaded (including SHAP)")
except FileNotFoundError:
    print("[WARNING] SHAP file not found - creating visualizations without SHAP data")
    # Create a dummy dataframe with same structure
    df_shap = pd.DataFrame({
        'Variable': df_importance['Variable'],
        'SHAP_Avg': 0.0
    })
    has_shap = False
    print("[OK] Results loaded (SHAP data not available)")

with open('analysis_outputs/level1_variable/01_metadata.json', 'r') as f:
    metadata = json.load(f)

# ==============================================================================
# VIZ 1: TOP 20 VARIABLES BY COMBINED IMPORTANCE
# ==============================================================================

print("\n" + "="*100)
print("VIZ 1: TOP 20 VARIABLES")
print("="*100)

fig, ax = plt.subplots(figsize=(14, 10))

top_20 = df_importance.head(20)

bars = ax.barh(range(len(top_20)), top_20['Combined_Score'],
              color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_yticks(range(len(top_20)))
ax.set_yticklabels(top_20['Variable'], fontsize=11)
ax.set_xlabel('Combined Importance Score', fontsize=13, fontweight='bold')
ax.set_title('LEVEL 1: TOP 20 MOST IMPORTANT VARIABLES\n' +
             'Combined Score: 35% Random Forest + 35% Gradient Boosting + 30% Correlation\n' +
             'Shows which VARIABLES (not specific values) matter most for call duration',
             fontsize=13, fontweight='bold', pad=25)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, score) in enumerate(zip(bars, top_20['Combined_Score'])):
    ax.text(score + 0.01, i, f'{score:.3f}', 
            va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/viz_06_top_20_variables.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_06_top_20_variables.png")
plt.close()

# ==============================================================================
# VIZ 2: SECTION-WISE ANALYSIS
# ==============================================================================

print("\nVIZ 2: SECTION-WISE ANALYSIS")

# Map variables to sections based on the original definition
VARIABLE_SECTIONS = {
    'lead_quality': ['LQ_Company_Name', 'LQ_Company_Address', 'LQ_Service', 'LQ_Customer_Name', 'Calls Count', 'Connection Made Calls'],
    'timings': ['TO_Event_O', 'timezone', 'season_status', 'season_month'],
    'lgs_department': ['TO_User_M', 'lgs_sentiment_style', 'lgs_agent_gender', 'TO_length_in_sec', 'is_decision_maker', 'ready_for_customers', 'forbidden_industry', 'ready_to_transfer'],
    'customer': ['customer_sentiment_lgs', 'customer_sentiment_omc', 'customer_language', 'customer_knows_marketing', 'customer_availability', 'who_said_hello_first_lgs', 'customer_marketing_experience'],
    'technical_quality': ['technical_quality_score', 'technical_quality_issues'],
    'omc_department': ['TO_OMC_User', 'TO_OMC_Disposiion', 'TO_OMC_Duration', 'omc_agent_sentiment_style', 'omc_who_said_hello_first'],
    'omc_engagement': ['customer_talk_percentage', 'total_discovery_questions', 'total_buying_signals'],
    'omc_opening': ['time_to_reason_seconds', 'location_mentioned', 'business_type_mentioned', 'within_45_seconds', 'call_structure_framed'],
    'omc_objections': ['total_objections', 'objections_acknowledged', 'price_mentions_final_2min', 'timeline_mentions_final_2min', 'contract_mentions_final_2min', 'objections_rebutted'],
    'omc_pace': ['total_interruptions'],
    'omc_outcome': ['commitment_type', 'call_result_tag']
}

# Map variables to sections
section_mapping = {}
for section, vars_list in VARIABLE_SECTIONS.items():
    for var in vars_list:
        section_mapping[var] = section

# Calculate section statistics
section_stats = []
for section, vars_list in VARIABLE_SECTIONS.items():
    section_vars = [v for v in df_importance['Variable'] if section_mapping.get(v) == section]
    
    if len(section_vars) == 0:
        continue
    
    # Get stats for these variables
    avg_importance = df_importance[df_importance['Variable'].isin(section_vars)]['Combined_Score'].mean()
    avg_corr = df_corr_target[df_corr_target['Variable'].isin(section_vars)]['Abs_Correlation'].mean()
    
    # Count significant variables
    sig_count_num = len(df_stats_num[(df_stats_num['Variable'].isin(section_vars)) & (df_stats_num['Significant_MW'] == 'Yes')])
    sig_count_cat = len(df_stats_cat[(df_stats_cat['Variable'].isin(section_vars)) & (df_stats_cat['Significant'] == 'Yes')])
    sig_count = sig_count_num + sig_count_cat
    
    section_stats.append({
        'Section': section,
        'Avg_Importance': avg_importance,
        'Avg_Correlation': avg_corr,
        'Significant_Count': sig_count,
        'Total_Variables': len(section_vars)
    })

df_sections = pd.DataFrame(section_stats)

# Create dual plot
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Plot 1: Average Importance
ax1 = axes[0]
df_sections_sorted = df_sections.sort_values('Avg_Importance', ascending=False)

bars1 = ax1.barh(range(len(df_sections_sorted)), df_sections_sorted['Avg_Importance'],
                color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)

ax1.set_yticks(range(len(df_sections_sorted)))
ax1.set_yticklabels(df_sections_sorted['Section'], fontsize=10)
ax1.set_xlabel('Average Importance Score', fontsize=11, fontweight='bold')
ax1.set_title('AVERAGE VARIABLE IMPORTANCE BY SECTION\n' +
              'Shows which sections have most important variables',
              fontsize=11, fontweight='bold', pad=10)
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)

for i, (bar, val) in enumerate(zip(bars1, df_sections_sorted['Avg_Importance'])):
    ax1.text(val + 0.005, i, f'{val:.3f}', va='center', fontsize=9, fontweight='bold')

# Plot 2: Significant Count
ax2 = axes[1]
df_sections_sorted2 = df_sections.sort_values('Significant_Count', ascending=False)

bars2 = ax2.barh(range(len(df_sections_sorted2)), df_sections_sorted2['Significant_Count'],
                color='#45B7D1', alpha=0.8, edgecolor='black', linewidth=1.5)

ax2.set_yticks(range(len(df_sections_sorted2)))
ax2.set_yticklabels(df_sections_sorted2['Section'], fontsize=10)
ax2.set_xlabel('Number of Significant Variables', fontsize=11, fontweight='bold')
ax2.set_title('STATISTICALLY SIGNIFICANT VARIABLES BY SECTION\n' +
              'Shows which sections have most significant variables (p<0.05)',
              fontsize=11, fontweight='bold', pad=10)
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)

for i, (bar, val, total) in enumerate(zip(bars2, df_sections_sorted2['Significant_Count'], df_sections_sorted2['Total_Variables'])):
    ax2.text(val + 0.2, i, f'{int(val)}/{int(total)}', va='center', fontsize=9, fontweight='bold')

plt.suptitle('LEVEL 1: SECTION-WISE VARIABLE ANALYSIS\n' +
             'Compares performance across variable sections (1-6.6)',
             fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/viz_06_section_analysis.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_06_section_analysis.png")
plt.close()

# ==============================================================================
# VIZ 3: CORRELATION VS FEATURE IMPORTANCE
# ==============================================================================

print("\nVIZ 3: CORRELATION VS FEATURE IMPORTANCE")

# Merge data
df_compare = df_importance[['Variable', 'Combined_Score']].merge(
    df_corr_target[['Variable', 'Abs_Correlation']], on='Variable'
).merge(
    df_shap[['Variable', 'SHAP_Avg']], on='Variable'
)

fig, ax = plt.subplots(figsize=(14, 10))

# Scatter plot
scatter = ax.scatter(df_compare['Abs_Correlation'], 
                     df_compare['Combined_Score'],
                     s=df_compare['SHAP_Avg'] * 1000,  # Size by SHAP
                     c=df_compare['Combined_Score'],
                     cmap='viridis',
                     alpha=0.6,
                     edgecolors='black',
                     linewidth=1)

# Label top 10 points
top_10 = df_compare.nlargest(10, 'Combined_Score')
for idx, row in top_10.iterrows():
    ax.annotate(row['Variable'], 
                xy=(row['Abs_Correlation'], row['Combined_Score']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=7, fontweight='normal',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.7, edgecolor='black', linewidth=0.5))

ax.set_xlabel('Absolute Correlation with Target', fontsize=13, fontweight='bold')
ax.set_ylabel('Combined Importance Score', fontsize=13, fontweight='bold')
ax.set_title('LEVEL 1: CORRELATION vs ML IMPORTANCE\n' +
             'Bubble size = SHAP importance | Color = Combined score\n' +
             'Top 10 variables labeled',
             fontsize=13, fontweight='bold', pad=20)
ax.grid(alpha=0.3)

# Colorbar
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Combined Importance', fontsize=11)

plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/viz_06_correlation_vs_importance.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_06_correlation_vs_importance.png")
plt.close()

# ==============================================================================
# VIZ 4: STATISTICAL SIGNIFICANCE SUMMARY
# ==============================================================================

print("\nVIZ 4: STATISTICAL SIGNIFICANCE SUMMARY")

# Combine numerical and categorical
df_stats_combined = pd.concat([
    df_stats_num[['Variable', 'Significant_MW', 'Abs_Cohens_D']].rename(
        columns={'Significant_MW': 'Significant', 'Abs_Cohens_D': 'Effect_Size'}
    ),
    df_stats_cat[['Variable', 'Significant', 'Cramers_V']].rename(
        columns={'Cramers_V': 'Effect_Size'}
    )
], ignore_index=True)

# Top 40 by effect size
top_40_effect = df_stats_combined.nlargest(40, 'Effect_Size')

fig, ax = plt.subplots(figsize=(14, 16))

colors = ['#4ECDC4' if s == 'Yes' else '#FF6B6B' for s in top_40_effect['Significant']]

bars = ax.barh(range(len(top_40_effect)), top_40_effect['Effect_Size'],
              color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_yticks(range(len(top_40_effect)))
ax.set_yticklabels(top_40_effect['Variable'], fontsize=9)
ax.set_xlabel('Effect Size (Cohen\'s D / Cramér\'s V)', fontsize=13, fontweight='bold')
ax.set_title('LEVEL 1: TOP 40 VARIABLES BY EFFECT SIZE\n' +
             'TEAL = Statistically Significant (p<0.05) | RED = Not Significant\n' +
             'Shows practical significance of differences between Short vs Long calls',
             fontsize=13, fontweight='bold', pad=25)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Add value labels at end of bars
for i, (bar, val) in enumerate(zip(bars, top_40_effect['Effect_Size'])):
    ax.text(val + 0.02, i, f'{val:.3f}', 
            va='center', fontsize=8, fontweight='bold')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#4ECDC4', edgecolor='black', label='Significant (p<0.05)'),
    Patch(facecolor='#FF6B6B', edgecolor='black', label='Not Significant')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.tight_layout()

# Save with error handling for Windows file locks
try:
    plt.savefig('analysis_outputs/level1_variable/viz_06_effect_sizes.png',
                dpi=300, bbox_inches='tight')
    print("[OK] Saved: viz_06_effect_sizes.png")
except Exception as e:
    print(f"[WARNING] Could not save viz_06_effect_sizes.png: {e}")
    print("[WARNING] File may be open in another program. Close it and retry.")
finally:
    plt.close()

# ==============================================================================
# VIZ 5: MODEL COMPARISON (RF vs GB)
# ==============================================================================

print("\nVIZ 5: MODEL COMPARISON")

# Top 20 variables
top_20_vars = df_importance.head(20)['Variable'].tolist()
df_model_compare = df_importance[df_importance['Variable'].isin(top_20_vars)].sort_values('RF_Importance', ascending=False)

fig, ax = plt.subplots(figsize=(14, 10))

x = np.arange(len(df_model_compare))
width = 0.35

bars1 = ax.barh(x - width/2, df_model_compare['RF_Importance'], width,
               label='Random Forest', color='#98D8C8', alpha=0.8, edgecolor='black')
bars2 = ax.barh(x + width/2, df_model_compare['GB_Importance'], width,
               label='Gradient Boosting', color='#F7DC6F', alpha=0.8, edgecolor='black')

ax.set_yticks(x)
ax.set_yticklabels(df_model_compare['Variable'], fontsize=10)
ax.set_xlabel('Feature Importance', fontsize=13, fontweight='bold')
ax.set_title('LEVEL 1: MODEL COMPARISON - TOP 20 VARIABLES\n' +
             'Comparing Random Forest vs Gradient Boosting feature importance\n' +
             'Consistent ranking = More reliable',
             fontsize=13, fontweight='bold', pad=20)
ax.invert_yaxis()
ax.legend(fontsize=11)
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_outputs/level1_variable/viz_06_model_comparison.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_06_model_comparison.png")
plt.close()

print("\n" + "="*100)
print("LEVEL 1 VISUALIZATIONS COMPLETE")
print("="*100)
print("\n[OK] Created 5 comprehensive visualizations")
print("   1. Top 20 variables by importance")
print("   2. Section-wise analysis")
print("   3. Correlation vs importance scatter")
print("   4. Effect sizes with significance")
print("   5. Model comparison (RF vs GB)")

