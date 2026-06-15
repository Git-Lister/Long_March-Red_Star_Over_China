"""Tests for event system."""

import pytest

from src.core.character import Character, Commander
from src.core.config import Config
from src.core.enums import Origin
from src.core.party import Party
from src.core.time_manager import TimeManager
from src.narrative.ai_service import AIService
from src.narrative.event_system import (
    EventManager,
    GameEvent,
    MajorStoryEvent,
    RandomEvent,
)


@pytest.fixture
def sample_party():
    cmd = Commander("Test", Origin.WORKER, {}, {})
    soldiers = [Character("S1", "", {"health": 100})]
    porters = []
    commissar = Character("Com", "", {"health": 100})
    p = Party(cmd, soldiers, porters, commissar)
    p.supplies["rice_kg"] = 100
    return p


@pytest.fixture
def time_mgr():
    return TimeManager("1934-10-16T06:00:00")


@pytest.fixture
def ai():
    return AIService(Config())


@pytest.fixture
def event_mgr():
    return EventManager()


def always_true(party, time):
    return True


def low_morale(party, time):
    return party.morale < 30


class TestEventTriggering:
    def test_active_event_triggered(self, sample_party, time_mgr, event_mgr):
        ev = GameEvent("test1", always_true, {"choices": []})
        event_mgr.register(ev)
        active = event_mgr.get_active_events(sample_party, time_mgr)
        assert len(active) == 1
        assert active[0].id == "test1"

    def test_completed_event_not_triggered(self, sample_party, time_mgr, event_mgr):
        ev = GameEvent("test2", always_true, {"choices": []})
        event_mgr.register(ev)
        event_mgr.completed.add("test2")
        active = event_mgr.get_active_events(sample_party, time_mgr)
        assert len(active) == 0

    def test_conditional_not_met(self, sample_party, time_mgr, event_mgr):
        ev = GameEvent("test3", low_morale, {"choices": []})
        event_mgr.register(ev)
        active = event_mgr.get_active_events(sample_party, time_mgr)
        assert len(active) == 0

    def test_major_story_event_node(self, sample_party, time_mgr, event_mgr):
        ev = MajorStoryEvent("major1", always_true, {}, trigger_node="zunyi")
        event_mgr.register(ev)
        assert ev.trigger_node == "zunyi"


class TestResolution:
    def test_resolve_applies_morale(self, sample_party, time_mgr, ai, event_mgr):
        data = {"choices": [{"text": "Boost morale", "effects": {"morale": 10}}]}
        ev = GameEvent("ev1", always_true, data)
        event_mgr.register(ev)
        res = event_mgr.resolve(ev, 0, sample_party, ai)
        assert sample_party.morale == 60
        assert res["event_id"] == "ev1"
        assert "narration" in res

    def test_resolve_applies_supply(self, sample_party, time_mgr, ai, event_mgr):
        data = {"choices": [{"text": "Find rice", "effects": {"rice_kg": 20}}]}
        ev = GameEvent("ev2", always_true, data)
        res = event_mgr.resolve(ev, 0, sample_party, ai)
        assert sample_party.supplies["rice_kg"] == 120
