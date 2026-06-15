#!/usr/bin/env python3
"""
Long March Project Scaffold Generator (no triple‑quoted strings)
Usage: python setup_project.py
"""

import os

SRC = "src"
PKGS = ["core", "combat", "narrative", "ui"]
DATA_DIRS = ["data", "saves", "assets", "tests"]
MODEL_DIR = "models"

# Each file is a list of lines; we'll join them with \n when writing.
FILES = {}

# ---------------------------------------------------------------------------
# core/config.py
# ---------------------------------------------------------------------------
FILES["src/core/config.py"] = [
    '"""Game configuration constants."""',
    "class Config:",
    '    DATA_PATH: str = "data/"',
    '    SAVE_PATH: str = "saves/"',
    '    ASSETS_PATH: str = "assets/"',
    "    SCREEN_WIDTH: int = 1280",
    "    SCREEN_HEIGHT: int = 720",
    "    FPS: int = 60",
    "",
    "    STRATEGIC_TIME_SCALE: int = 60",
    "    EVENT_TIME_SCALE: int = 1",
    "",
    "    BASE_SPEED_KMPH: float = 4.0",
    "    DAILY_RICE_KG_PER_PERSON: float = 0.6",
    "",
    '    LLM_MODEL_PATH: str = "models/llama-3-8b-q4.gguf"',
    "    USE_AI: bool = True",
    "    AI_MAX_TOKENS: int = 256",
    "",
    "    COMBAT_DICE_SIDES: int = 20",
    "",
]

# ---------------------------------------------------------------------------
# core/enums.py
# ---------------------------------------------------------------------------
FILES["src/core/enums.py"] = [
    '"""Enumerations for decisions, stances, terrain, origins."""',
    "from enum import Enum, auto",
    "",
    "class DecisionType(Enum):",
    "    COMMAND = auto()",
    "    SOVIET_VOTE = auto()",
    "    HIGHER_ORDER = auto()",
    "",
    "class UnitStance(Enum):",
    "    ASSAULT = auto()",
    "    DEFEND = auto()",
    "    FLANK_LEFT = auto()",
    "    FLANK_RIGHT = auto()",
    "    AMBUSH = auto()",
    "    RETREAT = auto()",
    "    LEAD_FROM_FRONT = auto()",
    "",
    "class TerrainType(Enum):",
    "    PLAINS = auto()",
    "    FOREST = auto()",
    "    HILLS = auto()",
    "    MOUNTAINS = auto()",
    "    RIVER = auto()",
    "    VILLAGE = auto()",
    "",
    "class Origin(Enum):",
    '    PEASANT = "peasant"',
    '    INTELLECTUAL = "intellectual"',
    '    WORKER = "worker"',
    '    FOREIGN_EDUCATED = "foreign_educated"',
    "",
    "class PrologueChoice(Enum):",
    '    WRITING_POETRY = "writing_poetry"',
    '    PHYSICAL_TRAINING = "physical_training"',
    '    STUDYING_MAPS = "studying_maps"',
    '    OPIUM = "opium"',
    "",
]

# ---------------------------------------------------------------------------
# core/utils.py
# ---------------------------------------------------------------------------
FILES["src/core/utils.py"] = [
    '"""Utility functions: clamp, weighted choice, JSON I/O."""',
    "from typing import Any, List",
    "import json",
    "",
    "def clamp(value: float, min_val: float, max_val: float) -> float:",
    "    raise NotImplementedError",
    "",
    "def weighted_choice(choices: List[Any], weights: List[float]) -> Any:",
    "    raise NotImplementedError",
    "",
    "def load_json(filepath: str) -> dict:",
    "    raise NotImplementedError",
    "",
    "def save_json(filepath: str, data: dict) -> None:",
    "    raise NotImplementedError",
    "",
]

# ---------------------------------------------------------------------------
# core/character.py
# ---------------------------------------------------------------------------
FILES["src/core/character.py"] = [
    '"""Base Character and Commander classes."""',
    "from typing import Dict, List",
    "from .enums import Origin",
    "",
    "class Character:",
    "    def __init__(self, name: str, bio: str, stats: Dict[str, int]):",
    "        self.name = name",
    "        self.bio = bio",
    "        self.stats = stats",
    "        self.status_effects: List[str] = []",
    "",
    "    def is_alive(self) -> bool:",
    '        return self.stats.get("health", 0) > 0',
    "",
    '    def apply_damage(self, amount: int, cause: str = "") -> None:',
    "        raise NotImplementedError",
    "",
    "    def add_effect(self, effect: str) -> None:",
    "        raise NotImplementedError",
    "",
    "class Commander(Character):",
    "    def __init__(self, name: str, origin: Origin, traits: Dict[str, int],",
    "                 inventory: Dict[str, int]):",
    '        super().__init__(name, "", traits)',
    "        self.origin = origin",
    "        self.traits = traits",
    "        self.inventory = inventory",
    "        self.reputation: Dict[str, int] = {}",
    "",
]

# ---------------------------------------------------------------------------
# core/party.py
# ---------------------------------------------------------------------------
FILES["src/core/party.py"] = [
    '"""Party (Red Army unit) class."""',
    "from typing import Dict, List",
    "from .character import Character, Commander",
    "",
    "class Party:",
    "    def __init__(self, commander: Commander, soldiers: List[Character],",
    "                 porters: List[Character], commissar: Character):",
    "        self.commander = commander",
    "        self.soldiers = soldiers",
    "        self.porters = porters",
    "        self.commissar = commissar",
    "        self.supplies = {",
    '            "rice_kg": 0.0,',
    '            "ammo": 0,',
    '            "medicine": 0,',
    '            "pamphlets": 0,',
    '            "batteries": 0',
    "        }",
    "        self.morale: int = 50",
    "        self.political_cohesion: int = 50",
    "        self.codex: List[str] = []",
    "",
    "    def total_people(self) -> int:",
    "        return len(self.soldiers) + len(self.porters) + 1",
    "",
    "    def consume_daily(self) -> Dict[str, float]:",
    "        raise NotImplementedError",
    "",
    '    def update_morale(self, delta: int, reason: str = "") -> None:',
    "        raise NotImplementedError",
    "",
    "    def remove_casualties(self, count: int, unit: str) -> List[Character]:",
    "        raise NotImplementedError",
    "",
]

# ---------------------------------------------------------------------------
# core/world_map.py
# ---------------------------------------------------------------------------
FILES["src/core/world_map.py"] = [
    '"""World map: nodes and the Long March route."""',
    "from typing import Dict, List, Optional, Tuple",
    "",
    "class MapNode:",
    "    def __init__(self, node_id: str, name: str, lat: float, lon: float,",
    "                 node_type: str, description: str):",
    "        self.id = node_id",
    "        self.name = name",
    "        self.lat = lat",
    "        self.lon = lon",
    "        self.type = node_type",
    "        self.description = description",
    "        self.connections: List[Tuple[str, float]] = []",
    "",
    "class WorldMap:",
    '    def __init__(self, route_file: str = "data/map.json"):',
    "        self.nodes: Dict[str, MapNode] = {}",
    '        self.current_node_id: str = ""',
    "        self.route: List[str] = []",
    "        self.distance_traveled: float = 0.0",
    "",
    "    def _load(self, filename: str) -> None:",
    "        raise NotImplementedError",
    "",
    "    def next_node(self) -> Optional[MapNode]:",
    "        raise NotImplementedError",
    "",
    "    def advance(self, km: float) -> bool:",
    "        raise NotImplementedError",
    "",
]

# ---------------------------------------------------------------------------
# core/time_manager.py
# ---------------------------------------------------------------------------
FILES["src/core/time_manager.py"] = [
    '"""Time manager with dynamic scaling."""',
    "from .config import Config",
    "",
    "class TimeManager:",
    '    def __init__(self, start_iso: str = "1934-10-16T06:00:00"):',
    "        self.current_iso: str = start_iso",
    "        self.time_scale: int = Config.STRATEGIC_TIME_SCALE",
    "",
    "    def update(self, real_dt: float) -> float:",
    "        raise NotImplementedError",
    "",
    "    def set_scale(self, scale: int) -> None:",
    "        raise NotImplementedError",
    "",
    "    def date_str(self) -> str:",
    "        raise NotImplementedError",
    "",
]

# ---------------------------------------------------------------------------
# combat/combat.py
# ---------------------------------------------------------------------------
FILES["src/combat/combat.py"] = [
    '"""Combat simulation: squads, battlefield, resolver."""',
    "from typing import Any, Dict, List",
    "from ..core.enums import TerrainType, UnitStance",
    "",
    "class Squad:",
    "    def __init__(self, name: str, size: int, stats: Dict[str, int]):",
    "        self.name = name",
    "        self.size = size",
    "        self.stats = stats",
    "        self.stance: UnitStance = UnitStance.DEFEND",
    "        self.casualties: int = 0",
    "",
    "class Battlefield:",
    "    def __init__(self, width: int, height: int, default_terrain: TerrainType):",
    "        self.grid: List[List[TerrainType]] = [",
    "            [default_terrain for _ in range(width)] for _ in range(height)",
    "        ]",
    "        self.red_squads: List[Squad] = []",
    "        self.enemy_squads: List[Squad] = []",
    "",
    "    def set_terrain(self, x: int, y: int, terrain: TerrainType) -> None:",
    "        raise NotImplementedError",
    "",
    "class CombatSimulator:",
    "    def __init__(self, battlefield: Battlefield):",
    "        self.bf = battlefield",
    "",
    "    def resolve(self) -> Dict[str, Any]:",
    "        raise NotImplementedError",
    "",
]

# ---------------------------------------------------------------------------
# narrative/event_system.py
# ---------------------------------------------------------------------------
FILES["src/narrative/event_system.py"] = [
    '"""Event system: base, random, major events, and manager."""',
    "from typing import Any, Callable, Dict, List, Optional",
    "from ..core.party import Party",
    "from ..core.time_manager import TimeManager",
    "",
    "class GameEvent:",
    "    def __init__(self, event_id: str,",
    "                 conditions: Callable[[Party, TimeManager], bool],",
    "                 data: dict):",
    "        self.id = event_id",
    "        self.conditions = conditions",
    "        self.data = data",
    "",
    "    def is_triggered(self, party: Party, time: TimeManager) -> bool:",
    "        return self.conditions(party, time)",
    "",
    "class RandomEvent(GameEvent):",
    "    def __init__(self, *args, frequency: float = 0.05):",
    "        super().__init__(*args)",
    "        self.frequency = frequency",
    "",
    "class MajorStoryEvent(GameEvent):",
    "    def __init__(self, *args, trigger_node: Optional[str] = None,",
    "                 trigger_date: Optional[str] = None):",
    "        super().__init__(*args)",
    "        self.trigger_node = trigger_node",
    "        self.trigger_date = trigger_date",
    "",
    "class EventManager:",
    "    def __init__(self):",
    "        self.events: List[GameEvent] = []",
    "        self.completed: set = set()",
    "",
    "    def register(self, event: GameEvent) -> None:",
    "        self.events.append(event)",
    "",
    "    def get_active_events(self, party: Party, time: TimeManager) -> List[GameEvent]:",
    "        raise NotImplementedError",
    "",
    "    def resolve(self, event: GameEvent, player_choice: int,",
    "                party: Party, ai) -> Dict[str, Any]:",
    "        raise NotImplementedError",
    "",
]

# ---------------------------------------------------------------------------
# narrative/prologue.py
# ---------------------------------------------------------------------------
FILES["src/narrative/prologue.py"] = [
    '"""Interactive prologue: the interview that shapes your commander."""',
    "from typing import Dict, List, Tuple",
    "from ..core.character import Commander",
    "",
    "class Prologue:",
    "    def __init__(self, ai_service):",
    "        self.ai = ai_service",
    "",
    "    def run(self) -> Commander:",
    "        raise NotImplementedError",
    "",
    "    def _ask(self, question: str, options: List[Tuple[str, Dict[str, int]]]) -> int:",
    "        raise NotImplementedError",
    "",
]

# ---------------------------------------------------------------------------
# narrative/journalist.py
# ---------------------------------------------------------------------------
FILES["src/narrative/journalist.py"] = [
    '"""Journalist narrator (Edgar Snow stand-in)."""',
    "from typing import Any, Dict, List",
    "from ..core.party import Party",
    "",
    "class Journalist:",
    "    def __init__(self, ai_service):",
    "        self.ai = ai_service",
    "        self.notes: List[str] = []",
    "",
    "    def interject(self, context: Dict[str, Any], party: Party) -> str:",
    "        raise NotImplementedError",
    "",
    "    def final_account(self) -> str:",
    "        raise NotImplementedError",
    "",
]

# ---------------------------------------------------------------------------
# narrative/ai_service.py
# ---------------------------------------------------------------------------
FILES["src/narrative/ai_service.py"] = [
    '"""AI service: local LLM with fallback."""',
    "from typing import Any, Dict",
    "from ..core.config import Config",
    "from ..core.character import Character",
    "",
    "class AIService:",
    "    def __init__(self, config: Config):",
    "        self.config = config",
    "        self.model_loaded = False",
    "",
    "    def _load_model(self, path: str) -> None:",
    "        raise NotImplementedError",
    "",
    "    def generate(self, system_prompt: str, user_prompt: str,",
    "                 max_tokens: int = 256) -> str:",
    "        raise NotImplementedError",
    "",
    "    def generate_dialogue(self, npc: Character, context: str) -> str:",
    "        raise NotImplementedError",
    "",
    "    def generate_narration(self, event_result: Dict[str, Any]) -> str:",
    "        raise NotImplementedError",
    "",
    "    def generate_combat_report(self, log: Dict[str, Any]) -> str:",
    "        raise NotImplementedError",
    "",
]

# ---------------------------------------------------------------------------
# ui/base.py
# ---------------------------------------------------------------------------
FILES["src/ui/base.py"] = [
    '"""Abstract UI interface."""',
    "from typing import Any, Dict, List",
    "from ..core.party import Party",
    "from ..core.world_map import WorldMap",
    "from ..combat.combat import Battlefield",
    "",
    "class BaseUI:",
    "    def display(self, screen: str, data: Dict[str, Any]) -> Any:",
    "        raise NotImplementedError",
    "    def show_decision(self, prompt: str, choices: List[str]) -> int:",
    "        raise NotImplementedError",
    "    def update_status(self, party: Party) -> None:",
    "        raise NotImplementedError",
    "    def render_map(self, world_map: WorldMap, party: Party) -> None:",
    "        raise NotImplementedError",
    "    def battle_setup(self, battlefield: Battlefield) -> Dict[str, Any]:",
    "        raise NotImplementedError",
    "",
]

# ---------------------------------------------------------------------------
# ui/terminal.py
# ---------------------------------------------------------------------------
FILES["src/ui/terminal.py"] = [
    '"""Terminal UI placeholder."""',
    "from .base import BaseUI",
    "",
    "class TerminalUI(BaseUI):",
    "    pass",
    "",
]

# ---------------------------------------------------------------------------
# ui/graphical.py
# ---------------------------------------------------------------------------
FILES["src/ui/graphical.py"] = [
    '"""Pygame-based graphical UI."""',
    "from .base import BaseUI",
    "from ..core.config import Config",
    "",
    "class GraphicalUI(BaseUI):",
    "    def __init__(self):",
    "        try:",
    "            import pygame",
    "            self.pygame = pygame",
    "        except ImportError:",
    "            raise RuntimeError(",
    '                "Pygame is required for graphical UI. Install with: pip install pygame"',
    "            )",
    "        self.screen = self.pygame.display.set_mode(",
    "            (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)",
    "        )",
    "        self.clock = self.pygame.time.Clock()",
    "        self.running = True",
    "",
    "    def main_loop(self, game: 'Game') -> None:",
    "        raise NotImplementedError",
    "",
]

# ---------------------------------------------------------------------------
# main.py
# ---------------------------------------------------------------------------
FILES["src/main.py"] = [
    '"""Game entry point."""',
    "from typing import Optional",
    "from .core.config import Config",
    "from .core.time_manager import TimeManager",
    "from .core.world_map import WorldMap",
    "from .core.party import Party",
    "from .core.character import Commander",
    "from .narrative.event_system import EventManager, GameEvent",
    "from .narrative.journalist import Journalist",
    "from .narrative.ai_service import AIService",
    "from .ui.base import BaseUI",
    "",
    "class Game:",
    "    def __init__(self, config: Config):",
    "        self.config = config",
    "        self.ai: AIService = AIService(config)",
    "        self.commander: Optional[Commander] = None",
    "        self.party: Optional[Party] = None",
    "        self.world_map: WorldMap = WorldMap()",
    "        self.time_mgr: TimeManager = TimeManager()",
    "        self.event_mgr: EventManager = EventManager()",
    "        self.journalist: Journalist = Journalist(self.ai)",
    "        self.ui: Optional[BaseUI] = None",
    '        self.state: str = "menu"',
    "",
    '    def new_game(self, ui_mode: str = "graphical") -> None:',
    "        raise NotImplementedError",
    "",
    "    def update(self, real_dt: float) -> None:",
    "        raise NotImplementedError",
    "",
    "    def handle_event(self, event: GameEvent) -> None:",
    "        raise NotImplementedError",
    "",
    "    def handle_battle(self, battle_data: dict) -> None:",
    "        raise NotImplementedError",
    "",
    "    def save_game(self, slot: int) -> None:",
    "        raise NotImplementedError",
    "",
    "    def load_game(self, slot: int) -> None:",
    "        raise NotImplementedError",
    "",
    "",
    "def main():",
    "    import logging",
    "    logging.basicConfig(level=logging.INFO)",
    "    cfg = Config()",
    "    game = Game(cfg)",
    '    game.new_game(ui_mode="graphical")',
    "",
    "",
    'if __name__ == "__main__":',
    "    main()",
    "",
]

# ---------------------------------------------------------------------------
# README.md
# ---------------------------------------------------------------------------
FILES["README.md"] = [
    "# 长征：红星照耀中国 · Long March: Red Star Over China",
    "",
    "*Historical survival narrative, collectivist decisions, harrowing battles.*",
    "",
    "## Quick Start (after scaffold generation)",
    "```bash",
    "python -m venv venv",
    "venv\\\\Scripts\\\\activate      # Windows",
    "# source venv/bin/activate   # macOS/Linux",
    "pip install -r requirements.txt",
    "```",
    "",
    "## Project Structure",
    "```",
    "long-march/",
    "├── src/              # main source",
    "│   ├── core/         # engine, party, config",
    "│   ├── combat/       # battle simulation",
    "│   ├── narrative/    # events, prologue, AI",
    "│   ├── ui/           # terminal/graphical UI",
    "│   └── main.py       # entry point",
    "├── data/             # map.json, events.json",
    "├── saves/            # game saves",
    "├── assets/           # images, fonts",
    "├── tests/            # unit tests",
    "├── models/           # optional local LLM",
    "├── setup.py",
    "├── requirements.txt",
    "└── README.md",
    "```",
    "",
    "## Development",
    "- All stub methods raise `NotImplementedError` until implemented.",
    "- The scaffold is solid; now implement one module at a time.",
    "",
    "*The Long March begins with a single step—and a solid scaffold.*",
    "",
]

# ---------------------------------------------------------------------------
# setup.py
# ---------------------------------------------------------------------------
FILES["setup.py"] = [
    '"""Setup script for Long March game."""',
    "from setuptools import setup, find_packages",
    "",
    "setup(",
    '    name="long_march",',
    '    version="0.0.1",',
    '    packages=find_packages(where="src"),',
    '    package_dir={"": "src"},',
    "    entry_points={",
    '        "console_scripts": [',
    '            "long-march = long_march.main:main",',
    "        ],",
    "    },",
    '    author="Your Name",',
    '    description="Long March: Red Star Over China — historical survival narrative",',
    '    license="MIT",',
    ")",
    "",
]

# ---------------------------------------------------------------------------
# requirements.txt
# ---------------------------------------------------------------------------
FILES["requirements.txt"] = [
    "# Core game dependencies (uncomment as needed)",
    "# pygame>=2.5",
    "# llama-cpp-python>=0.2",
    "# textual>=0.30",
    "# numpy>=1.24",
    "# pytest>=7.0",
    "",
]

# ---------------------------------------------------------------------------
# tests/conftest.py
# ---------------------------------------------------------------------------
FILES["tests/conftest.py"] = [
    '"""Test configuration."""',
    "import sys",
    "import os",
    "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))",
    "",
]


def create_directories():
    for d in DATA_DIRS + [MODEL_DIR]:
        os.makedirs(d, exist_ok=True)
        if d != "tests":
            with open(os.path.join(d, ".gitkeep"), "w") as f:
                pass

    for pkg in PKGS:
        pkg_dir = os.path.join(SRC, pkg)
        os.makedirs(pkg_dir, exist_ok=True)
        init_path = os.path.join(pkg_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                pass

    tests_init = os.path.join("tests", "__init__.py")
    if not os.path.exists(tests_init):
        with open(tests_init, "w") as f:
            pass


def write_files():
    for path, lines in FILES.items():
        parent = os.path.dirname(path)
        if parent:  # skip mkdir for files at root level
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"Created {path}")


if __name__ == "__main__":
    print("Setting up Long March project scaffold...\n")
    create_directories()
    write_files()
    print("\n✅ Project scaffold complete!")
    print("Next steps:")
    print("  1. python -m venv venv")
    print("  2. Activate venv")
    print("  3. python -m src.main")
