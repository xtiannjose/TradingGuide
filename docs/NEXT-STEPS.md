# Next steps

Where the project stands and what to do next. Read this first when continuing on another device or in a new Claude Code session.

## Status (2026-10-10)

- **Strategy:** 13 fxalexg videos studied and merged into `strategy/strategy.md`. Section 1 holds the **core rule set** that app v1 builds: one answer per topic, newer upload wins. Account modes, the one-timeframe mode, counter-weekly trades and other extras are **parked** (kept as history, not built).
- **Guide:** `Confluence-Trading-Guide.pdf` version 1.7, 42 pages, covers all 13 videos. Optional parts are labelled.
- **Videos:** no more planned. The 16 candidates in `docs/VIDEOS.md` are all older (2021 to 2025) and could only fill gaps, not change rules.
- **App:** first full version built (2026-10-10), then a second pass the same day. Checked so far: the data layer, the structure reading (reproduces the course examples), the candle shapes (0 violations on 300 real candles), the rule limits on boxes (0 violations on 21 pairs) and the answer-key comparison. Not yet checked by you: whether the boxes and verdicts match your own judgement.
  - **Open it:** double-click `Start-TradingGuide.cmd` (MetaTrader 5 open and logged in). It opens a TradingView-style terminal at http://127.0.0.1:8765/: watchlist of the 21 pairs, candle chart for 7 timeframes with the 50 EMA, structure lines, area-of-interest boxes, your own boxes dashed, optional swing-path and pattern layers, numbered markers that match the checklist, verdict, plan and lot size, alerts, an all-pairs table, light and dark themes. "Scan all" refreshes everything from MT5 in about 10 seconds.
  - **Engine** (`app/`): `candles.py`, `structure.py`, `aoi.py`, `signals.py`, `timegate.py`, `verdict.py`, `scan.py`, `backtest.py`, `validate.py`, `signal_gallery.py`, `lotsize.py`, `alerts.py`, `params.py` (every number in one place). 34 tests pass.
  - **Structure reading (decided by Claude from your "latest swing" wish, change in Settings):** weekly follows the course rule so the bias stays stable; daily and lower follow the latest swing. It reproduces every course example. Trade-off: the daily then flips 15 to 23 times a year instead of 6 to 11, so more pairs show "counter-trend".
  - **Right now (Friday close):** GBPJPY (grade A, a 2H rejection at a 4H resistance box) is waiting for Monday's pre-London hour. Most other pairs are WATCH or NO_TRADE.
  - **Answer-key check** (`python app/validate.py`): AUDUSD matches through a merged weekly+daily box (44% of yours); GBPUSD matches the tight core (38%) because the daily zone ends just above the bottom of your 60-pip box; AUDJPY's daily box stays visible for its retest after today's close above it, and only the weekly box counts as live.
  - **Backtest, honest result** (`python app/backtest.py all --weeks 12`, paper trades, no spread): 91 trades, 20 wins (22%), average -0.31R. Break-even at 1:2 needs about 33%. The weak spot is **short stops**: the 58 trades with stops under 15 pips averaged -0.50R (16% wins); the 33 trades with stops of 15 pips or more were about break-even (+0.01R and +0.05R). By signal timeframe the 15m and 2H signals did worst, the 30m, 4H and daily best. Twelve weeks and a few dozen trades is a small sample in one market regime, so this is a pointer for tuning and not a verdict on the strategy.
  - **Tuning comparison** (same 12 weeks, 21 pairs, in-sample, so a pointer and not proof): baseline 91 trades, 20 wins, -0.31R average; dropping the 15m and 2H confirmations 79 trades, -0.18R; a minimum stop of 0.25 daily ATR 43 trades, -0.13R; both 39 trades, -0.06R. Every version stayed at or below zero and the sample is too small to tell -0.06R from zero (the error on the average is about 0.2R). The one pattern that held in every version: trades with stops under 15 pips almost never won. So the app now defaults to a **minimum stop of 0.25 daily ATR** (Settings, "Minimum stop"; 0 turns it off; an app default consistent with the course's preference for a wide stop, not his rule). The 15m and 2H confirmations are left on because the course lists them as entry timeframes and the evidence (10 and 19 trades) is thin.
  - **Still open for you:** whether 15m and 2H confirmations should count; the GBPUSD zone edge and the "broken box" rule; and whether to test the whole thing on a longer history (the 15m data only goes back about 12 weeks, so a longer test would use the 1H for entries).
  - All 7 decisions in `docs/BUILD-PLAN.md` section 10 are confirmed (the defaults), except the risk placeholder, which the owner will set (10% or 20%).

## What the app will give you

For each pair: a verdict (SIGNAL, WATCH, WAIT_FOR_SESSION or NO_TRADE with the reason), chart pictures of the weekly, daily and signal timeframe with the 50 EMA, structure lines, AOI boxes and numbered confluence markers, a checklist explaining each confluence, and the plan (entry, stop, target, R:R, lot size). Prices come from MT5, not from TradingView: TradingView has no data API and scraping it is not allowed. You use TradingView to check and place trades. Details: `docs/ANALYSIS-SPEC.md` section 9.

The app and its tools work with the market closed (analysis for the next open). Only price alerts need the market open, because they watch live ticks.

## Your to-do list

Claude keeps this current. Only the items Claude cannot do for you are listed as open.

**Open (needs you)**

- [ ] **Try the terminal (about 10 minutes) and tell Claude what feels wrong, one item at a time.** Double-click `Start-TradingGuide.cmd`. Open GBPUSD, AUDUSD and AUDJPY on D and W: do the boxes (solid) land near your own (dashed)? Does the verdict make sense? The list of fixes you send becomes the next work.
- [ ] **Check the structure reading (about 5 minutes).** Claude chose the default for you (see Status). Look at AUDJPY, GBPUSD and AUDUSD on D: are HH/HL and LL/LH where you would draw them? If not, tell Claude, or switch in Settings between "Weekly: course rule, lower: latest swing", "Latest swing everywhere" and "Course rule everywhere" and press Scan all. Pictures of all four readings: `app/out/compare/` (made by `python app/chart.py <PAIR> --compare`).
- [ ] **Test the pop-up once:** run `python app/alerts.py --test` (the terminal also shows a toast and plays a beep when an alert fires, and can send a Windows notification if you allow it). Claude cannot see your screen, so a window must appear for you. Then, with MT5 open and the market open, run `python app/alerts.py`; it watches the six levels in `app/settings.toml` (the edges of your three daily boxes). Edit or add levels there.
- [ ] **Review Claude's weekly and daily draft boxes** (version 2: every box is 35 pips or less, the tightest cluster of at least 3 swing points, as the course prefers). Pictures: `app/out/ideas/` (`GBPUSD_boxes.png`, `AUDUSD_boxes.png`, `AUDJPY_boxes.png`; weekly on the left, daily on the right, your box in green). The numbers are in `docs/REFERENCE-AOIS.md`. Reply with the boxes you agree with and Claude moves them into your key. Best done before phase 3, because the key is what tunes the AOI finder.
- [ ] **Settle your risk per trade.** The owner said about 10% or 20%. Run `python app/lotsize.py EURUSD --stop 25 --balance <your real balance>` to see lots and the drawdown after 5 and 10 stops in a row for each level (at 10%, five stops in a row leave 59% of the balance; at 20%, 33%). Tell Claude the one number, the balance and the account currency before phase 5. The app then uses that same % on every trade.

- [ ] **Push to GitHub yourself:** run `git push origin main` in the repo folder. A git guard hook on this PC blocks Claude from pushing to `main`, and Claude's permission layer refuses to edit that hook, so the commits are local until you push. Or say "push a branch" and Claude pushes a branch for you to merge.

**Later**

- [ ] **Optional, when ready:** run `.\scripts\schedule-scan.ps1` to scan automatically before the window. Confirm the PC stays on and MT5 stays logged in at the run times, 12:30 PM Manila (1:30 PM in US winter) each trading day and Monday 5 AM Manila (6 AM in winter) for the weekly bias.
- [ ] Optional phone alerts: Telegram is built and off by default. To turn it on, create a bot with @BotFather, then set the Windows environment variables `TG_BOT_TOKEN` and `TG_CHAT_ID` and restart the terminal. The token stays in your environment and is never committed. Nothing is sent unless both are set.
- [ ] Rerun `python app/phase0.py` once after 1 November 2026, when the US clocks change, to confirm the broker clock is still New York + 7 h.
- [ ] Optional: decide if you want a news-calendar flag (the course only says to look at the red folders).

**Done**

- [x] Whole app built, with a browser terminal, alerts (pop-up, toast, optional Telegram), lot size, backtest, answer-key validation and a Windows scheduler script.
- [x] Structure reading chosen and tested against the course examples.
- [x] MT5 demo account, broker clock New York + 7 h (confirmed from the candles and from the last tick of the week), 21 pairs with plain names.
- [x] Daily reference boxes for GBPUSD, AUDUSD and AUDJPY (`docs/REFERENCE-AOIS.md`).
- [x] Weekly boxes drafted by Claude with confluences, kept apart from your key.
- [x] Lot size calculator and price alert watcher built.
- [x] Work committed locally.

## Setup steps (done; kept for a new machine)

1. **Decisions** - done (defaults).
2. **Set up an MT5 demo account** - done 2026-10-10.
   1. Pick a forex broker that offers MetaTrader 5 with a free demo account.
   2. Install MT5 on the Windows PC that will run the app. Open the demo account and log in.
   3. Check the broker's day ends at 5 PM New York: the server time should be **7 hours ahead of New York** (server midnight = 5 PM New York). `python app/phase0.py` checks this. If it differs, change `server_ny_offset_hours` in `app/settings.toml`.
   4. In Market Watch, right-click and choose "Show All". `python app/phase0.py` lists any pair name the broker does not have (some brokers add endings such as `.m`; set `symbol_suffix` in `app/settings.toml`).
   5. Never send or commit the MT5 password, account number or any login. The app reads candles from the running, logged-in MT5, so it never needs them.
3. **Draw your reference AOIs** - done 2026-10-10 for 3 pairs, daily only (`docs/REFERENCE-AOIS.md`). The steps below stay for adding more.
   1. Read Parts 5, 6 and 7 of the guide.
   2. Pick 3 to 5 pairs (for example EURUSD, GBPUSD, AUDJPY and two of your own).
   3. In MT5 or TradingView, on the weekly and daily, mark HH/HL or LH/LL on candle bodies, then draw the AOIs inside the zone: 3 or more touches, 5 to 60 pips tall, at most 3 per chart. In MT5, double-click a rectangle to read its two prices.
   4. Write each box down like this:
      ```
      EURUSD | Daily | AOI 1.1650 - 1.1685 | 4 touches | drawn 2026-10-12
      ```
   5. Send these to Claude. Do not change them after seeing the app's boxes; they are the answer key for phase 3.
4. **Phases 0 and 1** - built 2026-10-10. Next: your phase 1 eye check (to-do list above), then say "start Phase 2".
5. **Check each phase.** After each phase Claude shows the output (phase 1: trend lines; phase 3: AOI boxes). Compare with your charts and reply "OK" or what looks wrong. Settings are tuned, never special-cased per pair. Phases: `docs/BUILD-PLAN.md` section 7.

## Continuing on another device

1. One-time setup: follow `docs/SETUP.md`, then run `.\scripts\setup.ps1`.
2. `git clone https://github.com/xtiannjose/TradingGuide.git` (or `git pull` if already cloned).
3. Open the folder in VS Code with Claude Code and say: "read docs/NEXT-STEPS.md and continue".
4. Pull before you start working and push when you finish, so both devices stay in step.
5. The app must run on the Windows PC where MT5 is installed and logged in.
6. The downloaded videos and per-video study notes stay on the first PC (they are never committed). They are not needed to build the app, only to study more videos.
