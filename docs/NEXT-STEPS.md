# Next steps

Where the project stands and what to do next. Read this first when continuing on another device or in a new Claude Code session.

## Status (2026-10-10)

- **Strategy:** 13 fxalexg videos studied and merged into `strategy/strategy.md`. Section 1 holds the **core rule set** that app v1 builds: one answer per topic, newer upload wins. Account modes, the one-timeframe mode, counter-weekly trades and other extras are **parked** (kept as history, not built).
- **Guide:** `Confluence-Trading-Guide.pdf` version 1.7, 42 pages, covers all 13 videos. Optional parts are labelled.
- **Videos:** no more planned. The 16 candidates in `docs/VIDEOS.md` are all older (2021 to 2025) and could only fill gaps, not change rules.
- **App:** phases 0 and 1 built (2026-10-10). Phase 2 (alignment, zone, weekly bias) is next, once the phase 1 eye check below is answered.
  - Phase 0, `app/candles.py`: MT5 candles for all seven timeframes on the New York 5 PM boundary. `python app/phase0.py` is the check; it passes, and it also works with the market closed.
  - Phase 1, `app/structure.py`: HH/HL/LH/LL per timeframe. `python app/chart.py EURUSD` draws it. Swing threshold 0.5 x ATR, tuned on the course's EURUSD and AUDJPY examples. A rule check over all 21 pairs and 3 timeframes found no violations.
  - Tools: `python app/lotsize.py EURUSD --stop 25` (lot size and risk table), `python app/alerts.py` (pop-up when a price is crossed; levels are the `[[alert]]` blocks in `app/settings.toml`).
  - All 7 decisions in `docs/BUILD-PLAN.md` section 10 are confirmed (the defaults): MT5 demo, runs on a Windows PC, HTML report with annotated charts, his 21 pairs, 1% risk placeholder, Sunday and daily schedule, public repo with code in `app/`.

## What the app will give you

For each pair: a verdict (SIGNAL, WATCH, WAIT_FOR_SESSION or NO_TRADE with the reason), chart pictures of the weekly, daily and signal timeframe with the 50 EMA, structure lines, AOI boxes and numbered confluence markers, a checklist explaining each confluence, and the plan (entry, stop, target, R:R, lot size). Prices come from MT5, not from TradingView: TradingView has no data API and scraping it is not allowed. You use TradingView to check and place trades. Details: `docs/ANALYSIS-SPEC.md` section 9.

The app and its tools work with the market closed (analysis for the next open). Only price alerts need the market open, because they watch live ticks.

## Your to-do list

Claude keeps this current. Only the items Claude cannot do for you are listed as open.

**Open (needs you)**

- [ ] **Phase 1 eye check (about 5 minutes).** Claude has reviewed 10 of the 12 pictures and run the rule check, but cannot see your TradingView or judge how you would mark a level. Open `app/out/AUDJPY_D.png`, `GBPUSD_D.png` and `AUDUSD_D.png` (made by `python app/chart.py <PAIR>` with MT5 open) and say whether the HH/HL or LL/LH lines are where you would draw them. Reply "OK" or the pair, timeframe and what is wrong. Known miss: the AUDJPY daily of Sept 2025 skips a 0.28 dip that the course counts as the HL; if you see many of those, the swing threshold goes down.
- [ ] **Test the pop-up once:** run `python app/alerts.py --test`. Claude cannot see your screen, so a window must appear for you. Then, with MT5 open and the market open, run `python app/alerts.py`; it watches the six levels in `app/settings.toml` (the edges of your three daily boxes). Edit or add levels there.
- [ ] **Review Claude's weekly and daily draft boxes** in `docs/REFERENCE-AOIS.md`. Move the ones you agree with into your key, strike out the rest. Best done before phase 3, because the key is what tunes the AOI finder.
- [ ] **Choose your risk per trade.** Run `python app/lotsize.py EURUSD --stop 25 --balance <your real balance>` to see a table of risk levels. Then tell Claude the risk %, balance and account currency before phase 5. The demo account's small balance cannot risk 1% on a 25-pip stop (the smallest lot is already more); use your real balance.

**Later**

- [ ] Before phase 9: confirm the PC stays on and MT5 stays logged in at the run times, 12:30 PM Manila (1:30 PM in US winter) each trading day and Monday 5 AM Manila (6 AM in winter) for the weekly bias.
- [ ] Before phase 9: say whether you also want alerts on your phone (Telegram). A bot token must never be committed; it goes in an environment variable.
- [ ] Rerun `python app/phase0.py` once after 1 November 2026, when the US clocks change, to confirm the broker clock is still New York + 7 h.
- [ ] Before phase 10 (optional): decide if you want a small local UI and a news-calendar flag.

**Done**

- [x] MT5 demo account, broker clock New York + 7 h (confirmed from the candles and from the last tick of the week), 21 pairs with plain names.
- [x] Daily reference boxes for GBPUSD, AUDUSD and AUDJPY (`docs/REFERENCE-AOIS.md`).
- [x] Weekly boxes drafted by Claude with confluences, kept apart from your key.
- [x] Lot size calculator and price alert watcher built.
- [x] Work committed and pushed to GitHub.

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
