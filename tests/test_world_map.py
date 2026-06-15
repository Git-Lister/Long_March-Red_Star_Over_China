"""Tests for src.core.world_map."""

import json
import os
import tempfile

import pytest

from src.core.world_map import MapNode, WorldMap


@pytest.fixture
def sample_map_data():
    return {
        "nodes": [
            {
                "id": "ruijin",
                "name": "Ruijin",
                "lat": 25.9,
                "lon": 116.0,
                "type": "city",
                "description": "Starting point",
            },
            {
                "id": "xiang_river",
                "name": "Xiang River",
                "lat": 27.2,
                "lon": 112.0,
                "type": "river_crossing",
                "description": "Bloody crossing",
            },
            {
                "id": "zunyi",
                "name": "Zunyi",
                "lat": 27.7,
                "lon": 106.9,
                "type": "city",
                "description": "Zunyi Conference",
            },
            {
                "id": "yanan",
                "name": "Yan'an",
                "lat": 36.6,
                "lon": 109.5,
                "type": "city",
                "description": "End point",
            },
        ],
        "route": ["ruijin", "xiang_river", "zunyi", "yanan"],
    }


@pytest.fixture
def world_map(sample_map_data):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "map.json")
        with open(path, "w") as f:
            json.dump(sample_map_data, f)
        wm = WorldMap(route_file=path)
        return wm


class TestWorldMap:
    def test_load_nodes(self, world_map):
        assert len(world_map.nodes) == 4
        assert "ruijin" in world_map.nodes

    def test_route_setup(self, world_map):
        assert world_map.current_node_id == "ruijin"
        assert len(world_map.route) == 4

    def test_next_node(self, world_map):
        nxt = world_map.next_node()
        assert nxt is not None
        assert nxt.id == "xiang_river"

    def test_advance_partial(self, world_map):
        reached = world_map.advance(10.0)
        assert reached is False
        assert world_map.current_node_id == "ruijin"
        assert world_map.distance_traveled > 0

    def test_advance_reach_node(self, world_map):
        total = world_map._distance_between("ruijin", "xiang_river")
        reached = world_map.advance(total)
        assert reached is True
        assert world_map.current_node_id == "xiang_river"
        assert world_map.distance_traveled == 0.0

    def test_route_progress(self, world_map):
        assert world_map.route_progress() == 0.0
        while world_map.next_node():
            total = world_map._distance_between(
                world_map.current_node_id, world_map.next_node().id
            )
            world_map.advance(total)
        assert world_map.route_progress() == 1.0
