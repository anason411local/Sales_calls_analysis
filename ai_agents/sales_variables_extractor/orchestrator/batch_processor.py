"""
Batch Processor for Sales Variables Extraction
Orchestrates the extraction process across multiple rows with checkpoint support
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from data.data_handler import DataHandler
from graph.extraction_graph import run_extraction
from config.settings import (
    CHECKPOINT_FILE,
    BATCH_SIZE,
    RATE_LIMIT_DELAY,
    MAX_RETRIES
)
from utils.logger import get_logger, get_extraction_logger
from schemas.variable_schemas import SalesVariablesExtraction

logger = get_logger()
extraction_logger = get_extraction_logger()


class BatchProcessor:
    """Orchestrates batch processing of sales variables extraction"""
    
    def __init__(self):
        """Initialize batch processor"""
        self.data_handler = DataHandler()
        self.checkpoint_data = {}
        self.results = []
        
        # Load checkpoint if exists
        self._load_checkpoint()
    
    def _load_checkpoint(self):
        """Load checkpoint data if it exists"""
        if CHECKPOINT_FILE.exists():
            try:
                with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                    self.checkpoint_data = json.load(f)
                logger.info(f"Loaded checkpoint: {len(self.checkpoint_data.get('processed_rows', []))} rows already processed")
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {str(e)}")
                self.checkpoint_data = {}
    
    def _save_checkpoint(self, processed_rows: List[str]):
        """
        Save checkpoint data.
        
        Args:
            processed_rows: List of processed row IDs
        """
        try:
            checkpoint = {
                "processed_rows": processed_rows,
                "last_updated": datetime.now().isoformat(),
                "total_processed": len(processed_rows)
            }
            
            with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2)
            
            logger.info(f"Checkpoint saved: {len(processed_rows)} rows processed")
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {str(e)}")
    
    def _is_row_processed(self, lead_id: str) -> bool:
        """
        Check if a row has already been processed.
        
        Args:
            lead_id: Lead ID to check
        
        Returns:
            True if already processed, False otherwise
        """
        processed_rows = self.checkpoint_data.get('processed_rows', [])
        return lead_id in processed_rows
    
    def _convert_state_to_result(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert agent state to result dictionary for CSV output.
        
        Args:
            state: Final agent state
        
        Returns:
            Dictionary with flattened results
        """
        result = {
            "lead_id": state['lead_id'],
            "row_number": state['row_number'],
            "customer_name": state.get('customer_name', ''),
            "service": state.get('service', ''),
            "customer_address": state.get('customer_address', ''),
        }
        
        # LGS Variables
        if state['lgs_extraction_success'] and state['lgs_variables']:
            lgs_vars = state['lgs_variables']
            
            # Timing & Seasonality
            if hasattr(lgs_vars, 'timing_seasonality') and lgs_vars.timing_seasonality:
                ts = lgs_vars.timing_seasonality
                result['timezone'] = ts.timezone
                result['season_status'] = ts.season_status
                result['season_month'] = ts.season_month
            
            # Agent Variables
            if hasattr(lgs_vars, 'agent_variables') and lgs_vars.agent_variables:
                av = lgs_vars.agent_variables
                result['lgs_sentiment_style'] = av.lgs_sentiment_style
                result['lgs_agent_gender'] = av.lgs_agent_gender
                result['is_decision_maker'] = av.is_decision_maker
                result['ready_for_customers'] = av.ready_for_customers
                result['forbidden_industry'] = av.forbidden_industry
                result['ready_to_transfer'] = av.ready_to_transfer
                result['customer_sentiment_lgs'] = av.customer_sentiment
                result['customer_language'] = av.customer_language
                result['customer_knows_marketing'] = av.customer_knows_marketing
                result['customer_availability'] = av.customer_availability
                result['who_said_hello_first'] = av.who_said_hello_first
                result['customer_marketing_experience'] = av.customer_marketing_experience
                result['technical_quality_score'] = av.technical_quality_score
                result['technical_quality_issues'] = av.technical_quality_issues
        
        result['lgs_extraction_success'] = state['lgs_extraction_success']
        result['lgs_error_message'] = state.get('lgs_error_message', '')
        
        # OMC Variables
        if state['omc_extraction_success'] and state['omc_variables']:
            omc_vars = state['omc_variables']
            
            # Customer Engagement
            if hasattr(omc_vars, 'customer_engagement') and omc_vars.customer_engagement:
                ce = omc_vars.customer_engagement
                result['customer_talk_percentage'] = ce.customer_talk_percentage
                result['agent_talk_percentage'] = ce.agent_talk_percentage
                result['talk_ratio_classification'] = ce.talk_ratio_classification
                result['total_discovery_questions'] = ce.total_discovery_questions
                result['goal1_questions'] = ce.goal1_questions
                result['goal2_questions'] = ce.goal2_questions
                result['goal3_questions'] = ce.goal3_questions
                result['total_buying_signals'] = ce.total_buying_signals
                result['total_resistance_signals'] = ce.total_resistance_signals
                result['signal_ratio'] = ce.signal_ratio
                result['customer_sentiment_omc'] = ce.customer_sentiment
            
            # Call Opening
            if hasattr(omc_vars, 'call_opening') and omc_vars.call_opening:
                co = omc_vars.call_opening
                result['time_to_reason_seconds'] = co.time_to_reason_seconds
                result['business_type_mentioned'] = co.business_type_mentioned
                result['location_mentioned'] = co.location_mentioned
                result['within_45_seconds'] = co.within_45_seconds
                result['call_structure_framed'] = co.call_structure_framed
            
            # Objection Handling
            if hasattr(omc_vars, 'objection_handling') and omc_vars.objection_handling:
                oh = omc_vars.objection_handling
                result['total_objections'] = oh.total_objections
                result['objections_acknowledged'] = oh.objections_acknowledged
                result['objections_rebutted'] = oh.objections_rebutted
                result['acknowledgement_rate'] = oh.acknowledgement_rate
                result['price_mentions_final_2min'] = oh.price_mentions_final_2min
                result['timeline_mentions_final_2min'] = oh.timeline_mentions_final_2min
                result['contract_mentions_final_2min'] = oh.contract_mentions_final_2min
                result['roi_calculation_presented'] = oh.roi_calculation_presented
            
            # Pace Control
            if hasattr(omc_vars, 'pace_control') and omc_vars.pace_control:
                pc = omc_vars.pace_control
                result['average_monologue_length'] = pc.average_monologue_length
                result['longest_monologue_length'] = pc.longest_monologue_length
                result['total_interruptions'] = pc.total_interruptions
                result['conversation_balance'] = pc.conversation_balance
                result['script_adherence'] = pc.script_adherence
                result['stages_skipped'] = pc.stages_skipped
            
            # Emotional Tone
            if hasattr(omc_vars, 'emotional_tone') and omc_vars.emotional_tone:
                et = omc_vars.emotional_tone
                result['name_used_first_minute'] = et.name_used_first_minute
                result['name_usage_count'] = et.name_usage_count
                result['rapport_elements_count'] = et.rapport_elements_count
                result['sentiment_progression'] = et.sentiment_progression
                result['customer_frustrations'] = et.customer_frustrations
                result['empathy_responses'] = et.empathy_responses
                result['empathy_response_rate'] = et.empathy_response_rate
            
            # Outcome Timing
            if hasattr(omc_vars, 'outcome_timing') and omc_vars.outcome_timing:
                ot = omc_vars.outcome_timing
                result['total_call_duration'] = ot.total_call_duration
                result['disconnect_stage'] = ot.disconnect_stage
                result['hang_up_initiated_by'] = ot.hang_up_initiated_by
                result['commitment_type'] = ot.commitment_type
                result['call_result_tag'] = ot.call_result_tag
                result['primary_disconnect_reason'] = ot.primary_disconnect_reason
        
        result['omc_extraction_success'] = state['omc_extraction_success']
        result['omc_error_message'] = state.get('omc_error_message', '')
        result['extraction_complete'] = state.get('extraction_complete', False)
        
        return result
    
    def _process_single_row(self, row_index: int, row_data: Dict[str, Any], seasonality_data: str) -> Optional[Dict[str, Any]]:
        """
        Process a single row (helper function for parallel processing).
        
        Args:
            row_index: Row index
            row_data: Row data dictionary
            seasonality_data: Seasonality reference data
        
        Returns:
            Result dictionary or None if failed
        """
        try:
            lead_id = str(row_data.get('lead_id', ''))
            
            logger.info(f"Processing Row {row_index + 1} (ID: {lead_id})")
            
            # Run extraction workflow
            final_state = run_extraction(
                lead_id=lead_id,
                row_number=row_index + 1,
                lgs_user=row_data.get('lgs_user', ''),
                lgs_event_time=row_data.get('lgs_event_time', ''),
                lgs_duration=row_data.get('lgs_duration', 0),
                lgs_transcription=row_data.get('lgs_transcription', ''),
                omc_user=row_data.get('omc_user', ''),
                omc_call_date=row_data.get('omc_call_date', ''),
                omc_duration=row_data.get('omc_duration', 0),
                omc_transcription=row_data.get('omc_transcription', ''),
                customer_address=row_data.get('customer_address', ''),
                service=row_data.get('service', ''),
                customer_name=row_data.get('customer_name', ''),
                seasonality_data=seasonality_data,
                max_attempts=MAX_RETRIES
            )
            
            # Convert state to result
            result = self._convert_state_to_result(final_state)
            
            logger.info(f"Successfully processed Row {row_index + 1} (ID: {lead_id})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process Row {row_index + 1}: {str(e)}")
            return None
    
    def process_all(self, resume: bool = True):
        """
        Process all rows in the input CSV with PARALLEL batch processing.
        
        Args:
            resume: Whether to resume from checkpoint
        """
        logger.info("="*80)
        logger.info("STARTING PARALLEL BATCH PROCESSING")
        logger.info("="*80)
        
        # Load data
        self.data_handler.load_input_data()
        self.data_handler.load_seasonality_data()
        
        total_rows = self.data_handler.get_total_rows()
        logger.info(f"Total rows to process: {total_rows}")
        
        # Get seasonality data as string for prompts
        seasonality_data = self.data_handler.get_seasonality_data_as_string()
        
        # Get processed rows from checkpoint
        processed_rows = self.checkpoint_data.get('processed_rows', []) if resume else []
        
        # Prepare rows to process
        rows_to_process = []
        for row_index in range(total_rows):
            row_data = self.data_handler.get_row_data(row_index)
            lead_id = str(row_data.get('lead_id', ''))
            
            # Skip if already processed
            if resume and self._is_row_processed(lead_id):
                logger.info(f"Skipping Row {row_index + 1} (already processed)")
                continue
            
            rows_to_process.append((row_index, row_data, lead_id))
        
        if not rows_to_process:
            logger.info("No new rows to process!")
            return
        
        logger.info(f"Processing {len(rows_to_process)} rows in parallel batches of {BATCH_SIZE}")
        
        # Process in batches with parallel execution
        for batch_start in range(0, len(rows_to_process), BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, len(rows_to_process))
            batch = rows_to_process[batch_start:batch_end]
            
            batch_num = (batch_start // BATCH_SIZE) + 1
            total_batches = (len(rows_to_process) + BATCH_SIZE - 1) // BATCH_SIZE
            
            logger.info(f"\n{'='*80}")
            logger.info(f"PROCESSING BATCH {batch_num}/{total_batches} ({len(batch)} rows)")
            logger.info(f"{'='*80}")
            
            # Use ThreadPoolExecutor for parallel processing within batch
            max_workers = min(len(batch), BATCH_SIZE)
            logger.info(f"Using {max_workers} parallel workers for this batch")
            
            batch_results = []
            batch_lead_ids = []
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all rows in batch for parallel processing
                future_to_row = {
                    executor.submit(self._process_single_row, row_index, row_data, seasonality_data): (row_index, lead_id)
                    for row_index, row_data, lead_id in batch
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_row):
                    row_index, lead_id = future_to_row[future]
                    try:
                        result = future.result()
                        if result:
                            batch_results.append(result)
                            batch_lead_ids.append(lead_id)
                    except Exception as e:
                        logger.error(f"Exception in parallel processing for Row {row_index + 1}: {str(e)}")
            
            # Add batch results to overall results
            self.results.extend(batch_results)
            processed_rows.extend(batch_lead_ids)
            
            # Save checkpoint after each batch
            logger.info(f"Batch {batch_num} complete. Saving checkpoint...")
            self._save_checkpoint(processed_rows)
            self.data_handler.save_results(self.results)
            
            logger.info(f"Progress: {len(processed_rows)}/{len(rows_to_process)} rows processed")
        
        # Final save
        logger.info("\n" + "="*80)
        logger.info("PARALLEL BATCH PROCESSING COMPLETE")
        logger.info("="*80)
        
        self._save_checkpoint(processed_rows)
        self.data_handler.save_results(self.results)
        
        # Print statistics
        extraction_logger.print_stats()
        
        logger.info(f"\nResults saved to: {self.data_handler.output_df}")

