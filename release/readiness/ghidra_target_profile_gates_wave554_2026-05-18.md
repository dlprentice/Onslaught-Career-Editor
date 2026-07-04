# Ghidra Target/Profile Gates Wave554 Readiness Note

Date: 2026-05-18

## Scope

Wave554 saved static Ghidra owner/signature/comment/tag hardening for eight target/profile gate helpers:

| Address | Saved state |
| --- | --- |
| `0x00509e40` | `void * __cdecl TargetSet__GetEntryByIndex(int target_entry_index)` |
| `0x00509e90` | `void * __fastcall ProjectileBurst__ResolvePresetByPercentBucketFallback(void * burst_context)` |
| `0x00509f70` | `int __fastcall TargetProfileContext__IsEligibleByDistanceBucketOrRange(void * target_context)` |
| `0x0050a080` | `int __fastcall TargetProfileContext__CanProceedByTargetRangeGate(void * target_context)` |
| `0x0050a0b0` | `uint __thiscall CSquadNormal__HasActiveMaskMatchWithTarget(void * this, void * target_unit)` |
| `0x0050a0d0` | `uint __thiscall CUnit__HasMaskBitsA8(void * this, uint mask_bits)` |
| `0x0050a0e0` | `void __thiscall OID__ComputeForwardProjectedPointTowardTarget(void * this, void * out_point, void * target_unit)` |
| `0x0050a290` | `int __fastcall CUnit__IsTargetTimeoutBeforeProfileLimit(void * unit)` |

## Evidence

- `ApplyTargetProfileGatesWave554.java` dry: `updated=0 skipped=8 renamed=0 would_rename=4 missing=0 bad=0`.
- Apply: `updated=8 skipped=0 renamed=4 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back artifacts under `subagents/ghidra-static-reaudit/wave554-target-profile-gates-00509e40/`: `8` metadata rows, `8` tag rows, `20` xref rows, `1416` target instruction rows, `46` focused OID callsite instruction rows, `8` target decompile exports, and `17` caller decompile exports.
- Focused probe: `py -3 tools\ghidra_target_profile_gates_wave554_probe.py --check` PASS.
- NPM probe: `cmd.exe /c npm run test:ghidra-target-profile-gates-wave554` PASS.
- Queue refresh: `cmd.exe /c npm run test:ghidra-static-reaudit-queue` PASS.

## Queue Telemetry

Fresh post-Wave554 queue:

| Metric | Value |
| --- | ---: |
| Function objects | 6089 |
| Functions with comments | 2680 |
| Commentless functions | 3409 |
| Exact `undefined` signatures | 1535 |
| Signatures still using `param_N` | 1262 |
| Comment-backed proxy | `2680/6089 = 44.01%` |
| Strict comment-plus-clean-signature proxy | `2626/6089 = 43.13%` |

These are queue telemetry only, not completion claims.

## Backup

Post-wave verified Ghidra backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260518-145328_post_wave554_target_profile_gates_verified
Files: 19
Bytes: 159484807
MissingCount: 0
ExtraCount: 0
HashDiffCount: 0
```

## Not Proven

Exact source identities, concrete target-set/target-profile/burst-context/OID/SquadNormal/Unit/profile/target layouts, exact vector width, timeout units, runtime targeting/projectile/squad behavior, BEA patching, and rebuild parity remain unproven.
