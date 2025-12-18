"""
LangGraph Workflow for Sales Variables Extraction
Builds the complete agentic workflow using LangGraph StateGraph
"""
from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.extraction_nodes import (
    prepare_extraction_node,
    extract_lgs_node,
    extract_omc_node,
    check_lgs_retry_node,
    check_omc_retry_node,
    complete_extraction_node,
    route_next_action
)
from utils.logger import get_logger

logger = get_logger()


def create_extraction_graph() -> StateGraph:
    """
    Create the LangGraph workflow for sales variables extraction.
    
    This defines the complete agentic workflow with nodes and edges:
    1. Prepare extraction
    2. Extract LGS variables
    3. Check LGS retry if needed
    4. Extract OMC variables
    5. Check OMC retry if needed
    6. Complete extraction
    
    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("Creating extraction graph")
    
    # Initialize the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("prepare_extraction", prepare_extraction_node)
    workflow.add_node("extract_lgs", extract_lgs_node)
    workflow.add_node("extract_omc", extract_omc_node)
    workflow.add_node("check_lgs_retry", check_lgs_retry_node)
    workflow.add_node("check_omc_retry", check_omc_retry_node)
    workflow.add_node("complete_extraction", complete_extraction_node)
    
    # Set entry point
    workflow.set_entry_point("prepare_extraction")
    
    # Add conditional edges from prepare_extraction
    workflow.add_conditional_edges(
        "prepare_extraction",
        route_next_action,
        {
            "extract_lgs": "extract_lgs",
            "extract_omc": "extract_omc",
            "complete_extraction": "complete_extraction"
        }
    )
    
    # Add conditional edges from extract_lgs
    workflow.add_conditional_edges(
        "extract_lgs",
        route_next_action,
        {
            "extract_omc": "extract_omc",
            "check_lgs_retry": "check_lgs_retry",
            "complete_extraction": "complete_extraction"
        }
    )
    
    # Add conditional edges from check_lgs_retry
    workflow.add_conditional_edges(
        "check_lgs_retry",
        route_next_action,
        {
            "extract_lgs": "extract_lgs",
            "extract_omc": "extract_omc",
            "complete_extraction": "complete_extraction"
        }
    )
    
    # Add conditional edges from extract_omc
    workflow.add_conditional_edges(
        "extract_omc",
        route_next_action,
        {
            "check_omc_retry": "check_omc_retry",
            "complete_extraction": "complete_extraction"
        }
    )
    
    # Add conditional edges from check_omc_retry
    workflow.add_conditional_edges(
        "check_omc_retry",
        route_next_action,
        {
            "extract_omc": "extract_omc",
            "complete_extraction": "complete_extraction"
        }
    )
    
    # Terminal node
    workflow.add_edge("complete_extraction", END)
    
    # Compile the graph
    compiled_graph = workflow.compile()
    
    logger.info("Extraction graph created successfully")
    
    return compiled_graph


# Create the global graph instance
extraction_graph = create_extraction_graph()


def run_extraction(
    lead_id: str,
    row_number: int,
    lgs_user: str,
    lgs_event_time: str,
    lgs_duration: int,
    lgs_transcription: str,
    omc_user: str,
    omc_call_date: str,
    omc_duration: int,
    omc_transcription: str,
    customer_address: str,
    service: str,
    customer_name: str,
    seasonality_data: str,
    max_attempts: int = 3
) -> AgentState:
    """
    Run the extraction workflow for a single row.
    
    Args:
        lead_id: Unique lead identifier
        row_number: Row number in dataset
        lgs_user: LGS agent name
        lgs_event_time: LGS event timestamp
        lgs_duration: LGS call duration
        lgs_transcription: LGS transcription
        omc_user: OMC agent name
        omc_call_date: OMC call date
        omc_duration: OMC call duration
        omc_transcription: OMC transcription
        customer_address: Customer address
        service: Service type
        customer_name: Customer name
        seasonality_data: Seasonality reference data
        max_attempts: Maximum retry attempts
    
    Returns:
        Final agent state after workflow completion
    """
    # Initialize state
    initial_state: AgentState = {
        "lead_id": lead_id,
        "row_number": row_number,
        "lgs_user": lgs_user,
        "lgs_event_time": lgs_event_time,
        "lgs_duration": lgs_duration,
        "lgs_transcription": lgs_transcription,
        "omc_user": omc_user,
        "omc_call_date": omc_call_date,
        "omc_duration": omc_duration,
        "omc_transcription": omc_transcription,
        "customer_address": customer_address,
        "service": service,
        "customer_name": customer_name,
        "seasonality_data": seasonality_data,
        "lgs_variables": None,
        "lgs_extraction_success": False,
        "lgs_error_message": None,
        "lgs_attempt_count": 1,
        "lgs_should_retry": False,
        "omc_variables": None,
        "omc_extraction_success": False,
        "omc_error_message": None,
        "omc_attempt_count": 1,
        "omc_should_retry": False,
        "extraction_phase": "prepare",
        "max_attempts": max_attempts,
        "extraction_complete": False,
        "next_action": "prepare"
    }
    
    # Run the graph
    logger.info(f"Starting extraction workflow for Row {row_number} (ID: {lead_id})")
    
    try:
        final_state = extraction_graph.invoke(initial_state)
        return final_state
    
    except Exception as e:
        logger.error(f"Extraction workflow failed for Row {row_number}: {str(e)}")
        initial_state["extraction_complete"] = True
        initial_state["lgs_error_message"] = str(e)
        initial_state["omc_error_message"] = str(e)
        return initial_state

