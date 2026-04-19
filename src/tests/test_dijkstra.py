"""
Unit tests for Algorithms module (Dijkstra's algorithm implementations)
Tests shortest path finding on Ethiopian road networks
"""

import sys
import os
import unittest
import math
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.network import RoadNetwork
from src.graph.city import City
from src.graph.road import Road, RoadType
from src.algorithms.dijkstra_array import DijkstraArray
from src.algorithms.dijkstra_pq import DijkstraPriorityQueue
from src.algorithms.path_utils import PathUtils


class TestDijkstraArray(unittest.TestCase):
    """Test cases for array-based Dijkstra implementation"""
    
    def setUp(self):
        """Set up test fixtures with a small Ethiopian road network"""
        self.network = RoadNetwork()
        
        # Create Ethiopian cities
        self.addis = City(1, "Addis Ababa", "Addis Ababa", 9.03, 38.74)
        self.adama = City(2, "Adama", "Oromia", 8.54, 39.27)
        self.bahir = City(3, "Bahir Dar", "Amhara", 11.60, 37.38)
        self.gondar = City(4, "Gondar", "Amhara", 12.60, 37.47)
        self.mekelle = City(5, "Mekelle", "Tigray", 13.50, 39.47)
        
        for city in [self.addis, self.adama, self.bahir, self.gondar, self.mekelle]:
            self.network.add_city(city)
        
        # Add roads (realistic Ethiopian distances)
        roads = [
            Road(101, 1, 2, 85, RoadType.HIGHWAY),    # Addis - Adama
            Road(102, 1, 3, 380, RoadType.HIGHWAY),   # Addis - Bahir Dar
            Road(103, 2, 3, 380, RoadType.HIGHWAY),   # Adama - Bahir Dar
            Road(104, 3, 4, 180, RoadType.HIGHWAY),   # Bahir Dar - Gondar
            Road(105, 4, 5, 380, RoadType.HIGHWAY),   # Gondar - Mekelle
            Road(106, 1, 5, 783, RoadType.HIGHWAY),   # Addis - Mekelle (direct)
        ]
        
        for road in roads:
            self.network.add_road(road)
        
        self.dijkstra = DijkstraArray(self.network)
    
    def test_shortest_paths_from_addis(self):
        """Test shortest paths from Addis Ababa to all cities"""
        distances, parents = self.dijkstra.find_shortest_paths(1)
        
        # Check distances
        self.assertAlmostEqual(distances[1], 0)  # Self
        self.assertAlmostEqual(distances[2], 85)  # Addis to Adama
        self.assertAlmostEqual(distances[3], 380)  # Addis to Bahir Dar
        self.assertAlmostEqual(distances[4], 560)  # Addis to Gondar (380+180)
        self.assertAlmostEqual(distances[5], 783)  # Addis to Mekelle (direct)
        
        # Check paths
        # Addis -> Adama
        self.assertEqual(parents[2], 1)
        
        # Addis -> Bahir Dar (direct)
        self.assertEqual(parents[3], 1)
        
        # Addis -> Gondar (through Bahir Dar)
        self.assertEqual(parents[4], 3)
        
        # Addis -> Mekelle (direct)
        self.assertEqual(parents[5], 1)
    
    def test_shortest_paths_from_mekelle(self):
        """Test shortest paths from Mekelle to all cities"""
        distances, parents = self.dijkstra.find_shortest_paths(5)
        
        # Check distances
        self.assertAlmostEqual(distances[5], 0)
        self.assertAlmostEqual(distances[4], 380)  # Mekelle to Gondar
        self.assertAlmostEqual(distances[3], 560)  # Mekelle to Bahir Dar (380+180)
        self.assertAlmostEqual(distances[1], 783)  # Mekelle to Addis (direct)
        self.assertAlmostEqual(distances[2], 868)  # Mekelle to Adama (783+85)
    
    def test_path_reconstruction(self):
        """Test path reconstruction functionality"""
        distances, parents = self.dijkstra.find_shortest_paths(1)
        
        # Reconstruct path to Gondar
        path_utils = PathUtils(self.network)
        path_ids = path_utils.reconstruct_path(parents, 1, 4)
        
        self.assertEqual(len(path_ids), 3)
        self.assertEqual(path_ids[0], 1)  # Addis
        self.assertEqual(path_ids[1], 3)  # Bahir Dar
        self.assertEqual(path_ids[2], 4)  # Gondar
        
        # Reconstruct path to Adama
        path_ids = path_utils.reconstruct_path(parents, 1, 2)
        self.assertEqual(len(path_ids), 2)
        self.assertEqual(path_ids[0], 1)
        self.assertEqual(path_ids[1], 2)
    
    def test_unreachable_city(self):
        """Test handling of unreachable cities"""
        # Add isolated city
        isolated = City(6, "Isolated", "Unknown", 0, 0)
        self.network.add_city(isolated)
        
        distances, parents = self.dijkstra.find_shortest_paths(1)
        
        self.assertEqual(distances[6], float('inf'))
        self.assertEqual(parents[6], -1)
    
    def test_step_recording(self):
        """Test step-by-step recording functionality"""
        distances, parents = self.dijkstra.find_shortest_paths(1, record_steps=True)
        
        self.assertTrue(len(self.dijkstra.step_records) > 0)
        
        # Check first step
        first_step = self.dijkstra.step_records[0]
        self.assertEqual(first_step['step'], 1)
        self.assertIn('dist' in first_step, True)


class TestDijkstraPriorityQueue(unittest.TestCase):
    """Test cases for priority queue-based Dijkstra implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.network = RoadNetwork()
        
        # Create simple test network
        for i in range(1, 6):
            city = City(i, f"City_{i}", "Test", i*10, i*10)
            self.network.add_city(city)
        
        # Add edges to create a simple graph
        edges = [
            (1, 2, 10),
            (1, 3, 15),
            (2, 4, 12),
            (3, 4, 10),
            (4, 5, 5)
        ]
        
        road_id = 1
        for u, v, dist in edges:
            self.network.add_road(Road(road_id, u, v, dist))
            road_id += 1
        
        self.dijkstra = DijkstraPriorityQueue(self.network)
    
    def test_shortest_paths(self):
        """Test finding shortest paths"""
        distances, parents = self.dijkstra.find_shortest_paths(1)
        
        self.assertEqual(distances[1], 0)
        self.assertEqual(distances[2], 10)
        self.assertEqual(distances[3], 15)
        self.assertEqual(distances[4], 22)  # 10+12 or 15+10 = 25, so min is 22
        self.assertEqual(distances[5], 27)  # 22+5
    
    def test_point_to_point(self):
        """Test point-to-point shortest path"""
        distance, path = self.dijkstra.find_shortest_path_to(1, 5)
        
        self.assertEqual(distance, 27)
        self.assertEqual(path, [1, 2, 4, 5])
    
    def test_k_shortest_paths(self):
        """Test finding k shortest paths"""
        paths = self.dijkstra.find_k_shortest_paths(1, 5, k=2)
        
        self.assertTrue(len(paths) >= 1)
        self.assertEqual(paths[0][0], 27)  # Shortest path distance
    
    def test_operation_count(self):
        """Test operation counting for complexity analysis"""
        self.dijkstra.find_shortest_paths(1)
        ops = self.dijkstra.get_operation_count()
        
        self.assertTrue(ops > 0)
        self.assertIsInstance(ops, int)


class TestDijkstraComparison(unittest.TestCase):
    """Test cases comparing both implementations"""
    
    def setUp(self):
        """Set up test network for comparison"""
        self.network = RoadNetwork()
        self.network.generate_ethiopian_network(num_cities=20, num_roads=30)
        self.source_id = next(iter(self.network.cities.keys()))
        
        self.array_dijkstra = DijkstraArray(self.network)
        self.pq_dijkstra = DijkstraPriorityQueue(self.network)
    
    def test_implementations_agree(self):
        """Test that both implementations produce same results"""
        array_dist, array_parents = self.array_dijkstra.find_shortest_paths(self.source_id)
        pq_dist, pq_parents = self.pq_dijkstra.find_shortest_paths(self.source_id)
        
        # Compare distances
        for city_id in array_dist:
            if city_id in pq_dist:
                if array_dist[city_id] == float('inf') and pq_dist[city_id] == float('inf'):
                    continue
                self.assertAlmostEqual(array_dist[city_id], pq_dist[city_id], places=5)
        
        # Use comparison method
        comparison = DijkstraPriorityQueue.compare_with_array(array_dist, pq_dist)
        
        for city_id, (a_dist, pq_dist, match) in comparison.items():
            if a_dist != float('inf') or pq_dist != float('inf'):
                self.assertTrue(match)
    
    def test_path_consistency(self):
        """Test that paths are consistent between implementations"""
        array_dist, array_parents = self.array_dijkstra.find_shortest_paths(self.source_id)
        pq_dist, pq_parents = self.pq_dijkstra.find_shortest_paths(self.source_id)
        
        path_utils = PathUtils(self.network)
        
        # Test a few destinations
        destinations = list(self.network.cities.keys())[:3]
        
        for dest_id in destinations:
            if dest_id != self.source_id:
                array_path = path_utils.reconstruct_path(array_parents, self.source_id, dest_id)
                pq_path = path_utils.reconstruct_path(pq_parents, self.source_id, dest_id)
                
                # Both paths should exist or both not exist
                self.assertEqual(len(array_path) > 0, len(pq_path) > 0)
                
                if array_path and pq_path:
                    # Paths should be the same length
                    self.assertEqual(len(array_path), len(pq_path))


class TestPathUtils(unittest.TestCase):
    """Test cases for PathUtils class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.network = RoadNetwork()
        
        # Create simple path: 1-2-3-4
        for i in range(1, 5):
            city = City(i, f"City_{i}", "Test", i, i)
            self.network.add_city(city)
        
        roads = [
            Road(1, 1, 2, 50),
            Road(2, 2, 3, 60),
            Road(3, 3, 4, 70)
        ]
        
        for road in roads:
            self.network.add_road(road)
        
        self.path_utils = PathUtils(self.network)
        self.parents = {2: 1, 3: 2, 4: 3}
    
    def test_reconstruct_path(self):
        """Test path reconstruction"""
        path = self.path_utils.reconstruct_path(self.parents, 1, 4)
        self.assertEqual(path, [1, 2, 3, 4])
        
        path = self.path_utils.reconstruct_path(self.parents, 1, 2)
        self.assertEqual(path, [1, 2])
        
        # Invalid destination
        path = self.path_utils.reconstruct_path(self.parents, 1, 5)
        self.assertEqual(path, [])
    
    def test_get_path_string(self):
        """Test path string formatting"""
        path = [1, 2, 3, 4]
        
        # Without distances
        path_str = self.path_utils.get_path_string(path)
        self.assertIsInstance(path_str, str)
        self.assertIn("City_1", path_str)
        self.assertIn("City_4", path_str)
        
        # With distances
        path_str = self.path_utils.get_path_string(path, include_distances=True)
        self.assertIn("50km", path_str)
        self.assertIn("60km", path_str)
        self.assertIn("70km", path_str)
        
        # With regions
        path_str = self.path_utils.get_path_string(path, include_regions=True)
        self.assertIn("Test", path_str)
    
    def test_path_statistics(self):
        """Test path statistics calculation"""
        path = [1, 2, 3, 4]
        stats = self.path_utils.calculate_path_statistics(path)
        
        self.assertEqual(stats['num_cities'], 4)
        self.assertEqual(stats['num_segments'], 3)
        self.assertEqual(stats['total_distance'], 180)  # 50+60+70
        self.assertEqual(stats['avg_segment_distance'], 60)
        self.assertEqual(stats['max_segment_distance'], 70)
        self.assertEqual(stats['min_segment_distance'], 50)
    
    def test_path_details(self):
        """Test detailed path information"""
        path = [1, 2, 3, 4]
        details = self.path_utils.get_path_details(path)
        
        self.assertTrue(details['valid'])
        self.assertEqual(details['num_cities'], 4)
        self.assertEqual(details['total_distance'], 180)
        self.assertEqual(len(details['segments']), 3)
        self.assertEqual(len(details['cities']), 4)
    
    def test_export_to_geojson(self):
        """Test GeoJSON export"""
        path = [1, 2, 3, 4]
        geojson = self.path_utils.export_path_to_geojson(path)
        
        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertTrue(len(geojson['features']) > 0)
        
        # Should have both points and lines
        feature_types = [f['geometry']['type'] for f in geojson['features']]
        self.assertIn('Point', feature_types)
        self.assertIn('LineString', feature_types)
    
    def test_format_path_table(self):
        """Test path table formatting"""
        distances = {1: 0, 2: 50, 3: 110, 4: 180}
        parents = {2: 1, 3: 2, 4: 3}
        
        table = self.path_utils.format_path_table(1, distances, parents, max_cities=3)
        
        self.assertIsInstance(table, str)
        self.assertIn("City_2", table)
        self.assertIn("50.00", table)
        self.assertIn("City_4", table)
        self.assertIn("180.00", table)


if __name__ == '__main__':
    unittest.main(verbosity=2)