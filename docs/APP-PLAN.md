# App plan

Status: not built. This file records what the app should do and the decisions already made, so a new session does not start from scratch.

## What it does

Input: a list of forex pairs the user chooses.
For each pair, run the strategy in `strategy/strategy.md` against recent candles and write a report of what lines up and what does not. It is an analysis tool: it shows confluences and gates, it does not place trades and does not promise results.

## Report fields (per pair)

- Time window pass or fail (1:00 to 10:30 AM New York)
- Weekly, daily and 4-hour bias, with the HH, HL, LH, LL prices
- Agreement grade: none, two in a row, all three
- The zone (HH-HL or LH-LL) and the weekly and daily AOIs: touches, height in pips, merged boxes, distance from price to the nearest AOI
- EMA(50) side on each timeframe
- Latest candle signal at the AOI; pattern state (potential, neckline broken, retested)
- Suggested stop, target and risk:reward; lot size for the user's own risk setting
- The pre-trade checklist with pass or fail, and a clear "no trade" reason when a gate fails
- Optional: red-folder news in the next hours (needs a calendar feed)

## Decisions already made

- **Data source:** do not scrape TradingView. It has no public chart-data API and automating it is fragile and against its terms. Use a candle data API or a broker feed and compute everything from candles. TradingView can still be used by the human for viewing. (Provider not chosen yet: OANDA, Twelve Data and similar are candidates.)
- **Candles:** closed candles only. Daily and weekly candles aggregated on the New York 5 PM close, because body-close tests depend on the boundary.
- **Risk:** the user sets risk %. Do not use the creator's 100% to 35% challenge ladder. Compute pip value and lot size in the app (the creator's NZDJPY calculator example does not match standard yen pip maths).
- **Time:** all session logic in New York local time.
- **Output language of the report:** plain, with the reason for every pass or fail.

## Decisions still open (the course leaves them to the eye)

1. What counts as a "significant" swing (the clean-elbow test). Suggest a fractal or ZigZag rule with a minimum size per timeframe, adjustable.
2. What counts as one touch of an AOI (distance tolerance, candles per touch).
3. Where to place the AOI box when several touches compete; how to pick the best three touches.
4. When a retracement has "stopped" (confirms an HH or LL).
5. Stop buffer beyond the wick (his one example: 10 to 15 pips).
6. Whether structure on closes (line chart) matches his body-based lines. With the "No gaps candles" indicator each open equals the previous close, so it should; verify on real data.
7. The entry signal beyond engulfing and star candles: the creator withholds it. More videos may fill this in.
8. Tech stack, how the report is delivered (file, web page, app), and how often it runs. Ask the user when the build starts.

## Suggested build order

1. Data loader for the chosen provider, with the New York day boundary.
2. Structure engine per timeframe (the state machine in strategy.md section 3.3), with tests on hand-made price paths.
3. Top-down agreement and the zone.
4. AOI finder (touches, pips, merging).
5. Candle and pattern detectors.
6. Plan (stop, target, R:R, lot size) and the checklist.
7. Report writer.

Test each step against the creator's worked examples in the strategy file before moving on.
