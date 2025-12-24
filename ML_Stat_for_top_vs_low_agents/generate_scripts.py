"""
==============================================================================
AGENT-LEVEL ANALYSIS: SCRIPT GENERATOR
==============================================================================

This script generates all analysis scripts by adapting the original
ML V2 scripts for agent-level analysis.

Generates:
- 02_agent_correlation.py
- 03_agent_feature_importance.py
- 04_agent_statistical_tests.py
- 05_agent_shap.py
- 05b_agent_lime.py
- 06_agent_visualizations.py
- 07_comparison_report.py
==============================================================================
"""

import os
import sys

def generate_correlation_script():
    script = '''"""
==============================================================================
AGENT-LEVEL ANALYSIS: CORRELATION
==============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
import sys
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Get agent type from command line
AGENT_TYPE = sys.argv[2] if len(sys.argv) >= 3 else 'top_agent'
AGENT_NAME = sys.argv[1] if len(sys.argv) >= 2 else 'Unknown'

print("="*100)
print(f"AGENT-LEVEL CORRELATION ANALYSIS: {AGENT_NAME}")
print("="*100)

# Load data
df_short = pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/01_short_calls_original.csv')
df_long = pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/01_long_calls_original.csv')
df_combined = pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/01_combined_original.csv')

print(f"Short calls: {df_short.shape}")
print(f"Long calls: {df_long.shape}")
print(f"Combined: {df_combined.shape}")

# Prepare for correlation
def prepare_for_correlation(df):
    analysis_cols = [c for c in df.columns if c not in ['target', 'call_duration_group']]
    df_corr = df[analysis_cols].copy()
    
    for col in df_corr.columns:
        if df_corr[col].dtype == 'object' or df_corr[col].dtype == 'bool':
            if 'target' in df.columns:
                target_means = df.groupby(col)['target'].mean()
                mapping = {val: rank for rank, val in enumerate(target_means.sort_values().index)}
                df_corr[col] = df[col].map(mapping)
            else:
                df_corr[col] = pd.factorize(df[col])[0]
        
        if df_corr[col].isna().any():
            median_val = df_corr[col].median()
            df_corr[col].fillna(median_val, inplace=True)
    
    return df_corr

print("\\nCalculating correlations...")
df_short_corr = prepare_for_correlation(df_short)
df_long_corr = prepare_for_correlation(df_long)
df_combined_corr = prepare_for_correlation(df_combined)

corr_short = df_short_corr.corr(method='spearman')
corr_long = df_long_corr.corr(method='spearman')
corr_combined = df_combined_corr.corr(method='spearman')

# Correlation with target
target_corr_results = []
for col in df_combined_corr.columns:
    corr, pval = spearmanr(df_combined_corr[col], df_combined['target'], nan_policy='omit')
    target_corr_results.append({
        'Variable': col,
        'Correlation': corr,
        'Abs_Correlation': abs(corr),
        'P_Value': pval,
        'Significant': 'Yes' if pval < 0.05 else 'No',
        'Direction': 'Positive' if corr > 0 else 'Negative',
        'Strength': 'Strong' if abs(corr) > 0.5 else ('Moderate' if abs(corr) > 0.3 else 'Weak')
    })

df_target_corr = pd.DataFrame(target_corr_results).sort_values('Abs_Correlation', ascending=False)

print(f"\\nTOP 20 VARIABLES CORRELATED WITH CALL DURATION FOR {AGENT_NAME}:")
print("-" * 100)
for idx, row in df_target_corr.head(20).iterrows():
    direction = "+" if row['Direction'] == 'Positive' else "-"
    sig = "***" if row['Significant'] == 'Yes' else ""
    print(f"  {row['Variable']}: {direction}{row['Abs_Correlation']:.3f} ({row['Strength']}) {sig}")

# Save results
output_dir = f'analysis_outputs/{AGENT_TYPE}'
corr_short.to_csv(f'{output_dir}/02_correlation_short_calls.csv')
corr_long.to_csv(f'{output_dir}/02_correlation_long_calls.csv')
corr_combined.to_csv(f'{output_dir}/02_correlation_combined.csv')
df_target_corr.to_csv(f'{output_dir}/02_correlation_with_target.csv', index=False)

# Create heatmaps
fig, ax = plt.subplots(figsize=(28, 24))
sns.heatmap(corr_short, annot=True, fmt='.2f', annot_kws={'size': 8}, cmap='RdBu_r',
            vmin=-1, vmax=1, center=0, square=True, linewidths=0.1,
            cbar_kws={'label': 'Spearman Correlation', 'shrink': 0.8}, ax=ax)
ax.set_title(f'AGENT-LEVEL CORRELATION HEATMAP: {AGENT_NAME}\\nSHORT CALLS (<4.88 minutes)\\n' +
             f'Method: SPEARMAN | Variables: {len(corr_short)} | Calls: {len(df_short):,}',
             fontsize=18, fontweight='bold', pad=30)
plt.xticks(rotation=90, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig(f'{output_dir}/heatmap_02_short_calls.png', dpi=300, bbox_inches='tight')
plt.close()

fig, ax = plt.subplots(figsize=(28, 24))
sns.heatmap(corr_long, annot=True, fmt='.2f', annot_kws={'size': 8}, cmap='RdBu_r',
            vmin=-1, vmax=1, center=0, square=True, linewidths=0.1,
            cbar_kws={'label': 'Spearman Correlation', 'shrink': 0.8}, ax=ax)
ax.set_title(f'AGENT-LEVEL CORRELATION HEATMAP: {AGENT_NAME}\\nLONG CALLS (>4.88 minutes)\\n' +
             f'Method: SPEARMAN | Variables: {len(corr_long)} | Calls: {len(df_long):,}',
             fontsize=18, fontweight='bold', pad=30)
plt.xticks(rotation=90, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig(f'{output_dir}/heatmap_02_long_calls.png', dpi=300, bbox_inches='tight')
plt.close()

print("\\n[OK] Correlation analysis complete")
print(f"[OK] Saved heatmaps and correlation data to {output_dir}")
'''
    
    with open('02_agent_correlation.py', 'w') as f:
        f.write(script)
    print("[OK] Generated: 02_agent_correlation.py")

def generate_feature_importance_script():
    # Copy and adapt the feature importance script
    with open('../ML V2/03_variable_level_feature_importance.py', 'r', encoding='utf-8') as f:
        original = f.read()
    
    # Replace paths and output
    adapted = original.replace(
        "pd.read_csv('analysis_outputs/level1_variable/01_combined_original.csv')",
        "pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/01_combined_original.csv')"
    ).replace(
        "pd.read_csv('analysis_outputs/level1_variable/02_correlation_with_target.csv')",
        "pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/02_correlation_with_target.csv')"
    ).replace(
        "'analysis_outputs/level1_variable/",
        "f'analysis_outputs/{AGENT_TYPE}/"
    ).replace(
        "print(\"=\"*100)\nprint(\"LEVEL 1: VARIABLE-LEVEL FEATURE IMPORTANCE\")\nprint(\"=\"*100)",
        "import sys\n\nAGENT_TYPE = sys.argv[2] if len(sys.argv) >= 3 else 'top_agent'\nAGENT_NAME = sys.argv[1] if len(sys.argv) >= 2 else 'Unknown'\n\nprint(\"=\"*100)\nprint(f\"AGENT-LEVEL FEATURE IMPORTANCE: {AGENT_NAME}\")\nprint(\"=\"*100)"
    )
    
    with open('03_agent_feature_importance.py', 'w', encoding='utf-8') as f:
        f.write(adapted)
    print("[OK] Generated: 03_agent_feature_importance.py")

def generate_statistical_tests_script():
    # Copy and adapt statistical tests
    with open('../ML V2/04_variable_level_statistical_tests.py', 'r', encoding='utf-8') as f:
        original = f.read()
    
    adapted = original.replace(
        "pd.read_csv('analysis_outputs/level1_variable/",
        "pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/"
    ).replace(
        "'analysis_outputs/level1_variable/",
        "f'analysis_outputs/{AGENT_TYPE}/"
    ).replace(
        "print(\"=\"*100)\nprint(\"LEVEL 1: VARIABLE-LEVEL STATISTICAL TESTS\")\nprint(\"=\"*100)",
        "import sys\n\nAGENT_TYPE = sys.argv[2] if len(sys.argv) >= 3 else 'top_agent'\nAGENT_NAME = sys.argv[1] if len(sys.argv) >= 2 else 'Unknown'\n\nprint(\"=\"*100)\nprint(f\"AGENT-LEVEL STATISTICAL TESTS: {AGENT_NAME}\")\nprint(\"=\"*100)"
    )
    
    with open('04_agent_statistical_tests.py', 'w', encoding='utf-8') as f:
        f.write(adapted)
    print("[OK] Generated: 04_agent_statistical_tests.py")

def generate_shap_script():
    # Copy and adapt SHAP analysis
    with open('../ML V2/05_variable_level_shap.py', 'r', encoding='utf-8') as f:
        original = f.read()
    
    adapted = original.replace(
        "joblib.load('analysis_outputs/level1_variable/",
        "joblib.load(f'analysis_outputs/{AGENT_TYPE}/"
    ).replace(
        "pd.read_csv('analysis_outputs/level1_variable/",
        "pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/"
    ).replace(
        "'analysis_outputs/level1_variable/",
        "f'analysis_outputs/{AGENT_TYPE}/"
    ).replace(
        "print(\"=\"*100)\nprint(\"LEVEL 1: VARIABLE-LEVEL SHAP ANALYSIS\")\nprint(\"=\"*100)",
        "import sys\n\nAGENT_TYPE = sys.argv[2] if len(sys.argv) >= 3 else 'top_agent'\nAGENT_NAME = sys.argv[1] if len(sys.argv) >= 2 else 'Unknown'\n\nprint(\"=\"*100)\nprint(f\"AGENT-LEVEL SHAP ANALYSIS: {AGENT_NAME}\")\nprint(\"=\"*100)"
    )
    
    with open('05_agent_shap.py', 'w', encoding='utf-8') as f:
        f.write(adapted)
    print("[OK] Generated: 05_agent_shap.py")

def generate_lime_script():
    # Copy and adapt LIME analysis
    with open('../ML V2/05b_variable_level_lime.py', 'r', encoding='utf-8') as f:
        original = f.read()
    
    adapted = original.replace(
        "joblib.load('analysis_outputs/level1_variable/",
        "joblib.load(f'analysis_outputs/{AGENT_TYPE}/"
    ).replace(
        "pd.read_csv('analysis_outputs/level1_variable/",
        "pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/"
    ).replace(
        "'analysis_outputs/level1_variable/",
        "f'analysis_outputs/{AGENT_TYPE}/"
    ).replace(
        "print(\"=\"*100)\nprint(\"LEVEL 1: VARIABLE-LEVEL LIME ANALYSIS\")\nprint(\"=\"*100)",
        "import sys\n\nAGENT_TYPE = sys.argv[2] if len(sys.argv) >= 3 else 'top_agent'\nAGENT_NAME = sys.argv[1] if len(sys.argv) >= 2 else 'Unknown'\n\nprint(\"=\"*100)\nprint(f\"AGENT-LEVEL LIME ANALYSIS: {AGENT_NAME}\")\nprint(\"=\"*100)"
    )
    
    with open('05b_agent_lime.py', 'w', encoding='utf-8') as f:
        f.write(adapted)
    print("[OK] Generated: 05b_agent_lime.py")

def generate_visualizations_script():
    # Copy and adapt visualizations
    with open('../ML V2/06_variable_level_visualizations.py', 'r', encoding='utf-8') as f:
        original = f.read()
    
    adapted = original.replace(
        "pd.read_csv('analysis_outputs/level1_variable/",
        "pd.read_csv(f'analysis_outputs/{AGENT_TYPE}/"
    ).replace(
        "'analysis_outputs/level1_variable/",
        "f'analysis_outputs/{AGENT_TYPE}/"
    ).replace(
        "with open('analysis_outputs/level1_variable/01_metadata.json', 'r') as f:",
        "with open(f'analysis_outputs/{AGENT_TYPE}/01_metadata.json', 'r') as f:"
    ).replace(
        "print(\"=\"*100)\nprint(\"LEVEL 1: VARIABLE-LEVEL VISUALIZATIONS\")\nprint(\"=\"*100)",
        "import sys\n\nAGENT_TYPE = sys.argv[2] if len(sys.argv) >= 3 else 'top_agent'\nAGENT_NAME = sys.argv[1] if len(sys.argv) >= 2 else 'Unknown'\n\nprint(\"=\"*100)\nprint(f\"AGENT-LEVEL VISUALIZATIONS: {AGENT_NAME}\")\nprint(\"=\"*100)"
    )
    
    with open('06_agent_visualizations.py', 'w', encoding='utf-8') as f:
        f.write(adapted)
    print("[OK] Generated: 06_agent_visualizations.py")

def generate_comparison_report():
    script = '''"""
==============================================================================
AGENT COMPARISON REPORT
==============================================================================
"""

import pandas as pd
import json
from datetime import datetime

print("="*100)
print("GENERATING AGENT COMPARISON REPORT")
print("="*100)

# Load metadata for both agents
with open('analysis_outputs/top_agent/01_metadata.json', 'r') as f:
    top_meta = json.load(f)

with open('analysis_outputs/worst_agent/01_metadata.json', 'r') as f:
    worst_meta = json.load(f)

# Load importance data
top_imp = pd.read_csv('analysis_outputs/top_agent/03_importance_combined.csv')
worst_imp = pd.read_csv('analysis_outputs/worst_agent/03_importance_combined.csv')

# Load correlation data
top_corr = pd.read_csv('analysis_outputs/top_agent/02_correlation_with_target.csv')
worst_corr = pd.read_csv('analysis_outputs/worst_agent/02_correlation_with_target.csv')

# Generate report
report = []
report.append("="*100)
report.append("AGENT COMPARISON REPORT: TOP VS WORST PERFORMER")
report.append("="*100)
report.append(f"\\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

report.append(f"\\nTOP AGENT: {top_meta['agent_name']}")
report.append(f"  Total Calls: {top_meta['total_records']}")
report.append(f"  Short Calls: {top_meta['short_calls']} ({top_meta['short_calls']/top_meta['total_records']*100:.1f}%)")
report.append(f"  Long Calls: {top_meta['long_calls']} ({top_meta['long_calls']/top_meta['total_records']*100:.1f}%)")

report.append(f"\\nWORST AGENT: {worst_meta['agent_name']}")
report.append(f"  Total Calls: {worst_meta['total_records']}")
report.append(f"  Short Calls: {worst_meta['short_calls']} ({worst_meta['short_calls']/worst_meta['total_records']*100:.1f}%)")
report.append(f"  Long Calls: {worst_meta['long_calls']} ({worst_meta['long_calls']/worst_meta['total_records']*100:.1f}%)")

report.append("\\n" + "="*100)
report.append("TOP 10 MOST IMPORTANT VARIABLES - TOP AGENT")
report.append("="*100)
for idx, row in top_imp.head(10).iterrows():
    report.append(f"  {idx+1}. {row['Variable']}: {row['Combined_Score']:.4f}")

report.append("\\n" + "="*100)
report.append("TOP 10 MOST IMPORTANT VARIABLES - WORST AGENT")
report.append("="*100)
for idx, row in worst_imp.head(10).iterrows():
    report.append(f"  {idx+1}. {row['Variable']}: {row['Combined_Score']:.4f}")

# Save report
with open('analysis_outputs/AGENT_COMPARISON_REPORT.txt', 'w') as f:
    f.write("\\n".join(report))

print("\\n[OK] Comparison report saved to analysis_outputs/AGENT_COMPARISON_REPORT.txt")
'''
    
    with open('07_comparison_report.py', 'w') as f:
        f.write(script)
    print("[OK] Generated: 07_comparison_report.py")

if __name__ == '__main__':
    print("="*100)
    print("GENERATING AGENT-LEVEL ANALYSIS SCRIPTS")
    print("="*100)
    
    generate_correlation_script()
    generate_feature_importance_script()
    generate_statistical_tests_script()
    generate_shap_script()
    generate_lime_script()
    generate_visualizations_script()
    generate_comparison_report()
    
    print("\\n[SUCCESS] All scripts generated!")
    print("\\nRun: python RUN_AGENT_COMPARISON_ANALYSIS.py")

