# Ghidra CComplexThing / CAnimation Wave517 Readiness

Status: static read-back complete
Date: 2026-05-17

## Scope

Wave517 saved name/signature/comment/tag hardening for 18 CComplexThing, CAnimation, and adjacent CThing animation helpers:

- `0x004046d0` `CAnimation__ctor`
- `0x00404790` `CAnimation__Process`
- `0x00404860` `CAnimation__SetAnimMode`
- `0x004048c0` `CAnimation__GetRenderFrame`
- `0x004f3c80` `CThing__GetRenderThingFrameIncrement`
- `0x004f3e10` `CComplexThing__ctor_base`
- `0x004f3ee0` `CComplexThing__scalar_deleting_dtor`
- `0x004f3f00` `CComplexThing__dtor_base`
- `0x004f3fd0` `CComplexThing__Init`
- `0x004f4120` `CComplexThing__SetName`
- `0x004f41b0` `CComplexThing__Shutdown`
- `0x004f4230` `CComplexThing__SetScript`
- `0x004f43d0` `CComplexThing__AddShutdownEvent`
- `0x004f4430` `CComplexThing__StartDieProcess`
- `0x004f4480` `CComplexThing__Hit`
- `0x004f44a0` `CComplexThing__SetAnimMode`
- `0x004f45a0` `CComplexThing__FinishedPlayingCurrentAnimation`
- `0x004f45e0` `CComplexThing__SetVar`

The pass applied 13 renames, including superseding older `CAtmospheric__Constructor`, `CAtmospheric__UpdateBlendState`, `CAtmospheric__ConfigureTrail`, `CAtmospheric__GetInterpolatedBlendValue`, `CAtmospheric__GetSamplerValueOrDefault`, `CThing__SetName`, `CThing__SetSound`, `CThing__AddTrail`, and `CUnit__ResumeSavedScriptIfPresent` labels where current evidence points to CAnimation / CComplexThing behavior.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave517-ccomplexthing-tail-004f3e10/pre_*` and `animation_crosscheck/*`.
- Mutation script: `tools/ApplyCComplexThingAnimationWave517.java`.
- Dry run: `updated=0 skipped=18 renamed=0 would_rename=13 missing=0 bad=0`.
- Apply run: `updated=18 skipped=0 renamed=13 would_rename=0 missing=0 bad=0`.
- Verify dry run: `updated=0 skipped=18 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back: `18` metadata rows, `18` tag rows, `415` xref rows, `5202` instruction rows, and `18` decompile exports.
- Focused probe: `tools/ghidra_ccomplexthing_animation_wave517_probe.py --check`.
- Queue refresh after Wave517: `6078` functions, `2443` commented, `3635` commentless, `1608` exact-undefined signatures, and `1396` `param_N` signatures.
- Current whole-project telemetry proxy: comment-backed `2443/6078 = 40.19%`; strict comment-plus-clean-signature proxy `2389/6078 = 39.31%`.
- Backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260517-212455_post_wave517_ccomplexthing_animation_verified` with `19` files, `158567303` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Claim Boundary

This is static Ghidra metadata evidence only. It improves source-parity readability for CComplexThing construction, init, naming, mission-script, shutdown, hit/death, SetVar, and animation helpers. It does not prove runtime animation behavior, runtime mission-script behavior, exact CComplexThing or CAnimation layouts, exact source-body identity for every optimized retail helper, BEA patching, or rebuild parity.
