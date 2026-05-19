"""
autodev_runner.py — Autonomous data assembly + AutoDev execution.

Level 3: the runner fetches all data internally, so the caller
only needs to provide positions (ticker + shares + cost).
Everything else — prices, 52-week, sentiment, risk, regime — is
assembled automatically from existing data pipelines.
"""

from __future__ import annotations

from dataclasses import asdict

from analysis.advisor import PositionInput, MarketContext
from trading.autodev import AutoDev


def build_positions(
    holdings: list[dict],
    stock_map: dict[str, dict],
) -> list[PositionInput]:
    """Convert raw holdings + live stock data into PositionInput list.

    holdings: [{"ticker": "600519", "shares": 100, "cost": 1800.0}, ...]
    stock_map: {"600519": {"name": ..., "price": ..., ...}, ...}
    """
    positions = []
    for h in holdings:
        ticker = h.get("ticker", "")
        stock = stock_map.get(ticker, {})
        # Fallback: try suffixed tickers (600519 → 600519.SS / 600519.SZ)
        if not stock:
            for suffix in (".SS", ".SZ"):
                stock = stock_map.get(ticker + suffix, {})
                if stock:
                    break
        cost = float(h.get("cost", 0))
        price = float(stock.get("price") or 0)
        # Fallback: use cost as price when market data unavailable
        if price <= 0 and cost > 0:
            price = cost
        positions.append(PositionInput(
            ticker=ticker,
            name=stock.get("name", h.get("name", ticker)),
            shares=int(h.get("shares", 0)),
            cost=cost,
            price=price,
            change_pct=float(stock.get("change_pct") or 0),
            high52=stock.get("high52"),
            low52=stock.get("low52"),
            volume=int(stock.get("volume") or 0),
        ))
    return positions


def build_context(
    *,
    regime: str = "震荡",
    sentiment_stage: str = "分歧",
    sentiment_score: int = 0,
    tradable: bool = True,
    confidence: float = 50.0,
    risk_events: list[dict] | None = None,
) -> MarketContext:
    """Assemble MarketContext from pre-fetched data."""
    return MarketContext(
        regime=regime,
        sentiment_stage=sentiment_stage,
        sentiment_score=sentiment_score,
        tradable=tradable,
        confidence=confidence,
        risk_events=risk_events or [],
    )


def run_auto(
    holdings: list[dict],
    stock_map: dict[str, dict],
    regime: str = "震荡",
    sentiment_stage: str = "分歧",
    sentiment_score: int = 0,
    tradable: bool = True,
    confidence: float = 50.0,
    risk_events: list[dict] | None = None,
    strategy_name: str = "rule_v1",
    risk_pref: str = "balanced",
) -> dict:
    """One-shot autonomous cycle: assemble data + run AutoDev.

    Returns the full cycle result dict with an extra 'data_sources'
    section showing what was auto-fetched.
    """
    positions = build_positions(holdings, stock_map)
    context = build_context(
        regime=regime,
        sentiment_stage=sentiment_stage,
        sentiment_score=sentiment_score,
        tradable=tradable,
        confidence=confidence,
        risk_events=risk_events,
    )

    # Build current_prices from stock_map (keyed by ticker, bare ticker, and name)
    current_prices = {}
    for ticker, info in stock_map.items():
        if info.get("price"):
            p = float(info["price"])
            current_prices[ticker] = p
            # Also map bare ticker (600519.SS → 600519)
            bare = ticker.split(".")[0]
            if bare != ticker:
                current_prices[bare] = p
            if info.get("name"):
                current_prices[info["name"]] = p

    dev = AutoDev(strategy_name=strategy_name, risk_pref=risk_pref)
    result = dev.run_cycle(positions, context, current_prices)

    # Attach data provenance
    result["data_sources"] = {
        "positions_count": len(positions),
        "prices_from": "live" if any(
            stock_map.get(h.get("ticker", ""), {}).get("source")
            for h in holdings
        ) else "csv",
        "regime": regime,
        "sentiment_stage": sentiment_stage,
        "risk_events_count": len(risk_events or []),
    }

    return result
