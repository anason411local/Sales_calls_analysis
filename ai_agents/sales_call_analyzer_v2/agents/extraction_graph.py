"""
LangGraph Workflow Definition for Sales Call Extraction
Builds the complete agentic workflow using LangGraph StateGraph
"""
from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.extraction_nodes import (
    prepare_extraction_node,
    extract_data_node,
    validate_extraction_node,
    check_retry_node,
    complete_extraction_node,
    fail_extraction_node,
    route_next_action
)
from utils.logger import get_logger

logger = get_logger()


def create_extraction_graph() -> StateGraph:
    """
    Create the LangGraph workflow for sales call extraction.
    
    This defines the complete agentic workflow with nodes and edges:
    1. Prepare extraction
    2. Extract data from LLM
    3. Validate extraction
    4. Check if retry needed
    5. Complete or fail
    
    Returns:
        Compiled StateGraph ready for execution
    """
    
    # Initialize the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("prepare_extraction", prepare_extraction_node)
    workflow.add_node("extract_data", extract_data_node)
    workflow.add_node("validate_extraction", validate_extraction_node)
    workflow.add_node("check_retry", check_retry_node)
    workflow.add_node("complete_extraction", complete_extraction_node)
    workflow.add_node("fail_extraction", fail_extraction_node)
    
    # Set entry point
    workflow.set_entry_point("prepare_extraction")
    
    # Add edges
    # From prepare -> extract
    workflow.add_edge("prepare_extraction", "extract_data")
    
    # From extract -> conditional routing
    workflow.add_conditional_edges(
        "extract_data",
        route_next_action,
        {
            "validate_extraction": "validate_extraction",
            "check_retry": "check_retry"
        }
    )
    
    # From validate -> conditional routing
    workflow.add_conditional_edges(
        "validate_extraction",
        route_next_action,
        {
            "complete_extraction": "complete_extraction",
            "check_retry": "check_retry"
        }
    )
    
    # From check_retry -> conditional routing
    workflow.add_conditional_edges(
        "check_retry",
        route_next_action,
        {
            "extract_data": "extract_data",
            "fail_extraction": "fail_extraction"
        }
    )
    
    # Terminal nodes
    workflow.add_edge("complete_extraction", END)
    workflow.add_edge("fail_extraction", END)
    
    # Compile the graph
    compiled_graph = workflow.compile()
    
    logger.info("LangGraph extraction workflow created successfully")
    
    return compiled_graph


# Create the global graph instance
extraction_graph = create_extraction_graph()


def run_extraction(
    row_id: str,
    row_number: int,
    call_date: str,
    length_in_sec: int,
    transcription: str,
    fullname: str,
    system_instructions: str,
    extraction_prompt: str,
    max_attempts: int = 3
) -> AgentState:
    """
    Run the extraction workflow for a single sales call.
    
    Args:
        row_id: Unique identifier for the row
        row_number: Row number in the dataset
        call_date: Date of the call
        length_in_sec: Call duration in seconds
        transcription: Full call transcript
        fullname: Name of the sales rep
        system_instructions: System instructions for the agent
        extraction_prompt: Extraction prompt template
        max_attempts: Maximum retry attempts
    
    Returns:
        Final agent state after workflow completion
    """
    
    # Initialize state
    initial_state: AgentState = {
        "row_id": row_id,
        "row_number": row_number,
        "call_date": call_date,
        "length_in_sec": length_in_sec,
        "transcription": transcription,
        "fullname": fullname,
        "system_instructions": system_instructions,
        "extraction_prompt": extraction_prompt,
        "extraction_result": None,
        "attempt_count": 1,
        "max_attempts": max_attempts,
        "extraction_success": False,
        "error_message": None,
        "llm_response": None,
        "should_retry": False,
        "next_action": "extract"
    }
    
    # Run the graph
    logger.info(f"Starting extraction workflow for Row {row_number} (ID: {row_id})")
    
    try:
        final_state = extraction_graph.invoke(initial_state)
        return final_state
    
    except Exception as e:
        logger.error(f"Extraction workflow failed for Row {row_number}: {str(e)}")
        initial_state["extraction_success"] = False
        initial_state["error_message"] = str(e)
        return initial_state

