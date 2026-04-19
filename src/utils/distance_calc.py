"""
Distance Calculator Utility - Calculate distances between Ethiopian cities
Implements multiple distance calculation methods with geographic accuracy
"""

import math
from typing import Tuple, Optional, List, Dict
from enum import Enum


class DistanceMethod(Enum):
    """Available distance calculation methods"""
    HAVERSINE = "haversine"
    VINCENTY = "vincenty"
    EUCLIDEAN = "euclidean"
    ROAD_ESTIMATE = "road_estimate"


class DistanceCalculator:
    """
    Utility class for calculating distances between geographic coordinates
    Specialized for Ethiopian geography with elevation and terrain factors
    
    Features:
    - Multiple calculation methods
    - Elevation-aware distance calculation
    - Terrain factor estimation based on Ethiopian regions
    - Batch distance calculations
    - Bearing and midpoint calculations
    """
    
    # Earth constants
    EARTH_RADIUS_KM = 6371.0  # Mean radius in kilometers
    EARTH_RADIUS_MI = 3958.8   # Mean radius in miles
    EARTH_RADIUS_M = 6371000    # Radius in meters
    
    # Ethiopian region terrain factors
    REGION_TERRAIN_FACTORS = {
        'Addis Ababa': 1.1,      # Urban area
        'Oromia': 1.3,           # Mixed terrain
        'Amhara': 1.4,           # Highlands
        'Tigray': 1.4,           # Highlands
        'SNNPR': 1.5,            # Mountainous
        'Dire Dawa': 1.1,        # Lowland
        'Harari': 1.2,           # Hilly
        'Somali': 1.0,           # Flat lowland
        'Gambella': 1.1,         # Flat lowland
        'Benshangul': 1.2,       # Mixed
        'Afar': 1.0,             # Desert lowland
        'Unknown': 1.2
    }
    
    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float,
                  unit: str = 'km') -> float:
        """
        Calculate great-circle distance using Haversine formula
        
        Args:
            lat1, lon1: Coordinates of first point in degrees
            lat2, lon2: Coordinates of second point in degrees
            unit: 'km' for kilometers, 'mi' for miles, 'm' for meters
            
        Returns:
            Distance in specified unit
        """
        # Validate inputs
        DistanceCalculator._validate_coordinates(lat1, lon1, lat2, lon2)
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Apply earth radius based on unit
        if unit == 'km':
            radius = DistanceCalculator.EARTH_RADIUS_KM
        elif unit == 'mi':
            radius = DistanceCalculator.EARTH_RADIUS_MI
        else:  # meters
            radius = DistanceCalculator.EARTH_RADIUS_M
        
        distance = radius * c
        return round(distance, 2)
    
    @staticmethod
    def vincenty(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance using Vincenty's formula (more accurate for ellipsoid)
        
        Args:
            lat1, lon1: Coordinates of first point in degrees
            lat2, lon2: Coordinates of second point in degrees
            
        Returns:
            Distance in kilometers
        """
        DistanceCalculator._validate_coordinates(lat1, lon1, lat2, lon2)
        
        # WGS-84 ellipsoid parameters
        a = 6378137.0  # Semi-major axis in meters
        f = 1 / 298.257223563  # Flattening
        b = (1 - f) * a  # Semi-minor axis
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Reduced latitudes
        u1 = math.atan((1 - f) * math.tan(lat1_rad))
        u2 = math.atan((1 - f) * math.tan(lat2_rad))
        
        # Longitude difference
        L = lon2_rad - lon1_rad
        lambda_ = L
        lambda_prev = 0
        
        # Iterative calculation
        for _ in range(100):  # Max iterations
            sin_lambda = math.sin(lambda_)
            cos_lambda = math.cos(lambda_)
            
            sin_sigma = math.sqrt(
                (math.cos(u2) * sin_lambda) ** 2 +
                (math.cos(u1) * math.sin(u2) -
                 math.sin(u1) * math.cos(u2) * cos_lambda) ** 2
            )
            
            if sin_sigma == 0:
                return 0.0  # Coincident points
            
            cos_sigma = (math.sin(u1) * math.sin(u2) +
                        math.cos(u1) * math.cos(u2) * cos_lambda)
            
            sigma = math.atan2(sin_sigma, cos_sigma)
            
            sin_alpha = (math.cos(u1) * math.cos(u2) * sin_lambda /
                        sin_sigma) if sin_sigma != 0 else 0
            cos_sq_alpha = 1 - sin_alpha ** 2
            
            cos2_alpha_m = (cos_sigma - 2 * math.sin(u1) * math.sin(u2) /
                           cos_sq_alpha) if cos_sq_alpha != 0 else 0
            
            C = (f / 16) * cos_sq_alpha * (4 + f * (4 - 3 * cos_sq_alpha))
            
            lambda_prev = lambda_
            lambda_ = (L + (1 - C) * f * sin_alpha *
                      (sigma + C * sin_sigma *
                       (cos2_alpha_m + C * cos_sigma *
                        (-1 + 2 * cos2_alpha_m ** 2))))
            
            if abs(lambda_ - lambda_prev) < 1e-12:
                break
        
        # Calculate distance
        u_sq = cos_sq_alpha * (a ** 2 - b ** 2) / (b ** 2)
        A = 1 + (u_sq / 16384) * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
        B = (u_sq / 1024) * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))
        
        delta_sigma = (B * sin_sigma *
                      (cos2_alpha_m + (B / 4) *
                       (cos_sigma * (-1 + 2 * cos2_alpha_m ** 2) -
                        (B / 6) * cos2_alpha_m *
                        (-3 + 4 * sin_sigma ** 2) *
                        (-3 + 4 * cos2_alpha_m ** 2))))
        
        distance = b * A * (sigma - delta_sigma)
        return round(distance / 1000, 2)  # Convert to kilometers
    
    @staticmethod
    def euclidean_approx(lat1: float, lon1: float,
                        lat2: float, lon2: float) -> float:
        """
        Approximate Euclidean distance (for small distances only)
        
        Args:
            lat1, lon1: Coordinates of first point in degrees
            lat2, lon2: Coordinates of second point in degrees
            
        Returns:
            Approximate distance in kilometers
        """
        DistanceCalculator._validate_coordinates(lat1, lon1, lat2, lon2)
        
        # Approximate conversion: 1 degree latitude ≈ 111 km
        km_per_deg_lat = 111.0
        
        avg_lat = (lat1 + lat2) / 2
        km_per_deg_lon = 111.0 * math.cos(math.radians(avg_lat))
        
        dlat = (lat2 - lat1) * km_per_deg_lat
        dlon = (lon2 - lon1) * km_per_deg_lon
        
        distance = math.sqrt(dlat ** 2 + dlon ** 2)
        return round(distance, 2)
    
    @staticmethod
    def road_estimate(lat1: float, lon1: float, lat2: float, lon2: float,
                     region1: str = 'Unknown', region2: str = 'Unknown',
                     elevation1: Optional[float] = None,
                     elevation2: Optional[float] = None) -> float:
        """
        Estimate realistic road distance considering terrain and elevation
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            region1, region2: Ethiopian regions for terrain factor
            elevation1, elevation2: Elevations in meters
            
        Returns:
            Estimated road distance in kilometers
        """
        # Get base great-circle distance
        base_dist = DistanceCalculator.haversine(lat1, lon1, lat2, lon2)
        
        # Get terrain factor based on regions
        terrain_factor1 = DistanceCalculator.REGION_TERRAIN_FACTORS.get(region1, 1.2)
        terrain_factor2 = DistanceCalculator.REGION_TERRAIN_FACTORS.get(region2, 1.2)
        avg_terrain = (terrain_factor1 + terrain_factor2) / 2
        
        # Elevation factor (roads go up and down)
        elevation_factor = 1.0
        if elevation1 is not None and elevation2 is not None:
            elevation_diff = abs(elevation1 - elevation2)
            if elevation_diff > 1000:
                elevation_factor = 1.4  # Mountainous
            elif elevation_diff > 500:
                elevation_factor = 1.25  # Hilly
            elif elevation_diff > 200:
                elevation_factor = 1.1   # Rolling hills
        
        # Combined road factor
        road_factor = avg_terrain * elevation_factor
        
        # Minimum road factor (roads are never shorter than straight line)
        road_factor = max(road_factor, 1.1)
        
        return round(base_dist * road_factor, 2)
    
    @staticmethod
    def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate initial bearing from point1 to point2
        
        Args:
            lat1, lon1: Coordinates of first point in degrees
            lat2, lon2: Coordinates of second point in degrees
            
        Returns:
            Bearing in degrees (0-360)
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlon_rad = math.radians(lon2 - lon1)
        
        x = math.sin(dlon_rad) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))
        
        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        
        # Convert to 0-360 range
        compass_bearing = (initial_bearing + 360) % 360
        
        return round(compass_bearing, 2)
    
    @staticmethod
    def midpoint(lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[float, float]:
        """
        Calculate midpoint between two coordinates
        
        Args:
            lat1, lon1: Coordinates of first point in degrees
            lat2, lon2: Coordinates of second point in degrees
            
        Returns:
            (latitude, longitude) of midpoint
        """
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Convert to Cartesian coordinates
        x1 = math.cos(lat1_rad) * math.cos(lon1_rad)
        y1 = math.cos(lat1_rad) * math.sin(lon1_rad)
        z1 = math.sin(lat1_rad)
        
        x2 = math.cos(lat2_rad) * math.cos(lon2_rad)
        y2 = math.cos(lat2_rad) * math.sin(lon2_rad)
        z2 = math.sin(lat2_rad)
        
        # Average
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        z = (z1 + z2) / 2
        
        # Convert back to spherical coordinates
        lon = math.atan2(y, x)
        hyp = math.sqrt(x ** 2 + y ** 2)
        lat = math.atan2(z, hyp)
        
        return (round(math.degrees(lat), 4), round(math.degrees(lon), 4))
    
    @staticmethod
    def destination_point(lat: float, lon: float,
                         bearing: float, distance: float,
                         unit: str = 'km') -> Tuple[float, float]:
        """
        Calculate destination point given start point, bearing, and distance
        
        Args:
            lat, lon: Start coordinates in degrees
            bearing: Bearing in degrees
            distance: Distance to travel
            unit: 'km' or 'mi'
            
        Returns:
            (latitude, longitude) of destination
        """
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        
        # Angular distance
        if unit == 'km':
            angular_dist = distance / DistanceCalculator.EARTH_RADIUS_KM
        else:  # miles
            angular_dist = distance / DistanceCalculator.EARTH_RADIUS_MI
        
        # Calculate destination
        dest_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(angular_dist) +
            math.cos(lat_rad) * math.sin(angular_dist) * math.cos(bearing_rad)
        )
        
        dest_lon_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(angular_dist) * math.cos(lat_rad),
            math.cos(angular_dist) - math.sin(lat_rad) * math.sin(dest_lat_rad)
        )
        
        return (math.degrees(dest_lat_rad), math.degrees(dest_lon_rad))
    
    @staticmethod
    def batch_distance(points: List[Tuple[float, float]],
                      method: str = 'haversine') -> List[float]:
        """
        Calculate distances between consecutive points in a list
        
        Args:
            points: List of (lat, lon) tuples
            method: Distance method to use
            
        Returns:
            List of distances between consecutive points
        """
        if len(points) < 2:
            return []
        
        distances = []
        for i in range(len(points) - 1):
            lat1, lon1 = points[i]
            lat2, lon2 = points[i + 1]
            
            if method == 'haversine':
                dist = DistanceCalculator.haversine(lat1, lon1, lat2, lon2)
            elif method == 'vincenty':
                dist = DistanceCalculator.vincenty(lat1, lon1, lat2, lon2)
            else:
                dist = DistanceCalculator.euclidean_approx(lat1, lon1, lat2, lon2)
            
            distances.append(dist)
        
        return distances
    
    @staticmethod
    def total_distance(points: List[Tuple[float, float]],
                      method: str = 'haversine') -> float:
        """
        Calculate total distance along a path of points
        
        Args:
            points: List of (lat, lon) tuples
            method: Distance method to use
            
        Returns:
            Total distance
        """
        distances = DistanceCalculator.batch_distance(points, method)
        return sum(distances)
    
    @staticmethod
    def _validate_coordinates(lat1: float, lon1: float,
                             lat2: float, lon2: float):
        """Validate coordinate ranges"""
        if not -90 <= lat1 <= 90:
            raise ValueError(f"Latitude {lat1} must be between -90 and 90")
        if not -90 <= lat2 <= 90:
            raise ValueError(f"Latitude {lat2} must be between -90 and 90")
        if not -180 <= lon1 <= 180:
            raise ValueError(f"Longitude {lon1} must be between -180 and 180")
        if not -180 <= lon2 <= 180:
            raise ValueError(f"Longitude {lon2} must be between -180 and 180")
    
    @staticmethod
    def format_distance(distance: float, unit: str = 'km',
                       decimals: int = 1) -> str:
        """
        Format distance with appropriate units
        
        Args:
            distance: Distance value
            unit: Unit ('km', 'mi', 'm')
            decimals: Number of decimal places
            
        Returns:
            Formatted distance string
        """
        if distance < 0.1 and unit == 'km':
            # Convert to meters for small distances
            meters = distance * 1000
            return f"{meters:.0f} m"
        elif unit == 'km':
            return f"{distance:.{decimals}f} km"
        elif unit == 'mi':
            return f"{distance:.{decimals}f} mi"
        else:
            return f"{distance:.{decimals}f} {unit}"
    
    @staticmethod
    def get_distance_table(points: List[Tuple[float, float, str]],
                          method: str = 'haversine') -> str:
        """
        Create a formatted distance table for multiple points
        
        Args:
            points: List of (lat, lon, name) tuples
            method: Distance method
            
        Returns:
            Formatted table string
        """
        n = len(points)
        if n < 2:
            return "Need at least 2 points"
        
        lines = []
        lines.append("\n" + "="*70)
        lines.append("DISTANCE TABLE")
        lines.append("="*70)
        lines.append(f"{'From':<20} {'To':<20} {'Distance':<15} {'Bearing':<10}")
        lines.append("-"*70)
        
        for i in range(n):
            for j in range(i + 1, n):
                lat1, lon1, name1 = points[i]
                lat2, lon2, name2 = points[j]
                
                dist = DistanceCalculator.haversine(lat1, lon1, lat2, lon2)
                bearing = DistanceCalculator.bearing(lat1, lon1, lat2, lon2)
                
                lines.append(f"{name1:<20} {name2:<20} "
                           f"{DistanceCalculator.format_distance(dist):<15} "
                           f"{bearing}°")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    print("="*80)
    print("TESTING DISTANCE CALCULATOR WITH ETHIOPIAN CITIES")
    print("="*80)
    
    # Ethiopian cities coordinates
    cities = [
        (9.03, 38.74, "Addis Ababa"),
        (13.50, 39.47, "Mekelle"),
        (11.60, 37.38, "Bahir Dar"),
        (8.54, 39.27, "Adama"),
        (9.60, 41.87, "Dire Dawa")
    ]
    
    # Test different methods
    print("\n1. Distance between Addis Ababa and Mekelle:")
    lat1, lon1, name1 = cities[0]
    lat2, lon2, name2 = cities[1]
    
    print(f"   Haversine: {DistanceCalculator.haversine(lat1, lon1, lat2, lon2):.2f} km")
    print(f"   Vincenty: {DistanceCalculator.vincenty(lat1, lon1, lat2, lon2):.2f} km")
    print(f"   Euclidean: {DistanceCalculator.euclidean_approx(lat1, lon1, lat2, lon2):.2f} km")
    print(f"   Road estimate: {DistanceCalculator.road_estimate(lat1, lon1, lat2, lon2, 'Addis Ababa', 'Tigray', 2355, 2084):.2f} km")
    
    # Test bearing
    print(f"\n2. Bearing: {DistanceCalculator.bearing(lat1, lon1, lat2, lon2)}°")
    
    # Test midpoint
    mid_lat, mid_lon = DistanceCalculator.midpoint(lat1, lon1, lat2, lon2)
    print(f"\n3. Midpoint: ({mid_lat}, {mid_lon})")
    
    # Test distance table
    print(DistanceCalculator.get_distance_table(cities))