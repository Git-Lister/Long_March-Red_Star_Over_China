"""Tests for src.core.character."""

import pytest

from src.core.character import Character, Commander
from src.core.enums import Origin


class TestCharacter:
    def setup_method(self):
        self.char = Character("Test", "A test", {"health": 50, "loyalty": 80})

    def test_is_alive_true(self):
        assert self.char.is_alive() is True

    def test_is_alive_false(self):
        self.char.stats["health"] = 0
        assert self.char.is_alive() is False

    def test_apply_damage_normal(self):
        self.char.apply_damage(20)
        assert self.char.stats["health"] == 30

    def test_apply_damage_not_below_zero(self):
        self.char.apply_damage(100)
        assert self.char.stats["health"] == 0

    def test_apply_damage_negative_raises(self):
        with pytest.raises(ValueError):
            self.char.apply_damage(-10)

    def test_add_effect(self):
        self.char.add_effect("wounded")
        assert "wounded" in self.char.status_effects

    def test_add_duplicate_effect(self):
        self.char.add_effect("wounded")
        self.char.add_effect("wounded")
        assert self.char.status_effects.count("wounded") == 1

    def test_remove_effect(self):
        self.char.add_effect("exhausted")
        self.char.remove_effect("exhausted")
        assert "exhausted" not in self.char.status_effects


class TestCommander:
    def test_creation(self):
        traits = {"leadership": 70, "political_credibility": 60}
        inventory = {"pen": 1}
        cmd = Commander("Mao", Origin.PEASANT, traits, inventory)
        assert cmd.name == "Mao"
        assert cmd.origin == Origin.PEASANT
        assert cmd.stats["health"] == 100
        assert cmd.stats["leadership"] == 70
        assert cmd.inventory["pen"] == 1
