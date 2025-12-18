"""
Logging utilities for Sales Variables Extractor
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from config.settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT


def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Log file path
        level: Logging level
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Create timestamp for log files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Main logger
main_log_file = LOGS_DIR / f"variables_extraction_{timestamp}.log"
logger = setup_logger("sales_variables_extractor", str(main_log_file), getattr(logging, LOG_LEVEL))

# Error logger
error_log_file = LOGS_DIR / f"variables_extraction_errors_{timestamp}.log"
error_logger = setup_logger("sales_variables_extractor.errors", str(error_log_file), logging.ERROR)


def get_logger() -> logging.Logger:
    """Get the main logger"""
    return logger


def get_error_logger() -> logging.Logger:
    """Get the error logger"""
    return error_logger


class ExtractionLogger:
    """Specialized logger for tracking extraction progress"""
    
    def __init__(self):
        self.logger = get_logger()
        self.stats = {
            "total_rows": 0,
            "lgs_success": 0,
            "lgs_failed": 0,
            "omc_success": 0,
            "omc_failed": 0,
            "both_success": 0,
            "total_retries": 0
        }
    
    def log_extraction_start(self, row_id: str, row_number: int):
        """Log the start of extraction for a row"""
        self.logger.info(f"Starting extraction for Row {row_number} (ID: {row_id})")
        self.stats["total_rows"] += 1
    
    def log_lgs_success(self, row_id: str, row_number: int):
        """Log successful LGS extraction"""
        self.logger.info(f"LGS extraction successful for Row {row_number}")
        self.stats["lgs_success"] += 1
    
    def log_lgs_failure(self, row_id: str, row_number: int, error: str):
        """Log failed LGS extraction"""
        self.logger.error(f"LGS extraction failed for Row {row_number}: {error}")
        error_logger.error(f"Row {row_number} (ID: {row_id}) - LGS Error: {error}")
        self.stats["lgs_failed"] += 1
    
    def log_omc_success(self, row_id: str, row_number: int):
        """Log successful OMC extraction"""
        self.logger.info(f"OMC extraction successful for Row {row_number}")
        self.stats["omc_success"] += 1
    
    def log_omc_failure(self, row_id: str, row_number: int, error: str):
        """Log failed OMC extraction"""
        self.logger.error(f"OMC extraction failed for Row {row_number}: {error}")
        error_logger.error(f"Row {row_number} (ID: {row_id}) - OMC Error: {error}")
        self.stats["omc_failed"] += 1
    
    def log_retry(self, row_id: str, attempt: int, max_attempts: int):
        """Log a retry attempt"""
        self.logger.warning(f"Retry attempt {attempt}/{max_attempts} for Row ID: {row_id}")
        self.stats["total_retries"] += 1
    
    def log_complete_success(self, row_id: str, row_number: int):
        """Log successful extraction of both LGS and OMC"""
        self.logger.info(f"Complete extraction successful for Row {row_number}")
        self.stats["both_success"] += 1
    
    def print_stats(self):
        """Print extraction statistics"""
        self.logger.info("="*80)
        self.logger.info("EXTRACTION STATISTICS")
        self.logger.info("="*80)
        self.logger.info(f"Total Rows Processed: {self.stats['total_rows']}")
        self.logger.info(f"LGS Successful: {self.stats['lgs_success']}")
        self.logger.info(f"LGS Failed: {self.stats['lgs_failed']}")
        self.logger.info(f"OMC Successful: {self.stats['omc_success']}")
        self.logger.info(f"OMC Failed: {self.stats['omc_failed']}")
        self.logger.info(f"Both Successful: {self.stats['both_success']}")
        self.logger.info(f"Total Retries: {self.stats['total_retries']}")
        self.logger.info("="*80)


# Global extraction logger instance
extraction_logger = ExtractionLogger()


def get_extraction_logger() -> ExtractionLogger:
    """Get the extraction logger"""
    return extraction_logger

