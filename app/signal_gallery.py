"""Draw where the candle signals fire on real history, so the shapes can be judged by eye.

python app/signal_gallery.py GBPUSD [--tf 4H] [--bars 120]

Every candle is tested as if it were the latest closed one (no later candles are used). Buy
shapes are marked below the candle, sell shapes above. Pictures go to app/out/signals/.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import candles
import params
import signals

OUT = Path(__file__).with_name("out") / "signals"
COL = {"rejection": "#e08a00", "hammer": "#e08a00", "shooting_star": "#e08a00", "engulfing": "#1b8a3a",
       "morning_star": "#7b1fa2", "evening_star": "#7b1fa2", "doji": "#888888"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--tf", default="4H")
    ap.add_argument("--bars", type=int, default=120)
    a = ap.parse_args()
    cfg = params.load()
    mt5 = candles.connect()
    try:
        df = candles.load_pair(mt5, a.pair + cfg["data"]["symbol_suffix"], cfg["data"]["server_ny_offset_hours"])[a.tf]
    finally:
        mt5.shutdown()
    pip = 0.01 if a.pair.endswith("JPY") else 0.0001
    sp = cfg["signal"]
    n = len(df)
    start = n - a.bars
    hits = []
    for i in range(start, n):
        part = df.iloc[: i + 1]
        for side in ("buy", "sell"):
            for s in signals.candle_signals(part, side, sp, pip):
                if s["type"] != "doji":
                    hits.append((i, side, s["type"]))
    d = df.iloc[start:].reset_index(drop=True)
    x = np.arange(len(d))
    up = (d["close"] >= d["open"]).to_numpy()
    col = np.where(up, "#2962ff", "#ef5350")
    fig, ax = plt.subplots(figsize=(17, 8))
    ax.vlines(x, d["low"], d["high"], color=col, lw=1)
    ax.bar(x, (d["close"] - d["open"]).abs().clip(lower=pip), bottom=np.minimum(d["open"], d["close"]), color=col, width=0.7)
    rng = (d["high"].max() - d["low"].min())
    for i, side, kind in hits:
        j = i - start
        y = d["low"].iloc[j] - 0.03 * rng if side == "buy" else d["high"].iloc[j] + 0.03 * rng
        ax.scatter(j, y, marker="^" if side == "buy" else "v", color=COL.get(kind, "#000"), s=55, zorder=5)
    handles = [plt.Line2D([], [], marker="s", ls="", color=c, label=k) for k, c in COL.items() if k != "doji"]
    ax.legend(handles=handles, loc="upper left", fontsize=9, ncol=3)
    ticks = np.linspace(0, len(d) - 1, 9).astype(int)
    ax.set_xticks(ticks, [d["ny"].iloc[t].strftime("%d %b %H:%M") for t in ticks], fontsize=8)
    ax.set_title(f"{a.pair} {a.tf}: candle signals found in the last {a.bars} candles (up = buy shape, down = sell shape): {len(hits)}")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{a.pair}_{a.tf}.png"
    fig.savefig(path, dpi=85)
    counts = {}
    for _, side, kind in hits:
        counts[f"{side} {kind}"] = counts.get(f"{side} {kind}", 0) + 1
    print(f"{a.pair} {a.tf}: {len(hits)} signals in {a.bars} candles", counts)
    print(path)


if __name__ == "__main__":
    main()
