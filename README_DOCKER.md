# Rackspace Cloud Race - Docker

This version hosts the game and a shared leaderboard from one Docker container.

## Fastest start

From this folder:

```bash
docker compose up -d --build
```

Open:

```text
http://localhost:8080
```

To stop it:

```bash
docker compose down
```

The leaderboard is stored in the named Docker volume `rackspace_race_data`, so scores survive container rebuilds and restarts.

## Run without Docker Compose

```bash
docker build -t rackspace-cloud-race .
docker run -d \
  --name rackspace-cloud-race \
  -p 8080:8080 \
  -v rackspace-race-data:/data \
  --restart unless-stopped \
  rackspace-cloud-race
```

Then open `http://localhost:8080`.

## Host it for other people

Run the container on any Docker host and expose port 8080 through your normal reverse proxy/load balancer. For a public deployment, terminate HTTPS at the reverse proxy and proxy traffic to the container on port 8080.

The application needs these routes to reach the same container:

- `/` and `/index.html` - game
- `/api/leaderboard` - shared leaderboard
- `/healthz` - health check

## Leaderboard

- Scores are shared by everyone using the same hosted container/data volume.
- The top 8 times are retained.
- After a racer enters their name, the game immediately displays the leaderboard.
- Clear password defaults to `RACK`.
- To change the password, set `LEADERBOARD_PASSWORD` in `docker-compose.yml` or with `docker run -e`.

## Back up the leaderboard

The persistent data file is `/data/leaderboard.json` inside the container. With Docker Compose it is stored in the `rackspace_race_data` volume.

Audio: the Docker image serves `retro-race-theme.wav`, an original chiptune soundtrack bundled with the game.

Pause leaderboard:
- Press Menu/Start during a race to pause and show the shared leaderboard.
- A/Cross or Menu/Start resumes the race.
- The leaderboard refreshes from the Docker server when the pause screen opens.
- Keyboard fallback: P or Escape toggles the pause leaderboard.
