# The goal

Status: standing maintainer objective; not complete
Last updated: 2026-11-05 (the 0.2 hold and the standing 0.1.x authorization worded once; every Companion capability named in the migration; the mod platform direction recorded here)
Summary: what David wants from the project now, where each part is owned, and the evidence and safety rules that still apply.

This is the maintainer's statement of what is wanted. Measurements can correct implementation claims; they cannot
narrow or mark this objective complete. The earlier Ghidra campaign remains only in the private pre-flatten history
(before the public root commit of 2026-10-15), kept in the private historical maintainer archive.

## The direction (David, 2026-10-15; later items are dated inline)

- **Reverse engineering is grounded in decompilation.** The reconstruction matches every mapped game function
  in the maintainer's private working tree, with a documented one-byte object-code correction; without that correction,
  one function remains unmatched. Source-only matching without that concession remains a goal, alongside clear records
  of source stand-ins; matching does not prove the developer's original spelling or complete behavioural understanding. Its public
  export, [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), records its own coverage and the DirectX
  sample files it leaves out.
- **The faithful game is a native source port** of that decompilation, for Windows and Linux, published separately
  as [Onslaught CE](https://github.com/dlprentice/onslaught-ce): GPL-3.0-only source and binaries, no game files.
  Preserve a faithful baseline while fixing demonstrated defects and improving reliability, input, controller support,
  in-game guidance, window/display choices, 4K readability, performance and useful, privacy-conscious diagnostics.
  Prefer high ordinary visual settings and supported extra effects on capable hardware, while preserving saved
  preferences and the faithful reference path. Offer controls for terrain detail/LOD, pop-in and extended draw distance,
  alongside a separate optional maximum-distance/full-model mode; that more demanding mode is not requested as the
  default yet. Verify actual capability selection, image quality and performance before choosing defaults.
  Verify the developer console, cheats and free camera through usable controls rather than assuming each path works.
  Keep faithful reference recordings separate from a future way to record and test CE enhancements and controller input.
  Preserve the ordinary campaign and existing ways of playing with their intended rules, while retaining demonstrated
  bug fixes and useful quality-of-life improvements. New modes are optional and must not interfere with ordinary play.
- **Online play should be approachable (2026-10-29).** Prove independently controlled players across Linux and Windows, including
  co-op and opposing-team versus/skirmish maps. Extend co-op to the ordinary campaign with compatible saves and
  progression; support larger matches and maps as the implementation is validated, without fixing a final player
  limit here. Team colours and compatible Battle Engine/unit customization should make teams and players recognizable.
  Host/Join, failures and content compatibility need understandable in-game workflows. Offer a browser of public
  lobbies, creation and joining for public and private lobbies, a private invitation path, and in-game voice and text
  chat. Voice should provide proximity/local, squad and team channels, visible speaking indicators above participating
  units, and mute controls. Acceptance of these workflows remains open: text chat is partly implemented in
  development source and unaccepted, and voice is planned. A direct connection or idle synchronization is not
  completion.
- **Continuous real-time 3D RTS Commander inside native CE** (2026-11-02; a required native-CE mode since 2026-11-04) lets a player direct eligible friendly units with
  appropriate camera, selection, order and status controls. A map or a toggle into a 3D preview is partial work,
  not completion of this mode. Include an eventual multiplayer role alongside players piloting Battle Engines.
  Aim for Linux and Windows and later more than two participants. Missions and game events still determine outcomes.
  Prove this optional mode through a usable in-game workflow and controlled scenarios; its availability within
  particular modes and scenarios can develop without changing ordinary campaign play.
  David describes it as an RTS form of the game: beyond directing units, a commander should be able to select buildings
  and act through them, for example to construct units, reusing the game's own logic where it can. Because that changes
  how a battle plays, Commander will probably need maps of its own. This is a goal, not a completed capability.
- **Play any controllable unit (2026-11-02).** An optional way to directly play infantry, vehicles, mounted/fixed guns and eligible
  controllable structures, beyond the Battle Engine. In team matches, players should be able to pilot a Battle Engine
  or play another eligible unit; spawning as a unit and temporarily taking one over remain possible designs. Match
  rules determine eligibility. Direct play is a separate role from a commander issuing orders to units.
  Temporary control must preserve the unit's identity, team and squad membership. Release or disconnection should
  restore its AI with the latest valid orders, including orders received while a human controlled it. Define explicit
  fallback behavior for a last survivor, a missing squad, a destroyed target or an invalid destination. Give each type
  usable controls and HUD: infantry weapons/ammunition/reloading; vehicle and artillery aiming, traverse, firing arcs,
  trajectory, ammunition and reload; aircraft flight controls, weapon arcs, ammunition and reload; boats, ferries and
  other vehicles (wheeled, hover, walkers, drones) with the controls their type supports; fixed-gun traverse and
  leaving the position. Every other unit type in the catalogue's unit definitions gets a defined viewpoint, controls
  and HUD. Indicators must reflect actual native firing conditions and
  obstructions. The solo tank prototype is an early step on this path; its status is in
  [PROGRAM.md](PROGRAM.md#onslaught-ce-player-experience-and-online-play). It does not prescribe how
  future online roles work. Like other new modes, these roles must not interfere with ordinary campaign play;
  availability and final placement remain flexible.
- **3D map and mission editors usable inside native CE** (direction approved 2026-10-31; required in native CE
  2026-11-04), reached through its menus, should let players author,
  inspect, save, reopen and test maps and mission experiences in game. A button that launches an external editor does
  not meet this requirement. A modern CE-native project format and custom gameplay are first-class targets;
  original-game-compatible export is useful where practical but is not a prerequisite. Faithful behavior for the
  existing campaign remains a separate baseline. **An actual explorable 3D museum reached through CE's menus** is a
  separate required experience; the Goodies gallery and the separate museum construction test
  ([PROGRAM.md](PROGRAM.md#level-and-mission-tools)) are not museum completion.
  An evidence-based catalogue of textures, models, animations, audio and other content should support these tools,
  modding and future HD successors without distributing the game's proprietary assets.
  CE is the primary place to play, create and experiment. Move gameplay, content authoring, mod selection and
  in-game catalogue capabilities into CE in verified stages. Reuse the working tools, validated data and contracts;
  this player-experience requirement does not prescribe embedding another engine or runtime in CE.
- **Mods are a platform (2026-10-30).** Players can replace any model, texture, sound, music or text; add units,
  levels and missions; and use a scripting interface for new rules and modes, up to whole new games built inside CE.
  Safe authoring and compatibility, complete content coverage and HD successors remain open; the work is tracked in
  [PROGRAM.md](PROGRAM.md#level-and-mission-tools).
- **The Godot rebuild**, developed in [onslaught-godot](https://github.com/dlprentice/onslaught-godot), currently has
  a scoped proof of concept: a C# reimplementation aiming for startup through level 100 completion (win, loss and
  retry), with compatible career data. `OnslaughtRebuild.Parity` owns the simulation and `OnslaughtRebuild.Host`
  the presentation; parity is measured against retail and native-port recordings frame by frame (one Present call
  each), and
  onslaught-godot records it. The longer-term aim is a faithful full-game baseline, followed by optional enhancements
  such as modern creation tools, HD assets and expanded multiplayer. `rebuild/` here is a frozen copy.
- **Move every Companion capability into native CE, in verified stages, then phase out the separate app
  (2026-11-04).** CE should include the Companion's careers, saves and backups, settings, lore, content exploration
  and the catalogue, the editors and installation management, alongside native authoring and play. Every current
  Companion workflow and its subflows belong in the native CE migration, including media browsing/playback/exports,
  recovery, read-only inspection and authoring; the
  [migration checklist](PROGRAM.md#native-ce-migration-checklist) records their source owners and remaining requirements.
  The separate Companion stays supported, with its tools and evidence, until each replacement is verified to
  preserve its useful capabilities and safety. This does not prescribe an engine/runtime embedding architecture.
  The current standalone Godot .NET app for Linux and Windows still provides careers, Goodies, settings, backups,
  music, voices and lore, with protected writes and verified backups, and can launch Onslaught CE.
  It supports original-game and CE careers and backups, CE launcher settings and the steps for updating CE (the companion
  contacts nothing). For older CE installations, follow the [current release's migration guidance](https://github.com/dlprentice/onslaught-ce/releases/latest).
  Its [known limits](companion/OnslaughtToolkit.Godot/README.md#known-limits) distinguish
  the exercised Linux CE workflow and native Windows backend/load checks from Windows Godot UI
  acceptance still awaiting validation. Original-game save
  editing stays, with protected writes; executable patching and copied-install safe launch are retired, and
  enhancements belong in CE as opt-in options.
- **Recovery** should preserve unique project work, evidence, saves and necessary signing/recovery material off-site,
  with verified restoration and a replacement-machine rehearsal. Keep sensitive locations and keys private, avoid
  redundant large uploads, and describe uncovered data honestly.
- **Game documentation** lives in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation).
  This repository retains a frozen copy and its own tools; it carries no Ghidra database, decompiler output, retail
  binaries or assets, or decomp source.

## How progress is measured

Progress changes an outcome: a player can do something useful that was previously unavailable; a demonstrated defect
is fixed and verified; a specific unknown is resolved in a way that changes the next decision; or a meaningful
preservation or documentation gap is closed. Investigation and test infrastructure can be real progress, but report
what they establish and what remains rather than presenting them as a delivered feature.

Describe the stage separately: an idea, an experiment, reviewed source, integrated source, a validated release, or
player/device acceptance. A branch, passing synthetic test, idle network connection, byte match or release number is
not on its own completion. A capability is done only for the scope actually supported: it is reachable through the
intended workflow, preserves applicable saves and baseline behavior, and has evidence for the platforms and conditions
claimed. Real Internet and relevant physical-device checks remain distinct from local, simulated and VM tests. Do not
invent a project-wide percentage or promise universal parity from bounded checks.

[PROGRAM.md](PROGRAM.md) owns the dated cross-project chart and work queue. Product repositories own their detailed
release, design and evidence records; [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) owns this repository's
demonstrated capabilities. A dated continuity note from earlier work is a snapshot, not a competing roadmap: verify
current refs, claims and evidence before acting, and update the existing owner when a material milestone changes.

Work from the reported problems and current evidence while keeping the earlier and refreshed 0.1.99 checkpoints
(r1 and r2, defined in [PROGRAM.md](PROGRAM.md#order-after-0113)) reproducible.
Preserve their packages, accepted builds, Companion stages, launch profiles and copied user data until their
preservation has been verified; subsequent implementation and tests use separate outputs and profiles. Each
checkpoint's capability claims must follow its own evidence. A player's report adds useful acceptance or a problem
to investigate within the scope actually tried; it does not certify untried features. [PROGRAM.md](PROGRAM.md#order-after-0113)
owns the current order and remaining work.

Do not publish 0.2 until David's whole program is complete and has been tested internally: working multiplayer,
continuous native CE RTS Commander, play-any-unit controls for every unit type, usable in-game 3D map and mission
editors, the explorable in-game museum, every Companion capability moved into CE, and the other agreed requirements.
An experimental or alpha label does not authorize shipping unfinished pieces in their place, and internal playtest
checkpoints and continued development do not lift this release hold. 0.2 is not released until David gives an
explicit go-ahead after that, which no earlier standing release authorization covers. Gated 0.1.x maintenance
releases remain under David's standing authorization of 2026-10-27; 0.1.99 is an internal checkpoint label that is
never published. The wider foundation, rebuild, quality, documentation and recovery goals remain in scope.

## Evidence

Every behaviour claim needs a capture, byte comparison, focused test, or pinned source reference. The decompilation
is cited by function, never quoted. A name, one observed call or a model report alone is insufficient. Static
evidence establishes identities and structures; only controlled runtime evidence establishes causality and values.
Stuart Gillam's GPL Onslaught source (`stuart73/Onslaught`), pinned through the `dlprentice/Onslaught` fork at `references/Onslaught`, is a source reference, not proof of retail behaviour.
Unknowns are written as open questions with the cheapest falsifier.

## Safeguards

- Never write the pristine measurement specimen. Bind every byte finding to the SHA-256 of the exact file it was read from.
- Installed-game writes require the owner's informed choice and a verified backup before writing. Never label an
  already modified file as the original.
- Never destroy saves as a side effect. Use real save baselines and preserve length, reserved fields and unknown
  bytes; do not synthesize `.bes` saves.
- Career editing inside CE must retain verified backups, stale-write refusal and read-back checks, and coordinate
  with the game's loaded career state. An in-use career is protected; merely being on a frontend page does not make
  an edit safe, because CE may still hold a profile that would overwrite it. Design and test the save/reload hand-off
  before replacing the standalone Companion's running-game refusal.
- Keep retail material, Ghidra databases and decompiler output out of this repository (`npm run test:safety`).
- Preserve unique evidence and unrelated changes. Maintainers follow [AGENTS.md](AGENTS.md) for storage, publication
  and cleanup; contributors follow [CONTRIBUTING.md](CONTRIBUTING.md).
- Onslaught work does not use GitHub Actions or hosted CI/CD unless David changes that direction. Run the applicable
  local checks and documented release gates instead.

## Where the goal stands

Not met. Status by area: [PROGRAM.md](PROGRAM.md) owns the work queue, [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md)
what is demonstrated and [VALIDATION.md](VALIDATION.md) the checks; the native port's current downloads are in the
[Onslaught CE release list](https://github.com/dlprentice/onslaught-ce/releases/latest).
