"""
Batch Processor with Retry Logic
Orchestrates the processing of sales calls in batches
"""
import pandas as pd
from typing import List, Dict, Any
from agents.extraction_graph import run_extraction
from data.data_handler import DataHandler
from schemas.extraction_schemas import SalesCallExtraction
from config.settings import (
    BATCH_SIZE,
    MAX_RETRIES,
    INPUT_COLUMNS,
    SYSTEM_INSTRUCTIONS_FILE,
    EXTRACTION_PROMPT_FILE
)
from prompts.prompt_templates import load_prompt_file
from utils.logger import get_logger, get_sales_logger

logger = get_logger()
sales_logger = get_sales_logger()


class BatchProcessor:
    """Orchestrates batch processing of sales calls with retry logic"""
    
    def __init__(self):
        """Initialize batch processor"""
        self.data_handler = DataHandler()
        self.batch_size = BATCH_SIZE
        self.max_retries = MAX_RETRIES
        
        # Load system instructions and extraction prompt
        self.system_instructions = load_prompt_file(SYSTEM_INSTRUCTIONS_FILE)
        self.extraction_prompt = load_prompt_file(EXTRACTION_PROMPT_FILE)
        
        logger.info(f"BatchProcessor initialized with batch size: {self.batch_size}")
    
    def process_all(self):
        """
        Process all rows in the input CSV.
        Supports resuming from checkpoint.
        """
        try:
            # Load input data
            df = self.data_handler.load_input_data()
            total_rows = len(df)
            
            logger.info(f"Starting processing of {total_rows} rows")
            logger.info("=" * 80)
            
            # Load checkpoint if exists
            checkpoint = self.data_handler.load_checkpoint()
            start_row = 0
            if checkpoint:
                start_row = checkpoint.get('last_processed_row', -1) + 1
            
            # Process in batches
            successful_extractions = []
            failed_rows = []
            
            for batch_start in range(start_row, total_rows, self.batch_size):
                batch_end = min(batch_start + self.batch_size, total_rows)
                batch_df = df.iloc[batch_start:batch_end]
                
                batch_num = (batch_start // self.batch_size) + 1
                logger.info(f"\n{'='*80}")
                logger.info(f"Processing Batch {batch_num} (Rows {batch_start} to {batch_end-1})")
                logger.info(f"{'='*80}")
                
                sales_logger.log_batch_start(batch_num, len(batch_df))
                
                # Process batch
                batch_results = self._process_batch(batch_df, batch_start)
                
                # Separate successful and failed
                batch_success = [r for r in batch_results if r.extraction_success]
                batch_failed = [r for r in batch_results if not r.extraction_success]
                
                successful_extractions.extend(batch_success)
                failed_rows.extend(batch_failed)
                
                # Save results incrementally
                if batch_success:
                    self.data_handler.save_results(
                        batch_success,
                        append=(batch_start > start_row)
                    )
                
                # Save checkpoint
                self.data_handler.save_checkpoint(
                    last_processed_row=batch_end - 1,
                    total_processed=len(successful_extractions) + len(failed_rows)
                )
                
                sales_logger.log_batch_complete(
                    batch_num,
                    len(batch_success),
                    len(batch_failed)
                )
            
            # Retry failed rows
            if failed_rows:
                logger.info(f"\n{'='*80}")
                logger.info(f"Retrying {len(failed_rows)} failed rows")
                logger.info(f"{'='*80}")
                
                retry_results = self._retry_failed_rows(failed_rows, df)
                
                # Separate successful retries and permanent failures
                retry_success = [r for r in retry_results if r.extraction_success]
                permanent_failures = [r for r in retry_results if not r.extraction_success]
                
                # Save successful retries
                if retry_success:
                    self.data_handler.save_results(retry_success, append=True)
                    successful_extractions.extend(retry_success)
                
                # Save permanent failures with empty data
                if permanent_failures:
                    self.data_handler.save_results(permanent_failures, append=True)
            
            # Log final summary
            sales_logger.log_processing_complete(
                total_rows=total_rows,
                success_count=len(successful_extractions),
                fail_count=len(failed_rows) - len([r for r in retry_results if r.extraction_success]) if failed_rows else 0
            )
            
            logger.info(f"\nProcessing complete!")
            logger.info(f"Output saved to: {self.data_handler.output_file}")
            
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            raise
    
    def _process_batch(
        self,
        batch_df: pd.DataFrame,
        batch_start_idx: int
    ) -> List[SalesCallExtraction]:
        """
        Process a single batch of rows.
        
        Args:
            batch_df: DataFrame containing the batch
            batch_start_idx: Starting index of the batch in the full dataset
        
        Returns:
            List of SalesCallExtraction results
        """
        results = []
        
        for idx, row in batch_df.iterrows():
            row_number = batch_start_idx + (idx - batch_df.index[0])
            
            try:
                # Extract input data with NaN handling
                row_id = str(row.get(INPUT_COLUMNS['id'], f'row_{row_number}'))
                transcription_id = str(row.get(INPUT_COLUMNS['transcription_id'], '')) if pd.notna(row.get(INPUT_COLUMNS['transcription_id'])) else ""
                call_date = str(row[INPUT_COLUMNS['call_date']]) if pd.notna(row[INPUT_COLUMNS['call_date']]) else ""
                
                # Handle NaN for length_in_sec
                length_in_sec_raw = row[INPUT_COLUMNS['length_in_sec']]
                length_in_sec = int(length_in_sec_raw) if pd.notna(length_in_sec_raw) else 0
                
                transcription = str(row[INPUT_COLUMNS['transcription']]) if pd.notna(row[INPUT_COLUMNS['transcription']]) else ""
                fullname = str(row[INPUT_COLUMNS['fullname']]) if pd.notna(row[INPUT_COLUMNS['fullname']]) else ""
                
                # Skip rows with missing critical data (transcription)
                if not transcription or transcription == "nan":
                    logger.warning(f"Skipping row {row_number} - missing transcription")
                    failed_extraction = self.data_handler.create_failed_extraction(
                        row_id=row_id,
                        transcription_id=transcription_id,
                        call_date=call_date,
                        fullname=fullname,
                        length_in_sec=length_in_sec,
                        error_message="Missing transcription data"
                    )
                    results.append(failed_extraction)
                    continue
                
                # Run extraction workflow
                final_state = run_extraction(
                    row_id=row_id,
                    row_number=row_number,
                    call_date=call_date,
                    length_in_sec=length_in_sec,
                    transcription=transcription,
                    fullname=fullname,
                    system_instructions=self.system_instructions,
                    extraction_prompt=self.extraction_prompt,
                    max_attempts=self.max_retries
                )
                
                # Add transcription_id to the result
                if final_state['extraction_success'] and final_state['extraction_result']:
                    result = final_state['extraction_result']
                    # Store transcription_id in the extraction result
                    result.transcription_id = transcription_id
                    results.append(result)
                else:
                    # Create failed extraction
                    failed_extraction = self.data_handler.create_failed_extraction(
                        row_id=row_id,
                        transcription_id=transcription_id,
                        call_date=call_date,
                        fullname=fullname,
                        length_in_sec=length_in_sec,
                        error_message=final_state.get('error_message', 'Unknown error')
                    )
                    results.append(failed_extraction)
                
            except Exception as e:
                logger.error(f"Failed to process row {row_number}: {str(e)}")
                
                # Create failed extraction
                failed_extraction = self.data_handler.create_failed_extraction(
                    row_id=str(row.get(INPUT_COLUMNS['id'], f'row_{row_number}')),
                    transcription_id=str(row.get(INPUT_COLUMNS['transcription_id'], '')) if pd.notna(row.get(INPUT_COLUMNS['transcription_id'])) else "",
                    call_date=str(row.get(INPUT_COLUMNS['call_date'], '')),
                    fullname=str(row.get(INPUT_COLUMNS['fullname'], '')),
                    length_in_sec=int(row.get(INPUT_COLUMNS['length_in_sec'], 0)),
                    error_message=str(e)
                )
                results.append(failed_extraction)
        
        return results
    
    def _retry_failed_rows(
        self,
        failed_extractions: List[SalesCallExtraction],
        full_df: pd.DataFrame
    ) -> List[SalesCallExtraction]:
        """
        Retry failed extractions.
        
        Args:
            failed_extractions: List of failed SalesCallExtraction objects
            full_df: Full DataFrame to get original row data
        
        Returns:
            List of retry results
        """
        retry_results = []
        
        for failed in failed_extractions:
            try:
                # Find original row
                row_id = failed.row_id
                original_row = full_df[full_df['id'].astype(str) == row_id].iloc[0]
                
                # Extract input data with NaN handling
                call_date = str(original_row[INPUT_COLUMNS['call_date']]) if pd.notna(original_row[INPUT_COLUMNS['call_date']]) else ""
                
                length_in_sec_raw = original_row[INPUT_COLUMNS['length_in_sec']]
                length_in_sec = int(length_in_sec_raw) if pd.notna(length_in_sec_raw) else 0
                
                transcription = str(original_row[INPUT_COLUMNS['transcription']]) if pd.notna(original_row[INPUT_COLUMNS['transcription']]) else ""
                fullname = str(original_row[INPUT_COLUMNS['fullname']]) if pd.notna(original_row[INPUT_COLUMNS['fullname']]) else ""
                
                logger.info(f"Retrying extraction for Row ID: {row_id}")
                
                # Run extraction workflow with additional retry
                final_state = run_extraction(
                    row_id=row_id,
                    row_number=0,  # Row number not important for retry
                    call_date=call_date,
                    length_in_sec=length_in_sec,
                    transcription=transcription,
                    fullname=fullname,
                    system_instructions=self.system_instructions,
                    extraction_prompt=self.extraction_prompt,
                    max_attempts=self.max_retries
                )
                
                # Get extraction result
                if final_state['extraction_success'] and final_state['extraction_result']:
                    retry_results.append(final_state['extraction_result'])
                else:
                    # Still failed, keep the failed extraction
                    retry_results.append(failed)
                
            except Exception as e:
                logger.error(f"Retry failed for Row ID {failed.row_id}: {str(e)}")
                retry_results.append(failed)
        
        return retry_results

