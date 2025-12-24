# Agent-Level Comparison Analysis

## Overview
This folder contains scripts to perform comprehensive ML and statistical analysis comparing **TOP Agent** vs **WORST Agent** performance.

## Agent Configuration
- **TOP Agent**: DARWINSANCHEZ24
- **WORST Agent**: ARTURODELEON

## What This Does
Generates the **exact same analysis** as the main ML V2 pipeline, but filtered for specific agents:

### Analysis Steps:
1. **Preprocessing**: Filter calls for each agent from the long/short call datasets
2. **Correlation Analysis**: Spearman correlation matrices and heatmaps
3. **Feature Importance**: Random Forest + XGBoost models
4. **Statistical Tests**: T-tests, Mann-Whitney, Chi-square, effect sizes
5. **SHAP Analysis**: All SHAP visualizations (waterfall, summary, dependence, etc.)
6. **LIME Analysis**: LIME explanations and aggregated importance
7. **Visualizations**: Top 20 variables, section analysis, correlation vs importance, etc.
8. **Comparison Report**: Side-by-side comparison of both agents

### Visualizations Generated (per agent):
- `heatmap_02_short_calls.png`
- `heatmap_02_long_calls.png`
- `04_stat_effect_vs_pvalue.png`
- `lime_05b_aggregated_importance.png`
- `lime_05b_gb_individual_explanations.png`
- `lime_05b_rf_individual_explanations.png`
- `lime_05b_lime_vs_shap.png`
- `shap_05_rf_importance_bar.png`
- `shap_05_rf_summary_beeswarm.png`
- `shap_05_rf_waterfall.png`
- `shap_05_rf_dependence.png`
- `shap_05_xgb_importance_bar.png`
- `shap_05_xgb_summary_beeswarm.png`
- `shap_05_xgb_waterfall.png`
- `shap_05_xgb_dependence.png`
- `viz_06_top_20_variables.png`
- `viz_06_correlation_vs_importance.png`
- `viz_06_section_analysis.png`
- `viz_06_model_comparison.png`
- `viz_06_effect_sizes.png`

## Usage

### Quick Start (Run Complete Analysis):
```bash
python RUN_AGENT_COMPARISON_ANALYSIS.py
```

This will:
1. Run all 7 analysis steps for the TOP agent (DARWINSANCHEZ24)
2. Run all 7 analysis steps for the WORST agent (ARTURODELEON)
3. Generate a comparison report
4. Save all outputs to `analysis_outputs/top_agent/` and `analysis_outputs/worst_agent/`

### Run Individual Steps:
```bash
# For TOP agent
python 01_agent_preprocessing.py DARWINSANCHEZ24 top_agent
python 02_agent_correlation.py DARWINSANCHEZ24 top_agent
python 03_agent_feature_importance.py DARWINSANCHEZ24 top_agent
python 04_agent_statistical_tests.py DARWINSANCHEZ24 top_agent
python 05_agent_shap.py DARWINSANCHEZ24 top_agent
python 05b_agent_lime.py DARWINSANCHEZ24 top_agent
python 06_agent_visualizations.py DARWINSANCHEZ24 top_agent

# For WORST agent
python 01_agent_preprocessing.py ARTURODELEON worst_agent
python 02_agent_correlation.py ARTURODELEON worst_agent
python 03_agent_feature_importance.py ARTURODELEON worst_agent
python 04_agent_statistical_tests.py ARTURODELEON worst_agent
python 05_agent_shap.py ARTURODELEON worst_agent
python 05b_agent_lime.py ARTURODELEON worst_agent
python 06_agent_visualizations.py ARTURODELEON worst_agent

# Generate comparison report
python 07_comparison_report.py
```

## Output Structure
```
analysis_outputs/
├── top_agent/              # All outputs for DARWINSANCHEZ24
│   ├── 01_metadata.json
│   ├── 01_combined_original.csv
│   ├── 02_correlation_with_target.csv
│   ├── heatmap_02_short_calls.png
│   ├── heatmap_02_long_calls.png
│   ├── 03_importance_combined.csv
│   ├── 03_model_random_forest.pkl
│   ├── 03_model_xgboost.pkl
│   ├── 04_statistical_tests_combined.csv
│   ├── 04_stat_effect_vs_pvalue.png
│   ├── 05_shap_importance.csv
│   ├── shap_05_*.png (all SHAP visualizations)
│   ├── 05b_lime_importance.csv
│   ├── lime_05b_*.png (all LIME visualizations)
│   └── viz_06_*.png (all general visualizations)
│
├── worst_agent/            # All outputs for ARTURODELEON
│   └── (same structure as top_agent)
│
└── AGENT_COMPARISON_REPORT.txt  # Side-by-side comparison
```

## Requirements
- Python 3.7+
- All packages from ML V2 requirements:
  - pandas
  - numpy
  - scikit-learn
  - xgboost
  - shap
  - lime
  - matplotlib
  - seaborn
  - scipy
  - joblib

## Variables Analyzed
47 variables (excluding TO_OMC_User which is the agent identifier):
- Lead Quality (6 variables)
- Timings (3 variables)
- LGS Department (8 variables)
- Customer (7 variables)
- Technical Quality (2 variables)
- OMC Department (3 variables)
- OMC Engagement (3 variables)
- OMC Opening (5 variables)
- OMC Objections (6 variables)
- OMC Pace (1 variable)
- OMC Outcome (2 variables)

## Key Insights
After running the analysis, you can compare:
- Which variables are most important for each agent
- How correlations differ between top and worst performers
- Which agent's calls show stronger patterns
- Statistical significance of differences
- SHAP values showing feature impact differences
- LIME explanations for individual predictions

## Notes
- Analysis uses **Spearman correlation** (handles non-linear relationships)
- **SHAP** provides model-based feature importance
- **LIME** provides local explanations for individual predictions
- All visualizations match the style and format of the main ML V2 analysis
- Minimum sample size recommended: 30+ calls per agent for statistical significance

## Execution Time
Approximate time for complete analysis:
- Preprocessing: 10-30 seconds
- Correlation: 20-60 seconds
- Feature Importance: 1-3 minutes
- Statistical Tests: 30-90 seconds
- SHAP Analysis: 2-5 minutes
- LIME Analysis: 3-8 minutes
- Visualizations: 1-2 minutes

**Total**: ~10-20 minutes per agent (20-40 minutes for both agents)

## Troubleshooting
- If you get "No calls found for agent": Check the agent name spelling in TO_OMC_User column
- If analysis fails due to too few samples: Agent may not have enough calls for robust analysis
- If you get encoding errors: Scripts use UTF-8 encoding, ensure your terminal supports it
- For memory errors during SHAP/LIME: Reduce sample size in the respective scripts

## Generated By
Script generator: `generate_scripts.py`
- Automatically adapts ML V2 scripts for agent-level analysis
- Maintains identical methodology and output format
- Can be regenerated if ML V2 scripts are updated

---

**Ready to run!** Execute: `python RUN_AGENT_COMPARISON_ANALYSIS.py`

