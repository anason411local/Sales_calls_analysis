"""
VALUE-LEVEL VISUALIZATIONS
Creates clear visualizations showing which specific values within each variable matter most
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
print("CREATING VALUE-LEVEL VISUALIZATIONS")
print("="*100)

# ==================================================================================
# LOAD VALUE-LEVEL ANALYSIS RESULTS
# ==================================================================================

print("\nLoading value-level analysis results...")
df_values = pd.read_csv('analysis_outputs/08_value_level_analysis_all.csv')

print(f"Total value-level results: {len(df_values)}")
print(f"Unique variables: {df_values['Variable'].nunique()}")

# ==================================================================================
# VIZ 1: TOP VARIABLES - MOST DISCRIMINATIVE VALUES
# ==================================================================================

print("\n" + "="*100)
print("VIZ 1: TOP 30 MOST DISCRIMINATIVE VALUES (ALL VARIABLES)")
print("="*100)

fig, ax = plt.subplots(figsize=(16, 14))

top_30 = df_values.nlargest(30, 'Importance_Score')

colors = ['#4ECDC4' if d == 'Favors Long Calls' else '#FF6B6B' for d in top_30['Direction']]

bars = ax.barh(range(len(top_30)), top_30['Importance_Score'],
              color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_yticks(range(len(top_30)))
labels = [f"{row['Variable']}: {str(row['Value'])[:35]}" for _, row in top_30.iterrows()]
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel('Importance Score (% Deviation from 50-50 Split)', fontsize=13, fontweight='bold')
ax.set_title('TOP 30 MOST DISCRIMINATIVE VALUES ACROSS ALL VARIABLES\n' +
             'TEAL = Associated with LONG Calls (>4.88 min) | RED = Associated with SHORT Calls (<4.88 min)\n' +
             'Shows which specific values within each variable drive call duration differences', 
             fontsize=14, fontweight='bold', pad=25)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Add percentage labels
for i, (bar, row) in enumerate(zip(bars, top_30.iterrows())):
    row = row[1]
    pct = row['Pct_Long'] if row['Direction'] == 'Favors Long Calls' else row['Pct_Short']
    ax.text(row['Importance_Score'] + 1, i, f"{pct:.0f}%", 
            va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('analysis_outputs/viz_08_top_discriminative_values.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_08_top_discriminative_values.png")
plt.close()

# ==================================================================================
# VIZ 2: SPECIFIC VARIABLES - BREAKDOWN BY VALUE
# ==================================================================================

print("\n" + "="*100)
print("VIZ 2: TOP VARIABLES - VALUE BREAKDOWN")
print("="*100)

# Find top variables by average importance across their values
var_importance = df_values.groupby('Variable').agg({
    'Importance_Score': 'mean',
    'Value': 'count'
}).reset_index()
var_importance.columns = ['Variable', 'Avg_Importance', 'Value_Count']
var_importance = var_importance[var_importance['Value_Count'] >= 2]  # At least 2 values
var_importance = var_importance.sort_values('Avg_Importance', ascending=False)

top_vars = var_importance.head(12)['Variable'].tolist()

fig, axes = plt.subplots(4, 3, figsize=(22, 20))
axes = axes.flatten()

for idx, var in enumerate(top_vars):
    ax = axes[idx]
    
    var_data = df_values[df_values['Variable'] == var].sort_values('Pct_Long', ascending=False)
    
    if len(var_data) == 0:
        ax.axis('off')
        continue
    
    x = np.arange(len(var_data))
    width = 0.35
    
    # Create bars
    bars1 = ax.bar(x - width/2, var_data['Pct_Short'], width, 
                   label='Short Calls (<4.88)', color='#FF6B6B', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, var_data['Pct_Long'], width,
                   label='Long Calls (>4.88)', color='#4ECDC4', alpha=0.8, edgecolor='black')
    
    # Formatting
    ax.set_xticks(x)
    labels = [str(val)[:20] for val in var_data['Value']]
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Percentage (%)', fontsize=10, fontweight='bold')
    ax.set_title(f'{var}\nShows % of each value in Short vs Long Calls', 
                 fontsize=11, fontweight='bold', pad=10)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        if height > 5:
            ax.text(bar.get_x() + bar.get_width()/2., height/2,
                   f'{height:.0f}%', ha='center', va='center', fontsize=7, fontweight='bold')
    
    for bar in bars2:
        height = bar.get_height()
        if height > 5:
            ax.text(bar.get_x() + bar.get_width()/2., height/2,
                   f'{height:.0f}%', ha='center', va='center', fontsize=7, fontweight='bold')

plt.suptitle('TOP 12 VARIABLES: VALUE-LEVEL BREAKDOWN\n' +
             'Shows which specific values within each variable lead to Short vs Long Calls', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('analysis_outputs/viz_09_value_breakdown_top_variables.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_09_value_breakdown_top_variables.png")
plt.close()

# ==================================================================================
# VIZ 3: KEY QUESTIONS - TIMEZONE, MONTH, SENTIMENT
# ==================================================================================

print("\n" + "="*100)
print("VIZ 3: ANSWERING KEY QUESTIONS")
print("="*100)

key_vars = ['timezone', 'season_month', 'customer_sentiment_omc', 'customer_sentiment_lgs']
key_vars_found = [v for v in key_vars if v in df_values['Variable'].unique()]

if len(key_vars_found) > 0:
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()
    
    for idx, var in enumerate(key_vars_found[:4]):
        ax = axes[idx]
        
        var_data = df_values[df_values['Variable'] == var].sort_values('Pct_Long', ascending=False)
        
        if len(var_data) == 0:
            ax.axis('off')
            continue
        
        # Create stacked bar chart
        x = np.arange(len(var_data))
        
        bars1 = ax.barh(x, var_data['Pct_Short'], color='#FF6B6B', alpha=0.8, 
                       edgecolor='black', linewidth=1.5, label='Short Calls')
        bars2 = ax.barh(x, var_data['Pct_Long'], left=var_data['Pct_Short'], 
                       color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5, 
                       label='Long Calls')
        
        ax.set_yticks(x)
        ax.set_yticklabels([str(val)[:30] for val in var_data['Value']], fontsize=10)
        ax.set_xlabel('Percentage (%)', fontsize=11, fontweight='bold')
        
        # Dynamic title based on variable
        if var == 'timezone':
            title = 'WHICH TIMEZONE LEADS TO LONGER CALLS?'
        elif var == 'season_month':
            title = 'WHICH MONTH HAS HIGHEST % OF LONG CALLS?'
        elif 'sentiment' in var:
            title = f'WHICH {var.upper().replace("_", " ")} LEADS TO LONGER CALLS?'
        else:
            title = f'{var.upper()}: VALUE ANALYSIS'
        
        ax.set_title(title + '\n' + 
                    'RED = Short Calls (<4.88 min) | TEAL = Long Calls (>4.88 min)',
                    fontsize=11, fontweight='bold', pad=10)
        ax.legend(fontsize=9, loc='lower right')
        ax.grid(axis='x', alpha=0.3)
        ax.set_xlim(0, 100)
        ax.invert_yaxis()
        
        # Add percentage labels
        for i, (p_short, p_long) in enumerate(zip(var_data['Pct_Short'], var_data['Pct_Long'])):
            if p_short > 10:
                ax.text(p_short/2, i, f'{p_short:.0f}%', 
                       ha='center', va='center', fontsize=9, fontweight='bold', color='white')
            if p_long > 10:
                ax.text(p_short + p_long/2, i, f'{p_long:.0f}%', 
                       ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # Hide unused subplots
    for idx in range(len(key_vars_found), 4):
        axes[idx].axis('off')
    
    plt.suptitle('ANSWERING KEY QUESTIONS: VALUE-LEVEL ANALYSIS\n' +
                 'Shows which specific values drive longer call durations', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('analysis_outputs/viz_10_key_questions.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: viz_10_key_questions.png")
    plt.close()
else:
    print("[SKIP] Key variables not found in data")

# ==================================================================================
# VIZ 4: VARIABLE IMPORTANCE SUMMARY
# ==================================================================================

print("\n" + "="*100)
print("VIZ 4: VARIABLE IMPORTANCE SUMMARY")
print("="*100)

# Calculate summary stats per variable
var_summary = df_values.groupby('Variable').agg({
    'Importance_Score': ['mean', 'max'],
    'P_Value': lambda x: (x < 0.05).sum(),
    'Total_Count': 'sum'
}).reset_index()

var_summary.columns = ['Variable', 'Avg_Importance', 'Max_Importance', 'Significant_Values', 'Total_Observations']
var_summary = var_summary.sort_values('Avg_Importance', ascending=False).head(20)

fig, ax = plt.subplots(figsize=(14, 10))

bars = ax.barh(range(len(var_summary)), var_summary['Avg_Importance'],
              color='#96CEB4', alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_yticks(range(len(var_summary)))
ax.set_yticklabels(var_summary['Variable'], fontsize=11)
ax.set_xlabel('Average Importance Score Across All Values', fontsize=12, fontweight='bold')
ax.set_title('TOP 20 VARIABLES BY AVERAGE VALUE IMPORTANCE\n' +
             'Shows which variables have the most discriminative values overall\n' +
             'Higher = More impact on call duration across different values', 
             fontsize=14, fontweight='bold', pad=25)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, score, sig_count) in enumerate(zip(bars, var_summary['Avg_Importance'], var_summary['Significant_Values'])):
    ax.text(score + 0.5, i, f'{score:.1f} ({int(sig_count)} sig)', 
            va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('analysis_outputs/viz_11_variable_importance_summary.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_11_variable_importance_summary.png")
plt.close()

print("\n" + "="*100)
print("VALUE-LEVEL VISUALIZATIONS COMPLETE")
print("="*100)
print("\nGenerated Visualizations:")
print("  1. viz_08_top_discriminative_values.png - Top 30 values across all variables")
print("  2. viz_09_value_breakdown_top_variables.png - Detailed breakdown for top 12 variables")
print("  3. viz_10_key_questions.png - Answers to timezone/month/sentiment questions")
print("  4. viz_11_variable_importance_summary.png - Overall variable importance ranking")

