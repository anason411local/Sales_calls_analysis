"""
LangGraph State Definition for Sales Call Extraction Agent
"""
from typing import TypedDict, Optional, Dict, Any, List
from schemas.extraction_schemas import SalesCallExtraction


class AgentState(TypedDict):
    """
    State for the Sales Call Extraction Agent.
    This state is passed between all nodes in the LangGraph workflow.
    """
    # Input data
    row_id: str
    row_number: int
    call_date: str
    length_in_sec: int
    transcription: str
    fullname: str
    
    # System prompts
    system_instructions: str
    extraction_prompt: str
    
    # Extraction result
    extraction_result: Optional[SalesCallExtraction]
    
    # Processing metadata
    attempt_count: int
    max_attempts: int
    extraction_success: bool
    error_message: Optional[str]
    
    # LLM response (raw)
    llm_response: Optional[Dict[str, Any]]
    
    # Workflow control
    should_retry: bool
    next_action: str  # "extract", "validate", "retry", "complete", "fail"


class BatchState(TypedDict):
    """
    State for batch processing workflow.
    """
    # Batch information
    batch_number: int
    batch_rows: List[Dict[str, Any]]
    
    # Processing results
    successful_extractions: List[SalesCallExtraction]
    failed_rows: List[Dict[str, Any]]
    
    # Progress tracking
    total_processed: int
    total_success: int
    total_failed: int
    
    # Checkpoint data
    last_processed_row: int
    checkpoint_saved: bool

