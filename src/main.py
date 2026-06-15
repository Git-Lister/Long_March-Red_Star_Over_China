"""Game entry point — historical‑realism prototype (terminal + graphical)."""

import logging
import random
import sys
from typing import Any, Dict, Optional

from .combat.combat import Battlefield, CombatSimulator, Squad
from .core.character import Character, Commander
from .core.config import Config
from .core.enums import TerrainType
from .core.party import Party
from .core.time_manager import TimeManager
from .core.world_map import WorldMap
from .narrative.ai_service import AIService
from .narrative.event_system import EventManager, GameEvent, RandomEvent
from .narrative.journalist import Journalist
from .narrative.prologue import Prologue
from .ui.graphical import GraphicalUI
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
        self.ui: TerminalUI | GraphicalUI = TerminalUI()  # default
        self.state = "menu"
        self.no_ai = False  # set to True in graphical mode to skip AI calls
        self.event_cooldowns: dict[str, int] = {}
        self._setup_events()

    # ------------------------------------------------------------------
    # Prologue + new game
    # ------------------------------------------------------------------
    def new_game(self, ui_mode: str = "terminal") -> None:
        """Run prologue, initialise party, start main loop."""
        print("\n" + "=" * 60)
        print("  LONG MARCH: RED STAR OVER CHINA")
        print("=" * 60)

        # Prologue always uses current UI (terminal or graphical)
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
        self.party.supplies["rice_kg"] = 80.0
        self.party.supplies["ammo"] = 40

        print(f"\n{self.party.commander.name} takes command. The bugle sounds.")

    # ------------------------------------------------------------------
    # Graphical launcher
    # ------------------------------------------------------------------
    def run_graphical(self) -> None:
        """Switch to graphical UI without re‑running prologue."""
        self.ui = GraphicalUI()
        self.no_ai = True  # disable blocking AI calls
        print("\nLaunching graphical map...")
        self.ui.main_loop(self)

    # ------------------------------------------------------------------
    # Main terminal loop
    # ------------------------------------------------------------------
    def _game_loop(self) -> None:
        while self.state != "gameover":
            assert self.party is not None
            self._print_status()

            self._check_random_events()

            active_events = self.event_mgr.get_active_events(self.party, self.time_mgr)
            if active_events:
                self._handle_events(active_events)

            if self.world_map.next_node() is None:
                self._victory()
                return

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

            if self.party.total_people() == 0 or self.party.morale <= 0:
                self._game_over()
                return

    # ------------------------------------------------------------------
    # Action methods (unchanged)
    # ------------------------------------------------------------------
    def _march_normal(self) -> None:
        assert self.party is not None
        self.time_mgr.set_scale(1)
        self.time_mgr.update(8 * 3600)
        km = self.config.BASE_SPEED_KMPH * 8
        self._travel(km)
        self._consume_and_report()

    def _force_march(self) -> None:
        assert self.party is not None
        self.time_mgr.set_scale(1)
        self.time_mgr.update(12 * 3600)
        km = 5.0 * 12
        self._travel(km)
        for person in self.party.soldiers + self.party.porters + [self.party.commander]:
            if person.is_alive():
                person.apply_damage(5, "forced march")
        self.party.update_morale(-3, "exhaustion")
        self._consume_and_report()
        print(
            "⚠️  The forced march exhausts your unit. Soldiers stumble but cover ground."
        )

    def _rest(self) -> None:
        assert self.party is not None
        self.time_mgr.set_scale(1)
        self.time_mgr.update(24 * 3600)
        people = self.party.total_people()
        rice_consumed = people * self.config.DAILY_RICE_KG_PER_PERSON * 0.5
        self.party.supplies["rice_kg"] = max(
            0.0, self.party.supplies["rice_kg"] - rice_consumed
        )
        self.party.update_morale(5, "rest")
        print("You rest and rally the troops. Morale improves slightly.")

    def _forage(self) -> None:
        assert self.party is not None
        self.time_mgr.set_scale(1)
        self.time_mgr.update(24 * 3600)
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
        reached = self.world_map.advance(km)
        if reached:
            node = self.world_map.current_node()
            if node:
                print(f"\n🏁 You have reached **{node.name}** – {node.description}")

    def _consume_and_report(self) -> None:
        assert self.party is not None
        shortages = self.party.consume_daily()
        if shortages.get("rice_kg", 0) > 0:
            print("⚠️  Your unit goes hungry today.")

    # ------------------------------------------------------------------
    # Status display
    # ------------------------------------------------------------------
    def _print_status(self) -> None:
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
    # Events (unchanged)
    # ------------------------------------------------------------------
    def _check_random_events(self) -> None:
        assert self.party is not None
        for event in self.event_mgr.events:
            if event.id in self.event_mgr.completed:
                continue
            if not isinstance(event, RandomEvent):
                continue
            last = self.event_cooldowns.get(event.id, -999)
            if last > 0:
                self.event_cooldowns[event.id] = last - 1
                continue
            if random.random() < event.frequency:
                print(
                    f"\n⚡ Random event: {event.data.get('description', 'Something happens.')}"
                )
                self._handle_events([event])
                self.event_cooldowns[event.id] = 3

    def _handle_events(self, events) -> None:
        assert self.party is not None
        for event in events:
            if event.id in self.event_mgr.completed:
                continue
            if event.data.get("combat"):
                self._resolve_combat_event(event)
                self.event_mgr.completed.add(event.id)
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
    # Combat resolution (unchanged)
    # ------------------------------------------------------------------
    def _resolve_combat_event(self, event: GameEvent) -> Dict[str, Any]:
        assert self.party is not None
        red_squads = [
            Squad(
                "Red Commander",
                1,
                {
                    "attack": self.party.commander.traits.get("leadership", 10),
                    "defense": 10,
                },
            ),
        ]
        for soldier in self.party.soldiers:
            red_squads.append(Squad(soldier.name, 1, {"attack": 10, "defense": 10}))

        enemy_data = event.data.get("enemy_squads", [])
        enemy_squads = [
            Squad(
                d["name"], d["size"], {"attack": d["attack"], "defense": d["defense"]}
            )
            for d in enemy_data
        ]

        terrain = TerrainType.PLAINS
        if event.data.get("terrain") == "river":
            terrain = TerrainType.RIVER
        elif event.data.get("terrain") == "forest":
            terrain = TerrainType.FOREST
        elif event.data.get("terrain") == "mountain":
            terrain = TerrainType.MOUNTAINS

        bf = Battlefield(3, 3, terrain)
        bf.red_squads = red_squads
        bf.enemy_squads = enemy_squads

        self.ui.battle_setup(bf)
        sim = CombatSimulator(bf)
        log = sim.resolve()

        total_red_cas = sum(s.casualties for s in bf.red_squads)
        self.party.remove_casualties(total_red_cas, "soldiers")

        if log["victory"]:
            self.party.update_morale(10, "battle victory")
        else:
            self.party.update_morale(-15, "battle defeat")

        self.party.supplies["ammo"] = max(0, self.party.supplies["ammo"] - 5)
        report = self.ai.generate_combat_report(log)
        print(f"\n⚔️  BATTLE REPORT: {report}")
        print(f"   Red casualties: {log['red_casualties']}")
        print(f"   Enemy casualties: {log['enemy_casualties']}")
        print(f"   {'Victory!' if log['victory'] else 'Defeat...'}")
        return log

    # ------------------------------------------------------------------
    # Event definitions (unchanged)
    # ------------------------------------------------------------------
    def _setup_events(self) -> None:
        wm = self.world_map

        self.event_mgr.register(
            GameEvent(
                "ambush_xiang",
                lambda p, t: wm.current_node_id == "xiang_river",
                {
                    "description": "Nationalist troops ambush your column at the Xiang River crossing!",
                    "combat": True,
                    "terrain": "river",
                    "enemy_squads": [
                        {
                            "name": "Nationalist Regulars",
                            "size": 8,
                            "attack": 12,
                            "defense": 12,
                        },
                        {"name": "Local Militia", "size": 5, "attack": 8, "defense": 6},
                    ],
                },
            )
        )

        self.event_mgr.register(
            GameEvent(
                "zunyi_conference",
                lambda p, t: wm.current_node_id == "zunyi",
                {
                    "description": "The Zunyi Conference convenes. The Party debates strategy.",
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

        self.event_mgr.register(
            GameEvent(
                "jiajin_mountains",
                lambda p, t: wm.current_node_id == "jiajin_mountains",
                {
                    "description": "The Jiajin Mountains rise ahead, covered in snow.",
                    "choices": [
                        {
                            "text": "Press on immediately.",
                            "effects": {"morale": -10, "health": -20},
                        },
                        {
                            "text": "Wait a day and collect cold‑weather gear.",
                            "effects": {"rice_kg": -5, "health": -5, "morale": 5},
                        },
                    ],
                },
            )
        )

        self.event_mgr.register(
            GameEvent(
                "maogong_meeting",
                lambda p, t: wm.current_node_id == "maogong",
                {
                    "description": "At Maogong, you rendezvous with the Fourth Red Army.",
                    "choices": [
                        {
                            "text": "Merge forces and share supplies.",
                            "effects": {"rice_kg": 20, "morale": 15, "pamphlets": -5},
                        },
                        {
                            "text": "Stay independent, request only ammunition.",
                            "effects": {"ammo": 10, "political_cohesion": 5},
                        },
                    ],
                },
            )
        )

        self.event_mgr.register(
            GameEvent(
                "luding_bridge",
                lambda p, t: wm.current_node_id == "luding_bridge",
                {
                    "description": "The Luding Bridge – a chain bridge over a raging river.",
                    "combat": True,
                    "terrain": "mountain",
                    "enemy_squads": [
                        {
                            "name": "Nationalist Bridge Guard",
                            "size": 6,
                            "attack": 14,
                            "defense": 10,
                        },
                        {
                            "name": "Machine‑gun nest",
                            "size": 4,
                            "attack": 16,
                            "defense": 8,
                        },
                    ],
                },
            )
        )

        # Random events
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

        self.event_mgr.register(
            RandomEvent(
                "storm",
                lambda p, t: True,
                {
                    "description": "A violent rainstorm turns the path to mud.",
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

        self.event_mgr.register(
            RandomEvent(
                "local_guide",
                lambda p, t: True,
                {
                    "description": "A local offers to guide you through a hidden pass.",
                    "choices": [
                        {
                            "text": "Follow the guide.",
                            "effects": {"morale": 3, "rice_kg": -2},
                        },
                        {
                            "text": "Go alone, you know the way.",
                            "effects": {"morale": -2},
                        },
                    ],
                },
                frequency=0.12,
            )
        )

    # ------------------------------------------------------------------
    # Endings – handle both terminal (AI) and graphical (no AI)
    # ------------------------------------------------------------------
    def _victory(self) -> None:
        assert self.party is not None
        if self.no_ai:
            # Graphical mode: simple message
            print("\n🎉 Your unit staggers into Yan'an. The Long March is over.")
            print(f"Survivors: {self.party.total_people()}")
            self.state = "gameover"
            return

        # Terminal mode: full AI journalist account
        print("\n🎉 Your unit staggers into Yan'an. The Long March is over.")
        print(f"Survivors: {self.party.total_people()}")
        print(
            f"Morale: {self.party.morale}  |  Political cohesion: {self.party.political_cohesion}"
        )

        prompt = (
            f"The Long March has ended. Survivors: {self.party.total_people()}. "
            f"Morale: {self.party.morale}. Political cohesion: {self.party.political_cohesion}. "
            "Write a single paragraph in the voice of a Western journalist, summarising the journey "
            "and its significance, in the style of Edgar Snow's Red Star Over China."
        )
        account = self.ai.generate(
            system_prompt=self.ai._system_prompt("narration"),
            user_prompt=prompt,
            max_tokens=256,
        )
        print(f"\n📰 JOURNALIST'S ACCOUNT:\n{account}")
        self.state = "gameover"

    def _game_over(self) -> None:
        assert self.party is not None
        if self.no_ai:
            # Graphical mode: simple message
            print("\n💀 Your unit has perished.")
            print("The journalist closes his notebook.")
            self.state = "gameover"
            return

        # Terminal mode: full AI journalist note
        print("\n💀 Your unit has perished. The journalist closes his notebook.")
        prompt = (
            "The Red Army unit has been destroyed. Write a short, mournful paragraph "
            "from the journalist's perspective, reflecting on the sacrifice."
        )
        account = self.ai.generate(
            system_prompt=self.ai._system_prompt("narration"),
            user_prompt=prompt,
            max_tokens=192,
        )
        print(f"\n📰 JOURNALIST'S NOTE:\n{account}")
        self.state = "gameover"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    cfg = Config()
    game = Game(cfg)
    if "--graphical" in sys.argv:
        game.new_game(ui_mode="terminal")  # prologue in terminal
        game.run_graphical()  # then graphical UI
    else:
        game.new_game(ui_mode="terminal")
        game._game_loop()


if __name__ == "__main__":
    main()
