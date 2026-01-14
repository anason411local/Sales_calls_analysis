"""
LangGraph nodes for Script Compliance Analysis workflow
Analyzes OMC calls for adherence to the 10-section sales script
"""
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from graph.state import AnalysisState
from utils.logger import logger
from utils.gemini_client import get_script_compliance_llm
from prompts.prompt_templates import SCRIPT_COMPLIANCE_ANALYSIS_PROMPT
from schemas.analysis_schemas import (
    ScriptComplianceInsight,
    ScriptSectionCompliance,
    ObjectionRebuttalAnalysis,
    AgentScriptComplianceMetrics,
    ScriptComplianceSummary
)
from config.settings import CALL_DURATION_THRESHOLD, BATCH_SIZE
import pandas as pd


# Script section names for reference
SCRIPT_SECTIONS = [
    "1_Intro",
    "2_Qualifying", 
    "3_Problem_Setup",
    "4_Pitch",
    "5_Offer_Close",
    "6_Info_Check",
    "7_SMS_Agreement",
    "8_Timeline_Expectations",
    "9_Opening_Objections",
    "10_Closing_Objections"
]

CORE_SECTIONS = ["1_Intro", "2_Qualifying", "3_Problem_Setup", "4_Pitch", "5_Offer_Close"]


def _analyze_single_call_compliance(row: Dict, chain) -> ScriptComplianceInsight:
    """
    Analyze a single call for script compliance
    
    Args:
        row: Row data dictionary
        chain: LLM chain
        
    Returns:
        ScriptComplianceInsight for the call
    """
    try:
        call_id = str(row.get('TO_Lead_ID', 'unknown'))
        logger.info(f"Analyzing script compliance for call ID: {call_id}")
        
        # Handle missing values and convert duration safely
        omc_duration_raw = row.get('TO_OMC_Duration', 0)
        
        if pd.isna(omc_duration_raw) or omc_duration_raw == '' or omc_duration_raw == '-':
            omc_duration = 0
        else:
            try:
                omc_duration = int(float(omc_duration_raw))
            except (ValueError, TypeError):
                omc_duration = 0
        
        # Concatenate OMC transcription parts
        omc_trans_1 = str(row.get('TO_OMC_Transcription_VICI', ''))
        omc_trans_2 = str(row.get('TO_OMC_Transcription_VICI(32000-64000)Words', ''))
        omc_trans_3 = str(row.get('TO_OMC_Transcription_VICI(64000+ Words)', ''))
        omc_transcription = f"{omc_trans_1} {omc_trans_2} {omc_trans_3}".strip()
        
        if not omc_transcription or omc_transcription == 'nan nan nan' or omc_transcription == '- - -':
            omc_transcription = 'No transcription available'
            # Return minimal insight for calls without transcription
            return ScriptComplianceInsight(
                call_id=call_id,
                omc_agent=str(row.get('TO_OMC_User', 'unknown')),
                call_duration_seconds=omc_duration,
                is_script_followed=False,
                overall_compliance_percentage=0.0,
                compliance_tier="low",
                non_compliance_reason="technical_connection_issues",
                non_compliance_category="External Factor",
                non_compliance_details="No transcription available for analysis",
                analysis_success=True
            )
        
        # Prepare input for LLM
        analysis_input = {
            "TO_Lead_ID": call_id,
            "TO_OMC_User": str(row.get('TO_OMC_User', 'unknown')),
            "TO_Event_O": str(row.get('TO_Event_O', 'unknown')),
            "TO_OMC_Duration": omc_duration,
            "TO_OMC_Disposiion": str(row.get('TO_OMC_Disposiion', 'unknown')),
            "LQ_Company_Name": str(row.get('LQ_Company_Name', 'unknown')),
            "LQ_Service": str(row.get('LQ_Service', 'unknown')),
            "omc_transcription": omc_transcription
        }
        
        # Invoke LLM analysis
        insight: ScriptComplianceInsight = chain.invoke(analysis_input)
        
        # Ensure required fields are set
        insight.call_id = call_id
        insight.omc_agent = analysis_input["TO_OMC_User"]
        insight.call_duration_seconds = omc_duration
        insight.call_exceeded_5_minutes = omc_duration >= CALL_DURATION_THRESHOLD
        insight.script_compliance_with_long_call = (
            insight.is_script_followed and insight.call_exceeded_5_minutes
        )
        insight.analysis_success = True
        
        # Determine compliance tier if not set
        if insight.overall_compliance_percentage >= 70:
            insight.compliance_tier = "high"
        elif insight.overall_compliance_percentage >= 40:
            insight.compliance_tier = "medium"
        else:
            insight.compliance_tier = "low"
        
        logger.info(f"Script compliance analyzed for call {call_id} - "
                   f"Compliance: {insight.overall_compliance_percentage:.1f}%, "
                   f"Script Followed: {insight.is_script_followed}")
        return insight
        
    except Exception as e:
        logger.error(f"Failed to analyze script compliance for call {row.get('TO_Lead_ID', 'unknown')}: {str(e)}")
        
        # Create failed insight
        omc_duration_raw = row.get('TO_OMC_Duration', 0)
        try:
            omc_duration = int(float(omc_duration_raw)) if not pd.isna(omc_duration_raw) and omc_duration_raw != '' else 0
        except (ValueError, TypeError):
            omc_duration = 0
        
        failed_insight = ScriptComplianceInsight(
            call_id=str(row.get('TO_Lead_ID', 'unknown')),
            omc_agent=str(row.get('TO_OMC_User', 'unknown')),
            call_duration_seconds=omc_duration,
            is_script_followed=False,
            overall_compliance_percentage=0.0,
            compliance_tier="low",
            analysis_success=False,
            analysis_error=str(e)
        )
        return failed_insight


def analyze_script_compliance_node(state: AnalysisState) -> AnalysisState:
    """
    Analyze script compliance for all calls in the batch using parallel processing
    
    Args:
        state: Current analysis state
        
    Returns:
        Updated state with script compliance insights
    """
    logger.info(f"Analyzing script compliance for batch {state['batch_number']}")
    
    llm = get_script_compliance_llm()
    chain = SCRIPT_COMPLIANCE_ANALYSIS_PROMPT | llm
    
    compliance_insights = []
    batch_size = len(state['current_batch'])
    
    # Use ThreadPoolExecutor for parallel processing
    max_workers = min(batch_size, BATCH_SIZE)
    logger.info(f"Processing {batch_size} calls for script compliance with {max_workers} workers")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all calls for parallel processing
        future_to_row = {
            executor.submit(_analyze_single_call_compliance, row, chain): row 
            for row in state['current_batch']
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_row):
            row = future_to_row[future]
            try:
                insight = future.result()
                compliance_insights.append(insight)
                
                # Track errors
                if not insight.analysis_success:
                    state['script_compliance_errors'].append({
                        'call_id': row.get('TO_Lead_ID'),
                        'error': insight.analysis_error,
                        'batch': state['batch_number']
                    })
                    
            except Exception as e:
                logger.error(f"Exception in script compliance analysis for call {row.get('TO_Lead_ID')}: {str(e)}")
                
                omc_duration_raw = row.get('TO_OMC_Duration', 0)
                try:
                    omc_duration = int(float(omc_duration_raw)) if not pd.isna(omc_duration_raw) else 0
                except (ValueError, TypeError):
                    omc_duration = 0
                
                failed_insight = ScriptComplianceInsight(
                    call_id=str(row.get('TO_Lead_ID', 'unknown')),
                    omc_agent=str(row.get('TO_OMC_User', 'unknown')),
                    call_duration_seconds=omc_duration,
                    is_script_followed=False,
                    overall_compliance_percentage=0.0,
                    compliance_tier="low",
                    analysis_success=False,
                    analysis_error=str(e)
                )
                compliance_insights.append(failed_insight)
                
                state['script_compliance_errors'].append({
                    'call_id': row.get('TO_Lead_ID'),
                    'error': str(e),
                    'batch': state['batch_number']
                })
    
    # Add to accumulated insights
    state['script_compliance_insights'].extend(compliance_insights)
    
    logger.info(f"Script compliance analysis complete for batch {state['batch_number']}. "
               f"Total: {len(state['script_compliance_insights'])}")
    return state


def accumulate_script_compliance_metrics_node(state: AnalysisState) -> AnalysisState:
    """
    Accumulate script compliance metrics from analyzed calls
    
    Args:
        state: Current analysis state
        
    Returns:
        Updated state with accumulated compliance metrics
    """
    logger.info("Accumulating script compliance metrics")
    
    # Get batch insights (only new ones from current batch)
    batch_start = len(state['script_compliance_insights']) - len(state['current_batch'])
    batch_insights = state['script_compliance_insights'][batch_start:]
    
    for insight in batch_insights:
        if not insight.analysis_success:
            continue
        
        agent = insight.omc_agent
        if not agent or agent == 'unknown':
            continue
        
        # Initialize agent metrics if not exists
        if agent not in state['agent_script_compliance']:
            state['agent_script_compliance'][agent] = {
                'total_calls': 0,
                'calls_script_followed': 0,
                'calls_exceeding_5min': 0,
                'script_followed_and_long': 0,
                'compliance_scores': [],
                'sections_attempted': [],
                'objections_faced': 0,
                'objections_with_rebuttals': 0,
                'returns_to_script': 0,
                'best_sections': [],
                'weakest_sections': [],
                'non_compliance_reasons': []
            }
        
        metrics = state['agent_script_compliance'][agent]
        metrics['total_calls'] += 1
        
        if insight.is_script_followed:
            metrics['calls_script_followed'] += 1
        
        if insight.call_exceeded_5_minutes:
            metrics['calls_exceeding_5min'] += 1
        
        if insight.script_compliance_with_long_call:
            metrics['script_followed_and_long'] += 1
        
        metrics['compliance_scores'].append(insight.overall_compliance_percentage)
        metrics['sections_attempted'].append(insight.sections_attempted)
        
        # Track objections
        metrics['objections_faced'] += insight.total_objections_raised
        metrics['objections_with_rebuttals'] += insight.objections_with_rebuttals
        
        if insight.returned_to_script_after_objection:
            metrics['returns_to_script'] += 1
        
        # Track sections
        if insight.strongest_sections:
            metrics['best_sections'].extend(insight.strongest_sections)
        if insight.weakest_sections:
            metrics['weakest_sections'].extend(insight.weakest_sections)
        
        # Track non-compliance reasons
        if not insight.is_script_followed and insight.non_compliance_reason:
            metrics['non_compliance_reasons'].append(insight.non_compliance_reason)
        
        # Update global summary metrics
        _update_global_compliance_summary(state, insight)
    
    logger.info(f"Script compliance metrics accumulated. Agents tracked: {len(state['agent_script_compliance'])}")
    return state


def _update_global_compliance_summary(state: AnalysisState, insight: ScriptComplianceInsight):
    """Update global script compliance summary metrics"""
    
    summary = state['script_compliance_summary']
    
    summary['total_calls'] += 1
    
    if insight.is_script_followed:
        summary['calls_script_followed'] += 1
    
    if insight.script_compliance_with_long_call:
        summary['script_followed_and_over_5min'] += 1
    
    # Compliance tier distribution
    if insight.compliance_tier == "high":
        summary['high_compliance_calls'] += 1
    elif insight.compliance_tier == "medium":
        summary['medium_compliance_calls'] += 1
    else:
        summary['low_compliance_calls'] += 1
    
    # Non-compliance breakdown
    if not insight.is_script_followed and insight.non_compliance_reason:
        reason = insight.non_compliance_reason
        if reason not in summary['non_compliance_breakdown']:
            summary['non_compliance_breakdown'][reason] = 0
        summary['non_compliance_breakdown'][reason] += 1
        
        # Category breakdown
        category = insight.non_compliance_category
        if category == "External Factor":
            summary['external_factors_count'] += 1
        elif category == "Client Interruption":
            summary['client_interruption_count'] += 1
        elif category == "Agent Error":
            summary['agent_error_count'] += 1
    
    # Objection metrics
    summary['total_objections'] += insight.total_objections_raised
    summary['objections_with_rebuttals'] += insight.objections_with_rebuttals
    
    if insight.returned_to_script_after_objection:
        summary['objections_with_script_return'] += 1
    
    # Section compliance tracking
    for section_compliance in insight.section_compliance:
        section_name = section_compliance.section_name
        if section_name not in summary['section_compliance_scores']:
            summary['section_compliance_scores'][section_name] = []
        summary['section_compliance_scores'][section_name].append(section_compliance.compliance_percentage)
    
    # =========================================================================
    # NEW: Track objection types with examples for Top 6 breakdown
    # =========================================================================
    if 'objection_type_breakdown' not in summary:
        summary['objection_type_breakdown'] = {}
    
    for objection_analysis in insight.objection_analyses:
        obj_type = objection_analysis.objection_type
        
        # Normalize objection type name
        obj_type_normalized = obj_type.lower().replace(' ', '_').replace('-', '_')
        
        if obj_type_normalized not in summary['objection_type_breakdown']:
            summary['objection_type_breakdown'][obj_type_normalized] = {
                'display_name': obj_type,
                'times_raised': 0,
                'times_with_rebuttal': 0,
                'examples': []  # Store up to 3 examples with quotes
            }
        
        breakdown = summary['objection_type_breakdown'][obj_type_normalized]
        breakdown['times_raised'] += 1
        
        if objection_analysis.was_rebuttal_attempted:
            breakdown['times_with_rebuttal'] += 1
            
            # Store example if we have less than 3 and this has good quotes
            if (len(breakdown['examples']) < 3 and 
                objection_analysis.customer_objection_verbatim and 
                objection_analysis.agent_rebuttal_verbatim):
                breakdown['examples'].append({
                    'call_id': insight.call_id,
                    'agent': insight.omc_agent,
                    'customer_quote': objection_analysis.customer_objection_verbatim,
                    'agent_rebuttal': objection_analysis.agent_rebuttal_verbatim,
                    'rebuttal_quality': objection_analysis.rebuttal_quality,
                    'followed_avq': objection_analysis.followed_avq_pattern,
                    'returned_to_script': objection_analysis.returned_to_script
                })


def generate_script_compliance_report_data(state: AnalysisState) -> Dict:
    """
    Generate final script compliance report data
    
    Args:
        state: Analysis state with all compliance data
        
    Returns:
        Dictionary with formatted report data
    """
    logger.info("Generating script compliance report data")
    
    summary = state['script_compliance_summary']
    total = summary['total_calls']
    
    if total == 0:
        return {"error": "No calls analyzed for script compliance"}
    
    # Calculate percentages
    script_followed_pct = (summary['calls_script_followed'] / total * 100) if total > 0 else 0
    
    script_followed_calls = summary['calls_script_followed']
    over_5min_pct = (summary['script_followed_and_over_5min'] / script_followed_calls * 100) if script_followed_calls > 0 else 0
    
    rebuttal_rate = (summary['objections_with_rebuttals'] / summary['total_objections'] * 100) if summary['total_objections'] > 0 else 0
    script_return_rate = (summary['objections_with_script_return'] / summary['total_objections'] * 100) if summary['total_objections'] > 0 else 0
    
    # Calculate section averages
    section_averages = {}
    for section, scores in summary['section_compliance_scores'].items():
        section_averages[section] = sum(scores) / len(scores) if scores else 0
    
    # Sort sections by compliance
    sorted_sections = sorted(section_averages.items(), key=lambda x: x[1], reverse=True)
    most_followed = [s[0] for s in sorted_sections[:3]]
    least_followed = [s[0] for s in sorted_sections[-3:]]
    
    # Agent rankings
    agent_metrics = state['agent_script_compliance']
    agent_rankings = []
    
    for agent, metrics in agent_metrics.items():
        if metrics['total_calls'] > 0:
            compliance_rate = metrics['calls_script_followed'] / metrics['total_calls'] * 100
            avg_score = sum(metrics['compliance_scores']) / len(metrics['compliance_scores']) if metrics['compliance_scores'] else 0
            agent_rankings.append({
                'agent': agent,
                'compliance_rate': compliance_rate,
                'avg_score': avg_score,
                'total_calls': metrics['total_calls']
            })
    
    agent_rankings.sort(key=lambda x: x['compliance_rate'], reverse=True)
    top_agents = [a['agent'] for a in agent_rankings[:5]]
    bottom_agents = [a['agent'] for a in agent_rankings[-5:] if a['compliance_rate'] < 50]
    
    # =========================================================================
    # NEW: Generate Top 6 Objection Type Breakdown with Examples
    # =========================================================================
    objection_type_breakdown = summary.get('objection_type_breakdown', {})
    
    # Sort by times_raised (descending) and get top 6
    sorted_objections = sorted(
        objection_type_breakdown.items(),
        key=lambda x: x[1]['times_raised'],
        reverse=True
    )[:6]
    
    top_6_objections = []
    for obj_key, obj_data in sorted_objections:
        times_raised = obj_data['times_raised']
        times_with_rebuttal = obj_data['times_with_rebuttal']
        rebuttal_rate_obj = (times_with_rebuttal / times_raised * 100) if times_raised > 0 else 0
        
        top_6_objections.append({
            'objection_type': obj_data['display_name'],
            'times_raised': times_raised,
            'times_with_rebuttal': times_with_rebuttal,
            'rebuttal_rate': rebuttal_rate_obj,
            'examples': obj_data['examples'][:3]  # Ensure max 3 examples
        })
    
    report_data = {
        # Question 1: Script Following Rate
        "q1_calls_script_followed_count": summary['calls_script_followed'],
        "q1_calls_script_followed_percentage": script_followed_pct,
        "q1_total_calls": total,
        
        # Question 2: Script Followed AND > 5 min
        "q2_script_followed_over_5min_count": summary['script_followed_and_over_5min'],
        "q2_script_followed_over_5min_percentage": over_5min_pct,
        "q2_denominator": script_followed_calls,
        
        # Question 3: Non-Compliance Reasons
        "q3_non_compliance_breakdown": summary['non_compliance_breakdown'],
        "q3_external_factors_count": summary['external_factors_count'],
        "q3_client_interruption_count": summary['client_interruption_count'],
        "q3_agent_error_count": summary['agent_error_count'],
        
        # Question 4: Objection Rebuttals
        "q4_total_objections": summary['total_objections'],
        "q4_objections_with_rebuttals": summary['objections_with_rebuttals'],
        "q4_rebuttal_rate": rebuttal_rate,
        
        # NEW: Top 6 Objection Types with Examples
        "q4_top_6_objections": top_6_objections,
        
        # Question 5: Script Return After Objection
        "q5_objections_with_script_return": summary['objections_with_script_return'],
        "q5_script_return_rate": script_return_rate,
        
        # Compliance Distribution
        "compliance_high_count": summary['high_compliance_calls'],
        "compliance_medium_count": summary['medium_compliance_calls'],
        "compliance_low_count": summary['low_compliance_calls'],
        
        # Section Analysis
        "section_compliance_averages": section_averages,
        "most_followed_sections": most_followed,
        "least_followed_sections": least_followed,
        
        # Agent Rankings
        "agent_rankings": agent_rankings,
        "top_compliant_agents": top_agents,
        "agents_needing_training": bottom_agents
    }
    
    return report_data


def get_example_compliance_calls(state: AnalysisState, count: int = 3) -> Dict:
    """
    Get example calls for different compliance levels
    
    Args:
        state: Analysis state
        count: Number of examples per category
        
    Returns:
        Dictionary with example calls
    """
    high_compliance = []
    low_compliance = []
    good_objection_handling = []
    
    for insight in state['script_compliance_insights']:
        if not insight.analysis_success:
            continue
        
        example = {
            'call_id': insight.call_id,
            'agent': insight.omc_agent,
            'duration': insight.call_duration_seconds,
            'compliance_pct': insight.overall_compliance_percentage,
            'sections_attempted': insight.sections_attempted,
            'best_practice_quote': insight.best_practice_quote,
            'improvement_quote': insight.improvement_needed_quote,
            'recommendations': insight.specific_recommendations[:2] if insight.specific_recommendations else []
        }
        
        if insight.compliance_tier == "high" and len(high_compliance) < count:
            high_compliance.append(example)
        
        if insight.compliance_tier == "low" and len(low_compliance) < count:
            example['non_compliance_reason'] = insight.non_compliance_reason
            example['proof'] = insight.non_compliance_verbatim_proof
            low_compliance.append(example)
        
        # Good objection handling
        if insight.objections_with_rebuttals > 0 and insight.returned_to_script_after_objection:
            if len(good_objection_handling) < count:
                objection_example = {
                    'call_id': insight.call_id,
                    'agent': insight.omc_agent,
                    'objections_handled': insight.objections_with_rebuttals,
                    'returned_to_script': True,
                    'recovery_quality': insight.script_recovery_quality
                }
                if insight.objection_analyses:
                    objection_example['example_objection'] = {
                        'type': insight.objection_analyses[0].objection_type,
                        'customer_quote': insight.objection_analyses[0].customer_objection_verbatim,
                        'agent_rebuttal': insight.objection_analyses[0].agent_rebuttal_verbatim,
                        'quality': insight.objection_analyses[0].rebuttal_quality
                    }
                good_objection_handling.append(objection_example)
    
    return {
        'high_compliance_examples': high_compliance,
        'low_compliance_examples': low_compliance,
        'good_objection_handling_examples': good_objection_handling
    }
