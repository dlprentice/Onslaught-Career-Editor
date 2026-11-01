# Execution Program

Status: durable backlog under David's 2026-10-15 direction
Last updated: 2026-10-31 (museum approved; 3D editor and commander direction clarified)
Summary: the open work, its acceptance gates, and what was closed or paused, without an execution diary.

The [goal](GOAL.md) sets the direction. Toolkit capability claims belong in
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) and its checks in [VALIDATION.md](VALIDATION.md); CE and the Godot
rebuild own their own release and parity evidence. The queue that
ran the Ghidra campaign, the decompilation plan and the rebuild's work items until 2026-10-15 is in Git history;
the campaign's records are in the private `dlprentice/onslaught-re-archive`.

## Cross-project progress and priorities

This is the single cross-project chart. Snapshot checked **2026-10-31, 02:16 ET**; verify the linked owner and current
release before relying on it. A development branch is not a released feature. Update the affected row at a
material milestone rather than keeping a second live dashboard in a handoff. The [goal](GOAL.md#how-progress-is-measured)
defines progress and what a completion claim requires.

| Area | Current state and remaining outcome | Detailed owner |
| --- | --- | --- |
| CE release and player experience | 0.1.13 is the latest public release (published 2026-10-31). It adds Bonus Levels, CE Settings and Help & Info to the Onslaught CE menu page, a Photo Mode row in the pause menu, changes aimed at a Windows player's reports (the pause-menu mouse, the game clock after Alt-Tab, the system cursor in fullscreen) and puts the single-player HUD in the screen's corners on wide screens. Release-candidate checks, a read-back of the published release and a Linux live-update check from 0.1.12 passed; the Windows changes have not been seen on a real Windows PC. Documentation corrections made after its export await the next public export. Validate exact Linux and Windows packages and updates before shipping. | [CE releases](https://github.com/dlprentice/onslaught-ce/releases/latest), [CE README](https://github.com/dlprentice/onslaught-ce) |
| Reported Windows issues | One reproduced cause of double music is fixed in 0.1.12, with software-VM evidence, and Jeppi reports the audio fixed in 0.1.13 on their own Windows PC (a player's report; no log has been read). 0.1.13 adds changes aimed at the pause-menu mouse, the game clock after Alt-Tab and the system cursor in fullscreen; none has been seen on a real Windows PC. The reporter's physical AMD/input retest, separate stutter and reported graphics artifacts remain open. | [CE releases](https://github.com/dlprentice/onslaught-ce/releases/latest) |
| Online multiplayer | Experimental two-process work is not player-ready. Deliver independently controlled players, compatible content, reliable session lifecycle and approachable connections across Linux and Windows, then validate actual networks. | [Multiplayer work below](#onslaught-ce-player-experience-and-online-play), [CE README](https://github.com/dlprentice/onslaught-ce) |
| Campaign co-op and scale | Ordinary-campaign objectives, transitions, deaths, rejoin and safe progression are not established online. Larger matches, maps and Battle Engine customization are later goals. Local split-screen is not online co-op. | [Multiplayer work below](#onslaught-ce-player-experience-and-online-play) |
| Controls, display and guidance | Improve understandable dodge/zoom and free-camera help, controllers, accessible menus, window/display choices, 4K HUD and performance. Real devices and representative Windows graphics remain acceptance gaps. | [CE README](https://github.com/dlprentice/onslaught-ce) |
| Level and mission tools | The Level editor supports limited inspection and object movement into a CE mod. A compiler and edit model exist; player-facing 3D map and mission editors, source-preserving staging and full authoring remain unfinished. | [Level plan](roadmap/companion-level-editor.md), [mission plan](roadmap/companion-mission-editor.md) |
| Mods and content catalogue | Mods mean a platform (David, 2026-10-30): replace any model, texture, sound, music or text; add units, levels and missions; a scripting interface for new rules and modes, up to whole new games built inside CE. Today's experimental CE mods are world-file overrides on Linux. Windows mod support, safe authoring/compatibility, a complete verified content inventory and HD successors remain. The coverage report distinguishes represented logical paths, relationship targets and unrecorded parse status; it does not establish a complete asset inventory. | [CE README](https://github.com/dlprentice/onslaught-ce), [catalogue work below](#content-catalogue) |
| Museum and custom levels | A small CE-first exhibition room may be developed before the catalogue is complete, generic Windows mod support, or retail-compatible output; broader asset coverage and Windows support remain separate goals. Approved direction (David, 2026-10-31), nothing built. A self-guided museum built as its own world from scratch and reached from the main menu: every unit and model on display and inert, approached on foot or in flight in the Battle Engine, with the game's art on boards, turntables, lighting and signs. Beside it, small custom test levels that both the original and CE can run, so their behaviour can be compared exactly. ultimately needs a complete content catalogue, Windows mods, new CE object types (art board, turntable, sign) and level authoring; the art is read from the player's own install and never shipped, and the original levels keep playing with expected behavior protected by regression tests, while allowing documented bug fixes and improvements. Measured 2026-10-30: the original runs a level the Level editor changed, through an archive copy built locally from the player's own install, and CE runs the same change identically (every probe equal through a recorded input to Present 3,600); a level number the PC game lacks runs in both. David approved the museum and custom-level direction on 2026-10-31; the recorded estimates were: about six working days to a two-unit test level both games run, six to nine weeks to the museum. | [Order after 0.1.13](#order-after-0113) |
| Commander | A limited development foundation exists. A usable real-time 3D tactical commander, including eventual multiplayer, remains to be validated and delivered. | [Goal](GOAL.md), [CE](https://github.com/dlprentice/onslaught-ce) |
| Godot rebuild | Selected recorded level-100 comparisons exist; complete gameplay, audio and presentation parity and a finished playable replacement are not established. HD assets and expanded gameplay follow a faithful baseline. | [Godot parity record](https://github.com/dlprentice/onslaught-godot/blob/main/rebuild/PARITY.md) |
| Decompilation and baseline | The private mapped-function check uses a disclosed one-byte compiled-object concession; without it one mapped function remains unmatched. Stand-ins and full linked/runtime equivalence remain separate work. A correction to the public overview and score-write documentation is prepared in private source and awaits export. | [Public decompilation](https://github.com/dlprentice/onslaught-decomp) |
| Companion | CE/original careers, settings and backups exist with bounded tests. Broader Windows UI/device acceptance, listening and safe release remain. | [Companion README](companion/OnslaughtToolkit.Godot/README.md), [acceptance below](#companion--ce-integration) |
| Diagnostics and recording | Useful bounded logs and manual, informed reporting are available. Preserve faithful reference tapes and develop separate coverage for CE features and controller input; avoid telemetry or automatic uploads. | [CE reporting guidance](https://github.com/dlprentice/onslaught-ce#report-a-problem) |
| Special Thanks | Stuart Gillam, Jeppi and BermudaMaster are acknowledged in 0.1.12. Keep acknowledgements accurate as further contributors are identified. | [CE credits](https://github.com/dlprentice/onslaught-ce#credits-and-special-thanks) |
| Documentation, repositories and recovery | Reconcile the active owners and retained handoffs. Selected off-site data has been restored and checked; some restored sets still need discoverable index entries. Full corpus and replacement-machine recovery remain unproven. Private recovery details stay in private records. | [Project index](PROJECT-INDEX.md), repository guides |
| Showcase and website | The requested port footage has not met its brief and may resume with the next lead. The domain is owned; no website deployment is currently required. | Maintainer direction |

### Order after 0.1.13

David's direction (2026-10-30): what players see comes first, so 0.1.13 and then the experimental online co-op release lead. His direction of 2026-10-31: everything in progress is to be finished properly and included in 0.2.0, with no hurry to ship it. **0.2.0 carries all of the lanes below.** They run in parallel where they do not wait on each other, and the order is the order of dependence. It is a plan, not a set of dates.

1. Online co-op for two players on the shipped route: the first native Windows runs, then every row and control on the Windows guest, the Windows message pages and a played win reaching the career writer. Then more of it: every multiplayer map and versus over the network, three or four players (a lockstep design change) and play across the Internet without manual port forwarding.
2. The split-screen gamepad layer: a pad for each player in ordinary two-player split screen, with the menus and pause, and with faithful modes and recordings kept as retail. It comes first of the input lanes because the next lane uses it.
3. Commander on the merged main: gamepad control, the cases not yet covered, a Windows case and a co-op commander seat. Commander design should explore a Battle Engine pilot who can issue battlefield orders and an optional dedicated commander role; these are future proposals, not implemented roles. The team commander role is optional: an eligible player may take a vacant team role and step down, and teammates, including the commander, may vote to remove them; a tie does not remove them. Commander voting and commander AI remain planned, not implemented.
4. The remaining player-experience lanes: the CE Settings page as a table (pad navigation, a Windows run), a split-screen HUD scale per viewport (off in faithful modes), the fix for the crash on Retry in levels whose static shadows are bound to things that cannot hold one, the second phase of the sharper UI art, and launcher polish (a prompt that fits 1,280 pixels, a calmer line when a signature does not match).
5. The post-release review of every Onslaught repository: stale documents and how the products describe each other.
6. Mods toward the platform David describes: Windows support first (without it, a custom level reaches only Linux players), then replacing any asset, then adding content and a scripting interface, each designed before it is built; the approved 3D map and mission editor work, with prototypes and independent work proceeding where their dependencies allow. The tools that replace walker meshes continue with chains, bounds, skeletal and camera parts and skinned meshes.
7. Done 2026-10-30, ahead of this order at David's request: the original game loads a level the Level editor changed and CE runs the same change identically. Next, a writer that builds a level from scratch (terrain, world and mission), whose first targets are a two-unit test level that CE runs and the museum world, walked or flown around in the Battle Engine. Retail-compatible comparisons remain desirable where practical.
8. The content catalogue to a complete inventory (every model, texture and image, used or not), then the museum's art boards, turntables, lighting, signs and a main-menu entry. A future unified CE entry should make Play, Create and Multiplayer discoverable, with Create able to open the separate Companion.
9. Level and mission authoring from scratch: custom levels for players and small test levels that CE can run; the editors' remaining work and their acceptance in CE, with retail-compatible comparisons where practical.
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
The older [original-binary feasibility note](roadmap/original-binary-online-multiplayer-feasibility.md) concerns a
separate historical route, not a statement that CE already has online play.

### Level and mission tools

The Companion's Level editor can inspect and move placed objects (typed, dragged on the map or nudged with the arrow keys), list only the moved ones, copy a unit (appended after every row, so nothing else changes), show a map and mission scripts, and edit a script's
source (compile it, make the level use it, undo it); it saves changed world files as new CE mods and starts CE at the open level with the changes in a temporary folder of its own (its Play button). The page is covered by
tests and offscreen captures on Linux, and one edit of one script and one copy of a unit were staged by it and run in CE on Linux (section 16 of the mission
editor design and the level editor plan's M5 acceptance); nobody has used it by hand, and the mod does not preserve the edited source beside the world file. The [level editor plan](roadmap/companion-level-editor.md)
and [mission editor design](roadmap/companion-mission-editor.md) own their remaining gates, including source-preserving
staging, hand use and gameplay acceptance. CE's documented world-mod loader is currently Linux-only.

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
