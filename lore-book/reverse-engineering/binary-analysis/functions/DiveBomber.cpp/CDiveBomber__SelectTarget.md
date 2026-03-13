# CDiveBomber__SelectTarget

> Address: 0x00445070 | Source: DiveBomber.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (headless postscript + read-back verified, 2026-03-01)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

AI target selection logic for dive bomber aircraft. Iterates through potential targets, validates them, and selects the highest priority target for a dive bombing run.

## Signature
```c
void * __thiscall CDiveBomber__SelectTarget(void * this);
```

Read-back verified in `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` (`status=OK`).

## Responsibilities

- **Target iteration** - Loops through vehicles at offset 0x160
- **State validation** - Checks target vehicle state
- **Entity validation** - Validates dive bomber entities at offset 0x88
- **Distance filtering** - Filters by health/distance at offset 0x10
- **Priority selection** - Returns highest priority valid target

## Key Observations

- **AI function** - Part of enemy aircraft AI system
- **Debug assertions** - Contains assertions at lines 18, 19, 22, 23
- **Exception handling** - Uses SEH for runtime checks
- **No constructor** - Only assertion stubs reference the source file

## Notes

- Discovered via xref to debug path string at 0x006289c0
- All 4 xrefs are in exception/assertion code
- The function logic was identified from decompilation
- Dive bombers are enemy aircraft that perform diving attack runs

## Related Functions

- [CAirUnit__Init](../AirUnit.cpp/CAirUnit__Init.md) - Base class init
- [CBattleEngine__AddProjectile](../BattleEngine.cpp/CBattleEngine__AddProjectile.md) - Weapon fire

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
