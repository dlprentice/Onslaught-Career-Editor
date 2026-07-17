# Function Notes

This directory contains retained, address-specific notes that carry unique
static evidence. A filename or saved symbol is a research label, not a source-
identity or runtime-behavior claim.

Useful starting points:

- [Career save/load](Career.cpp/CCareer__Load.md) — save, progression, ranks, links, goodies, and
  kill tracking.
- [Battle Engine movement](BattleEngine.cpp/CBattleEngine__Move.md) and
  [jet movement](BattleEngineJetPart.cpp/CBattleEngineJetPart__Move.md) — movement, targeting,
  morph support, projectiles, and configuration.
- [Main game loop](game.cpp/CGame__MainLoop.md) — level lifecycle, objectives, respawn,
  camera, and multiplayer predicates.
- [Frontend processing](FrontEnd.cpp/CFrontEnd__Process.md) and [Goodies processing](FEPGoodies.cpp/CFEPGoodies__Process.md) —
  menu and frontend behavior.
- [Unit damage](Unit.cpp/CUnit__ApplyDamage.md) — unit initialization, damage, transform, and effects.

Browse the directory tree for the complete retained set. Generated rollups and
per-owner mirror indexes were removed; Git history preserves them if an old
research label must be traced.

Current corrections and provenance are owned by the
[full re-audit closeout](../ghidra-full-reaudit-closeout-2026-07-13.md) and
[reviewed correction plan](../ghidra-reviewed-correction-plan-2026-07-13.json).
