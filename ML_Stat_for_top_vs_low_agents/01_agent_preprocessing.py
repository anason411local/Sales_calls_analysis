"""
==============================================================================
AGENT-LEVEL ANALYSIS: PREPROCESSING
==============================================================================

Purpose: Filter and prepare data for a specific agent
- Load short and long call datasets
- Filter for specified agent (TO_OMC_User column)
- Keep all 47 variables for analysis
- Create binary target (Short vs Long calls)
- Save agent-specific datasets

==============================================================================
"""

import pandas as pd
import numpy as np
import sys
import json
import warnings
warnings.filterwarnings('ignore')

# Get agent name and type from command line
if len(sys.argv) >= 3:
    AGENT_NAME = sys.argv[1]
    AGENT_TYPE = sys.argv[2]  # 'top_agent' or 'worst_agent'
else:
    print("[ERROR] Usage: python 01_agent_preprocessing.py <AGENT_NAME> <AGENT_TYPE>")
    sys.exit(1)

print("="*100)
print(f"AGENT-LEVEL PREPROCESSING: {AGENT_NAME} ({AGENT_TYPE.upper()})")
print("="*100)

# ==============================================================================
# DEFINE 47 VARIABLES (EXCLUDING TO_OMC_User and TO_OMC_Duration)
# ==============================================================================

VARIABLE_SECTIONS = {
    'lead_quality': [
        'LQ_Company_Name', 'LQ_Company_Address', 'LQ_Service', 'LQ_Customer_Name',
        'Calls Count', 'Connection Made Calls'
    ],
    'timings': [
        'TO_Event_O', 'timezone', 'season_status'
    ],
    'lgs_department': [
        'TO_User_M', 'lgs_sentiment_style', 'lgs_agent_gender', 'TO_length_in_sec',
        'is_decision_maker', 'ready_for_customers', 'forbidden_industry', 'ready_to_transfer'
    ],
    'customer': [
        'customer_sentiment_lgs', 'customer_sentiment_omc', 'customer_language',
        'customer_knows_marketing', 'customer_availability', 'who_said_hello_first_lgs',
        'customer_marketing_experience'
    ],
    'technical_quality': [
        'technical_quality_score', 'technical_quality_issues'
    ],
    'omc_department': [
        # Excluding TO_OMC_User (agent identifier) and TO_OMC_Duration (perfect separator)
        'TO_OMC_Disposiion', 'omc_agent_sentiment_style', 'omc_who_said_hello_first'
    ],
    'omc_engagement': [
        'customer_talk_percentage', 'total_discovery_questions', 'total_buying_signals'
    ],
    'omc_opening': [
        'time_to_reason_seconds', 'location_mentioned', 'business_type_mentioned',
        'within_45_seconds', 'call_structure_framed'
    ],
    'omc_objections': [
        'total_objections', 'objections_acknowledged', 'price_mentions_final_2min',
        'timeline_mentions_final_2min', 'contract_mentions_final_2min', 'objections_rebutted'
    ],
    'omc_pace': [
        'total_interruptions'
    ],
    'omc_outcome': [
        'commitment_type', 'call_result_tag'
    ]
}

# Flatten to get all variables
ALL_VARIABLES = []
for section_vars in VARIABLE_SECTIONS.values():
    ALL_VARIABLES.extend(section_vars)

print(f"\nDefined {len(ALL_VARIABLES)} variables across {len(VARIABLE_SECTIONS)} sections")
print(f"(Excluding TO_OMC_User as it's the agent identifier)")

# ==============================================================================
# LOAD RAW DATA
# ==============================================================================

print("\n" + "="*100)
print("LOADING RAW DATA")
print("="*100)

df_short = pd.read_csv('../ML/Less_than_4.88_mnt..csv')
df_long = pd.read_csv('../ML/greater_than_4.88_mnt..csv')

print(f"\nShort calls (<4.88 min): {df_short.shape[0]} rows, {df_short.shape[1]} columns")
print(f"Long calls (>4.88 min): {df_long.shape[0]} rows, {df_long.shape[1]} columns")

# ==============================================================================
# FILTER FOR SPECIFIC AGENT
# ==============================================================================

print("\n" + "="*100)
print(f"FILTERING FOR AGENT: {AGENT_NAME}")
print("="*100)

# Check if TO_OMC_User column exists
if 'TO_OMC_User' not in df_short.columns or 'TO_OMC_User' not in df_long.columns:
    print("[ERROR] TO_OMC_User column not found in datasets")
    sys.exit(1)

# Filter for the specific agent
df_short_agent = df_short[df_short['TO_OMC_User'] == AGENT_NAME].copy()
df_long_agent = df_long[df_long['TO_OMC_User'] == AGENT_NAME].copy()

print(f"\nAgent: {AGENT_NAME}")
print(f"  Short calls: {len(df_short_agent)} ({len(df_short_agent)/len(df_short)*100:.2f}% of all short calls)")
print(f"  Long calls: {len(df_long_agent)} ({len(df_long_agent)/len(df_long)*100:.2f}% of all long calls)")
print(f"  Total calls for this agent: {len(df_short_agent) + len(df_long_agent)}")

if len(df_short_agent) == 0 and len(df_long_agent) == 0:
    print(f"\n[ERROR] No calls found for agent: {AGENT_NAME}")
    print(f"Available agents in dataset: {sorted(pd.concat([df_short['TO_OMC_User'], df_long['TO_OMC_User']]).unique()[:20])}")
    sys.exit(1)

if len(df_short_agent) < 10 or len(df_long_agent) < 10:
    print(f"\n[WARNING] Very few calls for this agent. Results may not be statistically significant.")

# ==============================================================================
# FILTER TO SPECIFIED VARIABLES
# ==============================================================================

print("\n" + "="*100)
print("FILTERING TO SPECIFIED VARIABLES")
print("="*100)

# Check which variables are available
available_in_short = [v for v in ALL_VARIABLES if v in df_short_agent.columns]
available_in_long = [v for v in ALL_VARIABLES if v in df_long_agent.columns]

missing = set(ALL_VARIABLES) - set(available_in_short)
if missing:
    print(f"\n[WARNING] Missing variables in dataset: {missing}")

print(f"\nAvailable variables: {len(available_in_short)}/{len(ALL_VARIABLES)}")

# Filter to available variables
df_short_filtered = df_short_agent[available_in_short].copy()
df_long_filtered = df_long_agent[available_in_long].copy()

print(f"Short calls filtered: {df_short_filtered.shape}")
print(f"Long calls filtered: {df_long_filtered.shape}")

# ==============================================================================
# CREATE BINARY TARGET
# ==============================================================================

print("\n" + "="*100)
print("CREATING BINARY TARGET")
print("="*100)

df_short_filtered['target'] = 0  # Short calls
df_long_filtered['target'] = 1  # Long calls

df_short_filtered['call_duration_group'] = 'Short (<4.88 min)'
df_long_filtered['call_duration_group'] = 'Long (>4.88 min)'

# Combine datasets
df_combined = pd.concat([df_short_filtered, df_long_filtered], ignore_index=True)

print(f"\nCombined dataset for {AGENT_NAME}: {df_combined.shape}")
print(f"  Short calls: {(df_combined['target'] == 0).sum()} ({(df_combined['target'] == 0).sum() / len(df_combined) * 100:.1f}%)")
print(f"  Long calls: {(df_combined['target'] == 1).sum()} ({(df_combined['target'] == 1).sum() / len(df_combined) * 100:.1f}%)")

# ==============================================================================
# IDENTIFY VARIABLE TYPES
# ==============================================================================

print("\n" + "="*100)
print("IDENTIFYING VARIABLE TYPES")
print("="*100)

categorical_vars = []
numerical_vars = []

for col in available_in_short:
    if df_combined[col].dtype in ['object', 'bool'] or df_combined[col].nunique() < 50:
        categorical_vars.append(col)
    else:
        numerical_vars.append(col)

print(f"\nCategorical variables: {len(categorical_vars)}")
print(f"Numerical variables: {len(numerical_vars)}")

# ==============================================================================
# DATA QUALITY CHECKS
# ==============================================================================

print("\n" + "="*100)
print("DATA QUALITY CHECKS")
print("="*100)

# Missing values
missing_summary = []
for col in available_in_short:
    missing_count = df_combined[col].isna().sum()
    missing_pct = missing_count / len(df_combined) * 100
    if missing_count > 0:
        missing_summary.append({
            'Variable': col,
            'Missing_Count': missing_count,
            'Missing_Pct': missing_pct
        })

df_missing = pd.DataFrame(missing_summary).sort_values('Missing_Pct', ascending=False) if missing_summary else pd.DataFrame()

print(f"\nVariables with missing values: {len(df_missing)}/{len(available_in_short)}")
if len(df_missing) > 0:
    print("\nTop 10 variables by missing %:")
    for idx, row in df_missing.head(10).iterrows():
        print(f"  {row['Variable']}: {row['Missing_Count']} ({row['Missing_Pct']:.1f}%)")

# ==============================================================================
# SAVE PREPROCESSED DATA
# ==============================================================================

print("\n" + "="*100)
print("SAVING PREPROCESSED DATA")
print("="*100)

# Create output directory
output_dir = f'analysis_outputs/{AGENT_TYPE}'

# Save datasets
df_short_filtered.to_csv(f'{output_dir}/01_short_calls_original.csv', index=False)
df_long_filtered.to_csv(f'{output_dir}/01_long_calls_original.csv', index=False)
df_combined.to_csv(f'{output_dir}/01_combined_original.csv', index=False)

print(f"\n[OK] Saved datasets to {output_dir}:")
print("  - 01_short_calls_original.csv")
print("  - 01_long_calls_original.csv")
print("  - 01_combined_original.csv")

# Save metadata
metadata = {
    'agent_name': AGENT_NAME,
    'agent_type': AGENT_TYPE,
    'total_variables': len(available_in_short),
    'categorical_variables': len(categorical_vars),
    'numerical_variables': len(numerical_vars),
    'categorical_list': categorical_vars,
    'numerical_list': numerical_vars,
    'total_records': len(df_combined),
    'short_calls': int((df_combined['target'] == 0).sum()),
    'long_calls': int((df_combined['target'] == 1).sum()),
    'sections': {section: len(vars_list) for section, vars_list in VARIABLE_SECTIONS.items()}
}

with open(f'{output_dir}/01_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("  - 01_metadata.json")

# Save missing values summary
if len(df_missing) > 0:
    df_missing.to_csv(f'{output_dir}/01_missing_values_summary.csv', index=False)
    print("  - 01_missing_values_summary.csv")

print("\n" + "="*100)
print(f"PREPROCESSING COMPLETE FOR {AGENT_NAME}")
print("="*100)
print(f"\n[OK] Prepared {len(available_in_short)} variables for agent-level analysis")
print("[OK] Data ready for correlation, feature importance, and SHAP analysis")

