# Ghidra Unit Support-Tail Wave540 Readiness Note

Date: 2026-05-18

## Scope

Wave540 saved static Ghidra name/signature/comment/tag corrections for eight adjacent Unit support-tail helpers:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x004fd230` | `CUnit__SpawnProfileDropPickup` | `void __fastcall CUnit__SpawnProfileDropPickup(void * this)` |
| `0x004fd3d0` | `CUnit__IsCandidateSideCompatibleForTargeting` | `bool __thiscall CUnit__IsCandidateSideCompatibleForTargeting(void * this, int candidate_side)` |
| `0x004fd500` | `CUnit__ApplyRenderPositionDeltaToVector` | `void __thiscall CUnit__ApplyRenderPositionDeltaToVector(void * this, void * inout_position)` |
| `0x004fd570` | `CSquadNormal__HasAnyLinkedUnitWithField94` | `bool __fastcall CSquadNormal__HasAnyLinkedUnitWithField94(void * this)` |
| `0x004fd5e0` | `CUnit__VFunc26_GetRecentSegmentDamageMeter` | `int __thiscall CUnit__VFunc26_GetRecentSegmentDamageMeter(void * this, int segment_index)` |
| `0x004fd6a0` | `CUnit__VFunc22_ActivateLinkedTargetsAndChildren` | `void __fastcall CUnit__VFunc22_ActivateLinkedTargetsAndChildren(void * this)` |
| `0x004fd700` | `CUnit__VFunc23_DeactivateLinkedTargetsAndChildren` | `void __fastcall CUnit__VFunc23_DeactivateLinkedTargetsAndChildren(void * this)` |
| `0x004fd760` | `CUnit__HasAnyLinkedUnitBeforeTargetTimeout` | `bool __fastcall CUnit__HasAnyLinkedUnitBeforeTargetTimeout(void * this)` |

The important corrections are stale owner cleanup and slot/signature hardening. `0x004fd230`, `0x004fd3d0`, `0x004fd500`, `0x004fd5e0`, `0x004fd6a0`, `0x004fd700`, and `0x004fd760` were renamed from weaker or stale labels; `0x004fd570` kept the existing `CSquadNormal` owner but gained tighter signature/comment evidence.

## Evidence

- Apply script: `tools/ApplyUnitSupportTailWave540.java`.
- Probe: `tools/ghidra_unit_support_tail_wave540_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave540-unit-support-tail-004fd230/`.
- Dry run: `updated=0 skipped=8 renamed=0 would_rename=7 missing=0 bad=0`.
- Apply: `updated=8 skipped=0 renamed=7 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back verified `8` metadata rows, `8` tag rows, `145` xref rows, `2088` instruction rows, `8` decompile exports, `30` caller decompile exports, and `2048` vtable rows.
- Focused probe: `py -3 tools\ghidra_unit_support_tail_wave540_probe.py --check` PASS.
- Npm wrapper: `cmd.exe /c npm run test:ghidra-unit-support-tail-wave540` PASS.
- Queue refresh: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check --json` PASS after refreshing the live quality snapshot.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-085137_post_wave540_unit_support_tail_verified`, `19` files, `159320967` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Queue Snapshot

Fresh queue telemetry after Wave540:

| Metric | Value |
| --- | ---: |
| Function objects | `6089` |
| Commented functions | `2643` |
| Commentless functions | `3446` |
| Exact-undefined signatures | `1535` |
| `param_N` signatures | `1298` |
| Comment-backed proxy | `2643/6089 = 43.41%` |
| Strict comment-plus-clean-signature proxy | `2586/6089 = 42.47%` |

This is telemetry only, not a completion milestone.

## Not Proven

- Runtime pickup spawning, targeting/faction behavior, HUD marker behavior, squad formation behavior, activation/deactivation behavior, or damage-meter behavior.
- Exact `CUnit`, `CSquadNormal`, profile, reader/list, segment-controller, or target layouts beyond observed offsets.
- Exact source-body identity; source and caller/vtable context are supporting evidence only here.
- BEA launch, executable patching, and rebuild parity.
