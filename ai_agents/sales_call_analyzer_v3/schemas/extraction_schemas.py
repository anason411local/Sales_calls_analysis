"""
Pydantic schemas for structured data extraction from sales calls.
These schemas match the extraction requirements from sales_data_extaction_prompt.txt
"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# Category 1: Customer Engagement & Interest
# ============================================================================

class CustomerEngagementInterest(BaseModel):
    """Customer Engagement & Interest metrics"""
    
    # Positive Engagement Signals
    positive_signal_count: int = Field(
        default=0,
        description="Count of positive engagement signals"
    )
    positive_signal_verbiage: str = Field(
        default="",
        description="Exact verbiage of positive signals"
    )
    positive_signal_timestamps: str = Field(
        default="",
        description="Timestamps of positive signals"
    )
    
    # Questions Asked by Customer
    customer_questions_count: int = Field(
        default=0,
        description="Number of questions asked by customer"
    )
    customer_questions_verbiage: str = Field(
        default="",
        description="Exact verbiage of customer questions"
    )
    customer_questions_timestamps: str = Field(
        default="",
        description="Timestamps of customer questions"
    )
    
    # Buying Intent Signals
    buying_intent_count: int = Field(
        default=0,
        description="Count of buying intent signals"
    )
    buying_intent_verbiage: str = Field(
        default="",
        description="Exact verbiage of buying intent"
    )
    buying_intent_timestamps: str = Field(
        default="",
        description="Timestamps of buying intent"
    )
    
    # Disengagement Signals
    disengagement_count: int = Field(
        default=0,
        description="Count of disengagement signals"
    )
    disengagement_verbiage: str = Field(
        default="",
        description="Exact verbiage of disengagement"
    )
    disengagement_timestamps: str = Field(
        default="",
        description="Timestamps of disengagement"
    )


# ============================================================================
# Category 2: Call Opening & Framing
# ============================================================================

class CallOpeningFraming(BaseModel):
    """Call Opening & Framing metrics"""
    
    # Opener Type
    opener_type: str = Field(
        default="",
        description="Type of call opener used"
    )
    opener_verbiage: str = Field(
        default="",
        description="Exact verbiage of opener"
    )
    
    # Permission Request
    permission_request_present: str = Field(
        default="No",
        description="Whether permission was requested (Yes/No)"
    )
    permission_request_verbiage: str = Field(
        default="",
        description="Exact verbiage of permission request"
    )
    
    # Value Proposition
    value_prop_present: str = Field(
        default="No",
        description="Whether value proposition was stated (Yes/No)"
    )
    value_prop_verbiage: str = Field(
        default="",
        description="Exact verbiage of value proposition"
    )
    value_prop_timestamp: str = Field(
        default="",
        description="Timestamp of value proposition"
    )
    
    # Agenda Setting
    agenda_set: str = Field(
        default="No",
        description="Whether agenda was set (Yes/No)"
    )
    agenda_verbiage: str = Field(
        default="",
        description="Exact verbiage of agenda"
    )


# ============================================================================
# Category 3: Objection Handling & Friction
# ============================================================================

class ObjectionHandlingFriction(BaseModel):
    """Objection Handling & Friction metrics"""
    
    # Objections Raised
    objections_count: int = Field(
        default=0,
        description="Number of objections raised"
    )
    objection_types: str = Field(
        default="",
        description="Types of objections (comma-separated)"
    )
    objection_verbiage: str = Field(
        default="",
        description="Exact verbiage of objections"
    )
    objection_timestamps: str = Field(
        default="",
        description="Timestamps of objections"
    )
    
    # Objection Handling
    objection_handling_present: str = Field(
        default="No",
        description="Whether objections were handled (Yes/No)"
    )
    objection_handling_verbiage: str = Field(
        default="",
        description="Exact verbiage of objection handling"
    )
    objection_handling_quality: str = Field(
        default="",
        description="Quality of objection handling (Strong/Moderate/Weak)"
    )
    
    # Friction Points
    friction_points_count: int = Field(
        default=0,
        description="Number of friction points"
    )
    friction_verbiage: str = Field(
        default="",
        description="Exact verbiage of friction points"
    )
    friction_timestamps: str = Field(
        default="",
        description="Timestamps of friction points"
    )


# ============================================================================
# Category 4: Pace, Control, and Interruptions
# ============================================================================

class PaceControlInterruptions(BaseModel):
    """Pace, Control, and Interruptions metrics"""
    
    # Sales Rep Interruptions
    rep_interruptions_count: int = Field(
        default=0,
        description="Number of times rep interrupted customer"
    )
    rep_interruptions_verbiage: str = Field(
        default="",
        description="Exact verbiage of rep interruptions"
    )
    rep_interruptions_timestamps: str = Field(
        default="",
        description="Timestamps of rep interruptions"
    )
    
    # Customer Interruptions
    customer_interruptions_count: int = Field(
        default=0,
        description="Number of times customer interrupted rep"
    )
    customer_interruptions_verbiage: str = Field(
        default="",
        description="Exact verbiage of customer interruptions"
    )
    customer_interruptions_timestamps: str = Field(
        default="",
        description="Timestamps of customer interruptions"
    )
    
    # Talk Ratio
    rep_talk_percentage: float = Field(
        default=0.0,
        description="Percentage of time rep was talking"
    )
    customer_talk_percentage: float = Field(
        default=0.0,
        description="Percentage of time customer was talking"
    )
    
    # Pace Assessment
    pace_assessment: str = Field(
        default="",
        description="Overall pace (Rushed/Balanced/Slow)"
    )
    pace_notes: str = Field(
        default="",
        description="Notes on pace"
    )


# ============================================================================
# Category 5: Emotional Tone & Rapport
# ============================================================================

class EmotionalToneRapport(BaseModel):
    """Emotional Tone & Rapport metrics"""
    
    # Customer Emotional Tone
    customer_tone_overall: str = Field(
        default="",
        description="Overall customer tone (Positive/Neutral/Negative)"
    )
    customer_tone_shifts: str = Field(
        default="",
        description="Description of tone shifts"
    )
    customer_tone_verbiage: str = Field(
        default="",
        description="Key verbiage indicating tone"
    )
    
    # Rep Emotional Tone
    rep_tone_overall: str = Field(
        default="",
        description="Overall rep tone (Professional/Friendly/Aggressive/etc)"
    )
    rep_tone_notes: str = Field(
        default="",
        description="Notes on rep tone"
    )
    
    # Rapport Building
    rapport_building_present: str = Field(
        default="No",
        description="Whether rapport building was present (Yes/No)"
    )
    rapport_building_verbiage: str = Field(
        default="",
        description="Exact verbiage of rapport building"
    )
    rapport_building_timestamps: str = Field(
        default="",
        description="Timestamps of rapport building"
    )
    
    # Empathy & Active Listening
    empathy_present: str = Field(
        default="No",
        description="Whether empathy was shown (Yes/No)"
    )
    empathy_verbiage: str = Field(
        default="",
        description="Exact verbiage showing empathy"
    )
    active_listening_present: str = Field(
        default="No",
        description="Whether active listening was demonstrated (Yes/No)"
    )
    active_listening_verbiage: str = Field(
        default="",
        description="Exact verbiage showing active listening"
    )


# ============================================================================
# Category 6: Outcome and Timing Markers
# ============================================================================

class OutcomeTimingMarkers(BaseModel):
    """Outcome and Timing Markers"""
    
    # Call Outcome
    call_outcome: str = Field(
        default="",
        description="Overall call outcome (Appointment Set/Follow-up Scheduled/Not Interested/etc)"
    )
    outcome_verbiage: str = Field(
        default="",
        description="Exact verbiage indicating outcome"
    )
    outcome_timestamp: str = Field(
        default="",
        description="Timestamp of outcome determination"
    )
    
    # Next Steps
    next_steps_defined: str = Field(
        default="No",
        description="Whether next steps were defined (Yes/No)"
    )
    next_steps_verbiage: str = Field(
        default="",
        description="Exact verbiage of next steps"
    )
    
    # Commitment Level
    commitment_level: str = Field(
        default="",
        description="Customer commitment level (High/Medium/Low/None)"
    )
    commitment_verbiage: str = Field(
        default="",
        description="Exact verbiage indicating commitment"
    )
    
    # Call Duration Analysis
    call_duration_seconds: int = Field(
        default=0,
        description="Total call duration in seconds"
    )
    optimal_duration: str = Field(
        default="",
        description="Whether duration was optimal (Yes/No/Too Short/Too Long)"
    )


# ============================================================================
# Complete Extraction Result
# ============================================================================

class SalesCallExtraction(BaseModel):
    """Complete extraction result for a single sales call"""
    
    # Metadata
    row_id: str = Field(description="Unique identifier for the row")
    transcription_id: str = Field(default="", description="Transcription ID for merging with source data")
    call_date: str = Field(description="Date of the call")
    fullname: str = Field(description="Full name of the sales rep")
    length_in_sec: int = Field(description="Length of call in seconds")
    
    # All extraction categories
    customer_engagement: CustomerEngagementInterest
    call_opening: CallOpeningFraming
    objection_handling: ObjectionHandlingFriction
    pace_control: PaceControlInterruptions
    emotional_tone: EmotionalToneRapport
    outcome_timing: OutcomeTimingMarkers
    
    # Processing metadata
    extraction_success: bool = Field(default=True, description="Whether extraction was successful")
    extraction_error: Optional[str] = Field(default=None, description="Error message if extraction failed")

