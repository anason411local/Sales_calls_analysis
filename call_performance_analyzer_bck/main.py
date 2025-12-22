"""
Main entry point for Call Performance Analyzer
"""
import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.batch_orchestrator import BatchOrchestrator
from utils.logger import logger
from config.settings import OUTPUT_FILE


def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(
        description="Call Performance Analyzer - Analyze LGS to OMC call performance"
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the analysis"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Resume from checkpoint (default: True)"
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Start fresh (ignore checkpoint)"
    )
    
    args = parser.parse_args()
    
    if not args.run:
        parser.print_help()
        return
    
    try:
        logger.info("Call Performance Analyzer Starting...")
        
        # Create orchestrator
        orchestrator = BatchOrchestrator()
        
        # Run analysis
        resume = not args.fresh
        report_path = orchestrator.run_analysis(resume=resume)
        
        logger.info(f"\n{'='*80}")
        logger.info("ANALYSIS COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Report saved to: {report_path}")
        logger.info(f"{'='*80}\n")
        
        print(f"\n[SUCCESS] Analysis complete! Report saved to: {report_path}\n")
        
    except KeyboardInterrupt:
        logger.warning("\nAnalysis interrupted by user")
        print("\n[WARNING] Analysis interrupted. Progress has been saved. Run with --resume to continue.\n")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\n[ERROR] {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

