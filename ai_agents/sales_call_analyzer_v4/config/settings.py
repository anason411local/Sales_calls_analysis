"""
Configuration settings for Sales Call Analyzer V3 - Multi-Agent Architecture
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from ai_agents directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # Go up to Sales_calls_analysis
DATA_DIR = PROJECT_ROOT / "input_data"
OUTPUT_DIR = PROJECT_ROOT / "output_data"
LOGS_DIR = PROJECT_ROOT / "logs"
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)

# Input/Output files
INPUT_CSV = DATA_DIR / "sales_calls_agent_testing_data.csv"
OUTPUT_CSV = OUTPUT_DIR / "extracted_sales_data_v3.csv"
CHECKPOINT_FILE = CHECKPOINTS_DIR / "extraction_checkpoint_v3.json"

# Season lookup CSV
SEASON_LOOKUP_CSV = DATA_DIR / "Sales Data points - High_Low season for that industy _ Location.csv"

# Input columns mapping
INPUT_COLUMNS = {
    "id": "id",
    "transcription_id": "transcription_id_omc",
    "call_date": "call_date_omc",
    "length_in_sec": "length_in_sec_omc",
    "transcription": "transcription",  # LGS transcription (Opener)
    "transcription_omc": "transcription_omc",  # OMC transcription (Closer)
    "fullname": "fullname_omc",
    "city": "city",
    "state": "state",
    "postal_code": "postal_code",
    "service": "service"  # For season classification
}

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-lite"  # Using Gemini 2.5 Flash Lite

# LangSmith Configuration
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "Sales_call_analysis_v3_multi_agent")

# Processing Configuration
BATCH_SIZE = 5  # Process 5 rows at a time (reduced for multi-agent complexity)
MAX_RETRIES = 3  # Maximum retry attempts for failed extractions
RETRY_DELAY = 2  # Seconds to wait between retries
PARALLEL_AGENTS = True  # Run independent agents in parallel

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Agent Configuration
AGENT_TIMEOUT = 60  # Timeout for each agent in seconds

# Timezone mapping (US timezones)
US_STATE_TIMEZONES = {
    # Eastern Time
    "CT": "Eastern", "DE": "Eastern", "FL": "Eastern", "GA": "Eastern",
    "ME": "Eastern", "MD": "Eastern", "MA": "Eastern", "NH": "Eastern",
    "NJ": "Eastern", "NY": "Eastern", "NC": "Eastern", "OH": "Eastern",
    "PA": "Eastern", "RI": "Eastern", "SC": "Eastern", "VT": "Eastern",
    "VA": "Eastern", "WV": "Eastern", "DC": "Eastern", "MI": "Eastern",
    "IN": "Eastern",  # Most of Indiana
    
    # Central Time
    "AL": "Central", "AR": "Central", "IL": "Central", "IA": "Central",
    "KS": "Central", "KY": "Central", "LA": "Central", "MN": "Central",
    "MS": "Central", "MO": "Central", "NE": "Central", "ND": "Central",
    "OK": "Central", "SD": "Central", "TN": "Central", "TX": "Central",
    "WI": "Central",
    
    # Mountain Time
    "AZ": "Mountain", "CO": "Mountain", "ID": "Mountain", "MT": "Mountain",
    "NM": "Mountain", "UT": "Mountain", "WY": "Mountain",
    
    # Pacific Time
    "CA": "Pacific", "NV": "Pacific", "OR": "Pacific", "WA": "Pacific",
    
    # Alaska Time
    "AK": "Alaska",
    
    # Hawaii-Aleutian Time
    "HI": "Hawaii-Aleutian"
}

# Forbidden Industries List (for qualification validation)
FORBIDDEN_INDUSTRIES = [
    "SEO", "Web Designers", "Graphic Designers", "Locksmith",
    "Escort Services", "Online Services", "Dentist", "Real Estate",
    "Hotel", "Restaurant", "Vacation Rental", "Sex-Related",
    "School", "Universities", "Big Corporations", "Corporations",
    "Hospitals", "Animal Hospitals", "Charity", "Government Agencies",
    "Churches", "Franchises", "Writer"
]

