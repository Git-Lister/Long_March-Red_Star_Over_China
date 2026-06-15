"""Graphical UI – interactive map with event dialogs (freeze‑fixed)."""

import math
import traceback
from typing import Any, Dict, List, Optional

import pygame

from ..combat.combat import Battlefield
from ..core.config import Config
from ..core.party import Party
from ..core.world_map import WorldMap
from .base import BaseUI

RED = (204, 0, 0)
BLACK = (0, 0, 0)
PAPER = (245, 240, 225)
BROWN = (139, 90, 43)
GOLD = (212, 175, 55)
BUTTON_COLOR = (180, 0, 0)
BUTTON_HOVER = (220, 50, 50)


class Button:
    def __init__(self, rect, text, callback, ui):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.ui = ui
        self.hovered = False

    def draw(self, surface):
        colour = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, colour, self.rect, border_radius=4)
        pygame.draw.rect(surface, GOLD, self.rect, 2, border_radius=4)
        txt = self.ui.font_small.render(self.text, True, PAPER)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                try:
                    self.callback()
                except Exception as e:
                    traceback.print_exc()
                    self.ui.error_msg = f"Button error: {e}"


class GraphicalUI(BaseUI):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Long March: Red Star Over China")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_small = pygame.font.Font(None, 18)
        self.font_medium = pygame.font.Font(None, 24)
        self.map_rect = pygame.Rect(
            Config.SCREEN_WIDTH // 3,
            0,
            2 * Config.SCREEN_WIDTH // 3,
            Config.SCREEN_HEIGHT,
        )
        self.buttons: List[Button] = []
        self.game = None
        self.error_msg = ""
        self.status_msg = ""

        # Dialog state
        self.dialog_active = False
        self.pending_events = []
        self.dialog_buttons: List[Button] = []
        self.dialog_title = ""
        self.dialog_text = ""

    # ---- BaseUI stubs ----
    def display(self, screen, data):
        pass

    def show_decision(self, prompt, choices):
        return 0

    def prompt_string(self, q, d=""):
        return "Graphical"

    def update_status(self, p):
        pass

    def render_map(self, wm, p):
        pass

    def battle_setup(self, bf):
        self.status_msg = "Battle! (auto‑deploy)"
        for squad in bf.red_squads:
            squad.stance = 0
        return {}

    # ---- Main loop ----
    def main_loop(self, game: "Game") -> None:
        self.game = game
        self._build_buttons()
        print("Graphical UI active. Use the buttons to play.")
        while self.running and game.state != "gameover":
            self.clock.tick(Config.FPS)
            self._handle_events()
            self._draw()
        pygame.quit()

    def _build_buttons(self):
        self.buttons.clear()
        x, y, w, h = 10, 10, Config.SCREEN_WIDTH // 3 - 20, 35
        actions = [
            ("March (32 km)", self._do_march),
            ("Force March (60 km)", self._do_force_march),
            ("Rest (1 day)", self._do_rest),
            ("Forage (1 day)", self._do_forage),
        ]
        for label, callback in actions:
            self.buttons.append(Button(pygame.Rect(x, y, w, h), label, callback, self))
            y += h + 5

    def _handle_events(self):
        self.status_msg = ""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game.state = "gameover"
            # Always allow dialog buttons if dialog is active; otherwise action buttons
            if self.dialog_active:
                for btn in self.dialog_buttons:
                    btn.handle_event(event)
            else:
                for btn in self.buttons:
                    btn.handle_event(event)

    def _draw(self):
        self.screen.fill(PAPER)
        self._draw_map(self.game.world_map, self.game.party)
        self._draw_status(self.game.party, self.game.time_mgr.date_str())
        if not self.dialog_active:
            for btn in self.buttons:
                btn.draw(self.screen)
        if self.error_msg:
            txt = self.font_small.render(self.error_msg, True, RED)
            self.screen.blit(txt, (10, Config.SCREEN_HEIGHT - 30))
        if self.status_msg:
            txt = self.font_small.render(self.status_msg, True, BLACK)
            self.screen.blit(
                txt, (Config.SCREEN_WIDTH // 3 + 10, Config.SCREEN_HEIGHT - 30)
            )
        if self.dialog_active:
            self._draw_dialog()
        pygame.display.flip()

    # ---- Dialog system ----
    def _show_event_dialog(self, event):
        """Display a modal dialog for a non‑combat event."""
        self.dialog_active = True
        self.dialog_title = event.data.get("description", "Event")
        self.dialog_text = "Choose your response:"
        choices = event.data.get("choices", [])
        self.dialog_buttons.clear()
        dialog_center = (Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2)
        btn_w, btn_h = 400, 40
        start_y = dialog_center[1] - (len(choices) * (btn_h + 5)) // 2 + 20
        for i, choice in enumerate(choices):
            rect = pygame.Rect(
                dialog_center[0] - btn_w // 2, start_y + i * (btn_h + 5), btn_w, btn_h
            )
            # Capture event and index safely
            btn = Button(
                rect,
                choice.get("text", f"Choice {i + 1}"),
                lambda ev=event, idx=i: self._resolve_event(ev, idx),
                self,
            )
            self.dialog_buttons.append(btn)

    def _resolve_event(self, event, choice_idx):
        """Apply the chosen effect and close the dialog."""
        try:
            choices = event.data.get("choices", [])
            if 0 <= choice_idx < len(choices):
                effects = choices[choice_idx].get("effects", {})
                for stat, delta in effects.items():
                    if stat == "morale":
                        self.game.party.update_morale(delta)
                    elif stat == "political_cohesion":
                        self.game.party.update_political_cohesion(delta)
                    elif stat in self.game.party.supplies:
                        if stat == "rice_kg":
                            self.game.party.supplies[stat] = max(
                                0.0, self.game.party.supplies[stat] + delta
                            )
                        else:
                            self.game.party.supplies[stat] = max(
                                0, int(self.game.party.supplies[stat] + delta)
                            )
                self.status_msg = f"{choices[choice_idx].get('text', '')[:50]}..."
            self.game.event_mgr.completed.add(event.id)
        except Exception as e:
            traceback.print_exc()
            self.error_msg = f"Resolve error: {e}"
        finally:
            self.dialog_active = False
            self.dialog_buttons.clear()

    def _draw_dialog(self):
        overlay = pygame.Surface(
            (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        box_w, box_h = 500, 300
        box_x = Config.SCREEN_WIDTH // 2 - box_w // 2
        box_y = Config.SCREEN_HEIGHT // 2 - box_h // 2
        dialog_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(self.screen, PAPER, dialog_rect, border_radius=8)
        pygame.draw.rect(self.screen, GOLD, dialog_rect, 3, border_radius=8)
        title_surf = self.font_medium.render(self.dialog_title, True, BLACK)
        self.screen.blit(title_surf, (box_x + 20, box_y + 15))
        desc_surf = self.font_small.render(self.dialog_text, True, BLACK)
        self.screen.blit(desc_surf, (box_x + 20, box_y + 50))
        for btn in self.dialog_buttons:
            btn.draw(self.screen)

    # ---- Action callbacks ----
    def _do_march(self):
        self.game._march_normal()
        self._after_action()

    def _do_force_march(self):
        self.game._force_march()
        self._after_action()

    def _do_rest(self):
        self.game._rest()
        self._after_action()

    def _do_forage(self):
        self.game._forage()
        self._after_action()

    def _after_action(self):
        """Check events, auto‑resolve combat (no AI), show non‑combat dialogs."""
        try:
            self.game._check_random_events()
            active = self.game.event_mgr.get_active_events(
                self.game.party, self.game.time_mgr
            )
            for event in active:
                if event.id in self.game.event_mgr.completed:
                    continue
                if event.data.get("combat"):
                    # Quick combat – no AI call
                    log = self.game._resolve_combat_event(event)
                    self.status_msg = f"Battle! Red lost {log['red_casualties']}, enemy lost {log['enemy_casualties']}"
                    self.game.event_mgr.completed.add(event.id)
                else:
                    self.pending_events.append(event)

            if self.pending_events:
                event = self.pending_events.pop(0)
                self._show_event_dialog(event)

            if self.game.world_map.next_node() is None:
                self.game._victory()
            if self.game.party.total_people() == 0 or self.game.party.morale <= 0:
                self.game._game_over()
        except Exception as e:
            traceback.print_exc()
            self.error_msg = f"Event error: {e}"

    # ---- Map / status drawing (unchanged) ----
    def _draw_map(self, world_map: WorldMap, party: Optional[Party]) -> None:
        pygame.draw.rect(self.screen, BLACK, self.map_rect, 2)
        route = world_map.route
        nodes = world_map.nodes
        if not route or not nodes:
            return
        pos = {}
        for nid in route:
            node = nodes.get(nid)
            if not node:
                continue
            x = self.map_rect.x + 20 + (node.lon - 102) * 18
            y = self.map_rect.y + 20 + (37 - node.lat) * 30
            pos[nid] = (x, y)
        for i in range(len(route) - 1):
            a = pos.get(route[i])
            b = pos.get(route[i + 1])
            if a and b:
                pygame.draw.line(self.screen, BROWN, a, b, 3)
        for nid, (x, y) in pos.items():
            node = nodes[nid]
            colour = RED if nid == world_map.current_node_id else BLACK
            pygame.draw.circle(self.screen, colour, (int(x), int(y)), 8)
            lbl = self.font_small.render(node.name, True, BLACK)
            self.screen.blit(lbl, (x + 12, y - 6))
        if world_map.current_node_id in pos:
            cx, cy = pos[world_map.current_node_id]
            self._draw_star(self.screen, GOLD, (int(cx), int(cy)), 10)

    def _draw_status(self, party: Optional[Party], date_str: str) -> None:
        panel_rect = pygame.Rect(
            0, 200, Config.SCREEN_WIDTH // 3, Config.SCREEN_HEIGHT - 200
        )
        pygame.draw.rect(self.screen, BLACK, panel_rect, 0)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 2)
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
            y = panel_rect.y + 10
            for line in lines:
                txt = self.font_small.render(line, True, PAPER)
                self.screen.blit(txt, (10, y))
                y += 22

    def _draw_star(self, surface, colour, center, size):
        cx, cy = center
        points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            r = size if i % 2 == 0 else size / 2
            points.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
        pygame.draw.polygon(surface, colour, points)
