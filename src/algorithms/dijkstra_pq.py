"""
Dijkstra's Algorithm implementation using Priority Queue (O((V+E) log V))
For comparison with array implementation on Ethiopian road networks
"""

import sys
import os
import heapq
from typing import List, Tuple, Dict, Optional
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.network import RoadNetwork
from src.graph.city import City


class DijkstraPriorityQueue:
    """
    Dijkstra's Algorithm implementation using Priority Queue (Heap)
    Time Complexity: O((V+E) log V) where V is vertices, E is edges
    Space Complexity: O(V)
    
    This implementation is more efficient for sparse graphs like road networks
    """
    
    def __init__(self, network: RoadNetwork):
        """
        Initialize Dijkstra's algorithm with an Ethiopian road network
        
        Args:
            network: RoadNetwork object containing Ethiopian cities and roads
        """
        self.network = network
        self.V = network.get_city_count()
        self.operation_count = 0  # For complexity analysis
        
    def find_shortest_paths(self, source_city_id: int, weight_func=None) -> Tuple[Dict[int, float], Dict[int, int]]:
        """
        Find shortest paths from source Ethiopian city to all cities using priority queue
        
        Args:
            source_city_id: ID of source Ethiopian city
            weight_func: Optional function to calculate weight of edge (default is distance)
            
        Returns:
            Tuple of (distances dictionary, parents dictionary)
        """
        self.operation_count = 0
        
        # Initialize distances and parents
        distances = {city_id: float('inf') for city_id in self.network.cities.keys()}
        parents = {city_id: -1 for city_id in self.network.cities.keys()}
        
        # Distance to source is 0
        distances[source_city_id] = 0
        
        # Priority queue: (distance, city_id)
        pq = [(0, source_city_id)]
        visited = set()
        
        while pq:
            # Get vertex with minimum distance (log V operation)
            current_dist, current_id = heapq.heappop(pq)
            self.operation_count += 1
            
            # Skip if already visited
            if current_id in visited:
                continue
            
            # Mark as visited
            visited.add(current_id)
            
            # Get all neighbors
            neighbors = self.network.get_neighbors(current_id)
            
            for neighbor_id, distance, road in neighbors:
                self.operation_count += 1
                
                # Apply weight function if provided
                if weight_func and road:
                    edge_val = weight_func(road)
                else:
                    edge_val = distance
                    
                if neighbor_id not in visited:
                    new_dist = current_dist + edge_val
                    
                    # If new distance is shorter, update
                    if new_dist < distances[neighbor_id]:
                        distances[neighbor_id] = new_dist
                        parents[neighbor_id] = current_id
                        heapq.heappush(pq, (new_dist, neighbor_id))  # log V operation
                        self.operation_count += 1
        
        return distances, parents
    
    def find_shortest_path_to(self, source_city_id: int, dest_city_id: int, weight_func=None) -> Tuple[float, List[int]]:
        """
        Find shortest path between two specific Ethiopian cities
        Optimized version that stops early when destination is reached
        
        Args:
            source_city_id: Source Ethiopian city ID
            dest_city_id: Destination Ethiopian city ID
            weight_func: Optional function to calculate weight of edge (default is distance)
            
        Returns:
            Tuple of (distance, list of city IDs in path)
        """
        # Initialize
        distances = {city_id: float('inf') for city_id in self.network.cities.keys()}
        parents = {city_id: -1 for city_id in self.network.cities.keys()}
        
        distances[source_city_id] = 0
        pq = [(0, source_city_id)]
        visited = set()
        
        while pq:
            current_dist, current_id = heapq.heappop(pq)
            
            # Early termination if we reached destination
            if current_id == dest_city_id:
                break
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            for neighbor_id, distance, road in self.network.get_neighbors(current_id):
                
                if weight_func and road:
                    edge_val = weight_func(road)
                else:
                    edge_val = distance
                    
                if neighbor_id not in visited:
                    new_dist = current_dist + edge_val
                    
                    if new_dist < distances[neighbor_id]:
                        distances[neighbor_id] = new_dist
                        parents[neighbor_id] = current_id
                        heapq.heappush(pq, (new_dist, neighbor_id))
        
        # Reconstruct path
        if distances[dest_city_id] == float('inf'):
            return float('inf'), []
        
        path = []
        current = dest_city_id
        while current != -1:
            path.append(current)
            current = parents[current]
        
        path.reverse()
        
        return distances[dest_city_id], path
    
    def find_k_shortest_paths(self, source_city_id: int, dest_city_id: int, k: int = 3) -> List[Tuple[float, List[int]]]:
        """
        Find k shortest paths between two Ethiopian cities using Yen's algorithm.

        Yen's algorithm works by:
          1. Finding the shortest path (spur paths from each node).
          2. Iteratively finding the next shortest by temporarily removing edges/nodes
             that were part of previous paths and computing spur paths.

        Args:
            source_city_id: Source Ethiopian city ID
            dest_city_id: Destination Ethiopian city ID
            k: Number of shortest paths to find

        Returns:
            List of (distance, path) tuples, sorted by distance ascending
        """
        import heapq as _heapq

        # A* shortest path helper that respects removed edges/nodes
        def _dijkstra_with_restrictions(
            src: int,
            dst: int,
            removed_edges: set,
            removed_nodes: set,
        ) -> Tuple[float, List[int]]:
            dist: Dict[int, float] = {cid: float('inf') for cid in self.network.cities}
            parent: Dict[int, int] = {cid: -1 for cid in self.network.cities}
            dist[src] = 0.0
            pq = [(0.0, src)]
            visited: set = set()

            while pq:
                d, u = _heapq.heappop(pq)
                if u == dst:
                    break
                if u in visited:
                    continue
                visited.add(u)

                for neighbor_id, distance, road in self.network.get_neighbors(u):
                    if neighbor_id in removed_nodes:
                        continue
                    if (u, neighbor_id) in removed_edges or (neighbor_id, u) in removed_edges:
                        continue
                    new_d = d + distance
                    if new_d < dist[neighbor_id]:
                        dist[neighbor_id] = new_d
                        parent[neighbor_id] = u
                        _heapq.heappush(pq, (new_d, neighbor_id))

            if dist[dst] == float('inf'):
                return float('inf'), []

            path: List[int] = []
            cur = dst
            while cur != -1:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return dist[dst], path

        # Step 1: find the first (shortest) path
        first_dist, first_path = self.find_shortest_path_to(source_city_id, dest_city_id)
        if first_dist == float('inf'):
            return []

        # A_k: confirmed k-shortest paths
        A: List[Tuple[float, List[int]]] = [(first_dist, first_path)]
        # B: candidate heap (dist, path)
        B: List[Tuple[float, List[int]]] = []
        seen_candidates: set = set()

        for _ in range(k - 1):
            prev_dist, prev_path = A[-1]

            for i in range(len(prev_path) - 1):
                spur_node = prev_path[i]
                root_path = prev_path[:i + 1]

                removed_edges: set = set()
                removed_nodes: set = set()

                # Remove edges that are part of previous paths sharing the same root
                for dist_p, path_p in A:
                    if len(path_p) > i and path_p[:i + 1] == root_path:
                        u = path_p[i]
                        v = path_p[i + 1]
                        removed_edges.add((u, v))
                        removed_edges.add((v, u))

                # Remove root path nodes (except spur node) to avoid cycles
                for node in root_path[:-1]:
                    removed_nodes.add(node)

                spur_dist, spur_path = _dijkstra_with_restrictions(
                    spur_node, dest_city_id, removed_edges, removed_nodes
                )

                if spur_dist == float('inf') or not spur_path:
                    continue

                total_path = root_path[:-1] + spur_path
                # Compute total distance
                total_dist = 0.0
                for j in range(len(total_path) - 1):
                    road = self.network.get_road_between(total_path[j], total_path[j + 1])
                    total_dist += road.distance if road else 0.0

                path_key = tuple(total_path)
                if path_key not in seen_candidates:
                    seen_candidates.add(path_key)
                    _heapq.heappush(B, (total_dist, total_path))

            if not B:
                break

            next_dist, next_path = _heapq.heappop(B)
            A.append((next_dist, next_path))

        return A
    
    def get_operation_count(self) -> int:
        """Get number of operations performed in last run"""
        return self.operation_count
    
    @staticmethod
    def compare_with_array(array_distances: Dict[int, float],
                          pq_distances: Dict[int, float]) -> Dict[int, Tuple[float, float, bool]]:
        """
        Compare results from array and priority queue implementations
        
        Args:
            array_distances: Distances from array implementation
            pq_distances: Distances from priority queue implementation
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {}
        
        for city_id in array_distances.keys():
            array_dist = array_distances.get(city_id, float('inf'))
            pq_dist = pq_distances.get(city_id, float('inf'))
            
            # Check if they match (allowing for floating point differences)
            if array_dist == float('inf') and pq_dist == float('inf'):
                match = True
            elif array_dist == float('inf') or pq_dist == float('inf'):
                match = False
            else:
                match = abs(array_dist - pq_dist) < 0.0001
            
            comparison[city_id] = (array_dist, pq_dist, match)
        
        return comparison


# Example usage with Ethiopian cities
if __name__ == "__main__":
    from src.graph.network import RoadNetwork
    import time
    
    print("="*80)
    print("COMPARING ARRAY VS PRIORITY QUEUE ON ETHIOPIAN ROAD NETWORK")
    print("="*80)
    
    # Create Ethiopian road network
    network = RoadNetwork()
    network.generate_ethiopian_network(num_cities=50, num_roads=75)
    
    # Get Addis Ababa as source (or first city)
    source_city = None
    for city in network.cities.values():
        if city.name == "Addis Ababa" or city.is_capital:
            source_city = city
            break
    
    if not source_city:
        source_city = list(network.cities.values())[0]
    
    print(f"\n📍 Source City: {source_city.name} (ID: {source_city.id})")
    
    # Test array implementation
    from src.algorithms.dijkstra_array import DijkstraArray
    array_dijkstra = DijkstraArray(network)
    
    print("\n⏱️  Running Array Implementation (O(V²))...")
    start_time = time.time()
    array_distances, array_parents = array_dijkstra.find_shortest_paths(source_city.id)
    array_time = time.time() - start_time
    print(f"   Completed in {array_time*1000:.2f} ms")
    
    # Test priority queue implementation
    pq_dijkstra = DijkstraPriorityQueue(network)
    
    print("\n⏱️  Running Priority Queue Implementation (O((V+E) log V))...")
    start_time = time.time()
    pq_distances, pq_parents = pq_dijkstra.find_shortest_paths(source_city.id)
    pq_time = time.time() - start_time
    print(f"   Completed in {pq_time*1000:.2f} ms")
    print(f"   Operations: {pq_dijkstra.get_operation_count()}")
    
    # Performance comparison
    print(f"\n📊 PERFORMANCE COMPARISON:")
    print("-" * 50)
    print(f"Array Implementation: {array_time*1000:.2f} ms")
    print(f"Priority Queue: {pq_time*1000:.2f} ms")
    print(f"Speedup: {array_time/pq_time:.2f}x faster with Priority Queue")
    
    # Accuracy comparison
    comparison = DijkstraPriorityQueue.compare_with_array(array_distances, pq_distances)
    
    all_match = all(match for _, _, match in comparison.values())
    if all_match:
        print("\n✅ Both implementations produced identical results!")
    else:
        mismatches = sum(1 for _, _, match in comparison.values() if not match)
        print(f"\n⚠️  Found {mismatches} differences between implementations")
    
    # Test point-to-point query
    print("\n🎯 TESTING POINT-TO-POINT QUERIES:")
    print("-" * 50)
    
    # Get a few destination cities
    dest_cities = []
    for city in network.cities.values():
        if city.id != source_city.id:
            dest_cities.append(city)
            if len(dest_cities) >= 3:
                break
    
    for dest in dest_cities:
        distance, path = pq_dijkstra.find_shortest_path_to(source_city.id, dest.id)
        if distance != float('inf'):
            path_names = [network.get_city_by_id(cid).name for cid in path]
            print(f"\n{source_city.name} → {dest.name}: {distance:.2f} km")
            print(f"   Path: {' → '.join(path_names)}")
            