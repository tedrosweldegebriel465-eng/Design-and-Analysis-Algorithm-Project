"""
City class representing an Ethiopian city in the GPS navigation system
"""

import math
from typing import Tuple, Optional, Dict, Any


class City:
    """
    Represents an Ethiopian city with geographic coordinates and properties
    
    Attributes:
        id (int): Unique identifier for the city
        name (str): City name
        region (str): Ethiopian region (e.g., 'Oromia', 'Amhara', 'Tigray')
        latitude (float): Latitude in degrees (-90 to 90)
        longitude (float): Longitude in degrees (-180 to 180)
        population (int): City population (optional)
        elevation (float): Elevation in meters (optional)
        is_capital (bool): Whether it's a regional capital
        timezone (str): Timezone (default: 'EAT' - East Africa Time)
    """
    
    # Common Ethiopian regions
    REGIONS = [
        'Addis Ababa', 'Oromia', 'Amhara', 'Tigray', 'SNNPR',
        'Dire Dawa', 'Harari', 'Somali', 'Gambella', 'Benshangul', 'Afar'
    ]
    
    def __init__(self,
                 id: int,
                 name: str,
                 region: str = "Unknown",
                 latitude: float = 0.0,
                 longitude: float = 0.0,
                 population: Optional[int] = None,
                 elevation: Optional[float] = None,
                 is_capital: bool = False,
                 timezone: str = "EAT"):
        """
        Initialize an Ethiopian city with required and optional attributes
        
        Args:
            id: Unique identifier
            name: City name
            region: Ethiopian region
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            population: City population
            elevation: Elevation above sea level
            is_capital: Whether it's a regional capital
            timezone: Timezone string
        """
        self.id = id
        self.name = name
        self.region = region
        self.latitude = latitude
        self.longitude = longitude
        self.population = population
        self.elevation = elevation
        self.is_capital = is_capital
        self.timezone = timezone
        
        # Validate coordinates
        self._validate_coordinates()
        
    def _validate_coordinates(self):
        """Validate that latitude and longitude are within valid ranges"""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude {self.latitude} must be between -90 and 90")
        
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude {self.longitude} must be between -180 and 180")
    
    def distance_to(self, other_city: 'City', method: str = 'haversine') -> float:
        """
        Calculate distance to another Ethiopian city
        
        Args:
            other_city: Another City object
            method: Distance calculation method ('haversine' or 'euclidean')
            
        Returns:
            Distance in kilometers
        """
        if method == 'haversine':
            return self._haversine_distance(other_city)
        elif method == 'euclidean':
            return self._euclidean_distance(other_city)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _haversine_distance(self, other_city: 'City') -> float:
        """
        Calculate great-circle distance using Haversine formula
        
        Args:
            other_city: Another City object
            
        Returns:
            Distance in kilometers
        """
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1 = math.radians(self.latitude)
        lon1 = math.radians(self.longitude)
        lat2 = math.radians(other_city.latitude)
        lon2 = math.radians(other_city.longitude)
        
        # Differences
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        # Haversine formula
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return round(distance, 2)
    
    def _euclidean_distance(self, other_city: 'City') -> float:
        """
        Calculate Euclidean distance (for small areas only!)
        
        Args:
            other_city: Another City object
            
        Returns:
            Approximate distance in kilometers
        """
        # Approximate conversion: 1 degree ≈ 111 km at equator
        DEGREE_TO_KM = 111.0
        
        dlat = (self.latitude - other_city.latitude) * DEGREE_TO_KM
        dlon = (self.longitude - other_city.longitude) * DEGREE_TO_KM * \
               math.cos(math.radians((self.latitude + other_city.latitude) / 2))
        
        distance = math.sqrt(dlat**2 + dlon**2)
        return round(distance, 2)
    
    def get_coordinates(self) -> Tuple[float, float]:
        """
        Get city coordinates as a tuple
        
        Returns:
            Tuple of (latitude, longitude)
        """
        return (self.latitude, self.longitude)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert city to dictionary for serialization
        
        Returns:
            Dictionary representation of the city
        """
        return {
            'id': self.id,
            'name': self.name,
            'region': self.region,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'population': self.population,
            'elevation': self.elevation,
            'is_capital': self.is_capital,
            'timezone': self.timezone
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'City':
        """
        Create a City object from dictionary
        
        Args:
            data: Dictionary with city attributes
            
        Returns:
            City object
        """
        return cls(
            id=data['id'],
            name=data['name'],
            region=data.get('region', 'Unknown'),
            latitude=data.get('latitude', 0.0),
            longitude=data.get('longitude', 0.0),
            population=data.get('population'),
            elevation=data.get('elevation'),
            is_capital=data.get('is_capital', False),
            timezone=data.get('timezone', 'EAT')
        )
    
    def __str__(self) -> str:
        """String representation of the city"""
        capital_mark = " (Capital)" if self.is_capital else ""
        if self.region and self.region != "Unknown":
            return f"{self.name}, {self.region}{capital_mark}"
        return f"{self.name}{capital_mark}"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (f"City(id={self.id}, name='{self.name}', region='{self.region}', "
                f"lat={self.latitude:.2f}, lon={self.longitude:.2f})")
    
    def __eq__(self, other) -> bool:
        """Check equality based on id"""
        if isinstance(other, City):
            return self.id == other.id
        return False
    
    def __hash__(self) -> int:
        """Hash based on id"""
        return hash(self.id)


# Example usage and testing
if __name__ == "__main__":
    # Create Ethiopian cities
    addis_ababa = City(
        id=1,
        name="Addis Ababa",
        region="Addis Ababa",
        latitude=9.03,
        longitude=38.74,
        population=3500000,
        elevation=2355,
        is_capital=True
    )
    
    bahir_dar = City(
        id=2,
        name="Bahir Dar",
        region="Amhara",
        latitude=11.60,
        longitude=37.38,
        population=350000,
        elevation=1800,
        is_capital=False
    )
    
    # Test distance calculation
    print(f"City 1: {addis_ababa}")
    print(f"City 2: {bahir_dar}")
    print(f"Haversine distance: {addis_ababa.distance_to(bahir_dar)} km")
    print(f"Euclidean distance: {addis_ababa.distance_to(bahir_dar, 'euclidean')} km")
    
    # Test dictionary conversion
    city_dict = addis_ababa.to_dict()
    print(f"\nDictionary representation: {city_dict}")
    
    # Test recreation from dictionary
    new_city = City.from_dict(city_dict)
    print(f"Recreated city: {new_city}")