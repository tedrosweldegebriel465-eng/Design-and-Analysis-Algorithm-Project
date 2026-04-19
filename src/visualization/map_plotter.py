"""
Map Plotter - Visualize Ethiopian cities and roads on real maps
Uses folium for interactive maps and matplotlib for static maps
"""

import sys
import os
import webbrowser
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.network import RoadNetwork
from src.graph.city import City
from src.graph.road import Road

# Try importing visualization libraries with helpful error messages
try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("⚠️  folium not installed. Install with: pip install folium")

try:
    import matplotlib.pyplot as plt
    import matplotlib.lines as mlines
    from matplotlib.patches import Circle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlib not installed. Install with: pip install matplotlib")

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False


class MapPlotter:
    """
    Class for visualizing Ethiopian road networks on interactive and static maps
    
    Features:
    - Interactive maps with folium (clickable cities, popup info)
    - Static maps with matplotlib for reports
    - Path highlighting
    - City markers with population-based sizing
    - Road coloring by type and condition
    """
    
    # Ethiopian region colors for consistent mapping
    REGION_COLORS = {
        'Addis Ababa': '#FF0000',  # Red
        'Oromia': '#00FF00',        # Green
        'Amhara': '#0000FF',        # Blue
        'Tigray': '#FFFF00',        # Yellow
        'SNNPR': '#FF00FF',         # Magenta
        'Dire Dawa': '#00FFFF',     # Cyan
        'Harari': '#FFA500',        # Orange
        'Somali': '#800080',        # Purple
        'Gambella': '#A52A2A',      # Brown
        'Benshangul': '#808000',    # Olive
        'Afar': '#FFC0CB'           # Pink
    }
    
    # Road type colors
    ROAD_COLORS = {
        'highway': '#FF0000',        # Red
        'national': '#0000FF',       # Blue
        'regional': '#00FF00',        # Green
        'local': '#808080',           # Gray
        'gravel': '#A52A2A',          # Brown
        'rural': '#FFA500'            # Orange
    }
    
    def __init__(self, network: RoadNetwork):
        """
        Initialize map plotter with Ethiopian road network
        
        Args:
            network: RoadNetwork object containing Ethiopian cities and roads
        """
        self.network = network
        self.map = None
        self.fig = None
        self.ax = None
        
        # Ethiopia bounds for map centering
        self.ethiopia_bounds = {
            'min_lat': 3.0,
            'max_lat': 15.0,
            'min_lon': 33.0,
            'max_lon': 48.0,
            'center_lat': 9.0,
            'center_lon': 38.5
        }
    
    def create_interactive_map(self,
                              title: str = "Ethiopian Road Network",
                              show_cities: bool = True,
                              show_roads: bool = True,
                              highlight_path: Optional[List[int]] = None,
                              output_file: Optional[str] = None) -> Optional[folium.Map]:
        """
        Create an interactive folium map of Ethiopian road network
        
        Args:
            title: Map title
            show_cities: Whether to show city markers
            show_roads: Whether to show roads
            highlight_path: List of city IDs to highlight as a path
            output_file: Path to save HTML file (if None, generates temp file)
            
        Returns:
            folium.Map object or None if folium not available
        """
        if not FOLIUM_AVAILABLE:
            print("❌ folium is required for interactive maps")
            return None
        
        # Create base map centered on Ethiopia
        self.map = folium.Map(
            location=[self.ethiopia_bounds['center_lat'],
                     self.ethiopia_bounds['center_lon']],
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Add title
        title_html = f'''
            <h3 align="center" style="font-size:16px">
                <b>{title}</b>
            </h3>
        '''
        self.map.get_root().html.add_child(folium.Element(title_html))
        
        # Add fullscreen button
        plugins.Fullscreen().add_to(self.map)
        
        # Add mouse position
        plugins.MousePosition().add_to(self.map)
        
        # Add cities if requested
        if show_cities:
            self._add_cities_to_map()
        
        # Add roads if requested
        if show_roads:
            self._add_roads_to_map()
        
        # Add highlighted path if requested
        if highlight_path:
            self._add_path_to_map(highlight_path)
        
        # Add layer control
        folium.LayerControl().add_to(self.map)
        
        # Add minimap
        plugins.MiniMap().add_to(self.map)
        
        # Add measure control
        plugins.MeasureControl(position='bottomleft').add_to(self.map)
        
        # Add draw tools
        plugins.Draw(export=True).add_to(self.map)
        
        # Save and open map
        if output_file:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            self.map.save(output_file)
            print(f"✅ Map saved to: {output_file}")
            webbrowser.open(f'file://{os.path.abspath(output_file)}')
        else:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
                self.map.save(tmp.name)
                print(f"✅ Temporary map created: {tmp.name}")
                webbrowser.open(f'file://{tmp.name}')
        
        return self.map
    
    def _add_cities_to_map(self):
        """Add Ethiopian cities as markers to the map"""
        # Create feature group for cities
        city_group = folium.FeatureGroup(name='Cities', show=True)
        
        for city in self.network.cities.values():
            # Determine marker color based on region or capital status
            if city.is_capital:
                color = 'gold'
            else:
                color = self.REGION_COLORS.get(city.region, 'blue')
            
            # Determine marker size based on population
            if city.population:
                if city.population > 1_000_000:
                    radius = 12
                elif city.population > 500_000:
                    radius = 10
                elif city.population > 100_000:
                    radius = 8
                else:
                    radius = 5
            else:
                radius = 5
            
            # FIXED: Format population properly - split into multiple lines
            if city.population:
                population_str = f"{city.population:,}"
            else:
                population_str = "N/A"
            
            # FIXED: Handle elevation
            elevation_str = f"{city.elevation}" if city.elevation else "N/A"
            
            # Create popup HTML with city information
            popup_html = f"""
            <div style="font-family: Arial; width: 200px;">
                <h4>{city.name}</h4>
                <hr>
                <b>Region:</b> {city.region}<br>
                <b>Population:</b> {population_str}<br>
                <b>Elevation:</b> {elevation_str} m<br>
                <b>Coordinates:</b> ({city.latitude:.4f}, {city.longitude:.4f})<br>
                <b>Capital:</b> {'Yes' if city.is_capital else 'No'}<br>
                <b>ID:</b> {city.id}
            </div>
            """
            
            # Create marker
            folium.CircleMarker(
                location=[city.latitude, city.longitude],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{city.name} ({city.region})",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2
            ).add_to(city_group)
        
        city_group.add_to(self.map)
    
    def _add_roads_to_map(self):
        """Add Ethiopian roads as lines to the map"""
        # Create feature groups for different road types
        road_groups = {}
        for road_type in self.ROAD_COLORS.keys():
            road_groups[road_type] = folium.FeatureGroup(
                name=f'{road_type.capitalize()} Roads',
                show=True
            )
        
        for road in self.network.roads.values():
            city1 = self.network.get_city_by_id(road.city1_id)
            city2 = self.network.get_city_by_id(road.city2_id)
            
            if not city1 or not city2:
                continue
            
            # Create line coordinates
            locations = [
                [city1.latitude, city1.longitude],
                [city2.latitude, city2.longitude]
            ]
            
            # Determine line style based on road condition
            weight = 3
            opacity = 0.8
            dash_array = None
            
            if hasattr(road.condition, 'value'):
                condition = road.condition.value
                if condition == 'excellent':
                    weight = 4
                    opacity = 1.0
                elif condition == 'good':
                    weight = 3
                    opacity = 0.9
                elif condition == 'fair':
                    weight = 3
                    opacity = 0.7
                    dash_array = '5, 5'
                elif condition == 'poor':
                    weight = 2
                    opacity = 0.5
                    dash_array = '10, 10'
                elif condition == 'under_construction':
                    weight = 2
                    opacity = 0.6
                    dash_array = '5, 10'
            
            # Create popup HTML with road information
            road_name = road.name if road.name else f'Road {road.id}'
            road_type_val = road.road_type.value if hasattr(road.road_type, 'value') else str(road.road_type)
            condition_val = road.condition.value if hasattr(road.condition, 'value') else str(road.condition)
            
            popup_html = f"""
            <div style="font-family: Arial; width: 250px;">
                <h4>{road_name}</h4>
                <hr>
                <b>From:</b> {city1.name}<br>
                <b>To:</b> {city2.name}<br>
                <b>Distance:</b> {road.distance} km<br>
                <b>Type:</b> {road_type_val.capitalize()}<br>
                <b>Condition:</b> {condition_val.capitalize()}<br>
                <b>Speed Limit:</b> {road.speed_limit} km/h<br>
                <b>Lanes:</b> {road.lanes}<br>
                <b>Toll:</b> {'Yes' if road.toll else 'No'}
            </div>
            """
            
            # Add line to appropriate group
            line_kwargs = {
                'locations': locations,
                'popup': folium.Popup(popup_html, max_width=300),
                'tooltip': f"{city1.name} ↔ {city2.name} ({road.distance} km)",
                'color': self.ROAD_COLORS.get(road_type_val, '#000000'),
                'weight': weight,
                'opacity': opacity
            }
            
            if dash_array:
                line_kwargs['dashArray'] = dash_array
            
            # Get the right group
            group_key = road_type_val if road_type_val in road_groups else 'local'
            folium.PolyLine(**line_kwargs).add_to(road_groups[group_key])
        
        # Add all road groups to map
        for group in road_groups.values():
            group.add_to(self.map)
    
    def _add_path_to_map(self, path_ids: List[int]):
        """
        Add highlighted path to the map
        
        Args:
            path_ids: List of city IDs in the path
        """
        if len(path_ids) < 2:
            return
        
        path_group = folium.FeatureGroup(name='Shortest Path', show=True)
        
        # Get coordinates for path
        coordinates = []
        for city_id in path_ids:
            city = self.network.get_city_by_id(city_id)
            if city:
                coordinates.append([city.latitude, city.longitude])
        
        if len(coordinates) < 2:
            return
        
        # Add path line
        folium.PolyLine(
            locations=coordinates,
            color='#FF00FF',
            weight=5,
            opacity=0.8,
            popup='Shortest Path',
            tooltip='Shortest Path'
        ).add_to(path_group)
        
        # Add start and end markers
        start_city = self.network.get_city_by_id(path_ids[0])
        end_city = self.network.get_city_by_id(path_ids[-1])
        
        if start_city:
            folium.Marker(
                location=[start_city.latitude, start_city.longitude],
                popup=f'Start: {start_city.name}',
                icon=folium.Icon(color='green', icon='play', prefix='fa')
            ).add_to(path_group)
        
        if end_city:
            folium.Marker(
                location=[end_city.latitude, end_city.longitude],
                popup=f'End: {end_city.name}',
                icon=folium.Icon(color='red', icon='stop', prefix='fa')
            ).add_to(path_group)
        
        path_group.add_to(self.map)
    
    def create_static_map(self,
                         title: str = "Ethiopian Road Network",
                         show_cities: bool = True,
                         show_roads: bool = True,
                         highlight_path: Optional[List[int]] = None,
                         figsize: Tuple[int, int] = (15, 10),
                         save_path: Optional[str] = None):
        """
        Create a static matplotlib map of Ethiopian road network
        
        Args:
            title: Map title
            show_cities: Whether to show city markers
            show_roads: Whether to show roads
            highlight_path: List of city IDs to highlight as a path
            figsize: Figure size (width, height) in inches
            save_path: Path to save image (if None, displays plot)
        """
        if not MATPLOTLIB_AVAILABLE:
            print("❌ matplotlib is required for static maps")
            return
        
        # Create figure
        self.fig, self.ax = plt.subplots(figsize=figsize)
        
        # Set map bounds
        self.ax.set_xlim(self.ethiopia_bounds['min_lon'],
                        self.ethiopia_bounds['max_lon'])
        self.ax.set_ylim(self.ethiopia_bounds['min_lat'],
                        self.ethiopia_bounds['max_lat'])
        
        # Add grid
        self.ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add roads if requested
        if show_roads:
            self._draw_roads_static()
        
        # Add cities if requested
        if show_cities:
            self._draw_cities_static()
        
        # Add highlighted path if requested
        if highlight_path:
            self._draw_path_static(highlight_path)
        
        # Add labels and title
        self.ax.set_xlabel('Longitude', fontsize=12)
        self.ax.set_ylabel('Latitude', fontsize=12)
        self.ax.set_title(title, fontsize=16, fontweight='bold')
        
        # Add legend
        self._add_legend()
        
        # Add region boundaries (simplified)
        self._draw_region_boundaries()
        
        plt.tight_layout()
        
        # Save or show
        if save_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Map saved to: {save_path}")
        else:
            plt.show()
    
    def _draw_roads_static(self):
        """Draw roads on static map"""
        for road in self.network.roads.values():
            city1 = self.network.get_city_by_id(road.city1_id)
            city2 = self.network.get_city_by_id(road.city2_id)
            
            if not city1 or not city2:
                continue
            
            # Determine line style
            road_type_val = road.road_type.value if hasattr(road.road_type, 'value') else str(road.road_type)
            color = self.ROAD_COLORS.get(road_type_val, '#000000')
            
            condition_val = road.condition.value if hasattr(road.condition, 'value') else str(road.condition)
            if condition_val == 'poor':
                linestyle = ':'
                alpha = 0.5
            elif condition_val == 'fair':
                linestyle = '--'
                alpha = 0.7
            else:
                linestyle = '-'
                alpha = 0.8
            
            # Draw line
            self.ax.plot([city1.longitude, city2.longitude],
                        [city1.latitude, city2.latitude],
                        color=color, linestyle=linestyle,
                        linewidth=2, alpha=alpha, zorder=1)
    
    def _draw_cities_static(self):
        """Draw cities on static map"""
        for city in self.network.cities.values():
            # Determine marker size based on population
            if city.population:
                if city.population > 1_000_000:
                    size = 200
                elif city.population > 500_000:
                    size = 150
                elif city.population > 100_000:
                    size = 100
                else:
                    size = 50
            else:
                size = 50
            
            # Determine marker color
            if city.is_capital:
                color = 'gold'
                edgecolor = 'black'
                marker = '*'
            else:
                color = self.REGION_COLORS.get(city.region, 'blue')
                edgecolor = 'black'
                marker = 'o'
            
            # Draw city
            self.ax.scatter(city.longitude, city.latitude,
                          s=size, c=color, marker=marker,
                          edgecolors=edgecolor, linewidth=1,
                          alpha=0.8, zorder=2)
            
            # Add city name label for major cities
            if city.population and city.population > 500_000:
                self.ax.annotate(city.name,
                               (city.longitude, city.latitude),
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, alpha=0.7)
    
    def _draw_path_static(self, path_ids: List[int]):
        """
        Draw highlighted path on static map
        
        Args:
            path_ids: List of city IDs in the path
        """
        if len(path_ids) < 2:
            return
        
        # Get coordinates
        lons = []
        lats = []
        for city_id in path_ids:
            city = self.network.get_city_by_id(city_id)
            if city:
                lons.append(city.longitude)
                lats.append(city.latitude)
        
        if len(lons) < 2:
            return
        
        # Draw path
        self.ax.plot(lons, lats, color='magenta', linewidth=4,
                    linestyle='-', alpha=0.7, zorder=3, label='Shortest Path')
        
        # Mark start and end
        start_city = self.network.get_city_by_id(path_ids[0])
        end_city = self.network.get_city_by_id(path_ids[-1])
        
        if start_city:
            self.ax.scatter(start_city.longitude, start_city.latitude,
                          s=300, c='green', marker='*',
                          edgecolors='black', linewidth=2,
                          zorder=4, label='Start')
        
        if end_city:
            self.ax.scatter(end_city.longitude, end_city.latitude,
                          s=300, c='red', marker='*',
                          edgecolors='black', linewidth=2,
                          zorder=4, label='End')
    
    def _draw_region_boundaries(self):
        """Draw simplified Ethiopian region boundaries"""
        # Simplified region boundaries - in reality, you'd load shapefiles
        # This is just a visual approximation
        region_boundaries = {
            'Oromia': [(34, 3), (43, 3), (43, 10), (34, 10)],
            'Amhara': [(36, 10), (40, 10), (40, 14), (36, 14)],
            'Tigray': [(36, 14), (40, 14), (40, 15), (36, 15)],
            'Somali': [(41, 4), (48, 4), (48, 11), (41, 11)]
        }
        
        for region, bounds in region_boundaries.items():
            bounds.append(bounds[0])  # Close the polygon
            lons, lats = zip(*bounds)
            self.ax.plot(lons, lats, color='gray', linewidth=1,
                        linestyle=':', alpha=0.3)
    
    def _add_legend(self):
        """Add legend to static map"""
        # Create legend elements
        legend_elements = []
        
        # Road types
        for road_type, color in self.ROAD_COLORS.items():
            legend_elements.append(
                mlines.Line2D([], [], color=color, linewidth=2,
                            label=f'{road_type.capitalize()} Road')
            )
        
        # City markers
        legend_elements.extend([
            plt.scatter([], [], s=100, c='gold', marker='*',
                       edgecolors='black', label='Capital City'),
            plt.scatter([], [], s=100, c='blue', marker='o',
                       edgecolors='black', label='Major City'),
            plt.scatter([], [], s=50, c='gray', marker='o',
                       edgecolors='black', label='Small City')
        ])
        
        # Add legend
        self.ax.legend(handles=legend_elements, loc='upper left',
                      bbox_to_anchor=(1, 1), fontsize=10)
    
    def create_population_heatmap(self, save_path: Optional[str] = None):
        """
        Create a heatmap of Ethiopian city populations
        
        Args:
            save_path: Path to save image
        """
        if not MATPLOTLIB_AVAILABLE:
            print("❌ matplotlib is required for heatmaps")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract data
        lats = []
        lons = []
        populations = []
        
        for city in self.network.cities.values():
            if city.population:
                lats.append(city.latitude)
                lons.append(city.longitude)
                populations.append(city.population)
        
        if not populations:
            print("❌ No population data available")
            return
        
        # Create scatter plot with population-based size and color
        scatter = ax.scatter(lons, lats, s=[p/10000 for p in populations],
                           c=populations, cmap='hot', alpha=0.6,
                           edgecolors='black', linewidth=0.5)
        
        # Add colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Population', fontsize=12)
        
        # Set labels and title
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.set_title('Ethiopian City Population Heatmap', fontsize=16, fontweight='bold')
        
        # Set map bounds
        ax.set_xlim(self.ethiopia_bounds['min_lon'],
                   self.ethiopia_bounds['max_lon'])
        ax.set_ylim(self.ethiopia_bounds['min_lat'],
                   self.ethiopia_bounds['max_lat'])
        
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Heatmap saved to: {save_path}")
        else:
            plt.show()
    
    def create_road_condition_map(self, save_path: Optional[str] = None):
        """
        Create a map showing road conditions
        
        Args:
            save_path: Path to save image
        """
        if not MATPLOTLIB_AVAILABLE:
            print("❌ matplotlib is required")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Color map for road conditions
        condition_colors = {
            'excellent': 'darkgreen',
            'good': 'green',
            'fair': 'orange',
            'poor': 'red',
            'under_construction': 'gray',
            'seasonal': 'brown'
        }
        
        # Draw roads with condition-based colors
        for road in self.network.roads.values():
            city1 = self.network.get_city_by_id(road.city1_id)
            city2 = self.network.get_city_by_id(road.city2_id)
            
            if not city1 or not city2:
                continue
            
            condition_val = road.condition.value if hasattr(road.condition, 'value') else str(road.condition)
            color = condition_colors.get(condition_val, 'gray')
            
            ax.plot([city1.longitude, city2.longitude],
                   [city1.latitude, city2.latitude],
                   color=color, linewidth=2, alpha=0.7)
        
        # Draw cities
        for city in self.network.cities.values():
            ax.scatter(city.longitude, city.latitude,
                      s=50, c='black', marker='o', alpha=0.5)
        
        # Create legend
        legend_elements = [
            mlines.Line2D([], [], color=color, linewidth=2, label=condition.capitalize())
            for condition, color in condition_colors.items()
        ]
        
        ax.legend(handles=legend_elements, loc='upper left',
                 bbox_to_anchor=(1, 1), fontsize=10)
        
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.set_title('Ethiopian Road Conditions', fontsize=16, fontweight='bold')
        ax.set_xlim(self.ethiopia_bounds['min_lon'], self.ethiopia_bounds['max_lon'])
        ax.set_ylim(self.ethiopia_bounds['min_lat'], self.ethiopia_bounds['max_lat'])
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Road condition map saved to: {save_path}")
        else:
            plt.show()


# Example usage
if __name__ == "__main__":
    from src.graph.network import RoadNetwork
    
    print("="*80)
    print("TESTING MAP VISUALIZATION FOR ETHIOPIAN ROAD NETWORK")
    print("="*80)
    
    # Create Ethiopian road network
    network = RoadNetwork()
    network.generate_ethiopian_network(num_cities=30, num_roads=50)
    
    # Create map plotter
    plotter = MapPlotter(network)
    
    # Test interactive map
    print("\n🗺️  Creating interactive map...")
    print("(This will open in your browser)")
    
    # Get a sample path for highlighting
    cities = list(network.cities.values())
    if len(cities) >= 2:
        path_ids = [cities[0].id, cities[1].id]
        plotter.create_interactive_map(
            title="Ethiopian Road Network Test",
            show_cities=True,
            show_roads=True,
            highlight_path=path_ids
        )
    
    # Test static map if matplotlib is available
    if MATPLOTLIB_AVAILABLE:
        print("\n📊 Creating static map...")
        plotter.create_static_map(
            title="Ethiopian Road Network",
            show_cities=True,
            show_roads=True,
            save_path="output/visualizations/maps/ethiopia_network.png"
        )