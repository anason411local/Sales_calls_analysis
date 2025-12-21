"""
STEP 7: COMPREHENSIVE VISUALIZATIONS
Creates clear, insightful visualizations for all analyses
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*100)
print("CREATING COMPREHENSIVE VISUALIZATIONS")
print("="*100)

# Load data
df_stats = pd.read_csv('analysis_outputs/03_statistical_analysis_all_features.csv')
df_combined_ranking = pd.read_csv('analysis_outputs/04_combined_feature_ranking.csv')
df_section = pd.read_csv('analysis_outputs/03_section_analysis.csv')
df_binning = pd.read_csv('analysis_outputs/05_numerical_binning_analysis.csv')
df_cat_values = pd.read_csv('analysis_outputs/05_categorical_value_importance.csv')

print("\nData loaded for visualizations")

# ==================================================================================
# VIZ 1: TOP 20 FEATURES BY COMBINED SCORE
# ==================================================================================

print("\nCreating Viz 1: Top 20 Features...")

fig, ax = plt.subplots(figsize=(14, 10))

top_20 = df_combined_ranking.head(20)

bars = ax.barh(range(len(top_20)), top_20['Final_Score'], 
              color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_yticks(range(len(top_20)))
ax.set_yticklabels([f.replace('_target_enc', '').replace('_freq_enc', '').replace('_label', '')[:40] 
                     for f in top_20['Feature']], fontsize=10)
ax.set_xlabel('Combined Importance Score (Higher = More Important)', fontsize=12, fontweight='bold')
ax.set_title('TOP 20 MOST IMPORTANT FEATURES FOR CALL DURATION\n' +
             'Combined Score: 35% Random Forest + 35% Gradient Boosting + 30% Correlation\n' +
             'Only includes variables from Sections 1-6.6 (49 specified variables)', 
             fontsize=13, fontweight='bold', pad=20)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, score) in enumerate(zip(bars, top_20['Final_Score'])):
    ax.text(score + 0.01, i, f'{score:.3f}', va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('analysis_outputs/viz_01_top_20_features.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_01_top_20_features.png")
plt.close()

# ==================================================================================
# VIZ 2: SECTION ANALYSIS COMPARISON
# ==================================================================================

print("Creating Viz 2: Section Analysis...")

fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Plot 1: Average Correlation by Section
ax1 = axes[0]
df_section_sorted = df_section.sort_values('Avg_Abs_Correlation', ascending=False)

bars1 = ax1.barh(range(len(df_section_sorted)), df_section_sorted['Avg_Abs_Correlation'],
                color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)

ax1.set_yticks(range(len(df_section_sorted)))
ax1.set_yticklabels(df_section_sorted['Section'], fontsize=10)
ax1.set_xlabel('Average |Correlation| (Point-Biserial)', fontsize=11, fontweight='bold')
ax1.set_title('AVERAGE CORRELATION STRENGTH BY SECTION\n' +
              'Shows which variable sections have strongest relationship with call duration', 
              fontsize=11, fontweight='bold', pad=10)
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)

# Plot 2: Significant Features Count
ax2 = axes[1]
df_section_sorted2 = df_section.sort_values('Significant_Features', ascending=False)

bars2 = ax2.barh(range(len(df_section_sorted2)), df_section_sorted2['Significant_Features'],
                color='#45B7D1', alpha=0.8, edgecolor='black', linewidth=1.5)

ax2.set_yticks(range(len(df_section_sorted2)))
ax2.set_yticklabels(df_section_sorted2['Section'], fontsize=10)
ax2.set_xlabel('Count of Significant Features (p < 0.05)', fontsize=11, fontweight='bold')
ax2.set_title('NUMBER OF SIGNIFICANT FEATURES BY SECTION\n' +
              'Shows which sections have most features that matter for call duration', 
              fontsize=11, fontweight='bold', pad=10)
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)

# Add value labels
for bars, values in [(bars1, df_section_sorted['Avg_Abs_Correlation']), 
                      (bars2, df_section_sorted2['Significant_Features'])]:
    for i, (bar, val) in enumerate(zip(bars, values)):
        if bars == bars2:
            ax2.text(val + 0.2, i, f'{int(val)}', va='center', fontsize=9, fontweight='bold')
        else:
            ax1.text(val + 0.005, i, f'{val:.3f}', va='center', fontsize=9, fontweight='bold')

plt.suptitle('ANALYSIS BY VARIABLE SECTION (Sections 1-6.6)\n' +
             'Left: Correlation Strength | Right: Statistical Significance Count', 
             fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('analysis_outputs/viz_02_section_analysis.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_02_section_analysis.png")
plt.close()

# ==================================================================================
# VIZ 3: NUMERICAL BINNING ANALYSIS (Top Variables)
# ==================================================================================

print("Creating Viz 3: Numerical Binning Analysis...")

top_vars_binning = df_binning['Variable'].unique()[:6]

fig, axes = plt.subplots(3, 2, figsize=(16, 18))
axes = axes.flatten()

for idx, var in enumerate(top_vars_binning):
    ax = axes[idx]
    var_data = df_binning[df_binning['Variable'] == var].copy()
    
    x = np.arange(len(var_data))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, var_data['Count_Short'], width, label='Short Calls',
                  color='#FF6B6B', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, var_data['Count_Long'], width, label='Long Calls',
                  color='#4ECDC4', alpha=0.8, edgecolor='black')
    
    ax.set_xticks(x)
    ax.set_xticklabels([str(b)[:10] for b in var_data['Bin']], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Call Count (Number of Calls)', fontsize=10, fontweight='bold')
    ax.set_title(f'{var}\nRED = Short Calls (<4.88 min) | TEAL = Long Calls (>4.88 min)', 
                 fontsize=10, fontweight='bold', pad=10)
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

plt.suptitle('NUMERICAL VARIABLE BINNING ANALYSIS: Which Ranges Matter Most?\n' +
             'Shows distribution of calls across different value ranges for top numeric variables', 
             fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('analysis_outputs/viz_03_numerical_binning.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_03_numerical_binning.png")
plt.close()

# ==================================================================================
# VIZ 4: CATEGORICAL VALUE IMPORTANCE (Top Variables)
# ==================================================================================

print("Creating Viz 4: Categorical Value Importance...")

top_vars_cat = df_cat_values[df_cat_values['Total'] >= 5].nlargest(30, 'Importance_Score')

fig, ax = plt.subplots(figsize=(14, 12))

colors = ['#4ECDC4' if d == 'Favors Long' else '#FF6B6B' for d in top_vars_cat['Direction']]

bars = ax.barh(range(len(top_vars_cat)), top_vars_cat['Importance_Score'],
              color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_yticks(range(len(top_vars_cat)))
labels = [f"{row['Variable']}: {str(row['Value'])[:30]}" 
          for _, row in top_vars_cat.iterrows()]
ax.set_yticklabels(labels, fontsize=9)
ax.set_xlabel('Importance Score (% Deviation from 50-50 Split)', fontsize=12, fontweight='bold')
ax.set_title('TOP 30 MOST DISCRIMINATIVE CATEGORICAL VALUES\n' +
             'TEAL = Strongly Associated with LONG Calls (>4.88 min)\n' +
             'RED = Strongly Associated with SHORT Calls (<4.88 min)', 
             fontsize=13, fontweight='bold', pad=20)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_outputs/viz_04_categorical_values.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_04_categorical_values.png")
plt.close()

# ==================================================================================
# VIZ 5: FEATURE TYPE COMPARISON
# ==================================================================================

print("Creating Viz 5: Feature Type Comparison...")

# Categorize features
feature_types = []
for feature in df_stats['Feature']:
    if '_target_enc' in feature:
        feature_types.append('Target Encoded')
    elif '_freq_enc' in feature:
        feature_types.append('Frequency Encoded')
    elif '_is_missing' in feature:
        feature_types.append('Missing Indicator')
    elif '_label' in feature:
        feature_types.append('Label Encoded')
    elif '_' in feature and len(feature.split('_')) >= 2:
        feature_types.append('One-Hot Encoded')
    else:
        feature_types.append('Original Numeric')

df_stats['Feature_Type'] = feature_types

type_summary = df_stats.groupby('Feature_Type').agg({
    'Abs_Correlation': 'mean',
    'Abs_Cohens_D': 'mean',
    'P_Value': lambda x: (x < 0.05).sum()
}).reset_index()

type_summary.columns = ['Feature_Type', 'Avg_Correlation', 'Avg_Effect_Size', 'Significant_Count']

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Plot 1: Average Correlation
ax1 = axes[0]
bars1 = ax1.bar(range(len(type_summary)), type_summary['Avg_Correlation'],
               color='#98D8C8', alpha=0.8, edgecolor='black', linewidth=1.5)
ax1.set_xticks(range(len(type_summary)))
ax1.set_xticklabels(type_summary['Feature_Type'], rotation=45, ha='right', fontsize=9)
ax1.set_ylabel('Average |Correlation|', fontsize=11, fontweight='bold')
ax1.set_title('AVERAGE CORRELATION\nShows strength of relationship', fontsize=11, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Plot 2: Average Effect Size
ax2 = axes[1]
bars2 = ax2.bar(range(len(type_summary)), type_summary['Avg_Effect_Size'],
               color='#F7DC6F', alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.set_xticks(range(len(type_summary)))
ax2.set_xticklabels(type_summary['Feature_Type'], rotation=45, ha='right', fontsize=9)
ax2.set_ylabel("Average |Cohen's D|", fontsize=11, fontweight='bold')
ax2.set_title("AVERAGE EFFECT SIZE\nShows practical significance", fontsize=11, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

# Plot 3: Significant Count
ax3 = axes[2]
bars3 = ax3.bar(range(len(type_summary)), type_summary['Significant_Count'],
               color='#45B7D1', alpha=0.8, edgecolor='black', linewidth=1.5)
ax3.set_xticks(range(len(type_summary)))
ax3.set_xticklabels(type_summary['Feature_Type'], rotation=45, ha='right', fontsize=9)
ax3.set_ylabel('Count (p<0.05)', fontsize=11, fontweight='bold')
ax3.set_title('SIGNIFICANT FEATURES COUNT\nStatistically significant (p<0.05)', fontsize=11, fontweight='bold')
ax3.grid(axis='y', alpha=0.3)

plt.suptitle('FEATURE PERFORMANCE BY ENCODING TYPE\n' +
             'Compares different encoding methods used for categorical variables', 
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('analysis_outputs/viz_05_feature_type_comparison.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_05_feature_type_comparison.png")
plt.close()

print("\n" + "="*100)
print("COMPREHENSIVE VISUALIZATIONS COMPLETE")
print("="*100)
print("\nCreated 5 comprehensive visualizations:")
print("  1. Top 20 Features by Combined Score")
print("  2. Section Analysis Comparison")
print("  3. Numerical Binning Analysis")
print("  4. Categorical Value Importance")
print("  5. Feature Type Comparison")

