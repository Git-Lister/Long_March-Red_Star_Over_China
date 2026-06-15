"""Game entry point — historical‑realism terminal prototype."""

import logging
import random
from typing import Optional

from .core.character import Character, Commander
from .core.config import Config
from .core.party import Party
from .core.time_manager import TimeManager
from .core.world_map import WorldMap
from .narrative.ai_service import AIService
from .narrative.event_system import EventManager, GameEvent, RandomEvent
from .narrative.journalist import Journalist
from .narrative.prologue import Prologue
from .ui.terminal import TerminalUI

logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------------------------
# Game class
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
        self.ui = TerminalUI()
        self.state = "menu"
        self.event_cooldowns: dict[
            str, int
        ] = {}  # event_id -> days until allowed again
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
                self.ui.show_decision(q, opts) if opts else self.ui.prompt_string(q)
            )
        )
        # Build party
        soldiers = [
            Character(
                "Li Wei", "Young peasant soldier", {"health": 100, "loyalty": 80}
            ),
            Character("Zhang San", "Veteran marksman", {"health": 90, "loyalty": 85}),
            Character("Wang Wu", "Former blacksmith", {"health": 110, "loyalty": 70}),
            Character(
                "Zhao Liu", "Farm boy, sharp eyes", {"health": 100, "loyalty": 75}
            ),
            Character(
                "Sun Qi", "Ex‑bandit, fierce fighter", {"health": 95, "loyalty": 60}
            ),
        ]
        porters = [
            Character("Old Chen", "Aged porter", {"health": 70, "loyalty": 60}),
            Character("Xiao Liu", "Teenage messenger", {"health": 80, "loyalty": 90}),
        ]
        commissar = Character(
            "Commissar Zhou", "Political officer", {"health": 100, "loyalty": 95}
        )
        self.party = Party(self.commander, soldiers, porters, commissar)
        self.party.supplies["rice_kg"] = (
            80.0  # historical: ~15 days of food for 8 people
        )
        self.party.supplies["ammo"] = 40

        print(f"\n{self.party.commander.name} takes command. The bugle sounds.")
        self._game_loop()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def _game_loop(self) -> None:
        while self.state != "gameover":
            assert self.party is not None
            self._print_status()

            # Check random events
            self._check_random_events()

            # Check for node‑triggered major events
            active_events = self.event_mgr.get_active_events(self.party, self.time_mgr)
            if active_events:
                self._handle_events(active_events)

            # Victory condition
            if self.world_map.next_node() is None:
                self._victory()
                return

            # Player action
            actions = [
                "March (32 km, 1 day)",
                "Force march (60 km, 1 day, fatigue)",
                "Rest (1 day, half rations)",
                "Forage (1 day, no movement)",
                "View map",
                "Quit",
            ]
            choice = self.ui.show_decision("What do you do, comrade?", actions)

            if choice == 0:
                self._march_normal()
            elif choice == 1:
                self._force_march()
            elif choice == 2:
                self._rest()
            elif choice == 3:
                self._forage()
            elif choice == 4:
                self.ui.render_map(self.world_map, self.party)
            elif choice == 5:
                print("The Long March awaits. 再见 comrade.")
                self.state = "gameover"

            # End‑of‑day check: starvation, morale collapse, all dead
            if self.party.total_people() == 0 or self.party.morale <= 0:
                print(
                    "\n💀 Your unit has perished. The journalist closes his notebook."
                )
                self.state = "gameover"

    # ------------------------------------------------------------------
    # Action methods
    # ------------------------------------------------------------------
    def _march_normal(self) -> None:
        """Standard march: 8 hours, 32 km, consumes full rations."""
        assert self.party is not None
        self.time_mgr.set_scale(1)
        self.time_mgr.update(8 * 3600)  # 8 hours
        km = self.config.BASE_SPEED_KMPH * 8  # 32 km
        self._travel(km)
        self._consume_and_report()

    def _force_march(self) -> None:
        """Forced march: 12 hours, 60 km, health & morale penalties."""
        assert self.party is not None
        self.time_mgr.set_scale(1)
        self.time_mgr.update(12 * 3600)
        km = 5.0 * 12  # 60 km at 5 km/h (strenuous)
        self._travel(km)
        # Fatigue damage: each person loses 5 health
        for person in self.party.soldiers + self.party.porters + [self.party.commander]:
            if person.is_alive():
                person.apply_damage(5, "forced march")
        self.party.update_morale(-3, "exhaustion")
        self._consume_and_report()
        print(
            "⚠️  The forced march exhausts your unit. Soldiers stumble but cover ground."
        )

    def _rest(self) -> None:
        """Rest one full day, consume half rations, gain morale."""
        assert self.party is not None
        self.time_mgr.set_scale(1)
        self.time_mgr.update(24 * 3600)
        # Half rations
        people = self.party.total_people()
        rice_consumed = people * self.config.DAILY_RICE_KG_PER_PERSON * 0.5
        self.party.supplies["rice_kg"] = max(
            0.0, self.party.supplies["rice_kg"] - rice_consumed
        )
        self.party.update_morale(5, "rest")
        print("You rest and rally the troops. Morale improves slightly.")

    def _forage(self) -> None:
        """Spend a day foraging – chance of food, ammo, or nothing."""
        assert self.party is not None
        self.time_mgr.set_scale(1)
        self.time_mgr.update(24 * 3600)
        # Still consume half rations (people eat while searching)
        people = self.party.total_people()
        rice_consumed = people * self.config.DAILY_RICE_KG_PER_PERSON * 0.5
        self.party.supplies["rice_kg"] = max(
            0.0, self.party.supplies["rice_kg"] - rice_consumed
        )

        roll = random.random()
        if roll < 0.3:
            found = random.uniform(5, 20)
            self.party.supplies["rice_kg"] += found
            print(f"🌾 Foragers discover a hidden cache! +{found:.1f} kg rice.")
        elif roll < 0.5:
            found = random.randint(1, 5)
            self.party.supplies["ammo"] += found
            print(f"💥 Foragers scavenge leftover ammunition. +{found} ammo.")
        elif roll < 0.7:
            print("🐀 Foragers catch a few rats and wild greens. Barely a supplement.")
            self.party.update_morale(2, "small find")
        else:
            print("🍂 The land is barren. Nothing found today.")
            self.party.update_morale(-2, "failed forage")

    def _travel(self, km: float) -> None:
        """Advance party on map by given kilometres."""
        reached = self.world_map.advance(km)
        if reached:
            node = self.world_map.current_node()
            if node:
                print(f"\n🏁 You have reached **{node.name}** – {node.description}")

    def _consume_and_report(self) -> None:
        """Consume daily supplies and print warnings."""
        assert self.party is not None
        shortages = self.party.consume_daily()
        if shortages.get("rice_kg", 0) > 0:
            print("⚠️  Your unit goes hungry today.")

    # ------------------------------------------------------------------
    # Status display
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------
    def _check_random_events(self) -> None:
        """Roll for random events each day based on frequency and cooldown."""
        assert self.party is not None
        now = self.time_mgr._datetime
        for event in self.event_mgr.events:
            if event.id in self.event_mgr.completed:
                continue
            if not isinstance(event, RandomEvent):
                continue
            # Check cooldown
            last = self.event_cooldowns.get(event.id, -999)
            if last > 0:
                # Reduce cooldown by 1 each day
                self.event_cooldowns[event.id] = last - 1
                continue
            if random.random() < event.frequency:
                # Trigger event
                print(
                    f"\n⚡ Random event: {event.data.get('description', 'Something happens.')}"
                )
                self._handle_events([event])
                # Set cooldown (3 days before this event can fire again)
                self.event_cooldowns[event.id] = 3

    def _handle_events(self, events) -> None:
        """Resolve a list of active events with player choices."""
        assert self.party is not None
        for event in events:
            if event.id in self.event_mgr.completed:
                continue
            choices = event.data.get("choices", [])
            if not choices:
                continue
            idx = self.ui.show_decision(
                event.data.get("description", "What do you do?"),
                [c.get("text", "Option") for c in choices],
            )
            result = self.event_mgr.resolve(event, idx, self.party, self.ai)
            print(f"📜 {result['narration']}")

    # ------------------------------------------------------------------
    # Event definitions
    # ------------------------------------------------------------------
    def _setup_events(self) -> None:
        """Register historical and random events."""
        wm = self.world_map

        # Major: Xiang River ambush
        self.event_mgr.register(
            GameEvent(
                "ambush_xiang",
                lambda p, t: wm.current_node_id == "xiang_river",
                {
                    "description": "Nationalist troops ambush your column at the Xiang River crossing!",
                    "choices": [
                        {
                            "text": "Fight through! (costly)",
                            "effects": {"morale": -10, "ammo": -10, "health": -30},
                        },
                        {
                            "text": "Retreat and find another ford.",
                            "effects": {"morale": -5, "rice_kg": -5, "pamphlets": -2},
                        },
                    ],
                },
            )
        )

        # Major: Zunyi Conference (Soviet vote simulation)
        self.event_mgr.register(
            GameEvent(
                "zunyi_conference",
                lambda p, t: wm.current_node_id == "zunyi",
                {
                    "description": "The Zunyi Conference convenes. The Party debates strategy. Your voice matters.",
                    "choices": [
                        {
                            "text": "Support Mao's bold northern thrust.",
                            "effects": {"political_cohesion": 15, "morale": 10},
                        },
                        {
                            "text": "Argue for a cautious, fortified retreat.",
                            "effects": {
                                "political_cohesion": -5,
                                "morale": -5,
                                "rice_kg": 20,
                            },
                        },
                    ],
                },
            )
        )

        # Random: peasant gift
        self.event_mgr.register(
            RandomEvent(
                "peasant_gift",
                lambda p, t: True,
                {
                    "description": "A local peasant offers your unit a small sack of rice.",
                    "choices": [
                        {
                            "text": "Accept gratefully.",
                            "effects": {"rice_kg": 8, "morale": 3},
                        },
                        {
                            "text": "Pay with political pamphlets.",
                            "effects": {
                                "rice_kg": 8,
                                "pamphlets": -2,
                                "political_cohesion": 3,
                            },
                        },
                    ],
                },
                frequency=0.15,
            )
        )

        # Random: storm
        self.event_mgr.register(
            RandomEvent(
                "storm",
                lambda p, t: True,
                {
                    "description": "A violent rainstorm turns the path to mud. Progress slows.",
                    "choices": [
                        {
                            "text": "Push through.",
                            "effects": {"morale": -3, "health": -5},
                        },
                        {
                            "text": "Halt and build shelters.",
                            "effects": {"rice_kg": -2, "morale": 1},
                        },
                    ],
                },
                frequency=0.1,
            )
        )

        # Random: deserter
        self.event_mgr.register(
            RandomEvent(
                "deserter",
                lambda p, t: len(p.soldiers) > 1,
                {
                    "description": "One of your soldiers attempts to desert in the night.",
                    "choices": [
                        {"text": "Let them go.", "effects": {"morale": -5}},
                        {
                            "text": "Execute them as an example.",
                            "effects": {"morale": -10, "political_cohesion": 5},
                        },
                    ],
                },
                frequency=0.08,
            )
        )

    # ------------------------------------------------------------------
    # Victory
    # ------------------------------------------------------------------
    def _victory(self) -> None:
        """Handle reaching Yan'an."""
        assert self.party is not None
        print("\n🎉 Your unit staggers into Yan'an. The Long March is over.")
        print(f"Survivors: {self.party.total_people()}")
        print(
            f"Morale: {self.party.morale}  |  Political cohesion: {self.party.political_cohesion}"
        )
        self.state = "gameover"


# Entry point
def main():
    cfg = Config()
    game = Game(cfg)
    game.new_game(ui_mode="terminal")


if __name__ == "__main__":
    main()
