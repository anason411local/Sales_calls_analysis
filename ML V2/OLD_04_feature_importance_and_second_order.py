"""
STEP 4-6: COMPREHENSIVE FEATURE IMPORTANCE & SECOND-ORDER ANALYSIS
Combines:
- Correlation analysis
- ML-based feature importance (Random Forest + Gradient Boosting)
- Second-order contribution analysis (binning for numeric, value analysis for categorical)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("="*100)
print("COMPREHENSIVE FEATURE IMPORTANCE & SECOND-ORDER ANALYSIS")
print("="*100)

# Load data
df_short = pd.read_csv('analysis_outputs/02_short_calls_encoded.csv')
df_long = pd.read_csv('analysis_outputs/02_long_calls_encoded.csv')
df_combined = pd.read_csv('analysis_outputs/02_combined_encoded.csv')
df_stats = pd.read_csv('analysis_outputs/03_statistical_analysis_all_features.csv')

print(f"\nData loaded: {df_combined.shape}")

# Prepare ML data
X = df_combined.drop('call_duration_group', axis=1)
y = (df_combined['call_duration_group'] == 'Long (>4.88 min)').astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

print(f"Training set: {X_train.shape[0]}, Test set: {X_test.shape[0]}")

# ==================================================================================
# RANDOM FOREST FEATURE IMPORTANCE
# ==================================================================================

print("\n" + "="*100)
print("RANDOM FOREST FEATURE IMPORTANCE")
print("="*100)

rf_model = RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_split=20,
                                  min_samples_leaf=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

rf_importance = pd.DataFrame({
    'Feature': X.columns,
    'RF_Importance': rf_model.feature_importances_
}).sort_values('RF_Importance', ascending=False)

train_acc = rf_model.score(X_train, y_train)
test_acc = rf_model.score(X_test, y_test)

print(f"\nRandom Forest Performance:")
print(f"  Training Accuracy: {train_acc:.4f}")
print(f"  Test Accuracy: {test_acc:.4f}")
print(f"  Overfitting Gap: {(train_acc - test_acc):.4f}")

rf_importance.to_csv('analysis_outputs/04_feature_importance_random_forest.csv', index=False)
print(f"\n[OK] Saved: 04_feature_importance_random_forest.csv")

# ==================================================================================
# GRADIENT BOOSTING FEATURE IMPORTANCE
# ==================================================================================

print("\n" + "="*100)
print("GRADIENT BOOSTING FEATURE IMPORTANCE")
print("="*100)

gb_model = GradientBoostingClassifier(n_estimators=150, max_depth=5, learning_rate=0.1,
                                      min_samples_split=20, min_samples_leaf=10, random_state=42)
gb_model.fit(X_train, y_train)

gb_importance = pd.DataFrame({
    'Feature': X.columns,
    'GB_Importance': gb_model.feature_importances_
}).sort_values('GB_Importance', ascending=False)

train_acc_gb = gb_model.score(X_train, y_train)
test_acc_gb = gb_model.score(X_test, y_test)

print(f"\nGradient Boosting Performance:")
print(f"  Training Accuracy: {train_acc_gb:.4f}")
print(f"  Test Accuracy: {test_acc_gb:.4f}")
print(f"  Overfitting Gap: {(train_acc_gb - test_acc_gb):.4f}")

gb_importance.to_csv('analysis_outputs/04_feature_importance_gradient_boosting.csv', index=False)
print(f"\n[OK] Saved: 04_feature_importance_gradient_boosting.csv")

# ==================================================================================
# COMBINED FEATURE RANKING
# ==================================================================================

print("\n" + "="*100)
print("COMBINED FEATURE RANKING (Stats + RF + GB)")
print("="*100)

# Merge all methods
combined = df_stats[['Feature', 'Correlation', 'Abs_Correlation', 'Cohens_D', 'P_Value']].copy()
combined = combined.merge(rf_importance, on='Feature', how='left')
combined = combined.merge(gb_importance, on='Feature', how='left')

# Normalize scores
combined['RF_Norm'] = combined['RF_Importance'] / combined['RF_Importance'].max()
combined['GB_Norm'] = combined['GB_Importance'] / combined['GB_Importance'].max()
combined['Corr_Norm'] = combined['Abs_Correlation'] / combined['Abs_Correlation'].max()
combined['Sig_Score'] = 1 - combined['P_Value']

# Combined score (weighted average)
combined['Final_Score'] = (
    0.25 * combined['RF_Norm'] +
    0.25 * combined['GB_Norm'] +
    0.25 * combined['Corr_Norm'] +
    0.25 * combined['Sig_Score']
)

combined = combined.sort_values('Final_Score', ascending=False)
combined.to_csv('analysis_outputs/04_combined_feature_ranking.csv', index=False)

print(f"\n[OK] Saved: 04_combined_feature_ranking.csv")
print("\nTop 30 Features by Combined Score:")
print(combined[['Feature', 'Final_Score', 'RF_Importance', 'GB_Importance', 'Correlation']].head(30).to_string(index=False))

# ==================================================================================
# SECOND-ORDER ANALYSIS: NUMERICAL BINNING
# ==================================================================================

print("\n" + "="*100)
print("SECOND-ORDER ANALYSIS: NUMERICAL BINNING")
print("="*100)

# Load original data for binning
df_short_orig = pd.read_csv('analysis_outputs/01_short_calls_data.csv')
df_long_orig = pd.read_csv('analysis_outputs/01_long_calls_data.csv')
df_comb_orig = pd.read_csv('analysis_outputs/01_combined_data.csv')

# Get top numeric features
top_numeric = combined[combined['Feature'].isin([
    'TO_OMC_Duration', 'total_discovery_questions', 'total_buying_signals',
    'objections_rebutted', 'total_objections', 'price_mentions_final_2min',
    'total_interruptions', 'objections_acknowledged', 'timeline_mentions_final_2min',
    'customer_talk_percentage', 'TO_length_in_sec', 'time_to_reason_seconds'
])]['Feature'].tolist()

binning_results = []

for var in top_numeric:
    if var not in df_comb_orig.columns:
        continue
    
    data = df_comb_orig[[var, 'call_duration_group']].dropna()
    
    if len(data) < 10:
        continue
    
    # Create quantile-based bins
    try:
        if data[var].nunique() <= 5:
            bins = sorted(data[var].unique())
            if len(bins) > 1:
                bins = [-np.inf] + list(bins) + [np.inf]
                data['bin'] = pd.cut(data[var], bins=bins, duplicates='drop')
        else:
            data['bin'] = pd.qcut(data[var], q=5, labels=False, duplicates='drop')
        
        # Analyze each bin
        for bin_val in data['bin'].unique():
            if pd.isna(bin_val):
                continue
            
            bin_data = data[data['bin'] == bin_val]
            count_short = (bin_data['call_duration_group'] == 'Short (<4.88 min)').sum()
            count_long = (bin_data['call_duration_group'] == 'Long (>4.88 min)').sum()
            total = len(bin_data)
            
            if total > 0:
                pct_long = (count_long / total) * 100
                binning_results.append({
                    'Variable': var,
                    'Bin': str(bin_val),
                    'Count_Short': count_short,
                    'Count_Long': count_long,
                    'Total': total,
                    'Pct_Long': pct_long,
                    'Importance_Score': abs(pct_long - 50),
                    'Direction': 'Favors Long' if pct_long > 50 else 'Favors Short'
                })
    except Exception as e:
        print(f"  Error binning {var}: {e}")
        continue

df_binning = pd.DataFrame(binning_results)
df_binning = df_binning.sort_values('Importance_Score', ascending=False)
df_binning.to_csv('analysis_outputs/05_numerical_binning_analysis.csv', index=False)

print(f"\n[OK] Saved: 05_numerical_binning_analysis.csv")
print("\nTop 20 Most Discriminative Bins:")
print(df_binning[['Variable', 'Bin', 'Count_Short', 'Count_Long', 'Pct_Long', 'Direction']].head(20).to_string(index=False))

# ==================================================================================
# SECOND-ORDER ANALYSIS: CATEGORICAL VALUE IMPORTANCE
# ==================================================================================

print("\n" + "="*100)
print("SECOND-ORDER ANALYSIS: CATEGORICAL VALUE IMPORTANCE")
print("="*100)

# Get top categorical features (target encoded)
top_categorical = combined[combined['Feature'].str.contains('_target_enc')].head(10)['Feature'].tolist()
top_categorical = [f.replace('_target_enc', '') for f in top_categorical]

categorical_value_results = []

for var in top_categorical:
    if var not in df_comb_orig.columns:
        continue
    
    # Get unique values
    unique_vals = df_comb_orig[var].unique()
    
    for val in unique_vals:
        if pd.isna(val):
            continue
        
        count_short = ((df_short_orig[var] == val) | (df_short_orig[var].isna() & pd.isna(val))).sum()
        count_long = ((df_long_orig[var] == val) | (df_long_orig[var].isna() & pd.isna(val))).sum()
        total = count_short + count_long
        
        if total > 0:
            pct_long = (count_long / total) * 100
            categorical_value_results.append({
                'Variable': var,
                'Value': str(val),
                'Count_Short': count_short,
                'Count_Long': count_long,
                'Total': total,
                'Pct_Long': pct_long,
                'Importance_Score': abs(pct_long - 50),
                'Direction': 'Favors Long' if pct_long > 50 else 'Favors Short'
            })

df_cat_values = pd.DataFrame(categorical_value_results)
df_cat_values = df_cat_values.sort_values('Importance_Score', ascending=False)
df_cat_values.to_csv('analysis_outputs/05_categorical_value_importance.csv', index=False)

print(f"\n[OK] Saved: 05_categorical_value_importance.csv")
print("\nTop 20 Most Discriminative Categorical Values:")
print(df_cat_values[['Variable', 'Value', 'Count_Short', 'Count_Long', 'Pct_Long', 'Direction']].head(20).to_string(index=False))

print("\n" + "="*100)
print("COMPREHENSIVE FEATURE IMPORTANCE & SECOND-ORDER ANALYSIS COMPLETE")
print("="*100)
print("\nKey ML Results:")
print(f"  Random Forest Test Accuracy: {test_acc:.4f}")
print(f"  Gradient Boosting Test Accuracy: {test_acc_gb:.4f}")
print(f"\nTop 3 Features:")
for idx, row in combined.head(3).iterrows():
    print(f"  {idx+1}. {row['Feature']}: Score={row['Final_Score']:.4f}, r={row['Correlation']:.3f}")

