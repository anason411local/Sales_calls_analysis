"""
Data Handler for CSV I/O and Resume Capability
Handles reading input CSV, writing output CSV, and managing checkpoints
"""
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from schemas.extraction_schemas import SalesCallExtraction
from config.settings import (
    INPUT_CSV,
    OUTPUT_CSV,
    CHECKPOINT_FILE,
    INPUT_COLUMNS
)
from utils.logger import get_logger, get_sales_logger

logger = get_logger()
sales_logger = get_sales_logger()


class DataHandler:
    """Handles all data I/O operations for the sales call analyzer"""
    
    def __init__(self):
        """Initialize data handler"""
        self.input_file = INPUT_CSV
        self.output_file = OUTPUT_CSV
        self.checkpoint_file = CHECKPOINT_FILE
        
        logger.info(f"DataHandler initialized")
        logger.info(f"Input file: {self.input_file}")
        logger.info(f"Output file: {self.output_file}")
    
    def load_input_data(self) -> pd.DataFrame:
        """
        Load input CSV data.
        
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
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            logger.info(f"Loaded {len(df)} rows from input file")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load input data: {str(e)}")
            raise
    
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint data if it exists.
        
        Returns:
            Checkpoint data dict or None if no checkpoint exists
        """
        try:
            if self.checkpoint_file.exists():
                logger.info(f"Loading checkpoint from {self.checkpoint_file}")
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                
                last_row = checkpoint.get('last_processed_row', -1)
                logger.info(f"Checkpoint found: last processed row = {last_row}")
                sales_logger.log_resume(last_row)
                
                return checkpoint
            else:
                logger.info("No checkpoint found, starting from beginning")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {str(e)}")
            return None
    
    def save_checkpoint(self, last_processed_row: int, total_processed: int):
        """
        Save checkpoint data.
        
        Args:
            last_processed_row: Index of last successfully processed row
            total_processed: Total number of rows processed so far
        """
        try:
            checkpoint = {
                'last_processed_row': last_processed_row,
                'total_processed': total_processed
            }
            
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
            
            sales_logger.log_checkpoint_save(total_processed)
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {str(e)}")
    
    def flatten_extraction_result(self, extraction: SalesCallExtraction) -> Dict[str, Any]:
        """
        Flatten a SalesCallExtraction object into a flat dictionary for CSV output.
        Creates one row with all extracted data in separate columns (wide format).
        
        Args:
            extraction: SalesCallExtraction object
        
        Returns:
            Flattened dictionary with all fields as separate columns
        """
        flat_dict = {}
        
        # Metadata fields
        flat_dict['transcription_id_omc'] = extraction.transcription_id  # For merging
        flat_dict['row_id'] = extraction.row_id
        flat_dict['call_date'] = extraction.call_date
        flat_dict['fullname'] = extraction.fullname
        flat_dict['length_in_sec'] = extraction.length_in_sec
        flat_dict['extraction_success'] = extraction.extraction_success
        flat_dict['extraction_error'] = extraction.extraction_error or ""
        
        # Category 1: Customer Engagement & Interest
        ce = extraction.customer_engagement
        flat_dict['ce_positive_signal_count'] = ce.positive_signal_count
        flat_dict['ce_positive_signal_verbiage'] = ce.positive_signal_verbiage
        flat_dict['ce_positive_signal_timestamps'] = ce.positive_signal_timestamps
        flat_dict['ce_customer_questions_count'] = ce.customer_questions_count
        flat_dict['ce_customer_questions_verbiage'] = ce.customer_questions_verbiage
        flat_dict['ce_customer_questions_timestamps'] = ce.customer_questions_timestamps
        flat_dict['ce_buying_intent_count'] = ce.buying_intent_count
        flat_dict['ce_buying_intent_verbiage'] = ce.buying_intent_verbiage
        flat_dict['ce_buying_intent_timestamps'] = ce.buying_intent_timestamps
        flat_dict['ce_disengagement_count'] = ce.disengagement_count
        flat_dict['ce_disengagement_verbiage'] = ce.disengagement_verbiage
        flat_dict['ce_disengagement_timestamps'] = ce.disengagement_timestamps
        
        # Category 2: Call Opening & Framing
        co = extraction.call_opening
        flat_dict['co_opener_type'] = co.opener_type
        flat_dict['co_opener_verbiage'] = co.opener_verbiage
        flat_dict['co_permission_request_present'] = co.permission_request_present
        flat_dict['co_permission_request_verbiage'] = co.permission_request_verbiage
        flat_dict['co_value_prop_present'] = co.value_prop_present
        flat_dict['co_value_prop_verbiage'] = co.value_prop_verbiage
        flat_dict['co_value_prop_timestamp'] = co.value_prop_timestamp
        flat_dict['co_agenda_set'] = co.agenda_set
        flat_dict['co_agenda_verbiage'] = co.agenda_verbiage
        
        # Category 3: Objection Handling & Friction
        oh = extraction.objection_handling
        flat_dict['oh_objections_count'] = oh.objections_count
        flat_dict['oh_objection_types'] = oh.objection_types
        flat_dict['oh_objection_verbiage'] = oh.objection_verbiage
        flat_dict['oh_objection_timestamps'] = oh.objection_timestamps
        flat_dict['oh_objection_handling_present'] = oh.objection_handling_present
        flat_dict['oh_objection_handling_verbiage'] = oh.objection_handling_verbiage
        flat_dict['oh_objection_handling_quality'] = oh.objection_handling_quality
        flat_dict['oh_friction_points_count'] = oh.friction_points_count
        flat_dict['oh_friction_verbiage'] = oh.friction_verbiage
        flat_dict['oh_friction_timestamps'] = oh.friction_timestamps
        
        # Category 4: Pace, Control & Interruptions
        pc = extraction.pace_control
        flat_dict['pc_rep_interruptions_count'] = pc.rep_interruptions_count
        flat_dict['pc_rep_interruptions_verbiage'] = pc.rep_interruptions_verbiage
        flat_dict['pc_rep_interruptions_timestamps'] = pc.rep_interruptions_timestamps
        flat_dict['pc_customer_interruptions_count'] = pc.customer_interruptions_count
        flat_dict['pc_customer_interruptions_verbiage'] = pc.customer_interruptions_verbiage
        flat_dict['pc_customer_interruptions_timestamps'] = pc.customer_interruptions_timestamps
        flat_dict['pc_rep_talk_percentage'] = pc.rep_talk_percentage
        flat_dict['pc_customer_talk_percentage'] = pc.customer_talk_percentage
        flat_dict['pc_pace_assessment'] = pc.pace_assessment
        flat_dict['pc_pace_notes'] = pc.pace_notes
        
        # Category 5: Emotional Tone & Rapport
        et = extraction.emotional_tone
        flat_dict['et_customer_tone_overall'] = et.customer_tone_overall
        flat_dict['et_customer_tone_shifts'] = et.customer_tone_shifts
        flat_dict['et_customer_tone_verbiage'] = et.customer_tone_verbiage
        flat_dict['et_rep_tone_overall'] = et.rep_tone_overall
        flat_dict['et_rep_tone_notes'] = et.rep_tone_notes
        flat_dict['et_rapport_building_present'] = et.rapport_building_present
        flat_dict['et_rapport_building_verbiage'] = et.rapport_building_verbiage
        flat_dict['et_rapport_building_timestamps'] = et.rapport_building_timestamps
        flat_dict['et_empathy_present'] = et.empathy_present
        flat_dict['et_empathy_verbiage'] = et.empathy_verbiage
        flat_dict['et_active_listening_present'] = et.active_listening_present
        flat_dict['et_active_listening_verbiage'] = et.active_listening_verbiage
        
        # Category 6: Outcome & Timing Markers
        ot = extraction.outcome_timing
        flat_dict['ot_call_outcome'] = ot.call_outcome
        flat_dict['ot_outcome_verbiage'] = ot.outcome_verbiage
        flat_dict['ot_outcome_timestamp'] = ot.outcome_timestamp
        flat_dict['ot_next_steps_defined'] = ot.next_steps_defined
        flat_dict['ot_next_steps_verbiage'] = ot.next_steps_verbiage
        flat_dict['ot_commitment_level'] = ot.commitment_level
        flat_dict['ot_commitment_verbiage'] = ot.commitment_verbiage
        flat_dict['ot_call_duration_seconds'] = ot.call_duration_seconds
        flat_dict['ot_optimal_duration'] = ot.optimal_duration
        
        return flat_dict
    
    def save_results(self, results: List[SalesCallExtraction], append: bool = False, merge_with_source: bool = True):
        """
        Save extraction results to CSV, optionally merged with source data.
        
        Args:
            results: List of SalesCallExtraction objects
            append: Whether to append to existing file or overwrite
            merge_with_source: Whether to merge with source dataset
        """
        try:
            logger.info(f"Saving {len(results)} results to {self.output_file}")
            
            # Flatten all results
            flattened_results = [self.flatten_extraction_result(r) for r in results]
            
            # Create DataFrame with extracted data
            extracted_df = pd.DataFrame(flattened_results)
            
            # Merge with source data if requested
            if merge_with_source:
                try:
                    # Load source data
                    source_df = pd.read_csv(self.input_file)
                    
                    if append and self.output_file.exists():
                        # APPEND MODE: Update existing output file
                        # Read the existing output (which already has source + previous extractions)
                        existing_df = pd.read_csv(self.output_file)
                        
                        # For each new extraction, update the corresponding row in existing_df
                        for _, extracted_row in extracted_df.iterrows():
                            tid = extracted_row['transcription_id_omc']
                            
                            # Find matching row in existing_df
                            mask = existing_df['transcription_id_omc'] == tid
                            
                            if mask.any():
                                # Update existing row with extracted data
                                for col in extracted_row.index:
                                    if col in existing_df.columns:
                                        existing_df.loc[mask, col] = extracted_row[col]
                            else:
                                # Row doesn't exist yet - merge with source and append
                                source_row = source_df[source_df['transcription_id_omc'] == tid]
                                if not source_row.empty:
                                    # Merge source row with extracted data
                                    merged_row = source_row.copy()
                                    for col in extracted_row.index:
                                        merged_row[col] = extracted_row[col]
                                    existing_df = pd.concat([existing_df, merged_row], ignore_index=True)
                        
                        df_to_save = existing_df
                        logger.info(f"Updated {len(results)} rows in existing output file")
                        
                    else:
                        # FIRST WRITE: Merge extracted data with full source dataset
                        # This creates a complete dataset with all source rows
                        merged_df = source_df.merge(
                            extracted_df,
                            on='transcription_id_omc',
                            how='left',
                            suffixes=('_source', '_extracted')
                        )
                        df_to_save = merged_df
                        logger.info(f"Created initial output with {len(source_df)} rows, {len(results)} with extracted data")
                    
                except Exception as e:
                    logger.error(f"Error during merge: {str(e)}")
                    logger.warning(f"Saving extracted data only without merge")
                    df_to_save = extracted_df
            else:
                # No merge - just save extracted data
                if append and self.output_file.exists():
                    existing_df = pd.read_csv(self.output_file)
                    df_to_save = pd.concat([existing_df, extracted_df], ignore_index=True)
                else:
                    df_to_save = extracted_df
            
            # Write to CSV
            df_to_save.to_csv(self.output_file, index=False)
            logger.info(f"Saved {len(df_to_save)} total rows to {self.output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
            raise
    
    def create_failed_extraction(
        self,
        row_id: str,
        transcription_id: str,
        call_date: str,
        fullname: str,
        length_in_sec: int,
        error_message: str
    ) -> SalesCallExtraction:
        """
        Create a SalesCallExtraction object for a failed extraction with NaN/empty values.
        
        Args:
            row_id: Row identifier
            call_date: Call date
            fullname: Sales rep name
            length_in_sec: Call duration
            error_message: Error message
        
        Returns:
            SalesCallExtraction with empty/default values
        """
        from schemas.extraction_schemas import (
            CustomerEngagementInterest,
            CallOpeningFraming,
            ObjectionHandlingFriction,
            PaceControlInterruptions,
            EmotionalToneRapport,
            OutcomeTimingMarkers
        )
        
        return SalesCallExtraction(
            row_id=row_id,
            transcription_id=transcription_id,
            call_date=call_date,
            fullname=fullname,
            length_in_sec=length_in_sec,
            customer_engagement=CustomerEngagementInterest(),
            call_opening=CallOpeningFraming(),
            objection_handling=ObjectionHandlingFriction(),
            pace_control=PaceControlInterruptions(),
            emotional_tone=EmotionalToneRapport(),
            outcome_timing=OutcomeTimingMarkers(),
            extraction_success=False,
            extraction_error=error_message
        )

