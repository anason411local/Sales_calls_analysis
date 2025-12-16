"""
Prompt templates for Sales Call Extraction Agent
Uses ChatPromptTemplate from Langchain to properly structure prompts
"""
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from pathlib import Path
from config.settings import SYSTEM_INSTRUCTIONS_FILE, EXTRACTION_PROMPT_FILE


def load_prompt_file(file_path: Path) -> str:
    """Load prompt content from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# Load system instructions and extraction prompt
SYSTEM_INSTRUCTIONS = load_prompt_file(SYSTEM_INSTRUCTIONS_FILE)
EXTRACTION_PROMPT = load_prompt_file(EXTRACTION_PROMPT_FILE)


def create_extraction_prompt_template() -> ChatPromptTemplate:
    """
    Create the main extraction prompt template using ChatPromptTemplate.
    This ensures proper formatting and comprehensive use of system instructions.
    """
    
    system_template = """
{system_instructions}

================================================================================
EXTRACTION FRAMEWORK
================================================================================

{extraction_prompt}

================================================================================
YOUR TASK
================================================================================

You are analyzing a sales call transcript. Your task is to extract ALL data points 
according to the framework above and return them in a structured format.

CRITICAL REQUIREMENTS:
1. Extract data for ALL 6 categories comprehensively
2. Use exact verbiage from the transcript (verbatim quotes)
3. Include precise timestamps in MM:SS format
4. Count all instances explicitly - never estimate
5. If a data point is not found, use empty strings or 0 for counts
6. Return data in the EXACT schema structure provided
7. Do NOT truncate or remove any categories
8. Do NOT make assumptions - extract only what is explicitly present

Remember: Your primary function is DATA EXTRACTION, not evaluation.
Focus on "what happened" not "how well it happened".
"""
    
    human_template = """
SALES CALL METADATA:
- Call Date: {call_date}
- Sales Rep: {fullname}
- Call Duration: {length_in_sec} seconds

TRANSCRIPT TO ANALYZE:
{transcription}

Please extract ALL data points from this transcript according to the 6-category framework.
Return the results in the structured format with all fields populated.
"""
    
    # Create the chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template)
    ])
    
    return prompt


def create_retry_extraction_prompt_template() -> ChatPromptTemplate:
    """
    Create a retry prompt template for failed extractions.
    This adds additional emphasis on following the schema.
    """
    
    system_template = """
{system_instructions}

================================================================================
EXTRACTION FRAMEWORK
================================================================================

{extraction_prompt}

================================================================================
RETRY EXTRACTION TASK
================================================================================

The previous extraction attempt failed. Please try again with EXTRA ATTENTION to:

1. EXACT SCHEMA ADHERENCE: Return data in the EXACT structure specified
2. ALL CATEGORIES: Include all 6 categories without exception
3. PROPER DATA TYPES: 
   - Use integers for counts (not strings)
   - Use strings for verbiage and classifications
   - Use proper nested structures for sub-categories
4. NO NULL VALUES: Use empty strings "" or 0 instead of null/None
5. COMPLETE EXTRACTION: Do not skip or truncate any sections

This is retry attempt. Please ensure the output matches the schema perfectly.
"""
    
    human_template = """
SALES CALL METADATA:
- Call Date: {call_date}
- Sales Rep: {fullname}
- Call Duration: {length_in_sec} seconds

TRANSCRIPT TO ANALYZE:
{transcription}

PREVIOUS ERROR: {error_message}

Please extract ALL data points carefully, ensuring perfect schema compliance.
"""
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template)
    ])
    
    return prompt


# Create prompt template instances
extraction_prompt_template = create_extraction_prompt_template()
retry_extraction_prompt_template = create_retry_extraction_prompt_template()


def format_extraction_prompt(
    call_date: str,
    fullname: str,
    length_in_sec: int,
    transcription: str,
    is_retry: bool = False,
    error_message: str = ""
) -> str:
    """
    Format the extraction prompt with actual data.
    
    Args:
        call_date: Date of the call
        fullname: Name of the sales rep
        length_in_sec: Call duration in seconds
        transcription: Full call transcript
        is_retry: Whether this is a retry attempt
        error_message: Error message from previous attempt (if retry)
    
    Returns:
        Formatted prompt string
    """
    
    base_vars = {
        "system_instructions": SYSTEM_INSTRUCTIONS,
        "extraction_prompt": EXTRACTION_PROMPT,
        "call_date": call_date,
        "fullname": fullname,
        "length_in_sec": length_in_sec,
        "transcription": transcription
    }
    
    if is_retry:
        base_vars["error_message"] = error_message
        return retry_extraction_prompt_template.format(**base_vars)
    else:
        return extraction_prompt_template.format(**base_vars)

