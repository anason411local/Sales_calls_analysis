"""
Pydantic Schemas for Sales Variables Extraction
Defines the structure of extracted variables from LGS and OMC calls
"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# LGS (Lead Generation Specialist) Variables Schemas
# ============================================================================

class TimingSeasonalityVariables(BaseModel):
    """Timing and Seasonality related variables"""
    timezone: Optional[str] = Field(None, description="Time zone based on customer address")
    season_status: Optional[str] = Field(None, description="High/Low season for the service in that location")
    season_month: Optional[str] = Field(None, description="Current month for seasonality assessment")


class LGSAgentVariables(BaseModel):
    """LGS Agent specific variables"""
    lgs_sentiment_style: Optional[str] = Field(
        None, 
        description="Agent's style: Expert, Confident & Assumptive, Consultative & Validating, Robotic & Script-Bound, Hesitant & Apologetic, Urgent & Pressing"
    )
    lgs_agent_gender: Optional[str] = Field(None, description="Male/Female/unknown")
    
    # Qualifying variables
    is_decision_maker: Optional[str] = Field(None, description="Yes/No/unknown - Business owner or decision maker")
    ready_for_customers: Optional[str] = Field(None, description="Yes/No/unknown - Ready to take on more customers")
    forbidden_industry: Optional[str] = Field(None, description="Yes/No/unknown - Falls into forbidden industries")
    ready_to_transfer: Optional[str] = Field(None, description="Yes/No/unknown - Agreed to be transferred")
    lgs_call_not_transferred: Optional[str] = Field(None, description="Yes/No/unknown - Was call transferred? If not, why?")
    
    # Customer variables
    customer_sentiment: Optional[str] = Field(None, description="Angry, Happy, Neutral, etc.")
    customer_language: Optional[str] = Field(None, description="English/Spanish/Unknown")
    customer_knows_marketing: Optional[str] = Field(None, description="Yes/No/unknown - Understands it's a marketing call")
    customer_availability: Optional[str] = Field(None, description="busy/available/unknown")
    who_said_hello_first: Optional[str] = Field(None, description="Customer/Agent/unknown")
    customer_marketing_experience: Optional[str] = Field(None, description="Novice/Skeptic/Transactional/Expert")
    
    # Technical quality
    technical_quality_score: Optional[float] = Field(None, description="0-5 score for call technical quality")
    technical_quality_issues: Optional[str] = Field(None, description="List of technical issues detected")


class LGSExtractedVariables(BaseModel):
    """Complete LGS extracted variables"""
    timing_seasonality: TimingSeasonalityVariables
    agent_variables: LGSAgentVariables


# ============================================================================
# OMC (Outbound Marketing Closer) Variables Schemas
# ============================================================================

class CustomerEngagement(BaseModel):
    """Customer Engagement & Interest metrics"""
    customer_talk_percentage: Optional[float] = Field(None, description="Percentage of conversation by customer")
    agent_talk_percentage: Optional[float] = Field(None, description="Percentage of conversation by agent")
    talk_ratio_classification: Optional[str] = Field(None, description="Mutual Dialogue/Agent-Heavy/Customer-Heavy")
    
    total_discovery_questions: Optional[int] = Field(None, description="Total discovery questions asked")
    goal1_questions: Optional[int] = Field(None, description="Demographics/Operations questions")
    goal2_questions: Optional[int] = Field(None, description="Competition/Marketing questions")
    goal3_questions: Optional[int] = Field(None, description="Practical Need/Mindset questions")
    discovery_quality: Optional[str] = Field(None, description="Surface-Level/Moderate Depth/Deep Discovery")
    advanced_discovery_used: Optional[str] = Field(None, description="Yes/No - Peeling the onion technique used")
    
    total_buying_signals: Optional[int] = Field(None, description="Number of buying signals detected")
    total_resistance_signals: Optional[int] = Field(None, description="Number of resistance signals detected")
    signal_ratio: Optional[str] = Field(None, description="Buying:Resistance signal ratio")
    customer_sentiment: Optional[str] = Field(None, description="Interested/Neutral/Resistant")


class CallOpening(BaseModel):
    """Call Opening & Framing metrics"""
    omc_agent_sentiment_style: Optional[str] = Field(
        None,
        description="OMC Agent's style: Expert, Confident & Assumptive, Consultative & Validating, Robotic & Script-Bound, Hesitant & Apologetic, Urgent & Pressing"
    )
    omc_who_said_hello_first: Optional[str] = Field(None, description="Customer/Agent/unknown - Who greeted first in OMC call")
    time_to_reason_seconds: Optional[int] = Field(None, description="Seconds to state reason for call and value")
    business_type_mentioned: Optional[str] = Field(None, description="Yes/No - Business type mentioned")
    location_mentioned: Optional[str] = Field(None, description="Yes/No - Location mentioned")
    within_45_seconds: Optional[str] = Field(None, description="Yes/No - Business & location within 30-45 seconds")
    call_structure_framed: Optional[str] = Field(None, description="Yes/No - Call structure communicated upfront")
    call_structure_clarity: Optional[str] = Field(None, description="Description of how call structure was framed")


class ObjectionHandling(BaseModel):
    """Objection Handling & Friction metrics"""
    total_objections: Optional[int] = Field(None, description="Total objections raised")
    objections_acknowledged: Optional[int] = Field(None, description="Objections acknowledged by agent")
    objections_rebutted: Optional[int] = Field(None, description="Objections rebutted by agent")
    acknowledgement_rate: Optional[float] = Field(None, description="Percentage of objections acknowledged")
    
    price_mentions_final_2min: Optional[int] = Field(None, description="Price mentions in final 2 minutes")
    timeline_mentions_final_2min: Optional[int] = Field(None, description="Timeline mentions in final 2 minutes")
    contract_mentions_final_2min: Optional[int] = Field(None, description="Contract mentions in final 2 minutes")
    price_timeline_contract_before_dropoff: Optional[int] = Field(None, description="Total price/timeline/contract mentions before drop-off")
    roi_calculation_presented: Optional[str] = Field(None, description="Yes/No - ROI calculation presented")


class PaceControl(BaseModel):
    """Pace, Control, and Interruptions metrics"""
    average_monologue_length: Optional[float] = Field(None, description="Average sentences per agent turn")
    longest_monologue_length: Optional[int] = Field(None, description="Longest monologue in sentences")
    extended_monologues_count: Optional[int] = Field(None, description="Number of monologues >5 sentences")
    short_monologues: Optional[int] = Field(None, description="1-2 sentences")
    medium_monologues: Optional[int] = Field(None, description="3-5 sentences")
    long_monologues: Optional[int] = Field(None, description="6-10 sentences")
    very_long_monologues: Optional[int] = Field(None, description=">10 sentences")
    
    total_interruptions: Optional[int] = Field(None, description="Times agent interrupted customer")
    interruption_rate: Optional[float] = Field(None, description="Interruptions per minute")
    interruption_pattern: Optional[str] = Field(None, description="Frequent/Occasional/Rare/None")
    conversation_balance: Optional[str] = Field(None, description="Mutual/Agent-Heavy/Choppy")
    
    script_adherence: Optional[str] = Field(None, description="Structured/Somewhat Structured/Unstructured")
    stages_skipped: Optional[str] = Field(None, description="List of skipped stages or 'None'")
    stages_out_of_order: Optional[str] = Field(None, description="Stages completed out of order")
    premature_closing_attempt: Optional[str] = Field(None, description="Yes/No - Premature closing detected")


class EmotionalTone(BaseModel):
    """Emotional Tone & Rapport metrics"""
    name_used_first_minute: Optional[str] = Field(None, description="Yes/No")
    name_usage_count: Optional[int] = Field(None, description="Times customer name used in first minute")
    rapport_elements_count: Optional[int] = Field(None, description="Rapport elements in first minute")
    tone_assessment: Optional[str] = Field(None, description="Warm/Professional/Cold/Rushed")
    personal_greeting: Optional[str] = Field(None, description="Yes/No")
    common_ground_established: Optional[str] = Field(None, description="Yes/No")
    
    sentiment_progression: Optional[str] = Field(None, description="Improved/Stable/Declined/Fluctuated")
    sentiment_opening: Optional[str] = Field(None, description="Positive/Neutral/Negative/Skeptical - 0:00-2:00")
    sentiment_early_middle: Optional[str] = Field(None, description="Positive/Neutral/Negative/Skeptical - 2:00-5:00")
    sentiment_late_middle: Optional[str] = Field(None, description="Positive/Neutral/Negative/Skeptical - 5:00-end-2min")
    sentiment_closing: Optional[str] = Field(None, description="Positive/Neutral/Negative/Skeptical - final 2 min")
    notable_sentiment_shifts: Optional[str] = Field(None, description="Description of sentiment changes")
    
    customer_frustrations: Optional[str] = Field(None, description="Number of frustrations expressed or 'Not Found'")
    empathy_responses: Optional[int] = Field(None, description="Number of empathy responses")
    empathy_response_rate: Optional[float] = Field(None, description="Percentage of frustrations with empathy")


class OutcomeTiming(BaseModel):
    """Outcome and Timing Markers"""
    total_call_duration: Optional[int] = Field(None, description="Call duration in seconds")
    disconnect_stage: Optional[str] = Field(None, description="Stage where call ended")
    hang_up_initiated_by: Optional[str] = Field(None, description="Customer/Agent/Mutual")
    time_in_final_stage: Optional[int] = Field(None, description="Seconds spent in final stage before disconnect")
    
    commitment_type: Optional[str] = Field(None, description="Type of commitment secured or 'None'")
    commitment_clarity: Optional[str] = Field(None, description="Explicit/Implied/Vague/None")
    assumptive_language_used: Optional[str] = Field(None, description="Yes/No - Assumptive closing language detected")
    full_sale_closed: Optional[str] = Field(None, description="Yes/No")
    payment_info_collected: Optional[str] = Field(None, description="Yes/No")
    followup_scheduled: Optional[str] = Field(None, description="Yes/No")
    
    call_result_tag: Optional[str] = Field(
        None, 
        description="Sale Completed, Early Disconnect, Disconnect - During Discovery, etc."
    )
    primary_disconnect_reason: Optional[str] = Field(None, description="Main reason for call ending")


class OMCExtractedVariables(BaseModel):
    """Complete OMC extracted variables from sales_data_extraction_prompt"""
    customer_engagement: CustomerEngagement
    call_opening: CallOpening
    objection_handling: ObjectionHandling
    pace_control: PaceControl
    emotional_tone: EmotionalTone
    outcome_timing: OutcomeTiming


# ============================================================================
# Combined Output Schema
# ============================================================================

class SalesVariablesExtraction(BaseModel):
    """Complete extraction result for a single row"""
    # Metadata
    lead_id: str
    row_number: int
    
    # LGS Variables
    lgs_variables: Optional[LGSExtractedVariables] = None
    lgs_extraction_success: bool = False
    lgs_error_message: Optional[str] = None
    
    # OMC Variables
    omc_variables: Optional[OMCExtractedVariables] = None
    omc_extraction_success: bool = False
    omc_error_message: Optional[str] = None
    
    # Overall status
    extraction_complete: bool = False

