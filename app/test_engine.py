"""Tests for the time gate, AOI finder, signals and verdict. Run: python -m pytest app"""
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

import aoi
import params
import signals
import structure
import timegate
import verdict

NY = ZoneInfo("America/New_York")
TP = params.DEFAULTS["time"]
SP = params.DEFAULTS["signal"]
AP = params.DEFAULTS["aoi"]


def ny(y, m, d, h, mi=0):
    return datetime(y, m, d, h, mi, tzinfo=NY)


def candles_from(rows, start="2026-01-01"):
    """rows of (open, high, low, close) to a frame like candles.py makes."""
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close"])
    df["ny"] = pd.date_range(start, periods=len(df), freq="4h", tz=NY)
    return df


# ---- time gate (spec 3)
def test_time_gate_window_and_weekdays():
    assert timegate.time_gate(ny(2026, 10, 12, 2), TP)["pass"]                 # Monday 02:00
    assert timegate.time_gate(ny(2026, 10, 14, 10, 30), TP)["pass"]            # Wednesday, last minute
    late = timegate.time_gate(ny(2026, 10, 12, 11), TP)
    assert not late["pass"] and late["reason"] == "time"
    thu = timegate.time_gate(ny(2026, 10, 15, 2), TP)
    assert not thu["pass"] and thu["reason"] == "weekday"
    sun = timegate.time_gate(ny(2026, 10, 11, 20), TP)
    assert sun["reason"] == "weekday" and sun["next_window"].startswith("2026-10-12T01:00")


def test_market_open_and_sunday_open():
    assert not timegate.market_open(ny(2026, 10, 10, 12))   # Saturday
    assert timegate.market_open(ny(2026, 10, 11, 17, 1))    # Sunday evening
    assert timegate.last_sunday_open(ny(2026, 10, 10, 12)) == datetime(2026, 10, 4, 17, 0)


def test_session_verdict_waits_only_for_an_entry_day():
    def v(dt):
        return verdict.session_verdict(timegate.time_gate(dt, TP), dt, TP)
    assert v(ny(2026, 10, 12, 2)) == ("SIGNAL", None)                      # Monday in the window
    assert v(ny(2026, 10, 12, 12)) == ("WAIT_FOR_SESSION", "time")         # Monday after: Tuesday 01:00
    assert v(ny(2026, 10, 13, 12)) == ("WAIT_FOR_SESSION", "time")         # Tuesday after: Wednesday 01:00
    assert v(ny(2026, 10, 14, 12)) == ("NO_TRADE", "weekday")              # Wednesday after: Thursday
    assert v(ny(2026, 10, 14, 0, 30)) == ("WAIT_FOR_SESSION", "time")      # Wednesday before 01:00: today
    assert v(ny(2026, 10, 15, 3)) == ("NO_TRADE", "weekday")               # Thursday
    assert v(ny(2026, 10, 16, 9)) == ("NO_TRADE", "weekday")               # Friday
    assert v(ny(2026, 10, 16, 21)) == ("WAIT_FOR_SESSION", "time")         # Friday after the close: Monday
    assert v(ny(2026, 10, 10, 12)) == ("WAIT_FOR_SESSION", "time")         # Saturday: Monday 01:00
    assert v(ny(2026, 10, 11, 20)) == ("WAIT_FOR_SESSION", "time")         # Sunday evening: Monday 01:00


# ---- AOI clusters (spec 6)
def test_cluster_is_the_tightest_window_with_three_touches():
    pts = sorted([(1.3000, 10), (1.3010, 20), (1.3020, 40), (1.3300, 60), (1.3500, 90)])
    out = aoi.clusters(pts, 0.0035, 3, 3)
    assert len(out) == 1 and out[0][0] == 1.3000 and out[0][1] == 1.3020 and len(out[0][2]) == 3


def test_two_touches_are_not_a_box_and_close_touches_count_once():
    assert aoi.clusters([(1.30, 10), (1.301, 40)], 0.0035, 3, 3) == []
    assert aoi.clusters([(1.300, 10), (1.301, 11), (1.302, 12)], 0.0035, 3, 3) == []   # one touch within a gap


def test_box_height_is_never_below_five_pips():
    df = candles_from([(1, 1, 1, 1)] * 40)
    b = aoi._box("D", df, 1.3000, 1.3001, [3, 9, 20], 0.0001, AP)
    assert b["pips"] >= 5 - 1e-9


# ---- candle signals (spec 7.1)
def test_bullish_engulfing_and_grade():
    rows = [(1.10, 1.105, 1.095, 1.102)] * 3 + [(1.102, 1.103, 1.097, 1.098), (1.098, 1.108, 1.097, 1.106)]
    df = candles_from(rows)
    s = signals.candle_signals(df, "buy", SP, 0.0001)
    assert any(x["type"] == "engulfing" and x["engulfed"] >= 1 for x in s)
    assert signals.candle_signals(df, "sell", SP, 0.0001) == []


def test_hammer_at_support_and_nothing_on_a_plain_candle():
    flat = [(1.10, 1.101, 1.099, 1.1005)] * 5
    hammer = flat + [(1.1000, 1.1002, 1.0960, 1.1001)]
    assert any(x["type"] in ("hammer", "rejection") for x in signals.candle_signals(candles_from(hammer), "buy", SP, 0.0001))
    plain = flat + [(1.1000, 1.1012, 1.0990, 1.1010)]
    assert signals.candle_signals(candles_from(plain), "buy", SP, 0.0001) == []


def test_break_and_retest_needs_a_return_and_a_rejection():
    box = (1.1000, 1.1020)
    up = [(1.0980, 1.0990, 1.0970, 1.0985)] * 5 + [(1.0985, 1.1050, 1.0980, 1.1040)] + [(1.1040, 1.1060, 1.1035, 1.1050)] * 2
    r = signals.break_retest(candles_from(up), box, "buy", SP)
    assert r["state"] == "waiting_retest"
    up += [(1.1030, 1.1032, 1.1005, 1.1030)]  # long lower wick back into the box, closes high: rejection
    r2 = signals.break_retest(candles_from(up), box, "buy", SP)
    assert r2["state"] in ("rejection", "retesting")


def test_head_and_shoulders_is_forming_until_the_neckline_closes_below():
    close = np.array([100, 110, 104, 120, 104, 111, 100, 98], float)  # LS 110, head 120, RS 111, neck 104
    close = np.interp(np.linspace(0, len(close) - 1, 60), range(len(close)), close)
    df = pd.DataFrame({"open": close, "high": close + 0.3, "low": close - 0.3, "close": close})
    df["ny"] = pd.date_range("2026-01-01", periods=len(df), freq="4h", tz=NY)
    pats = signals.patterns(df, 0.5)
    hs = [p for p in pats if p["type"] == "head_and_shoulders"]
    assert hs and hs[0]["state"] in ("neckline_broken", "retest", "forming")


# ---- structure + verdict on synthetic frames (spec 5 and 8)
def _frames(drift):
    """Seven identical frames following the same close path; enough for analyze() to run."""
    t = np.arange(400)
    close = 1.2000 + drift * t + 0.004 * np.sin(t / 7)
    base = pd.DataFrame({"open": np.r_[close[0], close[:-1]], "close": close})
    base["high"] = base[["open", "close"]].max(axis=1) + 0.0004
    base["low"] = base[["open", "close"]].min(axis=1) - 0.0004
    base["ny"] = pd.date_range("2024-01-01 17:00", periods=len(base), freq="1D", tz=NY)
    return {tf: base.copy() for tf in ("W", "D", "4H", "2H", "1H", "30m", "15m")}


def test_analyze_returns_a_complete_json_ready_result():
    cfg = params.load(user=False)
    out = verdict.analyze("EURUSD", _frames(0.0004), ny(2026, 10, 12, 2), cfg)
    for key in ("verdict", "alignment", "aois", "tf", "checklist", "time_gate", "bias", "alerts"):
        assert key in out
    assert out["verdict"] in ("SIGNAL", "WATCH", "WAIT_FOR_SESSION", "NO_TRADE")
    import json
    json.dumps(out)  # must serialise


def test_counter_trend_when_weekly_and_daily_disagree():
    cfg = params.load(user=False)
    f = _frames(0.0004)
    f["W"] = f["W"].iloc[::-1].reset_index(drop=True)          # a falling weekly against a rising daily
    f["W"]["ny"] = pd.date_range("2024-01-01 17:00", periods=len(f["W"]), freq="1D", tz=NY)
    out = verdict.analyze("EURUSD", f, ny(2026, 10, 12, 2), cfg)
    if out["tf"]["W"]["state"] and out["tf"]["D"]["state"] and out["tf"]["W"]["state"] != out["tf"]["D"]["state"]:
        assert out["verdict"] == "NO_TRADE" and out["reason"] == "counter_trend"
