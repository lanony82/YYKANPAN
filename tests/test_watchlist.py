"""P1 tests for watchlist CRUD and config export/import."""

from __future__ import annotations

import json
import pathlib
import sys
from unittest.mock import patch

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import server as stock_app
from config import cfg


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Flask test client with isolated watchlist file."""
    wl_path = tmp_path / "watchlist_cn.json"
    wl_path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(stock_app, "WATCHLIST", wl_path)
    monkeypatch.setattr(cfg, "WATCHLIST_PATH", wl_path)
    stock_app._invalidate_stocks_cache()
    stock_app.app.config["TESTING"] = True
    with stock_app.app.test_client() as c:
        yield c


FAKE_STOCK = {
    "ticker": "600519.SS",
    "name": "贵州茅台",
    "price": 1580.0,
    "prev_close": 1575.5,
    "change": 4.5,
    "change_pct": 0.29,
    "volume": 12345678,
    "high52": None,
    "low52": None,
    "market_cap": 1980000000000,
    "date": "2026-05-10",
    "source": "akshare",
    "error": None,
}


def _mock_fetch_stock(ticker, name=""):
    return {**FAKE_STOCK, "ticker": ticker, "name": name or ticker}


# ── POST /api/stocks — add stock ─────────────────────────────────────────────

class TestAddStock:
    def test_add_valid_ticker(self, client):
        with patch.object(stock_app, "fetch_stock", side_effect=_mock_fetch_stock):
            resp = client.post(
                "/api/stocks",
                json={"ticker": "600519.SS", "name": "贵州茅台"},
            )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is True
        assert data["stock"]["ticker"] == "600519.SS"

    def test_add_duplicate_ticker(self, client):
        with patch.object(stock_app, "fetch_stock", side_effect=_mock_fetch_stock):
            client.post("/api/stocks", json={"ticker": "600519.SS"})
            resp = client.post("/api/stocks", json={"ticker": "600519.SS"})
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is False
        assert "已在列表中" in data["msg"]

    def test_add_empty_ticker_returns_400(self, client):
        resp = client.post("/api/stocks", json={"ticker": ""})
        assert resp.status_code == 400

    def test_add_invalid_ticker_returns_error(self, client):
        def _fail_fetch(ticker, name=""):
            return {"ticker": ticker, "name": name, "error": "代码不存在"}

        with patch.object(stock_app, "fetch_stock", side_effect=_fail_fetch):
            resp = client.post("/api/stocks", json={"ticker": "ZZZZZZ"})
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is False
        assert "无法获取数据" in data["msg"]


# ── DELETE /api/stocks/<ticker> ──────────────────────────────────────────────

class TestRemoveStock:
    def test_delete_existing(self, client):
        with patch.object(stock_app, "fetch_stock", side_effect=_mock_fetch_stock):
            client.post("/api/stocks", json={"ticker": "600519.SS", "name": "贵州茅台"})
        resp = client.delete("/api/stocks/600519.SS")
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is True

    def test_delete_not_found_returns_404(self, client):
        resp = client.delete("/api/stocks/NOTEXIST")
        assert resp.status_code == 404


# ── GET /api/config/export ───────────────────────────────────────────────────

class TestConfigExport:
    def test_export_empty(self, client):
        resp = client.get("/api/config/export")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "watchlist" in data
        assert isinstance(data["watchlist"], list)
        assert "exported_at" in data

    def test_export_after_add(self, client):
        with patch.object(stock_app, "fetch_stock", side_effect=_mock_fetch_stock):
            client.post("/api/stocks", json={"ticker": "600519.SS", "name": "贵州茅台"})
        resp = client.get("/api/config/export")
        data = resp.get_json()
        assert len(data["watchlist"]) == 1
        assert data["watchlist"][0]["ticker"] == "600519.SS"


# ── POST /api/config/import ──────────────────────────────────────────────────

class TestConfigImport:
    def test_import_valid(self, client):
        payload = {
            "watchlist": [
                {"ticker": "600519.SS", "name": "贵州茅台"},
                {"ticker": "000858.SZ", "name": "五粮液"},
            ]
        }
        resp = client.post("/api/config/import", json=payload)
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is True
        assert data["count"] == 2

        # Verify export reflects the import
        export = client.get("/api/config/export").get_json()
        assert len(export["watchlist"]) == 2

    def test_import_missing_watchlist_key(self, client):
        resp = client.post("/api/config/import", json={"other": "data"})
        data = resp.get_json()
        assert data["ok"] is False

    def test_import_invalid_watchlist_type(self, client):
        resp = client.post("/api/config/import", json={"watchlist": "not a list"})
        data = resp.get_json()
        assert data["ok"] is False

    def test_import_entry_missing_ticker(self, client):
        resp = client.post(
            "/api/config/import",
            json={"watchlist": [{"name": "no ticker"}]},
        )
        data = resp.get_json()
        assert data["ok"] is False

    def test_import_overwrites_existing(self, client):
        # First import
        client.post(
            "/api/config/import",
            json={"watchlist": [{"ticker": "A"}, {"ticker": "B"}]},
        )
        # Second import replaces
        client.post(
            "/api/config/import",
            json={"watchlist": [{"ticker": "C"}]},
        )
        export = client.get("/api/config/export").get_json()
        assert len(export["watchlist"]) == 1
        assert export["watchlist"][0]["ticker"] == "C"


# ── GET /api/watchlist ──────────────────────────────────────────────────────

class TestWatchlistEndpoint:
    def test_watchlist_empty(self, client):
        resp = client.get("/api/watchlist")
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is True
        assert data["watchlist"] == []
        assert data["count"] == 0

    def test_watchlist_after_add(self, client):
        with patch.object(stock_app, "fetch_stock", side_effect=_mock_fetch_stock):
            client.post("/api/stocks", json={"ticker": "600519.SS", "name": "贵州茅台"})

        resp = client.get("/api/watchlist")
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is True
        assert data["count"] == 1
        assert data["watchlist"][0]["ticker"] == "600519.SS"
