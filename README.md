# TradingGuide

A study project that turns trading-strategy videos into (1) a plain-English guide and (2) a specification for a forex analysis app that reports the strategy's confluences for a list of pairs.

Educational only. Not financial advice. Unofficial: not affiliated with the creators of the videos studied.

## What is here

| Path | What it is |
|---|---|
| `Confluence-Trading-Guide.pdf` | 35-page beginner guide (version 1.1) to the strategy studied so far. Start here if you want to learn it. |
| `strategy/strategy.md` | The merged rule set: exact definitions, numbers, conflicts, gaps. The source of truth for the app. |
| `docs/APP-PLAN.md` | What the app should do and the open build decisions. |
| `docs/VIDEOS.md` | Videos studied, and which video time range each study part covers. |
| `docs/SETUP.md` | One-time machine setup (tools, plugin, GitHub login). |
| `docs/WORKFLOW.md` | Step by step: study a new video, merge it, rebuild the PDF, push. |
| `docs/AGENT-PROMPT.md` | The prompt template used for the study agents. |
| `scripts/` | `setup.ps1` (check or install tools), `study-video.ps1` (download + captions + frames), `segment.py` (clean and split captions). |
| `guide-src/` | Source that builds the PDF (HTML + SVG diagrams, printed by Edge). |
| `CLAUDE.md` | Standing instructions for Claude Code sessions in this repo. |

## Quick start

```powershell
git clone https://github.com/xtiannjose/TradingGuide.git
cd TradingGuide
.\scripts\setup.ps1            # checks the machine; add -Install to fix what is missing
```

Then see `docs/WORKFLOW.md` to study another video, or `docs/APP-PLAN.md` to build the app.

## Status

- Video 1 studied: fxalexg, "The Trading Industry Will Hate Me for This FREE 10+ Hour Course" (10h36m).
- Video 2 studied: fxalexg, "The ONLY confirmation YOU need..." (22 min): entry confirmation and entry timing.
- See `docs/VIDEOS.md` for both.
- App: not built yet. Plan and decisions are in `docs/APP-PLAN.md`.
- More videos are expected. Each one is merged into `strategy/strategy.md`, with differences between teachers kept visible.

## Source credit

The strategy ideas and teaching examples belong to their creators. This repo holds independent summaries for study and short attributed phrases only. Watch the original videos to learn from the source.
