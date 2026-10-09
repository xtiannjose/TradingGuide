"""Candle store: broker (MT5) candles on the New York 5 PM day/week boundary.

Rules: docs/ANALYSIS-SPEC.md sections 0 and 2. Only closed candles are returned.
Timestamps: `time` is UTC, `ny` is New York wall clock. Both are tz-aware.
"""
import time
import tomllib
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

NY = ZoneInfo("America/New_York")
SETTINGS = Path(__file__).with_name("settings.toml")

# name -> (MT5 constant, candle minutes, lookback days). Lookbacks from spec section 2.
# The weekly candle is built from the daily one, so daily is fetched for the weekly's 6 years.
TF = {
    "D": ("TIMEFRAME_D1", 1440, 6 * 365),
    "4H": ("TIMEFRAME_H4", 240, 365),
    "2H": ("TIMEFRAME_H2", 120, 90),
    "1H": ("TIMEFRAME_H1", 60, 90),
    "30m": ("TIMEFRAME_M30", 30, 90),
    "15m": ("TIMEFRAME_M15", 15, 90),
}
ORDER = ("W", "D", "4H", "2H", "1H", "30m", "15m")
WEEK_MINUTES = 5 * 1440  # Sunday 5 PM to Friday 5 PM New York


def settings():
    with open(SETTINGS, "rb") as f:
        return tomllib.load(f)


def to_frame(rates, offset_h):
    """MT5 rates to a frame. MT5 stamps are broker wall-clock seconds, not UTC.

    Broker time = New York time + offset_h, all year (the broker follows US daylight saving).
    """
    df = pd.DataFrame(rates)
    wall = pd.to_datetime(df["time"], unit="s") - pd.Timedelta(hours=offset_h)
    # Raises on a nonexistent or ambiguous hour; the market is closed then, so a hit means bad data.
    ny = wall.dt.tz_localize(NY)
    out = df[["open", "high", "low", "close", "tick_volume"]].copy()
    out.insert(0, "ny", ny)
    out.insert(0, "time", ny.dt.tz_convert("UTC"))
    return out.reset_index(drop=True)


def closed_only(df, minutes, now=None):
    """Drop candles still forming. `now` is New York wall clock (naive); default is the real clock."""
    now = now or datetime.now(NY).replace(tzinfo=None)
    end = df["ny"].dt.tz_localize(None) + pd.Timedelta(minutes=minutes)
    return df[end <= now].reset_index(drop=True)


def weekly_from_daily(d, offset_h):
    """Weekly candles (Sunday 5 PM to Friday 5 PM New York) from daily ones.

    Daily candles open 5 PM New York = broker midnight, so the broker date is Monday to Friday.
    """
    week = (d["ny"].dt.tz_localize(None) + pd.Timedelta(hours=offset_h)).dt.to_period("W")
    w = d.groupby(week, sort=True).agg(
        time=("time", "first"), ny=("ny", "first"),
        open=("open", "first"), high=("high", "max"), low=("low", "min"),
        close=("close", "last"), tick_volume=("tick_volume", "sum"),
    )
    # ponytail: always drops the first week, since history may start mid-week
    return w.iloc[1:].reset_index(drop=True)


def connect():
    import MetaTrader5 as mt5  # imported here so the tests run without the terminal
    if not mt5.initialize():
        raise RuntimeError(f"MT5 not reachable (terminal open and logged in?): {mt5.last_error()}")
    return mt5


def load_pair(mt5, symbol, offset_h, extra_days=0):
    """All seven timeframes for one symbol, closed candles only, oldest first.

    extra_days reaches further back than the spec lookbacks, for replays of past dates.
    """
    mt5.symbol_select(symbol, True)
    out = {}
    for name, (const, minutes, days) in TF.items():
        want = int((days + extra_days) * 5 / 7 * 1440 / minutes) + 50
        rates = mt5.copy_rates_from_pos(symbol, getattr(mt5, const), 0, want)
        if rates is None or len(rates) < want:  # the terminal may still be syncing history
            time.sleep(2)
            rates = mt5.copy_rates_from_pos(symbol, getattr(mt5, const), 0, want)
        if rates is None:
            raise RuntimeError(f"no {name} candles for {symbol}: {mt5.last_error()}")
        out[name] = closed_only(to_frame(rates, offset_h), minutes)
    out["W"] = closed_only(weekly_from_daily(out["D"], offset_h), WEEK_MINUTES)
    return {k: out[k] for k in ORDER}
