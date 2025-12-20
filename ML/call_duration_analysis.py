"""
SALES CALL DURATION ANALYSIS
Analyzing factors that contribute to longer call durations (>4.88 minutes vs <4.88 minutes)

Research Question: What variables and their weights contribute to calls lasting longer than 4.88 minutes?
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import chi2_contingency, mannwhitneyu, ttest_ind
import warnings
warnings.filterwarnings('ignore')

# Set style for beautiful visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

print("="*100)
print("SALES CALL DURATION ANALYSIS - DATA LOADING & PREPROCESSING")
print("="*100)

# Load datasets
df_short = pd.read_csv('Less_than_4.88_mnt..csv')
df_long = pd.read_csv('greater_than_4.88_mnt..csv')

# Add label column
df_short['call_duration_group'] = 'Short (<4.88 min)'
df_long['call_duration_group'] = 'Long (>4.88 min)'

print(f"\nShort calls: {df_short.shape[0]} rows")
print(f"Long calls: {df_long.shape[0]} rows")

# Columns to remove (as specified)
cols_to_remove = [
    'TO_Lead_ID', 'TO_Phone', 'TO_Status', 'TO_Campaing_ID', 'TO_Recording_Link',
    'TO_Transcription_VICI(0-32000) Words', 'TO_Transcription_VICI(32001-64000) Words',
    'TO_Transcription_VICI(64000+ Words)', 'TO_OMC_Campaign_ID', 'TO_OMC_Recording_Link',
    'TO_OMC_User_Group', 'TO_OMC_Transcription_VICI', 
    'TO_OMC_Transcription_VICI(32000-64000)Words', 
    'TO_OMC_Transcription_VICI(64000+ Words)', 'customer_name', 'customer_address',
    'lgs_error_message'  # 100% missing
]

# Remove columns
df_short_clean = df_short.drop(columns=[col for col in cols_to_remove if col in df_short.columns])
df_long_clean = df_long.drop(columns=[col for col in cols_to_remove if col in df_long.columns])

print(f"\nAfter removing unnecessary columns:")
print(f"  Short calls: {df_short_clean.shape[1]} columns")
print(f"  Long calls: {df_long_clean.shape[1]} columns")

# Combine datasets for analysis
df_combined = pd.concat([df_short_clean, df_long_clean], ignore_index=True)
print(f"\nCombined dataset: {df_combined.shape[0]} rows, {df_combined.shape[1]} columns")

# Separate numeric and categorical columns
numeric_cols = df_combined.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df_combined.select_dtypes(include=['object', 'bool']).columns.tolist()

# Remove the label column from categorical
if 'call_duration_group' in categorical_cols:
    categorical_cols.remove('call_duration_group')

print(f"\nNumeric columns: {len(numeric_cols)}")
print(f"Categorical columns: {len(categorical_cols)}")

# Create directory for outputs
import os
os.makedirs('analysis_outputs', exist_ok=True)

print("\n" + "="*100)
print("PREPROCESSING COMPLETE")
print("="*100)

# Save preprocessed data info
with open('analysis_outputs/preprocessing_summary.txt', 'w') as f:
    f.write("PREPROCESSING SUMMARY\n")
    f.write("="*80 + "\n\n")
    f.write(f"Original columns: {df_short.shape[1]}\n")
    f.write(f"Columns after removal: {df_short_clean.shape[1]}\n")
    f.write(f"Columns removed: {len(cols_to_remove)}\n\n")
    f.write(f"Numeric columns: {len(numeric_cols)}\n")
    f.write(f"Categorical columns: {len(categorical_cols)}\n\n")
    f.write("Numeric Columns:\n")
    for col in numeric_cols:
        f.write(f"  - {col}\n")
    f.write("\nCategorical Columns:\n")
    for col in categorical_cols:
        f.write(f"  - {col}\n")

print("\nPreprocessing summary saved to: analysis_outputs/preprocessing_summary.txt")

