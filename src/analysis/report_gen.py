"""
Report Generator - Generate comprehensive reports for Ethiopian road network analysis
Creates formatted reports in various formats (text, HTML, JSON, PDF)
"""

import sys
import os
import json
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.network import RoadNetwork
from src.algorithms.dijkstra_array import DijkstraArray
from src.algorithms.dijkstra_pq import DijkstraPriorityQueue
from src.algorithms.path_utils import PathUtils
from src.analysis.complexity import ComplexityAnalyzer

# Try importing optional report generation libraries
try:
    from jinja2 import Template
    JINJA_AVAILABLE = True
except ImportError:
    JINJA_AVAILABLE = False

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


class ReportGenerator:
    """
    Generates comprehensive reports for Ethiopian road network analysis
    
    Features:
    - Text reports for console output
    - HTML reports with formatting
    - JSON exports for data interchange
    - CSV exports for spreadsheet analysis
    - PDF reports (if fpdf available)
    - Customizable report sections
    - Ethiopian-specific formatting
    """
    
    def __init__(self, network: RoadNetwork, source_city_id: Optional[int] = None):
        """
        Initialize report generator
        
        Args:
            network: RoadNetwork object
            source_city_id: Source city ID (optional)
        """
        self.network = network
        self.source_city_id = source_city_id
        self.analyzer = ComplexityAnalyzer(network)
        self.path_utils = PathUtils(network)
        
        # Run Dijkstra if source provided
        self.distances = None
        self.parents = None
        if source_city_id:
            dijkstra = DijkstraArray(network)
            self.distances, self.parents = dijkstra.find_shortest_paths(source_city_id)
        
        self.report_data = {}
        
    def generate_text_report(self, include_all: bool = True) -> str:
        """
        Generate plain text report
        
        Args:
            include_all: Whether to include all sections
            
        Returns:
            Formatted text report
        """
        lines = []
        lines.append("="*80)
        lines.append("ETHIOPIAN ROAD NETWORK ANALYSIS REPORT")
        lines.append("="*80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Network Summary
        lines.append("📊 NETWORK SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Cities: {self.network.get_city_count()}")
        lines.append(f"Total Roads: {self.network.get_road_count()}")
        lines.append(f"Network Density: {self.network.get_density():.4f}")
        lines.append(f"Average Connections per City: {self.network.get_average_degree():.2f}")
        lines.append("")
        
        # Region Distribution
        lines.append("📍 CITIES BY REGION")
        lines.append("-" * 40)
        region_counts = self._count_cities_by_region()
        for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.network.get_city_count()) * 100
            lines.append(f"  {region}: {count} cities ({percentage:.1f}%)")
        lines.append("")
        
        # Road Statistics
        lines.append("🛣️  ROAD STATISTICS")
        lines.append("-" * 40)
        road_stats = self._analyze_roads()
        lines.append(f"  Average Road Length: {road_stats['avg_distance']:.2f} km")
        lines.append(f"  Shortest Road: {road_stats['min_distance']:.2f} km")
        lines.append(f"  Longest Road: {road_stats['max_distance']:.2f} km")
        lines.append(f"  Total Road Network Length: {road_stats['total_distance']:.2f} km")
        lines.append("")
        
        # Road Type Distribution
        lines.append("  Road Types:")
        for road_type, count in road_stats['by_type'].items():
            lines.append(f"    • {road_type}: {count}")
        lines.append("")
        
        # Source City Information
        if self.source_city_id:
            source_city = self.network.get_city_by_id(self.source_city_id)
            lines.append(f"📍 SOURCE CITY: {source_city.name} ({source_city.region})")
            lines.append("-" * 40)
            
            # Shortest paths summary
            reachable = sum(1 for d in self.distances.values() if d != float('inf')) - 1
            unreachable = self.network.get_city_count() - reachable - 1
            lines.append(f"  Reachable Cities: {reachable}")
            lines.append(f"  Unreachable Cities: {unreachable}")
            
            if reachable > 0:
                # Find farthest and closest
                farthest = max((cid for cid in self.distances if cid != self.source_city_id),
                              key=lambda x: self.distances[x] if self.distances[x] != float('inf') else -1)
                closest = min((cid for cid in self.distances if cid != self.source_city_id),
                             key=lambda x: self.distances[x] if self.distances[x] != float('inf') else float('inf'))
                
                farthest_city = self.network.get_city_by_id(farthest)
                closest_city = self.network.get_city_by_id(closest)
                
                lines.append(f"  Farthest City: {farthest_city.name} ({self.distances[farthest]:.2f} km)")
                lines.append(f"  Closest City: {closest_city.name} ({self.distances[closest]:.2f} km)")
            lines.append("")
            
            # Top 10 longest paths
            if reachable > 0:
                lines.append("  TOP 10 LONGEST PATHS:")
                sorted_cities = sorted([(cid, dist) for cid, dist in self.distances.items()
                                       if cid != self.source_city_id and dist != float('inf')],
                                      key=lambda x: x[1], reverse=True)[:10]
                
                for city_id, dist in sorted_cities:
                    city = self.network.get_city_by_id(city_id)
                    lines.append(f"    • {city.name}: {dist:.2f} km")
                lines.append("")
        
        # Complexity Analysis
        if include_all:
            lines.append("⏱️  COMPLEXITY ANALYSIS")
            lines.append("-" * 40)
            analysis = self.analyzer.analyze_theoretical()
            
            V = analysis['vertices']
            E = analysis['edges']
            
            lines.append(f"  Array Implementation: O(V²) = {V*V:,} operations")
            lines.append(f"  Priority Queue: O((V+E) log V) = {analysis['pq_implementation']['time_operations']:,} ops")
            lines.append(f"  Theoretical Speedup: {analysis['comparison']['speedup_theoretical']:.2f}x")
            lines.append("")
            
            # Empirical results
            empirical = self.analyzer.analyze_empirical(num_runs=3)
            if 'array_implementation' in empirical:
                lines.append("  EMPIRICAL PERFORMANCE (3 runs):")
                lines.append(f"    Array: {empirical['array_implementation']['avg_time_ms']:.2f} ms")
                lines.append(f"    Priority Queue: {empirical['pq_implementation']['avg_time_ms']:.2f} ms")
                lines.append(f"    Empirical Speedup: {empirical['comparison']['speedup_empirical']:.2f}x")
                lines.append("")
        
        # Sample Paths
        if self.source_city_id and include_all:
            lines.append("🔍 SAMPLE SHORTEST PATHS")
            lines.append("-" * 40)
            
            # Get 5 sample destinations
            sample_dests = list(self.distances.keys())[1:6] if len(self.distances) > 5 else list(self.distances.keys())[1:]
            
            for dest_id in sample_dests:
                if dest_id != self.source_city_id and self.distances[dest_id] != float('inf'):
                    dest_city = self.network.get_city_by_id(dest_id)
                    path_ids = self.path_utils.reconstruct_path(self.parents, self.source_city_id, dest_id)
                    path_str = self.path_utils.get_path_string(path_ids)
                    
                    lines.append(f"  To {dest_city.name}: {self.distances[dest_id]:.2f} km")
                    lines.append(f"    Path: {path_str}")
                    lines.append("")
        
        # Footer
        lines.append("="*80)
        lines.append("END OF REPORT")
        lines.append("="*80)
        
        return "\n".join(lines)
    
    def generate_html_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate HTML formatted report
        
        Args:
            output_file: Path to save HTML file
            
        Returns:
            HTML string
        """
        # Prepare data for template
        self._prepare_report_data()
        
        # HTML template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ethiopian Road Network Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
                h2 { color: #34495e; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }
                .summary { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }
                .stat { display: inline-block; margin: 10px 30px 10px 0; }
                .stat-value { font-size: 24px; font-weight: bold; color: #2980b9; }
                .stat-label { font-size: 14px; color: #7f8c8d; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th { background: #3498db; color: white; padding: 10px; }
                td { padding: 8px; border-bottom: 1px solid #ddd; }
                tr:hover { background: #f5f5f5; }
                .footer { margin-top: 50px; text-align: center; color: #7f8c8d; font-size: 12px; }
                .badge { background: #27ae60; color: white; padding: 3px 8px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>🇪🇹 Ethiopian Road Network Analysis Report</h1>
            <p>Generated: {{ timestamp }}</p>
            
            <div class="summary">
                <h2>Network Summary</h2>
                <div class="stat">
                    <div class="stat-value">{{ network.cities }}</div>
                    <div class="stat-label">Cities</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ network.roads }}</div>
                    <div class="stat-label">Roads</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ "%.4f"|format(network.density) }}</div>
                    <div class="stat-label">Density</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ "%.2f"|format(network.avg_degree) }}</div>
                    <div class="stat-label">Avg Connections</div>
                </div>
            </div>
            
            <h2>Cities by Region</h2>
            <table>
                <tr>
                    <th>Region</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
                {% for region, count in regions.items() %}
                <tr>
                    <td>{{ region }}</td>
                    <td>{{ count }}</td>
                    <td>{{ "%.1f"|format(count/network.cities*100) }}%</td>
                </tr>
                {% endfor %}
            </table>
            
            <h2>Road Statistics</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr><td>Average Length</td><td>{{ "%.2f"|format(road_stats.avg_distance) }} km</td></tr>
                <tr><td>Shortest Road</td><td>{{ "%.2f"|format(road_stats.min_distance) }} km</td></tr>
                <tr><td>Longest Road</td><td>{{ "%.2f"|format(road_stats.max_distance) }} km</td></tr>
                <tr><td>Total Network Length</td><td>{{ "%.2f"|format(road_stats.total_distance) }} km</td></tr>
            </table>
            
            <h2>Road Types</h2>
            <table>
                <tr>
                    <th>Type</th>
                    <th>Count</th>
                </tr>
                {% for type, count in road_stats.by_type.items() %}
                <tr>
                    <td>{{ type }}</td>
                    <td>{{ count }}</td>
                </tr>
                {% endfor %}
            </table>
            
            {% if source_city %}
            <h2>Source City: {{ source_city.name }} ({{ source_city.region }})</h2>
            
            <div class="summary">
                <div class="stat">
                    <div class="stat-value">{{ source_stats.reachable }}</div>
                    <div class="stat-label">Reachable Cities</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ source_stats.unreachable }}</div>
                    <div class="stat-label">Unreachable Cities</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ "%.2f"|format(source_stats.farthest.distance) }} km</div>
                    <div class="stat-label">Farthest City</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ "%.2f"|format(source_stats.closest.distance) }} km</div>
                    <div class="stat-label">Closest City</div>
                </div>
            </div>
            
            <h2>Top 10 Longest Paths from {{ source_city.name }}</h2>
            <table>
                <tr>
                    <th>Destination</th>
                    <th>Region</th>
                    <th>Distance (km)</th>
                </tr>
                {% for dest in longest_paths %}
                <tr>
                    <td>{{ dest.name }}</td>
                    <td>{{ dest.region }}</td>
                    <td>{{ "%.2f"|format(dest.distance) }}</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
            
            <h2>Complexity Analysis</h2>
            <table>
                <tr>
                    <th>Implementation</th>
                    <th>Time Complexity</th>
                    <th>Operations</th>
                    <th>Space (KB)</th>
                </tr>
                <tr>
                    <td>Array</td>
                    <td>O(V²)</td>
                    <td>{{ complexity.array.operations }}</td>
                    <td>{{ "%.2f"|format(complexity.array.memory) }}</td>
                </tr>
                <tr>
                    <td>Priority Queue</td>
                    <td>O((V+E) log V)</td>
                    <td>{{ complexity.pq.operations }}</td>
                    <td>{{ "%.2f"|format(complexity.pq.memory) }}</td>
                </tr>
            </table>
            
            <p>Theoretical Speedup: <span class="badge">{{ "%.2f"|format(complexity.speedup) }}x</span></p>
            
            <div class="footer">
                Generated by Ethiopian GPS Navigation System<br>
                &copy; 2024
            </div>
        </body>
        </html>
        """
        
        if JINJA_AVAILABLE:
            template = Template(html_template)
            html = template.render(**self.report_data)
        else:
            # Simple string replacement if jinja not available
            html = html_template
            for key, value in self._flatten_dict(self.report_data).items():
                html = html.replace(f"{{{{ {key} }}}}", str(value))
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ HTML report saved to: {output_file}")
        
        return html
    
    def generate_json_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate JSON formatted report
        
        Args:
            output_file: Path to save JSON file
            
        Returns:
            JSON string
        """
        self._prepare_report_data()
        
        # Add metadata
        self.report_data['metadata'] = {
            'generated': datetime.now().isoformat(),
            'version': '1.0',
            'system': 'Ethiopian GPS Navigation System'
        }
        
        json_str = json.dumps(self.report_data, indent=2, default=str)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"✅ JSON report saved to: {output_file}")
        
        return json_str
    
    def generate_csv_report(self, output_dir: str = "reports"):
        """
        Generate multiple CSV files for different aspects of the report
        
        Args:
            output_dir: Directory to save CSV files
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Cities CSV
        cities_file = os.path.join(output_dir, "cities.csv")
        with open(cities_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Region', 'Latitude', 'Longitude', 
                           'Population', 'Elevation', 'Is Capital'])
            
            for city in self.network.cities.values():
                writer.writerow([
                    city.id,
                    city.name,
                    city.region,
                    city.latitude,
                    city.longitude,
                    city.population or '',
                    city.elevation or '',
                    'Yes' if city.is_capital else 'No'
                ])
        
        # Roads CSV
        roads_file = os.path.join(output_dir, "roads.csv")
        with open(roads_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'From City', 'To City', 'Distance (km)', 
                           'Type', 'Condition', 'Speed Limit', 'Lanes', 'Toll'])
            
            for road in self.network.roads.values():
                city1 = self.network.get_city_by_id(road.city1_id)
                city2 = self.network.get_city_by_id(road.city2_id)
                
                writer.writerow([
                    road.id,
                    city1.name if city1 else f"City_{road.city1_id}",
                    city2.name if city2 else f"City_{road.city2_id}",
                    road.distance,
                    road.road_type.value,
                    road.condition.value,
                    road.speed_limit,
                    road.lanes,
                    'Yes' if road.toll else 'No'
                ])
        
        # Paths CSV if source provided
        if self.source_city_id and self.distances:
            paths_file = os.path.join(output_dir, "shortest_paths.csv")
            with open(paths_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Destination', 'Region', 'Distance (km)', 'Path'])
                
                source_city = self.network.get_city_by_id(self.source_city_id)
                
                for city_id, distance in self.distances.items():
                    if city_id != self.source_city_id and distance != float('inf'):
                        city = self.network.get_city_by_id(city_id)
                        path_ids = self.path_utils.reconstruct_path(self.parents, self.source_city_id, city_id)
                        path_str = self.path_utils.get_path_string(path_ids)
                        
                        writer.writerow([
                            city.name,
                            city.region,
                            f"{distance:.2f}",
                            path_str
                        ])
        
        print(f"✅ CSV reports saved to {output_dir}/")
    
    def generate_pdf_report(self, output_file: str = "report.pdf"):
        """
        Generate PDF report (if fpdf available)
        
        Args:
            output_file: Path to save PDF file
        """
        if not FPDF_AVAILABLE:
            print("❌ fpdf not installed. Install with: pip install fpdf")
            return
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 15)
                self.cell(0, 10, 'Ethiopian Road Network Analysis Report', 0, 1, 'C')
                self.ln(10)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
        pdf = PDF()
        pdf.add_page()
        
        # Get report data
        self._prepare_report_data()
        
        # Add content
        pdf.set_font('Arial', '', 12)
        
        # Network Summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Network Summary', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f"Cities: {self.report_data['network']['cities']}", 0, 1)
        pdf.cell(0, 8, f"Roads: {self.report_data['network']['roads']}", 0, 1)
        pdf.cell(0, 8, f"Density: {self.report_data['network']['density']:.4f}", 0, 1)
        pdf.cell(0, 8, f"Avg Connections: {self.report_data['network']['avg_degree']:.2f}", 0, 1)
        pdf.ln(10)
        
        # Source City
        if 'source_city' in self.report_data:
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, f"Source City: {self.report_data['source_city']['name']}", 0, 1)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f"Region: {self.report_data['source_city']['region']}", 0, 1)
            pdf.cell(0, 8, f"Reachable Cities: {self.report_data['source_stats']['reachable']}", 0, 1)
            pdf.cell(0, 8, f"Unreachable Cities: {self.report_data['source_stats']['unreachable']}", 0, 1)
            pdf.ln(10)
        
        # Complexity
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Complexity Analysis', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f"Array Operations: {self.report_data['complexity']['array']['operations']:,}", 0, 1)
        pdf.cell(0, 8, f"PQ Operations: {self.report_data['complexity']['pq']['operations']:,}", 0, 1)
        pdf.cell(0, 8, f"Speedup: {self.report_data['complexity']['speedup']:.2f}x", 0, 1)
        
        pdf.output(output_file)
        print(f"✅ PDF report saved to: {output_file}")
    
    def _prepare_report_data(self):
        """Prepare data for reports"""
        self.report_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'network': {
                'cities': self.network.get_city_count(),
                'roads': self.network.get_road_count(),
                'density': self.network.get_density(),
                'avg_degree': self.network.get_average_degree()
            },
            'regions': self._count_cities_by_region(),
            'road_stats': self._analyze_roads(),
            'complexity': self._get_complexity_data()
        }
        
        if self.source_city_id:
            source_city = self.network.get_city_by_id(self.source_city_id)
            if source_city:
                self.report_data['source_city'] = {
                    'id': source_city.id,
                    'name': source_city.name,
                    'region': source_city.region
                }
                
                if self.distances:
                    reachable = sum(1 for d in self.distances.values() if d != float('inf')) - 1
                    unreachable = self.network.get_city_count() - reachable - 1
                    
                    # Find farthest and closest
                    farthest_id = max((cid for cid in self.distances if cid != self.source_city_id),
                                     key=lambda x: self.distances[x] if self.distances[x] != float('inf') else -1)
                    closest_id = min((cid for cid in self.distances if cid != self.source_city_id),
                                    key=lambda x: self.distances[x] if self.distances[x] != float('inf') else float('inf'))
                    
                    farthest_city = self.network.get_city_by_id(farthest_id)
                    closest_city = self.network.get_city_by_id(closest_id)
                    
                    self.report_data['source_stats'] = {
                        'reachable': reachable,
                        'unreachable': unreachable,
                        'farthest': {
                            'name': farthest_city.name if farthest_city else 'Unknown',
                            'distance': self.distances[farthest_id]
                        },
                        'closest': {
                            'name': closest_city.name if closest_city else 'Unknown',
                            'distance': self.distances[closest_id]
                        }
                    }
                    
                    # Longest paths
                    longest = sorted([(cid, dist) for cid, dist in self.distances.items()
                                    if cid != self.source_city_id and dist != float('inf')],
                                   key=lambda x: x[1], reverse=True)[:10]
                    
                    self.report_data['longest_paths'] = []
                    for city_id, dist in longest:
                        city = self.network.get_city_by_id(city_id)
                        if city:
                            self.report_data['longest_paths'].append({
                                'name': city.name,
                                'region': city.region,
                                'distance': dist
                            })
    
    def _count_cities_by_region(self) -> Dict[str, int]:
        """Count cities by Ethiopian region"""
        counts = {}
        for city in self.network.cities.values():
            counts[city.region] = counts.get(city.region, 0) + 1
        return counts
    
    def _analyze_roads(self) -> Dict[str, Any]:
        """Analyze road statistics"""
        if not self.network.roads:
            return {
                'avg_distance': 0,
                'min_distance': 0,
                'max_distance': 0,
                'total_distance': 0,
                'by_type': {}
            }
        
        distances = [road.distance for road in self.network.roads.values()]
        
        # Count by type
        by_type = {}
        for road in self.network.roads.values():
            road_type = road.road_type.value
            by_type[road_type] = by_type.get(road_type, 0) + 1
        
        return {
            'avg_distance': sum(distances) / len(distances),
            'min_distance': min(distances),
            'max_distance': max(distances),
            'total_distance': sum(distances),
            'by_type': by_type
        }
    
    def _get_complexity_data(self) -> Dict[str, Any]:
        """Get complexity analysis data"""
        analysis = self.analyzer.analyze_theoretical()
        memory = self.analyzer.analyze_memory()
        
        return {
            'array': {
                'operations': analysis['array_implementation']['time_operations'],
                'memory': memory['array_implementation']['total_kb']
            },
            'pq': {
                'operations': analysis['pq_implementation']['time_operations'],
                'memory': memory['pq_implementation']['total_kb']
            },
            'speedup': analysis['comparison']['speedup_theoretical']
        }
    
    def _flatten_dict(self, d: Dict, parent_key: str = '') -> Dict:
        """Flatten nested dictionary for simple string replacement"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)


# Example usage
if __name__ == "__main__":
    from src.graph.network import RoadNetwork
    
    print("="*80)
    print("TESTING REPORT GENERATOR")
    print("="*80)
    
    # Create test network
    network = RoadNetwork()
    network.generate_ethiopian_network(num_cities=30, num_roads=45)
    
    # Get first city as source
    source_id = next(iter(network.cities.keys()))
    source_city = network.get_city_by_id(source_id)
    print(f"\n📍 Source City: {source_city.name}")
    
    # Create report generator
    generator = ReportGenerator(network, source_id)
    
    # Generate text report
    print("\n📄 Generating text report...")
    text_report = generator.generate_text_report()
    print(text_report[:500] + "...\n")
    
    # Generate HTML report
    print("\n🌐 Generating HTML report...")
    generator.generate_html_report("ethiopia_report.html")
    
    # Generate JSON report
    print("\n📊 Generating JSON report...")
    generator.generate_json_report("ethiopia_report.json")
    
    # Generate CSV reports
    print("\n📈 Generating CSV reports...")
    generator.generate_csv_report("reports")
    
    # Generate PDF report if available
    if FPDF_AVAILABLE:
        print("\n📑 Generating PDF report...")
        generator.generate_pdf_report("ethiopia_report.pdf")