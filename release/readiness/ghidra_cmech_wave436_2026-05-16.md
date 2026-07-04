# Ghidra CMech Wave436 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave436 corrected six CMech-adjacent and barrel/spinner mesh-token targets. It fixed two backwards or underspecified `CMeshPart` helper names, kept the shared vtable-slot `9` initializer owner-neutral, and saved bounded signatures/comments/tags for CMech leg-motion, cockpit/AI, and targeting/guide initialization.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x0049f600` | `CMeshPart__NameAvoidsBarrelSpinnerOptimizationTokens` | Corrected the old backwards token-match wording; the helper returns false for protected barrel/spinner optimization names and true otherwise. |
| `0x0049f670` | `CMeshPart__AnyChildNameMatchesBarrelSpinnerOptimizationTokens` | Scans child/subpart names through the `+0x15c`/`+0x160` child range for the same barrel/spinner token set. |
| `0x0049f820` | `SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820` | Shared slot-9 initializer referenced by vtables `0x005e0684` and `0x005e3074`; calls the ground-unit init path and vfunc slots `117`, `118`, and `119`. |
| `0x0049f940` | `CMech__InitLegMotion` | Finds `LegMotion`, allocates a `0xf0`-byte leg-motion controller, stores it at `this+0x70`, and initializes motion parameters from the init context plus `0.4`/`0.9` constants. |
| `0x0049fa30` | `CMech__InitCockpit` | Allocates a `0x64`-byte pool-`0x16` cockpit/AI object, calls the constructor-like initializer, and stores the result at `this+0x13c`. |
| `0x0049faa0` | `CMech__InitTargeting` | Allocates a `0x48`-byte pool-`0x17` guide/targeting object, calls the constructor-like initializer, and stores the result at `this+0x208`. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 -m py_compile tools\ghidra_cmech_wave436_probe.py tools\ghidra_cmech_wave436_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_cmech_wave436_probe_test.py` | PASS | Focused tests passed `4/4`. |
| Headless `ApplyCMechWave436.java` dry/apply/verify | PASS | Dry `updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`; apply `updated=6 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`; verify dry `updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`; apply passes included `REPORT: Save succeeded`. |
| Post-apply metadata/tag/xref/vtable/instruction/decompile read-back | PASS | Verified `6` metadata rows, `6` tag rows, `13` xref rows, `8` relevant vtable-slot rows, `1566` instruction rows, and `6` target decompile exports. |
| `cmd.exe /c npm run test:ghidra-cmech-wave436` | PASS | Focused probe returned `status: PASS` for all `6` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6055` total functions, `1797` commented functions, `4258` commentless functions, `1801` undefined signatures, and `1759` `param_N` signatures. |
| Actual Ghidra project backup verification after Wave436 mutation | PASS | Copied the live project to `[maintainer-local-ghidra-backup-root]\BEA_20260516-013200_post_wave436_cmech_verified`; compared `19` files and `155913095` bytes with `MissingCount=0`, `HashDiffCount=0`, and `ExtraCount=0`. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6055`
- Commented function objects: `1797`
- Commentless function objects: `4258`
- `undefined` signatures: `1801`
- Signatures still using `param_N`: `1759`

Telemetry-only proxies are comment-backed `1797/6055 = 29.68%` and strict clean-signature `1735/6055 = 28.65%`. These are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime mech leg/cockpit/targeting behavior; exact concrete layouts beyond observed offsets; exact virtual method names; exact local variable names/types; exact source-body identity; source-to-retail rebuild parity; BEA launch behavior; game patching; or runtime gameplay behavior.
