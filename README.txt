Rackspace Cloud Race - Mac/PC

Fastest way:
1. Unzip this folder.
2. Double-click index.html.
3. Play in Safari or Chrome.

Optional local web server:
1. Double-click RUN_GAME.command.
2. Your browser opens automatically.
3. Keep the Terminal window open while playing.

Controls:
- Left / Right arrows or A / D
- Space or W = jump
- Shift = turbo

Notes:
- No Node.js or npm required.
- The game is fully self-contained.
- Leaderboard resets when the page is refreshed.

Setting:
- A Rackspace-inspired data center with server rows, cooling infrastructure, fiber trunks, maintenance drones, secure cages, and VCF Cloud knowledge nodes.

Controller support:
- Works with standard controllers exposed through the browser Gamepad API.
- Left stick or D-pad: move.
- A / Cross: jump.
- B / Circle, right bumper, or right trigger: turbo.
- Keyboard controls continue to work at the same time.

Story:
- Start in the hyperscaler zone.
- Race through a data center while learning Rackspace VCF Cloud.
- Reach Rackspace Cloud as the finish destination.
- Difficulty increases as you progress.

Display:
- The game now expands to fill the browser window and keeps the play area dominant.

TV / Controller Mode:
- Optimized for a 16:9 widescreen TV.
- All essential actions can be completed with a standard game controller.
- Start screen: D-pad/stick navigates; A/Cross selects.
- Racer presets can be changed with the controller.
- Gameplay: left stick/D-pad moves; A/Cross jumps; B/Circle, RB, or RT activates turbo.
- Menu/Start button pauses and resumes.
- Quiz screens: D-pad/stick selects answers; A/Cross confirms.
- Finish screen: controller can choose the next racer and restart.

TV v10 fixes:
- True single-screen TV layout: body is locked to the visible display and does not page-scroll.
- Controller is polled continuously, including before the race and while quiz screens are open.
- Start screen: Left/Right changes racer; A/Cross starts immediately.
- Quiz: Up/Down (or Left/Right) selects; A/Cross submits.
- Gameplay: D-pad/left stick moves; A/Cross jumps; B/Circle/RB/RT turbos; Menu/Start pauses.

Safari TV mode v11:
- Layout is locked to Safari's measured window.innerHeight/window.innerWidth, with body scrolling disabled.
- All game UI is overlaid inside one TV screen.
- Safari may hide controllers until the first controller button press; press A/Cross once to activate it. That same press is treated as Start when possible.
- Menu confirm accepts any standard face button (0-3) to handle non-standard Safari controller mappings.
- Quiz navigation uses stick/D-pad; any face button confirms.

IMPORTANT FOR SAFARI + CONTROLLER:
1. Use RUN_IN_SAFARI.command instead of double-clicking index.html.
2. This serves the game from localhost and opens Safari.
3. After the page appears, press a controller face button once so Safari exposes the controller to the page.
4. A/Cross starts the race; stick/D-pad chooses quiz answers and any face button confirms.
5. The TV UI is locked to Safari's measured visible window and the page itself cannot scroll.

V12 race rules:
- Checkpoint questions are hard gates. A wrong answer adds 8 seconds, but the racer cannot enter the next zone until the correct answer is selected.
- Leaderboard names are entered only after finishing.
- Controller-only name entry is supported with the on-screen A-Z keyboard. Use D-pad/stick to move and A/Cross to select; choose SUBMIT SCORE to post the run.

Licensing Ghost:
- Appears exactly once per run at a randomized point in the middle of the course.
- Chases the player until it catches them.
- Catching the player pauses the race and displays a short VMware/Broadcom licensing lesson.
- A/Cross, Enter/Space, or the Continue button resumes the race.
- The encounter does not repeat during the same run.

Persistent leaderboard:
- Scores are saved in the browser and remain across refreshes and new runs.
- Use the Clear button, or Y/Triangle from the start screen, to open leaderboard admin.
- Password required to clear scores: RACK.
- The password screen can be fully operated with the controller.
- Clearing the leaderboard removes all saved local scores.

Difficulty:
- The final stage is still the hardest, but has slightly fewer stacked hazards and slower final drones for a more balanced finish.

Docker hosted version:
- Use docker compose up -d --build.
- Shared leaderboard is stored server-side in /data/leaderboard.json.
- Scores are shared across visitors to the same hosted instance.
- After a racer submits their name, the leaderboard is shown immediately.
- Password RACK clears the shared leaderboard.

Soundtrack:
- Includes an original 8-bit/chiptune race theme created for this game.
- Loops during gameplay.
- Music button or M toggles music.
- LB/L1 toggles music from a controller.
- Safari may require a one-time click/keyboard interaction or site autoplay permission before sound can begin.

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


Splash screen / 8-bit theme:
- Full-screen pixel-art Rackspace title screen.
- Start New Game and Leaderboard menu options.
- Controller: D-pad/stick selects, A/Cross confirms.
- Shared leaderboard is viewable before starting a race.
- Retro pixel styling is applied to menus, HUD, and overlays.
