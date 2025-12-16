"""
Main Entry Point for Sales Call Analyzer V2
Proper LangGraph Agentic Framework with Gemini 2.5 Flash Lite
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.batch_processor import BatchProcessor
from llm.gemini_client import GeminiClient
from utils.logger import get_logger
from config.settings import (
    GEMINI_MODEL,
    LANGSMITH_PROJECT,
    LANGSMITH_TRACING,
    INPUT_CSV,
    OUTPUT_CSV
)

logger = get_logger()


def print_banner():
    """Print welcome banner"""
    banner = """
================================================================================
    SALES CALL ANALYZER V2 - AGENTIC FRAMEWORK
================================================================================
    Model: Gemini 2.5 Flash Lite
    Framework: LangGraph + Langchain
    LangSmith Tracing: {}
    Project: {}
================================================================================
""".format(
        "ENABLED" if LANGSMITH_TRACING else "DISABLED",
        LANGSMITH_PROJECT if LANGSMITH_TRACING else "N/A"
    )
    print(banner)


def test_connection():
    """Test Gemini API connection"""
    logger.info("Testing Gemini API connection...")
    
    try:
        client = GeminiClient()
        model_info = client.get_model_info()
        
        print("\nModel Configuration:")
        print(f"  Model: {model_info['model']}")
        print(f"  API Key Configured: {model_info['api_key_configured']}")
        print(f"  LangSmith Enabled: {model_info['langsmith_enabled']}")
        print(f"  LangSmith Project: {model_info['langsmith_project']}")
        
        success = client.test_connection()
        
        if success:
            print("\n[SUCCESS] Gemini API connection test passed!")
            return True
        else:
            print("\n[ERROR] Gemini API connection test failed!")
            return False
            
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        print(f"\n[ERROR] Connection test failed: {str(e)}")
        return False


def run_extraction():
    """Run the main extraction process"""
    logger.info("Starting Sales Call Extraction Process")
    logger.info(f"Input file: {INPUT_CSV}")
    logger.info(f"Output file: {OUTPUT_CSV}")
    logger.info(f"Model: {GEMINI_MODEL}")
    
    try:
        # Initialize batch processor
        processor = BatchProcessor()
        
        # Process all rows
        processor.process_all()
        
        print("\n[SUCCESS] Extraction process completed successfully!")
        print(f"Results saved to: {OUTPUT_CSV}")
        
    except Exception as e:
        logger.error(f"Extraction process failed: {str(e)}")
        print(f"\n[ERROR] Extraction process failed: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Sales Call Analyzer V2 - LangGraph Agentic Framework"
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test Gemini API connection and exit"
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the extraction process"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # If no arguments, show help
    if not args.test_connection and not args.run:
        parser.print_help()
        print("\nExamples:")
        print("  python main.py --test-connection    # Test API connection")
        print("  python main.py --run                # Run extraction process")
        return
    
    # Test connection
    if args.test_connection:
        test_connection()
        return
    
    # Run extraction
    if args.run:
        # Test connection first
        print("Testing API connection before starting extraction...")
        if not test_connection():
            print("\n[ERROR] API connection test failed. Please check your configuration.")
            sys.exit(1)
        
        print("\nStarting extraction process...\n")
        run_extraction()


if __name__ == "__main__":
    main()

