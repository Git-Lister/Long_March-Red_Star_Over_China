"""World map: nodes and the Long March route."""

from typing import Dict, List, Optional, Tuple

from .utils import load_json


class MapNode:
    """A location along the march."""

    def __init__(
        self,
        node_id: str,
        name: str,
        lat: float,
        lon: float,
        node_type: str,
        description: str,
    ):
        self.id = node_id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.type = node_type  # 'city','river_crossing','mountain_pass','village'
        self.description = description
        self.connections: List[Tuple[str, float]] = []  # (neighbor_id, distance_km)


class WorldMap:
    """Holds all nodes and the historical route."""

    def __init__(self, route_file: str = "data/map.json"):
        self.nodes: Dict[str, MapNode] = {}
        self.current_node_id: str = ""
        self.route: List[str] = []  # ordered node IDs along the historical path
        self.route_index: int = 0  # position in self.route
        self.distance_traveled: float = 0.0  # km towards next node
        if route_file:
            self._load(route_file)

    def _load(self, filename: str) -> None:
        """Load nodes and route from a JSON file."""
        data = load_json(filename)
        # Load nodes
        for node_data in data.get("nodes", []):
            node = MapNode(
                node_id=node_data["id"],
                name=node_data["name"],
                lat=node_data["lat"],
                lon=node_data["lon"],
                node_type=node_data.get("type", "village"),
                description=node_data.get("description", ""),
            )
            self.nodes[node.id] = node
        # Load route
        self.route = data.get("route", [])
        if self.route:
            self.current_node_id = self.route[0]
            self.route_index = 0
        # Build connections from route (linear sequence)
        for i in range(len(self.route) - 1):
            cur_id = self.route[i]
            next_id = self.route[i + 1]
            dist = self._distance_between(cur_id, next_id)
            if cur_id in self.nodes:
                self.nodes[cur_id].connections.append((next_id, dist))

    def _distance_between(self, node_a: str, node_b: str) -> float:
        """
        Simple Euclidean distance from lat/lon.
        For now this is approximate; we can refine with proper GIS later.
        """
        a = self.nodes.get(node_a)
        b = self.nodes.get(node_b)
        if not a or not b:
            return 10.0  # fallback
        import math

        # Approximate: 1° ≈ 111 km
        dx = (a.lon - b.lon) * 111.0
        dy = (a.lat - b.lat) * 111.0
        return math.sqrt(dx * dx + dy * dy)

    def current_node(self) -> Optional[MapNode]:
        return self.nodes.get(self.current_node_id)

    def next_node(self) -> Optional[MapNode]:
        """Return the next node on the route, or None if at the end."""
        if self.route_index + 1 < len(self.route):
            next_id = self.route[self.route_index + 1]
            return self.nodes.get(next_id)
        return None

    def advance(self, km: float) -> bool:
        """
        Advance km toward the next node.
        Returns True if a node was reached (and current_node_id updated).
        """
        if self.route_index >= len(self.route) - 1:
            # At end of route
            return False

        current = self.current_node()
        target = self.next_node()
        if not current or not target:
            return False

        # Determine total distance to next node
        total_dist = 0.0
        for conn_id, dist in current.connections:
            if conn_id == target.id:
                total_dist = dist
                break
        if total_dist == 0.0:
            # Fallback: compute on the fly
            total_dist = self._distance_between(current.id, target.id)

        self.distance_traveled += km
        if self.distance_traveled >= total_dist:
            # Arrived at next node
            self.distance_traveled = 0.0
            self.route_index += 1
            self.current_node_id = self.route[self.route_index]
            return True
        return False

    def route_progress(self) -> float:
        """Return a progress fraction (0.0 to 1.0) along the entire route."""
        if len(self.route) < 2:
            return 1.0
        total_distance = 0.0
        travelled = 0.0
        for i in range(len(self.route) - 1):
            a = self.route[i]
            b = self.route[i + 1]
            d = self._distance_between(a, b)
            total_distance += d
            if i < self.route_index:
                travelled += d
            elif i == self.route_index:
                travelled += self.distance_traveled
        return min(travelled / total_distance, 1.0) if total_distance > 0 else 1.0
