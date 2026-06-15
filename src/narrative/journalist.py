"""Journalist narrator (Edgar Snow stand-in)."""
from typing import Any, Dict, List
from ..core.party import Party

class Journalist:
    def __init__(self, ai_service):
        self.ai = ai_service
        self.notes: List[str] = []

    def interject(self, context: Dict[str, Any], party: Party) -> str:
        raise NotImplementedError

    def final_account(self) -> str:
        raise NotImplementedError

