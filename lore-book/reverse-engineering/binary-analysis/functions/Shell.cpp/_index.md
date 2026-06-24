# Shell.cpp / CShell Static Evidence

> Source File: exact retail source file unconfirmed | Binary: BEA.exe

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Wave507 records the first focused CShell family evidence in the saved Ghidra project. The checked functions are tied to projectile-burst shell creation through `ProjectileBurst__SpawnFromCurrentPreset` and OID type `0x15`; the exact source filename and full class layout are still unproven.

Wave1020 (`projectile-burst-spawn-spine-review-wave1020`) re-read `0x004df530 CShell__CopyResourceNameToInlineBuffer` in the projectile-burst spawn spine. The callsite at `0x005076dc` from `0x005069f0 ProjectileBurst__SpawnFromCurrentPreset` still matches the saved Wave507 claim, and the helper still ends with `RET 0x4` after copying the resource name into `this+0x110`. No mutation was needed. Verified backup: `G:\GhidraBackups\BEA_20260531-214433_post_wave1020_projectile_burst_spawn_spine_review_verified`. Runtime shell/projectile behavior, exact buffer-size contract, exact source identity, BEA patching, and rebuild parity remain separate proof.

## Wave507 CShell Projectile-Burst Shell Helpers (2026-05-17)

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004df4c0 | CShell__Constructor | Calls `CThing__ctor_like_004f3e10`, installs the CShell/CActor-adjacent vtables at `0x005ded48` and `0x005decd0`, clears the inline `0x100`-byte resource/name buffer at `this+0x110`, and returns `this`. |
| 0x004df530 | CShell__CopyResourceNameToInlineBuffer | Corrects stale `CEngine__CopyCStringToObjectLabel110` ownership. `RET 0x4` proves one explicit `resource_name` argument; `ProjectileBurst__SpawnFromCurrentPreset` calls this after `OID__CreateObject(0x15)`, and the body copies a non-empty C string into `this+0x110`. |
| 0x004df550 | CShell__Init | Vtable `0x005ded48` slot 9. `RET 0x4` proves one explicit `init` argument; the body builds a `CResourceDescriptor` from `this+0x110`, creates a `PCRTID` render object, clears flag bit 1 at `this+0x2c`, calls `CActor__Init`, randomizes orientation at `this+0xe0`, and schedules event `2000`. |

This pass saved names, signatures, comments, and tags only. Runtime shell behavior, event semantics, render-object type, full CShell layout, exact source identity, local names, structure types, and rebuild parity remain unproven.
