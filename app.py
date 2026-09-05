#!/usr/bin/env python3
"""
Mesh & More — local-only holding page server.

Serves the static holding page and accepts lead submissions on
POST /api/lead, appending each lead as a JSON line to
leads/leads.jsonl. No external network calls for lead data.

Run:
    python3 app.py            # serves on http://127.0.0.1:8000
    python3 app.py 8080       # custom port

Stdlib only — no pip install required.
"""

import sys
import json
import os
import re
import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_DIR = os.path.join(BASE_DIR, "leads")
LEADS_FILE = os.path.join(LEADS_DIR, "leads.jsonl")

VALID_JOURNEYS = {"Puglia", "Andalusia", "Dolomites", "Crete", "Undecided"}
VALID_WINDOWS = {"2026-spring", "2026-autumn", "2027", "Flexible"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def save_lead(data: dict) -> bool:
    os.makedirs(LEADS_DIR, exist_ok=True)
    record = {
        "name": str(data.get("name", "")).strip(),
        "email": str(data.get("email", "")).strip(),
        "journey": str(data.get("journey", "")).strip(),
        "window": str(data.get("window", "")).strip(),
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "src": "holding-page",
    }
    with open(LEADS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return True


class Handler(BaseHTTPRequestHandler):
    server_version = "MeshAndMore/1.0"

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            path = "/index.html"
        # map to file under BASE_DIR, prevent traversal
        rel = os.path.normpath(path.lstrip("/"))
        full = os.path.join(BASE_DIR, rel)
        if not full.startswith(BASE_DIR) or not os.path.isfile(full):
            self._send(404, {"error": "not found"}, "application/json")
            return
        ctype = "text/html; charset=utf-8"
        if full.endswith(".css"):
            ctype = "text/css; charset=utf-8"
        elif full.endswith(".js"):
            ctype = "application/javascript; charset=utf-8"
        elif full.endswith(".json"):
            ctype = "application/json; charset=utf-8"
        with open(full, "rb") as f:
            self._send(200, f.read(), ctype)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/lead":
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            data = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            self._send(400, {"ok": False, "error": "invalid json"})
            return

        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        journey = str(data.get("journey", "")).strip()
        window = str(data.get("window", "")).strip()

        if not (name and email and journey and window):
            self._send(400, {"ok": False, "error": "all fields required"})
            return
        if not EMAIL_RE.match(email):
            self._send(400, {"ok": False, "error": "invalid email"})
            return
        if journey not in VALID_JOURNEYS:
            self._send(400, {"ok": False, "error": "invalid journey"})
            return
        if window not in VALID_WINDOWS:
            self._send(400, {"ok": False, "error": "invalid window"})
            return

        try:
            save_lead(data)
        except Exception as e:
            self._send(500, {"ok": False, "error": "could not save lead"})
            return

        self._send(200, {"ok": True, "message": "registered"})

    def log_message(self, fmt, *args):
        sys.stderr.write("[mesh] " + (fmt % args) + "\n")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Mesh & More holding page running at http://127.0.0.1:{port}")
    print(f"Leads are stored locally at: {LEADS_FILE}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
