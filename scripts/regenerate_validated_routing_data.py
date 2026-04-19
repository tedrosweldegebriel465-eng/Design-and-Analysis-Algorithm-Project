"""
Regenerate validated production routing datasets.

This script:
1) Safely de-duplicates city names
2) Rewrites roads against canonical city IDs/names
3) Flags/removes impossible road distances
4) Writes validated CSV files for production routing
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class CityRow:
    city_id: int
    city_name: str
    region: str
    latitude: float
    longitude: float
    population: str
    elevation: str
    is_capital: str
    timezone: str


def _norm_name(name: str) -> str:
    return " ".join((name or "").strip().lower().split())


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p = math.pi / 180.0
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    cities_in = root / "data" / "raw" / "processed" / "ethiopian_cities_clean.csv"
    roads_in = root / "data" / "raw" / "ethiopia_road_network.csv"

    out_dir = root / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    cities_out = out_dir / "ethiopian_cities_validated.csv"
    roads_out = out_dir / "ethiopia_road_network_validated.csv"
    flags_out = out_dir / "ethiopia_road_network_flagged.csv"

    with cities_in.open("r", encoding="utf-8", newline="") as f:
        city_rows_raw = list(csv.DictReader(f))

    cities: List[CityRow] = []
    for r in city_rows_raw:
        cities.append(
            CityRow(
                city_id=int(r["city_id"]),
                city_name=r["city_name"].strip(),
                region=r["region"].strip(),
                latitude=float(r["latitude"]),
                longitude=float(r["longitude"]),
                population=r.get("population", ""),
                elevation=r.get("elevation", ""),
                is_capital=r.get("is_capital", "0"),
                timezone=r.get("timezone", "EAT"),
            )
        )

    # Group by normalized city name.
    groups: Dict[str, List[CityRow]] = defaultdict(list)
    for c in cities:
        groups[_norm_name(c.city_name)].append(c)

    # Canonical city rows and ID remap.
    canonical_cities: List[CityRow] = []
    city_id_remap: Dict[int, int] = {}

    for _, group in groups.items():
        if len(group) == 1:
            c = group[0]
            canonical_cities.append(c)
            city_id_remap[c.city_id] = c.city_id
            continue

        # Same name appears multiple times.
        # Case A: exact duplicate city rows (same region + same coordinates) -> merge.
        signature_buckets: Dict[Tuple[str, float, float], List[CityRow]] = defaultdict(list)
        for c in group:
            signature = (c.region, round(c.latitude, 5), round(c.longitude, 5))
            signature_buckets[signature].append(c)

        if len(signature_buckets) == 1:
            # Pure duplicates: keep smallest ID.
            bucket = sorted(group, key=lambda x: x.city_id)
            keeper = bucket[0]
            canonical_cities.append(keeper)
            for c in bucket:
                city_id_remap[c.city_id] = keeper.city_id
            continue

        # Case B: truly ambiguous same-name places -> keep all, but disambiguate labels.
        # Use "Name (Region)" for duplicates by name.
        for c in sorted(group, key=lambda x: x.city_id):
            c.city_name = f"{c.city_name} ({c.region})"
            canonical_cities.append(c)
            city_id_remap[c.city_id] = c.city_id

    # Ensure deterministic output by city ID.
    canonical_cities = sorted(canonical_cities, key=lambda x: x.city_id)
    city_by_id: Dict[int, CityRow] = {c.city_id: c for c in canonical_cities}

    # Load roads and rewrite against canonical IDs/names.
    with roads_in.open("r", encoding="utf-8", newline="") as f:
        road_rows_raw = list(csv.DictReader(f))

    rewritten_roads: List[dict] = []
    for r in road_rows_raw:
        src_old = int(r["source_id"])
        dst_old = int(r["target_id"])
        src_new = city_id_remap.get(src_old, src_old)
        dst_new = city_id_remap.get(dst_old, dst_old)

        # Skip self-loop after remap (can happen if duplicate IDs collapse).
        if src_new == dst_new:
            continue

        src_city = city_by_id.get(src_new)
        dst_city = city_by_id.get(dst_new)
        if not src_city or not dst_city:
            continue

        rewritten_roads.append(
            {
                "source_id": src_new,
                "source_name": src_city.city_name,
                "target_id": dst_new,
                "target_name": dst_city.city_name,
                "distance_km": float(r["distance_km"]),
                "travel_time_hours": r.get("travel_time_hours", "").strip(),
                "road_type": (r.get("road_type", "regional") or "regional").strip(),
            }
        )

    # Flag impossible roads:
    # Impossible if road distance is meaningfully shorter than straight-line distance.
    # Tolerance avoids false positives from rounding and coordinate noise.
    #
    # Real-data mode:
    # - Keep all real roads in validated output.
    # - Record suspicious records in the flagged output for review.
    tolerance_km = 5.0
    validated_roads: List[dict] = []
    flagged_roads: List[dict] = []

    for r in rewritten_roads:
        src = city_by_id[int(r["source_id"])]
        dst = city_by_id[int(r["target_id"])]
        geo_km = _haversine_km(src.latitude, src.longitude, dst.latitude, dst.longitude)
        dist_km = float(r["distance_km"])

        if dist_km + tolerance_km < geo_km:
            flagged = dict(r)
            flagged["straight_line_km"] = round(geo_km, 2)
            flagged["reason"] = "distance_shorter_than_straight_line"
            flagged_roads.append(flagged)
        validated_roads.append(r)

    final_roads = sorted(
        validated_roads,
        key=lambda x: (int(x["source_id"]), int(x["target_id"]), float(x["distance_km"])),
    )

    # Write validated cities.
    with cities_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "city_id",
                "city_name",
                "region",
                "latitude",
                "longitude",
                "population",
                "elevation",
                "is_capital",
                "timezone",
            ]
        )
        for c in canonical_cities:
            writer.writerow(
                [
                    c.city_id,
                    c.city_name,
                    c.region,
                    f"{c.latitude:.5f}",
                    f"{c.longitude:.5f}",
                    c.population,
                    c.elevation,
                    c.is_capital,
                    c.timezone,
                ]
            )

    # Write validated roads.
    with roads_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "source_id",
                "source_name",
                "target_id",
                "target_name",
                "distance_km",
                "travel_time_hours",
                "road_type",
            ]
        )
        for r in final_roads:
            writer.writerow(
                [
                    r["source_id"],
                    r["source_name"],
                    r["target_id"],
                    r["target_name"],
                    f"{float(r['distance_km']):.2f}",
                    r["travel_time_hours"],
                    r["road_type"],
                ]
            )

    # Write flags for removed roads.
    with flags_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "source_id",
                "source_name",
                "target_id",
                "target_name",
                "distance_km",
                "straight_line_km",
                "road_type",
                "reason",
            ]
        )
        for r in flagged_roads:
            writer.writerow(
                [
                    r["source_id"],
                    r["source_name"],
                    r["target_id"],
                    r["target_name"],
                    f"{float(r['distance_km']):.2f}",
                    f"{float(r['straight_line_km']):.2f}",
                    r["road_type"],
                    r["reason"],
                ]
            )

    print("Validated routing datasets generated:")
    print(f"- {cities_out}")
    print(f"- {roads_out}")
    print(f"- {flags_out}")
    print(f"Cities: {len(canonical_cities)}")
    print(f"Roads kept: {len(final_roads)}")
    print(f"Roads flagged: {len(flagged_roads)}")


if __name__ == "__main__":
    main()

