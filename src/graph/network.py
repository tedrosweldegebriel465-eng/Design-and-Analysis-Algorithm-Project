"""
Road Network class managing Ethiopian cities and roads
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Tuple, Optional, Set
from src.graph.city import City
from src.graph.road import Road, RoadType, RoadCondition
import random


class RoadNetwork:
    """
    Manages the complete Ethiopian road network with cities and roads
    
    Attributes:
        cities (Dict[int, City]): Dictionary mapping city ID to City object
        roads (Dict[int, Road]): Dictionary mapping road ID to Road object
        adjacency_matrix (List[List[float]]): 2D array of distances
        city_indices (Dict[int, int]): Mapping city ID to matrix index
    """
    
    def __init__(self):
        """Initialize an empty road network"""
        self.cities: Dict[int, City] = {}
        self.roads: Dict[int, Road] = {}
        self.adjacency_matrix: List[List[float]] = []
        self.city_indices: Dict[int, int] = {}
        self.adjacency_list: Dict[int, List[Tuple[int, float, int]]] = {}
        self._road_lookup: Dict[frozenset, int] = {}
        self.next_city_id = 1
        self.next_road_id = 1
        
    def add_city(self, city: City) -> int:
        """
        Add an Ethiopian city to the network
        
        Args:
            city: City object to add
            
        Returns:
            ID of the added city
        """
        # Assign ID if not set
        if city.id == 0:
            city.id = self.next_city_id
            self.next_city_id += 1
        
        self.cities[city.id] = city
        self.adjacency_list.setdefault(city.id, [])
        self._rebuild_adjacency_matrix()
        return city.id
    
    def add_cities(self, cities: List[City]) -> List[int]:
        """
        Add multiple Ethiopian cities to the network
        
        Args:
            cities: List of City objects
            
        Returns:
            List of added city IDs
        """
        city_ids = []
        for city in cities:
            city_ids.append(self.add_city(city))
        return city_ids
    
    def add_road(self, road: Road) -> int:
        """
        Add a road to the network
        
        Args:
            road: Road object to add
            
        Returns:
            ID of the added road
            
        Raises:
            ValueError: If either city doesn't exist
        """
        # Verify both cities exist
        if road.city1_id not in self.cities:
            raise ValueError(f"City {road.city1_id} does not exist")
        if road.city2_id not in self.cities:
            raise ValueError(f"City {road.city2_id} does not exist")
        
        # Assign ID if not set
        if road.id == 0:
            road.id = self.next_road_id
            self.next_road_id += 1
        
        self.roads[road.id] = road
        self._road_lookup[frozenset((road.city1_id, road.city2_id))] = road.id
        self._upsert_adjacency_entry(road.city1_id, road.city2_id, road.distance, road.id)
        self._upsert_adjacency_entry(road.city2_id, road.city1_id, road.distance, road.id)
        self._update_matrix_for_road(road)
        return road.id
    
    def add_roads(self, roads: List[Road]) -> List[int]:
        """
        Add multiple roads to the network
        
        Args:
            roads: List of Road objects
            
        Returns:
            List of added road IDs
        """
        road_ids = []
        for road in roads:
            road_ids.append(self.add_road(road))
        return road_ids
    
    def _rebuild_adjacency_matrix(self):
        """Rebuild the adjacency matrix from current cities and roads"""
        city_count = len(self.cities)
        
        # Create mapping from city ID to index
        self.city_indices = {city_id: idx for idx, city_id in enumerate(sorted(self.cities.keys()))}
        self.adjacency_list = {city_id: [] for city_id in self.cities.keys()}
        self._road_lookup = {}
        
        # Initialize matrix with infinity
        self.adjacency_matrix = [[float('inf')] * city_count for _ in range(city_count)]
        
        # Set diagonal to 0
        for i in range(city_count):
            self.adjacency_matrix[i][i] = 0
        
        # Fill in roads
        for road in self.roads.values():
            idx1 = self.city_indices[road.city1_id]
            idx2 = self.city_indices[road.city2_id]
            self.adjacency_matrix[idx1][idx2] = road.distance
            self.adjacency_matrix[idx2][idx1] = road.distance  # Undirected
            self._road_lookup[frozenset((road.city1_id, road.city2_id))] = road.id
            self.adjacency_list[road.city1_id].append((road.city2_id, road.distance, road.id))
            self.adjacency_list[road.city2_id].append((road.city1_id, road.distance, road.id))

    def _upsert_adjacency_entry(self, from_city_id: int, to_city_id: int, distance: float, road_id: int) -> None:
        """Insert or update one directed adjacency-list edge."""
        if from_city_id not in self.adjacency_list:
            self.adjacency_list[from_city_id] = []

        edges = self.adjacency_list[from_city_id]
        for idx, (neighbor_id, _, _) in enumerate(edges):
            if neighbor_id == to_city_id:
                edges[idx] = (to_city_id, distance, road_id)
                return

        edges.append((to_city_id, distance, road_id))

    def _update_matrix_for_road(self, road: Road) -> None:
        """Update matrix cells for a single road when possible."""
        if road.city1_id not in self.city_indices or road.city2_id not in self.city_indices:
            self._rebuild_adjacency_matrix()
            return

        idx1 = self.city_indices[road.city1_id]
        idx2 = self.city_indices[road.city2_id]
        self.adjacency_matrix[idx1][idx2] = road.distance
        self.adjacency_matrix[idx2][idx1] = road.distance
    
    def get_city_by_id(self, city_id: int) -> Optional[City]:
        """
        Get Ethiopian city by ID
        
        Args:
            city_id: City ID
            
        Returns:
            City object or None if not found
        """
        return self.cities.get(city_id)
    
    def get_city_by_name(self, name: str) -> Optional[City]:
        """
        Get Ethiopian city by name (first match)
        
        Args:
            name: City name
            
        Returns:
            City object or None if not found
        """
        for city in self.cities.values():
            if city.name.lower() == name.lower():
                return city
        return None
    
    def get_cities_by_region(self, region: str) -> List[City]:
        """
        Get all cities in a specific Ethiopian region
        
        Args:
            region: Region name (e.g., 'Oromia', 'Amhara')
            
        Returns:
            List of City objects in that region
        """
        return [city for city in self.cities.values() if city.region.lower() == region.lower()]
    
    def get_road_between(self, city1_id: int, city2_id: int) -> Optional[Road]:
        """
        Get road connecting two Ethiopian cities
        
        Args:
            city1_id: First city ID
            city2_id: Second city ID
            
        Returns:
            Road object or None if not connected
        """
        road_id = self._road_lookup.get(frozenset((city1_id, city2_id)))
        if road_id is None:
            return None
        return self.roads.get(road_id)
    
    def get_neighbors(self, city_id: int) -> List[Tuple[int, float, Optional[Road]]]:
        """
        Get all neighboring Ethiopian cities with distances and roads
        
        Args:
            city_id: City ID
            
        Returns:
            List of (neighbor_id, distance, road) tuples
        """
        neighbors = []
        city_idx = self.city_indices.get(city_id)
        
        if city_idx is None:
            return neighbors
        
        for other_id, distance, road_id in self.adjacency_list.get(city_id, []):
            road = self.roads.get(road_id)
            neighbors.append((other_id, distance, road))
        
        return neighbors
    
    def get_city_count(self) -> int:
        """Get number of Ethiopian cities in network"""
        return len(self.cities)
    
    def get_road_count(self) -> int:
        """Get number of roads in network"""
        return len(self.roads)
    
    def get_density(self) -> float:
        """
        Calculate network density
        
        Returns:
            Density value between 0 and 1
        """
        V = self.get_city_count()
        if V < 2:
            return 0.0
        
        max_possible_roads = V * (V - 1) / 2
        return self.get_road_count() / max_possible_roads
    
    def get_average_degree(self) -> float:
        """
        Calculate average degree (connections per Ethiopian city)
        
        Returns:
            Average degree
        """
        V = self.get_city_count()
        if V == 0:
            return 0.0
        
        total_degree = 0
        for city_id in self.cities.keys():
            total_degree += len(self.get_neighbors(city_id))
        
        return total_degree / V
    
    def generate_ethiopian_network(self, 
                                   num_cities: int = 100,
                                   num_roads: int = 150,
                                   include_all_regions: bool = True):
        """
        Generate a realistic Ethiopian road network
        
        Args:
            num_cities: Number of cities to generate
            num_roads: Number of roads to generate
            include_all_regions: Whether to include all Ethiopian regions
        """
        # Clear existing network
        self.cities.clear()
        self.roads.clear()
        self.next_city_id = 1
        self.next_road_id = 1

        # Precise real-world coordinates for Ethiopian cities (lat, lon, region, population)
        CITY_DATA: List[tuple] = [
            # Addis Ababa
            ('Addis Ababa',    'Addis Ababa',  9.0300,  38.7400, 3500000, 2355, True),
            ('Akaki Kaliti',   'Addis Ababa',  8.8800,  38.7900,  250000, 2100, False),
            ('Bole',           'Addis Ababa',  9.0100,  38.8000,  180000, 2300, False),
            ('Kirkos',         'Addis Ababa',  9.0200,  38.7500,  160000, 2350, False),
            ('Kolfe Keranio',  'Addis Ababa',  9.0400,  38.7000,  200000, 2280, False),
            ('Lideta',         'Addis Ababa',  9.0100,  38.7300,  140000, 2320, False),
            ('Yeka',           'Addis Ababa',  9.0600,  38.8200,  170000, 2400, False),
            ('Gulele',         'Addis Ababa',  9.0700,  38.7400,  130000, 2450, False),
            # Oromia
            ('Adama',          'Oromia',       8.5400,  39.2700,  324000, 1550, False),
            ('Jimma',          'Oromia',       7.6700,  36.8300,  206000, 1780, False),
            ('Bishoftu',       'Oromia',       8.7500,  38.9800,  100000, 1920, False),
            ('Shashamane',     'Oromia',       7.2000,  38.5900,  100000, 1750, False),
            ('Ambo',           'Oromia',       8.9800,  37.8500,   58000, 2100, False),
            ('Nekemte',        'Oromia',       9.0900,  36.5500,   76000, 2100, False),
            ('Asella',         'Oromia',       7.9500,  39.1300,   68000, 2430, False),
            ('Bale Robe',      'Oromia',       7.1200,  40.0000,   55000, 1800, False),
            ('Gimbi',          'Oromia',       9.1700,  35.8300,   40000, 1900, False),
            ('Woliso',         'Oromia',       8.5300,  37.9800,   35000, 2000, False),
            ('Mojo',           'Oromia',       8.5900,  39.1200,   30000, 1700, False),
            ('Ziway',          'Oromia',       7.9300,  38.7100,   35000, 1640, False),
            ('Goba',           'Oromia',       7.0100,  39.9800,   30000, 2740, False),
            ('Bedele',         'Oromia',       8.4500,  36.3500,   25000, 2000, False),
            ('Metu',           'Oromia',       8.3000,  35.5800,   28000, 1700, False),
            ('Dembi Dolo',     'Oromia',       8.5300,  34.8000,   30000, 1500, False),
            ('Shambu',         'Oromia',       9.5700,  37.1000,   22000, 2200, False),
            ('Fiche',          'Oromia',       9.8000,  38.7300,   28000, 2750, False),
            ('Holeta',         'Oromia',       9.0500,  38.5000,   25000, 2400, False),
            ('Gebre Guracha',  'Oromia',       9.5800,  40.5200,   20000, 1900, False),
            ('Chiro',          'Oromia',       9.0800,  40.8700,   35000, 1750, False),
            ('Haramaya',       'Oromia',       9.4200,  42.0300,   25000, 1980, False),
            ('Moyale',         'Oromia',       3.5300,  39.0500,   20000,  900, False),
            ('Yabelo',         'Oromia',       4.8800,  38.0800,   18000, 1600, False),
            ('Negele Borana',  'Oromia',       5.3300,  39.5800,   22000, 1500, False),
            ('Buta Jira',      'Oromia',       8.1200,  38.3700,   20000, 2000, False),
            ('Welkite',        'Oromia',       8.2800,  37.7800,   25000, 1900, False),
            ('Sendafa',        'Oromia',       9.2200,  39.0300,   18000, 2600, False),
            # Amhara
            ('Bahir Dar',      'Amhara',      11.5900,  37.3900,  221991, 1800, False),
            ('Gondar',         'Amhara',      12.6000,  37.4700,  207044, 2200, False),
            ('Dessie',         'Amhara',      11.1300,  39.6400,  151000, 2470, False),
            ('Debre Birhan',   'Amhara',       9.6800,  39.5300,   65000, 2780, False),
            ('Debre Markos',   'Amhara',      10.3400,  37.7300,   80000, 2450, False),
            ('Woldia',         'Amhara',      11.8300,  39.6000,   45000, 1900, False),
            ('Lalibela',       'Amhara',      12.0300,  39.0500,   15000, 2630, False),
            ('Debre Tabor',    'Amhara',      11.8500,  38.0100,   40000, 2700, False),
            ('Kombolcha',      'Amhara',      11.0800,  39.7400,   60000, 1850, False),
            ('Bure',           'Amhara',      10.7000,  37.0700,   30000, 2100, False),
            ('Finote Selam',   'Amhara',      10.6900,  37.2700,   28000, 2000, False),
            ('Injibara',       'Amhara',      10.9800,  36.9500,   22000, 2600, False),
            ('Mota',           'Amhara',      11.0800,  37.8700,   20000, 2400, False),
            ('Debre Sina',     'Amhara',       9.8600,  39.7700,   18000, 2800, False),
            ('Hayk',           'Amhara',      11.3200,  39.6800,   15000, 2030, False),
            ('Kobo',           'Amhara',      12.1500,  39.6300,   20000, 1500, False),
            ('Sekota',         'Amhara',      12.6300,  39.0300,   12000, 1900, False),
            ('Metema',         'Amhara',      12.9600,  36.2000,   15000,  700, False),
            ('Addis Zemen',    'Amhara',      12.1200,  37.7900,   18000, 1900, False),
            ('Wereilu',        'Amhara',      10.6500,  39.4300,   12000, 2400, False),
            # Tigray
            ('Mekelle',        'Tigray',      13.4900,  39.4700,  215546, 2084, False),
            ('Axum',           'Tigray',      14.1200,  38.7200,   56500, 2131, False),
            ('Adwa',           'Tigray',      14.1700,  38.9000,   35000, 1900, False),
            ('Adigrat',        'Tigray',      14.2800,  39.4600,   60000, 2457, False),
            ('Shire',          'Tigray',      14.1000,  38.2800,   35000, 1900, False),
            ('Humera',         'Tigray',      14.2900,  36.5800,   20000,  600, False),
            ('Maychew',        'Tigray',      12.7800,  39.5300,   25000, 2480, False),
            ('Wukro',          'Tigray',      13.7800,  39.6000,   30000, 1900, False),
            ('Korem',          'Tigray',      12.5000,  39.5200,   15000, 2400, False),
            ('Alamata',        'Tigray',      12.4200,  39.5600,   20000, 1600, False),
            ('Hawzen',         'Tigray',      13.9700,  39.4600,   10000, 2100, False),
            # SNNPR
            ('Hawassa',        'SNNPR',        7.0600,  38.4800,  258808, 1708, False),
            ('Arba Minch',     'SNNPR',        6.0400,  37.5500,   74879, 1285, False),
            ('Wolaita Sodo',   'SNNPR',        6.8500,  37.7500,   80000, 1600, False),
            ('Hosaena',        'SNNPR',        7.5500,  37.8600,   55000, 2300, False),
            ('Dilla',          'SNNPR',        6.4100,  38.3100,   55000, 1580, False),
            ('Yirgalem',       'SNNPR',        6.7500,  38.4000,   25000, 1750, False),
            ('Bonga',          'SNNPR',        7.2700,  36.2400,   20000, 1720, False),
            ('Mizan Teferi',   'SNNPR',        6.9800,  35.5800,   25000, 1500, False),
            ('Jinka',          'SNNPR',        5.7800,  36.5600,   20000, 1490, False),
            ('Sawla',          'SNNPR',        6.3200,  36.8700,   15000, 1400, False),
            ('Boditi',         'SNNPR',        7.0000,  37.8700,   18000, 2000, False),
            ('Durame',         'SNNPR',        7.2300,  37.8800,   20000, 2100, False),
            ('Butajira',       'SNNPR',        8.1200,  38.3700,   25000, 2000, False),
            ('Yirga Chefe',    'SNNPR',        6.1500,  38.2000,   18000, 1800, False),
            ('Konso',          'SNNPR',        5.2500,  37.4800,   12000, 1650, False),
            # Somali
            ('Jigjiga',        'Somali',       9.3500,  42.8000,  125876, 1609, False),
            ('Gode',           'Somali',       5.9500,  43.5700,   35000,  295, False),
            ('Kebri Dahar',    'Somali',       6.7400,  44.2800,   20000,  500, False),
            ('Degehabur',      'Somali',       8.2200,  43.5600,   18000,  700, False),
            ('Warder',         'Somali',       6.9700,  45.3300,   12000,  500, False),
            ('Dolo Odo',       'Somali',       4.1700,  42.0700,   10000,  300, False),
            ('Kelafo',         'Somali',       5.6300,  44.1200,   12000,  300, False),
            ('Tog Wajaale',    'Somali',       9.6700,  43.4300,   15000,  900, False),
            # Afar
            ('Semera',         'Afar',        11.7900,  41.0100,   30000,  450, False),
            ('Asaita',         'Afar',        11.5700,  41.4300,   20000,  380, False),
            ('Dubti',          'Afar',        11.7300,  41.0800,   15000,  400, False),
            ('Logia',          'Afar',        11.7000,  41.0500,   12000,  420, False),
            ('Gewane',         'Afar',        10.1700,  40.6500,   10000,  750, False),
            ('Mille',          'Afar',        11.4300,  40.7700,   10000,  600, False),
            # Benshangul-Gumuz
            ('Assosa',         'Benshangul',  10.0700,  34.5300,   35000,  600, False),
            ('Bambasi',        'Benshangul',  10.7500,  34.7300,   10000,  700, False),
            ('Pawe',           'Benshangul',  11.3200,  36.3800,   15000,  900, False),
            ('Mandura',        'Benshangul',  10.8000,  35.5500,    8000,  800, False),
            ('Guba',           'Benshangul',  11.6000,  35.3500,    8000,  600, False),
            # Gambella
            ('Gambella',       'Gambella',     8.2500,  34.5900,   58432,  526, False),
            ('Itang',          'Gambella',     8.1500,  34.2700,   10000,  400, False),
            ('Abobo',          'Gambella',     7.8700,  34.5300,    8000,  450, False),
            ('Gog',            'Gambella',     8.2000,  34.7000,    6000,  500, False),
            # Harari
            ('Harar',          'Harari',       9.3100,  42.1200,  122000, 1885, False),
            ('Jugol',          'Harari',       9.3100,  42.1300,   30000, 1900, False),
            # Dire Dawa
            ('Dire Dawa',      'Dire Dawa',    9.5900,  41.8600,  341834, 1180, False),
            ('Legehare',       'Dire Dawa',    9.5800,  41.8700,   40000, 1200, False),
            ('Sabian',         'Dire Dawa',    9.6000,  41.8500,   35000, 1190, False),
        ]

        if not include_all_regions:
            major = {'Addis Ababa', 'Oromia', 'Amhara', 'Tigray', 'SNNPR'}
            CITY_DATA_filtered = [c for c in CITY_DATA if c[1] in major]
        else:
            CITY_DATA_filtered = CITY_DATA

        # Shuffle and pick up to num_cities
        random.shuffle(CITY_DATA_filtered)
        selected = CITY_DATA_filtered[:num_cities]

        # Always include Addis Ababa if possible
        has_addis = any(c[0] == 'Addis Ababa' for c in selected)
        if not has_addis:
            addis = next((c for c in CITY_DATA if c[0] == 'Addis Ababa'), None)
            if addis:
                selected[0] = addis

        # Add cities with exact coordinates
        for city_id, (name, region, lat, lon, pop, elev, is_cap) in enumerate(selected, start=1):
            city = City(
                id=city_id,
                name=name,
                region=region,
                latitude=lat,
                longitude=lon,
                population=pop,
                elevation=elev,
                is_capital=is_cap
            )
            self.add_city(city)

        # Generate roads — only connect cities within a realistic distance
        actual_city_count = len(self.cities)
        roads_generated = 0
        attempts = 0
        max_attempts = num_roads * 50
        # Max straight-line distance to allow a road (keeps map clean)
        MAX_ROAD_KM = 350

        while roads_generated < num_roads and attempts < max_attempts:
            city1_id = random.randint(1, actual_city_count)
            city2_id = random.randint(1, actual_city_count)
            attempts += 1

            if city1_id == city2_id:
                continue
            if self.get_road_between(city1_id, city2_id):
                continue

            city1 = self.cities.get(city1_id)
            city2 = self.cities.get(city2_id)
            if not city1 or not city2:
                continue

            # Straight-line distance
            straight = city1.distance_to(city2)

            # Skip if cities are too far apart — avoids cross-country chaos
            if straight > MAX_ROAD_KM:
                continue

            # Road distance is slightly longer than straight line
            distance = round(straight * random.uniform(1.1, 1.4), 2)

            # Road type based on distance
            if distance > 200:
                road_type = RoadType.HIGHWAY
            elif distance > 80:
                road_type = RoadType.NATIONAL
            else:
                road_type = RoadType.REGIONAL

            condition = random.choices(
                [RoadCondition.GOOD, RoadCondition.FAIR, RoadCondition.POOR],
                weights=[0.4, 0.4, 0.2]
            )[0]

            road = Road(
                id=0,
                city1_id=city1_id,
                city2_id=city2_id,
                distance=distance,
                road_type=road_type,
                condition=condition,
                speed_limit=100 if road_type == RoadType.HIGHWAY else 80,
                lanes=4 if road_type == RoadType.HIGHWAY else 2,
                name=f"R{roads_generated + 1}"
            )
            self.add_road(road)
            roads_generated += 1
    
    def get_adjacency_matrix(self) -> List[List[float]]:
        """
        Get the adjacency matrix (for algorithms)
        
        Returns:
            2D list of distances
        """
        return self.adjacency_matrix
    
    def get_city_list(self) -> List[City]:
        """
        Get list of all Ethiopian cities in ID order
        
        Returns:
            List of City objects
        """
        return [self.cities[cid] for cid in sorted(self.cities.keys())]
    
    def get_cities_by_region_summary(self) -> Dict[str, int]:
        """
        Get summary of cities by Ethiopian region
        
        Returns:
            Dictionary mapping region to count
        """
        summary = {}
        for city in self.cities.values():
            summary[city.region] = summary.get(city.region, 0) + 1
        return summary
    
    def to_dict(self) -> Dict:
        """
        Convert network to dictionary for serialization
        
        Returns:
            Dictionary representation
        """
        return {
            'cities': [city.to_dict() for city in self.cities.values()],
            'roads': [road.to_dict() for road in self.roads.values()]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RoadNetwork':
        """
        Create network from dictionary
        
        Args:
            data: Dictionary with cities and roads
            
        Returns:
            RoadNetwork object
        """
        network = cls()
        
        # Add cities
        for city_data in data['cities']:
            city = City.from_dict(city_data)
            network.add_city(city)
        
        # Add roads
        for road_data in data['roads']:
            road = Road.from_dict(road_data)
            network.add_road(road)
        
        return network
    
    def print_network_summary(self):
        """Print a summary of the Ethiopian road network"""
        print("\n" + "="*60)
        print("ETHIOPIAN ROAD NETWORK SUMMARY")
        print("="*60)
        print(f"Total Cities: {self.get_city_count()}")
        print(f"Total Roads: {self.get_road_count()}")
        print(f"Network Density: {self.get_density():.4f}")
        print(f"Average Connections per City: {self.get_average_degree():.2f}")
        
        # Region summary
        print("\nCities by Region:")
        region_summary = self.get_cities_by_region_summary()
        for region, count in sorted(region_summary.items()):
            print(f"  {region}: {count} cities")
        
        # Sample cities
        if self.get_city_count() > 0:
            print(f"\nSample Cities (first 5):")
            for i, city in enumerate(list(self.cities.values())[:5]):
                capital_mark = " (Capital)" if city.is_capital else ""
                print(f"  {i+1}. {city.name}, {city.region}{capital_mark}")
        
        # Sample roads
        if self.get_road_count() > 0:
            print(f"\nSample Roads (first 5):")
            for i, road in enumerate(list(self.roads.values())[:5]):
                city1 = self.get_city_by_id(road.city1_id)
                city2 = self.get_city_by_id(road.city2_id)
                print(f"  {i+1}. {city1.name} ↔ {city2.name}: {road.distance} km")


# Example usage
if __name__ == "__main__":
    # Create Ethiopian road network
    network = RoadNetwork()
    
    print("Generating Ethiopian road network...")
    network.generate_ethiopian_network(num_cities=50, num_roads=75)
    
    # Print summary
    network.print_network_summary()
    
    # Test adjacency matrix
    matrix = network.get_adjacency_matrix()
    print(f"\nAdjacency matrix size: {len(matrix)}x{len(matrix)}")
    
    # Test neighbor finding
    if network.get_city_count() > 0:
        first_city = list(network.cities.values())[0]
        print(f"\nNeighbors of {first_city.name}:")
        neighbors = network.get_neighbors(first_city.id)
        for neighbor_id, distance, road in neighbors[:5]:
            neighbor = network.get_city_by_id(neighbor_id)
            print(f"  → {neighbor.name}: {distance} km")