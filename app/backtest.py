"""Phase 8: replay the analysis over past weeks and count signals and R outcomes.

python app/backtest.py GBPUSD [AUDJPY ...] [--weeks 8]     or:  python app/backtest.py all --weeks 12
long test on the 1H: python app/backtest.py GBPUSD EURUSD --weeks 26 --sim 1H --extra-days 120

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


def steps(frames, weeks, tp, sim="15m"):
    """Hourly decision times (aware New York) in the window over the last `weeks` weeks."""
    last = frames[sim]["ny"].iloc[-1]
    start = last - timedelta(weeks=weeks)
    t = start.replace(minute=0, second=0, microsecond=0)
    s_h, e_h = int(tp["window_start"][:2]), int(tp["window_end"][:2])
    out = []
    while t <= last:
        if t.weekday() in tp["days"] and s_h <= t.hour <= e_h:
            out.append(t)
        t += timedelta(hours=1)
    return out


def simulate(plan, side, after_wall, m15, pip=None):
    """Walk candles after the signal. Returns ('win'|'loss'|'open', R, exit_time).

    Candles are bid prices. With `pip` and a spread column (MT5 gives it per candle, in points) a buy
    enters at the ask and a sell exits or stops at the ask, so the spread of the entry candle is paid.
    ponytail: one spread for the whole trade, the real one widens at rollover and news.
    """
    d = m15[m15["ny"].dt.tz_localize(None) >= after_wall]
    if d.empty:
        return "open", 0.0, None
    sp = float(d["spread"].iloc[0]) * pip / 10 if pip and "spread" in d.columns else 0.0  # points to price
    entry = float(d["open"].iloc[0]) + (sp if side == "buy" else 0.0)
    risk = abs(entry - plan["stop"])
    if risk <= 0:
        return "open", 0.0, None
    for _, c in d.iterrows():
        hit_stop = c["low"] <= plan["stop"] if side == "buy" else c["high"] + sp >= plan["stop"]
        hit_tgt = c["high"] >= plan["target"] if side == "buy" else c["low"] + sp <= plan["target"]
        if hit_stop:
            return "loss", -1.0, c["ny"].isoformat()
        if hit_tgt:
            return "win", abs(plan["target"] - entry) / risk, c["ny"].isoformat()
    return "open", 0.0, None


def run_pair(pair, frames, cfg, weeks, off=7, sim="15m", spread=True):
    trades, signals, busy_until = [], 0, None
    seen = {"SIGNAL": 0, "WAIT_FOR_SESSION": 0, "WATCH": 0, "NO_TRADE": 0}
    times = steps(frames, weeks, cfg["time"], sim)
    pip = 0.01 if pair.endswith("JPY") else 0.0001
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
        res, r, when = simulate(a["plan"], a["plan"]["side"], t.replace(tzinfo=None) + timedelta(minutes=1), frames[sim], pip if spread else None)
        trades.append({"at": t.isoformat(), "side": a["plan"]["side"], "grade": a["grade"], "result": res,
                       "r": r, "rr_planned": a["plan"]["rr"], "box": a["plan"]["box"], "exit": when,
                       "sig_tf": a["signal"]["tf"], "sig_type": a["signal"]["type"], "stop_pips": a["plan"]["stop_pips"],
                       "align_risk": a["alignment"]["risk"]})
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
    ap.add_argument("--set", action="append", default=[], metavar="PATH=VALUE",
                    help="override a setting for this run, e.g. plan.stop_min_atr_d=0.25 or signal.entry_tfs=[\"D\",\"4H\"]")
    ap.add_argument("--tag", default="", help="suffix for the output files, to keep variants apart")
    ap.add_argument("--sim", default="15m", help="timeframe the paper trades are walked on; 1H allows a longer history")
    ap.add_argument("--extra-days", type=int, default=0, help="load this many extra days of history (for long tests)")
    ap.add_argument("--no-spread", action="store_true", help="ignore the broker spread (the earlier, kinder way)")
    a = ap.parse_args()
    cfg = params.load()
    for item in a.set:
        path, _, raw = item.partition("=")
        node = cfg
        *head, last = path.split(".")
        for h in head:
            node = node[h]
        try:
            node[last] = json.loads(raw)
        except ValueError:
            node[last] = raw
    off = cfg["data"]["server_ny_offset_hours"]
    if a.pairs == ["all"]:
        a.pairs = cfg["pairs"]
    mt5 = candles.connect()
    try:
        data = {p: candles.load_pair(mt5, p + cfg["data"]["symbol_suffix"], off, a.extra_days) for p in a.pairs}
    finally:
        mt5.shutdown()
    DATA.mkdir(exist_ok=True)
    allt = []
    for p, frames in data.items():
        s = run_pair(p, frames, cfg, a.weeks, off, a.sim, not a.no_spread)
        (DATA / f"backtest_{p}{a.tag}.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
        print(f"{p}: {s['decision_points']} decision points, verdicts {s['verdict_counts']}")
        print(f"   signals {s['signals']} ({s['signals_per_week']}/week), closed {s['closed']}, wins {s['wins']}, "
              f"total {s['total_r']}R, average {s['avg_r']}R", flush=True)
        allt += [{**t, "pair": p} for t in s["trades"] if t["result"] in ("win", "loss")]
    if len(data) > 1 and allt:
        print("\nAll pairs together (closed paper trades only):")
        for name, key in (("grade", lambda t: t["grade"]), ("side", lambda t: t["side"]),
                          ("box", lambda t: t["box"].rstrip("0123456789")), ("signal tf", lambda t: t.get("sig_tf", "?")),
                          ("signal", lambda t: t.get("sig_type", "?")), ("4H agrees", lambda t: str(t.get("align_risk"))),
                          ("stop pips", lambda t: "<15" if t.get("stop_pips", 0) < 15 else "15-30" if t["stop_pips"] < 30 else "30+")):
            groups = {}
            for t in allt:
                groups.setdefault(key(t), []).append(t["r"])
            for g, rs in sorted(groups.items()):
                print(f"  by {name} {g:5}: {len(rs):3} trades, {sum(r > 0 for r in rs):3} wins, total {sum(rs):+.1f}R, average {np.mean(rs):+.2f}R")
        rs = [t["r"] for t in allt]
        print(f"  all: {len(rs)} trades, {sum(r > 0 for r in rs)} wins, total {sum(rs):+.1f}R, average {np.mean(rs):+.2f}R over {a.weeks} weeks and {len(data)} pairs")


if __name__ == "__main__":
    main()
