"""
Data handler for CSV I/O operations with resume capability.
Handles reading input data, writing output data, and managing checkpoints.
"""

import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..config.settings import settings
from ..utils.logger import logger


class DataHandler:
    """Handles all data I/O operations"""
    
    def __init__(self):
        """Initialize data handler"""
        self.input_path = settings.INPUT_DATA_DIR / settings.INPUT_CSV
        self.output_path = settings.OUTPUT_DATA_DIR / settings.OUTPUT_CSV
        self.checkpoint_path = settings.CHECKPOINT_DIR / "extraction_checkpoint.json"
        
        logger.info(f"Data handler initialized")
        logger.info(f"Input: {self.input_path}")
        logger.info(f"Output: {self.output_path}")
        logger.info(f"Checkpoint: {self.checkpoint_path}")
    
    def load_input_data(self) -> pd.DataFrame:
        """
        Load input CSV data.
        
        Returns:
            DataFrame with input data
        """
        try:
            logger.info(f"Loading input data from {self.input_path}")
            df = pd.read_csv(self.input_path)
            logger.info(f"[OK] Loaded {len(df)} rows from input CSV")
            logger.info(f"Columns: {list(df.columns)}")
            
            # Validate required columns
            required_cols = settings.INPUT_COLUMNS
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                logger.error(f"Missing required columns: {missing_cols}")
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            return df
            
        except FileNotFoundError:
            logger.error(f"Input file not found: {self.input_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading input data: {str(e)}")
            raise
    
    def save_output_data(
        self,
        results: List[Dict[str, Any]],
        mode: str = "w"
    ) -> None:
        """
        Save extracted data to output CSV.
        
        Args:
            results: List of flattened extraction results
            mode: Write mode ('w' for write, 'a' for append)
        """
        try:
            if not results:
                logger.warning("No results to save")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(results)
            
            # Ensure output directory exists
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to CSV
            if mode == "w":
                df.to_csv(self.output_path, index=False)
                logger.info(f"[OK] Saved {len(df)} rows to {self.output_path}")
            elif mode == "a":
                # Append mode - check if file exists
                if self.output_path.exists():
                    df.to_csv(self.output_path, mode='a', header=False, index=False)
                    logger.info(f"[OK] Appended {len(df)} rows to {self.output_path}")
                else:
                    df.to_csv(self.output_path, index=False)
                    logger.info(f"[OK] Created new file and saved {len(df)} rows to {self.output_path}")
            
        except Exception as e:
            logger.error(f"Error saving output data: {str(e)}")
            raise
    
    def save_checkpoint(
        self,
        processed_indices: List[int],
        failed_indices: List[int],
        batch_num: int,
        total_batches: int
    ) -> None:
        """
        Save processing checkpoint for resume capability.
        
        Args:
            processed_indices: List of successfully processed row indices
            failed_indices: List of failed row indices
            batch_num: Current batch number
            total_batches: Total number of batches
        """
        try:
            checkpoint_data = {
                "timestamp": datetime.now().isoformat(),
                "processed_indices": processed_indices,
                "failed_indices": failed_indices,
                "batch_num": batch_num,
                "total_batches": total_batches,
                "last_processed_index": max(processed_indices) if processed_indices else -1
            }
            
            # Ensure checkpoint directory exists
            self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save checkpoint
            with open(self.checkpoint_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            logger.log_checkpoint_save(self.checkpoint_path, len(processed_indices))
            
        except Exception as e:
            logger.error(f"Error saving checkpoint: {str(e)}")
            # Don't raise - checkpoint failure shouldn't stop processing
    
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Load processing checkpoint if it exists.
        
        Returns:
            Checkpoint data dictionary or None if no checkpoint exists
        """
        try:
            if not self.checkpoint_path.exists():
                logger.info("No checkpoint found - starting fresh")
                return None
            
            with open(self.checkpoint_path, 'r') as f:
                checkpoint_data = json.load(f)
            
            logger.log_checkpoint_load(
                self.checkpoint_path,
                checkpoint_data.get("last_processed_index", -1) + 1
            )
            
            return checkpoint_data
            
        except Exception as e:
            logger.error(f"Error loading checkpoint: {str(e)}")
            return None
    
    def clear_checkpoint(self) -> None:
        """Clear checkpoint file after successful completion"""
        try:
            if self.checkpoint_path.exists():
                self.checkpoint_path.unlink()
                logger.info("[OK] Checkpoint cleared")
        except Exception as e:
            logger.warning(f"Could not clear checkpoint: {str(e)}")
    
    def get_rows_to_process(
        self,
        df: pd.DataFrame,
        checkpoint: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[int], List[int]]:
        """
        Determine which rows need to be processed.
        
        Args:
            df: Input DataFrame
            checkpoint: Optional checkpoint data
            
        Returns:
            Tuple of (rows_to_process, failed_rows_to_retry)
        """
        total_rows = len(df)
        all_indices = list(range(total_rows))
        
        if checkpoint is None:
            # No checkpoint - process all rows
            return all_indices, []
        
        # Resume from checkpoint
        processed_indices = set(checkpoint.get("processed_indices", []))
        failed_indices = checkpoint.get("failed_indices", [])
        
        # Rows that haven't been processed yet
        remaining_indices = [i for i in all_indices if i not in processed_indices]
        
        logger.info(f"Resuming from checkpoint:")
        logger.info(f"  - Already processed: {len(processed_indices)} rows")
        logger.info(f"  - Failed (will retry): {len(failed_indices)} rows")
        logger.info(f"  - Remaining: {len(remaining_indices)} rows")
        
        return remaining_indices, failed_indices
    
    def prepare_row_data(self, row: pd.Series, index: int) -> Dict[str, Any]:
        """
        Prepare row data for processing.
        
        Args:
            row: DataFrame row
            index: Row index
            
        Returns:
            Dictionary with prepared data
        """
        return {
            "row_index": index,
            "call_id": row.get("id"),
            "call_date": str(row.get("call_date_omc", "")),
            "call_duration": int(row.get("length_in_sec_omc", 0)) if pd.notna(row.get("length_in_sec_omc")) else 0,
            "transcription": str(row.get("transcription_omc", "")),
            "agent_name": str(row.get("fullname_omc", "Unknown"))
        }
    
    def create_batches(
        self,
        indices: List[int],
        batch_size: int = None
    ) -> List[List[int]]:
        """
        Create batches of row indices.
        
        Args:
            indices: List of row indices
            batch_size: Size of each batch (default from settings)
            
        Returns:
            List of batches (each batch is a list of indices)
        """
        if batch_size is None:
            batch_size = settings.BATCH_SIZE
        
        batches = []
        for i in range(0, len(indices), batch_size):
            batch = indices[i:i + batch_size]
            batches.append(batch)
        
        logger.info(f"Created {len(batches)} batches of size {batch_size}")
        return batches
    
    def export_summary_report(
        self,
        total_rows: int,
        success_count: int,
        fail_count: int,
        failed_indices: List[int],
        duration: float
    ) -> None:
        """
        Export a summary report of the extraction process.
        
        Args:
            total_rows: Total number of rows processed
            success_count: Number of successful extractions
            fail_count: Number of failed extractions
            failed_indices: List of failed row indices
            duration: Total processing duration in seconds
        """
        try:
            report_path = settings.OUTPUT_DATA_DIR / f"extraction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_path, 'w') as f:
                f.write("="*80 + "\n")
                f.write("SALES CALL EXTRACTION SUMMARY REPORT\n")
                f.write("="*80 + "\n\n")
                
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write(f"Total Rows: {total_rows}\n")
                f.write(f"Successful: {success_count} ({success_count/total_rows*100:.1f}%)\n")
                f.write(f"Failed: {fail_count} ({fail_count/total_rows*100:.1f}%)\n\n")
                
                f.write(f"Total Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)\n")
                f.write(f"Average Time per Row: {duration/total_rows:.2f} seconds\n\n")
                
                if failed_indices:
                    f.write(f"Failed Row Indices:\n")
                    for idx in failed_indices:
                        f.write(f"  - Row {idx}\n")
                    f.write("\n")
                
                f.write(f"Input File: {self.input_path}\n")
                f.write(f"Output File: {self.output_path}\n\n")
                
                f.write("="*80 + "\n")
            
            logger.info(f"[OK] Summary report saved to {report_path}")
            
        except Exception as e:
            logger.warning(f"Could not save summary report: {str(e)}")

