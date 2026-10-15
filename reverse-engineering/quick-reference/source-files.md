Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Onslaught skills during the skill clean-slate pass.
Summary: Stuart source file organization lookup.
# Source File Organization

## Core Systems (52 files provided)

| File | Purpose |
|------|---------|
| Career.cpp/h | Save system, progression |
| Player.cpp/h | Kill tracking, state |
| thing.cpp/h | Base game object |
| actor.cpp/h | Movement, physics |
| engine.cpp/h | Render pipeline |
| game.cpp/h | Main loop, cheats |

## Frontend (FEP prefix)

| File | Purpose |
|------|---------|
| FEPGoodies.cpp | 232 goodie conditions |
| FEPLoadGame.cpp | Console save loading |
| FEPSaveGame.cpp | Saving, cheat codes |
| PCFEPLoadGame.cpp | **EMPTY STUB** |
| PCFEPSaveGame.cpp | **EMPTY STUB** |

## Battle Engine

| File | Purpose |
|------|---------|
| BattleEngine.cpp/h | Player mech, god mode |
| BattleEngineJetPart.cpp/h | Flight physics |
| BattleEngineWalkerPart.cpp/h | Ground movement |

## Platform

| File | Purpose |
|------|---------|
| Platform.cpp/h | Base routing |
| PCPlatform.cpp/h | Win32 impl |
| PCController.cpp/h | DirectInput |

## Storage (PC is STUBBED!)

| File | Purpose |
|------|---------|
| MemoryCard.cpp/h | Abstract interface |
| PCMemoryCard.cpp/h | **STUB** |
| XBoxMemoryCard.cpp/h | Full impl |

## Not Provided (117 of 169)

**High Priority:**
- Unit.cpp, Mech.cpp, Cannon.cpp, Missile.cpp

**MissionScript (7 files):**
- AsmInstruction.cpp (27 opcodes)
- ScriptObjectCode.cpp

**Rendering (19 DX*.cpp):**
- DXLandscape.cpp, DXShadows.cpp

**CITATION REPAIRED 2026-07-28 — and the figure it backed is now marked UNKNOWN.**
This line previously read, in full:

> See stuart-request-list.md for full inventory.

`stuart-request-list.md` **does not exist anywhere in this repository**
(`find . -iname 'stuart-request-list*'` outside `.git` returns nothing), so the
"117 of 169" heading above and the missing-file list under it had no resolvable
backing at all.

- **UNKNOWN** — the total original file count (169) and the 117 not provided are
  inherited from an archived note that is not in this repository. Nothing here
  can confirm or refute them. What would settle it: the archived request list
  itself, or a statement from Stuart of the original project's file count.
- **MEASURED** — the pinned drop's own inventory, read on 2026-07-28 from
  `git -C references/Onslaught ls-tree -r HEAD --name-only`: **108 entries — 52
  `.cpp`, 54 headers (53 `.h` + 1 `.H`), 1 `.md`, 1 `LICENSE`.** That confirms
  the "52 files provided" heading at the top of this document, and 52 + 117 = 169
  is internally consistent — but consistency is not evidence.
- The current inventory posture is owned by
  [`../source-code/reference-submodule-audit-2026-07-12.md`](../source-code/reference-submodule-audit-2026-07-12.md),
  which is the correct place to look and resolves from here.

This matters more than a normal dead link: a missing-corpus inventory is what
decides whether a rebuild lane ports from source or recovers from bytes.
