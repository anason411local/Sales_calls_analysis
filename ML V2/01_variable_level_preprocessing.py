"""
==============================================================================
LEVEL 1: VARIABLE-LEVEL PREPROCESSING
==============================================================================

Purpose: Prepare the 49 original variables for analysis
- Load raw data
- Filter to specified 49 variables (Sections 1-6.6)
- Create binary target (Short vs Long calls)
- Minimal processing (keep original values)
- Save clean data for Level 1 analysis

Note: Encoding happens ONLY when needed for ML models
==============================================================================
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("LEVEL 1: VARIABLE-LEVEL PREPROCESSING")
print("="*100)

# ==============================================================================
# DEFINE 49 VARIABLES (SECTIONS 1-6.6)
# ==============================================================================

VARIABLE_SECTIONS = {
    # Section 1: Lead Quality
    'lead_quality': [
        'LQ_Company_Name', 'LQ_Company_Address', 'LQ_Service', 'LQ_Customer_Name',
        'Calls Count', 'Connection Made Calls'
    ],
    
    # Section 2: Timings
    'timings': [
        'TO_Event_O', 'timezone', 'season_status'
        # Removed: 'season_month' (constant - only December)
    ],
    
    # Section 3: LGS Department
    'lgs_department': [
        'TO_User_M', 'lgs_sentiment_style', 'lgs_agent_gender', 'TO_length_in_sec',
        'is_decision_maker', 'ready_for_customers', 'forbidden_industry', 'ready_to_transfer'
    ],
    
    # Section 4: Customer
    'customer': [
        'customer_sentiment_lgs', 'customer_sentiment_omc', 'customer_language',
        'customer_knows_marketing', 'customer_availability', 'who_said_hello_first_lgs',
        'customer_marketing_experience'
    ],
    
    # Section 5: Technical Quality
    'technical_quality': [
        'technical_quality_score', 'technical_quality_issues'
    ],
    
    # Section 6.1: OMC Department
    'omc_department': [
        'TO_OMC_User', 'TO_OMC_Disposiion', 'omc_agent_sentiment_style',
        'omc_who_said_hello_first'
        # Removed: 'TO_OMC_Duration' (perfect separator - essentially call duration itself)
    ],
    
    # Section 6.2: OMC Customer Engagement
    'omc_engagement': [
        'customer_talk_percentage', 'total_discovery_questions', 'total_buying_signals'
    ],
    
    # Section 6.3: OMC Call Opening
    'omc_opening': [
        'time_to_reason_seconds', 'location_mentioned', 'business_type_mentioned',
        'within_45_seconds', 'call_structure_framed'
    ],
    
    # Section 6.4: OMC Objections
    'omc_objections': [
        'total_objections', 'objections_acknowledged', 'price_mentions_final_2min',
        'timeline_mentions_final_2min', 'contract_mentions_final_2min', 'objections_rebutted'
    ],
    
    # Section 6.5: Pace & Control
    'omc_pace': [
        'total_interruptions'
    ],
    
    # Section 6.6: Outcome
    'omc_outcome': [
        'commitment_type', 'call_result_tag'
    ]
}

# Flatten to get all 49 variables
ALL_49_VARIABLES = []
for section_vars in VARIABLE_SECTIONS.values():
    ALL_49_VARIABLES.extend(section_vars)

print(f"\nDefined {len(ALL_49_VARIABLES)} variables across {len(VARIABLE_SECTIONS)} sections")
for section, vars_list in VARIABLE_SECTIONS.items():
    print(f"  {section}: {len(vars_list)} variables")

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
# FILTER TO 49 VARIABLES
# ==============================================================================

print("\n" + "="*100)
print("FILTERING TO 49 SPECIFIED VARIABLES")
print("="*100)

# Check which variables are available
available_in_short = [v for v in ALL_49_VARIABLES if v in df_short.columns]
available_in_long = [v for v in ALL_49_VARIABLES if v in df_long.columns]

missing = set(ALL_49_VARIABLES) - set(available_in_short)
if missing:
    print(f"\n[WARNING] Missing variables in dataset: {missing}")

print(f"\nAvailable variables: {len(available_in_short)}/49")

# Filter to available variables
df_short_filtered = df_short[available_in_short].copy()
df_long_filtered = df_long[available_in_long].copy()

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

print(f"\nCombined dataset: {df_combined.shape}")
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

print("\nCategorical:", categorical_vars[:10], "..." if len(categorical_vars) > 10 else "")
print("Numerical:", numerical_vars)

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

df_missing = pd.DataFrame(missing_summary).sort_values('Missing_Pct', ascending=False)

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
os.makedirs('analysis_outputs/level1_variable', exist_ok=True)

# Save datasets
df_short_filtered.to_csv('analysis_outputs/level1_variable/01_short_calls_original.csv', index=False)
df_long_filtered.to_csv('analysis_outputs/level1_variable/01_long_calls_original.csv', index=False)
df_combined.to_csv('analysis_outputs/level1_variable/01_combined_original.csv', index=False)

print("\n[OK] Saved datasets:")
print("  - 01_short_calls_original.csv")
print("  - 01_long_calls_original.csv")
print("  - 01_combined_original.csv")

# Save metadata
metadata = {
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

import json
with open('analysis_outputs/level1_variable/01_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("  - 01_metadata.json")

# Save missing values summary
if len(df_missing) > 0:
    df_missing.to_csv('analysis_outputs/level1_variable/01_missing_values_summary.csv', index=False)
    print("  - 01_missing_values_summary.csv")

print("\n" + "="*100)
print("LEVEL 1 PREPROCESSING COMPLETE")
print("="*100)
print(f"\n[OK] Prepared {len(available_in_short)} variables for variable-level analysis")
print("[OK] Data kept in original format (no encoding)")
print("[OK] Ready for Level 1 analysis")

