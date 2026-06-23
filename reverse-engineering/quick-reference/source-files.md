Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
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

See stuart-request-list.md for full inventory.
