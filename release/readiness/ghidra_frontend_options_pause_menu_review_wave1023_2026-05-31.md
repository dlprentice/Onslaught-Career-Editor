# Ghidra Frontend Options / Pause Menu Review Wave1023

Status: complete static read-only evidence
Date: 2026-05-31
Scope: `frontend-options-pause-menu-review-wave1023`

Wave1023 re-read sixteen frontend options, controller, audio-reset, compact menu-item, pause-menu, and simple-game-menu helper rows. The pass made no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Reviewed anchors:

| Address | Saved state |
| --- | --- |
| `0x004cdd70 GameControllers__RelinquishControlForTarget` | Controller-target relinquish helper; loops controllers and releases matching controlled target. |
| `0x004cddf0 Audio__ReinitializeSoundAndRestoreMusic` | Audio reset/music restore wrapper; not a CEngine method. |
| `0x004ceef0 LandscapeDetail_SetLevel` | Landscape detail option setter. |
| `0x004cef30 LandscapeDetail_GetLevel` | Landscape detail option getter. |
| `0x004cef50 CTreeDetail__SetQualityLevel` | Tree/detail quality setter forwarding to `CRTMesh__SetQualityLevel`. |
| `0x004cf030 CMouseSensitivityMenuItem__scalar_deleting_dtor` | Mouse-sensitivity menu-item scalar deleting destructor. |
| `0x004cf8e0 CMultiSample__GetSampleCountLabel` | MSAA sample-count label resolver. |
| `0x004cffd0 CVideoDetailLevel__GetCurrentPresetFromItems` | Video-detail preset recognizer. |
| `0x004d01c0 CMenuItem__RestoreCompactVTable` | Compact menu-item vtable reset helper. |
| `0x004d0490 CMenuItem__shared_compact_scalar_deleting_dtor` | Shared compact menu-item scalar deleting destructor. |
| `0x004d04b0 CPauseMenu__scalar_deleting_dtor` | Pause-menu scalar deleting destructor. |
| `0x004d0510 CPauseMenu__LoadPauseTextures` | Pause-menu texture loader. |
| `0x004d05e0 CPauseMenu__dtor_base` | Pause-menu destructor body. |
| `0x004d11d0 CPauseMenu__Render` | Pause/options render body returning active range title text when applicable. |
| `0x004d1730 CSimpleGameMenu__scalar_deleting_dtor` | Simple-game-menu scalar deleting destructor. |
| `0x004d1750 CSimpleGameMenu__dtor_base` | Simple-game-menu destructor body. |

Read-back evidence:

- Fresh exports verified `16` metadata rows, `16` tag rows, `50` xref rows, `905` body-instruction rows, and `16` decompile rows.
- Headless logs reported metadata `targets=16 found=16 missing=0`, tags `rows=16 missing=0`, xrefs `Wrote 50 rows`, instructions `targets=16 missing=0`, and decompile `targets=16 dumped=16 missing=0 failed=0`.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress advances to `555/1408 = 39.42%`; expanded static surface progress advances to `784/1493 = 52.51%`; Wave911 top-500 risk-ranked coverage advances to `483/500 = 96.60%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-233831_post_wave1023_frontend_options_pause_menu_review_verified`, `19` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The selected frontend/options/pause-menu helper rows still read back with their saved bounded names, signatures, comments, and tags.
- The cluster remains coherent static evidence for options-menu detail settings, audio reset/music restore, compact menu-item destructor paths, pause-menu render/lifecycle, and simple-game-menu lifecycle.
- The live static function-quality queue remains closed at `6238/6238 = 100.00%`.

What remains unproven:

- Runtime options-menu behavior.
- Runtime audio/music reset behavior.
- Runtime pause-menu or simple-game-menu rendering behavior.
- Exact source-body identity.
- Concrete object layouts beyond observed offsets and vtable/call evidence.
- BEA patching behavior.
- Rebuild parity.

Probe token anchor: Wave1023; frontend-options-pause-menu-review-wave1023; 0x004cdd70 GameControllers__RelinquishControlForTarget; 0x004cddf0 Audio__ReinitializeSoundAndRestoreMusic; 0x004ceef0 LandscapeDetail_SetLevel; 0x004cffd0 CVideoDetailLevel__GetCurrentPresetFromItems; 0x004d04b0 CPauseMenu__scalar_deleting_dtor; 0x004d11d0 CPauseMenu__Render; 0x004d1750 CSimpleGameMenu__dtor_base; 555/1408 = 39.42%; 784/1493 = 52.51%; 483/500 = 96.60%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260531-233831_post_wave1023_frontend_options_pause_menu_review_verified; no mutation.
