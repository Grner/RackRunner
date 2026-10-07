#!/usr/bin/env python3
import json
import os
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '8080'))
PUBLIC_DIR = Path(os.environ.get('PUBLIC_DIR', '/app/public')).resolve()
DATA_DIR = Path(os.environ.get('DATA_DIR', '/data')).resolve()
DATA_FILE = DATA_DIR / 'leaderboard.json'
CLEAR_PASSWORD = os.environ.get('LEADERBOARD_PASSWORD', 'RACK')
MAX_SCORES = 8
LOCK = threading.Lock()

DATA_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_scores(raw):
    clean = []
    if not isinstance(raw, list):
        return clean
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = str(item.get('name', '')).strip()[:18]
        try:
            time_value = float(item.get('time', 0))
            hits = int(item.get('hits', 0))
        except (TypeError, ValueError):
            continue
        if not name or time_value <= 0 or time_value > 36000:
            continue
        clean.append({'name': name, 'time': round(time_value, 3), 'hits': max(0, hits)})
    clean.sort(key=lambda x: x['time'])
    return clean[:MAX_SCORES]


def load_scores():
    with LOCK:
        if not DATA_FILE.exists():
            return []
        try:
            return sanitize_scores(json.loads(DATA_FILE.read_text()))
        except Exception:
            return []


def save_scores(scores):
    clean = sanitize_scores(scores)
    tmp = DATA_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(clean, indent=2))
    tmp.replace(DATA_FILE)
    return clean


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def log_message(self, fmt, *args):
        print(f'{self.address_string()} - {fmt % args}')

    def send_json(self, status, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > 10000:
                return {}
            return json.loads(self.rfile.read(length).decode('utf-8'))
        except Exception:
            return {}

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/leaderboard':
            self.send_json(200, load_scores())
            return
        if path == '/healthz':
            self.send_json(200, {'ok': True})
            return
        if path == '/':
            self.path = '/index.html'
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path != '/api/leaderboard':
            self.send_json(404, {'error': 'Not found'})
            return
        data = self.read_json()
        name = str(data.get('name', '')).strip()[:18]
        try:
            time_value = float(data.get('time'))
            hits = int(data.get('hits', 0))
        except (TypeError, ValueError):
            self.send_json(400, {'error': 'Invalid score'})
            return
        if not name or time_value <= 0 or time_value > 36000:
            self.send_json(400, {'error': 'Invalid score'})
            return
        with LOCK:
            current = []
            if DATA_FILE.exists():
                try:
                    current = sanitize_scores(json.loads(DATA_FILE.read_text()))
                except Exception:
                    current = []
            current.append({'name': name, 'time': time_value, 'hits': max(0, hits)})
            saved = save_scores_unlocked(current)
        self.send_json(201, {'leaderboard': saved})

    def do_DELETE(self):
        path = urlparse(self.path).path
        if path != '/api/leaderboard':
            self.send_json(404, {'error': 'Not found'})
            return
        data = self.read_json()
        if str(data.get('password', '')) != CLEAR_PASSWORD:
            self.send_json(403, {'error': 'Incorrect password'})
            return
        with LOCK:
            save_scores_unlocked([])
        self.send_json(200, {'ok': True, 'leaderboard': []})


def save_scores_unlocked(scores):
    clean = sanitize_scores(scores)
    tmp = DATA_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(clean, indent=2))
    tmp.replace(DATA_FILE)
    return clean


if __name__ == '__main__':
    print(f'Rackspace Cloud Race listening on http://{HOST}:{PORT}')
    print(f'Serving: {PUBLIC_DIR}')
    print(f'Leaderboard data: {DATA_FILE}')
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
