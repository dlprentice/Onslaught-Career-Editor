# Ghidra Signature Debt Wave789 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `signature-debt-wave789`

Wave789 signature debt saved Ghidra comments, tags, and parameter-hardened signatures for five existing function rows whose remaining `param_N` names were directly supported by caller/decompile evidence. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Target rows:

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x00410c50 CMonitor__UpdateMovementTransitionAndEffects` | `void __fastcall CMonitor__UpdateMovementTransitionAndEffects(void * monitor)` | Sole checked caller `CMonitor__Process`; body repeatedly uses the ECX object as monitor state while updating tracked render pairs, movement/terrain integration, transition timers, impact effects, and hostile-environment penalty. |
| `0x00412ad0 CMonitor__UpdateSurfaceAlignmentAngle` | `void __fastcall CMonitor__UpdateSurfaceAlignmentAngle(void * monitor)` | Caller `CBattleEngineWalkerPart__Move`; body uses monitor fields at `+0x20`, `+0x24`, and `+0x28` while updating the wrapped surface-alignment angle. |
| `0x00414b30 TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit` | `int __fastcall TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit(void * target_set)` | Two calls from `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`; body scans a linked target/unit set and calls `CUnit__IsTargetTimeoutBeforeProfileLimit`. |
| `0x00418090 OpeningAnimationStateCallback__StartOpeningIfPending` | `int __fastcall OpeningAnimationStateCallback__StartOpeningIfPending(void * state_record)` | DATA xref `0x005d9080`; body uses state/timer fields `+0x254` and `+0x25c`, the `s_opening_00623ba4` string, `FindAnimationIndex`, and animation start vcall `+0xf0`. |
| `0x004879e0 CHud__RenderOverlayForViewpoint` | `void __thiscall CHud__RenderOverlayForViewpoint(void * this, void * viewpoint, int viewpoint_index, float unused_overlay_param)` | Caller `CHud__RenderOverlay`; body uses `viewpoint` and `viewpoint_index` for overlay state while the fourth float is not read in the exported decompile. |

Read-back evidence:

- `ApplySignatureDebtWave789.java dry`: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0`
- `ApplySignatureDebtWave789.java apply`: `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0`
- `ApplySignatureDebtWave789.java final dry`: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 5 metadata rows, 5 tag rows, 6 xref rows, 185 instruction rows, and 5 decompile rows.
- Queue after Wave789: 6098 total, 5544 commented, 554 commentless, 31 exact-undefined signatures, 22 `param_N`, comment-backed proxy `5544/6098 = 90.92%`, strict clean-signature proxy `5491/6098 = 90.05%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- The commentless high-signal queue remains empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-021024_post_wave789_signature_debt_verified`, 19 files, 171215751 bytes, `DiffCount=0`.

What this proves:

- The five target rows exist in the saved Ghidra project.
- The saved signatures replace the prior remaining `param_N` names with bounded names supported by static caller/decompile evidence.
- The saved comments and tags include `signature-debt-wave789` and `wave789-readback-verified`.
- The observed behavior is static retail Ghidra evidence tied to read-back metadata, decompile, instruction, xref, and queue exports.

What remains unproven:

- Exact source method identity.
- Concrete class/object layouts.
- Runtime behavior.
- BEA patching behavior.
- Rebuild parity.
