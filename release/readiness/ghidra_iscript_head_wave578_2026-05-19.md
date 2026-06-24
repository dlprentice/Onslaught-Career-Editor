# Wave578 IScript Head Static Ghidra Readiness

Date: 2026-05-19

## Scope

Wave578 saved a bounded static Ghidra correction tranche for the IScript head at `0x005333b0..0x00533840`.

Targets:

| Address | Saved state |
| --- | --- |
| `0x005333b0` | `void * __thiscall IScript__Constructor(void * this, void * owner_complex_thing, void * script_object_code)` |
| `0x00533430` | `void * __thiscall IScript__ScalarDeletingDestructor(void * this, byte flags)` |
| `0x00533450` | `void __thiscall IScript__Destructor(void * this)` |
| `0x00533500` | `void __thiscall IScript__CallEvent0AndRegisterNestedListeners(void * this)` |
| `0x005335a0` | `void __thiscall IScript__CallEventId6_OrReset(void * this)` |
| `0x005335d0` | `void __thiscall IScript__CreateThingRef(void * this, void * referenced_thing)` |
| `0x00533660` | `void __thiscall IScript__CallEventId5_OrReset(void * this)` |
| `0x00533690` | `void __thiscall IScript__CreateThingRefWithSquad(void * this, void * referenced_thing)` |
| `0x005337e0` | `void __thiscall IScript__CallEventId3_OrReset(void * this)` |
| `0x00533840` | `void __thiscall IScript__RestoreSavedStateAndGotoInstruction(void * this)` |

## Evidence

- `ApplyIScriptHeadWave578.java` dry run: `updated=0 skipped=10 renamed=0 would_rename=2 missing=0 bad=0`.
- Apply run: `updated=10 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`.
- Final dry read-back: `updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0`.
- Each headless run reported `REPORT: Save succeeded`.
- Post exports verified `10` metadata rows, `10` tag rows, `17` xref rows, `2610` target instruction rows, `10` decompile rows, and `288` vtable rows.
- The tranche corrected stale `CMonitor__ctor_like_005333b0` to `IScript__Constructor` and stale `IScript__ctor_like_00533450` to `IScript__Destructor`.
- The two CreateThingRef helpers are now documented as IScript thiscall `RET 0x4` helpers, not fixed three-stack-argument script-command handlers.

## Queue Telemetry

Post-Wave578 static re-audit queue:

| Metric | Value |
| --- | ---: |
| Function objects | 6093 |
| Commented functions | 2932 |
| Commentless functions | 3161 |
| Exact `undefined` signatures | 1423 |
| `param_N` signatures | 1131 |
| Comment-backed proxy | `2932/6093 = 48.12%` |
| Strict comment-plus-clean-signature proxy | `2881/6093 = 47.28%` |

Next queue head: `0x005339a0 IScript__GetSlotBitValue`.

## Backup

Verified Ghidra project backup:

- Path: `G:\GhidraBackups\BEA_20260519-034612_post_wave578_iscript_head_verified`
- Files: `19`
- Bytes: `160467847`
- Diff count: `0`
- Manifest SHA-256: `0461B29BD8FB6F10D5D17AE01BF4AB55FEA0068E75D4751C7B8DE548945EC860`

## Validation

- `py -3 tools\ghidra_iscript_head_wave578_probe.py --check --json`: PASS (`failureCount=0`).
- `cmd.exe /c npm run test:ghidra-iscript-head-wave578`: PASS.

## Not Proven

- runtime mission-script behavior remains unproven.
- Exact IScript/source hierarchy and the concrete object/datatype layouts remain unproven.
- Exact event-id enum names remain unproven.
- BEA executable patching and rebuild parity remain unproven.
