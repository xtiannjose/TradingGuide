"""Every tunable number in one place (docs/ANALYSIS-SPEC.md section 10).

Precedence: built-in defaults, then app/settings.toml, then app/data/user.json (written by
the UI settings panel). These are numbers, not rule switches: each value changes only the
number it names. The exception is structure.trail, the owner's open choice (spec 4.2).
"""
import copy
import json
from pathlib import Path

import candles

USER = Path(__file__).with_name("data") / "user.json"

DEFAULTS = {
    "pairs": [],
    "display_tz": "Asia/Manila",
    "structure": {"swing_atr": 0.5, "trail": False},
    "aoi": {
        "cluster_pips": 35,      # tightest cluster of >= min_touches swing points must fit here
        "max_pips": 60,          # hard ceiling (course)
        "min_pips": 5,           # hard floor (course)
        "min_touches": 3,        # course
        "max_count": 3,          # per timeframe (course: one, maybe two, max three)
        "touch_gap": 3,          # candles between two counted touches
        "at_aoi_frac": 0.25,     # price counts as "at" the box widened by this share of its height
        "at_aoi_min_pips": 5,
        "round_prox_pips": 10,
        "ema_prox_pips": 15,
        "include_4h": True,      # minor 4H boxes (videos 9 and 10)
        "lookback": {"W": 312, "D": 520, "4H": 1560},   # candles: 6 years, 2 years, 12 months
    },
    "signal": {
        "doji_body": 0.10,
        "rej_body": 0.30,
        "retest_window": 20,
        "entry_tfs": ["D", "4H", "2H", "1H", "30m", "15m"],
        "pattern_tf": "4H",
    },
    "plan": {"stop_buffer_pips": 7, "rr_min": 2.0, "rr_cap": 4.0, "target_tfs": ["D", "4H"]},
    "time": {"window_start": "01:00", "window_end": "10:30", "days": [0, 1, 2]},
    "account": {"risk_pct": 1.0, "balance": None},
    "ui": {"candles": "course"},   # "course" = blue up, red down; "classic" = green up, red down
    "alert": [],
    "reference": [],               # the owner's own boxes, drawn dashed on the chart
}


def merge(base, extra):
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            merge(base[k], v)
        else:
            base[k] = v
    return base


def load(user=True):
    toml = candles.settings()
    cfg = merge(copy.deepcopy(DEFAULTS), toml)
    if "risk_pct" in toml:
        cfg["account"]["risk_pct"] = toml["risk_pct"]
    if user and USER.exists():
        try:
            merge(cfg, json.loads(USER.read_text(encoding="utf-8")))
        except (ValueError, OSError):
            pass  # a broken user file must not stop the app; defaults apply
    return cfg


def save_user(update):
    """Merge `update` into app/data/user.json and return the new full config."""
    USER.parent.mkdir(exist_ok=True)
    cur = {}
    if USER.exists():
        try:
            cur = json.loads(USER.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            cur = {}
    merge(cur, update)
    USER.write_text(json.dumps(cur, indent=2), encoding="utf-8")
    return load()
