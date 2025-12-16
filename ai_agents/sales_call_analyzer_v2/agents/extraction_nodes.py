"""
LangGraph Nodes for Sales Call Extraction Agent
Implements proper agentic workflow with nodes, edges, and state management
"""
from typing import Dict, Any
from graph.state import AgentState
from llm.gemini_client import GeminiClient
from prompts.prompt_templates import format_extraction_prompt
from schemas.extraction_schemas import SalesCallExtraction
from utils.logger import get_logger, get_sales_logger

logger = get_logger()
sales_logger = get_sales_logger()


# Initialize Gemini client (singleton)
gemini_client = GeminiClient()


def prepare_extraction_node(state: AgentState) -> AgentState:
    """
    Node 1: Prepare the extraction by loading prompts and setting up state.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state
    """
    logger.info(f"Preparing extraction for Row {state['row_number']} (ID: {state['row_id']})")
    
    # Log extraction start
    sales_logger.log_extraction_start(state['row_id'], state['row_number'])
    
    # Update state
    state['next_action'] = 'extract'
    state['extraction_success'] = False
    state['error_message'] = None
    
    return state


def extract_data_node(state: AgentState) -> AgentState:
    """
    Node 2: Extract structured data from the sales call using Gemini.
    This is the core extraction node that calls the LLM.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state with extraction result
    """
    row_id = state['row_id']
    row_number = state['row_number']
    
    logger.info(f"Extracting data for Row {row_number} (ID: {row_id})")
    
    try:
        # Determine if this is a retry
        is_retry = state['attempt_count'] > 1
        
        # Format the prompt
        prompt = format_extraction_prompt(
            call_date=state['call_date'],
            fullname=state['fullname'],
            length_in_sec=state['length_in_sec'],
            transcription=state['transcription'],
            is_retry=is_retry,
            error_message=state.get('error_message', '')
        )
        
        # Log LLM call
        sales_logger.log_llm_call("gemini-2.5-flash-lite", row_id)
        
        # Call Gemini with structured output
        metadata = {
            "row_id": row_id,
            "row_number": row_number,
            "attempt": state['attempt_count'],
            "call_date": state['call_date'],
            "fullname": state['fullname']
        }
        
        extraction_result = gemini_client.extract_structured_data(
            prompt=prompt,
            row_id=row_id,
            metadata=metadata
        )
        
        # Log LLM response
        sales_logger.log_llm_response(row_id, True)
        
        # Update state with successful extraction
        state['extraction_result'] = extraction_result
        state['extraction_success'] = True
        state['next_action'] = 'validate'
        
        logger.info(f"Successfully extracted data for Row {row_number}")
        
    except Exception as e:
        # Log LLM response failure
        sales_logger.log_llm_response(row_id, False)
        
        error_msg = str(e)
        logger.error(f"Extraction failed for Row {row_number}: {error_msg}")
        
        # Update state with error
        state['extraction_success'] = False
        state['error_message'] = error_msg
        state['next_action'] = 'check_retry'
    
    return state


def validate_extraction_node(state: AgentState) -> AgentState:
    """
    Node 3: Validate the extracted data.
    Ensures all required fields are present and properly formatted.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state
    """
    row_id = state['row_id']
    row_number = state['row_number']
    
    logger.info(f"Validating extraction for Row {row_number}")
    
    try:
        extraction_result = state['extraction_result']
        
        # Basic validation checks
        if extraction_result is None:
            raise ValueError("Extraction result is None")
        
        # Check that all main categories are present
        required_fields = [
            'customer_engagement',
            'call_opening',
            'objection_handling',
            'pace_control',
            'emotional_tone',
            'outcome_timing'
        ]
        
        for field in required_fields:
            if not hasattr(extraction_result, field):
                raise ValueError(f"Missing required field: {field}")
            
            field_value = getattr(extraction_result, field)
            if field_value is None:
                raise ValueError(f"Field {field} is None")
        
        # Validation passed
        logger.info(f"Validation passed for Row {row_number}")
        state['next_action'] = 'complete'
        
    except Exception as e:
        error_msg = f"Validation failed: {str(e)}"
        logger.error(f"Validation failed for Row {row_number}: {error_msg}")
        
        # Update state with validation error
        state['extraction_success'] = False
        state['error_message'] = error_msg
        state['next_action'] = 'check_retry'
    
    return state


def check_retry_node(state: AgentState) -> AgentState:
    """
    Node 4: Check if we should retry the extraction.
    Determines whether to retry or mark as failed.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state
    """
    row_id = state['row_id']
    row_number = state['row_number']
    attempt_count = state['attempt_count']
    max_attempts = state['max_attempts']
    
    if attempt_count < max_attempts:
        # Retry
        logger.warning(f"Retry attempt {attempt_count + 1}/{max_attempts} for Row {row_number}")
        sales_logger.log_retry_attempt(row_id, attempt_count + 1, max_attempts)
        
        state['attempt_count'] += 1
        state['should_retry'] = True
        state['next_action'] = 'extract'
        
    else:
        # Max retries reached, mark as failed
        logger.error(f"Max retries reached for Row {row_number}. Marking as failed.")
        
        state['should_retry'] = False
        state['next_action'] = 'fail'
    
    return state


def complete_extraction_node(state: AgentState) -> AgentState:
    """
    Node 5: Complete the extraction successfully.
    Final node for successful extractions.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state
    """
    row_id = state['row_id']
    row_number = state['row_number']
    
    logger.info(f"Extraction complete for Row {row_number}")
    sales_logger.log_extraction_success(row_id, row_number)
    
    state['extraction_success'] = True
    state['next_action'] = 'complete'
    
    return state


def fail_extraction_node(state: AgentState) -> AgentState:
    """
    Node 6: Handle failed extraction after max retries.
    Final node for failed extractions.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state
    """
    row_id = state['row_id']
    row_number = state['row_number']
    error_message = state.get('error_message', 'Unknown error')
    
    logger.error(f"Extraction failed permanently for Row {row_number}")
    sales_logger.log_extraction_failure(row_id, row_number, error_message)
    
    # Create a failed extraction result with NaN/empty values
    state['extraction_result'] = None
    state['extraction_success'] = False
    state['next_action'] = 'fail'
    
    return state


def route_next_action(state: AgentState) -> str:
    """
    Routing function to determine the next node based on state.
    This is used by LangGraph to determine the workflow path.
    
    Args:
        state: Current agent state
    
    Returns:
        Name of the next node to execute
    """
    next_action = state.get('next_action', 'extract')
    
    routing_map = {
        'extract': 'extract_data',
        'validate': 'validate_extraction',
        'check_retry': 'check_retry',
        'complete': 'complete_extraction',
        'fail': 'fail_extraction'
    }
    
    return routing_map.get(next_action, 'extract_data')

