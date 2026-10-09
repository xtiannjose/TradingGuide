"""Inline SVG diagrams for the trading guide. Pure stdlib. All prices are illustrations, not real data."""

NAVY, GREEN, RED, BLUE = "#1f2937", "#15803d", "#b91c1c", "#2563eb"
TEAL, AMBER, GREY, LIGHT = "#0f766e", "#b45309", "#6b7280", "#e5e7eb"

DEFS = """<svg width="0" height="0" style="position:absolute"><defs>
<marker id="ah-navy" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#1f2937"/></marker>
<marker id="ah-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#15803d"/></marker>
<marker id="ah-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#b91c1c"/></marker>
<marker id="ah-grey" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#6b7280"/></marker>
<marker id="ah-teal" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#0f766e"/></marker>
</defs></svg>"""


def svg(w, h, body, title=""):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}" '
            f'style="width:100%;height:auto;font-family:\'Segoe UI\',Calibri,Arial,sans-serif">{body}</svg>')


def line(x1, y1, x2, y2, color=NAVY, w=1.5, dash=None, arrow=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#ah-{arrow})"' if arrow else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{d}{m}/>'


def poly(pts, color=NAVY, w=3, dash=None):
    p = " ".join(f"{x},{y}" for x, y in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linejoin="round" stroke-linecap="round"{d}/>')


def txt(x, y, s, size=13, color=NAVY, anchor="middle", weight="400", italic=False):
    st = ' font-style="italic"' if italic else ""
    lines = s.split("\n")
    if len(lines) == 1:
        return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
                f'font-weight="{weight}"{st}>{s}</text>')
    t = "".join(f'<tspan x="{x}" dy="{0 if i == 0 else size * 1.25:.1f}">{ln}</tspan>' for i, ln in enumerate(lines))
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{st}>{t}</text>')


def rect(x, y, w, h, fill="none", stroke="none", op=1, rx=0, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" fill-opacity="{op}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def circ(x, y, r, fill=NAVY, stroke="none", sw=1):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def badge(x, y, n, color=TEAL):
    return circ(x, y, 10, color) + txt(x, y + 4.5, str(n), 12, "#ffffff", weight="700")


def candle(x, o, h, l, c, w=14):
    """y values (down is higher price direction reversed): smaller y = higher price."""
    up = c < o
    col = BLUE if up else RED
    top, bot = min(o, c), max(o, c)
    if bot - top < 2:
        bot = top + 2
    return (line(x, h, x, l, col, 2) + rect(x - w / 2, top, w, bot - top, col, col, 1))


def note(x, y, s, size=11, color=GREY, anchor="start"):
    return txt(x, y, s, size, color, anchor, italic=True)


# ---------------------------------------------------------------- diagrams

def anatomy():
    b = ""
    b += candle(120, 150, 90, 175, 100, 40)   # up candle
    b += candle(330, 100, 80, 175, 150, 40)   # down candle
    b += txt(120, 205, "UP candle (blue)", 12, BLUE, weight="600")
    b += txt(330, 205, "DOWN candle (red)", 12, RED, weight="600")
    b += txt(120, 40, "Close", 12) + line(120, 46, 120, 98, GREY, 1, arrow="grey") if False else ""
    # labels for the up candle
    b += line(200, 100, 142, 100, GREY, 1, arrow="grey") + txt(205, 104, "close (top of body)", 12, NAVY, "start")
    b += line(200, 150, 142, 150, GREY, 1, arrow="grey") + txt(205, 154, "open (bottom of body)", 12, NAVY, "start")
    b += line(200, 85, 122, 90, GREY, 1, arrow="grey") + txt(205, 80, "WICK (upper): where price has been", 12, NAVY, "start")
    b += line(200, 172, 122, 172, GREY, 1, arrow="grey") + txt(205, 190, "WICK (lower)", 12, NAVY, "start")
    b += txt(120, 128, "BODY", 11, "#ffffff", weight="700")
    b += txt(330, 128, "BODY", 11, "#ffffff", weight="700")
    b += txt(480, 98, "The next candle opens\nwhere this one closed.", 12, NAVY, "start")
    b += txt(480, 150, "He reads structure from\nBODIES. Wicks are only\n\"where price has been\".", 12, TEAL, "start", "600")
    return svg(700, 215, b, "Candle anatomy")


def structure(flip=False):
    W, H = 720, 290
    m = (lambda y: H - y) if flip else (lambda y: y)
    pts = [(40, 235), (120, 170), (180, 205), (270, 120), (340, 160), (440, 70), (520, 110), (600, 85)]
    P = [(x, m(y)) for x, y in pts]
    peaks = {1, 3, 5}
    troughs = {2, 4, 6}
    if not flip:
        names = {1: "HH 1", 2: "HL 1", 3: "HH 2", 4: "HL 2", 5: "HH 3", 6: "HL 3"}
    else:
        names = {1: "LL 1", 2: "LH 1", 3: "LL 2", 4: "LH 2", 5: "LL 3", 6: "LH 3"}
    b = ""
    # zone
    yh, yl = P[5][1], P[6][1]
    top, bot = min(yh, yl), max(yh, yl)
    zc = GREEN if not flip else RED
    b += rect(P[6][0], top, 700 - P[6][0], bot - top, zc, op=0.10)
    b += line(P[5][0], P[5][1], 700, P[5][1], zc, 1.5, "6 4")
    b += line(P[6][0], P[6][1], 700, P[6][1], zc, 1.5, "6 4")
    b += poly(P, NAVY, 3)
    for i, (x, y) in enumerate(P):
        if i in names:
            above = (i in peaks) != flip
            col = GREEN if not flip else RED
            b += circ(x, y, 5, col)
            b += txt(x, y - 12 if above else y + 22, names[i], 13, col, weight="700")
    b += circ(P[7][0], P[7][1], 6, NAVY, "#ffffff", 2)
    b += txt(P[7][0] + 11, P[7][1] + 4, "price now", 11, NAVY, "start")
    if not flip:
        b += txt(700, yh - 8, "current HH", 12, GREEN, "end", "600")
        b += txt(700, yl + 18, "current HL", 12, GREEN, "end", "600")
        b += txt(615, (yh + yl) / 2 + 55, "Price is INSIDE HH and HL\n= BULLISH", 12, GREEN, "middle", "700")
        b += txt(40, 30, "BULLISH structure: higher highs + higher lows", 15, GREEN, "start", "700")
    else:
        b += txt(700, yl - 8, "current LH", 12, RED, "end", "600")
        b += txt(700, yh + 18, "current LL", 12, RED, "end", "600")
        b += txt(615, yh + 42, "Price is INSIDE LH and LL\n= BEARISH", 12, RED, "middle", "700")
        b += txt(40, 30, "BEARISH structure: lower lows + lower highs", 15, RED, "start", "700")
    b += note(40, H - 8, "Illustration, not real price. Each turning point (an \"elbow\") is a structure point.")
    return svg(W, H, b, "Bullish or bearish structure")


def body_vs_wick():
    b = ""
    ly = 110
    b += line(30, ly, 690, ly, TEAL, 2, "7 4")
    b += txt(690, ly - 8, "structure line (for example the current HH)", 12, TEAL, "end", "600")
    # left candle: wick above line, body below
    b += candle(150, 175, 70, 190, 125, 22)
    b += rect(40, 205, 280, 56, "#fef2f2", "#fecaca", 1, 6)
    b += txt(180, 224, "Wick pokes above the line,\nbut the BODY closes below it", 12.5, RED, weight="700")
    b += txt(180, 252, "NOTHING changes. Structure stays the same.", 11.5, NAVY)
    # right candle: body closes above the line
    b += candle(500, 170, 40, 180, 78, 22)
    b += rect(380, 205, 300, 56, "#f0fdf4", "#bbf7d0", 1, 6)
    b += txt(530, 224, "The BODY closes above the line", 12.5, GREEN, weight="700")
    b += txt(530, 244, "= BREAK. Structure has shifted.", 12.5, GREEN, weight="700")
    b += note(30, 22, "Only a closed candle counts, and only its body. Touches, near misses and wicks do not.", 12, NAVY)
    return svg(700, 272, b, "Body close versus wick")


def state_machine():
    b = ""
    b += rect(40, 110, 230, 100, "#f0fdf4", GREEN, 1, 12, 2)
    b += txt(155, 150, "BULLISH", 20, GREEN, weight="700")
    b += txt(155, 178, "price between HH and HL", 12.5, NAVY)
    b += rect(450, 110, 230, 100, "#fef2f2", RED, 1, 12, 2)
    b += txt(565, 150, "BEARISH", 20, RED, weight="700")
    b += txt(565, 178, "price between LH and LL", 12.5, NAVY)
    # transitions
    b += line(272, 138, 448, 138, RED, 2.2, arrow="red")
    b += txt(360, 128, "A BODY closes BELOW the HL", 11.5, RED, weight="700")
    b += line(448, 186, 272, 186, GREEN, 2.2, arrow="green")
    b += txt(360, 206, "A BODY closes ABOVE the LH", 11.5, GREEN, weight="700")
    # self loops
    b += '<path d="M90,108 C80,50 230,50 220,108" fill="none" stroke="#15803d" stroke-width="2" marker-end="url(#ah-green)"/>'
    b += txt(155, 36, "Body closes above the HH:\nmove the HH up, find the new HL", 11.5, GREEN, weight="600")
    b += '<path d="M500,108 C490,50 640,50 630,108" fill="none" stroke="#b91c1c" stroke-width="2" marker-end="url(#ah-red)"/>'
    b += txt(565, 36, "Body closes below the LL:\nmove the LL down, find the new LH", 11.5, RED, weight="600")
    b += rect(150, 240, 420, 34, "#f3f4f6", "none", 1, 6)
    b += txt(360, 262, "Anything else (wicks, touches, small wiggles) = nothing changes.", 12.5, NAVY, weight="600")
    return svg(720, 285, b, "Structure state machine")


def snake():
    b = ""
    P = [(40, 70), (110, 150), (170, 100), (230, 185), (265, 165), (340, 250)]
    b += poly(P, NAVY, 3)
    b += txt(40, 52, "start", 11, GREY)
    # new LL
    b += circ(340, 250, 6, RED)
    b += badge(340, 226, 1)
    b += txt(358, 255, "new LL = the HEAD of the snake", 12, RED, "start", "700")
    # soft bump
    b += circ(265, 165, 6, GREY)
    b += badge(265, 140, 2, GREY)
    b += txt(283, 138, "soft bump: price could slide\nright through it. SKIP.", 11.5, GREY, "start", "600")
    # LH
    b += circ(170, 100, 7, RED)
    b += badge(170, 74, 3)
    b += txt(188, 70, "first SHARP turn = the new LH", 12.5, RED, "start", "700")
    # walk-back arrow
    b += poly([(325, 238), (280, 190), (250, 150), (192, 110)], TEAL, 2.5, "7 5")
    b += line(196, 112, 180, 102, TEAL, 2.5, arrow="teal")
    b += txt(430, 120, "Walk BACKWARDS from the head.\nThe first clean turn is the\npaired point.", 12, TEAL, "start", "600")
    b += rect(430, 175, 270, 90, "#f3f4f6", "none", 1, 8)
    b += txt(445, 198, "New LL  ->  find the LH", 12.5, NAVY, "start", "700")
    b += txt(445, 222, "New HH  ->  find the HL", 12.5, NAVY, "start", "700")
    b += txt(445, 246, "(mirror image, same walk-back)", 11.5, GREY, "start")
    b += note(40, 285, "Illustration, not real price.")
    return svg(720, 295, b, "Snake trick")


def zone_aoi():
    b = ""
    HHy, HLy = 70, 195
    b += rect(40, HHy, 660, HLy - HHy, GREEN, op=0.07)
    b += line(40, HHy, 700, HHy, GREEN, 1.8, "7 4") + txt(698, HHy - 7, "HH (top of the zone)", 12, GREEN, "end", "700")
    b += line(40, HLy, 700, HLy, GREEN, 1.8, "7 4") + txt(698, HLy + 17, "HL (bottom of the zone)", 12, GREEN, "end", "700")
    # valid AOI
    b += rect(40, 112, 660, 28, BLUE, BLUE, 0.16, 0, 1.2)
    b += txt(46, 106, "AOI inside the zone = VALID (3 touches)", 12, BLUE, "start", "700")
    # invalid AOIs
    b += rect(40, 232, 660, 24, RED, RED, 0.10, 0, 1, "5 3")
    b += txt(46, 275, "Below the HL = INVALID (price would have to turn bearish first)", 12, RED, "start", "700")
    b += rect(40, 22, 660, 22, RED, RED, 0.10, 0, 1, "5 3")
    b += txt(46, 15, "Above the HH = INVALID", 12, RED, "start", "700")
    P = [(60, 185), (110, 138), (160, 188), (215, 118), (270, 172), (330, 140), (385, 100), (440, 150), (500, 92), (560, 128)]
    b += poly(P, NAVY, 2.8)
    for n, i in ((1, 1), (2, 3), (3, 5)):
        x, y = P[i]
        b += badge(x, y - 18 if i != 5 else y + 22, n, BLUE)
    b += txt(620, 100, "price comes back\nto the AOI", 12, NAVY, "start", "600")
    b += line(618, 112, 585, 132, NAVY, 1.5, arrow="navy")
    return svg(720, 285, b, "Zone and AOI")


def break_retest():
    b = ""
    b += rect(40, 108, 520, 26, BLUE, "#ef4444", 0.16, 0, 1.2)
    b += txt(46, 100, "Resistance AOI (needs 3+ touches)", 12, BLUE, "start", "700")
    P = [(40, 235), (95, 112), (140, 190), (200, 108), (250, 185), (300, 112), (320, 150)]
    b += poly(P, NAVY, 2.6)
    b += badge(95, 92, 1, GREY) + badge(200, 88, 1, GREY) + badge(300, 90, 1, GREY)
    # break candle
    b += candle(345, 155, 55, 165, 62, 20)
    b += badge(345, 36, 2)
    b += txt(360, 30, "BODY closes above the zone = confirmed break", 12, TEAL, "start", "700")
    # pullback & retest
    P2 = [(345, 62), (420, 118), (500, 70), (600, 45)]
    b += poly(P2, NAVY, 2.6)
    b += circ(420, 118, 6, GREEN)
    b += badge(420, 160, 3)
    b += line(420, 150, 420, 127, GREEN, 2, arrow="green")
    b += txt(440, 170, "Price returns to test the zone (it is now SUPPORT),\nand gets rejected. This is where you buy.", 12, GREEN, "start", "700")
    b += line(610, 40, 650, 25, GREEN, 2.2, arrow="green")
    b += rect(40, 215, 285, 56, "#f3f4f6", "none", 1, 6)
    b += txt(52, 236, "1  Price keeps getting rejected at the zone", 11.5, NAVY, "start")
    b += txt(52, 254, "Stop: just below the zone (the idea is wrong if it closes back under)", 11, GREY, "start")
    b += txt(52, 268, "", 10, GREY, "start")
    b += note(380, 262, "Mirror image for a sell below support.", 11.5)
    return svg(720, 285, b, "Break and retest")


def head_shoulders():
    b = ""
    ny = 195
    P = [(30, 250), (130, 140), (190, ny), (290, 68), (390, ny), (470, 140), (540, 222), (600, ny - 5), (700, 290)]
    b += line(150, ny, 640, ny, TEAL, 2.4, "8 4")
    b += txt(646, ny + 4, "NECKLINE\n(horizontal, at an AOI)", 12, TEAL, "start", "700")
    b += poly(P, NAVY, 2.8)
    b += txt(130, 126, "Left shoulder", 12.5, NAVY, weight="700")
    b += txt(290, 52, "Head", 12.5, NAVY, weight="700")
    b += txt(470, 126, "Right shoulder", 12.5, NAVY, weight="700")
    b += rect(430, 22, 230, 56, "#fef2f2", RED, 1, 6)
    b += txt(545, 42, "Do NOT sell the right shoulder.", 12, RED, weight="700")
    b += txt(545, 60, "Extremely high risk.", 12, RED, weight="600")
    b += badge(540, 244, 1)
    b += txt(556, 248, "Body closes below the neckline\n= structure has shifted", 11.5, NAVY, "start", "600")
    b += badge(600, 168, 2)
    b += txt(615, 160, "Retest of the neckline", 11.5, NAVY, "start", "600")
    b += circ(600, ny - 5, 6, RED)
    b += badge(660, 258, 3)
    b += txt(40, 275, "3  After a rejection candle at the retest (shooting star, evening star or bearish engulfing): SELL.", 12, RED, "start", "700")
    b += txt(40, 292, "Stop above the retest high. Target at the next structure point.", 11.5, GREY, "start")
    b += note(40, 20, "Regular H&S (bearish). The inverted version is the mirror image for buys.", 12, NAVY)
    return svg(760, 305, b, "Head and shoulders")


def _panel(inner, title, sub=""):
    s = rect(2, 2, 166, 172, "#ffffff", LIGHT, 1, 8)
    s += inner
    s += txt(85, 150, title, 12.5, NAVY, weight="700")
    if sub:
        s += txt(85, 166, sub, 10.5, GREY)
    return s


def candles_panels():
    def sp(inner, title, sub=""):
        return f'<g>{_panel(inner, title, sub)}</g>'

    def at(dx, dy, g):
        return f'<g transform="translate({dx},{dy})">{g}</g>'

    panels = []
    # doji
    panels.append(sp(candle(85, 78, 30, 118, 76, 22), "Doji", "indecision, slowdown"))
    # spinning top
    panels.append(sp(candle(85, 80, 30, 118, 62, 22), "Spinning top", "small body, both wicks"))
    # hammer: two down candles then hammer
    g = candle(35, 40, 30, 55, 60, 16) + candle(60, 55, 45, 70, 80, 16) + candle(100, 85, 80, 128, 78, 18)
    panels.append(sp(g, "Hammer", "at SUPPORT: rejection"))
    # inverted hammer
    g = candle(35, 40, 30, 55, 60, 16) + candle(60, 55, 45, 70, 80, 16) + candle(100, 90, 40, 92, 85, 18)
    panels.append(sp(g, "Inverted hammer", "\"wick fill\" at support"))
    # bullish engulfing
    g = candle(35, 60, 50, 80, 75, 16) + candle(62, 75, 65, 98, 92, 16) + candle(105, 100, 30, 108, 45, 28)
    panels.append(sp(g, "Bullish engulfing", "covers the last TWO bodies"))
    # morning star: down candle, doji, big up
    g = candle(35, 50, 40, 78, 72, 16) + candle(65, 90, 82, 112, 94, 16) + candle(105, 100, 30, 108, 42, 28)
    panels.append(sp(g, "Morning star", "his favourite (buy)"))
    # bearish engulfing
    g = candle(35, 95, 85, 105, 80, 16) + candle(62, 80, 70, 88, 62, 16) + candle(105, 55, 40, 130, 118, 28)
    panels.append(sp(g, "Bearish engulfing", "covers the last TWO bodies"))
    # evening star
    g = candle(35, 95, 85, 105, 68, 16) + candle(65, 62, 52, 70, 58, 16) + candle(105, 50, 40, 130, 118, 28)
    panels.append(sp(g, "Evening star", "his favourite (sell)"))
    b = ""
    for i, p in enumerate(panels):
        b += at((i % 4) * 176, (i // 4) * 182, p)
    b += note(4, 372, "Illustrations. Blue = up candle, red = down candle (the colours on his charts).")
    return svg(704, 382, b, "Candle signals")


def trade_plan():
    b = ""
    # sell example with his NZDUSD numbers
    ex = 150
    b += rect(40, 108, 640, 26, BLUE, "#ef4444", 0.14, 0, 1)
    b += txt(46, 102, "Resistance AOI (price rejected here)", 12, BLUE, "start", "700")
    b += rect(250, 90, 200, ex - 90 + 0, RED, op=0.0)
    # boxes
    b += rect(250, 98, 230, ex - 98, RED, RED, 0.18, 0, 1.2)
    b += rect(250, ex, 230, 2 * (ex - 98), GREEN, GREEN, 0.18, 0, 1.2)
    b += line(250, ex, 480, ex, NAVY, 2)
    b += poly([(60, 210), (120, 160), (170, 125), (210, 128), (235, 138), (250, ex)], NAVY, 2.6)
    b += candle(215, 122, 112, 146, 140, 12)
    b += txt(496, 105, "STOP 0.59469", 12.5, RED, "start", "700")
    b += txt(496, 121, "20.2 pips above the entry", 11.5, NAVY, "start")
    b += txt(496, ex + 4, "ENTRY 0.59267 (sell)", 12.5, NAVY, "start", "700")
    b += txt(496, ex + 2 * (ex - 98) - 14, "TARGET 0.58862", 12.5, GREEN, "start", "700")
    b += txt(496, ex + 2 * (ex - 98) + 2, "= twice the risk (R:R 1:2)", 11.5, NAVY, "start")
    b += txt(365, 130, "RISK", 13, RED, weight="700")
    b += txt(365, ex + 52, "REWARD", 13, GREEN, weight="700")
    b += note(40, 292, "His recorded NZDUSD sell (1H view). He later closed it at about 1:5. Picture is schematic.", 11.5)
    return svg(720, 305, b, "Trade plan")


def sessions():
    b = ""
    x0, x1 = 40, 720
    pw = (x1 - x0) / 24.0
    X = lambda h: x0 + h * pw
    rows = [("Sydney", [(17, 24), (0, 2)], "#a78bfa", 40), ("Tokyo", [(19, 24), (0, 4)], "#f59e0b", 78),
            ("London", [(3, 12)], "#2563eb", 116), ("New York", [(8, 17)], "#0f766e", 154)]
    # window
    b += rect(X(1), 24, X(10.5) - X(1), 170, GREEN, op=0.12)
    for name, spans, col, y in rows:
        b += txt(36, y + 19, name, 12.5, NAVY, "end", "700")
        for a, c in spans:
            b += rect(X(a), y, X(c) - X(a), 28, col, op=0.85, rx=4)
    for h in range(0, 25, 3):
        b += line(X(h), 196, X(h), 202, GREY, 1) + txt(X(h), 216, f"{h:02d}:00", 10.5, GREY)
    b += line(x0, 196, x1, 196, GREY, 1)
    b += txt(X(1), 18, "1:00 start", 11.5, GREEN, "middle", "700")
    b += txt(X(10.5), 18, "10:30 last entry", 11.5, GREEN, "middle", "700")
    b += txt(X(3), 236, "London opens 3:00", 10.5, NAVY)
    b += txt(X(8), 236, "New York opens 8:00", 10.5, NAVY)
    b += txt(X(17), 236, "Market closes 17:00", 10.5, NAVY)
    b += txt(X(5.75), 262, "Green band = his trading window", 12, GREEN, weight="700")
    b += note(40, 282, "Times are New York time, as in his session graphic. Bar edges are approximate (he calls the graphic \"a bit inaccurate\").", 11)
    return svg(740, 292, b, "Trading sessions")


def mini_trend(up=True, w=86, h=44):
    if up:
        P = [(4, 38), (22, 22), (32, 30), (52, 12), (62, 20), (82, 5)]
        col = GREEN
    else:
        P = [(4, 6), (22, 22), (32, 14), (52, 32), (62, 24), (82, 39)]
        col = RED
    return svg(w, h, poly(P, col, 3), "up" if up else "down")


# ------------------------------------------------ revised versions (override the drafts above)

def anatomy():
    b = ""
    b += candle(110, 150, 90, 175, 100, 40)
    b += txt(110, 205, "UP candle (blue)", 12, BLUE, weight="600")
    b += line(160, 100, 132, 100, GREY, 1, arrow="grey") + txt(166, 104, "close (top of body)", 12, NAVY, "start")
    b += line(160, 150, 132, 150, GREY, 1, arrow="grey") + txt(166, 154, "open (bottom of body)", 12, NAVY, "start")
    b += line(160, 80, 112, 90, GREY, 1, arrow="grey") + txt(166, 78, "upper WICK: where price has been", 12, NAVY, "start")
    b += line(160, 178, 112, 172, GREY, 1, arrow="grey") + txt(166, 186, "lower WICK", 12, NAVY, "start")
    b += txt(110, 128, "BODY", 11, "#ffffff", weight="700")
    b += txt(440, 96, "The next candle opens\nwhere this one closed.", 12.5, NAVY, "start")
    b += txt(440, 146, "He reads structure from\nBODIES. Wicks are only\n\"where price has been\".", 12.5, TEAL, "start", "600")
    b += candle(650, 100, 80, 175, 150, 40)
    b += txt(650, 128, "BODY", 11, "#ffffff", weight="700")
    b += txt(650, 205, "DOWN candle (red)", 12, RED, weight="600", anchor="middle")
    return svg(720, 215, b, "Candle anatomy")


def sessions():
    b = ""
    x0, x1 = 110, 720
    pw = (x1 - x0) / 24.0
    X = lambda h: x0 + h * pw
    rows = [("Sydney", [(17, 24), (0, 2)], "#a78bfa", 40), ("Tokyo", [(19, 24), (0, 4)], "#f59e0b", 78),
            ("London", [(3, 12)], "#2563eb", 116), ("New York", [(8, 17)], "#0f766e", 154)]
    b += rect(X(1), 24, X(10.5) - X(1), 170, GREEN, op=0.12)
    for name, spans, col, y in rows:
        b += txt(100, y + 19, name, 12.5, NAVY, "end", "700")
        for a, c in spans:
            b += rect(X(a), y, X(c) - X(a), 28, col, op=0.85, rx=4)
    for h in range(0, 25, 3):
        b += line(X(h), 196, X(h), 202, GREY, 1) + txt(X(h), 216, f"{h:02d}:00", 10.5, GREY)
    b += line(x0, 196, x1, 196, GREY, 1)
    b += txt(X(1), 18, "1:00 start", 11.5, GREEN, "middle", "700")
    b += txt(X(10.5), 18, "10:30 last entry", 11.5, GREEN, "middle", "700")
    b += txt(X(3), 236, "London opens 3:00", 10.5, NAVY)
    b += txt(X(8) + 14, 250, "New York opens 8:00", 10.5, NAVY)
    b += txt(X(17), 236, "Market closes 17:00", 10.5, NAVY)
    b += txt(X(5.75), 272, "Green band = his trading window", 12, GREEN, weight="700")
    b += note(40, 296, "Times are New York time, as in his session graphic. Bar edges are approximate (he calls the graphic \"a bit inaccurate\").", 11)
    return svg(740, 306, b, "Trading sessions")


def body_vs_wick():
    b = ""
    ly = 110
    b += line(30, ly, 690, ly, TEAL, 2, "7 4")
    b += txt(335, ly - 8, "structure line (for example the current HH)", 12, TEAL, "middle", "600")
    b += candle(150, 175, 70, 190, 125, 22)
    b += rect(40, 205, 280, 56, "#fef2f2", "#fecaca", 1, 6)
    b += txt(180, 224, "Wick pokes above the line,\nbut the BODY closes below it", 12.5, RED, weight="700")
    b += txt(180, 252, "NOTHING changes. Structure stays the same.", 11.5, NAVY)
    b += candle(540, 170, 40, 180, 78, 22)
    b += rect(400, 205, 290, 56, "#f0fdf4", "#bbf7d0", 1, 6)
    b += txt(545, 224, "The BODY closes above the line", 12.5, GREEN, weight="700")
    b += txt(545, 244, "= BREAK. Structure has shifted.", 12.5, GREEN, weight="700")
    b += note(30, 22, "Only a closed candle counts, and only its body. Touches, near misses and wicks do not.", 12, NAVY)
    return svg(700, 272, b, "Body close versus wick")


def snake():
    b = ""
    P = [(40, 70), (110, 150), (170, 100), (230, 185), (265, 165), (340, 250)]
    b += poly(P, NAVY, 3)
    b += txt(40, 52, "start", 11, GREY)
    b += circ(340, 250, 6, RED)
    b += badge(340, 226, 1)
    b += txt(340, 280, "new LL = the HEAD of the snake", 12.5, RED, "middle", "700")
    b += circ(265, 165, 6, GREY)
    b += badge(265, 140, 2, GREY)
    b += txt(284, 134, "soft bump: price could\nslide right through it.\nSKIP.", 11.5, GREY, "start", "600")
    b += circ(170, 100, 7, RED)
    b += badge(170, 74, 3)
    b += txt(188, 70, "first SHARP turn = the new LH", 12.5, RED, "start", "700")
    b += poly([(325, 238), (280, 190), (250, 150), (192, 110)], TEAL, 2.5, "7 5")
    b += line(196, 112, 180, 102, TEAL, 2.5, arrow="teal")
    b += txt(480, 100, "Walk BACKWARDS from the head.\nThe first clean turn is the\npaired point.", 12.5, TEAL, "start", "600")
    b += rect(480, 160, 220, 92, "#f3f4f6", "none", 1, 8)
    b += txt(494, 186, "New LL: find the LH", 12.5, NAVY, "start", "700")
    b += txt(494, 210, "New HH: find the HL", 12.5, NAVY, "start", "700")
    b += txt(494, 236, "(mirror image, same walk-back)", 11, GREY, "start")
    b += note(40, 300, "Illustration, not real price.")
    return svg(720, 310, b, "Snake trick")


def zone_aoi():
    b = ""
    HHy, HLy = 70, 195
    b += rect(40, HHy, 660, HLy - HHy, GREEN, op=0.07)
    b += line(40, HHy, 700, HHy, GREEN, 1.8, "7 4") + txt(698, HHy - 7, "HH (top of the zone)", 12, GREEN, "end", "700")
    b += line(40, HLy, 700, HLy, GREEN, 1.8, "7 4") + txt(698, HLy + 17, "HL (bottom of the zone)", 12, GREEN, "end", "700")
    b += rect(40, 112, 660, 28, BLUE, BLUE, 0.16, 0, 1.2)
    b += txt(698, 162, "Blue box = VALID AOI: inside the zone, 3 touches", 12, BLUE, "end", "700")
    b += rect(40, 232, 660, 24, RED, RED, 0.10, 0, 1, "5 3")
    b += txt(46, 275, "Below the HL = INVALID (price would have to turn bearish first)", 12, RED, "start", "700")
    b += rect(40, 22, 660, 22, RED, RED, 0.10, 0, 1, "5 3")
    b += txt(46, 15, "Above the HH = INVALID", 12, RED, "start", "700")
    P = [(60, 185), (110, 138), (160, 188), (215, 118), (270, 172), (330, 140), (385, 100), (440, 150), (500, 92), (560, 128)]
    b += poly(P, NAVY, 2.8)
    for n, i in ((1, 1), (2, 3), (3, 5)):
        x, y = P[i]
        b += badge(x, y + 24 if i != 3 else y - 20, n, BLUE)
    b += txt(600, 100, "price comes back\nto the AOI", 12, NAVY, "start", "600")
    b += line(598, 106, 568, 124, NAVY, 1.5, arrow="navy")
    return svg(720, 285, b, "Zone and AOI")


def break_retest():
    b = ""
    b += rect(40, 108, 520, 26, BLUE, "#ef4444", 0.16, 0, 1.2)
    b += txt(566, 118, "Resistance AOI\n(3+ touches)", 12, BLUE, "start", "700")
    P = [(40, 235), (95, 112), (140, 190), (200, 108), (250, 185), (300, 112), (320, 150)]
    b += poly(P, NAVY, 2.6)
    b += badge(95, 90, 1, GREY) + badge(200, 86, 1, GREY) + badge(300, 90, 1, GREY)
    b += candle(345, 155, 55, 165, 62, 20)
    b += badge(345, 36, 2)
    b += txt(362, 26, "BODY closes above the zone = confirmed break", 12, TEAL, "start", "700")
    b += poly([(345, 62), (420, 118), (500, 70), (600, 50)], NAVY, 2.6)
    b += circ(420, 118, 6, GREEN)
    b += badge(420, 160, 3)
    b += line(420, 150, 420, 127, GREEN, 2, arrow="green")
    b += txt(440, 164, "Price returns to test the zone (now SUPPORT)\nand is rejected. This is where you buy.", 12, GREEN, "start", "700")
    b += line(606, 48, 650, 30, GREEN, 2.2, arrow="green")
    b += badge(52, 264, 1, GREY) + txt(68, 268, "Price keeps getting rejected at the zone", 12, NAVY, "start")
    b += txt(68, 288, "Stop: just below the zone (the idea is wrong if price closes back under it)", 11.5, GREY, "start")
    b += note(68, 310, "Mirror image for a sell below support.", 11.5)
    return svg(720, 320, b, "Break and retest")


def head_shoulders():
    b = ""
    ny = 195
    P = [(30, 250), (130, 140), (190, ny), (290, 68), (390, ny), (470, 140), (535, 225), (590, ny - 3), (690, 290)]
    b += line(150, ny, 650, ny, TEAL, 2.4, "8 4")
    b += txt(290, ny + 26, "NECKLINE (horizontal, at an AOI)", 12, TEAL, "middle", "700")
    b += poly(P, NAVY, 2.8)
    b += txt(130, 126, "Left shoulder", 12.5, NAVY, weight="700")
    b += txt(290, 52, "Head", 12.5, NAVY, weight="700")
    b += txt(470, 126, "Right shoulder", 12.5, NAVY, weight="700")
    b += rect(500, 20, 250, 56, "#fef2f2", RED, 1, 6)
    b += txt(625, 41, "Do NOT sell the right shoulder.", 12, RED, weight="700")
    b += txt(625, 60, "Extremely high risk.", 12, RED, weight="600")
    b += circ(535, 225, 5, NAVY) + badge(507, 240, 1)
    b += circ(590, ny - 3, 6, RED) + badge(590, 168, 2)
    b += badge(640, 214, 3, RED)
    b += badge(52, 306, 1) + txt(68, 310, "Body closes below the neckline = structure has shifted", 12, NAVY, "start")
    b += badge(52, 330, 2) + txt(68, 334, "Price returns to retest the neckline", 12, NAVY, "start")
    b += badge(52, 354, 3, RED) + txt(68, 358, "Rejection candle at the retest (shooting star, evening star, bearish engulfing): SELL", 12, RED, "start", "700")
    b += txt(68, 378, "Stop above the retest high. Target at the next structure point.", 11.5, GREY, "start")
    b += note(40, 20, "Regular H&S (bearish). The inverted version is the mirror image for buys.", 12, NAVY)
    return svg(760, 390, b, "Head and shoulders")


def trade_plan():
    b = ""
    ex = 150
    top = 98
    b += rect(240, top, 230, ex - top, RED, RED, 0.18, 0, 1.2)
    b += rect(240, ex, 230, 2 * (ex - top), GREEN, GREEN, 0.18, 0, 1.2)
    b += line(240, ex, 470, ex, NAVY, 2)
    b += poly([(50, 250), (100, 210), (150, 165), (198, 122), (240, ex)], NAVY, 2.6)
    b += candle(198, 120, 108, 142, 138, 12)
    b += txt(50, 108, "price rallies into resistance\nand is rejected", 11.5, GREY, "start", "600")
    b += circ(240, ex, 5, NAVY)
    b += txt(496, 104, "STOP 0.59469", 12.5, RED, "start", "700")
    b += txt(496, 121, "20.2 pips above the entry", 11.5, NAVY, "start")
    b += txt(496, ex + 4, "ENTRY 0.59267 (sell)", 12.5, NAVY, "start", "700")
    b += txt(496, ex + 2 * (ex - top) - 14, "TARGET 0.58862", 12.5, GREEN, "start", "700")
    b += txt(496, ex + 2 * (ex - top) + 2, "= twice the risk (R:R 1:2)", 11.5, NAVY, "start")
    b += txt(355, 128, "RISK", 13, RED, weight="700")
    b += txt(355, ex + 56, "REWARD", 13, GREEN, weight="700")
    b += note(40, 292, "His recorded NZDUSD sell (1H view). He later closed it at about 1:5. Picture is schematic.", 11.5)
    return svg(720, 305, b, "Trade plan")


def stop_aoi():
    b = ""
    b += rect(40, 172, 460, 30, BLUE, BLUE, 0.16, 0, 1.2)
    b += txt(48, 192, "Support AOI (3+ touches)", 12, BLUE, "start", "700")
    b += poly([(40, 140), (130, 62), (185, 150), (232, 122), (282, 186)], NAVY, 2.6)
    b += line(130, 62, 330, 62, GREY, 1.2, "3 4")
    b += candle(292, 184, 178, 200, 194, 12) + candle(310, 196, 166, 199, 170, 14)
    b += badge(310, 150, 1)
    b += rect(330, 62, 170, 108, GREEN, GREEN, 0.15) + rect(330, 170, 170, 54, RED, RED, 0.15)
    b += line(322, 170, 500, 170, NAVY, 2)
    b += line(330, 224, 500, 224, RED, 2, "6 3") + line(330, 62, 500, 62, GREEN, 2, "6 3")
    b += txt(415, 120, "REWARD", 13, GREEN, weight="700") + txt(415, 214, "RISK", 13, RED, weight="700")
    b += txt(510, 58, "3 TARGET at the next\nstructure point (2 x risk)", 12, GREEN, "start", "700")
    b += txt(510, 166, "4 ENTRY at the open\nof the next candle", 12, NAVY, "start", "700")
    b += txt(510, 222, "2 STOP below the whole\nAOI + 5 to 10 pips", 12, RED, "start", "700")
    b += note(40, 262, "1 the signal candle closes inside the AOI; 2 set the stop; 3 then the target; 4 then enter.", 11.5)
    b += note(40, 278, "A buy; a sell is the mirror image. Schematic, not real prices.", 11.5)
    return svg(720, 288, b, "Stop beyond the whole AOI")


def zones_levels():
    b = ""
    x0, x1 = 120, 700
    lo, hi = 95.0, 99.0
    X = lambda p: x0 + (p - lo) / (hi - lo) * (x1 - x0)
    rows = [("Weekly", 95.4, 98.0, GREEN, "HL 95.4 to HH 98.0", 36),
            ("Daily", 96.6, 98.4, GREEN, "HL 96.6 to HH 98.4", 84),
            ("4-hour", 97.8, 98.1, RED, "LL 97.8 to LH 98.1", 132)]
    for name, a, c, col, label, y in rows:
        b += txt(110, y + 24, name, 13, NAVY, "end", "700")
        b += rect(X(a), y, X(c) - X(a), 36, col, op=0.85, rx=4)
        if X(c) - X(a) > 150:
            b += txt(X(a) + 12, y + 23, label, 12.5, "#ffffff", "start", "700")
        else:
            b += txt(X(a) - 10, y + 23, label, 12.5, col, "end", "700")
    py = X(97.88)
    b += line(py, 22, py, 186, NAVY, 1.6, "5 4")
    b += txt(py, 16, "price 97.88", 12, NAVY, weight="700")
    b += line(x0, 190, x1, 190, GREY, 1)
    for p in (95, 96, 97, 98, 99):
        b += line(X(p), 190, X(p), 196, GREY, 1) + txt(X(p), 211, f"{p}.0", 11, GREY)
    b += note(40, 236, "AUDJPY example (approximate levels). Green = bullish zone, red = bearish zone.", 11)
    return svg(720, 246, b, "Zones on one price axis")


ALL = {
    "zonelevels": zones_levels,
    "anatomy": anatomy,
    "bull": lambda: structure(False),
    "bear": lambda: structure(True),
    "bodywick": body_vs_wick,
    "state": state_machine,
    "snake": snake,
    "zone": zone_aoi,
    "breakretest": break_retest,
    "hs": head_shoulders,
    "candles": candles_panels,
    "plan": trade_plan,
    "stopaoi": stop_aoi,
    "sessions": sessions,
}
