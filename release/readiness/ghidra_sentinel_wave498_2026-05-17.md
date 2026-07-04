# Ghidra Sentinel Wave498 Readiness Note

Date: 2026-05-17

## Scope

Wave498 saved static Ghidra boundary/name/signature/comment/tag hardening for seven gameplay `CSentinel` functions:

| Address | Saved state |
| --- | --- |
| `0x004dea50` | `void __thiscall CSentinel__Init(void * this, void * init_data)` |
| `0x004dec00` | `void * __thiscall CSentinel__ScalarDeletingDestructor(void * this, byte flags)` |
| `0x004dec20` | `void __fastcall CSentinel__Destructor(void * this)` |
| `0x004decc0` | `void __fastcall CSentinel__UpdateFlamethrowers(void * this)` |
| `0x004ded30` | `void __fastcall CSentinel__Activate(void * this)` |
| `0x004ded60` | `int __fastcall CSentinel__Deactivate(void * this)` |
| `0x004dee00` | `int __thiscall CSentinel__CheckWeaponSlot(void * this, void * weapon_context)` |

Wave498 supersedes the older `0x004dea50` constructor/manual-creation note. The saved read-back evidence supports `CSentinel__Init`: primary table `0x005e0904` slot 0 points to it, `RET 0x4` confirms one `init_data` stack argument after `this`, and the body delegates to `CGroundUnit__Init` before attaching Sentinel helper components.

## Evidence

- Apply script: `tools/ApplySentinelWave498.java`
- Probe: `tools/ghidra_sentinel_wave498_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave498-sentinel-safeside-004de1d0/`
- Dry/apply/verify:
  - Initial dry: `updated=0 skipped=6 created=0 would_create=1 renamed=0 would_rename=1 missing=0 bad=0`
  - Initial apply: `updated=7 skipped=0 created=1 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`
  - Void correction apply: `updated=1 skipped=6 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
  - Int correction apply: `updated=1 skipped=6 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
  - Final verify dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post-readback verified `7` metadata rows, `7` tag rows, `7` xref rows, Sentinel primary table `0x005e0904` slots 0, 13, 50, 57, secondary table `0x005deca0` slot 0, and `7` decompile exports.
- Focused probe: `py -3 tools\ghidra_sentinel_wave498_probe.py --check` PASS.
- NPM probe: `cmd.exe /c npm run test:ghidra-sentinel-wave498` PASS.
- Queue refresh: `6078` total functions, `2267` commented, `3811` commentless, `1657` undefined signatures, `1514` `param_N`; strict comment-plus-clean-signature proxy `2211/6078 = 36.38%`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-115915_post_wave498_sentinel_verified` with `19` files, `157780871` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Public Boundary

This note is public-safe static RE accounting. It does not include private game assets, installed-game mutation, runtime launch proof, raw decompile bodies, or private media.

## Deferred

`0x004de1d0` (`CSafeSide__VFunc_02_004de1d0`) was reviewed as real but deferred because it is a separate non-Sentinel target.

## Not Proven

- Exact source virtual names and full Sentinel source-body identity.
- Concrete `CSentinel`, weapon-context, linked-list, helper-object, animation-owner, or `CMCSentinel` layouts.
- Runtime activation, deactivation, flamethrower firing, destruction, helper allocation, BEA launch behavior, game patching, and rebuild parity.
