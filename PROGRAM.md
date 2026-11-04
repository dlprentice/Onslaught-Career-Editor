# Execution Program

Status: durable backlog under David's 2026-10-15 direction
Last updated: 2026-11-04 (Mission project Save as reaches the Linux CE development runtime; isolated playtest checkpoint next)
Summary: the open work, its acceptance gates, and what was closed or paused, without an execution diary.

The [goal](GOAL.md) sets the direction. Toolkit capability claims belong in
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) and its checks in [VALIDATION.md](VALIDATION.md); CE and the Godot
rebuild own their own release and parity evidence. The queue that
ran the Ghidra campaign, the decompilation plan and the rebuild's work items until 2026-10-15 is in Git history;
the campaign's records are in the private historical maintainer archive.

## Cross-project progress and priorities

This is the single cross-project chart. Multiplayer status and the public contributor routes were rechecked
**2026-11-02**; older measurements retain their dates in the linked owners. Verify the owner and current release
before relying on a row.
A development branch is not a released feature. Update the affected row at a
material milestone rather than keeping a second live dashboard in a handoff. The [goal](GOAL.md#how-progress-is-measured)
defines progress and what a completion claim requires.

| Area | Current state and remaining outcome | Detailed owner |
| --- | --- | --- |
| CE release and player experience | Latest public release: 0.1.13 (published 2026-10-31). Its release notes describe shipped changes, checks and limits; physical Windows retesting remains open. Later public contributor setup and documentation corrections are exported. Validate exact packages and updates before shipping. | [0.1.13 release notes](https://github.com/dlprentice/onslaught-ce/releases/tag/v0.1.13), [CE README](https://github.com/dlprentice/onslaught-ce) |
| Reported Windows issues | One reproduced cause of double music is fixed in 0.1.12, with software-VM evidence, and Jeppi reports the audio fixed in 0.1.13 on their own Windows PC (a player's report; no log has been read). 0.1.13 adds changes aimed at the pause-menu mouse, the game clock after Alt-Tab and the system cursor in fullscreen; none has been seen on a real Windows PC. The reporter's physical AMD/input retest, separate stutter and reported graphics artifacts remain open. | [CE releases](https://github.com/dlprentice/onslaught-ce/releases/latest) |
| Online multiplayer | Unreleased multiplayer engineering is not player-ready. The public CE README still lists Internet multiplayer as planned; public 0.1.13 is unchanged. Ordinary in-game host/join, native Windows hosting, independent-machine networks and campaign progression remain acceptance gaps. Deliver independently controlled players, compatible content, reliable session lifecycle and approachable connections, then validate actual networks. | [Multiplayer work below](#onslaught-ce-player-experience-and-online-play), [CE README](https://github.com/dlprentice/onslaught-ce) |
| Campaign co-op and scale | Ordinary-campaign objectives, transitions, deaths, rejoin and safe progression are not established online. Larger matches, maps and Battle Engine customization are later goals. Local split-screen is not online co-op. | [Multiplayer work below](#onslaught-ce-player-experience-and-online-play) |
| Controls, display and guidance | Improve understandable dodge/zoom and free-camera help, controllers, accessible menus, window/display choices and performance while preserving the game's look and feel. Investigate the reported floaty mouse feel in the original game; CE behavior remains unknown. Scale the ordinary full-screen HUD and UI for 4K and other high-resolution displays; split-screen scaling is a separate requirement. Real devices and representative Windows graphics remain acceptance gaps. | [Player experience work below](#onslaught-ce-player-experience-and-online-play), [CE README](https://github.com/dlprentice/onslaught-ce) |
| Level and mission tools | Integrated Toolkit source provides authored mission projects with JSON Save/Open, a 3D placement view and a read-only preview of a linked installed map: sampled terrain, plus models only where a world lists its own. No installed level checked does, so installed maps preview as terrain and markers. CE development source now reads linked projects. The production page's Save as path produced projects that moved one existing level-221 object's X/Y in default Linux CE, independently reproduced; the object's initialization still controls its height. No released CE reads these projects. Existing installed-level mod edits retain bounded Linux acceptance. Terrain editing, source compilation, new playable levels, full mission authoring, human use and native Windows validation remain open; older installed-level project and waypoint candidates remain separate. | [Mission project evidence](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore), [Mission project workflow and limits](companion/OnslaughtToolkit.Godot/README.md#mission-project), [Installed-level workflow](roadmap/companion-level-editor.md#2-what-exists-today), [Remaining candidates](roadmap/companion-level-editor.md#unreleased-editor-candidates) |
| Mods and content catalogue | Released mods override existing files and supply worlds on Linux; Windows remains disabled. The Windows contract candidate awaits integration and native acceptance. The complete mod platform and verified catalogue remain open; catalogue path counts do not establish complete asset coverage. | [CE mods](https://github.com/dlprentice/onslaught-ce#mods-experimental), [Creation scope](#level-and-mission-tools), [Catalogue work](#content-catalogue), [Coverage limits](tools/README.md#catalogue-source-file-coverage) |
| Museum and custom levels | The CE-first museum and levels built from scratch remain goals; no playable museum exists. An initial exhibition may precede catalogue completion, Windows support and retail-compatible export. Full coverage and authoring remain open; existing edited-level comparisons establish bounded cases only. | [Museum and authoring scope](#level-and-mission-tools), [Order after 0.1.13](#order-after-0113), [Level evidence](roadmap/companion-level-editor.md#3-what-the-measurements-say-2026-10-29-level-100-the-read-only-retail-view) |
| Commander | CE 0.1.13 ships an opt-in, experimental commander map that pauses the battle and lets the player order squads. Development source not yet in CE's public export or a release adds a live 3D strategic view. On one level, under synthetic input and against matched runs without an order, Move, Advance and Fall back given on the map took one tank squad to the ordered place and Hold stopped it; a longer Move stalled partway, for a reason not yet found. Prove the optional real-time 3D commander works, including in controlled test scenarios, while protecting ordinary play. Its RTS direction includes selecting buildings to construct units and maps of its own; playing as any controllable unit is a separate optional goal. Final availability and placement remain flexible; physical input, other levels and units, native Windows runs, usability and eventual multiplayer still need validation. | [Goal](GOAL.md), [Mission-editor direction](roadmap/companion-mission-editor.md#optional-modes-and-ordinary-play), [CE commander map](https://github.com/dlprentice/onslaught-ce#commander-map-experimental) |
| Godot rebuild | Selected recorded level-100 comparisons exist; complete gameplay, audio and presentation parity and a finished playable replacement are not established. HD assets and expanded gameplay follow a faithful baseline. | [Godot parity record](https://github.com/dlprentice/onslaught-godot/blob/main/rebuild/PARITY.md) |
| Decompilation and baseline | The private mapped-function check uses a disclosed one-byte compiled-object concession; without it one mapped function remains unmatched. Stand-ins and full linked/runtime equivalence remain separate work. The corrected public [overview](https://github.com/dlprentice/onslaught-decomp/blob/9169f28862ebda0b768cbcc7ec354734af013f5e/README.md#L14-L18) and [score-write documentation](https://github.com/dlprentice/onslaught-decomp/blob/9169f28862ebda0b768cbcc7ec354734af013f5e/tools/README.md#L7-L10) are exported. | [Public decompilation](https://github.com/dlprentice/onslaught-decomp) |
| Companion | CE/original careers, settings and backups exist with bounded tests. Broader Windows UI/device acceptance, listening and safe release remain. | [Companion README](companion/OnslaughtToolkit.Godot/README.md), [acceptance below](#companion--ce-integration) |
| Diagnostics and recording | Useful bounded logs and manual, informed reporting are available. Preserve faithful reference tapes and develop separate coverage for CE features and controller input; avoid telemetry or automatic uploads. | [CE reporting guidance](https://github.com/dlprentice/onslaught-ce#report-a-problem) |
| Special Thanks | Stuart Gillam, Jeppi and BermudaMaster are acknowledged in 0.1.12. Keep acknowledgements accurate as further contributors are identified. | [CE credits](https://github.com/dlprentice/onslaught-ce#credits-and-special-thanks) |
| Documentation, repositories and recovery | Public setup and contribution workflows are published. Owner reconciliation and indexing of retained evidence and handoffs remain open. The verified restore covers one selected snapshot; restoration of the full corpus and recovery on a replacement machine remain unproven. | [Contributor workflow](CONTRIBUTING.md), [Recovery scope](#recovery-and-repository), [Project index](PROJECT-INDEX.md) |
| Showcase and website | The requested port footage has not met its brief and may resume with the next lead. The domain is owned; no website deployment is currently required. | Maintainer direction |

### Order after 0.1.13

Player experience and online co-op remain priorities. All lanes below remain requested outcomes; development will
determine how their capabilities fit 0.2. Prove editors, Commander and other features work, including in controlled
test scenarios, without forcing them into ordinary campaign play. Preserve useful gameplay and quality-of-life
improvements. Availability, product placement and packaging may change as development progresses; the order below
tracks dependencies, not dates.

The next delivery is a local **0.1.99 playtest checkpoint**, not a public release or completion of 0.2. Finish and
independently review the interrupted lanes already in progress, integrate what passes, and prepare CE and the
Companion with one short guide. Back up the normal CE user folder first; the checkpoint uses a separate user folder
and passes offscreen smoke checks before handoff. Then wait for David's feedback. The next Windows online gate and
bounded Internet pilot follow that checkpoint unless he changes the order. Keep broader outcomes below in scope.

1. Online co-op for two players on the shipped route: validate Windows hosting, the Windows guest rows and controls, message pages and a played win reaching the career writer. Windows hosting, a played win and Internet play remain unproven. Then more of it: every multiplayer map and versus over the network, three or four players (a lockstep design change) and play across the Internet without manual port forwarding.
2. The split-screen gamepad layer: a pad for each player in ordinary two-player split screen, with the menus and pause, and with faithful modes and recordings kept as retail. It comes first of the input lanes because the next lane uses it.
3. Prove Commander works and decide its availability and placement as development progresses: gamepad control, the cases not yet covered, a Windows case and a co-op commander seat. Commander design should explore a Battle Engine pilot who can issue battlefield orders and an optional dedicated commander role; these are future proposals, not implemented roles. The team commander role is optional: an eligible player may take a vacant team role and step down, and teammates, including the commander, may vote to remove them; a tie does not remove them. The proposed recall requires a majority of eligible team members, with eligibility, timeouts and disconnections to be defined. The commander role and its voting are proposed, not implemented. AI-controlled Battle Engines and expanded unit AI are planned; reuse of suitable existing unit behavior is to be explored, and no new AI behavior is claimed as implemented.
4. The remaining player-experience lanes: the CE Settings page as a table (pad navigation, a Windows run), a split-screen HUD scale per viewport (off in faithful modes), the fix for the crash on Retry in levels whose static shadows are bound to things that cannot hold one, the second phase of the sharper UI art, and launcher polish (a prompt that fits 1,280 pixels, a calmer line when a signature does not match). A future unified CE entry should make Play, Create and Multiplayer discoverable, with Create able to open the separate Companion. For 0.2 releases, bundle useful Companion and editor tools with CE or make them readily accessible alongside it when ready; decide the packaging and entry points and verify what each release provides.
5. The post-release review of every Onslaught repository: stale documents and how the products describe each other.
6. Mods toward the platform David describes: Windows support for the existing world-mod route first (without it, a custom level reaches only Linux players), then replacing any asset, then adding content and a scripting interface, each designed before it is built; the approved 3D map and mission editor work, with prototypes and independent work proceeding where their dependencies allow. The tools that replace walker meshes continue with chains, bounds, skeletal and camera parts and skinned meshes. Independent CE-native authoring may progress in parallel.
7. Done 2026-10-30, ahead of this order at David's request: CE ran editor changes in the bounded cases documented in the [level editor plan](roadmap/companion-level-editor.md). A comparison with the original is recorded privately and does not establish complete equivalence. Next, a writer that builds a level from scratch (terrain, world and mission), whose first targets are a two-unit test level that CE runs and the museum world, walked or flown around in the Battle Engine. Retail-compatible test levels are optional where useful.
8. The content catalogue to a complete inventory (every model, texture and image, used or not), alongside the museum's art boards, turntables, lighting, signs and a main-menu entry. The first CE exhibition can progress in parallel with catalogue work.
9. Level and mission authoring from scratch: custom levels for players and small test levels that CE can run; the editors' remaining work and their acceptance in CE, with optional retail-compatible test levels where useful.
10. The Companion's Windows acceptance: release invocation, input, dialogs, rendering and its UI as validation cases.
11. Windows validation of every lane before release, the release path's own script, and the reported Windows issues retested on real hardware.
12. The decompilation's last unmatched function and the Godot rebuild continue alongside as separate products, not part of the CE package.

## Open work

### Godot rebuild

The rebuild's work queue, milestones and measured parity are kept in
[onslaught-godot](https://github.com/dlprentice/onslaught-godot), where it is developed; `rebuild/` here is a frozen
copy.

### Companion — CE integration

The companion is a C# application built in code on Godot 4.8 beta1 .NET and .NET 10, and organised around players: careers
with a campaign map, Goodies, career editing, cheats, game settings, automatic backups that can be put back, music
and voices, and lore (see its [README](companion/OnslaughtToolkit.Godot/README.md)). Every write into the game is a
choice made after a verified backup, never while the game runs.
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore) records
what is proven. Players can choose the original game or CE, manage careers and backups, and use CE's two supported
launcher settings and the steps for updating CE (the companion contacts nothing). The CE launcher checks its own signed
feed and installs an update only when the player chooses Update.

Public contributor setup is implemented. A fresh anonymous public clone installed verified official tools,
compiled the Companion and passed its authored runtime gate without maintainer files or game data on 2026-11-02.
The [setup guide](companion/OnslaughtToolkit.Godot/README.md#build-test-capture-run-and-export) and
[validation record](VALIDATION.md#public-companion-setup--november-2) own the commands and measured scope.

Remaining acceptance and release work:

- Complete Windows UI acceptance. A [selected native Windows development workflow](VALIDATION.md#companion-native-windows-development-ui--october-25)
  exercised production-page actions and its screenshots were inspected; ordinary release invocation, physical input,
  file dialogs, hardware rendering and broader UI coverage remain open. The [Linux acceptance](VALIDATION.md#companion-with-real-onslaught-ce--october-24)
  uses the real CE launcher, protected edits and the game's own Load menu. Separate
  [native Windows checks](companion/OnslaughtToolkit.NativeChecks/README.md) cover production file/settings writes,
  real-process refusal, and CE loading the edited Unicode career. None is full campaign acceptance.
- Resolve the intermittent Windows launcher-version timeout: a reproduced failure waits in loader startup
  opening SDL3.dll, before the launcher's own version handling. The independently reproduced redirected-output
  defect is corrected in CE 0.1.5; it does not explain this separate startup wait.
- A human click-through and listening to the music and voices. See the companion README for the pinned source
  contract, backup scope and other limits. Public release remains at David's direction.

Any future media replacement would be a CE option (for example a CE user-data override folder), not a file swap
in an install.

Keep the companion's application code, the rebuild and private retail data separate. Beyond launching and managing
Onslaught CE, no store, account or community features are planned.

### Onslaught CE player experience and online play

Prioritize real player reports and a reliable corrective release while keeping the faithful reference path separate.
Fix reproduced retail bugs and improve performance while preserving the game's look and feel. Investigate the report
of floaty mouse input in the original game; CE behavior is unknown. Reproduce the report and compare the original
and CE with matched input, frame timing and display conditions before choosing a correction; no mouse fix is claimed.
Check actual release packages on each claimed platform, and distinguish an authored fixture, Wine, a software-rendered
VM and representative physical hardware. Confirm that controls and features are accessible in-game and that errors
help players act. Make planned menu options discoverable with honest disabled or coming-soon states, and pursue live
display changes where feasible instead of silently requiring a restart. Verify the developer console, cheats, free
camera and tutorial guidance rather than inferring that all paths work. Keep faithful reference tape and replay behavior
while developing a separate way to record and
validate CE enhancements and controller input. More logging must remain bounded, non-admin and user-controlled; do
not add telemetry or automatic report uploads.

For the reported Windows issues, Jeppi identified the screenshot as the tutorial map; a separate log records a Blackout
session but does not establish the screenshot's level or cause. Training and Blackout are comparison cases. Verify whether
his reported fly mode was aircraft flight or the detached/free camera, then compare that view with retail and the port;
distinguish software rendering from physical hardware and do not claim the reporter's AMD symptoms fixed without evidence.

For multiplayer, progress in dependency order: two independent players with their own input, viewpoint, HUD and audio;
complete host/join and session failure handling; Linux and native Windows in both host roles across actual networks;
then tutorial/early-campaign co-op, save-safe progression and broader campaign coverage. Validate compatibility,
latency, loss, disconnects and rejoin. Versus and skirmish are also goals. Larger player counts, custom maps and
Battle Engine customization must not be claimed as available merely because a protocol or menu anticipates them.
Do not assume a transport, paid service, new recipient or cross-platform determinism without evidence and authorization.

The intended menu is **Multiplayer → Local or Online**. Local should clearly distinguish split-screen from
local-network play. Online should offer a browser of available public lobbies and options to create or join public
and private lobbies, including a private invite/join path. Voice and text chat are planned multiplayer workflows,
with design and validation still open. Optional LAN discovery plus an online directory and relay is one preliminary
connection design, with initial game admission limited to two players. Cloudflare TURN is selected for relay
experimentation within the approved scope. Public lobby discovery and admission/broker hosting remain unselected;
their operators, recipients, information sent and data handling still need design. These experiments do not establish
a shipped CE multiplayer service or player-ready automatic connections. Private lobby access controls must be
designed and validated: being unlisted alone does not establish private access.

The older [original-binary feasibility note](roadmap/original-binary-online-multiplayer-feasibility.md) concerns a
separate historical route, not a statement that CE already has online play.

Multiplayer engineering results remain separate from public source and release acceptance. The
[published CE README](https://github.com/dlprentice/onslaught-ce/blob/bb4fa1f899db0d1826216b89a59c50781bb9cc9b/README.md#L721-L722)
lists Internet multiplayer as planned. Player-ready in-game host/join, native Windows hosting, two physical machines
across actual networks, a played campaign win and real-device controls still need acceptance; bandwidth requirements
still need measurement. The public release remains 0.1.13. The full program remains in scope; availability, placement
and packaging for 0.2 remain flexible.

### Level and mission tools

The creation target is a modern CE-native project format and custom gameplay. Original-game export is useful where
practical but is not a prerequisite; the existing campaign's faithful baseline remains separate. The integrated
[Mission project page](companion/OnslaughtToolkit.Godot/README.md#mission-project) creates an authored editor
document with placements, preserved source text and source links, saved and reopened as `.ceproject` JSON. Its 3D
view starts as a flat placement plane with markers, with orbit, zoom, drag and undo. A placement can be bound to one
named object of an installed level, and that level loaded as a read-only preview of sampled terrain and of the static
models its world lists. Base-world objects stay where the map puts them, and a name only the base world has, or that
two objects of the level share, is refused, following CE's project loader. No installed level checked lists models of
its own, so an installed map previews as terrain and markers, and resolving installed objects' models is not
implemented; the geometry seen so far comes from an authored scene. The page edits no terrain and has no source
compilation or new playable-level export. CE development source now reads linked projects. On 2026-11-03, projects
saved through the production page's Save as path moved one existing object's X/Y on level 221 in default Linux CE;
an independent review reproduced the path. The object initializes its own height, so stored Z is not a promise of
runtime height. These checks use programmatic page signals, not human dialog or drag input, and establish neither
Windows nor network-build behavior, mission completion or general object support. No released CE reads these
projects. The [capability record](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore)
owns the measured scope; the full format, authoring and runtime goals remain open.

David's mod-platform direction (2026-10-30) is to replace any model, texture, sound, music or text; add units, levels
and missions; and provide a scripting interface for new rules and modes, up to whole new games built inside CE.
Safe authoring and compatibility, complete content coverage and HD successors remain open.

The Companion's Level editor can inspect and move placed objects (typed, dragged on the map or nudged with the arrow keys), list only the moved ones, copy a unit (appended after every row so existing row, path and target indices do not shift; the copy retains its script and target), show a map and mission scripts, and edit a script's
source (compile it, make the level use it, undo it); it saves changed world files as new CE mods and starts CE at the open level with the changes in a temporary folder of its own (its Play button). The page is covered by
tests and offscreen captures on Linux; a script edit, a unit copy and two moved Target Tanks were staged by it and run in CE on Linux (section 16 of the mission
editor design and the level editor plan); nobody has used it by hand, and the mod does not preserve the edited source beside the world file. The [older installed-level candidates](roadmap/companion-level-editor.md#unreleased-editor-candidates)
record their scope separately from the new authored-project workflow. Installed-level world/terrain project Save/Open,
script-draft restoration and the waypoint-check workflow remain outside that integration. The [level editor plan](roadmap/companion-level-editor.md)
and [mission editor design](roadmap/companion-mission-editor.md) own their remaining gates, including source-preserving
staging, hand use and gameplay acceptance. CE's released world-mod route remains Linux-only. A pushed Windows
candidate constrains mod opens to read-only access and adds contract fixtures for fallback to the installed base
through MMIO; it remains outside main and public export, and native Windows mod loading is unproven.

The museum and custom-level direction was approved on 2026-10-31. The museum should be a self-guided world built
from scratch and reached from the main menu, displaying every unit and model, inert, for exploration on foot or in
flight in the Battle Engine. It should show the game's art on boards, with turntables, lighting and signs. The art
comes from the player's own installation and is never shipped. A small CE-first exhibition can progress before
catalogue completion, suitable Windows support or original-game-compatible output. Full museum coverage still needs
a complete catalogue, level authoring and suitable CE support on Windows and for boards, turntables, lighting and
signs. Protect the original campaign's expected behavior with regression tests while allowing documented bug fixes
and improvements. Small test levels runnable in both the original and CE remain optional where a direct comparison
is useful. Existing CE edit runs and the bounded comparison with the original do not establish complete equivalence;
the [level editor plan](roadmap/companion-level-editor.md) owns the CE runs' measured scope.

### Game documentation — ongoing

Write what the decompilation establishes as prose and specs in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation),
the one home of the game documentation, citing functions rather than quoting code;
[`reverse-engineering/`](reverse-engineering/RE-INDEX.md) here is a frozen copy. The companion's CE work (careers,
settings, launch) is the next consumer. Sections whose decompiler listings moved to the private archive on 2026-10-15 keep a pointer and,
where needed, a short summary; a fuller prose description is welcome wherever a reader needs one.

### Content catalogue

An evidence-based inventory of the game's content (textures, meshes, animations, sound, music, films, levels,
scripts, effects, interface art) with JSON metadata, as the basis for HD successors, modding, editors, multiplayer
compatibility and the rebuild. `tools/content_catalog.py` (schema `tools/content_catalog.schema.json`) surveys a
selected install and catalogues the families existing parsers read; every relationship names the loader function or
data that establishes it, and meshes and textures carry a usage summary for HD prioritisation. Its output is
retail-derived and stays in ignored `local-data/`. The `WRES` world bodies (every thing, waypoint path and compiled
mission script, with what the scripts' literal arguments name), the `ERES`, `SURF`, `SSHD`, `VSDS`, `PMIB` and `DMKR`
payloads, the
`sprintf`-built sky, water, detail and HUD texture names and the registry of named things (`WORLD.mNamedThings`:
which things are predicted to join on load and in which order, so a script's thing name has a source-modelled lookup;
`tools/named_things.py`, with the retail gate `tools/content_catalog_gate.py`), the battle engine configurations (with
the weapons, explosion, cockpit and description each names, and the levels that offer each) and the `sounds.sfx`
effects (with their chains and the bank samples they play; `tools/game_tables_decode.py`) are decoded in their
loaders' order. Next: the physics definitions' other fields (the sound effects, particles and HUD icons they name). A
catalogue is a foundation, not the mod system or an HD conversion.

### Decompilation and native port

The maintainer's private byte-matching check matches every mapped game function with a guarded one-byte
correction to a compiled object; without the correction, one function remains unmatched. Its public export,
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), records its own coverage with that concession,
explains the DirectX sample files it leaves out, and documents its divergences.
The function matches do not by themselves establish complete behavioural equivalence or a byte-identical linked
executable. Its native source port (Windows and Linux) is published as
[Onslaught CE](https://github.com/dlprentice/onslaught-ce) (GPL-3.0-only source and binaries, no game files). Nothing
from either is copied into this repository.
Concession-free matching remains open: one mapped function still needs the guarded object-code correction.

### Recovery and repository

Keep an inventory of unique source, evidence, saves and necessary recovery material; verify selected off-site restores
and eventually rehearse recovery on a replacement machine. Reuse existing backups and deduplicate rather than repeatedly
uploading large unchanged collections. Keep private paths, credentials and signing keys out of tracked files. Selected
restores are not proof that the full corpus or current worktrees can be recovered.

On 2026-11-01, a selected review-evidence delta was restored with a fresh cache: the exact 77-file set,
8,466,420 bytes, matched every recorded file hash. The private verification receipt
`ROOT-RESTORE-VERIFIED.private.json` has SHA-256
`2499c8105365440c626a2b0d92d71e9c8ba9243039fc1d65ad02c0da994a3fa3` and records that the original inputs were unchanged.
This establishes only the selected snapshot; it does not cover work created afterward. Full-corpus and replacement-machine recovery remain open.

- The public history was flattened to a single new root (approved by David); the full earlier history is a
  verified bundle and `refs/old/*` in the private RE archive. The third-party fork and GitHub's pull-request refs
  still hold the old history; whether to ask GitHub Support to purge the PR refs is David's decision.
- The split: the Godot rebuild is developed in [onslaught-godot](https://github.com/dlprentice/onslaught-godot) (the `rebuild/` copy here is frozen), and
  the game documentation is published as [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation). Still to come: this repository's
  full history is bundled into the private RE archive and flattened again, and the repository is renamed
  onslaught-companion. Each step is a separate, coordinated task.

## Paused

- **The earlier fixed-point rebuild's queue** (Core/Client/Godot, paused 2026-10-15 when the rebuild restarted around
  the parity core): World 110 generalization (former P7) and player-input replay tapes (former P8). Its final state is
  described in [rebuild/README.md](rebuild/README.md#the-earlier-rebuild-history). That historical queue was scoped to
  level 100; the current and longer-term rebuild goals are in [GOAL.md](GOAL.md).

## Closed

| Item | Outcome |
| --- | --- |
| Retail RE by Ghidra campaign (generations, contracts, promotion cohorts, record audit) | Superseded by the byte-matching decompilation; records in the private RE archive. |
| Private decompilation matching measurement | 5,482/5,482 mapped functions match with the guarded one-byte correction; one remains unmatched without it. The published [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) reproduces 5,449, with that concession. |
| WinUI toolkit, its UI tests and CLI (former P11) | Removed 2026-10-15; the companion replaced them. |
| Campaign bookkeeping relief (former P6) | Retired with the campaign. |
| Repository preparation (former P12) | The maintainer's checkout lives on a separate archive drive; `local-lab/` and `local-data/` are real ignored children. The 2026-10-15 cleanup moved the Ghidra checkpoint and RE machinery to the private archive and removed the WinUI surfaces. |
