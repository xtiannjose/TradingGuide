"""Phase 8: replay the analysis over past weeks and count signals and R outcomes.

python app/backtest.py GBPUSD [AUDJPY ...] [--weeks 8]

At each full hour inside the entry window (Mon to Wed, 01:00 to 10:00 New York) the analysis
sees only candles that were closed by then, so nothing uses future data. A SIGNAL opens one
paper trade per pair at the next 15 minute open; stop or target is checked candle by candle
(both in one candle counts as a loss). This checks that the rules behave sensibly and how
often they fire. It does not prove the strategy makes money.
"""
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

import candles
import params
import verdict

DATA = Path(__file__).with_name("data")


def frames_asof(frames, asof_wall):
    """Candles closed by asof (New York wall clock, naive). Same rule the live run uses."""
    out = {}
    for tf, df in frames.items():
        out[tf] = candles.closed_only(df, candles.MINUTES[tf], now=asof_wall)
    return out


def steps(frames, weeks, tp):
    """Hourly decision times (aware New York) in the window over the last `weeks` weeks."""
    last = frames["15m"]["ny"].iloc[-1]
    start = last - timedelta(weeks=weeks)
    t = start.replace(minute=0, second=0, microsecond=0)
    s_h, e_h = int(tp["window_start"][:2]), int(tp["window_end"][:2])
    out = []
    while t <= last:
        if t.weekday() in tp["days"] and s_h <= t.hour <= e_h:
            out.append(t)
        t += timedelta(hours=1)
    return out


def simulate(plan, side, after_wall, m15):
    """Walk 15 minute candles after the signal. Returns ('win'|'loss'|'open', R, exit_time)."""
    d = m15[m15["ny"].dt.tz_localize(None) >= after_wall]
    if d.empty:
        return "open", 0.0, None
    entry = float(d["open"].iloc[0])
    risk = abs(entry - plan["stop"])
    if risk <= 0:
        return "open", 0.0, None
    for _, c in d.iterrows():
        hit_stop = c["low"] <= plan["stop"] if side == "buy" else c["high"] >= plan["stop"]
        hit_tgt = c["high"] >= plan["target"] if side == "buy" else c["low"] <= plan["target"]
        if hit_stop:
            return "loss", -1.0, c["ny"].isoformat()
        if hit_tgt:
            return "win", abs(plan["target"] - entry) / risk, c["ny"].isoformat()
    return "open", 0.0, None


def run_pair(pair, frames, cfg, weeks, off=7):
    trades, signals, busy_until = [], 0, None
    seen = {"SIGNAL": 0, "WAIT_FOR_SESSION": 0, "WATCH": 0, "NO_TRADE": 0}
    times = steps(frames, weeks, cfg["time"])
    for t in times:
        if busy_until is not None and t < busy_until:
            continue
        f = frames_asof(frames, t.replace(tzinfo=None))
        if min(len(f[tf]) for tf in f) < 40:
            continue
        a = verdict.analyze(pair, f, t, cfg, None, None, off)
        seen[a["verdict"]] = seen.get(a["verdict"], 0) + 1
        if a["verdict"] != "SIGNAL" or not a["plan"] or a["plan"].get("target") is None:
            continue
        signals += 1
        res, r, when = simulate(a["plan"], a["plan"]["side"], t.replace(tzinfo=None) + timedelta(minutes=1), frames["15m"])
        trades.append({"at": t.isoformat(), "side": a["plan"]["side"], "grade": a["grade"], "result": res,
                       "r": r, "rr_planned": a["plan"]["rr"], "box": a["plan"]["box"], "exit": when})
        busy_until = datetime.fromisoformat(when) if when else None
    done = [x for x in trades if x["result"] in ("win", "loss")]
    summary = {
        "pair": pair, "weeks": weeks, "decision_points": len(times), "verdict_counts": seen,
        "signals": signals, "closed": len(done), "wins": sum(x["result"] == "win" for x in done),
        "total_r": round(sum(x["r"] for x in done), 2),
        "avg_r": round(float(np.mean([x["r"] for x in done])), 2) if done else None,
        "signals_per_week": round(signals / max(weeks, 1), 2), "trades": trades,
    }
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pairs", nargs="+")
    ap.add_argument("--weeks", type=int, default=8)
    a = ap.parse_args()
    cfg = params.load()
    off = cfg["data"]["server_ny_offset_hours"]
    mt5 = candles.connect()
    try:
        data = {p: candles.load_pair(mt5, p + cfg["data"]["symbol_suffix"], off) for p in a.pairs}
    finally:
        mt5.shutdown()
    DATA.mkdir(exist_ok=True)
    for p, frames in data.items():
        s = run_pair(p, frames, cfg, a.weeks, off)
        (DATA / f"backtest_{p}.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
        print(f"{p}: {s['decision_points']} decision points, verdicts {s['verdict_counts']}")
        print(f"   signals {s['signals']} ({s['signals_per_week']}/week), closed {s['closed']}, wins {s['wins']}, "
              f"total {s['total_r']}R, average {s['avg_r']}R")
        for t in s["trades"]:
            print(f"   {t['at'][:16]} {t['side']:4} grade {t['grade']} box {t['box']:5} {t['result']:5} {t['r']:+.2f}R")


if __name__ == "__main__":
    main()
