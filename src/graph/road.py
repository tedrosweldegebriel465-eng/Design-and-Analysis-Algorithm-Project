"""
Road class representing a connection between Ethiopian cities
"""

from enum import Enum
from typing import Optional, Dict, Any


class RoadType(Enum):
    """Enumeration of Ethiopian road types"""
    HIGHWAY = "highway"           # Federal highways
    NATIONAL = "national"          # National roads
    REGIONAL = "regional"          # Regional roads  
    LOCAL = "local"                # Local roads
    GRAVEL = "gravel"              # Gravel roads
    RURAL = "rural"                # Rural roads


class RoadCondition(Enum):
    """Enumeration of road conditions in Ethiopia"""
    EXCELLENT = "excellent"        # Newly paved
    GOOD = "good"                  # Good condition
    FAIR = "fair"                  # Some wear
    POOR = "poor"                  # Needs repair
    UNDER_CONSTRUCTION = "under_construction"  # Under construction
    SEASONAL = "seasonal"          # Passable only in dry season


class Road:
    """
    Represents a road connecting two Ethiopian cities with various attributes
    
    Attributes:
        id (int): Unique identifier for the road
        city1_id (int): ID of first city
        city2_id (int): ID of second city
        distance (float): Road distance in kilometers
        road_type (RoadType): Type of road
        condition (RoadCondition): Current road condition
        speed_limit (int): Speed limit in km/h
        lanes (int): Number of lanes
        toll (bool): Whether road requires toll payment
        name (str): Road name/number (e.g., "A1", "B30")
        terrain_factor (float): Terrain difficulty factor (1.0 = flat, >1.0 = hilly)
        seasonal (bool): Whether road is seasonal
    """
    
    def __init__(self,
                 id: int,
                 city1_id: int,
                 city2_id: int,
                 distance: float,
                 road_type: RoadType = RoadType.REGIONAL,
                 condition: RoadCondition = RoadCondition.GOOD,
                 speed_limit: int = 80,
                 lanes: int = 2,
                 toll: bool = False,
                 name: Optional[str] = None,
                 terrain_factor: float = 1.0,
                 seasonal: bool = False):
        """
        Initialize a road with required and optional attributes
        
        Args:
            id: Unique identifier
            city1_id: ID of first city
            city2_id: ID of second city
            distance: Distance in kilometers
            road_type: Type of road
            condition: Current road condition
            speed_limit: Speed limit in km/h
            lanes: Number of lanes
            toll: Whether toll is required
            name: Road name/number
            terrain_factor: Terrain difficulty
            seasonal: Whether road is seasonal
        """
        self.id = id
        self.city1_id = city1_id
        self.city2_id = city2_id
        self.distance = distance
        self.road_type = road_type
        self.condition = condition
        self.speed_limit = speed_limit
        self.lanes = lanes
        self.toll = toll
        self.name = name
        self.terrain_factor = terrain_factor
        self.seasonal = seasonal
        
        # Validate distance
        if distance <= 0:
            raise ValueError(f"Distance must be positive, got {distance}")
    
    def get_other_city(self, city_id: int) -> int:
        """
        Get the ID of the city on the other end of the road
        
        Args:
            city_id: ID of one city
            
        Returns:
            ID of the other city
            
        Raises:
            ValueError: If city_id is not one of the endpoints
        """
        if city_id == self.city1_id:
            return self.city2_id
        elif city_id == self.city2_id:
            return self.city1_id
        else:
            raise ValueError(f"City {city_id} is not an endpoint of this road")
    
    def get_travel_time(self, speed: Optional[float] = None) -> float:
        """
        Calculate estimated travel time in hours
        
        Args:
            speed: Actual speed in km/h (if None, uses speed_limit * factors)
            
        Returns:
            Travel time in hours
        """
        if speed is None:
            # Calculate effective speed considering conditions
            effective_speed = self.speed_limit
            
            # Adjust for road condition
            condition_factors = {
                RoadCondition.EXCELLENT: 1.0,
                RoadCondition.GOOD: 0.9,
                RoadCondition.FAIR: 0.7,
                RoadCondition.POOR: 0.5,
                RoadCondition.UNDER_CONSTRUCTION: 0.3,
                RoadCondition.SEASONAL: 0.4 if not self._is_dry_season() else 0.8
            }
            effective_speed *= condition_factors.get(self.condition, 0.9)
            
            # Adjust for terrain
            effective_speed /= self.terrain_factor
            
            # Adjust for lanes (more lanes = faster traffic flow)
            if self.lanes >= 4:
                effective_speed *= 1.1
            elif self.lanes == 1:
                effective_speed *= 0.8
        else:
            effective_speed = speed
        
        # Calculate time (distance / speed)
        if effective_speed <= 0:
            return float('inf')
        
        return self.distance / effective_speed
    
    def _is_dry_season(self) -> bool:
        """Helper to check if it's dry season (simplified)"""
        # In a real app, this would check current date
        # For Ethiopia, dry season is roughly October to May
        return True  # Simplified for now
    
    def get_effective_distance(self, consider_season: bool = True,
                              consider_terrain: bool = True) -> float:
        """
        Get effective distance considering various factors
        
        Args:
            consider_season: Whether to consider seasonal roads
            consider_terrain: Whether to include terrain factor
            
        Returns:
            Effective distance in kilometers
        """
        effective_dist = self.distance
        
        if consider_terrain:
            effective_dist *= self.terrain_factor
        
        if consider_season and self.seasonal and not self._is_dry_season():
            # Seasonal road becomes longer (detour) in wet season
            effective_dist *= 1.5
        
        return effective_dist
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert road to dictionary for serialization
        
        Returns:
            Dictionary representation of the road
        """
        return {
            'id': self.id,
            'city1_id': self.city1_id,
            'city2_id': self.city2_id,
            'distance': self.distance,
            'road_type': self.road_type.value,
            'condition': self.condition.value,
            'speed_limit': self.speed_limit,
            'lanes': self.lanes,
            'toll': self.toll,
            'name': self.name,
            'terrain_factor': self.terrain_factor,
            'seasonal': self.seasonal
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Road':
        """
        Create a Road object from dictionary
        
        Args:
            data: Dictionary with road attributes
            
        Returns:
            Road object
        """
        # Convert string enums back to Enum objects
        road_type_str = data.get('road_type', 'regional')
        road_type = RoadType.REGIONAL
        for rt in RoadType:
            if rt.value == road_type_str:
                road_type = rt
                break
        
        condition_str = data.get('condition', 'good')
        condition = RoadCondition.GOOD
        for cond in RoadCondition:
            if cond.value == condition_str:
                condition = cond
                break
        
        return cls(
            id=data['id'],
            city1_id=data['city1_id'],
            city2_id=data['city2_id'],
            distance=data['distance'],
            road_type=road_type,
            condition=condition,
            speed_limit=data.get('speed_limit', 80),
            lanes=data.get('lanes', 2),
            toll=data.get('toll', False),
            name=data.get('name'),
            terrain_factor=data.get('terrain_factor', 1.0),
            seasonal=data.get('seasonal', False)
        )
    
    def __str__(self) -> str:
        """String representation of the road"""
        if self.name:
            return f"{self.name}: {self.distance} km ({self.road_type.value})"
        else:
            return f"Road {self.id}: {self.distance} km ({self.road_type.value})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (f"Road(id={self.id}, cities=({self.city1_id},{self.city2_id}), "
                f"dist={self.distance}, type={self.road_type.value})")


# Example usage and testing
if __name__ == "__main__":
    # Create a test Ethiopian road
    addis_adama = Road(
        id=1,
        city1_id=1,  # Addis Ababa
        city2_id=2,  # Adama
        distance=85,
        road_type=RoadType.HIGHWAY,
        condition=RoadCondition.GOOD,
        speed_limit=100,
        lanes=4,
        name="A1 Highway",
        terrain_factor=1.1
    )
    
    print(f"Road: {addis_adama}")
    print(f"Other city from city 1: {addis_adama.get_other_city(1)}")
    print(f"Travel time: {addis_adama.get_travel_time():.2f} hours")
    print(f"Effective distance: {addis_adama.get_effective_distance():.2f} km")
    
    # Test dictionary conversion
    road_dict = addis_adama.to_dict()
    print(f"\nDictionary: {road_dict}")
    
    # Test recreation
    new_road = Road.from_dict(road_dict)
    print(f"Recreated: {new_road}")