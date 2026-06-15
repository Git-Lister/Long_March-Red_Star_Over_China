"""Tests for combat simulation."""

import pytest

from src.combat.combat import Battlefield, CombatSimulator, Squad
from src.core.enums import TerrainType, UnitStance


@pytest.fixture
def small_battlefield():
    bf = Battlefield(3, 3, TerrainType.PLAINS)
    bf.red_squads = [
        Squad("Red Guard 1", 10, {"attack": 12, "defense": 10}),
        Squad("Red Guard 2", 8, {"attack": 10, "defense": 8}),
    ]
    bf.enemy_squads = [
        Squad("Nationalist Squad", 10, {"attack": 10, "defense": 10}),
        Squad("Warlord Militia", 8, {"attack": 8, "defense": 6}),
    ]
    return bf


class TestCombat:
    def test_resolve_returns_log(self, small_battlefield):
        sim = CombatSimulator(small_battlefield)
        log = sim.resolve()
        assert "victory" in log
        assert "red_casualties" in log
        assert "enemy_casualties" in log
        assert len(log["rounds"]) > 0

    def test_stance_effects(self):
        # Assault vs Defend
        atk = Squad("A", 10, {"attack": 10, "defense": 10})
        atk.stance = UnitStance.ASSAULT
        defender = Squad("D", 10, {"attack": 10, "defense": 10})
        defender.stance = UnitStance.DEFEND
        assert atk.effective_attack(TerrainType.PLAINS) == 15
        assert defender.effective_defense(TerrainType.PLAINS) == 15

    def test_terrain_modifiers(self):
        squad = Squad("S", 10, {"attack": 10, "defense": 10})
        squad.stance = UnitStance.ASSAULT
        assert squad.effective_attack(TerrainType.FOREST) == 13  # 15 - 2
        assert squad.effective_defense(TerrainType.MOUNTAINS) == 14  # 10 + 4

    def test_casualties_applied(self, small_battlefield):
        sim = CombatSimulator(small_battlefield)
        log = sim.resolve()
        total_red_cas = sum(s.casualties for s in small_battlefield.red_squads)
        assert total_red_cas == log["red_casualties"]
