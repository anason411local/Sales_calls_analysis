"""
CORRELATION ANALYSIS & FEATURE IMPORTANCE
Identifies which variables have the strongest relationships with call duration
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pointbiserialr, spearmanr
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Set2")

print("="*100)
print("CORRELATION & FEATURE IMPORTANCE ANALYSIS")
print("="*100)

# Load data
df_short = pd.read_csv('Less_than_4.88_mnt..csv')
df_long = pd.read_csv('greater_than_4.88_mnt..csv')

df_short['call_duration_group'] = 0
df_long['call_duration_group'] = 1

# Remove unnecessary columns
cols_to_remove = [
    'TO_Lead_ID', 'TO_Phone', 'TO_Status', 'TO_Campaing_ID', 'TO_Recording_Link',
    'TO_Transcription_VICI(0-32000) Words', 'TO_Transcription_VICI(32001-64000) Words',
    'TO_Transcription_VICI(64000+ Words)', 'TO_OMC_Campaign_ID', 'TO_OMC_Recording_Link',
    'TO_OMC_User_Group', 'TO_OMC_Transcription_VICI', 
    'TO_OMC_Transcription_VICI(32000-64000)Words', 
    'TO_OMC_Transcription_VICI(64000+ Words)', 'customer_name', 'customer_address',
    'lgs_error_message', 'TO_OMC_Duration'
]

df_short = df_short.drop(columns=[col for col in cols_to_remove if col in df_short.columns])
df_long = df_long.drop(columns=[col for col in cols_to_remove if col in df_long.columns])

df_combined = pd.concat([df_short, df_long], ignore_index=True)

print(f"\nCombined dataset: {df_combined.shape}")

# ==================================================================================
# POINT-BISERIAL CORRELATION (for numeric variables with binary target)
# ==================================================================================
print("\n" + "="*100)
print("POINT-BISERIAL CORRELATION ANALYSIS (Numeric Variables)")
print("="*100)

numeric_cols = df_combined.select_dtypes(include=[np.number]).columns.tolist()
if 'call_duration_group' in numeric_cols:
    numeric_cols.remove('call_duration_group')

correlation_results = []

for col in numeric_cols:
    # Remove missing values
    valid_data = df_combined[[col, 'call_duration_group']].dropna()
    
    if len(valid_data) < 30:  # Need sufficient data
        continue
    
    try:
        # Point-biserial correlation
        correlation, p_value = pointbiserialr(valid_data['call_duration_group'], valid_data[col])
        
        correlation_results.append({
            'Variable': col,
            'Correlation': correlation,
            'Abs_Correlation': abs(correlation),
            'P_Value': p_value,
            'Significant': 'Yes' if p_value < 0.05 else 'No',
            'Direction': 'Positive (favors long)' if correlation > 0 else 'Negative (favors short)',
            'Strength': 'Strong' if abs(correlation) > 0.3 else ('Moderate' if abs(correlation) > 0.1 else 'Weak'),
            'N': len(valid_data)
        })
    except Exception as e:
        continue

df_correlation = pd.DataFrame(correlation_results).sort_values('Abs_Correlation', ascending=False)

# Save results
df_correlation.to_csv('analysis_outputs/correlation_analysis.csv', index=False)
print(f"\n[OK] Correlation analysis saved: analysis_outputs/correlation_analysis.csv")

print("\nTop 25 Variables by Correlation Strength:")
print("-" * 100)
display_cols = ['Variable', 'Correlation', 'P_Value', 'Strength', 'Direction', 'Significant']
print(df_correlation[display_cols].head(25).to_string(index=False))

# ==================================================================================
# FEATURE IMPORTANCE - RANDOM FOREST
# ==================================================================================
print("\n" + "="*100)
print("FEATURE IMPORTANCE - RANDOM FOREST METHOD")
print("="*100)

# Prepare data for ML
df_ml = df_combined.copy()

# Handle missing values - simple imputation for ML
for col in df_ml.select_dtypes(include=[np.number]).columns:
    if col != 'call_duration_group':
        df_ml[col].fillna(df_ml[col].median(), inplace=True)

# Encode categorical variables
label_encoders = {}
for col in df_ml.select_dtypes(include=['object', 'bool']).columns:
    if col != 'call_duration_group':
        le = LabelEncoder()
        df_ml[col] = df_ml[col].astype(str)
        df_ml[col] = le.fit_transform(df_ml[col])
        label_encoders[col] = le

# Prepare features and target
X = df_ml.drop('call_duration_group', axis=1)
y = df_ml['call_duration_group']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

print(f"\nTraining set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")
print(f"Features: {X_train.shape[1]}")

# Train Random Forest
print("\nTraining Random Forest Classifier...")
rf_model = RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_split=20,
                                  min_samples_leaf=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

# Get feature importances
feature_importance_rf = pd.DataFrame({
    'Variable': X.columns,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

# Save
feature_importance_rf.to_csv('analysis_outputs/feature_importance_random_forest.csv', index=False)
print(f"\n[OK] Random Forest feature importance saved: analysis_outputs/feature_importance_random_forest.csv")

print("\nTop 25 Most Important Features (Random Forest):")
print("-" * 100)
print(feature_importance_rf.head(25).to_string(index=False))

# Model performance
train_score = rf_model.score(X_train, y_train)
test_score = rf_model.score(X_test, y_test)
print(f"\nRandom Forest Performance:")
print(f"  Training Accuracy: {train_score:.4f}")
print(f"  Test Accuracy: {test_score:.4f}")

# ==================================================================================
# FEATURE IMPORTANCE - GRADIENT BOOSTING
# ==================================================================================
print("\n" + "="*100)
print("FEATURE IMPORTANCE - GRADIENT BOOSTING METHOD")
print("="*100)

print("\nTraining Gradient Boosting Classifier...")
gb_model = GradientBoostingClassifier(n_estimators=150, max_depth=5, learning_rate=0.1,
                                      min_samples_split=20, min_samples_leaf=10,
                                      random_state=42)
gb_model.fit(X_train, y_train)

# Get feature importances
feature_importance_gb = pd.DataFrame({
    'Variable': X.columns,
    'Importance': gb_model.feature_importances_
}).sort_values('Importance', ascending=False)

# Save
feature_importance_gb.to_csv('analysis_outputs/feature_importance_gradient_boosting.csv', index=False)
print(f"\n[OK] Gradient Boosting feature importance saved: analysis_outputs/feature_importance_gradient_boosting.csv")

print("\nTop 25 Most Important Features (Gradient Boosting):")
print("-" * 100)
print(feature_importance_gb.head(25).to_string(index=False))

# Model performance
train_score_gb = gb_model.score(X_train, y_train)
test_score_gb = gb_model.score(X_test, y_test)
print(f"\nGradient Boosting Performance:")
print(f"  Training Accuracy: {train_score_gb:.4f}")
print(f"  Test Accuracy: {test_score_gb:.4f}")

# ==================================================================================
# COMBINED FEATURE IMPORTANCE RANKING
# ==================================================================================
print("\n" + "="*100)
print("COMBINED FEATURE RANKING")
print("="*100)

# Normalize importance scores
feature_importance_rf['RF_Rank'] = feature_importance_rf['Importance'].rank(ascending=False)
feature_importance_gb['GB_Rank'] = feature_importance_gb['Importance'].rank(ascending=False)
df_correlation['Corr_Rank'] = df_correlation['Abs_Correlation'].rank(ascending=False)

# Merge all methods
combined = feature_importance_rf[['Variable', 'Importance']].rename(columns={'Importance': 'RF_Importance'})
combined = combined.merge(
    feature_importance_gb[['Variable', 'Importance']].rename(columns={'Importance': 'GB_Importance'}),
    on='Variable', how='outer'
)
combined = combined.merge(
    df_correlation[['Variable', 'Correlation', 'Abs_Correlation']],
    on='Variable', how='left'
)

# Calculate combined score (average of normalized ranks)
combined['RF_Importance_Norm'] = combined['RF_Importance'] / combined['RF_Importance'].max()
combined['GB_Importance_Norm'] = combined['GB_Importance'] / combined['GB_Importance'].max()
combined['Correlation_Norm'] = combined['Abs_Correlation'] / combined['Abs_Correlation'].max()

# Fill NaN with 0 for correlation
combined['Correlation_Norm'].fillna(0, inplace=True)
combined['Correlation'].fillna(0, inplace=True)
combined['Abs_Correlation'].fillna(0, inplace=True)

# Combined score (weighted average)
combined['Combined_Score'] = (
    0.35 * combined['RF_Importance_Norm'] +
    0.35 * combined['GB_Importance_Norm'] +
    0.30 * combined['Correlation_Norm']
)

combined = combined.sort_values('Combined_Score', ascending=False)

# Save
combined.to_csv('analysis_outputs/combined_feature_importance.csv', index=False)
print(f"\n[OK] Combined feature importance saved: analysis_outputs/combined_feature_importance.csv")

print("\nTop 30 Most Important Variables (Combined Ranking):")
print("-" * 100)
display_cols = ['Variable', 'Combined_Score', 'RF_Importance', 'GB_Importance', 'Correlation']
print(combined[display_cols].head(30).to_string(index=False))

print("\n" + "="*100)
print("FEATURE IMPORTANCE ANALYSIS COMPLETE")
print("="*100)

