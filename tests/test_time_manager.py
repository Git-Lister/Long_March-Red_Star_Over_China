"""Tests for src.core.time_manager."""

import pytest

from src.core.config import Config
from src.core.time_manager import TimeManager


class TestTimeManager:
    def setup_method(self):
        self.tm = TimeManager("1934-10-16T06:00:00")

    def test_update_strategic(self):
        self.tm.set_scale(60)
        gs = self.tm.update(1.0)
        assert gs == 60.0

    def test_update_event_scale(self):
        self.tm.set_scale(1)
        gs = self.tm.update(10.0)
        assert gs == 10.0

    def test_date_str(self):
        assert self.tm.date_str() == "1934-10-16"
        self.tm.set_scale(1)  # 1:1 time for predictable advance
        self.tm.update(86400)  # 86400 game seconds = 1 game day
        assert self.tm.date_str() == "1934-10-17"

    def test_set_scale_invalid(self):
        with pytest.raises(ValueError):
            self.tm.set_scale(0)
        with pytest.raises(ValueError):
            self.tm.set_scale(-5)

    def test_datetime_obj(self):
        dt = self.tm.datetime_obj()
        assert dt.year == 1934
        assert dt.month == 10
        assert dt.day == 16
