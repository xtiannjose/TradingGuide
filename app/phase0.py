"""Phase 0 check: pair names, seven timeframes, and the New York 5 PM boundary.

Run from the repo root with MT5 open and logged in:  python app/phase0.py [SYMBOL]
"""
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

import candles


def missing_names(mt5, pairs, suffix):
    """pair -> broker symbols that contain it, for every pair the broker does not list under that name."""
    out = {}
    for p in pairs:
        if mt5.symbol_info(p + suffix) is None:
            out[p] = [s.name for s in (mt5.symbols_get(f"*{p}*") or [])]
    return out


def live_offset(mt5, symbol, now_ny):
    """Broker clock minus New York clock (hours) from the latest tick, and which case was used.

    Market open: the tick is current, so compare it with the New York clock now.
    Market closed: the last tick is the weekly close, Friday 17:00 New York.
    Returns (None, reason) when the tick does not sit near a whole-hour offset.
    """
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None, "no tick"
    broker = datetime.fromtimestamp(tick.time, timezone.utc).replace(tzinfo=None)
    wall = now_ny.replace(tzinfo=None)
    wd, h = now_ny.weekday(), now_ny.hour
    closed = wd == 5 or (wd == 4 and h >= 17) or (wd == 6 and h < 17)
    if closed:
        ref = (wall - timedelta(days=(wd - 4) % 7)).replace(hour=17, minute=0, second=0, microsecond=0)
    else:
        ref = wall
    diff = (broker - ref).total_seconds() / 3600
    if abs(diff - round(diff)) > 0.25:  # a holiday close or a stale quote
        return None, "tick is not close enough to the expected time"
    return round(diff), "last tick vs Friday 17:00 close" if closed else "live tick"


def week_edges(h1, offset_h):
    """Weeks whose first hourly candle opens Sunday 5 PM and last opens Friday 4 PM New York."""
    wall = h1["ny"].dt.tz_localize(None)
    g = wall.groupby((wall + pd.Timedelta(hours=offset_h)).dt.to_period("W"))
    first, last = g.min(), g.max()
    ok = [(a.weekday(), a.hour, b.weekday(), b.hour) == (6, 17, 4, 16) for a, b in zip(first, last)]
    return sum(ok), len(ok)


def main():
    cfg = candles.settings()
    offset, suffix, tz = cfg["data"]["server_ny_offset_hours"], cfg["data"]["symbol_suffix"], ZoneInfo(cfg["display_tz"])
    symbol = (sys.argv[1] if len(sys.argv) > 1 else "EURUSD") + suffix
    mt5 = candles.connect()
    try:
        bad = []
        missing = missing_names(mt5, cfg["pairs"], suffix)
        print(f"Pairs: {len(cfg['pairs']) - len(missing)} of {len(cfg['pairs'])} found with suffix '{suffix}'")
        for p, alts in missing.items():
            print(f"  missing {p}: broker has {alts or 'nothing like it'}")
        if missing:
            bad.append("pair names")

        data = candles.load_pair(mt5, symbol, offset)
        print(f"\n{symbol}, closed candles ({datetime.now(ZoneInfo('America/New_York')):%Y-%m-%d %H:%M} New York now)")
        for name, df in data.items():
            if df.empty:
                bad.append(f"{name} empty")
                print(f"  {name:>3}: no candles")
                continue
            a, z = df["ny"].iloc[0], df["ny"].iloc[-1]
            print(f"  {name:>3}: {len(df):5d} bars, {a:%Y-%m-%d} to {z:%Y-%m-%d %H:%M} NY (last opened {z.astimezone(tz):%H:%M} Manila)")

        d = data["D"]
        at5 = int(((d["ny"].dt.hour == 17) & (d["ny"].dt.minute == 0)).sum())
        print(f"\nDaily candles opening at 17:00 New York: {at5} of {len(d)}")
        if at5 != len(d):
            bad.append("daily boundary")
        w = data["W"]
        w5 = int((w["ny"].dt.hour == 17).sum())
        sun5 = int(((w["ny"].dt.weekday == 6) & (w["ny"].dt.hour == 17)).sum())
        print(f"Weekly candles opening at 17:00 New York: {w5} of {len(w)}, on a Sunday: {sun5} (holiday weeks open another day)")
        if w5 != len(w) or sun5 < 0.98 * len(w):
            bad.append("weekly boundary")
        ok, n = week_edges(data["1H"], offset)
        print(f"Weeks opening Sun 17:00 and last 1H candle Fri 16:00 New York (holiday weeks may differ): {ok} of {n}")
        if ok < 0.8 * n:
            bad.append("week edges")

        est, how = live_offset(mt5, symbol, datetime.now(ZoneInfo("America/New_York")))
        if est is None:
            print(f"Tick check: inconclusive ({how}); the candle checks above still stand")
        else:
            print(f"Tick check ({how}): broker clock is New York + {est} h (setting: {offset})")
            if est != offset:
                bad.append("server offset")

        print("\nPHASE 0 " + ("PASS" if not bad else "FAIL: " + ", ".join(bad)))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
