"""
Main Entry Point for Sales Variables Extractor
Agentic AI framework for extracting LGS and OMC variables from sales call transcripts
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
    INPUT_CSV,
    OUTPUT_CSV
)

logger = get_logger()


def print_banner():
    """Print welcome banner"""
    banner = """
================================================================================
    SALES VARIABLES EXTRACTOR - AGENTIC AI FRAMEWORK
================================================================================
    Model: Gemini 2.0 Flash Exp
    Framework: LangGraph + Langchain
    
    Extracts:
    - LGS (Lead Generation Specialist) Variables
    - OMC (Outbound Marketing Closer) Variables
    
    Input: {input_file}
    Output: {output_file}
================================================================================
""".format(
        input_file=INPUT_CSV.name,
        output_file=OUTPUT_CSV.name
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
        print(f"  API Key Prefix: {model_info['api_key_prefix']}")
        
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


def run_extraction(resume: bool = True):
    """
    Run the main extraction process.
    
    Args:
        resume: Whether to resume from checkpoint
    """
    logger.info("Starting Sales Variables Extraction Process")
    logger.info(f"Input file: {INPUT_CSV}")
    logger.info(f"Output file: {OUTPUT_CSV}")
    logger.info(f"Model: {GEMINI_MODEL}")
    logger.info(f"Resume from checkpoint: {resume}")
    
    try:
        # Initialize batch processor
        processor = BatchProcessor()
        
        # Process all rows
        processor.process_all(resume=resume)
        
        print("\n[SUCCESS] Extraction process completed successfully!")
        print(f"Results saved to: {OUTPUT_CSV}")
        
    except Exception as e:
        logger.error(f"Extraction process failed: {str(e)}")
        print(f"\n[ERROR] Extraction process failed: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Sales Variables Extractor - LangGraph Agentic Framework"
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
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Start fresh (ignore checkpoint)"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # If no arguments, show help
    if not args.test_connection and not args.run:
        parser.print_help()
        print("\nExamples:")
        print("  python main.py --test-connection    # Test API connection")
        print("  python main.py --run                # Run extraction (resume from checkpoint)")
        print("  python main.py --run --fresh        # Run extraction (start fresh)")
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
        resume = not args.fresh
        run_extraction(resume=resume)


if __name__ == "__main__":
    main()

