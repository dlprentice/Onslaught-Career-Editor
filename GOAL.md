# The goal

Status: standing maintainer objective; not complete
Last updated: 2026-11-04 (authorized refresh of the local playtest checkpoint; broader development remains paused)
Summary: what David wants from the project now, where each part is owned, and the evidence and safety rules that still apply.

This is the maintainer's statement of what is wanted. Measurements can correct implementation claims; they cannot
narrow or mark this objective complete. The earlier Ghidra campaign remains in Git history and the private RE
archive.

## The direction (David, 2026-10-15, with the rebuild reactivated the same day)

- **Reverse engineering is grounded in decompilation.** The reconstruction matches all 5,482 mapped game functions
  in the maintainer's private working tree, with a documented one-byte object-code correction; without that correction,
  one function remains unmatched. Source-only matching without that concession remains a goal, alongside clear records
  of source stand-ins; matching does not prove the developer's original spelling or complete behavioural understanding. Its public
  export, [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), reproduces 5,449 of the 5,482 (99.40% when
  this was written; the other 33 are in four DirectX sample files the export leaves out).
- **The faithful game is a native source port** of that decompilation, for Windows and Linux, published separately
  as [Onslaught CE](https://github.com/dlprentice/onslaught-ce): GPL-3.0-only source and binaries, no game files.
  Preserve a faithful baseline while fixing demonstrated defects and improving reliability, input, controller support,
  in-game guidance, window/display choices, 4K readability, performance and useful, privacy-conscious diagnostics.
  Verify the developer console, cheats and free camera through usable controls rather than assuming each path works.
  Keep faithful reference recordings separate from a future way to record and test CE enhancements and controller input.
  Preserve the ordinary campaign and existing ways of playing with their intended rules, while retaining demonstrated
  bug fixes and useful quality-of-life improvements. New modes are optional and must not interfere with ordinary play.
- **Online play should be approachable.** Prove independently controlled players across Linux and Windows, including
  co-op and opposing-team versus/skirmish maps. Extend co-op to the ordinary campaign with compatible saves and
  progression; support larger matches and maps as the implementation is validated, without fixing a final player
  limit here. Team colours and compatible Battle Engine/unit customization should make teams and players recognizable.
  Host/Join, failures and content compatibility need understandable in-game workflows. Offer a browser of public
  lobbies, creation and joining for public and private lobbies, a private invitation path, and in-game voice and text
  chat. Voice should provide proximity/local, squad and team channels, visible speaking indicators above participating
  units, and mute controls. These are planned workflows whose implementation and acceptance remain open. A direct
  connection or idle synchronization is not completion.
- **A future real-time 3D commander role** lets a player direct eligible friendly units from a tactical view, including
  an eventual multiplayer mode alongside players piloting Battle Engines. Aim for Linux and Windows and later more than two
  participants. Missions and game events still determine outcomes. Prove this optional role works, including in
  controlled test scenarios; its availability and final product placement can be decided as development progresses.
  David describes it as an RTS form of the game: beyond directing units, a commander should be able to select buildings
  and act through them, for example to construct units, reusing the game's own logic where it can. Because that changes
  how a battle plays, Commander will probably need maps of its own. This is a goal, not a completed capability.
- **Play any controllable unit.** An optional way to directly play infantry, vehicles, mounted/fixed guns and eligible
  controllable structures, beyond the Battle Engine. In team matches, players should be able to pilot a Battle Engine
  or play another eligible unit; spawning as a unit and temporarily taking one over remain possible designs. Match
  rules determine eligibility. Direct play is a separate role from a commander issuing orders to units.
  Temporary control must preserve the unit's identity, team and squad membership. Release or disconnection should
  restore its AI with the latest valid orders, including orders received while a human controlled it. Define explicit
  fallback behavior for a last survivor, a missing squad, a destroyed target or an invalid destination. Give each type
  usable controls and HUD: infantry weapons/ammunition/reloading; vehicle and artillery aiming, traverse, firing arcs,
  trajectory, ammunition and reload; fixed-gun traverse and leaving the position. Indicators must reflect actual native
  firing conditions and obstructions. The solo tank prototype now has bounded squad-membership/current-AI hand-back,
  but exact formation/waypoint restoration, a unit HUD and network control remain open. It does not prescribe how
  future online roles work. Like other new modes, these roles must not interfere with ordinary campaign play;
  availability and final placement remain flexible.
- **Creation and modding tools** should let players inspect and create levels, missions and compatible modifications
  safely, including 3D map and mission editors. A modern CE-native project format and custom gameplay are first-class
  targets; original-game-compatible export is useful where practical but is not a prerequisite. Faithful behavior
  for the existing campaign remains a separate baseline. David approved a Goodies-style museum as a world of its own, alongside
  custom test levels. An evidence-based catalogue of textures, models, animations, audio and other content should
  support editors, modding and future HD successors without distributing the game's proprietary assets.
- **The Godot rebuild**, developed in [onslaught-godot](https://github.com/dlprentice/onslaught-godot), currently has
  a scoped proof of concept: a C# reimplementation aiming for startup through level 100 completion (win, loss and
  retry), with compatible career data. `OnslaughtRebuild.Parity` owns the simulation and `OnslaughtRebuild.Host`
  the presentation; parity is measured against retail and native-port recordings Present by Present, and
  onslaught-godot records it. The longer-term aim is a faithful full-game baseline, followed by optional enhancements
  such as modern creation tools, HD assets and expanded multiplayer. `rebuild/` here is a frozen copy.
- **The companion, Onslaught Companion, is the player app that can launch Onslaught CE.** A Godot .NET app for Linux
  and Windows, for careers, Goodies, settings, backups, music, voices and lore, with protected writes and verified backups.
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
demonstrated capabilities. A handoff is a dated continuity snapshot, not a competing roadmap: verify current refs,
claims and evidence before acting, and update the existing owner when a material milestone changes.

David has authorized a refreshed local 0.1.99 checkpoint containing the recent integrated work. This bounded refresh
may proceed while broader development remains paused. Preserve the earlier snapshot's packages, accepted builds,
Companion stage, launch setup/profile and copied user data; assemble and validate the refresh separately. Retaining
the earlier snapshot does not forbid providing an updated one. Each checkpoint's capability claims must follow its
own source, package and runtime evidence, with unfinished work stated plainly. The wider goals remain in scope;
[PROGRAM.md](PROGRAM.md#order-after-0113) owns the current order and remaining work.

Do not publish 0.2 while working multiplayer or the other agreed release requirements remain incomplete. Working
multiplayer must be part of that larger release. Internal playtest checkpoints and continued development do not lift
this release hold.

## Evidence

Every behaviour claim needs a capture, byte comparison, focused test, or pinned source reference. The decompilation
is cited by function, never quoted. A name, one observed call or a model report alone is insufficient. Static
evidence establishes identities and structures; only controlled runtime evidence establishes causality and values.
The upstream GPL Onslaught source (`stuart73/Onslaught`, in `references/Onslaught`) is a source reference, not proof of retail behaviour.
Unknowns are written as open questions with the cheapest falsifier.

## Safeguards

- Never write the pristine measurement specimen. Bind byte findings to its hash.
- Installed-game writes require the owner's informed choice and a verified backup before writing. Never label an
  already modified file as the original.
- Never destroy saves as a side effect. Use real save baselines and preserve length, reserved fields and unknown
  bytes; do not synthesize `.bes` saves.
- Keep retail material, Ghidra databases and decompiler output out of this repository (`npm run test:safety`).
- Preserve unique evidence and unrelated changes; follow [AGENTS.md](AGENTS.md) for storage, publication and
  cleanup rules.
- Onslaught work does not use GitHub Actions or hosted CI/CD unless David changes that direction. Run the applicable
  local checks and documented release gates instead.

## Where the goal stands

Not met. The mapped decompilation matches with the concession above; the native port is public as Onslaught CE,
with current downloads in the [release list](https://github.com/dlprentice/onslaught-ce/releases/latest); the rebuild proof of concept is in progress in onslaught-godot; the companion supports the original game
and CE, with remaining acceptance and release work in [PROGRAM.md](PROGRAM.md#companion--ce-integration).
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) owns what is demonstrated, [PROGRAM.md](PROGRAM.md) the work
queue and [VALIDATION.md](VALIDATION.md) the checks.
