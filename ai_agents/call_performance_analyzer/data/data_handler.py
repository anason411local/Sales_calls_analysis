"""
Data handler for loading, checkpointing, and saving analysis data
"""
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import logger
from config.settings import (
    INPUT_FILE,
    INPUT_COLUMNS,
    CHECKPOINT_FILE,
    OUTPUT_FILE,
    BATCH_SIZE
)


class DataHandler:
    """Handles all data I/O operations"""
    
    def __init__(self):
        self.input_file = INPUT_FILE
        self.checkpoint_file = CHECKPOINT_FILE
        self.output_file = OUTPUT_FILE
        
    def load_input_data(self) -> pd.DataFrame:
        """
        Load input CSV data
        
        Returns:
            DataFrame with input data
        """
        try:
            logger.info(f"Loading input data from {self.input_file}")
            
            df = pd.read_csv(self.input_file)
            
            # Verify required columns exist
            required_cols = list(INPUT_COLUMNS.values())
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                logger.warning(f"Missing columns: {missing_cols}")
            
            logger.info(f"Loaded {len(df)} rows from input file")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load input data: {str(e)}")
            raise
    
    def get_checkpoint(self) -> Optional[Dict]:
        """
        Load checkpoint if exists
        
        Returns:
            Checkpoint data or None
        """
        if not self.checkpoint_file.exists():
            logger.info("No checkpoint file found. Starting fresh.")
            return None
        
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            
            logger.info(f"Loaded checkpoint: {checkpoint['processed_rows']} rows processed")
            return checkpoint
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {str(e)}")
            return None
    
    def save_checkpoint(self, processed_rows: int, batch_number: int):
        """
        Save processing checkpoint
        
        Args:
            processed_rows: Number of rows processed
            batch_number: Current batch number
        """
        try:
            checkpoint = {
                'processed_rows': processed_rows,
                'batch_number': batch_number,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2)
            
            logger.debug(f"Checkpoint saved: {processed_rows} rows, batch {batch_number}")
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {str(e)}")
    
    def save_report(self, report_content: str):
        """
        Save final report to file
        
        Args:
            report_content: Markdown report content
        """
        try:
            logger.info(f"Saving report to {self.output_file}")
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Report saved successfully: {self.output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
            raise
    
    def clear_checkpoint(self):
        """Clear checkpoint file"""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            logger.info("Checkpoint cleared")
    
    def get_batches(self, df: pd.DataFrame, start_row: int = 0) -> List[pd.DataFrame]:
        """
        Split DataFrame into batches
        
        Args:
            df: Input DataFrame
            start_row: Row to start from (for resuming)
            
        Returns:
            List of DataFrame batches
        """
        if start_row > 0:
            df = df.iloc[start_row:]
            logger.info(f"Resuming from row {start_row}")
        
        batches = []
        for i in range(0, len(df), BATCH_SIZE):
            batch = df.iloc[i:i + BATCH_SIZE]
            batches.append(batch)
        
        logger.info(f"Created {len(batches)} batches of size {BATCH_SIZE}")
        return batches
    
    def dataframe_to_dict_list(self, df: pd.DataFrame) -> List[Dict]:
        """
        Convert DataFrame to list of dictionaries
        
        Args:
            df: Input DataFrame
            
        Returns:
            List of row dictionaries
        """
        return df.to_dict('records')

