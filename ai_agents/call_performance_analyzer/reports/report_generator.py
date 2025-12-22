"""
Report generation engine for creating comprehensive Markdown reports
"""
from typing import Dict, List
from graph.state import AnalysisState
from utils.logger import logger
from utils.gemini_client import get_report_llm
from prompts.prompt_templates import REPORT_GENERATION_PROMPT
from langchain_core.prompts import ChatPromptTemplate
import json
from datetime import datetime


def generate_comprehensive_report(state: AnalysisState) -> str:
    """
    Generate comprehensive Markdown report from accumulated insights
    
    Args:
        state: Analysis state with all accumulated data
        
    Returns:
        Markdown formatted report
    """
    logger.info("Starting comprehensive report generation")
    
    try:
        # Prepare data summaries for LLM
        accumulated_insights = _prepare_insights_summary(state)
        agent_performance = _prepare_agent_performance(state)
        daily_trends = _prepare_daily_trends(state)
        status_analysis = _prepare_status_analysis(state)
        
        # Prepare ML insights (NEW)
        ml_insights_summary = _prepare_ml_insights_summary(state)
        
        # Get LLM for report generation
        llm = get_report_llm()
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior business analyst creating executive reports."),
            ("human", REPORT_GENERATION_PROMPT)
        ])
        
        # Generate report
        chain = prompt | llm
        
        response = chain.invoke({
            "total_calls": len(state['all_insights']),
            "accumulated_insights": accumulated_insights,
            "agent_performance": agent_performance,
            "daily_trends": daily_trends,
            "status_analysis": status_analysis,
            "ml_insights": ml_insights_summary  # NEW
        })
        
        report = response.content
        
        # Add ML Insights Section (NEW)
        if state.get('ml_insights'):
            report += "\n\n" + _generate_ml_insights_section(state['ml_insights'])
        
        # Add metadata footer
        report += f"\n\n---\n\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        report += f"*Total calls analyzed: {len(state['all_insights'])}*\n"
        report += f"*Analysis period: {_get_date_range(state)}*\n"
        report += f"*Analysis Method: Agentic AI + Machine Learning*\n"
        
        logger.info("Report generation complete")
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        # Return a basic report if LLM fails
        return _generate_fallback_report(state)


def _prepare_insights_summary(state: AnalysisState) -> str:
    """Prepare summary of all insights for LLM"""
    
    total_calls = len(state['all_insights'])
    short_calls = sum(1 for i in state['all_insights'] if i.is_short_call)
    long_calls = total_calls - short_calls
    
    # Collect common issues and patterns
    all_short_reasons = []
    all_success_factors = []
    all_transferable_techniques = []
    critical_moments_short = []
    critical_moments_success = []
    
    for insight in state['all_insights']:
        if insight.is_short_call and insight.early_termination_reasons:
            all_short_reasons.extend(insight.early_termination_reasons)
            # Collect proof of issues with quotes
            if insight.proof_of_issue:
                critical_moments_short.append({
                    'call_id': insight.call_id,
                    'agent': insight.omc_agent,
                    'proof': insight.proof_of_issue,
                    'critical_moment': insight.critical_moment_quote
                })
        
        if not insight.is_short_call and insight.success_factors:
            all_success_factors.extend(insight.success_factors)
            # Collect transferable wisdom
            if insight.transferable_technique:
                all_transferable_techniques.append({
                    'call_id': insight.call_id,
                    'agent': insight.omc_agent,
                    'technique': insight.transferable_technique,
                    'application': insight.technique_application,
                    'persona': insight.agent_persona_insight,
                    'proof': insight.proof_of_success
                })
            # Collect success proofs
            if insight.proof_of_success:
                critical_moments_success.append({
                    'call_id': insight.call_id,
                    'agent': insight.omc_agent,
                    'proof': insight.proof_of_success,
                    'critical_moment': insight.critical_moment_quote
                })
    
    # Calculate percentages safely
    short_pct = (short_calls/total_calls*100) if total_calls > 0 else 0
    long_pct = (long_calls/total_calls*100) if total_calls > 0 else 0
    
    summary = f"""
TOTAL CALLS: {total_calls}
SHORT CALLS (<5 min): {short_calls} ({short_pct:.1f}%)
LONG CALLS (>=5 min): {long_calls} ({long_pct:.1f}%)

TOP REASONS FOR SHORT CALLS:
{_get_top_items(all_short_reasons, 10)}

TOP SUCCESS FACTORS FOR LONG CALLS:
{_get_top_items(all_success_factors, 10)}

LGS ISSUES IDENTIFIED:
{_get_top_items(state.get('lgs_issues', []), 10)}

CRITICAL MOMENTS - SHORT CALLS (With Proof):
{json.dumps(critical_moments_short[:5], indent=2)}

CRITICAL MOMENTS - SUCCESSFUL CALLS (With Proof):
{json.dumps(critical_moments_success[:5], indent=2)}

TRANSFERABLE WISDOM FROM SUCCESSFUL AGENTS:
{json.dumps(all_transferable_techniques[:5], indent=2)}

EXAMPLE SHORT CALLS:
{json.dumps(state.get('example_short_calls', [])[:3], indent=2)}

EXAMPLE SUCCESSFUL CALLS:
{json.dumps(state.get('example_successful_calls', [])[:3], indent=2)}
"""
    return summary


def _prepare_agent_performance(state: AnalysisState) -> str:
    """Prepare agent performance data"""
    
    agent_data = []
    for agent, metrics in state.get('agent_metrics', {}).items():
        avg_duration = metrics['total_duration'] / metrics['total_calls'] if metrics['total_calls'] > 0 else 0
        avg_score = sum(metrics['performance_scores']) / len(metrics['performance_scores']) if metrics['performance_scores'] else 0
        
        agent_data.append({
            'agent': agent,
            'total_calls': metrics['total_calls'],
            'short_calls': metrics['short_calls'],
            'long_calls': metrics['long_calls'],
            'avg_duration': round(avg_duration, 1),
            'avg_score': round(avg_score, 1),
            'short_call_rate': round(metrics['short_calls'] / metrics['total_calls'] * 100, 1) if metrics['total_calls'] > 0 else 0
        })
    
    # Sort by performance (lowest short call rate = best)
    agent_data.sort(key=lambda x: x['short_call_rate'])
    
    return json.dumps(agent_data, indent=2)


def _prepare_daily_trends(state: AnalysisState) -> str:
    """Prepare daily trends data"""
    
    daily_data = []
    for date, metrics in state.get('daily_metrics', {}).items():
        avg_duration = metrics['total_duration'] / metrics['total_calls'] if metrics['total_calls'] > 0 else 0
        
        daily_data.append({
            'date': date,
            'total_calls': metrics['total_calls'],
            'short_calls': metrics['short_calls'],
            'long_calls': metrics['long_calls'],
            'avg_duration': round(avg_duration, 1),
            'short_call_rate': round(metrics['short_calls'] / metrics['total_calls'] * 100, 1) if metrics['total_calls'] > 0 else 0
        })
    
    # Sort by date
    daily_data.sort(key=lambda x: x['date'])
    
    return json.dumps(daily_data, indent=2)


def _prepare_status_analysis(state: AnalysisState) -> str:
    """Prepare status analysis data"""
    
    status_data = []
    for status, metrics in state.get('status_metrics', {}).items():
        avg_duration = metrics['total_duration'] / metrics['count'] if metrics['count'] > 0 else 0
        
        status_data.append({
            'status': status,
            'count': metrics['count'],
            'avg_duration': round(avg_duration, 1)
        })
    
    # Sort by count
    status_data.sort(key=lambda x: x['count'], reverse=True)
    
    return json.dumps(status_data, indent=2)


def _get_top_items(items: List[str], top_n: int = 10) -> str:
    """Get top N most common items from list"""
    from collections import Counter
    
    if not items:
        return "None identified"
    
    counter = Counter(items)
    top_items = counter.most_common(top_n)
    
    result = []
    for item, count in top_items:
        result.append(f"- {item} (mentioned {count} times)")
    
    return "\n".join(result)


def _get_date_range(state: AnalysisState) -> str:
    """Get date range from daily metrics"""
    dates = list(state.get('daily_metrics', {}).keys())
    if not dates:
        return "Unknown"
    
    dates.sort()
    if len(dates) == 1:
        return dates[0]
    
    return f"{dates[0]} to {dates[-1]}"


def _generate_fallback_report(state: AnalysisState) -> str:
    """Generate basic report if LLM fails"""
    
    total_calls = len(state['all_insights'])
    short_calls = sum(1 for i in state['all_insights'] if i.is_short_call)
    long_calls = total_calls - short_calls
    
    # Calculate percentages safely
    short_pct = (short_calls/total_calls*100) if total_calls > 0 else 0
    long_pct = (long_calls/total_calls*100) if total_calls > 0 else 0
    
    report = f"""# CALL PERFORMANCE ANALYSIS REPORT

## Executive Summary

**Total Calls Analyzed:** {total_calls}
**Short Calls (<5 min):** {short_calls} ({short_pct:.1f}%)
**Long Calls (>=5 min):** {long_calls} ({long_pct:.1f}%)

## Key Findings

### Agent Performance
{len(state.get('agent_metrics', {}))} agents analyzed

### Daily Trends
{len(state.get('daily_metrics', {}))} days of data

### Status Breakdown
{len(state.get('status_metrics', {}))} different statuses

---

*This is a fallback report. Full report generation encountered an error.*
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return report


def _prepare_ml_insights_summary(state: AnalysisState) -> str:
    """
    Prepare ML insights summary for LLM
    
    Args:
        state: Analysis state
        
    Returns:
        ML insights summary string
    """
    ml_insights = state.get('ml_insights')
    
    if not ml_insights:
        return "ML insights not available"
    
    try:
        summary_parts = []
        
        # Top variables
        if ml_insights.top_variables:
            summary_parts.append(f"Top 10 Variables: {', '.join(ml_insights.top_variables[:10])}")
        
        # Statistical summary
        summary_parts.append(f"Statistical Summary: {ml_insights.statistical_summary}")
        
        # Key insights count
        summary_parts.append(f"Generated {len(ml_insights.key_insights)} ML-based insights")
        
        # Top 5 insights
        if ml_insights.key_insights:
            summary_parts.append("\nTop 5 ML Insights:")
            for i, insight in enumerate(ml_insights.key_insights[:5], 1):
                summary_parts.append(f"  {i}. [{insight.category.upper()}] {insight.insight}")
                summary_parts.append(f"     Evidence: {insight.evidence}")
        
        return "\n".join(summary_parts)
        
    except Exception as e:
        logger.error(f"Error preparing ML insights summary: {str(e)}")
        return "ML insights summary unavailable"


def _generate_ml_insights_section(ml_insights) -> str:
    """
    Generate ML Insights section for the report with embedded visualizations
    
    Args:
        ml_insights: MLInsightsCollection object
        
    Returns:
        Markdown formatted ML insights section
    """
    try:
        section = []
        
        section.append("---\n")
        section.append("# 🤖 MACHINE LEARNING INSIGHTS\n")
        section.append("*Advanced ML Analysis: Feature Importance, SHAP, LIME, Statistical Tests*\n")
        
        # Statistical Summary
        section.append("\n## 📊 Statistical Summary\n")
        section.append(f"{ml_insights.statistical_summary}\n")
        
        # Top Variables
        if ml_insights.top_variables:
            section.append("\n## 🎯 Top 10 Most Important Variables\n")
            section.append("*These variables have the strongest predictive power for call duration:*\n")
            for i, var in enumerate(ml_insights.top_variables, 1):
                section.append(f"{i}. **{var}**")
            section.append("")
        
        # Key Visualizations
        if ml_insights.visualizations_to_include:
            section.append("\n## 📈 Key ML Visualizations\n")
            
            for viz_path in ml_insights.visualizations_to_include[:6]:  # Top 6 visualizations
                # Convert absolute path to relative path for Markdown
                from pathlib import Path
                viz_path_obj = Path(viz_path)
                viz_name = viz_path_obj.name
                
                # Determine visualization title
                if "waterfall" in viz_name:
                    title = "SHAP Waterfall Plot - Individual Prediction Explanation"
                    description = "Shows how each variable contributes to pushing a call toward short or long duration"
                elif "top_20" in viz_name:
                    title = "Top 20 Variables by Combined Importance"
                    description = "Ranked by Random Forest, XGBoost, and Correlation analysis"
                elif "beeswarm" in viz_name:
                    title = "SHAP Summary Plot - Overall Feature Impact"
                    description = "Each dot represents one call, color shows feature value (red=high, blue=low)"
                elif "correlation" in viz_name:
                    title = "Correlation vs ML Importance"
                    description = "Compares statistical correlation with ML model importance"
                elif "effect_sizes" in viz_name:
                    title = "Statistical Effect Sizes"
                    description = "Variables with largest differences between short and long calls"
                elif "roc" in viz_name:
                    title = "ML Model Performance (ROC Curves)"
                    description = "Model accuracy in predicting call duration"
                else:
                    title = viz_name.replace("_", " ").replace(".png", "").title()
                    description = "ML analysis visualization"
                
                section.append(f"\n### {title}\n")
                section.append(f"*{description}*\n")
                section.append(f"![{title}]({viz_path})\n")
        
        # Key Insights by Category
        if ml_insights.key_insights:
            section.append("\n## 💡 Key ML Insights\n")
            
            # Group insights by category
            categories = {}
            for insight in ml_insights.key_insights:
                if insight.category not in categories:
                    categories[insight.category] = []
                categories[insight.category].append(insight)
            
            # Display by category
            category_names = {
                'correlation': '📉 Correlation Analysis',
                'feature_importance': '⭐ Feature Importance',
                'shap': '🔍 SHAP Explainability',
                'statistical': '📊 Statistical Significance',
                'lime': '🎯 LIME Local Explanations'
            }
            
            for category, insights_list in categories.items():
                section.append(f"\n### {category_names.get(category, category.title())}\n")
                
                for insight in insights_list[:5]:  # Top 5 per category
                    section.append(f"**{insight.insight}**")
                    section.append(f"- *Evidence:* {insight.evidence}")
                    section.append(f"- *Recommendation:* {insight.recommendation}")
                    section.append(f"- *Importance Score:* {insight.importance_score:.3f}")
                    section.append("")
        
        # Comprehensive Recommendations
        section.append("\n## 🎯 ML-Based Recommendations\n")
        section.append("*Actionable insights derived from machine learning analysis:*\n")
        section.append(f"{ml_insights.recommendations_summary}\n")
        
        # Methodology Note
        section.append("\n## 🔬 ML Methodology\n")
        section.append("This analysis combines multiple ML techniques:\n")
        section.append("- **Random Forest & XGBoost**: Tree-based models for feature importance")
        section.append("- **SHAP (SHapley Additive exPlanations)**: Model-agnostic explainability")
        section.append("- **LIME (Local Interpretable Model-agnostic Explanations)**: Local predictions")
        section.append("- **Statistical Tests**: T-tests, Mann-Whitney U, Chi-square, Cohen's D")
        section.append("- **Correlation Analysis**: Spearman correlation for non-linear relationships\n")
        
        return "\n".join(section)
        
    except Exception as e:
        logger.error(f"Error generating ML insights section: {str(e)}")
        return "\n---\n\n# MACHINE LEARNING INSIGHTS\n\n*ML insights unavailable - see logs for details*\n"

