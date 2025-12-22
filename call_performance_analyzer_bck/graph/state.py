"""
LangGraph state management for call performance analysis
"""
from typing import TypedDict, List, Dict, Optional
from schemas.analysis_schemas import CallInsight


class AnalysisState(TypedDict):
    """
    State for the call performance analysis workflow
    
    This state accumulates insights across batches and maintains
    all data needed for final report generation.
    """
    # Current batch processing
    current_batch: List[Dict]  # Current batch of rows being processed
    batch_number: int  # Current batch number
    total_rows: int  # Total rows to process
    
    # Accumulated insights from all batches
    all_insights: List[CallInsight]  # All call insights collected
    
    # Aggregated metrics (accumulated across batches)
    agent_metrics: Dict[str, Dict]  # Agent name -> metrics
    daily_metrics: Dict[str, Dict]  # Date -> metrics
    status_metrics: Dict[str, Dict]  # Status -> metrics
    
    # Pattern tracking
    short_call_patterns: List[Dict]  # Patterns in <2min calls
    long_call_patterns: List[Dict]  # Patterns in >=2min calls
    lgs_issues: List[str]  # LGS issues identified
    omc_issues: List[str]  # OMC issues identified
    
    # Examples for report
    example_short_calls: List[Dict]  # Example short calls
    example_successful_calls: List[Dict]  # Example successful calls
    
    # Processing metadata
    processed_count: int  # Number of rows processed
    failed_count: int  # Number of failed analyses
    retry_queue: List[Dict]  # Failed rows to retry
    
    # Final report flag
    ready_for_report: bool  # Whether all processing is complete
    final_report: Optional[str]  # Generated markdown report
    
    # Error tracking
    errors: List[Dict]  # Errors encountered during processing

