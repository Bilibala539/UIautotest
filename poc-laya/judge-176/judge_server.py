#!/usr/bin/env python3
"""Laya judge service -- typed-decision inference over HTTP (GPU box .176).

POST /predict  {"state": {...}, "questions": {...}, "model": optional}
            -> {"answers": {...}, "meta": {latency_ms, device, repo}}
GET  /health -> {"status", "ready", "device", "repo", "cuda_available"}
Auth: if token.txt exists and is non-empty, requests need header X-Judge-Token.
"""
import json, os, pathlib, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import torch
import laya

PORT = int(os.environ.get("JUDGE_PORT", "8089"))
HERE = pathlib.Path(__file__).resolve().parent
_token_file = HERE / "token.txt"
TOKEN = _token_file.read_text(encoding="utf-8").strip() if _token_file.exists() else None
REPO = os.environ.get("LAYA_REPO", "convaiinnovations/laya-multilingual")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
LOCK = threading.Lock()
AGENT = None

def get_agent():
    global AGENT
    if AGENT is None:
        t0 = time.time()
        try:
            AGENT = laya.load(REPO, device=DEVICE)
        except TypeError:
            AGENT = laya.load(REPO)
        try:
            AGENT.cfg["max_len"] = 2048
        except Exception:
            pass
        # warmup so the first real request is not cold
        try:
            AGENT.predict({"body": "warmup"}, {"ok": {"type": "noul", "instructions": "Is this text non-empty?"}})
        except Exception:
            pass
        print(f"model {REPO} loaded on {DEVICE} in {time.time()-t0:.0f}s", flush=True)
    return AGENT

class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("%s %s" % (self.address_string(), fmt % args), flush=True)

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "ok", "ready": AGENT is not None, "device": DEVICE,
                             "repo": REPO, "cuda_available": torch.cuda.is_available()})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/predict":
            self._json(404, {"error": "not found"}); return
        if TOKEN and self.headers.get("X-Judge-Token") != TOKEN:
            self._json(401, {"error": "bad or missing X-Judge-Token"}); return
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n).decode("utf-8"))
            state, questions = req["state"], req["questions"]
        except Exception as e:
            self._json(400, {"error": "bad request: %r" % (e,)}); return
        t0 = time.time()
        try:
            with LOCK:
                res = get_agent().predict(state, questions)
        except Exception as e:
            self._json(500, {"error": repr(e)}); return
        self._json(200, {"answers": res["answers"],
                         "meta": {"latency_ms": round((time.time() - t0) * 1000, 1),
                                  "device": DEVICE, "repo": REPO}})

if __name__ == "__main__":
    get_agent()
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), H)
    print(f"laya-judge listening on :{PORT} device={DEVICE} token={'on' if TOKEN else 'off'}", flush=True)
    srv.serve_forever()
