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


Audio fix (v18):
- The Docker image now explicitly copies retro-race-theme.wav into /app/public.
- The race explicitly starts the soundtrack when a run begins.
- Safari audio is primed muted on load and unlocked on the first trusted click/key gesture.
- If Safari still blocks controller-only autoplay, click Enable Music once or set Safari Auto-Play for the site to Allow All Auto-Play.


## v19 title screen

The game now opens on an 8-bit Rackspace-themed splash screen with two controller-friendly choices:

- **Start New Game**
- **Leaderboard**

Use the D-pad or left stick to change the menu selection and A/Cross to confirm. The leaderboard menu reads the same shared server-side scores used during the race. The UI uses an original pixel-art Rackspace treatment and retro styling throughout the game.

Required VCF Cloud quiz question:
- The Facility Entry checkpoint asks which solution provides a fully managed VMware Cloud Foundation environment with scalable, secure private cloud capacity.
- Correct answer: Rackspace VCF Cloud.

## Dedicated leaderboard site

The container now serves a standalone leaderboard at:

```text
http://localhost:8080/leaderboard
```

The page shows the fastest run prominently, including the racer name, run time, and the date/time the score was recorded. Every newly submitted score gets a server-generated UTC timestamp; the browser displays it in the viewer's local time zone.

### Leaderboard admin login

Default credentials for the leaderboard admin section are:

```text
Username: admin
Password: RACK
```

Change these for a hosted deployment in `docker-compose.yml` or through environment variables:

```yaml
LEADERBOARD_ADMIN_USERNAME: admin
LEADERBOARD_PASSWORD: change-this-password
LEADERBOARD_SESSION_HOURS: 8
```

Admin login creates an HTTP-only session cookie. Only an authenticated admin can use the reset control on the dedicated leaderboard site. The older in-game `RACK` reset flow remains compatible.


### Controller jump debounce
- A/Cross now uses a release latch: one physical press produces one jump.
- The button must be released for several frames before another jump can trigger.
- Airborne jump presses are no longer queued and cannot cause an automatic second jump on landing.


## Racer contact details
- Public leaderboard visitors only see racer name, time, and achieved date/time.
- After admin login, racer names become clickable.
- Admins can view/edit Contact Name, Title, Email Address, Company, and Notes.
- Contact fields are stored with the score in the persistent Docker volume but are excluded from the public leaderboard API.
- Resetting the leaderboard also removes the associated contact records.

## v24 Racer Contact Manager
The leaderboard admin UI was rebuilt to make contact management explicit and visible.

1. Open `/leaderboard`.
2. Log in with the admin account.
3. The **Racer Contact Manager** appears automatically. You can also click **MANAGE RACER CONTACTS**.
4. Each racer has a **VIEW / EDIT** button.
5. The button opens a large contact dialog with Contact Name, Title, Email Address, Company, and Notes.
6. Click **SAVE CONTACT DETAILS**.

Contact fields are admin-only. The public leaderboard API does not return them.

Tested in v24:
- leaderboard page serves successfully
- score submission and timestamps
- unauthenticated contact access rejected
- admin login
- private racer list
- individual private racer lookup
- contact save via POST
- saved contact persistence
- public API privacy after contact save
- leaderboard page JavaScript syntax

### CSV export
- After admin login on `/leaderboard`, use **EXPORT CSV** under Admin Controls.
- The export includes rank, racer name, raw and formatted time, hits, achieved date/time, contact name, title, email, company, and notes.
- Contact data remains admin-only; the export button is not shown to public visitors.
- The generated CSV includes a UTF-8 BOM for good compatibility with Excel.


### Easier course balance
- Reduced obstacle density across all six zones.
- Difficulty now ramps gradually instead of adding large clusters of hazards.
- Drones move slower and with less vertical travel.
- Player movement is slightly faster and jumps have more airtime.
- Hazard collision boxes are slightly more forgiving.
- An obstacle hit adds 3 seconds instead of 5 seconds.
- After a hit, the racer respawns nearby instead of at the beginning of the zone.
- A short post-hit grace period prevents immediate repeat collisions.


### Licensing Ghost hold
- When the Licensing Ghost catches the racer, the licensing message is locked on screen for 2 seconds.
- Continue input is disabled during the countdown.
- After 2 seconds, A/Cross, Enter/Space, or the Continue button resumes the race.


### Event-friendly easy mode
- Course difficulty has been reduced significantly across all six stages.
- Only three base hazards appear per stage, with very light additions later.
- Drones are slower and move over a smaller vertical range.
- Elevated platforms are wider and easier to land on.
- Normal movement is faster; jumps are higher with more airtime.
- Hazard collisions use smaller hitboxes.
- Obstacle hits add only 1 second and respawn the racer just before the obstacle.
- One VCF info node per zone is enough to unlock its quiz checkpoint.
- The Licensing Ghost chase is slower, but its 2-second licensing hold remains.
- The home screen now includes a complete How to Play guide.
- After a score is submitted and the leaderboard is shown, Return Home/A-Cross resets the game to the title screen.
