"""
Dijkstra's Algorithm implementation using arrays (O(V²))
For Ethiopian road network shortest path calculation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Tuple, Optional, Dict
from src.graph.network import RoadNetwork
from src.graph.city import City


class DijkstraArray:
    """
    Dijkstra's Algorithm implementation using arrays
    Time Complexity: O(V²) where V is number of vertices
    Space Complexity: O(V)
    
    This is the required implementation for the GPS navigation system
    """
    
    def __init__(self, network: RoadNetwork):
        """
        Initialize Dijkstra's algorithm with an Ethiopian road network
        
        Args:
            network: RoadNetwork object containing Ethiopian cities and roads
        """
        self.network = network
        self.V = network.get_city_count()
        self.dist = []      # Shortest distance array
        self.visited = []   # Visited vertices array
        self.parent = []    # Parent array for path reconstruction
        self.step_records = []  # For demonstration purposes
        
    def find_shortest_paths(self, source_city_id: int, record_steps: bool = False, weight_func=None) -> Tuple[Dict[int, float], Dict[int, int]]:
        """
        Find shortest paths from source Ethiopian city to all cities using array-based Dijkstra
        
        Args:
            source_city_id: ID of source Ethiopian city
            record_steps: Whether to record step-by-step progress for demonstration
            
        Returns:
            Tuple of (distances dictionary, parent dictionary)
            
        Raises:
            ValueError: If source city not found
        """
        # Store weight_func for use in relaxation
        self._weight_func = weight_func

        # Check if source exists
        if source_city_id not in self.network.city_indices:
            raise ValueError(f"Source city ID {source_city_id} not found in Ethiopian cities")
        
        # Get source index in adjacency matrix
        source_idx = self.network.city_indices[source_city_id]
        
        # Initialize arrays
        self.V = self.network.get_city_count()
        self.dist = [float('inf')] * self.V
        self.visited = [False] * self.V
        self.parent = [-1] * self.V
        
        # Clear step records
        self.step_records = []
        
        # Distance to source is 0
        self.dist[source_idx] = 0
        
        # Record initial state
        if record_steps:
            self._record_step(source_idx, -1, f"Starting from {self._get_city_name(source_idx)}")
        
        # Find shortest paths for all vertices
        for step in range(self.V):
            # Select the minimum distance vertex not yet visited
            u = self._min_distance_vertex()
            
            if u == -1:  # No more reachable vertices
                break
            
            # Mark as visited
            self.visited[u] = True
            
            if record_steps:
                self._record_step(u, -1, f"Selected {self._get_city_name(u)} (distance = {self.dist[u]:.2f} km)")
            
            # Update distances of adjacent vertices (relaxation)
            self._relax_neighbors(u, record_steps)
        
        # Convert to city ID-based arrays for return
        id_based_dist = self._convert_to_city_ids(self.dist)
        id_based_parent = self._convert_parent_to_city_ids(self.parent, source_idx)
        
        return id_based_dist, id_based_parent
    
    def _min_distance_vertex(self) -> int:
        """
        Find vertex with minimum distance among unvisited vertices
        
        Returns:
            Index of vertex with minimum distance, or -1 if none found
        """
        min_dist = float('inf')
        min_vertex = -1
        
        for v in range(self.V):
            if not self.visited[v] and self.dist[v] < min_dist:
                min_dist = self.dist[v]
                min_vertex = v
        
        return min_vertex
    
    def _relax_neighbors(self, u: int, record_steps: bool = False):
        """
        Relax all neighbors of vertex u
        
        Args:
            u: Vertex index
            record_steps: Whether to record steps
        """
        matrix = self.network.get_adjacency_matrix()
        
        for v in range(self.V):
            # Check if v is neighbor of u and not visited
            if not self.visited[v] and matrix[u][v] != float('inf'):
                # Apply weight function if provided, otherwise use matrix distance
                if self._weight_func:
                    # Resolve city IDs from indices to get the road object
                    idx_to_city = {idx: cid for cid, idx in self.network.city_indices.items()}
                    city_u = idx_to_city.get(u)
                    city_v = idx_to_city.get(v)
                    road = self.network.get_road_between(city_u, city_v) if city_u and city_v else None
                    edge_weight = self._weight_func(road) if road else matrix[u][v]
                else:
                    edge_weight = matrix[u][v]

                # Calculate new distance
                new_dist = self.dist[u] + edge_weight
                
                # If new distance is shorter, update
                if new_dist < self.dist[v]:
                    old_dist = self.dist[v]
                    self.dist[v] = new_dist
                    self.parent[v] = u
                    
                    if record_steps:
                        self._record_step(
                            v, u,
                            f"Relaxed {self._get_city_name(u)} → {self._get_city_name(v)}: "
                            f"{old_dist if old_dist != float('inf') else '∞'} → {new_dist:.2f}"
                        )
    
    def _record_step(self, vertex: int, parent_vertex: int, description: str):
        """
        Record a step for demonstration
        
        Args:
            vertex: Current vertex
            parent_vertex: Parent vertex
            description: Step description
        """
        # Create a snapshot of current state
        dist_snapshot = self.dist.copy()
        visited_snapshot = self.visited.copy()
        parent_snapshot = self.parent.copy()
        
        self.step_records.append({
            'step': len(self.step_records) + 1,
            'vertex': vertex,
            'parent': parent_vertex,
            'description': description,
            'dist': dist_snapshot,
            'visited': visited_snapshot,
            'parent_array': parent_snapshot
        })
    
    def _get_city_name(self, idx: int) -> str:
        """Get Ethiopian city name from index"""
        for city_id, city_idx in self.network.city_indices.items():
            if city_idx == idx:
                city = self.network.get_city_by_id(city_id)
                return city.name if city else f"City_{city_id}"
        return f"City_{idx}"
    
    def _convert_to_city_ids(self, array: List[float]) -> Dict[int, float]:
        """Convert index-based array to city ID-based dictionary"""
        # Create mapping from index to city ID
        idx_to_city = {idx: city_id for city_id, idx in self.network.city_indices.items()}
        
        # Create result dictionary with city IDs as keys
        result = {}
        for idx, value in enumerate(array):
            city_id = idx_to_city.get(idx)
            if city_id is not None:
                result[city_id] = value
        
        return result
    
    def _convert_parent_to_city_ids(self, parent_array: List[int], source_idx: int) -> Dict[int, int]:
        """Convert parent array to city ID-based dictionary"""
        # Create mapping from index to city ID
        idx_to_city = {idx: city_id for city_id, idx in self.network.city_indices.items()}
        
        # Create result dictionary
        result = {}
        for idx, parent_idx in enumerate(parent_array):
            city_id = idx_to_city.get(idx)
            if city_id is not None:
                if parent_idx != -1:
                    parent_city_id = idx_to_city.get(parent_idx)
                    result[city_id] = parent_city_id
                else:
                    result[city_id] = -1
        
        return result
    
    def get_shortest_path_to(self, dest_city_id: int,
                            distances: Dict[int, float],
                            parents: Dict[int, int]) -> Tuple[float, List[int]]:
        """
        Get shortest path to a specific Ethiopian city
        
        Args:
            dest_city_id: Destination Ethiopian city ID
            distances: Distances dictionary from find_shortest_paths
            parents: Parents dictionary from find_shortest_paths
            
        Returns:
            Tuple of (distance, list of city IDs in path)
        """
        if dest_city_id not in distances:
            raise ValueError(f"Destination city ID {dest_city_id} not found")
        
        if distances[dest_city_id] == float('inf'):
            return float('inf'), []
        
        # Reconstruct path
        path = []
        current = dest_city_id
        
        while current != -1:
            path.append(current)
            current = parents.get(current, -1)
        
        path.reverse()  # Reverse to get path from source to destination
        
        return distances[dest_city_id], path
    
    def print_step_by_step(self):
        """Print recorded steps for demonstration with Ethiopian cities"""
        if not self.step_records:
            print("No steps recorded. Run with record_steps=True first.")
            return
        
        print("\n" + "="*80)
        print("STEP-BY-STEP DIJKSTRA EXECUTION FOR ETHIOPIAN ROAD NETWORK")
        print("="*80)
        
        for record in self.step_records:
            print(f"\n📌 Step {record['step']}: {record['description']}")
            
            # Print current distances for all cities
            print("\n   Current distances:")
            print("   " + "-"*60)
            
            # Get cities in order of distance
            cities_with_dist = []
            for city_id, city_idx in self.network.city_indices.items():
                city = self.network.get_city_by_id(city_id)
                dist_val = record['dist'][city_idx]
                visited_mark = "✓" if record['visited'][city_idx] else " "
                cities_with_dist.append((city.name, dist_val, visited_mark))
            
            # Sort by distance for better readability
            cities_with_dist.sort(key=lambda x: (x[1] if x[1] != float('inf') else float('inf'), x[0]))
            
            for city_name, dist_val, visited_mark in cities_with_dist[:10]:  # Show first 10
                if dist_val == float('inf'):
                    print(f"     {city_name}[{visited_mark}]: ∞")
                else:
                    print(f"     {city_name}[{visited_mark}]: {dist_val:.2f} km")
            
            if len(cities_with_dist) > 10:
                print(f"     ... and {len(cities_with_dist) - 10} more cities")
            
            if record['step'] < len(self.step_records):
                input("\n   Press Enter to continue...")


# Example usage with Ethiopian cities
if __name__ == "__main__":
    from src.graph.network import RoadNetwork
    
    # Create a small Ethiopian test network
    print("="*80)
    print("TESTING DIJKSTRA ARRAY IMPLEMENTATION WITH ETHIOPIAN CITIES")
    print("="*80)
    
    network = RoadNetwork()
    network.generate_ethiopian_network(num_cities=10, num_roads=15)
    
    print("\n📊 Test Network Created:")
    network.print_network_summary()
    
    # Get first city as source (preferably Addis Ababa if it exists)
    source_city = None
    for city in network.cities.values():
        if city.name == "Addis Ababa" or city.is_capital:
            source_city = city
            break
    
    if not source_city:
        source_city = list(network.cities.values())[0]
    
    print(f"\n📍 Source City: {source_city.name} (ID: {source_city.id})")
    
    # Run Dijkstra with step recording
    dijkstra = DijkstraArray(network)
    distances, parents = dijkstra.find_shortest_paths(source_city.id, record_steps=True)
    
    # Print step-by-step execution
    dijkstra.print_step_by_step()
    
    # Print final results
    print("\n📊 FINAL SHORTEST PATHS FROM", source_city.name)
    print("-" * 60)
    
    # Sort destinations by distance
    destinations = [(city_id, dist) for city_id, dist in distances.items() 
                   if city_id != source_city.id and dist != float('inf')]
    destinations.sort(key=lambda x: x[1])
    
    for city_id, distance in destinations[:8]:  # Show first 8
        city = network.get_city_by_id(city_id)
        _, path = dijkstra.get_shortest_path_to(city_id, distances, parents)
        path_names = [network.get_city_by_id(cid).name for cid in path]
        print(f"\n{city.name}: {distance:.2f} km")
        print(f"   Path: {' → '.join(path_names)}")