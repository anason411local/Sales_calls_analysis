"""
Gemini LLM Client for Sales Variables Extraction
Handles API calls to Gemini with structured output
"""
import os
import json
import re
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from schemas.variable_schemas import LGSExtractedVariables, OMCExtractedVariables
from utils.logger import get_logger

logger = get_logger()


def clean_json_string(json_str: str) -> str:
    """
    Clean and repair common JSON formatting issues.
    
    Args:
        json_str: Potentially malformed JSON string
    
    Returns:
        Cleaned JSON string
    """
    # Remove any markdown code blocks
    json_str = re.sub(r'```json\s*', '', json_str)
    json_str = re.sub(r'```\s*$', '', json_str)
    
    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Try to fix unterminated strings by finding unmatched quotes
    # This is a simple heuristic - count quotes per line
    lines = json_str.split('\n')
    fixed_lines = []
    for line in lines:
        # Count unescaped quotes
        quote_count = len(re.findall(r'(?<!\\)"', line))
        if quote_count % 2 != 0:
            # Odd number of quotes - likely unterminated
            # Add closing quote before any trailing comma or brace
            line = re.sub(r'([^"])(\s*[,}\]])$', r'\1"\2', line)
        fixed_lines.append(line)
    
    json_str = '\n'.join(fixed_lines)
    
    return json_str.strip()


class GeminiClient:
    """Client for interacting with Gemini API"""
    
    def __init__(self):
        """Initialize Gemini client"""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize client with API key
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL
        
        logger.info(f"Gemini client initialized with model: {GEMINI_MODEL}")
    
    def extract_lgs_variables(
        self,
        prompt: str,
        row_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LGSExtractedVariables:
        """
        Extract LGS variables using Gemini with structured output.
        
        Args:
            prompt: Formatted extraction prompt
            row_id: Unique row identifier
            metadata: Optional metadata for logging
        
        Returns:
            LGSExtractedVariables object
        
        Raises:
            Exception: If extraction fails
        """
        try:
            logger.info(f"Extracting LGS variables for row {row_id}")
            
            # Generate content using new API with JSON mode
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Lower temperature for consistent JSON
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=32768,  # Doubled to prevent truncation for long transcripts
                    response_mime_type="application/json"
                )
            )
            
            # Parse response
            response_text = response.text
            
            # Clean JSON before parsing
            cleaned_json = clean_json_string(response_text)
            
            try:
                result_dict = json.loads(cleaned_json)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON cleaning didn't fix all issues for row {row_id}. Trying original...")
                result_dict = json.loads(response_text)  # Try original, will raise if still fails
            
            # Convert to Pydantic model
            lgs_variables = LGSExtractedVariables(**result_dict)
            
            logger.info(f"Successfully extracted LGS variables for row {row_id}")
            return lgs_variables
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for row {row_id}: {str(e)}")
            logger.error(f"Response preview: {response_text[:500] if 'response_text' in locals() else 'N/A'}")
            raise Exception(f"JSON parsing error: {str(e)}")
        
        except Exception as e:
            logger.error(f"LGS extraction failed for row {row_id}: {str(e)}")
            raise
    
    def extract_omc_variables(
        self,
        prompt: str,
        row_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OMCExtractedVariables:
        """
        Extract OMC variables using Gemini with structured output.
        
        Args:
            prompt: Formatted extraction prompt
            row_id: Unique row identifier
            metadata: Optional metadata for logging
        
        Returns:
            OMCExtractedVariables object
        
        Raises:
            Exception: If extraction fails
        """
        try:
            logger.info(f"Extracting OMC variables for row {row_id}")
            
            # Generate content using new API with JSON mode
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Lower temperature for consistent JSON
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=32768,  # Doubled to prevent truncation for long transcripts
                    response_mime_type="application/json"
                )
            )
            
            # Parse response
            response_text = response.text
            
            # Clean JSON before parsing
            cleaned_json = clean_json_string(response_text)
            
            try:
                result_dict = json.loads(cleaned_json)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON cleaning didn't fix all issues for row {row_id}. Trying original...")
                result_dict = json.loads(response_text)  # Try original, will raise if still fails
            
            # Convert to Pydantic model
            omc_variables = OMCExtractedVariables(**result_dict)
            
            logger.info(f"Successfully extracted OMC variables for row {row_id}")
            return omc_variables
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for row {row_id}: {str(e)}")
            logger.error(f"Response preview: {response_text[:500] if 'response_text' in locals() else 'N/A'}")
            raise Exception(f"JSON parsing error: {str(e)}")
        
        except Exception as e:
            logger.error(f"OMC extraction failed for row {row_id}: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test the Gemini API connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Hello, this is a test."
            )
            return bool(response.text)
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the configured model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model": self.model_name,
            "api_key_configured": bool(GEMINI_API_KEY),
            "api_key_prefix": GEMINI_API_KEY[:10] + "..." if GEMINI_API_KEY else "Not set"
        }

