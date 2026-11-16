"""Converts waypoint lists or CSV flight logs into GeoJSON LineString format."""

import json
from typing import List, Tuple

def waypoints_to_geojson(coords: List[Tuple[float, float]], output_path: str):
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[lon, lat] for lat, lon in coords]
                },
                "properties": {
                    "description": "KKRTI Autonomous UAV Flight Path"
                }
            }
        ]
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)
    print(f"Exported GeoJSON to {output_path}")
