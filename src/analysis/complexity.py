"""
Complexity Analyzer - Time and Space complexity analysis for Dijkstra's algorithm
on Ethiopian road networks with detailed performance metrics
"""

import sys
import os
import time
import math
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import gc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.network import RoadNetwork
from src.algorithms.dijkstra_array import DijkstraArray
from src.algorithms.dijkstra_pq import DijkstraPriorityQueue


class ComplexityAnalyzer:
    """
    Analyzes time and space complexity of Dijkstra's algorithm implementations
    
    Features:
    - Theoretical complexity analysis (O(V²) vs O((V+E) log V))
    - Empirical performance measurement
    - Memory usage analysis
    - Scalability testing
    - Comparative analysis between implementations
    - Proof of correctness with invariants
    """
    
    def __init__(self, network: RoadNetwork):
        """
        Initialize complexity analyzer with Ethiopian road network
        
        Args:
            network: RoadNetwork object to analyze
        """
        self.network = network
        self.results = {
            'theoretical': {},
            'empirical': {},
            'memory': {},
            'scalability': {},
            'correctness': {}
        }
        
    def analyze_theoretical(self) -> Dict[str, Any]:
        """
        Analyze theoretical time and space complexity
        
        Returns:
            Dictionary with theoretical complexity analysis
        """
        V = self.network.get_city_count()
        E = self.network.get_road_count()
        
        analysis = {
            'vertices': V,
            'edges': E,
            'array_implementation': {
                'time_complexity': 'O(V²)',
                'time_expression': f'O({V}²)',
                'time_operations': V * V,
                'space_complexity': 'O(V)',
                'space_expression': f'O({V})',
                'space_bytes': V * 24,  # Approximate bytes per array element
                'description': 'Uses arrays for distance tracking. Simple but slower for sparse graphs.',
                'best_case': 'O(V²)',
                'worst_case': 'O(V²)',
                'average_case': 'O(V²)'
            },
            'pq_implementation': {
                'time_complexity': 'O((V+E) log V)',
                'time_expression': f'O(({V}+{E}) log {V})',
                'time_operations': int((V + E) * math.log2(V)) if V > 1 else 0,
                'space_complexity': 'O(V)',
                'space_expression': f'O({V})',
                'space_bytes': V * 32,  # Approximate bytes per heap element
                'description': 'Uses priority queue (heap). More efficient for sparse graphs.',
                'best_case': 'O((V+E) log V)',
                'worst_case': 'O((V+E) log V)',
                'average_case': 'O((V+E) log V)'
            },
            'comparison': {
                'speedup_theoretical': (V * V) / ((V + E) * math.log2(V)) if V > 1 and E > 0 else 0,
                'when_to_use_array': 'Dense graphs (E ≈ V²), small graphs, simple implementation needed',
                'when_to_use_pq': 'Sparse graphs (E << V²), large graphs, performance critical'
            }
        }
        
        # Calculate graph density
        max_edges = V * (V - 1) / 2 if V > 1 else 1
        analysis['graph_density'] = E / max_edges if max_edges > 0 else 0
        analysis['graph_type'] = 'dense' if analysis['graph_density'] > 0.5 else 'sparse'
        
        self.results['theoretical'] = analysis
        return analysis
    
    def analyze_empirical(self, num_runs: int = 5) -> Dict[str, Any]:
        """
        Empirically measure actual runtime performance
        
        Args:
            num_runs: Number of runs for averaging
            
        Returns:
            Dictionary with empirical performance data
        """
        if self.network.get_city_count() == 0:
            return {'error': 'Network is empty'}
        
        # Get source city (first city)
        source_id = next(iter(self.network.cities.keys()))
        
        # Initialize algorithms
        array_dijkstra = DijkstraArray(self.network)
        pq_dijkstra = DijkstraPriorityQueue(self.network)
        
        array_times = []
        pq_times = []
        array_ops = []
        pq_ops = []
        
        for run in range(num_runs):
            # Force garbage collection
            gc.collect()
            
            # Test array implementation
            start_time = time.perf_counter()
            distances, parents = array_dijkstra.find_shortest_paths(source_id)
            end_time = time.perf_counter()
            array_times.append((end_time - start_time) * 1000)  # Convert to ms
            
            # Test priority queue implementation
            start_time = time.perf_counter()
            distances, parents = pq_dijkstra.find_shortest_paths(source_id)
            end_time = time.perf_counter()
            pq_times.append((end_time - start_time) * 1000)  # Convert to ms
            
            # Get operation counts
            array_ops.append(array_dijkstra.V * array_dijkstra.V)  # Approximate
            pq_ops.append(pq_dijkstra.get_operation_count())
        
        # Calculate statistics
        empirical = {
            'num_runs': num_runs,
            'array_implementation': {
                'times_ms': array_times,
                'avg_time_ms': sum(array_times) / len(array_times),
                'min_time_ms': min(array_times),
                'max_time_ms': max(array_times),
                'std_dev_ms': self._std_dev(array_times),
                'avg_operations': sum(array_ops) / len(array_ops)
            },
            'pq_implementation': {
                'times_ms': pq_times,
                'avg_time_ms': sum(pq_times) / len(pq_times),
                'min_time_ms': min(pq_times),
                'max_time_ms': max(pq_times),
                'std_dev_ms': self._std_dev(pq_times),
                'avg_operations': sum(pq_ops) / len(pq_ops)
            },
            'comparison': {
                'speedup_empirical': (sum(array_times) / len(array_times)) / 
                                     (sum(pq_times) / len(pq_times)) if pq_times else 0,
                'array_vs_pq_ratio': f"{sum(array_times)/len(array_times):.2f}ms vs "
                                     f"{sum(pq_times)/len(pq_times):.2f}ms"
            }
        }
        
        self.results['empirical'] = empirical
        return empirical
    
    def analyze_memory(self) -> Dict[str, Any]:
        """
        Analyze memory usage of different implementations
        
        Returns:
            Dictionary with memory usage analysis
        """
        V = self.network.get_city_count()
        E = self.network.get_road_count()
        
        # Approximate memory calculations (in bytes)
        # Python objects have overhead, these are rough estimates
        
        # Graph memory (shared)
        graph_memory = {
            'adjacency_matrix': V * V * 8,  # 8 bytes per float
            'cities': V * 200,  # Approximate City object size
            'roads': E * 150,  # Approximate Road object size
            'indices': V * 16,  # Dictionary overhead
            'total_graph_mb': (V * V * 8 + V * 200 + E * 150) / (1024 * 1024)
        }
        
        # Array implementation memory
        array_memory = {
            'dist_array': V * 8,  # float array
            'visited_array': V,  # boolean array (1 byte each)
            'parent_array': V * 4,  # integer array
            'total_bytes': V * 8 + V + V * 4,
            'total_kb': (V * 8 + V + V * 4) / 1024
        }
        
        # Priority queue implementation memory
        pq_memory = {
            'dist_dict': V * 72,  # Python dict overhead
            'parent_dict': V * 72,
            'heap': E * 32,  # Heap elements
            'visited_set': V * 36,  # Set overhead
            'total_bytes': V * 72 * 2 + E * 32 + V * 36,
            'total_kb': (V * 72 * 2 + E * 32 + V * 36) / 1024
        }
        
        memory_analysis = {
            'graph': graph_memory,
            'array_implementation': array_memory,
            'pq_implementation': pq_memory,
            'comparison': {
                'array_vs_pq': f"{array_memory['total_kb']:.2f}KB vs {pq_memory['total_kb']:.2f}KB",
                'memory_efficiency': 'Array' if array_memory['total_kb'] < pq_memory['total_kb'] else 'Priority Queue',
                'difference_percent': abs(array_memory['total_kb'] - pq_memory['total_kb']) / 
                                     min(array_memory['total_kb'], pq_memory['total_kb']) * 100
            }
        }
        
        self.results['memory'] = memory_analysis
        return memory_analysis
    
    def analyze_scalability(self, sizes: List[int] = None) -> Dict[str, Any]:
        """
        Analyze how algorithms scale with increasing graph size
        
        Args:
            sizes: List of graph sizes to test (number of cities)
            
        Returns:
            Dictionary with scalability analysis
        """
        if sizes is None:
            sizes = [10, 20, 50, 100, 200]
        
        scalability = {
            'sizes': sizes,
            'array_times': [],
            'pq_times': [],
            'array_operations': [],
            'pq_operations': []
        }
        
        for size in sizes:
            # Create test network of given size
            from src.graph.network import RoadNetwork
            test_network = RoadNetwork()
            # Generate sparse graph (approx 2*size edges)
            test_network.generate_ethiopian_network(num_cities=size, num_roads=size*2)
            
            if test_network.get_city_count() == 0:
                continue
            
            source_id = next(iter(test_network.cities.keys()))
            
            # Test array implementation
            array_dijkstra = DijkstraArray(test_network)
            start_time = time.perf_counter()
            array_dijkstra.find_shortest_paths(source_id)
            array_time = (time.perf_counter() - start_time) * 1000
            scalability['array_times'].append(array_time)
            scalability['array_operations'].append(size * size)
            
            # Test PQ implementation
            pq_dijkstra = DijkstraPriorityQueue(test_network)
            start_time = time.perf_counter()
            pq_dijkstra.find_shortest_paths(source_id)
            pq_time = (time.perf_counter() - start_time) * 1000
            scalability['pq_times'].append(pq_time)
            scalability['pq_operations'].append(int((size + size*2) * math.log2(size)) if size > 1 else 0)
        
        # Calculate scaling factors
        if len(sizes) > 1:
            array_growth = [scalability['array_times'][i] / scalability['array_times'][i-1] 
                           for i in range(1, len(sizes))]
            pq_growth = [scalability['pq_times'][i] / scalability['pq_times'][i-1] 
                        for i in range(1, len(sizes))]
            
            scalability['scaling_factors'] = {
                'array_average_growth': sum(array_growth) / len(array_growth),
                'pq_average_growth': sum(pq_growth) / len(pq_growth)
            }
        
        self.results['scalability'] = scalability
        return scalability
    
    def prove_correctness(self) -> Dict[str, Any]:
        """
        Prove correctness of Dijkstra's algorithm using invariants
        
        Returns:
            Dictionary with correctness proof
        """
        correctness = {
            'invariants': [
                {
                    'name': 'Shortest Path Invariant',
                    'statement': 'When vertex u is marked as visited, dist[u] is the true shortest distance from source to u.',
                    'proof': 'Proof by induction on the number of visited vertices.'
                },
                {
                    'name': 'Relaxation Invariant',
                    'statement': 'For any edge (u,v), if dist[u] is correct and we relax the edge, dist[v] becomes the shortest path using only visited vertices.',
                    'proof': 'Follows from triangle inequality and non-negative weights.'
                },
                {
                    'name': 'Priority Invariant',
                    'statement': 'The unvisited vertex with minimum distance will always be selected next.',
                    'proof': 'All edge weights are non-negative, so any alternative path must be at least as long.'
                }
            ],
            'proof_steps': [
                '1. Base case: Source vertex has dist[source] = 0, which is trivially correct.',
                '2. Inductive hypothesis: Assume all previously visited vertices have correct distances.',
                '3. Let u be the next vertex selected (minimum dist among unvisited).',
                '4. Any alternative path to u must go through some unvisited vertex w.',
                '5. Since all edges are non-negative, dist[w] ≥ dist[u].',
                '6. Therefore, the alternative path would be at least dist[u] + positive weight > dist[u].',
                '7. Hence, dist[u] must be the shortest distance.',
                '8. After marking u as visited, we relax all edges from u, maintaining the invariant.'
            ],
            'requirements': [
                'All edge weights must be non-negative',
                'Graph must be finite',
                'Source vertex must exist',
                'Distances are additive'
            ],
            'optimality': 'Dijkstra\'s algorithm is optimal for graphs with non-negative weights. No algorithm can do better than O(E + V log V) in the worst case.',
            'limitations': [
                'Cannot handle negative edge weights',
                'Not suitable for graphs with negative cycles',
                'Requires storing all vertices in memory'
            ]
        }
        
        self.results['correctness'] = correctness
        return correctness
    
    def _std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive complexity analysis report
        
        Returns:
            Complete analysis dictionary
        """
        # Run all analyses
        self.analyze_theoretical()
        self.analyze_empirical()
        self.analyze_memory()
        self.analyze_scalability()
        self.prove_correctness()
        
        # Add summary
        V = self.network.get_city_count()
        E = self.network.get_road_count()
        
        self.results['summary'] = {
            'network_size': f"{V} cities, {E} roads",
            'density': self.results['theoretical'].get('graph_density', 0),
            'graph_type': self.results['theoretical'].get('graph_type', 'unknown'),
            'recommended_algorithm': 'Priority Queue' if self.results['theoretical'].get('graph_density', 1) < 0.5 else 'Array',
            'theoretical_speedup': self.results['theoretical'].get('comparison', {}).get('speedup_theoretical', 0),
            'empirical_speedup': self.results.get('empirical', {}).get('comparison', {}).get('speedup_empirical', 0)
        }
        
        return self.results
    
    def print_analysis(self):
        """Print formatted analysis results"""
        if not self.results['theoretical']:
            self.generate_comprehensive_report()
        
        print("\n" + "="*80)
        print("COMPLEXITY ANALYSIS FOR ETHIOPIAN ROAD NETWORK")
        print("="*80)
        
        V = self.network.get_city_count()
        E = self.network.get_road_count()
        
        print(f"\n📊 NETWORK STATISTICS:")
        print(f"   • Cities (V): {V}")
        print(f"   • Roads (E): {E}")
        print(f"   • Density: {self.results['theoretical'].get('graph_density', 0):.4f}")
        print(f"   • Graph Type: {self.results['theoretical'].get('graph_type', 'unknown').upper()}")
        
        print(f"\n⏱️  THEORETICAL COMPLEXITY:")
        print(f"   • Array Implementation: O(V²) = O({V}²) = {V*V:,} operations")
        print(f"   • Priority Queue: O((V+E) log V) = O(({V}+{E}) log {V}) = "
              f"{self.results['theoretical']['pq_implementation']['time_operations']:,} operations")
        print(f"   • Theoretical Speedup: {self.results['theoretical']['comparison']['speedup_theoretical']:.2f}x")
        
        if 'empirical' in self.results and self.results['empirical']:
            print(f"\n📈 EMPIRICAL PERFORMANCE:")
            emp = self.results['empirical']
            print(f"   • Array: {emp['array_implementation']['avg_time_ms']:.2f} ms avg "
                  f"(min={emp['array_implementation']['min_time_ms']:.2f}, "
                  f"max={emp['array_implementation']['max_time_ms']:.2f})")
            print(f"   • Priority Queue: {emp['pq_implementation']['avg_time_ms']:.2f} ms avg "
                  f"(min={emp['pq_implementation']['min_time_ms']:.2f}, "
                  f"max={emp['pq_implementation']['max_time_ms']:.2f})")
            print(f"   • Empirical Speedup: {emp['comparison']['speedup_empirical']:.2f}x")
        
        if 'memory' in self.results and self.results['memory']:
            print(f"\n💾 MEMORY USAGE:")
            mem = self.results['memory']
            print(f"   • Array: {mem['array_implementation']['total_kb']:.2f} KB")
            print(f"   • Priority Queue: {mem['pq_implementation']['total_kb']:.2f} KB")
            print(f"   • Graph: {mem['graph']['total_graph_mb']:.2f} MB")
        
        print(f"\n✅ PROOF OF CORRECTNESS:")
        for invariant in self.results['correctness']['invariants']:
            print(f"   • {invariant['name']}: {invariant['statement']}")


# Example usage
if __name__ == "__main__":
    from src.graph.network import RoadNetwork
    
    print("="*80)
    print("TESTING COMPLEXITY ANALYZER")
    print("="*80)
    
    # Create test network
    network = RoadNetwork()
    network.generate_ethiopian_network(num_cities=50, num_roads=75)
    
    # Create analyzer
    analyzer = ComplexityAnalyzer(network)
    
    # Run analysis
    analyzer.print_analysis()