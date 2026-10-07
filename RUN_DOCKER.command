#!/bin/bash
set -e
cd "$(dirname "$0")"
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or is not in PATH."
  echo "Install Docker Desktop, then run this file again."
  read -r -p "Press Enter to close..."
  exit 1
fi

docker compose up -d --build
sleep 1
open "http://localhost:8080"
echo "Rackspace Cloud Race is running at http://localhost:8080"
echo "Shared leaderboard data is stored in the Docker volume rackspace_race_data."
