# Ghidra CMCBuggy/HiveBoss Wave431 Follow-up

Status: public-safe static Ghidra evidence note
Date: 2026-05-15
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave431 completed a compact follow-up to the Wave430 CMCBuggy / destructable-segment motion-controller pass. It corrected the duplicated destructor entry at `0x00497130` into an explicit thunk label and corrected the stale `CUnitAI` owner/signature on the adjacent named collision-cylinder cache helper at `0x00497140`.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x00497130` | `CDestructableSegmentsMotionController__DestructorThunk_00497130` | Instruction read-back proves a one-instruction `JMP 0x00494cc0` thunk to the canonical destructable-segments motion-controller destructor. The only observed xref is from `CMCHiveBoss__VFunc_01_00497110`. |
| `0x00497140` | `CDestructableSegmentsMotionController__CacheNamedCollisionCylinders` | `RET 0x4` proves one mesh/model stack argument after `this`. The body walks count/table fields at `mesh_model+0x15c/+0x160`, compares part names at `+0xdc` against named collision-cylinder tokens, caches matches into `this+0x18..+0x74`, and sets `this+0x14`. The only observed caller is a currently missing-boundary callsite at `0x004976f1`, which then calls `CDestructableSegmentsMotionController__ApplyRumbleTransform` and tests cached slots. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 tools\ghidra_cmcbuggy_hiveboss_wave431_probe_test.py` | PASS | Focused tests passed `4/4`. |
| Expected-red `cmd.exe /c npm run test:ghidra-cmcbuggy-hiveboss-wave431` before apply | PASS | Probe failed on missing dry/apply/read-back evidence before mutation. |
| Headless `ApplyCmcBuggyHiveBossWave431.java` dry/apply | PASS | Dry `updated=0 skipped=2 renamed=0 would_rename=2 missing=0 bad=0`; apply `updated=2 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Post-apply idempotent dry run | PASS | Dry `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `2` metadata rows, `2` tag rows, `2` xref rows, `522` focused instruction rows, `1201` full cylinder-cache instruction rows, and `2` target decompile exports. |
| `cmd.exe /c npm run test:ghidra-cmcbuggy-hiveboss-wave431` | PASS | Focused probe returned `status: PASS` with zero failures. |
| Actual Ghidra project backup verification after Wave431 mutation | PASS | Copied `BEA.gpr` and `BEA.rep` to `[maintainer-local-ghidra-backup-root]\BEA_20260515_173016_post_wave431_cmcbuggy_hiveboss_verified`; compared `19` files, `155618183` bytes, `HashDiffCount=0`, and `MissingCount=0`. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6043`
- Commented function objects: `1734`
- Commentless function objects: `4309`
- `undefined` signatures: `1820`
- Signatures still using `param_N`: `1789`

Telemetry-only proxies are comment-backed `1734/6043 = 28.69%` and strict clean-signature `1672/6043 = 27.67%`. These are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime destructable-segment behavior, runtime collision-cylinder behavior, exact concrete controller layout beyond observed offsets, exact local variable names/types, exact source-body identity, source-to-retail rebuild parity, BEA launch behavior, game patching, or runtime gameplay behavior.
