"""
LangGraph nodes for call performance analysis workflow
"""
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from graph.state import AnalysisState
from utils.logger import logger
from utils.gemini_client import get_analysis_llm
from prompts.prompt_templates import CALL_ANALYSIS_PROMPT
from schemas.analysis_schemas import CallInsight
from config.settings import CALL_DURATION_THRESHOLD, BATCH_SIZE
import pandas as pd


def prepare_batch_node(state: AnalysisState) -> AnalysisState:
    """
    Prepare current batch for analysis
    
    Args:
        state: Current analysis state
        
    Returns:
        Updated state with batch prepared
    """
    logger.info(f"Preparing batch {state['batch_number']}")
    
    # Initialize state fields if not present
    if 'all_insights' not in state:
        state['all_insights'] = []
    if 'agent_metrics' not in state:
        state['agent_metrics'] = {}
    if 'daily_metrics' not in state:
        state['daily_metrics'] = {}
    if 'status_metrics' not in state:
        state['status_metrics'] = {}
    if 'short_call_patterns' not in state:
        state['short_call_patterns'] = []
    if 'long_call_patterns' not in state:
        state['long_call_patterns'] = []
    if 'lgs_issues' not in state:
        state['lgs_issues'] = []
    if 'omc_issues' not in state:
        state['omc_issues'] = []
    if 'example_short_calls' not in state:
        state['example_short_calls'] = []
    if 'example_successful_calls' not in state:
        state['example_successful_calls'] = []
    if 'errors' not in state:
        state['errors'] = []
    
    logger.info(f"Batch {state['batch_number']} prepared with {len(state['current_batch'])} rows")
    return state


def _analyze_single_call(row: Dict, chain) -> CallInsight:
    """
    Analyze a single call (helper function for parallel processing)
    
    Args:
        row: Row data dictionary
        chain: LLM chain
        
    Returns:
        CallInsight for the call
    """
    try:
        from config.settings import INPUT_COLUMNS
        
        call_id = row.get('TO_Lead_ID', 'unknown')
        logger.info(f"Analyzing call ID: {call_id}")
        
        # Handle missing values and convert duration safely
        omc_duration_raw = row.get('TO_OMC_Duration', 0)
        lgs_duration_raw = row.get('TO_length_in_sec', 0)
        
        if pd.isna(omc_duration_raw) or omc_duration_raw == '' or omc_duration_raw == '-':
            omc_duration = 0
            logger.warning(f"Missing or invalid OMC duration for call {call_id}, using 0")
        else:
            try:
                omc_duration = int(float(omc_duration_raw))
            except (ValueError, TypeError):
                omc_duration = 0
                logger.warning(f"Invalid OMC duration '{omc_duration_raw}' for call {call_id}, using 0")
        
        if pd.isna(lgs_duration_raw) or lgs_duration_raw == '' or lgs_duration_raw == '-':
            lgs_duration = 0
        else:
            try:
                lgs_duration = int(float(lgs_duration_raw))
            except (ValueError, TypeError):
                lgs_duration = 0
        
        # Concatenate LGS transcription parts - using exact CSV column names
        lgs_trans_1 = str(row.get('TO_Transcription_VICI(0-32000) Words', ''))
        lgs_trans_2 = str(row.get('TO_Transcription_VICI(32001-64000) Words', ''))
        lgs_trans_3 = str(row.get('TO_Transcription_VICI(64000+ Words)', ''))
        lgs_transcription = f"{lgs_trans_1} {lgs_trans_2} {lgs_trans_3}".strip()
        if not lgs_transcription or lgs_transcription == 'nan nan nan' or lgs_transcription == '- - -':
            lgs_transcription = 'No transcription available'
        
        # Concatenate OMC transcription parts - using exact CSV column names
        omc_trans_1 = str(row.get('TO_OMC_Transcription_VICI', ''))
        omc_trans_2 = str(row.get('TO_OMC_Transcription_VICI(32000-64000)Words', ''))
        omc_trans_3 = str(row.get('TO_OMC_Transcription_VICI(64000+ Words)', ''))
        omc_transcription = f"{omc_trans_1} {omc_trans_2} {omc_trans_3}".strip()
        if not omc_transcription or omc_transcription == 'nan nan nan' or omc_transcription == '- - -':
            omc_transcription = 'No transcription available'
        
        # Prepare input for LLM with all variables
        analysis_input = {
            # Lead Quality
            "LQ_Company_Name": str(row.get('LQ_Company_Name', 'unknown')),
            "LQ_Company_Address": str(row.get('LQ_Company_Address', 'unknown')),
            "LQ_Service": str(row.get('LQ_Service', 'unknown')),
            "LQ_Customer_Name": str(row.get('LQ_Customer_Name', 'unknown')),
            "Calls_Count": str(row.get('Calls Count', 'unknown')),  # CSV has space
            "Connection_Made_Calls": str(row.get('Connection Made Calls', 'unknown')),  # CSV has space
            
            # Call Information
            "TO_Lead_ID": str(call_id),
            "TO_Event_O": str(row.get('TO_Event_O', 'unknown')),
            "TO_length_in_sec": lgs_duration,
            "TO_OMC_Duration": omc_duration,
            "TO_OMC_Disposiion": str(row.get('TO_OMC_Disposiion', 'unknown')),
            
            # LGS Data
            "TO_User_M": str(row.get('TO_User_M', 'unknown')),
            "lgs_transcription": lgs_transcription,
            
            # LGS Extracted Variables
            "season_status": str(row.get('season_status', 'unknown')),
            "lgs_agent_gender": str(row.get('lgs_agent_gender', 'unknown')),
            "is_decision_maker": str(row.get('is_decision_maker', 'unknown')),
            "ready_for_customers": str(row.get('ready_for_customers', 'unknown')),
            "forbidden_industry": str(row.get('forbidden_industry', 'unknown')),
            "ready_to_transfer": str(row.get('ready_to_transfer', 'unknown')),
            "customer_sentiment_lgs": str(row.get('customer_sentiment_lgs', 'unknown')),
            "customer_language": str(row.get('customer_language', 'unknown')),
            "who_said_hello_first_lgs": str(row.get('who_said_hello_first_lgs', 'unknown')),
            "lgs_sentiment_style": str(row.get('lgs_sentiment_style', 'unknown')),
            
            # OMC Data
            "TO_OMC_User": str(row.get('TO_OMC_User', 'unknown')),
            "omc_transcription": omc_transcription,
            
            # OMC Extracted Variables
            "timezone": str(row.get('timezone', 'unknown')),
            "customer_sentiment_omc": str(row.get('customer_sentiment_omc', 'unknown')),
            "customer_knows_marketing": str(row.get('customer_knows_marketing', 'unknown')),
            "customer_availability": str(row.get('customer_availability', 'unknown')),
            "customer_marketing_experience": str(row.get('customer_marketing_experience', 'unknown')),
            "technical_quality_score": str(row.get('technical_quality_score', 'unknown')),
            "omc_agent_sentiment_style": str(row.get('omc_agent_sentiment_style', 'unknown')),
            "omc_who_said_hello_first": str(row.get('omc_who_said_hello_first', 'unknown')),
            "customer_talk_percentage": str(row.get('customer_talk_percentage', 'unknown')),
            "total_discovery_questions": str(row.get('total_discovery_questions', 'unknown')),
            "total_buying_signals": str(row.get('total_buying_signals', 'unknown')),
            "time_to_reason_seconds": str(row.get('time_to_reason_seconds', 'unknown')),
            "location_mentioned": str(row.get('location_mentioned', 'unknown')),
            "business_type_mentioned": str(row.get('business_type_mentioned', 'unknown')),
            "within_45_seconds": str(row.get('within_45_seconds', 'unknown')),
            "call_structure_framed": str(row.get('call_structure_framed', 'unknown')),
            "total_objections": str(row.get('total_objections', 'unknown')),
            "objections_acknowledged": str(row.get('objections_acknowledged', 'unknown')),
            "price_mentions_final_2min": str(row.get('price_mentions_final_2min', 'unknown')),
            "timeline_mentions_final_2min": str(row.get('timeline_mentions_final_2min', 'unknown')),
            "contract_mentions_final_2min": str(row.get('contract_mentions_final_2min', 'unknown')),
            "objections_rebutted": str(row.get('objections_rebutted', 'unknown')),
            "total_interruptions": str(row.get('total_interruptions', 'unknown')),
            "commitment_type": str(row.get('commitment_type', 'unknown')),
            "call_result_tag": str(row.get('call_result_tag', 'unknown'))
        }
        
        # Invoke LLM analysis
        insight: CallInsight = chain.invoke(analysis_input)
        
        # Ensure required fields are set
        insight.call_id = analysis_input["TO_Lead_ID"]
        insight.call_date = analysis_input["TO_Event_O"]
        insight.omc_duration = analysis_input["TO_OMC_Duration"]
        insight.omc_status = analysis_input["TO_OMC_Disposiion"]
        insight.lgs_agent = analysis_input["TO_User_M"]
        insight.omc_agent = analysis_input["TO_OMC_User"]
        insight.is_short_call = insight.omc_duration < CALL_DURATION_THRESHOLD
        insight.call_category = "short" if insight.is_short_call else "long"
        insight.analysis_success = True
        
        logger.info(f"Successfully analyzed call {call_id} - Category: {insight.call_category}")
        return insight
        
    except Exception as e:
        from config.settings import INPUT_COLUMNS
        logger.error(f"Failed to analyze call {row.get(INPUT_COLUMNS['lead_id'], 'unknown')}: {str(e)}")
        
        # Create failed insight with safe duration conversion
        omc_duration_raw = row.get(INPUT_COLUMNS['omc_duration'], 0)
        try:
            omc_duration = int(float(omc_duration_raw)) if not pd.isna(omc_duration_raw) and omc_duration_raw != '' and omc_duration_raw != '-' else 0
        except (ValueError, TypeError):
            omc_duration = 0
        
        failed_insight = CallInsight(
            call_id=str(row.get(INPUT_COLUMNS['lead_id'], 'unknown')),
            call_date=str(row.get(INPUT_COLUMNS['call_date'], 'unknown')),
            omc_duration=omc_duration,
            omc_status=str(row.get(INPUT_COLUMNS['omc_status'], 'unknown')),
            lgs_agent=str(row.get(INPUT_COLUMNS['lgs_agent'], 'unknown')),
            omc_agent=str(row.get(INPUT_COLUMNS['omc_agent'], 'unknown')),
            analysis_success=False,
            analysis_error=str(e)
        )
        return failed_insight


def analyze_call_node(state: AnalysisState) -> AnalysisState:
    """
    Analyze individual calls in the batch using Gemini LLM with parallel processing
    
    Args:
        state: Current analysis state
        
    Returns:
        Updated state with call insights
    """
    logger.info(f"Analyzing batch {state['batch_number']} with PARALLEL processing")
    
    llm = get_analysis_llm()
    chain = CALL_ANALYSIS_PROMPT | llm
    
    batch_insights = []
    batch_size = len(state['current_batch'])
    
    # Use ThreadPoolExecutor for parallel processing
    max_workers = min(batch_size, BATCH_SIZE)  # Use batch size as max workers
    logger.info(f"Processing {batch_size} calls in parallel with {max_workers} workers")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all calls for parallel processing
        future_to_row = {
            executor.submit(_analyze_single_call, row, chain): row 
            for row in state['current_batch']
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_row):
            row = future_to_row[future]
            try:
                insight = future.result()
                batch_insights.append(insight)
                
                # Track errors
                if not insight.analysis_success:
                    from config.settings import INPUT_COLUMNS
                    state['errors'].append({
                        'call_id': row.get(INPUT_COLUMNS['lead_id']),
                        'error': insight.analysis_error,
                        'batch': state['batch_number']
                    })
                    
            except Exception as e:
                from config.settings import INPUT_COLUMNS
                logger.error(f"Exception in parallel processing for call {row.get(INPUT_COLUMNS['lead_id'])}: {str(e)}")
                
                # Create failed insight with safe duration conversion
                omc_duration_raw = row.get(INPUT_COLUMNS['omc_duration'], 0)
                try:
                    omc_duration = int(float(omc_duration_raw)) if not pd.isna(omc_duration_raw) and omc_duration_raw != '' and omc_duration_raw != '-' else 0
                except (ValueError, TypeError):
                    omc_duration = 0
                
                failed_insight = CallInsight(
                    call_id=str(row.get(INPUT_COLUMNS['lead_id'], 'unknown')),
                    call_date=str(row.get(INPUT_COLUMNS['omc_call_date'], 'unknown')),
                    omc_duration=omc_duration,
                    omc_status=str(row.get(INPUT_COLUMNS['omc_status'], 'unknown')),
                    lgs_agent=str(row.get(INPUT_COLUMNS['lgs_agent'], 'unknown')),
                    omc_agent=str(row.get(INPUT_COLUMNS['omc_agent'], 'unknown')),
                    analysis_success=False,
                    analysis_error=str(e)
                )
                batch_insights.append(failed_insight)
                
                state['errors'].append({
                    'call_id': row.get(INPUT_COLUMNS['lead_id']),
                    'error': str(e),
                    'batch': state['batch_number']
                })
    
    # Add batch insights to accumulated insights
    state['all_insights'].extend(batch_insights)
    state['processed_count'] = state.get('processed_count', 0) + len(batch_insights)
    
    logger.info(f"Batch {state['batch_number']} PARALLEL analysis complete. Total insights: {len(state['all_insights'])}")
    return state


def accumulate_metrics_node(state: AnalysisState) -> AnalysisState:
    """
    Accumulate metrics from analyzed calls
    
    Args:
        state: Current analysis state
        
    Returns:
        Updated state with accumulated metrics
    """
    logger.info("Accumulating metrics from batch")
    
    # Process only the latest batch insights
    batch_start = state['processed_count'] - len(state['current_batch'])
    batch_insights = state['all_insights'][batch_start:]
    
    for insight in batch_insights:
        if not insight.analysis_success:
            continue
        
        # Agent metrics
        agent = insight.omc_agent
        if agent and agent != 'unknown':
            if agent not in state['agent_metrics']:
                state['agent_metrics'][agent] = {
                    'total_calls': 0,
                    'short_calls': 0,
                    'long_calls': 0,
                    'total_duration': 0,
                    'performance_scores': [],
                    'issues': [],
                    'strengths': []
                }
            
            state['agent_metrics'][agent]['total_calls'] += 1
            if insight.is_short_call:
                state['agent_metrics'][agent]['short_calls'] += 1
            else:
                state['agent_metrics'][agent]['long_calls'] += 1
            
            state['agent_metrics'][agent]['total_duration'] += insight.omc_duration or 0
            
            if insight.agent_performance_rating:
                state['agent_metrics'][agent]['performance_scores'].append(insight.agent_performance_rating)
            
            if insight.specific_recommendations:
                state['agent_metrics'][agent]['issues'].extend(insight.specific_recommendations)
        
        # Daily metrics
        date = insight.call_date
        if date and date != 'unknown':
            if date not in state['daily_metrics']:
                state['daily_metrics'][date] = {
                    'total_calls': 0,
                    'short_calls': 0,
                    'long_calls': 0,
                    'total_duration': 0
                }
            
            state['daily_metrics'][date]['total_calls'] += 1
            if insight.is_short_call:
                state['daily_metrics'][date]['short_calls'] += 1
            else:
                state['daily_metrics'][date]['long_calls'] += 1
            
            state['daily_metrics'][date]['total_duration'] += insight.omc_duration or 0
        
        # Status metrics
        status = insight.omc_status
        if status and status != 'unknown':
            if status not in state['status_metrics']:
                state['status_metrics'][status] = {
                    'count': 0,
                    'total_duration': 0,
                    'patterns': []
                }
            
            state['status_metrics'][status]['count'] += 1
            state['status_metrics'][status]['total_duration'] += insight.omc_duration or 0
        
        # Collect patterns
        if insight.is_short_call and insight.early_termination_reasons:
            state['short_call_patterns'].append({
                'call_id': insight.call_id,
                'reasons': insight.early_termination_reasons,
                'agent': insight.omc_agent
            })
        
        if not insight.is_short_call and insight.success_factors:
            state['long_call_patterns'].append({
                'call_id': insight.call_id,
                'factors': insight.success_factors,
                'agent': insight.omc_agent
            })
        
        # Collect LGS issues
        if insight.lgs_issues:
            state['lgs_issues'].extend(insight.lgs_issues)
        
        # Collect examples (limit to 5 each)
        if insight.is_short_call and len(state['example_short_calls']) < 5:
            state['example_short_calls'].append({
                'call_id': insight.call_id,
                'agent': insight.omc_agent,
                'duration': insight.omc_duration,
                'reasons': insight.early_termination_reasons,
                'quotes': insight.notable_quotes
            })
        
        if not insight.is_short_call and len(state['example_successful_calls']) < 5:
            state['example_successful_calls'].append({
                'call_id': insight.call_id,
                'agent': insight.omc_agent,
                'duration': insight.omc_duration,
                'factors': insight.success_factors,
                'quotes': insight.notable_quotes
            })
    
    logger.info(f"Metrics accumulated. Total agents tracked: {len(state['agent_metrics'])}")
    return state


def check_completion_node(state: AnalysisState) -> AnalysisState:
    """
    Check if all batches are processed
    
    Args:
        state: Current analysis state
        
    Returns:
        Updated state with completion flag
    """
    processed = state.get('processed_count', 0)
    total = state.get('total_rows', 0)
    
    logger.info(f"Progress check: {processed}/{total} rows processed")
    
    if processed >= total:
        state['ready_for_report'] = True
        logger.info("All batches processed. Ready for report generation.")
    else:
        state['ready_for_report'] = False
        logger.info(f"More batches to process. {total - processed} rows remaining.")
    
    return state

