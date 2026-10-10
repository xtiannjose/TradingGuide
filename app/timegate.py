"""Module A: the time gate (docs/ANALYSIS-SPEC.md section 3). All rules run on New York time."""
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")


def hm(s):
    h, m = s.split(":")
    return time(int(h), int(m))


_hm = hm


def next_window(now_ny, tp):
    """Start of the next entry window on an allowed weekday, strictly after now."""
    start = _hm(tp["window_start"])
    for i in range(8):
        cand = datetime.combine(now_ny.date() + timedelta(days=i), start, tzinfo=NY)
        if cand > now_ny and cand.weekday() in tp["days"]:
            return cand


def time_gate(now_ny, tp):
    """T2 window and T3 weekdays. reason is 'weekday', 'time' or None."""
    day_ok = now_ny.weekday() in tp["days"]
    in_window = _hm(tp["window_start"]) <= now_ny.time() <= _hm(tp["window_end"])
    if day_ok and in_window:
        return {"pass": True, "reason": None, "next_window": None}
    return {"pass": False, "reason": "time" if day_ok else "weekday",
            "next_window": next_window(now_ny, tp).isoformat()}


def market_open(now_ny):
    """Forex trades from Sunday 17:00 to Friday 17:00 New York."""
    wd, h = now_ny.weekday(), now_ny.hour
    return not (wd == 5 or (wd == 4 and h >= 17) or (wd == 6 and h < 17))


def last_sunday_open(now_ny):
    """The most recent Sunday 17:00 New York, as a naive New York wall-clock datetime."""
    d = now_ny.date() - timedelta(days=(now_ny.weekday() + 1) % 7)
    t = datetime.combine(d, time(17, 0))
    if t > now_ny.replace(tzinfo=None):
        t -= timedelta(days=7)
    return t
