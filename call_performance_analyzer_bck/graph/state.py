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
    
    # First 5 Minutes Analysis (NEW)
    first_5min_short_call_failures: List[Dict]  # What failed in first 5 min of short calls
    first_5min_long_call_successes: List[Dict]  # What worked in first 5 min of long calls
    first_5min_key_phrases_success: List[str]  # Key phrases that worked
    first_5min_key_phrases_failure: List[str]  # Key phrases that failed
    first_5min_opening_techniques_success: List[Dict]  # Successful opening techniques
    first_5min_opening_techniques_failure: List[Dict]  # Failed opening techniques
    first_5min_engagement_hooks: List[str]  # Hooks that kept customers engaged
    first_5min_turning_points: List[Dict]  # Turning points in calls
    first_5min_verbiage_comparison: Dict[str, List[str]]  # Comparison of verbiage: success vs failure
    
    # Agent Performance Overview (High-Level Metrics from External Source)
    agent_performance_overview: Dict  # DPAD, Conversion Rate, Payability metrics per agent
    
    # Processing metadata
    processed_count: int  # Number of rows processed
    failed_count: int  # Number of failed analyses
    retry_queue: List[Dict]  # Failed rows to retry
    
    # Final report flag
    ready_for_report: bool  # Whether all processing is complete
    final_report: Optional[str]  # Generated markdown report
    
    # Error tracking
    errors: List[Dict]  # Errors encountered during processing

