# Ghidra TLS/Float/Lock Wave626 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave626 hardened nineteen adjacent TLS, cleanup, FPU/float-format, and CRT lock helper rows in the saved Ghidra project:

- `0x00560b2c CTexture__InitializeThreadLocalState`
- `0x00560b80 CTexture__InitializeThreadLocalRecordDefaults`
- `0x00560b93 CRT__GetOrInitThreadLocalRecord`
- `0x00560bfa CDXTexture__InvokeTlsCleanupCallbackAndFinalize`
- `0x00560c5b CDXTexture__InvokeGlobalCleanupCallbackAndFinalize`
- `0x00560cb1 CRT__InitFpuControlWord_0x10000_0x30000`
- `0x00560cc3 CDXTexture__ProbeFeatureModuloGate`
- `0x00560d01 CDXTexture__ProbeProcessorFeaturePresentOrFallback`
- `0x00560d2a CRT__InsertDecimalSeparatorBeforeExponent`
- `0x00560dea __fassign`
- `0x00560e28 CRT__FormatFloatScientificFromLongDouble`
- `0x00560e89 CRT__FormatFloatScientificCore`
- `0x00560f4b CRT__FormatFloatFixedFromLongDouble`
- `0x00560fa0 CRT__FormatFloatFixedCore`
- `0x00561047 CRT__FormatFloatGeneral_SelectStyle`
- `0x0056112b CRT__ShiftStringRightInPlace`
- `0x00561150 CTexture__InitializeGlobalCriticalSections`
- `0x00561179 CRT__LockByIndex`
- `0x005611da CRT__UnlockByIndex`

The pass saved bounded signatures, comments, and tags. It corrected the address-suffixed `CRT__InsertDecimalSeparatorBeforeExponent_00560d2a` label to `CRT__InsertDecimalSeparatorBeforeExponent`. It made no function-boundary changes and no executable byte changes.

## Evidence

- Dry mode reported `updated=0 skipped=19 renamed=0 would_rename=1 missing=0 bad=0`.
- Apply reported `updated=19 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry reported `updated=0 skipped=19 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post-state exports verified `19` metadata rows, `19` tag rows, `139` xref rows, `1653` instruction rows, and `19` clean decompile rows.
- TLS evidence covers global critical-section initialization, TLS slot allocation, 0x74-byte per-thread record creation, default record seeding, lazy TLS access, callback cleanup, and fatal-finalize routing.
- Float-format evidence covers decimal-separator insertion, `__fassign`, scientific/fixed/general formatting, locale decimal separator insertion, right-shift/memmove support, and FPU control-word startup.
- Lock evidence covers lazy critical-section allocation through CRT lock index `0x11`, indexed lock enter, and indexed lock leave.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260520-064302_post_wave626_tls_float_lock_verified` with `19` files, `162106247` bytes, and `DiffCount=0`.

## Queue Telemetry

Post-Wave626 queue telemetry:

- Total functions: `6093`
- Commented functions: `3296`
- Commentless functions: `2797`
- Exact `undefined` signatures: `1217`
- `param_N` signatures: `993`
- Comment-backed proxy: `3296/6093 = 54.09%`
- Strict clean-signature proxy: `3244/6093 = 53.24%`

Delta from Wave625: `+18` commented, `-18` commentless, exact-`undefined` signatures unchanged, `-10` `param_N`, and `+18` strict clean-signature rows. Nineteen rows were hardened; `__fassign` already carried a Ghidra library-match comment before the wave.

The next high-signal queue head is `0x00561618 CRT__ExtractFiniteExponentMaskOrPassThrough_00561618`.

## Boundaries

This is static saved-Ghidra TLS/float-format/lock evidence only. Exact CRT identity/version, exact TLS record and decimal-record layouts, full locale/FPU/formatting semantics, runtime texture/error/format behavior, BEA patching, and rebuild parity remain deferred.
