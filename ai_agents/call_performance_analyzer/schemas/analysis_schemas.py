"""
Pydantic schemas for call performance analysis
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# SCRIPT COMPLIANCE ENUMS AND CONSTANTS
# ============================================================================

class ScriptSectionEnum(str, Enum):
    """10 Mandatory Script Sections"""
    INTRO = "1_intro"
    QUALIFYING = "2_qualifying"
    PROBLEM_SETUP = "3_problem_setup"
    PITCH = "4_pitch"
    OFFER_CLOSE = "5_offer_close"
    INFO_CHECK = "6_info_check"
    SMS_AGREEMENT = "7_sms_agreement"
    TIMELINE_EXPECTATIONS = "8_timeline_expectations"
    OPENING_OBJECTIONS = "9_opening_objections"
    CLOSING_OBJECTIONS = "10_closing_objections"


class NonComplianceReasonEnum(str, Enum):
    """Reasons why script was not followed"""
    CUSTOMER_HUNG_UP_IMMEDIATELY = "customer_hung_up_immediately"
    CUSTOMER_OBJECTION_INTERRUPTED = "customer_objection_interrupted"
    TECHNICAL_CONNECTION_ISSUES = "technical_connection_issues"
    NOT_DECISION_MAKER = "not_decision_maker"
    WRONG_TIMING_BUSY = "wrong_timing_busy"
    LANGUAGE_BARRIER = "language_barrier"
    CUSTOMER_ALREADY_CLIENT = "customer_already_client"
    CUSTOMER_NOT_INTERESTED_UPFRONT = "customer_not_interested_upfront"
    AGENT_SKIPPED_SECTIONS = "agent_skipped_sections"
    AGENT_DEVIATED_FROM_SCRIPT = "agent_deviated_from_script"


class ObjectionTypeEnum(str, Enum):
    """Types of objections from the script"""
    # Opening Objections
    FULLY_BOOKED = "fully_booked"
    ALREADY_HAVE_WEBSITE = "already_have_website"
    TOO_MANY_CUSTOMERS = "too_many_customers"
    BUSY_RIGHT_NOW = "busy_right_now"
    WHATS_THIS_ABOUT = "whats_this_about"
    COSTS_MONEY = "costs_money"
    ALREADY_HAVE_MARKETING = "already_have_marketing"
    # Closing Objections
    SEND_EMAIL = "send_email"
    NO_MONEY_BUDGET = "no_money_budget"
    NO_TIME_TOO_BUSY = "no_time_too_busy"
    DRIVING_CALL_BACK = "driving_call_back"
    NO_URGENCY = "no_urgency"
    NO_TRUST = "no_trust"
    NO_CARD = "no_card"
    PREPAID_CARD = "prepaid_card"
    BAD_REVIEWS = "bad_reviews"
    BAD_EXPERIENCE = "bad_experience"
    TALK_TO_PARTNER = "talk_to_partner"
    TRIAL_CANCELLATION = "trial_cancellation"
    OTHER = "other"


class RebuttalQualityEnum(str, Enum):
    """Quality of rebuttal delivery"""
    EXCELLENT = "excellent"  # Closely follows script with AVQ pattern
    GOOD = "good"           # Paraphrased but captures key elements
    PARTIAL = "partial"     # Some elements present but incomplete
    POOR = "poor"           # Rebuttal attempted but ineffective
    NONE = "none"           # No rebuttal provided


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
    is_short_call: bool = Field(default=False, description="Whether call is under 5 minutes")
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
    
    # Examples (for report) - ENHANCED
    notable_quotes: Optional[List[str]] = Field(default_factory=list, description="Notable quotes from call")
    critical_moment_quote: Optional[str] = Field(default=None, description="The single most critical moment in the call with exact quote")
    proof_of_issue: Optional[str] = Field(default=None, description="Verbatim proof of the main issue identified")
    proof_of_success: Optional[str] = Field(default=None, description="Verbatim proof of success technique (for long calls)")
    
    # Transferable Wisdom (for successful calls)
    transferable_technique: Optional[str] = Field(default=None, description="Specific technique that can be taught to others")
    technique_application: Optional[str] = Field(default=None, description="How to apply this technique in other scenarios")
    agent_persona_insight: Optional[str] = Field(default=None, description="What makes this agent's approach unique and effective")
    
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


# ============================================================================
# SCRIPT COMPLIANCE SCHEMAS - NEW SECTION
# ============================================================================

class ScriptSectionCompliance(BaseModel):
    """Compliance analysis for a single script section"""
    section_name: str = Field(description="Name of the script section (1-10)")
    section_number: int = Field(description="Section number (1-10)")
    was_attempted: bool = Field(default=False, description="Whether agent attempted this section")
    compliance_percentage: float = Field(default=0.0, description="How well the section was followed (0-100%)")
    key_elements_covered: List[str] = Field(default_factory=list, description="Key elements from script that were covered")
    key_elements_missed: List[str] = Field(default_factory=list, description="Key elements that were missed")
    agent_verbatim: Optional[str] = Field(default=None, description="Exact quote showing agent's attempt")
    notes: Optional[str] = Field(default=None, description="Additional observations")


class ObjectionRebuttalAnalysis(BaseModel):
    """Analysis of a single objection-rebuttal exchange"""
    objection_type: str = Field(description="Type of objection raised")
    customer_objection_verbatim: str = Field(description="Exact customer objection quote")
    was_rebuttal_attempted: bool = Field(default=False, description="Did agent attempt a rebuttal?")
    rebuttal_quality: str = Field(default="none", description="Quality: excellent/good/partial/poor/none")
    agent_rebuttal_verbatim: Optional[str] = Field(default=None, description="Agent's rebuttal quote")
    followed_avq_pattern: bool = Field(default=False, description="Did agent use Acknowledge-Value-Question pattern?")
    returned_to_script: bool = Field(default=False, description="Did agent return to the calling script after rebuttal?")
    script_section_returned_to: Optional[str] = Field(default=None, description="Which section agent returned to")
    timestamp_in_call: Optional[str] = Field(default=None, description="When in the call this occurred (early/mid/late)")


class ScriptComplianceInsight(BaseModel):
    """Complete script compliance analysis for a single call"""
    call_id: str = Field(description="Unique call identifier")
    omc_agent: Optional[str] = Field(default=None, description="OMC agent name")
    call_duration_seconds: int = Field(default=0, description="Call duration in seconds")
    
    # Overall Script Compliance
    is_script_followed: bool = Field(default=False, description="Whether script was meaningfully followed")
    overall_compliance_percentage: float = Field(default=0.0, description="Overall script adherence (0-100%)")
    compliance_tier: str = Field(default="low", description="low (<40%), medium (40-70%), high (>70%)")
    
    # Section-by-Section Analysis
    sections_attempted: int = Field(default=0, description="Number of sections attempted (out of 10)")
    sections_completed_well: int = Field(default=0, description="Sections with >60% compliance")
    section_compliance: List[ScriptSectionCompliance] = Field(
        default_factory=list, 
        description="Detailed compliance for each of 10 sections"
    )
    
    # Script Flow Analysis
    followed_correct_sequence: bool = Field(default=False, description="Did agent follow 1→2→3→... sequence?")
    sequence_deviations: List[str] = Field(default_factory=list, description="Where sequence was broken")
    
    # Non-Compliance Reasons (if script not followed)
    non_compliance_reason: Optional[str] = Field(default=None, description="Primary reason script wasn't followed")
    non_compliance_category: str = Field(default="unknown", description="External factor / Agent error / Customer interruption")
    non_compliance_details: Optional[str] = Field(default=None, description="Detailed explanation")
    non_compliance_verbatim_proof: Optional[str] = Field(default=None, description="Quote proving why script wasn't followed")
    
    # Objection Handling Analysis
    total_objections_raised: int = Field(default=0, description="Total objections from customer")
    objections_with_rebuttals: int = Field(default=0, description="Objections that received rebuttals")
    objection_analyses: List[ObjectionRebuttalAnalysis] = Field(
        default_factory=list,
        description="Detailed analysis of each objection-rebuttal exchange"
    )
    
    # Post-Rebuttal Script Return
    returned_to_script_after_objection: bool = Field(default=False, description="Did agent return to script after handling objections?")
    script_recovery_quality: str = Field(default="none", description="How well agent recovered: excellent/good/partial/poor/none")
    
    # Call Duration vs Script Compliance
    call_exceeded_5_minutes: bool = Field(default=False, description="Did call go beyond 5 minutes?")
    script_compliance_with_long_call: bool = Field(default=False, description="Script followed AND call >5 min")
    
    # Key Insights
    strongest_sections: List[str] = Field(default_factory=list, description="Best performed sections")
    weakest_sections: List[str] = Field(default_factory=list, description="Sections needing improvement")
    specific_recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    
    # Evidence
    best_practice_quote: Optional[str] = Field(default=None, description="Quote showing good script adherence")
    improvement_needed_quote: Optional[str] = Field(default=None, description="Quote showing area for improvement")
    
    # Metadata
    analysis_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    analysis_success: bool = Field(default=True)
    analysis_error: Optional[str] = Field(default=None)


class AgentScriptComplianceMetrics(BaseModel):
    """Agent-level script compliance aggregated metrics"""
    agent_name: str = Field(description="Agent name")
    total_calls_analyzed: int = Field(default=0, description="Total calls for this agent")
    
    # Compliance Stats
    calls_script_followed: int = Field(default=0, description="Calls where script was followed")
    script_compliance_rate: float = Field(default=0.0, description="% of calls with script followed")
    avg_compliance_percentage: float = Field(default=0.0, description="Average compliance score")
    
    # Duration Stats
    calls_exceeding_5_min: int = Field(default=0, description="Calls > 5 minutes")
    script_followed_and_long: int = Field(default=0, description="Script followed AND > 5 min")
    
    # Section Performance
    best_sections: List[str] = Field(default_factory=list, description="Sections this agent does well")
    weakest_sections: List[str] = Field(default_factory=list, description="Sections needing work")
    avg_sections_attempted: float = Field(default=0.0, description="Average sections attempted per call")
    
    # Objection Handling
    total_objections_faced: int = Field(default=0, description="Total objections across all calls")
    objections_with_rebuttals: int = Field(default=0, description="Objections with rebuttal attempts")
    rebuttal_rate: float = Field(default=0.0, description="% of objections that got rebuttals")
    avg_rebuttal_quality: str = Field(default="none", description="Average rebuttal quality")
    returns_to_script_rate: float = Field(default=0.0, description="% of times agent returns to script after objection")
    
    # Non-Compliance Patterns
    common_non_compliance_reasons: List[str] = Field(default_factory=list, description="Top reasons for non-compliance")


class ScriptComplianceSummary(BaseModel):
    """Overall script compliance summary for all calls"""
    total_calls_analyzed: int = Field(default=0, description="Total calls analyzed")
    
    # Core Metrics (Questions 1-2)
    calls_script_followed_count: int = Field(default=0, description="Q1: Calls where script was followed")
    calls_script_followed_percentage: float = Field(default=0.0, description="Q1: % of calls with script followed")
    
    script_followed_and_over_5min_count: int = Field(default=0, description="Q2: Script followed AND > 5 min")
    script_followed_and_over_5min_percentage: float = Field(default=0.0, description="Q2: % of script-followed calls > 5 min")
    
    # Non-Compliance Analysis (Question 3)
    non_compliance_breakdown: Dict[str, int] = Field(
        default_factory=dict, 
        description="Q3: Breakdown by reason category"
    )
    external_factors_count: int = Field(default=0, description="Non-compliance due to external factors")
    client_interruption_count: int = Field(default=0, description="Non-compliance due to client interruptions")
    agent_error_count: int = Field(default=0, description="Non-compliance due to agent errors")
    
    # Objection Handling (Questions 4-5)
    total_objections_raised: int = Field(default=0, description="Q4: Total objections across all calls")
    objections_with_correct_rebuttal: int = Field(default=0, description="Q4: Objections with proper rebuttal")
    rebuttal_accuracy_rate: float = Field(default=0.0, description="Q4: % of correct rebuttals used")
    
    objections_with_script_return: int = Field(default=0, description="Q5: Objections after which agent returned to script")
    script_return_rate: float = Field(default=0.0, description="Q5: % of times agent returns to script")
    
    # Compliance Tier Distribution
    high_compliance_calls: int = Field(default=0, description="Calls with >70% compliance")
    medium_compliance_calls: int = Field(default=0, description="Calls with 40-70% compliance")
    low_compliance_calls: int = Field(default=0, description="Calls with <40% compliance")
    
    # Section-Level Stats
    section_compliance_avg: Dict[str, float] = Field(
        default_factory=dict,
        description="Average compliance % for each section"
    )
    most_followed_sections: List[str] = Field(default_factory=list, description="Best followed sections overall")
    least_followed_sections: List[str] = Field(default_factory=list, description="Sections most often skipped/poorly done")
    
    # Agent Rankings
    top_compliant_agents: List[str] = Field(default_factory=list, description="Agents with best script compliance")
    agents_needing_training: List[str] = Field(default_factory=list, description="Agents needing script training")
    
    # Recommendations
    key_findings: List[str] = Field(default_factory=list, description="Top findings from compliance analysis")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")

