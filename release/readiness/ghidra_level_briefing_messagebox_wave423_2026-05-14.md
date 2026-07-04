# Ghidra LevelBriefingLog / MessageBox Wave423 Static Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-14
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave423 serialized headless dry/apply/read-back corrected the current LevelBriefingLog lifecycle queue head and hardened one MessageBox activation helper. The pass updates saved Ghidra metadata for four existing function objects and does not create new function boundaries.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Previous saved label | Current saved state | Static evidence summary |
| --- | --- | --- | --- |
| `0x0048f540` | `CLevelBriefingLog__ctor_like_0048f540` | `void * __thiscall CLevelBriefingLog__ctor(void * this)` | Constructor installs vtable `0x005dc208`, clears fields `+0x04/+0x08/+0x0c`, resolves `FrontEnd_v2/FE_Blank.tga` through `CTexture__FindTexture`, stores the texture/ref handle at `+0x10`, and returns `this`. |
| `0x0048f5a0` | `CLevelBriefingLog__VFunc_01_0048f5a0` | `void * __thiscall CLevelBriefingLog__scalar_deleting_dtor(void * this, byte flags)` | Scalar-deleting destructor wrapper calls the destructor body, checks flags bit `0`, optionally frees `this` through `OID__FreeObject`, returns `this`, and ends with `RET 0x4`. |
| `0x0048f5c0` | `CLevelBriefingLog__ctor_like_0048f5c0` | `void __thiscall CLevelBriefingLog__dtor(void * this)` | Destructor body restores vtable `0x005dc208`, releases the `+0x10` texture/ref handle through `CHud__DecrementCounter9C` on `handle+0x08` when present, clears `+0x10`, then calls `CMonitor__Shutdown`. |
| `0x0048ff90` | `CMessageBox__ActivateWithFadeStep_0p1` | `void __thiscall CMessageBox__ActivateWithFadeStep_0p1(void * this)` | Activation helper writes active flag `+0x08 = 1` and fade/transition step `+0x0c = 0.1f` (`0x3dcccccd`), then returns. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 tools\ghidra_level_briefing_messagebox_wave423_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `py -3 -m py_compile tools\ghidra_level_briefing_messagebox_wave423_probe.py tools\ghidra_level_briefing_messagebox_wave423_probe_test.py` | PASS | Both focused Python files compile. |
| Pre-apply `cmd.exe /c npm run test:ghidra-level-briefing-messagebox-wave423` | FAIL, expected red | Probe rejected the missing post-apply artifacts before the saved Ghidra apply/read-back existed. |
| Headless `ApplyLevelBriefingMessageBoxWave423.java` dry run | PASS | `updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`, with `REPORT: Save succeeded`; dry logic made no metadata mutation. |
| Headless `ApplyLevelBriefingMessageBoxWave423.java` apply | PASS | `updated=4 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `4` metadata rows, `4` tag rows, `5` xref rows, `484` instruction rows, and `4` decompile exports. |
| Post-apply `cmd.exe /c npm run test:ghidra-level-briefing-messagebox-wave423` | PASS | Focused probe accepted the saved names, signatures, comments, tags, read-back tokens, and proof-boundary wording. |
| Headless whole-database quality snapshot | PASS | `total_functions=6043`; `commented_functions=1671`. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6043` functions, `4372` commentless functions, `1861` undefined signatures, `1809` `param_N` signatures, and zero broad uncertain/helper/wrapper debt. |
| Live Ghidra project backup | PASS | `[maintainer-local-ghidra-backup-root]\BEA_20260514_163227_post_wave423_level_briefing_messagebox_verified`, `19` files, `155159431` bytes, `HashDiffCount=0`, `MissingCount=0`. |

## Current Queue Telemetry

The refreshed static re-audit queue now reports:

- Total function objects: `6043`
- Functions with non-empty function comments: `1671`
- Commentless function objects: `4372`
- `undefined` signatures: `1861`
- Signatures still using `param_N`: `1809`
- Comment-backed telemetry proxy: `1671/6043 = 27.65%`
- Strict clean-signature telemetry proxy: `1608/6043 = 26.61%`

These are triage proxies only. They are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime LevelBriefingLog rendering, message-box menu behavior, voice/text reveal behavior, exact concrete object layouts, local variable names/types, complete MessageBox recovery, adjacent undecorated code after `0x0048ff90`, BEA launch behavior, game patching, or rebuild parity.
