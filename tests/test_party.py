"""Tests for src.core.party."""

import pytest

from src.core.character import Character, Commander
from src.core.enums import Origin
from src.core.party import Party


@pytest.fixture
def sample_commander():
    return Commander(
        "Test Commander",
        Origin.WORKER,
        {"leadership": 60, "political_credibility": 70},
        {},
    )


@pytest.fixture
def sample_soldiers():
    return [
        Character(f"Soldier {i}", "", {"health": 100, "loyalty": 80}) for i in range(3)
    ]


@pytest.fixture
def sample_porters():
    return [
        Character(f"Porter {i}", "", {"health": 80, "loyalty": 50}) for i in range(2)
    ]


@pytest.fixture
def sample_commissar():
    return Character(
        "Commissar Li", "Political officer", {"health": 100, "loyalty": 95}
    )


@pytest.fixture
def sample_party(sample_commander, sample_soldiers, sample_porters, sample_commissar):
    return Party(sample_commander, sample_soldiers, sample_porters, sample_commissar)


class TestParty:
    def test_total_people(self, sample_party):
        assert sample_party.total_people() == 3 + 2 + 1

    def test_consume_daily_reduces_rice(self, sample_party):
        sample_party.supplies["rice_kg"] = 10.0
        shortages = sample_party.consume_daily()
        assert sample_party.supplies["rice_kg"] == pytest.approx(6.4, 0.01)
        assert shortages["rice_kg"] == 0.0

    def test_consume_daily_starvation(self, sample_party):
        sample_party.supplies["rice_kg"] = 1.0
        shortages = sample_party.consume_daily()
        assert sample_party.supplies["rice_kg"] == 0.0
        assert shortages["rice_kg"] > 0
        assert sample_party.morale < 50

    def test_update_morale(self, sample_party):
        sample_party.update_morale(20)
        assert sample_party.morale == 70
        sample_party.update_morale(-100)
        assert sample_party.morale == 0

    def test_update_political_cohesion(self, sample_party):
        sample_party.update_political_cohesion(30)
        assert sample_party.political_cohesion == 80

    def test_remove_casualties(self, sample_party):
        initial_count = len(sample_party.soldiers)
        removed = sample_party.remove_casualties(2, "soldiers")
        assert len(removed) == 2
        assert len(sample_party.soldiers) == initial_count - 2
        assert sample_party.morale < 50

    def test_remove_more_casualties_than_exist(self, sample_party):
        removed = sample_party.remove_casualties(10, "porters")
        assert len(removed) == 2
        assert len(sample_party.porters) == 0
