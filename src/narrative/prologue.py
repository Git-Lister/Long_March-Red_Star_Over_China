"""Interactive prologue: the interview that shapes your commander."""

from typing import Callable, Dict, List, Optional, Tuple

from ..core.character import Commander
from ..core.enums import Origin, PrologueChoice


class Prologue:
    """Runs the opening interview; returns a Commander ready for the march."""

    def __init__(self, ai_service):
        self.ai = ai_service

    def run(self, prompt_callback: Optional[Callable] = None) -> Commander:
        """
        Conduct the interview.  `prompt_callback(question, options)` may be
        supplied for UI integration; if None, falls back to terminal input.
        Returns a fully configured Commander.
        """
        # 1. Wake-up scene
        self._narrate(
            "你醒来了 – You wake inside a cool yáodòng (cave‑house). "
            "A báiguǐzi (white devil) peers at you through round glasses."
        )
        # 2. Last night’s activity
        last_night = self._ask(
            "You recall last night you were…",
            [
                ("Writing poetry", PrologueChoice.WRITING_POETRY),
                ("Physical training", PrologueChoice.PHYSICAL_TRAINING),
                ("Studying maps", PrologueChoice.STUDYING_MAPS),
                ("Sneaking a pipe of opium", PrologueChoice.OPIUM),
            ],
            prompt_callback,
        )
        # 3. Origins
        origin_choice = self._ask(
            "The journalist asks about your background. You tell him you are…",
            [
                ("A peasant, born to the soil", Origin.PEASANT),
                ("An intellectual, raised on books", Origin.INTELLECTUAL),
                ("A factory worker, hands of callous", Origin.WORKER),
                ("Returned from study abroad", Origin.FOREIGN_EDUCATED),
            ],
            prompt_callback,
        )
        # 4. Name
        name = self._get_name(prompt_callback)

        # 5. Build commander from choices
        traits, inventory = self._apply_choices(last_night, origin_choice)
        commander = Commander(name, origin_choice, traits, inventory)
        # 6. Closing narration
        self._narrate(
            f"The journalist scratches notes. 'Comrade {commander.name}, "
            f"let us begin the account of your Long March.'"
        )
        return commander

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _narrate(self, text: str) -> None:
        """Show narration text; in terminal we simply print."""
        print(f"\n📖 {text}")

    def _ask(
        self,
        question: str,
        options: List[Tuple[str, object]],
        callback: Optional[Callable],
    ) -> object:
        """
        Present a question, return the chosen value.
        `callback(question, [label for label, val in options])` if provided,
        otherwise use built-in input.
        """
        labels = [opt[0] for opt in options]
        if callback:
            idx = callback(question, labels)
        else:
            print(f"\n❓ {question}")
            for i, label in enumerate(labels):
                print(f"  [{i + 1}] {label}")
            idx = int(input("Your choice: ")) - 1
        if idx < 0 or idx >= len(options):
            idx = 0
        return options[idx][1]

    def _get_name(self, callback: Optional[Callable]) -> str:
        """Ask for the commander’s name."""
        if callback:
            return callback("What is your name, comrade?", []) or "Anonymous"
        return input("\n✏️  What is your name, comrade? ") or "Anonymous"

    def _apply_choices(
        self, last_night: PrologueChoice, origin: Origin
    ) -> Tuple[Dict[str, int], Dict[str, int]]:
        """Convert narrative choices into game stats."""
        traits = {
            "health": 100,
            "leadership": 50,
            "political_credibility": 50,
            "survival": 50,
        }
        inventory = {}

        # Origin base modifiers
        if origin == Origin.PEASANT:
            traits["survival"] += 20
            traits["political_credibility"] -= 5
            inventory["sickle"] = 1
        elif origin == Origin.INTELLECTUAL:
            traits["leadership"] += 15
            traits["health"] -= 10
            inventory["books"] = 1
        elif origin == Origin.WORKER:
            traits["health"] += 10
            traits["political_credibility"] += 10
            inventory["hammer"] = 1
        elif origin == Origin.FOREIGN_EDUCATED:
            traits["leadership"] += 10
            traits["survival"] -= 10
            inventory["compass"] = 1

        # Last night modifiers
        if last_night == PrologueChoice.WRITING_POETRY:
            traits["political_credibility"] += 15
            inventory["pen"] = 1
        elif last_night == PrologueChoice.PHYSICAL_TRAINING:
            traits["health"] += 10
            traits["survival"] += 5
        elif last_night == PrologueChoice.STUDYING_MAPS:
            traits["leadership"] += 15
            traits["survival"] += 5
            inventory["map"] = 1
        elif last_night == PrologueChoice.OPIUM:
            traits["health"] -= 15
            traits["political_credibility"] -= 10
            inventory["opium_pipe"] = 1

        return traits, inventory
