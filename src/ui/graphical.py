"""Pygame-based graphical UI with Soviet propaganda aesthetic."""

import math
import sys
from typing import Any, Dict, List, Optional, Tuple

import pygame

from ..combat.combat import Battlefield
from ..core.config import Config
from ..core.party import Party
from ..core.world_map import WorldMap
from .base import BaseUI

# Colour palette – Soviet poster
RED = (204, 0, 0)
BLACK = (0, 0, 0)
PAPER = (245, 240, 225)
BROWN = (139, 90, 43)
GOLD = (212, 175, 55)


class GraphicalUI(BaseUI):
    """Pygame-based UI."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Long March: Red Star Over China")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_small = pygame.font.SysFont("timesnewroman", 16)
        self.font_medium = pygame.font.SysFont("timesnewroman", 24, bold=True)
        self.font_large = pygame.font.SysFont("timesnewroman", 36, bold=True)

        # Map viewport (right 2/3 of screen)
        self.map_rect = pygame.Rect(
            Config.SCREEN_WIDTH // 3,
            0,
            2 * Config.SCREEN_WIDTH // 3,
            Config.SCREEN_HEIGHT,
        )

    # ------------------------------------------------------------------
    # BaseUI interface methods
    # ------------------------------------------------------------------
    def display(self, screen: str, data: Dict[str, Any]) -> Any:
        """Show a generic screen (unused in graphical mode for now)."""
        pass

    def show_decision(self, prompt: str, choices: List[str]) -> int:
        """Blocking decision via Pygame event loop. Returns chosen index."""
        # For simplicity in early prototype, fall back to terminal input.
        print(f"\n[GRAPHICAL DECISION] {prompt}")
        for i, c in enumerate(choices):
            print(f"  [{i + 1}] {c}")
        while True:
            try:
                return int(input("Your choice: ")) - 1
            except ValueError:
                pass

    def prompt_string(self, question: str, default: str = "") -> str:
        """Blocking string input."""
        print(f"\n[GRAPHICAL INPUT] {question}")
        return input("  ") or default

    def update_status(self, party: Party) -> None:
        """Not used – status is drawn in main loop."""
        pass

    def render_map(self, world_map: WorldMap, party: Party) -> None:
        """Not used – map is drawn in main loop."""
        pass

    def battle_setup(self, battlefield: Battlefield) -> Dict[str, Any]:
        """Stub – will be graphical in Increment 2."""
        print("[GRAPHICAL] Battle setup not yet implemented – using terminal fallback.")
        from .terminal import TerminalUI

        tui = TerminalUI()
        return tui.battle_setup(battlefield)

    # ------------------------------------------------------------------
    # Main loop for the graphical game
    # ------------------------------------------------------------------
    def main_loop(self, game: "Game") -> None:
        """Run the game until quit."""
        while self.running:
            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    game.state = "gameover"
                    return

            # Clear screen
            self.screen.fill(PAPER)

            # Draw map
            self._draw_map(game.world_map, game.party)

            # Draw status panel (left 1/3)
            self._draw_status(game.party, game.time_mgr.date_str())

            pygame.display.flip()
            self.clock.tick(Config.FPS)

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------
    def _draw_map(self, world_map: WorldMap, party: Optional[Party]) -> None:
        """Draw a simplified node‑and‑path map."""
        pygame.draw.rect(self.screen, BLACK, self.map_rect, 2)

        # Collect node positions (simple linear projection)
        nodes = world_map.nodes
        route = world_map.route
        if not route:
            return

        # Compute positions
        pos = {}
        for i, nid in enumerate(route):
            node = nodes.get(nid)
            if not node:
                continue
            # Map lat/lon to screen (very rough)
            # Longitude range ~102‑116, Latitude ~25‑37
            x = self.map_rect.x + 20 + (node.lon - 102) * 18
            y = self.map_rect.y + 20 + (37 - node.lat) * 30
            pos[nid] = (x, y)

        # Draw connections
        for i in range(len(route) - 1):
            a = pos.get(route[i])
            b = pos.get(route[i + 1])
            if a and b:
                pygame.draw.line(self.screen, BROWN, a, b, 3)

        # Draw nodes
        for nid, (x, y) in pos.items():
            node = nodes[nid]
            colour = RED if nid == world_map.current_node_id else BLACK
            pygame.draw.circle(self.screen, colour, (int(x), int(y)), 8)
            # Label
            label = self.font_small.render(node.name, True, BLACK)
            self.screen.blit(label, (x + 12, y - 6))

        # Draw party marker (gold star) at current position
        if world_map.current_node_id in pos:
            cx, cy = pos[world_map.current_node_id]
            self._draw_star(self.screen, GOLD, (int(cx), int(cy)), 10)

    def _draw_status(self, party: Optional[Party], date_str: str) -> None:
        """Draw the status panel on the left."""
        panel_rect = pygame.Rect(0, 0, Config.SCREEN_WIDTH // 3, Config.SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 0)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3)

        y = 20
        if party:
            lines = [
                f"Date: {date_str}",
                f"Commander: {party.commander.name}",
                f"People: {party.total_people()}",
                f"Morale: {party.morale}",
                f"Cohesion: {party.political_cohesion}",
                f"Rice: {party.supplies.get('rice_kg', 0):.1f} kg",
                f"Ammo: {party.supplies.get('ammo', 0)}",
            ]
            for line in lines:
                text = self.font_small.render(line, True, PAPER)
                self.screen.blit(text, (10, y))
                y += 24

    def _draw_star(self, surface, colour, center, size):
        """Draw a five‑pointed star."""
        cx, cy = center
        points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            r = size if i % 2 == 0 else size / 2
            x = cx + r * math.cos(angle)
            y = cy - r * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(surface, colour, points)
