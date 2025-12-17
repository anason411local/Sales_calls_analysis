"""
Pydantic schemas for call performance analysis
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class CallInsight(BaseModel):
    """Individual call analysis insight"""
    call_id: str = Field(description="Unique call identifier")
    call_date: Optional[str] = Field(default=None, description="Date of the call")
    
    # LGS Data
    lgs_agent: Optional[str] = Field(default=None, description="LGS agent name")
    lgs_transcription: Optional[str] = Field(default=None, description="LGS call transcription")
    lgs_quality_score: Optional[int] = Field(default=None, description="LGS handoff quality (1-10)")
    lgs_issues: Optional[List[str]] = Field(default_factory=list, description="Issues identified in LGS call")
    lgs_strengths: Optional[List[str]] = Field(default_factory=list, description="Strengths in LGS call")
    
    # OMC Data
    omc_agent: Optional[str] = Field(default=None, description="OMC agent name")
    omc_transcription: Optional[str] = Field(default=None, description="OMC call transcription")
    omc_duration: Optional[int] = Field(default=None, description="OMC call duration in seconds")
    omc_status: Optional[str] = Field(default=None, description="Call outcome status")
    
    # Analysis
    is_short_call: bool = Field(default=False, description="Whether call is under 2 minutes")
    call_category: str = Field(default="unknown", description="Short (<2min) or Long (>=2min)")
    
    # Patterns & Issues
    early_termination_reasons: Optional[List[str]] = Field(default_factory=list, description="Why call ended early")
    success_factors: Optional[List[str]] = Field(default_factory=list, description="Factors contributing to success")
    objections_raised: Optional[List[str]] = Field(default_factory=list, description="Customer objections")
    objection_handling: Optional[str] = Field(default=None, description="How objections were handled")
    
    # Engagement Metrics
    customer_engagement_level: Optional[str] = Field(default=None, description="Low/Medium/High")
    agent_performance_rating: Optional[int] = Field(default=None, description="Agent performance (1-10)")
    
    # Recommendations
    specific_recommendations: Optional[List[str]] = Field(default_factory=list, description="Actionable recommendations")
    
    # Examples (for report)
    notable_quotes: Optional[List[str]] = Field(default_factory=list, description="Notable quotes from call")
    
    # Metadata
    analysis_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    analysis_success: bool = Field(default=True)
    analysis_error: Optional[str] = Field(default=None)


class AgentPerformance(BaseModel):
    """Agent-level performance metrics"""
    agent_name: str
    total_calls: int = 0
    short_calls_count: int = 0
    long_calls_count: int = 0
    avg_call_duration: float = 0.0
    success_rate: float = 0.0
    common_issues: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    performance_score: float = 0.0
    recommendations: List[str] = Field(default_factory=list)


class DailyTrend(BaseModel):
    """Daily performance trends"""
    date: str
    total_calls: int = 0
    short_calls: int = 0
    long_calls: int = 0
    avg_duration: float = 0.0
    success_rate: float = 0.0


class StatusAnalysis(BaseModel):
    """Analysis by status/outcome"""
    status: str
    count: int = 0
    avg_duration: float = 0.0
    common_patterns: List[str] = Field(default_factory=list)


class ComprehensiveReport(BaseModel):
    """Final comprehensive analysis report"""
    
    # Executive Summary
    total_calls_analyzed: int = 0
    analysis_period: str = ""
    overall_success_rate: float = 0.0
    avg_call_duration: float = 0.0
    
    # Key Findings
    short_calls_percentage: float = 0.0
    long_calls_percentage: float = 0.0
    top_issues_short_calls: List[str] = Field(default_factory=list)
    success_patterns_long_calls: List[str] = Field(default_factory=list)
    
    # LGS vs OMC
    lgs_handoff_quality_avg: float = 0.0
    lgs_issues_identified: List[str] = Field(default_factory=list)
    omc_performance_issues: List[str] = Field(default_factory=list)
    
    # Agent Performance
    top_performers: List[AgentPerformance] = Field(default_factory=list)
    agents_needing_support: List[AgentPerformance] = Field(default_factory=list)
    
    # Trends
    daily_trends: List[DailyTrend] = Field(default_factory=list)
    status_breakdown: List[StatusAnalysis] = Field(default_factory=list)
    
    # Recommendations
    immediate_actions: List[str] = Field(default_factory=list)
    training_recommendations: List[str] = Field(default_factory=list)
    process_improvements: List[str] = Field(default_factory=list)
    
    # Real Examples
    example_short_calls: List[Dict] = Field(default_factory=list)
    example_successful_calls: List[Dict] = Field(default_factory=list)
    
    # Metadata
    report_generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

