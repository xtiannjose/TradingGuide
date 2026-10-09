# Build plan: the chart-analysis app

Status: planned, not built. This file is the plan; `docs/ANALYSIS-SPEC.md` is what to build; `strategy/strategy.md` is where the rules come from.

## 1. The goal

An app that takes a list of forex pairs, reads their charts the way the studied strategy does, and gives you a clear report: what the market is doing on each timeframe, where the areas of interest are, whether a trade setup is forming or complete, and what the stop, target and lot size would be. You decide; the app never places orders.

What it is not: a signal seller, an auto-trader, or proof that the strategy makes money. It is an analysis assistant that does the slow reading for you and shows its reasons so you can check them.

## 2. What the study material gives us (digest)

Ten videos by one creator (fxalexg), merged into one rule set. When two videos disagree, the newer upload wins and both sides are kept in `strategy/strategy.md` section 6.

| # | Video | What it contributed |
|---|---|---|
| 1 | 10-hour course | The whole method: structure, top-down, AOI, candles, patterns, sessions, risk |
| 2 | Entry confirmation (22 min) | The confirmation candle, closed candles only, Monday to Wednesday, wait for the session |
| 3 | Liquidity (19 min) | Liquidity zone = AOI; ignore sweeps; round numbers |
| 4 | Price action (25 min) | Strength comes from location; wick fill; ranked break-and-retest entries |
| 5 | "Trading dumb" (28 min) | A simple mode: one pair, one timeframe, one session, one signal |
| 6 | Recent trades (21 min) | Counter-weekly recipe; stop philosophy; exit at 1:2; no plan B |
| 7 | Mindset (18 min) | Weekly bias fixed on Sunday; wait for retracement; 1:2 minimum, done at 1:4 |
| 8 | Small account (52 min, Feb 2026) | Small-account mode: fixed-dollar risk, 1:3 minimum, three timeframes in sync, no Sunday or late-Thursday entries, no lockout after a win |
| 9 | Three-step walkthrough (1:23, Jun 2026) | Entry signal only inside the AOI; AOIs on W/D/4H, each independent; stop 5 to 10 pips beyond the whole AOI; next candle open |
| 10 | Prop-firm course (1:18, Sep 2026) | Prop mode: 10-minute news block, one position at a time, 2% first trade then the same risk; five real trades; weekend rule |

**The strategy in ten lines**

1. Read market structure (higher highs/lows or lower highs/lows) from candle bodies on the weekly, daily and 4-hour charts.
2. Two timeframes in a row must agree; that fixes the direction. The bias is set on Sunday and held all week.
3. Price is trapped in a zone (between HH and HL, or LH and LL); only look inside it.
4. Find areas of interest (AOI) on the weekly and daily (4H as a minor extra): at least 3 touches, 5 to 60 pips, inside the zone.
5. Trade only when price is at an AOI, buying at support and selling at resistance.
6. Wait for a closed confirmation candle there (rejection or engulfing), in the trend direction. Never anticipate, never chase.
7. Break and retest, head and shoulders and similar patterns add confidence but are never enough alone.
8. Enter only in his window (about 1:00 to 10:30 AM New York) and on Monday to Wednesday.
9. Stop just beyond the whole AOI (5 to 10 pips); target the next structure point; at least 1:2 (1:3 on a small account), normally done by 1:4; lot size from your own risk amount.
10. Set it, forget it, accept the losses.

**How sure we are**

- Solid and computable: the structure rules, alignment, zones, the AOI numbers, the candle names, the time and weekday gates, the stop/target/R:R maths.
- Judgement the course leaves to the eye (the app must choose and expose a setting): what counts as a significant swing, what counts as one touch, where to place the AOI box, when a retracement has stopped, the exact candle shapes.
- Not given for a standard account: his base risk % (small accounts use fixed dollars, a prop challenge uses 2% on the first trade and the same after, and the 1% hints are inferred), a news filter outside prop mode (the firm's 10-minute window), the full "entry signal" he keeps for his livestream, and any back-test evidence.
- Three account modes follow from the newer videos: `standard`, `small_account` and `prop` (`docs/ANALYSIS-SPEC.md` 8.5).
- The course also disagrees with itself in small ways (engulfing size, window end, target cap). `strategy/strategy.md` section 6 lists each and the default chosen.

## 3. How the app works (concept)

```
 pairs list + settings
          |
          v
   [1 Data]   candles for weekly, daily, 4H, 2H, 1H, 30m, 15m
          |      (New York 5 PM day boundary, closed candles only)
          v
   [2 Structure]  per timeframe: bullish/bearish, HH/HL/LH/LL
          |
   [3 Alignment + zone + weekly bias]
          |
   [4 AOI finder]  weekly/daily boxes: touches, pips, merged
          |
   [5 Signals]    rejection, engulfing, stars, break and retest, H&S
          |
   [6 Verdict + plan]  NO_TRADE / WATCH / WAIT_FOR_SESSION / SIGNAL,
          |             stop, target, R:R, lot size, checklist
          v
   [7 Report]   one-page-per-pair HTML + summary table + JSON + annotated charts
```

What you see after a run: a summary table of all pairs (verdict, grade, bias, nearest AOI, what is awaited), then for each pair a checklist with a reason for every pass or fail, three timeframe reads, the AOIs, the signal candle, the plan, and alert levels. Every pair that fails a gate says exactly which gate and why. Two modes: **full** (three timeframes) and **simple** (one pair, timeframe and session).

### Time zones: New York (the strategy) and Manila (you)

All the strategy's times are New York time. The app evaluates its rules on the New York clock and shows your Manila time next to it everywhere (reports, schedule, alerts). Manila is 12 hours ahead of New York while the US is on summer time (EDT) and 13 hours ahead in winter (EST), because Manila does not change its clocks. The US changes on the second Sunday of March and the first Sunday of November (2026: 8 March and 1 November).

| Event | New York (rule) | Manila, US summer | Manila, US winter |
|---|---|---|---|
| App run before the window (planned) | 12:30 AM | 12:30 PM | 1:30 PM |
| Entry window opens, pre-London analysis | 1:00 AM | 1:00 PM | 2:00 PM |
| London opens | 3:00 AM | 3:00 PM | 4:00 PM |
| New York opens | 8:00 AM | 8:00 PM | 9:00 PM |
| Last entry | 10:30 AM | 10:30 PM | 11:30 PM |
| London ends | 12:00 PM | 12:00 AM (next day) | 1:00 AM (next day) |
| Daily and weekly candles close | 5:00 PM | 5:00 AM (next day) | 6:00 AM (next day) |
| Weekly bias run (Sunday market open) | Sunday 5:00 PM | Monday 5:00 AM | Monday 6:00 AM |

The entry window is on the same calendar day in Manila, so Monday to Wednesday is the same in both. London's clocks change on different dates from the US, so for 1 to 3 weeks each spring and autumn London opens at 4:00 AM New York time instead of 3:00 AM (2026: 8 to 29 March and 25 October to 1 November). The window stays on the New York clock because that is his rule.

## 4. "Reading the charts": how

The app does **not** read screenshots. It reads candle data (open, high, low, close) and computes everything, because the strategy is built from exact rules on candles (body closes, highs and lows, pips), and a screenshot reader would guess. To let you check it, the app **draws its own annotated chart** (structure lines, AOI boxes, EMA, signal candle, stop and target) in the same colours as the videos, and you compare it with your TradingView.

An optional later step is a vision-model cross-check on a screenshot as a sanity layer. It is not the engine.

## 5. Technology recommendation

| Part | Recommended | Why |
|---|---|---|
| Language | Python 3.12 | Already installed; best data and charting libraries; easy to test |
| Data handling | pandas, numpy | Candle series, ATR, EMA |
| Data source | MetaTrader 5 (if you use it), else OANDA; see section 6 | Real broker candles, free |
| Chart images | mplfinance or matplotlib (PNG), Plotly (interactive HTML) | Annotated charts |
| Report | Jinja2 templates to HTML (printable to PDF with Edge, as for the guide) | Reuses what we already built |
| Config | A settings file (YAML or TOML) | Every parameter in the spec is adjustable |
| Tests | pytest | The spec is written as tests first |
| Storage | SQLite or Parquet cache | Avoid re-downloading history |
| Scheduling | Windows Task Scheduler running the CLI | Sunday bias run, daily early-morning run |
| Alerts (later) | Desktop toast, Telegram or email | "Price reached your AOI", "signal closed" |
| UI (later) | Streamlit or a small local web page | Only after the engine is trusted |

Start as a **command-line tool that writes an HTML report**. A fancy UI before the engine is right would hide mistakes.

## 6. Data source options

All three give OHLC candles. Prices differ by a few points between brokers, so the strategy tests use tolerances. Check current terms and limits before committing; they change.

| Option | Good | Watch out for |
|---|---|---|
| **MetaTrader 5 Python package** (`pip install MetaTrader5`) | Free; real broker candles; the course already uses MT5; many forex brokers' server day ends at 5 PM New York (check yours), which matches the strategy's boundary | Windows only; needs the MT5 terminal installed and logged in (a demo account works); occasional connection quirks reported by users |
| **OANDA v20 REST API** | Clean REST candles (up to 5,000 per request), practice account for testing, token-based | Needs a v20 account (not offered by every OANDA entity); rate limits; verify availability in your country |
| **Twelve Data** (free tier) | Simple REST, many symbols | Free tier is small (about 800 requests a day and a low per-minute cap as of the last check) and for non-display use only; 21 pairs across 7 timeframes would use it quickly |
| Others (Dukascopy exports, yfinance) | Free history | Less reliable or unofficial; fine for experiments, not for the live run |

Recommendation: **MT5 demo account** if you already have or will have MT5; otherwise **OANDA practice**. Decide in phase 0.

Sources to re-check: the [MetaTrader 5 Python integration docs](https://www.mql5.com/en/docs/integration/python_metatrader5/), [OANDA's developer documentation](https://developer.oanda.com/rest-live-v20/introduction/), and [Twelve Data pricing](https://twelvedata.com/pricing).

## 7. Phases

Each phase ends with something you can run and check. Sizes: S (small), M (medium), L (large).

| Phase | Deliverable | Done when | Size |
|---|---|---|---|
| **0 Foundation** | `app/` folder, Python environment, settings file, data connector for the chosen source, candle store with the New York 5 PM day/week boundary, test setup | You can pull EURUSD candles for all seven timeframes and the daily candle close time is 5 PM New York | M |
| **1 Structure** | Module B: pivots, the state machine, snake trick, confirmed vs current; plus a first annotated chart | The EURUSD 4H and AUDJPY examples from the videos reproduce within tolerance; wick-only breaks do nothing; your TradingView agrees on 3 to 5 pairs | L |
| **2 Alignment, zone, bias** | Module C: two-in-a-row alignment, grades, zones, weekly bias stored on Sunday | W/D/4H reads and zones match the AUDJPY example; bias does not flip mid-week without a break | S |
| **3 AOI finder** | Module D: candidates, touches, 5 to 60 pips, inside-zone, merging, roles, extras | AUDJPY merged AOIs near 97.25 to 97.55 and 96.62 to 96.93 appear; invalid ones are dropped with a reason | L |
| **4 Signals and patterns** | Module E: candle shapes, engulfing grades, break and retest, head and shoulders, chase flag | Synthetic tests pass; no signal ever uses an unclosed candle; patterns only after the structure shift | L |
| **5 Verdict and plan** | Module F/G: gates, verdicts, grades, stop, target, R:R, lot size, checklist | The NZDUSD and EURAUD numbers and the lot-size cases reproduce; every "no trade" names its gate | M |
| **6 Report** | HTML report and summary table, JSON, annotated charts for all pairs in the Blue list | One command produces the full report for 21 pairs | M |
| **7 Simple mode and settings** | Single-timeframe mode; all parameters in the settings file | Switching modes changes only the gates described in the spec | S |
| **8 Validation** | Side-by-side checks with your charts; replay test; a back-test harness that counts signals and R outcomes | You trust the structure and AOI output on real pairs; signal frequency looks sane; no look-ahead | M |
| **9 Automation and alerts** | Scheduled Sunday and daily runs; alert levels pushed to you | Reports appear without you running anything; alerts fire at AOI edges and closed signals | M |
| **10 UI and extras** | Small local UI; news calendar flag; new videos folded in | Only if you want it | M |

Phases 1 to 5 are the core. If time is short, phases 0 to 6 give a usable tool.

## 8. How we will work

1. **Spec first.** Each phase starts from the matching part of `docs/ANALYSIS-SPEC.md`. If a rule is unclear, we settle it there before writing code.
2. **Tests before code** for each rule, using hand-built candles and the creator's worked examples.
3. **Look at the picture.** After each phase we render the annotated chart and you compare it with TradingView. A disagreement means adjust a parameter or fix the rule; it is not hidden.
4. **One small step at a time.** I build a phase, show the output, then you approve or change it.
5. **Keep the docs true.** New videos update `strategy/strategy.md`, then the spec, then the code.
6. **Safety.** No order placement. No keys or passwords in the repo (use environment variables). The report always says it is analysis, not advice.

Code location: a folder `app/` in this repository, so the study, the spec and the code stay together.

## 9. Risks and how we handle them

| Risk | Handling |
|---|---|
| The rules are partly subjective (swing, touch, AOI box) | Pick defaults, make them settings, verify visually, tune on real charts |
| Candle boundaries differ by feed (day end, daylight saving) | Build candles on the New York 5 PM boundary and test it first |
| Different brokers show slightly different prices | Test with tolerances; use the same source for analysis and execution |
| Overfitting when tuning | Tune only on structure and AOI agreement with your charts; keep the back-test for sanity, not optimisation |
| The strategy may not be profitable | The app says what the rules say; it never claims results. Use a demo account first |
| Over-reliance on the report | Every pass or fail has a reason you can check; no black boxes |
| Data terms and limits | Read the provider's terms; cache history; stay within limits |
| The creator's unpublished "entry signal" | Marked as a gap; the app uses the public confirmation only |
| Public repository | The repo is public; keep settings, keys and personal data out. Consider making it private before adding app code |

## 10. Decisions I need from you

Recommended defaults are in bold; say "go with the defaults" to accept them all.

1. **Data source:** **MetaTrader 5 demo** or OANDA practice? Which broker do you use or plan to use?
2. **Where it runs:** **your Windows PC** (the MT5 route needs it) or an always-on cloud machine later?
3. **First output:** **HTML report with annotated charts**, then notifications, then a UI.
4. **Pairs:** **the 21 pairs on his Blue list** (editable) or your own list?
5. **Starting mode:** **both modes**, full first.
6. **Risk per trade and account mode:** your number and which mode (`standard`, `small_account`, `prop`). The videos give none for a standard account; the prop preset is 2% first trade then the same; I will use a placeholder until you confirm.
7. **Run schedule:** **Sunday 5 PM New York for the weekly bias (Monday 5 AM Manila in US summer, 6 AM in winter), then each trading day at 12:30 AM New York (12:30 PM Manila in summer, 1:30 PM in winter)**, just before his 1:00 AM window, plus on demand. Both clocks are shown in every report. Display zone: Asia/Manila (confirmed).
8. **Repository:** keep it **public** and put code in `app/`, or make it private first?

## 11. First steps once you confirm

1. Phase 0: create `app/`, set up the environment and pull your first candles.
2. Show you the candle check (daily close at 5 PM New York) and one annotated chart skeleton.
3. Start phase 1 (structure) and compare with your TradingView.
