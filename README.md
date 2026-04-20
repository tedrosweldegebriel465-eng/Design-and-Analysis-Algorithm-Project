# 🇪🇹 Ethiopian GPS Navigation System

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A comprehensive GPS navigation system and interactive web dashboard that applies graph algorithms and network analytics to Ethiopian road networks.

---

## 📌 Overview

This project simulates a real-world GPS navigation system using **Dijkstra’s algorithm**, enriched with geographic calculations and network analysis.

It includes both:
- A **CLI-based navigation system**
- A **Flask-powered interactive web dashboard**

---

## 🖼️ Project Preview

### 🌍 Interactive Web Dashboard
![Dashboard1](assets/image.png)
![Dashboard2](assets/image1.png)
![Dashboard3](assets/image2.png)

---

## 🚀 Features

### 🔹 Core Features
- **Dijkstra's Algorithm Implementation**
  - Optimized using priority queue → `O((V + E) log V)`
  - Supports custom weights (distance, terrain, road condition)

- **Ethiopian Road Network Database**
  - Realistic city coordinates
  - Road attributes: distance, speed, condition

- **Interactive Web Dashboard**
  - Built with Flask
  - Folium-based interactive maps
  - Browser-based navigation experience

---

### 🔹 Advanced Analytics
- **Network Bottleneck Detection**
  - Betweenness Centrality analysis

- **Geographic Calculations**
  - Haversine distance formula

- **Data Visualization**
  - Graphs and reports
  - Heatmaps
  - Exported HTML visualizations

---

## 📂 Project Structure

```text
gps_navigation_system/
│
├── assets/                # Images used in README
├── data/                  # Raw dataset files
├── db/                    # SQL Database schemas
│   └── ethiopian_gps_schema.sql
├── notebooks/             # Jupyter notebooks
├── output/                # Generated outputs
│   ├── logs/
│   ├── reports/
│   └── visualizations/
│
├── src/
│   ├── algorithms/        # Dijkstra and A*
│   ├── analysis/          # Network analytics
│   ├── db/                # DB connections
│   ├── graph/             # Graph structures
│   ├── utils/             # Utilities
│   ├── visualization/     # Map plotting
│   └── web_app.py         # Flask app
│
├── main.py                # CLI entry point
├── requirements.txt
├── .gitignore
└── README.md
