# Ghidra CMCBuggy Wave430 Wheel-Motion Static Correction

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00494ce0` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe static Ghidra evidence note
Date: 2026-05-15
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave430 serialized headless dry/apply/read-back hardened fifteen saved functions in the `CMCBuggy` / wheel-motion neighborhood. The pass covers the buggy constructor/destructor/init/update helpers, shared Mat34/Vec3 helpers used by the wheel update path, mesh-part wheel token filters, and a nested/shared destructable-segment motion-controller table after the primary `CMCBuggy` vtable.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof. The retail debug string names `[maintainer-local-source-export-root]\MCBuggy.cpp`, but `MCBuggy.cpp` is absent from the current Stuart source snapshot, so this wave is binary-led rather than source-body parity.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x00493020` | `CMCBuggy__CMCBuggy` | Constructor installs vtable `0x005dc250`, stores owner/model state, clears wheel buffers, and seeds `-1.0f`; `RET 0x4` proves one stack argument after `this`. |
| `0x00493080` / `0x004930a0` | `CMCBuggy__scalar_deleting_destructor` / `CMCBuggy__destructor` | Delete-flags wrapper plus register-only destructor that frees observed wheel/motion buffers and calls the base motion-controller destructor. |
| `0x00493180` / `0x00493190` | `CMCBuggy__SetFieldC0` / `CMCBuggy__Init` | Field `+0xc0` setter plus wheel-base counting, wheel buffer allocation, `WheelMotion` lookup, and cached wheel pose setup. |
| `0x004934f0` | `CMCBuggy__UpdateWheel` | `RET 0x50` proves twenty stack arguments after `this`; static body evidence covers profiling, lazy init, wheel-token resolution, heightfield normal sampling, child-wheel recursion, and cached transform updates. |
| `0x00494310` | `CMCBuggy__ProfileEnd` | Register-only `rdtsc` profiling epilogue. |
| `0x00494350` / `0x004944b0` | `Mat34__InvertBasisToOut` / `Vec3__DivideInPlaceByScalar` | Corrected away from CMCBuggy-only ownership; both are shared math helpers. A first read-back caught the Ghidra `__thiscall` hidden-`this` nuance, then final signatures were corrected to `Mat34(this,out_matrix)` and `Vec3(this,scalar)`. |
| `0x00494b00` / `0x00494b50` | `CMeshPart__NameAvoidsBodyAxleWheelTokens` / `CMeshPart__HasWheelMotionAnimation` | Token read-back proves `Body`, `Axle`, `Wheel`, and `WheelMotion`; the older wheel-token match label was backwards. |
| `0x00494c60` / `0x00494ca0` / `0x00494cc0` / `0x00494ce0` | `CDestructableSegmentsMotionController__Ctor`, destructor pair, and `ApplyRumbleTransform` | Corrected away from narrow CMCBuggy wheel labels. Vtable `0x005dc27c` slots and `RET` cleanup evidence support the saved signatures; the duplicated destructor-like body at `0x00497130` remains follow-up. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 tools\ghidra_cmcbuggy_wave430_probe_test.py` | PASS | Focused tests passed `4/4`. |
| Initial headless `ApplyCmcBuggyWave430.java` dry/apply | PASS | Dry `updated=0 skipped=15 renamed=0 would_rename=9 missing=0 bad=0`; apply `updated=15 skipped=0 renamed=9 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Corrective headless `ApplyCmcBuggyWave430.java` dry/apply | PASS | Dry `updated=0 skipped=15 renamed=0 would_rename=0 missing=0 bad=0`; apply `updated=15 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. This corrected the shared-helper `__thiscall` parameter shape found during first read-back. |
| Post-apply metadata/tag/xref/instruction/decompile/string/vtable read-back | PASS | Verified `15` metadata rows, `15` tag rows, `42` xref rows, `7815` instruction rows, `15` target decompile exports, six string tokens, and vtable slots for `0x005dc250` / `0x005dc27c`. |
| `cmd.exe /c npm run test:ghidra-cmcbuggy-wave430` | PASS | `PASS ghidra-cmcbuggy-wave430 targetCount=15 failures=0`. |
| `py -3 -m py_compile tools\ghidra_cmcbuggy_wave430_probe.py tools\ghidra_cmcbuggy_wave430_probe_test.py` | PASS | Both focused Python files compile. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6043` functions, `4326` commentless functions, `1833` undefined signatures, `1792` `param_N` signatures, and zero broad uncertain/helper/wrapper debt. |
| Actual Ghidra project backup verification after Wave430 mutation | PASS | Copied `BEA.gpr` and `BEA.rep` to `[maintainer-local-ghidra-backup-root]\BEA_20260515_160834_post_wave430_cmcbuggy_verified`; compared `19` files, `155618183` bytes, `HashDiffCount=0`, and `MissingCount=0`. |
| `py -3 tools\release_curated_manifest.py` and `--check` | PASS | Curated manifest selected `2308` files and regenerated `release/readiness/public_candidate_allowlist.tsv`; check passed. |
| `py -3 tools\release_profile_snapshot.py` and `--check` | PASS | Release profile counts remain `R0=2370 R2=0 R3=2 R4=18188`; check passed. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Public allowlist safety check passed with `2308` rows checked. |
| Docs/hygiene gates | PASS | `md-links` PASS; `doc-commands` PASS with `3370` documented package-script references; `docsync_check.py` PASS; `repo-hygiene` PASS. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6043`
- Commentless function objects: `4326`
- `undefined` signatures: `1833`
- Signatures still using `param_N`: `1792`

The Wave430 targets were already comment-bearing before this pass, so the broad queue comment totals did not change. These are triage proxies only; they are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime wheel behavior, runtime destructable-segment behavior, exact concrete `CMCBuggy` or destructable-segment controller layout beyond observed offsets, exact local variable names/types, exact source-body identity, source-to-retail rebuild parity, BEA launch behavior, game patching, or runtime gameplay behavior.
