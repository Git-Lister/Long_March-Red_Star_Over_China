"""Combat simulation: squads, battlefield, resolver."""

import random
from typing import Any, Dict, List, Optional, Tuple

from ..core.config import Config
from ..core.enums import TerrainType, UnitStance


class Squad:
    """A tactical unit in combat."""

    def __init__(self, name: str, size: int, stats: Dict[str, int]):
        self.name = name
        self.size = size  # number of fighters
        self.stats = stats  # attack, defense, morale, experience
        self.stance: UnitStance = UnitStance.DEFEND
        self.casualties: int = 0

    def effective_attack(self, terrain: TerrainType) -> int:
        base = self.stats.get("attack", 10)
        # Stance modifiers
        if self.stance == UnitStance.ASSAULT:
            base += 5
        elif self.stance == UnitStance.AMBUSH:
            base += 8
        elif self.stance == UnitStance.RETREAT:
            base -= 4
        # Terrain modifiers
        if terrain == TerrainType.FOREST:
            base -= 2
        elif terrain == TerrainType.HILLS:
            base += 2
        elif terrain == TerrainType.RIVER:
            base -= 3
        return max(0, base)

    def effective_defense(self, terrain: TerrainType) -> int:
        base = self.stats.get("defense", 10)
        if self.stance == UnitStance.DEFEND:
            base += 5
        elif self.stance == UnitStance.RETREAT:
            base += 2
        if terrain == TerrainType.FOREST:
            base += 3
        elif terrain == TerrainType.MOUNTAINS:
            base += 4
        elif terrain == TerrainType.VILLAGE:
            base += 2
        return max(0, base)


class Battlefield:
    """A grid with terrain and deployed squads."""

    def __init__(self, width: int, height: int, default_terrain: TerrainType):
        self.width = width
        self.height = height
        self.grid: List[List[TerrainType]] = [
            [default_terrain for _ in range(width)] for _ in range(height)
        ]
        self.red_squads: List[Squad] = []
        self.enemy_squads: List[Squad] = []

    def set_terrain(self, x: int, y: int, terrain: TerrainType) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = terrain

    def terrain_at(self, x: int, y: int) -> TerrainType:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return TerrainType.PLAINS


class CombatSimulator:
    """Resolves a battle from unit stances and terrain."""

    def __init__(self, battlefield: Battlefield):
        self.bf = battlefield

    def resolve(self) -> Dict[str, Any]:
        """
        Run combat rounds until one side is destroyed or morale breaks.
        Returns a detailed log.
        """
        log = {
            "rounds": [],
            "victory": False,
            "red_casualties": 0,
            "enemy_casualties": 0,
            "morale_delta": 0,
            "notable_acts": [],
        }

        red_morale = 100
        enemy_morale = 100

        # Fight until one side has no squads or morale breaks
        while (
            self._red_alive()
            and self._enemy_alive()
            and red_morale > 0
            and enemy_morale > 0
        ):
            # Each squad attacks an opposing squad
            round_log = []

            # Red attacks
            for squad in self.bf.red_squads:
                if squad.size == 0:
                    continue
                target = self._choose_target(self.bf.enemy_squads)
                if target:
                    kills = self._resolve_attack(squad, target)
                    target.casualties += kills
                    target.size = max(0, target.size - kills)
                    if kills > 0:
                        round_log.append(f"{squad.name} kills {kills} of {target.name}")
                        if kills >= target.size * 0.5:
                            enemy_morale -= 10

            # Enemy attacks
            for squad in self.bf.enemy_squads:
                if squad.size == 0:
                    continue
                target = self._choose_target(self.bf.red_squads)
                if target:
                    kills = self._resolve_attack(squad, target)
                    target.casualties += kills
                    target.size = max(0, target.size - kills)
                    if kills > 0:
                        round_log.append(f"{squad.name} kills {kills} of {target.name}")
                        if kills >= target.size * 0.5:
                            red_morale -= 10

            log["rounds"].append(
                {
                    "red_morale": red_morale,
                    "enemy_morale": enemy_morale,
                    "events": round_log,
                }
            )

        # Determine outcome
        red_cas = sum(s.casualties for s in self.bf.red_squads)
        enemy_cas = sum(s.casualties for s in self.bf.enemy_squads)
        log["red_casualties"] = red_cas
        log["enemy_casualties"] = enemy_cas
        log["victory"] = self._red_alive() and red_morale > 0
        log["morale_delta"] = (
            -5 if not log["victory"] else (5 if enemy_cas > red_cas else 0)
        )

        return log

    def _resolve_attack(self, attacker: Squad, defender: Squad) -> int:
        """Roll dice and return number of kills."""
        terrain = TerrainType.PLAINS  # simplified; could be based on positions
        atk = attacker.effective_attack(terrain)
        df = defender.effective_defense(terrain)
        roll = random.randint(1, Config.COMBAT_DICE_SIDES)
        if roll == Config.COMBAT_DICE_SIDES:
            # Critical hit: max possible damage
            kills = max(1, int(attacker.size * 0.2))
        elif roll + atk > df + 10:
            kills = max(1, int(attacker.size * 0.15))
        else:
            kills = max(0, int(attacker.size * 0.05))
        return min(kills, defender.size)

    def _choose_target(self, targets: List[Squad]) -> Optional[Squad]:
        """Choose a random living squad to attack."""
        alive = [s for s in targets if s.size > 0]
        return random.choice(alive) if alive else None

    def _red_alive(self) -> bool:
        return any(s.size > 0 for s in self.bf.red_squads)

    def _enemy_alive(self) -> bool:
        return any(s.size > 0 for s in self.bf.enemy_squads)
