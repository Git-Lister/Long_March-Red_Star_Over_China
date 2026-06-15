"""Base Character and Commander classes."""
from typing import Dict, List, Optional
from .enums import Origin


class Character:
    """A named individual (soldier, porter, NPC)."""
    def __init__(self, name: str, bio: str, stats: Dict[str, int]):
        self.name = name
        self.bio = bio
        self.stats = stats           # e.g. health, loyalty, skill
        self.status_effects: List[str] = []

    def is_alive(self) -> bool:
        return self.stats.get("health", 0) > 0

    def apply_damage(self, amount: int, cause: str = "") -> None:
        """Reduce health by amount, optionally recording the cause."""
        if amount < 0:
            raise ValueError("Damage amount must be non-negative")
        self.stats["health"] = max(0, self.stats.get("health", 0) - amount)
        # The cause may be logged elsewhere; this method only applies the numeric effect.

    def add_effect(self, effect: str) -> None:
        """Add a status effect (e.g., 'wounded', 'exhausted')."""
        if effect not in self.status_effects:
            self.status_effects.append(effect)

    def remove_effect(self, effect: str) -> None:
        """Remove a status effect if present."""
        if effect in self.status_effects:
            self.status_effects.remove(effect)

    def __repr__(self) -> str:
        return f"Character({self.name}, health={self.stats.get('health', 0)})"


class Commander(Character):
    """Player character, shaped by prologue."""
    def __init__(self, name: str, origin: Origin, traits: Dict[str, int],
                 inventory: Dict[str, int]):
        # Start with full health; traits contain leadership, political_credibility, etc.
        base_stats = {"health": 100, **traits}
        super().__init__(name, "", base_stats)
        self.origin = origin
        self.traits = traits
        self.inventory = inventory    # personal items (e.g., "pen", "opium_pipe")
        self.reputation: Dict[str, int] = {}  # with NPCs/factions