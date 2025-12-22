"""
Standalone script to convert Markdown report to DOCX format
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.docx_converter import convert_report_to_docx
from utils.logger import logger


def main():
    """Convert the latest report to DOCX"""
    
    # Default paths
    reports_dir = Path(__file__).parent.parent.parent / "reports"
    markdown_file = reports_dir / "call_performance_analysis_report.md"
    
    # Check if custom path provided
    if len(sys.argv) > 1:
        markdown_file = Path(sys.argv[1])
    
    if not markdown_file.exists():
        print(f"[ERROR] Markdown file not found: {markdown_file}")
        print("\nUsage:")
        print("  python convert_to_docx.py [markdown_file]")
        print("\nExample:")
        print("  python convert_to_docx.py D:\\Sales_calls_analysis\\reports\\call_performance_analysis_report.md")
        sys.exit(1)
    
    try:
        print(f"\n[INFO] Converting: {markdown_file}")
        docx_path = convert_report_to_docx(str(markdown_file))
        print(f"\n[SUCCESS] DOCX report created!")
        print(f"[INFO] Location: {docx_path}")
        print(f"\nYou can now open this file in Microsoft Word.")
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
        print(f"\n[ERROR] Conversion failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

