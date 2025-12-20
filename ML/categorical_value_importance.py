"""
2ND LEVEL ANALYSIS - CATEGORICAL VALUE IMPORTANCE
Analyzing which specific categories within important categorical variables matter most
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("2ND LEVEL ANALYSIS - CATEGORICAL VALUE IMPORTANCE")
print("="*100)

# Load data
df_short = pd.read_csv('analysis_outputs/enhanced_short_calls_data.csv')
df_long = pd.read_csv('analysis_outputs/enhanced_long_calls_data.csv')
df_combined = pd.read_csv('analysis_outputs/enhanced_combined_data.csv')

# Load categorical variable results to get top variables
df_cat_results = pd.read_csv('analysis_outputs/enhanced_categorical_variables_tests.csv')

# Get top 20 most significant categorical variables
top_categorical = df_cat_results.nsmallest(20, 'P_Value')['Variable'].tolist()

print(f"\nAnalyzing {len(top_categorical)} most significant categorical variables")
print("-" * 100)

# ==================================================================================
# ANALYZE EACH CATEGORICAL VARIABLE'S VALUES
# ==================================================================================

category_importance_results = []

for var in top_categorical:
    print(f"\nAnalyzing: {var}")
    
    if var not in df_combined.columns:
        continue
    
    # Create contingency table
    try:
        ct = pd.crosstab(df_combined[var].fillna('Missing'), 
                        df_combined['call_duration_group'],
                        margins=True)
        
        # Get value counts
        value_counts_short = df_short[var].value_counts()
        value_counts_long = df_long[var].value_counts()
        
        # For each category value
        unique_values = df_combined[var].unique()
        
        for value in unique_values:
            if pd.isna(value):
                value_str = 'Missing'
            else:
                value_str = str(value)
            
            # Count in short and long
            count_short = (df_short[var] == value).sum() if not pd.isna(value) else df_short[var].isna().sum()
            count_long = (df_long[var] == value).sum() if not pd.isna(value) else df_long[var].isna().sum()
            
            total_count = count_short + count_long
            
            if total_count > 0:
                pct_short = (count_short / total_count) * 100
                pct_long = (count_long / total_count) * 100
                
                # Calculate "importance" as deviation from 50/50
                importance_score = abs(pct_long - 50)  # How much does this value favor long calls?
                
                # Direction
                if pct_long > pct_short:
                    direction = 'Favors Long Calls'
                elif pct_short > pct_long:
                    direction = 'Favors Short Calls'
                else:
                    direction = 'Neutral'
                
                category_importance_results.append({
                    'Variable': var,
                    'Category_Value': value_str,
                    'Count_Short': count_short,
                    'Count_Long': count_long,
                    'Total_Count': total_count,
                    'Pct_Short': pct_short,
                    'Pct_Long': pct_long,
                    'Importance_Score': importance_score,
                    'Direction': direction
                })
    
    except Exception as e:
        print(f"  Error analyzing {var}: {e}")
        continue

# Create DataFrame
df_category_importance = pd.DataFrame(category_importance_results)

# Sort by importance score
df_category_importance = df_category_importance.sort_values('Importance_Score', ascending=False)

# Save results
df_category_importance.to_csv('analysis_outputs/categorical_value_importance.csv', index=False)

print("\n" + "="*100)
print("TOP 30 MOST IMPORTANT CATEGORICAL VALUES")
print("="*100)

display_cols = ['Variable', 'Category_Value', 'Count_Short', 'Count_Long', 'Pct_Long', 'Direction']
print(df_category_importance[display_cols].head(30).to_string(index=False))

# ==================================================================================
# CREATE VISUALIZATIONS FOR TOP VARIABLES
# ==================================================================================
print("\n" + "="*100)
print("CREATING CATEGORICAL VALUE VISUALIZATIONS")
print("="*100)

# Get top 6 variables
top_6_vars = top_categorical[:6]

fig, axes = plt.subplots(3, 2, figsize=(16, 18))
axes = axes.flatten()

for idx, var in enumerate(top_6_vars):
    ax = axes[idx]
    
    if var not in df_combined.columns:
        continue
    
    # Get value counts for each group
    value_counts_short = df_short[var].value_counts().head(10)
    value_counts_long = df_long[var].value_counts().head(10)
    
    # Combine and get top 10 overall
    all_values = set(value_counts_short.index) | set(value_counts_long.index)
    top_values = list(all_values)[:10]
    
    # Create data for plotting
    short_counts = [value_counts_short.get(v, 0) for v in top_values]
    long_counts = [value_counts_long.get(v, 0) for v in top_values]
    
    x = np.arange(len(top_values))
    width = 0.35
    
    bars1 = ax.barh(x - width/2, short_counts, width, label='Short Calls', 
                   color='#FF6B6B', alpha=0.8, edgecolor='black')
    bars2 = ax.barh(x + width/2, long_counts, width, label='Long Calls', 
                   color='#4ECDC4', alpha=0.8, edgecolor='black')
    
    ax.set_yticks(x)
    ax.set_yticklabels([str(v)[:30] for v in top_values], fontsize=9)
    ax.set_xlabel('Count', fontsize=10, fontweight='bold')
    ax.set_title(f'{var}\n(Top 10 Values)', fontsize=11, fontweight='bold', pad=10)
    ax.legend(fontsize=9)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

plt.suptitle('Categorical Variable Value Distribution: Short vs Long Calls', 
            fontsize=15, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('analysis_outputs/cat_viz_01_value_distributions.png', dpi=300, bbox_inches='tight')
print("\n[OK] Saved: cat_viz_01_value_distributions.png")
plt.close()

print("\n" + "="*100)
print("CATEGORICAL VALUE IMPORTANCE ANALYSIS COMPLETE")
print("="*100)
print(f"\n[OK] Saved: categorical_value_importance.csv")
print(f"Total category values analyzed: {len(df_category_importance)}")

