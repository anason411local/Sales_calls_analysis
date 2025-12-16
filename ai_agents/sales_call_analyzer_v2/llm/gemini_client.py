"""
Gemini LLM Client with Structured Output Support
Integrates LangSmith tracing and uses Gemini 2.5 Flash Lite
"""
import os
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LANGSMITH_TRACING,
    LANGSMITH_API_KEY,
    LANGSMITH_PROJECT,
    LANGSMITH_ENDPOINT
)
from schemas.extraction_schemas import SalesCallExtraction
from utils.logger import get_logger

logger = get_logger()


class GeminiClient:
    """
    Gemini LLM client with structured output support using function calling.
    Integrates LangSmith for tracing and monitoring.
    """
    
    def __init__(self):
        """Initialize Gemini client with LangSmith integration"""
        
        # Set up LangSmith environment variables
        if LANGSMITH_TRACING and LANGSMITH_API_KEY:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_ENDPOINT"] = LANGSMITH_ENDPOINT or "https://api.smith.langchain.com"
            os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT or "Sales_call_analysis_agent"
            logger.info(f"LangSmith tracing enabled for project: {LANGSMITH_PROJECT}")
        else:
            logger.warning("LangSmith tracing disabled - API key not found")
        
        # Initialize Gemini model with structured output
        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.1,  # Low temperature for consistent extraction
            convert_system_message_to_human=True  # Gemini compatibility
        )
        
        # Create structured output LLM using with_structured_output
        self.structured_llm = self.llm.with_structured_output(
            SalesCallExtraction,
            method="function_calling"  # Use function calling for structured output
        )
        
        logger.info(f"Gemini client initialized with model: {GEMINI_MODEL}")
    
    def extract_structured_data(
        self,
        prompt: str,
        row_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SalesCallExtraction:
        """
        Extract structured data from a sales call using Gemini with function calling.
        
        Args:
            prompt: Formatted prompt with system instructions and transcript
            row_id: Unique identifier for the row
            metadata: Optional metadata for LangSmith tracking
        
        Returns:
            SalesCallExtraction: Structured extraction result
        
        Raises:
            Exception: If extraction fails
        """
        try:
            logger.debug(f"Calling {GEMINI_MODEL} for Row ID: {row_id}")
            
            # Add metadata for LangSmith tracking
            if metadata is None:
                metadata = {}
            metadata.update({
                "row_id": row_id,
                "model": GEMINI_MODEL,
                "extraction_type": "sales_call"
            })
            
            # Invoke the structured LLM
            # The with_structured_output method automatically handles function calling
            result = self.structured_llm.invoke(
                prompt,
                config={"metadata": metadata}
            )
            
            logger.debug(f"LLM response successful for Row ID: {row_id}")
            
            # Validate that we got a proper SalesCallExtraction object
            if not isinstance(result, SalesCallExtraction):
                raise ValueError(f"Expected SalesCallExtraction, got {type(result)}")
            
            return result
            
        except Exception as e:
            logger.error(f"LLM extraction failed for Row ID: {row_id}: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test the Gemini API connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info("Testing Gemini API connection...")
            
            # Simple test prompt
            test_prompt = "Respond with 'OK' if you can read this message."
            response = self.llm.invoke(test_prompt)
            
            logger.info("Gemini API connection successful")
            logger.info(f"Test response: {response.content[:100]}")
            
            return True
            
        except Exception as e:
            logger.error(f"Gemini API connection failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about the current model configuration.
        
        Returns:
            Dict with model information
        """
        return {
            "model": GEMINI_MODEL,
            "api_key_configured": bool(GEMINI_API_KEY),
            "langsmith_enabled": LANGSMITH_TRACING,
            "langsmith_project": LANGSMITH_PROJECT if LANGSMITH_TRACING else "N/A"
        }

