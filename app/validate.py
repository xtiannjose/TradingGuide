"""Phase 8 checks on the last scan (app/data/analysis): rule invariants and the owner's answer key.

python app/validate.py

1. Invariants: every box is 5 to 60 pips, has 3 or more touches, sits inside its timeframe's
   zone, and the verdict is consistent with its checklist. No human eye needed.
2. Answer key: for each [[reference]] box in settings.toml, which of the app's boxes overlap it
   (share of the owner's box covered, and how tall the app's box is). A match is a tuning
   signal, never an input: the app never reads the reference boxes.
"""
import json
from pathlib import Path

import params

DATA = Path(__file__).with_name("data") / "analysis"


def invariants(a):
    """List of broken rules for one pair's analysis."""
    bad, pip = [], a["pip"]
    for b in a["aois"]:
        if not (5 - 1e-6 <= b["pips"] <= 60 + 1e-6):
            bad.append(f"{b['id']} is {b['pips']:.1f} pips")
        if b["touches"] < 3 and b["tf"] != "W+D":
            bad.append(f"{b['id']} has {b['touches']} touches")
        tf = "D" if b["tf"] == "W+D" else b["tf"]
        z = a["tf"].get(tf, {}).get("zone")
        if z and (b["low"] < z["low"] - pip or b["high"] > z["high"] + pip):
            bad.append(f"{b['id']} sticks out of the {tf} zone")
    v, r = a["verdict"], a["reason"]
    if v == "SIGNAL" and not all(c["pass"] for c in a["checklist"] if c["item"] != "4H agrees (extra)"):
        bad.append("SIGNAL with a failed checklist item")
    if v == "NO_TRADE" and not r:
        bad.append("NO_TRADE without a reason")
    if a["alignment"]["pass"] and a["tf"]["W"]["state"] != a["tf"]["D"]["state"]:
        bad.append("aligned but weekly and daily differ")
    return bad


def overlap(ref, b):
    lo, hi = max(ref["low"], b["low"]), min(ref["high"], b["high"])
    return max(hi - lo, 0) / (ref["high"] - ref["low"])


def main():
    cfg = params.load(user=False)
    files = sorted(DATA.glob("*.json"))
    if not files:
        raise SystemExit("No scan yet. Run: python app/scan.py")
    broken = 0
    for f in files:
        a = json.loads(f.read_text(encoding="utf-8"))
        bad = invariants(a)
        broken += len(bad)
        if bad:
            print(f"{a['pair']}: " + "; ".join(bad))
    print(f"Invariants over {len(files)} pairs: {broken} violation(s)\n")
    print("Answer key (your daily boxes) against the app's boxes:")
    for ref in cfg.get("reference", []):
        p = DATA / f"{ref['pair']}.json"
        if not p.exists():
            continue
        a = json.loads(p.read_text(encoding="utf-8"))
        pip = a["pip"]
        print(f"  {ref['pair']} {ref['tf']} {ref['low']} - {ref['high']} ({(ref['high'] - ref['low']) / pip:.0f} pips)")
        hits = sorted(((overlap(ref, b), b) for b in a["aois"]), key=lambda x: -x[0])
        hits = [h for h in hits if h[0] > 0]
        if not hits:
            print("     no app box touches it")
        for cov, b in hits[:4]:
            print(f"     {b['id']:5} {b['tf']:4} {b['low']:.5g} - {b['high']:.5g} ({b['pips']:.0f}p, {b['touches']} touches"
                  f"{', flagged broken' if b['broken'] else ''}) covers {cov:.0%} of your box")
        print(f"     price {a['price']:.5g}, verdict {a['verdict']}")


if __name__ == "__main__":
    main()
