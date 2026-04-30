"""
Smoke regression test for FUN Stock Tracker.

Checks:
- Flask app imports and routes respond.
- Core local endpoints return JSON with expected keys.
- Auto endpoints are reachable and return JSON objects (even if upstream data is flaky).
- Beijing timezone helper outputs parseable datetime/date strings.

Run:
    python tests/smoke_test.py
"""

from __future__ import annotations

import pathlib
import sys
import unittest


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import app as stock_app  # noqa: E402


class SmokeRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        stock_app.app.testing = True
        cls.client = stock_app.app.test_client()

    def _json_get(self, path: str):
        res = self.client.get(path)
        self.assertEqual(res.status_code, 200, f"GET {path} status={res.status_code}")
        data = res.get_json(silent=True)
        self.assertIsInstance(data, dict, f"GET {path} did not return JSON object")
        return data

    def _json_post(self, path: str, payload: dict):
        res = self.client.post(path, json=payload)
        self.assertEqual(res.status_code, 200, f"POST {path} status={res.status_code}")
        data = res.get_json(silent=True)
        self.assertIsInstance(data, dict, f"POST {path} did not return JSON object")
        return data

    def test_beijing_time_helpers(self):
        date_s = stock_app._bj_date_str()
        dt_s = stock_app._bj_datetime_str()
        ymd = stock_app._bj_yyyymmdd()

        self.assertRegex(date_s, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(dt_s, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
        self.assertRegex(ymd, r"^\d{8}$")

    def test_stocks_endpoint_reachable(self):
        res = self.client.get("/api/stocks")
        self.assertEqual(res.status_code, 200)
        data = res.get_json(silent=True)
        self.assertIsInstance(data, list)

    def test_quickread_endpoint(self):
        data = self._json_post("/api/quickread", {"text": "公司财报显示营收增长，EPS超预期"})
        self.assertIn("ok", data)
        self.assertTrue(data.get("ok"))
        self.assertIn("plain", data)

    def test_macro_impact_endpoint(self):
        data = self._json_post(
            "/api/macro-impact",
            {"indicator": "cpi", "previous": 2.1, "current": 2.3},
        )
        self.assertIn("ok", data)
        self.assertTrue(data.get("ok"))
        self.assertIn("plain", data)

    def test_glossary_endpoint(self):
        data = self._json_get("/api/glossary?term=pe")
        self.assertIn("ok", data)
        self.assertTrue(data.get("ok"))
        self.assertIn("plain", data)

    def test_market_sentiment_manual_endpoint(self):
        payload = {
            "up_count": 3000,
            "down_count": 1200,
            "limit_up_count": 45,
            "consecutive_limit_count": 10,
        }
        data = self._json_post("/api/market-sentiment", payload)
        self.assertIn("ok", data)
        self.assertTrue(data.get("ok"))
        self.assertIn("stage", data)
        self.assertIn("tradable_text", data)

    def test_auto_endpoints_return_json(self):
        for path in [
            "/api/auto-brief",
            "/api/market-sentiment-auto",
            "/api/mainline-auto",
            "/api/ai-edge",
            "/api/limit-stats",
        ]:
            with self.subTest(path=path):
                data = self._json_get(path)
                self.assertIn("ok", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
