from __future__ import annotations

from datetime import datetime, timedelta, timezone, date


class BeijingTime:
    """Shared UTC+8 time utilities used across app, collector, and summary."""

    TZ = timezone(timedelta(hours=8))

    @classmethod
    def now(cls) -> datetime:
        return datetime.now(cls.TZ)

    @classmethod
    def date_str(cls) -> str:
        return cls.now().strftime("%Y-%m-%d")

    @classmethod
    def datetime_str(cls) -> str:
        return cls.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def yyyymmdd(cls) -> str:
        return cls.now().strftime("%Y%m%d")

    @classmethod
    def today(cls) -> date:
        return cls.now().date()
