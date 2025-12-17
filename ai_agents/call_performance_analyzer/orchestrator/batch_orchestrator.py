"""
Batch orchestrator for managing the entire analysis workflow
"""
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from data.data_handler import DataHandler
from graph.analysis_graph import create_analysis_graph
from graph.state import AnalysisState
from reports.report_generator import generate_comprehensive_report
from utils.logger import logger
from config.settings import BATCH_SIZE
import pandas as pd


class BatchOrchestrator:
    """
    Orchestrates the entire call performance analysis workflow
    """
    
    def __init__(self):
        self.data_handler = DataHandler()
        self.graph = create_analysis_graph()
        
    def run_analysis(self, resume: bool = True) -> str:
        """
        Run complete analysis workflow
        
        Args:
            resume: Whether to resume from checkpoint
            
        Returns:
            Path to generated report
        """
        logger.info("=" * 80)
        logger.info("STARTING CALL PERFORMANCE ANALYSIS")
        logger.info("=" * 80)
        
        try:
            # Load input data
            df = self.data_handler.load_input_data()
            total_rows = len(df)
            
            # Check for checkpoint
            start_row = 0
            if resume:
                checkpoint = self.data_handler.get_checkpoint()
                if checkpoint:
                    start_row = checkpoint['processed_rows']
                    logger.info(f"Resuming from row {start_row}")
            
            # Get batches
            batches = self.data_handler.get_batches(df, start_row)
            
            # Initialize state
            state: AnalysisState = {
                'current_batch': [],
                'batch_number': 0,
                'total_rows': total_rows,
                'all_insights': [],
                'agent_metrics': {},
                'daily_metrics': {},
                'status_metrics': {},
                'short_call_patterns': [],
                'long_call_patterns': [],
                'lgs_issues': [],
                'omc_issues': [],
                'example_short_calls': [],
                'example_successful_calls': [],
                'processed_count': start_row,
                'failed_count': 0,
                'retry_queue': [],
                'ready_for_report': False,
                'final_report': None,
                'errors': []
            }
            
            # Process batches
            for batch_idx, batch_df in enumerate(batches, start=1):
                logger.info("=" * 80)
                logger.info(f"PROCESSING BATCH {batch_idx}/{len(batches)}")
                logger.info("=" * 80)
                
                # Convert batch to dict list
                batch_data = self.data_handler.dataframe_to_dict_list(batch_df)
                
                # Update state with current batch
                state['current_batch'] = batch_data
                state['batch_number'] = batch_idx
                
                # Run graph for this batch
                try:
                    state = self.graph.invoke(state)
                    
                    # Save checkpoint after each batch
                    self.data_handler.save_checkpoint(
                        processed_rows=state['processed_count'],
                        batch_number=batch_idx
                    )
                    
                    logger.info(f"Batch {batch_idx} complete. Progress: {state['processed_count']}/{total_rows}")
                    
                except Exception as e:
                    logger.error(f"Error processing batch {batch_idx}: {str(e)}")
                    state['failed_count'] += len(batch_data)
                    continue
            
            # Mark as ready for report
            state['ready_for_report'] = True
            
            # Generate final report
            logger.info("=" * 80)
            logger.info("GENERATING COMPREHENSIVE REPORT")
            logger.info("=" * 80)
            
            report = generate_comprehensive_report(state)
            
            # Save report (Markdown)
            markdown_path = self.data_handler.save_report(report)
            
            # Convert to DOCX
            logger.info("Converting report to DOCX format...")
            try:
                from utils.docx_converter import convert_report_to_docx
                docx_path = convert_report_to_docx(markdown_path)
                logger.info(f"DOCX report saved to: {docx_path}")
            except Exception as e:
                logger.warning(f"Failed to generate DOCX: {str(e)}")
                logger.warning("Markdown report is still available")
                docx_path = None
            
            # Clear checkpoint
            self.data_handler.clear_checkpoint()
            
            logger.info("=" * 80)
            logger.info("ANALYSIS COMPLETE")
            logger.info(f"Total calls analyzed: {len(state['all_insights'])}")
            logger.info(f"Markdown report: {markdown_path}")
            if docx_path:
                logger.info(f"DOCX report: {docx_path}")
            logger.info("=" * 80)
            
            return str(markdown_path)
            
        except Exception as e:
            logger.error(f"Fatal error in analysis workflow: {str(e)}")
            raise
    
    def run_parallel_batch_analysis(self, batch_data: List[Dict], state: AnalysisState) -> AnalysisState:
        """
        Run parallel analysis within a batch (if needed in future)
        
        Args:
            batch_data: List of row dictionaries
            state: Current state
            
        Returns:
            Updated state
        """
        # For now, we process sequentially within each batch
        # Can be enhanced with parallel processing if needed
        return state

