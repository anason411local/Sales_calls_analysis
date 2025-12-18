"""
Comprehensive logging setup for Sales Call Analyzer V2
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from config.settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT


class SalesCallLogger:
    """Centralized logger for the sales call analyzer"""
    
    def __init__(self, name: str = "SalesCallAnalyzer"):
        self.name = name
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with file and console handlers"""
        # Create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Ensure logs directory exists
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = LOGS_DIR / f"sales_call_analysis_{timestamp}.log"
        
        # File handler - detailed logs
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # Console handler - important logs only (no Unicode characters for Windows)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt=LOG_DATE_FORMAT
        )
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Logger initialized. Log file: {log_file}")
    
    def get_logger(self):
        """Get the configured logger instance"""
        return self.logger
    
    def log_extraction_start(self, row_id: str, row_num: int):
        """Log the start of extraction for a row"""
        self.logger.info(f"Starting extraction for Row {row_num} (ID: {row_id})")
    
    def log_extraction_success(self, row_id: str, row_num: int):
        """Log successful extraction"""
        self.logger.info(f"Successfully extracted data for Row {row_num} (ID: {row_id})")
    
    def log_extraction_failure(self, row_id: str, row_num: int, error: str):
        """Log extraction failure"""
        self.logger.error(f"Failed to extract data for Row {row_num} (ID: {row_id}): {error}")
    
    def log_batch_start(self, batch_num: int, batch_size: int):
        """Log the start of a batch"""
        self.logger.info(f"Processing Batch {batch_num} ({batch_size} rows)")
    
    def log_batch_complete(self, batch_num: int, success_count: int, fail_count: int):
        """Log batch completion"""
        self.logger.info(
            f"Batch {batch_num} complete - "
            f"Success: {success_count}, Failed: {fail_count}"
        )
    
    def log_retry_attempt(self, row_id: str, attempt: int, max_attempts: int):
        """Log retry attempt"""
        self.logger.warning(
            f"Retry attempt {attempt}/{max_attempts} for Row ID: {row_id}"
        )
    
    def log_checkpoint_save(self, processed_count: int):
        """Log checkpoint save"""
        self.logger.info(f"Checkpoint saved. Processed rows: {processed_count}")
    
    def log_resume(self, last_processed_row: int):
        """Log resume from checkpoint"""
        self.logger.info(f"Resuming from row {last_processed_row + 1}")
    
    def log_llm_call(self, model: str, row_id: str):
        """Log LLM API call"""
        self.logger.debug(f"Calling {model} for Row ID: {row_id}")
    
    def log_llm_response(self, row_id: str, success: bool):
        """Log LLM response"""
        status = "successful" if success else "failed"
        self.logger.debug(f"LLM response {status} for Row ID: {row_id}")
    
    def log_processing_complete(self, total_rows: int, success_count: int, fail_count: int):
        """Log overall processing completion"""
        self.logger.info("=" * 80)
        self.logger.info("PROCESSING COMPLETE")
        self.logger.info(f"Total rows: {total_rows}")
        self.logger.info(f"Successfully processed: {success_count}")
        self.logger.info(f"Failed: {fail_count}")
        self.logger.info(f"Success rate: {(success_count/total_rows)*100:.2f}%")
        self.logger.info("=" * 80)


# Global logger instance
_logger_instance = None

def get_logger() -> logging.Logger:
    """Get or create the global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SalesCallLogger()
    return _logger_instance.get_logger()


def get_sales_logger() -> SalesCallLogger:
    """Get or create the global SalesCallLogger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SalesCallLogger()
    return _logger_instance

