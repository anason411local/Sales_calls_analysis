"""
Configuration settings for the Sales Call Analyzer Agent.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"  # Gemini 2.0 Flash Experimental (latest available)
    
    # LangSmith Configuration
    LANGSMITH_TRACING: str = os.getenv("LANGSMITH_TRACING", "false")
    LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "Sales_call_analysis_agent")
    
    # File Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent
    INPUT_DATA_DIR: Path = PROJECT_ROOT / "input_data"
    OUTPUT_DATA_DIR: Path = PROJECT_ROOT / "output_data"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    CHECKPOINT_DIR: Path = PROJECT_ROOT / "checkpoints"
    
    INPUT_CSV: str = "sales_calls_agent_testing_data.csv"
    OUTPUT_CSV: str = "sales_calls_extracted_data.csv"
    
    # Prompt Files
    PROMPTS_DIR: Path = PROJECT_ROOT / "ai_agents" / "ai_agent_for_Sales_prompt_variobles_extarctoin"
    SYSTEM_INSTRUCTIONS_FILE: str = "system Instrutions.txt"
    EXTRACTION_PROMPT_FILE: str = "sales_data_extaction_prompt.txt"
    
    # Processing Configuration
    BATCH_SIZE: int = 10  # Process 10 rows at a time
    MAX_RETRIES: int = 3  # Retry failed rows up to 3 times
    RETRY_DELAY_SECONDS: int = 2  # Delay between retries
    
    # LLM Configuration
    LLM_TEMPERATURE: float = 0.1  # Low temperature for consistent extraction
    LLM_MAX_TOKENS: int = 8000  # Maximum tokens for response
    LLM_TIMEOUT_SECONDS: int = 120  # Timeout for LLM calls
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # Resume Configuration
    ENABLE_CHECKPOINTING: bool = True
    CHECKPOINT_FREQUENCY: int = 1  # Save checkpoint after every batch
    
    # Data Validation
    VALIDATE_WITH_PYDANTIC: bool = True
    FILL_MISSING_WITH_NAN: bool = True
    
    # Input Columns
    INPUT_COLUMNS: list = [
        "call_date_omc",
        "length_in_sec_omc",
        "transcription_omc",
        "fullname_omc"
    ]
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def ensure_directories():
    """Create necessary directories if they don't exist"""
    settings.OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    settings.CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


def get_system_instructions() -> str:
    """Load system instructions from file"""
    instructions_path = settings.PROMPTS_DIR / settings.SYSTEM_INSTRUCTIONS_FILE
    with open(instructions_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_extraction_prompt() -> str:
    """Load extraction prompt from file"""
    prompt_path = settings.PROMPTS_DIR / settings.EXTRACTION_PROMPT_FILE
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

