"""
DPAD Analysis - Step 1: Data Preprocessing
===========================================

Purpose:
--------
Load and preprocess sales call data to compare High-DPAD (>1 deal/agent/day) 
vs Low-DPAD (<1 deal/agent/day) agents.

What This Script Does:
----------------------
1. Loads two datasets:
   - High DPAD agents (>1 deal/day): All calls from top performers
   - Low DPAD agents (<1 deal/day): All calls from underperformers

2. Creates binary target variable:
   - high_dpad = 1 for calls from high-DPAD agents
   - high_dpad = 0 for calls from low-DPAD agents

3. Cleans and prepares data:
   - Handles missing values
   - Encodes categorical variables
   - Scales numerical features
   - Removes columns not suitable for analysis

4. Saves processed datasets for downstream analysis

Key Insight:
-----------
Each agent appears in ONLY ONE dataset (high or low DPAD), never both.
We're analyzing what call characteristics differentiate successful agents.

Author: AI Agent
Date: 2025
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

# Sklearn for preprocessing
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

# Create output directories
def create_output_directories():
    """Create all necessary output directories"""
    base_dir = Path("ML_for_DPAD")
    
    directories = [
        base_dir / "analysis_outputs" / "preprocessed_data",
        base_dir / "analysis_outputs" / "correlations",
        base_dir / "analysis_outputs" / "feature_importance",
        base_dir / "analysis_outputs" / "statistical_tests",
        base_dir / "analysis_outputs" / "shap_analysis",
        base_dir / "analysis_outputs" / "lime_analysis",
        base_dir / "analysis_outputs" / "visualizations",
        base_dir / "analysis_outputs" / "agent_level_comparison",
        base_dir / "analysis_outputs" / "final_report"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ Created output directory structure")
    return base_dir


def load_datasets():
    """
    Load High-DPAD and Low-DPAD datasets
    
    Returns:
    --------
    high_dpad_df: DataFrame with calls from high-DPAD agents (>1 deal/day)
    low_dpad_df: DataFrame with calls from low-DPAD agents (<1 deal/day)
    """
    print("\n" + "="*70)
    print("LOADING DATASETS")
    print("="*70)
    
    # File paths
    high_dpad_file = "output_data/dpad_gretaer_than_1_temp.csv"
    low_dpad_file = "output_data/dpad_less_than_1_temp.csv"
    
    # Check if files exist
    if not os.path.exists(high_dpad_file):
        raise FileNotFoundError(f"High DPAD file not found: {high_dpad_file}")
    if not os.path.exists(low_dpad_file):
        raise FileNotFoundError(f"Low DPAD file not found: {low_dpad_file}")
    
    # Load datasets
    print(f"\n📂 Loading High-DPAD dataset: {high_dpad_file}")
    high_dpad_df = pd.read_csv(high_dpad_file, low_memory=False)
    print(f"   ✓ Loaded {len(high_dpad_df):,} calls from HIGH-DPAD agents")
    
    print(f"\n📂 Loading Low-DPAD dataset: {low_dpad_file}")
    low_dpad_df = pd.read_csv(low_dpad_file, low_memory=False)
    print(f"   ✓ Loaded {len(low_dpad_df):,} calls from LOW-DPAD agents")
    
    # Add target variable
    high_dpad_df['high_dpad'] = 1  # High performers
    low_dpad_df['high_dpad'] = 0   # Low performers
    
    print(f"\n✅ Created binary target: high_dpad (1=High, 0=Low)")
    
    return high_dpad_df, low_dpad_df


def verify_agent_separation(high_dpad_df, low_dpad_df):
    """
    Verify that agents don't appear in both datasets
    This is a critical data integrity check
    """
    print("\n" + "="*70)
    print("VERIFYING AGENT SEPARATION")
    print("="*70)
    
    high_agents = set(high_dpad_df['TO_OMC_User'].dropna().unique())
    low_agents = set(low_dpad_df['TO_OMC_User'].dropna().unique())
    
    overlap = high_agents.intersection(low_agents)
    
    print(f"\n📊 Agent Distribution:")
    print(f"   High-DPAD agents: {len(high_agents):,}")
    print(f"   Low-DPAD agents:  {len(low_agents):,}")
    print(f"   Overlap:          {len(overlap):,}")
    
    if len(overlap) > 0:
        print(f"\n⚠️  WARNING: {len(overlap)} agents appear in BOTH datasets!")
        print(f"   This should NOT happen. Overlapping agents: {list(overlap)[:5]}")
    else:
        print(f"\n✅ Perfect separation - No agents appear in both datasets")
    
    return len(overlap) == 0


def get_columns_to_exclude():
    """
    Define columns that should NOT be used as features
    
    Categories:
    -----------
    1. IDs and Keys: Not predictive, just identifiers
    2. Text/Transcription: Too high cardinality, needs NLP
    3. Dates: Already encoded as season/month
    4. Links: Not useful for ML
    5. Target-related: The outcome we're predicting
    6. Raw names: High cardinality, not standardized
    """
    
    exclude_columns = [
        # IDs and Keys
        'TO_Lead_ID', 'lead_id', 'row_number',
        
        # Phone numbers
        'TO_Phone',
        
        # Agent/User identifiers (keep for grouping, but exclude from features)
        'TO_User_M', 'TO_OMC_User', 'LQ_User',
        
        # Campaign IDs
        'TO_Campaing_ID', 'TO_OMC_Campaign_ID',
        
        # Dates (already have season_status, season_month)
        'TO_Event_O', 'TO_OMC_Call_Date_O',
        
        # Recording links
        'TO_Recording_Link', 'TO_OMC_Recording_Link',
        
        # Transcription text (needs separate NLP analysis)
        'TO_Transcription_VICI(0-32000) Words',
        'TO_Transcription_VICI(32001-64000) Words',
        'TO_Transcription_VICI(64000+ Words)',
        'TO_OMC_Transcription_VICI',
        'TO_OMC_Transcription_VICI(32000-64000)Words',
        'TO_OMC_Transcription_VICI(64000+ Words)',
        
        # Raw names (high cardinality, not standardized)
        'LQ_Customer_Name', 'customer_name',
        'LQ_Company_Name',
        
        # Addresses (too specific, but we have timezone/location_mentioned)
        'LQ_Company_Address', 'customer_address',
        
        # Disposition codes (too many categories, needs separate encoding)
        'TO_Status', 'TO_OMC_Disposiion', 'TO_OMC_User_Group',
        
        # Error messages (only present when extraction failed)
        'lgs_error_message', 'omc_error_message',
        
        # Service details (high cardinality)
        'LQ_Service', 'service',
        
        # Success flags (metadata, not predictive features)
        'lgs_extraction_success', 'omc_extraction_success', 'extraction_complete'
    ]
    
    return exclude_columns


def identify_feature_types(df, exclude_cols):
    """
    Identify which columns are categorical, numerical, or boolean
    
    Returns:
    --------
    Dictionary with 'categorical', 'numerical', and 'boolean' column lists
    """
    
    # Get columns that are NOT excluded and NOT the target
    feature_cols = [col for col in df.columns 
                    if col not in exclude_cols and col != 'high_dpad']
    
    categorical_cols = []
    numerical_cols = []
    boolean_cols = []
    
    for col in feature_cols:
        # Skip if mostly missing
        if df[col].isna().sum() / len(df) > 0.95:
            continue
            
        dtype = df[col].dtype
        n_unique = df[col].nunique()
        
        # Boolean columns
        if dtype == 'bool' or n_unique == 2:
            boolean_cols.append(col)
        
        # Numerical columns
        elif dtype in ['int64', 'float64']:
            # If few unique values, might be categorical
            if n_unique < 10:
                categorical_cols.append(col)
            else:
                numerical_cols.append(col)
        
        # Categorical columns
        elif dtype == 'object':
            # If many unique values, might need special handling
            if n_unique < 50:
                categorical_cols.append(col)
    
    return {
        'categorical': categorical_cols,
        'numerical': numerical_cols,
        'boolean': boolean_cols
    }


def handle_missing_values(df, feature_types):
    """
    Handle missing values based on column type
    
    Strategy:
    ---------
    - Numerical: Fill with median
    - Categorical: Fill with 'Unknown'
    - Boolean: Fill with False (more conservative)
    """
    print("\n" + "="*70)
    print("HANDLING MISSING VALUES")
    print("="*70)
    
    df_clean = df.copy()
    
    # Track missing value handling
    missing_report = []
    
    # Numerical columns - fill with median
    for col in feature_types['numerical']:
        if col in df_clean.columns:
            missing_count = df_clean[col].isna().sum()
            if missing_count > 0:
                median_val = df_clean[col].median()
                df_clean[col].fillna(median_val, inplace=True)
                missing_report.append({
                    'column': col,
                    'type': 'numerical',
                    'missing_count': missing_count,
                    'fill_value': median_val
                })
    
    # Categorical columns - fill with 'Unknown'
    for col in feature_types['categorical']:
        if col in df_clean.columns:
            missing_count = df_clean[col].isna().sum()
            if missing_count > 0:
                df_clean[col].fillna('Unknown', inplace=True)
                missing_report.append({
                    'column': col,
                    'type': 'categorical',
                    'missing_count': missing_count,
                    'fill_value': 'Unknown'
                })
    
    # Boolean columns - fill with False
    for col in feature_types['boolean']:
        if col in df_clean.columns:
            missing_count = df_clean[col].isna().sum()
            if missing_count > 0:
                df_clean[col].fillna(False, inplace=True)
                missing_report.append({
                    'column': col,
                    'type': 'boolean',
                    'missing_count': missing_count,
                    'fill_value': False
                })
    
    print(f"\n✅ Handled missing values in {len(missing_report)} columns")
    print(f"   - Numerical: {sum(1 for x in missing_report if x['type']=='numerical')}")
    print(f"   - Categorical: {sum(1 for x in missing_report if x['type']=='categorical')}")
    print(f"   - Boolean: {sum(1 for x in missing_report if x['type']=='boolean')}")
    
    return df_clean, missing_report


def encode_categorical_variables(df, feature_types):
    """
    Encode categorical variables using Label Encoding
    
    For ML models, we need numerical representations
    """
    print("\n" + "="*70)
    print("ENCODING CATEGORICAL VARIABLES")
    print("="*70)
    
    df_encoded = df.copy()
    encoders = {}
    
    # First, convert Yes/No boolean strings to actual booleans/integers
    # Do this for ALL columns, not just boolean feature_types
    for col in df_encoded.columns:
        if df_encoded[col].dtype == 'object':
            unique_vals = set(df_encoded[col].dropna().astype(str).unique())
            # Check if it's a Yes/No column
            if unique_vals.issubset({'Yes', 'No', 'yes', 'no', 'YES', 'NO', 'True', 'False', 'true', 'false', 'PASS'}):
                df_encoded[col] = df_encoded[col].map({
                    'Yes': 1, 'yes': 1, 'YES': 1,
                    'No': 0, 'no': 0, 'NO': 0,
                    'True': 1, 'true': 1,
                    'False': 0, 'false': 0,
                    'PASS': 1  # PASS is like Yes
                })
                print(f"   ✓ Converted Yes/No column: {col}")
    
    # Now encode categorical variables
    for col in feature_types['categorical']:
        if col in df_encoded.columns:
            # Skip if already numeric
            if pd.api.types.is_numeric_dtype(df_encoded[col]):
                continue
                
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
            encoders[col] = le
            
            print(f"   ✓ Encoded {col}: {len(le.classes_)} unique values")
    
    # Convert boolean columns to int
    for col in feature_types['boolean']:
        if col in df_encoded.columns:
            if not pd.api.types.is_numeric_dtype(df_encoded[col]):
                # Try to convert, if fails, use label encoding
                try:
                    df_encoded[col] = df_encoded[col].astype(int)
                except:
                    le = LabelEncoder()
                    df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                    encoders[col] = le
            else:
                df_encoded[col] = df_encoded[col].astype(int)
    
    print(f"\n✅ Encoded {len(encoders)} categorical columns")
    print(f"✅ Converted boolean columns to integers")
    
    return df_encoded, encoders


def prepare_final_dataset(df, exclude_cols, feature_types):
    """
    Prepare final dataset for ML analysis
    
    Steps:
    ------
    1. Remove excluded columns
    2. Handle missing values
    3. Encode categorical variables
    4. Separate features and target
    """
    print("\n" + "="*70)
    print("PREPARING FINAL DATASET")
    print("="*70)
    
    # Step 1: Handle missing values
    df_clean, missing_report = handle_missing_values(df, feature_types)
    
    # Step 2: Encode categorical variables
    df_encoded, encoders = encode_categorical_variables(df_clean, feature_types)
    
    # Step 3: Remove excluded columns (but keep agent ID for later grouping)
    agent_col = 'TO_OMC_User'
    cols_to_keep = [col for col in df_encoded.columns 
                    if col not in exclude_cols or col == agent_col or col == 'high_dpad']
    
    df_final = df_encoded[cols_to_keep].copy()
    
    # Step 4: Separate features and target
    X = df_final.drop(['high_dpad', agent_col], axis=1, errors='ignore')
    y = df_final['high_dpad']
    agent_ids = df_final[agent_col] if agent_col in df_final.columns else None
    
    print(f"\n📊 Final Dataset Shape:")
    print(f"   Features (X): {X.shape}")
    print(f"   Target (y):   {y.shape}")
    print(f"   Class distribution: High-DPAD: {(y==1).sum():,} | Low-DPAD: {(y==0).sum():,}")
    
    return X, y, agent_ids, encoders, missing_report


def generate_preprocessing_report(high_dpad_df, low_dpad_df, X, y, 
                                   feature_types, missing_report, output_dir):
    """
    Generate comprehensive preprocessing report
    """
    print("\n" + "="*70)
    print("GENERATING PREPROCESSING REPORT")
    print("="*70)
    
    report = []
    report.append("# DPAD Analysis - Preprocessing Report")
    report.append("=" * 70)
    report.append("")
    
    # Dataset Overview
    report.append("## 1. Dataset Overview")
    report.append("")
    report.append(f"**High-DPAD Calls (>1 deal/agent/day):** {len(high_dpad_df):,}")
    report.append(f"**Low-DPAD Calls (<1 deal/agent/day):**  {len(low_dpad_df):,}")
    report.append(f"**Total Calls:**                         {len(high_dpad_df) + len(low_dpad_df):,}")
    report.append("")
    
    # Agent Distribution
    high_agents = high_dpad_df['TO_OMC_User'].nunique()
    low_agents = low_dpad_df['TO_OMC_User'].nunique()
    report.append(f"**High-DPAD Agents:** {high_agents}")
    report.append(f"**Low-DPAD Agents:**  {low_agents}")
    report.append(f"**Total Agents:**     {high_agents + low_agents}")
    report.append("")
    
    # Feature Overview
    report.append("## 2. Feature Types")
    report.append("")
    report.append(f"**Numerical Features:**   {len(feature_types['numerical'])}")
    report.append(f"**Categorical Features:** {len(feature_types['categorical'])}")
    report.append(f"**Boolean Features:**     {len(feature_types['boolean'])}")
    report.append(f"**Total Features:**       {X.shape[1]}")
    report.append("")
    
    # Missing Values
    report.append("## 3. Missing Value Handling")
    report.append("")
    if missing_report:
        report.append(f"**Columns with missing values:** {len(missing_report)}")
        report.append("")
        report.append("Top 10 columns by missing count:")
        sorted_missing = sorted(missing_report, key=lambda x: x['missing_count'], reverse=True)[:10]
        for item in sorted_missing:
            report.append(f"- {item['column']}: {item['missing_count']:,} missing ({item['type']})")
    else:
        report.append("**No missing values found**")
    report.append("")
    
    # Class Balance
    report.append("## 4. Class Balance")
    report.append("")
    high_count = (y == 1).sum()
    low_count = (y == 0).sum()
    high_pct = (high_count / len(y)) * 100
    low_pct = (low_count / len(y)) * 100
    report.append(f"**High-DPAD (Class 1):** {high_count:,} ({high_pct:.1f}%)")
    report.append(f"**Low-DPAD (Class 0):**  {low_count:,} ({low_pct:.1f}%)")
    
    # Imbalance check
    if high_pct < 40 or high_pct > 60:
        report.append("")
        report.append("⚠️ **Class Imbalance Detected** - Consider using class weights or SMOTE")
    report.append("")
    
    # Save report
    report_path = output_dir / "analysis_outputs" / "preprocessed_data" / "preprocessing_report.txt"
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Preprocessing report saved: {report_path}")
    
    # Also print to console
    print("\n" + '\n'.join(report))


def save_processed_data(X, y, agent_ids, encoders, feature_types, output_dir):
    """
    Save all preprocessed data and metadata
    """
    print("\n" + "="*70)
    print("SAVING PROCESSED DATA")
    print("="*70)
    
    output_path = output_dir / "analysis_outputs" / "preprocessed_data"
    
    # Save features and target
    X.to_csv(output_path / "X_features.csv", index=False)
    y.to_csv(output_path / "y_target.csv", index=False, header=True)
    
    print(f"   ✓ Saved features: X_features.csv")
    print(f"   ✓ Saved target: y_target.csv")
    
    # Save agent IDs if available
    if agent_ids is not None:
        agent_ids.to_csv(output_path / "agent_ids.csv", index=False, header=True)
        print(f"   ✓ Saved agent IDs: agent_ids.csv")
    
    # Save feature names and types
    feature_metadata = {
        'feature_names': list(X.columns),
        'numerical_features': feature_types['numerical'],
        'categorical_features': feature_types['categorical'],
        'boolean_features': feature_types['boolean']
    }
    
    with open(output_path / "feature_metadata.json", 'w') as f:
        json.dump(feature_metadata, f, indent=2)
    
    print(f"   ✓ Saved feature metadata: feature_metadata.json")
    
    # Save encoders
    import pickle
    with open(output_path / "encoders.pkl", 'wb') as f:
        pickle.dump(encoders, f)
    
    print(f"   ✓ Saved encoders: encoders.pkl")
    
    print(f"\n✅ All processed data saved to: {output_path}")


def main():
    """Main preprocessing pipeline"""
    
    print("\n" + "="*70)
    print("DPAD ANALYSIS - PREPROCESSING")
    print("="*70)
    print("\nComparing High-DPAD (>1) vs Low-DPAD (<1) Agents")
    print("="*70)
    
    # Create output directories
    output_dir = create_output_directories()
    
    # Load datasets
    high_dpad_df, low_dpad_df = load_datasets()
    
    # Verify agent separation (data integrity check)
    verify_agent_separation(high_dpad_df, low_dpad_df)
    
    # Combine datasets
    print("\n" + "="*70)
    print("COMBINING DATASETS")
    print("="*70)
    df_combined = pd.concat([high_dpad_df, low_dpad_df], ignore_index=True)
    print(f"✅ Combined dataset: {len(df_combined):,} total calls")
    
    # Get columns to exclude
    exclude_cols = get_columns_to_exclude()
    print(f"\n📋 Excluding {len(exclude_cols)} columns from feature set")
    
    # Identify feature types
    feature_types = identify_feature_types(df_combined, exclude_cols)
    print("\n📊 Feature Type Distribution:")
    print(f"   Numerical:   {len(feature_types['numerical'])}")
    print(f"   Categorical: {len(feature_types['categorical'])}")
    print(f"   Boolean:     {len(feature_types['boolean'])}")
    
    # Prepare final dataset
    X, y, agent_ids, encoders, missing_report = prepare_final_dataset(
        df_combined, exclude_cols, feature_types
    )
    
    # Generate preprocessing report
    generate_preprocessing_report(
        high_dpad_df, low_dpad_df, X, y, 
        feature_types, missing_report, output_dir
    )
    
    # Save processed data
    save_processed_data(X, y, agent_ids, encoders, feature_types, output_dir)
    
    print("\n" + "="*70)
    print("✅ PREPROCESSING COMPLETE")
    print("="*70)
    print(f"\nReady for downstream analysis:")
    print(f"  - Features: {X.shape[1]} variables")
    print(f"  - Samples:  {X.shape[0]:,} calls")
    print(f"  - Target:   High-DPAD vs Low-DPAD classification")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

