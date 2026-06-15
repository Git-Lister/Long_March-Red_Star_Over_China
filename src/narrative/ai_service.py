"""AI service: local LLM with fallback."""

from typing import Any, Dict

from ..core.character import Character
from ..core.config import Config


class AIService:
    """Placeholder AI – returns simple template strings, no model needed."""

    def __init__(self, config: Config):
        self.config = config
        self.model_loaded = False

    def _load_model(self, path: str) -> None:
        """Not yet implemented – reserved for llama.cpp."""
        self.model_loaded = False

    def generate(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 256
    ) -> str:
        """Fallback generator – returns user prompt echoed as a quote."""
        return f"[AI placeholder] {user_prompt[:80]}..."

    def generate_dialogue(self, npc: Character, context: str) -> str:
        """Return a simple in‑character line based on NPC name and context."""
        return f'{npc.name} says: "We must stay united. {context}"'

    def generate_narration(self, event_result: Dict[str, Any]) -> str:
        """Turn event result dict into a plain sentence."""
        desc = event_result.get("description", "Something happened.")
        return f"📜 {desc}"

    def generate_combat_report(self, log: Dict[str, Any]) -> str:
        """Turn battle stats into a brief summary."""
        return (
            f"Battle report: Red casualties {log.get('red_casualties', 0)}, "
            f"enemy casualties {log.get('enemy_casualties', 0)}."
        )
