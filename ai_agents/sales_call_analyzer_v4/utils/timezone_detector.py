"""
Timezone Detector Utility
Detects timezone from city/state/postal_code (priority) or transcription analysis (fallback)
"""
from typing import Tuple, Optional
import pandas as pd
from config.settings import US_STATE_TIMEZONES
from utils.logger import get_logger

logger = get_logger()


class TimezoneDetector:
    """
    Detects timezone using location data (city/state/postal) first,
    then falls back to transcription analysis if needed
    """
    
    def __init__(self):
        """Initialize timezone detector"""
        self.state_timezones = US_STATE_TIMEZONES
    
    def detect_from_location(
        self,
        city: str,
        state: str,
        postal_code: str
    ) -> Tuple[Optional[str], str, str]:
        """
        Detect timezone from location data (city, state, postal_code).
        
        Args:
            city: City name
            state: State code (2-letter)
            postal_code: Postal/ZIP code
        
        Returns:
            Tuple of (timezone, detection_method, confidence)
            - timezone: Detected timezone or None
            - detection_method: How it was detected
            - confidence: 'high', 'medium', 'low'
        """
        
        # Try state-based detection first (most reliable)
        if state and not pd.isna(state) and str(state).strip():
            state_code = str(state).strip().upper()
            
            if state_code in self.state_timezones:
                timezone = self.state_timezones[state_code]
                return (timezone, "location_data", "high")
        
        # If state detection failed but we have city, try city-based detection
        if city and not pd.isna(city) and str(city).strip():
            city_name = str(city).strip().lower()
            
            # Known major cities (fallback)
            city_timezones = {
                "new york": "Eastern", "nyc": "Eastern", "manhattan": "Eastern",
                "boston": "Eastern", "philadelphia": "Eastern", "miami": "Eastern",
                "atlanta": "Eastern", "washington": "Eastern", "baltimore": "Eastern",
                
                "chicago": "Central", "dallas": "Central", "houston": "Central",
                "austin": "Central", "san antonio": "Central", "minneapolis": "Central",
                "new orleans": "Central", "kansas city": "Central",
                
                "denver": "Mountain", "phoenix": "Mountain", "salt lake city": "Mountain",
                "albuquerque": "Mountain", "boise": "Mountain",
                
                "los angeles": "Pacific", "san francisco": "Pacific", "seattle": "Pacific",
                "portland": "Pacific", "san diego": "Pacific", "las vegas": "Pacific",
                
                "anchorage": "Alaska", "fairbanks": "Alaska",
                
                "honolulu": "Hawaii-Aleutian"
            }
            
            for city_key, tz in city_timezones.items():
                if city_key in city_name:
                    return (tz, "location_data", "medium")
        
        # No location-based detection successful
        return (None, "failed", "low")
    
    def detect_from_transcription(self, transcription: str) -> Tuple[Optional[str], str]:
        """
        Detect timezone from transcription text (fallback method).
        Looks for location mentions in the transcript.
        
        Args:
            transcription: Call transcription text
        
        Returns:
            Tuple of (timezone, confidence)
        """
        
        if not transcription or pd.isna(transcription):
            return (None, "low")
        
        transcription_lower = str(transcription).lower()
        
        # Look for state mentions
        for state_code, timezone in self.state_timezones.items():
            # Look for state names (approximate)
            state_names = {
                "CT": "connecticut", "FL": "florida", "GA": "georgia",
                "NY": "new york", "CA": "california", "TX": "texas",
                "IL": "illinois", "PA": "pennsylvania", "OH": "ohio",
                "MI": "michigan", "NC": "north carolina", "VA": "virginia",
                "WA": "washington", "MA": "massachusetts", "AZ": "arizona",
                "TN": "tennessee", "IN": "indiana", "MO": "missouri",
                "MD": "maryland", "WI": "wisconsin", "CO": "colorado",
                "MN": "minnesota", "SC": "south carolina", "AL": "alabama",
                "LA": "louisiana", "KY": "kentucky", "OR": "oregon",
                "OK": "oklahoma", "NV": "nevada", "NM": "new mexico",
                "NE": "nebraska", "WV": "west virginia", "ID": "idaho",
                "HI": "hawaii", "ME": "maine", "NH": "new hampshire",
                "RI": "rhode island", "MT": "montana", "DE": "delaware",
                "SD": "south dakota", "ND": "north dakota", "AK": "alaska",
                "VT": "vermont", "WY": "wyoming", "UT": "utah",
                "IA": "iowa", "AR": "arkansas", "MS": "mississippi",
                "KS": "kansas"
            }
            
            state_name = state_names.get(state_code, "").lower()
            if state_name and state_name in transcription_lower:
                return (timezone, "medium")
        
        # Look for city mentions
        city_timezones = {
            "new york": "Eastern", "boston": "Eastern", "miami": "Eastern",
            "chicago": "Central", "dallas": "Central", "houston": "Central",
            "denver": "Mountain", "phoenix": "Mountain",
            "los angeles": "Pacific", "san francisco": "Pacific", "seattle": "Pacific"
        }
        
        for city, timezone in city_timezones.items():
            if city in transcription_lower:
                return (timezone, "low")
        
        return (None, "low")
    
    def detect_timezone(
        self,
        city: str,
        state: str,
        postal_code: str,
        transcription: str
    ) -> dict:
        """
        Detect timezone using location data first, then transcription as fallback.
        
        Args:
            city: City name
            state: State code
            postal_code: Postal code
            transcription: Call transcription
        
        Returns:
            Dictionary with timezone detection results
        """
        
        # Try location-based detection first
        timezone, method, confidence = self.detect_from_location(city, state, postal_code)
        
        if timezone:
            return {
                "timezone": timezone,
                "detection_method": method,
                "confidence": confidence,
                "source_data": f"{city}, {state} {postal_code}".strip()
            }
        
        # Fallback to transcription analysis
        logger.debug("Location-based timezone detection failed, trying transcription analysis")
        timezone, confidence = self.detect_from_transcription(transcription)
        
        if timezone:
            return {
                "timezone": timezone,
                "detection_method": "transcription_analysis",
                "confidence": confidence,
                "source_data": "Extracted from transcription"
            }
        
        # No detection successful
        return {
            "timezone": "UNKNOWN",
            "detection_method": "failed",
            "confidence": "low",
            "source_data": "No location data or transcription clues found"
        }

