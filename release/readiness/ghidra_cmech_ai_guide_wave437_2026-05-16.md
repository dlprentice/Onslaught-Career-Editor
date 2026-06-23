# Ghidra CMechAI / CMechGuide Wave437 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave437 corrected eleven CMechAI, CMechGuide, CMCMech, and shared ground-unit slot targets. It hardened the large `CMCMech__UpdateBone` signature/comment, corrected two stale shared ground-unit slot owner labels, and saved constructor/destructor/update/target-selection names for the CMechAI/CMechGuide cluster allocated by Wave436's CMech initialization slots.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x00499e30` | `CMCMech__UpdateBone` | Hardened the large bone-update signature/comment; called by `CMCMech__Reset` and recursive hierarchy update, with exact parameter roles still open. |
| `0x0049fc10` | `SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10` | Shared/default slot-66 body for vtables `0x005e0684` and `0x005e3074`; concrete GillM/ThunderHead-style slot-66 overrides call into it. |
| `0x0049fdb0` | `SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0` | Shared slot-71 body across sampled Mech/GillM/ThunderHead-style tables; searches `Generic Mesh` and spawns anchored break effects. |
| `0x004a02e0` | `CMechAI__ctor` | Constructor for the `0x64` CMechAI object allocated by `CMech__InitCockpit`; installs vtable `0x005dc4c0` and randomizes field `+0x60`. |
| `0x004a0390` | `CMechAI__scalar_deleting_dtor` | Vtable `0x005dc4c0` slot 1 scalar-deleting destructor wrapper around `CUnitAI__dtor_base`. |
| `0x004a03b0` | `CUnitAI__dtor_base` | Restores vtable `0x005d8d1c`, removes linked reader cells at `+0x28`, `+0x24`, and `+0x0c`, then calls `CMonitor__Shutdown`. |
| `0x004a0a20` | `CMechGuide__ctor` | Constructor for the `0x48` CMechGuide object allocated by `CMech__InitTargeting`; installs vtable `0x005dc4f4`, initializes path fields, and schedules event `2000`. |
| `0x004a0b10` | `CMechGuide__scalar_deleting_dtor` | Vtable `0x005dc4f4` slot 1 scalar-deleting destructor wrapper around `CMechGuide__dtor_base`. |
| `0x004a0b30` | `CMechGuide__dtor_base` | Removes active-reader state at `+0x44`, frees guide buffers at `+0x3c` and `+0x34`, then calls `CMonitor__Shutdown`. |
| `0x004a0bc0` | `CMechGuide__VFunc_03_UpdateGuidanceState_004a0bc0` | Vtable `0x005dc4f4` slot 3 guidance update body using owner, active-reader, AI-state, and path-buffer fields. |
| `0x004a1270` | `CMechGuide__SelectNearestHostileTargetReader` | Clears active reader field `+0x44`, scans nearby `CMapWho` entries, and stores the nearest compatible hostile reader. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyCMechAIGuideWave437.java` dry/apply/verify | PASS | Dry found `11` targets with `would_rename=10`; apply reported `updated=11`, `renamed=10`, `missing=0`, `bad=0`; verify dry reported `updated=0`, `skipped=11`, `would_rename=0`, `missing=0`, `bad=0`. |
| Post-apply metadata/tag/decompile/vtable read-back | PASS | Verified `11` metadata rows, `11` tag rows, `11` decompile exports, `504` ground-table vtable-slot rows, and `24` CMechAI/CMechGuide vtable-slot rows. |
| `py -3 -m py_compile tools\ghidra_cmech_ai_guide_wave437_probe.py tools\ghidra_cmech_ai_guide_wave437_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_cmech_ai_guide_wave437_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `cmd.exe /c npm run test:ghidra-cmech-ai-guide-wave437` | PASS | Focused probe returned `status: PASS` for all `11` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6055` total functions, `1808` commented functions, `4247` commentless functions, `1800` undefined signatures, and `1749` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6055`
- Commented function objects: `1808`
- Commentless function objects: `4247`
- `undefined` signatures: `1800`
- Signatures still using `param_N`: `1749`

Telemetry-only proxies are comment-backed `1808/6055 = 29.86%` and strict clean-signature `1746/6055 = 28.84%`. These are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime CMechAI/CMechGuide targeting behavior; exact concrete layouts beyond observed offsets; exact virtual method names; exact local variable names/types; exact source-body identity; source-to-retail rebuild parity; BEA launch behavior; game patching; or runtime gameplay behavior.
