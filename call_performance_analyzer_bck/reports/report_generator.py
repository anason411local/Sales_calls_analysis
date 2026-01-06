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
        first_5min_analysis = _prepare_first_5min_analysis(state)
        agent_performance_overview = _prepare_agent_performance_overview(state)  # NEW - High-level metrics
        
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
            "first_5min_analysis": first_5min_analysis,
            "agent_performance_overview": agent_performance_overview  # NEW
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


def _prepare_first_5min_analysis(state: AnalysisState) -> str:
    """
    Prepare first 5 minutes analysis data for the new report section
    
    This is the critical comparison between <5 min and >5 min calls
    focusing on what agents SAY in the first 5 minutes
    """
    from collections import Counter
    
    # Get short call failures
    short_call_failures = state.get('first_5min_short_call_failures', [])
    
    # Get long call successes
    long_call_successes = state.get('first_5min_long_call_successes', [])
    
    # Get key phrases
    success_phrases = state.get('first_5min_key_phrases_success', [])
    failure_phrases = state.get('first_5min_key_phrases_failure', [])
    
    # Get opening techniques
    success_openings = state.get('first_5min_opening_techniques_success', [])
    failure_openings = state.get('first_5min_opening_techniques_failure', [])
    
    # Get engagement hooks
    engagement_hooks = state.get('first_5min_engagement_hooks', [])
    
    # Get turning points
    turning_points = state.get('first_5min_turning_points', [])
    
    # Get verbiage comparison
    verbiage_comparison = state.get('first_5min_verbiage_comparison', {'success': [], 'failure': []})
    
    # Count most common success phrases
    success_phrase_counts = Counter(success_phrases).most_common(10)
    failure_phrase_counts = Counter(failure_phrases).most_common(10)
    
    # Count most common engagement hooks
    hook_counts = Counter(engagement_hooks).most_common(10)
    
    # Prepare summary
    summary = f"""
==========================================================================
FIRST 5 MINUTES ANALYSIS: WHAT TO SAY TO KEEP THE CUSTOMER
==========================================================================

OVERVIEW:
- Short Calls (<5 min) Analyzed: {len(short_call_failures)}
- Long Calls (>=5 min) Analyzed: {len(long_call_successes)}

==========================================================================
TOP KEY PHRASES THAT WORK (From Successful Long Calls):
==========================================================================
{_format_phrase_counts(success_phrase_counts)}

==========================================================================
KEY PHRASES THAT FAIL (From Short Calls):
==========================================================================
{_format_phrase_counts(failure_phrase_counts)}

==========================================================================
ENGAGEMENT HOOKS THAT KEEP CUSTOMERS (Most Effective):
==========================================================================
{_format_phrase_counts(hook_counts)}

==========================================================================
SUCCESSFUL OPENING TECHNIQUES (With Verbatim Examples):
==========================================================================
{json.dumps(success_openings[:10], indent=2)}

==========================================================================
FAILED OPENING TECHNIQUES (What NOT to Say):
==========================================================================
{json.dumps(failure_openings[:10], indent=2)}

==========================================================================
TURNING POINTS - WHERE CALLS ARE WON OR LOST:
==========================================================================
{json.dumps(turning_points[:15], indent=2)}

==========================================================================
VERBIAGE COMPARISON: SUCCESS vs FAILURE
==========================================================================

SUCCESS VERBIAGE (What Kept Customers Past 5 Minutes):
{json.dumps(verbiage_comparison.get('success', [])[:10], indent=2)}

FAILURE VERBIAGE (What Lost Customers Before 5 Minutes):
{json.dumps(verbiage_comparison.get('failure', [])[:10], indent=2)}

==========================================================================
DETAILED SHORT CALL FAILURES (First 5 Min Analysis):
==========================================================================
{json.dumps(short_call_failures[:8], indent=2)}

==========================================================================
DETAILED LONG CALL SUCCESSES (First 5 Min Analysis):
==========================================================================
{json.dumps(long_call_successes[:8], indent=2)}

"""
    return summary


def _format_phrase_counts(phrase_counts: list) -> str:
    """Format phrase counts for display"""
    if not phrase_counts:
        return "No data available"
    
    result = []
    for phrase, count in phrase_counts:
        if phrase and phrase.strip():
            result.append(f"- \"{phrase}\" (mentioned {count} times)")
    
    return "\n".join(result) if result else "No data available"


def _prepare_agent_performance_overview(state: AnalysisState) -> str:
    """
    Prepare agent performance overview data (DPAD, Conversion Rate, Payability)
    from external high-level metrics source
    
    This provides business context about agent performance beyond call transcription analysis
    """
    overview = state.get('agent_performance_overview', {})
    
    if not overview or not overview.get('agents'):
        return "No agent performance overview data available."
    
    agents = overview.get('agents', [])
    total_agents = overview.get('total_agents', len(agents))
    
    summary = f"""
==========================================================================
AGENT PERFORMANCE OVERVIEW (High-Level Business Metrics)
==========================================================================

TOTAL AGENTS IN OVERVIEW: {total_agents}

This data provides high-level business metrics for agents including:
- DPAD (Deals Per Agent Per Day): Productivity measure
- Conversion Rate: Percentage of calls that convert to deals
- Payability (30/60/90 Days): Revenue quality and sustainability

==========================================================================
AGENT PERFORMANCE TABLE:
==========================================================================

| Agent Name | Attendance | Deals | Calls | DPAD | Conversion Rate | 30-Day Payability | 60-Day Payability | 90-Day Payability | 0-90 Day Payability |
|------------|------------|-------|-------|------|-----------------|-------------------|-------------------|-------------------|---------------------|
"""
    
    for agent in agents:
        summary += f"| {agent.get('name', 'Unknown')} | {agent.get('attendance', '-')} | {agent.get('deals', '-')} | {agent.get('calls', '-')} | {agent.get('dpad', '-')} | {agent.get('conversion_rate', '-')} | {agent.get('payability_30_days', '-')} | {agent.get('payability_60_days', '-')} | {agent.get('payability_90_days', '-')} | {agent.get('payability_0_90_days', '-')} |\n"
    
    summary += f"""

==========================================================================
KEY INSIGHTS FROM AGENT PERFORMANCE OVERVIEW:
==========================================================================

TOP PERFORMERS BY DPAD (Deals Per Agent Per Day):
"""
    
    # Sort by DPAD and list top performers
    sorted_by_dpad = sorted(agents, key=lambda x: float(x.get('dpad', 0)) if x.get('dpad') else 0, reverse=True)
    for i, agent in enumerate(sorted_by_dpad[:5], 1):
        summary += f"{i}. {agent.get('name', 'Unknown')} - DPAD: {agent.get('dpad', '-')}, Conversion: {agent.get('conversion_rate', '-')}\n"
    
    summary += """
CORRELATION INSIGHTS:
- Use this data to correlate DPAD and Conversion Rate with call transcription analysis
- High DPAD agents may have specific techniques visible in their call patterns
- Low payability may indicate issues with qualification or promise-keeping
- Cross-reference with First 5 Minutes analysis for actionable insights

==========================================================================
RAW AGENT DATA (For Reference):
==========================================================================
"""
    summary += json.dumps(agents, indent=2)
    
    return summary


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

