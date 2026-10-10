# Reference AOIs (answer key)

Hand-drawn by the owner on 2026-10-10 on MT5 demo daily charts, before any app output exists. They are the answer key for phase 3 (AOI finder). Do not edit them after seeing the app's boxes. The app never reads this file as input; it only compares against it.

Format: `pair | timeframe | AOI low - high | touches | drawn date`

```
GBPUSD | Daily | AOI 1.31598 - 1.32199 | 3+ touches | drawn 2026-10-10
AUDUSD | Daily | AOI 0.70890 - 0.71255 | 3+ touches | drawn 2026-10-10
AUDJPY | Daily | AOI 110.002 - 110.580 | 3+ touches | drawn 2026-10-10
```

## Notes

| Pair | Height | Note |
|---|---|---|
| GBPUSD | 60.1 pips | 0.1 pip over the 60-pip cap. Kept as drawn. Score it with a 1 pip tolerance. |
| AUDUSD | 36.5 pips | Valid. Price broke down through it in mid-September, so it now sits above price as resistance. |
| AUDJPY | 57.8 pips | Valid. JPY pairs: 0.01 = 1 pip. An earlier draft (109.561 - 110.419, 85.8 pips) was over the cap and was redrawn. |

Touch counts are the owner's rough count ("3 or more"), not an exact number. The key holds daily boxes only; the ideas below are Claude's draft.

## Claude's draft ideas (not the answer key)

Snapshot of 2026-10-10 (version 2, tight), made from MT5 candles. Touches are the swing points the structure module finds (a reversal of 0.5 x ATR on closes). A box is the **tightest cluster of at least 3 swing points that fits in 35 pips**, the top of the course's 20 to 35 pip sweet spot ("the tighter the better and the more respected it's going to be"; never stretch a box to collect touches; video 1 part H). Boxes sit inside the zone of their timeframe (weekly: last 6 years, daily: last 2 years). Up to the 3 boxes nearest to price are listed per timeframe, plus any box that overlaps your own.

Version 1 used a 60-pip cap and gave 48 to 60 pip boxes; those were too loose and were replaced.

This is a rough first version of what the AOI finder (phase 3) will do, so it is **kept apart from your key**: the app is never graded against its own output. If you agree with a box, move it into the key above; if not, strike it out. Pictures: `app/out/ideas/` (local, not in the repository).

"Confluences" lists what else sits at the box. Distances are from the last price. The state line is a hand reading of the core rules (`docs/ANALYSIS-SPEC.md` section 5), not app output, and uses the course-rule structure reading (option A in `docs/NEXT-STEPS.md`).

### GBPUSD (price 1.3233)

Weekly bearish, daily bullish, 4H bearish. Weekly and daily disagree, so under the core rules this is `NO_TRADE(counter_trend)`.

| Timeframe | Box | Pips | Touches | Role | Confluences |
|---|---|---|---|---|---|
| Weekly | 1.3324 - 1.3341 | 17 | 3 | resistance, 100 pips up | round number 1.335 |
| Weekly | 1.3371 - 1.3394 | 23 | 3 | resistance, 150 pips up | weekly 50 EMA 1.3381; daily 50 EMA 1.3374; round number 1.34 |
| Weekly | 1.3434 - 1.3454 | 20 | 4 | resistance, 212 pips up | round number 1.345 |
| Daily | 1.3242 - 1.3275 | 33 | 7 | resistance, 26 pips up | round number 1.325 |
| Daily | 1.3197 - 1.3220 | 23 | 6 | support, 24 pips below | overlaps your daily box (it is the tight core of it); round number 1.32 |

### AUDUSD (price 0.69842)

Weekly bullish, daily bearish, 4H bullish. Daily against weekly, so `NO_TRADE(counter_trend)`.

| Timeframe | Box | Pips | Touches | Role | Confluences |
|---|---|---|---|---|---|
| Weekly | 0.68745 - 0.69007 | 26 | 3 | support, 97 pips below | round number 0.69 |
| Weekly | 0.69956 - 0.70278 | 32 | 3 | resistance, 27 pips up | round number 0.70 |
| Weekly | 0.71082 - 0.71402 | 32 | 4 | resistance, 140 pips up | overlaps your daily box; round number 0.71 |
| Daily | 0.69306 - 0.69567 | 26 | 6 | support, 41 pips below | weekly 50 EMA 0.69436; round number 0.695 |
| Daily | 0.70004 - 0.70333 | 33 | 8 | resistance, 33 pips up | round number 0.70 |
| Daily | 0.70568 - 0.70869 | 30 | 5 | resistance, 88 pips up | round number 0.705 |
| Daily | 0.70997 - 0.71241 | 24 | 5 | resistance, 128 pips up | overlaps your daily box (the tight core of it); round number 0.71 |

### AUDJPY (price 110.65)

Weekly bearish, daily bearish, 4H bullish. Weekly and daily agree, and the 4H is against them (a pullback, "mid risk"). Under the core rules the idea is to wait for a sell at resistance, so the boxes above price matter most.

| Timeframe | Box | Pips | Touches | Role | Confluences |
|---|---|---|---|---|---|
| Weekly | 109.86 - 110.17 | 31 | 3 | support, 63 pips below | overlaps your daily box; round number 110 |
| Weekly | 111.53 - 111.83 | 31 | 3 | resistance, 103 pips up | round number 111.5 |
| Daily | 109.68 - 109.84 | 17 | 3 | support, 89 pips below | none |
| Daily | 110.14 - 110.48 | 34 | 4 | support, 34 pips below | overlaps your daily box; round number 110.5 |

Note: the daily resistance near 111.5 to 112.0 that version 1 listed (LH 112.02) does not appear here: its swing points do not fit inside 35 pips with 3 touches.
