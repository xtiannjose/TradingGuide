"""Run from the repo root: python -m pytest app"""
import numpy as np
import pandas as pd

import structure as s


def path(*pts, step=0.5):
    """Closes moving in straight lines through pts, `step` per candle."""
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, round(abs(b - a) / step))
        out += list(np.linspace(a, b, n + 1)[1:])
    return np.array(out)


def run(close, k=1.0):
    return s.replay(close, np.ones(len(close)), k)  # constant ATR 1, so the swing threshold is k


def test_flips_bull_to_bear_to_bull():
    # 10 up to 20, down to 15, up to 25 (bull: HH 25, HL 15), down to 8 (bear), up to 30 (bull)
    r = run(path(10, 20, 15, 25, 8, 30))
    assert [e["state"] for e in r["events"] if e["flip"]] == ["bull", "bear", "bull"]
    assert r["state"] == "bull"
    assert r["ext"][1] == 30 and r["pair"][1] == 8  # HH, and HL = the low of the bear leg


def test_pair_is_always_earlier_than_extreme():
    r = run(path(10, 20, 15, 25, 8, 30, 22, 35))
    assert all(e["pair"][0] < e["ext"][0] for e in r["events"])


def test_pullback_after_the_head_is_not_the_hl_until_a_new_hh():
    base = path(10, 20, 15, 25)                    # bull, HH 25, HL 15
    r = run(np.r_[base, path(25, 18, 24)[1:]])     # pullback to 18 (a swing), back to 24: no new HH
    assert r["state"] == "bull" and r["ext"][1] == 25 and r["pair"][1] == 15
    r = run(np.r_[base, path(25, 18, 30)[1:]])     # new HH: the pullback low becomes the HL
    assert r["ext"][1] == 30 and r["pair"][1] == 18


def test_soft_bump_is_skipped_by_the_snake():
    base = path(10, 20, 15, 25)                    # bull, HL 15
    r = run(np.r_[base, path(25, 24.5, 26, 30)[1:]])  # 0.5 dip is under the threshold of 1
    assert r["ext"][1] == 30 and r["pair"][1] == 15


def test_break_needs_a_close_not_a_touch():
    base = path(10, 20, 15, 25)                    # HL 15
    r = run(np.r_[base, path(25, 15.5)[1:]])       # stops just above the HL
    assert r["state"] == "bull"
    r = run(np.r_[base, path(25, 14.5)[1:]])       # closes below it
    assert r["state"] == "bear"


def test_same_candles_same_state_and_no_look_ahead():
    close = path(10, 20, 15, 25, 8, 30, 22, 35, 12)
    a, b = run(close), run(close)
    assert (a["state"], a["ext"], a["pair"]) == (b["state"], b["ext"], b["pair"])
    for m in range(5, len(close)):                 # the state after m candles never depends on later ones
        part = run(close[:m])
        past = [e for e in a["events"] if e["i"] < m]
        assert (part["state"], part["ext"], part["pair"]) == \
               ((past[-1]["state"], past[-1]["ext"], past[-1]["pair"]) if past else (None, None, None))


def test_wick_only_break_changes_nothing():
    close = path(10, 20, 15, 25, 23)
    df = pd.DataFrame({"close": close, "open": np.r_[close[0], close[:-1]]})
    df["high"], df["low"] = df[["open", "close"]].max(axis=1) + 0.2, df[["open", "close"]].min(axis=1) - 0.2
    df["ny"] = pd.date_range("2026-01-01", periods=len(df), freq="D", tz="America/New_York")
    before = s.read(df)
    df.loc[df.index[-1], "high"] = 40.0   # the last candle spikes far above HH but closes at 23
    after = s.read(df)
    assert (after["state"], after["HH"]["price"], after["HL"]["price"]) == \
           (before["state"], before["HH"]["price"], before["HL"]["price"]) == ("bullish", 25, 15)
