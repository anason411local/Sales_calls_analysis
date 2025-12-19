"""
Configuration settings for Call Performance Analyzer
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
INPUT_DIR = PROJECT_ROOT / "input_data"
OUTPUT_DIR = PROJECT_ROOT / "output_data"
LOGS_DIR = PROJECT_ROOT / "logs"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Input/Output files
INPUT_FILE = INPUT_DIR / "mergeed_for_test_og.csv"
OUTPUT_FILE = REPORTS_DIR / "call_performance_analysis_report.md"
CHECKPOINT_FILE = OUTPUT_DIR / "analysis_checkpoint.json"

# Prompts
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
SYSTEM_INSTRUCTIONS_FILE = PROMPTS_DIR / "system_instructions.txt"
ANALYSIS_PROMPT_FILE = PROMPTS_DIR / "analysis_prompt.txt"

# Input columns - Updated for new dataset structure
INPUT_COLUMNS = {
    # Lead Quality Information
    "company_name": "LQ_Company_Name",
    "company_address": "LQ_Company_Address",
    "company_service": "LQ_Service",
    "customer_name": "LQ_Customer_Name",
    "calls_count": "Calls Count",
    "connection_made_calls": "Connection Made Calls",
    
    # Call Information
    "lead_id": "TO_Lead_ID",
    "call_date": "TO_Event_O",
    "lgs_duration": "TO_length_in_sec",
    "omc_duration": "TO_OMC_Duration",
    "omc_status": "TO_OMC_Disposiion",
    
    # LGS Data
    "lgs_agent": "TO_User_M",
    "lgs_transcription_1": "TO_Transcription_VICI(0-32000) Words",
    "lgs_transcription_2": "TO_Transcription_VICI(32001-64000) Words",
    "lgs_transcription_3": "TO_Transcription_VICI(64000+ Words)",
    
    # OMC Data
    "omc_agent": "TO_OMC_User",
    "omc_transcription_1": "TO_OMC_Transcription_VICI",
    "omc_transcription_2": "TO_OMC_Transcription_VICI(32000-64000)Words",
    "omc_transcription_3": "TO_OMC_Transcription_VICI(64000+ Words)"
}

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

# LangSmith Configuration
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "Call_Performance_Analysis")

# Processing Configuration
BATCH_SIZE = 40  # Process 40 rows at a time
MAX_RETRIES = 2
CALL_DURATION_THRESHOLD = 300  # 5 minutes in seconds

# Company Context
COMPANY_CONTEXT = """
COMPANY CONTEXT - 411 LOCALS:
411 Locals is an internet advertising agency founded in 2007, headquartered in Las Vegas, Nevada, 
with offices across North America, Europe, and Asia. We serve over 70,000 businesses with a team 
of 950+ professionals and maintain a 95%+ client retention rate.

Our core services include:
- Search Engine Optimization (SEO) - especially local SEO
- Web Design and Development  
- Content Marketing
- Social Media Marketing
- Pay-Per-Click (PPC) Advertising
- Online Reputation Management
- Call Answering Services (411 Connect)
- Review Management
- Facebook/Google Ads management

DEPARTMENTS:
- LGS (Lead Generation System): Makes initial calls and transfers qualified leads to OMC
- OMC (Outbound Marketing Center): Closes deals and sells products/services
"""

# Analysis Focus Areas
ANALYSIS_FOCUS = {
    "short_calls": "Calls under 5 minutes (<300 seconds)",
    "long_calls": "Calls over 5 minutes (>=300 seconds)",
    "lgs_handoff": "Quality of LGS to OMC handoff",
    "agent_performance": "Individual agent performance metrics",
    "patterns": "Successful vs unsuccessful call patterns",
    "recommendations": "Actionable insights for improvement"
}

