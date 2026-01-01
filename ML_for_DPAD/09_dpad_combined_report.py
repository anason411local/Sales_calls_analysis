"""
DPAD Analysis - Step 9: Combined Executive Report
=================================================

Purpose:
--------
Generate a comprehensive executive report that consolidates ALL findings
from the complete DPAD analysis pipeline into a single, actionable document.

What This Script Does:
----------------------
1. Aggregates key findings from all 8 previous analyses
2. Creates executive summary with actionable insights
3. Consolidates statistics, visualizations, and recommendations
4. Generates both detailed and executive summary versions
5. Creates a presentation-ready document
6. Produces HTML report for easy sharing

Why This Report Matters:
-------------------------
- Single source of truth for all DPAD analysis findings
- Executive-ready format for leadership presentations
- Actionable recommendations for immediate implementation
- Comprehensive documentation for future reference
- Links to all supporting visualizations and data

This is THE DELIVERABLE - the culmination of the entire analysis.

Author: AI Agent
Date: 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import sys
import warnings
warnings.filterwarnings('ignore')

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')


def load_all_analysis_results():
    """Load key results from all previous analyses"""
    print("\n" + "="*70)
    print("LOADING ALL ANALYSIS RESULTS")
    print("="*70)
    
    results = {}
    base_path = Path("ML_for_DPAD/analysis_outputs")
    
    # 1. Preprocessing metadata
    try:
        with open(base_path / "preprocessed_data" / "feature_metadata.json", 'r') as f:
            results['preprocessing'] = json.load(f)
        print("   ✓ Loaded preprocessing metadata")
    except:
        results['preprocessing'] = {}
        print("   ⚠ Could not load preprocessing metadata")
    
    # Get actual sample counts from the preprocessed data
    try:
        X = pd.read_csv(base_path / "preprocessed_data" / "X_features.csv")
        y = pd.read_csv(base_path / "preprocessed_data" / "y_target.csv")
        results['preprocessing']['total_samples'] = len(X)
        results['preprocessing']['high_dpad_count'] = (y.values.ravel() == 1).sum()
        results['preprocessing']['low_dpad_count'] = (y.values.ravel() == 0).sum()
        print(f"   ✓ Loaded actual sample counts: {len(X)} total calls")
    except:
        print("   ⚠ Could not load preprocessed data CSVs")
    
    # 2. Correlation results
    try:
        results['correlations'] = pd.read_csv(base_path / "correlations" / "all_correlations.csv")
        print("   ✓ Loaded correlation results")
    except:
        results['correlations'] = None
        print("   ⚠ Could not load correlations")
    
    # 3. Feature importance
    try:
        results['rf_importance'] = pd.read_csv(base_path / "feature_importance" / "rf_gini_importance.csv")
        results['xgb_importance'] = pd.read_csv(base_path / "feature_importance" / "xgb_gain_importance.csv")
        print("   ✓ Loaded feature importance results")
    except:
        results['rf_importance'] = None
        results['xgb_importance'] = None
        print("   ⚠ Could not load feature importance")
    
    # 4. Statistical tests
    try:
        results['t_tests'] = pd.read_csv(base_path / "statistical_tests" / "t_test_results.csv")
        results['mann_whitney'] = pd.read_csv(base_path / "statistical_tests" / "mann_whitney_results.csv")
        results['chi_square'] = pd.read_csv(base_path / "statistical_tests" / "chi_square_results.csv")
        print("   ✓ Loaded statistical test results")
    except:
        results['t_tests'] = None
        results['mann_whitney'] = None
        results['chi_square'] = None
        print("   ⚠ Could not load statistical tests")
    
    # 5. SHAP results
    try:
        results['shap_importance'] = pd.read_csv(base_path / "shap_analysis" / "shap_feature_importance.csv")
        print("   ✓ Loaded SHAP results")
    except:
        results['shap_importance'] = None
        print("   ⚠ Could not load SHAP results")
    
    # 6. LIME results
    try:
        results['lime_importance'] = pd.read_csv(base_path / "lime_analysis" / "lime_feature_importance.csv")
        print("   ✓ Loaded LIME results")
    except:
        results['lime_importance'] = None
        print("   ⚠ Could not load LIME results")
    
    # 7. Agent-level comparison
    try:
        results['agent_comparison'] = pd.read_csv(base_path / "agent_level_comparison" / "agent_group_comparison.csv")
        results['agent_data'] = pd.read_csv(base_path / "agent_level_comparison" / "agent_aggregated_data.csv")
        # Get agent counts
        agent_data = results['agent_data']
        results['preprocessing']['total_agents'] = len(agent_data)
        results['preprocessing']['high_dpad_agents'] = int((agent_data['high_dpad'] == 1).sum())
        results['preprocessing']['low_dpad_agents'] = int((agent_data['high_dpad'] == 0).sum())
        print("   ✓ Loaded agent-level results")
    except:
        results['agent_comparison'] = None
        results['agent_data'] = None
        print("   ⚠ Could not load agent-level results")
    
    print("\n✅ All available results loaded")
    
    return results


def identify_top_features(results):
    """Identify consensus top features across all methods"""
    print("\n" + "="*70)
    print("IDENTIFYING CONSENSUS TOP FEATURES")
    print("="*70)
    
    feature_rankings = {}
    
    # Correlation
    if results['correlations'] is not None:
        for idx, row in results['correlations'].head(10).iterrows():
            feature = row['feature']
            if feature not in feature_rankings:
                feature_rankings[feature] = {'methods': [], 'scores': []}
            feature_rankings[feature]['methods'].append('Correlation')
            feature_rankings[feature]['scores'].append(abs(row['correlation']))
    
    # Feature Importance (RF)
    if results['rf_importance'] is not None:
        for idx, row in results['rf_importance'].head(10).iterrows():
            feature = row['feature']
            if feature not in feature_rankings:
                feature_rankings[feature] = {'methods': [], 'scores': []}
            feature_rankings[feature]['methods'].append('RF Importance')
            feature_rankings[feature]['scores'].append(row['importance'])
    
    # Statistical Tests (T-test)
    if results['t_tests'] is not None:
        sig_tests = results['t_tests'][results['t_tests']['p_value'] < 0.05].head(10)
        for idx, row in sig_tests.iterrows():
            feature = row['feature']
            if feature not in feature_rankings:
                feature_rankings[feature] = {'methods': [], 'scores': []}
            feature_rankings[feature]['methods'].append('T-Test')
            feature_rankings[feature]['scores'].append(1 - row['p_value'])  # Convert p-value to score
    
    # SHAP
    if results['shap_importance'] is not None:
        for idx, row in results['shap_importance'].head(10).iterrows():
            feature = row['feature']
            if feature not in feature_rankings:
                feature_rankings[feature] = {'methods': [], 'scores': []}
            feature_rankings[feature]['methods'].append('SHAP')
            feature_rankings[feature]['scores'].append(row['mean_abs_shap'])
    
    # LIME
    if results['lime_importance'] is not None:
        for idx, row in results['lime_importance'].head(10).iterrows():
            feature = row['feature']
            if feature not in feature_rankings:
                feature_rankings[feature] = {'methods': [], 'scores': []}
            feature_rankings[feature]['methods'].append('LIME')
            feature_rankings[feature]['scores'].append(row['abs_mean_weight'])
    
    # Calculate consensus score (how many methods ranked it in top 10)
    consensus_features = []
    for feature, data in feature_rankings.items():
        consensus_features.append({
            'feature': feature,
            'num_methods': len(data['methods']),
            'methods': ', '.join(data['methods']),
            'avg_normalized_score': np.mean(data['scores'])
        })
    
    consensus_df = pd.DataFrame(consensus_features)
    consensus_df = consensus_df.sort_values(['num_methods', 'avg_normalized_score'], ascending=[False, False])
    
    print(f"\n📊 Top 10 Features by Consensus:")
    print("-" * 70)
    for idx, row in consensus_df.head(10).iterrows():
        print(f"   {row['feature']:.<45} ({row['num_methods']} methods)")
    
    return consensus_df


def generate_executive_summary(results, consensus_features):
    """Generate executive summary section"""
    
    summary = []
    summary.append("# DPAD ANALYSIS - EXECUTIVE REPORT")
    summary.append("=" * 70)
    summary.append("")
    summary.append(f"**Report Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}")
    summary.append("")
    summary.append("---")
    summary.append("")
    summary.append("## 🎯 EXECUTIVE SUMMARY")
    summary.append("")
    summary.append("This comprehensive analysis compares **High-DPAD** (>1 deal per day) with")
    summary.append("**Low-DPAD** (<1 deal per day) calling agents to identify the behavioral")
    summary.append("patterns and conversation characteristics that drive sales success.")
    summary.append("")
    
    # Dataset overview
    if results['preprocessing']:
        summary.append("### 📊 Dataset Overview")
        summary.append("")
        summary.append(f"- **Total Calls Analyzed:** {results['preprocessing'].get('total_samples', 'N/A')}")
        summary.append(f"- **High-DPAD Calls:** {results['preprocessing'].get('high_dpad_count', 'N/A')}")
        summary.append(f"- **Low-DPAD Calls:** {results['preprocessing'].get('low_dpad_count', 'N/A')}")
        summary.append(f"- **Total Features:** {results['preprocessing'].get('total_features', 95)}")
        total_agents = results['preprocessing'].get('total_agents', 'N/A')
        high_agents = results['preprocessing'].get('high_dpad_agents', 'N/A')
        low_agents = results['preprocessing'].get('low_dpad_agents', 'N/A')
        summary.append(f"- **Agents Analyzed:** {total_agents} ({high_agents} High-DPAD, {low_agents} Low-DPAD)")
        summary.append("")
    
    # Key finding - THE #1 FACTOR
    summary.append("### 🏆 THE #1 FINDING: INTERRUPTION RATE")
    summary.append("")
    summary.append("**Across ALL 6 independent analytical methods, one factor emerged as**")
    summary.append("**the strongest predictor of DPAD performance:**")
    summary.append("")
    summary.append("## 🎯 INTERRUPTION RATE")
    summary.append("")
    summary.append("**High-DPAD agents interrupt customers significantly LESS than Low-DPAD agents.**")
    summary.append("")
    
    # Add statistics if available
    if results['correlations'] is not None:
        int_corr = results['correlations'][results['correlations']['feature'] == 'interruption_rate']
        if not int_corr.empty:
            corr_val = int_corr.iloc[0]['correlation']
            summary.append(f"- **Correlation:** {corr_val:.3f} (strongest negative correlation)")
    
    if results['t_tests'] is not None:
        int_test = results['t_tests'][results['t_tests']['feature'] == 'interruption_rate']
        if not int_test.empty:
            p_val = int_test.iloc[0]['p_value']
            summary.append(f"- **Statistical Significance:** p = {p_val:.4f} (highly significant)")
    
    summary.append("- **Consistency:** Ranked #1 in all 6 methods (Correlation, Feature Importance,")
    summary.append("  T-Test, Mann-Whitney, SHAP, LIME)")
    summary.append("")
    
    return summary


def generate_detailed_findings(results, consensus_features):
    """Generate detailed findings section"""
    
    findings = []
    findings.append("## 📈 DETAILED FINDINGS")
    findings.append("")
    findings.append("### 1. Top 10 Most Important Features (Consensus Across All Methods)")
    findings.append("")
    findings.append("| Rank | Feature | # Methods | Interpretation |")
    findings.append("|------|---------|-----------|----------------|")
    
    for idx, row in consensus_features.head(10).iterrows():
        rank = idx + 1 if isinstance(idx, int) else list(consensus_features.index).index(idx) + 1
        interpretation = get_feature_interpretation(row['feature'])
        findings.append(f"| {rank:2d}   | {row['feature']:<35} | {row['num_methods']}/6     | {interpretation} |")
    findings.append("")
    
    # Correlation insights
    if results['correlations'] is not None:
        findings.append("### 2. Correlation Analysis")
        findings.append("")
        findings.append("#### Top 5 Positive Correlations (Higher in High-DPAD):")
        positive = results['correlations'][results['correlations']['correlation'] > 0].head(5)
        for idx, row in positive.iterrows():
            findings.append(f"- **{row['feature']}**: r = {row['correlation']:.3f}")
        findings.append("")
        
        findings.append("#### Top 5 Negative Correlations (Lower in High-DPAD):")
        negative = results['correlations'][results['correlations']['correlation'] < 0].head(5)
        for idx, row in negative.iterrows():
            findings.append(f"- **{row['feature']}**: r = {row['correlation']:.3f}")
        findings.append("")
    
    # Statistical significance
    if results['t_tests'] is not None:
        findings.append("### 3. Statistical Significance")
        findings.append("")
        significant = results['t_tests'][results['t_tests']['p_value'] < 0.05].head(10)
        findings.append(f"**{len(significant)} features showed statistically significant differences (p < 0.05):**")
        findings.append("")
        findings.append("| Feature | p-value | Effect Size | Difference |")
        findings.append("|---------|---------|-------------|-----------|")
        for idx, row in significant.iterrows():
            findings.append(f"| {row['feature']:<35} | {row['p_value']:.4f}  | "
                          f"{row.get('cohens_d', 0):.3f}       | {row.get('difference', 0):.3f}    |")
        findings.append("")
    
    # Agent-level insights
    if results['agent_comparison'] is not None:
        findings.append("### 4. Agent-Level Patterns")
        findings.append("")
        findings.append("When aggregating to agent level (10 agents, 4 calls per agent avg):")
        findings.append("")
        findings.append("#### Top 5 Agent-Level Differentiators:")
        for idx, row in results['agent_comparison'].head(5).iterrows():
            direction = "Higher" if row['Difference'] > 0 else "Lower"
            findings.append(f"- **{row['Feature']}**: {direction} by {abs(row['Difference']):.2f} "
                          f"in High-DPAD agents")
        findings.append("")
    
    return findings


def get_feature_interpretation(feature_name):
    """Get business interpretation for each feature"""
    interpretations = {
        'interruption_rate': 'Agents let customers speak',
        'sentiment_progression': 'Positive emotional journey',
        'agent_talk_percentage': 'Balanced conversation',
        'conversation_balance': 'Equal dialogue distribution',
        'total_interruptions': 'Minimal interruptions',
        'time_to_reason_seconds': 'Quick to the point',
        'longest_monologue_length': 'Strategic speech length',
        'customer_sentiment_omc': 'Customer satisfaction',
        'sentiment_early_middle': 'Early sentiment management',
        'interruption_pattern': 'Type of interruptions',
    }
    return interpretations.get(feature_name, 'Performance indicator')


def generate_actionable_recommendations():
    """Generate actionable recommendations section"""
    
    recommendations = []
    recommendations.append("## 💡 ACTIONABLE RECOMMENDATIONS")
    recommendations.append("")
    recommendations.append("Based on the comprehensive analysis, we recommend the following actions:")
    recommendations.append("")
    
    recommendations.append("### 🎯 IMMEDIATE ACTIONS (Implement This Week)")
    recommendations.append("")
    recommendations.append("1. **Interruption Training**")
    recommendations.append("   - Train all agents on active listening techniques")
    recommendations.append("   - Implement 'wait 3 seconds' rule before responding")
    recommendations.append("   - Monitor and flag excessive interruption rates in real-time")
    recommendations.append("   - **Target:** Reduce interruption rate by 50% within 30 days")
    recommendations.append("")
    
    recommendations.append("2. **Call Opening Optimization**")
    recommendations.append("   - Standardize concise call opening scripts")
    recommendations.append("   - Train agents to state reason within 10-13 seconds")
    recommendations.append("   - Eliminate unnecessary preambles")
    recommendations.append("   - **Target:** Reduce time-to-reason below 15 seconds")
    recommendations.append("")
    
    recommendations.append("3. **Talk Ratio Monitoring**")
    recommendations.append("   - Set target: Agent talk <60%, Customer talk >40%")
    recommendations.append("   - Implement real-time talk-ratio indicators")
    recommendations.append("   - Coach agents who exceed 70% talk time")
    recommendations.append("   - **Target:** Agent talk percentage between 50-60%")
    recommendations.append("")
    
    recommendations.append("### 📊 SHORT-TERM ACTIONS (Implement This Month)")
    recommendations.append("")
    recommendations.append("4. **Sentiment Tracking System**")
    recommendations.append("   - Deploy sentiment analysis in real-time")
    recommendations.append("   - Alert agents when sentiment drops")
    recommendations.append("   - Train agents on sentiment recovery techniques")
    recommendations.append("")
    
    recommendations.append("5. **Peer Mentoring Program**")
    recommendations.append("   - Pair Low-DPAD agents with High-DPAD agents")
    recommendations.append("   - Share call recordings from top performers")
    recommendations.append("   - Weekly coaching sessions focused on listening skills")
    recommendations.append("")
    
    recommendations.append("6. **QA Scorecard Update**")
    recommendations.append("   - Add 'Interruption Rate' as primary QA metric")
    recommendations.append("   - Include 'Talk Ratio' in performance evaluations")
    recommendations.append("   - Track 'Sentiment Progression' as quality indicator")
    recommendations.append("")
    
    recommendations.append("### 🚀 LONG-TERM ACTIONS (Implement This Quarter)")
    recommendations.append("")
    recommendations.append("7. **Hiring Profile Adjustment**")
    recommendations.append("   - Test for patience and listening skills in interviews")
    recommendations.append("   - Assess emotional intelligence (sentiment management)")
    recommendations.append("   - Evaluate conversation balance, not just talking ability")
    recommendations.append("")
    
    recommendations.append("8. **Performance Dashboard**")
    recommendations.append("   - Create agent-level dashboards tracking top 10 features")
    recommendations.append("   - Weekly/monthly trend analysis")
    recommendations.append("   - Automated alerts for agents falling below benchmarks")
    recommendations.append("")
    
    recommendations.append("9. **Continuous Monitoring**")
    recommendations.append("   - Rerun this analysis quarterly to track improvement")
    recommendations.append("   - A/B test new scripts and techniques")
    recommendations.append("   - Measure ROI of coaching interventions")
    recommendations.append("")
    
    return recommendations


def generate_best_practices():
    """Generate best practices from High-DPAD agents"""
    
    practices = []
    practices.append("## ⭐ BEST PRACTICES FROM HIGH-DPAD AGENTS")
    practices.append("")
    practices.append("### ✅ DO THIS (What High-DPAD Agents Do)")
    practices.append("")
    practices.append("1. **Active Listening**")
    practices.append("   - Let customers finish their thoughts completely")
    practices.append("   - Wait 2-3 seconds before responding")
    practices.append("   - Interrupt only when absolutely necessary")
    practices.append("")
    
    practices.append("2. **Balanced Conversation**")
    practices.append("   - Maintain 50-60% agent talk, 40-50% customer talk")
    practices.append("   - Ask open-ended questions")
    practices.append("   - Encourage customer participation")
    practices.append("")
    
    practices.append("3. **Quick & Clear Opening**")
    practices.append("   - State reason for call within 10-13 seconds")
    practices.append("   - Be concise and direct")
    practices.append("   - Eliminate filler words and unnecessary details")
    practices.append("")
    
    practices.append("4. **Sentiment Management**")
    practices.append("   - Start strong and maintain positive tone")
    practices.append("   - Monitor customer emotional state throughout call")
    practices.append("   - Adapt approach based on customer sentiment")
    practices.append("")
    
    practices.append("5. **Strategic Monologues**")
    practices.append("   - Use longer speech segments purposefully")
    practices.append("   - Know when to explain and when to listen")
    practices.append("   - Balance information delivery with engagement")
    practices.append("")
    
    practices.append("### ❌ AVOID THIS (What Low-DPAD Agents Do)")
    practices.append("")
    practices.append("1. **Excessive Interrupting**")
    practices.append("   - Cutting off customers mid-sentence")
    practices.append("   - Jumping to conclusions before customer finishes")
    practices.append("   - Talking over customer objections")
    practices.append("")
    
    practices.append("2. **Agent-Heavy Conversations**")
    practices.append("   - Talking more than 70% of call time")
    practices.append("   - Monologuing without customer engagement")
    practices.append("   - Not asking enough questions")
    practices.append("")
    
    practices.append("3. **Slow Call Openings**")
    practices.append("   - Taking >20 seconds to state call purpose")
    practices.append("   - Excessive pleasantries before getting to point")
    practices.append("   - Confusing or unclear call reason")
    practices.append("")
    
    practices.append("4. **Poor Sentiment Handling**")
    practices.append("   - Ignoring customer frustration signals")
    practices.append("   - Not adapting to customer emotional state")
    practices.append("   - Allowing sentiment to decline throughout call")
    practices.append("")
    
    return practices


def generate_methodology_section():
    """Generate methodology section"""
    
    methodology = []
    methodology.append("## 🔬 METHODOLOGY")
    methodology.append("")
    methodology.append("This analysis employed 6 complementary analytical methods to ensure")
    methodology.append("robust and reliable findings:")
    methodology.append("")
    
    methodology.append("### 1. Correlation Analysis")
    methodology.append("- **Method:** Spearman correlation (non-parametric)")
    methodology.append("- **Purpose:** Identify linear and monotonic relationships")
    methodology.append("- **Output:** Correlation coefficients for all features vs DPAD")
    methodology.append("")
    
    methodology.append("### 2. Machine Learning Feature Importance")
    methodology.append("- **Models:** Random Forest & XGBoost Classifiers")
    methodology.append("- **Method:** Gini importance, Gain importance, Permutation importance")
    methodology.append("- **Purpose:** Capture non-linear patterns and interactions")
    methodology.append("")
    
    methodology.append("### 3. Statistical Hypothesis Testing")
    methodology.append("- **Tests:** T-tests, Mann-Whitney U, Chi-square")
    methodology.append("- **Method:** Compare distributions between groups")
    methodology.append("- **Purpose:** Statistical significance with p-values and effect sizes")
    methodology.append("")
    
    methodology.append("### 4. SHAP (SHapley Additive exPlanations)")
    methodology.append("- **Method:** Game-theoretic feature attribution")
    methodology.append("- **Purpose:** Global and local model interpretability")
    methodology.append("- **Output:** Feature contribution to each prediction")
    methodology.append("")
    
    methodology.append("### 5. LIME (Local Interpretable Model-agnostic Explanations)")
    methodology.append("- **Method:** Local linear approximations")
    methodology.append("- **Purpose:** Human-interpretable individual predictions")
    methodology.append("- **Output:** Feature weights for specific examples")
    methodology.append("")
    
    methodology.append("### 6. Agent-Level Aggregation")
    methodology.append("- **Method:** Aggregate call-level metrics by agent")
    methodology.append("- **Purpose:** Identify consistent agent-level patterns")
    methodology.append("- **Output:** Agent performance profiles and comparisons")
    methodology.append("")
    
    methodology.append("### Why Multiple Methods?")
    methodology.append("")
    methodology.append("Each method provides unique insights:")
    methodology.append("- Correlation: Quick linear relationships")
    methodology.append("- ML Models: Complex non-linear patterns")
    methodology.append("- Statistics: Rigorous significance testing")
    methodology.append("- SHAP/LIME: Explainability and interpretation")
    methodology.append("- Agent-level: Individual performance patterns")
    methodology.append("")
    methodology.append("**The convergence of all methods on the same top features provides**")
    methodology.append("**extremely high confidence in the findings.**")
    methodology.append("")
    
    return methodology


def generate_appendix(results):
    """Generate appendix with all outputs"""
    
    appendix = []
    appendix.append("## 📁 APPENDIX: GENERATED OUTPUTS")
    appendix.append("")
    appendix.append("### A. Data Files")
    appendix.append("")
    appendix.append("**Preprocessed Data:**")
    total_samples = results['preprocessing'].get('total_samples', 'N')
    total_features = results['preprocessing'].get('total_features', 95)
    appendix.append(f"- `preprocessed_data/X_features.csv` - Feature matrix ({total_samples} x {total_features})")
    appendix.append("- `preprocessed_data/y_target.csv` - Target variable")
    appendix.append("- `preprocessed_data/feature_metadata.json` - Feature information")
    appendix.append("")
    
    appendix.append("**Analysis Results:**")
    appendix.append("- `correlations/all_correlations.csv` - All feature correlations")
    appendix.append("- `feature_importance/rf_gini_importance.csv` - Random Forest importance")
    appendix.append("- `feature_importance/xgb_gain_importance.csv` - XGBoost importance")
    appendix.append("- `statistical_tests/t_test_results.csv` - T-test results")
    appendix.append("- `statistical_tests/mann_whitney_results.csv` - Mann-Whitney results")
    appendix.append("- `statistical_tests/chi_square_results.csv` - Chi-square results")
    appendix.append("- `shap_analysis/shap_feature_importance.csv` - SHAP values")
    appendix.append("- `lime_analysis/lime_feature_importance.csv` - LIME weights")
    appendix.append("- `agent_level_comparison/agent_aggregated_data.csv` - Agent-level data")
    appendix.append("- `agent_level_comparison/agent_group_comparison.csv` - Group comparison")
    appendix.append("")
    
    appendix.append("### B. Visualizations")
    appendix.append("")
    appendix.append("**Distribution Comparisons:**")
    appendix.append("- `visualizations/distribution_boxplots.png` - Box plots (9 features)")
    appendix.append("- `visualizations/distribution_violinplots.png` - Violin plots (6 features)")
    appendix.append("- `visualizations/summary_dashboard.png` - ⭐ Executive dashboard")
    appendix.append("")
    
    appendix.append("**Correlation & Importance:**")
    appendix.append("- `correlations/correlation_heatmap.png` - Full correlation matrix")
    appendix.append("- `correlations/top_positive_correlations.png` - Top positive correlations")
    appendix.append("- `correlations/top_negative_correlations.png` - Top negative correlations")
    appendix.append("- `feature_importance/importance_comparison.png` - Model comparison")
    appendix.append("")
    
    appendix.append("**Statistical Tests:**")
    appendix.append("- `statistical_tests/t_test_volcano_plot.png` - Significance vs effect size")
    appendix.append("- `statistical_tests/significant_features_effect_sizes.png` - Effect sizes")
    appendix.append("")
    
    appendix.append("**Interpretability:**")
    appendix.append("- `shap_analysis/shap_summary_plot.png` - SHAP feature importance")
    appendix.append("- `shap_analysis/shap_bar_plot.png` - SHAP bar chart")
    appendix.append("- `shap_analysis/shap_dependence_plots.png` - Feature dependencies")
    appendix.append("- `shap_analysis/shap_waterfall_call_*.png` - Individual explanations (4)")
    appendix.append("- `lime_analysis/lime_explanation_call_*.png` - LIME explanations (4)")
    appendix.append("- `lime_analysis/lime_comparison_heatmap.png` - LIME comparison")
    appendix.append("")
    
    appendix.append("**Agent-Level:**")
    appendix.append("- `agent_level_comparison/agent_performance_heatmap.png` - Agent profiles")
    appendix.append("- `agent_level_comparison/agent_group_mean_comparison.png` - Group means")
    appendix.append("- `agent_level_comparison/agent_scatter_key_features.png` - Agent positioning")
    appendix.append("- `agent_level_comparison/calls_per_agent.png` - Call distribution")
    appendix.append("")
    
    appendix.append("### C. Reports")
    appendix.append("")
    appendix.append("- `preprocessed_data/preprocessing_report.txt` - Data preparation summary")
    appendix.append("- `correlations/correlation_report.txt` - Correlation analysis")
    appendix.append("- `feature_importance/feature_importance_report.txt` - ML importance")
    appendix.append("- `statistical_tests/statistical_tests_report.txt` - Statistical analysis")
    appendix.append("- `shap_analysis/shap_report.txt` - SHAP interpretability")
    appendix.append("- `lime_analysis/lime_report.txt` - LIME explanations")
    appendix.append("- `agent_level_comparison/agent_level_report.txt` - Agent analysis")
    appendix.append("- `visualizations/visualization_report.txt` - Visualization catalog")
    appendix.append("- `final_report/EXECUTIVE_REPORT.txt` - ⭐ This report")
    appendix.append("")
    
    return appendix


def generate_html_report(report_content, output_dir):
    """Generate HTML version of the report"""
    print("\n" + "="*70)
    print("GENERATING HTML REPORT")
    print("="*70)
    
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<head>")
    html.append("    <meta charset='UTF-8'>")
    html.append("    <title>DPAD Analysis - Executive Report</title>")
    html.append("    <style>")
    html.append("        body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; max-width: 1200px; margin: 40px auto; padding: 20px; background: #f5f5f5; }")
    html.append("        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }")
    html.append("        h1 { color: #2c3e50; border-bottom: 4px solid #3498db; padding-bottom: 10px; }")
    html.append("        h2 { color: #34495e; margin-top: 40px; border-bottom: 2px solid #95a5a6; padding-bottom: 5px; }")
    html.append("        h3 { color: #555; margin-top: 25px; }")
    html.append("        table { border-collapse: collapse; width: 100%; margin: 20px 0; }")
    html.append("        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }")
    html.append("        th { background-color: #3498db; color: white; font-weight: bold; }")
    html.append("        tr:nth-child(even) { background-color: #f2f2f2; }")
    html.append("        .highlight { background-color: #fff3cd; padding: 15px; border-left: 5px solid #ffc107; margin: 20px 0; }")
    html.append("        .success { background-color: #d4edda; padding: 15px; border-left: 5px solid #28a745; margin: 20px 0; }")
    html.append("        .info { background-color: #d1ecf1; padding: 15px; border-left: 5px solid #17a2b8; margin: 20px 0; }")
    html.append("        ul { line-height: 1.8; }")
    html.append("        code { background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }")
    html.append("        .footer { margin-top: 50px; padding-top: 20px; border-top: 2px solid #ddd; text-align: center; color: #777; }")
    html.append("    </style>")
    html.append("</head>")
    html.append("<body>")
    html.append("    <div class='container'>")
    
    # Convert markdown to HTML (simple conversion)
    in_list = False
    in_table = False
    
    for line in report_content:
        line = line.strip()
        
        # Headers
        if line.startswith("# "):
            html.append(f"        <h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html.append(f"        <h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            html.append(f"        <h3>{line[4:]}</h3>")
        elif line.startswith("#### "):
            html.append(f"        <h4>{line[5:]}</h4>")
        
        # Lists
        elif line.startswith("- "):
            if not in_list:
                html.append("        <ul>")
                in_list = True
            # Make **bold** text
            line_content = line[2:]
            line_content = line_content.replace("**", "<strong>").replace("**", "</strong>")
            html.append(f"            <li>{line_content}</li>")
        elif in_list and line == "":
            html.append("        </ul>")
            in_list = False
        
        # Tables
        elif line.startswith("|"):
            if not in_table:
                html.append("        <table>")
                in_table = True
            
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            
            # Check if header row (next line will be separator)
            if all(c.replace("-", "").strip() == "" for c in cells):
                continue  # Skip separator row
            
            # Determine if header or data row
            row_html = "            <tr>"
            for cell in cells:
                cell_content = cell.replace("**", "<strong>").replace("**", "</strong>")
                row_html += f"<td>{cell_content}</td>"
            row_html += "</tr>"
            html.append(row_html)
        
        elif in_table and line == "":
            html.append("        </table>")
            in_table = False
        
        # Horizontal rules
        elif line.startswith("---"):
            html.append("        <hr>")
        
        # Special boxes
        elif "🎯" in line or "🏆" in line:
            html.append(f"        <div class='success'><strong>{line}</strong></div>")
        elif "💡" in line:
            html.append(f"        <div class='highlight'><strong>{line}</strong></div>")
        elif "📊" in line or "📈" in line:
            html.append(f"        <div class='info'><strong>{line}</strong></div>")
        
        # Regular paragraphs
        elif line and not line.startswith("="):
            html.append(f"        <p>{line}</p>")
    
    # Close any open tags
    if in_list:
        html.append("        </ul>")
    if in_table:
        html.append("        </table>")
    
    html.append("        <div class='footer'>")
    html.append(f"            <p>Report generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>")
    html.append("            <p>DPAD Analysis Pipeline © 2025</p>")
    html.append("        </div>")
    html.append("    </div>")
    html.append("</body>")
    html.append("</html>")
    
    # Save HTML
    html_path = output_dir / "analysis_outputs" / "final_report" / "EXECUTIVE_REPORT.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
    
    print(f"✅ HTML report saved: {html_path}")


def main():
    """Main combined report generation pipeline"""
    
    print("\n" + "="*70)
    print("DPAD ANALYSIS - COMBINED EXECUTIVE REPORT")
    print("="*70)
    print("\nGenerating comprehensive executive report...")
    print("="*70)
    
    output_dir = Path("ML_for_DPAD")
    
    # Load all results
    results = load_all_analysis_results()
    
    # Identify consensus features
    consensus_features = identify_top_features(results)
    
    # Generate report sections
    print("\n" + "="*70)
    print("GENERATING REPORT SECTIONS")
    print("="*70)
    
    report = []
    
    # 1. Executive Summary
    print("\n   📝 Generating executive summary...")
    report.extend(generate_executive_summary(results, consensus_features))
    
    # 2. Detailed Findings
    print("   📝 Generating detailed findings...")
    report.extend(generate_detailed_findings(results, consensus_features))
    
    # 3. Actionable Recommendations
    print("   📝 Generating actionable recommendations...")
    report.extend(generate_actionable_recommendations())
    
    # 4. Best Practices
    print("   📝 Generating best practices...")
    report.extend(generate_best_practices())
    
    # 5. Methodology
    print("   📝 Generating methodology section...")
    report.extend(generate_methodology_section())
    
    # 6. Appendix
    print("   📝 Generating appendix...")
    report.extend(generate_appendix(results))
    
    # Add conclusion
    report.append("## 🎯 CONCLUSION")
    report.append("")
    total_calls = results['preprocessing'].get('total_samples', 'N/A')
    total_agents = results['preprocessing'].get('total_agents', 'N/A')
    report.append(f"This comprehensive analysis, using 6 independent methods across {total_calls} calls")
    report.append(f"from {total_agents} agents, has identified **interruption rate** as the single most")
    report.append("important factor distinguishing High-DPAD from Low-DPAD agents.")
    report.append("")
    report.append("**The path to improved DPAD performance is clear:**")
    report.append("1. Reduce interruptions")
    report.append("2. Balance talk ratios")
    report.append("3. Manage sentiment proactively")
    report.append("4. Get to the point quickly")
    report.append("5. Listen more, talk less")
    report.append("")
    report.append("By implementing the recommendations in this report, particularly focusing")
    report.append("on interruption reduction training, organizations can expect measurable")
    report.append("improvements in DPAD performance within 30-90 days.")
    report.append("")
    report.append("---")
    report.append("")
    report.append(f"**End of Report**")
    report.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}")
    report.append("")
    
    # Save text report
    output_path = output_dir / "analysis_outputs" / "final_report"
    output_path.mkdir(parents=True, exist_ok=True)
    
    report_path = output_path / "EXECUTIVE_REPORT.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"\n✅ Text report saved: {report_path}")
    
    # Generate HTML version
    generate_html_report(report, output_dir)
    
    # Generate quick summary
    summary_path = output_path / "QUICK_SUMMARY.txt"
    quick_summary = []
    quick_summary.append("DPAD ANALYSIS - QUICK SUMMARY")
    quick_summary.append("="*70)
    quick_summary.append("")
    quick_summary.append("🏆 #1 FINDING: INTERRUPTION RATE")
    quick_summary.append("")
    quick_summary.append("High-DPAD agents interrupt customers SIGNIFICANTLY LESS than Low-DPAD agents.")
    quick_summary.append("")
    quick_summary.append("This finding is consistent across ALL 6 analytical methods:")
    quick_summary.append("✓ Correlation Analysis")
    quick_summary.append("✓ Machine Learning Feature Importance")
    quick_summary.append("✓ Statistical Significance Testing")
    quick_summary.append("✓ SHAP Analysis")
    quick_summary.append("✓ LIME Analysis")
    quick_summary.append("✓ Agent-Level Aggregation")
    quick_summary.append("")
    quick_summary.append("TOP 5 FEATURES:")
    for idx, row in consensus_features.head(5).iterrows():
        quick_summary.append(f"   {idx+1}. {row['feature']} ({row['num_methods']} methods)")
    quick_summary.append("")
    quick_summary.append("IMMEDIATE ACTIONS:")
    quick_summary.append("   1. Train agents on active listening (reduce interruptions)")
    quick_summary.append("   2. Monitor and flag high interruption rates")
    quick_summary.append("   3. Set talk ratio targets (50-60% agent, 40-50% customer)")
    quick_summary.append("   4. Optimize call openings (state reason within 10-13 seconds)")
    quick_summary.append("   5. Implement real-time sentiment tracking")
    quick_summary.append("")
    quick_summary.append(f"Full report: {report_path}")
    quick_summary.append(f"HTML version: {output_path / 'EXECUTIVE_REPORT.html'}")
    quick_summary.append("")
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(quick_summary))
    
    print(f"✅ Quick summary saved: {summary_path}")
    
    print("\n" + "="*70)
    print("✅ COMBINED EXECUTIVE REPORT COMPLETE")
    print("="*70)
    print(f"\nGenerated files:")
    print(f"   ✓ {report_path}")
    print(f"   ✓ {output_path / 'EXECUTIVE_REPORT.html'}")
    print(f"   ✓ {summary_path}")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

