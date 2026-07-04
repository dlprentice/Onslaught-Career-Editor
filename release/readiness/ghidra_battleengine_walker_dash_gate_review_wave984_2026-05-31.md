# Ghidra BattleEngine Walker Dash Gate Review Wave984 (2026-05-31)

Status: read-only static review
Date: 2026-05-31
Branch: `main`
Tag: `battleengine-walker-dash-gate-review-wave984`

## Scope

Wave984 re-reviewed the BattleEngine walker dash/special-move gate and its Morph caller after the Wave900-Wave983 recheck gate.

| Address | Saved name | Result |
| --- | --- | --- |
| `0x0040a580` | `CBattleEngine__Morph` | Reviewed; no mutation |
| `0x00412d80` | `CBattleEngineWalkerPart__Forward` | Reviewed; no mutation |
| `0x00412f70` | `CBattleEngineWalkerPart__Backward` | Reviewed; no mutation |
| `0x00413160` | `CBattleEngineWalkerPart__StrafeLeft` | Reviewed; no mutation |
| `0x00413360` | `CBattleEngineWalkerPart__StrafeRight` | Reviewed; no mutation |
| `0x004135d0` | `CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove` | Reviewed; no mutation |
| `0x004135e0` | `CBattleEngineWalkerPart__ActivateLandingJets` | Reviewed; no mutation |
| `0x00413760` | `CBattleEngineWalkerPart__Move` | Reviewed; no mutation |

No Ghidra mutation was performed. The pass made no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, and did not launch BEA.

## Evidence

Fresh read-only artifacts are under the ignored private evidence root:

```text
subagents/ghidra-static-reaudit/wave984-battleengine-walker-dash-gate-review/
```

Read-back result:

```text
metadata: 8/8 OK
tags: 8/8 OK
xrefs: 14 rows
instructions: 1084 rows
decompile: 8/8 OK
queue: 6222/6222, 0 commentless, 0 undefined signatures, 0 param_N
```

Normalized progress tokens:

```text
static closure: 6222/6222 = 100.00%
Wave911 focused re-audit progress: 392/1408 = 27.84%
expanded static surface progress: 451/1478 = 30.51%
```

## Review Result

Fresh Ghidra evidence confirms the current saved names are coherent:

- `0x004135d0 CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove` returns whether the WalkerPart dash/special-walker counter at `this+0x44` is active.
- `0x0040a580 CBattleEngine__Morph` calls `CBattleEngineJetPart__IsStateMachineActive` and then `CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove` before either transform branch.
- The Morph body still contains the `s_flytowalk_006234bc` and `s_walktofly_006234b0` transition animation strings and transform event IDs `0x1771` and `6000`.
- The four dash direction helpers keep the saved WalkerPart owner names and one-float `__thiscall` signatures.
- `0x004135e0 CBattleEngineWalkerPart__ActivateLandingJets` and `0x00413760 CBattleEngineWalkerPart__Move` remain the Wave308 source-parity labels, not the Wave307 intermediate velocity-latch/monitor labels.

This normalizes the current static evidence for `transform_reject_special_moves`, `transform_morph_method_anchor`, `transform_jet_to_walker_event`, and `transform_walker_to_jet_energy_gate`. Older 2026-05-06/2026-05-07 candidate docs and scratch exports that refer to `0x0040a580 CMonitor__UpdateFlightWalkerTransitionState` or `0x004135d0 CGeneralVolume__IsDashLockoutActive` are historical provisional labels, not current saved Ghidra truth.

## Backup

Verified post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260531-005829_post_wave984_battleengine_walker_dash_gate_review_verified
files=19
bytes=173837191
MissingCount=0
ExtraCount=0
DiffCount=0
HashDiffCount=0
```

## Truth Boundary

This review proves static Ghidra coherence for the selected BattleEngine/WalkerPart dash and Morph-gate helpers only. It does not prove exact `CBattleEngine` or `CBattleEngineWalkerPart` structure layouts, runtime dash behavior, runtime transform rejection, runtime landing-jets or movement behavior, BEA patch behavior, or rebuild parity.
