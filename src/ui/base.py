"""Abstract UI interface."""
from typing import Any, Dict, List
from ..core.party import Party
from ..core.world_map import WorldMap
from ..combat.combat import Battlefield

class BaseUI:
    def display(self, screen: str, data: Dict[str, Any]) -> Any:
        raise NotImplementedError
    def show_decision(self, prompt: str, choices: List[str]) -> int:
        raise NotImplementedError
    def update_status(self, party: Party) -> None:
        raise NotImplementedError
    def render_map(self, world_map: WorldMap, party: Party) -> None:
        raise NotImplementedError
    def battle_setup(self, battlefield: Battlefield) -> Dict[str, Any]:
        raise NotImplementedError

