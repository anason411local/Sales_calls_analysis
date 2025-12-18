"""
Data Handler for Sales Variables Extractor
Handles CSV reading, writing, and data transformations
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
from config.settings import (
    INPUT_CSV, 
    OUTPUT_CSV, 
    INPUT_COLUMNS,
    SEASONALITY_CSV
)
from utils.logger import get_logger

logger = get_logger()


class DataHandler:
    """Handles all data operations for the extractor"""
    
    def __init__(self):
        """Initialize data handler"""
        self.input_df = None
        self.output_df = None
        self.seasonality_df = None
        self.seasonality_lookup = {}
    
    def load_input_data(self) -> pd.DataFrame:
        """
        Load the input CSV file.
        
        Returns:
            DataFrame with input data
        
        Raises:
            FileNotFoundError: If input file doesn't exist
        """
        if not INPUT_CSV.exists():
            raise FileNotFoundError(f"Input file not found: {INPUT_CSV}")
        
        logger.info(f"Loading input data from: {INPUT_CSV}")
        
        self.input_df = pd.read_csv(INPUT_CSV, encoding='utf-8')
        
        logger.info(f"Loaded {len(self.input_df)} rows from input file")
        
        # Validate required columns exist
        self._validate_columns()
        
        return self.input_df
    
    def load_seasonality_data(self) -> pd.DataFrame:
        """
        Load seasonality reference data.
        
        Returns:
            DataFrame with seasonality data
        """
        if not SEASONALITY_CSV.exists():
            logger.warning(f"Seasonality file not found: {SEASONALITY_CSV}")
            return pd.DataFrame()
        
        logger.info(f"Loading seasonality data from: {SEASONALITY_CSV}")
        
        self.seasonality_df = pd.read_csv(SEASONALITY_CSV, encoding='utf-8')
        
        # Create lookup dictionary for faster access
        self._build_seasonality_lookup()
        
        logger.info(f"Loaded seasonality data for {len(self.seasonality_df)} service categories")
        
        return self.seasonality_df
    
    def _build_seasonality_lookup(self):
        """Build a lookup dictionary for seasonality data"""
        if self.seasonality_df is None or self.seasonality_df.empty:
            return
        
        # Create a dictionary mapping service categories to monthly seasonality
        for _, row in self.seasonality_df.iterrows():
            category = row.get('Category', '')
            if category:
                self.seasonality_lookup[category.lower()] = {
                    'Jan': row.get('Jan', ''),
                    'Feb': row.get('Feb', ''),
                    'Mar': row.get('Mar', ''),
                    'Apr': row.get('Apr', ''),
                    'May': row.get('May', ''),
                    'Jun': row.get('Jun', ''),
                    'Jul': row.get('Jul', ''),
                    'Aug': row.get('Aug', ''),
                    'Sep': row.get('Sep', ''),
                    'Oct': row.get('Oct', ''),
                    'Nov': row.get('Nov', ''),
                    'Dec': row.get('Dec', '')
                }
    
    def get_seasonality_for_service(self, service: str, month: str) -> str:
        """
        Get seasonality status for a service in a given month.
        
        Args:
            service: Service type
            month: Month abbreviation (Jan, Feb, etc.)
        
        Returns:
            "High season", "Low season", or "Unknown"
        """
        if not self.seasonality_lookup:
            return "Unknown"
        
        # Try to match service to category
        service_lower = service.lower()
        
        for category, months in self.seasonality_lookup.items():
            if any(keyword in service_lower for keyword in category.split()):
                season = months.get(month, '')
                return season if season else "Unknown"
        
        return "Unknown"
    
    def get_seasonality_data_as_string(self) -> str:
        """
        Get seasonality data formatted as a string for prompts.
        
        Returns:
            Formatted seasonality data string
        """
        if self.seasonality_df is None or self.seasonality_df.empty:
            return "No seasonality data available"
        
        return self.seasonality_df.to_string(index=False)
    
    def _validate_columns(self):
        """Validate that required columns exist in input DataFrame"""
        if self.input_df is None:
            return
        
        missing_columns = []
        
        for col_name, csv_col in INPUT_COLUMNS.items():
            if csv_col not in self.input_df.columns:
                missing_columns.append(csv_col)
        
        if missing_columns:
            logger.warning(f"Missing columns in input CSV: {missing_columns}")
    
    def get_row_data(self, row_index: int) -> Dict[str, Any]:
        """
        Get data for a specific row.
        
        Args:
            row_index: Row index (0-based)
        
        Returns:
            Dictionary with row data
        """
        if self.input_df is None:
            raise ValueError("Input data not loaded")
        
        if row_index >= len(self.input_df):
            raise IndexError(f"Row index {row_index} out of range")
        
        row = self.input_df.iloc[row_index]
        
        # Map columns to standardized names
        row_data = {}
        for col_name, csv_col in INPUT_COLUMNS.items():
            row_data[col_name] = row.get(csv_col, None)
        
        # Add row number
        row_data['row_number'] = row_index + 1
        
        return row_data
    
    def save_results(self, results: List[Dict[str, Any]]):
        """
        Save extraction results to CSV, merged with original input data.
        
        Args:
            results: List of extraction result dictionaries
        """
        logger.info(f"Saving results to: {OUTPUT_CSV}")
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        
        # Merge with input data to include all original columns
        if self.input_df is not None and not results_df.empty:
            logger.info("Merging extracted variables with original input data...")
            
            # Create a mapping of row_number to lead_id for proper merging
            # Add all original columns to results
            merged_rows = []
            for _, result_row in results_df.iterrows():
                row_num = result_row['row_number']
                
                # Get the original input row (row_number is 1-indexed)
                if row_num > 0 and row_num <= len(self.input_df):
                    original_row = self.input_df.iloc[row_num - 1].to_dict()
                    
                    # Merge: original columns + extracted variables
                    merged_row = {**original_row, **result_row.to_dict()}
                    merged_rows.append(merged_row)
                else:
                    # If row not found, just use extracted data
                    merged_rows.append(result_row.to_dict())
            
            output_df = pd.DataFrame(merged_rows)
            logger.info(f"Merged data: {len(output_df)} rows with {len(output_df.columns)} columns")
        else:
            output_df = results_df
            logger.warning("No input data to merge with, saving extracted variables only")
        
        # Save to CSV
        output_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
        
        logger.info(f"Saved {len(output_df)} rows to output file: {OUTPUT_CSV}")
        
        self.output_df = output_df
    
    def merge_with_input(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge extraction results with original input data.
        
        Args:
            results_df: DataFrame with extraction results
        
        Returns:
            Merged DataFrame
        """
        if self.input_df is None:
            raise ValueError("Input data not loaded")
        
        # Merge on lead_id
        merged_df = self.input_df.merge(
            results_df,
            left_on=INPUT_COLUMNS['lead_id'],
            right_on='lead_id',
            how='left'
        )
        
        return merged_df
    
    def get_total_rows(self) -> int:
        """Get total number of rows in input data"""
        if self.input_df is None:
            return 0
        return len(self.input_df)

