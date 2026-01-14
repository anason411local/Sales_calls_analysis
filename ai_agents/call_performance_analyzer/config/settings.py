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
INPUT_FILE = INPUT_DIR / "dpad_sales_variables_extracted.csv"
OUTPUT_FILE = REPORTS_DIR / "call_performance_analysis_report.md"
CHECKPOINT_FILE = OUTPUT_DIR / "analysis_checkpoint.json"

# Prompts
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
SYSTEM_INSTRUCTIONS_FILE = PROMPTS_DIR / "system_instructions.txt"
ANALYSIS_PROMPT_FILE = PROMPTS_DIR / "analysis_prompt.txt"

# Input columns - Updated for new dataset structure with extracted variables
INPUT_COLUMNS = {
    # Lead Quality Information
    "company_name": "LQ_Company_Name",
    "company_address": "LQ_Company_Address",
    "company_service": "LQ_Service",
    "customer_name": "LQ_Customer_Name",
    "calls_count": "Calls Count",  # CSV column name with space
    "connection_made_calls": "Connection Made Calls",  # CSV column name with space
    
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
    "omc_transcription_3": "TO_OMC_Transcription_VICI(64000+ Words)",
    
    # NEW: LGS Extracted Variables
    "season_status": "season_status",
    "lgs_agent_gender": "lgs_agent_gender",
    "is_decision_maker": "is_decision_maker",
    "ready_for_customers": "ready_for_customers",
    "forbidden_industry": "forbidden_industry",
    "ready_to_transfer": "ready_to_transfer",
    "customer_sentiment_lgs": "customer_sentiment",
    "customer_language": "customer_language",
    "who_said_hello_first_lgs": "who_said_hello_first",
    "lgs_sentiment_style": "lgs_sentiment_style",
    
    # NEW: OMC Extracted Variables
    "timezone": "timezone",
    "customer_sentiment_omc": "customer_sentiment_omc",
    "customer_knows_marketing": "customer_knows_marketing",
    "customer_availability": "customer_availability",
    "customer_marketing_experience": "customer_marketing_experience",
    "technical_quality_score": "technical_quality_score",
    "omc_agent_sentiment_style": "omc_agent_sentiment_style",
    "omc_who_said_hello_first": "omc_who_said_hello_first",
    "customer_talk_percentage": "customer_talk_percentage",
    "total_discovery_questions": "total_discovery_questions",
    "total_buying_signals": "total_buying_signals",
    "time_to_reason_seconds": "time_to_reason_seconds",
    "location_mentioned": "location_mentioned",
    "business_type_mentioned": "business_type_mentioned",
    "within_45_seconds": "within_45_seconds",
    "call_structure_framed": "call_structure_framed",
    "total_objections": "total_objections",
    "objections_acknowledged": "objections_acknowledged",
    "price_mentions_final_2min": "price_mentions_final_2min",
    "timeline_mentions_final_2min": "timeline_mentions_final_2min",
    "contract_mentions_final_2min": "contract_mentions_final_2min",
    "objections_rebutted": "objections_rebutted",
    "total_interruptions": "total_interruptions",
    "commitment_type": "commitment_type",
    "call_result_tag": "call_result_tag"
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
    "recommendations": "Actionable insights for improvement",
    "script_compliance": "How well agents follow the 10-section sales script"
}

# ============================================================================
# SCRIPT COMPLIANCE CONFIGURATION
# ============================================================================

# Script compliance thresholds
SCRIPT_COMPLIANCE_THRESHOLDS = {
    "high_compliance": 70,      # >= 70% = High compliance
    "medium_compliance": 40,    # 40-69% = Medium compliance
    "low_compliance": 0,        # < 40% = Low compliance
    "script_followed_min": 40,  # Minimum % to consider script "followed"
    "min_core_sections": 4      # Minimum core sections (1-5) to be attempted
}

# 10 Mandatory Script Sections
SCRIPT_SECTIONS = {
    1: {
        "name": "Intro",
        "full_name": "Intro (Hook + Control)",
        "key_elements": [
            "Greeting with customer name",
            "Real quick phrase",
            "Reference to assistant/previous contact",
            "Looking for reliable business mention",
            "Online searches reference",
            "Sound good acknowledgment"
        ]
    },
    2: {
        "name": "Qualifying",
        "full_name": "Qualifying (Keep it light & curious)",
        "key_elements": [
            "What kind of jobs question",
            "Average job question",
            "Profit per job question",
            "Lead closing rate question",
            "Marketing ROI question",
            "Best customers question",
            "Best areas question"
        ]
    },
    3: {
        "name": "Problem_Setup",
        "full_name": "Problem + Setup",
        "key_elements": [
            "Google presence question",
            "ZIP code reference",
            "Competitors on first page mention",
            "84% statistic",
            "94% first page statistic",
            "Visibility opportunity question"
        ]
    },
    4: {
        "name": "Pitch",
        "full_name": "Pitch (Clear and Simple)",
        "key_elements": [
            "411 Locals introduction",
            "70,000 businesses mention",
            "Local SEO explanation",
            "17-page website",
            "50+ directories",
            "Booking Engine offer",
            "Digital Business Card",
            "Google Ads option"
        ]
    },
    5: {
        "name": "Offer_Close",
        "full_name": "Offer + Close (Hard Close)",
        "key_elements": [
            "Original price anchor",
            "Discounted offer",
            "Monthly pricing",
            "No contract mention",
            "ROI calculation",
            "Assumptive close",
            "Payment method request"
        ]
    },
    6: {
        "name": "Info_Check",
        "full_name": "Info Check",
        "key_elements": [
            "Business name confirmation",
            "Address",
            "Phone & Email",
            "Hours of operation",
            "Top services",
            "Payment methods",
            "Address visibility"
        ]
    },
    7: {
        "name": "SMS_Agreement",
        "full_name": "SMS Agreement",
        "key_elements": [
            "Text agreement mention",
            "Reply I agree instruction",
            "Price lock mention",
            "Exclusivity mention"
        ]
    },
    8: {
        "name": "Timeline_Expectations",
        "full_name": "Timeline & Expectations",
        "key_elements": [
            "Month 1 setup explanation",
            "Months 2-4 optimization",
            "Month 6+ results",
            "Review request",
            "SEO growth metaphor",
            "Welcome call transfer"
        ]
    },
    9: {
        "name": "Opening_Objections",
        "full_name": "Opening Objections",
        "is_situational": True,
        "key_elements": [
            "I'm fully booked handling",
            "Already have website handling",
            "Too many customers handling",
            "I'm busy handling",
            "What's this about handling",
            "Costs money handling",
            "Already have marketing handling"
        ]
    },
    10: {
        "name": "Closing_Objections",
        "full_name": "Closing Objections",
        "is_situational": True,
        "key_elements": [
            "Send email handling",
            "No money/budget handling",
            "No time handling",
            "Driving/call back handling",
            "No urgency handling",
            "No trust handling",
            "No card handling",
            "Prepaid card handling",
            "Bad reviews handling",
            "Bad experience handling",
            "Talk to partner handling",
            "Trial/cancellation handling"
        ]
    }
}

# Non-compliance reason categories
NON_COMPLIANCE_CATEGORIES = {
    "external_factors": [
        "customer_hung_up_immediately",
        "technical_connection_issues",
        "customer_already_client",
        "language_barrier"
    ],
    "client_interruptions": [
        "customer_objection_interrupted",
        "not_decision_maker",
        "wrong_timing_busy",
        "customer_not_interested_upfront"
    ],
    "agent_errors": [
        "agent_skipped_sections",
        "agent_deviated_from_script"
    ]
}

# Objection types from script
SCRIPT_OBJECTIONS = {
    "opening": [
        "fully_booked",
        "already_have_website",
        "too_many_customers",
        "busy_right_now",
        "whats_this_about",
        "costs_money",
        "already_have_marketing"
    ],
    "closing": [
        "send_email",
        "no_money_budget",
        "no_time_too_busy",
        "driving_call_back",
        "no_urgency",
        "no_trust",
        "no_card",
        "prepaid_card",
        "bad_reviews",
        "bad_experience",
        "talk_to_partner",
        "trial_cancellation"
    ]
}

