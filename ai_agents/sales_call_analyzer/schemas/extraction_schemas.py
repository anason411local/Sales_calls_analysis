"""
Pydantic schemas for sales call data extraction.
Comprehensive models covering all 6 categories from the extraction framework.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# CATEGORY I: CUSTOMER ENGAGEMENT & INTEREST
# ============================================================================

class TalkRatioData(BaseModel):
    """I.1 Customer vs Agent Talk Ratio"""
    total_agent_turns: int = Field(description="Total number of agent speaking turns")
    total_customer_turns: int = Field(description="Total number of customer speaking turns")
    agent_percentage: float = Field(description="Percentage of conversation by agent")
    customer_percentage: float = Field(description="Percentage of conversation by customer")
    classification: Literal["Mutual Dialogue", "Agent-Heavy", "Customer-Heavy"] = Field(
        description="Talk ratio classification"
    )
    agent_verbiage_sample: Optional[str] = Field(None, description="Representative agent speaking pattern")
    customer_verbiage_sample: Optional[str] = Field(None, description="Representative customer speaking pattern")


class DiscoveryQuestion(BaseModel):
    """Individual discovery question data"""
    question_text: str = Field(description="The discovery question asked")
    asked: bool = Field(description="Whether the question was asked")
    timestamp: Optional[str] = Field(None, description="Timestamp in MM:SS format")
    agent_verbiage: Optional[str] = Field(None, description="Exact quote from agent")
    customer_response: Optional[str] = Field(None, description="Customer's response")


class DiscoveryQuestionsData(BaseModel):
    """I.2 Discovery Questions Asked Before Disengage"""
    # Goal 1 - Demographics/Operations (9 questions)
    goal1_q1_business_duration: DiscoveryQuestion
    goal1_q2_service_type: DiscoveryQuestion
    goal1_q3_service_radius: DiscoveryQuestion
    goal1_q4_top_services: DiscoveryQuestion
    goal1_q5_team_size: DiscoveryQuestion
    goal1_q6_work_location: DiscoveryQuestion
    goal1_q7_equipment: DiscoveryQuestion
    goal1_q8_business_motivation: DiscoveryQuestion
    goal1_total: int = Field(description="Total Goal 1 questions asked")
    
    # Goal 2 - Competition/Marketing (6 questions)
    goal2_q1_website: DiscoveryQuestion
    goal2_q2_marketing_management: DiscoveryQuestion
    goal2_q3_advertising_type: DiscoveryQuestion
    goal2_q4_advertising_spend: DiscoveryQuestion
    goal2_q5_services_for_price: DiscoveryQuestion
    goal2_q6_prospect_sources: DiscoveryQuestion
    goal2_total: int = Field(description="Total Goal 2 questions asked")
    
    # Goal 3 - Practical Need/Mindset (4 questions)
    goal3_q1_google_usage: DiscoveryQuestion
    goal3_q2_search_success: DiscoveryQuestion
    goal3_q3_phone_usage_observation: DiscoveryQuestion
    goal3_q4_others_online_behavior: DiscoveryQuestion
    goal3_total: int = Field(description="Total Goal 3 questions asked")
    
    # Advanced Discovery
    advanced_initial_pain_point_asked: bool = Field(description="Initial open-ended pain point question asked")
    advanced_initial_question_verbiage: Optional[str] = Field(None, description="Initial pain point question")
    advanced_probing_done: bool = Field(description="Agent probed deeper with follow-ups")
    advanced_probing_verbiage: Optional[str] = Field(None, description="Probing questions asked")
    
    # Summary
    total_discovery_questions: int = Field(description="Total discovery questions across all goals")
    quality_assessment: Literal["Surface-Level", "Moderate Depth", "Deep Discovery"] = Field(
        description="Quality of discovery process"
    )


class BuyingSignal(BaseModel):
    """Individual buying signal"""
    signal_type: str = Field(description="Type of buying signal")
    detected: bool = Field(description="Whether signal was detected")
    timestamp: Optional[str] = Field(None, description="Timestamp in MM:SS format")
    customer_verbiage: Optional[str] = Field(None, description="Customer's exact words")


class ResistanceSignal(BaseModel):
    """Individual resistance signal"""
    signal_type: str = Field(description="Type of resistance signal")
    detected: bool = Field(description="Whether signal was detected")
    timestamp: Optional[str] = Field(None, description="Timestamp in MM:SS format")
    customer_verbiage: Optional[str] = Field(None, description="Customer's exact words")


class SignalsData(BaseModel):
    """I.3 Buying Signals vs Resistance Signals"""
    # Buying Signals
    buying_asks_about_results: BuyingSignal
    buying_asks_about_price: BuyingSignal
    buying_asks_about_next_steps: BuyingSignal
    buying_asks_about_timeline: BuyingSignal
    buying_positive_sentiment: BuyingSignal
    total_buying_signals: int = Field(description="Total buying signals detected")
    
    # Resistance Signals
    resistance_price_pushback: ResistanceSignal
    resistance_not_interested: ResistanceSignal
    resistance_bad_experience: ResistanceSignal
    resistance_timing_concerns: ResistanceSignal
    resistance_budget_constraints: ResistanceSignal
    total_resistance_signals: int = Field(description="Total resistance signals detected")
    
    # Summary
    signal_ratio: str = Field(description="Ratio of buying to resistance signals (X:Y)")
    overall_sentiment: Literal["Interested", "Neutral", "Resistant"] = Field(
        description="Overall customer sentiment"
    )


class CustomerEngagementData(BaseModel):
    """Complete Category I: Customer Engagement & Interest"""
    talk_ratio: TalkRatioData
    discovery_questions: DiscoveryQuestionsData
    signals: SignalsData


# ============================================================================
# CATEGORY II: CALL OPENING & FRAMING
# ============================================================================

class TimeToReasonData(BaseModel):
    """II.1 Time to State Clear Reason for Call"""
    initial_greeting_timestamp: str = Field(description="Timestamp of initial greeting (MM:SS)")
    reason_stated_timestamp: str = Field(description="Timestamp when reason was stated (MM:SS)")
    time_elapsed_seconds: int = Field(description="Seconds elapsed between greeting and reason")
    reason_verbiage: Optional[str] = Field(None, description="Exact quote of reason for call")
    reason_clear: bool = Field(description="Whether reason was stated clearly")
    complete_opening_statement: Optional[str] = Field(None, description="Complete opening through reason")


class PersonalizationData(BaseModel):
    """II.2 Business Type & Location Referenced in First 30-45 Seconds"""
    business_type_mentioned: bool = Field(description="Business type mentioned")
    business_type_timestamp: Optional[str] = Field(None, description="Timestamp of business type mention")
    business_type_verbiage: Optional[str] = Field(None, description="Exact quote mentioning business type")
    
    location_mentioned: bool = Field(description="Location mentioned")
    location_timestamp: Optional[str] = Field(None, description="Timestamp of location mention")
    location_verbiage: Optional[str] = Field(None, description="Exact quote mentioning location")
    
    within_30_seconds: bool = Field(description="Personalization within first 30 seconds")
    within_45_seconds: bool = Field(description="Personalization within first 45 seconds")
    personalization_quality: Literal["Generic", "Specific", "Highly Tailored"] = Field(
        description="Quality of personalization"
    )


class CallStructureData(BaseModel):
    """II.3 Clarity of Call Structure Communicated Up Front"""
    structure_mentioned: bool = Field(description="Call structure mentioned")
    structure_timestamp: Optional[str] = Field(None, description="Timestamp of structure framing")
    framing_phrases: Optional[str] = Field(None, description="Exact framing phrases used")
    
    time_expectation_set: bool = Field(description="Time expectation communicated")
    time_expectation_verbiage: Optional[str] = Field(None, description="Time expectation quote")
    
    purpose_stated: bool = Field(description="Call purpose stated")
    purpose_verbiage: Optional[str] = Field(None, description="Purpose statement quote")
    
    process_outlined: bool = Field(description="Process outlined")
    process_verbiage: Optional[str] = Field(None, description="Process outline quote")


class CallOpeningData(BaseModel):
    """Complete Category II: Call Opening & Framing"""
    time_to_reason: TimeToReasonData
    personalization: PersonalizationData
    call_structure: CallStructureData


# ============================================================================
# CATEGORY III: OBJECTION HANDLING & FRICTION
# ============================================================================

class ObjectionInstance(BaseModel):
    """Individual objection and response"""
    objection_number: int = Field(description="Objection sequence number")
    objection_type: Literal["Price", "Timeline", "Previous Experience", "Contract", "Value", "Other"] = Field(
        description="Type of objection"
    )
    timestamp: str = Field(description="Timestamp in MM:SS format")
    customer_verbiage: str = Field(description="Exact objection quote")
    agent_acknowledged: bool = Field(description="Agent acknowledged the objection")
    agent_response_verbiage: Optional[str] = Field(None, description="Agent's response quote")
    rebuttal_provided: bool = Field(description="Agent provided a rebuttal")


class ObjectionHandlingData(BaseModel):
    """III.1 Objections Raised and Rebutted"""
    objections: List[ObjectionInstance] = Field(default_factory=list, description="List of all objections")
    total_objections: int = Field(description="Total objections raised")
    total_acknowledged: int = Field(description="Total objections acknowledged")
    total_rebutted: int = Field(description="Total objections rebutted")
    total_unaddressed: int = Field(description="Total unaddressed objections")


class AcknowledgementPattern(BaseModel):
    """Acknowledgement phrase pattern"""
    phrase: str = Field(description="Acknowledgement phrase")
    used: bool = Field(description="Whether phrase was used")
    count: int = Field(description="Number of times used")


class AcknowledgementData(BaseModel):
    """III.2 Agent Acknowledged Objection First"""
    objection_acknowledgements: List[dict] = Field(
        default_factory=list,
        description="Acknowledgement details for each objection"
    )
    
    # Common patterns
    pattern_thank_you: AcknowledgementPattern
    pattern_frustrating: AcknowledgementPattern
    pattern_long_time: AcknowledgementPattern
    pattern_absolutely_right: AcknowledgementPattern
    pattern_understand: AcknowledgementPattern
    other_patterns: List[str] = Field(default_factory=list, description="Other acknowledgement phrases")
    
    acknowledgement_rate: float = Field(description="Percentage of objections acknowledged")


class FrictionMention(BaseModel):
    """Price/Timeline/Contract mention"""
    mention_type: Literal["Price", "Timeline", "Contract"] = Field(description="Type of mention")
    timestamp: str = Field(description="Timestamp in MM:SS format")
    verbiage: str = Field(description="Exact quote")
    in_final_2_minutes: bool = Field(description="Whether mention was in final 2 minutes")


class FrictionData(BaseModel):
    """III.3 Price, Timeline, or Contract Mentions Near Drop-Off"""
    price_mentions: List[FrictionMention] = Field(default_factory=list)
    timeline_mentions: List[FrictionMention] = Field(default_factory=list)
    contract_mentions: List[FrictionMention] = Field(default_factory=list)
    
    total_price_mentions: int = Field(description="Total price mentions in call")
    price_mentions_final_2min: int = Field(description="Price mentions in final 2 minutes")
    
    total_timeline_mentions: int = Field(description="Total timeline mentions in call")
    timeline_mentions_final_2min: int = Field(description="Timeline mentions in final 2 minutes")
    
    total_contract_mentions: int = Field(description="Total contract mentions in call")
    contract_mentions_final_2min: int = Field(description="Contract mentions in final 2 minutes")
    
    roi_discussed: bool = Field(description="ROI/value calculation presented")
    roi_timestamp: Optional[str] = Field(None, description="ROI discussion timestamp")
    roi_verbiage: Optional[str] = Field(None, description="ROI discussion quote")
    roi_used_customer_data: bool = Field(description="ROI calculation used customer's data")
    
    correlation_to_dropoff: Literal["High", "Medium", "Low", "N/A"] = Field(
        description="Correlation between mentions and call end"
    )


class ObjectionFrictionData(BaseModel):
    """Complete Category III: Objection Handling & Friction"""
    objection_handling: ObjectionHandlingData
    acknowledgement: AcknowledgementData
    friction: FrictionData


# ============================================================================
# CATEGORY IV: PACE, CONTROL, AND INTERRUPTIONS
# ============================================================================

class MonologueData(BaseModel):
    """IV.1 Average Monologue Length of Agent"""
    total_agent_turns: int = Field(description="Total agent speaking turns")
    extended_monologues_count: int = Field(description="Number of monologues >5 sentences")
    longest_monologue_duration: str = Field(description="Longest monologue duration (seconds/sentences)")
    longest_monologue_verbiage: Optional[str] = Field(None, description="Longest monologue quote")
    average_monologue_length: str = Field(description="Average monologue length (seconds/sentences)")
    
    short_monologues: int = Field(description="Count of 1-2 sentence monologues")
    medium_monologues: int = Field(description="Count of 3-5 sentence monologues")
    long_monologues: int = Field(description="Count of 6-10 sentence monologues")
    very_long_monologues: int = Field(description="Count of >10 sentence monologues")
    
    conversation_balance: Literal["Mutual", "Agent-Heavy", "Choppy"] = Field(
        description="Overall conversation balance"
    )


class InterruptionInstance(BaseModel):
    """Individual interruption"""
    interruption_number: int = Field(description="Interruption sequence number")
    timestamp: str = Field(description="Timestamp in MM:SS format")
    customer_incomplete_thought: str = Field(description="What customer was saying")
    agent_interruption: str = Field(description="What agent interrupted with")
    interruption_type: Literal["Cutting off", "Talking over", "Finishing sentence"] = Field(
        description="Type of interruption"
    )


class InterruptionData(BaseModel):
    """IV.2 Instances Where Agent Interrupts Customer"""
    interruptions: List[InterruptionInstance] = Field(default_factory=list)
    total_interruptions: int = Field(description="Total interruption count")
    interruption_rate: float = Field(description="Interruptions per minute")
    pattern_analysis: Literal["Frequent", "Occasional", "Rare", "None"] = Field(
        description="Interruption pattern"
    )


class ScriptStage(BaseModel):
    """Individual script stage"""
    stage_number: int = Field(description="Stage number in sequence")
    stage_name: str = Field(description="Name of the stage")
    present: bool = Field(description="Whether stage was present")
    timestamp: Optional[str] = Field(None, description="Timestamp in MM:SS format")
    skipped: bool = Field(description="Whether stage was skipped")


class ScriptDeviationData(BaseModel):
    """IV.3 Deviation from Expected Script Order"""
    stage_1_introduction: ScriptStage
    stage_2_reason_for_call: ScriptStage
    stage_3_discovery_questions: ScriptStage
    stage_4_fomo_competitor: ScriptStage
    stage_5_value_proposition: ScriptStage
    stage_6_roi_calculation: ScriptStage
    stage_7_assume_sale: ScriptStage
    stage_8_call_control: ScriptStage
    
    out_of_order_segments: List[str] = Field(default_factory=list, description="Segments done out of order")
    skipped_segments: List[str] = Field(default_factory=list, description="Segments skipped entirely")
    repeated_segments: List[str] = Field(default_factory=list, description="Segments repeated")
    premature_closing: bool = Field(description="Premature closing attempt detected")
    premature_closing_timestamp: Optional[str] = Field(None, description="Premature closing timestamp")
    returned_to_earlier_stage: bool = Field(description="Returned to earlier stage")
    return_details: Optional[str] = Field(None, description="Details of stage return")
    
    flow_assessment: Literal["Structured", "Somewhat Structured", "Unstructured"] = Field(
        description="Overall script flow assessment"
    )


class PaceControlData(BaseModel):
    """Complete Category IV: Pace, Control, and Interruptions"""
    monologue: MonologueData
    interruptions: InterruptionData
    script_deviation: ScriptDeviationData


# ============================================================================
# CATEGORY V: EMOTIONAL TONE & RAPPORT
# ============================================================================

class RapportMomentsData(BaseModel):
    """V.1 Rapport Moments in First Minute"""
    customer_name_used: bool = Field(description="Customer name used in first minute")
    name_usage_count: int = Field(description="Number of times name used")
    name_usage_timestamps: List[str] = Field(default_factory=list, description="Timestamps of name usage")
    name_usage_verbiage: Optional[str] = Field(None, description="Examples of name usage")
    
    context_reference_made: bool = Field(description="Context reference made")
    context_type: Optional[str] = Field(None, description="Type of context reference")
    context_verbiage: Optional[str] = Field(None, description="Context reference quote")
    
    pleasantry_small_talk: bool = Field(description="Pleasantry or small talk present")
    pleasantry_verbiage: Optional[str] = Field(None, description="Pleasantry quote")
    
    tone_assessment: Literal["Warm", "Professional", "Cold", "Rushed"] = Field(
        description="Tone in first minute"
    )
    
    personal_greeting: bool = Field(description="Personal greeting used")
    previous_interaction_reference: bool = Field(description="Reference to previous interaction")
    common_ground_established: bool = Field(description="Common ground established")
    genuine_interest_expressed: bool = Field(description="Genuine interest expressed")


class SentimentSegment(BaseModel):
    """Customer sentiment in a time segment"""
    segment_name: str = Field(description="Name of time segment")
    time_range: str = Field(description="Time range (MM:SS-MM:SS)")
    sentiment: Literal["Positive", "Neutral", "Negative", "Skeptical"] = Field(
        description="Customer sentiment"
    )
    customer_verbiage_sample: Optional[str] = Field(None, description="Representative customer quote")


class SentimentData(BaseModel):
    """V.2 Sentiment of Customer Responses Over Time"""
    opening_segment: SentimentSegment
    early_middle_segment: SentimentSegment
    late_middle_segment: SentimentSegment
    closing_segment: SentimentSegment
    
    sentiment_progression: Literal["Improved", "Stable", "Declined", "Fluctuated"] = Field(
        description="Overall sentiment progression"
    )
    notable_shifts: List[dict] = Field(
        default_factory=list,
        description="Notable sentiment shifts with timestamps and triggers"
    )


class FrustrationMoment(BaseModel):
    """Individual customer frustration moment"""
    frustration_number: int = Field(description="Frustration sequence number")
    timestamp: str = Field(description="Timestamp in MM:SS format")
    customer_verbiage: str = Field(description="Customer frustration quote")
    agent_empathy_shown: bool = Field(description="Agent showed empathy")
    agent_empathy_verbiage: Optional[str] = Field(None, description="Agent empathy response")
    empathy_type: Literal["Acknowledgement", "Validation", "Shared Experience", "None"] = Field(
        description="Type of empathy shown"
    )


class EmpathyPattern(BaseModel):
    """Empathy phrase pattern"""
    phrase: str = Field(description="Empathy phrase")
    used: bool = Field(description="Whether phrase was used")
    count: int = Field(description="Number of times used")


class EmpathyData(BaseModel):
    """V.3 Empathy Statements When Customer Shares Frustration"""
    frustration_moments: List[FrustrationMoment] = Field(default_factory=list)
    
    pattern_frustrating: EmpathyPattern
    pattern_sounds_tough: EmpathyPattern
    pattern_hear_from_lot: EmpathyPattern
    pattern_understand: EmpathyPattern
    other_patterns: List[str] = Field(default_factory=list, description="Other empathy phrases")
    
    total_frustrations: int = Field(description="Total frustrations expressed")
    total_empathy_responses: int = Field(description="Total empathy responses")
    empathy_response_rate: float = Field(description="Percentage of frustrations with empathy")


class EmotionalToneData(BaseModel):
    """Complete Category V: Emotional Tone & Rapport"""
    rapport_moments: RapportMomentsData
    sentiment: SentimentData
    empathy: EmpathyData


# ============================================================================
# CATEGORY VI: OUTCOME AND TIMING MARKERS
# ============================================================================

class HangUpTimingData(BaseModel):
    """VI.1 Timestamp of Hang-Up Relative to Key Stages"""
    total_call_duration: str = Field(description="Total call duration (MM:SS)")
    hangup_timestamp: str = Field(description="Hang-up timestamp (MM:SS)")
    hangup_initiated_by: Literal["Customer", "Agent", "Mutual"] = Field(
        description="Who initiated hang-up"
    )
    
    last_completed_stage: str = Field(description="Name of last completed stage")
    last_stage_timestamp_range: str = Field(description="Last stage timestamp range")
    verbiage_at_hangup: Optional[str] = Field(None, description="Final 2-3 exchanges")
    
    stage_at_disconnect: Literal[
        "I/II - Introduction and Reason",
        "III - Discovery Phase",
        "IV - FOMO/Competitor",
        "V/VI - Value Prop and ROI",
        "VII - Closing/Payment",
        "Post-Close"
    ] = Field(description="Stage progression at disconnect")
    
    time_in_final_stage: str = Field(description="Time spent in final stage (MM:SS)")


class CommitmentData(BaseModel):
    """VI.2 Next Step or Micro-Commitment Secured"""
    commitment_type: Literal[
        "Full Sale Closed",
        "Payment Information Collected",
        "Follow-up Call Scheduled",
        "Email/Information Send Agreed",
        "Think It Over - Specific Timeline",
        "Discuss with Partner",
        "Review Materials",
        "No Commitment Secured"
    ] = Field(description="Type of commitment secured")
    
    commitment_timestamp: Optional[str] = Field(None, description="Commitment timestamp")
    agent_verbiage: Optional[str] = Field(None, description="Agent's assumptive language or closing attempt")
    customer_verbiage: Optional[str] = Field(None, description="Customer's response")
    commitment_clarity: Literal["Explicit", "Implied", "Vague", "None"] = Field(
        description="Clarity of commitment"
    )
    
    assumptive_gather_details: bool = Field(description="'Gather details' language used")
    assumptive_gather_details_timestamp: Optional[str] = Field(None)
    
    assumptive_get_started: bool = Field(description="'Get started' language used")
    assumptive_get_started_timestamp: Optional[str] = Field(None)
    
    assumptive_any_questions: bool = Field(description="'Any questions' language used")
    assumptive_any_questions_timestamp: Optional[str] = Field(None)
    
    other_assumptive_phrases: List[str] = Field(default_factory=list, description="Other assumptive phrases")


class CallResultData(BaseModel):
    """VI.3 Call Result Tag"""
    result_classification: Literal[
        "Sale Completed",
        "Early Disconnect - Before Discovery",
        "Disconnect - During Discovery",
        "Disconnect - After Discovery, Before Pitch",
        "Disconnect - During Pitch/Value Prop",
        "Disconnect - Post-Price/ROI",
        "Disconnect - During Close Attempt",
        "Follow-up Scheduled",
        "Soft Decline (Not Now)",
        "Hard Decline (Not Interested)"
    ] = Field(description="Call result classification")
    
    disconnect_reason_price: bool = Field(description="Price objection caused disconnect")
    disconnect_reason_timeline: bool = Field(description="Timeline concerns caused disconnect")
    disconnect_reason_trust: bool = Field(description="Lack of trust/rapport caused disconnect")
    disconnect_reason_consult: bool = Field(description="Need to consult others caused disconnect")
    disconnect_reason_not_qualified: bool = Field(description="Not qualified/interested caused disconnect")
    disconnect_reason_technical: bool = Field(description="Technical issue caused disconnect")
    disconnect_reason_agent_error: bool = Field(description="Agent error caused disconnect")
    disconnect_reason_unclear: bool = Field(description="Disconnect reason unclear")
    
    supporting_verbiage: Optional[str] = Field(None, description="Quotes indicating disconnect reason")


class OutcomeTimingData(BaseModel):
    """Complete Category VI: Outcome and Timing Markers"""
    hangup_timing: HangUpTimingData
    commitment: CommitmentData
    call_result: CallResultData


# ============================================================================
# MASTER SCHEMA: ALL CATEGORIES COMBINED
# ============================================================================

class SalesCallExtraction(BaseModel):
    """
    Master schema for complete sales call data extraction.
    Contains all 6 categories with comprehensive data points.
    """
    # Metadata
    call_id: Optional[str] = Field(None, description="Unique identifier for the call")
    call_date: Optional[str] = Field(None, description="Date of the call")
    call_duration_seconds: Optional[int] = Field(None, description="Call duration in seconds")
    agent_name: Optional[str] = Field(None, description="Agent's full name")
    
    # Category I: Customer Engagement & Interest
    customer_engagement: CustomerEngagementData
    
    # Category II: Call Opening & Framing
    call_opening: CallOpeningData
    
    # Category III: Objection Handling & Friction
    objection_friction: ObjectionFrictionData
    
    # Category IV: Pace, Control, and Interruptions
    pace_control: PaceControlData
    
    # Category V: Emotional Tone & Rapport
    emotional_tone: EmotionalToneData
    
    # Category VI: Outcome and Timing Markers
    outcome_timing: OutcomeTimingData
    
    # Processing metadata
    extraction_timestamp: Optional[str] = Field(None, description="When extraction was performed")
    extraction_status: Literal["Success", "Partial", "Failed"] = Field(
        default="Success",
        description="Status of extraction"
    )
    extraction_notes: Optional[str] = Field(None, description="Any notes about extraction process")


# ============================================================================
# FLATTENED OUTPUT SCHEMA FOR CSV
# ============================================================================

class FlattenedCallData(BaseModel):
    """
    Flattened version of SalesCallExtraction for CSV output.
    All nested fields are flattened with descriptive column names.
    """
    # Metadata
    call_id: Optional[str] = None
    call_date_omc: Optional[str] = None
    length_in_sec_omc: Optional[int] = None
    fullname_omc: Optional[str] = None
    transcription_omc: Optional[str] = None
    
    # I.1 Talk Ratio
    i1_total_agent_turns: Optional[int] = None
    i1_total_customer_turns: Optional[int] = None
    i1_agent_percentage: Optional[float] = None
    i1_customer_percentage: Optional[float] = None
    i1_classification: Optional[str] = None
    i1_agent_verbiage_sample: Optional[str] = None
    i1_customer_verbiage_sample: Optional[str] = None
    
    # I.2 Discovery Questions - Goal 1
    i2_goal1_q1_asked: Optional[bool] = None
    i2_goal1_q1_timestamp: Optional[str] = None
    i2_goal1_q1_verbiage: Optional[str] = None
    
    i2_goal1_q2_asked: Optional[bool] = None
    i2_goal1_q2_timestamp: Optional[str] = None
    i2_goal1_q2_verbiage: Optional[str] = None
    
    i2_goal1_q3_asked: Optional[bool] = None
    i2_goal1_q3_timestamp: Optional[str] = None
    i2_goal1_q3_verbiage: Optional[str] = None
    
    i2_goal1_q4_asked: Optional[bool] = None
    i2_goal1_q4_timestamp: Optional[str] = None
    i2_goal1_q4_verbiage: Optional[str] = None
    
    i2_goal1_q5_asked: Optional[bool] = None
    i2_goal1_q5_timestamp: Optional[str] = None
    i2_goal1_q5_verbiage: Optional[str] = None
    
    i2_goal1_q6_asked: Optional[bool] = None
    i2_goal1_q6_timestamp: Optional[str] = None
    i2_goal1_q6_verbiage: Optional[str] = None
    
    i2_goal1_q7_asked: Optional[bool] = None
    i2_goal1_q7_timestamp: Optional[str] = None
    i2_goal1_q7_verbiage: Optional[str] = None
    
    i2_goal1_q8_asked: Optional[bool] = None
    i2_goal1_q8_timestamp: Optional[str] = None
    i2_goal1_q8_verbiage: Optional[str] = None
    
    i2_goal1_total: Optional[int] = None
    
    # I.2 Discovery Questions - Goal 2
    i2_goal2_q1_asked: Optional[bool] = None
    i2_goal2_q1_timestamp: Optional[str] = None
    i2_goal2_q1_verbiage: Optional[str] = None
    
    i2_goal2_q2_asked: Optional[bool] = None
    i2_goal2_q2_timestamp: Optional[str] = None
    i2_goal2_q2_verbiage: Optional[str] = None
    
    i2_goal2_q3_asked: Optional[bool] = None
    i2_goal2_q3_timestamp: Optional[str] = None
    i2_goal2_q3_verbiage: Optional[str] = None
    
    i2_goal2_q4_asked: Optional[bool] = None
    i2_goal2_q4_timestamp: Optional[str] = None
    i2_goal2_q4_verbiage: Optional[str] = None
    
    i2_goal2_q5_asked: Optional[bool] = None
    i2_goal2_q5_timestamp: Optional[str] = None
    i2_goal2_q5_verbiage: Optional[str] = None
    
    i2_goal2_q6_asked: Optional[bool] = None
    i2_goal2_q6_timestamp: Optional[str] = None
    i2_goal2_q6_verbiage: Optional[str] = None
    
    i2_goal2_total: Optional[int] = None
    
    # I.2 Discovery Questions - Goal 3
    i2_goal3_q1_asked: Optional[bool] = None
    i2_goal3_q1_timestamp: Optional[str] = None
    i2_goal3_q1_verbiage: Optional[str] = None
    
    i2_goal3_q2_asked: Optional[bool] = None
    i2_goal3_q2_timestamp: Optional[str] = None
    i2_goal3_q2_verbiage: Optional[str] = None
    
    i2_goal3_q3_asked: Optional[bool] = None
    i2_goal3_q3_timestamp: Optional[str] = None
    i2_goal3_q3_verbiage: Optional[str] = None
    
    i2_goal3_q4_asked: Optional[bool] = None
    i2_goal3_q4_timestamp: Optional[str] = None
    i2_goal3_q4_verbiage: Optional[str] = None
    
    i2_goal3_total: Optional[int] = None
    
    # I.2 Advanced Discovery
    i2_advanced_initial_pain_asked: Optional[bool] = None
    i2_advanced_initial_verbiage: Optional[str] = None
    i2_advanced_probing_done: Optional[bool] = None
    i2_advanced_probing_verbiage: Optional[str] = None
    i2_total_discovery_questions: Optional[int] = None
    i2_quality_assessment: Optional[str] = None
    
    # I.3 Buying Signals
    i3_buying_results_detected: Optional[bool] = None
    i3_buying_results_timestamp: Optional[str] = None
    i3_buying_results_verbiage: Optional[str] = None
    
    i3_buying_price_detected: Optional[bool] = None
    i3_buying_price_timestamp: Optional[str] = None
    i3_buying_price_verbiage: Optional[str] = None
    
    i3_buying_next_steps_detected: Optional[bool] = None
    i3_buying_next_steps_timestamp: Optional[str] = None
    i3_buying_next_steps_verbiage: Optional[str] = None
    
    i3_buying_timeline_detected: Optional[bool] = None
    i3_buying_timeline_timestamp: Optional[str] = None
    i3_buying_timeline_verbiage: Optional[str] = None
    
    i3_buying_positive_sentiment_detected: Optional[bool] = None
    i3_buying_positive_sentiment_timestamp: Optional[str] = None
    i3_buying_positive_sentiment_verbiage: Optional[str] = None
    
    i3_total_buying_signals: Optional[int] = None
    
    # I.3 Resistance Signals
    i3_resistance_price_detected: Optional[bool] = None
    i3_resistance_price_timestamp: Optional[str] = None
    i3_resistance_price_verbiage: Optional[str] = None
    
    i3_resistance_not_interested_detected: Optional[bool] = None
    i3_resistance_not_interested_timestamp: Optional[str] = None
    i3_resistance_not_interested_verbiage: Optional[str] = None
    
    i3_resistance_bad_experience_detected: Optional[bool] = None
    i3_resistance_bad_experience_timestamp: Optional[str] = None
    i3_resistance_bad_experience_verbiage: Optional[str] = None
    
    i3_resistance_timing_detected: Optional[bool] = None
    i3_resistance_timing_timestamp: Optional[str] = None
    i3_resistance_timing_verbiage: Optional[str] = None
    
    i3_resistance_budget_detected: Optional[bool] = None
    i3_resistance_budget_timestamp: Optional[str] = None
    i3_resistance_budget_verbiage: Optional[str] = None
    
    i3_total_resistance_signals: Optional[int] = None
    i3_signal_ratio: Optional[str] = None
    i3_overall_sentiment: Optional[str] = None
    
    # II.1 Time to Reason
    ii1_greeting_timestamp: Optional[str] = None
    ii1_reason_timestamp: Optional[str] = None
    ii1_time_elapsed_seconds: Optional[int] = None
    ii1_reason_verbiage: Optional[str] = None
    ii1_reason_clear: Optional[bool] = None
    ii1_complete_opening: Optional[str] = None
    
    # II.2 Personalization
    ii2_business_type_mentioned: Optional[bool] = None
    ii2_business_type_timestamp: Optional[str] = None
    ii2_business_type_verbiage: Optional[str] = None
    ii2_location_mentioned: Optional[bool] = None
    ii2_location_timestamp: Optional[str] = None
    ii2_location_verbiage: Optional[str] = None
    ii2_within_30_seconds: Optional[bool] = None
    ii2_within_45_seconds: Optional[bool] = None
    ii2_personalization_quality: Optional[str] = None
    
    # II.3 Call Structure
    ii3_structure_mentioned: Optional[bool] = None
    ii3_structure_timestamp: Optional[str] = None
    ii3_framing_phrases: Optional[str] = None
    ii3_time_expectation_set: Optional[bool] = None
    ii3_time_expectation_verbiage: Optional[str] = None
    ii3_purpose_stated: Optional[bool] = None
    ii3_purpose_verbiage: Optional[str] = None
    ii3_process_outlined: Optional[bool] = None
    ii3_process_verbiage: Optional[str] = None
    
    # III.1 Objection Handling
    iii1_total_objections: Optional[int] = None
    iii1_total_acknowledged: Optional[int] = None
    iii1_total_rebutted: Optional[int] = None
    iii1_total_unaddressed: Optional[int] = None
    iii1_objections_detail: Optional[str] = None  # JSON string of objection list
    
    # III.2 Acknowledgement
    iii2_acknowledgement_rate: Optional[float] = None
    iii2_pattern_thank_you_count: Optional[int] = None
    iii2_pattern_frustrating_count: Optional[int] = None
    iii2_pattern_long_time_count: Optional[int] = None
    iii2_pattern_right_count: Optional[int] = None
    iii2_pattern_understand_count: Optional[int] = None
    iii2_other_patterns: Optional[str] = None
    
    # III.3 Friction
    iii3_total_price_mentions: Optional[int] = None
    iii3_price_mentions_final_2min: Optional[int] = None
    iii3_total_timeline_mentions: Optional[int] = None
    iii3_timeline_mentions_final_2min: Optional[int] = None
    iii3_total_contract_mentions: Optional[int] = None
    iii3_contract_mentions_final_2min: Optional[int] = None
    iii3_roi_discussed: Optional[bool] = None
    iii3_roi_timestamp: Optional[str] = None
    iii3_roi_verbiage: Optional[str] = None
    iii3_roi_used_customer_data: Optional[bool] = None
    iii3_correlation_to_dropoff: Optional[str] = None
    
    # IV.1 Monologue
    iv1_total_agent_turns: Optional[int] = None
    iv1_extended_monologues_count: Optional[int] = None
    iv1_longest_monologue_duration: Optional[str] = None
    iv1_longest_monologue_verbiage: Optional[str] = None
    iv1_average_monologue_length: Optional[str] = None
    iv1_short_monologues: Optional[int] = None
    iv1_medium_monologues: Optional[int] = None
    iv1_long_monologues: Optional[int] = None
    iv1_very_long_monologues: Optional[int] = None
    iv1_conversation_balance: Optional[str] = None
    
    # IV.2 Interruptions
    iv2_total_interruptions: Optional[int] = None
    iv2_interruption_rate: Optional[float] = None
    iv2_pattern_analysis: Optional[str] = None
    iv2_interruptions_detail: Optional[str] = None  # JSON string
    
    # IV.3 Script Deviation
    iv3_stage1_present: Optional[bool] = None
    iv3_stage1_timestamp: Optional[str] = None
    iv3_stage2_present: Optional[bool] = None
    iv3_stage2_timestamp: Optional[str] = None
    iv3_stage3_present: Optional[bool] = None
    iv3_stage3_timestamp: Optional[str] = None
    iv3_stage4_present: Optional[bool] = None
    iv3_stage4_timestamp: Optional[str] = None
    iv3_stage5_present: Optional[bool] = None
    iv3_stage5_timestamp: Optional[str] = None
    iv3_stage6_present: Optional[bool] = None
    iv3_stage6_timestamp: Optional[str] = None
    iv3_stage7_present: Optional[bool] = None
    iv3_stage7_timestamp: Optional[str] = None
    iv3_stage8_present: Optional[bool] = None
    iv3_out_of_order_segments: Optional[str] = None
    iv3_skipped_segments: Optional[str] = None
    iv3_repeated_segments: Optional[str] = None
    iv3_premature_closing: Optional[bool] = None
    iv3_premature_closing_timestamp: Optional[str] = None
    iv3_returned_to_earlier: Optional[bool] = None
    iv3_return_details: Optional[str] = None
    iv3_flow_assessment: Optional[str] = None
    
    # V.1 Rapport
    v1_name_used: Optional[bool] = None
    v1_name_usage_count: Optional[int] = None
    v1_name_usage_timestamps: Optional[str] = None
    v1_name_usage_verbiage: Optional[str] = None
    v1_context_reference: Optional[bool] = None
    v1_context_type: Optional[str] = None
    v1_context_verbiage: Optional[str] = None
    v1_pleasantry: Optional[bool] = None
    v1_pleasantry_verbiage: Optional[str] = None
    v1_tone_assessment: Optional[str] = None
    v1_personal_greeting: Optional[bool] = None
    v1_previous_interaction_ref: Optional[bool] = None
    v1_common_ground: Optional[bool] = None
    v1_genuine_interest: Optional[bool] = None
    
    # V.2 Sentiment
    v2_opening_sentiment: Optional[str] = None
    v2_opening_verbiage: Optional[str] = None
    v2_early_middle_sentiment: Optional[str] = None
    v2_early_middle_verbiage: Optional[str] = None
    v2_late_middle_sentiment: Optional[str] = None
    v2_late_middle_verbiage: Optional[str] = None
    v2_closing_sentiment: Optional[str] = None
    v2_closing_verbiage: Optional[str] = None
    v2_sentiment_progression: Optional[str] = None
    v2_notable_shifts: Optional[str] = None  # JSON string
    
    # V.3 Empathy
    v3_total_frustrations: Optional[int] = None
    v3_total_empathy_responses: Optional[int] = None
    v3_empathy_response_rate: Optional[float] = None
    v3_pattern_frustrating_count: Optional[int] = None
    v3_pattern_tough_count: Optional[int] = None
    v3_pattern_hear_lot_count: Optional[int] = None
    v3_pattern_understand_count: Optional[int] = None
    v3_other_patterns: Optional[str] = None
    v3_frustrations_detail: Optional[str] = None  # JSON string
    
    # VI.1 Hangup Timing
    vi1_total_duration: Optional[str] = None
    vi1_hangup_timestamp: Optional[str] = None
    vi1_hangup_initiated_by: Optional[str] = None
    vi1_last_completed_stage: Optional[str] = None
    vi1_last_stage_time_range: Optional[str] = None
    vi1_verbiage_at_hangup: Optional[str] = None
    vi1_stage_at_disconnect: Optional[str] = None
    vi1_time_in_final_stage: Optional[str] = None
    
    # VI.2 Commitment
    vi2_commitment_type: Optional[str] = None
    vi2_commitment_timestamp: Optional[str] = None
    vi2_agent_verbiage: Optional[str] = None
    vi2_customer_verbiage: Optional[str] = None
    vi2_commitment_clarity: Optional[str] = None
    vi2_assumptive_gather_details: Optional[bool] = None
    vi2_assumptive_gather_timestamp: Optional[str] = None
    vi2_assumptive_get_started: Optional[bool] = None
    vi2_assumptive_started_timestamp: Optional[str] = None
    vi2_assumptive_questions: Optional[bool] = None
    vi2_assumptive_questions_timestamp: Optional[str] = None
    vi2_other_assumptive: Optional[str] = None
    
    # VI.3 Call Result
    vi3_result_classification: Optional[str] = None
    vi3_disconnect_reason_price: Optional[bool] = None
    vi3_disconnect_reason_timeline: Optional[bool] = None
    vi3_disconnect_reason_trust: Optional[bool] = None
    vi3_disconnect_reason_consult: Optional[bool] = None
    vi3_disconnect_reason_not_qualified: Optional[bool] = None
    vi3_disconnect_reason_technical: Optional[bool] = None
    vi3_disconnect_reason_agent_error: Optional[bool] = None
    vi3_disconnect_reason_unclear: Optional[bool] = None
    vi3_supporting_verbiage: Optional[str] = None
    
    # Processing metadata
    extraction_timestamp: Optional[str] = None
    extraction_status: Optional[str] = None
    extraction_notes: Optional[str] = None

    class Config:
        """Pydantic config"""
        arbitrary_types_allowed = True

