"""Module B: market structure for one timeframe (docs/ANALYSIS-SPEC.md section 4).

Everything runs on closes, so a wick can never break a level (strategy.md 3.3).
One forward pass: a level is never changed by later candles, so the state after
candle i is the same whether it is read live or replayed from history.

"""
import numpy as np
import pandas as pd


def atr(df, n=14):
    pc = df["close"].shift()
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()  # Wilder smoothing


def replay(close, atr, k=1.0, trail=False):
    """Walk the closes once. `atr` is an array of the same length; k is P-SWING-ATR.

    trail=False is the course rule: the paired level is placed at a new extreme and stays
    until the next one. trail=True moves it to every newly confirmed swing (latest swing).

    Returns state ("bull"/"bear"/None), ext and pair as (index, price) -- HH and HL when
    bull, LL and LH when bear -- plus the swing points, the open leg and the event list.
    """
    piv = []                         # confirmed swing points (index, price, "H" or "L")
    dirn, ei, ep = 0, 0, close[0]    # open leg: direction, extreme index, extreme price
    hi = lo = (0, close[0])          # running high and low until the first swing point exists
    state = ext = pair = None
    events = []

    def snake(kind, before):
        """Nearest confirmed swing point of `kind` earlier than `before` (the snake trick)."""
        for j, p, t in reversed(piv):
            if t == kind and j < before:
                return (j, p)

    for i, c in enumerate(close):
        t = k * atr[i]
        # 1. zigzag on closes: a swing point is confirmed when price reverses by t
        if dirn == 0:
            if c > hi[1]:
                hi = (i, c)
            if c < lo[1]:
                lo = (i, c)
            if c - lo[1] >= t:
                piv.append((*lo, "L"))
                dirn, ei, ep = 1, i, c
            elif hi[1] - c >= t:
                piv.append((*hi, "H"))
                dirn, ei, ep = -1, i, c
        elif dirn > 0:
            if c > ep:
                ei, ep = i, c
            elif ep - c >= t:
                piv.append((ei, ep, "H"))
                dirn, ei, ep = -1, i, c
        else:
            if c < ep:
                ei, ep = i, c
            elif c - ep >= t:
                piv.append((ei, ep, "L"))
                dirn, ei, ep = 1, i, c

        # 2. state machine on body closes beyond a level
        if state is None:
            if len(piv) >= 2:  # initial anchor: first close beyond the first confirmed high or low
                h0 = next(p for _, p, k_ in piv if k_ == "H")
                l0 = next(p for _, p, k_ in piv if k_ == "L")
                if c > h0:
                    state, ext, pair = "bull", (i, c), snake("L", i)
                elif c < l0:
                    state, ext, pair = "bear", (i, c), snake("H", i)
                else:
                    continue
                events.append({"i": i, "state": state, "ext": ext, "pair": pair, "flip": True})
        elif state == "bull":
            if c > ext[1]:
                ext, pair = (i, c), snake("L", i)
                events.append({"i": i, "state": state, "ext": ext, "pair": pair, "flip": False})
            elif c < pair[1]:
                state, ext, pair = "bear", (i, c), snake("H", i)
                events.append({"i": i, "state": state, "ext": ext, "pair": pair, "flip": True})
            elif trail and (new := snake("L", i)) and new[0] > pair[0]:  # the latest swing low is the HL
                pair = new
                events.append({"i": i, "state": state, "ext": ext, "pair": pair, "flip": False})
        else:
            if c < ext[1]:
                ext, pair = (i, c), snake("H", i)
                events.append({"i": i, "state": state, "ext": ext, "pair": pair, "flip": False})
            elif c > pair[1]:
                state, ext, pair = "bull", (i, c), snake("L", i)
                events.append({"i": i, "state": state, "ext": ext, "pair": pair, "flip": True})
            elif trail and (new := snake("H", i)) and new[0] > pair[0]:  # the latest swing high is the LH
                pair = new
                events.append({"i": i, "state": state, "ext": ext, "pair": pair, "flip": False})

    extreme_kind = "H" if state == "bull" else "L"
    return {
        "state": state, "ext": ext, "pair": pair,
        "ext_confirmed": ext is not None and any(j == ext[0] and t == extreme_kind for j, _, t in piv),
        "pivots": piv, "leg": (dirn, ei, ep), "events": events,
    }


def tf_settings(cs, tf):
    """(swing size in ATR, trail?) for one timeframe from the [structure] settings.

    mode "mixed" (default): weekly follows the course rule so the weekly bias stays stable,
    every lower timeframe follows the latest swing. "latest": all timeframes. "course": none.
    """
    k = cs.get("swing_atr_tf", {}).get(tf, cs["swing_atr"])
    mode = cs.get("mode", "mixed")
    return k, (mode == "latest" or (mode == "mixed" and tf != "W"))


def read(df, k=1.0, trail=False):
    """Structure of one timeframe from a closed-candle frame (candles.py). Output as spec 4.3."""
    r = replay(df["close"].to_numpy(), atr(df).to_numpy(), k, trail)

    def at(p):
        return None if p is None else {"i": p[0], "price": float(p[1]), "time": df["ny"].iloc[p[0]]}

    ev = r["events"]
    flips = [e for e in ev if e["flip"]]
    names = ("HH", "HL") if r["state"] == "bull" else ("LL", "LH")
    out = {
        "state": {"bull": "bullish", "bear": "bearish", None: None}[r["state"]],
        "last_break": df["ny"].iloc[ev[-1]["i"]] if ev else None,
        "last_flip": df["ny"].iloc[flips[-1]["i"]] if flips else None,
        "ext_confirmed": r["ext_confirmed"],
        "raw": r,
    }
    if r["state"]:
        out[names[0]], out[names[1]] = at(r["ext"]), at(r["pair"])
    return out
