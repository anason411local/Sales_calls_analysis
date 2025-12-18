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

SECTION E: CUSTOMER SENTIMENT
{LGS_CUSTOMER_SENTIMENT}

SECTION F: CUSTOMER LANGUAGE
5. **customer_language**: Language used by customer
   - Return "English", "Spanish", or "Unknown"

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
    "total_buying_signals": number,
    "total_resistance_signals": number,
    "signal_ratio": "string",
    "customer_sentiment": "string"
  }},
  "call_opening": {{
    "time_to_reason_seconds": number,
    "business_type_mentioned": "string (Yes/No)",
    "location_mentioned": "string (Yes/No)",
    "within_45_seconds": "string (Yes/No)",
    "call_structure_framed": "string (Yes/No)"
  }},
  "objection_handling": {{
    "total_objections": number,
    "objections_acknowledged": number,
    "objections_rebutted": number,
    "acknowledgement_rate": number,
    "price_mentions_final_2min": number,
    "timeline_mentions_final_2min": number,
    "contract_mentions_final_2min": number,
    "roi_calculation_presented": "string (Yes/No)"
  }},
  "pace_control": {{
    "average_monologue_length": number,
    "longest_monologue_length": number,
    "total_interruptions": number,
    "conversation_balance": "string",
    "script_adherence": "string",
    "stages_skipped": "string"
  }},
  "emotional_tone": {{
    "name_used_first_minute": "string (Yes/No)",
    "name_usage_count": number,
    "rapport_elements_count": number,
    "sentiment_progression": "string",
    "customer_frustrations": "string (e.g. '3' or 'Not Found')",
    "empathy_responses": number,
    "empathy_response_rate": number
  }},
  "outcome_timing": {{
    "total_call_duration": number (seconds as integer, e.g. 155),
    "disconnect_stage": "string",
    "hang_up_initiated_by": "string",
    "commitment_type": "string",
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

