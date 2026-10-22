# The goal

Status: standing maintainer objective; not complete
Last updated: 2026-10-22 (the companion is Onslaught Companion, the future CE launcher; exe patching and safe launch retired; earlier: decompilation done, port preview published separately as Onslaught CE, rebuild PoC in progress)
Summary: what David wants from the project now, where each part is owned, and the evidence and safety rules that still apply.

This is the maintainer's statement of what is wanted. Measurements can correct implementation claims; they cannot
narrow or mark this objective complete. The earlier Ghidra campaign remains in Git history and the private RE
archive.

## The direction (David, 2026-10-15, with the rebuild reactivated the same day)

- **Reverse engineering is done by decompilation.** The byte-matching decompilation of the retail executable
  (private, 5,482 of 5,482 functions) is done and is the authority on what the game does.
- **The faithful game is a native source port** of that decompilation, for Windows and Linux. Its preview is in
  progress and is published separately as Onslaught CE: GPL-3.0-only source and binaries, no game files (link added
  at release). A later remake, if any, forks that port.
- **The Godot rebuild is active as a scoped proof of concept**: a C# reimplementation on Godot 4.8 dev6 .NET that
  is 1:1 with retail from startup to exit, with level 100 playable to completion (win, loss and retry) and the
  career it writes identical to retail's. `OnslaughtRebuild.Parity` owns the simulation and `OnslaughtRebuild.Host`
  the presentation; parity is measured against retail and native-port recordings Present by Present, as
  [`rebuild/PARITY.md`](rebuild/PARITY.md) records.
- **The companion, Onslaught Companion, is the player app and the future Onslaught CE launcher**, paused until David
  sets new requirements. A Godot .NET app for Linux and Windows, for players: careers, Goodies, settings, backups,
  music, voices and lore, with no known data-loss path. Today it works with the original game; next it finds, launches
  and updates Onslaught CE and manages CE's careers and settings. Original-game save editing stays, with protected
  writes; executable patching and copied-install safe launch are retired, and enhancements belong in CE as opt-in
  options.
- **This repository documents the game in public**: formats, behaviours and findings as prose and specs, with our
  own tools. It carries no Ghidra database, decompiler output, retail binaries or data, or decomp source.

## Evidence

Every behaviour claim needs a capture, byte comparison, focused test, or pinned source reference. The decompilation
is cited by function, never quoted. A name, one observed call or a model report alone is insufficient. Static
evidence establishes identities and structures; only controlled runtime evidence establishes causality and values.
Stuart's partial GPL source release (GitHub `stuart73/Onslaught`, in `references/Onslaught`) is a source reference, not proof of retail behaviour.
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

## Where the goal stands

Not met. The decompilation is done; the native port's preview and the rebuild proof of concept are in progress;
the companion is paused.
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) owns what is demonstrated, [PROGRAM.md](PROGRAM.md) the work
queue and [VALIDATION.md](VALIDATION.md) the checks.
