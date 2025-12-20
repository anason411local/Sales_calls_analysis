"""
SEPARATE DATASET ANALYSIS
Internal analysis for Short and Long calls datasets independently
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("SEPARATE DATASET ANALYSIS - INTERNAL PATTERNS")
print("="*100)

# Load data
df_short = pd.read_csv('analysis_outputs/enhanced_short_calls_data.csv')
df_long = pd.read_csv('analysis_outputs/enhanced_long_calls_data.csv')

def analyze_dataset(df, name):
    """Perform internal analysis on a single dataset"""
    
    print(f"\n{'='*100}")
    print(f"ANALYZING: {name}")
    print(f"{'='*100}")
    
    results = {
        'dataset_name': name,
        'total_records': len(df),
        'numeric_variables': len(df.select_dtypes(include=[np.number]).columns),
        'categorical_variables': len(df.select_dtypes(include=['object', 'bool']).columns)
    }
    
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'call_duration_group' in numeric_cols:
        numeric_cols.remove('call_duration_group')
    
    print(f"\n1. BASIC STATISTICS")
    print(f"   - Total Records: {results['total_records']}")
    print(f"   - Numeric Variables: {results['numeric_variables']}")
    print(f"   - Categorical Variables: {results['categorical_variables']}")
    
    # ==================================================================================
    # DESCRIPTIVE STATISTICS
    # ==================================================================================
    print(f"\n2. DESCRIPTIVE STATISTICS FOR KEY VARIABLES")
    
    key_vars = ['TO_OMC_Duration', 'total_call_duration', 'total_discovery_questions', 
                'total_buying_signals', 'total_objections', 'time_in_final_stage']
    
    descriptive_stats = []
    for var in key_vars:
        if var in df.columns:
            stats_dict = {
                'Variable': var,
                'Mean': df[var].mean(),
                'Median': df[var].median(),
                'Std': df[var].std(),
                'Min': df[var].min(),
                'Q25': df[var].quantile(0.25),
                'Q75': df[var].quantile(0.75),
                'Max': df[var].max(),
                'Missing': df[var].isnull().sum(),
                'Missing_Pct': (df[var].isnull().sum() / len(df)) * 100
            }
            descriptive_stats.append(stats_dict)
    
    df_desc = pd.DataFrame(descriptive_stats)
    print(df_desc.to_string(index=False))
    
    # Save descriptive stats
    df_desc.to_csv(f'analysis_outputs/descriptive_stats_{name.lower().replace(" ", "_")}.csv', index=False)
    
    # ==================================================================================
    # CORRELATION WITH TO_OMC_DURATION
    # ==================================================================================
    print(f"\n3. TOP 20 CORRELATIONS WITH TO_OMC_DURATION")
    
    if 'TO_OMC_Duration' in df.columns:
        correlations = []
        for col in numeric_cols:
            if col != 'TO_OMC_Duration':
                valid_data = df[[col, 'TO_OMC_Duration']].dropna()
                if len(valid_data) > 10:
                    corr, p_value = stats.pearsonr(valid_data[col], valid_data['TO_OMC_Duration'])
                    correlations.append({
                        'Variable': col,
                        'Correlation': corr,
                        'Abs_Correlation': abs(corr),
                        'P_Value': p_value,
                        'Significant': 'Yes' if p_value < 0.05 else 'No'
                    })
        
        df_corr = pd.DataFrame(correlations).sort_values('Abs_Correlation', ascending=False)
        print(df_corr.head(20)[['Variable', 'Correlation', 'P_Value', 'Significant']].to_string(index=False))
        
        # Save correlations
        df_corr.to_csv(f'analysis_outputs/internal_correlations_{name.lower().replace(" ", "_")}.csv', index=False)
        results['significant_correlations'] = (df_corr['P_Value'] < 0.05).sum()
    
    # ==================================================================================
    # CATEGORICAL VARIABLE DISTRIBUTIONS
    # ==================================================================================
    print(f"\n4. TOP CATEGORICAL VARIABLE DISTRIBUTIONS")
    
    categorical_cols = df.select_dtypes(include=['object', 'bool']).columns.tolist()
    if 'call_duration_group' in categorical_cols:
        categorical_cols.remove('call_duration_group')
    
    cat_distributions = []
    for col in categorical_cols[:10]:  # Top 10 categorical
        value_counts = df[col].value_counts()
        cat_distributions.append({
            'Variable': col,
            'Unique_Values': df[col].nunique(),
            'Most_Common': value_counts.index[0] if len(value_counts) > 0 else 'N/A',
            'Most_Common_Count': value_counts.iloc[0] if len(value_counts) > 0 else 0,
            'Most_Common_Pct': (value_counts.iloc[0] / len(df)) * 100 if len(value_counts) > 0 else 0
        })
    
    df_cat_dist = pd.DataFrame(cat_distributions)
    print(df_cat_dist.to_string(index=False))
    
    # Save categorical distributions
    df_cat_dist.to_csv(f'analysis_outputs/categorical_distributions_{name.lower().replace(" ", "_")}.csv', index=False)
    
    # ==================================================================================
    # VARIANCE ANALYSIS
    # ==================================================================================
    print(f"\n5. VARIANCE ANALYSIS - HIGH VS LOW VARIABILITY")
    
    variance_data = []
    for col in numeric_cols[:20]:  # Top 20 numeric
        if df[col].std() > 0:
            cv = (df[col].std() / df[col].mean()) * 100 if df[col].mean() != 0 else 0
            variance_data.append({
                'Variable': col,
                'Std_Dev': df[col].std(),
                'Mean': df[col].mean(),
                'Coefficient_of_Variation': cv,
                'Variability': 'High' if cv > 50 else ('Medium' if cv > 20 else 'Low')
            })
    
    df_variance = pd.DataFrame(variance_data).sort_values('Coefficient_of_Variation', ascending=False)
    print(df_variance.head(15).to_string(index=False))
    
    # Save variance analysis
    df_variance.to_csv(f'analysis_outputs/variance_analysis_{name.lower().replace(" ", "_")}.csv', index=False)
    
    return results

# ==================================================================================
# ANALYZE BOTH DATASETS
# ==================================================================================
results_short = analyze_dataset(df_short, "SHORT CALLS")
results_long = analyze_dataset(df_long, "LONG CALLS")

# ==================================================================================
# COMPARISON SUMMARY
# ==================================================================================
print(f"\n{'='*100}")
print(f"COMPARISON SUMMARY")
print(f"{'='*100}")

comparison = pd.DataFrame([results_short, results_long])
print(comparison.to_string(index=False))

comparison.to_csv('analysis_outputs/separate_dataset_analysis_summary.csv', index=False)

print(f"\n{'='*100}")
print(f"SEPARATE DATASET ANALYSIS COMPLETE")
print(f"{'='*100}")

