"""The local web server: static files, the JSON API shape, and the cross-site guard."""
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import server


class FakeCore:
    """Stands in for Core so the tests need no MT5."""
    mt5 = None
    mt5_error = "test"
    cfg = {"data": {"server_ny_offset_hours": 7}, "display_tz": "Asia/Manila", "pairs": ["EURUSD"],
           "account": {}, "structure": {}, "aoi": {"cluster_pips": 35}, "ui": {}, "plan": {}}
    lock = threading.RLock()
    scan = {"running": False}
    prices, fired = {}, []

    def alert_list(self):
        return []

    def delete_alert(self, aid):
        self.deleted = aid


def start():
    server.CORE = FakeCore()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def call(port, path, method="GET", headers=None, body=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method, headers=headers or {}, data=body)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def test_pages_and_api():
    srv, port = start()
    try:
        code, body = call(port, "/")
        assert code == 200 and b"TradingGuide" in body
        assert call(port, "/vendor/lightweight-charts.standalone.production.js")[0] == 200
        code, body = call(port, "/api/state")
        assert code == 200 and json.loads(body)["mt5"] is False
        assert call(port, "/api/pair/NOPE")[0] == 404
        assert call(port, "/api/candles/EURUSD/XX")[0] == 404
    finally:
        srv.shutdown()


def test_cannot_read_files_outside_web():
    srv, port = start()
    try:
        for p in ("/../server.py", "/..%2fserver.py", "/%2e%2e/server.py"):
            assert call(port, p)[0] == 404
    finally:
        srv.shutdown()


def test_foreign_origin_and_host_are_refused():
    srv, port = start()
    try:
        assert call(port, "/api/state", headers={"Host": "evil.example"})[0] == 403
        assert call(port, "/api/alerts/x", "DELETE", headers={"Origin": "https://evil.example"})[0] == 403
        ok = call(port, "/api/alerts/x", "DELETE", headers={"Origin": f"http://127.0.0.1:{port}"})
        assert ok[0] == 200
    finally:
        srv.shutdown()
