"""Game entry point — terminal prototype."""

import logging
from typing import Optional

from .core.character import Character, Commander
from .core.config import Config
from .core.party import Party
from .core.time_manager import TimeManager
from .core.world_map import WorldMap
from .narrative.ai_service import AIService
from .narrative.event_system import EventManager, GameEvent
from .narrative.journalist import Journalist
from .narrative.prologue import Prologue

logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------------------------
# Simple terminal input helpers (until TerminalUI is complete)
# ---------------------------------------------------------------------------
def terminal_choice(question: str, choices: list) -> int:
    """Display a question and return the index of the chosen option."""
    print(f"\n❓ {question}")
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


def terminal_input(question: str, default: str = "Anonymous") -> str:
    """Ask for a string."""
    return input(f"\n✏️  {question} ") or default


# ---------------------------------------------------------------------------
# Main Game class
# ---------------------------------------------------------------------------
class Game:
    def __init__(self, config: Config):
        self.config = config
        self.ai = AIService(config)
        self.commander: Optional[Commander] = None
        self.party: Optional[Party] = None
        self.world_map = WorldMap()
        self.time_mgr = TimeManager()
        self.event_mgr = EventManager()
        self.journalist = Journalist(self.ai)
        self.state = "menu"
        self._setup_events()

    def new_game(self, ui_mode: str = "terminal") -> None:
        """Run prologue, initialise party, start main loop."""
        print("\n" + "=" * 60)
        print("  LONG MARCH: RED STAR OVER CHINA")
        print("=" * 60)
        # Prologue
        prologue = Prologue(self.ai)
        self.commander = prologue.run(
            prompt_callback=lambda q, opts: (
                terminal_choice(q, opts) if opts else terminal_input(q)
            )
        )
        # Build party
        soldiers = [
            Character(
                "Li Wei", "Young peasant soldier", {"health": 100, "loyalty": 80}
            ),
            Character("Zhang San", "Veteran marksman", {"health": 90, "loyalty": 85}),
            Character("Wang Wu", "Former blacksmith", {"health": 110, "loyalty": 70}),
        ]
        porters = [
            Character("Old Chen", "Aged porter", {"health": 70, "loyalty": 60}),
            Character("Xiao Liu", "Teenage messenger", {"health": 80, "loyalty": 90}),
        ]
        commissar = Character(
            "Commissar Zhou", "Political officer", {"health": 100, "loyalty": 95}
        )
        self.party = Party(self.commander, soldiers, porters, commissar)
        self.party.supplies["rice_kg"] = 50.0
        self.party.supplies["ammo"] = 30

        # Begin the march
        print(f"\n{self.party.commander.name} takes command. The bugle sounds.")
        self._game_loop()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def _game_loop(self) -> None:
        """Simple turn‑based loop: travel → check events → status → repeat."""
        while self.state != "gameover":
            self._print_status()

            # Check for events
            if self.party is None:
                return
            active_events = self.event_mgr.get_active_events(self.party, self.time_mgr)
            if active_events:
                self._handle_events(active_events)

            # Check victory
            if self.world_map.next_node() is None:
                self._victory()
                return

            # Player action menu
            print("\nActions:")
            print("  [1] March forward one day")
            print("  [2] Rest one day (recover morale)")
            print("  [3] Check detailed status")
            print("  [4] Quit")
            choice = terminal_choice(
                "What do you do, comrade?", ["March", "Rest", "Status", "Quit"]
            )
            if choice == 0:
                self._march_one_day()
            elif choice == 1:
                self._rest_one_day()
            elif choice == 2:
                continue  # status already shown
            elif choice == 3:
                print("The Long March awaits. 再见 comrade.")
                self.state = "gameover"

            # Game over conditions
            if self.party.total_people() == 0 or self.party.morale <= 0:
                print(
                    "\n💀 Your unit has perished. The journalist closes his notebook."
                )
                self.state = "gameover"

    def _march_one_day(self) -> None:
        """Advance time, move on map, consume supplies."""
        assert self.party is not None
        self.time_mgr.set_scale(Config.STRATEGIC_TIME_SCALE)
        self.time_mgr.update(3600)  # 1 hour real = 60 game hours ≈ 2.5 game days
        km_per_day = Config.BASE_SPEED_KMPH * 10
        reached = self.world_map.advance(km_per_day)
        shortages = self.party.consume_daily()
        if shortages.get("rice_kg", 0) > 0:
            print("⚠️  Your unit goes hungry today.")
        if reached:
            node = self.world_map.current_node()
            if node:
                print(f"\n🏁 You have reached **{node.name}** – {node.description}")

    def _rest_one_day(self) -> None:
        """Rest: morale boost, smaller resource consumption."""
        assert self.party is not None
        self.time_mgr.set_scale(1)  # 1:1 time
        self.time_mgr.update(86400)  # exactly one game day
        self.party.update_morale(5, "rest")
        self.party.consume_daily()
        print("You rest and rally the troops. Morale improves slightly.")

    def _print_status(self) -> None:
        """Print current party and location status."""
        assert self.party is not None
        node = self.world_map.current_node()
        node_name = node.name if node else "Unknown"
        progress = self.world_map.route_progress() * 100
        print(f"\n--- {self.time_mgr.date_str()} ---")
        print(f"Location: {node_name}  ({progress:.0f}% of journey)")
        print(
            f"People: {self.party.total_people()}  |  Morale: {self.party.morale}  |  "
            f"Cohesion: {self.party.political_cohesion}"
        )
        print(
            f"Supplies: rice={self.party.supplies['rice_kg']:.1f}kg, "
            f"ammo={self.party.supplies['ammo']}"
        )

    def _handle_events(self, events) -> None:
        """Resolve a list of active events with player choices."""
        assert self.party is not None
        for event in events:
            if event.id in self.event_mgr.completed:
                continue
            print(f"\n⚡ Event: {event.data.get('description', 'Something happens.')}")
            choices = event.data.get("choices", [])
            if not choices:
                continue
            idx = terminal_choice(
                event.data.get("description", "What do you do?"),
                [c.get("text", "Option") for c in choices],
            )
            result = self.event_mgr.resolve(event, idx, self.party, self.ai)
            print(f"📜 {result['narration']}")

    # ------------------------------------------------------------------
    # Event setup
    # ------------------------------------------------------------------
    def _setup_events(self) -> None:
        """Register sample events for the demo."""
        # Ambush near Xiang River (event condition can access self.world_map via closure)
        wm = self.world_map  # capture for lambda
        self.event_mgr.register(
            GameEvent(
                "ambush_1",
                lambda p, t: wm.current_node_id == "xiang_river",
                {
                    "description": "Nationalist troops ambush your column!",
                    "choices": [
                        {
                            "text": "Fight through!",
                            "effects": {"morale": -5, "ammo": -5, "health": -20},
                        },
                        {
                            "text": "Retreat and find another path.",
                            "effects": {"morale": -10, "rice_kg": -5},
                        },
                    ],
                },
            )
        )
        # Food cache (one‑time random event – we'll improve frequency later)
        self.event_mgr.register(
            GameEvent(
                "food_cache",
                lambda p, t: True,  # triggers once
                {
                    "description": "A peasant offers your unit a hidden cache of rice.",
                    "choices": [
                        {
                            "text": "Accept gratefully.",
                            "effects": {"rice_kg": 10, "morale": 5},
                        },
                        {
                            "text": "Pay for it with pamphlets.",
                            "effects": {"rice_kg": 10, "pamphlets": -2},
                        },
                    ],
                },
            )
        )

    # ------------------------------------------------------------------
    # Victory / game over
    # ------------------------------------------------------------------
    def _victory(self) -> None:
        """Handle reaching Yan'an."""
        assert self.party is not None
        print("\n🎉 Your unit staggers into Yan'an. The Long March is over.")
        print(f"Survivors: {self.party.total_people()}")
        self.state = "gameover"


# Entry point for `python -m src.main`
def main():
    cfg = Config()
    game = Game(cfg)
    game.new_game(ui_mode="terminal")


if __name__ == "__main__":
    main()
