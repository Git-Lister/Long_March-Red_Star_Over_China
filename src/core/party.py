"""Party (Red Army unit) class: supplies, morale, casualties."""

from typing import Dict, List

from .character import Character, Commander
from .utils import clamp


class Party:
    """The entire Red Army unit under player command."""

    def __init__(
        self,
        commander: Commander,
        soldiers: List[Character],
        porters: List[Character],
        commissar: Character,
    ):
        self.commander = commander
        self.soldiers = soldiers
        self.porters = porters
        self.commissar = commissar
        self.supplies = {
            "rice_kg": 0.0,
            "ammo": 0,
            "medicine": 0,
            "pamphlets": 0,
            "batteries": 0,
        }
        self.morale: int = 50
        self.political_cohesion: int = 50
        self.codex: List[str] = []  # unlocked historical terms

    def total_people(self) -> int:
        return len(self.soldiers) + len(self.porters) + 1  # +1 for commander

    def consume_daily(self) -> Dict[str, float]:
        """
        Deduct daily resource consumption.
        Returns a dict of any shortages (negative values mean deficit).
        """
        people = self.total_people()
        # Rice: each person eats DAILY_RICE_KG_PER_PERSON kg
        from .config import Config

        rice_needed = people * Config.DAILY_RICE_KG_PER_PERSON
        rice_available = self.supplies.get("rice_kg", 0.0)
        rice_consumed = min(rice_needed, rice_available)
        self.supplies["rice_kg"] -= rice_consumed

        # Other supplies are consumed at flat rates (placeholder logic)
        # Ammo: 1 unit per 10 people if travelling through hostile territory
        # For now, just a minimal consumption
        self.supplies["ammo"] = max(0, self.supplies.get("ammo", 0) - 1)

        shortages = {
            "rice_kg": rice_needed - rice_consumed,
        }
        # If rice was insufficient, apply starvation morale penalty
        if shortages["rice_kg"] > 0:
            self.update_morale(-5, "starvation")
        return shortages

    def update_morale(self, delta: int, reason: str = "") -> None:
        self.morale = int(clamp(self.morale + delta, 0, 100))

    def update_political_cohesion(self, delta: int, reason: str = "") -> None:
        self.political_cohesion = int(clamp(self.political_cohesion + delta, 0, 100))

    def remove_casualties(self, count: int, unit: str) -> List[Character]:
        """
        Remove dead/wounded from the specified unit ('soldiers' or 'porters').
        Returns the list of removed Characters.
        """
        target = self.soldiers if unit == "soldiers" else self.porters
        if count > len(target):
            count = len(target)
        removed = target[:count]
        del target[:count]
        # Losing people impacts morale
        self.update_morale(-3 * count, f"casualties in {unit}")
        return removed
