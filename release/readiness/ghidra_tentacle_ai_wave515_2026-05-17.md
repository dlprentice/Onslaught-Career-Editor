# Ghidra Tentacle / AI Wave515 Readiness

Status: static read-back complete
Date: 2026-05-17

## Scope

Wave515 saved signature/comment/tag hardening for 7 tentacle, TentacleAI, CMCTentacle, and adjacent CUnit helpers:

- `0x004f0760` `CTentacle__CreateTentacleGuide`
- `0x004f07e0` `CTentacle__CreateTentacleAI`
- `0x004f0860` `CTentacle__CreateWarspiteAI`
- `0x004f08f0` `CTentacleAI__scalar_deleting_dtor`
- `0x004f0910` `CTentacleAI__dtor_base`
- `0x004f0c50` `CMCTentacle__BuildOrientationMatrixFromEuler`
- `0x004f1220` `CUnit__GetSpeedScaleByFlag30C`

The pass applied 2 renames: the CTentacleAI scalar deleting destructor and adjacent destructor-base cleanup body.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave515-tentacle-ai-004f0760/pre_*`.
- Mutation script: `tools/ApplyTentacleAIWave515.java`.
- Dry run: `updated=0 skipped=7 renamed=0 would_rename=2 missing=0 bad=0`.
- Apply run: `updated=7 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`.
- Verify dry run: `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back: `7` metadata rows, `7` tag rows, `8` xref rows, `3507` instruction rows, and `7` decompile exports.
- Focused probe: `tools/ghidra_tentacle_ai_wave515_probe.py --check`.
- Queue refresh after Wave515: `6078` functions, `2411` commented, `3667` commentless, `1611` exact-undefined signatures, and `1424` `param_N` signatures.
- Current whole-project telemetry proxy: comment-backed `2411/6078 = 39.67%`; strict comment-plus-clean-signature proxy `2357/6078 = 38.78%`.
- Backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260517-202309_post_wave515_tentacle_ai_verified` with `19` files, `158436231` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Claim Boundary

This is static Ghidra metadata evidence only. It improves CTentacle factory, CTentacleAI destructor, CMCTentacle matrix, and CUnit speed-scale readability. It does not prove runtime tentacle behavior, runtime AI behavior, runtime spline motion behavior, exact source-body identity, concrete CTentacle/CTentacleAI/CMCTentacle/CUnit layouts, BEA patching, or rebuild parity.
