# Ghidra WorldPhysics Load/Resolve Wave846 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `worldphysics-load-resolve-wave846`
Probe anchor: Wave846 WorldPhysics load/resolve

Wave846 hardened four WorldPhysicsManager load/resolve/free rows as no-argument `void __cdecl ... (void)` functions after serialized headless dry/apply/read-back. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00510520 CWorldPhysicsManager__ResolveLoadedDefinitionReferences` | `void __cdecl CWorldPhysicsManager__ResolveLoadedDefinitionReferences(void)` | Called from `0x0046cdd7 CGame__LoadResources` with no pushed arguments or ECX receiver setup. Iterates `DAT_008553ec`, `DAT_008553f0`, `DAT_008553f8`, `DAT_008553fc`, `DAT_00855400`, `DAT_00855404`, and `DAT_00855408`; uses Wave560 resolver helpers plus particle-set and sound-effect lookup paths. |
| `0x00510740 CWorldPhysicsManager__FreeNestedThingSets_6C` | `void __cdecl CWorldPhysicsManager__FreeNestedThingSets_6C(void)` | Called from `0x0046cc61 CGame__ShutdownRestartLoop`; drains nested `entry+0x6c` sets for thing/component definition lists `DAT_008553fc` and `DAT_00855400`. |
| `0x00510800 CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData` | `void __cdecl CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData(void)` | Called from `0x004f0092 CLTShell__InitializeRuntimeAndLoadCoreResources`; clears/reinitializes definition lists, loads `data/default_physics.dat`, drains `DAT_006602a0`, creates a default `CBattleEngineData`, then loads `data/battle_engine_configuration`. |
| `0x00510a90 CWorldPhysicsManager__ClearAndFreeAllDefinitionLists` | `void __cdecl CWorldPhysicsManager__ClearAndFreeAllDefinitionLists(void)` | Called from `0x004f00e0 CLTShell__ShutdownRuntimeAndReleaseResources` and `0x0051081e` inside the reload path; drains `DAT_006602a0`, removes/frees entries from `DAT_008553e8` through `DAT_00855408`, then clears/frees/nulls every list container. |

Read-back evidence:

- `ApplyWorldPhysicsLoadResolveWave846.java dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=0 missing=0 bad=0`
- `ApplyWorldPhysicsLoadResolveWave846.java apply`: `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=0 missing=0 bad=0`
- `ApplyWorldPhysicsLoadResolveWave846.java final dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 4 metadata rows, 4 tag rows, 5 xref rows, 3300 instruction rows, 325 caller-site instruction rows, 23 context metadata rows, 23 context tag rows, and 4 decompile rows.
- Queue after Wave846: 6098 total functions, 5673 commented, 425 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5673/6098 = 93.03%`, strict clean-signature proxy `5673/6098 = 93.03%`.
- Next raw commentless row is `0x00512040 CLTShell__InitUnhandledExceptionLogFile`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260525-060333_post_wave846_worldphysics_load_resolve_verified`, 19 files, 171871111 bytes, `DiffCount=0`.

What this proves:

- The four target rows exist in the saved Ghidra project.
- The saved signatures are no-argument `void __cdecl ... (void)` signatures.
- The saved comments and tags include `worldphysics-load-resolve-wave846` and `wave846-readback-verified`.
- The observed bodies are static retail Ghidra evidence for WorldPhysicsManager definition resolution, nested set draining, default physics/BattleEngineData reload, and global definition-list teardown.

What remains unproven:

- Exact source method identity.
- Exact definition-list, entry, and `CBattleEngineData` schemas.
- Runtime load/resolve/shutdown/reload behavior.
- BEA patching behavior.
- Rebuild parity.
