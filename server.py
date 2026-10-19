#!/usr/bin/env python3
import json
import os
import secrets
import threading
import time
from datetime import datetime, timezone
from hmac import compare_digest
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '8080'))
PUBLIC_DIR = Path(os.environ.get('PUBLIC_DIR', '/app/public')).resolve()
DATA_DIR = Path(os.environ.get('DATA_DIR', '/data')).resolve()
DATA_FILE = DATA_DIR / 'leaderboard.json'
ADMIN_USERNAME = os.environ.get('LEADERBOARD_ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('LEADERBOARD_PASSWORD', 'RACK')
ADMIN_SESSION_HOURS = max(1, int(os.environ.get('LEADERBOARD_SESSION_HOURS', '8')))
MAX_SCORES = 8
LOCK = threading.Lock()
SESSIONS = {}

DATA_DIR.mkdir(parents=True, exist_ok=True)


def normalize_timestamp(value):
    if not value:
        return None
    try:
        text = str(value).strip()
        parsed = datetime.fromisoformat(text.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    except Exception:
        return None


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
        clean.append({
            'name': name,
            'time': round(time_value, 3),
            'hits': max(0, hits),
            'achieved_at': normalize_timestamp(item.get('achieved_at')),
        })
    clean.sort(key=lambda x: x['time'])
    return clean[:MAX_SCORES]


def load_scores_unlocked():
    if not DATA_FILE.exists():
        return []
    try:
        return sanitize_scores(json.loads(DATA_FILE.read_text()))
    except Exception:
        return []


def load_scores():
    with LOCK:
        return load_scores_unlocked()


def save_scores_unlocked(scores):
    clean = sanitize_scores(scores)
    tmp = DATA_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(clean, indent=2))
    tmp.replace(DATA_FILE)
    return clean


def cleanup_sessions():
    now = time.time()
    expired = [token for token, expiry in SESSIONS.items() if expiry <= now]
    for token in expired:
        SESSIONS.pop(token, None)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def log_message(self, fmt, *args):
        print(f'{self.address_string()} - {fmt % args}')

    def send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
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

    def admin_token(self):
        cookie_header = self.headers.get('Cookie', '')
        if not cookie_header:
            return None
        try:
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            morsel = cookie.get('race_admin')
            return morsel.value if morsel else None
        except Exception:
            return None

    def is_admin(self):
        cleanup_sessions()
        token = self.admin_token()
        return bool(token and SESSIONS.get(token, 0) > time.time())

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/leaderboard':
            self.send_json(200, load_scores())
            return
        if path == '/api/admin/status':
            self.send_json(200, {'authenticated': self.is_admin(), 'username': ADMIN_USERNAME if self.is_admin() else None})
            return
        if path == '/healthz':
            self.send_json(200, {'ok': True})
            return
        if path in ('/leaderboard', '/leaderboard/'):
            self.path = '/leaderboard.html'
        elif path == '/':
            self.path = '/index.html'
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        data = self.read_json()

        if path == '/api/admin/login':
            username = str(data.get('username', ''))
            password = str(data.get('password', ''))
            if not (compare_digest(username, ADMIN_USERNAME) and compare_digest(password, ADMIN_PASSWORD)):
                self.send_json(401, {'error': 'Invalid username or password'})
                return
            token = secrets.token_urlsafe(32)
            SESSIONS[token] = time.time() + ADMIN_SESSION_HOURS * 3600
            cookie = f'race_admin={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={ADMIN_SESSION_HOURS * 3600}'
            self.send_json(200, {'ok': True, 'username': ADMIN_USERNAME}, {'Set-Cookie': cookie})
            return

        if path == '/api/admin/logout':
            token = self.admin_token()
            if token:
                SESSIONS.pop(token, None)
            self.send_json(200, {'ok': True}, {'Set-Cookie': 'race_admin=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'})
            return

        if path != '/api/leaderboard':
            self.send_json(404, {'error': 'Not found'})
            return

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

        achieved_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        with LOCK:
            current = load_scores_unlocked()
            current.append({
                'name': name,
                'time': time_value,
                'hits': max(0, hits),
                'achieved_at': achieved_at,
            })
            saved = save_scores_unlocked(current)
        self.send_json(201, {'leaderboard': saved, 'achieved_at': achieved_at})

    def do_DELETE(self):
        path = urlparse(self.path).path
        if path != '/api/leaderboard':
            self.send_json(404, {'error': 'Not found'})
            return

        data = self.read_json()
        password_ok = compare_digest(str(data.get('password', '')), ADMIN_PASSWORD)
        if not self.is_admin() and not password_ok:
            self.send_json(403, {'error': 'Admin login required'})
            return

        with LOCK:
            save_scores_unlocked([])
        self.send_json(200, {'ok': True, 'leaderboard': []})


if __name__ == '__main__':
    print(f'Rackspace Cloud Race listening on http://{HOST}:{PORT}')
    print(f'Serving: {PUBLIC_DIR}')
    print(f'Leaderboard page: http://{HOST}:{PORT}/leaderboard')
    print(f'Leaderboard data: {DATA_FILE}')
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
