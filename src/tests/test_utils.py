"""
Unit tests for Utils module (DataLoader, DistanceCalculator, Validators)
Tests utility functions for Ethiopian GPS navigation system
"""

import sys
import os
import unittest
import tempfile
import csv
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.data_loader import DataLoader
from src.utils.distance_calc import DistanceCalculator, DistanceMethod
from src.utils.validators import Validators, ValidationError
from src.graph.city import City
from src.graph.road import Road, RoadType, RoadCondition
from src.graph.network import RoadNetwork


class TestDataLoader(unittest.TestCase):
    """Test cases for DataLoader class"""
    
    def setUp(self):
        """Set up test fixtures with temporary files"""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = DataLoader(data_dir=self.temp_dir, verbose=False)
        
        # Create test CSV files
        self.cities_file = os.path.join(self.temp_dir, "test_cities.csv")
        self.roads_file = os.path.join(self.temp_dir, "test_roads.csv")
        
        # Write test cities CSV
        with open(self.cities_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['city_id', 'city_name', 'region', 'latitude', 'longitude', 
                           'population', 'elevation', 'is_capital'])
            writer.writerow([1, 'Addis Ababa', 'Addis Ababa', 9.03, 38.74, 3500000, 2355, '1'])
            writer.writerow([2, 'Bahir Dar', 'Amhara', 11.60, 37.38, 350000, 1800, '0'])
            writer.writerow([3, 'Mekelle', 'Tigray', 13.50, 39.47, 340000, 2084, '0'])
        
        # Write test roads CSV
        with open(self.roads_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['road_id', 'city1_id', 'city2_id', 'distance_km', 
                           'road_type', 'condition', 'speed_limit', 'lanes', 'toll', 'name'])
            writer.writerow([101, 1, 2, 380, 'highway', 'good', 100, 4, 'false', 'Addis-Bahir'])
            writer.writerow([102, 2, 3, 380, 'highway', 'good', 100, 4, 'false', 'Bahir-Mekelle'])
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_cities(self):
        """Test loading cities from CSV"""
        cities = self.loader.load_ethiopian_cities(
            filename=os.path.basename(self.cities_file),
            use_processed=False
        )
        
        self.assertEqual(len(cities), 3)
        
        # Check first city
        addis = cities[0]
        self.assertEqual(addis.id, 1)
        self.assertEqual(addis.name, "Addis Ababa")
        self.assertEqual(addis.region, "Addis Ababa")
        self.assertEqual(addis.latitude, 9.03)
        self.assertEqual(addis.longitude, 38.74)
        self.assertEqual(addis.population, 3500000)
        self.assertEqual(addis.elevation, 2355)
        self.assertTrue(addis.is_capital)
    
    def test_load_roads(self):
        """Test loading roads from CSV"""
        # First load cities for validation
        cities = self.loader.load_ethiopian_cities(
            filename=os.path.basename(self.cities_file),
            use_processed=False
        )
        cities_dict = {city.id: city for city in cities}
        
        roads = self.loader.load_ethiopian_roads(
            filename=os.path.basename(self.roads_file),
            cities_dict=cities_dict
        )
        
        self.assertEqual(len(roads), 2)
        
        # Check first road
        road = roads[0]
        self.assertEqual(road.id, 101)
        self.assertEqual(road.city1_id, 1)
        self.assertEqual(road.city2_id, 2)
        self.assertEqual(road.distance, 380)
        self.assertEqual(road.road_type, RoadType.HIGHWAY)
        self.assertEqual(road.condition, RoadCondition.GOOD)
    
    def test_create_network_from_files(self):
        """Test creating complete network from files"""
        network = self.loader.create_network_from_files(
            cities_file=os.path.basename(self.cities_file),
            roads_file=os.path.basename(self.roads_file)
        )
        
        self.assertEqual(network.get_city_count(), 3)
        self.assertEqual(network.get_road_count(), 2)
        
        # Check connections
        road = network.get_road_between(1, 2)
        self.assertIsNotNone(road)
        self.assertEqual(road.distance, 380)
    
    def test_export_network(self):
        """Test exporting network to CSV"""
        # First create network
        network = self.loader.create_network_from_files(
            cities_file=os.path.basename(self.cities_file),
            roads_file=os.path.basename(self.roads_file)
        )
        
        # Export to new files
        self.loader.export_network_to_csv(
            network,
            cities_output="export_cities.csv",
            roads_output="export_roads.csv"
        )
        
        # Check that files were created
        self.assertTrue(os.path.exists(os.path.join(self.loader.processed_dir, "export_cities.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.loader.processed_dir, "export_roads.csv")))
    
    def test_load_sample_network(self):
        """Test loading sample network (should handle missing files gracefully)"""
        # This should not raise an exception even if sample files don't exist
        try:
            network = self.loader.load_sample_network()
            # If files exist, check network
            if network.get_city_count() > 0:
                self.assertIsInstance(network, RoadNetwork)
        except FileNotFoundError:
            # Expected if sample files don't exist
            pass


class TestDistanceCalculator(unittest.TestCase):
    """Test cases for DistanceCalculator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Addis Ababa coordinates
        self.addis_lat, self.addis_lon = 9.03, 38.74
        # Mekelle coordinates
        self.mekelle_lat, self.mekelle_lon = 13.50, 39.47
        # Bahir Dar coordinates
        self.bahir_lat, self.bahir_lon = 11.60, 37.38
    
    def test_haversine(self):
        """Test Haversine formula"""
        # Known distance: Addis to Mekelle ~ 783 km
        dist = DistanceCalculator.haversine(
            self.addis_lat, self.addis_lon,
            self.mekelle_lat, self.mekelle_lon
        )
        
        self.assertIsInstance(dist, float)
        self.assertTrue(750 < dist < 800)  # Should be around 783 km
        
        # Test same point
        dist = DistanceCalculator.haversine(
            self.addis_lat, self.addis_lon,
            self.addis_lat, self.addis_lon
        )
        self.assertAlmostEqual(dist, 0, places=2)
    
    def test_vincenty(self):
        """Test Vincenty formula (more accurate)"""
        dist = DistanceCalculator.vincenty(
            self.addis_lat, self.addis_lon,
            self.mekelle_lat, self.mekelle_lon
        )
        
        self.assertIsInstance(dist, float)
        self.assertTrue(750 < dist < 800)
    
    def test_euclidean_approx(self):
        """Test Euclidean approximation"""
        dist = DistanceCalculator.euclidean_approx(
            self.addis_lat, self.addis_lon,
            self.mekelle_lat, self.mekelle_lon
        )
        
        self.assertIsInstance(dist, float)
        # Euclidean will be less accurate but should be in same ballpark
        self.assertTrue(700 < dist < 900)
    
    def test_road_estimate(self):
        """Test road distance estimation with terrain factors"""
        dist = DistanceCalculator.road_estimate(
            self.addis_lat, self.addis_lon,
            self.mekelle_lat, self.mekelle_lon,
            region1="Addis Ababa", region2="Tigray",
            elevation1=2355, elevation2=2084
        )
        
        self.assertIsInstance(dist, float)
        # Road distance should be > straight line
        haversine_dist = DistanceCalculator.haversine(
            self.addis_lat, self.addis_lon,
            self.mekelle_lat, self.mekelle_lon
        )
        self.assertTrue(dist > haversine_dist)
    
    def test_bearing(self):
        """Test bearing calculation"""
        bearing = DistanceCalculator.bearing(
            self.addis_lat, self.addis_lon,
            self.mekelle_lat, self.mekelle_lon
        )
        
        self.assertIsInstance(bearing, float)
        self.assertTrue(0 <= bearing <= 360)
        
        # Bearing from Addis to Mekelle should be roughly north-east
        self.assertTrue(30 < bearing < 60)
    
    def test_midpoint(self):
        """Test midpoint calculation"""
        lat, lon = DistanceCalculator.midpoint(
            self.addis_lat, self.addis_lon,
            self.mekelle_lat, self.mekelle_lon
        )
        
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)
        
        # Midpoint should be between the two points
        self.assertTrue(min(self.addis_lat, self.mekelle_lat) <= lat <= max(self.addis_lat, self.mekelle_lat))
        self.assertTrue(min(self.addis_lon, self.mekelle_lon) <= lon <= max(self.addis_lon, self.mekelle_lon))
    
    def test_destination_point(self):
        """Test destination point calculation"""
        # Go 100 km north from Addis
        dest_lat, dest_lon = DistanceCalculator.destination_point(
            self.addis_lat, self.addis_lon,
            bearing=0, distance=100
        )
        
        self.assertIsInstance(dest_lat, float)
        self.assertIsInstance(dest_lon, float)
        
        # Should be north of Addis
        self.assertTrue(dest_lat > self.addis_lat)
        # Longitude should be similar
        self.assertAlmostEqual(dest_lon, self.addis_lon, places=1)
    
    def test_batch_distance(self):
        """Test batch distance calculation"""
        points = [
            (self.addis_lat, self.addis_lon),
            (self.bahir_lat, self.bahir_lon),
            (self.mekelle_lat, self.mekelle_lon)
        ]
        
        distances = DistanceCalculator.batch_distance(points)
        
        self.assertEqual(len(distances), 2)
        self.assertTrue(all(isinstance(d, float) for d in distances))
    
    def test_total_distance(self):
        """Test total distance along path"""
        points = [
            (self.addis_lat, self.addis_lon),
            (self.bahir_lat, self.bahir_lon),
            (self.mekelle_lat, self.mekelle_lon)
        ]
        
        total = DistanceCalculator.total_distance(points)
        
        self.assertIsInstance(total, float)
        self.assertTrue(total > 0)
    
    def test_format_distance(self):
        """Test distance formatting"""
        # Kilometers
        formatted = DistanceCalculator.format_distance(783.5, 'km')
        self.assertEqual(formatted, "783.5 km")
        
        # Meters for small distances
        formatted = DistanceCalculator.format_distance(0.05, 'km')
        self.assertIn("m", formatted)
        
        # Miles
        formatted = DistanceCalculator.format_distance(100, 'mi')
        self.assertEqual(formatted, "100.0 mi")
    
    def test_distance_table(self):
        """Test distance table generation"""
        points = [
            (self.addis_lat, self.addis_lon, "Addis"),
            (self.bahir_lat, self.bahir_lon, "Bahir"),
            (self.mekelle_lat, self.mekelle_lon, "Mekelle")
        ]
        
        table = DistanceCalculator.get_distance_table(points)
        
        self.assertIsInstance(table, str)
        self.assertIn("Addis", table)
        self.assertIn("Bahir", table)
        self.assertIn("Mekelle", table)
        self.assertIn("km", table)


class TestValidators(unittest.TestCase):
    """Test cases for Validators class"""
    
    def test_validate_city_name(self):
        """Test city name validation"""
        # Valid names
        valid_names = ["Addis Ababa", "Gondar", "Debre Markos", "Hawassa"]
        for name in valid_names:
            is_valid, error = Validators.validate_city_name(name)
            self.assertTrue(is_valid, f"Failed for {name}: {error}")
        
        # Invalid names
        invalid_names = ["", "A", "City123", "VeryLongName" * 20]
        for name in invalid_names:
            is_valid, _ = Validators.validate_city_name(name)
            self.assertFalse(is_valid)
    
    def test_validate_region(self):
        """Test Ethiopian region validation"""
        # Valid regions
        for region in Validators.ETHIOPIAN_REGIONS:
            is_valid, error = Validators.validate_region(region)
            self.assertTrue(is_valid, f"Failed for {region}: {error}")
        
        # Case insensitive
        is_valid, _ = Validators.validate_region("oromia")
        self.assertTrue(is_valid)
        
        # Invalid region
        is_valid, _ = Validators.validate_region("InvalidRegion")
        self.assertFalse(is_valid)
    
    def test_validate_coordinates(self):
        """Test coordinate validation"""
        # Valid coordinates
        valid_coords = [(9.03, 38.74), (0, 0), (90, 180), (-90, -180)]
        for lat, lon in valid_coords:
            is_valid, error = Validators.validate_coordinates(lat, lon)
            self.assertTrue(is_valid, f"Failed for ({lat}, {lon}): {error}")
        
        # Invalid coordinates
        invalid_coords = [(100, 38.74), (9.03, 200), (-100, 38.74)]
        for lat, lon in invalid_coords:
            is_valid, _ = Validators.validate_coordinates(lat, lon)
            self.assertFalse(is_valid)
    
    def test_validate_within_ethiopia(self):
        """Test Ethiopia bounds validation"""
        # Within Ethiopia
        ethiopia_coords = [(9.03, 38.74), (13.5, 39.47), (6.0, 37.0)]
        for lat, lon in ethiopia_coords:
            is_valid, error = Validators.validate_within_ethiopia(lat, lon)
            self.assertTrue(is_valid, f"Failed for ({lat}, {lon}): {error}")
        
        # Outside Ethiopia
        outside_coords = [(20, 38.74), (9.03, 50), (0, 38.74)]
        for lat, lon in outside_coords:
            is_valid, _ = Validators.validate_within_ethiopia(lat, lon)
            self.assertFalse(is_valid)
    
    def test_validate_distance(self):
        """Test distance validation"""
        # Valid distances
        valid_dists = [10, 100, 500, 1000]
        for dist in valid_dists:
            is_valid, error = Validators.validate_distance(dist)
            self.assertTrue(is_valid, f"Failed for {dist}: {error}")
        
        # Invalid distances
        invalid_dists = [0, -10, 5000]
        for dist in invalid_dists:
            is_valid, _ = Validators.validate_distance(dist)
            self.assertFalse(is_valid)
    
    def test_validate_speed(self):
        """Test speed validation"""
        # Valid speeds
        valid_speeds = [30, 60, 100, 120]
        for speed in valid_speeds:
            is_valid, error = Validators.validate_speed(speed)
            self.assertTrue(is_valid, f"Failed for {speed}: {error}")
        
        # Invalid speeds
        invalid_speeds = [0, -10, 300]
        for speed in invalid_speeds:
            is_valid, _ = Validators.validate_speed(speed)
            self.assertFalse(is_valid)
    
    def test_validate_population(self):
        """Test population validation"""
        # Valid populations
        valid_pops = [0, 1000, 1000000, 5000000]
        for pop in valid_pops:
            is_valid, error = Validators.validate_population(pop)
            self.assertTrue(is_valid, f"Failed for {pop}: {error}")
        
        # Invalid populations
        invalid_pops = [-100, 20000000]
        for pop in invalid_pops:
            is_valid, _ = Validators.validate_population(pop)
            self.assertFalse(is_valid)
    
    def test_validate_elevation(self):
        """Test elevation validation"""
        # Valid elevations
        valid_ele = [-100, 0, 1000, 2500, 4000]
        for ele in valid_ele:
            is_valid, error = Validators.validate_elevation(ele)
            self.assertTrue(is_valid, f"Failed for {ele}: {error}")
        
        # Invalid elevations
        invalid_ele = [-1000, 6000]
        for ele in invalid_ele:
            is_valid, _ = Validators.validate_elevation(ele)
            self.assertFalse(is_valid)
    
    def test_validate_city_id(self):
        """Test city ID validation"""
        existing_ids = [1, 2, 3]
        
        # Valid ID
        is_valid, _ = Validators.validate_city_id(4, existing_ids)
        self.assertTrue(is_valid)
        
        # Duplicate ID
        is_valid, _ = Validators.validate_city_id(1, existing_ids)
        self.assertFalse(is_valid)
        
        # Invalid ID (non-positive)
        is_valid, _ = Validators.validate_city_id(0, existing_ids)
        self.assertFalse(is_valid)
    
    def test_validate_road_connection(self):
        """Test road connection validation"""
        # Different cities
        is_valid, _ = Validators.validate_road_connection(1, 2)
        self.assertTrue(is_valid)
        
        # Same city
        is_valid, _ = Validators.validate_road_connection(1, 1)
        self.assertFalse(is_valid)
    
    def test_validate_road_type(self):
        """Test road type validation"""
        # Valid types
        for road_type in Validators.ROAD_TYPES:
            is_valid, error = Validators.validate_road_type(road_type)
            self.assertTrue(is_valid, f"Failed for {road_type}: {error}")
        
        # Invalid type
        is_valid, _ = Validators.validate_road_type("invalid")
        self.assertFalse(is_valid)
    
    def test_validate_road_condition(self):
        """Test road condition validation"""
        # Valid conditions
        for condition in Validators.ROAD_CONDITIONS:
            is_valid, error = Validators.validate_road_condition(condition)
            self.assertTrue(is_valid, f"Failed for {condition}: {error}")
        
        # Invalid condition
        is_valid, _ = Validators.validate_road_condition("invalid")
        self.assertFalse(is_valid)
    
    def test_validate_path(self):
        """Test path validation"""
        # Valid path
        is_valid, _ = Validators.validate_path([1, 2, 3, 4], 1, 4)
        self.assertTrue(is_valid)
        
        # Empty path
        is_valid, _ = Validators.validate_path([], 1, 4)
        self.assertFalse(is_valid)
        
        # Wrong start
        is_valid, _ = Validators.validate_path([2, 3, 4], 1, 4)
        self.assertFalse(is_valid)
        
        # Wrong end
        is_valid, _ = Validators.validate_path([1, 2, 3], 1, 4)
        self.assertFalse(is_valid)
        
        # Contains cycle
        is_valid, _ = Validators.validate_path([1, 2, 1, 3, 4], 1, 4)
        self.assertFalse(is_valid)
    
    def test_validate_range(self):
        """Test range validation"""
        # Within range
        is_valid, _ = Validators.validate_range(50, 0, 100, "test")
        self.assertTrue(is_valid)
        
        # Below range
        is_valid, _ = Validators.validate_range(-10, 0, 100, "test")
        self.assertFalse(is_valid)
        
        # Above range
        is_valid, _ = Validators.validate_range(200, 0, 100, "test")
        self.assertFalse(is_valid)
    
    def test_validate_not_empty(self):
        """Test non-empty validation"""
        # Non-empty values
        is_valid, _ = Validators.validate_not_empty("hello", "test")
        self.assertTrue(is_valid)
        is_valid, _ = Validators.validate_not_empty([1, 2], "test")
        self.assertTrue(is_valid)
        
        # Empty values
        is_valid, _ = Validators.validate_not_empty("", "test")
        self.assertFalse(is_valid)
        is_valid, _ = Validators.validate_not_empty([], "test")
        self.assertFalse(is_valid)
        is_valid, _ = Validators.validate_not_empty(None, "test")
        self.assertFalse(is_valid)
    
    def test_validate_ethiopian_phone(self):
        """Test Ethiopian phone number validation"""
        # Valid phone numbers
        valid_phones = [
            "0912345678",
            "0111234567",
            "+251912345678",
            "251912345678",
            "09-12-34-56-78"
        ]
        for phone in valid_phones:
            is_valid, error = Validators.validate_ethiopian_phone(phone)
            self.assertTrue(is_valid, f"Failed for {phone}: {error}")
        
        # Invalid phone numbers
        invalid_phones = [
            "12345",
            "09999999999",
            "abcdefghij",
            ""
        ]
        for phone in invalid_phones:
            is_valid, _ = Validators.validate_ethiopian_phone(phone)
            self.assertFalse(is_valid)
    
    def test_validate_email(self):
        """Test email validation"""
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@ethiopia.et",
            "user+label@gmail.com"
        ]
        for email in valid_emails:
            is_valid, error = Validators.validate_email(email)
            self.assertTrue(is_valid, f"Failed for {email}: {error}")
        
        # Invalid emails
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            ""
        ]
        for email in invalid_emails:
            is_valid, _ = Validators.validate_email(email)
            self.assertFalse(is_valid)


if __name__ == '__main__':
    unittest.main(verbosity=2)