# Ghidra InitThing Wave419 Static Correction

Date: 2026-05-14

## Summary

Wave419 saved a focused static-Ghidra correction for the InitThing queue head. The pass corrected the stale `0x0048dcf0` label from `CInfluenceMap__Init` to `CInitThing__ctor`, promoted the adjacent base copy and squad-load helpers, hardened the InitThing factory signature/comment, refreshed the full static re-audit queue, and backed up the live Ghidra project to `[maintainer-local-ghidra-backup-root]\BEA_20260514_143404_post_wave419_initthing_verified`.

This is public-safe saved static retail-binary evidence. It is not runtime level-load proof, not complete class-layout recovery, not local-variable/type recovery, and not rebuild parity.

## Saved Ghidra Changes

| Address | Saved state | Evidence boundary |
| --- | --- | --- |
| `0x0040e1b0` | `CInitThing__CopyFrom` | Corrected the old generic vtable-slot label to the source-aligned base copy helper for transform/orientation, script/name/spawn-script arrays, and tail fields. |
| `0x0048c650` | `InitThing__CreateThingByType` | Preserved the factory name while hardening the one-argument retail signature and source-aligned SpawnInitThing/OID allocation context. |
| `0x0048d8d0` | `CSquadInitThing__LoadFromMemBuffer` | Corrected the old vfunc-slot label to the source-aligned squad load wrapper over `CInitThing__LoadFromMemBuffer`, with version-gated squad mode state. |
| `0x0048dcf0` | `CInitThing__ctor` | Corrected the stale `CInfluenceMap__Init` label; the body seeds base CInitThing defaults and installs the base vtable at `0x005dc1cc`. |

Stuart's `InitThing.cpp` and `InitThing.h` remain useful architecture/name evidence here. The Steam retail Ghidra read-back remains the authority for the saved function boundaries, signatures, comments, and vtable-slot resolution.

## Validation

- Headless dry run: `updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`.
- Headless apply: `updated=4 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back exports verified `4` metadata rows, `4` tag rows, `79` xref rows, `740` instruction rows, `4` decompile exports, and `66` checked vtable-slot rows.
- Vtable read-back resolved base vtable `0x005dc1cc` slot `0` to `CInitThing__CopyFrom`, base slot `1` to `CInitThing__LoadFromMemBuffer`, and CSquad vtable `0x005dc1b0` slot `1` to `CSquadInitThing__LoadFromMemBuffer`.
- Focused probe tests passed: `py -3 tools\ghidra_initthing_wave419_probe_test.py`.
- Focused probe passed through npm: `cmd.exe /c npm run test:ghidra-initthing-wave419`.
- Python compile check passed for the Wave419 probe and tests.
- Full static queue refreshed to `6043` functions, `1644` commented functions, `4399` commentless functions, `1876` undefined signatures, and `1821` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1644/6043 = 27.21%`; strict comment-plus-clean-signature `1578/6043 = 26.11%`.
- Live Ghidra backup verification: `19` files, `155093895` bytes, `HashDiffCount=0`, and `MissingCount=0`.

## Not Proven

- Runtime level loading or object spawning is not proven.
- Complete CInitThing / CSquadInitThing concrete layouts are not proven.
- Exact local-variable names and recovered Ghidra data types remain open.
- The source `inReportErrors` factory parameter is not separately observed in the checked retail signature.
- BEA was not launched, patched, or debugged in this wave.
- This does not prove rebuild parity or game-behavior equivalence.
