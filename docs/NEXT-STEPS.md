# Next steps

Where the project stands and what to do next. Read this first when continuing on another device or in a new Claude Code session.

## Status (2026-10-09)

- **Strategy:** 13 fxalexg videos studied and merged into `strategy/strategy.md`. Section 1 holds the **core rule set** that app v1 builds: one answer per topic, newer upload wins. Account modes, the one-timeframe mode, counter-weekly trades and other extras are **parked** (kept as history, not built).
- **Guide:** `Confluence-Trading-Guide.pdf` version 1.7, 42 pages, covers all 13 videos. Optional parts are labelled.
- **Videos:** no more planned. The 16 candidates in `docs/VIDEOS.md` are all older (2021 to 2025) and could only fill gaps, not change rules.
- **App:** not built yet. All 7 decisions in `docs/BUILD-PLAN.md` section 10 are confirmed (the defaults): MT5 demo, runs on a Windows PC, HTML report with annotated charts, his 21 pairs, 1% risk placeholder, Sunday and daily schedule, public repo with code in `app/`.

## What the app will give you

For each pair: a verdict (SIGNAL, WATCH, WAIT_FOR_SESSION or NO_TRADE with the reason), chart pictures of the weekly, daily and signal timeframe with the 50 EMA, structure lines, AOI boxes and numbered confluence markers, a checklist explaining each confluence, and the plan (entry, stop, target, R:R, lot size). Prices come from MT5, not from TradingView: TradingView has no data API and scraping it is not allowed. You use TradingView to check and place trades. Details: `docs/ANALYSIS-SPEC.md` section 9.

## Your steps

1. **Decisions** - done (defaults).
2. **Set up an MT5 demo account** (about 15 minutes)
   1. Pick a forex broker that offers MetaTrader 5 with a free demo account.
   2. Install MT5 on the Windows PC that will run the app. Open the demo account and log in.
   3. Check the broker's day ends at 5 PM New York: in Market Watch the server time should be **7 hours ahead of New York** (server midnight = 5 PM New York). If not, note the difference.
   4. In Market Watch, right-click and choose "Show All". Note the exact pair names (some brokers add endings such as `EURUSD.m`).
   5. Send Claude: the time difference and the pair names. Never send or commit the MT5 password, account number or any login. The app reads candles from the running, logged-in MT5, so it never needs them.
3. **Draw your reference AOIs** (about 1 to 2 hours; the most important step for tuning)
   1. Read Parts 5, 6 and 7 of the guide.
   2. Pick 3 to 5 pairs (for example EURUSD, GBPUSD, AUDJPY and two of your own).
   3. In TradingView, on the weekly and daily, mark HH/HL or LH/LL on candle bodies, then draw the AOIs inside the zone: 3 or more touches, 5 to 60 pips tall, at most 3 per chart.
   4. Save a screenshot of each chart and write each box down like this:
      ```
      EURUSD | Daily | AOI 1.1650 - 1.1685 | 4 touches | drawn 2026-10-12
      ```
   5. Send these to Claude. Do not change them after seeing the app's boxes; they are the answer key for phase 3.
4. **Say "start Phase 0".** Claude creates `app/`, connects to MT5, pulls candles and shows that the daily candle closes at 5 PM New York.
5. **Check each phase.** After each phase Claude shows the output (phase 1: trend lines; phase 3: AOI boxes). Compare with TradingView and reply "OK" or what looks wrong. Settings are tuned, never special-cased per pair. Phases: `docs/BUILD-PLAN.md` section 7.

## Continuing on another device

1. One-time setup: follow `docs/SETUP.md`, then run `.\scripts\setup.ps1`.
2. `git clone https://github.com/xtiannjose/TradingGuide.git` (or `git pull` if already cloned).
3. Open the folder in VS Code with Claude Code and say: "read docs/NEXT-STEPS.md and continue".
4. Pull before you start working and push when you finish, so both devices stay in step.
5. The app must run on the Windows PC where MT5 is installed and logged in.
6. The downloaded videos and per-video study notes stay on the first PC (they are never committed). They are not needed to build the app, only to study more videos.
