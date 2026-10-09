"""Phase 1: read the structure of a pair and draw it.

python app/chart.py [SYMBOL] [--tf W,D,4H] [--asof 2025-09-19] [--k 0.5] [--trail]
python app/chart.py [SYMBOL] --compare [--tf W,D]     four readings side by side

Needs MT5 open and logged in. Pictures go to app/out/ (not committed). Candles are blue
up and red down, as in the course; orange is the 50 EMA; grey dotted is the swing path.
"""
import argparse
from datetime import datetime, time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import candles
import structure

OUT = Path(__file__).with_name("out")
SHOW = {"W": 160, "D": 260, "4H": 320, "2H": 320, "1H": 320, "30m": 320, "15m": 320}  # candles drawn
MINUTES = {k: v[1] for k, v in candles.TF.items()} | {"W": candles.WEEK_MINUTES}
COLORS = {"HH": "#1b8a3a", "HL": "#1b8a3a", "LH": "#c62828", "LL": "#c62828"}
# (label, swing threshold in ATR, trail the paired level to the latest swing)
VARIANTS = [
    ("A  course rule, swings 0.5 ATR (the app today)", 0.5, False),
    ("B  latest swing trails, swings 0.5 ATR", 0.5, True),
    ("C  course rule, finer swings 0.35 ATR", 0.35, False),
    ("D  latest swing trails, finer swings 0.35 ATR", 0.35, True),
]


def plot(ax, df, res, bars, title):
    off = max(len(df) - bars, 0)
    d = df.iloc[off:].reset_index(drop=True)
    x = np.arange(len(d))
    up = (d["close"] >= d["open"]).to_numpy()
    col = np.where(up, "#2962ff", "#ef5350")
    ax.vlines(x, d["low"], d["high"], color=col, lw=1)
    body = (d["close"] - d["open"]).abs()
    ax.bar(x, body.clip(lower=body.median() * 0.05), bottom=np.minimum(d["open"], d["close"]), color=col, width=0.7)
    ema = df["close"].ewm(span=50, adjust=False).mean().iloc[off:]
    ax.plot(x, ema.to_numpy(), color="orange", lw=1.2)

    raw = res["raw"]
    pts = [(i - off, p) for i, p, _ in raw["pivots"] if i >= off]
    if raw["leg"][0] != 0 and raw["leg"][1] >= off:
        pts.append((raw["leg"][1] - off, raw["leg"][2]))
    if len(pts) > 1:
        ax.plot(*zip(*pts), color="grey", lw=1, ls=":", marker="o", ms=3)

    for name in ("HH", "HL", "LH", "LL"):
        lvl = res.get(name)
        if lvl:
            x0 = max(lvl["i"] - off, 0)
            ax.hlines(lvl["price"], x0, len(d) - 1, colors=COLORS[name], lw=1.4)
            ax.text(len(d) - 1, lvl["price"], f" {name} {lvl['price']:.5g}", color=COLORS[name], va="center", fontsize=9)
    for e in raw["events"]:
        if e["flip"] and e["i"] >= off:
            ax.annotate("▲" if e["state"] == "bull" else "▼", (e["i"] - off, d["close"].iloc[e["i"] - off]),
                        ha="center", fontsize=10, color="black")

    ticks = np.linspace(0, len(d) - 1, 7).astype(int)
    ax.set_xticks(ticks, [d["ny"].iloc[t].strftime("%d %b %y") for t in ticks], fontsize=8)
    ax.set_xlim(-1, len(d) + 14)
    ax.set_title(title, fontsize=10)
    ax.grid(alpha=0.25)


def draw(df, res, title, path, bars):
    fig, ax = plt.subplots(figsize=(15, 7))
    plot(ax, df, res, bars, title)
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


def compare(df, symbol, tf, path, bars):
    fig, axes = plt.subplots(2, 2, figsize=(17, 10))
    for ax, (label, k, trail) in zip(axes.flat, VARIANTS):
        res = structure.read(df, k, trail)
        if res["state"]:
            a, b = ("HH", "HL") if res["state"] == "bullish" else ("LL", "LH")
            head = f"{res['state']}: {a} {res[a]['price']:.5g}, {b} {res[b]['price']:.5g}"
        else:
            head = "no structure yet"
        plot(ax, df, res, bars, f"{label}\n{head}")
    fig.suptitle(f"{symbol} {tf}: the same candles, four readings", fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=90)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("symbol", nargs="?", default="EURUSD")
    ap.add_argument("--tf", default="W,D,4H")
    ap.add_argument("--asof", help="New York date or datetime; a date means that day's 17:00 close")
    ap.add_argument("--k", type=float)
    ap.add_argument("--trail", action="store_true", help="paired level follows the latest swing")
    ap.add_argument("--compare", action="store_true", help="draw four readings side by side")
    a = ap.parse_args()

    cfg = candles.settings()
    k = a.k or cfg["structure"]["swing_atr"]
    now = None
    if a.asof:
        now = datetime.fromisoformat(a.asof)
        if len(a.asof) <= 10:
            now = datetime.combine(now.date(), time(17, 0))
    extra = (datetime.now() - now).days + 10 if now else 0
    symbol = a.symbol + cfg["data"]["symbol_suffix"]

    mt5 = candles.connect()
    try:
        data = candles.load_pair(mt5, symbol, cfg["data"]["server_ny_offset_hours"], extra)
    finally:
        mt5.shutdown()

    OUT.mkdir(exist_ok=True)
    tag = f" as of {now:%Y-%m-%d %H:%M} NY" if now else ""
    if a.compare:
        folder = OUT / "compare"
        folder.mkdir(exist_ok=True)
        for tf in a.tf.split(","):
            df = candles.closed_only(data[tf], MINUTES[tf], now=now) if now else data[tf]
            compare(df, symbol, tf, folder / f"{a.symbol}_{tf}.png", 130)
            print(f"{symbol} {tf}:")
            for label, kk, trail in VARIANTS:
                r = structure.read(df, kk, trail)
                if r["state"]:
                    n1, n2 = ("HH", "HL") if r["state"] == "bullish" else ("LL", "LH")
                    print(f"  {label[0]}: {r['state']:8} {n1} {r[n1]['price']:.5g} ({r[n1]['time']:%d %b}) "
                          f"{n2} {r[n2]['price']:.5g} ({r[n2]['time']:%d %b})")
        print(f"Pictures in {folder}")
        return

    print(f"{symbol}{tag}, swing = {k} x ATR(14){', latest swing trails' if a.trail else ''}")
    for tf in a.tf.split(","):
        df = candles.closed_only(data[tf], MINUTES[tf], now=now) if now else data[tf]
        res = structure.read(df, k, a.trail)
        if not res["state"]:
            print(f"  {tf:>3}: no structure yet")
            continue
        hh, hl = ("HH", "HL") if res["state"] == "bullish" else ("LL", "LH")
        ext, pair = res[hh], res[hl]
        conf = "confirmed" if res["ext_confirmed"] else "current"
        print(f"  {tf:>3}: {res['state']:8} {hh} {ext['price']:.5g} ({ext['time']:%d %b %y}, {conf})"
              f"  {hl} {pair['price']:.5g} ({pair['time']:%d %b %y})  last flip {res['last_flip']:%d %b %y}")
        png = OUT / f"{a.symbol}_{tf}{'_' + a.asof if a.asof else ''}.png"
        draw(df, res, f"{symbol} {tf}{tag}: {res['state']}", png, SHOW[tf])
    print(f"Pictures in {OUT}")


if __name__ == "__main__":
    main()
