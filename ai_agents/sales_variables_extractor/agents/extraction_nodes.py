"""
LangGraph Nodes for Sales Variables Extraction
Implements the agentic workflow with specialized nodes for each extraction phase
"""
from typing import Dict, Any
from graph.state import AgentState
from llm.gemini_client import GeminiClient
from prompts.prompt_templates import format_lgs_extraction_prompt, format_omc_extraction_prompt
from utils.logger import get_logger, get_extraction_logger
from datetime import datetime

logger = get_logger()
extraction_logger = get_extraction_logger()

# Initialize Gemini client (singleton)
gemini_client = GeminiClient()


def prepare_extraction_node(state: AgentState) -> AgentState:
    """
    Node 1: Prepare the extraction by initializing state and logging start.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state
    """
    logger.info(f"Preparing extraction for Row {state['row_number']} (ID: {state['lead_id']})")
    
    # Log extraction start
    extraction_logger.log_extraction_start(state['lead_id'], state['row_number'])
    
    # Initialize extraction state
    state['lgs_extraction_success'] = False
    state['omc_extraction_success'] = False
    state['lgs_attempt_count'] = 1
    state['omc_attempt_count'] = 1
    state['lgs_should_retry'] = False
    state['omc_should_retry'] = False
    state['extraction_complete'] = False
    state['extraction_phase'] = 'prepare'
    
    # Determine next action based on available data
    if state.get('lgs_transcription'):
        state['next_action'] = 'extract_lgs'
    elif state.get('omc_transcription'):
        state['next_action'] = 'extract_omc'
    else:
        logger.warning(f"No transcription data available for Row {state['row_number']}")
        state['next_action'] = 'complete'
        state['extraction_complete'] = True
    
    return state


def extract_lgs_node(state: AgentState) -> AgentState:
    """
    Node 2: Extract LGS variables from the transcription.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state with LGS extraction results
    """
    row_id = state['lead_id']
    row_number = state['row_number']
    
    logger.info(f"Extracting LGS variables for Row {row_number}")
    
    try:
        # Check if LGS transcription is available
        if not state.get('lgs_transcription'):
            logger.warning(f"No LGS transcription for Row {row_number}, skipping LGS extraction")
            state['lgs_extraction_success'] = False
            state['lgs_error_message'] = "No LGS transcription available"
            state['next_action'] = 'extract_omc' if state.get('omc_transcription') else 'complete'
            return state
        
        # Determine if this is a retry
        is_retry = state['lgs_attempt_count'] > 1
        
        # Format the LGS extraction prompt
        prompt = format_lgs_extraction_prompt(
            lgs_user=state.get('lgs_user', ''),
            lgs_event_time=state.get('lgs_event_time', ''),
            lgs_duration=state.get('lgs_duration', 0),
            lgs_transcription=state['lgs_transcription'],
            customer_address=state.get('customer_address', ''),
            service=state.get('service', ''),
            seasonality_data=state.get('seasonality_data', ''),
            is_retry=is_retry,
            error_message=state.get('lgs_error_message', '')
        )
        
        # Call Gemini to extract LGS variables
        metadata = {
            "row_id": row_id,
            "row_number": row_number,
            "attempt": state['lgs_attempt_count'],
            "extraction_type": "LGS"
        }
        
        lgs_variables = gemini_client.extract_lgs_variables(
            prompt=prompt,
            row_id=row_id,
            metadata=metadata
        )
        
        # Update state with successful extraction
        state['lgs_variables'] = lgs_variables
        state['lgs_extraction_success'] = True
        state['lgs_error_message'] = None
        
        # Log success
        extraction_logger.log_lgs_success(row_id, row_number)
        
        # Move to OMC extraction if available
        if state.get('omc_transcription'):
            state['next_action'] = 'extract_omc'
        else:
            state['next_action'] = 'complete'
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"LGS extraction failed for Row {row_number}: {error_msg}")
        
        # Update state with error
        state['lgs_extraction_success'] = False
        state['lgs_error_message'] = error_msg
        
        # Log failure
        extraction_logger.log_lgs_failure(row_id, row_number, error_msg)
        
        # Determine if we should retry
        state['next_action'] = 'check_lgs_retry'
    
    return state


def extract_omc_node(state: AgentState) -> AgentState:
    """
    Node 3: Extract OMC variables from the transcription.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state with OMC extraction results
    """
    row_id = state['lead_id']
    row_number = state['row_number']
    
    logger.info(f"Extracting OMC variables for Row {row_number}")
    
    try:
        # Check if OMC transcription is available
        if not state.get('omc_transcription'):
            logger.warning(f"No OMC transcription for Row {row_number}, skipping OMC extraction")
            state['omc_extraction_success'] = False
            state['omc_error_message'] = "No OMC transcription available"
            state['next_action'] = 'complete'
            return state
        
        # Determine if this is a retry
        is_retry = state['omc_attempt_count'] > 1
        
        # Format the OMC extraction prompt
        prompt = format_omc_extraction_prompt(
            omc_user=state.get('omc_user', ''),
            omc_call_date=state.get('omc_call_date', ''),
            omc_duration=state.get('omc_duration', 0),
            omc_transcription=state['omc_transcription'],
            service=state.get('service', ''),
            is_retry=is_retry,
            error_message=state.get('omc_error_message', '')
        )
        
        # Call Gemini to extract OMC variables
        metadata = {
            "row_id": row_id,
            "row_number": row_number,
            "attempt": state['omc_attempt_count'],
            "extraction_type": "OMC"
        }
        
        omc_variables = gemini_client.extract_omc_variables(
            prompt=prompt,
            row_id=row_id,
            metadata=metadata
        )
        
        # Update state with successful extraction
        state['omc_variables'] = omc_variables
        state['omc_extraction_success'] = True
        state['omc_error_message'] = None
        
        # Log success
        extraction_logger.log_omc_success(row_id, row_number)
        
        # Move to completion
        state['next_action'] = 'complete'
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"OMC extraction failed for Row {row_number}: {error_msg}")
        
        # Update state with error
        state['omc_extraction_success'] = False
        state['omc_error_message'] = error_msg
        
        # Log failure
        extraction_logger.log_omc_failure(row_id, row_number, error_msg)
        
        # Determine if we should retry
        state['next_action'] = 'check_omc_retry'
    
    return state


def check_lgs_retry_node(state: AgentState) -> AgentState:
    """
    Node 4: Check if LGS extraction should be retried.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state with retry decision
    """
    row_id = state['lead_id']
    row_number = state['row_number']
    attempt_count = state['lgs_attempt_count']
    max_attempts = state['max_attempts']
    
    if attempt_count < max_attempts:
        # Retry LGS extraction
        logger.warning(f"Retrying LGS extraction for Row {row_number} (Attempt {attempt_count + 1}/{max_attempts})")
        extraction_logger.log_retry(row_id, attempt_count + 1, max_attempts)
        
        state['lgs_attempt_count'] += 1
        state['lgs_should_retry'] = True
        state['next_action'] = 'extract_lgs'
    else:
        # Max retries reached, move to OMC or complete
        logger.error(f"Max LGS retries reached for Row {row_number}")
        state['lgs_should_retry'] = False
        
        if state.get('omc_transcription'):
            state['next_action'] = 'extract_omc'
        else:
            state['next_action'] = 'complete'
    
    return state


def check_omc_retry_node(state: AgentState) -> AgentState:
    """
    Node 5: Check if OMC extraction should be retried.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state with retry decision
    """
    row_id = state['lead_id']
    row_number = state['row_number']
    attempt_count = state['omc_attempt_count']
    max_attempts = state['max_attempts']
    
    if attempt_count < max_attempts:
        # Retry OMC extraction
        logger.warning(f"Retrying OMC extraction for Row {row_number} (Attempt {attempt_count + 1}/{max_attempts})")
        extraction_logger.log_retry(row_id, attempt_count + 1, max_attempts)
        
        state['omc_attempt_count'] += 1
        state['omc_should_retry'] = True
        state['next_action'] = 'extract_omc'
    else:
        # Max retries reached, complete
        logger.error(f"Max OMC retries reached for Row {row_number}")
        state['omc_should_retry'] = False
        state['next_action'] = 'complete'
    
    return state


def complete_extraction_node(state: AgentState) -> AgentState:
    """
    Node 6: Complete the extraction and finalize state.
    
    Args:
        state: Current agent state
    
    Returns:
        Final agent state
    """
    row_id = state['lead_id']
    row_number = state['row_number']
    
    logger.info(f"Completing extraction for Row {row_number}")
    
    # Mark extraction as complete
    state['extraction_complete'] = True
    state['extraction_phase'] = 'complete'
    state['next_action'] = 'end'
    
    # Log complete success if both extractions succeeded
    if state['lgs_extraction_success'] and state['omc_extraction_success']:
        extraction_logger.log_complete_success(row_id, row_number)
    
    return state


def route_next_action(state: AgentState) -> str:
    """
    Routing function to determine the next node based on state.
    
    Args:
        state: Current agent state
    
    Returns:
        Name of the next node to execute
    """
    next_action = state.get('next_action', 'prepare')
    
    routing_map = {
        'prepare': 'prepare_extraction',
        'extract_lgs': 'extract_lgs',
        'extract_omc': 'extract_omc',
        'check_lgs_retry': 'check_lgs_retry',
        'check_omc_retry': 'check_omc_retry',
        'complete': 'complete_extraction',
        'end': 'END'
    }
    
    return routing_map.get(next_action, 'prepare_extraction')

