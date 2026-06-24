# Ghidra CMCMine / CMCSentinel Wave434 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-15
Scope: saved retail `BEA.exe` Ghidra create/name/signature/comment/tag correction

## Summary

Wave434 corrected the adjacent `CMCMine` and `CMCSentinel` motion-controller cluster. It fixed seven lifecycle/vtable labels and recovered two missing vtable-slot function boundaries from the corrected vtable starts at `0x005dc3f4` (`CMCMine`) and `0x005dc420` (`CMCSentinel`).

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x0049c3e0` | `CMCMine__Constructor` | `RET 0x4`; calls the base motion-controller constructor, installs vtable `0x005dc3f4`, stores the owner mine at `+0x08`, and returns `this`. |
| `0x0049c400` | `CMCMine__ScalarDeletingDestructor` | Delete-flags wrapper for `CMCMine__Destructor`; frees through `OID__FreeObject` only when flag bit 0 is set. |
| `0x0049c420` | `CMCMine__Destructor` | Restores vtable `0x005dc3f4`, clears owner `+0x08`, seeds cached `+0x0c` with `0xc7c34ff3`, and tails into the base motion-controller destructor. |
| `0x0049c440` | `CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440` | Vtable slot 4; reads owner `+0x08`, checks the first stack argument at `+0x88`, adjusts the second transform argument at `+0x08` using owner `+0x250/+0x254`, refreshes cached `+0x0c`, and ends with `RET 0x10`. |
| `0x0049c4b0` | `CMCMine__VFunc_08_CheckCachedHeightState_0049c4b0` | Created vtable slot-8 boundary; compares cached `this+0x0c` against owner `+0x250` and returns true when the cached value differs. |
| `0x0049c5d0` | `CMCSentinel__Constructor` | `RET 0x4`; calls the base motion-controller constructor, installs vtable `0x005dc420`, stores the owner sentinel at `+0x08`, and seeds cached `+0x0c/+0x10` with `0xc479c000`. |
| `0x0049c600` | `CMCSentinel__ScalarDeletingDestructor` | Delete-flags wrapper for `CMCSentinel__Destructor`; frees through `OID__FreeObject` only when flag bit 0 is set. |
| `0x0049c620` | `CMCSentinel__Destructor` | Restores vtable `0x005dc420`, clears owner `+0x08`, and tails into the base motion-controller destructor. |
| `0x0049c640` | `CMCSentinel__VFunc_04_UpdateX1TurretOrBarrelTransform_0049c640` | Created vtable slot-4 boundary; checks mesh-part tokens `X1 turret` and `X1 barrel`, performs shared matrix/vector transform work, writes transform outputs, refreshes cached `+0x0c/+0x10` from owner `+0xe0/+0xe8`, and ends with `RET 0x10`. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 -m py_compile tools\ghidra_cmcmine_sentinel_wave434_probe.py tools\ghidra_cmcmine_sentinel_wave434_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_cmcmine_sentinel_wave434_probe_test.py` | PASS | Focused tests passed `4/4`. |
| Expected-red `py -3 tools\ghidra_cmcmine_sentinel_wave434_probe.py --check` before apply | PASS | Probe failed before mutation because expected dry/apply/read-back evidence was not present yet. |
| Headless `ApplyCmcMineSentinelWave434.java` dry/apply | PASS | Dry `updated=0 skipped=7 created=0 would_create=2 renamed=0 would_rename=7 missing=0 bad=0`; apply `updated=9 skipped=0 created=2 would_create=0 renamed=7 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Post-apply verify dry | PASS | `updated=0 skipped=9 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`. |
| Post-apply metadata/tag/xref/vtable/instruction/decompile read-back | PASS | Verified `9` metadata rows, `9` tag rows, `11` xref rows, `32` vtable-slot rows, `945` instruction rows, and `9` target decompile exports. |
| `cmd.exe /c npm run test:ghidra-cmcmine-sentinel-wave434` | PASS | Focused probe returned `status: PASS` for all `9` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6051` total functions, `1773` commented functions, `4278` commentless functions, `1811` undefined signatures, and `1768` `param_N` signatures. |
| Actual Ghidra project backup verification after Wave434 mutation | PASS | Copied the live project to `G:\GhidraBackups\BEA_20260515-223534_post_wave434_cmcmine_sentinel_verified`; compared `19` files and `155814791` bytes with `MissingCount=0`, `HashDiffCount=0`, and `ExtraCount=0`. |

An initial overlapped read-only instruction export hit a Ghidra project `LockException`; it was rerun serially before final read-back, and no mutation was running during that failed export.

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6051`
- Commented function objects: `1773`
- Commentless function objects: `4278`
- `undefined` signatures: `1811`
- Signatures still using `param_N`: `1768`

Telemetry-only proxies are comment-backed `1773/6051 = 29.30%` and strict clean-signature `1711/6051 = 28.28%`. These are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime mine/sentinel motion behavior; exact `CMCMine` or `CMCSentinel` concrete layouts beyond observed offsets; exact virtual method names; exact local variable names/types; exact source-body identity; source-to-retail rebuild parity; BEA launch behavior; game patching; or runtime gameplay behavior.
