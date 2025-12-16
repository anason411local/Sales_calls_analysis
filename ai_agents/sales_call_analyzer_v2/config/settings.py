"""
Configuration settings for Sales Call Analyzer V2
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from parent ai_agents directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # Go up to Sales_calls_analysis
DATA_DIR = PROJECT_ROOT / "input_data"
OUTPUT_DIR = PROJECT_ROOT / "output_data"
LOGS_DIR = PROJECT_ROOT / "logs"
PROMPTS_DIR = PROJECT_ROOT / "ai_agents" / "ai_agent_for_Sales_prompt_variobles_extarctoin"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Input/Output files
INPUT_CSV = DATA_DIR / "sales_calls_agent_testing_data.csv"
OUTPUT_CSV = OUTPUT_DIR / "extracted_sales_data.csv"
CHECKPOINT_FILE = OUTPUT_DIR / "processing_checkpoint.json"

# System prompts
SYSTEM_INSTRUCTIONS_FILE = PROMPTS_DIR / "system Instrutions.txt"
EXTRACTION_PROMPT_FILE = PROMPTS_DIR / "sales_data_extaction_prompt.txt"

# Input columns
INPUT_COLUMNS = {
    "id": "id",  # Row identifier
    "transcription_id": "transcription_id_omc",  # For merging
    "call_date": "call_date_omc",
    "length_in_sec": "length_in_sec_omc",
    "transcription": "transcription_omc",
    "fullname": "fullname_omc"
}

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-lite"  # Using the correct model code

# LangSmith Configuration
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "Sales_call_analysis_agent")

# Processing Configuration
BATCH_SIZE = 10  # Process 10 rows at a time
MAX_RETRIES = 3  # Maximum retry attempts for failed extractions
RETRY_DELAY = 2  # Seconds to wait between retries

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

