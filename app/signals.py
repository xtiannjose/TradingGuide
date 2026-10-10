"""Module E: candle signals and patterns (docs/ANALYSIS-SPEC.md section 7). Closed candles only.

A signal is only looked for on the latest closed candle of a timeframe (video 9 enters at the
next candle's open, so an older one is stale). Shapes are app defaults from params.py.
"""
import numpy as np

import structure


def _ohlc(df):
    return tuple(df[k].to_numpy(float) for k in ("open", "high", "low", "close"))


def _shape(o, h, l, c, i, side, sp):
    """Doji or rejection shape of candle i for a `side` setup, or None."""
    rng = h[i] - l[i]
    if rng <= 0:
        return None
    body = abs(c[i] - o[i])
    lower, upper = min(o[i], c[i]) - l[i], h[i] - max(o[i], c[i])
    wick, opp = (lower, upper) if side == "buy" else (upper, lower)
    if body <= sp["rej_body"] * rng and wick >= 2 * body and wick >= 0.5 * rng:
        if opp <= 0.1 * rng:
            return "hammer" if side == "buy" else "shooting_star"
        return "rejection"
    if body <= sp["doji_body"] * rng:
        return "doji"
    return None


def candle_signals(df, side, sp, pip):
    """Signals on the latest closed candle for a 'buy' or 'sell' setup, strongest first."""
    n = len(df)
    if n < 4:
        return []
    o, h, l, c = _ohlc(df)
    i = n - 1
    out = []
    shape = _shape(o, h, l, c, i, side, sp)
    if shape:
        out.append({"type": shape, "grade": 1 if shape == "doji" else 2})
    # engulfing: the last body closes beyond the bodies of the previous N candles, N >= 1
    bullish = c[i] > o[i]
    prev_opposite = (c[i - 1] < o[i - 1]) if side == "buy" else (c[i - 1] > o[i - 1])
    if (side == "buy") == bullish and prev_opposite:
        tol = 0.1 * pip
        best = 0
        for m in range(1, min(6, i) + 1):
            sl = slice(i - m, i)
            top, bot = np.maximum(o[sl], c[sl]).max(), np.minimum(o[sl], c[sl]).min()
            if side == "buy" and c[i] > top and o[i] <= bot + tol:
                best = m
            elif side == "sell" and c[i] < bot and o[i] >= top - tol:
                best = m
        if best:
            kind = "engulfing"
            if best >= 2 and _shape(o, h, l, c, i - 1, side, sp):
                kind = "morning_star" if side == "buy" else "evening_star"
            out.append({"type": kind, "grade": best + (1 if kind != "engulfing" else 0), "engulfed": best})
    out.sort(key=lambda s: -s["grade"])
    return out


def break_retest(df, box, side, sp):
    """Close beyond the box, then a return into it with a rejection (spec 7.2).

    side 'buy': the box is broken upward and retested from above. Returns a dict or None.
    """
    n = len(df)
    if n < 6:
        return None
    o, h, l, c = _ohlc(df)
    lo, hi = box
    look = range(n - 1, max(n - 80, 1), -1)
    b = None
    for i in look:
        if side == "buy" and c[i] > hi and c[i - 1] <= hi:
            b = i
            break
        if side == "sell" and c[i] < lo and c[i - 1] >= lo:
            b = i
            break
    if b is None:
        return None
    ret = [j for j in range(b + 1, n) if (l[j] <= hi if side == "buy" else h[j] >= lo)]
    if not ret:
        return {"type": "break_and_retest", "side": side, "state": "waiting_retest", "break_index": b}
    if ret[0] - b > sp["retest_window"]:
        return {"type": "break_and_retest", "side": side, "state": "missed", "break_index": b}
    last_in_box = ret[-1] == n - 1
    rejected = last_in_box and bool(candle_signals(df, side, sp, 1e-4))
    return {"type": "break_and_retest", "side": side, "break_index": b, "retest_index": ret[0],
            "state": "rejection" if rejected else "retesting"}


PATTERN_DEFAULTS = {
    "head_min_atr": 2.0,       # the head stands at least this many ATR above the troughs: a sizeable pattern, not noise
    "head_over": 0.15,         # the head clears the higher shoulder by this share of its own height
    "shoulder_min": 0.30,      # each shoulder rises at least this share of the head height above the troughs
    "shoulder_diff": 0.40,     # the two shoulders differ by at most this share of the head height
    "trough_diff": 0.35,       # the two troughs differ by at most this share of the head height (a level neckline)
    "double_depth_atr": 1.5,   # a double top or bottom is at least this many ATR deep
    "double_peak_diff": 0.30,  # its two peaks differ by at most this share of that depth
    "head_min_bars": 24,       # head and shoulders spans at least this many candles (4 days on the 4H)
    "double_min_bars": 12,     # a double top or bottom spans at least this many candles
}


def patterns(df, k, side_hint=None, pp=None):
    """Head and shoulders (and inverse) and double top/bottom from the swing points of df.

    Valid only after a body close beyond the neckline; the right shoulder alone never signals.
    Proportion limits are app defaults (`pp`, PATTERN_DEFAULTS): the course gives the shapes, not numbers.
    """
    pp = {**PATTERN_DEFAULTS, **(pp or {})}
    r = structure.replay(df["close"].to_numpy(float), structure.atr(df).to_numpy(), k)
    piv = r["pivots"]
    close = df["close"].to_numpy(float)
    n = len(df)
    atr_now = float(structure.atr(df).iloc[-1])
    out = []

    def state(neck, after_idx, sell):
        tail = close[after_idx + 1:]
        if not len(tail):
            return "forming", None
        hit = np.where(tail < neck)[0] if sell else np.where(tail > neck)[0]
        if not len(hit):
            return "forming", None
        b = after_idx + 1 + int(hit[0])
        back = close[b + 1:]
        retest = bool(len(back) and ((back >= neck).any() if sell else (back <= neck).any()))
        return ("retest" if retest else "neckline_broken"), b

    def head_and_shoulders(p, sell):
        """p: five swing points. Heights are measured from the mean of the two troughs."""
        sign = 1 if sell else -1
        ls, t1, hd, t2, rs = (x[1] * sign for x in p)   # flip so the head is always the highest
        base = (t1 + t2) / 2
        h = hd - base
        if h < pp["head_min_atr"] * atr_now or p[4][0] - p[0][0] < pp["head_min_bars"]:
            return False
        return (hd - max(ls, rs) >= pp["head_over"] * h
                and min(ls, rs) - base >= pp["shoulder_min"] * h
                and abs(ls - rs) <= pp["shoulder_diff"] * h
                and abs(t1 - t2) <= pp["trough_diff"] * h)

    if len(piv) >= 5:
        p = piv[-5:]
        kinds = "".join(x[2] for x in p)
        if kinds == "HLHLH" and head_and_shoulders(p, True):
            neck = p[1][1]
            st, b = state(neck, p[4][0], True)
            out.append({"type": "head_and_shoulders", "side": "sell", "neckline": neck, "state": st,
                        "break_index": b, "points": [x[0] for x in p]})
        if kinds == "LHLHL" and head_and_shoulders(p, False):
            neck = p[1][1]
            st, b = state(neck, p[4][0], False)
            out.append({"type": "inverse_head_and_shoulders", "side": "buy", "neckline": neck, "state": st,
                        "break_index": b, "points": [x[0] for x in p]})
    if len(piv) >= 3:
        p = piv[-3:]
        kinds = "".join(x[2] for x in p)
        depth = abs((p[0][1] + p[2][1]) / 2 - p[1][1])
        if (depth >= pp["double_depth_atr"] * atr_now and abs(p[0][1] - p[2][1]) <= pp["double_peak_diff"] * depth
                and p[2][0] - p[0][0] >= pp["double_min_bars"]):
            if kinds == "HLH":
                st, b = state(p[1][1], p[2][0], True)
                out.append({"type": "double_top", "side": "sell", "neckline": p[1][1], "state": st,
                            "break_index": b, "points": [x[0] for x in p]})
            if kinds == "LHL":
                st, b = state(p[1][1], p[2][0], False)
                out.append({"type": "double_bottom", "side": "buy", "neckline": p[1][1], "state": st,
                            "break_index": b, "points": [x[0] for x in p]})
    if side_hint:
        out = [x for x in out if x["side"] == side_hint]
    return out
