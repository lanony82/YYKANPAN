"""Tests for 新股新债 (IPO & convertible bond subscription) feature."""

import json
import io
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest

import server as stock_app


# ── Fixtures ──────────────────────────────────────────────────────────────────

BJT = timezone(timedelta(hours=8))
FIXED_NOW = datetime(2026, 5, 12, 10, 0, tzinfo=BJT)


def _make_ipo_response(rows):
    """Build a fake East Money IPO API response."""
    return {"success": True, "result": {"data": rows}}


def _make_bond_response(rows):
    """Build a fake East Money bond API response."""
    return {"success": True, "result": {"data": rows}}


SAMPLE_IPO_ROWS = [
    {"SECURITY_CODE": "688001", "SECURITY_NAME": "测试科技",
     "APPLY_DATE": "2026-05-13 00:00:00", "ISSUE_PRICE": 28.50,
     "ONLINE_ISSUE_LWR": 0.0003, "INITIAL_MULTIPLE": 5000.0},
    {"SECURITY_CODE": "301002", "SECURITY_NAME": "未来电子",
     "APPLY_DATE": "2026-05-12 00:00:00", "ISSUE_PRICE": 15.20,
     "ONLINE_ISSUE_LWR": None, "INITIAL_MULTIPLE": None},
    # Old — should be filtered out (>3 days ago)
    {"SECURITY_CODE": "600099", "SECURITY_NAME": "过期股份",
     "APPLY_DATE": "2026-05-01 00:00:00", "ISSUE_PRICE": 10.0,
     "ONLINE_ISSUE_LWR": 0.001, "INITIAL_MULTIPLE": 100.0},
]

SAMPLE_BOND_ROWS = [
    {"SECURITY_CODE": "123456", "SECURITY_NAME_ABBR": "测试转债",
     "CORRECODE_NAME_ABBR": "测试发债",
     "PUBLIC_START_DATE": "2026-05-11 00:00:00",
     "LISTING_DATE": "2026-05-20 00:00:00",
     "ONLINE_GENERAL_LWR": 0.0012},
    # Old — should be filtered out
    {"SECURITY_CODE": "113001", "SECURITY_NAME_ABBR": "旧转债",
     "CORRECODE_NAME_ABBR": "旧发债",
     "PUBLIC_START_DATE": "2026-04-01 00:00:00",
     "LISTING_DATE": "2026-04-15 00:00:00",
     "ONLINE_GENERAL_LWR": 0.0005},
]


@pytest.fixture(autouse=True)
def _reset_cache():
    """Reset xgxz cache before each test."""
    stock_app._XGXZ_CACHE = None
    stock_app._XGXZ_CACHE_DATE = ""
    yield
    stock_app._XGXZ_CACHE = None
    stock_app._XGXZ_CACHE_DATE = ""


def _mock_urlopen(ipo_resp=None, bond_resp=None, ipo_error=None, bond_error=None):
    """Return a side_effect function that returns different responses per URL."""
    def side_effect(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "RPTA_APP_IPOAPPLY" in url:
            if ipo_error:
                raise ipo_error
            body = json.dumps(ipo_resp or {"success": False}).encode()
        else:
            if bond_error:
                raise bond_error
            body = json.dumps(bond_resp or {"success": False}).encode()
        cm = MagicMock()
        cm.__enter__ = lambda s: io.BytesIO(body)
        cm.__exit__ = MagicMock(return_value=False)
        return cm
    return side_effect


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestFetchXinguXinzhai:
    """Tests for _fetch_xingu_xinzhai()."""

    @patch.object(stock_app, "_bj_now", return_value=FIXED_NOW)
    @patch("server.urlrequest.urlopen")
    def test_basic_parse(self, mock_urlopen, mock_now):
        mock_urlopen.side_effect = _mock_urlopen(
            ipo_resp=_make_ipo_response(SAMPLE_IPO_ROWS),
            bond_resp=_make_bond_response(SAMPLE_BOND_ROWS),
        )
        result = stock_app._fetch_xingu_xinzhai()

        assert result["ok"] is True
        assert result["date"] == "2026-05-12"
        # Old items filtered out
        assert len(result["ipo"]) == 2
        assert len(result["bond"]) == 1

    @patch.object(stock_app, "_bj_now", return_value=FIXED_NOW)
    @patch("server.urlrequest.urlopen")
    def test_ipo_fields(self, mock_urlopen, mock_now):
        mock_urlopen.side_effect = _mock_urlopen(
            ipo_resp=_make_ipo_response(SAMPLE_IPO_ROWS[:1]),
            bond_resp=_make_bond_response([]),
        )
        result = stock_app._fetch_xingu_xinzhai()
        ipo = result["ipo"][0]

        assert ipo["code"] == "688001"
        assert ipo["name"] == "测试科技"
        assert ipo["apply_date"] == "2026-05-13"  # truncated
        assert ipo["price"] == 28.50
        assert ipo["win_rate"] == 0.0003
        assert ipo["multiple"] == 5000.0

    @patch.object(stock_app, "_bj_now", return_value=FIXED_NOW)
    @patch("server.urlrequest.urlopen")
    def test_bond_fields(self, mock_urlopen, mock_now):
        mock_urlopen.side_effect = _mock_urlopen(
            ipo_resp=_make_ipo_response([]),
            bond_resp=_make_bond_response(SAMPLE_BOND_ROWS[:1]),
        )
        result = stock_app._fetch_xingu_xinzhai()
        bond = result["bond"][0]

        assert bond["code"] == "123456"
        assert bond["name"] == "测试转债"
        assert bond["apply_name"] == "测试发债"
        assert bond["apply_date"] == "2026-05-11"
        assert bond["list_date"] == "2026-05-20"
        assert bond["win_rate"] == 0.0012

    @patch.object(stock_app, "_bj_now", return_value=FIXED_NOW)
    @patch("server.urlrequest.urlopen")
    def test_date_filter_cutoff(self, mock_urlopen, mock_now):
        """Items older than 3 days from today are excluded."""
        mock_urlopen.side_effect = _mock_urlopen(
            ipo_resp=_make_ipo_response(SAMPLE_IPO_ROWS),
            bond_resp=_make_bond_response(SAMPLE_BOND_ROWS),
        )
        result = stock_app._fetch_xingu_xinzhai()

        ipo_dates = [r["apply_date"] for r in result["ipo"]]
        assert "2026-05-01" not in ipo_dates  # >3 days old
        assert "2026-05-13" in ipo_dates      # future
        assert "2026-05-12" in ipo_dates      # today

        bond_dates = [r["apply_date"] for r in result["bond"]]
        assert "2026-04-01" not in bond_dates  # >3 days old

    @patch.object(stock_app, "_bj_now", return_value=FIXED_NOW)
    @patch("server.urlrequest.urlopen")
    def test_cap_at_8(self, mock_urlopen, mock_now):
        """Each section is capped at 8 items max."""
        many_rows = [
            {"SECURITY_CODE": f"6880{i:02d}", "SECURITY_NAME": f"股票{i}",
             "APPLY_DATE": "2026-05-15 00:00:00", "ISSUE_PRICE": 10.0,
             "ONLINE_ISSUE_LWR": None, "INITIAL_MULTIPLE": None}
            for i in range(12)
        ]
        mock_urlopen.side_effect = _mock_urlopen(
            ipo_resp=_make_ipo_response(many_rows),
            bond_resp=_make_bond_response([]),
        )
        result = stock_app._fetch_xingu_xinzhai()
        assert len(result["ipo"]) == 8

    @patch.object(stock_app, "_bj_now", return_value=FIXED_NOW)
    @patch("server.urlrequest.urlopen")
    def test_cache_hit(self, mock_urlopen, mock_now):
        """Second call same day returns cached data without API call."""
        mock_urlopen.side_effect = _mock_urlopen(
            ipo_resp=_make_ipo_response(SAMPLE_IPO_ROWS[:1]),
            bond_resp=_make_bond_response([]),
        )
        r1 = stock_app._fetch_xingu_xinzhai()
        call_count = mock_urlopen.call_count

        r2 = stock_app._fetch_xingu_xinzhai()
        assert mock_urlopen.call_count == call_count  # no new calls
        assert r1 is r2  # exact same object

    @patch.object(stock_app, "_bj_now", return_value=FIXED_NOW)
    @patch("server.urlrequest.urlopen")
    def test_cache_miss_new_day(self, mock_urlopen, mock_now):
        """Cache is invalidated when Beijing date changes."""
        mock_urlopen.side_effect = _mock_urlopen(
            ipo_resp=_make_ipo_response(SAMPLE_IPO_ROWS[:1]),
            bond_resp=_make_bond_response([]),
        )
        stock_app._fetch_xingu_xinzhai()
        first_calls = mock_urlopen.call_count

        # Simulate next day
        next_day = FIXED_NOW + timedelta(days=1)
        mock_now.return_value = next_day
        stock_app._fetch_xingu_xinzhai()
        assert mock_urlopen.call_count > first_calls

    @patch.object(stock_app, "_bj_now", return_value=FIXED_NOW)
    @patch("server.urlrequest.urlopen")
    def test_ipo_api_failure(self, mock_urlopen, mock_now):
        """IPO API failure is caught; bond data still returned."""
        mock_urlopen.side_effect = _mock_urlopen(
            ipo_error=TimeoutError("timeout"),
            bond_resp=_make_bond_response(SAMPLE_BOND_ROWS[:1]),
        )
        result = stock_app._fetch_xingu_xinzhai()
        assert result["ok"] is True
        assert result["ipo"] == []
        assert len(result["bond"]) == 1

    @patch.object(stock_app, "_bj_now", return_value=FIXED_NOW)
    @patch("server.urlrequest.urlopen")
    def test_bond_api_failure(self, mock_urlopen, mock_now):
        """Bond API failure is caught; IPO data still returned."""
        mock_urlopen.side_effect = _mock_urlopen(
            ipo_resp=_make_ipo_response(SAMPLE_IPO_ROWS[:1]),
            bond_error=ConnectionError("refused"),
        )
        result = stock_app._fetch_xingu_xinzhai()
        assert result["ok"] is True
        assert len(result["ipo"]) == 1
        assert result["bond"] == []

    @patch.object(stock_app, "_bj_now", return_value=FIXED_NOW)
    @patch("server.urlrequest.urlopen")
    def test_both_apis_fail(self, mock_urlopen, mock_now):
        """Both APIs fail — returns ok with empty lists."""
        mock_urlopen.side_effect = _mock_urlopen(
            ipo_error=TimeoutError("timeout"),
            bond_error=TimeoutError("timeout"),
        )
        result = stock_app._fetch_xingu_xinzhai()
        assert result["ok"] is True
        assert result["ipo"] == []
        assert result["bond"] == []

    @patch.object(stock_app, "_bj_now", return_value=FIXED_NOW)
    @patch("server.urlrequest.urlopen")
    def test_null_fields(self, mock_urlopen, mock_now):
        """Null price/win_rate/multiple are preserved as None."""
        row = {"SECURITY_CODE": "688001", "SECURITY_NAME": "空值测试",
               "APPLY_DATE": "2026-05-15 00:00:00", "ISSUE_PRICE": None,
               "ONLINE_ISSUE_LWR": None, "INITIAL_MULTIPLE": None}
        mock_urlopen.side_effect = _mock_urlopen(
            ipo_resp=_make_ipo_response([row]),
            bond_resp=_make_bond_response([]),
        )
        result = stock_app._fetch_xingu_xinzhai()
        ipo = result["ipo"][0]
        assert ipo["price"] is None
        assert ipo["win_rate"] is None
        assert ipo["multiple"] is None
