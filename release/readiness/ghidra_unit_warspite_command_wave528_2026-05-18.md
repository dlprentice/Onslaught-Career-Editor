# Ghidra Unit / Warspite Command Tail Wave528 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for Unit trigger/message helpers, script-driven Engine thing-name flags, SquadNormal active-reader/support selection helpers, UnitAI command-score accumulation, and Warspite init/update helpers.

## Scope

Wave528 hardened nine adjacent Unit, Engine, SquadNormal, UnitAI, and Warspite command-tail helpers using static retail Ghidra evidence only. No semantic renames were applied in this wave; the pass saved signatures, comments, and tags over existing function names.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004fe030` | `void __thiscall CUnit__TriggerEffect(void * this, void * trigger_context)` | `RET 0x4` proves one explicit trigger-context argument after ECX. The body gates weapon/mount compatibility through `trigger_context+0x138`, selects Tara/Billy/default pilot text IDs, allocates `CMessage`, and queues it through the global message box when present. |
| `0x004fe390` | `void __thiscall CEngine__EnableThingByNameFlag(void * this, void * thing_name)` | `RET 0x4` proves one script-provided thing-name argument after ECX. The body walks `this+0x18c`, compares entry profile/name pointers, and sets matched field `+0x3f4` to `1`. |
| `0x004fe3f0` | `void __thiscall CEngine__DisableThingByNameFlag(void * this, void * thing_name)` | `RET 0x4` proves one script-provided thing-name argument after ECX. The body walks `this+0x18c`, clears matched field `+0x3f4`, clears the active reader when it points at the matched entry, and refreshes support selection when present. |
| `0x004fe480` | `int __fastcall CEngine__DispatchBoundCallbackIfPresent(void * this)` | ECX-only helper checks `this+0x208` and dispatches callback/controller vfunc `+0x24` when present, otherwise returns `0`. |
| `0x004fe500` | `void __thiscall CSquadNormal__SetReaderAndUnregisterFromFactionSets(void * this, void * reader)` | `RET 0x4` proves one explicit reader argument after ECX. The body writes active-reader field `this+0x148` and removes this squad from global faction sets `DAT_008550c0` and `DAT_008550b0` when the reader is non-null. |
| `0x004fe540` | `void __thiscall CUnitAI__AccumulateForwardedCommandScore(void * this, int score_delta)` | `RET 0x4` proves one score-like argument after ECX. The caller provides the forwarded command score, and the body schedules event `0xfa5`, accumulates a scaled value into `this+0x218` with a cap, and writes cooldown/timer field `+0x21c` to `10`. |
| `0x004fe710` | `void * __thiscall CWarspite__Init(void * this, void * owner_unit, void * init_context)` | `RET 0x8` proves owner-unit and init-context stack arguments after ECX. The helper returns `this`, initializes active readers from init-context fields, schedules events `0x7d3`, `0xbb9`, and `0xbba`, and seeds oscillation fields when profile data is present. |
| `0x004fef40` | `float __fastcall CWarspite__Update(void * this)` | ECX-only vtable update returns a float-like value through the x87 path. The body advances Warspite state, checks owner-unit callbacks, updates aim/reader state, refreshes support selection, may call `CWarspite__TransitionToUndeploying`, and returns randomized timing/oscillation values. |
| `0x004ffdd0` | `void __thiscall CSquadNormal__SetReaderAndRefreshSupportSelection(void * this, void * reader, void * selection_context)` | `RET 0x8` proves two explicit stack arguments after ECX. The body writes active reader field `this+0xc`, refreshes support selection for `this+0x8`, and stores `selection_context` into `this+0x10`. |

## Evidence

- Mutation script: `tools/ApplyUnitWarspiteCommandWave528.java`
- Probe script: `tools/ghidra_unit_warspite_command_wave528_probe.py`
- Evidence root: `subagents/ghidra-static-reaudit/wave528-unit-warspite-command-004fe030/`
- Dry summary: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
- Apply summary: `updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back rows: `9` metadata rows, `9` tag rows, `119 target xref rows`, `3789` instruction rows, `9` target decompile exports, and `11` context decompile exports from `12` context targets.
- Focused probe: `py -3 tools\ghidra_unit_warspite_command_wave528_probe.py --check`
- NPM probe: `npm run test:ghidra-unit-warspite-command-wave528`
- Queue probe: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check`

## Queue Impact

Fresh queue after Wave528:

- Function objects: 6082
- Functions with comments: 2536
- Commentless functions: 3546
- Exact `undefined` signatures: 1590
- Signatures still using `param_N` names: 1330
- Comment-backed telemetry: `2536/6082 = 41.70%`
- Strict clean-signature telemetry: `2482/6082 = 40.81%`

These are queue telemetry only, not certification and not a milestone.

## Backup

Verified backup:

- Path: `[maintainer-local-ghidra-backup-root]\BEA_20260518-025058_post_wave528_unit_warspite_command_verified`
- Files: 19
- Bytes: 158927751
- MissingCount: 0
- ExtraCount: 0
- HashDiffCount: 0

## Boundaries

This is static retail Ghidra evidence only. Runtime AI behavior, runtime message/UI behavior, script command behavior, support selection behavior, exact owner/source identity, concrete Unit/Engine/SquadNormal/Warspite layouts, local-variable recovery, BEA patching, and rebuild parity remain unproven.
