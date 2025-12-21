# Sales Call Duration Analysis V2

## Overview
This folder contains a completely rebuilt analysis pipeline focused on understanding **why not all OMC calls last longer than 4.88 minutes**.

## Research Question
**What variables and their contributions (including second-order effects) determine whether an OMC call extends beyond 4.88 minutes?**

## Selected Variables (49 total)

### Section 1: Lead Quality (6 variables)
- LQ_Company_Name, LQ_Company_Address, LQ_Service, LQ_Customer_Name
- Calls Count, Connection Made Calls

### Section 2: Timings (4 variables)
- TO_Event_O, timezone, season_status, season_month

### Section 3: LGS Department (8 variables)
- TO_User_M, lgs_sentiment_style, lgs_agent_gender, TO_length_in_sec
- is_decision_maker, ready_for_customers, forbidden_industry, ready_to_transfer

### Section 4: Customer (7 variables)
- customer_sentiment_lgs, customer_sentiment_omc, customer_language
- customer_knows_marketing, customer_availability, who_said_hello_first_lgs
- customer_marketing_experience

### Section 5: Technical Quality (2 variables)
- technical_quality_score, technical_quality_issues

### Section 6.1: OMC Department (5 variables)
- TO_OMC_User, TO_OMC_Disposiion, TO_OMC_Duration
- omc_agent_sentiment_style, omc_who_said_hello_first

### Section 6.2: OMC Customer Engagement (3 variables)
- customer_talk_percentage, total_discovery_questions, total_buying_signals

### Section 6.3: OMC Call Opening (5 variables)
- time_to_reason_seconds, location_mentioned, business_type_mentioned
- within_45_seconds, call_structure_framed

### Section 6.4: OMC Objections (6 variables)
- total_objections, objections_acknowledged, price_mentions_final_2min
- timeline_mentions_final_2min, contract_mentions_final_2min, objections_rebutted

### Section 6.5: Pace & Control (1 variable)
- total_interruptions

### Section 6.6: Outcome (2 variables)
- commitment_type, call_result_tag

## Analysis Pipeline

### Step 1: Data Exploration & Preprocessing
**Script:** `01_data_exploration_and_preprocessing.py`
- Loads and filters data to selected 49 variables
- Analyzes distributions, missing values, and unique value counts
- Identifies encoding requirements based on cardinality
- **Output:** Filtered datasets, column analysis summaries

### Step 2: Intelligent Encoding
**Script:** `02_intelligent_encoding_and_preprocessing.py`
- **Low Cardinality (2-10 values):** One-Hot Encoding
- **Medium Cardinality (11-50 values):** Target + Frequency Encoding
- **High Cardinality (>50 values):** Target Encoding with rare category grouping
- **Missing Values:** Imputation + indicator variables
- **Result:** 49 variables expanded to 150 features

### Step 3: Statistical Analysis
**Script:** `03_comprehensive_statistical_analysis.py`
- T-tests / Mann-Whitney U tests for all features
- Point-biserial correlation analysis
- Effect size calculations (Cohen's D)
- Section-wise analysis
- **Output:** Statistical significance rankings, p-values, effect sizes

### Step 4: Feature Importance & Second-Order Analysis
**Script:** `04_feature_importance_and_second_order.py`
- **Random Forest:** Feature importance scores (98.09% accuracy)
- **Gradient Boosting:** Feature importance scores (99.73% accuracy)
- **Second-Order Numeric:** Binning analysis to identify critical value ranges
- **Second-Order Categorical:** Value-level importance for categorical variables
- **Output:** Combined rankings, binning results, categorical value importance

### Step 5: Visualizations
**Script:** `06_create_visualizations.py`
- Top 20 features visualization
- Section analysis comparison
- Numerical binning charts
- Categorical value importance
- Feature type comparison
- **Output:** 5 high-quality PNG visualizations

### Step 6: Comprehensive Report
**Script:** `07_generate_comprehensive_report.py`
- Executive summary
- Top features with detailed statistics
- Section-by-section analysis
- Second-order findings
- Actionable recommendations
- **Output:** COMPREHENSIVE_ANALYSIS_REPORT_V2.txt

## How to Run

### Option 1: Run Complete Pipeline
```bash
python RUN_COMPLETE_ANALYSIS_V2.py
```
This executes all 6 scripts in sequence and generates all outputs.

### Option 2: Run Individual Scripts
```bash
python 01_data_exploration_and_preprocessing.py
python 02_intelligent_encoding_and_preprocessing.py
python 03_comprehensive_statistical_analysis.py
python 04_feature_importance_and_second_order.py
python 06_create_visualizations.py
python 07_generate_comprehensive_report.py
```

## Key Findings

### Top 5 Most Important Features
1. **TO_OMC_Duration** (r=0.640) - Direct call duration measure
2. **total_discovery_questions** (r=0.561) - # of discovery questions asked
3. **call_result_tag** (r=0.560) - Outcome classification
4. **TO_OMC_Disposiion** (r=0.422) - Call disposition
5. **total_buying_signals** (r=0.404) - # of buying signals identified

### Most Important Variable Sections
1. **OMC Outcome** (avg |r|=0.313)
2. **OMC Engagement** (avg |r|=0.212)
3. **OMC Pace** (avg |r|=0.170)
4. **OMC Objections** (avg |r|=0.157)
5. **OMC Department** (avg |r|=0.157)

### Critical Success Factors
- **Discovery Questions:** 8+ questions strongly predict longer calls
- **Buying Signals:** Identifying 2+ signals increases call length significantly
- **Objection Handling:** Rebutting objections extends duration
- **Call Structure:** Proper opening/framing correlates with longer calls
- **Customer Engagement:** Higher customer talk percentage in long calls

## Output Files

### CSV Files (Data)
- `01_column_analysis_summary.csv` - Column-level statistics
- `01_categorical_distributions.csv` - Categorical value distributions
- `01_numeric_distributions.csv` - Numeric variable statistics
- `02_short_calls_encoded.csv` - Encoded short calls data
- `02_long_calls_encoded.csv` - Encoded long calls data
- `02_combined_encoded.csv` - Combined encoded dataset
- `03_statistical_analysis_all_features.csv` - Full statistical results
- `03_top_50_features.csv` - Top 50 features by combined score
- `03_section_analysis.csv` - Analysis by variable section
- `04_feature_importance_random_forest.csv` - RF importance scores
- `04_feature_importance_gradient_boosting.csv` - GB importance scores
- `04_combined_feature_ranking.csv` - **MAIN RANKING FILE**
- `05_numerical_binning_analysis.csv` - Second-order numeric analysis
- `05_categorical_value_importance.csv` - Second-order categorical analysis

### Visualizations (PNG)
- `viz_01_top_20_features.png` - Top features bar chart
- `viz_02_section_analysis.png` - Section comparison
- `viz_03_numerical_binning.png` - Binning analysis charts
- `viz_04_categorical_values.png` - Categorical importance
- `viz_05_feature_type_comparison.png` - Encoding method comparison

### Reports (TXT)
- `COMPREHENSIVE_ANALYSIS_REPORT_V2.txt` - **MAIN REPORT**

### Metadata (JSON)
- `02_encoding_info.json` - Encoding strategy details
- `key_metrics_summary.json` - Key metrics at a glance

## Technical Details

### Data Statistics
- **Total Calls:** 1,218 (609 short + 609 long)
- **Original Variables:** 49
- **Encoded Features:** 150
- **Feature Expansion:** 3.06x

### Machine Learning Performance
- **Random Forest:** 98.09% test accuracy (minimal overfitting)
- **Gradient Boosting:** 99.73% test accuracy (excellent generalization)

### Statistical Significance
- **67 features** (44.7%) show significant differences (p<0.05)
- **44 features** (29.3%) highly significant (p<0.001)
- **5 features** with large effect sizes (|d|>0.8)
- **12 features** with strong correlations (|r|>0.3)

## Requirements
- Python 3.7+
- pandas
- numpy
- scipy
- scikit-learn
- matplotlib
- seaborn

## Notes
- All categorical variables properly encoded for correlation analysis
- Second-order analysis reveals which specific value ranges matter most
- Focus on actionable insights for call duration improvement
- No markdown files created (per user request)

