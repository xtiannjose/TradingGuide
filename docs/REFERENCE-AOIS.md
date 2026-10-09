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

Touch counts are the owner's rough count ("3 or more"), not an exact number. The key holds daily boxes only; the weekly ideas below are Claude's draft.

## Claude's draft ideas (not the answer key)

Snapshot of 2026-10-10, made from MT5 candles. Touches are the swing points the structure module finds (a reversal of 0.5 x ATR on closes), boxes are at most 60 pips tall and must sit inside the zone of their timeframe (weekly: last 6 years, daily: last 2 years). This is a rough first version of what the AOI finder (phase 3) will do, so it is **kept apart from your key**: the app is never graded against its own output. If you agree with a box, move it into the key above; if not, strike it out.

"Confluences" lists what else sits at the box. Distances are from the last price. The verdict line is a hand reading of the core rules (`docs/ANALYSIS-SPEC.md` section 5), not app output.

### GBPUSD (price 1.3233)

Weekly bearish, daily bullish, 4H bearish. Weekly and daily disagree, so under the core rules this is `NO_TRADE(counter_trend)`. Weekly 50 EMA is 1.3381, daily 1.3374.

| Timeframe | Box | Pips | Touches | Role | Confluences |
|---|---|---|---|---|---|
| Daily | 1.3197 - 1.3248 | 51 | 9 | price is inside it | overlaps your daily box; round number 1.32 |
| Weekly | 1.3324 - 1.3376 | 51 | 5 | resistance, 117 pips up | round number 1.335; daily 50 EMA inside it (1.3374), weekly 50 EMA just above (1.3381) |
| Weekly | 1.3394 - 1.3454 | 60 | 5 | resistance, 192 pips up | round number 1.34 |
| Weekly | 1.3592 - 1.3640 | 48 | 4 | resistance, 384 pips up | round number 1.36; it holds the weekly lower high |

Note: your daily box (1.31598 - 1.32199) reaches below the daily zone's low of 1.3197. By the strict rule the part under 1.3197 is outside the zone. The daily structure only flipped bullish on 5 Oct inside a narrow range, so this may settle in a few days.

### AUDUSD (price 0.69842)

Weekly bullish, daily bearish, 4H bullish. Daily against weekly, so `NO_TRADE(counter_trend)`. Weekly 50 EMA is 0.6944, daily 0.7055.

| Timeframe | Box | Pips | Touches | Role | Confluences |
|---|---|---|---|---|---|
| Daily | 0.69306 - 0.69828 | 52 | 8 | support, 28 pips below | weekly 50 EMA (0.6944); round number 0.695 |
| Daily | 0.69966 - 0.70486 | 52 | 11 | resistance, 38 pips up | round number 0.70 |
| Daily | 0.70706 - 0.71241 | 53 | 9 | resistance, 113 pips up | overlaps your daily box; round number 0.71 |
| Weekly | 0.68651 - 0.69007 | 36 | 4 | support, 101 pips below | round number 0.69; it holds the weekly higher low |
| Weekly | 0.69956 - 0.70278 | 32 | 3 | resistance, 27 pips up | round number 0.70 |
| Weekly | 0.71082 - 0.71402 | 32 | 4 | resistance, 140 pips up | overlaps your daily box (merged weekly + daily idea); round number 0.71 |

### AUDJPY (price 110.65)

Weekly bearish, daily bearish, 4H bullish. Weekly and daily agree, and the 4H is against them (a pullback, "mid risk"). Under the core rules the idea is to wait for a sell at resistance, so the weekly and daily boxes above price matter most. Weekly 50 EMA is 109.1, daily 111.46.

| Timeframe | Box | Pips | Touches | Role | Confluences |
|---|---|---|---|---|---|
| Daily | 110.03 - 110.48 | 45 | 5 | support, 39 pips below | overlaps your daily box; round number 110.5 |
| Weekly | 109.86 - 110.17 | 31 | 3 | support, 63 pips below | overlaps your daily box; round number 110 |
| Daily | 109.32 - 109.84 | 53 | 5 | support, 107 pips below | round number 109.5; holds the daily lower low |
| Daily | 111.48 - 112.02 | 53 | 5 | resistance, 110 pips up | daily 50 EMA (111.46); round number 111.5; holds the daily lower high |
| Weekly | 111.53 - 111.83 | 31 | 3 | resistance, 103 pips up | overlaps the daily box above (weekly + daily idea); round number 111.5; holds the weekly lower high |

Your daily box (110.002 - 110.580) is 57.8 pips tall. The draft's daily support (110.03 - 110.48) sits inside it, and the weekly support (109.86 - 110.17) overlaps its lower part.
