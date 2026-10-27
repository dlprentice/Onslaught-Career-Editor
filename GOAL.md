# The goal

Status: standing maintainer objective; not complete
Last updated: 2026-10-27 (longer-term port, commander and Godot goals clarified)
Summary: what David wants from the project now, where each part is owned, and the evidence and safety rules that still apply.

This is the maintainer's statement of what is wanted. Measurements can correct implementation claims; they cannot
narrow or mark this objective complete. The earlier Ghidra campaign remains in Git history and the private RE
archive.

## The direction (David, 2026-10-15, with the rebuild reactivated the same day)

- **Reverse engineering is grounded in decompilation.** The reconstruction matches all 5,482 mapped game functions
  with a documented one-byte object-code correction; without that correction, one function remains unmatched.
  Matching does not by itself establish complete behavioural understanding. Its public export is
  [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp).
- **The faithful game is a native source port** of that decompilation, for Windows and Linux, published separately
  as [Onslaught CE](https://github.com/dlprentice/onslaught-ce): GPL-3.0-only source and binaries, no game files.
  Preserve a faithful baseline while improving reliability, controls, 4K readability and performance, and adding
  cross-platform online play, campaign co-op and modding support.
- **A future commander role** is an opt-in CE multiplayer mode in which one player directs eligible friendly units
  from a tactical view while others pilot battle engines. Aim for Linux and Windows and eventually more than two
  participants. Ordinary campaign play remains available when the mode is off; host-run missions and game events
  determine its outcomes. This is a goal, not a current capability.
- **The Godot rebuild**, developed in [onslaught-godot](https://github.com/dlprentice/onslaught-godot), currently has
  a scoped proof of concept: a C# reimplementation aiming for startup through level 100 completion (win, loss and
  retry), with compatible career data. `OnslaughtRebuild.Parity` owns the simulation and `OnslaughtRebuild.Host`
  the presentation; parity is measured against retail and native-port recordings Present by Present, and
  onslaught-godot records it. The longer-term aim is a faithful full-game baseline, followed by optional enhancements
  such as modern creation tools, HD assets and expanded multiplayer. `rebuild/` here is a frozen copy.
- **The companion, Onslaught Companion, is the player app and Onslaught CE launcher.** A Godot .NET app for Linux
  and Windows, for players: careers, Goodies, settings, backups, music, voices and lore, with no known data-loss path.
  It supports original-game and CE careers and backups, CE launcher settings and signed update information. A safety
  hold applies to affected CE launchers; see the [CE safety notice](https://github.com/dlprentice/onslaught-ce).
  Its [known limits](companion/OnslaughtToolkit.Godot/README.md#known-limits) distinguish
  the exercised Linux CE workflow and native Windows backend/load checks from Windows Godot UI
  acceptance still awaiting validation. Original-game save
  editing stays, with protected writes; executable patching and copied-install safe launch are retired, and
  enhancements belong in CE as opt-in options.
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

Not met. The mapped decompilation matches with the concession above; the native port is public as Onslaught CE,
with its 0.1 preview as the first release; the rebuild proof of concept is in progress in onslaught-godot; the companion supports the original game
and CE, with remaining acceptance and release work in [PROGRAM.md](PROGRAM.md#companion--ce-integration).
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) owns what is demonstrated, [PROGRAM.md](PROGRAM.md) the work
queue and [VALIDATION.md](VALIDATION.md) the checks.
