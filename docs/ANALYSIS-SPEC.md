# Analysis spec v1: what the app computes

This is the app-ready version of the **core rule set** in `strategy/strategy.md` section 1: the rules turned into inputs, steps, parameters, outputs and tests. One rule set, no modes; parked extras are listed in section 13. `strategy/strategy.md` explains where each rule comes from and how sure we are. This file says exactly what to build.

Where the videos give a number, it is used and marked **course**. Where they leave a choice to the eye, the value here is an **app default**: my suggestion, adjustable in a settings file, to be checked against real charts (see `docs/BUILD-PLAN.md`).

## 0. Conventions

- **Candles** are OHLC bars with a UTC timestamp. Only **closed** candles are analysed; the live candle is ignored.
- **New York time** (`America/New_York`, with daylight saving) is used for every clock rule and for the day/week boundary: a daily candle runs 5:00 PM to 5:00 PM New York; a weekly candle runs from Sunday 5:00 PM to Friday 5:00 PM. Higher-timeframe candles are built from lower ones (or taken from a feed that uses this boundary).
- **Two clocks.** Every strategy rule is evaluated in **New York time** (his). Reports, schedules and alerts also show the user's local time, set by `display_tz` (default `Asia/Manila`, UTC+8, no daylight saving). Times are stored in UTC and converted for display; the two zones are always shown side by side, for example `01:00 NY (13:00 Manila)`. Manila is NY + 12 hours while the US is on summer time (EDT) and NY + 13 hours in winter (EST); the US changes on the second Sunday of March and the first Sunday of November (2026: 8 March and 1 November).

  | Event | New York (rule) | Manila, US summer | Manila, US winter |
  |---|---|---|---|
  | Entry window opens | 01:00 | 13:00 | 14:00 |
  | London opens | 03:00 | 15:00 | 16:00 |
  | New York opens | 08:00 | 20:00 | 21:00 |
  | Last entry | 10:30 | 22:30 | 23:30 |
  | London ends | 12:00 | 00:00 (+1 day) | 01:00 (+1 day) |
  | Daily/weekly candle close | 17:00 | 05:00 (+1 day) | 06:00 (+1 day) |
  | Sunday market open, weekly bias | Sun 17:00 | Mon 05:00 | Mon 06:00 |

  The entry window falls on the same calendar day in Manila, so Monday to Wednesday is the same in both. The US and UK change clocks on different dates, so for 1 to 3 weeks each spring and autumn London opens at 04:00 NY instead of 03:00 (2026: 8 to 29 March and 25 October to 1 November). The entry window stays on the New York clock (his rule); "the hour before London" (T5) uses London's real 08:00 local open.
- **Pip** = 0.01 for pairs quoted in JPY, otherwise 0.0001.
- **Body top / body bottom** = max / min of open and close. A **body close beyond a level** means the candle's close is beyond it (open and close beyond for a full body; the rule needs the close).
- **Direction**: +1 bullish (buy), -1 bearish (sell).
- Parameters are written `P-NAME`; their defaults are in section 10.

## 1. Inputs and settings

| Setting | Meaning | Default |
|---|---|---|
| `pairs` | List of forex pairs to analyse | the 21 pairs of his "Blue list" |
| `risk_pct`, `account_balance`, `account_currency` | For lot size. The same % on every trade (videos 8, 10, 13) | `risk_pct` has no course default; placeholder 1.0, user must confirm |
| `display_tz` | Second clock shown next to New York time everywhere | `Asia/Manila` |

There are deliberately no switches between rule versions: app v1 runs one core rule set (`strategy/strategy.md` section 1). Everything that used to be a mode or an option is listed in section 13 (parked).

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
4. **T3** Weekdays: Monday to Wednesday only (video 2). Sunday, Thursday and Friday fail with `weekday`. (His rare Thursday exceptions are discretionary and not coded.)
5. **T5** If a confirmation prints outside the window, the verdict is `WAIT_FOR_SESSION` until the hour before London (course).
6. **T6** Not the first minutes of Monday's open nor the last 3 hours before the weekly close (course, no exact minutes: app default 3 hours at the close, 1 hour at the open).
7. Output: `time_gate: pass | fail(reason)`.

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
- The paired point is always **earlier in time** than its extreme: `HL.time < HH.time`, `LH.time < LL.time` (video 12: "the higher low could never be in the future"). A pullback low after the current HH is not the HL until a new HH forms.
- **Snake trick:** from the new extreme at candle i, walk back; the first pivot of the opposite type that passes the pivot filter is the paired point. Soft bumps that fail the filter are skipped; a clearly strong single candle can count (app default: a single-candle pullback counts only if its body is at least `P-SOFT-BODY` of ATR).
- An extreme is **current** while its candle is open or price is still pushing, and **confirmed** once its candle has closed and price has pulled back at least `P-CONFIRM-ATR x ATR`. Report both.
- **Initial anchor** (app default; the course starts by eye from "the most obvious highest high"): take the first confirmed pivot high H0 and pivot low L0 in the lookback; the first body close above H0 starts the state as bull (HH from that push, HL by the snake trick), the first body close below L0 starts it as bear. Replay forward from there; the state after the last closed candle is the answer, and the same candles always give the same state. Do not re-read history each day: store the state and update it on each new closed candle.
- Never infer the trend from price level.

### 4.3 Output example (one timeframe)

```json
{"tf":"4H","state":"bearish","LH":{"price":98.10,"time":"..."},"LL":{"price":97.80,"time":"..."},
 "last_break":"...","ll_confirmed":false}
```

## 5. Module C: alignment, zone, weekly bias

1. Run Module B on weekly, daily and 4H.
2. **C1 Alignment**: pass only if the **weekly and daily agree**; that sets the direction. Risk label **`low`** when the 4H agrees too; **`mid`** when the 4H is against, which is normal while price pulls back into the AOI (videos 8, 9, 12).
3. **C2 Counter-trend**: daily (and 4H) against the weekly is his "high risk" counter-trend case: verdict `NO_TRADE(counter_trend)`, reported so the user sees it. Weekly and daily disagreeing in any other way: `NO_TRADE(no_alignment)`.
4. **C3 Zone** per timeframe: between HH and HL (bull) or LH and LL (bear). Price must be inside the zone of the timeframe being used; if price is outside, the state would already have flipped.
5. **C4 Weekly bias** (video 7): fixed at Sunday 5:00 PM New York from the weekly and daily states and stored. During the week it changes only when a state flip from Module B changes the higher-timeframe alignment. The bias is shown in every report.
6. **C5 Weekly level in the way** (video 6: do not buy below a weekly level, nor sell above one): if an opposing weekly AOI (resistance for a buy, support for a sell) starts between the entry and the 2R point, the verdict is `NO_TRADE(against_weekly_level)`.

## 6. Module D: areas of interest

Input: weekly and daily candles, their zones. Output: up to `P-AOI-MAX-COUNT` AOIs, each with box (low, high), pips, touch count, timeframes, role (support or resistance relative to current price).

1. **Candidates**: cluster the structure pivots (closes/bodies) that lie inside the zone. A box is a price band whose height is at most `P-AOI-MAX-PIPS` and at least `P-AOI-MIN-PIPS` (course 60 and 5), as tight as possible while containing the touches (do not stretch for more touches). Sweet spot 20 to 35 pips (course).
2. **Touch** (app default): a pivot whose body extreme lies inside the box expanded by `P-TOUCH-TOL`; two touches must be at least `P-TOUCH-GAP` candles apart. Support and resistance touches may be mixed (course). Wicks do not create touches (course).
3. **Valid** if touches >= `P-AOI-MIN-TOUCH` (3, course). More touches rank higher ("more than three" ideal, video 3).
4. **Inside the zone** only (course): drop any box outside the HH-HL (bull) or LH-LL (bear) zone of its timeframe. Weekly AOIs are checked against the weekly zone, daily against the daily zone. Weekly and daily AOIs first. Videos 9 and 10 (newer than the 2025 note "4hr NO AOI") allow AOIs on the 4H as well: draw them, mark `minor=true`, rank them below weekly and daily. Look back at least two years for AOIs (video 10).
5. **Merge** a weekly and a daily AOI that overlap into one box that still has at least 3 touches on both; mark `overlap=true` (course).
6. Keep at most 3 (video 9: typically 2 to 3), preferring nearness to price, then touches (a soft score: more taps are not a hard rank, video 9); drop boxes far behind another zone (course). Rank by nearness: the nearest AOI is the first.
   - **Independent AOIs** (video 9): evaluate each AOI as its own trade; a lost trade at one does not affect the next AOI.
   - **Broken AOI** (video 9, newer): a body close through a box removes it from the candidate list. It may come back only as a flipped zone after a break-and-retest (Module E).
7. **Role**: price above a box = support (buy side); below = resistance (sell side). A flipped zone needs a break and retest first (course).
8. **At the AOI**: price (or the signal candle) is inside the box expanded by `P-AT-AOI`. No AOI at price means no trade. **The entry-signal step is not evaluated at all until price is inside or at an AOI** (video 9).
9. **Extras at the AOI** (each yes/no): 50 EMA rejection (daily, 4H, weekly or 1H); round number inside or within `P-ROUND-PROX` of the box (levels at multiples of 0.005, or 0.5 for JPY pairs); previous daily swing level inside the box; neckline coincidence (Module E).
10. If no AOI qualifies, `aoi: none` and the verdict is `NO_TRADE(no_aoi)` (course).

## 7. Module E: entry signals and patterns

All signals require: a **closed** candle; price **at an AOI** (6.8); direction equals the bias and the AOI role (buy at support, sell at resistance); time gate passed.

### 7.1 Candle signals (shapes are app defaults; the course gives names, not numbers)

For a bullish setup (mirror for bearish), with `range = high - low`:

- **Doji**: body <= `P-DOJI-BODY` x range.
- **Rejection**: body <= `P-REJ-BODY` x range and the rejection-side wick >= 2 x body and >= 50% of range. Includes dragonfly doji and hammer.
- **Hammer**: rejection candle with an upper wick <= 10% of range. **Inverted hammer / wick fill**: upper wick >= 50% of range, lower wick <= 10%.
- **Engulfing**: the last candle's body closes beyond the bodies of the previous N candles; **N >= 1** is valid (course, videos 2 and 5); grade = N (N >= 2 is "strong"; whole consolidation = his favourite). Wicks ignored; a hairline excess counts.
- **Morning / evening star**: a doji or hammer candle followed by an engulfing candle that covers it and the one before (his form).
- Rejected and ignored: piercing line, three soldiers/crows, dark cloud cover.
- **Confirmation**: a rejection and/or an engulfing at the AOI. Both together or several dojis first score higher. Higher timeframe scores higher (daily > 4H > 2H > 1H > 30m > 15m).
- **Which candle counts** (app default, so every run picks the same one): check the daily, 4H, 2H, 1H, 30m and 15m. A confirmation counts only if it is the **latest closed candle** of its timeframe (video 9 enters at the next candle's open, so an older one is stale). If several timeframes confirm at once, report the highest timeframe.
- **Strength by location**: the same candle away from an AOI is weak and ignored (video 4).

### 7.2 Patterns (all optional extras, never a trade by themselves)

- **Break and retest**: (1) price at an AOI; (2) a body close beyond the box; (3) within `P-RETEST-WINDOW` entry-timeframe candles price returns into the box; (4) a rejection candle there; then enter on the far side of the box. Only the retest with a rejection candle counts (his favourite). If the retest never comes, `missed`.
- **Head and shoulders (and inverse)**: five alternating pivots (left shoulder, trough, head higher than both shoulders, trough, right shoulder) on bodies; neckline is horizontal at the previous higher low; **valid only after a body close below the neckline** (structure shift); then wait for the retest of the neckline (which should coincide with an AOI) and a confirmation candle. **Never signal on a potential pattern or the right shoulder.** Mirror for the inverse. Double top/bottom uses the same neckline rule.
## 8. Modules F and G: verdict, plan, size

### 8.1 Verdict

States:

- `NO_TRADE(reason)`: a gate failed. Reasons: `time`, `weekday`, `no_alignment`, `counter_trend`, `no_aoi`, `price_not_at_aoi`, `no_confirmation`, `against_weekly_level`, `rr_below_2`.
- `WATCH`: structure and alignment pass and an AOI exists, but price is not at it (or the confirmation is not closed yet). The report gives the AOI edges as alert levels and says what is awaited.
- `WAIT_FOR_SESSION`: a confirmation closed outside the time gate; enter in the pre-London hour (T5). Only if that hour falls on Monday to Wednesday (otherwise `NO_TRADE(weekday)`), and only while price is still inside or at the AOI with no body close beyond its far edge (app default).
- `SIGNAL`: every core gate passes and a confirmation has closed. Carries the plan below.

Core (mandatory): trend (weekly and daily aligned), AOI at price, closed confirmation. Extras (never mandatory): the 4H aligned too, weekly+daily AOI overlap, break and retest, a pattern neckline at the AOI, higher-timeframe candle, EMA rejection, round number, previous daily level, many touches. **Grade (app default)**: A = core + risk `low` (4H agrees) + at least two extras; B = core + at least one extra; C = core only. The course gives no weights; show the checklist and let the user judge.

### 8.2 Plan (course numbers where given)

- **Entry** (video 9): the signal candle closes; set stop, then take profit; enter at the **next candle's open** (market entry). Before that candle opens the report uses the signal close as the estimate.
- **Stop** (video 9, newer): beyond the **far edge of the AOI box** the signal formed at (weekly, daily, merged or minor 4H), plus `P-STOP-BUFFER` (5 to 10 pips). It does not depend on the signal candle's timeframe or wick. Video 10 keeps the stop tight on purpose so that 1:2 holds: if the target is then closer than 1:2 the setup is skipped, never squeezed inside the AOI.
- **Target** (videos 9 and 13: "the nearest structure point", the last place the market reacted from; app default for which one): the nearest of (a) the latest confirmed swing pivot beyond the entry in the trade direction on `P-TARGET-TF` (daily and 4H), and (b) the near edge of the nearest opposing AOI. Let `R_next` = distance to the target divided by the stop distance.
  - `R_next < 2` -> `NO_TRADE(rr_below_2)` (every video: minimum 1:2).
  - `R_next > 4` -> target capped at 4R (`P-RR-CAP`, video 7: "at 1:4 the trade is done").
- Video 5's rule "match stop and target to the entry timeframe" belonged to its single-timeframe mode; video 9's stop beyond the whole AOI (newer) replaces it. Show the expected time to target only as a note.
- **Lot size** = risk amount / (stop pips x pip value per lot). Risk amount = `account_balance` x `risk_pct`. Pip value is computed from the quote currency and the current rate to the account currency. Verified cases: EURUSD, $100, 10%, 20 pips -> 0.05 lot; GBPUSD, $20, 25 pips -> 0.08 lot. A yen pair must use the yen conversion (his NZDJPY calculator example of 0.17 lot for $50 at 30 pips is not standard; at USDJPY near 147 it is about 0.25 lot).
- Output also: R:R, stop pips, target pips, risk amount, lot size, and the reminder "set and forget".

## 9. Outputs

### 9.1 Machine output (JSON per pair)

```json
{
 "pair": "EURUSD", "asof": "2026-10-12T05:30:00-04:00",
 "time_gate": {"pass": true},
 "weekly_bias": "bearish",
 "tf": {"W": {...}, "D": {...}, "4H": {...}},
 "alignment": {"pass": true, "risk": "low"},
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

One image per timeframe that matters (weekly, daily, signal timeframe), embedded as PNG in the report, plus an interactive version (TradingView's open-source Lightweight Charts library, with its required attribution). Drawn: candles (blue up, red down), the 50 EMA, the structure lines and labels (HH, HL, LH, LL) per timeframe, the zone shading, AOI boxes with a dot on each counted touch and a label (timeframe, touches, pips), a round-number line and a neckline when present, the signal candle highlighted, the stop (red) and target (green) boxes with the R:R. Each confluence gets a **numbered marker** on the chart that matches its line in the checklist. No other indicators (his method uses only the 50 EMA). This is the main way the user verifies the app against TradingView.

## 10. Default parameters

| Parameter | Meaning | Default | Source |
|---|---|---|---|
| `P-TZ` | Clock and candle boundary | America/New_York, 5 PM close | course (inferred) |
| `P-WINDOW` | Entry window | 01:00 to 10:30 | course |
| `P-DAYS` | Entry days | Mon to Wed | course |
| `P-SWING-ATR` | ZigZag reversal threshold | 0.5 x ATR(14) | app default, tuned in phase 1: reproduces the EURUSD 4H flip (HL 1.1713, close 1.1698) and the AUDJPY 4H and weekly reads; 1.0 was too coarse. The AUDJPY daily HL (a 0.28 dip) needs about 0.4 and is left to the owner's chart check |
| `P-SOFT-BODY` | Single-candle pullback counts if body at least | not used | A one-candle pullback of at least `P-SWING-ATR` is already a swing |
| `P-CONFIRM-ATR` | Retrace to confirm an HH/LL | same as `P-SWING-ATR` | An extreme is confirmed when its swing point is |
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
| `P-STOP-BUFFER` | Beyond the AOI edge | 7 pips (range 5 to 10) | video 9 (the 7 is an app default inside his range) |
| `P-RR-MIN` | Minimum reward to risk | 2.0 | every video |
| `P-RR-CAP` | Normal exit ceiling | 4.0 | course (video 7) |
| `P-TARGET-TF` | Timeframes whose swing pivots can be the target | daily, 4H | app default (videos 9, 13: nearest structure point) |
| `P-EMA` | EMA length | 50 | course |
| `risk_pct` | Risk per trade | user-set, the same every trade (placeholder 1.0) | not a course rule |
| `P-AOI-LOOKBACK` | AOI look-back | 2 years minimum | video 10 |

## 11. Test plan

1. **Unit tests on hand-built candle series** for every rule above: state machine flips (bull to bear to bull), wick-only breaks do nothing, soft bumps skipped, snake trick, initial anchor gives the same state on every run, alignment risk labels, signal freshness (only the latest closed candle counts), target selection and the 4R cap, AOI touch counting and the 5/60-pip limits, outside-zone AOIs dropped, engulfing grades, H&S valid only after the neckline break, break-and-retest ordering, time gate and weekday, R:R and lot-size maths.
2. **Golden examples from the videos** (real prices are fetched later; compare approximately):
   - EURUSD 4H replay: bullish with HL near 1.1713, a close near 1.1697 flips bearish [video 1, part F].
   - AUDJPY (Sept 2025): weekly bullish (HH about 98.0, HL about 95.4), daily bullish (98.4 / 96.6), 4H bearish (LH about 98.1, LL about 97.8) -> alignment W+D, 4H against; merged AOIs about 97.25 to 97.55 and 96.62 to 96.93 [parts G, H].
   - NZDUSD short: entry 0.59267, stop 0.59469 = 20.2 pips, 1:2 target 0.58862 [part J].
   - EURAUD 4H short: stop 45.1 pips, target 98.5 pips, R:R 2.18 [video 6]. R:R maths only: it was a counter-weekly trade, so the verdict must be `NO_TRADE(counter_trend)`.
   - Video 10 challenge trades (Sept 2026, dates not stated; fetch the weeks around the Eightcap challenge): AUDCHF weekly range break and retest with a 4H inverted H&S (round number 0.56500, first R:R 1:2.66); GBPCHF counter-weekly sell off a right shoulder (the app must NOT signal it); EURGBP, USDCHF and GBPNZD as listed in `strategy/strategy.md` 3.10. No prices are given in the video, so these are shape checks only.
   - GBPUSD (late January 2026): weekly, daily and 4H bullish; W+D AOI overlap about 1.351 to 1.358, below the 4H HL (about 1.368) [video 12].
   - GBPNZD daily buy (March 2026): weekly bearish after a shift, daily shifted bullish; entry about 2.279, stop about 2.269 under a support box, target about 2.302 at a weekly zone just above 2.3000; closed at 1:2 [video 11, read from the frame]. Counter-weekly, so the verdict must be `NO_TRADE(counter_trend)`; the levels still check the stop and target logic.
   - EURAUD 4H head and shoulders sell (early April 2026): HL break, neckline retest, sell, closed at 1:2 [video 13]. Shape check for H&S detection (an extra).
   - Lot sizes above.
   Data from different brokers differs by a few points, so tests use tolerances.
3. **Visual checks**: for 3 to 5 pairs, render the annotated chart and compare with TradingView. Differences are resolved by adjusting parameters, not by special-casing.
4. **Replay**: run the engine over past data candle by candle and check that signals appear only on closed candles and never use future data.
5. **Back-test harness (later)**: counts signals and R outcomes per rule set. This checks that the rules behave sensibly and how often they fire; it does not prove the strategy makes money.

## 12. Out of scope (for now)

Placing or managing orders; reading screenshots with a vision model (candle data is exact; screenshots are not); live news feed; the creator's unpublished "entry signal"; anything marked as a gap in `strategy/strategy.md` section 7; everything in section 13.

## 13. Parked (not in app v1)

Kept in `strategy/strategy.md` as his teaching, left out of the app so it runs one consistent rule set. Add one back only if testing shows the core misses something he clearly does.

| Parked item | Source | Why parked |
|---|---|---|
| Small-account mode (fixed-dollar risk, 1:3, Thursday before 9 AM, 2 trades a week) | video 8 | One account type |
| Prop-challenge mode (news block, 1 position, 1 trade a day, 2% Strong Start, weekend only at TP, firm profile) | video 10 | One account type |
| $50 plan (4H head and shoulders only, majors) | video 13 | One account type |
| Single-timeframe "trading dumb" mode | video 5 | Second version of the method |
| Counter-weekly recipe | video 6 | High risk; against "trade with the trend"; reported as `counter_trend` instead |
| Lower-timeframe (2H to 15m) vote | video 9 | Never decides a trade |
| Exit at exactly 1:2, weekly-close hold, weekend policy, early exits, scale-ins, re-entries | videos 5, 6, 10, 11 | Trade management; the app does not manage trades |
| Breakout entry without retest, strict two-candle engulfing, Thursday exceptions | course, videos 2, 4 | Second versions of a rule |
| Chase flag, wick-fill flag, consolidation breakout | videos 3, 4, 7, course | Covered by the AOI gate, or an extra that never decides |
| News feed | course, video 10 | Information only in his standard method |
