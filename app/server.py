"""Local web app: a TradingView-style terminal for the analysis (phase 10).

python app/server.py [--port 8765] [--no-browser]

Binds to 127.0.0.1 only. Reads app/data/*.json written by scan.py, and keeps one MT5
connection for scans, live prices and price alerts. It never places orders.
"""
import argparse
import json
import mimetypes
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

import alerts as alert_logic
import candles
import lotsize
import params
import scan

ROOT = Path(__file__).parent
WEB = ROOT / "web"
DATA = ROOT / "data"
NY = ZoneInfo("America/New_York")
TFS = candles.ORDER


class Core:
    """MT5 connection, scan thread, price cache and alert watcher, all behind one lock."""

    def __init__(self):
        self.lock = threading.RLock()
        self.mt5 = None
        self.mt5_error = None
        self.cfg = params.load()
        self.scan = {"running": False, "done": 0, "total": 0, "current": None, "error": None, "finished": None}
        self.prices = {}
        self.fired = []
        self._last = {}
        self._dead = set()
        threading.Thread(target=self._watch, daemon=True).start()

    # ---- MT5
    def connect(self):
        with self.lock:
            if self.mt5 is not None:
                return True
            try:
                self.mt5 = candles.connect()
                self.mt5_error = None
                return True
            except Exception as e:  # terminal closed or not logged in
                self.mt5, self.mt5_error = None, str(e)
                return False

    def reload(self):
        with self.lock:
            self.cfg = params.load()

    # ---- alerts: settings.toml seeds, user.json adds
    def alert_list(self):
        seeds = [{**a, "id": f"toml-{n}", "source": "settings"} for n, a in enumerate(self.cfg.get("alert", []))]
        mine = []
        user = DATA / "user.json"
        if user.exists():
            try:
                mine = json.loads(user.read_text(encoding="utf-8")).get("user_alerts", [])
            except ValueError:
                mine = []
        return [a for a in seeds if a["id"] not in self._dead] + [{**a, "source": "you"} for a in mine]

    def _save_alerts(self, mine):
        DATA.mkdir(exist_ok=True)
        user = DATA / "user.json"
        cur = {}
        if user.exists():
            try:
                cur = json.loads(user.read_text(encoding="utf-8"))
            except ValueError:
                cur = {}
        cur["user_alerts"] = mine
        user.write_text(json.dumps(cur, indent=2), encoding="utf-8")

    def add_alert(self, pair, price, note):
        with self.lock:
            mine = [a for a in self.alert_list() if a["source"] == "you"]
            a = {"id": f"u{int(time.time() * 1000)}", "pair": pair, "price": float(price), "note": note or "", "active": True}
            self._save_alerts([{k: v for k, v in x.items() if k != "source"} for x in mine] + [a])
            return a

    def delete_alert(self, aid):
        with self.lock:
            if aid.startswith("toml-"):
                self._dead.add(aid)
                return
            mine = [{k: v for k, v in a.items() if k != "source"} for a in self.alert_list() if a["source"] == "you"]
            self._save_alerts([a for a in mine if a["id"] != aid])

    def save_settings(self, upd):
        with self.lock:  # same lock as the alert writes: both rewrite user.json
            params.save_user(upd)
            self.reload()

    def _watch(self):
        """Every 2 seconds: refresh prices of the watchlist and fire alerts on a cross."""
        while True:
            time.sleep(2)
            with self.lock:
                if self.mt5 is None or self.scan["running"]:
                    continue
                try:
                    suffix = self.cfg["data"]["symbol_suffix"]
                    syms = set(self.cfg.get("pairs", [])) | {a["pair"] for a in self.alert_list()}
                    for p in syms:
                        t = self.mt5.symbol_info_tick(p + suffix)
                        if t is not None and t.bid:
                            self.prices[p] = float(t.bid)
                    for a in self.alert_list():
                        px = self.prices.get(a["pair"])
                        if px is None or a.get("active") is False or a["id"] in {f["alert"] for f in self.fired}:
                            continue
                        if alert_logic.crossed(self._last.get(a["id"]), px, a["price"]):
                            now = datetime.now(NY)
                            self.fired.append({
                                "n": len(self.fired) + 1, "alert": a["id"], "pair": a["pair"], "price": a["price"],
                                "bid": px, "note": a.get("note", ""), "ny": now.strftime("%a %H:%M"),
                                "manila": now.astimezone(ZoneInfo(self.cfg["display_tz"])).strftime("%a %H:%M"),
                            })
                            f = self.fired[-1]  # phone message too, if Telegram is set up (opt-in, see alerts.telegram)
                            threading.Thread(target=alert_logic.telegram, daemon=True, args=(
                                f"TradingGuide: {f['pair']} crossed {f['price']} (bid {f['bid']}). {f['note']} {f['ny']} NY / {f['manila']} Manila",)).start()
                        self._last[a["id"]] = px
                except Exception as e:
                    self.mt5_error = str(e)
                    self.mt5 = None

    # ---- scanning
    def start_scan(self, pairs):
        with self.lock:
            if self.scan["running"]:
                return False
            self.scan.update({"running": True, "done": 0, "total": len(pairs), "current": None,
                              "error": None, "finished": None})
        threading.Thread(target=self._scan, args=(pairs,), daemon=True).start()
        return True

    def _scan(self, pairs):
        try:
            if not self.connect():
                raise RuntimeError(self.mt5_error or "MT5 is not reachable")
            self.reload()
            rows = []
            for n, p in enumerate(pairs, 1):
                with self.lock:
                    self.scan["current"] = p
                try:
                    with self.lock:
                        rows.append(scan.scan_pair(self.mt5, p, self.cfg))
                except Exception as e:
                    rows.append({"pair": p, "verdict": "ERROR", "reason": str(e)[:160]})
                with self.lock:
                    self.scan["done"] = n
            scan.write_summary(rows)
        except Exception as e:
            with self.lock:
                self.scan["error"] = str(e)
        finally:
            with self.lock:
                self.scan.update({"running": False, "current": None, "finished": datetime.now(NY).isoformat()})


CORE = None


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


class Handler(BaseHTTPRequestHandler):
    server_version = "TradingGuide"

    def log_message(self, *a):  # quiet
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return {}

    def _local_only(self, write):
        """Refuse DNS-rebinding (wrong Host) and cross-site writes (foreign Origin)."""
        port = self.server.server_address[1]
        if self.headers.get("Host", "") not in (f"127.0.0.1:{port}", f"localhost:{port}"):
            return False
        origin = self.headers.get("Origin")
        return not (write and origin and origin not in (f"http://127.0.0.1:{port}", f"http://localhost:{port}"))

    def do_GET(self):
        if not self._local_only(False):
            return self._send(403, {"error": "forbidden"})
        u = urlparse(self.path)
        path, q = u.path, parse_qs(u.query)
        if path.startswith("/api/"):
            return self._api_get(path[5:], q)
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        f = (WEB / rel).resolve()
        if WEB.resolve() not in f.parents and f != WEB.resolve() or not f.is_file():
            return self._send(404, {"error": "not found"})
        ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
        if f.suffix == ".js":
            ctype = "text/javascript"
        self._send(200, f.read_bytes(), ctype + ("; charset=utf-8" if ctype.startswith("text") else ""))

    def do_POST(self):
        if not self._local_only(True):
            return self._send(403, {"error": "forbidden"})
        u = urlparse(self.path)
        return self._api_post(u.path[5:], self._body())

    def do_DELETE(self):
        if not self._local_only(True):
            return self._send(403, {"error": "forbidden"})
        u = urlparse(self.path)
        parts = u.path[5:].split("/")
        if parts[0] == "alerts" and len(parts) == 2:
            CORE.delete_alert(parts[1])
            return self._send(200, {"ok": True})
        self._send(404, {"error": "not found"})

    def _api_get(self, route, q):
        c = CORE
        parts = route.split("/")
        if route == "state":
            with c.lock:
                return self._send(200, {
                    "mt5": c.mt5 is not None, "mt5_error": c.mt5_error, "scan": dict(c.scan),
                    "now_ny": datetime.now(NY).isoformat(), "offset": c.cfg["data"]["server_ny_offset_hours"],
                    "display_tz": c.cfg["display_tz"], "pairs": c.cfg["pairs"],
                    "reference": c.cfg.get("reference", []),
                    "settings": {"account": c.cfg["account"], "structure": c.cfg["structure"],
                                 "aoi": {"cluster_pips": c.cfg["aoi"]["cluster_pips"]}, "ui": c.cfg["ui"],
                                 "plan": {"stop_min_atr_d": c.cfg["plan"].get("stop_min_atr_d", 0.0)}},
                })
        if route == "summary":
            return self._send(200, read_json(DATA / "summary.json", {"updated": None, "pairs": []}))
        if parts[0] == "pair" and len(parts) == 2:
            d = read_json(DATA / "analysis" / f"{parts[1]}.json")
            return self._send(200 if d else 404, d or {"error": "no analysis yet, run a scan"})
        if parts[0] == "candles" and len(parts) == 3 and parts[2] in TFS:
            d = read_json(DATA / "candles" / f"{parts[1]}_{parts[2]}.json")
            return self._send(200 if d else 404, d or {"error": "no candles yet, run a scan"})
        if route == "prices":
            with c.lock:
                return self._send(200, dict(c.prices))
        if route == "alerts":
            with c.lock:
                return self._send(200, {"alerts": c.alert_list(), "fired": c.fired})
        if route == "lotsize":
            return self._send(200, self._lots(q))
        self._send(404, {"error": "not found"})

    def _lots(self, q):
        try:
            pair = q["pair"][0]
            stop, risk = float(q["stop"][0]), float(q["risk"][0])
            bal = float(q["balance"][0])
            a = read_json(DATA / "analysis" / f"{pair}.json", {})
            acc = a.get("account") or {}
            if not acc.get("pip_value"):
                return {"error": "no pip value yet, run a scan for this pair"}
            lot, raw = lotsize.lots(bal * risk / 100, stop, acc["pip_value"], acc.get("step", 0.01),
                                    acc.get("min_lot", 0.01))
            return {"lots": lot, "raw": raw, "risk_amount": bal * risk / 100, "currency": acc.get("currency"),
                    "min_lot_exceeds_risk": raw < acc.get("min_lot", 0.01)}
        except (KeyError, ValueError, IndexError):
            return {"error": "pair, stop, risk and balance are required"}

    def _api_post(self, route, body):
        c = CORE
        if route == "scan":
            pairs = body.get("pairs") or c.cfg["pairs"]
            ok = c.start_scan([p for p in pairs if isinstance(p, str)])
            return self._send(200 if ok else 409, {"started": ok})
        if route == "connect":
            return self._send(200, {"mt5": c.connect(), "error": c.mt5_error})
        if route == "settings":
            allowed = {"account": ("risk_pct", "balance"), "structure": ("swing_atr", "mode"),
                       "aoi": ("cluster_pips",), "ui": ("candles",), "plan": ("stop_min_atr_d",)}
            upd = {s: {k: body[s][k] for k in keys if k in body.get(s, {})} for s, keys in allowed.items() if s in body}
            c.save_settings(upd)
            return self._send(200, {"ok": True})
        if route == "alerts":
            try:
                a = c.add_alert(str(body["pair"]), float(body["price"]), str(body.get("note", ""))[:80])
            except (KeyError, ValueError):
                return self._send(400, {"error": "pair and price are required"})
            return self._send(200, a)
        self._send(404, {"error": "not found"})


def main():
    global CORE
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    CORE = Core()
    CORE.connect()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    url = f"http://127.0.0.1:{a.port}/"
    print(f"TradingGuide terminal at {url}  (MT5 {'connected' if CORE.mt5 else 'not connected: ' + str(CORE.mt5_error)})")
    print("Ctrl+C to stop.")
    if not a.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if CORE.mt5 is not None:
            CORE.mt5.shutdown()


if __name__ == "__main__":
    main()
