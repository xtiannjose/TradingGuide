"""Price alerts: a pop-up window when a pair crosses a price you set.

python app/alerts.py          keep it running while MT5 is open; Ctrl+C stops it
python app/alerts.py --test   show one pop-up now to check that pop-ups work

Levels are the [[alert]] blocks in app/settings.toml. Each fires once per run, on the bid
crossing the price (not on being past it when the script starts). Places no orders.
"""
import argparse
import ctypes
import os
import threading
import time
import urllib.parse
import urllib.request
import winsound
from datetime import datetime
from zoneinfo import ZoneInfo

import candles

NY = ZoneInfo("America/New_York")
# MessageBoxW flags: information icon, bring to front, always on top
FLAGS = 0x40 | 0x10000 | 0x40000


def crossed(prev, now, level):
    """True when price went from one side of `level` to the other (or onto it)."""
    return prev is not None and (prev < level <= now or prev > level >= now)


def telegram(text):
    """Send text to your phone via Telegram, only if TG_BOT_TOKEN and TG_CHAT_ID are set on this PC.

    Opt-in: with no variables set nothing is sent. The token lives in your environment, never
    in the repository. Returns True when Telegram accepted the message.
    """
    token, chat = os.environ.get("TG_BOT_TOKEN"), os.environ.get("TG_CHAT_ID")
    if not (token and chat):
        return False
    body = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", body, timeout=8) as r:
            return r.status == 200
    except OSError:
        return False


def popup(title, text):
    winsound.MessageBeep()
    # not a daemon thread: the process stays alive until the window is closed
    threading.Thread(target=ctypes.windll.user32.MessageBoxW, args=(None, text, title, FLAGS)).start()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--every", type=float, default=2.0, help="seconds between price checks")
    a = ap.parse_args()
    if a.test:
        popup("TradingGuide alert test", "Pop-ups work. Price alerts will look like this.")
        return

    cfg = candles.settings()
    alerts, suffix = cfg.get("alert", []), cfg["data"]["symbol_suffix"]
    if not alerts:
        raise SystemExit("No [[alert]] blocks in app/settings.toml.")
    tz = ZoneInfo(cfg["display_tz"])

    mt5 = candles.connect()
    last, live = {}, set(range(len(alerts)))
    try:
        for n, al in enumerate(alerts):
            sym = al["pair"] + suffix
            mt5.symbol_select(sym, True)
            tick = mt5.symbol_info_tick(sym)
            now = f"now {tick.bid:.5g}" if tick else "no price yet"
            print(f"  {al['pair']} {al['price']:.5g}  ({now})  {al.get('note', '')}")
        print("Watching. Ctrl+C to stop.")
        while live:
            for n in sorted(live):
                al = alerts[n]
                tick = mt5.symbol_info_tick(al["pair"] + suffix)
                if tick is None:
                    continue
                if crossed(last.get(n), tick.bid, al["price"]):
                    t = datetime.now(NY)
                    msg = (f"{al['pair']} crossed {al['price']:.5g} (bid {tick.bid:.5g})\n"
                           f"{al.get('note', '')}\n{t:%H:%M} New York / {t.astimezone(tz):%H:%M} Manila")
                    print(msg.replace("\n", "  "))
                    popup(f"TradingGuide: {al['pair']}", msg)
                    threading.Thread(target=telegram, args=(f"TradingGuide: {msg}",), daemon=True).start()
                    live.discard(n)
                last[n] = tick.bid
            time.sleep(a.every)
        print("All alerts fired.")
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
