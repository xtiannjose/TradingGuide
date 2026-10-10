# Next steps

Where the project stands and what to do next. Read this first when continuing on another device or in a new Claude Code session.

## Status (2026-10-10)

- **Strategy:** 13 fxalexg videos studied and merged into `strategy/strategy.md`. Section 1 holds the **core rule set** that app v1 builds: one answer per topic, newer upload wins. Account modes, the one-timeframe mode, counter-weekly trades and other extras are **parked** (kept as history, not built).
- **Guide:** `Confluence-Trading-Guide.pdf` version 1.7, 42 pages, covers all 13 videos. Optional parts are labelled.
- **Videos:** no more planned. The 16 candidates in `docs/VIDEOS.md` are all older (2021 to 2025) and could only fill gaps, not change rules.
- **App:** first full version built (2026-10-10), in one pass. All phases exist; only phase 0 and the phase 1 structure have been checked against real charts. The rest is a draft to tune one item at a time.
  - **Open it:** double-click `Start-TradingGuide.cmd` (MetaTrader 5 open and logged in). It opens a TradingView-style terminal at http://127.0.0.1:8765/: watchlist of the 21 pairs, candle chart for 7 timeframes with the 50 EMA, structure lines, area-of-interest boxes, your own boxes dashed, numbered markers that match the checklist, verdict, plan and lot size, alerts, an all-pairs table, light and dark themes. "Scan all" refreshes everything from MT5 in about 15 seconds.
  - **Engine** (`app/`): `candles.py` (data), `structure.py`, `aoi.py`, `signals.py`, `timegate.py`, `verdict.py` (alignment, bias, verdict, stop, target, R:R), `scan.py`, `backtest.py`, `lotsize.py`, `alerts.py`, `params.py` (every number in one place). 32 tests pass.
  - **First look at real data:** 21 pairs scanned; most are WATCH or NO_TRADE (counter-trend, or the next structure point is under 1:2), which is what the rules should say on a Friday-close snapshot. A 8-week replay gave 0.25 to 1 signals a week per pair. It is a sanity check on a few trades, not evidence the strategy works.
  - **Answer-key check** (`python app/validate.py`, after a scan): 0 rule violations on 21 pairs. Against your three daily boxes: AUDUSD matches through a merged weekly+daily box (0.71082 to 0.71241, 44% of yours); GBPUSD matches the tight core (1.3197 to 1.3220, 38%) because the daily zone ends at 1.3197, just above the bottom of your 60-pip box; AUDJPY's daily box (110.14 to 110.48, 58% of yours) is flagged broken by today's close above it, so only the weekly box (109.86 to 110.17) counts as live. These gaps are the first tuning items.
  - **Known first-pass limits:** the box finder and signal shapes use app defaults that nobody has checked against the owner's charts yet; the structure reading has an open choice (course rule or latest swing); the chart labels can overlap when boxes sit close together; the engine ignores the spread and news.
  - All 7 decisions in `docs/BUILD-PLAN.md` section 10 are confirmed (the defaults), except the risk placeholder, which the owner will set (10% or 20%).

## What the app will give you

For each pair: a verdict (SIGNAL, WATCH, WAIT_FOR_SESSION or NO_TRADE with the reason), chart pictures of the weekly, daily and signal timeframe with the 50 EMA, structure lines, AOI boxes and numbered confluence markers, a checklist explaining each confluence, and the plan (entry, stop, target, R:R, lot size). Prices come from MT5, not from TradingView: TradingView has no data API and scraping it is not allowed. You use TradingView to check and place trades. Details: `docs/ANALYSIS-SPEC.md` section 9.

The app and its tools work with the market closed (analysis for the next open). Only price alerts need the market open, because they watch live ticks.

## Your to-do list

Claude keeps this current. Only the items Claude cannot do for you are listed as open.

**Open (needs you)**

- [ ] **Try the terminal (about 10 minutes) and tell Claude what feels wrong, one item at a time.** Double-click `Start-TradingGuide.cmd`. Open GBPUSD, AUDUSD and AUDJPY on D and W: do the boxes (solid) land near your own (dashed)? Does the verdict make sense? The list of fixes you send becomes the next work.
- [ ] **Pick how the structure should be read (about 5 minutes).** Your first eye check said the levels were too tied to older HH/HL and LL/LH. Open the pictures in `app/out/compare/` (`AUDUSD_D.png`, `AUDJPY_D.png`, `GBPUSD_D.png` and the `_W.png` ones). Each shows the same candles read four ways: A is the course rule as built, B lets the HL/LH follow the latest swing, C and D are A and B with finer swings. Reply with the letter that matches how you would mark it, or say what is still wrong. The course (video 12) keeps the HL behind the HH until a new HH forms (A), while B flips earlier, on the latest swing; you decide.
- [ ] **Test the pop-up once:** run `python app/alerts.py --test` (the terminal also shows a toast and plays a beep when an alert fires, and can send a Windows notification if you allow it). Claude cannot see your screen, so a window must appear for you. Then, with MT5 open and the market open, run `python app/alerts.py`; it watches the six levels in `app/settings.toml` (the edges of your three daily boxes). Edit or add levels there.
- [ ] **Review Claude's weekly and daily draft boxes** (version 2: every box is 35 pips or less, the tightest cluster of at least 3 swing points, as the course prefers). Pictures: `app/out/ideas/` (`GBPUSD_boxes.png`, `AUDUSD_boxes.png`, `AUDJPY_boxes.png`; weekly on the left, daily on the right, your box in green). The numbers are in `docs/REFERENCE-AOIS.md`. Reply with the boxes you agree with and Claude moves them into your key. Best done before phase 3, because the key is what tunes the AOI finder.
- [ ] **Settle your risk per trade.** The owner said about 10% or 20%. Run `python app/lotsize.py EURUSD --stop 25 --balance <your real balance>` to see lots and the drawdown after 5 and 10 stops in a row for each level (at 10%, five stops in a row leave 59% of the balance; at 20%, 33%). Tell Claude the one number, the balance and the account currency before phase 5. The app then uses that same % on every trade.

- [ ] **Push to GitHub yourself:** run `git push origin main` in the repo folder. A git guard hook on this PC blocks Claude from pushing to `main`, and Claude's permission layer refuses to edit that hook, so the commits are local until you push. Or say "push a branch" and Claude pushes a branch for you to merge.

**Later**

- [ ] **Optional, when ready:** run `.\scripts\schedule-scan.ps1` to scan automatically before the window. Confirm the PC stays on and MT5 stays logged in at the run times, 12:30 PM Manila (1:30 PM in US winter) each trading day and Monday 5 AM Manila (6 AM in winter) for the weekly bias.
- [ ] Before phase 9: say whether you also want alerts on your phone (Telegram). A bot token must never be committed; it goes in an environment variable.
- [ ] Rerun `python app/phase0.py` once after 1 November 2026, when the US clocks change, to confirm the broker clock is still New York + 7 h.
- [ ] Before phase 10 (optional): decide if you want a small local UI and a news-calendar flag.

**Done**

- [x] Whole app built in a first version, with a browser terminal, alerts, lot size, backtest and a Windows scheduler script.
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
