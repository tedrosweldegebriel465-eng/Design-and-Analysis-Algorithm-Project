"""
Path reconstruction and utility functions for Ethiopian road network shortest paths
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Tuple, Optional, Any
from src.graph.network import RoadNetwork
from src.graph.city import City
from src.graph.road import Road


class PathUtils:
    """
    Utility class for path reconstruction and analysis in Ethiopian road network
    """
    
    def __init__(self, network: RoadNetwork):
        """
        Initialize with Ethiopian road network
        
        Args:
            network: RoadNetwork object
        """
        self.network = network
    
    def reconstruct_path(self, parents: Dict[int, int],
                        source_id: int,
                        dest_id: int) -> List[int]:
        """
        Reconstruct path from source to destination using parent array
        
        Args:
            parents: Dictionary mapping city ID to its parent in shortest path
            source_id: Source Ethiopian city ID
            dest_id: Destination Ethiopian city ID
            
        Returns:
            List of city IDs in order from source to destination
        """
        if dest_id not in parents:
            return []
        
        path = []
        current = dest_id
        
        # Traverse backwards from destination to source
        while current != -1 and current in parents:
            path.append(current)
            if current == source_id:
                break
            current = parents[current]
        
        # If we didn't reach source, no valid path
        if not path or path[-1] != source_id:
            return []
        
        # Reverse to get path from source to destination
        path.reverse()
        return path
    
    def get_path_string(self, path_ids: List[int],
                       include_distances: bool = False,
                       distances: Optional[Dict[int, float]] = None,
                       include_regions: bool = False) -> str:
        """
        Convert path IDs to readable string with Ethiopian city names
        
        Args:
            path_ids: List of Ethiopian city IDs in path
            include_distances: Whether to include distances between cities
            distances: Dictionary of distances (if include_distances is True)
            include_regions: Whether to include region names
            
        Returns:
            Formatted path string
        """
        if not path_ids:
            return "No path found"
        
        path_parts = []
        cumulative_dist = 0
        
        for i, city_id in enumerate(path_ids):
            city = self.network.get_city_by_id(city_id)
            if not city:
                city_name = f"Unknown_{city_id}"
            else:
                if include_regions:
                    city_name = f"{city.name} ({city.region})"
                else:
                    city_name = city.name
            
            if i == 0:
                path_parts.append(city_name)
            else:
                if include_distances and distances:
                    # Get distance between previous and current city
                    prev_id = path_ids[i-1]
                    road = self.network.get_road_between(prev_id, city_id)
                    if road:
                        cumulative_dist += road.distance
                        path_parts.append(f"──[{road.distance} km]→ {city_name}")
                    else:
                        path_parts.append(f"→ {city_name}")
                else:
                    path_parts.append(f"→ {city_name}")
        
        return " ".join(path_parts)
    
    def format_path_table(self, source_id: int,
                         distances: Dict[int, float],
                         parents: Dict[int, int],
                         max_cities: int = 10) -> str:
        """
        Format paths as a readable table for Ethiopian cities
        
        Args:
            source_id: Source Ethiopian city ID
            distances: Distances dictionary
            parents: Parents dictionary
            max_cities: Maximum number of cities to show
            
        Returns:
            Formatted table string
        """
        source_city = self.network.get_city_by_id(source_id)
        source_name = source_city.name if source_city else f"City_{source_id}"
        
        lines = []
        lines.append("\n" + "="*90)
        lines.append(f"SHORTEST PATHS FROM {source_name} TO ETHIOPIAN CITIES")
        lines.append("="*90)
        lines.append(f"{'Destination':<35} {'Distance (km)':<15} {'Path'}")
        lines.append("-"*90)
        
        # Sort cities by distance
        city_distances = [(cid, dist) for cid, dist in distances.items()
                         if cid != source_id and dist != float('inf')]
        city_distances.sort(key=lambda x: x[1])
        
        # Show only top max_cities
        for city_id, dist in city_distances[:max_cities]:
            city = self.network.get_city_by_id(city_id)
            dest_name = city.name if city else f"City_{city_id}"
            
            # Add region if available
            if city and city.region:
                dest_name = f"{dest_name} ({city.region})"
            
            path_ids = self.reconstruct_path(parents, source_id, city_id)
            path_str = self.get_path_string(path_ids)
            
            # Truncate long paths
            if len(path_str) > 45:
                path_str = path_str[:42] + "..."
            
            lines.append(f"{dest_name:<35} {dist:<15.2f} {path_str}")
        
        if len(city_distances) > max_cities:
            lines.append(f"\n... and {len(city_distances) - max_cities} more Ethiopian cities")
        
        return "\n".join(lines)
    
    def get_path_details(self, path_ids: List[int]) -> Dict[str, Any]:
        """
        Get detailed information about a path
        
        Args:
            path_ids: List of Ethiopian city IDs in path
            
        Returns:
            Dictionary with path details
        """
        if len(path_ids) < 2:
            return {
                'valid': False,
                'message': 'Path must contain at least 2 cities'
            }
        
        details = {
            'valid': True,
            'num_cities': len(path_ids),
            'num_segments': len(path_ids) - 1,
            'total_distance': 0.0,
            'segments': [],
            'cities': [],
            'regions_visited': set(),
            'road_types': set()
        }
        
        # Add city information
        for city_id in path_ids:
            city = self.network.get_city_by_id(city_id)
            if city:
                details['cities'].append({
                    'id': city_id,
                    'name': city.name,
                    'region': city.region,
                    'is_capital': city.is_capital
                })
                details['regions_visited'].add(city.region)
        
        # Add segment information
        for i in range(len(path_ids) - 1):
            city1_id = path_ids[i]
            city2_id = path_ids[i + 1]
            
            road = self.network.get_road_between(city1_id, city2_id)
            if road:
                details['total_distance'] += road.distance
                details['segments'].append({
                    'from_id': city1_id,
                    'to_id': city2_id,
                    'distance': road.distance,
                    'road_name': road.name,
                    'road_type': road.road_type.value,
                    'condition': road.condition.value
                })
                details['road_types'].add(road.road_type.value)
        
        # Convert sets to lists for JSON serialization
        details['regions_visited'] = list(details['regions_visited'])
        details['road_types'] = list(details['road_types'])
        
        # Add summary statistics
        if details['segments']:
            distances = [s['distance'] for s in details['segments']]
            details['avg_segment_distance'] = sum(distances) / len(distances)
            details['max_segment_distance'] = max(distances)
            details['min_segment_distance'] = min(distances)
        
        return details
    
    def find_alternative_paths(self, source_id: int, dest_id: int,
                              k: int = 3) -> List[Tuple[float, List[int]]]:
        """
        Find alternative paths between two Ethiopian cities
        
        Args:
            source_id: Source Ethiopian city ID
            dest_id: Destination Ethiopian city ID
            k: Number of alternative paths to find
            
        Returns:
            List of (distance, path) tuples
        """
        from src.algorithms.dijkstra_pq import DijkstraPriorityQueue
        
        dijkstra = DijkstraPriorityQueue(self.network)
        
        # Use the k-shortest paths method
        return dijkstra.find_k_shortest_paths(source_id, dest_id, k)
    
    def export_path_to_geojson(self, path_ids: List[int]) -> Dict:
        """
        Export path as GeoJSON for mapping
        
        Args:
            path_ids: List of Ethiopian city IDs in path
            
        Returns:
            GeoJSON FeatureCollection
        """
        features = []
        
        # Add cities as points
        for city_id in path_ids:
            city = self.network.get_city_by_id(city_id)
            if city:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [city.longitude, city.latitude]
                    },
                    "properties": {
                        "name": city.name,
                        "region": city.region,
                        "type": "city",
                        "is_capital": city.is_capital
                    }
                }
                features.append(feature)
        
        # Add roads as lines
        for i in range(len(path_ids) - 1):
            city1 = self.network.get_city_by_id(path_ids[i])
            city2 = self.network.get_city_by_id(path_ids[i + 1])
            road = self.network.get_road_between(path_ids[i], path_ids[i + 1])
            
            if city1 and city2:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [city1.longitude, city1.latitude],
                            [city2.longitude, city2.latitude]
                        ]
                    },
                    "properties": {
                        "from": city1.name,
                        "to": city2.name,
                        "distance": road.distance if road else 0,
                        "road_name": road.name if road else None,
                        "type": "road"
                    }
                }
                features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def calculate_path_cost_with_factors(self, path_ids: List[int],
                                        consider_traffic: bool = False,
                                        consider_season: bool = False) -> float:
        """
        Calculate path cost considering various factors
        
        Args:
            path_ids: List of Ethiopian city IDs in path
            consider_traffic: Whether to consider traffic
            consider_season: Whether to consider seasonal roads
            
        Returns:
            Total effective distance/cost
        """
        if len(path_ids) < 2:
            return float('inf')
        
        total_cost = 0.0
        
        for i in range(len(path_ids) - 1):
            road = self.network.get_road_between(path_ids[i], path_ids[i + 1])
            if road:
                if consider_season and road.seasonal:
                    # Seasonal road factor
                    total_cost += road.distance * 1.5
                else:
                    total_cost += road.distance
                
                if consider_traffic:
                    # Traffic factor based on road type and time
                    traffic_factors = {
                        'highway': 1.2,
                        'national': 1.1,
                        'regional': 1.0,
                        'local': 0.9
                    }
                    total_cost *= traffic_factors.get(road.road_type.value, 1.0)
        
        return round(total_cost, 2)


# Example usage with Ethiopian cities
if __name__ == "__main__":
    from src.graph.network import RoadNetwork
    from src.algorithms.dijkstra_pq import DijkstraPriorityQueue
    
    print("="*80)
    print("PATH UTILITIES FOR ETHIOPIAN ROAD NETWORK")
    print("="*80)
    
    # Create Ethiopian road network
    network = RoadNetwork()
    network.generate_ethiopian_network(num_cities=20, num_roads=30)
    
    # Create path utils
    path_utils = PathUtils(network)
    
    # Get source and destination
    cities = list(network.cities.values())
    source = cities[0]
    dest = cities[-1]
    
    print(f"\n📍 Source: {source.name} ({source.region})")
    print(f"📍 Destination: {dest.name} ({dest.region})")
    
    # Find shortest path
    dijkstra = DijkstraPriorityQueue(network)
    distances, parents = dijkstra.find_shortest_paths(source.id)
    
    # Reconstruct path
    path_ids = path_utils.reconstruct_path(parents, source.id, dest.id)
    
    if path_ids:
        print("\n✅ Shortest path found:")
        path_str = path_utils.get_path_string(path_ids, include_distances=True, include_regions=True)
        print(f"\n   {path_str}")
        
        # Get path details
        print("\n📊 Path Details:")
        details = path_utils.get_path_details(path_ids)
        print(f"   Total distance: {details['total_distance']:.2f} km")
        print(f"   Number of cities: {details['num_cities']}")
        print(f"   Regions visited: {', '.join(details['regions_visited'])}")
        print(f"   Road types: {', '.join(details['road_types'])}")
        
        # Format as table
        print(path_utils.format_path_table(source.id, distances, parents))
        
        # Export to GeoJSON
        geojson = path_utils.export_path_to_geojson(path_ids)
        print(f"\n🗺️  GeoJSON exported with {len(geojson['features'])} features")