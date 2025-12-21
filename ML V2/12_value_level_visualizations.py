"""
==============================================================================
LEVEL 2: VALUE-LEVEL VISUALIZATIONS
==============================================================================

Purpose: Visualize which specific values matter most
- Top discriminative values
- Variable-specific value breakdowns
- Answers to key questions (timezone/month/sentiment)

==============================================================================
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
print("LEVEL 2: VALUE-LEVEL VISUALIZATIONS")
print("="*100)

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("\nLoading data...")
df_values = pd.read_csv('analysis_outputs/level2_value/07_categorical_value_analysis.csv')
df_importance = pd.read_csv('analysis_outputs/level2_value/09_importance_combined_values.csv')

print(f"Values: {len(df_values)}")
print(f"Value features: {len(df_importance)}")

# ==============================================================================
# VIZ 1: TOP 30 DISCRIMINATIVE VALUES
# ==============================================================================

print("\n" + "="*100)
print("VIZ 1: TOP 30 DISCRIMINATIVE VALUES")
print("="*100)

fig, ax = plt.subplots(figsize=(14, 12))

top_30 = df_values.head(30)

colors = ['#4ECDC4' if d == 'Favors Long Calls' else '#FF6B6B' for d in top_30['Direction']]

bars = ax.barh(range(len(top_30)), top_30['Importance_Score'],
              color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_yticks(range(len(top_30)))
labels = [f"{row['Variable']}: {str(row['Value'])[:30]}" for _, row in top_30.iterrows()]
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel('Importance Score (% Deviation from 50-50)', fontsize=13, fontweight='bold')
ax.set_title('LEVEL 2: TOP 30 MOST DISCRIMINATIVE VALUES\n' +
             'TEAL = Associated with LONG Calls | RED = Associated with SHORT Calls\n' +
             'Shows which SPECIFIC VALUES (not just variables) drive call duration',
             fontsize=13, fontweight='bold', pad=25)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

for i, (bar, row) in enumerate(zip(bars, top_30.iterrows())):
    row = row[1]
    pct = row['Pct_Long'] if row['Direction'] == 'Favors Long Calls' else row['Pct_Short']
    ax.text(row['Importance_Score'] + 1, i, f"{pct:.0f}%",
            va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('analysis_outputs/level2_value/viz_12_top_discriminative_values.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_12_top_discriminative_values.png")
plt.close()

# ==============================================================================
# VIZ 2: KEY QUESTIONS (TIMEZONE, MONTH, SENTIMENT)
# ==============================================================================

print("\nVIZ 2: KEY QUESTIONS")

key_vars = ['timezone', 'season_month', 'customer_sentiment_omc']
key_vars_found = [v for v in key_vars if v in df_values['Variable'].unique()]

if len(key_vars_found) > 0:
    fig, axes = plt.subplots(len(key_vars_found), 1, figsize=(14, 5*len(key_vars_found)))
    
    if len(key_vars_found) == 1:
        axes = [axes]
    
    for idx, var in enumerate(key_vars_found):
        ax = axes[idx]
        
        var_data = df_values[df_values['Variable'] == var].sort_values('Pct_Long', ascending=False)
        
        x = np.arange(len(var_data))
        
        bars1 = ax.barh(x, var_data['Pct_Short'], color='#FF6B6B', alpha=0.8,
                       edgecolor='black', linewidth=1.5, label='Short Calls')
        bars2 = ax.barh(x, var_data['Pct_Long'], left=var_data['Pct_Short'],
                       color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5,
                       label='Long Calls')
        
        ax.set_yticks(x)
        ax.set_yticklabels([str(v)[:30] for v in var_data['Value']], fontsize=10)
        ax.set_xlabel('Percentage (%)', fontsize=11, fontweight='bold')
        
        if var == 'timezone':
            title = 'WHICH TIMEZONE LEADS TO LONGER CALLS?'
        elif var == 'season_month':
            title = 'WHICH MONTH HAS HIGHEST % OF LONG CALLS?'
        else:
            title = f'WHICH {var.upper().replace("_", " ")} LEADS TO LONGER CALLS?'
        
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.legend(fontsize=9)
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
    
    plt.suptitle('LEVEL 2: ANSWERING KEY QUESTIONS - VALUE-LEVEL ANALYSIS\n' +
                 'Shows which specific values drive longer calls',
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('analysis_outputs/level2_value/viz_12_key_questions_values.png',
                dpi=300, bbox_inches='tight')
    print("[OK] Saved: viz_12_key_questions_values.png")
    plt.close()

# ==============================================================================
# VIZ 3: TOP VARIABLES BY VALUE DISCRIMINATION
# ==============================================================================

print("\nVIZ 3: VARIABLE SUMMARY")

var_summary = df_values.groupby('Variable').agg({
    'Importance_Score': ['mean', 'max'],
    'Significant': lambda x: (x == 'Yes').sum(),
    'Total_Count': 'sum'
}).reset_index()

var_summary.columns = ['Variable', 'Avg_Importance', 'Max_Importance', 'Sig_Values', 'Total_Obs']
var_summary = var_summary.sort_values('Avg_Importance', ascending=False).head(20)

fig, ax = plt.subplots(figsize=(12, 8))

bars = ax.barh(range(len(var_summary)), var_summary['Avg_Importance'],
              color='#96CEB4', alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_yticks(range(len(var_summary)))
ax.set_yticklabels(var_summary['Variable'], fontsize=10)
ax.set_xlabel('Average Value Importance Score', fontsize=12, fontweight='bold')
ax.set_title('LEVEL 2: TOP 20 VARIABLES BY VALUE DISCRIMINATION\n' +
             'Shows which variables have the most discriminative specific values\n' +
             'Higher = More variation in outcomes across different values',
             fontsize=13, fontweight='bold', pad=20)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

for i, (bar, score, sig) in enumerate(zip(bars, var_summary['Avg_Importance'], var_summary['Sig_Values'])):
    ax.text(score + 0.5, i, f'{score:.1f} ({int(sig)} sig)',
            va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('analysis_outputs/level2_value/viz_12_variable_value_summary.png',
            dpi=300, bbox_inches='tight')
print("[OK] Saved: viz_12_variable_value_summary.png")
plt.close()

print("\n" + "="*100)
print("LEVEL 2 VISUALIZATIONS COMPLETE")
print("="*100)
print("\n[OK] Created 3 comprehensive visualizations")
print("   1. Top 30 discriminative values")
print("   2. Key questions (timezone/month/sentiment)")
print("   3. Variable-level value summary")

