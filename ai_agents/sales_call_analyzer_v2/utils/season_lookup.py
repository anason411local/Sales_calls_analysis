"""
Season lookup utility for determining high/low season based on industry and date
"""
import pandas as pd
from pathlib import Path
from typing import Tuple
from datetime import datetime
from utils.logger import logger


class SeasonLookup:
    """Lookup high/low season from CSV data"""
    
    def __init__(self, csv_path: str = None):
        """
        Initialize season lookup
        
        Args:
            csv_path: Path to season data CSV (optional, uses default if not provided)
        """
        if csv_path is None:
            # Default path
            project_root = Path(__file__).parent.parent.parent.parent
            csv_path = project_root / "input_data" / "Sales Data points - High_Low season for that industy _ Location.csv"
        
        self.csv_path = Path(csv_path)
        self.season_data = None
        self._load_season_data()
    
    def _load_season_data(self):
        """Load season data from CSV"""
        try:
            self.season_data = pd.read_csv(self.csv_path)
            logger.info(f"Loaded season data: {len(self.season_data)} categories")
        except Exception as e:
            logger.error(f"Failed to load season data: {str(e)}")
            self.season_data = None
    
    def get_season(self, industry_category: str, call_date: str) -> Tuple[str, str, str]:
        """
        Get season for industry and date
        
        Args:
            industry_category: Industry category name
            call_date: Call date (various formats supported)
            
        Returns:
            Tuple of (season, month, rationale)
        """
        if self.season_data is None:
            return ("UNKNOWN", "", "Season data not loaded")
        
        try:
            # Parse month from date
            month = self._extract_month(call_date)
            if not month:
                return ("UNKNOWN", "", "Could not parse month from date")
            
            # Find matching industry
            matching_row = self._find_industry(industry_category)
            if matching_row is None:
                return ("UNKNOWN", month, f"Industry '{industry_category}' not found in season data")
            
            # Get season for month
            season_value = matching_row[month].iloc[0] if month in matching_row.columns else None
            
            if pd.isna(season_value) or season_value == "":
                return ("UNKNOWN", month, f"No season data for {industry_category} in {month}")
            
            season = str(season_value).strip()
            rationale = f"{industry_category} in {month}: {season}"
            
            return (season, month, rationale)
            
        except Exception as e:
            logger.error(f"Error in season lookup: {str(e)}")
            return ("UNKNOWN", "", f"Error: {str(e)}")
    
    def _extract_month(self, date_str: str) -> str:
        """
        Extract month abbreviation from date string
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Month abbreviation (Jan, Feb, Mar, etc.) or empty string
        """
        if not date_str or pd.isna(date_str):
            return ""
        
        try:
            # Try parsing various date formats
            date_str = str(date_str).strip()
            
            # Common formats: DD/MM/YY, YYYY-MM-DD, MM/DD/YYYY, etc.
            for fmt in ["%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%m-%Y"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    month_num = dt.month
                    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                    return month_names[month_num - 1]
                except ValueError:
                    continue
            
            # If all parsing fails, return empty
            logger.warning(f"Could not parse date: {date_str}")
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting month: {str(e)}")
            return ""
    
    def _find_industry(self, industry_category: str) -> pd.DataFrame:
        """
        Find matching industry row in season data
        
        Args:
            industry_category: Industry category to find
            
        Returns:
            DataFrame row or None if not found
        """
        if self.season_data is None:
            return None
        
        industry_lower = industry_category.lower().strip()
        
        # Try exact match on Category column
        exact_match = self.season_data[
            self.season_data['Category'].str.lower().str.strip() == industry_lower
        ]
        if not exact_match.empty:
            return exact_match
        
        # Try partial match on Category
        partial_match = self.season_data[
            self.season_data['Category'].str.lower().str.contains(industry_lower, na=False)
        ]
        if not partial_match.empty:
            return partial_match.head(1)
        
        # Try match on Industries/Services column
        services_match = self.season_data[
            self.season_data['Industries / Services'].str.lower().str.contains(industry_lower, na=False)
        ]
        if not services_match.empty:
            return services_match.head(1)
        
        # No match found
        return None
    
    def get_all_categories(self) -> list:
        """Get list of all available industry categories"""
        if self.season_data is None:
            return []
        return self.season_data['Category'].tolist()


# Singleton instance
_season_lookup_instance = None

def get_season_lookup() -> SeasonLookup:
    """Get singleton instance of SeasonLookup"""
    global _season_lookup_instance
    if _season_lookup_instance is None:
        _season_lookup_instance = SeasonLookup()
    return _season_lookup_instance





