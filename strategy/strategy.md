# fxalexg confluence strategy: consolidated spec

Sources, both by fxalexg (Swing Trading Lab), studied from auto-captions plus video frames:
- **Video 1:** "The Trading Industry Will Hate Me for This FREE 10+ Hour Course", https://www.youtube.com/watch?v=grw58BIzotU, 10:35:59 long, studied 2026-10-08 in 12 parts.
- **Video 2:** "The ONLY confirmation YOU need to make $1000/day Trading Forex", https://www.youtube.com/watch?v=BcWxqfcjk9A, 22:03 long, studied 2026-10-09. Teaches the entry confirmation and entry timing. Cited as `[V2 mm:ss]`.
- **Video 3:** "How to Master Liquidity in Trading (Advanced Guide)", https://www.youtube.com/watch?v=Rua24ytuHuY, 19:18 long, studied 2026-10-09. Teaches what "liquidity" means in his method and why he does not trade liquidity sweeps. Cited as `[V3 mm:ss]`.
- **Video 4:** "Price Action Trading Was Hard, Until I Discovered This", https://www.youtube.com/watch?v=WEyJ-zKAEoA, 25:23 long, studied 2026-10-09. Teaches strong vs weak candles, rejection vs wick fill, patterns as extra confluence, and break-and-retest entry options. Cited as `[V4 mm:ss]`.

Citations look like `[E 3:44]` = study part E of video 1, video time 3:44 (h:mm:ss or mm:ss). Part letters follow the time ranges in `docs/VIDEOS.md`. The detailed per-part study notes (quotes, numbers, worked examples, open questions) are kept locally and are not published here. This file is the merged rule set and the source of truth for the app.

Wording convention: "(app default)" marks something I chose to fill a gap. It is not his rule.

---

## 0. How far to trust this

- Captions are machine-made. Frames confirmed many points; a few numbers stay uncertain and are flagged.
- The video description's chapter titles do not match where topics are taught. "Confluence Trading" (2:28:00 to 4:01:40) is actually market-structure basics. I merged by content, not by chapter.
- **His "entry signal" is only partly public.** In video 1 he says a specific entry signal is explained only on his livestream [L 10:14:48]. Video 2 teaches an "entry confirmation" in the open (closed rejection or engulfing candle at a support/resistance zone, with the trend, at the right session and weekday). That is the best public statement of it and is documented in 3.6, but he never says it is the same thing he withholds.
- Video 2's title and intro quote income figures ($500 to $1,000 a day). Those are marketing claims, not evidence.
- The course never gives a base risk %, a numeric rule for what counts as a "significant" swing or a "touch", or a news filter. See section 7.
- Video 3's view that "liquidity sweeps" and bank stop-hunting are mostly a myth is his opinion, given without data. It is recorded as his method (do not anticipate or wait for sweeps), not as a fact about markets.
- Trade results and win rates in the video are his own claims. Nothing was back-tested (he opposes back-testing [C 2:07:52]). This is a description of his method, not evidence that it makes money.

---

## 1. The strategy on one page

He calls it **confluence trading**: a trade is valid only when three things line up [L 10:19:20, J 7:45:08].

1. **Market structure read correctly**, top-down on weekly, daily and 4H.
2. **Price at an Area of Interest (AOI)**: a support/resistance zone drawn on the weekly and daily.
3. **An entry signal at the AOI**, always in the direction of the trend.

Optional extras add quality, not permission: a pattern (head and shoulders, break and retest, breakout), 50 EMA rejection, a round number, a previous structure level.

Fixed attitudes: trade with the trend only ("the trend is your friend" [F 4:33:56]); never predict tops or bottoms [A 0:24:31]; few trades; market execution only (never pending orders); set the stop and target, then **set and forget** [D 2:47:06, J 7:52:46].

Decision pipeline, in order. A failed gate means "no trade, next pair".

| # | Gate | Pass condition |
|---|---|---|
| 1 | Pair | On his watchlist (section 2); weekly shortlist |
| 2 | Time | Inside his 1:00 to 10:30 AM New York window, not Sydney/Tokyo |
| 3 | Structure | Bullish or bearish read on weekly, daily, 4H |
| 4 | Alignment | Two consecutive timeframes agree (W+D or D+4H) |
| 5 | Zone | HH-HL (bull) or LH-LL (bear) drawn on W/D/4H |
| 6 | AOI | Price is at a valid AOI inside that zone |
| 7 | Entry signal | Confirmation candle/pattern at the AOI, trend direction |
| 8 | Plan | Stop beyond the level, target at next structure, R:R at least 1:2 |
| 9 | Size | Lot size from risk amount and stop pips |

---

## 2. Chart setup and universe

- **Platform split:** analyse on TradingView, fund at a broker, execute on MetaTrader 5. He spends 90 to 95% of analysis time on TradingView [D 2:28:48, C 1:44:22].
- **Chart types:** candlesticks (trading, patterns) and the line chart (reading structure). Nothing else [A 0:47:17].
- **Indicators:** only two. (1) "No gaps candles" (community indicator that fills gaps so each candle opens at the previous close; native candles hidden; up candles blue, down candles red) [C 1:46:25]. (2) **50 EMA**: his settings panel offers 20/50/100/200 and only the 50 is ticked; "use only one indicator: 50 EMA" [J 7:18:39, 7:21:50]. No volume [C 1:47:26].
- **Timeframes:** weekly, daily, 4H, 2H, 1H, 30m, 15m only; never below 15m [C 1:51:14, B 0:57:16].
  - Trend + AOI timeframes: weekly, daily, 4H.
  - Entry-signal timeframes: 2H, 1H, 30m, 15m, "completely avoided until ready to enter" [F 4:40:31]. In his live trades he also confirms on 4H [J 7:50:01] and daily/weekly candles [L 10:01:10], so entry timeframe is flexible.
- **Chart timezone:** UTC-4 New York [C 1:58:10]. Interpretation: all his clock times are New York local time (see 3.2).
- **Drawing tools he uses:** trend line (only to create structure points), horizontal line and ray, rectangles for zones (fill about 4 to 5%), long/short position tool, head and shoulders tool, path, ellipse, text, measure. No Fibonacci, no pitchforks [C 2:09:56, D 2:17:29]. Alerts at key levels instead of pending orders [C 1:53:16].
- **Watchlist ("Blue list"), fixed, never edited** [C 1:59:43]. Forex (21): USDCHF, NZDUSD, GBPUSD, AUDCHF, NZDJPY, EURGBP, GBPCHF, USDCAD, GBPCAD, AUDCAD, AUDJPY, GBPNZD, EURJPY, NZDCAD, USDJPY, CADJPY, EURAUD, GBPJPY, GBPAUD, EURUSD, AUDUSD. Also OIL, ETHUSD, SOLUSD, DOGEUSD, XRP, BTCUSD, SPX500. He trades 15 to 20 pairs and prefers the 7 majors for volatility and cleaner reactions [A 0:40:43, 0:42:44]. Forex is the target for this app.
- **Pips:** 0.0001 for most pairs, 0.01 for JPY pairs (his chart shows 0.307 = 30.7 pips on NZDJPY) [D V5].

---

## 3. The rules

### 3.1 Weekly pair selection ("Sunday Swings")

- Break down about 10 markets, keep about 3, trade the 1 that gives the exact signal with every timeframe in agreement [K 8:31:12, 8:43:43].
- The alignment test (3.4) alone removes about half of the watchlist each week [G 5:00:58].
- Do not trade a market that lacks aligned timeframes. Skipping a week is normal [K 9:06:46].

### 3.2 Time-of-day filter

[B 1:07:54 to 1:16:36]. Times are "EST" as he says them; interpretation: New York local time (London opens 3:00 AM New York time for almost the whole year).

- Do not trade the Sydney or Tokyo sessions (no volume).
- Be active from about **1:00 AM to about 10:30 AM** New York time. He says "10:00" in places; the marker he drew sits at about 10:30. He has taken no trade after 10:30 AM in about four years [B 1:13:49].
- Entry moments: just before London (pre-London), in the middle of London, or just before volatility fades (9 to 10 AM, end of the London/New York overlap).
- Reference times: pre-London analysis from 1:00 AM; London opens 3:00 AM; New York opens 8:00 AM; London ends about 12:00 PM; market closes 5:00 PM.
- USD pairs: the dollar side wakes at the New York open, so these get "double volatility" from London into New York [B 1:15:34].
- Being inside the window is not a trade trigger; the strategy still has to say yes [B 1:16:16].
- **Weekday and wait-for-session rules (video 2):** enter only on **Monday, Tuesday and Wednesday**. After Wednesday there is not enough time to reach a take profit (his average TP is about 80 to 100 pips; Thursday New York offers only about 5 hours, about 14 to 15 hours of decent volume remain). He breaks this only for a shorter TP, a very strong confirmation or strong momentum [V2 17:26 to 18:28].
- If the confirmation prints **before a session** (for example before Sydney), do not enter yet: **wait until right before London** and enter inside the session. "That's the black and white rule." Waiting may cost a better or worse price; he accepts it because the confirmation then has proven itself. Do not enter just because a confirmation printed first thing Monday morning or in the last 3 hours before the weekly close [V2 14:41 to 19:30].
- He avoids entries where there would be only about an hour of volume followed by about 9 hours of none [V2 15:22].
- News: Forex Factory, red-folder events only, as information. He does not change his approach for news and says it does not build a strategy. Occasionally sits out a big speech or event [B 1:27:49, D 3:00:11].

### 3.3 Market structure (the core)

Taught across E, F, G. This is fully rule-based and the most reliable part.

**Definitions**
- Bullish = higher highs (HH) and higher lows (HL). Bearish = lower lows (LL) and lower highs (LH). Structure points are the "elbows" (turning points) [E 3:14:45].
- Price **inside** the pair (between HH and HL when bullish, between LH and LL when bearish) keeps the bias.
- A break counts only on a **candle body close** beyond the level. Touches, wicks, near misses and "three touches" do not. A small body-close break still counts. The candle must be closed [E 3:20:44, 3:43:57, 3:48:04].
- Structure is read from candle **bodies**, never wicks. The line chart (closes) is the cleaner way to spot elbows, then the lines are moved to the bodies [E 3:58:22, F 4:18:12, G 5:20:18].
- Structure differs on every timeframe [F 4:15:27].

**State machine**
```
bullish: HH, HL                       bearish: LL, LH
 body closes above HH -> HH moves to the new highest point of the push; HL re-placed by the snake trick
 body closes below HL -> BIAS FLIPS to bearish; LL = lowest point of the move; LH placed by the snake trick
 bearish mirror: body closes below LL -> LL moves, LH re-placed; body closes above LH -> flips to bullish
 anything else (wicks, touches, small swings that do not break) -> nothing changes ("a curb in the road")
```
- A new HH always brings a new HL; a new LL always brings a new LH [E 3:20:44, 3:27:46].
- A HL or LH can only be assigned once a new HH or LL exists [E 3:31:33].
- An HH/LL is only **confirmed** once its candle has closed and price has stopped/retraced; until then it is just the current extreme and the line moves with it [F 4:03:49, 4:08:54].

**Snake trick** (finds the paired point) [E 3:33:17, F 4:03:28, G 4:48:47]
1. Head of the snake = the new extreme (new HH or LL).
2. Walk backwards along price.
3. The **first significant turn** is the paired point (HL after a new HH; LH after a new LL).
4. Skip soft bumps: a candidate counts only if the snake "would have to make a turn"; if price could "slide right through" it, it is not a point. Soft one-candle pullbacks are not counted; a clear single engulfing candle is [G 4:53:00 to 4:55:47, E 3:55:38].
5. If a small bump and a sharper turn further back both exist, he picks the sharper, cleaner one [E 3:56:00, F 4:23:21]. No numeric size rule is given (see section 7).

**Lookback** [G 4:45:18 to 4:47:04, H 5:52:23]: weekly 5 to 6 years max; daily 1 to 2 years (on-screen note); 4H 6 to 12 months. Once read, do not re-read history; just track the live HH/HL (or LH/LL) until something breaks [G 4:45:42]. Centre the chart on current action; not too zoomed in or out [F 4:12:42].

**Never** call the trend from price level alone; USDCHF at its lows is bearish because of its LH and LL, not because price is low [F 4:10:58].

### 3.4 Top-down alignment and the zone

- Run 3.3 on **weekly, daily and 4H** separately [G 5:07:08].
- **Two consecutive timeframes must agree** (weekly+daily, or daily+4H). Bullish/bearish/bullish does not count [G 4:59:36, 5:00:18].
- All three agreeing = "not a high-risk trade". Weekly+daily agree while 4H disagrees: either take the risk or wait for 4H to turn [G 5:01:41]. In practice he says he trades "with all the time frames in my favour" [K 8:55:07] and that weekly+daily "double check" the trend [J 7:41:00].
- Then write the HH/HL (or LH/LL) of each timeframe on the chart to "trap price" into a zone; only look inside it [G 5:03:23, 5:06:47]. Weekly points are copied onto the lower charts at the same price [F 4:35:37].
- Bias must be stated per timeframe even if weekly and daily differ; when the daily has moved on inside the weekly structure, use recent daily action for the daily call [F 4:16:28].
- Trade only with the trend. He calls counter-trend trades "degen"; the two he describes (USDCHF, EURUSD) both lost [E 3:54:16, K 9:07:07].

### 3.5 Area of Interest (AOI)

His one name for support/resistance = supply/demand = order block [G 5:10:36]. Taught in G and H.

A valid AOI is:
- **inside the zone** (between HH and HL when bullish, LH and LL when bearish). Anything outside is invalid; price breaking beyond the HL means that timeframe is bearish and the buy idea is void [G 5:03:23, 5:25:12];
- **at least 3 touches** (any mix of support and resistance touches). More is better [G 5:15:07, 5:17:12];
- **5 to 60 pips tall**, tight is better, sweet spot 20 to 35 pips; do not stretch the box to collect touches [H 5:38:54, 5:40:56, 6:01:38];
- built from **body elbows, never wicks** [G 5:20:18];
- counted first on the **line chart**, then checked on candles; unclean touches are dropped, and if 3 clean ones remain it stands [H 5:53:44];
- drawn on the **weekly and daily only** (no AOI on the 4H) [H 5:50:41, on-screen "4hr NO AOI"]. Weekly AOI inside the weekly zone; daily AOI inside the daily zone;
- kept to "maybe one, maybe two, max three" [H 5:51:22]. Far AOIs that price must break through first can be dropped [H 6:00:38].

Combining: where a weekly and a daily AOI overlap, merge them into one tight box that still has at least 3 touches on both. Overlap = timeframes "in sync" = higher probability [H 6:00:58].

Using it:
- **No AOI reached, no trade** [G 5:17:53, H 5:44:05].
- Buy at support, sell at resistance. Never buy at resistance or sell at support. To buy from a level, price must be above it [G 5:28:55, 5:30:40].
- Resistance becomes support (and the reverse) **only** after a break and a retest [G 5:13:23].
- If price breaks below a buy AOI, do not buy it; wait for a break back above and a retest from above [G 5:34:06].
- A retracement into an AOI respected 4 to 5 times is more likely to react than one touched once [G 5:31:23].

Things that add to an AOI (confluence, from his live trades): previous daily structure level, a round psychological number (e.g. 157.500, 1.12500), the daily/weekly/1H EMA, a head-and-shoulders or double-top neckline [K 8:49:57, 9:26:35].

**"Liquidity" in his method** [V3 0:41 to 5:50]. Liquidity just means buyers and sellers (with their take profits and stops) at a price. He says it is everywhere but strongest where price has **consistently rejected**, which is exactly his AOI (support/resistance, supply and demand, order block). Consequences:
- Above the zone buyers dominate (buy); below it sellers dominate (sell). A zone with one rejection is less predictable; he wants a **higher-timeframe zone with multiple taps, "more than three" ideal** [V3 5:29 to 5:50]. This matches the 3-touch rule in 3.5.
- **Round numbers hold liquidity.** Example: Ethereum failed to reach 5,000 because many holders set take profits just below it (4,999, 4,998...), so selling began just short of the round number [V3 1:01 to 1:41]. For the app this supports a "near a round number" confluence, and price may stall a few points short of it. No distance rule is given.
- Do not buy at the high; wait for a retracement into a zone with a track record of rejections ("a discount") [V3 14:29 to 15:09].

### 3.6 Entry

Core gate [J 7:45:08, L 10:19:20]: trend + AOI + entry signal. No minimum count of extras, but "more confluences = lower-risk trade" [J 7:35:29, 7:36:10]. Seen checklist: 1 Trend, 2 AOI, 3 Entry, 4 Patterns [J 7:42:05].

**Execution rules**
- Market execution only (99.99% of the time). No buy/sell limit or stop orders: they enter "without confirmation" [C 1:39:10 to 1:40:12].
- Set an alert at the level you are waiting for, wait, and when it fires check whether a real confluence is there, never entry "just based off momentum" [C 1:53:16, D 2:42:58]. Often he places the alert so that a close beyond it is the engulfing candle [K 9:42:29].
- Wait for the signal candle to **close** before acting [E 3:25:16, F 4:02:07].
- If a trade is entered too early and the AOI can still be retested, he closed it, waited, and re-entered later at a worse price [L 9:56:22]. Entering before confirmation is a flagged mistake.

**Entry candles (his versions, used only at an AOI, in the trend direction)** [H 6:21:56 to 6:40:32, I 6:40:52 to 6:45:40]
- **Bullish engulfing:** the last candle's body closes beyond the bodies of the **last two** candles (wicks ignored; a hairline excess counts). Mirror for bearish [H 6:30:31, I 6:42:56].
- **Morning star** (bullish) = a doji/hammer/inverted-hammer candle followed by a bullish engulfing of the last two candles. His favourite. **Evening star** is the bearish mirror. A morning star at resistance, or in a bearish market, is "no use" [H 6:31:51 to 6:36:21, 6:39:50, I 6:43:36].
- **Doji / spinning top:** slowdown at an AOI after a push, next candle may engulf [H 6:25:02].
- **Hammer** (long lower wick, little upper wick, at support) and **inverted hammer = "wick fill"** (upside wick, next candle expected to fill it) [H 6:28:06 to 6:30:11].
- Dragonfly doji = hammer; gravestone doji = hanging man = shooting star. Treated as the same families [H 6:30:11, 6:35:40].
- **Rejected patterns:** piercing line, three white soldiers / three black crows, dark cloud cover [H 6:31:51 to 6:34:17].
- Higher timeframe = stronger formation (daily doji at an AOI is "amazing", 4H good, 1H okay) [H 6:26:45].
- **A candle's strength comes from where it forms, not its size** [V4 2:46 to 6:53]. A giant bullish candle in the middle of the chart is weak (it may fully reverse); a small doji rejection at a strong support that already caused a big reaction is strong. The same candle mid-chart, with nothing holding it up, is weak. He enters before the impulse and does not chase momentum.
- **Patterns are extra confluence, never the whole trade.** He takes many trades with no pattern and will not take a trade that is only a pattern [V4 14:05 to 14:47].
- In his challenge he says plainly "you need an engulfing candlestick to enter a sell or a bullish engulfing to enter a buy" [K 8:50:58].

**The entry confirmation, in his own summary (video 2)** [V2 0:00 to 21:13]
- **Confirmation, not anticipation.** Wait for the candle to **close** (any timeframe, 1 minute to monthly). One second before the close it is still anticipation and can reverse [V2 1:02, 2:43].
- Two types: **(a) a rejection candle** (doji or small body with a long wick, also "wick fill") and **(b) an engulfing candle** (bullish to buy, bearish to sell). Together they are stronger; several dojis in a row then an engulfing at support is better. A small candle then an engulfing also works. No rejection and no engulfing means no entry [V2 1:42 to 4:24].
- The engulfing must **body-close beyond the last candle** (even a tiny one counts). This is looser than video 1's "last two bodies" (see section 6) [V2 3:43 to 4:04].
- **Higher timeframe = stronger** [V2 4:04].
- Only **at a support/resistance zone** (supply/demand, order block). Bullish confirmation at support, bearish at resistance. Mid-chart confirmations are ignored [V2 8:31 to 9:32].
- He may enter on the rejection alone or wait for the engulfing too. It depends on the strategy, level strength, timeframe, days left in the week, R:R and other confluences ("extra extra extra confirmations"). Waiting avoids losses but misses trades; he accepts both [V2 9:52 to 11:36].
- **Pro-trend only.** A confirmation points the same way as the trend. A counter-direction engulfing does not flip the bias; bias does not change overnight, and on intraday/swing it holds for almost a month. Entering the opposite engulfing is "gambling" [V2 11:56 to 14:21].
- **Wick fill (daily vs 4H):** a daily candle with a long lower wick can be a wick fill rather than a plain rejection if the 4H within that day went bearish into the area and then made a higher low. The next daily bullish engulfing is then the entry. He quotes "almost 70%" chance of a bullish push the day after a strong daily confirmation [V2 5:06 to 7:28]. Video 4 gives the same idea: a candle that looks like a rejection against your trade (for example from the EMA) may only be a wick fill if the 4H shows a retracement or higher low. One contrary candle must not cancel a top-down read when a major support has held price three times [V4 10:19 to 13:44, 12:01 to 12:41].
- **Everything must line up.** A perfect setup on a Tuesday at the London open still gets no trade without the confirmation [V2 19:30 to 20:12].

**Liquidity sweeps: do not anticipate them, do not wait for them** (video 3)
- A wick through a zone that then reverses is called a "liquidity sweep / grab / fake out". He considers the stop-hunting story largely unproven and says no strategy can anticipate or consistently trade sweeps [V3 6:11 to 9:36]. This agrees with the body-close rule: wicks do not count (3.3).
- **Wait for the confirmation, not the sweep.** Waiting for a sweep is "playing defense"; entering on a confirmation is "playing offense". In his example the market approached one support zone 7 times; only one gave a sweep, and the other six gave a bullish engulfing, a morning star with engulfing, a bullish rejection candle or a bullish pin bar. Waiting for the sweep would have missed six trades [V3 9:57 to 17:13].
- If price moves **against** the direction you want (for example several bullish closes when you want to sell at resistance), do not sell yet and do not guess it is a sweep. Wait for a candle that confirms your direction (a bearish candle for a sell) [V3 10:39 to 12:48].
- The next step after the zone is a confirmation candle, never a sweep [V3 15:29].
- His own recap: candle closed; rejection or engulfing (stronger with more rejections and one strong engulfing); at a strong support/resistance zone; at the right time [V2 20:12 to 21:13].

**Break and retest** (his favourite continuation pattern) [H 6:10:12 to 6:19:52, I 6:47:46]
1. Price is held at an AOI. A **body close** beyond the zone is the confirmed break (wicks do not count).
2. Price returns into the zone and gets rejected from it (wick or body rejections).
3. Enter above the broken zone (buy) or below it (sell).
- **Breakout** entry (no retest) is allowed but is not counted as the break-and-retest confluence. He enters on the breakout about 30% of the time, base case is the retest. After a breakout it is "50/50" that price retests, then "50/50" that it reacts [H 6:11:34 to 6:14:16].
- "BOS = CHoCH = shift of structure" are one concept: the break of the HL (bull) or LH (bear) [H 6:09:52].
- Consolidation breakout: do not enter inside a range at the AOI; wait for the breakout, then the quick retest/pullback with an engulfing or rejection, then enter [L 10:08:08, 10:14:26].
- **Three ways to enter a break and retest, ranked by him** [V4 19:36 to 23:22]: (1) on the breakout itself (least favourite); (2) on the retest with no rejection candle (also least favourite); (3) **on the retest with a rejection candle** (favourite, about 8 in 10 of his trades with this pattern). Missing a trade because the retest never comes is accepted: "if you change your rules every single time, so will your results."
- **Live example** [V4 19:56 to 21:40]: price failed 4 times to break a support zone and broke on the 5th. He entered on the retest with rejection candles and lost 1%; price broke again, retested, he entered again on the same kind of candles and made 6% (net +5%). He re-enters when the setup returns. Frames show EURAUD 4H with two short boxes, the second with a much larger target.

**Head and shoulders** (reversal; valid only on the shift of structure) [I 6:49:30 to 7:13:33, J 7:13:53 to 7:17:38, L 10:04:58]
- Regular H&S forms at a high/resistance (bearish reversal); inverted at a low/support (bullish). Draw on bodies. Shape need not be textbook; slanted or unequal is fine.
- The **neckline is horizontal**, at the previous structure point (the higher low), at an AOI. Not the diagonal the drawing tool makes.
- **Valid only after the neckline breaks** (body close). Never sell a potential H&S, and never sell off the right shoulder (his current rule, "extremely high risk" otherwise) [J 7:56:12].
- After the break: mark the LL and LH (snake trick), draw the box between them, find the AOI inside it by working up from the LL; the AOI that coincides with the neckline is the entry zone. Wait for the retest; then a shooting star / evening star / bearish engulfing; then sell. Buy side is the exact mirror.
- A pattern can still lose, and one that never breaks the neckline is simply not traded [I 7:03:33, 7:05:17]. Video 4 repeats: never sell the anticipated right shoulder; the pattern exists only after the structure shift; take it on that break or on the neckline retest; works on any timeframe, stronger on higher. His claim that a reversal follows "7 out of 10" times is unverified [V4 15:07 to 18:54].
- Double top with a neckline is treated the same way [K 9:26:13].

**What the live trades actually show** (not a stated rule): trend alignment, then AOI (structure level + EMA + round number + neckline), then break and retest, then an engulfing/evening-star candle on 1H, 30m or 15m, then set and forget [K 8:49:15 to 9:48:27, L 9:50:05 to 10:19:20].

### 3.7 Stop loss and target

- **Stop:** just beyond the level that, if broken, proves the idea wrong. His wording: "a little bit above this level" (sell) [K 9:09:29]. On the NZDUSD recorded trade: "10 to 15 pips above the wick", about 20 pips from entry [J 7:48:37]. Stops seen on his examples run from about 20 to 50 pips. No fixed pip rule. Rule of thumb he states for pre-trade sanity: the stop sits "at a point where if it gets hit you are completely wrong" [D V3, low confidence, from an on-chart note].
- **Target:** the next structure point / previous swing low or high (next 4H low), not the furthest one ("we're not going to be greedy") [L 10:09:52, J 7:48:37].
- **Risk:reward:** always at least **1:2**; set the trade up so 1:4 is possible; hold for it [K 8:37:51 to 8:39:37]. Wording conflicts ("minimum of 1:4" vs "aim for potential 1:4"); read as potential. Seen: 1:2 to 1:3.5 typical, 1:5 to 1:11 on a few [K R34, L 10:03:14].
- Use the TradingView long/short position tool to read the ratio before entering [C 2:13:41].
- His average take profit is about **80 to 100 pips** [V2 17:26].

### 3.8 Risk and position size

- **Position size** (mechanical, from the calculator he shows): lots = risk amount / (stop pips x pip value). Examples: $100 account, 10% risk, 20 pips, EURUSD -> 0.05 lot [C 1:41:12]; $1,000, 5% ($50), 30 pips -> 0.17 lot on NZDJPY [D 2:36:50]. Lot size must be fixed **before** entry [C 1:40:32]. His $10 per pip per standard lot for USD-quoted pairs is correct [K 9:35:09].
  - My check: his NZDJPY output (0.17) does not match standard JPY pip maths (about 0.25 lot at USDJPY near 147). The app should compute pip value itself and not copy his calculator.
- **How much to risk: his base risk % is never stated.** What he says:
  - Challenge ladder ($100 to $1M) [K 8:29:06, slide at 8:36:28]: $100 and $400: 100%; about $3,200: 60 to 50%; about $8,000: 50 to 40%; from about $15,000: 40 to 35%; never below 35% (sometimes 30% or 27%). A later remark says 50 to 75% at $3 to 5K. He took a counter-trend trade at 20% [K 9:07:27].
  - "The higher I go in the account I lower my risk by 25 to 50%" [L 10:07:26].
  - More confluences = lower risk = risk more money; no numbers [J 7:36:10].
  - Examples in teaching: $10 on $100, $50 on $1,000 [A 0:27:57, D 2:34:40].
  - A live break-and-retest example "lost 1%" then "made back 6%" [V4 21:19]. That implies about 1% risk per trade on that example (inferred; he states no risk rule) and a reward of about 6 times the risk.
  - **This ladder is a stunt, not a rule to copy.** Risking 100% of an account on a trade means one miss ends it, and his own earlier attempt went $100 to about $330,000 and then blew up in one week [J 8:20:41]. The app should take the user's own risk % and not use his ladder.
- **Frequency:** "one and done" in the challenge: one trade a week, win or lose [K 8:32:59]. His normal swing/day mix is a few trades a month [A 0:30:42].

### 3.9 Management and exit

- **Set and forget:** after entry do nothing until the stop or target is hit. Exceptions about 1 in 20 [J 7:52:46 to 7:53:07, L 10:17:35]. Do not let post-entry emotion change the decision [J 7:53:27]. Expect an immediate small drawdown from the spread [C 1:43:40].
- Alerts at key structure points (e.g. a 4H body close beyond a structure point) then wait [J 7:55:10, L 10:05:41].
- Discretionary exits he describes (optional, for a short; mirror for a buy): a 30-minute break above the last structure point; at a structure point near the target, watch the candle close (closes back above the line: close; closes under it: hold); a clear structure shift; if the daily closes under a previous structure level, hold "for a long time" [J 8:01:05, K 9:01:56, 8:53:44].
- When price runs past the target he sometimes closes at a chosen point ("do not get greedy", e.g. closed about 1:5) [J 8:10:03].
- Wick-outs are inevitable and accepted ("if you want to avoid a wick out, don't trade") [J 8:05:11]. They still happen to him about once every 2 weeks; he takes the next trade and does not let it affect it [V3 17:33 to 17:53].
- Split larger positions into several orders to limit slippage [K 9:39:04].

---

## 4. The confluence list for the report

Core (mandatory): **trend** (two consecutive timeframes aligned), **AOI** (price inside a valid weekly/daily AOI), **entry signal** (confirmation candle or break-and-retest at the AOI, in trend direction).

Extras that raise quality (none mandatory, no minimum count):
- all three timeframes aligned (W, D, 4H)
- weekly AOI and daily AOI overlapping
- break and retest of the zone (vs a plain breakout)
- head and shoulders / inverted H&S / double top with the neckline at the AOI
- higher-timeframe candle at the AOI (daily/weekly doji, engulfing, evening/morning star, pin bar)
- 50 EMA rejection (daily, 4H, weekly or 1H); price above EMA = support, below = resistance; "cherry on top", never required [J 7:20:03 to 7:25:53]
- round psychological number at the AOI
- previous daily structure level at the AOI
- an AOI with many touches

His own examples, as test cases:
- AUDCHF sell note: weekly/daily/4H bearish; at weekly resistance; weekly evening star; under daily S/R at 0.69000; rejection from the daily EMA; under the 4H EMA and structure [C 2:05:55].
- Five confluences on an AUDJPY daily buy: strong bull trend, two timeframes in sync, AOI, break and retest, morning star with doji [H 6:38:24].
- Seven confluences on a sell: daily rejects AOI; daily bearish engulfing/pin bar; 4H H&S; 4H neckline break + retest; 1H H&S; break + retest of the neckline; EMA rejection; 1H bearish engulfing [J 7:37:12].

---

## 5. What the app can compute (OHLC only) vs what needs a choice

**Directly computable from closed candles** (ignore the live, unclosed candle)
- Candle bodies, body-close breaks, the structure state machine per timeframe (3.3), bias, HH/HL/LH/LL levels, "inside the zone" test.
- W/D/4H alignment, sync pair, zone per timeframe.
- Zone height in pips (5 to 60), touch counting inside a zone, weekly/daily overlap, price-at-AOI, above/below AOI.
- Engulfing (two prior bodies), doji, spinning top, hammer, inverted hammer, morning/evening star as he defines them, body-close break and retest detection.
- EMA(50) side and rejection; round-number proximity; previous daily swing level.
- Session flags from the New York clock; pip/lot/R:R maths.

**Judgement in the course. The app will have to choose and expose these** (my suggestions are "app default", not his):
1. What a "significant swing" is (the "clean elbow" / "sharp turn" test). Suggestion: a fractal or ZigZag threshold with a minimum size per timeframe, user-tunable.
2. Whether his line chart equals closes. With "No gaps candles" each open equals the previous close, so body extremes sit at closes and structure on closes should match his body-based lines (my inference, unverified in the video).
3. What counts as one "touch" (distance tolerance, candles per touch).
4. AOI box placement (the "happy medium" merge and which three touches to pick).
5. When a retracement has "stopped" (confirms an HH/LL).
6. Stop buffer beyond the wick (his 10 to 15 pips on one example).
7. Daily and weekly candle boundaries: aggregate with the New York 5 PM close, since body-close tests are boundary-sensitive (my inference from his "market closes 5:00 PM EST").

**Proposed report fields (per pair)**: time window pass/fail; W/D/4H bias with HH/HL/LH/LL prices; alignment grade (none / two / three); zone; weekly and daily AOIs with touch count and pips, merged boxes, price relative to nearest AOI; EMA side per timeframe; latest candle signal at the AOI; pattern state (H&S/double top: potential vs neckline broken vs retested); proposed stop, target, R:R; lot size for the user's risk; confluence checklist with pass/fail; "no trade" reason when a gate fails; red-folder news in the next hours (needs a calendar feed).

---

## 6. Conflicts in the course and the default I would use

| Topic | What he said | Default |
|---|---|---|
| Trend alignment | "Two consecutive timeframes" [G]; "all three"/"majority" [F]; "weekly and daily" [J] | Pass on W+D or D+4H; grade A when all three agree |
| AOI timeframes | W/D/4H identify AOI [F 4:40:52] vs AOI only weekly and daily, "4hr NO AOI" [H] vs AOI concept valid on all timeframes [J 7:26:14] | Draw AOIs on W and D only (the later, explicit teaching) |
| AOIs per chart | "Four and five" [G 5:26:54] vs "one, maybe two, max three" [H 5:51:22] | Keep up to 3 |
| Window end | "10:00" vs "about 10:30" [B] | 10:30 AM New York |
| Window start vs Sydney/Tokyo | He trades from 1:00 AM, but his session graphic has Sydney to 2 AM and Tokyo to 4 AM [B] | Start 1:00 AM; his rule is "pre-London counts" |
| Mandatory confluences | "No minimum" [J 7:35:29] vs "if the plan isn't checked, don't trade" [J 7:45:08] | The core three are mandatory; extras are not |
| Close before SL/TP | "Never" [J] vs closes early in a few live trades [K, L] | Default hold to SL/TP; flag early-exit ideas as manual |
| Stop and target in teaching samples | Spoken ratios differ from the position tool on screen (AUDJPY: "1 to 2, 118 pips" vs tool 2.71 [H 6:38:45]; NZDJPY: said 2 vs tool 2.47 [D V9]) | Use the stop/target the app derives; do not copy these samples |
| Risk % | 100% to 35% ladder, "50 to 75%" at $3 to 5K, "lower risk 25 to 50% as account grows" | Not his rule to copy; user-set |
| Engulfing definition | Must cover the last **two** bodies [H 6:30:31, I 6:42:56] vs body-close beyond the **last** candle, even a tiny one [V2 3:43] | Valid minimum: beyond the last candle's body. Grade higher when it covers the last two bodies (his "morning/evening star" form) |
| Entry timing | Pre-London entries from 1:00 AM [B] vs "wait until right before London" if the confirmation printed before Sydney [V2 16:25] | Same window; a confirmation that prints outside a session waits for the pre-London hour, then enters |
| Retest entry | Video 1: wick or body rejection on the retest is the confirmation [H 6:13:37]; breakout entry allowed about 30% of the time [H 6:12:35]. Video 4 ranks entry on the breakout and entry on the retest without a rejection candle as least favourite [V4 23:02] | Require a rejection candle on the retest; breakout entry is an option the user can switch on |
| Weekday | No weekday rule in video 1 (challenge trades on various days) vs Monday to Wednesday only [V2 17:26] | Mon to Wed by default; user can relax it, and he allows exceptions |
| Break wording | He once says a body close "above the higher high or the higher low" shifts structure [E 3:21:05]. His examples and on-screen notes show: beyond the extreme moves the labels, beyond the **protecting** point (HL when bullish, LH when bearish) flips the bias | Use the state machine in 3.3 |

---

## 7. Gaps: not given in the videos studied

- **His full "entry signal"** (video 1 says it is livestream only [L 10:14:48]). Video 2 gives the public entry confirmation (3.6) but does not say it is the same thing.
- Numeric limits for a rejection doji (body size, wick ratio) and for "first thing Monday morning" [V2].
- EMA **length is only given once** (50 EMA) and is not tied to a timeframe rule [J 7:21:50]. Earlier segments said "later"; no other value appears.
- A numeric definition of a significant swing, an elbow, a touch, "slowdown", doji body size, wick ratios.
- His normal (non-challenge) risk % (video 4's "lost 1%, made 6%" example hints at about 1% but is not a stated rule), max trades, daily/weekly loss limits, withdrawals, journaling. His "Perfect Trade Checklist" sheet exists but is never shown [L 10:26:57].
- A news filter beyond "look at the red folders".
- Any statistics: no back-test; win-rate claims are loose and inconsistent (e.g. 60 to 65% swing, 70% on 7 trades) [A 0:32:06, K 8:25:11].
- He says the YouTube challenge series and other videos explain more.

---

## 8. Using this

- For the build: read this file and `docs/APP-PLAN.md`. Where each topic is taught: structure state machine in parts E, F, G; AOI in G, H; candles and patterns in H, I, J; entry/exit/risk in practice in J, K, L; tooling and setup in B, C, D.
- When more videos are studied (see `docs/WORKFLOW.md`), update the sections here and list any change in a "changed by video N" line so differences between teachers stay visible.

**Changelog**
- **Video 4 (2026-10-09):** added candle strength by location (3.6), patterns as extra confluence only, the three ranked entries for a break and retest with a live example (3.6), H&S reminders, a risk hint of about 1% (3.8, inferred), and a conflicts row on retest entries (require a rejection candle). Other rules restated, not changed.
- **Video 3 (2026-10-09):** added the liquidity framing of the AOI (3.5), the rule to ignore liquidity sweeps and wait for confirmation (3.6), wick-out frequency (3.9), and a caution that his stop-hunting view is opinion. No rule from videos 1 or 2 changed; it restates them (zones with 3+ taps, confirmation not anticipation, bodies not wicks).
- **Video 2 (2026-10-09):** added the entry confirmation rules (3.6), Monday to Wednesday and wait-for-session timing (3.2), average TP of 80 to 100 pips (3.7), three rows in the conflicts table (engulfing definition, entry timing, weekday), and updated the gaps. Everything else in video 1's rules is unchanged and consistent with video 2 (same creator).
