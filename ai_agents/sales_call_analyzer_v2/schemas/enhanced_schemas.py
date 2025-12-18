"""
Enhanced Pydantic schemas for new extraction requirements.
These schemas are for the new agentic variables (timezone, season, sentiment, etc.)
"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# NEW REQUIREMENT 1: Timezone Detection
# ============================================================================

class TimezoneDetection(BaseModel):
    """Timezone detection based on location data"""
    
    timezone: str = Field(
        default="UNKNOWN",
        description="Detected timezone (e.g., 'Eastern', 'Pacific', 'Central', 'Mountain', 'Alaska', 'Hawaii-Aleutian', or 'UNKNOWN')"
    )
    detection_method: str = Field(
        default="",
        description="How timezone was detected (city/state, postal_code, transcription, or unknown)"
    )
    confidence: str = Field(
        default="",
        description="Confidence level (High/Medium/Low)"
    )
    source_data: str = Field(
        default="",
        description="The data used for detection"
    )


# ============================================================================
# NEW REQUIREMENT 2: High/Low Season Detection
# ============================================================================

class SeasonDetection(BaseModel):
    """High/Low season detection based on industry and date"""
    
    season: str = Field(
        default="UNKNOWN",
        description="Season status ('High season', 'Low season', or 'UNKNOWN')"
    )
    industry_category: str = Field(
        default="",
        description="Detected industry category from CSV"
    )
    call_month: str = Field(
        default="",
        description="Month of the call (Jan, Feb, Mar, etc.)"
    )
    season_rationale: str = Field(
        default="",
        description="Explanation of season determination"
    )


# ============================================================================
# NEW REQUIREMENT 3: LGS Sentiment Analysis
# ============================================================================

class LGSSentimentAnalysis(BaseModel):
    """LGS Agent sentiment/stance classification"""
    
    sentiment_classification: str = Field(
        default="UNKNOWN",
        description="One of: Expert, Confident & Assumptive, Consultative & Validating, Robotic & Script-Bound, Hesitant & Apologetic, Urgent & Pressing, N/A - No Interaction"
    )
    evidence_quote: str = Field(
        default="",
        description="Brief (3-10 word) quote from transcript justifying classification"
    )
    confidence: str = Field(
        default="",
        description="Confidence level (High/Medium/Low)"
    )
    additional_notes: str = Field(
        default="",
        description="Additional observations about agent's style"
    )


# ============================================================================
# NEW REQUIREMENT 4: LGS Agent Gender
# ============================================================================

class LGSGenderDetection(BaseModel):
    """LGS Agent gender detection"""
    
    gender: str = Field(
        default="unknown",
        description="Detected gender: Male, Female, or unknown"
    )
    agent_name: str = Field(
        default="",
        description="Agent name used for detection"
    )
    detection_method: str = Field(
        default="",
        description="How gender was detected (name analysis, transcription context, or unknown)"
    )
    confidence: str = Field(
        default="",
        description="Confidence level (High/Medium/Low)"
    )


# ============================================================================
# NEW REQUIREMENT 5: Lead Qualification Analysis
# ============================================================================

class LeadQualificationAnalysis(BaseModel):
    """Lead qualification analysis (4 sub-variables)"""
    
    # 5.1: Decision Maker Validation
    is_decision_maker: str = Field(
        default="unknown",
        description="Yes/No/unknown - Is the lead the Business Owner/Decision Maker?"
    )
    decision_maker_evidence: str = Field(
        default="",
        description="Quote or evidence for decision maker status"
    )
    decision_maker_category: str = Field(
        default="",
        description="Explicit Confirmation, Implicit/Assumed, or Not Confirmed/Gatekeeper"
    )
    
    # 5.2: Ready for More Customers
    ready_for_growth: str = Field(
        default="unknown",
        description="Yes/No/unknown - Are they ready to take on more customers?"
    )
    growth_evidence: str = Field(
        default="",
        description="Quote or evidence for growth readiness"
    )
    
    # 5.3: Forbidden Industries Check
    forbidden_industry_check: str = Field(
        default="unknown",
        description="PASS/FAIL/unknown - Is the industry on the forbidden list?"
    )
    identified_industry: str = Field(
        default="",
        description="The identified industry"
    )
    forbidden_status: str = Field(
        default="",
        description="Explanation of forbidden status"
    )
    
    # 5.4: Transfer Consent
    transfer_consent: str = Field(
        default="unknown",
        description="Yes/No/unknown - Did lead agree to speak to manager?"
    )
    transfer_consent_evidence: str = Field(
        default="",
        description="Quote showing transfer consent"
    )
    
    # Overall Qualification
    overall_qualification: str = Field(
        default="",
        description="QUALIFIED/NOT QUALIFIED/PARTIAL - Overall lead qualification status"
    )
    disqualification_reasons: List[str] = Field(
        default_factory=list,
        description="List of reasons if not qualified"
    )


# ============================================================================
# Complete Enhanced Extraction Result
# ============================================================================

class EnhancedSalesCallExtraction(BaseModel):
    """Complete enhanced extraction result including all new variables"""
    
    # Metadata
    row_id: str = Field(description="Unique identifier for the row")
    transcription_id: str = Field(default="", description="Transcription ID for merging")
    
    # New Variables (Requirements 1-5)
    timezone: TimezoneDetection
    season: SeasonDetection
    lgs_sentiment: LGSSentimentAnalysis
    lgs_gender: LGSGenderDetection
    lead_qualification: LeadQualificationAnalysis
    
    # Processing metadata
    extraction_success: bool = Field(default=True, description="Whether extraction was successful")
    extraction_error: Optional[str] = Field(default=None, description="Error message if extraction failed")
    processing_timestamp: str = Field(default="", description="When this was processed")


# ============================================================================
# Combined Result (Existing + Enhanced)
# ============================================================================

class CombinedExtractionResult(BaseModel):
    """Combined result containing both existing and new extractions"""
    
    # Metadata
    row_id: str = Field(description="Unique identifier for the row")
    transcription_id: str = Field(default="", description="Transcription ID for merging")
    
    # Existing extraction (from original system)
    existing_extraction: Optional[dict] = Field(default=None, description="Original extraction data")
    
    # New enhanced extraction
    enhanced_extraction: EnhancedSalesCallExtraction
    
    # Overall status
    overall_success: bool = Field(default=True, description="Whether all extractions succeeded")
    errors: List[str] = Field(default_factory=list, description="List of any errors encountered")



