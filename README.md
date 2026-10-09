# TradingGuide

A study project that turns trading-strategy videos into (1) a plain-English guide and (2) a specification for a forex analysis app that reports the strategy's confluences for a list of pairs.

Educational only. Not financial advice. Unofficial: not affiliated with the creators of the videos studied.

## What is here

| Path | What it is |
|---|---|
| `Confluence-Trading-Guide.pdf` | 42-page beginner guide (version 1.7) to the strategy of all thirteen videos. Start here if you want to learn it. |
| `strategy/strategy.md` | The merged rule set: exact definitions, numbers, conflicts, gaps. The source of truth for the app. |
| `docs/NEXT-STEPS.md` | Current status, your next steps, and how to continue on another device. Read this first. |
| `docs/BUILD-PLAN.md` | The plan for the chart-analysis app: study digest, architecture, data options, phases, decisions needed. |
| `docs/ANALYSIS-SPEC.md` | App-ready spec: exact rules, parameters, outputs and tests the app must implement. |
| `docs/VIDEOS.md` | Videos studied, and which video time range each study part covers. |
| `docs/SETUP.md` | One-time machine setup (tools, plugin, GitHub login). |
| `docs/WORKFLOW.md` | Step by step: study a new video, merge it, rebuild the PDF, push. |
| `docs/AGENT-PROMPT.md` | The prompt template used for the study agents. |
| `scripts/` | `setup.ps1` (check or install tools), `study-video.ps1` (download + captions + frames), `segment.py` (clean and split captions). |
| `guide-src/` | Source that builds the PDF (HTML + SVG diagrams, printed by Edge). |
| `app/` | The chart-analysis app (Python, reads MT5 candles): candle store, market structure, chart pictures, lot size calculator, price alerts, tests. See `docs/SETUP.md`. |
| `docs/REFERENCE-AOIS.md` | The owner's hand-drawn boxes (the answer key for tuning) and Claude's separate draft ideas with confluences. |
| `CLAUDE.md` | Standing instructions for Claude Code sessions in this repo. |

## Quick start

```powershell
git clone https://github.com/xtiannjose/TradingGuide.git
cd TradingGuide
.\scripts\setup.ps1            # checks the machine; add -Install to fix what is missing
```

Then see `docs/WORKFLOW.md` to study another video, or `docs/BUILD-PLAN.md` to build the app.

## Status

- Video 1 studied: fxalexg, "The Trading Industry Will Hate Me for This FREE 10+ Hour Course" (10h36m).
- Video 2 studied: fxalexg, "The ONLY confirmation YOU need..." (22 min): entry confirmation and entry timing.
- Video 3 studied: fxalexg, "How to Master Liquidity in Trading (Advanced Guide)" (19 min): liquidity zones are his AOI; do not wait for sweeps.
- Video 4 studied: fxalexg, "Price Action Trading Was Hard, Until I Discovered This" (25 min): candle strength by location, wick fill, break-and-retest entries.
- Video 5 studied: fxalexg, "How Trading Dumb Made Me a Millionaire Trader (You Can Too)" (28 min): the simple one-pair, one-timeframe, one-session, one-signal version.
- Video 6 studied: fxalexg, "This trading strategy is boring, but it makes me $150,000/week" (21 min): streak discipline and four recent trades.
- Video 7 studied: fxalexg, "If I Wanted to Make $1,000/Day Trading, I'd Do This" (18 min): mindset and the 1:2 minimum (no charts).
- Video 8 studied: fxalexg, "How to Grow a Small Trading Account From Scratch in 2026" (52 min, uploaded 2026-02-22): small-account mode and psychology.
- Video 9 studied: fxalexg, "This is Boring, But it'll make your first $100,000 Trading" (1h23m, 2026-06-28): the three steps in order, AOI rules, stop beyond the AOI.
- Video 10 studied: fxalexg, "The Prop Firm Industry is Going to Hate Me For This Free Course" (1h18m, 2026-09-06): prop-firm rules, his four challenge rules, five real trades.
- Video 11 studied: fxalexg, "The Only Trading Strategy You Need To Be Profitable | Swing Trading" (27 min, 2026-05-25): Sunday analysis, the weekly retracement, stops at a level.
- Video 12 studied: fxalexg, "Best Top Down Analysis Strategy for 2026" (33 min, 2026-02-02): four sectors, the HL behind the HH, AOI on the weekly and daily.
- Video 13 studied: fxalexg, "How to Start Trading with Just $50" (37 min, 2026-07-26): the 4H head-and-shoulders plan for a $50 start.
- The PDF guide (version 1.7) covers all thirteen videos, with a new part for the three account plans (small account, prop challenge, $50 start).
- See `docs/VIDEOS.md` for all thirteen, with upload dates and the rule that the newer upload wins. More candidate videos are listed there.
- App v1 scope: the core rule set only (`strategy/strategy.md` section 1). Account modes and optional variants are parked so it runs his method the same way every time.
- App: phases 0 and 1 built (candles, market structure, charts), plus a lot size calculator and price alerts; later phases follow. The plan is in `docs/BUILD-PLAN.md` (its 7 decisions are confirmed: the defaults, starting with an MT5 demo on a Windows PC) and the exact rules are in `docs/ANALYSIS-SPEC.md`.
- More videos are expected. Each one is merged into `strategy/strategy.md`, with differences between teachers kept visible.

## Source credit

The strategy ideas and teaching examples belong to their creators. This repo holds independent summaries for study and short attributed phrases only. Watch the original videos to learn from the source.
