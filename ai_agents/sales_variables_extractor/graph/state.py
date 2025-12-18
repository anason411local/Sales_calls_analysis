"""
LangGraph State Definition for Sales Variables Extraction
Defines the state structure that flows through the agentic workflow
"""
from typing import TypedDict, Optional, Any, Dict
from schemas.variable_schemas import LGSExtractedVariables, OMCExtractedVariables


class AgentState(TypedDict):
    """
    State that flows through the LangGraph workflow.
    Contains all data needed for extraction and tracking.
    """
    # Row identification
    lead_id: str
    row_number: int
    
    # LGS Input Data
    lgs_user: Optional[str]
    lgs_event_time: Optional[str]
    lgs_duration: Optional[int]
    lgs_transcription: Optional[str]
    
    # OMC Input Data
    omc_user: Optional[str]
    omc_call_date: Optional[str]
    omc_duration: Optional[int]
    omc_transcription: Optional[str]
    
    # Common Data
    customer_address: Optional[str]
    service: Optional[str]
    customer_name: Optional[str]
    
    # Reference Data
    seasonality_data: Optional[str]
    
    # LGS Extraction State
    lgs_variables: Optional[LGSExtractedVariables]
    lgs_extraction_success: bool
    lgs_error_message: Optional[str]
    lgs_attempt_count: int
    lgs_should_retry: bool
    
    # OMC Extraction State
    omc_variables: Optional[OMCExtractedVariables]
    omc_extraction_success: bool
    omc_error_message: Optional[str]
    omc_attempt_count: int
    omc_should_retry: bool
    
    # Overall State
    extraction_phase: str  # "prepare", "extract_lgs", "extract_omc", "complete", "fail"
    max_attempts: int
    extraction_complete: bool
    
    # Routing
    next_action: str  # Determines which node to execute next

