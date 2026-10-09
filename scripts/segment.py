"""Clean a watch report's rolling YouTube auto-captions and split them into study parts.

usage:
  python segment.py REPORT.md OUT_DIR [--minutes 50] [--cuts 0:56:08,1:29:13,...]
  python segment.py --chapters VIDEO.info.json        # print chapter start times, then exit

REPORT.md is the stdout of watch.py (see study-video.ps1). Output: OUT_DIR/seg_A.txt, seg_B.txt, ...
Each line is "[H:MM:SS] text". With --cuts, parts split at those times; otherwise every --minutes.
"""
import argparse
import json
import re
import string
import sys
from pathlib import Path

LINE = re.compile(r"^\[(?:(\d+):)?(\d+):(\d+)\]\s?(.*)$")


def parse(report):
    text = Path(report).read_text(encoding="utf-8-sig", errors="replace")
    body = text.split("## Transcript", 1)[1]
    body = body.split("```", 2)[1]
    for raw in body.splitlines():
        m = LINE.match(raw)
        if m:
            h, mi, s, t = m.groups()
            yield int(h or 0) * 3600 + int(mi) * 60 + int(s), t.strip()


def dedup(lines):
    """Rolling captions: each line = tail of the previous one + new words, and the tail repeats alone."""
    prev = ""
    for t, txt in lines:
        if not txt or txt == prev:
            continue
        if prev and txt.startswith(prev):
            new = txt[len(prev):].strip()
            prev = txt
            if new:
                yield t, new
        elif prev and prev.endswith(txt):
            prev = txt
        else:
            prev = txt
            yield t, txt


def paragraphs(items, gap=20):
    start, buf = None, []
    for t, w in items:
        if start is None:
            start = t
        elif t - start >= gap:
            yield start, " ".join(buf)
            start, buf = t, []
        buf.append(w)
    if buf:
        yield start, " ".join(buf)


def stamp(t):
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}"


def to_sec(s):
    parts = [int(x) for x in s.split(":")]
    sec = 0
    for p in parts:
        sec = sec * 60 + p
    return sec


def name(i):
    letters = string.ascii_uppercase
    return letters[i] if i < 26 else letters[i // 26 - 1] + letters[i % 26]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--minutes", type=int, default=50)
    ap.add_argument("--cuts", default="")
    ap.add_argument("--chapters", help="info.json from yt-dlp: print chapters and exit")
    a = ap.parse_args()

    if a.chapters:
        d = json.loads(Path(a.chapters).read_text(encoding="utf-8"))
        for c in d.get("chapters") or []:
            print(stamp(int(c["start_time"])), "|", c["title"])
        return
    if not a.report or not a.out:
        ap.error("REPORT and OUT_DIR are required")

    paras = list(paragraphs(dedup(parse(a.report))))
    end = (paras[-1][0] + 1) if paras else 0
    if a.cuts:
        bounds = [0] + [to_sec(c) for c in a.cuts.split(",") if c.strip()] + [end]
    else:
        step = a.minutes * 60
        bounds = list(range(0, end, step)) + [end]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for i in range(len(bounds) - 1):
        lo, hi = bounds[i], bounds[i + 1]
        rows = [(t, p) for t, p in paras if lo <= t < hi]
        words = sum(len(p.split()) for _, p in rows)
        total += words
        label = f"{stamp(lo)}-{stamp(hi)}"
        with open(out / f"seg_{name(i)}.txt", "w", encoding="utf-8") as f:
            f.write(f"# PART {name(i)}: video time {label}\n"
                    f"# lines are [H:MM:SS] absolute video time; auto-captions, expect mis-heard words\n\n")
            for t, p in rows:
                f.write(f"[{stamp(t)}] {p}\n")
        print(f"seg_{name(i)}: {len(rows)} lines, {words} words, {label}")
    print("total words", total)


if __name__ == "__main__":
    sys.exit(main())
