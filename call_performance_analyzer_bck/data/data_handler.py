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
    BATCH_SIZE,
    AGENT_PERFORMANCE_FILE
)


class DataHandler:
    """Handles all data I/O operations"""
    
    def __init__(self):
        self.input_file = INPUT_FILE
        self.checkpoint_file = CHECKPOINT_FILE
        self.output_file = OUTPUT_FILE
        self.agent_performance_file = AGENT_PERFORMANCE_FILE
        
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
    
    def load_agent_performance_data(self) -> Optional[pd.DataFrame]:
        """
        Load agent performance overview data (DPAD, Conversion Rate, Payability, etc.)
        
        Returns:
            DataFrame with agent performance data or None if file doesn't exist
        """
        try:
            if not self.agent_performance_file.exists():
                logger.warning(f"Agent performance file not found: {self.agent_performance_file}")
                return None
            
            logger.info(f"Loading agent performance data from {self.agent_performance_file}")
            
            df = pd.read_csv(self.agent_performance_file)
            
            # Expected columns
            expected_cols = [
                'Agent_Name', '# Attandance', '# Deals', '# Calls', 'DPAD',
                'Conversion Rate', '30 Days Payability', '60 Days Payability',
                '90 Days Payability', '0 - 90 Days Payability'
            ]
            
            missing_cols = [col for col in expected_cols if col not in df.columns]
            if missing_cols:
                logger.warning(f"Missing agent performance columns: {missing_cols}")
            
            logger.info(f"Loaded {len(df)} agents from agent performance file")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load agent performance data: {str(e)}")
            return None
    
    def get_agent_performance_summary(self) -> Dict:
        """
        Get agent performance data as a summary dictionary for report generation
        
        Returns:
            Dictionary with agent performance metrics
        """
        df = self.load_agent_performance_data()
        
        if df is None:
            return {}
        
        summary = {
            'total_agents': len(df),
            'agents': []
        }
        
        for _, row in df.iterrows():
            agent_data = {
                'name': row.get('Agent_Name', 'Unknown'),
                'attendance': row.get('# Attandance', 0),
                'deals': row.get('# Deals', 0),
                'calls': row.get('# Calls', 0),
                'dpad': row.get('DPAD', 0),
                'conversion_rate': row.get('Conversion Rate', '-'),
                'payability_30_days': row.get('30 Days Payability', '-'),
                'payability_60_days': row.get('60 Days Payability', '-'),
                'payability_90_days': row.get('90 Days Payability', '-'),
                'payability_0_90_days': row.get('0 - 90 Days Payability', '-')
            }
            summary['agents'].append(agent_data)
        
        # Sort by DPAD (highest first)
        summary['agents'].sort(key=lambda x: float(x['dpad']) if x['dpad'] else 0, reverse=True)
        
        return summary
    
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
    
    def save_report(self, report_content: str) -> str:
        """
        Save final report to file
        
        Args:
            report_content: Markdown report content
            
        Returns:
            Path to saved report file
        """
        try:
            logger.info(f"Saving report to {self.output_file}")
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Report saved successfully: {self.output_file}")
            return str(self.output_file)
            
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

