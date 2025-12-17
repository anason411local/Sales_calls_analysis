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
            "status_analysis": status_analysis
        })
        
        report = response.content
        
        # Add metadata footer
        report += f"\n\n---\n\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        report += f"*Total calls analyzed: {len(state['all_insights'])}*\n"
        report += f"*Analysis period: {_get_date_range(state)}*\n"
        
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
    
    summary = f"""
TOTAL CALLS: {total_calls}
SHORT CALLS (<2 min): {short_calls} ({short_calls/total_calls*100:.1f}%)
LONG CALLS (>=2 min): {long_calls} ({long_calls/total_calls*100:.1f}%)

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
    
    report = f"""# CALL PERFORMANCE ANALYSIS REPORT

## Executive Summary

**Total Calls Analyzed:** {total_calls}
**Short Calls (<2 min):** {short_calls} ({short_calls/total_calls*100:.1f}%)
**Long Calls (>=2 min):** {total_calls - short_calls} ({(total_calls-short_calls)/total_calls*100:.1f}%)

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

