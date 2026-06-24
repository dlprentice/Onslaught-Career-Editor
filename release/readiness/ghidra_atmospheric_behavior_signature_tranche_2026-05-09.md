# Ghidra Atmospheric Behavior Signature Tranche - 2026-05-09

Status: public-safe saved-Ghidra signature/comment evidence, not final type/source/runtime proof

## Objective

Continue the saved-Ghidra static re-audit by revisiting the remaining named CAtmospheric behavior helpers after the earlier lifecycle/list tranche. This pass hardens only the four function signatures whose current decompile, xref, and instruction read-back support stable calling conventions and parameters.

## Inputs

- Targets:
  - `0x00404210` `CAtmospheric__Process`
  - `0x00404790` `CAtmospheric__UpdateBlendState`
  - `0x00404860` `CAtmospheric__ConfigureTrail`
  - `0x004048c0` `CAtmospheric__GetInterpolatedBlendValue`
- Raw evidence root: `subagents/ghidra-static-reaudit/atmospheric-behavior-signature-tranche/current/`
- Signature script: `tools/ApplyAtmosphericBehaviorSignatureTranche.java`
- Probe: `tools/ghidra_atmospheric_behavior_signature_tranche_probe.py`
- Probe test: `tools/ghidra_atmospheric_behavior_signature_tranche_probe_test.py`

## Commands

Focused validation:

```powershell
py -3 tools\ghidra_atmospheric_behavior_signature_tranche_probe_test.py
py -3 tools\ghidra_atmospheric_behavior_signature_tranche_probe.py --check
py -3 -m py_compile tools\ghidra_atmospheric_behavior_signature_tranche_probe.py tools\ghidra_atmospheric_behavior_signature_tranche_probe_test.py
cmd.exe /c npm run test:ghidra-atmospheric-behavior-signature-tranche
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Mutation/read-back summary:

- Read-only metadata/decompile/xref/instruction exports captured the four selected CAtmospheric behavior targets.
- Headless signature dry/apply updated all four targets.
- Headless comment dry/apply saved proof-boundary comments for the same four targets.
- Metadata, decompile, xref, and instruction read-back verified the saved signatures/comments.

## Result

```text
Atmospheric behavior signature tranche: PASS
Targets: 4
Signature-hardened targets: 4
Stale param signatures: 0
Comment overclaims: 0
Xref rows: 4
Instruction rows: 1684
```

Saved signatures:

| Address | Saved signature |
| --- | --- |
| `0x00404210` | `void __fastcall CAtmospheric__Process(void * this)` |
| `0x00404790` | `void __fastcall CAtmospheric__UpdateBlendState(void * this)` |
| `0x00404860` | `bool __thiscall CAtmospheric__ConfigureTrail(void * this, int samplerIndex, int resetBlendPosition, int blendMode)` |
| `0x004048c0` | `double __fastcall CAtmospheric__GetInterpolatedBlendValue(void * this)` |

Queue refresh after this pass:

- Total functions: `5866`
- Commented functions: `418`
- Commentless functions: `5448`
- Undefined signatures: `2078`
- `param_N` signatures: `2531`
- Uncertain owner names: `0`
- Address-suffixed helper names: `0`
- Address-suffixed wrapper names: `0`

## What This Proves

- The four selected CAtmospheric behavior helpers no longer carry stale object-pointer `param_1` signatures in the saved Ghidra project.
- `CAtmospheric__ConfigureTrail` now has a saved three-stack-argument `__thiscall` boolean signature matching the observed `ret 0xc` and post-signature decompile `return true` shape.
- The saved comments record bounded evidence for the process/update loop, blend-state update, trail configuration, and interpolated blend accessor.
- The comments and probe explicitly guard against runtime/source/type overclaims.

## What This Does Not Prove

- This does not prove the concrete CAtmospheric structure layout.
- This does not prove exact Stuart-source method identity; the checked source corpus does not currently include a dedicated `Atmospherics.cpp`.
- This does not add Ghidra tags, recover local variable names, or create structure types.
- This does not prove runtime atmospheric, weather, particle, trail, or rendering behavior.
- This does not prove rebuild parity.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, signatures, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
