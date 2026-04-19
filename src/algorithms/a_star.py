"""
A* Search Algorithm implementation (O((V+E) log V))
For comparison with Dijkstra on Ethiopian road networks.
Uses geographic coordinates for heuristic guidance.
"""

import sys
import os
import heapq
from typing import List, Tuple, Dict, Optional
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.network import RoadNetwork
from src.graph.city import City
from src.utils.distance_calc import DistanceCalculator

class AStarSearch:
    """
    A* Search Algorithm implementation using Priority Queue (Heap)
    Time Complexity: O((V+E) log V) in worst case, but practically much faster than Dijkstra
    Space Complexity: O(V)
    
    This implementation uses Haversine distance as an admissible heuristic.
    """
    
    def __init__(self, network: RoadNetwork):
        """
        Initialize A* algorithm with an Ethiopian road network
        
        Args:
            network: RoadNetwork object containing Ethiopian cities and roads
        """
        self.network = network
        self.V = network.get_city_count()
        self.operation_count = 0  # For complexity analysis
        
    def _heuristic(self, curr_city_id: int, dest_city_id: int) -> float:
        """
        Calculate heuristic function h(n)
        Uses straight-line Haversine distance from current city to destination city.
        Since straight-line distance is always <= actual road distance, this is an admissible heuristic.
        """
        curr_city = self.network.get_city_by_id(curr_city_id)
        dest_city = self.network.get_city_by_id(dest_city_id)
        
        if not curr_city or not dest_city:
            return float('inf')
            
        return DistanceCalculator.haversine(
            curr_city.latitude, curr_city.longitude,
            dest_city.latitude, dest_city.longitude
        )
        
    def find_shortest_path_to(self, source_city_id: int, dest_city_id: int, weight_func=None) -> Tuple[float, List[int]]:
        """
        Find shortest path between two specific Ethiopian cities using A*
        
        Args:
            source_city_id: Source Ethiopian city ID
            dest_city_id: Destination Ethiopian city ID
            weight_func: Optional function to calculate weight of edge (default is distance)
            
        Returns:
            Tuple of (actual shortest distance, list of city IDs in path)
        """
        self.operation_count = 0
        
        # g_score: actual distance from source to a node
        g_scores = {city_id: float('inf') for city_id in self.network.cities.keys()}
        parents = {city_id: -1 for city_id in self.network.cities.keys()}
        
        g_scores[source_city_id] = 0
        
        # Priority queue stores (f_score, city_id)
        # f_score = g_score + h_score
        start_f_score = self._heuristic(source_city_id, dest_city_id)
        pq = [(start_f_score, source_city_id)]
        
        visited = set()
        
        while pq:
            # Get vertex with minimum f_score
            current_f, current_id = heapq.heappop(pq)
            self.operation_count += 1
            
            # Early termination if we reached destination
            if current_id == dest_city_id:
                break
            
            # Since a node might be pushed multiple times with different f_scores before being visited
            if current_id in visited:
                continue
                
            visited.add(current_id)
            
            # Explore neighbors
            current_g = g_scores[current_id]
            
            for neighbor_id, distance, road in self.network.get_neighbors(current_id):
                self.operation_count += 1
                
                if weight_func and road:
                    edge_val = weight_func(road)
                else:
                    edge_val = distance
                
                if neighbor_id in visited:
                    continue
                    
                tentative_g = current_g + edge_val
                
                if tentative_g < g_scores[neighbor_id]:
                    # This path to neighbor is better than any previous one
                    parents[neighbor_id] = current_id
                    g_scores[neighbor_id] = tentative_g
                    
                    # Calculate new f_score and push to queue
                    f_score = tentative_g + self._heuristic(neighbor_id, dest_city_id)
                    heapq.heappush(pq, (f_score, neighbor_id))
                    
        # Reconstruct path
        if g_scores[dest_city_id] == float('inf'):
            return float('inf'), []
            
        path = []
        current = dest_city_id
        while current != -1:
            path.append(current)
            current = parents[current]
            
        path.reverse()
        
        return g_scores[dest_city_id], path

    def get_operation_count(self) -> int:
        """Get number of operations performed in last run"""
        return self.operation_count

# Example usage
if __name__ == "__main__":
    import time
    from src.algorithms.dijkstra_pq import DijkstraPriorityQueue
    
    print("="*80)
    print("COMPARING A* VS DIJKSTRA ON ETHIOPIAN ROAD NETWORK")
    print("="*80)
    
    # Create Ethiopian road network
    network = RoadNetwork()
    network.generate_ethiopian_network(num_cities=200, num_roads=400)
    
    cities = list(network.cities.values())
    source_city = cities[0]
    dest_city = cities[-1]
    
    print(f"Network: {network.get_city_count()} cities, {network.get_road_count()} roads")
    print(f"Routing from {source_city.name} to {dest_city.name}")
    
    # Dijkstra
    dijkstra = DijkstraPriorityQueue(network)
    start_time = time.time()
    d_dist, d_path = dijkstra.find_shortest_path_to(source_city.id, dest_city.id)
    dijkstra_time = time.time() - start_time
    
    # A*
    a_star = AStarSearch(network)
    
    # Test shortest distance flag
    start_time = time.time()
    a_dist, a_path = a_star.find_shortest_path_to(source_city.id, dest_city.id)
    astar_time = time.time() - start_time
    
    # Test fastest route flag
    a_dist_time, a_path_time = a_star.find_shortest_path_to(source_city.id, dest_city.id, weight_func=lambda road: road.get_travel_time())
    
    print("\nResults:")
    print(f"Dijkstra:")
    print(f"  Distance  : {d_dist:.2f} km")
    print(f"  Operations: {dijkstra.get_operation_count()}")
    print(f"  Time      : {dijkstra_time*1000:.2f} ms")
    
    print(f"\nA* Search (Shortest Distance):")
    print(f"  Distance  : {a_dist:.2f} km")
    print(f"  Operations: {a_star.get_operation_count()}")
    print(f"  Time      : {astar_time*1000:.2f} ms")
    
    print(f"\nA* Search (Fastest Time):")
    print(f"  Travel Time: {a_dist_time:.2f} hours")
    print(f"  Path matches shortest? {a_path == a_path_time}")
    
    if d_path == a_path:
        print("\n✅ Both found the exact same path!")
    elif abs(d_dist - a_dist) < 0.01:
        print("\n✅ Both found paths of the identical optimal length!")
    else:
        print("\n⚠️ Divergence found.")
