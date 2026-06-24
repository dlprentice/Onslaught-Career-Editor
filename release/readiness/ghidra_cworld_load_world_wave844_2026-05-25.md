# Ghidra CWorld LoadWorld Wave844 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cworld-load-world-wave844`

Wave844 CWorld LoadWorld saved a bounded function comment and tags for `0x0050b9c0 CWorld__LoadWorld`. The pass preserved the existing `bool __thiscall CWorld__LoadWorld(void * this, void * levelName)` signature, made no rename, made no function-boundary change, and made no executable-byte change.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0050b9c0 CWorld__LoadWorld` | Main world-load body reached by `CWorld__LoadWorldFile` callsite `0x0050b720`. |
| `0x0050b9da` | Prologue calls `CRT__AllocaProbe` for a `0x38cc-byte stack frame`; tail returns with `RET 0xc`. |
| `0x0050ba7a` / `0x0050baed` | Calls `CWorld__InitLODLists` and `CWorld__LoadWorldHeader`. |
| `0x0050bbde` / `0x0050bbf5` | Calls `CWorld__LoadScriptEvents` and can recursively call `CWorld__LoadWorldFile` for base-world loading. |
| `0x0050bd8a`, `0x0050ca98`, `0x0050bf56`, `0x0050c146` | Calls `CWorldPhysicsManager__CreateSquad`, `CWorldPhysicsManager__CreateThingByType`, `CWorldPhysicsManager__CreateEffect`, and `CWorldPhysicsManager__CreateTrigger`. |
| `0x0050cad1` | Adds mesh names through `CWorldMeshList__Add`. |
| `0x0050cf23` / `0x0050cf38` | Chooses `CInfluenceMapManager__SkipLoad` or `CInfluenceMapManager__Load`. |
| `0x0050d187` | Loads waypoints through `CWaypointManager__LoadWaypoints`. |
| `0x0050d331`, `0x0050d363`, `0x0050d386` | Runs version-gated occupancy chunk skip/load/header paths. |
| `0x0050d431`, `0x0050d456`, `0x0050d473`, `0x0050d47a` | Non-base-world tail calls `CWorld__SpawnInitialThings`, old-version occupancy clearing, `CWorld__ApplyStaticMaskToOccupancyBitplanes`, or `CWorld__RebuildOccupancyGridFromDynamicSet`. |

Read-back evidence:

- `ApplyCWorldLoadWorldWave844.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyCWorldLoadWorldWave844.java apply`: `READBACK_OK` and `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyCWorldLoadWorldWave844.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 3201 instruction-window rows with 2023 rows inside `CWorld__LoadWorld`, 11 context metadata rows, 11 context tag rows, and 1 decompile row.
- Queue after Wave844: 6098 total functions, 5668 commented, 430 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5668/6098 = 92.95%`, strict clean-signature proxy `5668/6098 = 92.95%`.
- Next raw commentless row: `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`.
- Verified backup: `G:\GhidraBackups\BEA_20260525-050626_post_wave844_cworld_load_world_verified`, 19 files, 171871111 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved signature remains `bool __thiscall CWorld__LoadWorld(void * this, void * levelName)`.
- The saved comment and tags include `cworld-load-world-wave844` and `wave844-readback-verified`.
- The observed body is a static retail world-load orchestration body tied to the caller xref, complete instruction read-back rows, context helper metadata, and decompile export.

What remains unproven:

- Exact world-buffer schema.
- Concrete stack-local structure layouts.
- Exact source-body identity.
- Runtime load behavior.
- BEA patching behavior.
- Rebuild parity.
