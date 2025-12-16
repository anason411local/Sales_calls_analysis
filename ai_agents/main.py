"""
Main execution script for Sales Call Analyzer.
Run this script to process sales call data and extract structured information.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sales_call_analyzer.config import settings, ensure_directories
from sales_call_analyzer.utils import logger
from sales_call_analyzer.orchestrator import BatchProcessor


def main():
    """Main execution function"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Sales Call Analyzer - Extract structured data from call transcriptions"
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start fresh without resuming from checkpoint"
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test Gemini API connection and exit"
    )
    
    args = parser.parse_args()
    
    # Ensure directories exist
    ensure_directories()
    
    # Print banner
    print("\n" + "="*80)
    print("SALES CALL ANALYZER - AI AGENT")
    print("="*80)
    print(f"Model: {settings.GEMINI_MODEL}")
    print(f"Batch Size: {settings.BATCH_SIZE}")
    print(f"Input: {settings.INPUT_CSV}")
    print(f"Output: {settings.OUTPUT_CSV}")
    print("="*80 + "\n")
    
    # Test connection if requested
    if args.test_connection:
        logger.info("Testing Gemini API connection...")
        from sales_call_analyzer.llm import GeminiClient
        client = GeminiClient()
        success = client.test_connection()
        if success:
            print("\n[OK] Gemini API connection successful!")
            return 0
        else:
            print("\n[FAIL] Gemini API connection failed!")
            return 1
    
    try:
        # Initialize batch processor
        logger.info("Initializing batch processor...")
        processor = BatchProcessor()
        
        # Process all data
        resume = not args.no_resume
        logger.info(f"Starting extraction process (resume={'enabled' if resume else 'disabled'})...")
        
        success_count, fail_count = processor.process_all(resume=resume)
        
        # Print summary
        print("\n" + "="*80)
        print("EXTRACTION COMPLETE")
        print("="*80)
        print(f"[OK] Successful: {success_count}")
        print(f"[FAIL] Failed: {fail_count}")
        print(f"Success Rate: {success_count/(success_count+fail_count)*100:.1f}%")
        print(f"\nOutput saved to: {settings.OUTPUT_DATA_DIR / settings.OUTPUT_CSV}")
        print(f"Logs saved to: {settings.LOGS_DIR}")
        print("="*80 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n\nProcess interrupted by user")
        print("\n[WARN] Process interrupted. Progress has been saved.")
        print("Run again to resume from checkpoint.\n")
        return 130
        
    except Exception as e:
        logger.critical(f"Fatal error in main execution: {str(e)}")
        print(f"\n[FAIL] Fatal error: {str(e)}")
        print("Check logs for details.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

