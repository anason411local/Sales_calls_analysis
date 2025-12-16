"""
Comprehensive logging utility for the Sales Call Analyzer Agent.
Logs all activities, processes, and errors from start to finish.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from ..config.settings import settings


class SalesCallLogger:
    """Custom logger for sales call analysis"""
    
    def __init__(self, name: str = "SalesCallAnalyzer"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file and console handlers"""
        
        # Ensure logs directory exists
        settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Create formatters
        formatter = logging.Formatter(
            settings.LOG_FORMAT,
            datefmt=settings.LOG_DATE_FORMAT
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler - main log
        log_filename = f"sales_call_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = settings.LOGS_DIR / log_filename
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # File handler - error log
        error_log_filename = f"sales_call_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        error_log_path = settings.LOGS_DIR / error_log_filename
        error_handler = logging.FileHandler(error_log_path, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        self.logger.info(f"Logger initialized. Main log: {log_path}")
        self.logger.info(f"Error log: {error_log_path}")
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info: bool = True, **kwargs):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info: bool = True, **kwargs):
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)
    
    def log_batch_start(self, batch_num: int, total_batches: int, rows: list):
        """Log batch processing start"""
        self.info(f"\n{'='*80}")
        self.info(f"BATCH {batch_num}/{total_batches} - Processing {len(rows)} rows")
        self.info(f"{'='*80}")
    
    def log_batch_end(self, batch_num: int, success_count: int, fail_count: int, duration: float):
        """Log batch processing end"""
        self.info(f"BATCH {batch_num} COMPLETED - Success: {success_count}, Failed: {fail_count}, Duration: {duration:.2f}s")
        self.info(f"{'='*80}\n")
    
    def log_row_start(self, row_index: int, call_id: Optional[str] = None):
        """Log row processing start"""
        call_info = f" (Call ID: {call_id})" if call_id else ""
        self.info(f"Processing Row {row_index}{call_info}")
    
    def log_row_success(self, row_index: int, duration: float):
        """Log successful row processing"""
        self.info(f"[OK] Row {row_index} completed successfully in {duration:.2f}s")
    
    def log_row_failure(self, row_index: int, error: str, retry_count: int = 0):
        """Log failed row processing"""
        retry_info = f" (Retry {retry_count}/{settings.MAX_RETRIES})" if retry_count > 0 else ""
        self.error(f"[FAIL] Row {row_index} failed{retry_info}: {error}")
    
    def log_extraction_start(self, total_rows: int):
        """Log extraction process start"""
        self.info(f"\n{'#'*80}")
        self.info(f"SALES CALL EXTRACTION STARTED")
        self.info(f"Total rows to process: {total_rows}")
        self.info(f"Batch size: {settings.BATCH_SIZE}")
        self.info(f"{'#'*80}\n")
    
    def log_extraction_end(self, total_rows: int, success_count: int, fail_count: int, total_duration: float):
        """Log extraction process end"""
        self.info(f"\n{'#'*80}")
        self.info(f"SALES CALL EXTRACTION COMPLETED")
        self.info(f"Total rows processed: {total_rows}")
        self.info(f"Successful: {success_count} ({success_count/total_rows*100:.1f}%)")
        self.info(f"Failed: {fail_count} ({fail_count/total_rows*100:.1f}%)")
        self.info(f"Total duration: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
        self.info(f"Average time per row: {total_duration/total_rows:.2f}s")
        self.info(f"{'#'*80}\n")
    
    def log_checkpoint_save(self, checkpoint_path: Path, processed_rows: int):
        """Log checkpoint save"""
        self.info(f"[CHECKPOINT] Saved: {checkpoint_path} (Processed: {processed_rows} rows)")
    
    def log_checkpoint_load(self, checkpoint_path: Path, resume_from: int):
        """Log checkpoint load"""
        self.info(f"[CHECKPOINT] Loaded: {checkpoint_path} (Resuming from row: {resume_from})")
    
    def log_llm_call(self, model: str, prompt_length: int):
        """Log LLM API call"""
        self.debug(f"LLM Call - Model: {model}, Prompt length: {prompt_length} chars")
    
    def log_llm_response(self, response_length: int, tokens_used: Optional[int] = None):
        """Log LLM response"""
        token_info = f", Tokens: {tokens_used}" if tokens_used else ""
        self.debug(f"LLM Response - Length: {response_length} chars{token_info}")
    
    def log_validation_error(self, row_index: int, field: str, error: str):
        """Log Pydantic validation error"""
        self.warning(f"Validation error in Row {row_index}, Field '{field}': {error}")
    
    def log_data_quality(self, row_index: int, missing_fields: list, incomplete_fields: list):
        """Log data quality issues"""
        if missing_fields:
            self.warning(f"Row {row_index} - Missing fields: {', '.join(missing_fields)}")
        if incomplete_fields:
            self.warning(f"Row {row_index} - Incomplete fields: {', '.join(incomplete_fields)}")


# Global logger instance
logger = SalesCallLogger()

