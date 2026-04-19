"""
Data Loader Utility - Load and process CSV data for Ethiopian cities and roads
Handles multiple data formats and provides robust error handling
"""

import csv
import os
import sys
import json
from typing import List, Dict, Tuple, Optional, Any, Union
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.city import City
from src.graph.road import Road, RoadType, RoadCondition
from src.graph.network import RoadNetwork
from src.db.session import Base, _engine
from src.db.models import CityDB, RoadDB


class DataLoader:
    """
    Utility class for loading Ethiopian city and road data from various file formats
    
    Features:
    - Load from CSV, JSON, or TXT files
    - Automatic format detection
    - Data validation and cleaning
    - Progress tracking for large datasets
    - Error handling and reporting
    - Support for Ethiopian specific data formats
    """
    
    # Expected CSV column names and their variations
    CITY_COLUMN_MAPPINGS = {
        'id': ['id', 'city_id', 'ID', 'CityID', 'index'],
        'name': ['name', 'city_name', 'City', 'city', 'CityName'],
        'region': ['region', 'Region', 'state', 'State', 'admin'],
        'latitude': ['latitude', 'lat', 'Latitude', 'LAT', 'y'],
        'longitude': ['longitude', 'lon', 'lng', 'Longitude', 'LON', 'x'],
        'population': ['population', 'Population', 'pop', 'POP'],
        'elevation': ['elevation', 'Elevation', 'altitude', 'ALT'],
        'is_capital': ['is_capital', 'capital', 'Capital', 'IsCapital']
    }
    
    ROAD_COLUMN_MAPPINGS = {
        'id': ['id', 'road_id', 'ID', 'RoadID', 'edge_id'],
        'city1_id': ['city1_id', 'source_id', 'from_id', 'u', 'start_id'],
        'city2_id': ['city2_id', 'target_id', 'to_id', 'v', 'end_id'],
        'distance': ['distance', 'distance_km', 'dist', 'Distance', 'length', 'weight', 'km'],
        'road_type': ['road_type', 'type', 'RoadType', 'roadtype'],
        'condition': ['condition', 'Condition', 'road_condition'],
        'speed_limit': ['speed_limit', 'speed', 'Speed', 'speedlimit'],
        'lanes': ['lanes', 'Lanes', 'lane_count'],
        'toll': ['toll', 'Toll', 'is_toll'],
        'name': ['name', 'road_name', 'Name', 'RoadName']
    }
    
    def __init__(self, data_dir: str = "data", verbose: bool = True):
        """
        Initialize DataLoader with data directory
        
        Args:
            data_dir: Path to data directory (default: "data")
            verbose: Whether to print progress messages
        """
        self.data_dir = data_dir
        self.verbose = verbose
        self.raw_dir = os.path.join(data_dir, "raw")
        self.processed_dir = os.path.join(data_dir, "processed")
        self.sample_dir = os.path.join(data_dir, "sample")
        
        # Create directories if they don't exist
        for dir_path in [self.raw_dir, self.processed_dir, self.sample_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        self.load_stats = {
            'cities_loaded': 0,
            'roads_loaded': 0,
            'errors': 0,
            'warnings': 0
        }
    
    def load_ethiopian_cities(self,
                             filename: str = "ethiopian_cities_clean.csv",
                             use_processed: bool = True,
                             encoding: str = 'utf-8') -> List[City]:
        """
        Load Ethiopian cities from CSV file with automatic column detection
        
        Args:
            filename: Name of CSV file
            use_processed: If True, load from processed directory, else from raw
            encoding: File encoding (default: utf-8)
            
        Returns:
            List of City objects
        """
        self.load_stats = {'cities_loaded': 0, 'roads_loaded': 0, 'errors': 0, 'warnings': 0}
        
        # Determine file path
        if use_processed:
            filepath = os.path.join(self.processed_dir, filename)
        else:
            filepath = os.path.join(self.raw_dir, filename)
        
        # Try alternative paths if file not found
        if not os.path.exists(filepath):
            alt_paths = [
                os.path.join(self.data_dir, "raw", "processed", filename),
                os.path.join(self.data_dir, "raw", filename),
                os.path.join(self.sample_dir, "ethiopia_sample_graph.csv"),
                os.path.join(self.raw_dir, "ethiopian_cities_raw.csv"),
                os.path.join(self.data_dir, "cities.csv")
            ]
            
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    filepath = alt_path
                    if self.verbose:
                        print(f"📁 Using alternative file: {alt_path}")
                    break
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"City data file not found: {filepath}")
        
        cities = []
        column_mapping = {}
        
        try:
            with open(filepath, 'r', encoding=encoding) as file:
                # Detect delimiter
                first_line = file.readline()
                file.seek(0)
                
                delimiter = self._detect_delimiter(first_line)
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Map columns
                column_mapping = self._map_columns(reader.fieldnames, self.CITY_COLUMN_MAPPINGS)
                
                if self.verbose:
                    print(f"\n📊 Loading cities from: {os.path.basename(filepath)}")
                    print(f"   Delimiter: '{delimiter}'")
                    print(f"   Column mapping: {column_mapping}")
                
                # Read rows
                for row_num, row in enumerate(reader, start=2):
                    try:
                        city = self._parse_city_row(row, column_mapping, row_num)
                        if city:
                            cities.append(city)
                            self.load_stats['cities_loaded'] += 1
                    except Exception as e:
                        self.load_stats['errors'] += 1
                        if self.verbose:
                            print(f"   ⚠️  Error at line {row_num}: {e}")
                        
                        if self.load_stats['errors'] > 10:
                            raise ValueError("Too many errors, aborting load")
            
            if self.verbose:
                print(f"   ✅ Loaded {len(cities)} Ethiopian cities")
                if self.load_stats['errors'] > 0:
                    print(f"   ⚠️  {self.load_stats['errors']} errors encountered")
            
            return cities
            
        except Exception as e:
            raise Exception(f"Error loading cities from {filepath}: {e}")
    
    def load_ethiopian_roads(self,
                            filename: str = "ethiopia_road_network.csv",
                            cities_dict: Optional[Dict[int, City]] = None,
                            encoding: str = 'utf-8') -> List[Road]:
        """
        Load Ethiopian roads from CSV file with automatic column detection
        
        Args:
            filename: Name of CSV file
            cities_dict: Dictionary mapping city IDs to City objects (for validation)
            encoding: File encoding
            
        Returns:
            List of Road objects
        """
        # Try different possible file locations
        possible_paths = [
            os.path.join(self.processed_dir, filename),
            os.path.join(self.data_dir, "raw", "processed", filename),
            os.path.join(self.raw_dir, filename),
            os.path.join(self.data_dir, "raw", filename),
            os.path.join(self.raw_dir, "ethiopian_roads_raw.csv"),
            os.path.join(self.sample_dir, "sample_roads.csv"),
            os.path.join(self.data_dir, "roads.csv")
        ]
        
        filepath = None
        for path in possible_paths:
            if os.path.exists(path):
                filepath = path
                break
        
        if not filepath:
            raise FileNotFoundError(f"Road data file not found in any location")
        
        roads = []
        road_id_counter = 1
        column_mapping = {}
        
        try:
            with open(filepath, 'r', encoding=encoding) as file:
                # Detect delimiter
                first_line = file.readline()
                file.seek(0)
                
                delimiter = self._detect_delimiter(first_line)
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Map columns
                column_mapping = self._map_columns(reader.fieldnames, self.ROAD_COLUMN_MAPPINGS)
                
                if self.verbose:
                    print(f"\n🛣️  Loading roads from: {os.path.basename(filepath)}")
                    print(f"   Delimiter: '{delimiter}'")
                    print(f"   Column mapping: {column_mapping}")
                
                # Read rows
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Use existing ID or generate new one
                        if 'id' in column_mapping:
                            road_id = int(row[column_mapping['id']])
                        else:
                            road_id = road_id_counter
                            road_id_counter += 1
                        
                        # Parse required fields
                        city1_id = int(row[column_mapping['city1_id']])
                        city2_id = int(row[column_mapping['city2_id']])
                        distance = float(row[column_mapping['distance']])
                        
                        # Validate cities if dictionary provided
                        if cities_dict:
                            if city1_id not in cities_dict:
                                self.load_stats['warnings'] += 1
                                if self.verbose:
                                    print(f"   ⚠️  Warning at line {row_num}: City {city1_id} not found")
                                continue
                            if city2_id not in cities_dict:
                                self.load_stats['warnings'] += 1
                                if self.verbose:
                                    print(f"   ⚠️  Warning at line {row_num}: City {city2_id} not found")
                                continue
                        
                        # Parse optional fields with defaults
                        road_type = self._parse_road_type(
                            row.get(column_mapping.get('road_type', ''), 'regional')
                        )
                        
                        condition = self._parse_road_condition(
                            row.get(column_mapping.get('condition', ''), 'good')
                        )
                        
                        speed_limit = int(row.get(column_mapping.get('speed_limit', ''), 80))
                        lanes = int(row.get(column_mapping.get('lanes', ''), 2))
                        toll = row.get(column_mapping.get('toll', ''), 'False').lower() in ['true', 'yes', '1']
                        name = row.get(column_mapping.get('name', ''), f"Road_{road_id}")
                        
                        road = Road(
                            id=road_id,
                            city1_id=city1_id,
                            city2_id=city2_id,
                            distance=distance,
                            road_type=road_type,
                            condition=condition,
                            speed_limit=speed_limit,
                            lanes=lanes,
                            toll=toll,
                            name=name
                        )
                        roads.append(road)
                        self.load_stats['roads_loaded'] += 1
                        
                    except Exception as e:
                        self.load_stats['errors'] += 1
                        if self.verbose:
                            print(f"   ⚠️  Error at line {row_num}: {e}")
                        
                        if self.load_stats['errors'] > 10:
                            raise ValueError("Too many errors, aborting load")
            
            if self.verbose:
                print(f"   ✅ Loaded {len(roads)} Ethiopian roads")
                print(f"   ⚠️  {self.load_stats['warnings']} warnings, {self.load_stats['errors']} errors")
            
            return roads
            
        except Exception as e:
            raise Exception(f"Error loading roads from {filepath}: {e}")
    
    def _detect_delimiter(self, first_line: str) -> str:
        """Detect CSV delimiter from first line"""
        common_delimiters = [',', ';', '\t', '|']
        
        for delimiter in common_delimiters:
            if delimiter in first_line:
                return delimiter
        
        return ','  # Default to comma
    
    def _map_columns(self, fieldnames: List[str], mappings: Dict) -> Dict[str, str]:
        """
        Map actual column names to expected column names
        
        Args:
            fieldnames: List of actual column names from CSV
            mappings: Dictionary of expected column names and their variations
            
        Returns:
            Dictionary mapping expected column names to actual column names
        """
        if not fieldnames:
            return {}
        
        fieldnames_lower = [f.lower().strip() for f in fieldnames]
        column_mapping = {}
        
        for expected_col, variations in mappings.items():
            for variation in variations:
                if variation.lower() in fieldnames_lower:
                    idx = fieldnames_lower.index(variation.lower())
                    column_mapping[expected_col] = fieldnames[idx]
                    break
        
        return column_mapping
    
    def _parse_city_row(self, row: Dict, column_mapping: Dict, row_num: int) -> Optional[City]:
        """Parse a CSV row into a City object"""
        try:
            # Get required fields
            city_id = int(row[column_mapping.get('id', 'id')])
            name = row[column_mapping.get('name', 'name')].strip()
            
            # Get optional fields with defaults
            region = row.get(column_mapping.get('region', ''), 'Unknown').strip()
            latitude = float(row.get(column_mapping.get('latitude', ''), 0))
            longitude = float(row.get(column_mapping.get('longitude', ''), 0))
            
            # Parse population (handle commas in numbers)
            pop_str = row.get(column_mapping.get('population', ''), '')
            if pop_str:
                population = int(pop_str.replace(',', ''))
            else:
                population = None
            
            # Parse elevation
            elevation_str = row.get(column_mapping.get('elevation', ''), '')
            elevation = float(elevation_str) if elevation_str else None
            
            # Parse is_capital
            capital_str = row.get(column_mapping.get('is_capital', ''), 'false')
            is_capital = capital_str.lower() in ['true', 'yes', '1', 't']
            
            return City(
                id=city_id,
                name=name,
                region=region,
                latitude=latitude,
                longitude=longitude,
                population=population,
                elevation=elevation,
                is_capital=is_capital
            )
            
        except KeyError as e:
            raise ValueError(f"Missing required column: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid data format: {e}")
    
    def _parse_road_type(self, value: str) -> RoadType:
        """Parse road type string to RoadType enum"""
        value = value.lower().strip()
        
        type_mapping = {
            'highway': RoadType.HIGHWAY,
            'motorway': RoadType.HIGHWAY,
            'expressway': RoadType.HIGHWAY,
            'national': RoadType.NATIONAL,
            'trunk': RoadType.NATIONAL,
            'regional': RoadType.REGIONAL,
            'local': RoadType.LOCAL,
            'gravel': RoadType.GRAVEL,
            'dirt': RoadType.GRAVEL,
            'rural': RoadType.RURAL
        }
        
        return type_mapping.get(value, RoadType.REGIONAL)
    
    def _parse_road_condition(self, value: str) -> RoadCondition:
        """Parse road condition string to RoadCondition enum"""
        value = value.lower().strip()
        
        condition_mapping = {
            'excellent': RoadCondition.EXCELLENT,
            'good': RoadCondition.GOOD,
            'fair': RoadCondition.FAIR,
            'poor': RoadCondition.POOR,
            'bad': RoadCondition.POOR,
            'construction': RoadCondition.UNDER_CONSTRUCTION,
            'under construction': RoadCondition.UNDER_CONSTRUCTION,
            'seasonal': RoadCondition.SEASONAL
        }
        
        return condition_mapping.get(value, RoadCondition.GOOD)
    
    def create_network_from_files(self,
                                 cities_file: str = "ethiopian_cities_clean.csv",
                                 roads_file: str = "ethiopia_road_network.csv") -> RoadNetwork:
        """
        Create a complete road network from city and road files
        
        Args:
            cities_file: Name of cities CSV file
            roads_file: Name of roads CSV file
            
        Returns:
            RoadNetwork object populated with cities and roads
        """
        network = RoadNetwork()
        
        # Load and add cities
        cities = self.load_ethiopian_cities(cities_file)
        for city in cities:
            network.add_city(city)
        
        # Create cities dictionary for validation
        cities_dict = {city.id: city for city in cities}
        
        # Load and add roads
        roads = self.load_ethiopian_roads(roads_file, cities_dict)
        for road in roads:
            try:
                network.add_road(road)
            except ValueError as e:
                if self.verbose:
                    print(f"   ⚠️  Could not add road {road.id}: {e}")
                continue
        
        if self.verbose:
            print(f"\n📊 Network Statistics:")
            print(f"   - Cities: {network.get_city_count()}")
            print(f"   - Roads: {network.get_road_count()}")
            print(f"   - Density: {network.get_density():.4f}")
            print(f"   - Avg connections: {network.get_average_degree():.2f}")
        
        return network
    
    def load_sample_network(self) -> RoadNetwork:
        """
        Load a small sample network for demonstration
        
        Returns:
            Small RoadNetwork object for testing
        """
        return self.create_network_from_files(
            cities_file="ethiopia_sample_graph.csv",
            roads_file="sample_roads.csv"
        )
    
    def export_network_to_csv(self, network: RoadNetwork,
                             cities_output: str = "exported_cities.csv",
                             roads_output: str = "exported_roads.csv"):
        """
        Export network to CSV files
        
        Args:
            network: RoadNetwork to export
            cities_output: Output filename for cities
            roads_output: Output filename for roads
        """
        # Export cities
        cities_path = os.path.join(self.processed_dir, cities_output)
        
        with open(cities_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['city_id', 'city_name', 'region', 'latitude',
                           'longitude', 'population', 'elevation', 'is_capital'])
            
            for city in network.cities.values():
                writer.writerow([
                    city.id,
                    city.name,
                    city.region,
                    city.latitude,
                    city.longitude,
                    city.population or '',
                    city.elevation or '',
                    '1' if city.is_capital else '0'
                ])
        
        # Export roads
        roads_path = os.path.join(self.processed_dir, roads_output)
        with open(roads_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['road_id', 'city1_id', 'city2_id', 'distance_km',
                           'road_type', 'condition', 'speed_limit', 'lanes',
                           'toll', 'name'])
            
            for road in network.roads.values():
                writer.writerow([
                    road.id,
                    road.city1_id,
                    road.city2_id,
                    road.distance,
                    road.road_type.value,
                    road.condition.value,
                    road.speed_limit,
                    road.lanes,
                    '1' if road.toll else '0',
                    road.name or ''
                ])
        
        if self.verbose:
            print(f"\n💾 Exported {len(network.cities)} cities to {cities_path}")
            print(f"💾 Exported {len(network.roads)} roads to {roads_path}")
    
    def load_from_json(self, filename: str) -> RoadNetwork:
        """
        Load network from JSON file
        
        Args:
            filename: JSON file path
            
        Returns:
            RoadNetwork object
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        network = RoadNetwork()
        
        # Add cities
        for city_data in data.get('cities', []):
            city = City.from_dict(city_data)
            network.add_city(city)
        
        # Add roads
        for road_data in data.get('roads', []):
            road = Road.from_dict(road_data)
            try:
                network.add_road(road)
            except ValueError:
                continue
        
        if self.verbose:
            print(f"\n📊 Loaded network from JSON:")
            print(f"   - Cities: {network.get_city_count()}")
            print(f"   - Roads: {network.get_road_count()}")
        
        return network
    
    def export_to_json(self, network: RoadNetwork, filename: str):
        """
        Export network to JSON file
        
        Args:
            network: RoadNetwork to export
            filename: Output JSON file path
        """
        data = network.to_dict()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"\n💾 Exported network to {filename}")

    # ------------------------------------------------------------------
    # Database integration
    # ------------------------------------------------------------------

    def init_database_schema(self):
        """
        Create database tables if they do not already exist.

        This is safe to call multiple times.
        """
        Base.metadata.create_all(bind=_engine)

    def save_network_to_database(self, network: RoadNetwork):
        """
        Persist the given network to the database, replacing existing data.
        """
        from src.db.session import get_session

        self.init_database_schema()

        with get_session() as session:
            # Clear existing data
            session.query(RoadDB).delete()
            session.query(CityDB).delete()

            # Insert cities
            for city in network.cities.values():
                city_row = CityDB(
                    id=city.id,
                    name=city.name,
                    region=city.region,
                    latitude=city.latitude,
                    longitude=city.longitude,
                    population=city.population,
                    elevation=city.elevation,
                    is_capital=city.is_capital,
                    timezone=city.timezone,
                )
                session.add(city_row)

            # Insert roads
            for road in network.roads.values():
                road_row = RoadDB(
                    id=road.id,
                    city1_id=road.city1_id,
                    city2_id=road.city2_id,
                    distance=road.distance,
                    road_type=road.road_type.value,
                    condition=road.condition.value,
                    speed_limit=road.speed_limit,
                    lanes=road.lanes,
                    toll=road.toll,
                    name=road.name,
                    terrain_factor=road.terrain_factor,
                    seasonal=road.seasonal,
                )
                session.add(road_row)

            session.commit()

        if self.verbose:
            print("💾 Saved network to database.")

    def create_network_from_database(self) -> RoadNetwork:
        """
        Create a RoadNetwork populated from the database.

        Raises:
            FileNotFoundError if the database has no city data yet.
        """
        from src.db.session import get_session

        self.init_database_schema()

        network = RoadNetwork()

        with get_session() as session:
            cities_db = session.query(CityDB).all()
            if not cities_db:
                raise FileNotFoundError("Database contains no cities. Populate it first.")

            # Add cities
            for c in cities_db:
                city = City(
                    id=c.id,
                    name=c.name,
                    region=c.region or "Unknown",
                    latitude=c.latitude,
                    longitude=c.longitude,
                    population=c.population,
                    elevation=c.elevation,
                    is_capital=c.is_capital,
                    timezone=c.timezone or "EAT",
                )
                network.add_city(city)

            # Add roads
            roads_db = session.query(RoadDB).all()
            for r in roads_db:
                road = Road(
                    id=r.id,
                    city1_id=r.city1_id,
                    city2_id=r.city2_id,
                    distance=r.distance,
                    road_type=self._parse_road_type(r.road_type),
                    condition=self._parse_road_condition(r.condition),
                    speed_limit=r.speed_limit,
                    lanes=r.lanes,
                    toll=r.toll,
                    name=r.name,
                    terrain_factor=r.terrain_factor,
                    seasonal=r.seasonal,
                )
                try:
                    network.add_road(road)
                except ValueError:
                    continue

        if self.verbose:
            print("\n📊 Loaded network from database:")
            print(f"   - Cities: {network.get_city_count()}")
            print(f"   - Roads: {network.get_road_count()}")

        return network


# Example usage
if __name__ == "__main__":
    loader = DataLoader(verbose=True)
    
    print("="*80)
    print("TESTING DATA LOADER WITH ETHIOPIAN CITIES")
    print("="*80)
    
    # Load sample network
    print("\n1. Loading sample network...")
    sample_network = loader.load_sample_network()
    
    # Try loading full network
    print("\n2. Attempting to load full Ethiopian road network...")
    try:
        full_network = loader.create_network_from_files()
        print(f"✅ Full network loaded successfully!")
    except FileNotFoundError as e:
        print(f"   Could not load full network: {e}")
        print(f"   Using sample network for demonstration...")
        full_network = sample_network
    
    # Export network
    print("\n3. Exporting network to CSV...")
    loader.export_network_to_csv(full_network,
                                cities_output="test_cities.csv",
                                roads_output="test_roads.csv")