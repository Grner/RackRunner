#!/bin/bash
cd "$(dirname "$0")"
PORT=8765
while lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; do PORT=$((PORT+1)); done
python3 -m http.server "$PORT" --bind 127.0.0.1 >/tmp/rackspace-cloud-race-http.log 2>&1 &
PID=$!
sleep 1
open -a Safari "http://127.0.0.1:$PORT/index.html"
echo "Rackspace Cloud Race opened in Safari at http://127.0.0.1:$PORT/index.html"
echo "For controller support, press any controller button once after the page appears."
echo "Keep this Terminal window open. Press Control-C to stop the local server."
trap 'kill $PID 2>/dev/null' EXIT INT TERM
wait $PID
