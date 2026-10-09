"""Run from the repo root: python -m pytest app"""
from datetime import datetime

import pandas as pd

import candles as c


def rates(stamps, **cols):
    """MT5-like rates. Stamps are broker wall-clock; MT5 stores them as if they were UTC."""
    n = len(stamps)
    t = [int(pd.Timestamp(s, tz="UTC").timestamp()) for s in stamps]
    base = {"time": t, "open": [1.0] * n, "high": [1.0] * n, "low": [1.0] * n,
            "close": [1.0] * n, "tick_volume": [1] * n}
    base.update(cols)
    return pd.DataFrame(base)


def test_broker_midnight_is_5pm_new_york_in_summer_and_winter():
    f = c.to_frame(rates(["2026-07-14 00:00", "2026-01-13 00:00"]), 7)
    assert [(x.hour, x.day, x.month) for x in f["ny"]] == [(17, 13, 7), (17, 12, 1)]
    assert [x.hour for x in f["time"]] == [21, 22]  # EDT is UTC-4, EST is UTC-5


def test_forming_candle_is_dropped():
    f = c.to_frame(rates(["2026-07-14 00:00", "2026-07-15 00:00"]), 7)
    # first daily candle ends 2026-07-14 17:00 New York, second ends a day later
    assert len(c.closed_only(f, 1440, now=datetime(2026, 7, 14, 17, 0))) == 1
    assert len(c.closed_only(f, 1440, now=datetime(2026, 7, 14, 16, 59))) == 0


def test_weekly_runs_sunday_5pm_to_friday_5pm_new_york():
    days = ["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10",  # cut-off first week
            "2026-07-13", "2026-07-14", "2026-07-15", "2026-07-16", "2026-07-17",  # the week under test
            "2026-07-20", "2026-07-21"]                                            # still running
    n = len(days)
    d = c.to_frame(rates([f"{x} 00:00" for x in days],
                         open=list(range(n)), close=[i + 0.5 for i in range(n)],
                         high=[i + 1 for i in range(n)], low=[i - 1 for i in range(n)]), 7)
    w = c.closed_only(c.weekly_from_daily(d, 7), c.WEEK_MINUTES, now=datetime(2026, 7, 18, 12, 0))
    assert len(w) == 1
    row = w.iloc[0]
    assert (row["open"], row["close"], row["high"], row["low"]) == (5, 9.5, 10, 4)
    assert (row["ny"].weekday(), row["ny"].hour) == (6, 17)  # Sunday 5 PM
