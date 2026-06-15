"""Event system: base, random, major events, and manager."""

from typing import Any, Callable, Dict, List, Optional

from ..core.party import Party
from ..core.time_manager import TimeManager


class GameEvent:
    """Any encounter: random, story, or choice‑based."""

    def __init__(
        self,
        event_id: str,
        conditions: Callable[[Party, TimeManager], bool],
        data: dict,
    ):
        self.id = event_id
        self.conditions = conditions  # triggered when True
        self.data = data  # holds choices, effects, flavour

    def is_triggered(self, party: Party, time: TimeManager) -> bool:
        return self.conditions(party, time)


class RandomEvent(GameEvent):
    """Random encounter that may fire at any time based on frequency."""

    def __init__(self, *args, frequency: float = 0.05):
        super().__init__(*args)
        self.frequency = frequency  # chance per check


class MajorStoryEvent(GameEvent):
    """Key historical event tied to a specific node or date."""

    def __init__(
        self,
        *args,
        trigger_node: Optional[str] = None,
        trigger_date: Optional[str] = None,
    ):
        super().__init__(*args)
        self.trigger_node = trigger_node
        self.trigger_date = trigger_date


class EventManager:
    """Holds all events, checks triggers, applies choices."""

    def __init__(self):
        self.events: List[GameEvent] = []
        self.completed: set = set()

    def register(self, event: GameEvent) -> None:
        self.events.append(event)

    def get_active_events(self, party: Party, time: TimeManager) -> List[GameEvent]:
        """Return events whose conditions are met and not yet completed."""
        active = []
        for ev in self.events:
            if ev.id in self.completed:
                continue
            if ev.is_triggered(party, time):
                active.append(ev)
        return active

    def resolve(
        self, event: GameEvent, player_choice: int, party: Party, ai
    ) -> Dict[str, Any]:
        """
        Apply the player's choice index to the event.
        Returns a dict with narrative, stat changes, and completion flag.
        """
        choices = event.data.get("choices", [])
        if player_choice < 0 or player_choice >= len(choices):
            return {"description": "Invalid choice.", "effects": {}}

        chosen = choices[player_choice]
        effects = chosen.get("effects", {})

        # Apply numeric effects
        for stat, delta in effects.items():
            if stat == "morale":
                party.update_morale(delta)
            elif stat == "political_cohesion":
                party.update_political_cohesion(delta)
            elif stat in party.supplies:
                party.supplies[stat] = max(0, party.supplies[stat] + delta)
            elif stat == "health" and party.commander:
                party.commander.apply_damage(-delta if delta < 0 else delta)

        # Mark event as completed
        self.completed.add(event.id)

        # Generate narrative via AI
        narration = ai.generate_narration(
            {
                "description": chosen.get("text", "You made a choice."),
                "effects": effects,
            }
        )

        return {
            "text": chosen.get("text", ""),
            "narration": narration,
            "effects": effects,
            "event_id": event.id,
        }
