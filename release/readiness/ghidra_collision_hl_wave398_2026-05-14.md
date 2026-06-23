# Ghidra High-Level Collision Detector Correction Tranche - 2026-05-14

Status: public-safe static evidence note

This note records a serialized static Ghidra correction wave for seven high-level collision detector and map/who collision sweep targets. It documents saved Ghidra metadata only. It does not include private decompile excerpts, private screenshots, copied executables, copied saves, raw runtime evidence, or private asset payloads.

## What Changed

| Address | Saved state | Public-safe evidence summary |
| --- | --- | --- |
| `0x00480a30` | `void __thiscall CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions(void * this, void * collision_component)` | Corrected the older `CCollisionSeekingRound` owner label to `CHLCollisionDetector` context. Static read-back shows collision component storage, MapWho neighbor-sector scanning, top-layer quad traversal, candidate filtering, pair dispatch, and unexpected collision-change warning context. |
| `0x00480c90` | `void __thiscall CHLCollisionDetector__HandleCollisionEnter(void * this, void * candidate_component)` | Removed the stale extra parameter and saved enter-callback context. Static read-back shows the checks counter, targeting-position/radius comparison, `0x100` collision-filter checks, current-component enter callback, and follow-up dispatch/scheduling context. |
| `0x00480db0` | `void __thiscall CHLCollisionDetector__HandleCollisionExit(void * this, void * candidate_component)` | Removed the stale extra parameter and saved exit-callback context. Static read-back shows null/self rejection, mutual filters, unexpected collision-change warning, pair dispatch, and flag clear context. |
| `0x00480e10` | `void __thiscall CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions(void * this, void * mapwho_entry_or_quad_node)` | Corrected the older `CCollisionSeekingRound` owner label to `CHLCollisionDetector` context. Static read-back shows recursive four-child traversal, shared MapWho iterator usage, candidate collision-component resolution, mutual filters, and pair dispatch. |
| `0x00480ed0` | `void __thiscall CHLCollisionDetector__DispatchCollisionEventForPair(void * this, void * candidate_component)` | Removed the stale extra parameter and saved pair-dispatch context. Static read-back shows too-many-objects warning, targeting-position comparison, separation-distance calculation, event `2000` scheduling through `EVENT_MANAGER`, and saved event-pointer reuse. |
| `0x00481060` | `void __thiscall CHLCollisionDetector__ProcessMapWhoCollisionSweep(void * this, void * previous_sector, void * current_sector)` | Removed the stale extra parameter and saved the two-sector sweep shape. Static read-back shows previous/current sector comparison, layer descent, neighbor-cell scanning, exit callbacks, and pair dispatch for newly entered cells. |
| `0x004812d0` | `void __thiscall CHLCollisionDetector__HandleScheduledCollisionEvent(void * this, void * event)` | Renamed the vfunc-style label to scheduled event handling. Static read-back shows event number `2000`, event data pointer use, event-pointer reuse, `HandleCollisionEnter` dispatch, and detector field cleanup. |

## Validation

- `ApplyCollisionHLWave398.java` dry run: expected no mutation and reported seven skipped targets with three would-rename corrections.
- `ApplyCollisionHLWave398.java` apply run: saved the project and reported seven updated targets with three renamed targets.
- Metadata/decompile/xref/tag/instruction read-back is stored under ignored `subagents/`.
- Focused probe: `tools/ghidra_collision_hl_wave398_probe.py --check`.
- Self-test: `tools/ghidra_collision_hl_wave398_probe_test.py`.

## Claim Boundary

This tranche narrows static high-level collision detector ownership/signature evidence and saves those corrections in Ghidra. It does not prove runtime collision behavior, does not prove exact source identity for every branch, does not recover concrete structure types/locals, does not launch or patch `BEA.exe`, and does not prove rebuild parity.
