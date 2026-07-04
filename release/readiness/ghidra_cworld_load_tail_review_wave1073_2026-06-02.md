# Ghidra CWorld Load/Tail Review Wave1073 Readiness Note

Status: complete static read-only evidence
Date: 2026-06-02
Scope: `cworld-load-tail-review-wave1073`

Wave1073 re-read twenty-three existing Wave555/Wave556 CWorld load/core, CWorld tail, CWorldMeshList, and CWorldPhysicsManager factory rows plus eighteen caller/context rows without Ghidra mutation. The pass made no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0050a870 CWorld__ClearSetArrays` | Existing Wave555 row; clears nineteen CWorld `CSPtrSet` slots and is still tagged `cworld-load-core-wave555`. |
| `0x0050a9c0 CWorld__InitSetArraysAndState` | Existing Wave555 row; initializes the same set-array/state surface before world loading. |
| `0x0050ac70 CWorld__LoadScriptEvents` | Existing Wave555 row; `CWorld__LoadWorld` context calls it at `0x0050bbde` while deserializing script-event state. |
| `0x0050b520 CWorld__LoadWorldFile` | Existing Wave555 row; xrefs from `CGame__LoadLevel` and recursive/base-world handling inside `CWorld__LoadWorld`. |
| `0x0050b780 CWorld__DeserializeWorld` | Existing Wave555 row; preserves the bounded world-buffer deserialize label. |
| `0x0050d4c0 CWorld__LoadWorldHeader` | Existing Wave555 row; `CWorld__LoadWorld` calls it while setting up the level header/configuration context. |
| `0x0050d6a0 CWorld__PushWorldTextSlot` | Existing Wave556 row; uses `CText__GetStringById` and world text slot fields around `+0x20c`, `+0x21c`, `+0x23c`, `+0x24c`, and `+0x25c`. |
| `0x0050d720 CWorld__UpdateWorldTextSlotTiming` | Existing Wave556 row; updates world-text slot timing/auxiliary state around the same slot arrays. |
| `0x0050d7f0 CWorld__ClearLinkedObjectPairSet` | Existing Wave556 row; clears linked object-pair set state with no stronger layout claim. |
| `0x0050d9e0 CWorldMeshList__Add` | Existing Wave556 row; xrefs from `CWorld__LoadWorld`, `CSpawnerThng__Init`, `CScriptObjectCode__CollectSpawnThings`, and recursive self-calls. |
| `0x0050dc20 CWorldMeshList__MarkUsed` | Existing Wave556 row; xref from `CUnit__Init` marks a mesh list entry used by name. |
| `0x0050dcb0 CWorld__SpawnInitialThings` | Existing Wave556 row; `CWorld__LoadWorld` tail calls it at `0x0050d431`, and the body calls `CWorldPhysicsManager__CreateThingByType`. |
| `0x0050df80 CWorldPhysicsManager__CreateThingByType` | Existing Wave556 row; xrefs from `CWorld__LoadWorld`, `CWorld__SpawnInitialThings`, `CSpawnerThng`, `CSquad`, `CWingmanStart`, and raw script/create fragments. |

Raw boundary follow-up:

- Fresh xref evidence still includes no-function callsite neighborhoods into the already named cluster: `0x0050a865`, `0x0050a845`, `0x005358a4`, `0x005367ee`, `0x005369fa`, `0x0053624d`, `0x0053628f`, `0x00536341`, `0x00536d3c`, and `0x004e63cf`.
- Context xrefs also show no-function neighborhoods at `0x00537185`, `0x00537c51`, `0x00462afc`, `0x004d027b`, `0x0045a979`, `0x0045aadf`, `0x004d35fb`, `0x004d6373`, and `0x004dfa78`.
- The raw windows around apparent standalone helpers `0x00537c40` and `0x004dfa47` are logged as follow-up boundary-recovery candidates. Wave1073 does not mutate them because the current tranche was scoped to the saved CWorld load/tail rows and their context, not a mixed raw-boundary recovery pass.

Read-back evidence:

- Primary exports: `23` metadata rows, `23` tag rows, `62` xref rows, `2095` function-body instruction rows, and `23` decompile rows.
- Context exports: `18` metadata rows, `18` tag rows, `362` xref rows, `6272` function-body instruction rows, and `18` decompile rows.
- Raw xref windows: `253` instruction rows around `11` no-function/raw-neighborhood callsite addresses.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1357/1560 = 86.99%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved Ghidra names, signatures, comments, and tags for the twenty-three primary Wave555/Wave556 rows remain internally coherent with fresh metadata, tag, xref, instruction, and decompile evidence.
- The CWorld load/tail rows still align with `CWorld__LoadWorld`, `CGame__LoadLevel`, resource-read, LOD/header, script-event, world-text, occupancy, WorldMeshList, initial-spawn, and WorldPhysicsManager factory context.
- The WorldMeshList rows remain tied to world loading, spawner init, script-object spawn collection, recursive child mesh collection, and CUnit mesh-use marking.
- The CreateThingByType row remains tied to world load, initial spawn, spawner, squad, wingman-start, and raw script/create callsite context.

What remains separate proof:

- Runtime world-load, script-event, world-text, mesh-list, spawn, occupancy, factory, and level-load behavior.
- Exact CWorld, CWorldMeshList, CWorldPhysicsManager, definition-list, world-text slot, object-pair, and script-event layouts.
- Exact raw-boundary identities for the no-function neighborhoods.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: prefer a small raw-boundary recovery tranche for the apparent standalone script/text/create fragments around `0x00537c40` and `0x004dfa47`, or continue the next expanded static re-audit cluster with read-only review first.

Probe token anchor: Wave1073; cworld-load-tail-review-wave1073; 0x0050a870 CWorld__ClearSetArrays; 0x0050ac70 CWorld__LoadScriptEvents; 0x0050b520 CWorld__LoadWorldFile; 0x0050d6a0 CWorld__PushWorldTextSlot; 0x0050d9e0 CWorldMeshList__Add; 0x0050dcb0 CWorld__SpawnInitialThings; 0x0050df80 CWorldPhysicsManager__CreateThingByType; 0x00537c40; 0x004dfa47; 812/1408 = 57.67%; 1357/1560 = 86.99%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified; read-only review.
