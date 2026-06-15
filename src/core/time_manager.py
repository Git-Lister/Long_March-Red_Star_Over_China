"""Time manager: game clock and time scale switching."""

from datetime import datetime, timedelta

from .config import Config


class TimeManager:
    """Maintains game time and handles time‑scale switching."""

    def __init__(self, start_iso: str = "1934-10-16T06:00:00"):
        self.current_iso: str = start_iso
        self.time_scale: int = Config.STRATEGIC_TIME_SCALE
        self._datetime = datetime.fromisoformat(start_iso)

    def update(self, real_dt: float) -> float:
        """
        Advance game time by real_dt real‑seconds, scaled by time_scale.
        Returns the number of game‑seconds that passed.
        """
        game_seconds = real_dt * self.time_scale
        self._datetime += timedelta(seconds=game_seconds)
        self.current_iso = self._datetime.isoformat()
        return game_seconds

    def set_scale(self, scale: int) -> None:
        """Switch time scale (e.g., between strategic and event mode)."""
        if scale <= 0:
            raise ValueError("Time scale must be positive")
        self.time_scale = scale

    def date_str(self) -> str:
        """Return human‑readable date, e.g., '1934-10-17'."""
        return self._datetime.strftime("%Y-%m-%d")

    def datetime_obj(self) -> datetime:
        """Return the current datetime object for comparisons."""
        return self._datetime
