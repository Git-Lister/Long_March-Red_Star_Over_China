"""Tests for the prologue interview."""

import pytest

from src.core.config import Config
from src.core.enums import Origin, PrologueChoice
from src.narrative.ai_service import AIService
from src.narrative.prologue import Prologue


class TestPrologue:
    @pytest.fixture
    def ai(self):
        return AIService(Config())

    @pytest.fixture
    def prologue(self, ai):
        return Prologue(ai)

    def test_run_creates_commander_peasant_poet(self, prologue):
        """Feed a deterministic set of answers and verify the resulting Commander."""
        answers = iter(
            [
                0,  # last night: writing poetry
                0,  # origin: peasant
                "Test Commander",
            ]
        )

        def callback(q, opts):
            if not opts:  # name prompt
                return next(answers)
            return next(answers)

        cmd = prologue.run(prompt_callback=callback)
        assert cmd.name == "Test Commander"
        assert cmd.origin == Origin.PEASANT
        assert cmd.traits["survival"] >= 70  # peasant bonus + maybe maps
        assert cmd.traits["political_credibility"] >= 60  # poetry bonus
        assert "pen" in cmd.inventory
        assert "sickle" in cmd.inventory

    def test_run_worker_training(self, prologue):
        answers = iter(
            [
                1,  # physical training
                2,  # worker
                "Iron Will",
            ]
        )

        def callback(q, opts):
            return next(answers)

        cmd = prologue.run(prompt_callback=callback)
        assert cmd.origin == Origin.WORKER
        assert cmd.traits["health"] >= 120  # base 100 + worker 10 + training 10
        assert "hammer" in cmd.inventory
        assert "opium_pipe" not in cmd.inventory
