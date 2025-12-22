"""
Gemini LLM client with structured output
"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LANGSMITH_TRACING,
    LANGSMITH_API_KEY,
    LANGSMITH_ENDPOINT,
    LANGSMITH_PROJECT
)
from schemas.analysis_schemas import CallInsight
from utils.logger import logger

# Configure LangSmith if enabled
if LANGSMITH_TRACING and LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = LANGSMITH_ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
    logger.info(f"LangSmith tracing enabled for project: {LANGSMITH_PROJECT}")

def get_analysis_llm():
    """
    Get Gemini LLM configured for call analysis with structured output
    
    Returns:
        Configured LLM with structured output
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.1,  # Low temperature for consistent analysis
            convert_system_message_to_human=True
        )
        
        # Configure structured output
        structured_llm = llm.with_structured_output(CallInsight)
        
        logger.info(f"Gemini LLM initialized: {GEMINI_MODEL}")
        return structured_llm
        
    except Exception as e:
        logger.error(f"Failed to initialize Gemini LLM: {str(e)}")
        raise

def get_report_llm():
    """
    Get Gemini LLM for report generation (no structured output)
    
    Returns:
        Configured LLM for text generation
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.3,  # Slightly higher for creative report writing
            convert_system_message_to_human=True
        )
        
        logger.info(f"Report generation LLM initialized: {GEMINI_MODEL}")
        return llm
        
    except Exception as e:
        logger.error(f"Failed to initialize report LLM: {str(e)}")
        raise

