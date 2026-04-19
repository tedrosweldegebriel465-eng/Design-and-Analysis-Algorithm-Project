"""
Ethiopian GPS Navigation System
Main entry point for the application
Author: Tedros Weldegebriel
Date: 2026
"""

import sys
import os
import time
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
import logging

# Add src to path - FIXED: Add both root and src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, current_dir)
sys.path.insert(0, src_dir)

# FIXED: Better import handling with try/except
try:
    from src.logging_config import setup_logging
    from src.config import get_config
    from src.graph.network import RoadNetwork
    from src.graph.city import City
    from src.algorithms.dijkstra_array import DijkstraArray
    from src.algorithms.dijkstra_pq import DijkstraPriorityQueue
    from src.algorithms.a_star import AStarSearch
    from src.algorithms.path_utils import PathUtils
    from src.utils.data_loader import DataLoader
    from src.visualization.map_plotter import MapPlotter
    from src.visualization.graph_viz import GraphVisualizer
    from src.analysis.complexity import ComplexityAnalyzer
    from src.analysis.report_gen import ReportGenerator
except ImportError as e:
    # Fallback to plain prints here because logging may not be configured yet
    print(f"Import error: {e}")
    print("Make sure all modules are in the correct location:")
    print("   src/graph/")
    print("   src/algorithms/")
    print("   src/utils/")
    print("   src/visualization/")
    print("   src/analysis/")
    sys.exit(1)


class EthiopianGPSNavigation:
    """
    Main Ethiopian GPS Navigation System Class
    Integrates all components with Ethiopian-specific features
    """
    
    def __init__(self):
        """Initialize the GPS Navigation System"""
        self.logger = logging.getLogger(self.__class__.__name__)

        self.network = None
        self.source_city = None
        self.distances = None
        self.parents = None
        self.a_star_distance = None
        self.a_star_path = None
        self.routing_preference = "distance"  # or "time"
        self.path_utils = None
        self.last_destination_city = None
        self.last_computed_path = None
        
        # System configuration
        self.config = get_config()
        
        # Create output directories
        self._create_output_dirs()
        
        self._print_banner()
    
    def _create_output_dirs(self):
        """Create necessary output directories"""
        base_output = self.config.output_dir
        dirs = [
            os.path.join(base_output, 'visualizations/maps'),
            os.path.join(base_output, 'visualizations/graphs'),
            os.path.join(base_output, 'visualizations/charts'),
            os.path.join(base_output, 'visualizations/animations'),
            os.path.join(base_output, 'reports/text'),
            os.path.join(base_output, 'reports/html'),
            os.path.join(base_output, 'reports/json'),
            os.path.join(base_output, 'reports/csv'),
            os.path.join(base_output, 'reports/pdf'),
        ]
        
        for d in dirs:
            try:
                os.makedirs(d, exist_ok=True)
            except Exception as e:
                self.logger.warning("Could not create directory %s: %s", d, e)
    
    def _print_banner(self):
        """Print system banner"""
        print("=" * 80)
        print(f"     ETHIOPIAN GPS NAVIGATION SYSTEM v{self.config.version}")
        print("=" * 80)
        print("  Dijkstra's Algorithm Implementation for Ethiopian Road Networks")
        print("  Features: 100+ Cities | 500+ Roads | Interactive Maps | Reports")
        print("=" * 80)
    
    def run(self):
        """Main application loop"""
        while True:
            self._print_menu()
            choice = input("\nEnter your choice (1-11, 0 to exit): ").strip()
            
            if choice == '1':
                self._load_ethiopian_dataset()
            elif choice == '2':
                self._generate_random_network()
            elif choice == '3':
                self._select_source_city()
            elif choice == '4':
                self._run_dijkstra()
            elif choice == '5':
                self._show_shortest_paths()
            elif choice == '6':
                self._visualize_map()
            elif choice == '7':
                self._visualize_graph()
            elif choice == '8':
                self._analyze_complexity()
            elif choice == '9':
                self._generate_reports()
            elif choice == '10':
                self._run_demonstration()
            elif choice == '11':
                self._launch_dashboard()
            elif choice == '0':
                self._exit_system()
            else:
                print("Invalid choice. Please try again (1-11 or 0).")
    
    def _print_menu(self):
        """Print main menu"""
        print("\n" + "=" * 50)
        print("MAIN MENU")
        print("=" * 50)
        print("1. Load Ethiopian cities dataset")
        print("2. Generate random Ethiopian road network")
        print("3. Select source city")
        print("4. Run Routing Algorithms (Dijkstra vs A*)")
        print("5. Show shortest paths")
        print("6. Visualize on map")
        print("7. Visualize graph")
        print("8. Analyze complexity")
        print("9. Generate reports")
        print("10. Run complete demonstration")
        print("11. Launch Web Dashboard")
        print("0. Exit")
        
        if self.network:
            try:
                print(f"\nCurrent Status:")
                print(f"   Network: {self.network.get_city_count()} cities, {self.network.get_road_count()} roads")
                if self.source_city:
                    print(f"   Source: {self.source_city.name}")
            except Exception as e:
                print(f"   Could not get network stats: {e}")
    
    def _load_ethiopian_dataset(self):
        """Load Ethiopian cities dataset"""
        print("\nLoading Ethiopian Cities Dataset")
        print("-" * 40)
        
        try:
            loader = DataLoader(data_dir=str(self.config.data_dir))

            # Always prefer curated CSV files for deterministic, real coordinates/roads.
            try:
                self.network = loader.create_network_from_files(
                    cities_file="ethiopian_cities_validated.csv",
                    roads_file="ethiopia_road_network_validated.csv"
                )
            except FileNotFoundError:
                self.network = loader.create_network_from_files(
                    cities_file="ethiopian_cities_clean.csv",
                    roads_file="ethiopia_road_network.csv"
                )
            print("\nSuccessfully loaded Ethiopian dataset from CSV files!")
            try:
                loader.save_network_to_database(self.network)
                self.logger.info("Network saved to database.")
            except Exception as db_err:
                self.logger.warning("Could not save network to database: %s", db_err)
            
        except FileNotFoundError as e:
            print(f"\nDataset files not found: {e}")
            print("   Generating sample network instead...")
            self._generate_random_network()
        except Exception as e:
            print(f"\nError loading dataset: {e}")
            print("   Generating sample network instead...")
            self._generate_random_network()
        
        if self.network:
            self.path_utils = PathUtils(self.network)
    
    def _generate_random_network(self):
        """Generate random Ethiopian road network"""
        print("\nGenerating Ethiopian Road Network")
        print("-" * 40)
        print("Note: This mode creates synthetic data for testing only.")
        print("  For exact real-world routing, use option 1 (Load Ethiopian dataset).")
        
        try:
            num_cities_input = input("Enter number of cities (default 100): ").strip()
            num_cities = int(num_cities_input) if num_cities_input else 100
            
            num_roads_input = input("Enter number of roads (default 500): ").strip()
            num_roads = int(num_roads_input) if num_roads_input else 500
            
        except ValueError:
            print("Invalid input. Using defaults.")
            num_cities, num_roads = 100, 500
        
        try:
            self.network = RoadNetwork()
            self.network.generate_ethiopian_network(
                num_cities=max(num_cities, 10),  # Reduced min for testing
                num_roads=max(num_roads, 20)      # Reduced min for testing
            )
            
            self.path_utils = PathUtils(self.network)
            self.network.print_network_summary()
            
        except Exception as e:
            print(f"Error generating network: {e}")
            import traceback
            traceback.print_exc()
    
    def _select_source_city(self):
        """Select source city"""
        if not self.network:
            print("Please load a network first!")
            return
        
        print("\nSelect Source City")
        print("-" * 40)
        
        # Show available cities
        cities = list(self.network.cities.values())
        if not cities:
            print("No cities in network!")
            return
        
        print(f"\nAvailable cities (first 20 of {len(cities)}):")
        for i, city in enumerate(cities[:20], 1):
            capital = " (Capital)" if hasattr(city, 'is_capital') and city.is_capital else ""
            print(f"   {i}. {city.name}, {city.region}{capital}")
        
        # Let user select
        while True:
            choice = input("\nEnter city name or number (or 'list' for more): ").strip()
            
            if not choice:
                continue
            
            if choice.lower() == 'list':
                # Show more cities
                for i, city in enumerate(cities[20:40], 21):
                    print(f"   {i}. {city.name}, {city.region}")
                continue
            
            # Try number input
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(cities):
                    self.source_city = cities[idx]
                    break
                else:
                    print(f"Number must be between 1 and {len(cities)}")
            
            # Try name input
            else:
                city = self.network.get_city_by_name(choice)
                if city:
                    self.source_city = city
                    break
                else:
                    print(f"City '{choice}' not found. Try again.")
        
        print(f"\nSource city set to: {self.source_city.name}")
    
    def _run_dijkstra(self):
        """Run Dijkstra's algorithm"""
        if not self.network or not self.source_city:
            print("Please load network and select source city first!")
            return
        
        print(f"\nRunning Routing Algorithms from {self.source_city.name}")
        print("-" * 40)
        
        # Ensure we have a destination for A*
        dest_city = None
        cities = list(self.network.cities.values())
        print("\nTo compare A* efficiently, please select a destination city.")
        print("If you skip, A* will default to a random far city.")
        
        choice = input("Enter destination city name or number (or press Enter to skip): ").strip()
        if choice:
            if choice.isdigit() and 1 <= int(choice) <= len(cities):
                dest_city = cities[int(choice) - 1]
            else:
                city = self.network.get_city_by_name(choice)
                if city:
                    dest_city = city
        
        if not dest_city:
            # Pick a destination that is not the source
            for city in reversed(cities):
                if city.id != self.source_city.id:
                    dest_city = city
                    break
                    
        print(f"\nDestination selected: {dest_city.name}")
        self.last_destination_city = dest_city
        
        # Ask for routing preference
        print("\nRouting Preference:")
        print("1. Shortest Distance (km)")
        print("2. Fastest Time (hours) - Considering speed limits and condition")
        pref_choice = input("Enter choice (1/2, default 1): ").strip()
        
        self.routing_preference = "time" if pref_choice == '2' else "distance"
        
        # Determine weight function and units
        if self.routing_preference == "time":
            weight_func = lambda road: road.get_travel_time()
            metric_name = "Travel Time"
            unit = "hours"
        else:
            weight_func = None  # Default is distance
            metric_name = "Distance"
            unit = "km"
        
        print(f"\nOptimization target: {metric_name}")
        
        try:
            # --- Array Implementation ---
            print("\nDijkstra Array (O(V^2))...")
            array_dijkstra = DijkstraArray(self.network)
            start = time.time()
            self.distances, self.parents = array_dijkstra.find_shortest_paths(
                self.source_city.id, record_steps=True, weight_func=weight_func
            )
            array_time = (time.time() - start) * 1000
            
            # --- PQ Implementation ---
            print("Dijkstra Priority Queue (O((V+E) log V))...")
            pq_dijkstra = DijkstraPriorityQueue(self.network)
            start = time.time()
            pq_distances, pq_parents = pq_dijkstra.find_shortest_paths(self.source_city.id, weight_func=weight_func)
            pq_time = (time.time() - start) * 1000
            
            # --- A* Implementation ---
            print("A* Search Algorithm...")
            a_star = AStarSearch(self.network)
            start = time.time()
            self.a_star_distance, self.a_star_path = a_star.find_shortest_path_to(
                self.source_city.id, dest_city.id, weight_func=weight_func
            )
            astar_time = (time.time() - start) * 1000
            self.last_computed_path = self.a_star_path if self.a_star_path else None
            
            # --- Show Comparison ---
            print(f"\nPerformance Comparison (Routing to {dest_city.name}):")
            print(f"   Dijkstra Array : {array_time:.2f} ms")
            print(f"   Dijkstra PQ    : {pq_time:.2f} ms")
            print(f"   A* Search      : {astar_time:.2f} ms")
            
            # Node Expansion Comparison
            print(f"\nSearch Operations:")
            print(f"   Dijkstra PQ    : {pq_dijkstra.get_operation_count()} operations")
            print(f"   A* Search      : {a_star.get_operation_count()} operations")
            
            if a_star.get_operation_count() > 0:
                speedup = pq_dijkstra.get_operation_count() / a_star.get_operation_count()
                print(f"   A* expanded {speedup:.1f}x fewer nodes than Dijkstra!")
            else:
                print("   A* expanded fewer nodes than Dijkstra!")
            
            # Show comparison
            print(f"\nPerformance Comparison:")
            print(f"   Array: {array_time:.2f} ms")
            print(f"   Priority Queue: {pq_time:.2f} ms")
            if pq_time > 0:
                print(f"   Speedup: {array_time/pq_time:.2f}x")
            else:
                print(f"   Speedup: N/A")
            
            # Verify results match
            if self.distances and pq_distances:
                matches = 0
                total = 0
                for cid in self.distances:
                    if cid in pq_distances:
                        total += 1
                        if (self.distances[cid] == float('inf') and pq_distances[cid] == float('inf')) or \
                           (abs(self.distances[cid] - pq_distances[cid]) < 0.01):
                            matches += 1
                print(f"\nResults match for {matches}/{total} cities")
            
        except Exception as e:
            print(f"Error running Dijkstra: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_shortest_paths(self):
        """Show shortest paths from source"""
        if not self.distances or not self.parents:
            print("Please run Dijkstra's algorithm first!")
            return
        if not self.path_utils:
            print("Path utils not initialized!")
            return
        
        print(f"\nShortest Paths from {self.source_city.name}")
        print("-" * 70)
        
        try:
            # Get reachable cities
            reachable = []
            for cid, dist in self.distances.items():
                if cid != self.source_city.id and dist != float('inf'):
                    reachable.append((cid, dist))
            
            reachable.sort(key=lambda x: x[1])
            
            print(f"\nStatistics:")
            print(f"   Reachable cities: {len(reachable)}")
            print(f"   Unreachable cities: {self.network.get_city_count() - len(reachable) - 1}")
            
            if reachable:
                closest_city = self.network.get_city_by_id(reachable[0][0])
                farthest_city = self.network.get_city_by_id(reachable[-1][0])
                print(f"   Closest city: {closest_city.name if closest_city else 'Unknown'} ({reachable[0][1]:.2f} km)")
                print(f"   Farthest city: {farthest_city.name if farthest_city else 'Unknown'} ({reachable[-1][1]:.2f} km)")
            
            # Show top 10 shortest paths
            if hasattr(self, 'routing_preference') and self.routing_preference == "time":
                metric_col = "Time (hrs)"
            else:
                metric_col = "Distance"
                
            print(f"\nTop 10 Paths:")
            print(f"{'#':<3} {'Destination':<20} {metric_col:<12} {'Path'}")
            print("-" * 70)
            
            for i, (city_id, distance) in enumerate(reachable[:10], 1):
                city = self.network.get_city_by_id(city_id)
                if not city:
                    continue
                    
                path_ids = self.path_utils.reconstruct_path(self.parents, self.source_city.id, city_id)
                path_str = self.path_utils.get_path_string(path_ids)
                if len(path_str) > 35:
                    path_str = path_str[:32] + "..."
                print(f"{i:<3} {city.name:<20} {distance:<12.2f} {path_str}")
                
        except Exception as e:
            print(f"Error showing paths: {e}")
    
    def _visualize_map(self):
        """Create map visualization"""
        if not self.network:
            print("Please load a network first!")
            return
        
        print("\nCreating Map Visualization")
        print("-" * 40)
        
        try:
            plotter = MapPlotter(self.network)
            
            # Get path to highlight if available
            highlight_path = None
            map_title = "Ethiopian Road Network"
            show_roads = False

            # Prefer the exact latest route selected by user.
            if self.last_computed_path and len(self.last_computed_path) > 1 and self.source_city and self.last_destination_city:
                highlight_path = self.last_computed_path
                map_title = f"Route: {self.source_city.name} -> {self.last_destination_city.name}"
            elif self.source_city and self.distances and self.parents and self.path_utils:
                dest_input = input("Enter destination city for map (required): ").strip()
                dest_city = self.network.get_city_by_name(dest_input) if dest_input else None
                if not dest_city:
                    print("Destination city is required to avoid misleading map output.")
                    print("  Run option 4 first or enter a valid destination.")
                    return
                highlight_path = self.path_utils.reconstruct_path(
                    self.parents, self.source_city.id, dest_city.id
                )
                if not highlight_path:
                    print(f"No route found from {self.source_city.name} to {dest_city.name}.")
                    return
                self.last_destination_city = dest_city
                self.last_computed_path = highlight_path
                map_title = f"Route: {self.source_city.name} -> {dest_city.name}"
            else:
                print("No computed route available.")
                print("  Run option 4 (Routing Algorithms) first, then visualize map.")
                return
            
            # Generate filename with timestamp (use configured output directory)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(
                str(self.config.output_dir),
                "visualizations",
                "maps",
                f"ethiopia_map_{timestamp}.html",
            )
            
            # Create map
            plotter.create_interactive_map(
                title=map_title,
                show_cities=True,
                show_roads=show_roads,
                highlight_path=highlight_path,
                output_file=filename
            )
            
            print(f"Map saved to: {filename}")
            
        except Exception as e:
            print(f"Error creating map: {e}")
            import traceback
            traceback.print_exc()
    
    def _visualize_graph(self):
        """Create graph visualization"""
        if not self.network:
            print("Please load a network first!")
            return
        
        print("\nCreating Graph Visualization")
        print("-" * 40)
        
        try:
            viz = GraphVisualizer(self.network)
            
            # Get path to highlight
            highlight_path = None
            if self.source_city and self.distances and self.parents and self.path_utils:
                reachable = []
                for cid, dist in self.distances.items():
                    if cid != self.source_city.id and dist != float('inf'):
                        reachable.append((cid, dist))
                
                if reachable:
                    farthest_id = max(reachable, key=lambda x: x[1])[0]
                    highlight_path = self.path_utils.reconstruct_path(
                        self.parents, self.source_city.id, farthest_id
                    )
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Spring layout
            viz.set_layout('spring')
            spring_path = os.path.join(
                str(self.config.output_dir),
                "visualizations",
                "graphs",
                f"spring_{timestamp}.png",
            )
            viz.draw_graph(
                title="Ethiopian Road Network - Spring Layout",
                node_color_by='region',
                edge_color_by='type',
                show_labels=True,
                highlight_path=highlight_path,
                save_path=spring_path
            )
            print(f"Spring layout graph saved to: {spring_path}")
            
            # Geographic layout
            viz.set_layout('geographic')
            geo_path = os.path.join(
                str(self.config.output_dir),
                "visualizations",
                "graphs",
                f"geo_{timestamp}.png",
            )
            viz.draw_graph(
                title="Ethiopian Road Network - Geographic Layout",
                node_color_by='population',
                edge_color_by='condition',
                show_labels=True,
                highlight_path=highlight_path,
                save_path=geo_path
            )
            print(f"Geographic layout graph saved to: {geo_path}")
            
        except Exception as e:
            print(f"Error creating graph: {e}")
            import traceback
            traceback.print_exc()
    
    def _analyze_complexity(self):
        """Analyze algorithm complexity"""
        if not self.network:
            print("Please load a network first!")
            return
        
        print("\nComplexity Analysis")
        print("-" * 40)
        
        try:
            analyzer = ComplexityAnalyzer(self.network)
            analyzer.print_analysis()
        except Exception as e:
            print(f"Error analyzing complexity: {e}")
    
    def _generate_reports(self):
        """Generate comprehensive reports"""
        if not self.network:
            print("Please load a network first!")
            return
        
        print("\nGenerating Reports")
        print("-" * 40)
        
        try:
            if not self.source_city:
                print("No source city selected. Reports will not include path data.")
                source_id = None
            else:
                source_id = self.source_city.id
            
            reporter = ReportGenerator(self.network, source_id)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            base_reports_dir = os.path.join(str(self.config.output_dir), "reports")
            
            # Generate text report
            print("Generating text report...")
            text_report = reporter.generate_text_report()
            text_path = os.path.join(
                base_reports_dir,
                "text",
                f"report_{timestamp}.txt",
            )
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_report)
            print(f"   Saved to: {text_path}")
            
            # Generate HTML report
            print("Generating HTML report...")
            html_path = os.path.join(
                base_reports_dir,
                "html",
                f"report_{timestamp}.html",
            )
            reporter.generate_html_report(html_path)
            print(f"   Saved to: {html_path}")
            
            # Generate JSON report
            print("Generating JSON report...")
            json_path = os.path.join(
                base_reports_dir,
                "json",
                f"report_{timestamp}.json",
            )
            reporter.generate_json_report(json_path)
            print(f"   Saved to: {json_path}")
            
            # Generate CSV reports
            print("Generating CSV reports...")
            csv_dir = os.path.join(base_reports_dir, "csv")
            reporter.generate_csv_report(csv_dir)
            print(f"   Saved to: {csv_dir}/")
            
            print(f"\nAll reports saved to {base_reports_dir}/")
            
        except Exception as e:
            print(f"Error generating reports: {e}")
            import traceback
            traceback.print_exc()
    
    def _run_demonstration(self):
        """Run complete demonstration"""
        print("\nRunning Complete Demonstration")
        print("=" * 60)
        
        try:
            # Step 1: Load or generate network
            print("\n1. Setting up Ethiopian road network...")
            if not self.network:
                self._generate_random_network()
            
            if not self.network:
                print("Failed to create network!")
                return
            
            # Step 2: Select source city (Addis Ababa if available)
            print("\n2. Selecting source city...")
            addis = self.network.get_city_by_name("Addis Ababa")
            if addis:
                self.source_city = addis
            else:
                # Find any capital city
                for city in self.network.cities.values():
                    if hasattr(city, 'is_capital') and city.is_capital:
                        self.source_city = city
                        break
                if not self.source_city:
                    # Just pick the first city
                    self.source_city = list(self.network.cities.values())[0]
            
            print(f"   Source: {self.source_city.name}")
            
            # Step 3: Run Dijkstra
            print("\n3. Running Dijkstra's algorithm...")
            self._run_dijkstra()
            
            # Step 4: Show paths
            print("\n4. Displaying shortest paths...")
            self._show_shortest_paths()
            
            # Step 5: Create visualizations
            print("\n5. Creating visualizations...")
            self._visualize_map()
            self._visualize_graph()
            
            # Step 6: Analyze complexity
            print("\n6. Analyzing complexity...")
            self._analyze_complexity()
            
            # Step 7: Generate reports
            print("\n7. Generating reports...")
            self._generate_reports()
            
            print("\n" + "=" * 60)
            print("Demonstration Complete!")
            print("Check the 'output' directory for results")
            print("=" * 60)
            
        except Exception as e:
            print(f"\nError in demonstration: {e}")
            import traceback
            traceback.print_exc()
    
    def _launch_dashboard(self):
        """Launch the web dashboard"""
        print("\nLaunching Web Dashboard...")
        print("   The server will run on http://127.0.0.1:5000/dashboard")
        print("   Starting server in the background...")
        
        try:
            import subprocess
            import webbrowser
            import sys
            
            # Start web_app.py as a separate process
            server_process = subprocess.Popen(
                [sys.executable, "-m", "src.web_app"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            print("   Server started (PID: {}).".format(server_process.pid))
            print("   Opening browser...")
            time.sleep(2)  # Give the server a moment to start
            webbrowser.open("http://127.0.0.1:5000/dashboard")
            
            input("\n   Press ENTER to stop the server and return to the menu...")
            
            server_process.terminate()
            server_process.wait(timeout=5)
            print("   Server stopped.")
            
        except Exception as e:
            print(f"Error launching web dashboard: {e}")
            import traceback
            traceback.print_exc()

    def _exit_system(self):
        """Exit the system"""
        print("\nThank you for using Ethiopian GPS Navigation System!")
        print("   Generated outputs saved in 'output' directory")
        print("   Goodbye!")
        sys.exit(0)


def main():
    """Main entry point"""
    try:
        # Initialize logging before creating the system
        setup_logging()

        system = EthiopianGPSNavigation()
        system.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()