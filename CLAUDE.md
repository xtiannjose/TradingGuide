# TradingGuide: instructions for Claude Code

This repo is a study project: trading-strategy videos become a guide (PDF) and an app specification. Read `README.md` for the map.

## Ground rules

- **Source of truth:** `strategy/strategy.md`. When a new video is studied, update it. Keep each teacher's differences visible (a "changed by video N" line), and keep citations in the form `[PART mm:ss]`.
- **The user's goal:** a forex app that takes a list of pairs, analyses each against the strategy, and writes a report of confluences (areas of interest, structure, daily bias and so on). Strategy first, app later. The user left the choice of method to Claude.
- **Do not copy the creators' risk numbers.** The course's 100% to 35% challenge risk ladder is not a rule. The app takes the user's own risk %.
- **Do not scrape TradingView.** It has no public data API and automating it is fragile and against its terms. Use a candle data API and compute everything from candles (see `docs/APP-PLAN.md`).
- **Do not invent rules.** If a video does not state something, write "not stated" and list it as a gap.
- **This repo is public.** Never commit keys, tokens, `.env` files, cookies, personal data or local absolute paths. Keep quotes from videos short and attributed. Do not publish downloaded videos or full transcripts.
- **Detailed per-part study notes stay local** (`<workdir>\<video-id>\notes\`), not in this repo.

## Studying a video

Follow `docs/WORKFLOW.md`. The points that matter:

- Use `scripts/study-video.ps1` (local engine, no key). The Gemini engine is not set up.
- Hours-long videos: clean and split the captions with `scripts/segment.py`, then use study agents with the template in `docs/AGENT-PROMPT.md`.
- **Run at most 4 study agents at a time.** Twelve at once hit the account session limit and all died. Tell each agent to write its notes file first and view at most about 12 frames afterwards.
- Video chapter titles can be wrong about what is taught. Judge by content.

## Rebuilding the PDF

`python guide-src/make.py <out.pdf>` (needs Edge and `pymupdf`; run `scripts/setup.ps1` first). Check the pages visually after changes (render to images with pymupdf and look for overlapping labels and near-empty pages). Then copy the PDF to the repo root as `Confluence-Trading-Guide.pdf`.

## Environment

Windows, PowerShell. Tools: Python 3.12, yt-dlp, Deno, FFmpeg, git, GitHub CLI, Microsoft Edge, Claude Code plugin `watch@claude-video`. Details in `docs/SETUP.md`. Commit messages end with the attribution line given by the session.
