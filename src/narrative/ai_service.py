"""AI service: Ollama integration with fallback."""

import logging
from typing import Any, Dict, Optional

from ..core.character import Character
from ..core.config import Config

logger = logging.getLogger(__name__)


class AIService:
    """Generates text via Ollama. Falls back to static text if unavailable."""

    def __init__(self, config: Config):
        self.config = config
        self.ollama = None
        self.model_loaded = False
        if config.USE_AI and config.AI_BACKEND == "ollama":
            self._init_ollama(config.OLLAMA_MODEL, config.OLLAMA_HOST)

    def _init_ollama(self, model: str, host: str) -> None:
        """Connect to Ollama and verify the model exists."""
        try:
            import ollama

            client = ollama.Client(host=host)
            # Verify model exists
            response = client.list()
            models = response.get("models", [])
            # The model name can be accessed via m['model'] or m.model
            model_names = {
                m["model"] if isinstance(m, dict) else m.model for m in models
            }
            if model not in model_names:
                logger.warning(
                    f"Model '{model}' not found in Ollama. Available: {model_names}. Using fallback."
                )
                return
            self.ollama = client
            self.model_loaded = True
            logger.info(f"Ollama connected, model '{model}' ready.")
        except ImportError:
            logger.warning(
                "ollama Python package not installed. Run `pip install ollama`. Using fallback."
            )
        except Exception as e:
            logger.warning(f"Ollama init failed: {e}. Using fallback.")

    def generate(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 256
    ) -> str:
        """Core generation. Falls back if Ollama unavailable."""
        if not self.model_loaded or self.ollama is None:
            return self._fallback(user_prompt)

        try:
            response = self.ollama.chat(
                model=self.config.OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={
                    "temperature": 0.7,
                    "num_predict": max_tokens,
                },
            )
            text = response["message"]["content"]
            return text.strip()
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return self._fallback(user_prompt)

    def _fallback(self, user_prompt: str) -> str:
        """Static fallback text when AI is disabled."""
        return f"[The journalist records your actions in his notebook.] {user_prompt[:60]}..."

    def generate_dialogue(self, npc: Character, context: str) -> str:
        prompt = (
            f"The character is {npc.name}, a {npc.bio}. "
            f"The current situation: {context}. "
            f"Respond in one short paragraph as if speaking directly to the commander."
        )
        return self.generate(
            system_prompt=self._system_prompt("dialogue"),
            user_prompt=prompt,
            max_tokens=128,
        )

    def generate_narration(self, event_result: Dict[str, Any]) -> str:
        desc = event_result.get("description", "An event occurred.")
        effects = event_result.get("effects", {})
        prompt = (
            f"Event: {desc}\n"
            f"Outcome: {effects}\n"
            "Write a brief, heroic, Soviet-realist style narration of this event "
            "as if it were recorded by a Red Army journalist. Keep it under 3 sentences."
        )
        return self.generate(
            system_prompt=self._system_prompt("narration"),
            user_prompt=prompt,
            max_tokens=192,
        )

    def generate_combat_report(self, log: Dict[str, Any]) -> str:
        red_cas = log.get("red_casualties", 0)
        enemy_cas = log.get("enemy_casualties", 0)
        victory = log.get("victory", False)
        prompt = (
            f"Battle result: {'Victory' if victory else 'Defeat'}.\n"
            f"Red Army casualties: {red_cas}. Enemy casualties: {enemy_cas}.\n"
            "Write a vivid, woodcut-poster-style report of the battle, highlighting "
            "individual heroism and the cost of revolution."
        )
        return self.generate(
            system_prompt=self._system_prompt("combat"),
            user_prompt=prompt,
            max_tokens=256,
        )

    def _system_prompt(self, mode: str) -> str:
        base = (
            "You are a Communist Party propagandist embedded with the Red Army during "
            "the 1934-35 Long March. Your writing style is inspired by Edgar Snow's "
            "'Red Star Over China' and Chinese Soviet woodcut posters. Use vivid, "
            "heroic, and occasionally grim imagery. Never break character. "
            "Do not use modern terms or references. Write in English."
        )
        if mode == "dialogue":
            return base + " You are speaking as this NPC. Use first-person. Be terse."
        elif mode == "narration":
            return base + " Narrate in third person. Be poetic but concise."
        elif mode == "combat":
            return (
                base
                + " Describe the battle with stark realism. Mention sacrifice and resolve."
            )
        return base
