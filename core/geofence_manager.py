"""Geofence Validator and Breach Detection System for UAVs."""

import json
from typing import List, Dict, Any, Tuple, Optional
from core.telemetry import calculate_haversine_distance, Position


class GeofenceManager:
    """Monitors drone position against horizontal 2D polygon boundaries and altitude limits."""

    def __init__(self, config_path: Optional[str] = None):
        self.enabled: bool = False
        self.polygon_vertices: List[Tuple[float, float]] = []  # List of (lat, lon)
        self.max_altitude_rel: float = 50.0                    # meters
        self.min_altitude_rel: float = 0.5                     # meters
        self.max_distance_from_home: float = 1000.0            # meters
        self.name: str = "Default_Geofence"

        if config_path:
            self.load_from_json(config_path)

    def load_from_json(self, file_path: str):
        """Loads geofence definitions from a JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.name = data.get("name", "Unnamed_Fence")
        self.enabled = data.get("enabled", True)
        self.max_altitude_rel = data.get("max_altitude_relative", 50.0)
        self.min_altitude_rel = data.get("min_altitude_relative", 0.5)
        self.max_distance_from_home = data.get("max_distance_from_home_meters", 1000.0)

        raw_poly = data.get("polygon_vertices", [])
        self.polygon_vertices = [(item["lat"], item["lon"]) for item in raw_poly]

    def set_polygon(self, vertices: List[Tuple[float, float]]):
        """Sets vertices directly as [(lat, lon), ...]."""
        self.polygon_vertices = vertices

    def is_point_inside_polygon(self, lat: float, lon: float) -> bool:
        """Ray-casting algorithm to test whether a (lat, lon) coordinate is inside the boundary polygon."""
        if len(self.polygon_vertices) < 3:
            # If no polygon is set, assume no boundary breach
            return True

        n = len(self.polygon_vertices)
        inside = False

        p1_lat, p1_lon = self.polygon_vertices[0]
        for i in range(n + 1):
            p2_lat, p2_lon = self.polygon_vertices[i % n]
            if lon > min(p1_lon, p2_lon):
                if lon <= max(p1_lon, p2_lon):
                    if lat <= max(p1_lat, p2_lat):
                        if p1_lon != p2_lon:
                            xinters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                        if p1_lat == p2_lat or lat <= xinters:
                            inside = not inside
            p1_lat, p1_lon = p2_lat, p2_lon

        return inside

    def check_position(self, pos: Position, home: Optional[Position] = None) -> Tuple[bool, str]:
        """Validates current position against all fence constraints.
        
        Returns:
            (is_safe: bool, reason: str)
        """
        if not self.enabled:
            return True, "Geofence Disabled"

        # 1. Altitude Upper Limit
        if pos.alt_rel > self.max_altitude_rel:
            return False, f"Upper Altitude Breach: {pos.alt_rel:.1f}m > max {self.max_altitude_rel:.1f}m"

        # 2. Polygon Boundary Breach
        if len(self.polygon_vertices) >= 3 and not self.is_point_inside_polygon(pos.lat, pos.lon):
            return False, f"Boundary Breach: Lat={pos.lat:.6f}, Lon={pos.lon:.6f} outside polygon"

        # 3. Maximum Radius from Home (Cylinder Fence)
        if home is not None and self.max_distance_from_home > 0:
            dist = calculate_haversine_distance(pos.lat, pos.lon, home.lat, home.lon)
            if dist > self.max_distance_from_home:
                return False, f"Max Radius Breach: {dist:.1f}m > limit {self.max_distance_from_home:.1f}m"

        return True, "Within Safe Perimeter"
