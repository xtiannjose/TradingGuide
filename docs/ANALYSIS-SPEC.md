# Analysis spec v1: what the app computes

This is the app-ready version of `strategy/strategy.md`: the rules turned into inputs, steps, parameters, outputs and tests. `strategy/strategy.md` explains where each rule comes from and how sure we are. This file says exactly what to build.

Where the videos give a number, it is used and marked **course**. Where they leave a choice to the eye, the value here is an **app default**: my suggestion, adjustable in a settings file, to be checked against real charts (see `docs/BUILD-PLAN.md`).

## 0. Conventions

- **Candles** are OHLC bars with a UTC timestamp. Only **closed** candles are analysed; the live candle is ignored.
- **New York time** (`America/New_York`, with daylight saving) is used for every clock rule and for the day/week boundary: a daily candle runs 5:00 PM to 5:00 PM New York; a weekly candle runs from Sunday 5:00 PM to Friday 5:00 PM. Higher-timeframe candles are built from lower ones (or taken from a feed that uses this boundary).
- **Pip** = 0.01 for pairs quoted in JPY, otherwise 0.0001.
- **Body top / body bottom** = max / min of open and close. A **body close beyond a level** means the candle's close is beyond it (open and close beyond for a full body; the rule needs the close).
- **Direction**: +1 bullish (buy), -1 bearish (sell).
- Parameters are written `P-NAME`; their defaults are in section 10.

## 1. Inputs and settings

| Setting | Meaning | Default |
|---|---|---|
| `pairs` | List of forex pairs to analyse | the 21 pairs of his "Blue list" |
| `mode` | `full` (weekly, daily, 4H top-down) or `simple` (one pair, one timeframe, one session) | `full` |
| `simple.timeframe` / `simple.session` | For simple mode | `4H`, `London` |
| `risk_pct`, `account_balance`, `account_currency` | For lot size | `risk_pct` has no course default; placeholder 1.0, user must confirm |
| `weekdays` | Allowed entry days | Mon, Tue, Wed |
| `window` | Allowed entry hours, New York | 01:00 to 10:30 |
| `exit_policy` | `next_structure` or `rr2` (see 8.2) | `next_structure` |
| `strict_engulfing` | Engulfing must cover two bodies | off |

## 2. Data needed per pair

| Timeframe | Lookback | Used for |
|---|---|---|
| Weekly | 6 years | structure, zone, AOI |
| Daily | 2 years | structure, zone, AOI, EMA |
| 4-hour | 12 months | structure, zone, EMA, signals |
| 2H, 1H, 30m, 15m | about 3 months | entry signals and retests |

The 50 EMA is computed on each timeframe from closes (course). Candles must be gap-free in the sense of his "No gaps candles" indicator: for structure on closes this makes no difference (inference to verify).

## 3. Module A: time gate

1. Convert "now" (or the candle time being analysed) to New York time.
2. **T1** Sydney/Tokyo-only hours are closed (course).
3. **T2** Entry window: 01:00 to 10:30 New York (course; he says "10:00" in places).
4. **T3** Weekdays: Monday to Wednesday (course, with exceptions he allows).
5. **T4** Session by market (simple mode): London unless the market is the S&P or gold (New York) (course).
6. **T5** If a confirmation prints outside the window, the verdict is `WAIT_FOR_SESSION` until the hour before London (course).
7. **T6** Not the first minutes of Monday's open nor the last 3 hours before the weekly close (course, no exact minutes: app default 3 hours at the close, 1 hour at the open).
8. Output: `time_gate: pass | fail(reason)`.

## 4. Module B: market structure (per timeframe)

Input: closed candles of one timeframe within its lookback. Output per timeframe: `state` (bullish/bearish), the four levels (HH, HL, LH, LL with price and time), `last_break_time`, `current_vs_confirmed` flags.

### 4.1 Pivots (app default)

The course finds "elbows" by eye on the line chart (closes). The app uses a **ZigZag on closing prices**: a pivot is confirmed when price reverses by at least `P-SWING-ATR x ATR(14)` of that timeframe. This filters the "soft bumps" he says to skip. Alternative to test: fractal with `k=2`. Keep the method pluggable.

### 4.2 State machine (course)

Walk the closed candles in time order.

```
state in {bull, bear}; levels: bull -> HH, HL ; bear -> LL, LH
bull:
  close > HH  -> HH := highest close of the push (keeps rising until a pullback pivot);
                 HL := snake(back from the new HH)
  close < HL  -> state := bear; LL := lowest close of the move;
                 LH := snake(back from the new LL)
bear (mirror):
  close < LL  -> LL moves down; LH := snake(...)
  close > LH  -> state := bull; HH := highest close of the move; HL := snake(...)
otherwise -> no change (touches, wicks, small swings)
```

- Use **bodies**: for the break test compare the close (and, for drawing lines, body tops/bottoms) with the level. Wicks never count.
- A new HH always creates a new HL; a new LL always creates a new LH.
- **Snake trick:** from the new extreme at candle i, walk back; the first pivot of the opposite type that passes the pivot filter is the paired point. Soft bumps that fail the filter are skipped; a clearly strong single candle can count (app default: a single-candle pullback counts only if its body is at least `P-SOFT-BODY` of ATR).
- An extreme is **current** while its candle is open or price is still pushing, and **confirmed** once its candle has closed and price has pulled back at least `P-CONFIRM-ATR x ATR`. Report both.
- **Initial anchor:** start from the most obvious highest high in the lookback (course) and replay forward; the state after the last closed candle is the answer. Do not re-read history each day: store the state and update it on each new closed candle.
- Never infer the trend from price level.

### 4.3 Output example (one timeframe)

```json
{"tf":"4H","state":"bearish","LH":{"price":98.10,"time":"..."},"LL":{"price":97.80,"time":"..."},
 "last_break":"...","ll_confirmed":false}
```

## 5. Module C: alignment, zone, weekly bias

1. Run Module B on weekly, daily and 4H.
2. **C1 Alignment** (course): pass if weekly and daily agree, or daily and 4H agree. Grade A if all three agree. Weekly and 4H alone do not count.
3. **C2 Higher-risk flags**: weekly against daily/4H ("counter-weekly"; allowed only in his video-6 form, see 8.4); weekly+daily agree but 4H differs ("take the risk or wait").
4. **C3 Zone** per timeframe: between HH and HL (bull) or LH and LL (bear). Price must be inside the zone of the timeframe being used; if price is outside, the state would already have flipped.
5. **C4 Weekly bias** (video 7): fixed at Sunday 5:00 PM New York from the weekly/daily/4H states and stored. During the week it changes only when a state flip from Module B changes the higher-timeframe alignment. The bias is shown in every report.
6. **C5** Do not buy while price is below a weekly level, nor sell while above one (video 6).

## 6. Module D: areas of interest

Input: weekly and daily candles, their zones. Output: up to `P-AOI-MAX-COUNT` AOIs, each with box (low, high), pips, touch count, timeframes, role (support or resistance relative to current price).

1. **Candidates**: cluster the structure pivots (closes/bodies) that lie inside the zone. A box is a price band whose height is at most `P-AOI-MAX-PIPS` and at least `P-AOI-MIN-PIPS` (course 60 and 5), as tight as possible while containing the touches (do not stretch for more touches). Sweet spot 20 to 35 pips (course).
2. **Touch** (app default): a pivot whose body extreme lies inside the box expanded by `P-TOUCH-TOL`; two touches must be at least `P-TOUCH-GAP` candles apart. Support and resistance touches may be mixed (course). Wicks do not create touches (course).
3. **Valid** if touches >= `P-AOI-MIN-TOUCH` (3, course). More touches rank higher ("more than three" ideal, video 3).
4. **Inside the zone** only (course): drop any box outside the HH-HL (bull) or LH-LL (bear) zone of its timeframe. Weekly AOIs are checked against the weekly zone, daily against the daily zone. **Weekly and daily only**, no 4H AOIs (course).
5. **Merge** a weekly and a daily AOI that overlap into one box that still has at least 3 touches on both; mark `overlap=true` (course).
6. Keep at most 3, preferring more touches and nearness to price; drop boxes far behind another zone (course).
7. **Role**: price above a box = support (buy side); below = resistance (sell side). A flipped zone needs a break and retest first (course).
8. **At the AOI**: price (or the signal candle) is inside the box expanded by `P-AT-AOI`. No AOI at price means no trade.
9. **Extras at the AOI** (each yes/no): 50 EMA rejection (daily, 4H, weekly or 1H); round number inside or within `P-ROUND-PROX` of the box (levels at multiples of 0.005, or 0.5 for JPY pairs); previous daily swing level inside the box; neckline coincidence (Module E).
10. If no AOI qualifies, `aoi: none` and the verdict is `NO_TRADE(no_aoi)` (course).

## 7. Module E: entry signals and patterns

All signals require: a **closed** candle; price **at an AOI** (6.8); direction equals the bias and the AOI role (buy at support, sell at resistance); time gate passed.

### 7.1 Candle signals (shapes are app defaults; the course gives names, not numbers)

For a bullish setup (mirror for bearish), with `range = high - low`:

- **Doji**: body <= `P-DOJI-BODY` x range.
- **Rejection**: body <= `P-REJ-BODY` x range and the rejection-side wick >= 2 x body and >= 50% of range. Includes dragonfly doji and hammer.
- **Hammer**: rejection candle with an upper wick <= 10% of range. **Inverted hammer / wick fill**: upper wick >= 50% of range, lower wick <= 10%.
- **Engulfing**: the last candle's body closes beyond the bodies of the previous N candles; **N >= 1** is valid (course, videos 2 and 5); grade = N (N >= 2 is "strong"; whole consolidation = his favourite). If `strict_engulfing`, require N >= 2. Wicks ignored; a hairline excess counts.
- **Morning / evening star**: a doji or hammer candle followed by an engulfing candle that covers it and the one before (his form).
- Rejected and ignored: piercing line, three soldiers/crows, dark cloud cover.
- **Confirmation**: a rejection and/or an engulfing at the AOI. Both together or several dojis first score higher. Higher timeframe scores higher (daily > 4H > 1H > 30m).
- **Strength by location**: the same candle away from an AOI is weak and ignored (video 4).
- **Wick fill (informational)**: a daily candle with a long lower (upper) wick where the 4H inside the day went against, then made a higher low (lower high): flag `wick_fill`; do not cancel the setup because of one contrary candle when the AOI has 3+ touches (video 4).

### 7.2 Patterns (all optional extras, never a trade by themselves)

- **Break and retest**: (1) price at an AOI; (2) a body close beyond the box; (3) within `P-RETEST-WINDOW` entry-timeframe candles price returns into the box; (4) a rejection candle there; then enter on the far side of the box. Ranked entries: on the breakout (off by default), retest without a rejection (off), retest with a rejection (default). If the retest never comes, `missed`.
- **Head and shoulders (and inverse)**: five alternating pivots (left shoulder, trough, head higher than both shoulders, trough, right shoulder) on bodies; neckline is horizontal at the previous higher low; **valid only after a body close below the neckline** (structure shift); then wait for the retest of the neckline (which should coincide with an AOI) and a confirmation candle. **Never signal on a potential pattern or the right shoulder.** Mirror for the inverse. Double top/bottom uses the same neckline rule.
- **Consolidation breakout**: a tight range at an AOI, breakout by body close, quick retest, rejection or engulfing.

### 7.3 Chase flag

If price is at or within `P-CHASE-ATR` x ATR of the latest swing extreme and has not pulled back at least 1 x ATR from it, flag `chase` and downgrade (course: never buy the high or sell the low, videos 3 and 7).

## 8. Modules F and G: verdict, plan, size

### 8.1 Verdict

States:

- `NO_TRADE(reason)`: a gate failed. Reasons: `time`, `weekday`, `no_alignment`, `no_aoi`, `price_not_at_aoi`, `no_confirmation`, `against_weekly_level`, `chase`, `rr_below_2`.
- `WATCH`: structure and alignment pass and an AOI exists, but price is not at it (or the confirmation is not closed yet). The report gives the AOI edges as alert levels and says what is awaited.
- `WAIT_FOR_SESSION`: a confirmation closed outside the time gate; enter in the pre-London hour (T5).
- `SIGNAL`: every core gate passes and a confirmation has closed. Carries the plan below.

Core (mandatory): trend (alignment), AOI at price, closed confirmation. Extras (never mandatory): all three timeframes aligned, weekly+daily AOI overlap, break and retest, a pattern neckline at the AOI, higher-timeframe candle, EMA rejection, round number, previous daily level, many touches. **Grade (app default)**: A = core + three-timeframe alignment + at least two extras; B = core + at least one extra; C = core only. The course gives no weights; show the checklist and let the user judge.

### 8.2 Plan (course numbers where given)

- **Stop**: just beyond the level that proves the idea wrong: the far edge of the AOI or the structure point, or the signal wick extreme, plus a buffer `P-STOP-BUFFER` (his one example: 10 to 15 pips beyond the wick). Not the tightest stop.
- **Target**: the next structure point or opposing AOI edge. Let `R_next` = distance to it divided by the stop distance.
  - `R_next < 2` -> `NO_TRADE(rr_below_2)` (course: minimum 1:2).
  - `exit_policy = next_structure`: target at the next structure point, capped at `P-RR-CAP` (4, video 7: "at 1:4 the trade is done").
  - `exit_policy = rr2`: target at exactly 2 R (video 6: "always get out at a 1:2" unless it clearly makes sense to hold); also report where the next structure sits.
- **Target and entry timeframe must match** (video 5): derive stop and target from the same timeframe as the entry candle, and show the expected time to target as a note (4H about 1.5 days, daily about 5 days in his example).
- **Lot size** = risk amount / (stop pips x pip value per lot). Risk amount = `account_balance` x `risk_pct`. Pip value is computed from the quote currency and the current rate to the account currency. Verified cases: EURUSD, $100, 10%, 20 pips -> 0.05 lot; GBPUSD, $20, 25 pips -> 0.08 lot. A yen pair must use the yen conversion (his NZDJPY calculator example of 0.17 lot for $50 at 30 pips is not standard; at USDJPY near 147 it is about 0.25 lot).
- Output also: R:R, stop pips, target pips, risk amount, lot size, and the reminder "set and forget".

### 8.3 Simple mode (video 5)

Skip the three-timeframe alignment. Use only `simple.timeframe` (default 4H): read its structure (Module B) as the direction; run Modules D (AOI from the same timeframe's pivots), E and G with that timeframe; session gate = `simple.session`. Same checklist, fewer gates, labelled `mode: simple`.

### 8.4 Counter-weekly trades (video 6)

Allowed only when the weekly is against, the daily has shifted (above/below its EMA, break and retest), the 4H agrees, a weekly AOI lies ahead in the trade direction, and the target is placed at that weekly AOI. Flag `higher_risk`.

## 9. Outputs

### 9.1 Machine output (JSON per pair)

```json
{
 "pair": "EURUSD", "mode": "full", "asof": "2026-10-12T05:30:00-04:00",
 "time_gate": {"pass": true},
 "weekly_bias": "bearish",
 "tf": {"W": {...}, "D": {...}, "4H": {...}},
 "alignment": {"pass": true, "grade": "A"},
 "aois": [{"tf": "W+D", "low": 1.1650, "high": 1.1685, "pips": 35, "touches": 4, "role": "resistance", "extras": ["ema","round_number"]}],
 "signal": {"type": "bearish_engulfing", "n_engulfed": 3, "tf": "1H", "closed_at": "..."},
 "verdict": "SIGNAL", "grade": "B",
 "plan": {"side": "sell", "entry": 1.1662, "stop": 1.1702, "target": 1.1582, "rr": 2.0, "stop_pips": 40, "lots": 0.05},
 "checklist": [{"item": "alignment", "pass": true}, "..."],
 "no_trade_reason": null
}
```

### 9.2 Human report (one page per pair, plus a summary table)

1. Summary table of all pairs: verdict, grade, bias, nearest AOI and distance, what is awaited.
2. Per pair: the checklist (pass/fail with the reason), the three timeframe reads with their HH/HL/LH/LL prices, the AOIs, the signal candle, the plan, alert levels, and a "why no trade" line when a gate fails.
3. A "changed since last run" list (bias flips, new signals).
4. Always: educational analysis only, not advice; the user's own risk setting; no orders are placed.

### 9.3 Annotated chart (PNG or interactive HTML)

Candles (blue up, red down), 50 EMA, the structure lines (HH, HL, LH, LL) per timeframe, AOI boxes, the signal candle highlighted, the stop and target boxes. This is the main way the user verifies the app against TradingView.

## 10. Default parameters

| Parameter | Meaning | Default | Source |
|---|---|---|---|
| `P-TZ` | Clock and candle boundary | America/New_York, 5 PM close | course (inferred) |
| `P-WINDOW` | Entry window | 01:00 to 10:30 | course |
| `P-DAYS` | Entry days | Mon to Wed | course |
| `P-SWING-ATR` | ZigZag reversal threshold | 1.0 x ATR(14) | app default |
| `P-SOFT-BODY` | Single-candle pullback counts if body at least | 1.0 x ATR | app default |
| `P-CONFIRM-ATR` | Retrace to confirm an HH/LL | 1.0 x ATR | app default |
| `P-LOOKBACK` | W / D / 4H | 6y / 2y / 12mo | course |
| `P-AOI-MIN-TOUCH` | Touches for an AOI | 3 | course |
| `P-AOI-MIN-PIPS`, `P-AOI-MAX-PIPS` | AOI height | 5, 60 (sweet spot 20 to 35) | course |
| `P-AOI-MAX-COUNT` | AOIs kept | 3 | course |
| `P-TOUCH-TOL` | Touch tolerance | 10% of box height, at least 3 pips | app default |
| `P-TOUCH-GAP` | Candles between two touches | 3 | app default |
| `P-AT-AOI` | Price counts as "at" the AOI | box widened by 25% of height, at least 5 pips | app default |
| `P-ROUND-PROX` | Round-number proximity | 10 pips | app default |
| `P-DOJI-BODY` | Doji body | 10% of range | app default |
| `P-REJ-BODY` | Rejection candle body | at most 30% of range, wick at least 2 x body | app default |
| `P-ENGULF-MIN` | Candles engulfed | 1 (2 = strong) | course |
| `P-RETEST-WINDOW` | Candles allowed for the retest | 20 | app default |
| `P-CHASE-ATR` | Chase flag distance | 0.5 x ATR | app default |
| `P-STOP-BUFFER` | Beyond level or wick | 10 pips | course example (10 to 15) |
| `P-RR-MIN` | Minimum reward to risk | 2.0 | course |
| `P-RR-CAP` | Normal exit ceiling | 4.0 | course (video 7) |
| `P-EMA` | EMA length | 50 | course |
| `risk_pct` | Risk per trade | user-set (placeholder 1.0) | not in the course |

## 11. Test plan

1. **Unit tests on hand-built candle series** for every rule above: state machine flips (bull to bear to bull), wick-only breaks do nothing, soft bumps skipped, snake trick, alignment grades, AOI touch counting and the 5/60-pip limits, outside-zone AOIs dropped, engulfing grades, H&S valid only after the neckline break, break-and-retest ordering, time gate and weekday, R:R and lot-size maths.
2. **Golden examples from the videos** (real prices are fetched later; compare approximately):
   - EURUSD 4H replay: bullish with HL near 1.1713, a close near 1.1697 flips bearish [video 1, part F].
   - AUDJPY (Sept 2025): weekly bullish (HH about 98.0, HL about 95.4), daily bullish (98.4 / 96.6), 4H bearish (LH about 98.1, LL about 97.8) -> alignment W+D, 4H against; merged AOIs about 97.25 to 97.55 and 96.62 to 96.93 [parts G, H].
   - NZDUSD short: entry 0.59267, stop 0.59469 = 20.2 pips, 1:2 target 0.58862 [part J].
   - EURAUD 4H short: stop 45.1 pips, target 98.5 pips, R:R 2.18 [video 6].
   - Lot sizes above.
   Data from different brokers differs by a few points, so tests use tolerances.
3. **Visual checks**: for 3 to 5 pairs, render the annotated chart and compare with TradingView. Differences are resolved by adjusting parameters, not by special-casing.
4. **Replay**: run the engine over past data candle by candle and check that signals appear only on closed candles and never use future data.
5. **Back-test harness (later)**: counts signals and R outcomes per rule set. This checks that the rules behave sensibly and how often they fire; it does not prove the strategy makes money.

## 12. Out of scope (for now)

Placing or managing orders; reading screenshots with a vision model (candle data is exact; screenshots are not); live news feed; the creator's unpublished "entry signal"; anything marked as a gap in `strategy/strategy.md` section 7.
