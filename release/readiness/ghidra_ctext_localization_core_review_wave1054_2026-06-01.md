# Ghidra CText Localization Core Review Wave1054 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-01
Scope: `ctext-localization-core-review-wave1054`

Wave1054 saved a CText localization-core comment/tag correction for eight existing `text.cpp` functions. The pass made no renames, no signature changes, no function-boundary changes, no executable-byte changes, no BEA launch, and no runtime/game-file mutation.

Primary targets:

| Address | Saved row | Evidence summary |
| --- | --- | --- |
| `0x004f2140` | `CText__ResetCoreFields` | Resets the observed CText core fields before construction/init/reload paths. |
| `0x004f2150` | `CText__Ctor` | Constructor path that delegates through the reset helper and initializes CText state. |
| `0x004f2170` | `CText__FreeBuffer` | Frees the loaded text backing buffer and clears dependent string/audio pool pointers. |
| `0x004f2190` | `CText__GetLanguageName` | Maps language IDs to language-name strings used by frontend language selection. |
| `0x004f21f0` | `CText__Init` | Loads `data\\LANGUAGE` language DAT files, handles the `0xffffffbb` format marker, and sets up string/audio pools. |
| `0x004f24b0` | `CText__GetAudioNameById` | Bounds audio-name lookups through the loaded audio pool. |
| `0x004f2500` | `CText__GetStringByIdAfter` | Performs bounded string lookup from the text pool after an ID/cursor-style input. |
| `0x004f2580` | `CText__GetStringById` | Performs bounded direct string lookup and returns localized/fallback text pointers. |

Context anchors: `0x004f2660 CText__CopyFrom`, `0x00466ab0 CFrontEnd__SetLanguage`, `0x0046a1f0 FrontEndText__GetLevelNameTextAfterCode`, `0x0046a220 FrontEndText__GetMultiplayerLevelDescriptionByType`, `0x0046a2a0 FrontEndText__GetLocalizedOrFallbackTextByToken`, `0x0050d6a0 CWorld__PushWorldTextSlot`, `0x00412420 CGeneralVolume__GetMode3CurrentEntryDisplayString`, `0x004145a0 CBattleEngineWalkerPart__GetWeaponName`, and `0x005482c0 CDXMemBuffer__GetFileSize`. Decompile evidence also preserves the `MultiByteToWideChar` conversion path.

Read-back evidence:

- Dry run: `updated=0 skipped=8 comment_updated=8 tags_added=80 missing=0 bad=0`.
- Apply: `updated=8 skipped=0 comment_updated=8 tags_added=80 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry run: `updated=0 skipped=8 comment_updated=0 tags_added=0 missing=0 bad=0`.
- Primary exports: `8` metadata rows, `8` tag rows, `340` xref rows, `399` function-body instruction rows, and `8` decompile rows.
- Context exports: `9` metadata rows, `9` tag rows, `100` xref rows, `986` function-body instruction rows, and `9` decompile rows.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `769/1408 = 54.62%`.
- Expanded static surface progress advances to `1065/1509 = 70.58%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-165852_post_wave1054_ctext_localization_core_review_verified`, `19` files, `174656391` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The eight CText primary function rows exist in the saved Ghidra project.
- The saved comments and tags include `ctext-localization-core-review-wave1054` and `wave1054-readback-verified`.
- The comments are bounded to static retail Ghidra metadata/decompile/xref evidence and call out the source-adjacent CText localization core.
- The CText rows remain coherent with frontend language switching, frontend text lookup wrappers, world text slots, volume/weapon-name consumers, `CText__CopyFrom`, and `CDXMemBuffer__GetFileSize`.

What remains separate proof:

- Runtime language switching and localization behavior.
- Exact concrete `CText` layout beyond observed static offsets.
- Exact source-body identity and source-layout identity.
- BEA patching, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1054; ctext-localization-core-review-wave1054; 0x004f2140 CText__ResetCoreFields; 0x004f21f0 CText__Init; 0x004f24b0 CText__GetAudioNameById; 0x004f2500 CText__GetStringByIdAfter; 0x004f2580 CText__GetStringById; CText__CopyFrom; CFrontEnd__SetLanguage; CDXMemBuffer__GetFileSize; data\\LANGUAGE; 0xffffffbb; MultiByteToWideChar; 769/1408 = 54.62%; 1065/1509 = 70.58%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-165852_post_wave1054_ctext_localization_core_review_verified; comment/tag correction.
