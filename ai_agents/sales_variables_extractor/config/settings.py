"""
Configuration Settings for Sales Variables Extractor
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent.parent
INPUT_DIR = BASE_DIR / "input_data"
OUTPUT_DIR = BASE_DIR / "output_data"
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
OUTPUT_DIR.mkdir(exist_ok=True)
CHECKPOINTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Input/Output files
INPUT_CSV = INPUT_DIR / "mergeed_for_test_2.csv"
OUTPUT_CSV = OUTPUT_DIR / "sales_variables_extracted.csv"
CHECKPOINT_FILE = CHECKPOINTS_DIR / "variables_extraction_checkpoint.json"

# Seasonality and timezone reference files
SEASONALITY_CSV = INPUT_DIR / "seasonality.csv"
TIMEZONE_FILE = Path(__file__).parent.parent / "prompts" / "timezone_mapping.txt"

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-lite"  # Using Gemini 2.5 Flash

# LangSmith Configuration (optional)
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "sales-variables-extractor")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"

# Processing Configuration
MAX_RETRIES = 2
BATCH_SIZE = 10  # Process 10 rows at a time in parallel
RATE_LIMIT_DELAY = 0.5  # Seconds between API calls (reduced for parallel processing)

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Column mappings for input CSV
INPUT_COLUMNS = {
    # LGS Columns
    "lgs_user": "TO_User_M",
    "lgs_event_time": "TO_Event_O",
    "lgs_duration": "TO_length_in_sec",
    "lgs_transcription": "TO_Transcription_VICI(0-32000) Words",
    
    # OMC Columns
    "omc_user": "TO_OMC_User",
    "omc_call_date": "TO_OMC_Call_Date_O",
    "omc_duration": "TO_OMC_Duration",
    "omc_transcription": "TO_OMC_Transcription_VICI",
    
    # Common Columns
    "lead_id": "TO_Lead_ID",
    "customer_address": "LQ_Company_Address",
    "service": "LQ_Service",
    "customer_name": "LQ_Customer_Name",
}

# Validation settings
REQUIRED_LGS_FIELDS = ["lgs_transcription", "service", "customer_address"]
REQUIRED_OMC_FIELDS = ["omc_transcription", "service"]

