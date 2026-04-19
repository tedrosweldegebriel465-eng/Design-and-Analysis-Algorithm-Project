"""
Graph Visualizer - Visualize road network as graph structures
Shows cities as nodes and roads as edges with various properties
"""

import sys
import os
from typing import List, Dict, Tuple, Optional, Any
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.network import RoadNetwork
from src.graph.city import City
from src.graph.road import Road

# Try importing visualization libraries
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("⚠️  networkx not installed. Install with: pip install networkx")

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import Patch
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class GraphVisualizer:
    """
    Class for visualizing Ethiopian road network as graph structures
    
    Features:
    - Graph with nodes (cities) and edges (roads)
    - Different layouts (spring, circular, geographic)
    - Color-coded nodes by region
    - Edge thickness based on road distance
    - Edge color based on road type/condition
    - Highlight shortest paths
    """
    
    # Ethiopian region colors (same as MapPlotter for consistency)
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
        Initialize graph visualizer with Ethiopian road network
        
        Args:
            network: RoadNetwork object
        """
        self.network = network
        self.graph = None
        self.pos = None
        
        if NETWORKX_AVAILABLE:
            self._create_networkx_graph()
    
    def _create_networkx_graph(self):
        """Create NetworkX graph from road network"""
        if not NETWORKX_AVAILABLE:
            return
        
        self.graph = nx.Graph()
        
        # Add nodes (cities)
        for city in self.network.cities.values():
            self.graph.add_node(
                city.id,
                name=city.name,
                region=city.region,
                population=city.population,
                latitude=city.latitude,
                longitude=city.longitude,
                is_capital=city.is_capital,
                elevation=city.elevation
            )
        
        # Add edges (roads)
        for road in self.network.roads.values():
            self.graph.add_edge(
                road.city1_id,
                road.city2_id,
                distance=road.distance,
                road_type=road.road_type.value if hasattr(road.road_type, 'value') else str(road.road_type),
                condition=road.condition.value if hasattr(road.condition, 'value') else str(road.condition),
                speed_limit=road.speed_limit,
                lanes=road.lanes,
                toll=road.toll,
                name=road.name,
                weight=road.distance  # For layout algorithms
            )
    
    def set_layout(self, layout: str = 'spring', **kwargs):
        """
        Set graph layout
        
        Args:
            layout: Layout type ('spring', 'circular', 'geographic', 'kamada_kawai', 'random')
            **kwargs: Additional arguments for layout function
        """
        if not NETWORKX_AVAILABLE or self.graph is None:
            return
        
        if layout == 'geographic':
            # Use actual geographic coordinates
            self.pos = {}
            for node in self.graph.nodes():
                city = self.network.get_city_by_id(node)
                if city:
                    # Scale coordinates for better visualization
                    self.pos[node] = (city.longitude, city.latitude)
        elif layout == 'spring':
            self.pos = nx.spring_layout(self.graph, seed=42, **kwargs)
        elif layout == 'circular':
            self.pos = nx.circular_layout(self.graph, **kwargs)
        elif layout == 'kamada_kawai':
            self.pos = nx.kamada_kawai_layout(self.graph, **kwargs)
        elif layout == 'random':
            self.pos = nx.random_layout(self.graph, seed=42, **kwargs)
        else:
            self.pos = nx.spring_layout(self.graph, seed=42)
    
    def draw_graph(self,
                  title: str = "Ethiopian Road Network Graph",
                  node_color_by: str = 'region',
                  edge_color_by: str = 'type',
                  show_labels: bool = True,
                  show_weights: bool = False,
                  highlight_path: Optional[List[int]] = None,
                  figsize: Tuple[int, int] = (14, 10),
                  save_path: Optional[str] = None):
        """
        Draw the graph visualization
        
        Args:
            title: Graph title
            node_color_by: Color nodes by ('region', 'population', 'capital')
            edge_color_by: Color edges by ('type', 'condition', 'distance')
            show_labels: Whether to show city labels
            show_weights: Whether to show edge weights (distances)
            highlight_path: List of city IDs to highlight as a path
            figsize: Figure size
            save_path: Path to save image
        """
        if not MATPLOTLIB_AVAILABLE or not NETWORKX_AVAILABLE:
            print("❌ matplotlib and networkx are required for graph visualization")
            return
        
        if self.graph is None:
            self._create_networkx_graph()
            if self.graph is None:
                print("❌ Failed to create graph")
                return
        
        if self.pos is None:
            self.set_layout('spring')
        
        # Create figure
        plt.figure(figsize=figsize)
        
        # Draw nodes with colors based on criteria
        node_colors = self._get_node_colors(node_color_by)
        node_sizes = self._get_node_sizes()
        
        nx.draw_networkx_nodes(
            self.graph, self.pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.8,
            edgecolors='black',
            linewidths=1
        )
        
        # Draw edges with colors based on criteria
        edge_colors, edge_widths = self._get_edge_properties(edge_color_by)
        
        nx.draw_networkx_edges(
            self.graph, self.pos,
            edge_color=edge_colors,
            width=edge_widths,
            alpha=0.6,
            style='solid'
        )
        
        # Draw labels if requested
        if show_labels:
            labels = {node: self.graph.nodes[node]['name'] for node in self.graph.nodes()}
            nx.draw_networkx_labels(
                self.graph, self.pos,
                labels,
                font_size=8,
                font_weight='bold'
            )
        
        # Draw edge weights if requested
        if show_weights:
            edge_labels = {(u, v): f"{d['distance']:.0f}km"
                          for u, v, d in self.graph.edges(data=True)}
            nx.draw_networkx_edge_labels(
                self.graph, self.pos,
                edge_labels,
                font_size=6
            )
        
        # Highlight path if requested
        if highlight_path and len(highlight_path) > 1:
            self._highlight_path(highlight_path)
        
        # Add legend
        self._add_graph_legend(node_color_by, edge_color_by)
        
        # Set title
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Remove axes
        plt.axis('off')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save or show
        if save_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Graph saved to: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def _get_node_colors(self, color_by: str) -> List[str]:
        """Get node colors based on criteria"""
        colors = []
        
        for node in self.graph.nodes():
            data = self.graph.nodes[node]
            
            if color_by == 'region':
                region = data.get('region', 'Unknown')
                colors.append(self.REGION_COLORS.get(region, '#808080'))
            
            elif color_by == 'population':
                pop = data.get('population', 0)
                if pop and pop > 1_000_000:
                    colors.append('#FF0000')  # Red
                elif pop and pop > 500_000:
                    colors.append('#FFA500')  # Orange
                elif pop and pop > 100_000:
                    colors.append('#00FF00')  # Green
                else:
                    colors.append('#0000FF')  # Blue
            
            elif color_by == 'capital':
                colors.append('#FFD700' if data.get('is_capital', False) else '#C0C0C0')
            
            else:
                colors.append('#1f78b4')  # Default blue
        
        return colors
    
    def _get_node_sizes(self) -> List[int]:
        """Get node sizes based on population"""
        sizes = []
        
        for node in self.graph.nodes():
            pop = self.graph.nodes[node].get('population', 0)
            if pop and pop > 1_000_000:
                sizes.append(800)
            elif pop and pop > 500_000:
                sizes.append(600)
            elif pop and pop > 100_000:
                sizes.append(400)
            else:
                sizes.append(200)
        
        return sizes
    
    def _get_edge_properties(self, color_by: str) -> Tuple[List[str], List[float]]:
        """Get edge colors and widths based on criteria"""
        colors = []
        widths = []
        
        for u, v, data in self.graph.edges(data=True):
            if color_by == 'type':
                road_type = data.get('road_type', 'regional')
                colors.append(self.ROAD_COLORS.get(road_type, '#000000'))
            elif color_by == 'condition':
                condition = data.get('condition', 'good')
                condition_colors = {
                    'excellent': '#006400',
                    'good': '#008000',
                    'fair': '#FFA500',
                    'poor': '#FF0000',
                    'under_construction': '#808080',
                    'seasonal': '#A52A2A'
                }
                colors.append(condition_colors.get(condition, '#008000'))
            elif color_by == 'distance':
                # Color by distance (red = longer)
                dist = data.get('distance', 100)
                max_dist = 500  # Assume max distance
                normalized = min(dist / max_dist, 1.0)
                colors.append((normalized, 0, 1 - normalized))  # RGB
            else:
                colors.append('#000000')
            
            # Edge width based on distance (thicker = longer)
            dist = data.get('distance', 100)
            widths.append(1 + (dist / 200))
        
        return colors, widths
    
    def _highlight_path(self, path_ids: List[int]):
        """
        Highlight a path in the graph
        
        Args:
            path_ids: List of city IDs in the path
        """
        # Draw path edges in magenta
        path_edges = [(path_ids[i], path_ids[i + 1]) for i in range(len(path_ids) - 1)]
        
        nx.draw_networkx_edges(
            self.graph, self.pos,
            edgelist=path_edges,
            edge_color='magenta',
            width=4,
            alpha=0.8
        )
        
        # Highlight path nodes
        nx.draw_networkx_nodes(
            self.graph, self.pos,
            nodelist=path_ids,
            node_color='yellow',
            node_size=500,
            edgecolors='red',
            linewidths=2
        )
        
        # Mark start and end
        if path_ids:
            nx.draw_networkx_nodes(
                self.graph, self.pos,
                nodelist=[path_ids[0]],
                node_color='green',
                node_size=600,
                edgecolors='black',
                linewidths=2
            )
            
            nx.draw_networkx_nodes(
                self.graph, self.pos,
                nodelist=[path_ids[-1]],
                node_color='red',
                node_size=600,
                edgecolors='black',
                linewidths=2
            )
    
    def _add_graph_legend(self, node_color_by: str, edge_color_by: str):
        """Add legend to graph"""
        legend_elements = []
        
        # Node legend
        if node_color_by == 'region':
            # Get unique regions
            regions = set()
            for node in self.graph.nodes():
                region = self.graph.nodes[node].get('region', 'Unknown')
                regions.add(region)
            
            for region in sorted(regions):
                if region in self.REGION_COLORS:
                    legend_elements.append(
                        Patch(color=self.REGION_COLORS[region], label=f'{region} Region')
                    )
        
        elif node_color_by == 'population':
            legend_elements.extend([
                Patch(color='#FF0000', label='Population > 1M'),
                Patch(color='#FFA500', label='Population > 500K'),
                Patch(color='#00FF00', label='Population > 100K'),
                Patch(color='#0000FF', label='Population < 100K')
            ])
        
        elif node_color_by == 'capital':
            legend_elements.extend([
                Patch(color='#FFD700', label='Capital City'),
                Patch(color='#C0C0C0', label='Other City')
            ])
        
        # Edge legend
        if edge_color_by == 'type':
            for road_type, color in self.ROAD_COLORS.items():
                legend_elements.append(
                    Patch(color=color, label=f'{road_type.capitalize()} Road')
                )
        
        elif edge_color_by == 'condition':
            conditions = ['excellent', 'good', 'fair', 'poor']
            condition_colors = ['#006400', '#008000', '#FFA500', '#FF0000']
            for condition, color in zip(conditions, condition_colors):
                legend_elements.append(
                    Patch(color=color, label=f'{condition.capitalize()} Condition')
                )
        
        if legend_elements:
            plt.legend(handles=legend_elements, loc='upper left',
                      bbox_to_anchor=(1, 1), fontsize=8)
    
    def draw_degree_distribution(self, save_path: Optional[str] = None):
        """
        Draw degree distribution of the graph
        
        Args:
            save_path: Path to save image
        """
        if not MATPLOTLIB_AVAILABLE or not NETWORKX_AVAILABLE:
            return
        
        if self.graph is None:
            self._create_networkx_graph()
            if self.graph is None:
                return
        
        degrees = [d for n, d in self.graph.degree()]
        
        plt.figure(figsize=(10, 6))
        
        # Create histogram
        plt.hist(degrees, bins=20, alpha=0.7, color='blue', edgecolor='black')
        
        # Add statistics
        if NUMPY_AVAILABLE:
            plt.axvline(np.mean(degrees), color='red', linestyle='--',
                       label=f'Mean: {np.mean(degrees):.2f}')
            plt.axvline(np.median(degrees), color='green', linestyle='--',
                       label=f'Median: {np.median(degrees):.2f}')
        
        plt.xlabel('Degree (Number of Connections)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Degree Distribution of Ethiopian Road Network', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Degree distribution saved to: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def draw_path_comparison(self, paths: List[Tuple[float, List[int]]],
                            labels: Optional[List[str]] = None,
                            save_path: Optional[str] = None):
        """
        Compare multiple paths on the same graph
        
        Args:
            paths: List of (distance, path_ids) tuples
            labels: Labels for each path
            save_path: Path to save image
        """
        if not MATPLOTLIB_AVAILABLE or not NETWORKX_AVAILABLE:
            return
        
        if self.graph is None:
            self._create_networkx_graph()
            if self.graph is None:
                return
        
        if self.pos is None:
            self.set_layout('spring')
        
        plt.figure(figsize=(14, 10))
        
        # Draw base graph in gray
        nx.draw_networkx_nodes(
            self.graph, self.pos,
            node_color='lightgray',
            node_size=300,
            alpha=0.3
        )
        
        nx.draw_networkx_edges(
            self.graph, self.pos,
            edge_color='lightgray',
            width=1,
            alpha=0.3
        )
        
        # Draw paths with different colors
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        
        for i, (distance, path_ids) in enumerate(paths):
            if i >= len(colors):
                break
            
            color = colors[i]
            label = labels[i] if labels and i < len(labels) else f'Path {i+1} ({distance:.0f}km)'
            
            # Draw path edges
            path_edges = [(path_ids[j], path_ids[j + 1]) for j in range(len(path_ids) - 1)]
            
            nx.draw_networkx_edges(
                self.graph, self.pos,
                edgelist=path_edges,
                edge_color=color,
                width=3,
                alpha=0.8,
                label=label
            )
        
        # Draw city labels
        labels_dict = {node: self.graph.nodes[node]['name'] for node in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, self.pos, labels_dict, font_size=8)
        
        plt.title('Path Comparison', fontsize=16, fontweight='bold')
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Path comparison saved to: {save_path}")
        else:
            plt.show()
        
        plt.close()


# Example usage
if __name__ == "__main__":
    from src.graph.network import RoadNetwork
    
    print("="*80)
    print("TESTING GRAPH VISUALIZATION FOR ETHIOPIAN ROAD NETWORK")
    print("="*80)
    
    # Create Ethiopian road network
    network = RoadNetwork()
    network.generate_ethiopian_network(num_cities=20, num_roads=30)
    
    # Create graph visualizer
    visualizer = GraphVisualizer(network)
    
    # Test different layouts
    print("\n📊 Creating graph visualizations...")
    
    # Spring layout
    visualizer.set_layout('spring')
    visualizer.draw_graph(
        title="Ethiopian Road Network (Spring Layout)",
        node_color_by='region',
        edge_color_by='type',
        show_labels=True,
        save_path="output/visualizations/graphs/ethiopia_graph_spring.png"
    )
    
    print("✅ Graph visualization complete!")