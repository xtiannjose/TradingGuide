"""Build guide.html from content + diagrams. usage: python build.py <out.html> [pages.json]"""
import json
import sys
from pathlib import Path

import diagrams as D

PARTS = [
    ("p1", "Part 1", "The big idea"),
    ("p2", "Part 2", "Forex basics you need"),
    ("p3", "Part 3", "Your chart setup"),
    ("p4", "Part 4", "When to trade"),
    ("p5", "Part 5", "Market structure"),
    ("p6", "Part 6", "Top-down analysis"),
    ("p7", "Part 7", "Areas of Interest (AOI)"),
    ("p8", "Part 8", "Entry signals"),
    ("p9", "Part 9", "Plan the trade: stop, target, size"),
    ("p10", "Part 10", "Manage the trade"),
    ("p11", "Part 11", "Your weekly and daily routine"),
    ("p12", "Part 12", "Account plans: small, prop challenge, $50"),
    ("p13", "Part 13", "The one-page checklist"),
    ("p14", "Part 14", "What this guide cannot tell you"),
    ("pa", "Appendix A", "Glossary"),
    ("pb", "Appendix B", "Notes for app builders"),
    ("pc", "Appendix C", "Where it is taught, and credits"),
]

CSS = """
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; box-sizing: border-box; }
@page { size: A4; margin: 18mm 16mm 19mm 16mm;
  @bottom-center { content: counter(page); font: 9pt 'Segoe UI', Arial, sans-serif; color: #6b7280; }
  @top-right { content: "The Confluence Trading Guide"; font: 8.5pt 'Segoe UI', Arial, sans-serif; color: #9ca3af; } }
@page :first { margin: 0; @bottom-center { content: none; } @top-right { content: none; } }
html { font-family: 'Segoe UI', Calibri, Arial, sans-serif; font-size: 10.2pt; line-height: 1.46; color: #1f2937; }
body { margin: 0; }
h1, h2, h3 { break-after: avoid; }
h1 { font-size: 25pt; line-height: 1.15; color: #12263a; margin: 0 0 6mm 0; padding-bottom: 3mm; border-bottom: 3px solid #0f766e; }
.kicker { font-size: 10pt; letter-spacing: 2px; text-transform: uppercase; color: #0f766e; font-weight: 700; margin-bottom: 2mm; }
section.part { break-before: page; }
h2 { font-size: 14.5pt; color: #0f766e; margin: 7mm 0 2mm 0; }
h3 { font-size: 11.5pt; color: #12263a; margin: 4.5mm 0 1mm 0; }
p { margin: 0 0 2.6mm 0; }
ul, ol { margin: 0 0 3mm 0; padding-left: 6mm; }
li { margin-bottom: 1.2mm; }
b, strong { color: #111827; }
.lead { font-size: 12pt; color: #374151; margin-bottom: 4mm; }
.callout { border-left: 4px solid #0f766e; background: #f0fdfa; padding: 3mm 4mm; margin: 3mm 0 4mm 0; border-radius: 3px; break-inside: avoid; }
.callout .t { font-weight: 700; font-size: 9.5pt; letter-spacing: .8px; text-transform: uppercase; color: #0f766e; display: block; margin-bottom: 1mm; }
.callout p:last-child, .callout ul:last-child { margin-bottom: 0; }
.callout.warn { border-color: #b45309; background: #fffbeb; } .callout.warn .t { color: #b45309; }
.callout.ex { border-color: #2563eb; background: #eff6ff; } .callout.ex .t { color: #2563eb; }
.callout.bad { border-color: #b91c1c; background: #fef2f2; } .callout.bad .t { color: #b91c1c; }
.fig { margin: 3mm 0 5mm 0; break-inside: avoid; }
.fig .cap { font-size: 9pt; color: #6b7280; font-style: italic; margin-top: 1mm; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 4.5mm 0; font-size: 9.6pt; }
th { background: #12263a; color: #fff; text-align: left; padding: 1.8mm 2.5mm; font-weight: 600; }
td { padding: 1.8mm 2.5mm; border-bottom: 1px solid #e5e7eb; vertical-align: top; }
tr { break-inside: avoid; }
tbody tr:nth-child(even) td { background: #f9fafb; }
.cards { display: flex; gap: 4mm; margin: 3mm 0 4mm 0; }
.card { flex: 1; border: 1.5px solid #cbd5e1; border-radius: 6px; padding: 3.5mm 3.5mm; break-inside: avoid; background: #fff; }
.card .n { display: inline-block; width: 7mm; height: 7mm; line-height: 7mm; text-align: center; border-radius: 50%; background: #0f766e; color: #fff; font-weight: 700; margin-bottom: 1.5mm; }
.card h4 { margin: 0 0 1mm 0; font-size: 11pt; color: #12263a; }
.card p { font-size: 9.6pt; margin-bottom: 1.5mm; }
.pill { display: inline-block; padding: 0 2.2mm; border-radius: 9px; font-size: 8.8pt; font-weight: 700; }
.pill.g { background: #dcfce7; color: #15803d; } .pill.r { background: #fee2e2; color: #b91c1c; } .pill.a { background: #fef3c7; color: #b45309; }
.cols2 { display: flex; gap: 6mm; } .cols2 > div { flex: 1; }
.steps { counter-reset: s; list-style: none; padding-left: 0; }
.steps > li { counter-increment: s; position: relative; padding-left: 9mm; margin-bottom: 2.2mm; break-inside: avoid; }
.steps > li::before { content: counter(s); position: absolute; left: 0; top: 0; width: 6.2mm; height: 6.2mm; line-height: 6.2mm; text-align: center; border-radius: 50%; background: #12263a; color: #fff; font-weight: 700; font-size: 9pt; }
.check { list-style: none; padding-left: 0; }
.check li { position: relative; padding-left: 8mm; margin-bottom: 1.8mm; }
.check li::before { content: ""; position: absolute; left: 0; top: .5mm; width: 4.2mm; height: 4.2mm; border: 1.6px solid #12263a; border-radius: 1px; }
.small { font-size: 9pt; color: #4b5563; }
.toc td { border: none; padding: .55mm 0; font-size: 10.2pt; } .toc td.pg { text-align: right; width: 12mm; color: #0f766e; font-weight: 700; }
.toc a { color: #1f2937; text-decoration: none; } .toc tbody tr:nth-child(even) td { background: none; }
.cover { height: 296.5mm; background: #12263a; color: #fff; padding: 38mm 24mm 22mm 24mm; position: relative; break-after: page; overflow: hidden; }
.cover .band { position: absolute; left: 0; right: 0; top: 0; height: 9mm; background: #0f766e; }
.cover h1 { color: #fff; font-size: 40pt; border: none; line-height: 1.08; margin: 0 0 8mm 0; padding: 0; }
.cover .sub { font-size: 16pt; color: #99f6e4; line-height: 1.35; max-width: 150mm; margin-bottom: 10mm; }
.cover .line { width: 38mm; height: 3px; background: #0f766e; margin: 9mm 0; }
.cover .for { font-size: 11.5pt; color: #cbd5e1; max-width: 140mm; }
.cover .disc { position: absolute; left: 24mm; right: 24mm; bottom: 22mm; font-size: 9pt; color: #94a3b8; border-top: 1px solid #334155; padding-top: 4mm; line-height: 1.45; }
.cover .mini { position: absolute; right: 18mm; top: 60mm; width: 70mm; opacity: .9; }
.sidebyside { display: flex; gap: 5mm; align-items: flex-start; } .sidebyside > * { flex: 1; }
.tl td:first-child { white-space: nowrap; font-weight: 700; color: #12263a; }
.tag { font-size: 8.5pt; color: #6b7280; }
#p11 h2, #pb h2 { margin-top: 4.5mm; } #p11 li, #pb li { margin-bottom: .6mm; } #p11 td, #pb td { padding-top: 1.1mm; padding-bottom: 1.1mm; } #p11 .steps > li { margin-bottom: 1.2mm; }
#p11 p, #pb p { margin-bottom: 2mm; }
#pc td { padding-top: .8mm; padding-bottom: .8mm; } #pc h2 { margin-top: 4mm; } #pc li { margin-bottom: .6mm; }
#p4 h2 { margin-top: 4.5mm; } #p4 li { margin-bottom: .7mm; } #p4 td { padding-top: 1mm; padding-bottom: 1mm; } #p4 p { margin-bottom: 2mm; } #p4 .callout { margin: 2mm 0 2.5mm 0; } #p4 .fig { margin: 2mm 0 3mm 0; }
#p11 td { padding-top: .9mm; padding-bottom: .9mm; } #p11 h2 { margin-top: 4mm; } #p11 .steps > li { margin-bottom: .9mm; }
#p10 h2 { margin-top: 4.5mm; } #p10 li { margin-bottom: .7mm; } #p10 p { margin-bottom: 2mm; } #p10 .callout { margin: 2mm 0 2mm 0; }
#p5 h2, #p7 h2, #p8 h2 { margin-top: 4.5mm; } #p5 li, #p7 li, #p8 li { margin-bottom: .7mm; } #p5 p, #p7 p, #p8 p { margin-bottom: 2mm; }
#p5 .callout, #p7 .callout, #p8 .callout { margin: 2mm 0 2.5mm 0; } #p5 .fig, #p7 .fig, #p8 .fig { margin: 2mm 0 3mm 0; } #p5 .steps > li, #p7 .steps > li, #p8 .steps > li { margin-bottom: 1.4mm; }
#p10 ul { margin-bottom: 2mm; } #p10 { line-height: 1.4; } #p10 h2 { margin-top: 3.5mm; } #p10 li { margin-bottom: .4mm; }
"""


def toc(pages):
    rows = ""
    for pid, label, title in PARTS:
        pg = pages.get(pid, "")
        rows += (f'<tr><td><a href="#{pid}"><b>{label}</b> &nbsp; {title}</a></td>'
                 f'<td class="pg">{pg}</td></tr>')
    return f'<table class="toc"><tbody>{rows}</tbody></table>'


def fig(name, cap):
    return f'<div class="fig">{D.ALL[name]()}<div class="cap">{cap}</div></div>'


def part(pid, label, title, inner):
    return (f'<section class="part" id="{pid}"><div class="kicker">{label}</div><h1>{title}</h1>'
            f'{inner}</section>')


def callout(kind, title, html):
    cls = {"rule": "", "warn": " warn", "ex": " ex", "bad": " bad"}[kind]
    return f'<div class="callout{cls}"><span class="t">{title}</span>{html}</div>'


COVER = """
<div class="cover"><div class="band"></div>
<div style="font-size:11pt;letter-spacing:3px;color:#5eead4;font-weight:700;text-transform:uppercase;margin-bottom:8mm">Study guide</div>
<h1>The Confluence<br>Trading Guide</h1>
<div class="sub">Market structure, areas of interest and entry confirmation, explained step by step.</div>
<div class="line"></div>
<div class="for">A plain-English guide to one complete way of trading forex, built from fxalexg's 10-hour trading course and twelve follow-up videos (entry confirmation, liquidity, price action, top-down analysis, swing trading, a simple version, recent trades, mindset, small accounts, prop-firm challenges and a $50 start). Every rule has a picture, an example, and a place on the final checklist.</div>
<div class="disc"><b style="color:#e2e8f0">Educational summary only. Not financial advice.</b> Trading leveraged products such as forex can lose you more than you expect, including all of your deposit. This is an unofficial study guide. It is not affiliated with or endorsed by the course creator. Any results mentioned are the creator's own claims and have not been verified.<br>Updated 9 October 2026 &middot; Version 1.7</div>
</div>
"""

FRONT = """
<section id="front">
<h1 style="font-size:22pt">How to use this guide</h1>
<p class="lead">This guide turns a 10-hour video course and its follow-up videos into something you can read in an evening and use at your desk. Where two videos disagree, the newer one wins, and Part 14 lists both sides. It keeps the course's own method and wording, and explains each step in plain language.</p>
<div class="cols2">
<div>
<h3>If you are new</h3>
<p>Read Parts 1 to 4 first. They give you the big picture, the basic words and the setup. Then read Parts 5 to 10 in order, because each step builds on the last.</p>
<h3>If you just want to trade it</h3>
<p>Keep Part 13 (the one-page checklist) next to your screen. If you trade a small account, a prop-firm challenge or a $50 start, read Part 12 too. Come back to the earlier parts when a word or rule is unclear.</p>
</div>
<div>
<h3>How the boxes work</h3>
<div class="callout" style="margin:1mm 0 2mm 0"><span class="t">Rule</span>A rule from the course.</div>
<div class="callout warn" style="margin:1mm 0 2mm 0"><span class="t">Watch out</span>A common mistake or a risk.</div>
<div class="callout ex" style="margin:1mm 0 2mm 0"><span class="t">Example</span>A worked example.</div>
</div>
</div>
<p class="small">The diagrams are illustrations, not real prices. Candles are drawn <b style="color:#2563eb">blue for up</b> and <b style="color:#b91c1c">red for down</b>, like the creator's own charts. Prices quoted in examples were read off his charts and are approximate.</p>
<h2>Contents</h2>
{{TOC}}
</section>
"""

P1 = """
<p class="lead">The whole strategy fits in one sentence: <b>do nothing until three things line up, then place the trade, set your stop and target, and leave it alone.</b></p>
<div class="cards">
<div class="card"><div class="n">1</div><h4>Market structure</h4><p><i>Is the market going up or down?</i></p><p>Read it on the weekly, daily and 4-hour charts. Only trade in the direction of the trend.</p></div>
<div class="card"><div class="n">2</div><h4>Area of Interest (AOI)</h4><p><i>Where might price react?</i></p><p>A support or resistance zone on the weekly or daily. No AOI at the current price means no trade.</p></div>
<div class="card"><div class="n">3</div><h4>Entry signal</h4><p><i>Has price confirmed it?</i></p><p>A candle or pattern at the AOI that points the same way as the trend.</p></div>
</div>
{{CALL:rule|His three steps, always in this order|<p>In his newest walkthrough he puts it as three steps: <b>(1) top-down analysis</b> decides the direction (it removes either the buy or the sell button); <b>(2) the AOI</b> decides where; <b>(3) the entry signal</b> is the reason to enter, and you may only look for it once price is <b>inside or at the AOI</b>. Then the stop and the target. He says his own early mistake was to "jump the gun" straight to step 3.</p>}}
<p>The course calls this <b>confluence trading</b>: having the most reasons to take (or skip) a trade. Extra reasons make a trade better but are never required. Examples are a pattern such as head and shoulders, a bounce off the 50 EMA line, a round price number, or a previous support or resistance level. The creator's own view is that more reasons means a lower-risk trade, and no trade is ever guaranteed.</p>
<h2>The nine checks, in order</h2>
<p>Every trade idea goes through these gates. If a gate fails, the answer is simply "no trade, next pair".</p>
<table>
<thead><tr><th style="width:7mm">#</th><th>Check</th><th>Plain question</th><th>Passes when</th><th style="width:14mm">Part</th></tr></thead>
<tbody>
<tr><td>1</td><td><b>Pair</b></td><td>Is this one of my pairs?</td><td>It is on your watchlist and on this week's shortlist</td><td>3, 11</td></tr>
<tr><td>2</td><td><b>Time</b></td><td>Is it the right time of day?</td><td>Inside the 1:00 to 10:30 AM New York window, not the Sydney or Tokyo session</td><td>4</td></tr>
<tr><td>3</td><td><b>Structure</b></td><td>Up or down on each chart?</td><td>You have a clear bullish or bearish read on weekly, daily and 4H</td><td>5</td></tr>
<tr><td>4</td><td><b>Agreement</b></td><td>Do the charts agree?</td><td>The weekly and daily agree (the 4H too is best)</td><td>6</td></tr>
<tr><td>5</td><td><b>Zone</b></td><td>Where is price trapped?</td><td>You have marked the HH-HL (up) or LH-LL (down) boundaries</td><td>6</td></tr>
<tr><td>6</td><td><b>AOI</b></td><td>Is price at a zone that matters?</td><td>Price is at a valid AOI inside that zone</td><td>7</td></tr>
<tr><td>7</td><td><b>Signal</b></td><td>Has price confirmed it?</td><td>A confirmation candle or pattern prints at the AOI, in trend direction</td><td>8</td></tr>
<tr><td>8</td><td><b>Plan</b></td><td>Is the trade worth it?</td><td>Stop just beyond the level, target at the next structure point, reward at least twice the risk</td><td>9</td></tr>
<tr><td>9</td><td><b>Size</b></td><td>How big?</td><td>Lot size set from the money you accept to lose and the stop distance</td><td>9</td></tr>
</tbody></table>
{{CALL:ex|Optional: a simpler version (not in this guide's checklist)|<p>In a later video he strips the strategy down to <b>one pair, one timeframe, one session and one entry signal</b>, and says to stick to it until you are consistently profitable before adding anything. His picks: <b>EURUSD</b> (low costs, very liquid, predictable patterns), the <b>4-hour</b> chart, the <b>London</b> session, and the <b>engulfing candle</b> as the entry signal. You read the structure on that one chart, trade only that direction, and enter on the engulfing candle. He calls the three-timeframe method in this guide "the more advanced approach". Both are valid; start with whichever you can follow consistently.</p><p>A newer video (a plan for a $50 start) keeps the "one thing only" idea but makes the one thing a <b>pattern</b>: the head and shoulders on the 4-hour chart, searched across all the major pairs, because one pair alone may not show it for months. See Part 12.</p>}}
<h2>The mindset rules</h2>
<ul>
<li><b>Trade with the trend.</b> "The trend is your friend." Never try to pick the top or the bottom.</li>
<li><b>Fewer, better trades.</b> Money is made by entering the right trade at the right spot, not by being busy. Every extra trade is extra risk.</li>
<li><b>You are never obliged to trade.</b> He compares it to a baseball batter who only swings at the perfect pitch. Waiting is part of the strategy.</li>
<li><b>Decide before you enter.</b> The stop, the target and the amount at risk are all fixed before you click.</li>
<li><b>Set and forget.</b> After you enter, you leave the trade alone until it hits the stop or the target.</li>
<li><b>Use alerts, not guesses.</b> Set a price alert at the level you are waiting for, step away, and check when it rings.</li>
<li><b>Confirmation, not anticipation.</b> Wait for the candle to close and "let the market show you its hand" before you enter.</li>
<li><b>Wait for the pullback; never chase.</b> After a big push, do not buy the high or sell the low. Wait for the "discount", then your confirmation.</li>
<li><b>Think in weeks, not days.</b> Aim for a weekly result, not a daily one, so you are never tempted to force a trade. One good trade can make the week. He expects "one good setup a week, maybe two".</li>
<li><b>Analyse when the market is closed.</b> On Sunday, before the open, you cannot enter a trade, so your read is neutral: you are finding the direction, not hunting for an entry.</li>
<li><b>Never raise your risk</b> after a loss (to win it back) or after reaching a goal (greed). Keep the same risk every trade.</li>
</ul>
"""

P2 = """
<h2>Currency pairs: who is winning the fight?</h2>
<p>You always trade one currency against another. In <b>EUR/USD</b> the euro is the <b>base</b> (first) currency and the US dollar is the <b>quote</b> (second) currency. The price tells you how many dollars one euro costs.</p>
<table>
<thead><tr><th>If EUR/USD...</th><th>It means</th><th>You would</th></tr></thead>
<tbody>
<tr><td>goes <span class="pill g">UP</span></td><td>The euro (base) is getting stronger than the dollar</td><td>Buy (bet the base strengthens)</td></tr>
<tr><td>goes <span class="pill r">DOWN</span></td><td>The dollar (quote) is getting stronger than the euro</td><td>Sell (bet the quote strengthens)</td></tr>
</tbody></table>
<p>The creator calls this "the fight": two currencies in an endless battle, and the chart is the trail the fight leaves behind. Buying and selling are <b>equally valid</b>. A falling market is not less tradable than a rising one.</p>
<p>You never own the currency. You are betting on whether the price will go up or down.</p>
<h2>Which pairs?</h2>
<ul>
<li><b>The 7 majors</b> are his preferred pairs: EUR/USD, GBP/USD, USD/JPY, USD/CHF, USD/CAD, AUD/USD, NZD/USD. They move more, cost less to trade, and tend to be "respected" (cleaner reactions, fewer random spikes).</li>
<li>He also trades crosses such as GBP/CHF, AUD/JPY and NZD/CAD. In total he works with about 15 to 20 pairs (full list in Part 3).</li>
<li>Exotic pairs have lower volume and big moves are less likely. He sees them as riskier.</li>
</ul>
<h2>Reading a candle</h2>
{{D:anatomy}}
<ul>
<li>A candle is one period of time (for example 4 hours). It shows where price <b>opened</b>, <b>closed</b>, and the highest and lowest points it reached.</li>
<li>The thick part is the <b>body</b> (open to close). The thin lines are <b>wicks</b>. A wick is a record of where price has been.</li>
<li>A wick usually means <b>rejection</b>: price went there and was pushed back. Wicks are respected on every timeframe.</li>
<li>The next candle opens where the last one closed.</li>
</ul>
{{CALL:rule|The rule that runs through the whole course|<p><b>Structure is judged by candle bodies, never by wicks.</b> You will see this again in Parts 5, 7 and 8.</p>}}
<h2>Timeframes: choosing your seat</h2>
<p>The same market looks different on every timeframe. He compares it to watching a boxing match: the higher the timeframe, the higher your seat in the arena, and the better the view of the whole fight. The weekly chart is the best seat.</p>
<table>
<thead><tr><th>Timeframe</th><th>Job</th></tr></thead>
<tbody>
<tr><td><b>Weekly</b>, <b>Daily</b>, <b>4-hour</b></td><td><b>The trend timeframes.</b> You read the trend here, and you draw your areas of interest here (weekly and daily first; the 4-hour only as a minor extra).</td></tr>
<tr><td><b>2-hour</b>, <b>1-hour</b>, <b>30-minute</b>, <b>15-minute</b></td><td><b>The entry timeframes.</b> "Completely avoided" until you are ready to enter. This is where the entry signal shows up. He never goes below 15 minutes. Newer videos read them together as a fourth "lower timeframe" group that gives an extra vote on direction (Part 6).</td></tr>
</tbody></table>
<p>He pictures the timeframes as a building: the weekly is the foundation, the daily the walls, the 4-hour the concrete that holds them, and the lower timeframes the inside, which you can arrange as you like as long as the structure is strong.</p>
<p>A big move on a low timeframe does not change the look of the higher-timeframe candle. When in doubt, judge the move from the higher timeframe.</p>
<h2>Pips</h2>
<p>A <b>pip</b> is the standard small unit of price movement. For most pairs it is the 4th decimal place (0.0001). For pairs with the Japanese yen it is the 2nd decimal place (0.01). Example: EUR/USD moving from 1.1700 to 1.1720 is 20 pips. You use pips to measure stop sizes and the height of an AOI.</p>
<h2>Trading styles</h2>
<p>He describes four styles by how often you trade: position trader (1 to 2 trades a month), swing trader (4 to 5), day trader (8 to 12) and scalper (14 to 25). His own approach is a <b>hybrid of swing and day trading</b>: swing-style higher-timeframe analysis and bigger targets, with the sharp entries of a day trader.</p>
<p>In a later video he puts rough numbers on three styles: a <b>scalp</b> lasts 30 minutes to an hour; a <b>day trade</b> lasts 5 to 8 hours or overnight, one or two a day at most; a <b>swing trade</b> lasts about 4 to 9 days, one or two a week "if that". He calls swing trading the calmest choice for someone with a job, because the weekly direction does the work.</p>
"""

P3 = """
<h2>Three tools, three jobs</h2>
<table>
<thead><tr><th>Tool</th><th>What it is for</th></tr></thead>
<tbody>
<tr><td><b>TradingView</b></td><td>Analysis. Charts, drawing, alerts. He spends 90 to 95% of his time here. It shows the raw market price.</td></tr>
<tr><td><b>A broker</b></td><td>"The bank". Holds your money. It adds a small fee (the spread) to the price.</td></tr>
<tr><td><b>MetaTrader 5</b></td><td>Execution. You only open it to press buy or sell, with the lot size, stop and target already decided.</td></tr>
</tbody></table>
<p>Because the broker adds a spread, a new trade starts slightly negative. That is normal.</p>
<h2>Setting up the chart</h2>
<ol class="steps">
<li><b>Use candlesticks</b> for trading and patterns, and the <b>line chart</b> for reading structure. Ignore bar charts and everything else.</li>
<li><b>Remove the volume bars.</b> He never uses them.</li>
<li><b>Add the indicator "No gaps candles"</b> (a free community indicator). It fills the gaps between candles so every candle opens at the previous close. Then switch off the chart's own candles (untick body, borders and wick in the chart settings) so only the gap-free ones show. His candles are blue when up and red when down.</li>
<li><b>Add one moving average: the 50 EMA.</b> It is the only other indicator he uses. It acts as a moving support or resistance line: when price is above it, it acts as support; below it, resistance. It is a "cherry on top", never a requirement.</li>
<li><b>Star your timeframes</b> so they sit in the top bar: 15m, 30m, 1h, 2h, 4h, daily, weekly. Nothing else.</li>
<li><b>Chart time zone:</b> New York (UTC-4 in summer). All his clock times are New York time.</li>
</ol>
<h2>Drawing tools he uses (and ignores)</h2>
<table>
<thead><tr><th>Uses</th><th>Ignores</th></tr></thead>
<tbody><tr>
<td><ul style="margin:0"><li>Horizontal line and horizontal ray (levels)</li><li>Rectangle for zones, with a light fill of about 4 to 5% so you can still see the price</li><li>Trend line (only to help find structure points)</li><li>Long and short position tool (shows risk versus reward)</li><li>Head and shoulders tool, path, ellipse, text, measure tool</li><li><b>Price alerts</b> at key levels</li></ul></td>
<td><ul style="margin:0"><li>Fibonacci tools</li><li>Pitchforks</li><li>Other chart patterns</li><li>The "buy/sell" gauge, seasonals and other side panels</li><li>Back-testing (he prefers live testing)</li></ul></td>
</tr></tbody></table>
<h2>His watchlist</h2>
<p>He keeps a fixed list of the markets he trades and never edits it. The forex pairs on it:</p>
<table>
<tbody>
<tr><td><b>USD pairs</b></td><td>EURUSD, GBPUSD, AUDUSD, NZDUSD, USDJPY, USDCAD, USDCHF</td></tr>
<tr><td><b>GBP crosses</b></td><td>GBPJPY, GBPCHF, GBPCAD, GBPAUD, GBPNZD, EURGBP</td></tr>
<tr><td><b>Other crosses</b></td><td>EURJPY, EURAUD, AUDJPY, AUDCHF, AUDCAD, NZDJPY, NZDCAD, CADJPY</td></tr>
</tbody></table>
<p class="small">He also keeps a few non-forex markets (oil, bitcoin, ethereum and others). This guide covers forex only.</p>
<h2>How you place orders</h2>
<ul>
<li><b>Market execution only.</b> You enter immediately at the current price, with the stop and target already typed in.</li>
<li><b>No pending orders</b> (buy limit, sell limit, buy stop, sell stop). He does not believe in entering "without confirmation". Instead you set an alert at the area and decide when price gets there.</li>
</ul>
"""

P4 = """
<p>Forex is open 24 hours a day, five days a week, but not every hour is worth trading. His rule is to be in the market only when the big sessions are active.</p>
{{D:sessions}}
{{CALL:rule|The time rules|<ul><li><b>Do not trade during the Sydney or Tokyo sessions.</b> There is little volume and little movement.</li><li><b>Trade roughly between 1:00 AM and 10:30 AM New York time.</b> (He says "10:00" in places. The marker he drew sits at about 10:30.)</li><li><b>No new trade after about 10:30 AM.</b> He has not taken one later in about four years.</li><li><b>Best moments to enter:</b> just before London opens (pre-London), in the middle of London, or just before the volatility fades around 9 to 10 AM at the end of the London and New York overlap.</li></ul>}}
<h2>New York time and Manila time side by side</h2>
<p>Every time in the course is New York time. Manila is 12 hours ahead while the US is on summer time (about March to early November) and 13 hours ahead in winter, because Manila does not change its clocks. In 2026 the US clocks go back on 1 November.</p>
<table>
<thead><tr><th>Event</th><th>New York (his)</th><th>Manila, US summer (EDT)</th><th>Manila, US winter (EST)</th></tr></thead>
<tbody>
<tr><td>Window opens, pre-London analysis</td><td>1:00 AM</td><td>1:00 PM</td><td>2:00 PM</td></tr>
<tr><td>London opens</td><td>3:00 AM</td><td>3:00 PM</td><td>4:00 PM</td></tr>
<tr><td>New York opens</td><td>8:00 AM</td><td>8:00 PM</td><td>9:00 PM</td></tr>
<tr><td>Last entry</td><td>10:30 AM</td><td>10:30 PM</td><td>11:30 PM</td></tr>
<tr><td>London ends</td><td>12:00 PM</td><td>12:00 AM (next day)</td><td>1:00 AM (next day)</td></tr>
<tr><td>Daily and weekly candles close</td><td>5:00 PM</td><td>5:00 AM (next day)</td><td>6:00 AM (next day)</td></tr>
<tr><td>Sunday market open, weekly bias</td><td>Sunday 5:00 PM</td><td>Monday 5:00 AM</td><td>Monday 6:00 AM</td></tr>
</tbody></table>
<p class="small">The whole entry window falls on the same calendar day in Manila, so "Monday to Wednesday" is the same in both places. London's clocks change on different dates from the US, so for about 1 to 3 weeks each spring and autumn London opens at 4:00 AM New York time instead of 3:00 AM (in 2026: 8 to 29 March and 25 October to 1 November). His window is written in New York time, so it does not move.</p>
<h2>Why this window</h2>
<ul>
<li>London opens at 3:00 AM and New York at 8:00 AM. Where they overlap, volatility is highest.</li>
<li>After about 12:00 PM there is little movement for roughly 10 hours. A trade opened at noon just sits there, and holding past the 5:00 PM market close can add swap or commission costs.</li>
<li>He starts his <b>pre-London analysis at 1:00 AM</b>.</li>
<li>Pairs with the US dollar get "double the volatility" from the London open into the New York open, because the dollar side wakes up at the New York open.</li>
<li>The window applies to every pair, not only USD pairs.</li>
<li><b>Match the session to the market.</b> The S&amp;P 500 and gold depend on New York; GBPUSD leans London. For EURUSD, and in his view any other market, he uses London because London and the overlap give you both sessions. Enter 1 to 2 hours before London and hold through it.</li>
</ul>
{{CALL:rule|Which days, and what to do if the signal comes early|<ul><li><b>Enter only on Monday, Tuesday and Wednesday.</b> After Wednesday there is not enough time to reach a take profit (his average target is about 80 to 100 pips, and Thursday's New York session gives only about 5 hours). He breaks this only rarely (a shorter target, a very strong confirmation, or strong momentum); this guide's checklist does not.</li><li><b>If the confirmation prints before a session</b> (for example before Sydney), <b>wait until right before London</b> and enter inside the session. He calls this the "black and white rule". You may get a worse or a better price, but the confirmation has proven itself.</li><li>Do not enter just because a confirmation printed first thing on Monday morning or in the last 3 hours before the weekly close.</li><li><b>Never on Sunday.</b></li><li>Avoid entries where you would get only about an hour of volume and then roughly 9 hours of nothing.</li></ul>}}
{{CALL:warn|Watch out|<p>Being inside the window is <b>not</b> a reason to trade. It only means you are allowed to. The strategy still has to say yes.</p><p>His own session graphic shows Sydney lasting until about 2 AM and Tokyo until about 4 AM, which overlaps his 1:00 AM start. He treats the "pre-London" hours as tradable anyway. This is one of the small inconsistencies in the course (see Part 14).</p>}}
<h2>News</h2>
<p>He checks a calendar called <b>Forex Factory</b> for the date, time and impact of news. Only the <b>red folder</b> (high-impact) events matter; he ignores yellow and grey, and orange is less important. He does not change his strategy around news and does not use news to create a strategy: for him, price action decides, and fundamentals are only an added reason. Occasionally he sits out a big speech or event. Prop firms are stricter: no new trade within <b>10 minutes</b> either side of news (Part 12).</p>
"""

P5 = """
<p class="lead">Market structure is the most important skill in the course. He calls it "the core foundation of everything else". Everything below it (zones, entries, patterns) depends on getting this right.</p>
<h2>Up or down? Highs and lows decide.</h2>
{{D:bull}}
{{D:bear}}
<ul>
<li><b>Bullish</b> = the market is making <b>higher highs (HH)</b> and <b>higher lows (HL)</b>. Each push goes higher, and each pullback stops higher than the last.</li>
<li><b>Bearish</b> = the market is making <b>lower lows (LL)</b> and <b>lower highs (LH)</b>.</li>
<li>These turning points are called <b>structure points</b> or "elbows". Think of them as the bends in a road.</li>
<li>You can only call the market bullish or bearish <b>after you have placed these points</b>. Price level alone tells you nothing: a pair at its lowest price is bearish because of its lower highs and lower lows, not because it is low.</li>
</ul>
{{CALL:rule|"Inside" the structure|<p>As long as price stays <b>between the current HH and HL</b>, the market is bullish. As long as it stays <b>between the current LH and LL</b>, it is bearish. Nothing changes until something breaks.</p>}}
<h2>What counts as a break?</h2>
{{D:bodywick}}
<ul>
<li>A break counts only when a <b>candle body closes</b> beyond the level.</li>
<li>Wicks do not count. Touching a level does not count. Getting close ("three touches") does not count.</li>
<li>The candle must be <b>closed</b>. A candle still forming can change completely before it ends.</li>
<li>A small body-close break still counts. He gives no minimum size.</li>
</ul>
<h2>The four situations</h2>
{{D:state}}
<table>
<thead><tr><th>You are...</th><th>A candle body closes...</th><th>What happens</th></tr></thead>
<tbody>
<tr><td><span class="pill g">Bullish</span></td><td>above the HH</td><td>Still bullish. The HH moves up to the top of the push. A new HH always brings a new HL (use the snake trick, below).</td></tr>
<tr><td><span class="pill g">Bullish</span></td><td>below the HL</td><td><b>The bias flips to bearish.</b> The lowest point of the move is the new LL, and you find the new LH with the snake trick.</td></tr>
<tr><td><span class="pill r">Bearish</span></td><td>below the LL</td><td>Still bearish. The LL moves down. A new LL always brings a new LH.</td></tr>
<tr><td><span class="pill r">Bearish</span></td><td>above the LH</td><td><b>The bias flips to bullish.</b> The new high is the HH, and you find the new HL with the snake trick.</td></tr>
</tbody></table>
<h2>The snake trick: finding the paired point</h2>
<p>After a new extreme appears, you need to place its partner (the new LH after a new LL, or the new HL after a new HH). The "snake trick" does it in three moves.</p>
{{D:snake}}
<ol class="steps">
<li><b>Start at the head of the snake</b>: the new extreme (the new LL, or the new HH).</li>
<li><b>Walk backwards</b> along price.</li>
<li><b>The first clean, sharp turn</b> is the partner. Skip soft bumps: if the snake could "slide right through" a small wiggle without really turning, it is not a structure point.</li>
</ol>
<p>A single-candle pullback usually does not count unless it is a clear, strong candle (for example an engulfing candle that "makes a statement"). If a small bump and a sharper turn both exist, he chooses the sharper, cleaner one. He admits there is no perfect rule here: it takes practice and some judgement.</p>
<h2>Use the line chart, then draw on the bodies</h2>
<ol class="steps">
<li>Switch to the <b>line chart</b>. It shows only closing prices, so the elbows are easy to see. He calls it his "cheat sheet".</li>
<li>Find and label the structure points.</li>
<li>Switch back to <b>candlesticks</b> and move each line to the <b>body</b> of the candle (not the wick tip).</li>
<li>Check each point has a visible "elbow" on the candles. If the candles show no turn, do not count it.</li>
</ol>
<h2>Confirmed or current?</h2>
<p>A new HH or LL is only <b>current</b> while its candle is still open or price is still pushing. It becomes <b>confirmed</b> once the candle has closed and price has pulled back or stopped. Until then, keep sliding the line along with the latest extreme.</p>
{{CALL:rule|Three checks from the newer videos|<ul><li><b>The HL is always behind the HH</b> (and the LH behind the LL). The newest extreme is always "in front". "The higher low could never be in the future": a dip after the current HH is just a pullback until a new HH forms.</li><li><b>One timeframe cannot be bullish and bearish at once.</b> You never have a HH together with a LH on the same chart. Different timeframes can disagree.</li><li><b>Take the points from recent price action</b>, not from a swing two months back. Run the snake trick from the current head.</li></ul>}}
<h2>How far back to look</h2>
<table>
<thead><tr><th>Timeframe</th><th>Look back at most</th></tr></thead>
<tbody>
<tr><td>Weekly</td><td>5 to 6 years</td></tr>
<tr><td>Daily</td><td>1 to 2 years</td></tr>
<tr><td>4-hour</td><td>6 to 12 months</td></tr>
</tbody></table>
<p>Read the history once. After that you only track the live HH and HL (or LH and LL) and wait for something to break. Keep the chart at a healthy zoom: not so zoomed out the candles are tiny, and not so zoomed in that you only see the last five candles. Structure is different on every timeframe.</p>
{{CALL:ex|Example: a quick flip on the EURUSD 4-hour chart|<p>The market is bullish. The HL sits at about 1.1713. A 4-hour candle closes at about 1.1697, <b>below</b> the HL. The market is now bearish, and the old rally top becomes the lower high. Later in the same replay, a large blue candle closes <b>above</b> the lower high and the market is bullish again. On one stretch of this chart the bias went bearish, bullish, bearish and bullish again within about 12 hours (three 4-hour candles). This is why you wait for each candle to close before deciding. (Prices read off his chart.)</p>}}
{{CALL:warn|Common mistakes|<ul><li>Counting a wick as a break.</li><li>Acting on a candle that has not closed yet.</li><li>Calling the trend from the price level instead of the highs and lows.</li><li>Counting every tiny wiggle as a structure point.</li><li>Forgetting to move the partner point when a new HH or LL appears.</li><li>Zooming so far out (or in) that you can no longer read the candles.</li></ul>}}
"""

P6 = """
<p class="lead">One chart is never enough. You read the structure on three timeframes, check that they agree, and only then look for a trade.</p>
<h2>The steps</h2>
<ol class="steps">
<li><b>Read the weekly.</b> Bullish or bearish? Mark its HH and HL (or LH and LL).</li>
<li><b>Read the daily.</b> Same job. If the daily has moved on inside the weekly structure, use the recent daily action for the daily call.</li>
<li><b>Read the 4-hour.</b> Same job.</li>
<li><b>Check agreement</b> (next section).</li>
<li><b>Mark the zone.</b> Draw the HH, HL, LH and LL lines of each timeframe on your chart. Price is now "trapped" between them, and that area is the only part of the chart you look at.</li>
</ol>
<h2>Do the timeframes agree?</h2>
<p>In this guide's core plan the <b>weekly and daily must agree</b>; that sets the direction. The 4-hour agreeing too makes it the best grade. (His course rule is "two timeframes in a row", which also allows daily and 4-hour against the weekly; he calls that case high risk, so it is optional below.)</p>
<table>
<thead><tr><th>Weekly</th><th>Daily</th><th>4H</th><th>Verdict</th></tr></thead>
<tbody>
<tr><td><span class="pill g">Up</span></td><td><span class="pill g">Up</span></td><td><span class="pill g">Up</span></td><td><b>Best case, "low risk".</b> All three agree. Look for buys.</td></tr>
<tr><td><span class="pill g">Up</span></td><td><span class="pill g">Up</span></td><td><span class="pill r">Down</span></td><td><b>"Mid risk".</b> Weekly and daily agree. Either take the extra risk, or (his advice in a later video) wait for the 4H to turn up again.</td></tr>
<tr><td><span class="pill r">Down</span></td><td><span class="pill g">Up</span></td><td><span class="pill g">Up</span></td><td><b>"High risk", counter-trend.</b> Not in the core plan. He sometimes trades it with the optional recipe below.</td></tr>
<tr><td><span class="pill g">Up</span></td><td><span class="pill r">Down</span></td><td><span class="pill g">Up</span></td><td><b>Skip.</b> Weekly and 4H match but not two in a row. This is not "in sync".</td></tr>
<tr><td><span class="pill r">Down</span></td><td><span class="pill r">Down</span></td><td><span class="pill r">Down</span></td><td><b>Best case for sells.</b> Mirror of the first row.</td></tr>
</tbody></table>
<p>This check alone removes about half of the markets on his watchlist every week.</p>
<p><b>The lower timeframes get a vote too.</b> In newer videos he also reads the 2-hour, 1-hour, 30-minute and 15-minute charts and counts which way most timeframes point. The weekly and daily together outweigh all the lower ones: weekly up, daily up, 4H down, 2H down, 1H up is still a buy bias. When the weekly, daily and 4-hour agree, "what the lower time frames are doing doesn't really matter". This vote is optional: it never decides a trade, so the checklist leaves it out.</p>
{{CALL:ex|Why the 4-hour turns against you before a good buy|<p>All three timeframes are bullish, and your weekly and daily AOI sits <b>below</b> the 4-hour higher low. For price to come down into the AOI, the 4-hour has to break its higher low and turn bearish. That is normal: "somebody has to go bearish" for the retracement to happen. Do not sell that pullback (you would be selling into support). At the AOI, either wait for the 4-hour to shift back up or take the higher risk; he calls this "trader preference". His GBPUSD example (January 2026) had the weekly and daily AOI at about 1.351 to 1.358, below a 4-hour higher low near 1.368.</p>}}
<h2>Trapping price: the zone</h2>
<p>Once you know the direction, draw the lines that trap price:</p>
<ul>
<li><b>Bullish:</b> the zone is between the HH (top) and the HL (bottom).</li>
<li><b>Bearish:</b> the zone is between the LH (top) and the LL (bottom).</li>
</ul>
<p>You only look for trades <b>inside the zone</b>. This is the area where the market is valid for buying (if bullish) or selling (if bearish). If price drops below a bullish HL, the zone no longer exists, because the market has turned bearish.</p>
{{D:zonelevels}}
{{CALL:ex|Example: AUDJPY (September 2025)|<table style="margin:0"><thead><tr><th>Timeframe</th><th>Read</th><th>Key levels (approx.)</th></tr></thead><tbody>
<tr><td>Weekly</td><td><span class="pill g">Bullish</span></td><td>HH about 98.0, HL about 95.4</td></tr>
<tr><td>Daily</td><td><span class="pill g">Bullish</span></td><td>HH about 98.4, HL about 96.6</td></tr>
<tr><td>4-hour</td><td><span class="pill r">Bearish</span></td><td>LH about 98.1, LL about 97.8 (price about 97.88)</td></tr></tbody></table><p style="margin-top:2mm">Weekly and daily are in sync, so the market is worth watching for buys. The 4-hour disagrees, so he either takes the extra risk or waits for the 4-hour to turn bullish. He stressed that agreement means "it makes sense to buy", not "buy now". You still need an AOI and an entry signal.</p>}}
{{CALL:ex|Optional, high risk: trading against the weekly|<p>He sometimes trades <b>against</b> the weekly trend and calls it aggressive. His GBPNZD buy (a win) and EURAUD sell (a win) followed the same steps:</p><ol style="margin:0 0 0 5mm"><li>The weekly is bearish but "overdue" for a deep retracement toward a weekly AOI.</li><li>The <b>daily</b> shifts (above its EMA, break and retest of structure) and the <b>4-hour agrees</b>. This is the "daily + 4H in sync" case from the table above.</li><li>Enter on the retest after the candle closes. Stop beyond the AOI or daily structure point.</li><li><b>Target 1:2, placed at the weekly AOI</b>, where the weekly may react.</li></ol><p style="margin-top:2mm">In another video he tells the GBPNZD trade from the weekly side: after a big weekly drop, the market "needs" a retracement before the next leg down, and the <b>daily</b> shifting to higher highs and higher lows was his sign that the retracement had started. He bought it with the target at the weekly zone just above the round number 2.3000 and closed at 1:2.</p><p>He also showed losses: an NZDCAD buy taken <b>below</b> a weekly resistance, off a choppy 4-hour, which he "should have stayed away" from; and in 2026 a GBPCHF sell against the weekly, taken off a head-and-shoulders right shoulder, which he calls "premature". Do not buy while price is below a weekly level, and never take this recipe on a small account.</p>}}
{{CALL:warn|Common top-down mistakes|<ul><li>Comparing the weekly with the 4-hour and skipping the daily.</li><li>Letting the 2-hour or lower charts decide the trend. They are for entries and, at most, an extra vote.</li><li>Treating agreement as a buy signal. It is only permission to keep looking.</li><li>Forgetting that each timeframe has its own HH, HL, LH and LL.</li></ul>}}
"""

P7 = """
<p class="lead">An Area of Interest is a zone where price has reacted before and may react again. He uses one word for support, resistance, supply and demand, and order blocks: <b>AOI</b>. "It is all the same thing."</p>
<h2>What makes an AOI valid?</h2>
{{D:zone}}
<ol class="steps">
<li><b>Inside the zone.</b> It must sit between the HH and HL (bullish) or between the LH and LL (bearish). Anything outside is invalid.</li>
<li><b>At least 3 touches.</b> A touch is one clear reaction (a rejection) from the area. Support and resistance touches can be mixed. More touches is better. With fewer than 3, it is not an AOI.</li>
<li><b>Between 5 and 60 pips tall.</b> Tighter is better; 20 to 35 pips is the sweet spot. Do not stretch the box just to collect more touches.</li>
<li><b>Built from bodies, not wicks.</b> Count the elbows on the line chart first, then check them on candles. Drop any touch that is not clean. If 3 clean ones remain, the AOI stands.</li>
<li><b>Drawn on the weekly and daily first.</b> The 2025 course said "no AOI on the 4-hour", and an early-2026 video still said "only two time frames". His newest videos also use 4-hour AOIs, so you may add one, but treat it as <b>minor</b>. Weekly AOIs go inside the weekly zone; daily AOIs inside the daily zone.</li>
<li><b>Few of them.</b> Typically two or three, never more. Drop any AOI that sits far away behind another zone price would have to break first.</li>
<li><b>Look back at least two years</b> for them: "whatever happened in the past can very clearly happen again".</li>
</ol>
<h2>When weekly and daily overlap</h2>
<p>If a weekly AOI and a daily AOI sit on top of each other, merge them into one tight box that still has at least 3 touches on both charts. The overlap means two timeframes agree, which gives a higher-probability area. He labels such a box "weekly and daily AOI" so he can see at a glance that it is "two areas of interest strong". They overlap "for the most part".</p>
{{CALL:ex|Example: the AUDJPY areas|<p>After merging, he ended up with two areas where weekly and daily overlap: one at about 97.25 to 97.55 and one at about 96.62 to 96.93 (about 31 pips, sitting on the daily higher low). Price then had to retrace into one of them before he would look for an entry. If forced to pick one, he chose the lower one, because price had broken a previous structure point and then retested it.</p>}}
<h2>How to use an AOI</h2>
<ul>
<li><b>No AOI at the current price = no trade.</b> You cannot enter unless price is at a valid AOI. If price retraces but never reaches one, move on to the next pair.</li>
<li><b>Buy at support, sell at resistance.</b> Never buy at resistance or sell at support. To buy from a level, price must be <b>above</b> it. If price is below a level, that level is resistance.</li>
<li><b>Support and resistance can swap roles</b>, but only after a break <b>and a retest</b>.</li>
<li>If price breaks below the AOI you wanted to buy from, <b>do not buy it</b>. In his newer teaching a broken AOI is simply removed; it can only come back as a flipped zone after a break and a retest from the other side.</li>
<li><b>The AOI answers "where", never "when".</b> Once it is drawn, wait for price to come back into it. Only then look for the entry signal.</li>
<li><b>Nearest AOI first, and each AOI is its own trade.</b> Treat the one closest to price as the first. Once price is there, act as if no other AOI exists. If that trade loses and price runs on to the next AOI, that is a brand-new trade.</li>
<li>An AOI respected 4 or 5 times "should" react more than one touched once, "but that's never always the case". Use the touch count as a hint, not a ranking.</li>
</ul>
<h2>Things that make an AOI stronger</h2>
<p>In his live trades he often stacked several reasons at the same area:</p>
<ul>
<li>a previous daily support or resistance level</li>
<li>the daily, weekly or 1-hour EMA</li>
<li>a round psychological number (for example 157.500 or 1.12500)</li>
<li>the neckline of a head and shoulders or a double top</li>
</ul>
{{CALL:rule|"Liquidity" is just another word for your AOI|<p>In a later video he explains that <b>liquidity</b> simply means buyers and sellers (with their take profits and stop losses) sitting at a price. It is strongest where price has <b>rejected again and again</b>, which is exactly what an AOI is. Above the zone buyers dominate, below it sellers do. He wants zones on higher timeframes with more than three taps.</p><p><b>Round numbers hold liquidity too.</b> His example: Ethereum never quite reached 5,000 because many holders set take profits just below it, so selling began a little short of the round number. Price may likewise stall a few points before a round level; he gives no exact distance.</p>}}
{{CALL:warn|Watch out|<p>The course gives no exact test for what counts as "one touch" (how close is close enough). It also leaves some choices to your eye, such as which three touches to use. Expect to practise on many charts before your AOIs look like his.</p>}}
"""

P8 = """
<p class="lead">At the AOI you wait for confirmation. This part lists the confirmations he uses. They only count <b>at an AOI</b>, <b>in the direction of the trend</b>, and on a <b>closed candle</b>.</p>
{{CALL:rule|No AOI, no step 3|<p>A trend on every chart is still not an entry: "that doesn't mean that we could just go ahead and buy". You may only look for the entry signal once price is <b>inside or at the AOI</b> (touching the edge counts). Price on its way to the AOI is just "the trade on the way to the area".</p><p><b>Order of actions</b> (newest walkthrough): the signal candle closes; you set the <b>stop first</b> ("the most important step"), <b>then the target</b>, and enter at the <b>open of the next candle</b>. He accepts the slightly worse price as the cost of having a real signal.</p>}}
<h2>The entry confirmation in five checks</h2>
<p>In a follow-up video he calls this "the only confirmation you need". His core idea: <b>enter off a confirmation, not an anticipation</b>. "You want the market to show you its hand first." A confirmation is something that has already happened; an anticipation is a guess.</p>
<ol class="steps">
<li><b>The candle has closed.</b> This works on any timeframe, from 1 minute to monthly. One second before the close it is still anticipation: he has seen candles reverse completely in the last 5 seconds.</li>
<li><b>It is a rejection or an engulfing.</b> A rejection is a doji or small-bodied candle with a long wick. An engulfing is a candle whose body closes beyond the last candle (bullish to buy, bearish to sell). Having both is stronger, and several dojis in a row before an engulfing is stronger still. If you have neither, you do not enter.</li>
<li><b>It is at a support or resistance zone</b> (your AOI). Confirmations in the middle of the chart are everywhere and mean nothing.</li>
<li><b>It points the same way as the trend.</b> A bullish confirmation at support in an uptrend; a bearish one at resistance in a downtrend.</li>
<li><b>The time is right.</b> The right session and the right weekday (Part 4).</li>
</ol>
{{CALL:ex|Rejection alone, or wait for the engulfing too?|<p>He may enter on the rejection alone, or wait for the engulfing as well. It depends on how strong the level is, the timeframe, how many days are left in the week, the risk-to-reward, and your other reasons. Waiting avoids some losses but misses some good trades. He calls these the "extra extra extra confirmations" and says either choice is fine as long as you understand the trade and are comfortable with the risk.</p>}}
{{CALL:warn|Do not flip on a counter-direction candle|<p>If a bearish engulfing appears after a bullish setup, you do <b>not</b> switch sides. Direction does not change every day; on swing and day trades it often holds for almost a month. Entering the opposite candle "is not a strategy, that's gambling". Skip that trade and wait for the next setup that fits your plan.</p>}}
<h3>Liquidity sweeps: do not wait for them</h3>
<p>A "liquidity sweep" (or "grab", or "fake out") is a wick that pokes through a zone and then reverses. Many traders believe banks hunt stop losses this way. He calls that story "almost a big hoax" with no hard evidence (his opinion, and he offers no data). What matters for you is his rule: <b>you cannot predict a sweep, so do not wait for one.</b></p>
<ul>
<li>Waiting for a sweep is "playing defense". Entering on a confirmation is "playing offense".</li>
<li><b>His example:</b> price approached one support zone 7 times. Only once did it sweep. The other six times it gave a bullish engulfing, a morning star, a bullish rejection candle or a pin bar. A trader who waited for the sweep missed six trades.</li>
<li>If price moves <b>against</b> the direction you want (for example bullish candles when you want to sell at resistance), do not sell yet and do not guess it is a sweep. Wait for a candle that confirms your direction, such as a bearish candle for a sell.</li>
<li>You will still get wicked out sometimes. It happens to him about once every two weeks. He takes the next trade and does not let it affect it.</li>
</ul>
<h3>Reading a daily candle with the 4-hour (the "wick fill")</h3>
<p>A daily candle with a long lower wick looks like a rejection. Sometimes it is really a <b>wick fill</b>: inside that same day the 4-hour went down into the area, then turned up and made a higher low. The 4-hour higher low is what sets up the next daily bullish engulfing, which is your entry. He says a strong bullish daily with a strong lower rejection gives "almost 70%" odds of a push up the next day (his figure, not tested).</p>
<h2>Candle signals</h2>
{{D:candles}}
<table>
<thead><tr><th>Signal</th><th>What it looks like</th><th>How he uses it</th></tr></thead>
<tbody>
<tr><td><b>Doji</b> / spinning top</td><td>Almost no body (doji) or a small body with wicks on both sides</td><td>A slowdown at the AOI after a push. The next candle might engulf. A weak signal on its own.</td></tr>
<tr><td><b>Hammer</b></td><td>Small body at the top, long lower wick, little or no upper wick</td><td>At support: sellers pushed down and buyers closed it back up. A rejection.</td></tr>
<tr><td><b>Inverted hammer</b> ("wick fill")</td><td>Small body at the bottom, long upper wick</td><td>At support, the wick is in the trade direction. The next candle is expected to fill it.</td></tr>
<tr><td><b>Engulfing</b></td><td>The last candle's <b>body</b> closes beyond the body of the previous candle; <b>the more candles it engulfs, the better</b> (two or more is stronger; swallowing a whole consolidation is his favourite)</td><td>Stronger than the signals above. A tiny hairline beyond the last body still counts. Wicks are ignored. (In the follow-up video the last candle alone is enough; in the course he wanted two. Treat two as the stronger version.)</td></tr>
<tr><td><b>Morning star</b> / <b>evening star</b></td><td>A doji (or hammer) followed by an engulfing candle covering the last two candles</td><td>His favourite. Morning star to buy, evening star to sell. Not useful against the trend.</td></tr>
</tbody></table>
<ul>
<li>The <b>higher the timeframe, the stronger</b> the signal. A daily doji at an AOI is "amazing", a 4-hour is good, a 1-hour is okay.</li>
<li><b>Where a candle forms matters more than how big it is.</b> A giant candle in the middle of the chart is weak: it may reverse completely. A small doji at a strong support that already caused a big reaction is strong. The same candle, with nothing holding it up, is weak.</li>
<li>Gravestone doji, hanging man and shooting star are treated as the same family (the bearish side). Dragonfly doji is treated as a hammer.</li>
<li><b>He rejects:</b> piercing line, three white soldiers, three black crows and dark cloud cover. "If it's not an engulfing, it's not strong enough."</li>
<li>A morning star at a resistance, or in a bearish market, is not respected.</li>
</ul>
<h2>Break and retest (his favourite)</h2>
{{D:breakretest}}
<ol class="steps">
<li>Price is held at an AOI. A <b>body closes beyond</b> the zone. That is the confirmed break.</li>
<li>Price comes back into the zone and gets <b>rejected</b> from it (a wick or body rejection).</li>
<li>You enter on the far side of the zone (buy above a broken resistance, sell below a broken support), with the stop just beyond the zone.</li>
</ol>
<div style="break-inside:avoid">
<p>He ranks the three ways to enter a break and retest:</p>
<table>
<thead><tr><th>Entry</th><th>His view</th></tr></thead>
<tbody>
<tr><td>1. On the <b>breakout</b> itself (no retest)</td><td>Least favourite. Allowed, but it does not count as the break-and-retest confluence. After a breakout it is about 50/50 that price comes back to retest.</td></tr>
<tr><td>2. On the <b>retest with no rejection candle</b></td><td>Also his least favourite.</td></tr>
<tr><td>3. On the <b>retest with a rejection candle</b></td><td><b>His favourite</b>, used on about 8 in 10 of his trades with this pattern.</td></tr>
</tbody></table>
</div>
<p>If the retest never comes, the trade is missed ("it is what it is"). He sticks to the same rule every time: "if you change your rules every single time, so will your results."</p>
{{CALL:ex|His live example: one loss, then a win|<p>On a EURAUD 4-hour chart, price failed four times to break a support zone and broke on the fifth. He waited for the retest and entered on the rejection candles, and <b>lost 1%</b>. Price broke the zone again, retested it, and he entered again on the same kind of candles and <b>made 6%</b>: net +5%. He is not afraid to re-enter when the setup returns.</p>}}
<p>Break of structure, change of character ("CHoCH") and shift of structure are all the same idea: the break of the HL in an uptrend (or LH in a downtrend).</p>
<h2>Head and shoulders</h2>
{{D:hs}}
<ol class="steps">
<li>The market is bullish and price makes a left shoulder, a higher head, then a right shoulder. Draw it on candle <b>bodies</b>. The shape does not need to be perfect.</li>
<li>The <b>neckline is horizontal</b>, at the previous higher low, and it sits at an AOI. (Not the diagonal line the drawing tool gives you.)</li>
<li><b>Do nothing until the neckline breaks</b> (a body closes below it). Before that it is only a "potential" pattern.</li>
<li>After the break, find the new LL and LH (snake trick), then look for the AOI between them. The AOI that matches the neckline is your entry zone.</li>
<li><b>Wait for the retest</b>, then wait for a bearish confirmation (shooting star, evening star, bearish engulfing). Then sell.</li>
</ol>
{{CALL:warn|Do not sell the right shoulder|<p>He used to sell at the right shoulder and now calls it extremely high risk. Even a perfect pattern can lose: he showed a losing example on purpose. A pattern that never breaks the neckline is simply not traded. In 2026 he broke this rule himself on a prop challenge (a GBPCHF sell off the right shoulder, against the weekly), lost, watched price then reach his target, and called it "premature".</p>}}
<p>In his $50 plan the 4-hour head and shoulders is the <b>only</b> setup (Part 12). He names no entry candle there; this guide keeps the confirmation candle.</p>
<p>The <b>inverted head and shoulders</b> is the exact mirror image at the bottom of a trend: break above the neckline, retest, then a bullish engulfing or morning star, then buy. A <b>double top</b> with a neckline is handled the same way.</p>
<h2>Other setups he trades (optional)</h2>
<ul>
<li><b>Consolidation breakout.</b> Price sits in a tight range at an AOI. Do not trade inside the range. Wait for the breakout, then the quick retest with an engulfing or rejection candle, then enter in the breakout direction.</li>
<li><b>Adding to a trade.</b> Wait for a retest (for a sell, a lower high) in the right session, then add. On a 2026 AUDCHF buy he added on an inverted head-and-shoulders neckline retest (minor 4-hour AOI, rising EMA, morning star or engulfing); no size given.</li>
<li><b>Better entry, re-entry.</b> If the first touch is messy, wait for a cleaner pattern there. If a wick stops you out and the zone gives a new rejection candle, enter again.</li>
</ul>
{{CALL:bad|One thing he still keeps back|<p>In the last hours of the 10-hour course he says there is a specific "entry signal" that he does not discuss, and that he explains only on his livestream. The follow-up video above teaches the entry confirmation openly, and everything in this part is what he <b>does</b> show: closed rejection and engulfing candles, stars, and breaks with retests at the AOI. He never says whether that is the same thing as the livestream signal, so the real one may be more specific than this guide. Two later videos (swing trading, top-down) say outright that they show only how to read the market, "not my exact strategy".</p>}}
<h2>What not to do</h2>
<ul>
<li>Do not enter just because the setup looks close. He lists several trades he skipped and "dodged" in a week.</li>
<li>Do not enter before the confirmation candle has closed. In one example he entered early, saw the AOI could still be retested, closed the trade, and re-entered later at a worse price.</li>
<li>Do not trade against the trend. The counter-trend trades he describes both lost.</li>
<li>Do not use pending orders.</li>
</ul>
"""

P9 = """
<h2>Step 1: the stop loss</h2>
<p>Put the stop <b>just beyond the level that would prove the idea wrong</b>. "If it gets hit, I am entirely wrong." Never pick a pip number "for literally no reason" (20, 25, 27 pips): the chart decides.</p>
{{D:stopaoi}}
<ul>
<li><b>Beyond the whole AOI</b> (his newest walkthrough): for a buy, below the bottom of the AOI, not just below the signal candle's wick, because if price falls through the whole area you are wrong about the trade. Add a buffer of about <b>5 to 10 pips</b>.</li>
<li><b>Check the 1:2 before you enter.</b> In his 2026 challenge trades he kept the stop just beyond the AOI on purpose so that the next structure point was still at least twice as far away. If a sensible stop leaves less than 1:2, skip the trade; do not squeeze the stop inside the AOI.</li>
<li>Older examples: on his recorded NZDUSD trade the stop was "10 to 15 pips above the wick", about 20 pips from entry. Stops in his examples range from about 20 to 50 pips.</li>
</ul>
<p>He does <b>not</b> hunt for the tightest stop. He wants a level that is very hard for price to reach if the idea is right. Sometimes price hits the stop, then reverses and goes your way; he accepts those losses ("I'm entirely wrong about the direction, and that is totally fine").</p>
<h2>Step 2: the target</h2>
<p>Place the target at the <b>next structure point</b>: the previous swing low (for a sell) or high (for a buy), or the next 4-hour low. He picks a realistic one, not the furthest one ("we're not going to be greedy"). In his newest walkthrough he calls it "the checkpoint": the nearest place the market last reacted from. When the AOI is on the daily he sets the stop on the 4-hour and the target on the daily.</p>
<p><b>Match your target to your entry chart.</b> The same head-and-shoulders entry on the 4-hour chart needed a smaller stop and reached a 1:2 target in about a day and a half. On the daily chart the stop was much larger and 1:2 took about 5 days; on the 1-hour about 10 hours. Never enter on a 1-hour chart and use a daily-chart target (or the reverse): a winner for that timeframe can turn into a loser.</p>
<h2>Step 3: check the reward is worth the risk</h2>
{{D:plan}}
{{CALL:rule|Risk to reward|<ul><li>Every trade needs at least <b>1:2</b> (the reward at least twice the risk). "No ifs, ands or buts."</li><li>Set it up so that <b>1:4</b> is possible, and let it run to there. <b>This guide's rule:</b> target the next structure point if it is at least 1:2 away; by about 1:4 the trade is done. His newest videos place the target the same way.</li><li>Use TradingView's long/short position tool to read the ratio before you enter: the red box is your risk, the green box is your reward.</li><li>At 1:4 the trade is done ("a home run"). Do not close at 1:1 to lock in profit: that was not the plan. The maths: lose 5 of 10 trades at -1 and win 5 at +2, and you are still +5. At 1:4 even a 30% win rate is +5 over 10 trades.</li><li>Some accounts need more: <b>1:3</b> or better on a small account, and 1:2.5 is "even better" on a prop challenge (Part 12).</li></ul>}}
<h2>Real examples from his charts</h2>
<div style="break-inside:avoid">
<table>
<thead><tr><th>Trade</th><th>Stop</th><th>Plan</th><th>What happened</th></tr></thead>
<tbody>
<tr><td>NZDUSD sell</td><td>20.2 pips</td><td>About 1:2</td><td>Ran far past the target; he closed at about 1:5</td></tr>
<tr><td>USDCAD sell</td><td>20 pips</td><td>70 pips (1:3.5)</td><td>Hit the target</td></tr>
<tr><td>GBPCHF sell</td><td>about 35 pips</td><td>Next 4-hour low</td><td>Closed at the target: about 1:2.7 (+102 pips)</td></tr>
<tr><td>GBPNZD buy (against the weekly)</td><td>Below a daily support zone</td><td>1:2 at the weekly zone above 2.3000</td><td>Hit the target (about 5 days)</td></tr>
<tr><td>EURAUD sell (4H H&amp;S, $50 plan)</td><td>Above the wick</td><td>Next structure point</td><td>Closed at 1:2</td></tr>
<tr><td>EURAUD sell (H&amp;S at resistance)</td><td>45 pips</td><td>98.5 pips (R:R 2.18)</td><td>Closed at 1:2; price later went to about 1:6</td></tr>
<tr><td>GBPCAD sell (perfect setup)</td><td>Above the area</td><td>-</td><td><b>Stopped out</b>, then price rose</td></tr>
<tr><td>NZDCAD sell (H&amp;S)</td><td>about 37 to 39 pips</td><td>-</td><td><b>Stopped out (a loss)</b></td></tr>
<tr><td>USDJPY sell (H&amp;S)</td><td>-</td><td>-</td><td><b>Loss</b>: up about 1:1, then price returned through the stop</td></tr>
</tbody></table>
<p class="small">Losses are part of the method. Reading these figures as "he wins most trades" would be a mistake: they are examples picked for teaching.</p>
</div>
<h2>Step 4: the lot size</h2>
<p>Decide how much money you accept to lose on the trade, then let the stop distance set the size. He uses a free <b>lot size calculator</b> before every entry. You type in the account balance, the risk, the stop in pips and the pair.</p>
{{CALL:rule|The formula|<p><b>Lot size = money you risk &divide; (stop in pips &times; value of one pip per lot)</b></p><p>For pairs where the US dollar is the second currency (EURUSD, GBPUSD, AUDUSD, NZDUSD), one pip on one standard lot is worth about <b>$10</b>.</p>}}
{{CALL:ex|Example: his demo|<p>Account $100, risk 10% ($10), stop 20 pips, EURUSD: 10 &divide; (20 &times; 10) = <b>0.05 lot</b>. His calculator gave the same answer.</p><p><b>Our own example:</b> you decide to risk $20, with a 25-pip stop on GBPUSD: 20 &divide; (25 &times; 10) = <b>0.08 lot</b>.</p>}}
<p>For yen pairs the pip value in dollars is different and changes with the exchange rate. His NZDJPY example (0.17 lot for $50 at 30 pips) does not match standard yen pip maths, so always use a calculator that converts correctly and check its answer.</p>
<h2>How much should you risk?</h2>
<p>This is the one number the course never gives for normal trading. Later videos give numbers only for special accounts (Part 12): a fixed dollar amount on a small account, 2% on the first trade of a prop challenge and then the same every trade, or a fixed 0.5 to 1% on a $50 challenge. All of them agree on one thing: <b>keep the risk the same every trade</b>; never raise it after a loss or after a goal. What he says elsewhere:</p>
<ul>
<li>In his "$100 to $1,000,000" challenge he risked <b>100%</b> of the account at the start, then 60 to 50%, 50 to 40%, and 40 to 35% as the account grew. He never went below 35%.</li>
<li>He says that as an account grows he lowers risk by 25 to 50%.</li>
<li>His teaching examples use $10 on a $100 account and $50 on $1,000.</li>
<li>He says the more reasons a trade has, the more he is willing to risk on it, but gives no numbers.</li>
<li>In a later video he mentions a trade where he "lost 1%" and then "made back 6%". That suggests about 1% risk on that trade, but he does not state it as a rule.</li>
</ul>
{{CALL:bad|Do not copy his challenge risk|<p>Risking 100% of an account on a trade means one loss ends it. An earlier attempt at the challenge grew $100 to about $330,000 and then lost it all in a single week, and he says he failed about five times before it worked. His percentages come from a high-risk challenge made for video, not from a rule for normal trading.</p><p><b>Choose your own risk per trade, and make it an amount you can lose many times in a row.</b> Many traders use 1 to 2% of the account as a starting point (this is general practice, not from the course).</p>}}
"""

P10 = """
<h2>Set and forget</h2>
<p>This is the heart of his trade management. Once you enter, you do nothing until the stop or the target is hit.</p>
<ul>
<li><b>Never close before the stop or the target.</b> He allows an exception roughly once in 20 trades.</li>
<li><b>Do not let emotions change your decision.</b> The plan was made when you were calm. After entry, watch the chart to see whether the trade still makes sense, not the profit and loss number.</li>
<li>Expect a small drawdown right away, because of the spread. Do not panic in drawdown.</li>
<li><b>Holding overnight:</b> hold a London entry through the Sydney and Tokyo hours if the market still shows it can reach the target. "Doing nothing is doing something."</li>
<li><b>Over the weekend:</b> hold if the target still looks reachable; close a losing trade that is about halfway to the stop before the weekend. (A prop challenge has its own rule, Part 12.) Pullbacks after entry are normal.</li>
<li><b>Live your life.</b> Set alerts and walk away. Hold times of 2 to 3 days on higher-timeframe setups are normal.</li>
</ul>
<h2>Alerts</h2>
<p>Put a price alert at the level you are waiting for (for example the neckline, or a structure point a 4-hour candle needs to close beyond). When it rings, check the chart and act only if the plan says yes. He sometimes sets two alerts close above and below price to "trap" it.</p>
<h2>When he does close early (optional, for experts)</h2>
<p>These are things he mentions doing in some live trades, not rules of the system. For a sell (mirror for buys):</p>
<ul>
<li>The 30-minute chart breaks above its last structure point.</li>
<li>Price reaches a structure point near the target and a candle <b>closes back above</b> the line: close the trade. If it closes under the line instead, keep holding.</li>
<li>The structure clearly starts to shift against you.</li>
<li>If a <b>daily</b> candle closes under a previous structure level, hold for a long time ("set and forget").</li>
<li>When price runs far past your target, you may close at a point you choose instead of getting greedy.</li>
</ul>
<h2>Accepting the outcome</h2>
<ul>
<li><b>Wick-outs happen.</b> You can be stopped out by a wick, and then price runs to your target without you. He accepts it: "If you want to avoid a wick out, don't trade."</li>
<li><b>Missed profit is not a loss.</b> If the target is hit and price keeps going, you made money and you move on.</li>
<li><b>No catch-up, no lockout.</b> Never try to catch up for lost time ("it puts you in a deeper hole") or fill the wait with a counter-trend trade. An earlier win or loss does not stop a real setup later.</li>
<li>No trade is guaranteed. A good plan wins about 50 to 60% of the time, so 40 to 50% of trades lose. If you are not ready to lose the amount you risked, do not take the trade.</li>
<li><b>No plan B.</b> In a losing streak do not change the strategy or your risk to win losses back. Every trade is independent of the last ten. In a winning streak keep the same sessions and timeframe; do not tighten stops or stretch targets.</li>
</ul>"""

P11 = """
<h2>Once a week: pick your pairs</h2>
<p>He calls this his <b>Sunday swings</b>. It is a weekly analysis session to choose the best markets of the week, done while the market is closed so the read stays neutral, keeping only the clean markets. You also fix the week's direction on Sunday and do not change it with your mood or the news.</p>
<ol class="steps">
<li>List your watchlist (about 10 markets you are focusing on).</li>
<li>Read the structure on weekly, daily and 4-hour for each.</li>
<li>Apply the agreement check (Part 6), which removes about half. Mark the zone and AOIs on the survivors.</li>
<li>Keep the best 2 or 3. Set alerts at the AOIs. Add a note on each chart saying what you are waiting for ("waiting for a shift in structure", "waiting for my entry signal").</li>
</ol>
<h2>Each trading day</h2>
<table class="tl">
<thead><tr><th>New York (his)</th><th>Manila (summer / winter)</th><th>What happens</th></tr></thead>
<tbody>
<tr><td>1:00 AM</td><td>1:00 PM / 2:00 PM</td><td>Pre-London analysis. Check your shortlist and where price is relative to the AOIs. Check the news calendar for red folders.</td></tr>
<tr><td>Which days</td><td>Same days</td><td>Monday, Tuesday or Wednesday only. A confirmation that prints before a session waits for the hour before London.</td></tr>
<tr><td>3:00 AM</td><td>3:00 PM / 4:00 PM</td><td>London opens. Entries are allowed from before this time through the London session.</td></tr>
<tr><td>8:00 AM</td><td>8:00 PM / 9:00 PM</td><td>New York opens. The overlap adds volatility. Last good entries around 9 to 10 AM New York.</td></tr>
<tr><td>10:30 AM</td><td>10:30 PM / 11:30 PM</td><td>No new trades after this time.</td></tr>
<tr><td>Rest of day</td><td>-</td><td>Leave open trades alone. Alerts do the watching.</td></tr>
</tbody></table>
<p class="small" style="margin-top:-2mm">He says only that pre-London analysis starts at 1:00 AM; what you do in that hour is a sensible reading. Manila: add 12 hours in US summer, 13 in winter.</p>
<h2>The full walk-through, start to finish</h2>
<ol class="steps">
<li>Open the pair. Is it the right time of day?</li>
<li>Read weekly, daily and 4-hour structure. Do two in a row agree?</li>
<li>Mark the zone (HH-HL or LH-LL). Find the weekly and daily AOIs inside it and merge overlaps.</li>
<li>Is price at an AOI? If not, set an alert and leave.</li>
<li>Price arrives. Wait for a closed confirmation candle or a break-and-retest at the AOI, in the trend direction.</li>
<li>Check the extras (EMA, round number, previous level, pattern).</li>
<li>Draw the stop (beyond the whole AOI) first, then the target. Is the reward at least twice the risk?</li>
<li>Work out the lot size for the money you accept to lose. Enter with a market order at the next candle's open, stop and target in place, set alerts, then leave the trade alone.</li>
</ol>
"""

P12 = """
<p class="lead"><b>Optional.</b> Three later videos give extra rules for three kinds of account. They are not part of this guide's core plan or checklist. Read a plan only if it matches your account; everything else in this guide still applies.</p>
<h2>A small account ($500 to $2,000)</h2>
<ul>
<li><b>Treat the deposit as already lost.</b> Then you will not force trades or try to win losses back.</li>
<li><b>1 to 2 trades a week at most</b>; one is better. Three trades open at once "literally blow the account".</li>
<li><b>At least 1:3</b> on every trade.</li>
<li><b>Only the "low risk" setup</b>: weekly, daily and 4-hour all agree. Wait for the pullback to a weekly or daily AOI and for the 4-hour to line up again. No trades against the weekly.</li>
<li><b>No Sunday trades</b>, and no new trade from Thursday after about 8 to 9 AM New York. Focus on Monday to Wednesday in London.</li>
<li><b>Risk:</b> below about $25,000 he risks a fixed dollar amount (his "money game") and lowers it as the account grows; above that, 1 to 2% (the "percentage game"). His dollar examples are aggressive account-flipping amounts, not something to copy.</li>
<li><b>Leverage</b> 1:500 at a broker. He stresses that leverage is only access to margin; your risk comes from your lot size.</li>
<li>He says this plan is "not for learning a strategy": it is for someone who already has some experience.</li>
</ul>
<h2>A prop-firm challenge</h2>
<p>A prop firm sells a "challenge": you trade its account under its rules, and if you reach the profit target without breaking a loss limit you get a funded account and a share of the profit. He passed a $5,000 one-step challenge in 2026 in about three weeks. The firm's rules as shown in his video (September 2026) are below; firms change them, so always check the current ones.</p>
<table>
<thead><tr><th>Firm rule</th><th>One-step</th><th>Two-step</th></tr></thead>
<tbody>
<tr><td>Maximum daily loss</td><td>4%</td><td>5%</td></tr>
<tr><td>Maximum total loss</td><td>8%</td><td>10%</td></tr>
<tr><td>Profit target</td><td>10%</td><td>9%, then 5%</td></tr>
<tr><td>Minimum trading days</td><td>5</td><td>3</td></tr>
<tr><td>Leverage, profit split</td><td>1:100, 80%</td><td>1:100, 80%</td></tr>
<tr><td>News</td><td colspan="2">No new trade within 10 minutes before or after news. No time limit; weekend holding allowed.</td></tr>
</tbody></table>
<h3>His four rules for the challenge</h3>
<ol class="steps">
<li><b>Strong Start.</b> Wait for the strongest possible setup for your first trade, however long it takes, and risk <b>2%</b> on it (half of the 4% daily loss limit).</li>
<li><b>One trade a day and one position at a time.</b> If two setups appear together, take the better one.</li>
<li><b>At least 1:2</b> on every trade; 1:2.5 is even better. "You don't need to win more than you lose. You just need to make more than you lose."</li>
<li><b>Trade daily confirmations.</b> The daily (or weekly) candle at the AOI sets up the trade. In his real trades the entry candle was often on the 4-hour.</li>
</ol>
<p>After the first trade he keeps <b>the same risk %</b> on every trade: no dropping to 1% after a loss, no raising it after a win. On a two-step challenge he allows up to two trades a day and 4-hour confirmations.</p>
<div style="break-inside:avoid">
<h3>His five challenge trades</h3>
<table>
<thead><tr><th>Trade</th><th>Setup</th><th>Result</th></tr></thead>
<tbody>
<tr><td>GBPCHF sell</td><td>Against the weekly, off a 4-hour right shoulder, tight stop</td><td><b>Loss</b>; price then reached the target. "Premature."</td></tr>
<tr><td>AUDCHF buy</td><td>Weekly range break and retest, daily morning star, 4-hour inverted H&amp;S, added on the neckline retest, round number 0.56500</td><td>Win; closed Friday at about 1:1 to 1:1.3</td></tr>
<tr><td>USDCHF buy</td><td>Weekly bullish, daily morning star and engulfing at the AOI</td><td>Win; closed late Friday before the target</td></tr>
<tr><td>EURGBP sell</td><td>Weekly bearish, daily double top and engulfing, neckline retest, tight stop</td><td><b>Loss</b> (wick-out); he would take it "10 out of 10 times"</td></tr>
<tr><td>GBPNZD sell</td><td>Daily zone, double top and engulfing, 4-hour shift of structure, 4-hour evening star</td><td>Win</td></tr>
</tbody></table>
<p class="small">Three wins and two losses. Results are his own claims.</p>
</div>
<h2>Starting with $50</h2>
<p>$50 is the <b>learning phase, not the scaling phase</b>: use it to test your strategy, your risk rules, your emotions and your plan. Expect 3 to 4 months, not 24 hours.</p>
<ul>
<li><b>1 to 2 trades a week</b>, held intraday: the target should be reached the same day or the next. Swing holds cost overnight and weekend fees that eat a small balance.</li>
<li><b>Major pairs only</b> (cheapest and calmest), but look at all of them for the setup.</li>
<li><b>One setup only: the 4-hour head and shoulders</b>, entered on the neckline retest after the break (Part 8). No other patterns: "tunnel vision".</li>
<li>His path: buy a small challenge, pass it, take the payout, put it into a personal broker account and grow it there, rather than buying a bigger challenge.</li>
</ul>
{{CALL:rule|His cheat sheet for the $50 plan|<ol style="margin:0 0 0 5mm"><li>Only this one setup. No setup, no trade.</li><li>Enter only after a confirmation (the confirmed break), never on an anticipation.</li><li>Round numbers such as 0.80000 or 1.00000 make the trade slightly better; they do not make or break it.</li><li>A fixed risk on the challenge: 1%, or half a percent.</li><li>At least 1:2.</li></ol>}}
{{CALL:bad|These are his numbers for his accounts|<p>The risk figures in this part come from his videos for those specific accounts. This guide does not set your risk: choose an amount you can lose many times in a row, and keep it the same every trade.</p>}}
"""

P13 = """
<p class="small" style="margin-top:-2mm">Print this page and keep it by your screen. Every box must be ticked, except those marked <i>optional</i>.</p>
<div class="cols2">
<div>
<h3>A. Is it the right time and pair?</h3>
<ul class="check"><li>Pair is on my watchlist and this week's shortlist</li><li>Time is 1:00 to 10:30 AM New York (not Sydney/Tokyo)</li><li>Day is Monday to Wednesday</li></ul>
<h3>B. Structure (weekly, daily, 4H)</h3>
<ul class="check"><li>HH/HL or LH/LL placed on each chart, using candle bodies</li><li>Only closed candles used; no wick breaks</li><li>Weekly and daily agree (4H too is best)</li><li>I am trading <b>with</b> the weekly trend</li></ul>
<h3>C. Zone and AOI</h3>
<ul class="check"><li>Zone drawn (HH-HL or LH-LL)</li><li>AOI is inside the zone</li><li>At least 3 clean touches</li><li>5 to 60 pips tall (tight is better)</li><li>Drawn on weekly or daily (4H only as minor)</li><li>Price is <b>inside or at</b> the AOI now</li><li>Buying at support / selling at resistance</li></ul>
</div>
<div>
<h3>D. Entry signal</h3>
<ul class="check"><li>Confirmation candle has <b>closed</b> at the AOI (engulfing, morning/evening star, rejection)</li><li>OR break and retest completed</li><li>If it printed before a session, I waited for the hour before London</li><li>Signal points the same way as the trend</li><li><i>Optional:</i> head and shoulders / double top neckline at the AOI</li></ul>
<h3>E. Extras (optional, add quality)</h3>
<ul class="check"><li>All three timeframes agree</li><li>Weekly and daily AOI overlap</li><li>50 EMA rejection</li><li>Round number at the AOI</li><li>Previous daily level at the AOI</li></ul>
<h3>F. The plan</h3>
<ul class="check"><li>Stop beyond the whole AOI (set first)</li><li>Target at the next structure point</li><li>Reward is at least 2 &times; risk</li><li>Lot size from my chosen risk amount</li><li>Market order, stop and target entered</li><li>Alerts set. Now I leave it alone.</li></ul>
</div>
</div>
<div class="callout bad" style="margin-top:3mm"><span class="t">If any core box is empty</span><p style="margin:0">Structure, an AOI at the price, and a confirmed entry signal are the three that cannot be skipped. If one is empty: <b>no trade</b>. Set an alert and come back.</p></div>
<h3>Example: his own AUDCHF sell note (six reasons)</h3>
<p class="small">Weekly, daily and 4H all bearish &middot; at a weekly resistance &middot; weekly evening star &middot; under a daily support/resistance level &middot; rejection from the daily EMA &middot; under the 4H EMA and structure.</p>
<h3>Example: five reasons on an AUDJPY buy</h3>
<p class="small">Strong bullish trend &middot; two timeframes in sync &middot; area of interest &middot; break and retest &middot; morning star with a doji.</p>
"""

P14 = """
<p>This guide is faithful to the course, which means it also carries the course's gaps. Know them before you rely on it.</p>
<h2>What is missing</h2>
<table>
<thead><tr><th>Gap</th><th>What the course says</th></tr></thead>
<tbody>
<tr><td><b>The full entry signal</b></td><td>In the course he says there is one that he explains only on his livestream. His follow-up video teaches an open entry confirmation (Part 8), but he never says whether it is the same thing. Two later videos say they show only how to read the market, "not my exact strategy".</td></tr>
<tr><td><b>Normal risk per trade</b></td><td>Never stated for a normal account. Only the challenge ladder, small teaching examples, a hint of about 1%, and the special-account numbers in Part 12.</td></tr>
<tr><td><b>Exact definitions</b></td><td>No numbers for a "significant" swing, a "clean elbow", a "touch", a "slowdown", or how big a doji's body can be.</td></tr>
<tr><td><b>EMA</b></td><td>Only the 50 EMA is named, and only once. No rule ties it to a timeframe.</td></tr>
<tr><td><b>News</b></td><td>No filter for a normal account, only "look at the red folders". Prop firms block entries 10 minutes either side of news.</td></tr>
<tr><td><b>Loss limits</b></td><td>No personal daily or weekly loss limit or withdrawal rules. Prop firms set their own (Part 12).</td></tr>
<tr><td><b>Head and shoulders plan</b></td><td>In the $50 plan: which wick the stop goes above, whether a candle is needed at the retest, and what to do if the target is not reached by the next day.</td></tr>
<tr><td><b>Evidence</b></td><td>No back-test. He dislikes back-testing. Win rates he mentions are loose and inconsistent.</td></tr>
</tbody></table>
<h2>Small contradictions between the videos</h2>
<p>When two videos disagree, this guide follows the <b>newer upload</b>.</p>
<table>
<thead><tr><th>Topic</th><th>What he said</th><th>What this guide uses</th></tr></thead>
<tbody>
<tr><td>Timeframes in sync</td><td>"Two in a row", "all three", "weekly and daily" at different times; later "mid risk, probably wait" when the 4H disagrees</td><td>Weekly and daily must agree; all three is best; never against the weekly</td></tr>
<tr><td>Which timeframes get AOIs</td><td>"4hr NO AOI" in the course and "only weekly and daily" in early 2026; weekly, daily and 4H in his two newest videos</td><td>Weekly and daily first; 4H as a minor extra (newest rule)</td></tr>
<tr><td>AOIs per chart</td><td>"Four or five" once; "one, maybe two, max three" later; "typically two to three" newest</td><td>Up to three</td></tr>
<tr><td>Where the stop goes</td><td>10 to 15 pips beyond the wick (course); beyond the whole AOI plus 5 to 10 pips (newer); kept tight so 1:2 still works (newest)</td><td>Beyond the whole AOI; skip the trade if that leaves less than 1:2</td></tr>
<tr><td>Weekend</td><td>Hold if the target still looks reachable; later, hold only a trade already at its target</td><td>Hold if the target still looks reachable (the challenge rule is in Part 12)</td></tr>
<tr><td>One pair or many</td><td>One pair (EURUSD) for beginners; later, all the majors for one pattern</td><td>The full method on your own pair list; both simple plans are optional</td></tr>
<tr><td>Window end</td><td>"10:00" and "10:30"</td><td>10:30 AM New York</td></tr>
<tr><td>Required reasons</td><td>"No minimum" vs "if the plan isn't checked off, don't trade"</td><td>The three core items are mandatory; extras are not</td></tr>
<tr><td>Closing early</td><td>"Never" vs a few early exits in live trades</td><td>Hold to the stop or target by default</td></tr>
<tr><td>Teaching samples</td><td>Stop and target numbers on screen sometimes differ from what he says</td><td>Work out your own from the chart</td></tr>
</tbody></table>
<h2>Reliability of this guide</h2>
<ul>
<li>It was written from the videos' auto-generated captions plus screenshots of the charts. Machine captions contain mistakes, and some numbers read from the screen are approximate.</li>
<li>The video's chapter titles do not always match what is taught under them (for example, "Confluence Trading" is mainly market-structure basics), so this guide follows the content, not the titles.</li>
<li>It describes one trader's method from one course and twelve follow-up videos. It does not prove the method is profitable. Any profit figures in the videos are the creator's own claims.</li>
</ul>
{{CALL:bad|The risk of losing money|<p>Forex trading with leverage can lose money quickly. Practise on a demo account first. Never risk money you cannot afford to lose. This guide is for education and is not personal financial advice.</p>}}
"""

GLOSSARY = [
    ("AOI (Area of Interest)", "A support/resistance zone where price has reacted before. At least 3 touches, 5 to 60 pips tall, inside the HH-HL or LH-LL zone, drawn on weekly and daily (4-hour as a minor extra)."),
    ("Alert", "A TradingView price alarm at a level you are waiting for."),
    ("Confirmation (vs anticipation)", "Something that has already happened, such as a closed rejection or engulfing candle. Entering on a guess before the candle closes is anticipation."),
    ("Rejection candle", "A doji or small-bodied candle with a long wick, showing price was pushed back from a level."),
    ("Base / quote currency", "The first and second currency of a pair. Price up means the base is stronger; price down means the quote is stronger."),
    ("BOS / CHoCH / shift of structure", "Three names for the same thing: the break of the HL (uptrend) or LH (downtrend), which flips the trend."),
    ("Body", "The thick part of a candle, from open to close."),
    ("Break and retest", "A body closes beyond a zone, price returns to test it, gets rejected, and you enter."),
    ("Breakout", "Entering as soon as a body closes beyond a zone, without waiting for the retest."),
    ("Bullish / bearish", "Bullish: higher highs and higher lows. Bearish: lower lows and lower highs."),
    ("Confluence", "A reason to take a trade. More reasons make a better trade."),
    ("Doji", "A candle with almost no body, showing indecision."),
    ("Elbow", "A turning point on a chart. Structure points are elbows."),
    ("EMA (50)", "The 50-period exponential moving average. Above it acts as support, below it as resistance. An optional extra."),
    ("Engulfing", "The last candle's body closes beyond the previous candle's body. The more candles it covers, the stronger."),
    ("Low, mid and high risk", "His labels for timeframe agreement: all three agree (low), weekly and daily agree but the 4-hour does not (mid), trading against the weekly (high)."),
    ("Lower timeframes (LT)", "The 2-hour, 1-hour, 30-minute and 15-minute charts read together. An extra vote on direction; the weekly and daily outweigh them."),
    ("Prop-firm challenge", "A paid test on a firm's account with a profit target and loss limits. Pass it and you trade a funded account for a share of the profit."),
    ("Strong Start", "His first rule for a prop challenge: wait for the strongest setup for the first trade and risk 2% on it."),
    ("Entry signal", "The confirmation at the AOI that tells you to enter."),
    ("Evening star / morning star", "A doji followed by an engulfing candle covering the last two candles. Evening for sells, morning for buys."),
    ("Head and shoulders", "A reversal pattern. Valid only after the horizontal neckline breaks; you enter on the retest."),
    ("HH, HL, LH, LL", "Higher high, higher low, lower high, lower low."),
    ("Inside (the structure)", "Price sitting between the current HH and HL (bullish) or LH and LL (bearish)."),
    ("Liquidity", "Buyers and sellers, with their take profits and stops, sitting at a price. Strongest where price has rejected many times, which is an AOI."),
    ("Liquidity sweep", "A wick that pokes through a zone and reverses (also called a grab or fake out). He says it cannot be predicted, so you do not wait for it."),
    ("Lot", "The size of a position. A standard lot is 100,000 units."),
    ("Market execution", "Entering immediately at the current price."),
    ("Neckline", "The horizontal line at the previous structure point in a head and shoulders. It sits at an AOI."),
    ("No gaps candles", "A TradingView indicator that fills gaps so each candle opens at the previous close."),
    ("Pip", "A small unit of price movement (0.0001 for most pairs, 0.01 for yen pairs)."),
    ("Retest", "Price returning to a broken level to test it."),
    ("Risk:reward (R:R)", "Reward divided by risk. At least 1:2 is required."),
    ("Set and forget", "After entering, do nothing until the stop or target is hit."),
    ("Shiny object syndrome", "Jumping between strategies, pairs and signals. He says to pick one simple approach and stick to it until it is consistently profitable."),
    ("Snake trick","Start at a new extreme and walk backwards to the first clean turn to find its partner point."),
    ("Spread", "The broker's small fee built into the price."),
    ("Stop loss", "The price where a losing trade is closed automatically."),
    ("Strong / weak candle", "A candle is strong because of where it forms (at a key zone, followed by a push), not because of its size. The same candle mid-chart is weak."),
    ("Take profit (target)", "The price where a winning trade is closed automatically."),
    ("Top-down analysis", "Reading weekly, then daily, then 4-hour to decide the trend."),
    ("Touch", "One clear reaction (rejection) from an AOI."),
    ("Trap price", "Drawing the HH/HL or LH/LL lines so price is boxed in a zone."),
    ("Trend timeframes", "Weekly, daily and 4-hour: used for trend and AOIs."),
    ("Wick", "The thin line on a candle showing where price has been. Counted as rejection but not used for structure breaks."),
    ("Wick fill", "His name for an inverted hammer (the next candle is expected to fill the upper wick). Also a daily candle with a long lower wick that the 4-hour shows is really setting up a higher low."),
    ("Zone", "The area between HH and HL, or between LH and LL, where you look for trades."),
]

PB = """
<p>This appendix is for anyone turning the strategy into software (for example a tool that scans a list of pairs and writes a report).</p>
<h2>What a computer can do directly from price data</h2>
<table>
<thead><tr><th>Task</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>Candle bodies, body-close breaks</td><td>Use closed candles only. Ignore the live candle.</td></tr>
<tr><td>Structure state machine per timeframe</td><td>Bullish/bearish, HH/HL/LH/LL levels, "inside the zone" test (Part 5).</td></tr>
<tr><td>Timeframe agreement and the zone</td><td>Two-in-a-row check, grade A when all three agree.</td></tr>
<tr><td>AOI checks</td><td>Zone height in pips, touch count, weekly and daily overlap, price at or above/below the AOI.</td></tr>
<tr><td>Candle signals</td><td>Engulfing over two bodies, doji, hammer, inverted hammer, morning and evening star.</td></tr>
<tr><td>Break and retest, H&amp;S, double top</td><td>Detectable once the swing rule is chosen.</td></tr>
<tr><td>EMA(50), round numbers, previous daily levels</td><td>Simple calculations.</td></tr>
<tr><td>Session flags, pip value, lot size, R:R</td><td>Use New York time; compute pip value in the app instead of copying his calculator.</td></tr>
</tbody></table>
<h2>Decisions you will have to make (the course leaves them to the eye)</h2>
<ol>
<li>What is a "significant" swing (the clean-elbow test)? A common starting point is a fractal or ZigZag rule with a minimum size per timeframe, made adjustable.</li>
<li>What counts as one touch (distance tolerance, candles per touch)?</li>
<li>Where exactly to place the AOI box when several touches compete.</li>
<li>When a retracement has "stopped" (to confirm an HH or LL).</li>
<li>How far beyond the AOI to put the stop (5 to 10 pips in his newest walkthrough; 10 to 15 pips beyond a wick on one older trade).</li>
<li>Where daily and weekly candles start and end. Body-close tests depend on it; his market close is 5:00 PM New York.</li>
</ol>
<h2>Suggested report, per pair</h2>
<p>Time window pass or fail; weekly, daily and 4-hour bias with the HH/HL/LH/LL prices; agreement grade (none, two, three); the zone and the weekly/daily AOIs (touches, pips) with the distance from price to the nearest one; EMA side on each timeframe; latest candle signal at the AOI; pattern state (potential, neckline broken, retested); suggested stop, target and R:R; lot size for the user's own risk setting; the Part 13 checklist with pass/fail and a "no trade" reason when a gate fails.</p>
<p class="small">The app's first version builds only the core plan (Part 13); optional variants are left out. Data tip: TradingView has no public data feed; use a candle data service.</p>
"""

PC = """
<h2>Where each topic is taught in the video</h2>
<p>The video is "The Trading Industry Will Hate Me for This FREE 10+ Hour Course" by fxalexg (Swing Trading Lab), 10 hours 36 minutes: <b>https://www.youtube.com/watch?v=grw58BIzotU</b>. Times are h:mm:ss.</p>
<table>
<thead><tr><th style="width:34mm">Video time</th><th>What is taught</th></tr></thead>
<tbody>
<tr><td>0:00 to 1:29</td><td>Markets, trading styles, currency pairs, chart types, timeframes, candles and wicks, sessions, platforms, news calendar</td></tr>
<tr><td>1:29 to 3:12</td><td>Broker and MetaTrader demo, TradingView setup, alerts, watchlist, drawing tools, lot size, order types, first definition of structure</td></tr>
<tr><td>3:12 to 5:35</td><td>Market structure (HH/HL/LL/LH, body closes, snake trick), top-down analysis, the zone, AOI basics</td></tr>
<tr><td>5:35 to 7:14</td><td>AOI rules in full, break of structure, break and retest, candlestick patterns, head and shoulders</td></tr>
<tr><td>7:14 to 8:25</td><td>Head and shoulders wrap-up, the 50 EMA, confluence trading, a recorded NZDUSD trade, trade management</td></tr>
<tr><td>8:25 to 10:36</td><td>The $100 to $1M challenge: risk ladder, risk:reward, weeks 1 to 14, short recap</td></tr>
</tbody></table>
<h2>Follow-up videos (all by fxalexg)</h2>
<ul>
<li>"The ONLY confirmation YOU need..." (22 min): <b>youtube.com/watch?v=BcWxqfcjk9A</b>. Entry confirmation, weekday and session timing (Parts 4, 8).</li>
<li>"How to Master Liquidity in Trading" (19 min): <b>youtube.com/watch?v=Rua24ytuHuY</b>. AOI as a liquidity zone; ignoring sweeps (Parts 7, 8).</li>
<li>"Price Action Trading Was Hard, Until I Discovered This" (25 min): <b>youtube.com/watch?v=WEyJ-zKAEoA</b>. Strong vs weak candles, wick fill, break-and-retest entries (Part 8).</li>
<li>"How Trading Dumb Made Me a Millionaire Trader" (28 min): <b>youtube.com/watch?v=KPVVOa6c6dY</b>. The simple one-pair, one-timeframe version (Parts 1, 4, 9, 10).</li>
<li>"This trading strategy is boring, but it makes me $150,000/week" (21 min): <b>youtube.com/watch?v=1fGzVHI7rN0</b>. Streak discipline, four recent trades (Parts 6, 9, 10).</li>
<li>"If I Wanted to Make $1,000/Day Trading, I'd Do This" (18 min): <b>youtube.com/watch?v=M8wDlKjaQRk</b>. Weekly goals, pullbacks, weekly bias, accepting losses (Parts 1, 9 to 11).</li>
<li>"How to Grow a Small Trading Account From Scratch in 2026" (53 min, Feb 2026): <b>youtube.com/watch?v=LwMsai2ppKc</b>. Small-account plan, risk labels, no lockout (Parts 6, 10, 12).</li>
<li>"This is Boring, But it'll make your first $100,000 Trading" (1 h 23 min, Jun 2026): <b>youtube.com/watch?v=MhWSZp4yS2c</b>. The three steps, AOI rules, stop beyond the whole AOI (Parts 1, 5, 7 to 9).</li>
<li>"The Prop Firm Industry is Going to Hate Me For This Free Course" (1 h 18 min, Sep 2026): <b>youtube.com/watch?v=7QNdSEwQUJE</b>. Prop challenge rules and five trades (Parts 4, 8 to 10, 12).</li>
<li>"The Only Trading Strategy You Need To Be Profitable | Swing Trading" (27 min, May 2026): <b>youtube.com/watch?v=1dL3xmxA2e0</b>. Swing trading, the weekly retracement, stops at a level (Parts 2, 6, 9 to 11).</li>
<li>"Best Top Down Analysis Strategy for 2026" (33 min, Feb 2026): <b>youtube.com/watch?v=pD1vAUMbSjw</b>. Four sectors, the HL behind the HH, the 4-hour pullback (Parts 2, 5 to 8).</li>
<li>"How to Start Trading with Just $50" (37 min, Jul 2026): <b>youtube.com/watch?v=hb7ot1_szWI</b>. The 4-hour head and shoulders plan (Parts 1, 8, 12).</li>
</ul>
<p class="small">Income and "millionaire" claims in these titles are marketing and were not verified.</p><h2>Credits and notes</h2>
<ul>
<li>The strategy ideas and examples belong to fxalexg / Swing Trading Lab. This is an independent study summary that quotes only short phrases; watch the videos to learn from the source. Diagrams are original drawings, not real prices or screenshots.</li></ul>
"""


def glossary_html():
    rows = "".join(f"<tr><td style='width:46mm'><b>{t}</b></td><td>{d}</td></tr>"
                   for t, d in sorted(GLOSSARY, key=lambda x: x[0].lower()))
    return f"<table><tbody>{rows}</tbody></table>"


def expand(html):
    import re
    html = re.sub(r"\{\{D:(\w+)\}\}", lambda m: f'<div class="fig">{D.ALL[m.group(1)]()}</div>', html)

    def call(m):
        kind, title, body = m.group(1), m.group(2), m.group(3)
        return callout(kind, title, body)
    html = re.sub(r"\{\{CALL:(\w+)\|([^|]*)\|(.*?)\}\}(?=\s*(?:<|\{\{|$))", call, html, flags=re.S)
    return html


def build(pages):
    bodies = {"p1": P1, "p2": P2, "p3": P3, "p4": P4, "p5": P5, "p6": P6, "p7": P7, "p8": P8, "p9": P9,
              "p10": P10, "p11": P11, "p12": P12, "p13": P13, "p14": P14, "pa": glossary_html(), "pb": PB, "pc": PC}
    out = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>The Confluence Trading Guide</title>"
           f"<style>{CSS}</style></head><body>{D.DEFS}", COVER, FRONT.replace("{{TOC}}", toc(pages))]
    for pid, label, title in PARTS:
        out.append(part(pid, label, title, expand(bodies[pid])))
    out.append("</body></html>")
    return "".join(out)


if __name__ == "__main__":
    pages = {}
    if len(sys.argv) > 2 and Path(sys.argv[2]).exists():
        pages = json.loads(Path(sys.argv[2]).read_text())
    Path(sys.argv[1]).write_text(build(pages), encoding="utf-8")
    print("wrote", sys.argv[1])
