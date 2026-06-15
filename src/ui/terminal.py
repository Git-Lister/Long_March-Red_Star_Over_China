"""Terminal UI implementing the BaseUI interface."""

from typing import Any, Dict, List

from ..combat.combat import Battlefield
from ..core.party import Party
from ..core.world_map import WorldMap
from .base import BaseUI


class TerminalUI(BaseUI):
    """Concrete UI for terminal/console play."""

    def display(self, screen: str, data: Dict[str, Any]) -> Any:
        """Generic display method; unused in terminal prototype."""
        print(data.get("text", ""))

    def show_decision(self, prompt: str, choices: List[str]) -> int:
        """Present a list of choices and return the selected index."""
        print(f"\n❓ {prompt}")
        for i, opt in enumerate(choices):
            print(f"  [{i + 1}] {opt}")
        while True:
            try:
                choice = int(input("Your choice: ")) - 1
                if 0 <= choice < len(choices):
                    return choice
            except ValueError:
                pass
            print("Invalid choice, try again.")

    def prompt_string(self, question: str, default: str = "") -> str:
        """Ask for a string input."""
        return input(f"\n✏️  {question} ") or default

    def update_status(self, party: Party) -> None:
        """Print the current party and location status."""
        # This will be called from Game with all needed info,
        # but for now we keep status printing in main loop.
        pass

    def render_map(self, world_map: WorldMap, party: Party) -> None:
        """Display a simple text map (stub)."""
        node = world_map.current_node()
        if node:
            print(f"\n📍 Current location: {node.name} – {node.description}")
            print(f"   Distance travelled: {world_map.distance_traveled:.0f} km")
            next_node = world_map.next_node()
            if next_node:
                print(f"   Next stop: {next_node.name}")

    def battle_setup(self, battlefield: Battlefield) -> Dict[str, Any]:
        """Stub for tactical battle; returns empty deployment."""
        print("\n⚔️  BATTLE STATIONS! (Tactical combat not yet implemented)")
        return {}
