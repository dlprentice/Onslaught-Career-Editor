# The goal

Status: standing maintainer objective; not complete
Last updated: 2026-10-15 (David's new direction: decomp done and private, native port, companion active, Godot rebuild parked)
Summary: what David wants from the project now, where each part is owned, and the evidence and safety rules that still apply.

This is the maintainer's statement of what is wanted. Measurements can correct implementation claims; they cannot
narrow or mark this objective complete. Earlier directions (the Ghidra campaign and the Godot 1:1 rebuild) remain
in Git history and the private RE archive.

## The direction (David, 2026-10-15)

- **Reverse engineering is done by decompilation.** The byte-matching decompilation of the retail executable
  (private `bea-decomp`, 5,482 of 5,482 functions) is the authority on what the game does. It is planned for
  publication as "Onslaught CE": GPL-3.0 source and binaries, no game files, once its native port plays like retail.
- **The faithful game is a native source port** of that decompilation, in progress and private, for Windows and
  Linux. A later remake, if any, forks that port.
- **The companion is the public product.** A polished Godot .NET toolkit for Linux and Windows, for players: careers,
  Goodies, settings, backups, music, voices and lore, and later a mod manager built on the AppCore patching core,
  with no known data-loss path.
- **The Godot rebuild is parked**; `rebuild/` keeps its parked state as reference.
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

Not met. The decompilation is complete; the native port and the companion's next phase are in progress.
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) owns what is demonstrated, [PROGRAM.md](PROGRAM.md) the work
queue and [VALIDATION.md](VALIDATION.md) the checks.
