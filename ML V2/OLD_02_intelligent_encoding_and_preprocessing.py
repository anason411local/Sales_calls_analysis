"""
STEP 2: INTELLIGENT ENCODING AND PREPROCESSING
Preparing categorical variables for correlation and statistical analysis

Encoding Strategy:
- Low Cardinality (2-10): One-Hot Encoding
- Medium Cardinality (11-50): Target Encoding + Frequency Encoding
- High Cardinality (>50): Target Encoding with rare category grouping
- Missing Values: Create 'Missing' indicator where appropriate
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("INTELLIGENT ENCODING AND PREPROCESSING")
print("="*100)

# Load data
df_short = pd.read_csv('analysis_outputs/01_short_calls_data.csv')
df_long = pd.read_csv('analysis_outputs/01_long_calls_data.csv')
df_combined = pd.read_csv('analysis_outputs/01_combined_data.csv')

print(f"\nLoaded data:")
print(f"  Short: {df_short.shape}")
print(f"  Long: {df_long.shape}")
print(f"  Combined: {df_combined.shape}")

# Create binary target for encoding
df_combined['target'] = (df_combined['call_duration_group'] == 'Long (>4.88 min)').astype(int)

# Separate columns by type
numeric_cols = df_combined.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df_combined.select_dtypes(include=['object', 'bool']).columns.tolist()

# Remove label and target
if 'call_duration_group' in categorical_cols:
    categorical_cols.remove('call_duration_group')
if 'target' in numeric_cols:
    numeric_cols.remove('target')

print(f"\nVariable types:")
print(f"  Numeric: {len(numeric_cols)}")
print(f"  Categorical: {len(categorical_cols)}")

# ==================================================================================
# DEFINE ENCODING STRATEGY BASED ON CARDINALITY
# ==================================================================================

print("\n" + "="*100)
print("ENCODING STRATEGY")
print("="*100)

low_cardinality = []
medium_cardinality = []
high_cardinality = []

for col in categorical_cols:
    nunique = df_combined[col].nunique()
    if nunique <= 10:
        low_cardinality.append(col)
    elif nunique <= 50:
        medium_cardinality.append(col)
    else:
        high_cardinality.append(col)

print(f"\nLow Cardinality (One-Hot): {len(low_cardinality)} columns")
for col in low_cardinality:
    print(f"  - {col}: {df_combined[col].nunique()} unique values")

print(f"\nMedium Cardinality (Target + Frequency): {len(medium_cardinality)} columns")
for col in medium_cardinality:
    print(f"  - {col}: {df_combined[col].nunique()} unique values")

print(f"\nHigh Cardinality (Target Encoding): {len(high_cardinality)} columns")
for col in high_cardinality:
    print(f"  - {col}: {df_combined[col].nunique()} unique values")

# ==================================================================================
# ENCODING: LOW CARDINALITY (ONE-HOT)
# ==================================================================================

print("\n" + "="*100)
print("ENCODING: LOW CARDINALITY (ONE-HOT)")
print("="*100)

df_encoded = df_combined.copy()

one_hot_columns = []

for col in low_cardinality:
    print(f"\nOne-Hot Encoding: {col}")
    
    # Fill missing with 'Missing'
    df_encoded[col] = df_encoded[col].fillna('Missing')
    
    # One-hot encode
    dummies = pd.get_dummies(df_encoded[col], prefix=col, drop_first=False)
    
    # Add to dataframe
    df_encoded = pd.concat([df_encoded, dummies], axis=1)
    one_hot_columns.extend(dummies.columns.tolist())
    
    print(f"  Created {len(dummies.columns)} binary columns")
    
    # Drop original
    df_encoded = df_encoded.drop(col, axis=1)

print(f"\nTotal one-hot encoded columns created: {len(one_hot_columns)}")

# ==================================================================================
# ENCODING: MEDIUM CARDINALITY (TARGET + FREQUENCY)
# ==================================================================================

print("\n" + "="*100)
print("ENCODING: MEDIUM CARDINALITY (TARGET + FREQUENCY)")
print("="*100)

target_encoded_columns = []
frequency_encoded_columns = []

for col in medium_cardinality:
    print(f"\nProcessing: {col}")
    
    # Fill missing
    df_encoded[col] = df_encoded[col].fillna('Missing')
    
    # 1. Target Encoding
    target_encoding = df_encoded.groupby(col)['target'].mean().to_dict()
    df_encoded[f'{col}_target_enc'] = df_encoded[col].map(target_encoding)
    target_encoded_columns.append(f'{col}_target_enc')
    
    # 2. Frequency Encoding
    frequency_encoding = df_encoded[col].value_counts(normalize=True).to_dict()
    df_encoded[f'{col}_freq_enc'] = df_encoded[col].map(frequency_encoding)
    frequency_encoded_columns.append(f'{col}_freq_enc')
    
    print(f"  Created target encoding: {col}_target_enc")
    print(f"  Created frequency encoding: {col}_freq_enc")
    
    # Keep original as label encoded for reference
    le = LabelEncoder()
    df_encoded[f'{col}_label'] = le.fit_transform(df_encoded[col].astype(str))
    
    # Drop original
    df_encoded = df_encoded.drop(col, axis=1)

print(f"\nTotal target encoded columns: {len(target_encoded_columns)}")
print(f"Total frequency encoded columns: {len(frequency_encoded_columns)}")

# ==================================================================================
# ENCODING: HIGH CARDINALITY (TARGET ENCODING WITH GROUPING)
# ==================================================================================

print("\n" + "="*100)
print("ENCODING: HIGH CARDINALITY (TARGET + RARE CATEGORY GROUPING)")
print("="*100)

for col in high_cardinality:
    print(f"\nProcessing: {col}")
    
    # Fill missing
    df_encoded[col] = df_encoded[col].fillna('Missing')
    
    # Get value counts
    value_counts = df_encoded[col].value_counts()
    
    # Group rare categories (appearing <5 times)
    rare_threshold = 5
    rare_categories = value_counts[value_counts < rare_threshold].index.tolist()
    
    if rare_categories:
        print(f"  Grouping {len(rare_categories)} rare categories (count < {rare_threshold})")
        df_encoded[col] = df_encoded[col].replace(rare_categories, 'RARE_CATEGORY')
    
    # Target Encoding
    target_encoding = df_encoded.groupby(col)['target'].mean().to_dict()
    df_encoded[f'{col}_target_enc'] = df_encoded[col].map(target_encoding)
    target_encoded_columns.append(f'{col}_target_enc')
    
    # Frequency Encoding
    frequency_encoding = df_encoded[col].value_counts(normalize=True).to_dict()
    df_encoded[f'{col}_freq_enc'] = df_encoded[col].map(frequency_encoding)
    frequency_encoded_columns.append(f'{col}_freq_enc')
    
    print(f"  Final unique categories: {df_encoded[col].nunique()}")
    print(f"  Created: {col}_target_enc, {col}_freq_enc")
    
    # Drop original
    df_encoded = df_encoded.drop(col, axis=1)

# ==================================================================================
# HANDLE MISSING VALUES IN NUMERIC COLUMNS
# ==================================================================================

print("\n" + "="*100)
print("HANDLING MISSING VALUES IN NUMERIC COLUMNS")
print("="*100)

for col in numeric_cols:
    missing_count = df_encoded[col].isnull().sum()
    if missing_count > 0:
        missing_pct = (missing_count / len(df_encoded)) * 100
        print(f"\n{col}: {missing_count} missing ({missing_pct:.1f}%)")
        
        # Create missing indicator
        df_encoded[f'{col}_is_missing'] = df_encoded[col].isnull().astype(int)
        
        # Impute with median
        median_value = df_encoded[col].median()
        df_encoded[col] = df_encoded[col].fillna(median_value)
        
        print(f"  Created: {col}_is_missing")
        print(f"  Imputed with median: {median_value:.2f}")

# ==================================================================================
# FINAL DATASET
# ==================================================================================

print("\n" + "="*100)
print("FINAL ENCODED DATASET")
print("="*100)

# Remove original call_duration_group and target
df_encoded_final = df_encoded.drop(['call_duration_group', 'target'], axis=1)

print(f"\nFinal dataset shape: {df_encoded_final.shape}")
print(f"  Total features: {df_encoded_final.shape[1]}")

# Count feature types
original_numeric = len([c for c in df_encoded_final.columns if c in numeric_cols or c.endswith('_is_missing')])
one_hot_features = len([c for c in df_encoded_final.columns if any(c.startswith(f"{lc}_") for lc in low_cardinality)])
target_features = len([c for c in df_encoded_final.columns if c.endswith('_target_enc')])
freq_features = len([c for c in df_encoded_final.columns if c.endswith('_freq_enc')])
label_features = len([c for c in df_encoded_final.columns if c.endswith('_label')])

print(f"\nFeature breakdown:")
print(f"  Original numeric: {original_numeric}")
print(f"  One-hot encoded: {one_hot_features}")
print(f"  Target encoded: {target_features}")
print(f"  Frequency encoded: {freq_features}")
print(f"  Label encoded: {label_features}")

# ==================================================================================
# SPLIT BACK INTO SHORT AND LONG
# ==================================================================================

print("\n" + "="*100)
print("SPLITTING ENCODED DATA")
print("="*100)

# Recreate labels
df_encoded_final['call_duration_group'] = df_combined['call_duration_group'].values

# Split
df_short_encoded = df_encoded_final[df_encoded_final['call_duration_group'] == 'Short (<4.88 min)'].copy()
df_long_encoded = df_encoded_final[df_encoded_final['call_duration_group'] == 'Long (>4.88 min)'].copy()

print(f"\nEncoded datasets:")
print(f"  Short: {df_short_encoded.shape}")
print(f"  Long: {df_long_encoded.shape}")

# ==================================================================================
# SAVE ENCODED DATA
# ==================================================================================

print("\n" + "="*100)
print("SAVING ENCODED DATA")
print("="*100)

df_short_encoded.to_csv('analysis_outputs/02_short_calls_encoded.csv', index=False)
df_long_encoded.to_csv('analysis_outputs/02_long_calls_encoded.csv', index=False)
df_encoded_final.to_csv('analysis_outputs/02_combined_encoded.csv', index=False)

print(f"\n[OK] Saved: 02_short_calls_encoded.csv")
print(f"[OK] Saved: 02_long_calls_encoded.csv")
print(f"[OK] Saved: 02_combined_encoded.csv")

# Save encoding mapping
encoding_info = {
    'low_cardinality_columns': low_cardinality,
    'medium_cardinality_columns': medium_cardinality,
    'high_cardinality_columns': high_cardinality,
    'one_hot_features': one_hot_features,
    'target_encoded_features': target_features,
    'frequency_encoded_features': freq_features,
    'total_features': df_encoded_final.shape[1]
}

import json
with open('analysis_outputs/02_encoding_info.json', 'w') as f:
    json.dump(encoding_info, f, indent=2)

print("[OK] Saved: 02_encoding_info.json")

# ==================================================================================
# SUMMARY STATISTICS
# ==================================================================================

print("\n" + "="*100)
print("ENCODING SUMMARY")
print("="*100)

print(f"\nOriginal columns: {len(categorical_cols) + len(numeric_cols)}")
print(f"Final features: {df_encoded_final.shape[1] - 1}")  # -1 for label
print(f"Feature expansion ratio: {(df_encoded_final.shape[1] - 1) / (len(categorical_cols) + len(numeric_cols)):.2f}x")

print("\n" + "="*100)
print("INTELLIGENT ENCODING COMPLETE")
print("="*100)
print("\nReady for:")
print("  1. Correlation analysis (all variables now numeric)")
print("  2. Statistical testing")
print("  3. Machine learning feature importance")
print("  4. Second-order contribution analysis")

