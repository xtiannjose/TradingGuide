"""Module D: areas of interest (docs/ANALYSIS-SPEC.md section 6).

A box is the tightest cluster of at least `min_touches` swing points of one timeframe that
fits in `cluster_pips`, inside that timeframe's zone (between HH and HL, or LH and LL).
Wicks never create touches; only swing points (closes) do.
"""
import numpy as np


def zone_of(res):
    """(low, high) of the zone from a structure.read result, or None."""
    if not res or not res.get("state"):
        return None
    a, b = ("HH", "HL") if res["state"] == "bullish" else ("LL", "LH")
    return tuple(sorted((res[a]["price"], res[b]["price"])))


def clusters(pts, cap, minn, gap):
    """pts: sorted [(price, index)]. Non-overlapping windows of >= minn touches, best first.

    Windows are maximal runs of swing points no taller than cap. Two touches closer than
    `gap` candles count once. Ranked by touches, then by tightness.
    """
    wins = []
    for i in range(len(pts)):
        j = i
        while j + 1 < len(pts) and pts[j + 1][0] - pts[i][0] <= cap:
            j += 1
        if j > i:
            wins.append((i, j))
    wins = [w for w in wins if not any(o != w and o[0] <= w[0] and o[1] >= w[1] for o in wins)]
    cands = []
    for i, j in wins:
        kept = []
        for x in sorted(p[1] for p in pts[i:j + 1]):
            if not kept or x - kept[-1] >= gap:
                kept.append(x)
        if len(kept) >= minn:
            cands.append((pts[i][0], pts[j][0], kept))
    cands.sort(key=lambda c: (-len(c[2]), c[1] - c[0]))
    out = []
    for lo, hi, kept in cands:
        if all(hi < o[0] or lo > o[1] for o in out):
            out.append((lo, hi, kept))
    return out


def _box(tf, df, lo, hi, kept, pip, ap):
    if hi - lo < ap["min_pips"] * pip:  # a tight cluster still needs a visible box
        mid = (lo + hi) / 2
        lo, hi = mid - ap["min_pips"] * pip / 2, mid + ap["min_pips"] * pip / 2
    return {"tf": tf, "low": float(lo), "high": float(hi), "pips": float((hi - lo) / pip),
            "touches": len(kept), "touch_idx": kept,
            "touch_times": [df["ny"].iloc[i] for i in kept], "minor": tf == "4H"}


def _broken(df, box):
    """True when price has gone to the other side of the box since its last touch."""
    c = df["close"].to_numpy(float)
    t = box["touch_idx"][-1]
    before = None
    for j in range(t - 1, max(t - 60, -1), -1):
        if c[j] > box["high"]:
            before = "above"
            break
        if c[j] < box["low"]:
            before = "below"
            break
    now = "above" if c[-1] > box["high"] else "below" if c[-1] < box["low"] else None
    return before is not None and now is not None and before != now


def at_aoi(price, box, pip, ap):
    """Price is inside the box widened by a quarter of its height (at least 5 pips)."""
    pad = max(ap["at_aoi_frac"] * (box["high"] - box["low"]), ap["at_aoi_min_pips"] * pip)
    return box["low"] - pad <= price <= box["high"] + pad


def _extras(box, pip, ap, emas, recent_daily):
    prox = ap["ema_prox_pips"] * pip
    ema = [tf for tf in ("W", "D", "4H", "1H") if emas.get(tf) is not None
           and box["low"] - prox <= emas[tf] <= box["high"] + prox]
    step = 0.5 if pip >= 0.01 else 0.005
    mid = (box["low"] + box["high"]) / 2
    rn = round(mid / step) * step
    rp = ap["round_prox_pips"] * pip
    return {
        "ema": ema,
        "round_number": float(rn) if box["low"] - rp <= rn <= box["high"] + rp else None,
        "previous_daily_swing": any(box["low"] - prox <= p <= box["high"] + prox for p in recent_daily),
    }


def find_aois(frames, results, price, pip, ap, emas):
    """All valid boxes, nearest first. frames: tf -> closed candles; results: tf -> structure.read."""
    found = []
    for tf in ("W", "D", "4H") if ap["include_4h"] else ("W", "D"):
        res, df = results.get(tf), frames.get(tf)
        z = zone_of(res)
        if z is None or df is None:
            continue
        look = ap["lookback"][tf]
        piv = sorted((pr, i) for i, pr, _ in res["raw"]["pivots"] if i >= len(df) - look and z[0] <= pr <= z[1])
        cl = clusters(piv, ap["cluster_pips"] * pip, ap["min_touches"], ap["touch_gap"])
        if not cl:  # nothing that tight: allow the course's hard ceiling before giving up
            cl = clusters(piv, ap["max_pips"] * pip, ap["min_touches"], ap["touch_gap"])
        boxes = [_box(tf, df, lo, hi, kept, pip, ap) for lo, hi, kept in cl]
        boxes = [b for b in boxes if b["pips"] <= ap["max_pips"] + 1e-9]
        for b in boxes:
            b["_df"] = df
        boxes.sort(key=lambda b: _dist(price, b))
        found += boxes[:2 if tf == "4H" else ap["max_count"]]
    found = _merge(found, pip, ap, frames, results)
    daily = results.get("D")
    recent_daily = [pr for _, pr, _ in daily["raw"]["pivots"][-6:]] if daily else []
    out = []
    for n, b in enumerate(sorted(found, key=lambda b: _dist(price, b)), 1):
        df = b.pop("_df")
        b["broken"] = _broken(df, b)
        b["role"] = ("inside" if b["low"] <= price <= b["high"]
                     else "support" if price > b["high"] else "resistance")
        if b["broken"]:  # a broken box flips role; it only comes back after a break and retest
            b["role"] = {"support": "resistance", "resistance": "support"}.get(b["role"], b["role"])
        b["dist_pips"] = float(_dist(price, b) / pip)
        b["at"] = at_aoi(price, b, pip, ap)
        b["extras"] = _extras(b, pip, ap, emas, recent_daily)
        b["id"] = f"{b['tf']}{n}"
        out.append(b)
    return out


def _dist(price, b):
    if b["low"] <= price <= b["high"]:
        return 0.0
    return min(abs(price - b["low"]), abs(price - b["high"]))


def _merge(boxes, pip, ap, frames, results):
    """A weekly and a daily box that overlap become one box with >= min_touches on both."""
    ws = [b for b in boxes if b["tf"] == "W"]
    ds = [b for b in boxes if b["tf"] == "D"]
    used, merged = set(), []
    if ws and ds:
        wp = {i: pr for i, pr, _ in results["W"]["raw"]["pivots"]}
        dp = {i: pr for i, pr, _ in results["D"]["raw"]["pivots"]}
    for w in ws:
        for d in ds:
            lo, hi = max(w["low"], d["low"]), min(w["high"], d["high"])
            if hi <= lo or id(d) in used or id(w) in used:
                continue
            nw = [i for i in w["touch_idx"] if lo <= wp.get(i, np.nan) <= hi]
            nd = [i for i in d["touch_idx"] if lo <= dp.get(i, np.nan) <= hi]
            if len(nw) >= ap["min_touches"] and len(nd) >= ap["min_touches"] and (hi - lo) >= ap["min_pips"] * pip:
                m = _box("W", d["_df"], lo, hi, nd, pip, ap)
                m.update({"tf": "W+D", "minor": False, "overlap": True, "touches_w": len(nw),
                          "touches_d": len(nd), "_df": d["_df"]})
                merged.append(m)
                used.update((id(w), id(d)))
    rest = [b for b in boxes if id(b) not in used]
    for b in rest:
        b.setdefault("overlap", False)
        other = ds if b["tf"] == "W" else ws if b["tf"] == "D" else []
        b["overlaps_other_tf"] = any(not (b["high"] < o["low"] or b["low"] > o["high"]) for o in other)
    return merged + rest
