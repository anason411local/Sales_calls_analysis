"""
Prompt Templates for Sales Variables Extraction
Formats prompts for LGS and OMC variable extraction
"""
from pathlib import Path
from typing import Optional


# Load prompt files
PROMPTS_DIR = Path(__file__).parent

def load_prompt_file(filename: str) -> str:
    """Load a prompt file from the prompts directory"""
    file_path = PROMPTS_DIR / filename
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


# Load all prompt templates
SYSTEM_INSTRUCTIONS = load_prompt_file("system Instrutions.txt")
SALES_DATA_EXTRACTION_PROMPT = load_prompt_file("sales_data_extaction_prompt.txt")
TIMEZONE_MAPPING = load_prompt_file("timezone.txt")
LGS_SENTIMENT_ANALYSIS = load_prompt_file("LGS_Sentiiment_analysis.txt")
LGS_QUALIFYING = load_prompt_file("LGS_Qualifying.txt")
LGS_CUSTOMER_SENTIMENT = load_prompt_file("LGS_Customer_sentiment_analysis.txt")
LGS_CUSTOMER_MARKETING = load_prompt_file("LGS_Customer_marketing_understanfing.txt")
LGS_TECHNICAL_QUALITY = load_prompt_file("LGS_technical_quality_of__call.txt")


def format_lgs_extraction_prompt(
    lgs_user: str,
    lgs_event_time: str,
    lgs_duration: int,
    lgs_transcription: str,
    customer_address: str,
    service: str,
    seasonality_data: str,
    is_retry: bool = False,
    error_message: str = ""
) -> str:
    """
    Format the LGS variable extraction prompt.
    
    Args:
        lgs_user: LGS agent name
        lgs_event_time: Event timestamp
        lgs_duration: Call duration in seconds
        lgs_transcription: LGS call transcription
        customer_address: Customer address/location
        service: Service provided by customer
        seasonality_data: Seasonality reference data
        is_retry: Whether this is a retry attempt
        error_message: Previous error message if retry
    
    Returns:
        Formatted prompt string
    """
    
    retry_context = ""
    if is_retry and error_message:
        retry_context = f"""
IMPORTANT - THIS IS A RETRY ATTEMPT:
Previous extraction failed with error: {error_message}
Please carefully review the requirements and ensure all fields are properly extracted.
"""
    
    prompt = f"""{retry_context}

TASK: Extract LGS (Lead Generation Specialist) Variables from Sales Call

================================================================================
CALL INFORMATION
================================================================================
LGS Agent: {lgs_user}
Event Time: {lgs_event_time}
Call Duration: {lgs_duration} seconds
Customer Address: {customer_address}
Service Type: {service}

================================================================================
CALL TRANSCRIPTION (LGS AGENT)
================================================================================
{lgs_transcription}

================================================================================
REFERENCE DATA
================================================================================

TIMEZONE MAPPING:
{TIMEZONE_MAPPING}

SEASONALITY DATA:
{seasonality_data}

================================================================================
EXTRACTION INSTRUCTIONS
================================================================================

You must extract the following variables:

SECTION A: TIMING & SEASONALITY
1. **timezone**: Determine the timezone based on the customer address
   - Use the timezone mapping provided above
   - Extract state/location from customer address
   - Return timezone (e.g., "Eastern", "Pacific", "Central", "Mountain")

2. **season_status**: Determine if it's high or low season for the service
   - Use the seasonality data provided above
   - Match the service type to the seasonality table
   - Consider the current month from lgs_event_time
   - Return "High season" or "Low season"

SECTION B: LGS AGENT SENTIMENT/STYLE
{LGS_SENTIMENT_ANALYSIS}

SECTION C: LGS AGENT GENDER
3. **lgs_agent_gender**: Infer gender from agent's name
   - Return "Male", "Female", or "unknown"

SECTION D: QUALIFYING VARIABLES
{LGS_QUALIFYING}

SECTION D.1: CALL TRANSFER STATUS
11. **lgs_call_not_transferred**: Was the call transferred to OMC?
   - Analyze if the call was successfully transferred
   - If not transferred, identify why (customer declined, not qualified, technical issue, etc.)
   - Return "Yes" (transferred), "No - [reason]", or "unknown"

SECTION E: CUSTOMER SENTIMENT
{LGS_CUSTOMER_SENTIMENT}

SECTION F: CUSTOMER LANGUAGE
5. **customer_language**: Language used by customer
   
   CLASSIFICATION RULES:
   
   SPANISH: Classify as "Spanish" if:
   - The call opens with the greeting "Hola" OR
   - The agent asks a variation of "Do you prefer English or Spanish/Español?"
   
   ENGLISH: Classify as "English" if:
   - The conversation proceeds in English without the specific Spanish triggers mentioned above
   
   UNKNOWN: Classify as "Unknown" if:
   - The language cannot be determined from the transcript
   - The transcript is too short or unclear
   
   Return: "English", "Spanish", or "Unknown"

SECTION G: CUSTOMER UNDERSTANDING
6. **customer_knows_marketing**: Does customer understand this is a marketing call?
   - Return "Yes", "No", or "unknown"

SECTION H: CUSTOMER AVAILABILITY
7. **customer_availability**: Is customer busy or available?
   - Return "busy", "available", or "unknown"

SECTION I: WHO SAID HELLO FIRST
8. **who_said_hello_first**: At call start, who greets first?
   - Return "Customer", "Agent", or "unknown"

SECTION J: CUSTOMER MARKETING SOPHISTICATION
{LGS_CUSTOMER_MARKETING}

SECTION K: TECHNICAL CALL QUALITY
{LGS_TECHNICAL_QUALITY}

================================================================================
OUTPUT FORMAT - CRITICAL
================================================================================

You MUST return a JSON object with this EXACT structure:

{{
  "timing_seasonality": {{
    "timezone": "string (Eastern/Pacific/Central/Mountain/unknown)",
    "season_status": "string (High season/Low season/unknown)",
    "season_month": "string (month name)"
  }},
  "agent_variables": {{
    "lgs_sentiment_style": "string",
    "lgs_agent_gender": "string (Male/Female/unknown)",
    "is_decision_maker": "string (Yes/No/unknown)",
    "ready_for_customers": "string (Yes/No/unknown)",
    "forbidden_industry": "string (Yes/No/unknown)",
    "ready_to_transfer": "string (Yes/No/unknown)",
    "lgs_call_not_transferred": "string (Yes/No - reason/unknown)",
    "customer_sentiment": "string",
    "customer_language": "string (English/Spanish/Unknown)",
    "customer_knows_marketing": "string (Yes/No/unknown)",
    "customer_availability": "string (busy/available/unknown)",
    "who_said_hello_first": "string (Customer/Agent/unknown)",
    "customer_marketing_experience": "string (Novice/Skeptic/Transactional/Expert)",
    "technical_quality_score": number (0-5),
    "technical_quality_issues": "string (comma-separated list)"
  }}
}}

CRITICAL RULES:
1. Use ONLY these two top-level keys: "timing_seasonality" and "agent_variables"
2. Do NOT use "SECTION_A", "section_a", "lgs_agent_variables" or any other names
3. All string values must be properly escaped and quoted
4. Use null for unknown values, not "unknown" string
5. Ensure all JSON is valid - no unterminated strings, missing commas, or syntax errors
"""
    
    return prompt


def format_omc_extraction_prompt(
    omc_user: str,
    omc_call_date: str,
    omc_duration: int,
    omc_transcription: str,
    service: str,
    is_retry: bool = False,
    error_message: str = ""
) -> str:
    """
    Format the OMC variable extraction prompt.
    
    Args:
        omc_user: OMC agent name
        omc_call_date: Call date timestamp
        omc_duration: Call duration in seconds
        omc_transcription: OMC call transcription
        service: Service provided by customer
        is_retry: Whether this is a retry attempt
        error_message: Previous error message if retry
    
    Returns:
        Formatted prompt string
    """
    
    retry_context = ""
    if is_retry and error_message:
        retry_context = f"""
IMPORTANT - THIS IS A RETRY ATTEMPT:
Previous extraction failed with error: {error_message}
Please carefully review the requirements and ensure all fields are properly extracted.
"""
    
    prompt = f"""{retry_context}

TASK: Extract OMC (Outbound Marketing Closer) Variables from Sales Call

================================================================================
SYSTEM INSTRUCTIONS
================================================================================
{SYSTEM_INSTRUCTIONS}

================================================================================
CALL INFORMATION
================================================================================
OMC Agent: {omc_user}
Call Date: {omc_call_date}
Call Duration: {omc_duration} seconds
Service Type: {service}

================================================================================
CALL TRANSCRIPTION (OMC AGENT)
================================================================================
{omc_transcription}

================================================================================
EXTRACTION FRAMEWORK
================================================================================
{SALES_DATA_EXTRACTION_PROMPT}

================================================================================
ADDITIONAL EXTRACTION REQUIREMENTS
================================================================================

CATEGORY I: CUSTOMER ENGAGEMENT & INTEREST
-------------------------------------------
1. TALK RATIO: Calculate percentage of conversation by agent vs customer
   - Count total utterances/turns for each
   - Classify as: Mutual Dialogue (40-60% customer) / Agent-Heavy (<30% customer) / Customer-Heavy (>70% customer)

2. DISCOVERY QUESTIONS: Count and categorize all discovery questions
   - Goal 1 (Demographics/Operations): Business duration, services, team size, equipment, etc.
   - Goal 2 (Competition/Marketing): Website, advertising spend, marketing management, etc.
   - Goal 3 (Practical Need/Mindset): Google usage, online search behavior, etc.
   - Quality Assessment: Surface-Level (just asking) / Moderate Depth (some follow-up) / Deep Discovery (peeling the onion)
   - Advanced Discovery: Did agent ask open-ended pain point questions and probe deeper with follow-ups?

3. BUYING vs RESISTANCE SIGNALS:
   - Buying: Asks about results, price, next steps, timeline, expresses positive sentiment
   - Resistance: Price pushback, "not interested", bad experience, timing concerns, budget constraints
   - Calculate ratio and overall sentiment

CATEGORY II: CALL OPENING & FRAMING
------------------------------------
4. OMC AGENT SENTIMENT/STYLE: Classify agent's sales stance (NOT customer's):
   - Expert: Advisor/consultant approach
   - Confident & Assumptive: Controls frame, assumes sale, declarative statements
   - Consultative & Validating: Active listening, mirrors, validates
   - Robotic & Script-Bound: Mechanical, reads verbatim, excessive fillers
   - Hesitant & Apologetic: Unsure, submissive, apologizes unnecessarily
   - Urgent & Pressing: High-pressure, ignores soft "no", speeds up

5. WHO SAID HELLO FIRST: At OMC call start, who greeted first (Customer/Agent/unknown)

6. TIME TO STATE REASON: Seconds from greeting to clearly stating reason + value to customer

7. PERSONALIZATION: Business type AND location mentioned within first 30-45 seconds?

8. CALL STRUCTURE CLARITY: Did agent frame what will happen in the call?
   - Time expectation set? Purpose stated? Process outlined?

CATEGORY III: OBJECTION HANDLING & FRICTION
--------------------------------------------
9. OBJECTIONS: Count total objections, how many acknowledged, how many rebutted
   - Track acknowledgement patterns (empathy, validation, clarification)
   - Calculate acknowledgement rate

10. PRICE/TIMELINE/CONTRACT MENTIONS: Track mentions in final 2 minutes
    - Separate counts for price, timeline, contract
    - Total mentions before drop-off
    - Was ROI calculation presented?

CATEGORY IV: PACE, CONTROL, AND INTERRUPTIONS
----------------------------------------------
11. MONOLOGUE ANALYSIS: Analyze agent's speaking patterns
    - Average monologue length (sentences or seconds)
    - Longest monologue
    - Extended monologues (>5 sentences)
    - Distribution: Short (1-2) / Medium (3-5) / Long (6-10) / Very Long (>10)
    - Conversation balance: Mutual / Agent-Heavy / Choppy

12. INTERRUPTIONS: Count times agent interrupted customer
    - Calculate interruption rate (per minute)
    - Pattern: Frequent / Occasional / Rare / None

13. SCRIPT ADHERENCE: Map call flow against expected structure
    - Expected stages: Introduction → Reason → Discovery → FOMO → Value Prop → ROI → Close
    - Which stages were skipped?
    - Were stages completed out of order?
    - Premature closing attempt?
    - Overall: Structured / Somewhat Structured / Unstructured

CATEGORY V: EMOTIONAL TONE & RAPPORT
-------------------------------------
14. RAPPORT IN FIRST MINUTE:
    - Customer name used? How many times?
    - Personal greeting? Context reference? Common ground?
    - Tone: Warm / Professional / Cold / Rushed

15. SENTIMENT TIMELINE: Track customer sentiment at different periods
    - Opening (0:00-2:00): Positive / Neutral / Negative / Skeptical
    - Early Middle (2:00-5:00)
    - Late Middle (5:00-end-2min)
    - Closing (final 2 min)
    - Overall progression: Improved / Stable / Declined / Fluctuated
    - Notable shifts and triggers

16. EMPATHY RESPONSES: When customer shares frustration, did agent show empathy?
    - Count frustrations expressed
    - Count empathy responses
    - Calculate empathy response rate

CATEGORY VI: OUTCOME AND TIMING MARKERS
----------------------------------------
17. CALL TIMING:
    - Total duration in seconds
    - Stage where call ended
    - Who initiated hang-up (Customer/Agent/Mutual)
    - Time spent in final stage before disconnect

18. COMMITMENTS SECURED:
    - Type: Full Sale / Payment Info / Follow-up / Think It Over / No Commitment
    - Clarity: Explicit / Implied / Vague / None
    - Assumptive language used?
    - Full sale closed? Payment info collected? Follow-up scheduled?

19. CALL RESULT TAG:
    - Sale Completed / Early Disconnect / Disconnect - During Discovery / etc.
    - Primary disconnect reason: Price / Timeline / Trust / Need to consult / Not qualified / Technical / Agent error / Unclear

================================================================================
OUTPUT FORMAT - CRITICAL
================================================================================

You MUST return a JSON object with this EXACT structure:

{{
  "customer_engagement": {{
    "customer_talk_percentage": number,
    "agent_talk_percentage": number,
    "talk_ratio_classification": "string",
    "total_discovery_questions": number,
    "goal1_questions": number,
    "goal2_questions": number,
    "goal3_questions": number,
    "discovery_quality": "string (Surface-Level/Moderate Depth/Deep Discovery)",
    "advanced_discovery_used": "string (Yes/No - peeling the onion)",
    "total_buying_signals": number,
    "total_resistance_signals": number,
    "signal_ratio": "string",
    "customer_sentiment": "string"
  }},
  "call_opening": {{
    "omc_agent_sentiment_style": "string (Expert/Confident & Assumptive/Consultative & Validating/Robotic & Script-Bound/Hesitant & Apologetic/Urgent & Pressing)",
    "omc_who_said_hello_first": "string (Customer/Agent/unknown)",
    "time_to_reason_seconds": number (seconds to state reason and value),
    "business_type_mentioned": "string (Yes/No)",
    "location_mentioned": "string (Yes/No)",
    "within_45_seconds": "string (Yes/No - business & location within 30-45 sec)",
    "call_structure_framed": "string (Yes/No)",
    "call_structure_clarity": "string (description of how structure was communicated)"
  }},
  "objection_handling": {{
    "total_objections": number,
    "objections_acknowledged": number,
    "objections_rebutted": number,
    "acknowledgement_rate": number,
    "price_mentions_final_2min": number,
    "timeline_mentions_final_2min": number,
    "contract_mentions_final_2min": number,
    "price_timeline_contract_before_dropoff": number (total mentions before drop-off),
    "roi_calculation_presented": "string (Yes/No)"
  }},
  "pace_control": {{
    "average_monologue_length": number,
    "longest_monologue_length": number,
    "extended_monologues_count": number (monologues >5 sentences),
    "short_monologues": number (1-2 sentences),
    "medium_monologues": number (3-5 sentences),
    "long_monologues": number (6-10 sentences),
    "very_long_monologues": number (>10 sentences),
    "total_interruptions": number,
    "interruption_rate": number (per minute),
    "interruption_pattern": "string (Frequent/Occasional/Rare/None)",
    "conversation_balance": "string",
    "script_adherence": "string",
    "stages_skipped": "string",
    "stages_out_of_order": "string",
    "premature_closing_attempt": "string (Yes/No)"
  }},
  "emotional_tone": {{
    "name_used_first_minute": "string (Yes/No)",
    "name_usage_count": number,
    "rapport_elements_count": number,
    "tone_assessment": "string (Warm/Professional/Cold/Rushed)",
    "personal_greeting": "string (Yes/No)",
    "common_ground_established": "string (Yes/No)",
    "sentiment_progression": "string (Improved/Stable/Declined/Fluctuated)",
    "sentiment_opening": "string (Positive/Neutral/Negative/Skeptical - 0:00-2:00)",
    "sentiment_early_middle": "string (Positive/Neutral/Negative/Skeptical - 2:00-5:00)",
    "sentiment_late_middle": "string (Positive/Neutral/Negative/Skeptical - 5:00-end-2min)",
    "sentiment_closing": "string (Positive/Neutral/Negative/Skeptical - final 2 min)",
    "notable_sentiment_shifts": "string (description)",
    "customer_frustrations": "string (e.g. '3' or 'Not Found')",
    "empathy_responses": number,
    "empathy_response_rate": number
  }},
  "outcome_timing": {{
    "total_call_duration": number (seconds as integer, e.g. 155),
    "disconnect_stage": "string",
    "hang_up_initiated_by": "string",
    "time_in_final_stage": number (seconds in final stage),
    "commitment_type": "string",
    "commitment_clarity": "string (Explicit/Implied/Vague/None)",
    "assumptive_language_used": "string (Yes/No)",
    "full_sale_closed": "string (Yes/No)",
    "payment_info_collected": "string (Yes/No)",
    "followup_scheduled": "string (Yes/No)",
    "call_result_tag": "string",
    "primary_disconnect_reason": "string"
  }}
}}

CRITICAL RULES:
1. Use ONLY these six top-level keys: customer_engagement, call_opening, objection_handling, pace_control, emotional_tone, outcome_timing
2. Do NOT use different key names or nest them differently
3. All string values must be properly escaped and quoted - NO UNTERMINATED STRINGS
4. Use null for unknown values
5. Ensure all JSON is valid - check for missing commas, quotes, and brackets
6. If a quote contains a quote character, escape it with backslash
"""
    
    return prompt


def format_combined_prompt(
    lgs_prompt: str,
    omc_prompt: str
) -> str:
    """
    Combine LGS and OMC prompts for sequential extraction.
    
    Args:
        lgs_prompt: Formatted LGS extraction prompt
        omc_prompt: Formatted OMC extraction prompt
    
    Returns:
        Combined prompt string
    """
    return f"""
You are tasked with extracting variables from TWO separate call transcriptions:
1. LGS (Lead Generation Specialist) call
2. OMC (Outbound Marketing Closer) call

Please process each section independently and return a combined result.

================================================================================
SECTION 1: LGS VARIABLE EXTRACTION
================================================================================
{lgs_prompt}

================================================================================
SECTION 2: OMC VARIABLE EXTRACTION
================================================================================
{omc_prompt}

================================================================================
FINAL OUTPUT
================================================================================
Return a single JSON object containing both lgs_variables and omc_variables.
"""

