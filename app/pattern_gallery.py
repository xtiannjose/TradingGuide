"""Find head-and-shoulders and double tops/bottoms on real history and draw them for a visual check.

python app/pattern_gallery.py [PAIR ...] [--tf 4H] [--bars 600]

Each candle is tested as if it were the latest closed one (no later candles are used). A pattern
is counted once, at the furthest state it reached: forming, neckline_broken, retest. Valid only
after a body close beyond the neckline (spec 7.2); "forming" never signals. Pictures go to
app/out/patterns/.
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
import structure

OUT = Path(__file__).with_name("out") / "patterns"
RANK = {"forming": 0, "neckline_broken": 1, "retest": 2}


def find(df, k, start, step=2, pp=None):
    """Unique patterns over history: key -> best record, with the candle index where it was seen."""
    best = {}
    for i in range(start, len(df), step):
        for p in signals.patterns(df.iloc[: i + 1], k, None, pp):
            key = (p["type"], tuple(p["points"]))
            if key not in best or RANK[p["state"]] > RANK[best[key]["state"]]:
                best[key] = {**p, "seen": i}
    return best


def draw(df, pats, pair, tf, path, bars=260):
    off = len(df) - bars
    d = df.iloc[off:].reset_index(drop=True)
    x = np.arange(len(d))
    up = (d["close"] >= d["open"]).to_numpy()
    col = np.where(up, "#2962ff", "#ef5350")
    fig, ax = plt.subplots(figsize=(17, 8))
    ax.vlines(x, d["low"], d["high"], color=col, lw=1)
    ax.bar(x, (d["close"] - d["open"]).abs().clip(lower=1e-5), bottom=np.minimum(d["open"], d["close"]), color=col, width=0.7)
    for p in pats:
        pts = [i - off for i in p["points"]]
        if pts[0] < 0:
            continue
        ys = [float(df["close"].iloc[i]) for i in p["points"]]
        ax.plot(pts, ys, color="#e08a00" if p["side"] == "sell" else "#1b8a3a", lw=2)
        ax.hlines(p["neckline"], pts[0], min(pts[-1] + 25, len(d)), colors="#7b1fa2", linestyles="--")
        ax.text(pts[2] if len(pts) > 2 else pts[-1], max(ys) if p["side"] == "sell" else min(ys),
                f"{p['type'].replace('_', ' ')}: {p['state'].replace('_', ' ')}", fontsize=8, ha="center",
                va="bottom" if p["side"] == "sell" else "top")
    ticks = np.linspace(0, len(d) - 1, 9).astype(int)
    ax.set_xticks(ticks, [d["ny"].iloc[t].strftime("%d %b %y") for t in ticks], fontsize=8)
    ax.set_title(f"{pair} {tf}: patterns found (orange sell, green buy, purple dashed neckline)")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=85)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pairs", nargs="*")
    ap.add_argument("--tf", default="4H")
    ap.add_argument("--bars", type=int, default=600)
    a = ap.parse_args()
    cfg = params.load()
    pairs = a.pairs or cfg["pairs"]
    mt5 = candles.connect()
    try:
        data = {p: candles.load_pair(mt5, p + cfg["data"]["symbol_suffix"], cfg["data"]["server_ny_offset_hours"])[a.tf] for p in pairs}
    finally:
        mt5.shutdown()
    k = structure.tf_settings(cfg["structure"], a.tf)[0]
    total = {}
    per = {}
    for p, df in data.items():
        found = find(df, k, len(df) - a.bars, 2, cfg["signal"].get("pattern"))
        per[p] = found
        for rec in found.values():
            key = (rec["type"], rec["state"])
            total[key] = total.get(key, 0) + 1
    print(f"{a.tf}, last {a.bars} candles, {len(pairs)} pairs")
    for (t, s), n in sorted(total.items()):
        print(f"  {t:28} {s:16} {n}")
    for p in sorted(per, key=lambda q: -len(per[q]))[:2]:
        recs = [r for r in per[p].values() if r["state"] != "forming"] or list(per[p].values())
        path = OUT / f"{p}_{a.tf}.png"
        draw(data[p], recs[-6:], p, a.tf, path)
        print("picture:", path)


if __name__ == "__main__":
    main()
