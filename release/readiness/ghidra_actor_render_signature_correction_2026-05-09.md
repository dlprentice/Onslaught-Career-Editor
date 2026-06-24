# Ghidra Actor Render Signature Correction - 2026-05-09

Status: public-safe saved-Ghidra name/signature/comment correction evidence, not final type/runtime proof

## Objective

Continue the saved-Ghidra static re-audit by revisiting the early `CActor` render/fraction cluster after source review showed that `0x00401b50` was incorrectly labeled as a CMCMine scale helper. This pass corrects three saved names, hardens their signatures, and saves proof-boundary comments without claiming concrete `CActor`, `FVector`, or `FMatrix` layouts.

## Inputs

- Targets:
  - `0x00401b50` `CActor__GetFractionTime`
  - `0x00401be0` `CActor__GetRenderPos`
  - `0x00401c50` `CActor__GetRenderOrientation`
- Raw evidence root: `subagents/ghidra-static-reaudit/actor-render-signature-correction/current/`
- Signature script: `tools/ApplyActorRenderSignatureCorrection.java`
- Probe: `tools/ghidra_actor_render_signature_correction_probe.py`
- Probe test: `tools/ghidra_actor_render_signature_correction_probe_test.py`

## Commands

Focused validation:

```powershell
py -3 tools\ghidra_actor_render_signature_correction_probe_test.py
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\actor-render-signature-correction\current\rename_map_actor_render_signature_correction.txt
cmd.exe /c npm run test:ghidra-actor-render-signature-correction
py -3 -m py_compile tools\ghidra_actor_render_signature_correction_probe.py tools\ghidra_actor_render_signature_correction_probe_test.py
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Mutation/read-back summary:

- Read-only metadata, decompile, xref, and instruction exports captured the selected early Actor render/fraction cluster.
- Headless rename dry/apply corrected `0x00401b50` from `CMCMine__ComputeClampedScaleFactor` to `CActor__GetFractionTime`.
- Headless rename dry/apply corrected `0x00401be0` and `0x00401c50` from generic `VFuncSlot_*` labels to `CActor__GetRenderPos` and `CActor__GetRenderOrientation`.
- Headless signature dry/apply hardened all three selected targets.
- Headless comment dry/apply saved proof-boundary comments for all three targets.
- Metadata, decompile, xref, instruction, and quality-snapshot read-back verified the saved project state.

## Result

```text
CActor render signature correction: PASS
Targets: 3
Renamed targets: 3
Signature-hardened targets: 3
Commented targets: 3
Stale token hits: 0
Comment overclaims: 0
Xref rows: 85
Instruction rows: 435
```

Saved signatures:

| Address | Saved signature |
| --- | --- |
| `0x00401b50` | `float __thiscall CActor__GetFractionTime(void * this)` |
| `0x00401be0` | `void __thiscall CActor__GetRenderPos(void * this, void * outRenderPos)` |
| `0x00401c50` | `void __thiscall CActor__GetRenderOrientation(void * this, void * outRenderOrientation)` |

Queue refresh after this pass:

- Total functions: `5866`
- Commented functions: `432`
- Commentless functions: `5434`
- Undefined signatures: `2076`
- `param_N` signatures: `2519`
- Uncertain owner names: `0`
- Address-suffixed helper names: `0`
- Address-suffixed wrapper names: `0`

## What This Proves

- The saved Ghidra project no longer carries `CMCMine__ComputeClampedScaleFactor` at `0x00401b50`.
- `0x00401b50` now matches the source `CActor::GetFractionTime()` shape: virtual `GetMoveMultiplier` call, timing/global frame-fraction context, `this+0xd8` last-move-time-style read, and fraction clamp behavior.
- `0x00401be0` now matches the source `CActor::GetRenderPos()` shape: hidden-return `FVector` output built from old/current position interpolation.
- `0x00401c50` now matches the source `CActor::GetRenderOrientation()` shape: hidden-return `FMatrix` output built from old/current orientation interpolation and row-copy helpers.
- The broad subclass DATA xrefs on `0x00401be0` and `0x00401c50` are now documented as inherited Actor render-slot usage rather than owner-specific leaf methods.

## What This Does Not Prove

- This does not prove concrete `CActor`, `FVector`, or `FMatrix` layouts.
- This does not add Ghidra tags, recover local variable names, or create structure types.
- This does not prove runtime rendering, animation interpolation, camera behavior, or frame pacing.
- This does not prove every subclass vtable owner for the inherited render slots.
- This does not prove rebuild parity.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, signatures, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
