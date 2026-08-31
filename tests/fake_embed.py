#!/usr/bin/env python3
"""A fake embedding provider on localhost. Deterministic, offline, free.

rate.py talks to any OpenAI-compatible /embeddings endpoint, so the test suite
serves one. Vectors are derived from the text, so the same text always embeds to
the same place and a test can assert an exact distribution.

Usage: python3 fake_embed.py [port]   -> prints the endpoint URL, then serves.
"""
import hashlib
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

DIM = 32


def vector(text):
    """Deterministic pseudo-embedding. Similar strings land near each other."""
    digest = hashlib.sha256(text.lower().encode()).digest()
    base = [(digest[i % len(digest)] - 128) / 128.0 for i in range(DIM)]
    # Let a couple of marker words dominate, so tests can steer similarity.
    for marker, slot in (("exactly", 0), ("not", 1), ("might", 2), ("but", 3)):
        if marker in text.lower():
            base[slot] += 3.0
    return base


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        texts = body["input"]
        texts = [texts] if isinstance(texts, str) else texts
        payload = {"data": [{"index": i, "embedding": vector(t)} for i, t in enumerate(texts)]}
        raw = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *args):
        pass


def serve(port=0):
    server = HTTPServer(("127.0.0.1", port), Handler)
    return server, "http://127.0.0.1:{}/v1/embeddings".format(server.server_port)


if __name__ == "__main__":
    srv, url = serve(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
    print(url, flush=True)
    srv.serve_forever()
