/* TradingGuide terminal: watchlist, chart with boxes, verdict, plan, alerts. No framework. */
(() => {
'use strict';
const TFS = ['W', 'D', '4H', '2H', '1H', '30m', '15m'];
const VORDER = { SIGNAL: 0, WAIT_FOR_SESSION: 1, WATCH: 2, NO_TRADE: 3, ERROR: 4 };
const VLABEL = { SIGNAL: 'SIGNAL', WAIT_FOR_SESSION: 'WAIT', WATCH: 'WATCH', NO_TRADE: 'NO TRADE', ERROR: 'ERROR' };
const REASON = {
  counter_trend: 'Daily is against the weekly (counter-trend)', no_alignment: 'Weekly or daily not readable',
  no_aoi: 'No area of interest on the right side', price_not_at_aoi: 'Price not at the area yet',
  no_confirmation: 'No closed confirmation yet', rr_below_2: 'Next structure point is under 1:2',
  against_weekly_level: 'A weekly level is in the way', weekday: 'Not a Monday to Wednesday entry day',
  time: 'Outside the 1:00 to 10:30 New York window',
};
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const store = {
  get(k, d) { try { return localStorage.getItem('tg.' + k) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem('tg.' + k, v); } catch { /* private mode */ } },
};
const S = {
  pair: store.get('pair', null), tf: store.get('tf', 'D'), tab: store.get('tab', 'verdict'),
  summary: [], analysis: null, bars: [], ema: [], prices: {}, state: null, filter: 'all', q: '',
  firedSeen: 0, clickPrice: null, sort: ['verdict', 1], lines: [], scanWas: false,
  layers: { swings: store.get('l.swings', '0') === '1', boxes: store.get('l.boxes', '1') === '1', patterns: store.get('l.patterns', '1') === '1' },
};
let chart, candle, emaLine, ro;

const isJpy = p => (p || '').endsWith('JPY');
const dig = p => (isJpy(p) ? 3 : 5);
const fmt = (p, v) => (v == null || Number.isNaN(v) ? '-' : Number(v).toFixed(dig(p)));
const pips = (p, v) => (v == null ? '-' : Number(v).toFixed(1));
async function api(path, opt) {
  const r = await fetch('/api/' + path, opt);
  let body = null;
  try { body = await r.json(); } catch { /* empty */ }
  if (!r.ok && !(body && body.error)) throw new Error(r.status + '');
  return body;
}
const post = (path, body) => api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });

/* ---------- time ---------- */
function tzOffsetMin(tz, ms) {
  const f = new Intl.DateTimeFormat('en-US', { timeZone: tz, hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const p = Object.fromEntries(f.formatToParts(new Date(ms)).map(x => [x.type, x.value]));
  return (Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute, +p.second) - Math.floor(ms / 1000) * 1000) / 60000;
}
function wallToInstant(wallMs, tz) {
  let g = wallMs - tzOffsetMin(tz, wallMs) * 60000;
  g = wallMs - tzOffsetMin(tz, g) * 60000;
  return g;
}
const hm = (ms, tz) => new Intl.DateTimeFormat('en-GB', { timeZone: tz, weekday: 'short', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).format(ms);
function brokerToTz(t, tz) {  // broker seconds are New York wall clock + offset
  const off = (S.state && S.state.offset) || 7;
  return hm(wallToInstant((t - off * 3600) * 1000, 'America/New_York'), tz);
}
function tickClocks() {
  const now = Date.now();
  $('#clkNy').textContent = hm(now, 'America/New_York');
  $('#clkMnl').textContent = hm(now, (S.state && S.state.display_tz) || 'Asia/Manila');
}

/* ---------- chart ---------- */
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
function candleColors() {
  const classic = S.state && S.state.settings.ui.candles === 'classic';
  return classic ? { up: '#26a69a', down: '#ef5350' } : { up: css('--up'), down: css('--down') };
}
function applyTheme() {
  if (!chart) return;
  const c = candleColors();
  chart.applyOptions({
    layout: { background: { type: 'solid', color: css('--bg') }, textColor: css('--muted'), fontFamily: css('--mono'), fontSize: 11 },
    grid: { vertLines: { color: css('--line') }, horzLines: { color: css('--line') } },
    rightPriceScale: { borderColor: css('--line') }, timeScale: { borderColor: css('--line') },
  });
  candle.applyOptions({ upColor: c.up, downColor: c.down, wickUpColor: c.up, wickDownColor: c.down, borderVisible: false });
  emaLine.applyOptions({ color: css('--watch') });
  draw();
}
function initChart() {
  const el = $('#chart'), wrap = $('#chartwrap');
  chart = LightweightCharts.createChart(el, {
    width: wrap.clientWidth || 800, height: wrap.clientHeight || 500,
    timeScale: { timeVisible: true, secondsVisible: false, rightOffset: 10, barSpacing: 8 },
    crosshair: { mode: 0 },
    localization: { priceFormatter: p => Number(p).toFixed(dig(S.pair)) },
  });
  candle = chart.addCandlestickSeries({ priceLineVisible: false });
  emaLine = chart.addLineSeries({ lineWidth: 2, priceLineVisible: false, lastValueVisible: false, crosshairMarkerVisible: false });
  chart.subscribeCrosshairMove(onCross);
  chart.subscribeClick(onClick);
  chart.timeScale().subscribeVisibleLogicalRangeChange(() => requestAnimationFrame(draw));
  ro = new ResizeObserver(() => {
    const w = $('#chartwrap').clientWidth, h = $('#chartwrap').clientHeight;
    if (w > 0 && h > 0) chart.resize(w, h);
    requestAnimationFrame(draw);
  });
  ro.observe($('#chartwrap'));
  applyTheme();
  (function loop() { draw(true); requestAnimationFrame(loop); })();
}
function snap(t) {
  const b = S.bars;
  if (!b.length) return null;
  let lo = 0, hi = b.length - 1;
  if (t <= b[0][0]) return b[0][0];
  if (t >= b[hi][0]) return b[hi][0];
  while (lo < hi - 1) { const m = (lo + hi) >> 1; if (b[m][0] <= t) lo = m; else hi = m; }
  return b[lo][0];
}
let lastSig = '';
function draw(onlyIfMoved) {
  const cv = $('#overlay'), wrap = $('#chartwrap');
  if (!chart || !candle) return;
  const w = wrap.clientWidth, h = wrap.clientHeight, dpr = window.devicePixelRatio || 1;
  const ts = chart.timeScale();
  const probe = S.bars.length ? S.bars[S.bars.length - 1] : null;
  const sig = [w, h, dpr, probe ? candle.priceToCoordinate(probe[4]) : 0, probe ? ts.timeToCoordinate(probe[0]) : 0,
    ts.getVisibleLogicalRange() ? JSON.stringify(ts.getVisibleLogicalRange()) : '', S.analysis ? S.analysis.asof_ny : '', S.tf].join('|');
  if (onlyIfMoved === true && sig === lastSig) return;
  lastSig = sig;
  if (cv.width !== w * dpr || cv.height !== h * dpr) { cv.width = w * dpr; cv.height = h * dpr; cv.style.width = w + 'px'; cv.style.height = h + 'px'; }
  const ctx = cv.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, w, h);
  const a = S.analysis;
  if (!a || !S.bars.length) return;
  const plotW = w - chart.priceScale('right').width();
  const X = t => { const x = ts.timeToCoordinate(snap(t)); return x == null ? null : x; };
  const Y = p => candle.priceToCoordinate(p);
  const col = tf => ({ W: css('--w'), 'W+D': css('--w'), D: css('--d'), '4H': css('--h4') }[tf] || css('--muted'));
  ctx.font = '11px ' + css('--mono');
  const badges = [], labels = [];

  // reference boxes (the owner's own)
  for (const r of ((S.state && S.state.reference) || []).filter(r => r.pair === S.pair)) {
    const y1 = Y(r.high), y2 = Y(r.low);
    if (y1 == null || y2 == null) continue;
    ctx.save();
    ctx.setLineDash([5, 4]); ctx.strokeStyle = css('--yours'); ctx.lineWidth = 1;
    ctx.strokeRect(0.5, Math.min(y1, y2), plotW - 1, Math.abs(y2 - y1));
    ctx.restore();
    labels.push({ y: Math.min(y1, y2) + 11, text: 'YOUR box ' + (r.tf || ''), color: css('--yours') });
  }
  // swing path: the confirmed swing points of this timeframe joined, as the structure module sees them
  if (S.layers.swings) {
    const sw = (a.tf[S.tf] && a.tf[S.tf].swings) || [];
    ctx.save();
    ctx.strokeStyle = css('--muted'); ctx.lineWidth = 1; ctx.setLineDash([2, 3]); ctx.beginPath();
    let first = true;
    for (const s of sw) { const x = X(s.t), y = Y(s.price); if (x == null || y == null) continue; if (first) ctx.moveTo(x, y); else ctx.lineTo(x, y); first = false; }
    ctx.stroke(); ctx.setLineDash([]);
    for (const s of sw) {
      const x = X(s.t), y = Y(s.price); if (x == null || y == null) continue;
      ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI * 2); ctx.fillStyle = s.kind === 'H' ? css('--down') : css('--up'); ctx.fill();
    }
    ctx.restore();
  }
  // patterns (head and shoulders, double top or bottom, break and retest) on the pattern timeframe
  if (S.layers.patterns && S.tf === a.pattern_tf) {
    const pc = css('--accent-text');
    for (const pt of a.patterns || []) {
      const nm = pt.type.replaceAll('_', ' ');
      if (pt.point_t) {
        ctx.save(); ctx.strokeStyle = pc; ctx.lineWidth = 1.5; ctx.beginPath();
        pt.point_t.forEach((t, i) => { const x = X(t), y = Y(pt.point_p[i]); if (x == null || y == null) return; if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); });
        ctx.stroke(); ctx.restore();
      }
      if (pt.neckline != null) {
        const y = Y(pt.neckline), x0 = pt.point_t ? (X(pt.point_t[0]) ?? 0) : 0;
        if (y != null) {
          ctx.save(); ctx.strokeStyle = pc; ctx.setLineDash([6, 4]); ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(plotW, y); ctx.stroke(); ctx.restore();
          labels.push({ y: y - 3, text: `${nm} neckline ${fmt(a.pair, pt.neckline)} (${pt.state.replaceAll('_', ' ')})`, color: pc });
        }
      }
      const bx = (a.aois || []).find(b => b.id === pt.box);
      if (pt.type === 'break_and_retest' && bx) {
        for (const [key, word, edge] of [['break_t', 'break', pt.side === 'buy' ? bx.high : bx.low], ['retest_t', 'retest', pt.side === 'buy' ? bx.high : bx.low]]) {
          const x = pt[key] ? X(pt[key]) : null, y = Y(edge);
          if (x == null || y == null) continue;
          ctx.save(); ctx.fillStyle = pc; ctx.font = '600 10px ' + css('--mono'); ctx.textAlign = 'center'; ctx.fillText(word, x, pt.side === 'buy' ? y - 6 : y + 14); ctx.restore();
        }
        labels.push({ y: Y(bx.high) - 3, text: `${bx.id} break and retest: ${pt.state.replaceAll('_', ' ')}`, color: pc });
      }
    }
  }
  // areas of interest
  const lowTf = ['4H', '2H', '1H', '30m', '15m'].includes(S.tf);
  for (const b of (S.layers.boxes ? a.aois : [])) {
    // a broken box is removed from the candidates (video 9); one broken in the last 5 candles of its own
    // timeframe stays visible, faint and dashed, for the retest. Older ones are only in the Levels tab.
    if (b.broken && !(b.broken_age != null && b.broken_age <= 5)) continue;
    if (b.tf === '4H' && !lowTf) continue;  // minor 4H boxes only on 4H and lower charts
    const y1 = Y(b.high), y2 = Y(b.low);
    if (y1 == null || y2 == null) continue;
    let x1 = b.touch_t && b.touch_t.length ? X(b.touch_t[0]) : 0;
    x1 = Math.max(0, x1 == null ? 0 : x1);
    const top = Math.min(y1, y2), hh = Math.max(Math.abs(y2 - y1), 2);
    const c = col(b.tf);
    ctx.save();
    ctx.globalAlpha = b.broken ? 0.08 : 0.16; ctx.fillStyle = c; ctx.fillRect(x1, top, plotW - x1, hh);
    ctx.globalAlpha = 0.9; ctx.strokeStyle = c; ctx.lineWidth = b.tf === 'W+D' ? 2.5 : 1;
    if (b.broken) ctx.setLineDash([4, 3]);
    ctx.strokeRect(x1 + 0.5, top + 0.5, plotW - x1 - 1, hh);
    ctx.restore();
    labels.push({ y: top + 11, text: `${b.id} ${b.tf} ${b.touches}x ${b.pips.toFixed(0)}p ${b.broken ? 'broken, retest? ' : ''}${b.role}`, color: c });
    if (a.candidate === b.id) badges.push([5, x1 + 4, top - 2]);
  }
  // box labels sit at the right edge, pushed apart so none overlap
  labels.sort((l, m) => l.y - m.y);
  let prev = -1e9;
  for (const l of labels) {
    l.y = Math.max(l.y, prev + 13); prev = l.y;
    ctx.fillStyle = css('--bg'); ctx.globalAlpha = 0.75;
    const wdt = ctx.measureText(l.text).width + 8;
    ctx.fillRect(plotW - wdt - 4, l.y - 10, wdt, 13);
    ctx.globalAlpha = 1; ctx.fillStyle = l.color;
    ctx.fillText(l.text, plotW - wdt, l.y);
  }
  // reward and risk of the plan
  const p = a.plan, sg = a.signal;
  if (p && sg && p.target != null) {
    const x1 = X(sg.t) ?? 0, ye = Y(p.entry), ys = Y(p.stop), yt = Y(p.target);
    if (ye != null && ys != null && yt != null) {
      ctx.save();
      ctx.globalAlpha = 0.14; ctx.fillStyle = css('--error'); ctx.fillRect(x1, Math.min(ye, ys), plotW - x1, Math.abs(ys - ye));
      ctx.fillStyle = css('--signal'); ctx.fillRect(x1, Math.min(ye, yt), plotW - x1, Math.abs(yt - ye));
      ctx.globalAlpha = 1; ctx.fillStyle = css('--text');
      ctx.fillText(`1:${p.rr.toFixed(1)}`, x1 + 6, yt + (yt < ye ? 12 : -4));
      ctx.restore();
      badges.push([10, plotW - 16, yt]);
    }
  }
  if (sg) { const x = X(sg.t), y = Y(S.bars[S.bars.length - 1][2]); if (x != null && y != null) badges.push([7, x, y - 14]); }
  const lastY = Y(S.bars[S.bars.length - 1][4]);
  if (a.candidate && lastY != null) badges.push([6, plotW - 40, lastY]);
  // numbered markers match the checklist
  for (const [n, x, y] of badges) {
    ctx.save();
    ctx.beginPath(); ctx.arc(x, y, 8, 0, Math.PI * 2); ctx.fillStyle = css('--accent'); ctx.fill();
    ctx.fillStyle = '#fff'; ctx.font = '600 10px ' + css('--mono'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(String(n), x, y + 0.5);
    ctx.restore();
  }
}
function clearLines() { for (const l of S.lines) { try { candle.removePriceLine(l); } catch { /* gone */ } } S.lines = []; }
function addLine(price, color, title, style = 2, width = 1) {
  if (price == null) return;
  S.lines.push(candle.createPriceLine({ price, color, lineWidth: width, lineStyle: style, axisLabelVisible: true, title }));
}
function paintStructure() {
  clearLines();
  const a = S.analysis;
  if (!a) return;
  const tf = a.tf[S.tf];
  if (tf && tf.state) {
    for (const [name, l] of Object.entries(tf.levels)) {
      addLine(l.price, name.startsWith('H') ? css('--signal') : css('--error'), name, 0, 1);
    }
  }
  if (a.plan && S.tab !== 'levels') {
    addLine(a.plan.entry, css('--accent-text'), 'Entry', 2);
    addLine(a.plan.stop, css('--error'), 'Stop', 0, 2);
    if (a.plan.target != null) addLine(a.plan.target, css('--signal'), 'Target', 0, 2);
  }
  const mk = [];
  if (tf && tf.flips) {
    for (const f of tf.flips) {
      const t = snap(f.t);
      if (t == null) continue;
      mk.push(f.state === 'bull'
        ? { time: t, position: 'belowBar', color: css('--up'), shape: 'arrowUp', text: '' }
        : { time: t, position: 'aboveBar', color: css('--down'), shape: 'arrowDown', text: '' });
    }
  }
  if (a.signal && S.tf === a.signal.tf) {
    mk.push({ time: snap(a.signal.t), position: a.signal.side === 'buy' ? 'belowBar' : 'aboveBar', color: css('--signal'), shape: 'circle', text: a.signal.type });
  }
  mk.sort((x, y) => x.time - y.time);
  candle.setMarkers(mk);
}
function onCross(param) {
  const lg = $('#legend');
  const a = S.analysis;
  const head = `<b>${esc(S.pair || '')}</b> <span class="dim">${esc(S.tf)}</span>`;
  const bar = param && param.time ? param.seriesData.get(candle) : null;
  const last = S.bars.length ? S.bars[S.bars.length - 1] : null;
  const o = bar ? bar : last ? { open: last[1], high: last[2], low: last[3], close: last[4] } : null;
  let s = head;
  if (o) {
    s += ` <span class="dim">O</span> ${fmt(S.pair, o.open)} <span class="dim">H</span> ${fmt(S.pair, o.high)} <span class="dim">L</span> ${fmt(S.pair, o.low)} <span class="dim">C</span> ${fmt(S.pair, o.close)}`;
  }
  if (param && param.time) s += ` <span class="dim">NY</span> ${brokerToTz(param.time, 'America/New_York')} <span class="dim">Manila</span> ${brokerToTz(param.time, (S.state && S.state.display_tz) || 'Asia/Manila')}`;
  if (a) {
    const st = a.tf[S.tf] && a.tf[S.tf].state;
    s += `<br><span class="dim">Structure</span> ${st || 'not readable'}`;
    const e = a.emas && a.emas[S.tf];
    if (e) s += ` <span class="dim">EMA50</span> ${fmt(S.pair, e)}`;
  }
  lg.innerHTML = s;
}
function onClick(param) {
  const btn = $('#alertHere');
  if (!param || !param.point || !S.pair) { btn.hidden = true; return; }
  const price = candle.coordinateToPrice(param.point.y);
  if (price == null) { btn.hidden = true; return; }
  S.clickPrice = price;
  btn.textContent = `Alert at ${fmt(S.pair, price)}`;
  btn.style.left = Math.min(param.point.x + 8, $('#chartwrap').clientWidth - 150) + 'px';
  btn.style.top = Math.max(param.point.y - 30, 28) + 'px';
  btn.hidden = false;
}

/* ---------- data ---------- */
async function loadSummary() {
  const s = await api('summary');
  S.summary = s.pairs || [];
  renderWatch(); renderTable();
}
async function loadPair(pair, keepView) {
  if (!pair) return;
  S.pair = pair; store.set('pair', pair);
  $('#pairInput').value = pair;
  $$('.wrow').forEach(r => r.classList.toggle('on', r.dataset.pair === pair));
  $('#chartEmpty').hidden = true;
  const [a, c] = await Promise.all([api('pair/' + pair), api(`candles/${pair}/${S.tf}`)]);
  S.analysis = a && !a.error ? a : null;
  S.bars = c && c.bars ? c.bars : []; S.ema = c && c.ema ? c.ema : [];
  const empty = $('#chartEmpty');
  if (!S.bars.length) {
    empty.hidden = false;
    empty.innerHTML = `<div><b>No data for ${esc(pair)} yet.</b><br>Open MetaTrader 5, then press "Scan pair".</div>`;
  }
  candle.setData(S.bars.map(b => ({ time: b[0], open: b[1], high: b[2], low: b[3], close: b[4] })));
  emaLine.setData(S.ema.map(e => ({ time: e[0], value: e[1] })));
  if (!keepView && S.bars.length) {
    const n = S.bars.length;
    chart.timeScale().setVisibleLogicalRange({ from: Math.max(0, n - 140), to: n + 8 });
  }
  paintStructure(); onCross(null); renderPane(); renderKey(); draw();
  $('#alertHere').hidden = true;
  if (location.hash === '#debug' && S.bars.length) {
    const w = $('#chartwrap'), l = S.bars[S.bars.length - 1];
    console.log('TGDBG ' + JSON.stringify({ w: w.clientWidth, h: w.clientHeight, bars: S.bars.length, last: l,
      y: candle.priceToCoordinate(l[4]), x: chart.timeScale().timeToCoordinate(l[0]),
      vr: chart.timeScale().getVisibleLogicalRange(), pw: chart.priceScale('right').width() }));
  }
}
async function loadTf(tf) {
  S.tf = tf; store.set('tf', tf);
  $$('#tfs button').forEach(b => b.classList.toggle('on', b.dataset.tf === tf));
  await loadPair(S.pair);
}

/* ---------- panels ---------- */
function stArrow(s) { return `<span class="tri ${s || 'none'}" title="${s || 'not readable'}"></span>`; }
function renderWatch() {
  const q = S.q.trim().toUpperCase();
  let rows = S.summary.slice();
  if (S.filter !== 'all') rows = rows.filter(r => r.verdict === S.filter || (S.filter === 'SIGNAL' && r.verdict === 'WAIT_FOR_SESSION'));
  if (q) rows = rows.filter(r => r.pair.includes(q));
  rows.sort((a, b) => (VORDER[a.verdict] ?? 9) - (VORDER[b.verdict] ?? 9) || ((a.nearest && a.nearest.dist_pips) ?? 1e9) - ((b.nearest && b.nearest.dist_pips) ?? 1e9));
  const el = $('#watchlist');
  if (!S.summary.length) {
    el.innerHTML = '<div class="pane"><p>No analysis yet.</p><p class="hint">Open MetaTrader 5 and press "Scan all". The first scan can take a few minutes.</p></div>';
    return;
  }
  el.innerHTML = rows.map(r => {
    const px = S.prices[r.pair] ?? r.price;
    const st = r.states || {};
    return `<button class="wrow ${r.pair === S.pair ? 'on' : ''}" data-pair="${r.pair}">
      <span class="wsym">${r.pair}</span><span class="wpx">${fmt(r.pair, px)}</span>
      <span class="wsub"><span class="vtag v-${r.verdict}">${VLABEL[r.verdict] || r.verdict}</span>${r.grade ? `<span class="mono">${r.grade}</span>` : ''}
      <span class="st" title="Weekly, daily, 4H">${stArrow(st.W)}${stArrow(st.D)}${stArrow(st['4H'])}</span>
      ${r.nearest ? `<span class="mono">${r.nearest.dist_pips.toFixed(0)}p</span>` : ''}</span></button>`;
  }).join('') || '<div class="pane"><p class="hint">No pairs match.</p></div>';
}
function renderKey() {
  $('#keyrow').innerHTML = `
    <span><i class="sw" style="background:var(--w)"></i>Weekly box</span>
    <span><i class="sw" style="background:var(--d)"></i>Daily box</span>
    <span><i class="sw" style="background:var(--h4)"></i>4H minor box</span>
    <span><i class="sw" style="background:var(--yours)"></i>Your box (dashed)</span>
    <span><i class="sw" style="background:var(--signal)"></i>HH / HL, target</span>
    <span><i class="sw" style="background:var(--error)"></i>LL / LH, stop</span>
    <span><i class="sw" style="background:var(--watch)"></i>EMA 50</span>
    <span>Numbers match the checklist</span>`;
}
function tag(t, c) { return `<span class="tag">${esc(t)}</span>`; }
function renderPane() {
  const a = S.analysis, el = $('#pane');
  $$('#tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === S.tab));
  if (!a) { el.innerHTML = '<div class="skeleton"></div><div class="skeleton"></div><p class="hint">No analysis for this pair yet. Press "Scan pair".</p>'; return; }
  if (S.tab === 'verdict') return paneVerdict(a, el);
  if (S.tab === 'plan') return panePlan(a, el);
  if (S.tab === 'levels') return paneLevels(a, el);
  return paneAlerts(a, el);
}
function paneVerdict(a, el) {
  const rs = a.reason ? (REASON[a.reason] || a.reason) : '';
  const rows = ['W', 'D', '4H'].map(tf => {
    const t = a.tf[tf] || {};
    if (!t.state) return `<tr><td>${tf}</td><td colspan="2">not readable</td></tr>`;
    const [x, y] = [t.ext_name, t.pair_name];
    return `<tr><td>${tf}</td><td>${stArrow(t.state)} ${t.state}${t.ext_confirmed ? '' : ' (current)'}</td>
      <td>${x} ${fmt(a.pair, t.levels[x].price)}<br>${y} ${fmt(a.pair, t.levels[y].price)}</td></tr>`;
  }).join('');
  const extras = (a.extras || []).map(x => tag(x.replaceAll('_', ' '))).join('') || '<span class="hint">none yet</span>';
  const pats = (a.patterns || []).map(p => tag(`${p.type.replaceAll('_', ' ')}: ${p.state.replaceAll('_', ' ')}`)).join('') || '<span class="hint">none</span>';
  el.innerHTML = `
    <div class="big"><span class="vtag v-${a.verdict}">${VLABEL[a.verdict] || a.verdict}</span>${a.grade ? `<span class="grade" title="A: core + 4H agrees + 2 extras. B: core + 1 extra. C: core only">${a.grade}</span>` : ''}
      <span class="mono">${fmt(a.pair, a.price)}</span></div>
    ${rs && a.verdict !== 'NO_TRADE' ? `<div class="hint">${esc(rs)}</div>` : ''}
    <div class="awaiting">${esc(a.awaiting || rs)}</div>
    <div class="hint">Bias now: <b>${a.bias.now || 'none'}</b>. Set on Sunday: <b>${a.bias.sunday || 'none'}</b>${a.bias.changed ? ' (changed since)' : ''}. Risk: <b>${a.alignment.risk || '-'}</b>.</div>
    <h3>Structure</h3>
    <table class="kv">${rows}</table>
    <h3>Checklist</h3>
    <ul class="checklist">${a.checklist.map(c => `<li><span class="n">${c.n}</span><span>${esc(c.item)}</span><span class="pf ${c.pass ? 'pass' : 'fail'}">${c.pass ? 'PASS' : 'FAIL'}</span>${c.detail ? `<span class="d">${esc(c.detail)}</span>` : ''}</li>`).join('')}</ul>
    <h3>Confluences</h3><div>${extras}</div>
    <h3>Patterns</h3><div>${pats}</div>
    <p class="hint">Analysis as of ${esc(a.asof_ny.slice(0, 16).replace('T', ' '))} New York. Market ${a.market_open ? 'open' : 'closed'}.</p>`;
}
function lotsFor(a, stopPips, riskPct, balance) {
  const pv = a.account && a.account.pip_value;
  if (!pv || !stopPips || !balance) return null;
  const step = a.account.step || 0.01, min = a.account.min_lot || 0.01;
  const raw = (balance * riskPct / 100) / (stopPips * pv);
  return { lots: Math.max(Math.floor(raw / step + 1e-9) * step, min), raw, amount: balance * riskPct / 100, min };
}
function panePlan(a, el) {
  const p = a.plan;
  const risk = (S.state && S.state.settings.account.risk_pct) || 1;
  const bal = (S.state && S.state.settings.account.balance) || '';
  if (!p) {
    el.innerHTML = `<p>No plan yet.</p><p class="hint">A plan appears when a closed confirmation sits at an area of interest. Until then the app shows where it is waiting.</p>
      <h3>Lot size calculator</h3>${calcHtml(a, 25, risk, bal)}`;
    wireCalc(a); return;
  }
  const side = p.side === 'buy' ? 'Buy' : 'Sell';
  el.innerHTML = `
    <div class="big"><span class="vtag v-${a.verdict}">${VLABEL[a.verdict] || a.verdict}</span><span class="mono">${side} ${a.pair}</span></div>
    <table class="kv">
      <tr><td>Entry (price now; the fill is the next open)</td><td>${fmt(a.pair, p.entry)}</td></tr>
      <tr><td>Stop (beyond box ${esc(p.box)}, plus buffer)</td><td>${fmt(a.pair, p.stop)}</td></tr>
      <tr><td>Stop distance</td><td>${pips(a.pair, p.stop_pips)} pips</td></tr>
      <tr><td>Target (${esc(p.target_reason || '')})</td><td>${p.target != null ? fmt(a.pair, p.target) : '-'}</td></tr>
      <tr><td>Reward to risk${p.capped ? ' (capped)' : ''}</td><td>${p.rr != null ? '1:' + p.rr.toFixed(2) : '-'}</td></tr>
    </table>
    <h3>Lot size</h3>${calcHtml(a, p.stop_pips, risk, bal)}
    <p class="hint">Set the stop and target, then leave the trade alone. Never move the stop to avoid a loss.</p>
    <div class="row"><button class="btn small" id="copyPlan">Copy plan</button></div>`;
  wireCalc(a);
  const cp = $('#copyPlan');
  if (cp) cp.onclick = () => navigator.clipboard && navigator.clipboard.writeText(
    `${side} ${a.pair}  entry ${fmt(a.pair, p.entry)}  stop ${fmt(a.pair, p.stop)}  target ${fmt(a.pair, p.target)}  1:${(p.rr || 0).toFixed(2)}`);
}
function calcHtml(a, stop, risk, bal) {
  const cur = (a.account && a.account.currency) || '';
  return `<div class="cols">
    <div class="fld"><label for="cRisk">Risk %</label><input id="cRisk" type="number" step="0.1" value="${risk}"></div>
    <div class="fld"><label for="cBal">Balance ${esc(cur)}</label><input id="cBal" type="number" step="1" value="${bal}" placeholder="MT5 account"></div>
    <div class="fld"><label for="cStop">Stop (pips)</label><input id="cStop" type="number" step="0.5" value="${Number(stop).toFixed(1)}"></div>
    <div class="fld"><label>Lots</label><div id="cLots" class="mono" style="height:30px;display:flex;align-items:center">-</div></div></div>
    <div id="cNote" class="hint"></div>`;
}
function wireCalc(a) {
  const run = () => {
    const risk = parseFloat($('#cRisk').value), stop = parseFloat($('#cStop').value);
    let bal = parseFloat($('#cBal').value);
    if (!bal) bal = (a.account && a.account.balance) || (S.state && S.state.mt5_balance) || 0;
    const r = lotsFor(a, stop, risk, bal || 0);
    const out = $('#cLots'), note = $('#cNote');
    if (!r) { out.textContent = '-'; note.textContent = 'Enter a balance and run a scan so the pip value is known.'; return; }
    out.textContent = r.lots.toFixed(2);
    note.innerHTML = `Risk amount ${r.amount.toFixed(2)} ${esc((a.account && a.account.currency) || '')}.` +
      (r.raw < r.min ? ` <span class="warn">The smallest lot (${r.min}) already risks more than that.</span>` : '');
  };
  ['cRisk', 'cBal', 'cStop'].forEach(id => $('#' + id).addEventListener('input', run));
  run();
}
function paneLevels(a, el) {
  const sorted = a.aois.slice().sort((x, y) => (x.broken - y.broken) || (x.dist_pips - y.dist_pips));
  const rows = sorted.map(b => `<div class="box${b.broken ? ' dead' : ''}${a.candidate === b.id ? ' pick' : ''}">
    <div class="box-top"><span class="sw" style="background:var(--${b.tf === 'D' ? 'd' : b.tf === '4H' ? 'h4' : 'w'})"></span><b>${b.id}</b> ${b.tf}
      <span class="mono">${fmt(a.pair, b.low)} to ${fmt(a.pair, b.high)}</span></div>
    <div class="box-sub">${b.pips.toFixed(0)} pips, ${b.touches} touches, ${b.broken ? 'broken, now ' : ''}${b.role}${b.at ? ', price is at it' : ''}, ${b.dist_pips.toFixed(0)} pips away${a.candidate === b.id ? ' (chosen)' : ''}</div>
    <div class="box-act"><button class="btn small" data-al="${b.high}" data-note="${b.tf} top">Alert at top</button> <button class="btn small" data-al="${b.low}" data-note="${b.tf} bottom">Alert at bottom</button></div></div>`).join('');
  el.innerHTML = `<h3>Areas of interest (nearest first)</h3>
    ${a.aois.length ? rows : '<p class="hint">No box has 3 touches inside the zone right now.</p>'}
    <h3>Extras at the chosen area</h3>
    ${(() => { const c = a.aois.find(b => b.id === a.candidate); if (!c) return '<p class="hint">No chosen area yet.</p>'; const e = c.extras;
      return `<div>${e.ema.length ? tag('EMA 50 near: ' + e.ema.join(', ')) : ''}${e.round_number != null ? tag('Round number ' + fmt(a.pair, e.round_number)) : ''}${e.previous_daily_swing ? tag('Previous daily swing') : ''}${c.overlap || c.overlaps_other_tf ? tag('Weekly and daily overlap') : ''}</div>`; })()}
    <h3>Swing points (${esc(S.tf)})</h3>
    <p class="hint">${(a.tf[S.tf] && a.tf[S.tf].swings || []).slice(-8).map(s => `${s.kind} ${fmt(a.pair, s.price)}`).join(', ') || 'none'}</p>
    <h3>Settings used</h3><p class="hint">Swing ${a.params.swing_atr} x ATR (daily 0.35), structure mode "${a.params.mode}", boxes up to ${a.params.cluster_pips} pips.</p>`;
  $$('[data-al]', el).forEach(b => b.onclick = async () => { await post('alerts', { pair: a.pair, price: parseFloat(b.dataset.al), note: b.dataset.note }); toast('Alert added', `${a.pair} at ${fmt(a.pair, parseFloat(b.dataset.al))}`); S.tab = 'alerts'; renderPane(); });
}
async function paneAlerts(a, el) {
  const d = await api('alerts');
  const price = S.clickPrice ?? a.price;
  el.innerHTML = `<h3>Add a price alert</h3>
    <div class="cols"><div class="fld"><label for="aPrice">${esc(a.pair)} price</label><input id="aPrice" type="number" step="any" value="${fmt(a.pair, price)}"></div>
    <div class="fld"><label for="aNote">Note</label><input id="aNote" maxlength="80"></div></div>
    <div class="row"><button class="btn small primary" id="aAdd">Add alert</button></div>
    <p class="hint">Alerts are watched while this terminal runs with MT5 open. You can also click the chart and press the alert button.</p>
    <h3>Active alerts</h3>
    ${d.alerts.length ? `<table class="grid"><tbody>${d.alerts.map(x => `<tr><td>${x.pair}</td><td class="n">${fmt(x.pair, x.price)}</td><td>${esc(x.note || '')}</td><td><button class="btn small" data-del="${x.id}">Remove</button></td></tr>`).join('')}</tbody></table>` : '<p class="hint">None.</p>'}
    <h3>Fired</h3>
    ${d.fired.length ? `<table class="grid"><tbody>${d.fired.slice().reverse().map(f => `<tr><td>${f.pair}</td><td class="n">${fmt(f.pair, f.price)}</td><td>${f.ny} NY<br>${f.manila} Manila</td></tr>`).join('')}</tbody></table>` : '<p class="hint">Nothing yet.</p>'}`;
  $('#aAdd').onclick = async () => {
    const v = parseFloat($('#aPrice').value);
    if (!v) return;
    await post('alerts', { pair: a.pair, price: v, note: $('#aNote').value });
    renderPane();
  };
  $$('[data-del]', el).forEach(b => b.onclick = async () => { await api('alerts/' + b.dataset.del, { method: 'DELETE' }); renderPane(); });
}
function renderTable() {
  const [key, dir] = S.sort;
  const val = r => ({ pair: r.pair, verdict: VORDER[r.verdict] ?? 9, grade: r.grade || 'Z', bias: r.bias || '', dist: (r.nearest && r.nearest.dist_pips) ?? 1e9 }[key]);
  const rows = S.summary.slice().sort((a, b) => (val(a) > val(b) ? 1 : val(a) < val(b) ? -1 : 0) * dir);
  const head = [['pair', 'Pair'], ['verdict', 'Verdict'], ['reason', 'Reason'], ['grade', 'Grade'], ['bias', 'Bias'], ['w', 'W'], ['d', 'D'], ['h', '4H'], ['near', 'Nearest area'], ['dist', 'Away'], ['aw', 'Waiting for']];
  const st = s => `${stArrow(s)}`;
  $('#summary').innerHTML = `<thead><tr>${head.map(h => `<th data-k="${h[0]}">${h[1]}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `
    <tr class="clk ${r.pair === S.pair ? 'on' : ''}" data-pair="${r.pair}"><td><b class="mono">${r.pair}</b></td>
    <td><span class="vtag v-${r.verdict}">${VLABEL[r.verdict] || r.verdict}</span></td><td>${esc(REASON[r.reason] || r.reason || '')}</td>
    <td class="n">${r.grade || ''}</td><td>${r.bias || ''}</td>
    <td>${st((r.states || {}).W)}</td><td>${st((r.states || {}).D)}</td><td>${st((r.states || {})['4H'])}</td>
    <td class="n">${r.nearest ? `${r.nearest.tf} ${fmt(r.pair, r.nearest.low)} to ${fmt(r.pair, r.nearest.high)} ${r.nearest.role}` : ''}</td>
    <td class="n">${r.nearest ? r.nearest.dist_pips.toFixed(0) + 'p' : ''}</td><td>${esc(r.awaiting || '')}</td></tr>`).join('')}</tbody>`;
}

/* ---------- toasts, alerts ---------- */
function toast(title, text) {
  const t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = `<b>${esc(title)}</b>${esc(text)}`;
  $('#toasts').appendChild(t);
  setTimeout(() => t.remove(), 9000);
}
function beep() {
  try {
    const c = new (window.AudioContext || window.webkitAudioContext)();
    const o = c.createOscillator(); const g = c.createGain();
    o.connect(g); g.connect(c.destination); o.frequency.value = 880; g.gain.value = 0.05;
    o.start(); setTimeout(() => { o.stop(); c.close(); }, 220);
  } catch { /* no audio */ }
}
async function pollAlerts() {
  try {
    const d = await api('alerts');
    if (d.fired.length > S.firedSeen) {
      for (const f of d.fired.slice(S.firedSeen)) {
        toast(`${f.pair} crossed ${fmt(f.pair, f.price)}`, `${f.note || ''} ${f.ny} New York, ${f.manila} Manila`);
        if ('Notification' in window && Notification.permission === 'granted') new Notification(`${f.pair} crossed ${fmt(f.pair, f.price)}`, { body: f.note || '' });
        beep();
      }
      S.firedSeen = d.fired.length;
    }
  } catch { /* server busy */ }
}

/* ---------- state, scan ---------- */
async function pollState() {
  try {
    S.state = Object.assign(S.state || {}, await api('state'));
  } catch {
    $('#conn').textContent = 'Server offline'; $('#conn').className = 'chip bad'; return;
  }
  const st = S.state;
  const c = $('#conn');
  c.textContent = st.mt5 ? 'MT5 connected' : 'MT5 offline';
  c.className = 'chip ' + (st.mt5 ? 'ok' : 'bad');
  c.title = st.mt5_error || '';
  const sc = st.scan, bar = $('#scanbar');
  bar.hidden = !sc.running && !sc.error;
  if (sc.running) {
    $('#scanfill').style.width = (sc.total ? 100 * sc.done / sc.total : 0) + '%';
    $('#scantext').textContent = `Scanning ${sc.current || ''} (${sc.done} of ${sc.total})`;
  } else if (sc.error) {
    $('#scanfill').style.width = '0';
    $('#scantext').textContent = 'Scan failed: ' + sc.error;
  }
  if (S.scanWas && !sc.running) { await loadSummary(); await loadPair(S.pair, true); }
  S.scanWas = sc.running;
  $('#scanBtn').disabled = sc.running; $('#scanAllBtn').disabled = sc.running;
}
async function pollPrices() {
  try {
    S.prices = await api('prices');
    $$('.wrow').forEach(r => { const p = S.prices[r.dataset.pair]; if (p != null) $('.wpx', r).textContent = fmt(r.dataset.pair, p); });
  } catch { /* offline */ }
}

/* ---------- wiring ---------- */
function wire() {
  $('#tfs').innerHTML = TFS.map(t => `<button data-tf="${t}" class="${t === S.tf ? 'on' : ''}">${t}</button>`).join('');
  $('#tfs').addEventListener('click', e => { const b = e.target.closest('button'); if (b) loadTf(b.dataset.tf); });
  $('#tabs').addEventListener('click', e => { const b = e.target.closest('button'); if (b) { S.tab = b.dataset.tab; store.set('tab', S.tab); renderPane(); paintStructure(); draw(); } });
  $('#watchlist').addEventListener('click', e => { const r = e.target.closest('.wrow'); if (r) loadPair(r.dataset.pair); });
  $('#summary').addEventListener('click', e => {
    const th = e.target.closest('th'); if (th) { const k = th.dataset.k; S.sort = [k, S.sort[0] === k ? -S.sort[1] : 1]; renderTable(); return; }
    const tr = e.target.closest('tr[data-pair]'); if (tr) loadPair(tr.dataset.pair);
  });
  $('#vchips').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; S.filter = b.dataset.f; $$('#vchips button').forEach(x => x.classList.toggle('on', x === b)); renderWatch(); });
  $('#filterInput').addEventListener('input', e => { S.q = e.target.value; renderWatch(); });
  $('#pairInput').addEventListener('change', e => { const v = e.target.value.trim().toUpperCase(); if ((S.state.pairs || []).includes(v)) loadPair(v); else e.target.value = S.pair; });
  $('#scanBtn').onclick = async () => { await post('connect'); const r = await post('scan', { pairs: [S.pair] }); if (!r.started) toast('Scan', 'A scan is already running.'); pollState(); };
  $('#scanAllBtn').onclick = async () => { await post('connect'); const r = await post('scan', {}); if (!r.started) toast('Scan', 'A scan is already running.'); pollState(); };
  for (const [id, key] of [['tgSwings', 'swings'], ['tgBoxes', 'boxes'], ['tgPatterns', 'patterns']]) {
    const el = $('#' + id);
    el.checked = S.layers[key];
    el.addEventListener('change', () => { S.layers[key] = el.checked; store.set('l.' + key, el.checked ? '1' : '0'); draw(); });
  }
  $('#alertHere').onclick = async () => {
    if (S.clickPrice == null) return;
    await post('alerts', { pair: S.pair, price: S.clickPrice, note: 'chart click' });
    toast('Alert added', `${S.pair} at ${fmt(S.pair, S.clickPrice)}`);
    $('#alertHere').hidden = true;
    if ('Notification' in window && Notification.permission === 'default') Notification.requestPermission();
    if (S.tab === 'alerts') renderPane();
  };
  $('#drawerBtn').onclick = () => { const d = $('#drawer'); d.classList.toggle('closed'); $('#drawerBtn').setAttribute('aria-expanded', String(!d.classList.contains('closed'))); window.dispatchEvent(new Event('resize')); };
  $('#themeBtn').onclick = () => { const r = document.documentElement; const n = r.dataset.theme === 'dark' ? 'light' : 'dark'; r.dataset.theme = n; store.set('theme', n); applyTheme(); paintStructure(); };
  $('#settingsBtn').onclick = () => {
    const s = S.state.settings;
    $('#sRisk').value = s.account.risk_pct; $('#sBalance').value = s.account.balance ?? '';
    $('#sSwing').value = s.structure.swing_atr; $('#sTrail').value = s.structure.mode || 'mixed';
    $('#sCluster').value = s.aoi.cluster_pips; $('#sCandles').value = s.ui.candles;
    $('#sMinStop').value = s.plan ? s.plan.stop_min_atr_d : 0;
    $('#settingsDlg').showModal();
  };
  $('#settingsForm').addEventListener('submit', async e => {
    const v = e.submitter && e.submitter.value;
    if (v !== 'save') return;
    const bal = $('#sBalance').value;
    await post('settings', {
      account: { risk_pct: parseFloat($('#sRisk').value) || 1, balance: bal ? parseFloat(bal) : null },
      structure: { swing_atr: parseFloat($('#sSwing').value) || 0.5, mode: $('#sTrail').value },
      aoi: { cluster_pips: parseFloat($('#sCluster').value) || 35 }, ui: { candles: $('#sCandles').value },
      plan: { stop_min_atr_d: parseFloat($('#sMinStop').value) || 0 },
    });
    await pollState(); applyTheme(); renderPane();
    toast('Settings saved', 'Press "Scan all" so the structure and boxes use the new numbers.');
  });
  document.addEventListener('keydown', e => {
    if (/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName) || e.ctrlKey || e.metaKey) return;
    const n = parseInt(e.key, 10);
    if (n >= 1 && n <= 7) loadTf(TFS[n - 1]);
    if (e.key === ']' || e.key === '[') {
      const list = $$('.wrow').map(r => r.dataset.pair); const i = list.indexOf(S.pair);
      if (list.length) loadPair(list[(i + (e.key === ']' ? 1 : -1) + list.length) % list.length]);
    }
  });
}

async function boot() {
  // links like /#pair=GBPUSD&tf=4H&tab=plan&theme=light open that view
  const h = Object.fromEntries(new URLSearchParams(location.hash.slice(1)));
  if (h.pair) S.pair = h.pair.toUpperCase();
  if (TFS.includes(h.tf)) S.tf = h.tf;
  if (['verdict', 'plan', 'levels', 'alerts'].includes(h.tab)) S.tab = h.tab;
  if (h.theme) store.set('theme', h.theme);
  document.documentElement.dataset.theme = store.get('theme', window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  wire();
  initChart();
  tickClocks(); setInterval(tickClocks, 1000);
  await pollState();
  const pairs = (S.state && S.state.pairs) || [];
  $('#pairList').innerHTML = pairs.map(p => `<option value="${p}">`).join('');
  S.state.reference = S.state.reference || [];
  applyTheme();
  await loadSummary();
  if (!S.pair || !pairs.includes(S.pair)) S.pair = (S.summary[0] && S.summary[0].pair) || pairs[0];
  await loadPair(S.pair);
  renderKey();
  setInterval(pollState, 2000); setInterval(pollPrices, 3000); setInterval(pollAlerts, 3000);
  pollPrices();
}
boot();
})();
