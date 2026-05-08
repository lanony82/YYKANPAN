"""Tests for src/time_utils.py — BeijingTime UTC+8 helpers."""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from time_utils import BeijingTime


BJ_TZ = timezone(timedelta(hours=8))
FIXED_BJ = datetime(2026, 5, 8, 14, 30, 45, tzinfo=BJ_TZ)


@pytest.fixture(autouse=True)
def _freeze_time():
    with patch.object(BeijingTime, "now", return_value=FIXED_BJ):
        yield


def test_now_returns_utc8():
    dt = BeijingTime.now()
    assert dt.utcoffset() == timedelta(hours=8)


def test_date_str_format():
    assert BeijingTime.date_str() == "2026-05-08"


def test_datetime_str_format():
    assert BeijingTime.datetime_str() == "2026-05-08 14:30:45"


def test_yyyymmdd_format():
    assert BeijingTime.yyyymmdd() == "20260508"


def test_today_returns_date():
    d = BeijingTime.today()
    assert d.year == 2026
    assert d.month == 5
    assert d.day == 8
