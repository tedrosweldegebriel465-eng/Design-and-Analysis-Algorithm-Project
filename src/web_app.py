"""
Simple Flask web interface for the Ethiopian GPS Navigation System.

Endpoints:
    - GET /health
    - GET /route?from=Addis%20Ababa&to=Bahir%20Dar
    - GET /map?from=Addis%20Ababa&to=Bahir%20Dar

This reuses the existing RoadNetwork, DataLoader, Dijkstra algorithm,
PathUtils, and MapPlotter components from the console application.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, List, Set
import heapq
import json
import secrets

from flask import Flask, jsonify, request, send_from_directory, abort
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from src.config import get_config
from src.utils.data_loader import DataLoader
from src.graph.network import RoadNetwork
from src.algorithms.dijkstra_pq import DijkstraPriorityQueue
from src.algorithms.path_utils import PathUtils
from src.visualization.map_plotter import MapPlotter
from src.db.session import get_session
from src.db.models import UserDB, SavedRouteDB
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("GPS_SECRET_KEY", secrets.token_hex(32))
_auth_serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="gps-auth")

_config = get_config()
_network: Optional[RoadNetwork] = None
_path_utils: Optional[PathUtils] = None


def _ensure_network_loaded() -> None:
    """
    Lazily load the Ethiopian network from the database (or fallback files).
    This is shared by all endpoints.
    """
    global _network, _path_utils

    if _network is not None and _path_utils is not None:
        return

    loader = DataLoader(data_dir=str(_config.data_dir), verbose=False)

    try:
        # Prefer curated dataset files for stable/realistic routing output.
        try:
            _network = loader.create_network_from_files(
                cities_file="ethiopian_cities_validated.csv",
                roads_file="ethiopia_road_network_validated.csv",
            )
        except FileNotFoundError:
            _network = loader.create_network_from_files(
                cities_file="ethiopian_cities_clean.csv",
                roads_file="ethiopia_road_network.csv",
            )
    except FileNotFoundError:
        # Fallback to database if files are unavailable.
        _network = loader.create_network_from_database()

    _path_utils = PathUtils(_network)


def _parse_list_param(value: Optional[str]) -> List[str]:
    """Parse a comma-separated query parameter into a list of lowercase strings."""
    if not value:
        return []
    return [part.strip().lower() for part in value.split(",") if part.strip()]


def _create_access_token(user_id: int, username: str) -> str:
    """Create a signed token for API authentication."""
    return _auth_serializer.dumps({"user_id": user_id, "username": username})


def _get_current_user_or_401() -> Dict[str, Any]:
    """
    Authenticate user from bearer token.

    Accepted headers:
      Authorization: Bearer <token>
      X-Auth-Token: <token>
    """
    auth_header = request.headers.get("Authorization", "")
    token = ""
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
    if not token:
        token = (request.headers.get("X-Auth-Token") or "").strip()
    if not token:
        abort(401, description="Missing authentication token.")

    try:
        payload = _auth_serializer.loads(token, max_age=60 * 60 * 24)
    except SignatureExpired:
        abort(401, description="Authentication token expired.")
    except BadSignature:
        abort(401, description="Invalid authentication token.")

    user_id = payload.get("user_id")
    if not user_id:
        abort(401, description="Invalid authentication token.")

    with get_session() as session:
        user = session.get(UserDB, user_id)
        if not user:
            abort(401, description="User not found for token.")
        return {"id": user.id, "username": user.username}


def _edge_cost_for_mode(road, base_distance: float, mode: str) -> float:
    """
    Compute edge cost based on routing mode.

    - shortest: physical distance in km
    - fastest: estimated travel time in hours
    - safest: penalize poor/seasonal/under_construction roads
    """
    mode = mode.lower()
    if mode == "fastest":
        # Use travel time in hours
        return float(road.get_travel_time())

    if mode == "safest":
        cost = float(road.distance)
        cond = road.condition.value if hasattr(road.condition, "value") else str(
            road.condition
        ).lower()
        penalties = {
            "excellent": 1.0,
            "good": 1.0,
            "fair": 1.3,
            "poor": 2.0,
            "under_construction": 3.0,
            "seasonal": 2.5,
        }
        cost *= penalties.get(cond, 1.0)
        return cost

    # Default: shortest
    return float(road.distance if base_distance <= 0 or base_distance == float("inf") else base_distance)


def _find_route_with_options(
    source_city_name: str,
    dest_city_name: str,
    mode: str,
    avoid_conditions: List[str],
    allowed_regions: List[str],
    avoid_regions: List[str],
) -> Dict[str, Any]:
    """
    Dijkstra between two cities with advanced options:
      - mode: shortest | fastest | safest
      - avoid_conditions: list of road condition strings to avoid completely
      - allowed_regions: if non-empty, only allow cities in these regions
      - avoid_regions: cities in these regions are not allowed
    """
    _ensure_network_loaded()
    assert _network is not None
    assert _path_utils is not None

    mode = (mode or "shortest").lower()
    if mode not in {"shortest", "fastest", "safest"}:
        abort(400, description="Invalid mode. Use 'shortest', 'fastest', or 'safest'.")

    source_city = _network.get_city_by_name(source_city_name)
    dest_city = _network.get_city_by_name(dest_city_name)

    if not source_city:
        abort(404, description=f"Source city '{source_city_name}' not found")
    if not dest_city:
        abort(404, description=f"Destination city '{dest_city_name}' not found")

    allowed_regions_set: Set[str] = {r.lower() for r in allowed_regions}
    avoid_regions_set: Set[str] = {r.lower() for r in avoid_regions}
    avoid_conditions_set: Set[str] = {c.lower() for c in avoid_conditions}

    # Standard Dijkstra but with custom edge filtering and cost.
    distances: Dict[int, float] = {
        cid: float("inf") for cid in _network.cities.keys()
    }
    parents: Dict[int, int] = {cid: -1 for cid in _network.cities.keys()}

    source_id = source_city.id
    dest_id = dest_city.id

    distances[source_id] = 0.0
    pq: List[Any] = [(0.0, source_id)]
    visited: Set[int] = set()

    while pq:
        current_cost, current_id = heapq.heappop(pq)

        if current_id == dest_id:
            break
        if current_id in visited:
            continue
        visited.add(current_id)

        current_city = _network.get_city_by_id(current_id)
        if current_city is None:
            continue

        for neighbor_id, base_distance, road in _network.get_neighbors(current_id):
            if neighbor_id in visited or road is None:
                continue

            neighbor_city = _network.get_city_by_id(neighbor_id)
            if neighbor_city is None:
                continue

            # Region filters
            cur_region = (current_city.region or "").lower()
            nei_region = (neighbor_city.region or "").lower()

            if allowed_regions_set:
                if cur_region not in allowed_regions_set or nei_region not in allowed_regions_set:
                    continue
            if avoid_regions_set:
                if cur_region in avoid_regions_set or nei_region in avoid_regions_set:
                    continue

            # Road condition closures
            cond_val = road.condition.value if hasattr(road.condition, "value") else str(
                road.condition
            ).lower()
            if cond_val in avoid_conditions_set:
                continue

            edge_cost = _edge_cost_for_mode(road, base_distance, mode)
            if edge_cost == float("inf"):
                continue

            new_cost = current_cost + edge_cost
            if new_cost < distances[neighbor_id]:
                distances[neighbor_id] = new_cost
                parents[neighbor_id] = current_id
                heapq.heappush(pq, (new_cost, neighbor_id))

    if distances[dest_id] == float("inf"):
        abort(
            404,
            description=f"No path found between '{source_city_name}' and '{dest_city_name}' with given constraints.",
        )

    # Reconstruct path
    path_ids: List[int] = _path_utils.reconstruct_path(parents, source_id, dest_id)
    if not path_ids:
        abort(
            404,
            description=f"No path found between '{source_city_name}' and '{dest_city_name}' with given constraints.",
        )

    # Compute physical distance and travel time along the path
    total_distance_km = 0.0
    total_travel_time_h = 0.0
    for i in range(len(path_ids) - 1):
        road = _network.get_road_between(path_ids[i], path_ids[i + 1])
        if not road:
            continue
        total_distance_km += float(road.distance)
        total_travel_time_h += float(road.get_travel_time())

    path_str = _path_utils.get_path_string(path_ids)

    return {
        "from": source_city.name,
        "to": dest_city.name,
        "mode": mode,
        "distance_km": round(total_distance_km, 2),
        "travel_time_hours": round(total_travel_time_h, 2),
        "city_ids": path_ids,
        "path": path_str,
        "steps": len(path_ids),
        "options": {
            "avoid_conditions": sorted(list(avoid_conditions_set)),
            "allowed_regions": sorted(list(allowed_regions_set)),
            "avoid_regions": sorted(list(avoid_regions_set)),
        },
    }


def _compute_summary_stats() -> Dict[str, Any]:
    """Compute high-level network statistics for the dashboard."""
    _ensure_network_loaded()
    assert _network is not None

    total_cities = _network.get_city_count()
    total_roads = _network.get_road_count()
    density = _network.get_density()
    avg_degree = _network.get_average_degree()

    return {
        "total_cities": total_cities,
        "total_roads": total_roads,
        "density": round(density, 4),
        "average_degree": round(avg_degree, 2),
    }


def _compute_region_stats() -> Dict[str, int]:
    """Return number of cities per region."""
    _ensure_network_loaded()
    assert _network is not None
    return _network.get_cities_by_region_summary()


def _compute_condition_stats() -> Dict[str, int]:
    """Return count of roads by condition."""
    _ensure_network_loaded()
    assert _network is not None

    counts: Dict[str, int] = {}
    for road in _network.roads.values():
        condition = road.condition.value if hasattr(road.condition, "value") else str(
            road.condition
        )
        counts[condition] = counts.get(condition, 0) + 1
    return counts


def _compute_top_cities_by_degree(limit: int = 10) -> Dict[str, Any]:
    """
    Compute a simple 'centrality' metric: degree (number of neighboring roads).
    Returns the top N cities by degree.
    """
    _ensure_network_loaded()
    assert _network is not None

    degrees: Dict[int, int] = {}
    for city_id in _network.cities.keys():
        degrees[city_id] = len(_network.get_neighbors(city_id))

    # Sort by degree descending
    sorted_items = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:limit]

    city_names: List[str] = []
    city_degrees: List[int] = []
    for cid, deg in sorted_items:
        city = _network.get_city_by_id(cid)
        if city:
            city_names.append(city.name)
            city_degrees.append(deg)

    return {
        "cities": city_names,
        "degrees": city_degrees,
    }


@app.get("/health")
def health() -> Any:
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "app": _config.name, "version": _config.version})


@app.get("/route")
def route() -> Any:
    """
    GET /route?from=Addis%20Ababa&to=Bahir%20Dar

    Returns JSON describing the shortest path between the two cities.
    """
    source = request.args.get("from")
    dest = request.args.get("to")
    mode = request.args.get("mode", "shortest")
    avoid_conditions = _parse_list_param(request.args.get("avoid"))
    allowed_regions = _parse_list_param(request.args.get("allowed_regions"))
    avoid_regions = _parse_list_param(request.args.get("avoid_regions"))

    if not source or not dest:
        abort(400, description="Query params 'from' and 'to' are required")

    result = _find_route_with_options(
        source,
        dest,
        mode=mode,
        avoid_conditions=avoid_conditions,
        allowed_regions=allowed_regions,
        avoid_regions=avoid_regions,
    )
    return jsonify(result)


@app.get("/map")
def map_view() -> Any:
    """
    GET /map?from=Addis%20Ababa&to=Bahir%20Dar

    Generates (or reuses) an interactive HTML map highlighting the shortest path.
    Returns the HTML file directly.
    """
    source = request.args.get("from")
    dest = request.args.get("to")
    mode = request.args.get("mode", "shortest")
    avoid_conditions = _parse_list_param(request.args.get("avoid"))
    allowed_regions = _parse_list_param(request.args.get("allowed_regions"))
    avoid_regions = _parse_list_param(request.args.get("avoid_regions"))
    show_network = request.args.get("show_network", "0").strip().lower() in {"1", "true", "yes"}

    if not source or not dest:
        abort(400, description="Query params 'from' and 'to' are required")

    _ensure_network_loaded()
    assert _network is not None
    assert _path_utils is not None

    # Compute the path first (will 404 if not reachable)
    result = _find_route_with_options(
        source,
        dest,
        mode=mode,
        avoid_conditions=avoid_conditions,
        allowed_regions=allowed_regions,
        avoid_regions=avoid_regions,
    )
    path_ids = result["city_ids"]

    # Generate map file path under configured output directory
    maps_dir = os.path.join(str(_config.output_dir), "visualizations", "maps")
    os.makedirs(maps_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"route_{source}_{dest}_{mode}_{timestamp}.html".replace(" ", "_")
    full_path = os.path.join(maps_dir, filename)

    plotter = MapPlotter(_network)
    plotter.create_interactive_map(
        title=f"Route: {result['from']} → {result['to']}",
        show_cities=True,
        # Keep map focused on the selected route by default.
        show_roads=show_network,
        highlight_path=path_ids,
        output_file=full_path,
    )

    # Serve the generated file
    return send_from_directory(maps_dir, filename)


@app.get("/api/cities")
def api_cities() -> Any:
    """JSON: sorted list of all city names."""
    _ensure_network_loaded()
    assert _network is not None
    cities = sorted([c.name for c in _network.cities.values()])
    return jsonify({"cities": cities})


@app.get("/stats/summary")
def stats_summary() -> Any:
    """JSON: high-level network statistics."""
    return jsonify(_compute_summary_stats())


@app.get("/stats/regions")
def stats_regions() -> Any:
    """JSON: number of cities per region."""
    return jsonify(_compute_region_stats())


@app.get("/stats/conditions")
def stats_conditions() -> Any:
    """JSON: number of roads per condition."""
    return jsonify(_compute_condition_stats())


@app.get("/stats/top-cities")
def stats_top_cities() -> Any:
    """JSON: top cities by degree (connectedness)."""
    limit_param = request.args.get("limit")
    try:
        limit = int(limit_param) if limit_param else 10
    except ValueError:
        limit = 10
    return jsonify(_compute_top_cities_by_degree(limit=limit))


@app.get("/dashboard")
def dashboard() -> Any:
    """
    Simple analytics dashboard page.

    Serves a static HTML file with JavaScript that calls the /stats/* APIs
    and visualizes the data using Plotly (loaded via CDN).
    """
    web_dir = os.path.join(os.path.dirname(__file__), "..", "web")
    return send_from_directory(web_dir, "dashboard.html")


# ---------------------------------------------------------------------------
# User accounts & saved routes
# ---------------------------------------------------------------------------


@app.post("/register")
def register() -> Any:
    """
    Register a new user.

    JSON body:
    {
      "username": "alice",
      "password": "secret123"
    }
    """
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        abort(400, description="Both 'username' and 'password' are required.")

    with get_session() as session:
        existing = session.query(UserDB).filter(UserDB.username == username).first()
        if existing:
            abort(409, description="Username already exists.")

        user = UserDB(
            username=username,
            password_hash=generate_password_hash(password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        token = _create_access_token(user.id, user.username)

        return jsonify(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                },
                "token": token,
            }
        ), 201


@app.post("/login")
def login() -> Any:
    """
    Log in a user (simple API login).

    JSON body:
    {
      "username": "alice",
      "password": "secret123"
    }

    Returns:
      { "user": { "id": ..., "username": ... }, "token": "..." }
    """
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        abort(400, description="Both 'username' and 'password' are required.")

    with get_session() as session:
        user = session.query(UserDB).filter(UserDB.username == username).first()
        if not user or not check_password_hash(user.password_hash, password):
            abort(401, description="Invalid username or password.")

        token = _create_access_token(user.id, user.username)
        return jsonify({"user": {"id": user.id, "username": user.username}, "token": token})


@app.post("/routes/save")
def save_route() -> Any:
    """
    Save a favorite route for a user.

    Requires Authorization: Bearer <token>
    JSON body:
    {
      "from": "Addis Ababa",
      "to": "Bahir Dar",
      "mode": "shortest|fastest|safest",
      "avoid": "poor,seasonal",
      "allowed_regions": "Amhara,Oromia",
      "avoid_regions": "Somali"
    }
    """
    current_user = _get_current_user_or_401()
    data = request.get_json(silent=True) or {}
    source = (data.get("from") or "").strip()
    dest = (data.get("to") or "").strip()
    mode = (data.get("mode") or "shortest").strip()
    avoid_raw = data.get("avoid")
    allowed_regions_raw = data.get("allowed_regions")
    avoid_regions_raw = data.get("avoid_regions")

    if not source or not dest:
        abort(400, description="'from' and 'to' are required.")

    avoid_conditions = _parse_list_param(avoid_raw)
    allowed_regions = _parse_list_param(allowed_regions_raw)
    avoid_regions = _parse_list_param(avoid_regions_raw)

    # Reuse routing logic to compute the route and metrics
    result = _find_route_with_options(
        source,
        dest,
        mode=mode,
        avoid_conditions=avoid_conditions,
        allowed_regions=allowed_regions,
        avoid_regions=avoid_regions,
    )

    options_dict = {
        "avoid": avoid_conditions,
        "allowed_regions": allowed_regions,
        "avoid_regions": avoid_regions,
    }

    with get_session() as session:
        saved = SavedRouteDB(
            user_id=current_user["id"],
            source_city=result["from"],
            dest_city=result["to"],
            mode=result["mode"],
            options_json=json.dumps(options_dict),
            distance_km=result.get("distance_km"),
            travel_time_hours=result.get("travel_time_hours"),
        )
        session.add(saved)
        session.commit()
        session.refresh(saved)

        return (
            jsonify(
                {
                    "id": saved.id,
                    "user_id": saved.user_id,
                    "source_city": saved.source_city,
                    "dest_city": saved.dest_city,
                    "mode": saved.mode,
                    "distance_km": saved.distance_km,
                    "travel_time_hours": saved.travel_time_hours,
                    "options": options_dict,
                    "created_at": saved.created_at.isoformat()
                    if saved.created_at
                    else None,
                }
            ),
            201,
        )


@app.get("/routes/mine")
def list_saved_routes() -> Any:
    """
    List all saved routes for a user.

    Requires Authorization: Bearer <token>
    """
    current_user = _get_current_user_or_401()
    user_id = current_user["id"]

    with get_session() as session:
        user = session.get(UserDB, user_id)
        if not user:
            abort(404, description="User not found.")

        records = (
            session.query(SavedRouteDB)
            .filter(SavedRouteDB.user_id == user_id)
            .order_by(SavedRouteDB.created_at.desc())
            .all()
        )

        items = []
        for r in records:
            try:
                options = json.loads(r.options_json) if r.options_json else {}
            except json.JSONDecodeError:
                options = {}
            items.append(
                {
                    "id": r.id,
                    "source_city": r.source_city,
                    "dest_city": r.dest_city,
                    "mode": r.mode,
                    "distance_km": r.distance_km,
                    "travel_time_hours": r.travel_time_hours,
                    "options": options,
                    "created_at": r.created_at.isoformat()
                    if r.created_at
                    else None,
                }
            )

        return jsonify({"user": {"id": user.id, "username": user.username}, "routes": items})


@app.get("/routes/export")
def export_saved_routes() -> Any:
    """
    Export saved routes for a user as JSON.

    Requires Authorization: Bearer <token>
    """
    current_user = _get_current_user_or_401()
    user_id = current_user["id"]

    with get_session() as session:
        user = session.get(UserDB, user_id)
        if not user:
            abort(404, description="User not found.")

        records = (
            session.query(SavedRouteDB)
            .filter(SavedRouteDB.user_id == user_id)
            .order_by(SavedRouteDB.created_at.desc())
            .all()
        )

        export_data = []
        for r in records:
            try:
                options = json.loads(r.options_json) if r.options_json else {}
            except json.JSONDecodeError:
                options = {}
            export_data.append(
                {
                    "source_city": r.source_city,
                    "dest_city": r.dest_city,
                    "mode": r.mode,
                    "distance_km": r.distance_km,
                    "travel_time_hours": r.travel_time_hours,
                    "options": options,
                    "created_at": r.created_at.isoformat()
                    if r.created_at
                    else None,
                }
            )

        return jsonify(
            {
                "user": {"id": user.id, "username": user.username},
                "routes": export_data,
            }
        )


if __name__ == "__main__":
    # For local development:
    #   python -m src.web_app
    # then open http://127.0.0.1:5000/dashboard
    app.run(host="127.0.0.1", port=5000, debug=False)

