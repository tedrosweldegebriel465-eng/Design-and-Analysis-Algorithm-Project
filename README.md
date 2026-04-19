  Ethiopian GPS Navigation System

[Python Version] (https://img.shields.io/badge/python-3.8%2B-blue)
[License](https://img.shields.io/badge/license-MIT-green)

A comprehensive GPS navigation system and interactive web dashboard implementing Dijkstra's algorithm and network analytics for Ethiopian road networks. 

  Table of Contents
- [Features](-features)
- [Project Structure] (-project-structure)
- [Installation](-installation)
- [Database Setup] (-database-setup)
- [Usage Examples] (-usage-examples)

  Features

    Core Features
-  Complete Dijkstra's Algorithm Implementation
  - Priority queue version (O((V+E) log V))
  - Support for custom terrain and condition weights
-  Ethiopian Road Network Database
  - Schema for Ethiopian cities with real coordinates
  - Database schema for roads with realistic distances, speeds, and conditions
-Interactive Web Dashboard
  - Flask-based web interface built to interact with the map
  - Interactive Folium maps accessible directly from the browser

 Advanced Analytics
-Network Analytics: Identify network bottlenecks using Betweenness Centrality.
-Geographic Calculations: Haversine distance formulas.
-Visualizations: Auto-generated graphs, heatmaps, and HTML outputs.









 Project Structure

```text
gps_navigation_system/
│
├── data/                  # Raw dataset files
├── db/                    # SQL Database schemas
│   └── ethiopian_gps_schema.sql
├── notebooks/             # Jupyter notebooks for interactive demonstrations
├── output/                # Generated outputs
│   ├── logs/              # Execution logs
│   ├── reports/           # Generated analytical reports
│   └── visualizations/    # Generated maps and graph images
│
├── src/                   # Core Source code
│   ├── algorithms/        # Dijkstra and A* Implementations
│   ├── analysis/          # Analytics like Betweenness Centrality
│   ├── db/                # Database connection handlers
│   ├── graph/             # Core Graph data structures
│   ├── utils/             # Helper / utility functions
│   ├── visualization/     # Map plotting modules
│   └── web_app.py         # Flask Web Dashboard backend
│
├── .gitignore             # Git ignore configuration
├── requirements.txt       # Dependencies
├── README.md              # Project Documentation
└── main.py                # Main CLI entry point
```






     Installation

    Prerequisites
- Python 3.8 or higher
- XAMPP / MySQL Server

 Step-by-Step Installation

1.  Clone the repository 
```bash
git clone https://github.com/yourusername/ethiopian-gps-navigation.git
cd ethiopian-gps-navigation
```

2. Create a Virtual Environment
```bash
   Windows
python -m venv venv
venv\Scripts\activate

   Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

    Database Setup

This project uses a MySQL database named `ethiopian_gps` to store cities and roads.

1. Start Apache and MySQL from your XAMPP control panel.
2. Open phpMyAdmin in your browser (`http://localhost/phpmyadmin`).
3. Create a new database named `ethiopian_gps`.
4. Go to the “Import” tab.
5. Choose File and select `db/ethiopian_gps_schema.sql` from this project.
6. Click “Go” to generate the tables.

    Usage

You can run the application via the main Command Line Interface:

```bash
python main.py
```

From the CLI menu, you can select options to:
1. Run Route Calculations (Dijkstra)
2. Generate Static/Interactive Visualizations
3. Run Data Analytics (e.g. Betweenness Centrality)
4. Launch the **Web Dashboard** on localhost for the interactive GUI experience.
