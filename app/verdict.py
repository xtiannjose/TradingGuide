"""Modules C, F and G: alignment, zone, weekly bias, verdict and plan.

docs/ANALYSIS-SPEC.md sections 5 and 8. analyze() takes closed candles for the seven
timeframes and returns one JSON-ready dict per pair (spec 9.1). It never places orders.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

import aoi
import candles
import lotsize
import signals
import structure
import timegate

ORDER = ("W", "D", "4H", "2H", "1H", "30m", "15m")
ENTRY = ("D", "4H", "2H", "1H", "30m", "15m")
NY = ZoneInfo("America/New_York")


def broker_seconds(ts, offset_h):
    """Chart time: MT5's own clock (New York + offset) as seconds, so D candles sit on their date."""
    return int((ts.tz_localize(None) + pd.Timedelta(hours=offset_h)).timestamp())


def _level(df, p, offset_h):
    ts = df["ny"].iloc[p[0]]
    return {"price": float(p[1]), "time": ts.isoformat(), "t": broker_seconds(ts, offset_h), "index": int(p[0])}


def _tf_block(df, res, offset_h):
    if not res["state"]:
        return {"state": None}
    raw = res["raw"]
    a, b = ("HH", "HL") if res["state"] == "bullish" else ("LL", "LH")
    z = aoi.zone_of(res)
    return {
        "state": res["state"],
        "levels": {a: _level(df, raw["ext"], offset_h), b: _level(df, raw["pair"], offset_h)},
        "ext_name": a, "pair_name": b,
        "ext_confirmed": bool(res["ext_confirmed"]),
        "last_flip": res["last_flip"].isoformat() if res["last_flip"] is not None else None,
        "zone": {"low": float(z[0]), "high": float(z[1])},
        "swings": [{"t": broker_seconds(df["ny"].iloc[i], offset_h), "price": float(pr), "kind": k}
                   for i, pr, k in raw["pivots"][-24:]],
        "flips": [{"t": broker_seconds(df["ny"].iloc[e["i"]], offset_h), "state": e["state"]}
                  for e in raw["events"] if e["flip"]][-12:],
    }


def _clean(o):
    """Recursively turn numpy and pandas values into plain JSON types."""
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, (pd.Timestamp, datetime)):
        return o.isoformat()
    if isinstance(o, float) and o != o:
        return None
    return o


def _target(side, entry, risk, res, aois, pl, pip):
    """Nearest structure point beyond the entry: latest swing on the target timeframes or an opposing box."""
    cands = []
    for tf in pl["target_tfs"]:
        if tf not in res or not res[tf].get("state"):
            continue
        for i, pr, kind in reversed(res[tf]["raw"]["pivots"]):
            if side == "buy" and kind == "H" and pr > entry + 0.5 * risk:
                cands.append((pr - entry, f"{tf} swing high {pr:.5g}", pr))
                break
            if side == "sell" and kind == "L" and pr < entry - 0.5 * risk:
                cands.append((entry - pr, f"{tf} swing low {pr:.5g}", pr))
                break
    for b in aois:
        if side == "buy" and b["low"] > entry and b["role"] == "resistance":
            cands.append((b["low"] - entry, f"{b['tf']} resistance box {b['low']:.5g}", b["low"]))
        if side == "sell" and b["high"] < entry and b["role"] == "support":
            cands.append((entry - b["high"], f"{b['tf']} support box {b['high']:.5g}", b["high"]))
    return min(cands) if cands else None


def _plan(side, box, entry, res, aois, pl, pip, acct, risk_pct):
    stop = box["low"] - pl["stop_buffer_pips"] * pip if side == "buy" else box["high"] + pl["stop_buffer_pips"] * pip
    risk = abs(entry - stop)
    plan = {"side": side, "entry": float(entry), "stop": float(stop), "stop_pips": float(risk / pip),
            "box": box["id"], "note": "Entry is the current price; the real fill is the next candle's open."}
    tgt = _target(side, entry, risk, res, aois, pl, pip)
    if tgt is None:
        plan.update({"target": None, "rr": None, "target_reason": "no structure point beyond the entry"})
        return plan
    dist, why, price = tgt
    rr = dist / risk
    capped = rr > pl["rr_cap"]
    if capped:
        price = entry + pl["rr_cap"] * risk if side == "buy" else entry - pl["rr_cap"] * risk
        rr = pl["rr_cap"]
    plan.update({"target": float(price), "target_pips": float(abs(price - entry) / pip), "rr": float(rr),
                 "rr_next": float(dist / risk), "target_reason": why, "capped": capped})
    if acct and acct.get("balance") and acct.get("pip_value"):
        amount = acct["balance"] * risk_pct / 100
        lot, raw = lotsize.lots(amount, plan["stop_pips"], acct["pip_value"], acct.get("step", 0.01),
                                acct.get("min_lot", 0.01), acct.get("max_lot", 100.0))
        plan.update({"risk_pct": risk_pct, "risk_amount": float(amount), "lots": float(lot),
                     "min_lot_exceeds_risk": bool(raw < acct.get("min_lot", 0.01))})
    return plan


def analyze(pair, frames, now_ny, cfg, acct=None, price=None, offset_h=7):
    """One pair, as of now_ny (an aware New York datetime). frames: tf -> closed candle frame."""
    sp, ap, pl, tp = cfg["signal"], cfg["aoi"], cfg["plan"], cfg["time"]
    k, trail = cfg["structure"]["swing_atr"], cfg["structure"]["trail"]
    pip = 0.01 if pair.endswith("JPY") else 0.0001
    px = float(price) if price is not None else float(frames["15m"]["close"].iloc[-1])
    res = {tf: structure.read(frames[tf], k, trail) for tf in ORDER if tf in frames and len(frames[tf]) > 30}
    emas = {tf: float(frames[tf]["close"].ewm(span=50, adjust=False).mean().iloc[-1])
            for tf in ("W", "D", "4H", "1H") if tf in frames and len(frames[tf])}

    tfb = {tf: _tf_block(frames[tf], res[tf], offset_h) for tf in res}
    sw, sd, s4 = (res[t]["state"] if t in res else None for t in ("W", "D", "4H"))
    if sw is None or sd is None:
        align = {"pass": False, "reason": "no_alignment", "direction": None, "risk": None}
    elif sw != sd:
        align = {"pass": False, "reason": "counter_trend", "direction": None, "risk": "high"}
    else:
        align = {"pass": True, "reason": None, "direction": sw, "risk": "low" if s4 == sw else "mid"}

    sun = timegate.last_sunday_open(now_ny)
    sunday_states = []
    for tf in ("W", "D"):
        df = candles.closed_only(frames[tf], candles.MINUTES[tf], now=sun)
        sunday_states.append(structure.read(df, k, trail)["state"] if len(df) > 30 else None)
    bias_sun = sunday_states[0] if sunday_states[0] == sunday_states[1] else None
    bias = {"now": align["direction"], "sunday": bias_sun, "sunday_at": sun.isoformat(),
            "changed": bool(bias_sun != align["direction"])}

    aois = aoi.find_aois(frames, res, px, pip, ap, emas)
    gate = timegate.time_gate(now_ny, tp)

    side = None
    if align["pass"]:
        side = "buy" if align["direction"] == "bullish" else "sell"
    want = ("support", "inside") if side == "buy" else ("resistance", "inside")

    cand, retest = None, None
    patt = []
    if side:
        live = [b for b in aois if not b["broken"] and b["role"] in want and b["tf"] != "4H"]
        minor = [b for b in aois if not b["broken"] and b["role"] in want and b["tf"] == "4H"]
        pool = live or minor
        cand = min(pool, key=lambda b: b["dist_pips"]) if pool else None
        for b in aois:  # a broken box can come back as a flipped zone after break and retest
            if b["broken"] and b["role"] in want and "4H" in frames:
                br = signals.break_retest(frames[sp["pattern_tf"]], (b["low"], b["high"]), side, sp)
                if br:
                    br["box"] = b["id"]
                    patt.append(br)
                    if br["state"] == "rejection" and cand is None:
                        cand, retest = b, br
        patt += [pt for pt in signals.patterns(frames[sp["pattern_tf"]], k, side)]

    signal = None
    if cand is not None and cand["at"]:
        for tf in ENTRY:
            if tf not in frames or len(frames[tf]) < 5:
                continue
            sigs = signals.candle_signals(frames[tf], side, sp, pip)
            if not sigs:
                continue
            last = frames[tf].iloc[-1]
            near = aoi.at_aoi(float(last["close"]), cand, pip, ap) or \
                (side == "buy" and last["low"] <= cand["high"] and last["close"] >= cand["low"]) or \
                (side == "sell" and last["high"] >= cand["low"] and last["close"] <= cand["high"])
            if near:
                s = sigs[0]
                signal = {**s, "tf": tf, "side": side, "close": float(last["close"]),
                          "closed_at": last["ny"].isoformat(), "t": broker_seconds(last["ny"], offset_h)}
                break

    plan, reason, verdict = None, None, None
    risk_pct = cfg["account"]["risk_pct"]
    if not align["pass"]:
        verdict, reason = "NO_TRADE", align["reason"]
    elif cand is None:
        verdict, reason = "NO_TRADE", "no_aoi"
    elif not cand["at"]:
        verdict, reason = "WATCH", "price_not_at_aoi"
    elif signal is None:
        verdict, reason = "WATCH", "no_confirmation"
    else:
        # entry is the market price now (the next candle's open), not the signal close: a daily or 4H
        # confirmation can be hours old, and the stop and target are measured from where you would enter
        plan = _plan(side, cand, px, res, aois, pl, pip, acct, risk_pct)
        weekly = [b for b in aois if b["tf"] in ("W", "W+D") and b["id"] != cand["id"]]
        opposite = "resistance" if side == "buy" else "support"
        two_r = 2 * abs(px - plan["stop"])
        if plan["target"] is None or plan["rr_next"] < pl["rr_min"]:
            verdict, reason = "NO_TRADE", "rr_below_2"
        elif any(b["role"] == opposite and
                 ((side == "buy" and px < b["low"] <= px + two_r) or (side == "sell" and px > b["high"] >= px - two_r))
                 for b in weekly):
            verdict, reason = "NO_TRADE", "against_weekly_level"
        else:
            verdict, reason = session_verdict(gate, now_ny, tp)
    if verdict in ("NO_TRADE",) and reason in ("rr_below_2", "against_weekly_level"):
        plan = plan  # keep the numbers so the owner can see why it failed

    extras = []
    if cand is not None:
        if cand["tf"] == "W+D" or cand.get("overlaps_other_tf"):
            extras.append("weekly_daily_overlap")
        if cand["extras"]["ema"]:
            extras.append("ema_" + "_".join(cand["extras"]["ema"]))
        if cand["extras"]["round_number"] is not None:
            extras.append("round_number")
        if cand["extras"]["previous_daily_swing"]:
            extras.append("previous_daily_swing")
        if cand["touches"] > 3:
            extras.append("many_touches")
    if align["pass"] and align["risk"] == "low":
        extras.append("four_hour_agrees")
    if retest:
        extras.append("break_and_retest")
    if any(pt.get("state") in ("neckline_broken", "retest") for pt in patt if pt["type"] != "break_and_retest"):
        extras.append("pattern_neckline")
    if signal and signal["tf"] in ("D",):
        extras.append("higher_timeframe_candle")
    grade = None
    if verdict in ("SIGNAL", "WAIT_FOR_SESSION"):
        grade = "A" if (align["risk"] == "low" and len(extras) >= 2) else ("B" if extras else "C")

    awaiting = _awaiting(verdict, reason, cand, side, gate, px, pip, now_ny)
    check = _checklist(now_ny, gate, tfb, align, cand, side, signal, plan, reason, extras, pl)
    alerts = []
    for b in aois:
        alerts.append({"price": b["high"], "note": f"{b['tf']} box top ({b['role']})", "box": b["id"]})
        alerts.append({"price": b["low"], "note": f"{b['tf']} box bottom ({b['role']})", "box": b["id"]})

    out_aois = []
    for b in aois:
        c = {k2: v for k2, v in b.items() if k2 not in ("touch_idx", "touch_times")}
        c["touch_t"] = [broker_seconds(t, offset_h) for t in b["touch_times"]]
        out_aois.append(c)
    return _clean({
        "pair": pair, "asof_ny": now_ny.isoformat(), "price": px, "pip": pip,
        "data_last": {tf: frames[tf]["ny"].iloc[-1].isoformat() for tf in frames if len(frames[tf])},
        "time_gate": gate, "market_open": timegate.market_open(now_ny),
        "tf": tfb, "alignment": align, "bias": bias, "emas": emas,
        "aois": out_aois, "candidate": cand["id"] if cand else None,
        "signal": signal, "patterns": patt, "verdict": verdict, "reason": reason, "grade": grade,
        "awaiting": awaiting, "plan": plan, "extras": extras, "checklist": check, "alerts": alerts,
        "params": {"swing_atr": k, "trail": trail, "cluster_pips": ap["cluster_pips"]},
    })


def session_verdict(gate, now_ny, tp):
    """Verdict once a confirmed setup exists (spec 8.1, T5).

    SIGNAL inside the window. Outside it: WAIT_FOR_SESSION only if the next pre-London hour
    falls on an entry day (Monday to Wednesday), otherwise NO_TRADE(weekday). On Saturday and
    Sunday that hour is Monday's. After the window on Wednesday it is Thursday's.
    """
    if gate["pass"]:
        return "SIGNAL", None
    wd = now_ny.weekday()
    if wd in (5, 6):
        return "WAIT_FOR_SESSION", "time"
    if wd not in tp["days"]:
        return "NO_TRADE", "weekday"
    nxt = wd + 1 if now_ny.time() >= timegate.hm(tp["window_start"]) else wd
    return ("WAIT_FOR_SESSION", "time") if nxt in tp["days"] else ("NO_TRADE", "weekday")


def _awaiting(verdict, reason, cand, side, gate, px, pip, now_ny):
    if verdict == "SIGNAL":
        return "Confirmation closed inside the entry window. Enter at the next candle open."
    if verdict == "WAIT_FOR_SESSION":
        return f"Confirmation closed outside the window. Enter in the pre-London hour: {gate['next_window']}."
    if reason == "weekday" and cand and gate["reason"] is not None and now_ny.weekday() in (2, 3, 4):
        return "Setup is ready but the next pre-London hour is not a Monday to Wednesday: skipped."
    if reason == "price_not_at_aoi" and cand:
        return f"Price to reach {cand['tf']} {cand['role']} {cand['low']:.5g} to {cand['high']:.5g} ({cand['dist_pips']:.0f} pips away)."
    if reason == "no_confirmation" and cand:
        return f"At the {cand['tf']} box. Waiting for a closed {side} confirmation (rejection or engulfing)."
    return {
        "counter_trend": "Daily is against the weekly: counter-trend, not traded.",
        "no_alignment": "Weekly or daily structure is not readable yet.",
        "no_aoi": "No valid area of interest on the right side of price.",
        "rr_below_2": "The next structure point gives less than 1:2: skipped.",
        "against_weekly_level": "A weekly level sits in the way of the target: skipped.",
        "weekday": "Thursday and Friday give no entries. Next window: " + str(gate.get("next_window")),
    }.get(reason, "")


def _checklist(now_ny, gate, tfb, align, cand, side, signal, plan, reason, extras, pl):
    def st(tf):
        return tfb.get(tf, {}).get("state")
    items = [
        ("Weekly structure", st("W") is not None, st("W") or "not readable"),
        ("Daily structure", st("D") is not None, st("D") or "not readable"),
        ("Weekly and daily agree", align["pass"],
         f"{align['direction']} ({align['risk']} risk)" if align["pass"] else (align["reason"] or "")),
        ("4H agrees (extra)", align["pass"] and align["risk"] == "low", st("4H") or "not readable"),
        ("Area of interest on the right side", cand is not None,
         f"{cand['tf']} {cand['low']:.5g} to {cand['high']:.5g}, {cand['touches']} touches" if cand else "none"),
        ("Price at the area", bool(cand and cand["at"]),
         f"{cand['dist_pips']:.0f} pips away" if cand and not cand["at"] else ("inside" if cand else "")),
        ("Closed confirmation at the area", signal is not None,
         f"{signal['type']} on {signal['tf']}" if signal else "none yet"),
        ("Weekday is Monday to Wednesday", gate["reason"] != "weekday", now_ny.strftime("%A")),
        ("Inside the entry window", gate["reason"] is None, f"{now_ny:%H:%M} New York"),
        ("Reward to risk at least 1:2", bool(plan and plan.get("rr_next") is not None and plan["rr_next"] >= pl["rr_min"]),
         f"1:{plan['rr_next']:.1f}" if plan and plan.get("rr_next") else "not computed"),
        ("No weekly level in the way", reason != "against_weekly_level", ""),
    ]
    out = [{"n": n, "item": a, "pass": bool(b), "detail": c} for n, (a, b, c) in enumerate(items, 1)]
    return out
