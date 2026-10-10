"""Run the analysis for pairs and write app/data/*.json for the UI (phases 5 and 6).

python app/scan.py                  all pairs in settings.toml
python app/scan.py GBPUSD AUDJPY    some pairs
python app/scan.py --scheduled      only runs inside the planned run windows (for Task Scheduler)

Needs MT5 open and logged in. Output is analysis for you to judge; it places no orders.
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

import candles
import params
import verdict

DATA = Path(__file__).with_name("data")
NY = ZoneInfo("America/New_York")
KEEP = {"W": 260, "D": 700, "4H": 1000, "2H": 800, "1H": 900, "30m": 1000, "15m": 1200}
EPOCH = pd.Timestamp("1970-01-01")


def account_for(mt5, symbol, cfg):
    """Broker pip value in the account currency, balance and lot limits. None if unavailable."""
    info, acc = mt5.symbol_info(symbol), mt5.account_info()
    if info is None or acc is None or not info.trade_tick_value:
        return None
    pip = 0.01 if info.currency_profit == "JPY" else 0.0001
    return {
        "balance": cfg["account"]["balance"] or float(acc.balance),
        "currency": acc.currency,
        "pip_value": float(info.trade_tick_value * pip / info.trade_tick_size),
        "step": float(info.volume_step), "min_lot": float(info.volume_min), "max_lot": float(info.volume_max),
    }


def candle_json(df, tf, offset_h, digits):
    d = df.tail(KEEP[tf])
    t = ((d["ny"].dt.tz_localize(None) + pd.Timedelta(hours=offset_h)) - EPOCH) // pd.Timedelta(seconds=1)
    ema = df["close"].ewm(span=50, adjust=False).mean().tail(KEEP[tf])
    return {
        "tf": tf,
        "bars": [[int(a), round(float(o), digits), round(float(h), digits), round(float(l), digits),
                  round(float(c), digits)] for a, o, h, l, c in zip(t, d["open"], d["high"], d["low"], d["close"])],
        "ema": [[int(a), round(float(v), digits)] for a, v in zip(t, ema)],
    }


def scan_pair(mt5, pair, cfg, now_ny=None):
    """Load, analyse and write one pair. Returns its summary row."""
    now_ny = now_ny or datetime.now(NY)
    off = cfg["data"]["server_ny_offset_hours"]
    sym = pair + cfg["data"]["symbol_suffix"]
    frames = candles.load_pair(mt5, sym, off)
    tick = mt5.symbol_info_tick(sym)
    price = float(tick.bid) if tick is not None and tick.bid else None
    acct = account_for(mt5, sym, cfg)
    out = verdict.analyze(pair, frames, now_ny, cfg, acct, price, off)
    out["account"] = {k: v for k, v in (acct or {}).items() if k in ("currency", "pip_value", "min_lot", "step", "balance")}
    digits = 3 if pair.endswith("JPY") else 5
    (DATA / "analysis").mkdir(parents=True, exist_ok=True)
    (DATA / "candles").mkdir(parents=True, exist_ok=True)
    (DATA / "analysis" / f"{pair}.json").write_text(json.dumps(out), encoding="utf-8")
    for tf in candles.ORDER:
        (DATA / "candles" / f"{pair}_{tf}.json").write_text(
            json.dumps(candle_json(frames[tf], tf, off, digits)), encoding="utf-8")
    return summary_row(out)


def summary_row(a):
    near = min((b for b in a["aois"] if not b["broken"]), key=lambda b: b["dist_pips"], default=None)
    return {
        "pair": a["pair"], "verdict": a["verdict"], "reason": a["reason"], "grade": a["grade"],
        "bias": a["alignment"]["direction"], "risk": a["alignment"]["risk"],
        "states": {tf: a["tf"].get(tf, {}).get("state") for tf in ("W", "D", "4H")},
        "price": a["price"], "awaiting": a["awaiting"], "asof": a["asof_ny"],
        "nearest": {"id": near["id"], "tf": near["tf"], "low": near["low"], "high": near["high"],
                    "role": near["role"], "dist_pips": near["dist_pips"]} if near else None,
    }


def scan_all(mt5, pairs, cfg, progress=None):
    rows = []
    for n, pair in enumerate(pairs, 1):
        if progress:
            progress(pair, n, len(pairs))
        try:
            rows.append(scan_pair(mt5, pair, cfg))
        except Exception as e:  # one broken pair must not stop the run
            rows.append({"pair": pair, "verdict": "ERROR", "reason": str(e)[:160]})
    write_summary(rows)
    return rows


def write_summary(rows):
    """Merge rows into summary.json so a partial scan keeps the other pairs."""
    path = DATA / "summary.json"
    cur = {}
    if path.exists():
        try:
            cur = {r["pair"]: r for r in json.loads(path.read_text(encoding="utf-8"))["pairs"]}
        except (ValueError, KeyError):
            cur = {}
    for r in rows:
        cur[r["pair"]] = r
    DATA.mkdir(exist_ok=True)
    path.write_text(json.dumps({"updated": datetime.now(NY).isoformat(), "pairs": list(cur.values())}),
                    encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pairs", nargs="*")
    ap.add_argument("--scheduled", action="store_true",
                    help="exit unless it is 12:30 to 12:59 AM New York Mon-Wed or Sunday 17:00 to 17:29")
    a = ap.parse_args()
    cfg = params.load()
    if a.scheduled:
        n = datetime.now(NY)
        ok = (n.weekday() in (0, 1, 2) and n.hour == 0 and n.minute >= 30) or \
             (n.weekday() == 6 and n.hour == 17 and n.minute < 30)
        if not ok:
            print("Outside the run windows; nothing to do.")
            return
    pairs = a.pairs or cfg["pairs"]
    mt5 = candles.connect()
    try:
        t0 = time.time()
        rows = scan_all(mt5, pairs, cfg, lambda p, i, n: print(f"[{i}/{n}] {p}", flush=True))
    finally:
        mt5.shutdown()
    for r in rows:
        print(f"{r['pair']:8} {r['verdict']:17} {r.get('reason') or '':22} {r.get('grade') or '':2} "
              f"{(r.get('bias') or '-'):8} {r.get('awaiting', '')[:70]}")
    print(f"Done in {time.time() - t0:.0f}s. Data in {DATA}")


if __name__ == "__main__":
    main()
