"""
Season Lookup Service
Determines High/Low/Normal season based on industry and month from CSV lookup table
"""
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional
from config.settings import SEASON_LOOKUP_CSV
from utils.logger import get_logger

logger = get_logger()


class SeasonLookupService:
    """
    Service to lookup season classification based on industry and month
    Uses the Sales Data points - High_Low season for that industy _ Location.csv
    """
    
    def __init__(self):
        """Initialize the season lookup service"""
        self.lookup_df = None
        self.load_lookup_table()
    
    def load_lookup_table(self):
        """Load the season lookup CSV"""
        try:
            logger.info(f"Loading season lookup table from {SEASON_LOOKUP_CSV}")
            self.lookup_df = pd.read_csv(SEASON_LOOKUP_CSV)
            logger.info(f"Loaded {len(self.lookup_df)} industry categories")
            
            # Log available columns
            logger.debug(f"Lookup table columns: {list(self.lookup_df.columns)}")
            
        except Exception as e:
            logger.error(f"Failed to load season lookup table: {str(e)}")
            self.lookup_df = None
    
    def extract_month_from_date(self, call_date: str) -> Optional[str]:
        """
        Extract month name from call_date string.
        Expected format: DD/MM/YY (e.g., "20/11/25")
        
        Args:
            call_date: Date string in DD/MM/YY format
        
        Returns:
            Month name (e.g., "Jan", "Feb") or None if parsing fails
        """
        try:
            # Parse DD/MM/YY format
            parts = call_date.split('/')
            if len(parts) >= 2:
                month_num = int(parts[1])  # Get MM part
                
                # Map to month names used in CSV
                month_names = {
                    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
                    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
                    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
                }
                
                return month_names.get(month_num)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract month from date '{call_date}': {str(e)}")
            return None
    
    def find_matching_industry(self, service: str) -> Optional[str]:
        """
        Find matching industry category from service description.
        Uses fuzzy matching to find the best match.
        
        Args:
            service: Service description from input data
        
        Returns:
            Matched category name or None
        """
        if not service or pd.isna(service) or not self.lookup_df is not None:
            return None
        
        service_lower = str(service).lower()
        
        # Try exact match first
        for idx, row in self.lookup_df.iterrows():
            category = str(row['Category'])
            industries = str(row['Industries / Services']).lower()
            
            # Check if service matches any industry in the list
            if service_lower in industries or any(
                keyword.strip() in service_lower 
                for keyword in industries.split(',')
            ):
                return category
        
        # Try partial matching
        for idx, row in self.lookup_df.iterrows():
            category = str(row['Category'])
            industries = str(row['Industries / Services']).lower()
            
            # Check for partial matches
            industry_keywords = [kw.strip() for kw in industries.split(',')]
            for keyword in industry_keywords:
                if len(keyword) > 3 and keyword in service_lower:
                    return category
        
        return None
    
    def get_season(
        self,
        service: str,
        call_date: str
    ) -> Tuple[str, str, str, str]:
        """
        Get season classification for a given service and call date.
        
        Args:
            service: Service/industry description
            call_date: Call date in DD/MM/YY format
        
        Returns:
            Tuple of (season, industry_category, month, confidence)
            - season: "High season", "Low season", or "Normal Season"
            - industry_category: Matched category name
            - month: Month name
            - confidence: "exact_match", "partial_match", or "no_match"
        """
        
        # Extract month
        month = self.extract_month_from_date(call_date)
        if not month:
            return ("Normal Season", "", "", "no_match")
        
        # Find matching industry
        industry_category = self.find_matching_industry(service)
        if not industry_category:
            return ("Normal Season", "", month, "no_match")
        
        # Lookup season for this industry and month
        try:
            # Find the row for this industry
            row = self.lookup_df[self.lookup_df['Category'] == industry_category]
            
            if row.empty:
                return ("Normal Season", industry_category, month, "no_match")
            
            # Get the season value for this month
            season_value = row[month].values[0]
            
            # Handle NaN or empty values
            if pd.isna(season_value) or season_value == '':
                season = "Normal Season"
                confidence = "exact_match"  # We found the industry, just no specific season
            elif "High season" in str(season_value):
                season = "High season"
                confidence = "exact_match"
            elif "Low season" in str(season_value):
                season = "Low season"
                confidence = "exact_match"
            else:
                season = "Normal Season"
                confidence = "exact_match"
            
            return (season, industry_category, month, confidence)
            
        except Exception as e:
            logger.error(f"Error looking up season: {str(e)}")
            return ("Normal Season", industry_category, month, "no_match")
    
    def get_season_info(self, service: str, call_date: str) -> dict:
        """
        Get detailed season information as a dictionary.
        
        Args:
            service: Service/industry description
            call_date: Call date string
        
        Returns:
            Dictionary with season information
        """
        season, industry, month, confidence = self.get_season(service, call_date)
        
        return {
            "season": season,
            "industry_category": industry,
            "month": month,
            "confidence": confidence
        }

