"""
Validators Utility - Input validation for the Ethiopian GPS navigation system
Provides comprehensive validation for all inputs with Ethiopian-specific rules
"""

import re
from typing import Any, List, Tuple, Optional, Union, Dict
from datetime import datetime
import math


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Validators:
    """
    Utility class for validating all inputs to the Ethiopian GPS navigation system
    
    Features:
    - Ethiopian city name validation
    - Geographic coordinate validation
    - Road distance and speed validation
    - Ethiopian region validation
    - Path validation
    - Data type and range validation
    """
    
    # Ethiopian regions list
    ETHIOPIAN_REGIONS = [
        'Addis Ababa', 'Oromia', 'Amhara', 'Tigray', 'SNNPR',
        'Dire Dawa', 'Harari', 'Somali', 'Gambella', 'Benshangul', 'Afar'
    ]
    
    # Ethiopian road types
    ROAD_TYPES = ['highway', 'national', 'regional', 'local', 'gravel', 'rural']
    
    # Road conditions
    ROAD_CONDITIONS = ['excellent', 'good', 'fair', 'poor', 'under_construction', 'seasonal']
    
    @staticmethod
    def validate_city_name(name: str, allow_ethiopian_chars: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Validate Ethiopian city name
        
        Args:
            name: City name to validate
            allow_ethiopian_chars: Whether to allow Ethiopian characters (Amharic, etc.)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "City name cannot be empty"
        
        if len(name) < 2:
            return False, "City name must be at least 2 characters long"
        
        if len(name) > 100:
            return False, "City name cannot exceed 100 characters"
        
        if allow_ethiopian_chars:
            # Allow Unicode letters (including Ethiopian) and common punctuation
            if not re.match(r"^[\w\s\-'\.]+$", name, re.UNICODE):
                return False, "City name contains invalid characters"
        else:
            # ASCII only
            if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
                return False, "City name can only contain letters, spaces, hyphens, apostrophes, and periods"
        
        return True, None
    
    @staticmethod
    def validate_region(region: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Ethiopian region name
        
        Args:
            region: Region name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not region:
            return False, "Region cannot be empty"
        
        # Check against known Ethiopian regions (case-insensitive)
        region_lower = region.lower()
        for valid_region in Validators.ETHIOPIAN_REGIONS:
            if valid_region.lower() == region_lower:
                return True, None
        
        # Allow custom regions with validation
        if len(region) > 50:
            return False, "Region name too long (max 50 characters)"
        
        if not re.match(r"^[a-zA-Z\s\-]+$", region):
            return False, "Region name contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, Optional[str]]:
        """
        Validate geographic coordinates
        
        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(latitude, (int, float)):
            return False, f"Latitude must be a number, got {type(latitude).__name__}"
        
        if not isinstance(longitude, (int, float)):
            return False, f"Longitude must be a number, got {type(longitude).__name__}"
        
        if not -90 <= latitude <= 90:
            return False, f"Latitude must be between -90 and 90, got {latitude}"
        
        if not -180 <= longitude <= 180:
            return False, f"Longitude must be between -180 and 180, got {longitude}"
        
        return True, None
    
    @staticmethod
    def validate_within_ethiopia(latitude: float, longitude: float) -> Tuple[bool, Optional[str]]:
        """
        Validate that coordinates are within Ethiopia's approximate bounds
        
        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Ethiopia approximate bounds
        if not (3.0 <= latitude <= 15.0):
            return False, f"Latitude {latitude} is outside Ethiopia (approx 3°N to 15°N)"
        
        if not (33.0 <= longitude <= 48.0):
            return False, f"Longitude {longitude} is outside Ethiopia (approx 33°E to 48°E)"
        
        return True, None
    
    @staticmethod
    def validate_distance(distance: float) -> Tuple[bool, Optional[str]]:
        """
        Validate road distance
        
        Args:
            distance: Distance in kilometers
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(distance, (int, float)):
            return False, f"Distance must be a number, got {type(distance).__name__}"
        
        if distance <= 0:
            return False, f"Distance must be positive, got {distance}"
        
        if distance > 2000:  # Max possible road distance in Ethiopia
            return False, f"Distance too large for Ethiopia (max 2000 km), got {distance}"
        
        return True, None
    
    @staticmethod
    def validate_speed(speed: float) -> Tuple[bool, Optional[str]]:
        """
        Validate speed value
        
        Args:
            speed: Speed in km/h
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(speed, (int, float)):
            return False, f"Speed must be a number, got {type(speed).__name__}"
        
        if speed <= 0:
            return False, f"Speed must be positive, got {speed}"
        
        if speed > 200:  # Max realistic speed in Ethiopia
            return False, f"Speed too high for Ethiopia (max 200 km/h), got {speed}"
        
        return True, None
    
    @staticmethod
    def validate_population(population: int) -> Tuple[bool, Optional[str]]:
        """
        Validate city population
        
        Args:
            population: Population count
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(population, int):
            return False, f"Population must be an integer, got {type(population).__name__}"
        
        if population < 0:
            return False, f"Population cannot be negative, got {population}"
        
        if population > 10_000_000:  # Max Ethiopian city population
            return False, f"Population too large for Ethiopia (max 10 million), got {population:,}"
        
        return True, None
    
    @staticmethod
    def validate_elevation(elevation: float) -> Tuple[bool, Optional[str]]:
        """
        Validate elevation
        
        Args:
            elevation: Elevation in meters
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(elevation, (int, float)):
            return False, f"Elevation must be a number, got {type(elevation).__name__}"
        
        if elevation < -150:  # Below sea level (Danakil Depression)
            return False, f"Elevation too low for Ethiopia (min -150 m), got {elevation}"
        
        if elevation > 5000:  # Highest peaks (Ras Dashen ~4550m)
            return False, f"Elevation too high for Ethiopia (max 5000 m), got {elevation}"
        
        return True, None
    
    @staticmethod
    def validate_city_id(city_id: int, existing_ids: Optional[List[int]] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate city ID
        
        Args:
            city_id: City ID to validate
            existing_ids: List of existing city IDs (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(city_id, int):
            return False, f"City ID must be an integer, got {type(city_id).__name__}"
        
        if city_id <= 0:
            return False, f"City ID must be positive, got {city_id}"
        
        if existing_ids and city_id in existing_ids:
            return False, f"City ID {city_id} already exists"
        
        return True, None
    
    @staticmethod
    def validate_road_id(road_id: int, existing_ids: Optional[List[int]] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate road ID
        
        Args:
            road_id: Road ID to validate
            existing_ids: List of existing road IDs (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(road_id, int):
            return False, f"Road ID must be an integer, got {type(road_id).__name__}"
        
        if road_id <= 0:
            return False, f"Road ID must be positive, got {road_id}"
        
        if existing_ids and road_id in existing_ids:
            return False, f"Road ID {road_id} already exists"
        
        return True, None
    
    @staticmethod
    def validate_road_connection(city1_id: int, city2_id: int) -> Tuple[bool, Optional[str]]:
        """
        Validate road connection
        
        Args:
            city1_id: First city ID
            city2_id: Second city ID
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if city1_id == city2_id:
            return False, f"Cannot create road from city {city1_id} to itself"
        
        return True, None
    
    @staticmethod
    def validate_road_type(road_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate road type
        
        Args:
            road_type: Road type string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not road_type:
            return False, "Road type cannot be empty"
        
        road_type_lower = road_type.lower()
        if road_type_lower not in Validators.ROAD_TYPES:
            return False, f"Invalid road type. Must be one of: {', '.join(Validators.ROAD_TYPES)}"
        
        return True, None
    
    @staticmethod
    def validate_road_condition(condition: str) -> Tuple[bool, Optional[str]]:
        """
        Validate road condition
        
        Args:
            condition: Road condition string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not condition:
            return False, "Road condition cannot be empty"
        
        condition_lower = condition.lower()
        if condition_lower not in Validators.ROAD_CONDITIONS:
            return False, f"Invalid road condition. Must be one of: {', '.join(Validators.ROAD_CONDITIONS)}"
        
        return True, None
    
    @staticmethod
    def validate_lanes(lanes: int) -> Tuple[bool, Optional[str]]:
        """
        Validate number of lanes
        
        Args:
            lanes: Number of lanes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(lanes, int):
            return False, f"Lanes must be an integer, got {type(lanes).__name__}"
        
        if lanes < 1:
            return False, f"Number of lanes must be at least 1, got {lanes}"
        
        if lanes > 10:
            return False, f"Number of lanes too high (max 10), got {lanes}"
        
        return True, None
    
    @staticmethod
    def validate_toll(toll: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate toll value
        
        Args:
            toll: Toll value (can be bool, int, str)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Convert to bool if needed
        if isinstance(toll, str):
            toll_lower = toll.lower()
            if toll_lower in ['true', 'yes', '1']:
                return True, None
            elif toll_lower in ['false', 'no', '0']:
                return True, None
            else:
                return False, f"Invalid toll string. Use 'true' or 'false'"
        
        return True, None
    
    @staticmethod
    def validate_path(path: List[int], source_id: int, dest_id: int) -> Tuple[bool, Optional[str]]:
        """
        Validate reconstructed path
        
        Args:
            path: List of city IDs in path
            source_id: Source city ID
            dest_id: Destination city ID
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not path:
            return False, "Path is empty"
        
        if not isinstance(path, list):
            return False, f"Path must be a list, got {type(path).__name__}"
        
        if path[0] != source_id:
            return False, f"Path must start with source {source_id}, starts with {path[0]}"
        
        if path[-1] != dest_id:
            return False, f"Path must end with destination {dest_id}, ends with {path[-1]}"
        
        # Check for duplicates (cycles)
        if len(path) != len(set(path)):
            return False, "Path contains duplicate cities (cycles)"
        
        return True, None
    
    @staticmethod
    def validate_positive_number(value: float, name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate positive number
        
        Args:
            value: Number to validate
            name: Name of the value for error message
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, (int, float)):
            return False, f"{name} must be a number, got {type(value).__name__}"
        
        if value <= 0:
            return False, f"{name} must be positive, got {value}"
        
        return True, None
    
    @staticmethod
    def validate_non_negative_number(value: float, name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate non-negative number
        
        Args:
            value: Number to validate
            name: Name of the value for error message
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, (int, float)):
            return False, f"{name} must be a number, got {type(value).__name__}"
        
        if value < 0:
            return False, f"{name} cannot be negative, got {value}"
        
        return True, None
    
    @staticmethod
    def validate_range(value: float, min_val: float, max_val: float,
                      name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate value is within range
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            name: Name of the value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, (int, float)):
            return False, f"{name} must be a number, got {type(value).__name__}"
        
        if value < min_val or value > max_val:
            return False, f"{name} must be between {min_val} and {max_val}, got {value}"
        
        return True, None
    
    @staticmethod
    def validate_not_empty(value: Any, name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate value is not empty
        
        Args:
            value: Value to validate
            name: Name of the value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            return False, f"{name} cannot be None"
        
        if isinstance(value, str) and not value.strip():
            return False, f"{name} cannot be empty string"
        
        if isinstance(value, (list, dict, set)) and len(value) == 0:
            return False, f"{name} cannot be empty"
        
        return True, None
    
    @staticmethod
    def validate_ethiopian_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Ethiopian phone number
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone:
            return False, "Phone number cannot be empty"
        
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        # Ethiopian phone patterns
        patterns = [
            r'^09\d{8}$',           # Mobile: 09XXXXXXXX
            r'^011\d{7}$',          # Addis Ababa landline
            r'^0[1-9]\d{7}$',       # Other regions landline
            r'^2519\d{8}$',          # International format mobile
            r'^2511\d{7}$'           # International format landline
        ]
        
        for pattern in patterns:
            if re.match(pattern, cleaned):
                return True, None
        
        return False, "Invalid Ethiopian phone number format"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email address
        
        Args:
            email: Email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email cannot be empty"
        
        # Basic email regex
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, None


# Example usage
if __name__ == "__main__":
    print("="*80)
    print("TESTING VALIDATORS FOR ETHIOPIAN GPS SYSTEM")
    print("="*80)
    
    # Test city name validation
    print("\n1. Testing city name validation:")
    test_names = ["Addis Ababa", "Gonder123", "", "A very very long city name that exceeds the maximum allowed length of one hundred characters which is definitely too long for a city name"]
    
    for name in test_names:
        is_valid, error = Validators.validate_city_name(name)
        print(f"   '{name}': {'✅' if is_valid else '❌'} {error if error else ''}")
    
    # Test coordinate validation
    print("\n2. Testing coordinate validation:")
    test_coords = [(9.03, 38.74), (100, 38.74), (9.03, 200)]
    
    for lat, lon in test_coords:
        is_valid, error = Validators.validate_coordinates(lat, lon)
        print(f"   ({lat}, {lon}): {'✅' if is_valid else '❌'} {error if error else ''}")
    
    # Test Ethiopia bounds
    print("\n3. Testing Ethiopia bounds:")
    ethiopia_coords = [(9.03, 38.74), (20.0, 38.74), (9.03, 50.0)]
    
    for lat, lon in ethiopia_coords:
        is_valid, error = Validators.validate_within_ethiopia(lat, lon)
        print(f"   ({lat}, {lon}): {'✅' if is_valid else '❌'} {error if error else ''}")
    
    # Test road validation
    print("\n4. Testing road validation:")
    is_valid, error = Validators.validate_distance(850)
    print(f"   Distance 850 km: {'✅' if is_valid else '❌'}")
    
    is_valid, error = Validators.validate_road_type("highway")
    print(f"   Road type 'highway': {'✅' if is_valid else '❌'}")
    
    is_valid, error = Validators.validate_road_condition("good")
    print(f"   Condition 'good': {'✅' if is_valid else '❌'}")