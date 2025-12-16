"""
Batch processor orchestrator with retry logic.
Coordinates the extraction workflow across multiple batches of data.
"""

import time
from typing import List, Dict, Any, Tuple
from tqdm import tqdm

from ..agents.extraction_agent import SalesCallExtractionAgent
from ..data.data_handler import DataHandler
from ..config.settings import settings
from ..utils.logger import logger


class BatchProcessor:
    """
    Orchestrates batch processing of sales calls with retry logic.
    """
    
    def __init__(self):
        """Initialize batch processor"""
        self.agent = SalesCallExtractionAgent()
        self.data_handler = DataHandler()
        
        self.processed_indices = []
        self.failed_indices = []
        self.results = []
        
        logger.info("Batch processor initialized")
    
    def process_all(self, resume: bool = True) -> Tuple[int, int]:
        """
        Process all rows in the input CSV.
        
        Args:
            resume: Whether to resume from checkpoint if available
            
        Returns:
            Tuple of (success_count, fail_count)
        """
        start_time = time.time()
        
        # Load input data
        df = self.data_handler.load_input_data()
        total_rows = len(df)
        
        # Check for checkpoint
        checkpoint = None
        if resume and settings.ENABLE_CHECKPOINTING:
            checkpoint = self.data_handler.load_checkpoint()
        
        # Determine rows to process
        rows_to_process, failed_rows_to_retry = self.data_handler.get_rows_to_process(df, checkpoint)
        
        # If resuming, load already processed indices
        if checkpoint:
            self.processed_indices = checkpoint.get("processed_indices", [])
        
        # Log extraction start
        logger.log_extraction_start(total_rows)
        
        # Process main batches
        if rows_to_process:
            logger.info(f"\n{'='*80}")
            logger.info(f"PROCESSING MAIN BATCHES")
            logger.info(f"{'='*80}\n")
            
            batches = self.data_handler.create_batches(rows_to_process)
            self._process_batches(df, batches, is_retry=False)
        
        # Retry failed rows
        if failed_rows_to_retry or self.failed_indices:
            all_failed = list(set(failed_rows_to_retry + self.failed_indices))
            
            if all_failed:
                logger.info(f"\n{'='*80}")
                logger.info(f"RETRYING FAILED ROWS")
                logger.info(f"Total failed rows to retry: {len(all_failed)}")
                logger.info(f"{'='*80}\n")
                
                # Clear current failed list for retry
                self.failed_indices = []
                
                # Process failed rows in batches
                retry_batches = self.data_handler.create_batches(all_failed)
                self._process_batches(df, retry_batches, is_retry=True)
        
        # Save all results
        if self.results:
            self.data_handler.save_output_data(self.results, mode="w")
        
        # Calculate statistics
        success_count = len(self.processed_indices)
        fail_count = len(self.failed_indices)
        total_duration = time.time() - start_time
        
        # Log extraction end
        logger.log_extraction_end(total_rows, success_count, fail_count, total_duration)
        
        # Export summary report
        self.data_handler.export_summary_report(
            total_rows=total_rows,
            success_count=success_count,
            fail_count=fail_count,
            failed_indices=self.failed_indices,
            duration=total_duration
        )
        
        # Clear checkpoint on successful completion
        if settings.ENABLE_CHECKPOINTING:
            self.data_handler.clear_checkpoint()
        
        return success_count, fail_count
    
    def _process_batches(
        self,
        df,
        batches: List[List[int]],
        is_retry: bool = False
    ) -> None:
        """
        Process multiple batches.
        
        Args:
            df: Input DataFrame
            batches: List of batches (each batch is a list of row indices)
            is_retry: Whether this is a retry pass
        """
        total_batches = len(batches)
        
        for batch_num, batch_indices in enumerate(batches, 1):
            batch_start_time = time.time()
            
            # Log batch start
            logger.log_batch_start(batch_num, total_batches, batch_indices)
            
            # Process batch
            batch_results, batch_success, batch_failed = self._process_batch(
                df,
                batch_indices,
                batch_num,
                is_retry
            )
            
            # Store results
            self.results.extend(batch_results)
            self.processed_indices.extend(batch_success)
            self.failed_indices.extend(batch_failed)
            
            # Calculate batch statistics
            batch_duration = time.time() - batch_start_time
            
            # Log batch end
            logger.log_batch_end(
                batch_num,
                len(batch_success),
                len(batch_failed),
                batch_duration
            )
            
            # Save checkpoint after each batch
            if settings.ENABLE_CHECKPOINTING and not is_retry:
                self.data_handler.save_checkpoint(
                    processed_indices=self.processed_indices,
                    failed_indices=self.failed_indices,
                    batch_num=batch_num,
                    total_batches=total_batches
                )
    
    def _process_batch(
        self,
        df,
        batch_indices: List[int],
        batch_num: int,
        is_retry: bool = False
    ) -> Tuple[List[Dict[str, Any]], List[int], List[int]]:
        """
        Process a single batch of rows.
        
        Args:
            df: Input DataFrame
            batch_indices: List of row indices in this batch
            batch_num: Batch number
            is_retry: Whether this is a retry pass
            
        Returns:
            Tuple of (results, successful_indices, failed_indices)
        """
        batch_results = []
        batch_success = []
        batch_failed = []
        
        # Create progress bar for batch
        pbar = tqdm(
            batch_indices,
            desc=f"Batch {batch_num}",
            unit="row",
            leave=True
        )
        
        for idx in pbar:
            try:
                # Get row data
                row = df.iloc[idx]
                row_data = self.data_handler.prepare_row_data(row, idx)
                
                # Log row start
                logger.log_row_start(idx, row_data.get("call_id"))
                
                # Update progress bar
                pbar.set_postfix({
                    "call_id": str(row_data.get("call_id", "N/A"))[:20],
                    "status": "processing"
                })
                
                # Process row
                row_start_time = time.time()
                result = self._process_single_row(row_data)
                row_duration = time.time() - row_start_time
                
                # Check if successful
                if result and result.get("extraction_status") == "success":
                    batch_results.append(result)
                    batch_success.append(idx)
                    logger.log_row_success(idx, row_duration)
                    pbar.set_postfix({
                        "call_id": str(row_data.get("call_id", "N/A"))[:20],
                        "status": "[OK] success"
                    })
                else:
                    # Failed but still save result with NaN values
                    batch_results.append(result)
                    batch_failed.append(idx)
                    error_msg = result.get("extraction_notes", "Unknown error") if result else "No result returned"
                    logger.log_row_failure(idx, error_msg)
                    pbar.set_postfix({
                        "call_id": str(row_data.get("call_id", "N/A"))[:20],
                        "status": "[FAIL] failed"
                    })
                
            except Exception as e:
                # Unexpected error
                error_msg = f"Unexpected error: {str(e)}"
                logger.log_row_failure(idx, error_msg)
                batch_failed.append(idx)
                
                # Create fallback result
                fallback_result = self._create_error_result(row_data, error_msg)
                batch_results.append(fallback_result)
                
                pbar.set_postfix({
                    "call_id": str(row_data.get("call_id", "N/A"))[:20],
                    "status": "[ERROR]"
                })
        
        pbar.close()
        
        return batch_results, batch_success, batch_failed
    
    def _process_single_row(self, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single row through the extraction agent.
        
        Args:
            row_data: Prepared row data
            
        Returns:
            Flattened extraction result
        """
        try:
            result = self.agent.process_call(
                row_index=row_data["row_index"],
                call_id=row_data.get("call_id"),
                call_date=row_data["call_date"],
                call_duration=row_data["call_duration"],
                transcription=row_data["transcription"],
                agent_name=row_data["agent_name"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing row {row_data['row_index']}: {str(e)}")
            return self._create_error_result(row_data, str(e))
    
    def _create_error_result(
        self,
        row_data: Dict[str, Any],
        error_msg: str
    ) -> Dict[str, Any]:
        """
        Create an error result with basic metadata and NaN values.
        
        Args:
            row_data: Original row data
            error_msg: Error message
            
        Returns:
            Error result dictionary
        """
        from ..schemas.extraction_schemas import FlattenedCallData
        
        # Create result with metadata only
        error_result = {
            "call_id": row_data.get("call_id"),
            "call_date_omc": row_data.get("call_date"),
            "length_in_sec_omc": row_data.get("call_duration"),
            "fullname_omc": row_data.get("agent_name"),
            "transcription_omc": row_data.get("transcription", "")[:500],
            "extraction_status": "failed",
            "extraction_notes": error_msg
        }
        
        # Fill all other fields with None
        for field_name in FlattenedCallData.model_fields.keys():
            if field_name not in error_result:
                error_result[field_name] = None
        
        return error_result
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Dictionary with statistics
        """
        total = len(self.processed_indices) + len(self.failed_indices)
        
        return {
            "total_processed": total,
            "successful": len(self.processed_indices),
            "failed": len(self.failed_indices),
            "success_rate": len(self.processed_indices) / total * 100 if total > 0 else 0,
            "processed_indices": self.processed_indices,
            "failed_indices": self.failed_indices
        }

