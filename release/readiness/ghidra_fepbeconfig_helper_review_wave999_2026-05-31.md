# Ghidra FEPBEConfig Helper Review Wave999 Readiness Note

Status: complete read-only static read-back evidence
Date: 2026-05-31
Scope: `fepbeconfig-helper-review-wave999`

Wave999 re-reviewed the Wave911 risk-ranked FEPBEConfig / FEPMultiplayerStart helper island around the prior Wave367 and Wave403 corrections. Fresh read-only metadata, tag, xref, instruction, and decompile exports matched the already-saved evidence, so this wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary targets:

| Address | Read-back evidence |
| --- | --- |
| `0x0044eb30 CFEPMultiplayerStart__SetConfigDescriptionByIndex` | Walks the selected config list, resolves the matched config name through `DAT_006602a0`, maps record type field `+0xa4` to text tokens, and falls back to `Unknown Configuration`. |
| `0x0044f530 CFEPBEConfig__PlayWeaponSound` | Primary weapon-name path through selected profile data, `DAT_008553e8` weapon records, weapon-record field `+0x0f`, and `Unknown Weapon` fallback. |
| `0x0044f830 CFEPBEConfig__PlayWeaponSoundAlt` | Alternate weapon-name path through matched config record fields `+0x50/+0x58`, `DAT_008553e8`, weapon-record field `+0x0f`, and `Unknown Weapon` fallback. |
| `0x00451a40 FEPBEConfig__FindSelectedEntryByGlobalId` | Wave403 owner correction remains valid: callers pass `0x0089da14`, the body walks list-state `+0x20/+0x28` links, and it returns the entry whose leading id matches `DAT_0089d94c`. |

Context targets:

`0x0044eab0 CFEPMultiplayerStart__GetConfigIdByIndex`, `0x0044ecf0 CFEPMultiplayerStart__GetConfigCount`, `0x0044f030 CFEPBEConfig__GetWeaponProperty`, `0x0044f300 CFEPBEConfig__GetWeaponPropertyAlt`, `0x00450090 CFEPBEConfig__ButtonPressed`, `0x004505b0 CFEPBEConfig__Render`, and `0x00451930 CFEPBEConfig__FindEntryByName`.

Fresh read-back evidence:

- Exports: `11` metadata rows, `11` tag rows, `31` xref rows, `3001` body-instruction rows, and `11` decompile rows.
- Existing Wave367 and Wave403 probes passed: `test:ghidra-fep-beconfig-boundary-signature` and `test:ghidra-fepbeconfig-selected-entry-wave403`.
- Queue closure remains `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress remains `467/1408 = 33.17%` because this is a risk-ranked residual island rather than a new focused-candidate anchor.
- Expanded static surface progress is now `596/1478 = 40.32%`.
- Wave911 top-500 risk-ranked coverage for this residual pass advances to `343/500 = 68.60%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-094628_post_wave999_fepbeconfig_helper_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave999; `fepbeconfig-helper-review-wave999`; `0x0044eb30 CFEPMultiplayerStart__SetConfigDescriptionByIndex`; `0x0044f530 CFEPBEConfig__PlayWeaponSound`; `0x0044f830 CFEPBEConfig__PlayWeaponSoundAlt`; `0x00451a40 FEPBEConfig__FindSelectedEntryByGlobalId`; `467/1408 = 33.17%`; `596/1478 = 40.32%`; `343/500 = 68.60%`; `6222/6222 = 100.00%`; `G:\GhidraBackups\BEA_20260531-094628_post_wave999_fepbeconfig_helper_review_verified`; no mutation.

What this proves:

- The reviewed FEPBEConfig / FEPMultiplayerStart rows exist in the saved Ghidra project with the expected names, signatures, comments, and tags.
- The saved Wave367 helper labels and Wave403 selected-entry owner correction still match fresh retail Ghidra xref/decompile/instruction evidence.
- The frontend config text/property helper island remains statically coherent around `CFEPBEConfig__Render`, `DAT_0089d94c`, `DAT_006602a0`, and `DAT_008553e8`.

What remains unproven:

- Exact Stuart source-body identity.
- Concrete FEPBEConfig, config-entry, weapon-record, or frontend list layouts.
- Runtime frontend menu behavior.
- Runtime audio/text presentation behavior.
- BEA patching behavior.
- Rebuild parity.
