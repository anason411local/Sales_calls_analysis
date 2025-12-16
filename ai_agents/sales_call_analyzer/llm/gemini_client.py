"""
Gemini LLM client for sales call extraction.
Handles API calls, structured output, and error handling.
"""

import json
import time
from typing import Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from ..config.settings import settings, get_system_instructions, get_extraction_prompt
from ..utils.logger import logger
from ..schemas.extraction_schemas import SalesCallExtraction


class GeminiClient:
    """Client for interacting with Gemini API"""
    
    def __init__(self):
        """Initialize Gemini client"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={
                "temperature": settings.LLM_TEMPERATURE,
                "max_output_tokens": settings.LLM_MAX_TOKENS,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Load prompts
        self.system_instructions = get_system_instructions()
        self.extraction_prompt = get_extraction_prompt()
        
        logger.info(f"Gemini client initialized with model: {settings.GEMINI_MODEL}")
        logger.debug(f"System instructions loaded: {len(self.system_instructions)} chars")
        logger.debug(f"Extraction prompt loaded: {len(self.extraction_prompt)} chars")
    
    def extract_call_data(
        self,
        call_date: str,
        call_duration: int,
        transcription: str,
        agent_name: str,
        call_id: Optional[str] = None,
        retry_count: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from a sales call transcription.
        
        Args:
            call_date: Date of the call
            call_duration: Duration in seconds
            transcription: Call transcription text
            agent_name: Agent's full name
            call_id: Optional call identifier
            retry_count: Current retry attempt
            
        Returns:
            Extracted data as dictionary or None if failed
        """
        try:
            # Build the extraction prompt
            user_prompt = self._build_extraction_prompt(
                call_date=call_date,
                call_duration=call_duration,
                transcription=transcription,
                agent_name=agent_name,
                call_id=call_id
            )
            
            # Log LLM call
            logger.log_llm_call(
                model=settings.GEMINI_MODEL,
                prompt_length=len(user_prompt)
            )
            
            # Make API call
            start_time = time.time()
            response = self._call_gemini_api(user_prompt)
            duration = time.time() - start_time
            
            if response is None:
                logger.error(f"Gemini API returned None response")
                return None
            
            # Log response
            logger.log_llm_response(
                response_length=len(response),
                tokens_used=None  # Gemini doesn't always provide token count
            )
            logger.debug(f"LLM call completed in {duration:.2f}s")
            
            # Parse and validate response
            extracted_data = self._parse_and_validate_response(response, call_id)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error in extract_call_data: {str(e)}")
            if retry_count < settings.MAX_RETRIES:
                logger.info(f"Retrying... (Attempt {retry_count + 1}/{settings.MAX_RETRIES})")
                time.sleep(settings.RETRY_DELAY_SECONDS)
                return self.extract_call_data(
                    call_date=call_date,
                    call_duration=call_duration,
                    transcription=transcription,
                    agent_name=agent_name,
                    call_id=call_id,
                    retry_count=retry_count + 1
                )
            return None
    
    def _build_extraction_prompt(
        self,
        call_date: str,
        call_duration: int,
        transcription: str,
        agent_name: str,
        call_id: Optional[str] = None
    ) -> str:
        """Build the complete extraction prompt"""
        
        prompt = f"""
{self.system_instructions}

================================================================================
EXTRACTION FRAMEWORK
================================================================================

{self.extraction_prompt}

================================================================================
CALL DATA TO ANALYZE
================================================================================

Call ID: {call_id or "N/A"}
Call Date: {call_date}
Call Duration: {call_duration} seconds
Agent Name: {agent_name}

TRANSCRIPTION:
{transcription}

================================================================================
EXTRACTION INSTRUCTIONS
================================================================================

Please analyze the above sales call transcription and extract ALL data points according to the framework provided.

IMPORTANT REQUIREMENTS:
1. Extract data for ALL 6 categories comprehensively
2. Use exact verbatim quotes from the transcription
3. Provide timestamps in MM:SS format
4. Count all instances explicitly - never estimate
5. Mark fields as "Not Found in Transcript" if data is not present
6. Follow the Pydantic schema structure exactly
7. Ensure all boolean fields are true/false
8. Ensure all numeric fields are numbers (use 0 if not found)
9. Use null/None for optional string fields if not found

OUTPUT FORMAT:
Return the extracted data as a valid JSON object that matches the SalesCallExtraction Pydantic schema structure.

The JSON should have this top-level structure:
{{
  "call_id": "{call_id or "N/A"}",
  "call_date": "{call_date}",
  "call_duration_seconds": {call_duration},
  "agent_name": "{agent_name}",
  "customer_engagement": {{ ... }},
  "call_opening": {{ ... }},
  "objection_friction": {{ ... }},
  "pace_control": {{ ... }},
  "emotional_tone": {{ ... }},
  "outcome_timing": {{ ... }},
  "extraction_timestamp": "<current_timestamp>",
  "extraction_status": "Success",
  "extraction_notes": "<any notes>"
}}

Begin extraction now. Return ONLY the JSON object, no additional text.
"""
        return prompt
    
    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Make API call to Gemini"""
        try:
            response = self.model.generate_content(prompt)
            
            # Check if response has text
            if not response or not response.text:
                logger.error("Gemini API returned empty response")
                return None
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            return None
    
    def _parse_and_validate_response(
        self,
        response_text: str,
        call_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Parse JSON response and validate against Pydantic schema"""
        try:
            # Clean response text (remove markdown code blocks if present)
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            try:
                data = json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {str(e)}")
                logger.debug(f"Response text (first 500 chars): {cleaned_text[:500]}")
                return None
            
            # Validate with Pydantic if enabled
            if settings.VALIDATE_WITH_PYDANTIC:
                try:
                    validated_data = SalesCallExtraction(**data)
                    return validated_data.model_dump()
                except Exception as e:
                    logger.warning(f"Pydantic validation failed: {str(e)}")
                    logger.warning("Proceeding with unvalidated data")
                    return data
            else:
                return data
                
        except Exception as e:
            logger.error(f"Error parsing/validating response: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """Test Gemini API connection"""
        try:
            logger.info("Testing Gemini API connection...")
            response = self.model.generate_content("Hello, this is a test. Please respond with 'OK'.")
            if response and response.text:
                logger.info(f"[OK] Gemini API connection successful. Response: {response.text[:100]}")
                return True
            else:
                logger.error("[FAIL] Gemini API connection failed - no response")
                return False
        except Exception as e:
            logger.error(f"[FAIL] Gemini API connection failed: {str(e)}")
            return False

