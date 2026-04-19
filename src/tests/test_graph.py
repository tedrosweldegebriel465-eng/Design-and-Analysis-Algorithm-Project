"""
Unit tests for Graph module (City, Road, RoadNetwork classes)
Tests Ethiopian city and road network functionality
"""

import sys
import os
import unittest
import math
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.city import City
from src.graph.road import Road, RoadType, RoadCondition
from src.graph.network import RoadNetwork


class TestCity(unittest.TestCase):
    """Test cases for City class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.addis_ababa = City(
            id=1,
            name="Addis Ababa",
            region="Addis Ababa",
            latitude=9.03,
            longitude=38.74,
            population=3500000,
            elevation=2355,
            is_capital=True
        )
        
        self.bahir_dar = City(
            id=2,
            name="Bahir Dar",
            region="Amhara",
            latitude=11.60,
            longitude=37.38,
            population=350000,
            elevation=1800
        )
    
    def test_city_creation(self):
        """Test city object creation and attributes"""
        self.assertEqual(self.addis_ababa.id, 1)
        self.assertEqual(self.addis_ababa.name, "Addis Ababa")
        self.assertEqual(self.addis_ababa.region, "Addis Ababa")
        self.assertEqual(self.addis_ababa.latitude, 9.03)
        self.assertEqual(self.addis_ababa.longitude, 38.74)
        self.assertEqual(self.addis_ababa.population, 3500000)
        self.assertEqual(self.addis_ababa.elevation, 2355)
        self.assertTrue(self.addis_ababa.is_capital)
    
    def test_invalid_coordinates(self):
        """Test validation of invalid coordinates"""
        with self.assertRaises(ValueError):
            City(3, "Invalid", latitude=100, longitude=38.74)
        
        with self.assertRaises(ValueError):
            City(4, "Invalid", latitude=9.03, longitude=200)
    
    def test_distance_calculation(self):
        """Test distance calculation between cities"""
        # Haversine distance
        dist = self.addis_ababa.distance_to(self.bahir_dar)
        self.assertIsInstance(dist, float)
        self.assertTrue(400 < dist < 500)  # Approximate distance
        
        # Euclidean distance (approximate)
        dist_euclidean = self.addis_ababa.distance_to(self.bahir_dar, 'euclidean')
        self.assertIsInstance(dist_euclidean, float)
    
    def test_city_equality(self):
        """Test city equality based on ID"""
        city1 = City(1, "Test1", latitude=0, longitude=0)
        city2 = City(1, "Test2", latitude=0, longitude=0)  # Same ID
        city3 = City(3, "Test3", latitude=0, longitude=0)  # Different ID
        
        self.assertEqual(city1, city2)
        self.assertNotEqual(city1, city3)
    
    def test_city_string_representation(self):
        """Test string representation of city"""
        # With region
        str_repr = str(self.addis_ababa)
        self.assertIn("Addis Ababa", str_repr)
        self.assertIn("Addis Ababa", str_repr)
        
        # Capital marker
        self.assertIn("Capital", str_repr) if self.addis_ababa.is_capital else None
    
    def test_city_to_dict(self):
        """Test conversion to dictionary"""
        city_dict = self.addis_ababa.to_dict()
        
        self.assertEqual(city_dict['id'], 1)
        self.assertEqual(city_dict['name'], "Addis Ababa")
        self.assertEqual(city_dict['region'], "Addis Ababa")
        self.assertEqual(city_dict['latitude'], 9.03)
        self.assertEqual(city_dict['longitude'], 38.74)
        self.assertTrue(city_dict['is_capital'])
    
    def test_city_from_dict(self):
        """Test creation from dictionary"""
        city_dict = {
            'id': 5,
            'name': 'Mekelle',
            'region': 'Tigray',
            'latitude': 13.50,
            'longitude': 39.47,
            'population': 340000,
            'elevation': 2084,
            'is_capital': False
        }
        
        city = City.from_dict(city_dict)
        self.assertEqual(city.id, 5)
        self.assertEqual(city.name, "Mekelle")
        self.assertEqual(city.region, "Tigray")
        self.assertEqual(city.latitude, 13.50)
        self.assertEqual(city.longitude, 39.47)
        self.assertEqual(city.population, 340000)
        self.assertEqual(city.elevation, 2084)
        self.assertFalse(city.is_capital)


class TestRoad(unittest.TestCase):
    """Test cases for Road class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.road = Road(
            id=101,
            city1_id=1,
            city2_id=2,
            distance=85.5,
            road_type=RoadType.HIGHWAY,
            condition=RoadCondition.GOOD,
            speed_limit=100,
            lanes=4,
            toll=False,
            name="A1 Highway",
            terrain_factor=1.1
        )
    
    def test_road_creation(self):
        """Test road object creation and attributes"""
        self.assertEqual(self.road.id, 101)
        self.assertEqual(self.road.city1_id, 1)
        self.assertEqual(self.road.city2_id, 2)
        self.assertEqual(self.road.distance, 85.5)
        self.assertEqual(self.road.road_type, RoadType.HIGHWAY)
        self.assertEqual(self.road.condition, RoadCondition.GOOD)
        self.assertEqual(self.road.speed_limit, 100)
        self.assertEqual(self.road.lanes, 4)
        self.assertFalse(self.road.toll)
        self.assertEqual(self.road.name, "A1 Highway")
        self.assertEqual(self.road.terrain_factor, 1.1)
    
    def test_invalid_distance(self):
        """Test validation of invalid distance"""
        with self.assertRaises(ValueError):
            Road(102, 1, 2, -10)  # Negative distance
    
    def test_get_other_city(self):
        """Test getting the other city endpoint"""
        self.assertEqual(self.road.get_other_city(1), 2)
        self.assertEqual(self.road.get_other_city(2), 1)
        
        with self.assertRaises(ValueError):
            self.road.get_other_city(3)  # Invalid city ID
    
    def test_travel_time(self):
        """Test travel time calculation"""
        # Without specified speed
        time = self.road.get_travel_time()
        self.assertIsInstance(time, float)
        self.assertTrue(0.5 < time < 1.5)  # Reasonable time
        
        # With specified speed
        time = self.road.get_travel_time(speed=50)
        self.assertAlmostEqual(time, 85.5 / 50, places=2)
    
    def test_effective_distance(self):
        """Test effective distance calculation"""
        # With terrain factor
        eff_dist = self.road.get_effective_distance(consider_terrain=True)
        self.assertAlmostEqual(eff_dist, 85.5 * 1.1, places=2)
        
        # Without terrain factor
        eff_dist = self.road.get_effective_distance(consider_terrain=False)
        self.assertEqual(eff_dist, 85.5)
    
    def test_road_to_dict(self):
        """Test conversion to dictionary"""
        road_dict = self.road.to_dict()
        
        self.assertEqual(road_dict['id'], 101)
        self.assertEqual(road_dict['city1_id'], 1)
        self.assertEqual(road_dict['city2_id'], 2)
        self.assertEqual(road_dict['distance'], 85.5)
        self.assertEqual(road_dict['road_type'], 'highway')
        self.assertEqual(road_dict['condition'], 'good')
    
    def test_road_from_dict(self):
        """Test creation from dictionary"""
        road_dict = {
            'id': 102,
            'city1_id': 2,
            'city2_id': 3,
            'distance': 180.0,
            'road_type': 'regional',
            'condition': 'fair',
            'speed_limit': 80,
            'lanes': 2,
            'toll': False,
            'name': 'Gondar Road'
        }
        
        road = Road.from_dict(road_dict)
        self.assertEqual(road.id, 102)
        self.assertEqual(road.city1_id, 2)
        self.assertEqual(road.city2_id, 3)
        self.assertEqual(road.distance, 180.0)
        self.assertEqual(road.road_type, RoadType.REGIONAL)
        self.assertEqual(road.condition, RoadCondition.FAIR)


class TestRoadNetwork(unittest.TestCase):
    """Test cases for RoadNetwork class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.network = RoadNetwork()
        
        # Add test cities
        self.city1 = City(1, "Addis Ababa", "Addis Ababa", 9.03, 38.74, is_capital=True)
        self.city2 = City(2, "Adama", "Oromia", 8.54, 39.27)
        self.city3 = City(3, "Bahir Dar", "Amhara", 11.60, 37.38)
        
        self.network.add_city(self.city1)
        self.network.add_city(self.city2)
        self.network.add_city(self.city3)
        
        # Add test roads
        self.road1 = Road(101, 1, 2, 85, RoadType.HIGHWAY)
        self.road2 = Road(102, 2, 3, 380, RoadType.HIGHWAY)
        
        self.network.add_road(self.road1)
        self.network.add_road(self.road2)
    
    def test_network_creation(self):
        """Test network initialization"""
        self.assertEqual(self.network.get_city_count(), 3)
        self.assertEqual(self.network.get_road_count(), 2)
    
    def test_add_city(self):
        """Test adding cities to network"""
        new_city = City(4, "Dire Dawa", "Dire Dawa", 9.60, 41.87)
        city_id = self.network.add_city(new_city)
        
        self.assertEqual(city_id, 4)
        self.assertEqual(self.network.get_city_count(), 4)
        self.assertIsNotNone(self.network.get_city_by_id(4))
    
    def test_add_duplicate_city(self):
        """Test adding duplicate city (should work with different ID)"""
        duplicate = City(1, "Different", "Oromia", 0, 0)  # Same ID
        self.network.add_city(duplicate)  # Should replace or add?
        # Note: Behavior depends on implementation
    
    def test_add_road(self):
        """Test adding roads to network"""
        new_road = Road(103, 1, 3, 700, RoadType.HIGHWAY)
        road_id = self.network.add_road(new_road)
        
        self.assertEqual(road_id, 103)
        self.assertEqual(self.network.get_road_count(), 3)
    
    def test_add_road_invalid_cities(self):
        """Test adding road with non-existent cities"""
        invalid_road = Road(104, 1, 99, 100)  # City 99 doesn't exist
        
        with self.assertRaises(ValueError):
            self.network.add_road(invalid_road)
    
    def test_get_city_by_id(self):
        """Test retrieving city by ID"""
        city = self.network.get_city_by_id(1)
        self.assertEqual(city.name, "Addis Ababa")
        
        city = self.network.get_city_by_id(999)
        self.assertIsNone(city)
    
    def test_get_city_by_name(self):
        """Test retrieving city by name"""
        city = self.network.get_city_by_name("Addis Ababa")
        self.assertEqual(city.id, 1)
        
        city = self.network.get_city_by_name("NonExistent")
        self.assertIsNone(city)
    
    def test_get_cities_by_region(self):
        """Test retrieving cities by region"""
        oromia_cities = self.network.get_cities_by_region("Oromia")
        self.assertEqual(len(oromia_cities), 1)
        self.assertEqual(oromia_cities[0].name, "Adama")
        
        amhara_cities = self.network.get_cities_by_region("Amhara")
        self.assertEqual(len(amhara_cities), 1)
    
    def test_get_road_between(self):
        """Test retrieving road between two cities"""
        road = self.network.get_road_between(1, 2)
        self.assertEqual(road.id, 101)
        
        road = self.network.get_road_between(1, 3)  # No direct road
        self.assertIsNone(road)
    
    def test_get_neighbors(self):
        """Test getting neighbors of a city"""
        neighbors = self.network.get_neighbors(1)
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0][0], 2)  # neighbor ID
        self.assertEqual(neighbors[0][1], 85)  # distance
        
        neighbors = self.network.get_neighbors(2)
        self.assertEqual(len(neighbors), 2)  # Connected to both 1 and 3
    
    def test_network_statistics(self):
        """Test network statistical calculations"""
        density = self.network.get_density()
        max_possible = 3 * 2 / 2  # Complete graph edges
        expected_density = 2 / max_possible
        self.assertAlmostEqual(density, expected_density)
        
        avg_degree = self.network.get_average_degree()
        self.assertAlmostEqual(avg_degree, (1 + 2 + 1) / 3)  # Degrees: city1=1, city2=2, city3=1
    
    def test_adjacency_matrix(self):
        """Test adjacency matrix generation"""
        matrix = self.network.get_adjacency_matrix()
        
        self.assertEqual(len(matrix), 3)
        self.assertEqual(len(matrix[0]), 3)
        
        # Check distances
        self.assertEqual(matrix[0][0], 0)  # Self distance
        self.assertEqual(matrix[0][1], 85)  # City1 to City2
        self.assertEqual(matrix[1][2], 380)  # City2 to City3
        self.assertEqual(matrix[2][0], float('inf'))  # No direct connection
    
    def test_generate_ethiopian_network(self):
        """Test generating random Ethiopian network"""
        self.network.generate_ethiopian_network(num_cities=10, num_roads=15)
        
        self.assertEqual(self.network.get_city_count(), 10)
        self.assertEqual(self.network.get_road_count(), 15)
        
        # Check that all cities have valid regions
        for city in self.network.cities.values():
            self.assertIn(city.region, City.REGIONS + ['Unknown'])
    
    def test_network_serialization(self):
        """Test network to/from dictionary"""
        # Convert to dict
        network_dict = self.network.to_dict()
        
        self.assertEqual(len(network_dict['cities']), 3)
        self.assertEqual(len(network_dict['roads']), 2)
        
        # Recreate from dict
        new_network = RoadNetwork.from_dict(network_dict)
        
        self.assertEqual(new_network.get_city_count(), 3)
        self.assertEqual(new_network.get_road_count(), 2)
        
        # Check data integrity
        city = new_network.get_city_by_id(1)
        self.assertEqual(city.name, "Addis Ababa")
        
        road = new_network.get_road_between(1, 2)
        self.assertEqual(road.distance, 85)


if __name__ == '__main__':
    unittest.main(verbosity=2)