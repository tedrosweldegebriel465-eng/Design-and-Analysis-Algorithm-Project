"""
test_run.py - Quick test script for Ethiopian GPS Navigation System
Run this first to verify all modules are working correctly
"""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')

# Add both directories to path
sys.path.insert(0, current_dir)
sys.path.insert(0, src_dir)

print("="*60)
print(" TESTING ETHIOPIAN GPS NAVIGATION SYSTEM")
print("="*60)
print(f" Current directory: {current_dir}")
print(f" Src directory: {src_dir}")
print(f" Python path: {sys.path[0]}")
print("-"*60)

# Test counters
passed = 0
failed = 0
tests = []

def run_test(test_name, test_func):
    """Run a single test and track results"""
    global passed, failed
    try:
        test_func()
        print(f" {test_name}")
        passed += 1
        tests.append((test_name, True, None))
    except Exception as e:
        print(f" {test_name}: {e}")
        failed += 1
        tests.append((test_name, False, str(e)))

print("\n Running Module Tests...")
print("-"*60)

# Test 1: Graph module
def test_graph():
    from src.graph.city import City
    from src.graph.road import Road, RoadType, RoadCondition
    from src.graph.network import RoadNetwork
    
    # Test City creation
    city = City(1, "Addis Ababa", "Addis Ababa", 9.03, 38.74, 3500000, 2355, True)
    assert city.name == "Addis Ababa"
    assert city.latitude == 9.03
    
    # Test Road creation
    road = Road(1, 1, 2, 85, RoadType.HIGHWAY, RoadCondition.GOOD)
    assert road.distance == 85
    
    # Test Network
    network = RoadNetwork()
    network.add_city(city)
    assert network.get_city_count() == 1

run_test("Graph Module", test_graph)

# Test 2: Algorithms module - FIXED
def test_algorithms():
    from src.algorithms.dijkstra_array import DijkstraArray
    from src.algorithms.dijkstra_pq import DijkstraPriorityQueue
    from src.algorithms.path_utils import PathUtils
    from src.graph.network import RoadNetwork
    from src.graph.city import City  # IMPORTANT: Need to import City
    
    # Create simple network
    network = RoadNetwork()
    city1 = City(1, "City1", "Test", 0, 0)
    city2 = City(2, "City2", "Test", 1, 1)
    network.add_city(city1)
    network.add_city(city2)
    
    # Test DijkstraArray
    dijkstra = DijkstraArray(network)
    assert dijkstra is not None
    
    # Test DijkstraPriorityQueue
    pq_dijkstra = DijkstraPriorityQueue(network)
    assert pq_dijkstra is not None
    
    # Test PathUtils
    path_utils = PathUtils(network)
    assert path_utils is not None
    
    # Test basic functionality
    distances, parents = dijkstra.find_shortest_paths(1)
    assert distances is not None

run_test("Algorithms Module", test_algorithms)

# Test 3: Utils module
def test_utils():
    from src.utils.data_loader import DataLoader
    from src.utils.distance_calc import DistanceCalculator
    from src.utils.validators import Validators
    
    # Test DistanceCalculator
    dist = DistanceCalculator.haversine(9.03, 38.74, 13.50, 39.47)
    assert dist > 0
    print(f"   📏 Haversine distance: {dist:.2f} km")
    
    # Test Validators
    is_valid, _ = Validators.validate_city_name("Addis Ababa")
    assert is_valid
    
    # Test DataLoader
    loader = DataLoader()
    assert loader is not None

run_test("Utils Module", test_utils)

# Test 4: Visualization module
def test_visualization():
    from src.visualization.map_plotter import MapPlotter
    from src.visualization.graph_viz import GraphVisualizer
    from src.graph.network import RoadNetwork
    from src.graph.city import City
    
    network = RoadNetwork()
    city = City(1, "Test", "Test", 0, 0)
    network.add_city(city)
    
    plotter = MapPlotter(network)
    assert plotter is not None
    
    viz = GraphVisualizer(network)
    assert viz is not None

run_test("Visualization Module", test_visualization)

# Test 5: Analysis module
def test_analysis():
    from src.analysis.complexity import ComplexityAnalyzer
    from src.analysis.report_gen import ReportGenerator
    from src.graph.network import RoadNetwork
    from src.graph.city import City
    
    network = RoadNetwork()
    city = City(1, "Test", "Test", 0, 0)
    network.add_city(city)
    
    analyzer = ComplexityAnalyzer(network)
    assert analyzer is not None
    
    reporter = ReportGenerator(network)
    assert reporter is not None

run_test("Analysis Module", test_analysis)

# Test 6: Import main
def test_main():
    import main
    assert main is not None

run_test("Main Module", test_main)

# Test 7: Check for required packages
def test_packages():
    required_packages = [
        'numpy', 'pandas', 'matplotlib', 'folium', 
        'networkx', 'jinja2'
    ]
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        raise Exception(f"Missing required packages: {', '.join(missing)}")

run_test("Required Packages", test_packages)

# Test 8: Check file structure
def test_file_structure():
    required_files = [
        'src/graph/__init__.py',
        'src/graph/city.py',
        'src/graph/road.py',
        'src/graph/network.py',
        'src/algorithms/__init__.py',
        'src/algorithms/dijkstra_array.py',
        'src/algorithms/dijkstra_pq.py',
        'src/algorithms/path_utils.py',
        'src/utils/__init__.py',
        'src/utils/data_loader.py',
        'src/utils/distance_calc.py',
        'src/utils/validators.py',
        'src/visualization/__init__.py',
        'src/visualization/map_plotter.py',
        'src/visualization/graph_viz.py',
        'src/analysis/__init__.py',
        'src/analysis/complexity.py',
        'src/analysis/report_gen.py',
        'main.py'
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    if missing:
        raise Exception(f"Missing files: {', '.join(missing)}")

run_test("File Structure", test_file_structure)

# Summary
print("\n" + "="*60)
print(" TEST SUMMARY")
print("="*60)
print(f" Passed: {passed}")
print(f" Failed: {failed}")
print(f" Total: {passed + failed}")
print("-"*60)

if failed == 0:
    print("\n ALL TESTS PASSED! Your project is ready to run!")
    print("\n Next steps:")
    print("   1. Run: python main.py")
    print("   2. Choose option 2 to generate a network")
    print("   3. Choose option 3 to select a source city")
    print("   4. Choose option 4 to run Dijkstra")
    print("   5. Choose option 6 to see the map in your browser!")
else:
    print("\n  Some tests failed. Common fixes:")
    print("   1. Make sure all files are in correct locations")
    print("   2. Install required packages: pip install -r requirements.txt")
    print("   3. Check that you're running from project root")
    print("\n Expected structure:")
    print("   GPS_Navigation_Project/")
    print("   ├── src/")
    print("   │   ├── graph/")
    print("   │   ├── algorithms/")
    print("   │   ├── utils/")
    print("   │   ├── visualization/")
    print("   │   └── analysis/")
    print("   ├── main.py")
    print("   └── test_run.py")
    
    # Show detailed failures
    print("\n Detailed failures:")
    for test_name, success, error in tests:
        if not success:
            print(f"   • {test_name}: {error}")

print("="*60)