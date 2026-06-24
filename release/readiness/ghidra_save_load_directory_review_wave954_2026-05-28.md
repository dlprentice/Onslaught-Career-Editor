# Ghidra Save/Load/Directory Review Wave954 Readiness Note

Status: read-only static review with doc-address correction
Date: 2026-05-28
Scope: `save-load-directory-review-wave954`

Wave954 re-reviewed three Wave911 focused frontend save/load/directory candidates and adjacent context rows after fresh serialized headless Ghidra exports. no mutation was needed in Ghidra: all 30 exported function entries exist with clean saved signatures, comments, and tags. The review did find and correct one repo-doc context drift: `PCPlatform__DeleteSaveFile` is the live function at `0x00514ec0`, not `0x00514cc0`.

Primary Wave911 targets:

| Address | Result |
| --- | --- |
| `0x00461c40 CFEPLoadGame__Init` | Still matches the FEPLoadGame vtable init slot and source-correlated selected-save initialization boundary. |
| `0x00464620 CFEPSaveGame__Init` | Still matches the FEPSaveGame vtable init slot and source-correlated save selection initialization boundary. |
| `0x0051ad30 CFEPDirectory__RefreshSaveFileList` | Still matches the shared directory refresh helper called by `CFEPDirectory__Process` and `CFEPVirtualKeyboard__Process`; it checks storage, counts saves, allocates/fills/frees 0x200-byte save-name buffers, and clamps selection. |

Context anchors:

- Load flow: `0x00461e20 CFEPLoadGame__DoLoad` reads `savegames\\<name>.bes` through `PCPlatform__ReadSaveFile`, loads `CAREER`, and can call `0x0051f680 CFEPOptions__WriteDefaultOptionsFile`.
- Save flow: `0x00464c50 CFEPSaveGame__CreateSave` enumerates existing saves, serializes `CAREER`, writes through `PCPlatform__WriteSaveFile`, and can call `0x00514ec0 PCPlatform__DeleteSaveFile`.
- Directory flow: `0x0051ac40 CFEPDirectory__Process` reaches `0x00514ec0 PCPlatform__DeleteSaveFile` after confirmation; `0x0051ae70 CFEPDirectory__RenderSaveFileList` is shared with `0x00521100 CFEPVirtualKeyboard__Render`.
- Vtable snapshots: `0x005db920` covers FEPSaveGame init/process/button/render/transition slots, `0x005db948` covers FEPLoadGame init/process/button/render/transition slots, and `0x005db800` covers CFEPDirectory init/shutdown/process/button/render slots.
- Debug strings: `0x00629a78` is `C:\dev\ONSLAUGHT2\FEPSaveGame.cpp`; `0x0063fb4c` is `C:\dev\ONSLAUGHT2\FEPDirectory.cpp`.

Read-back evidence:

- Exports: 30 metadata rows, 30 tag rows, 76 xref rows, 2994 instruction rows, 30 decompile rows, and 36 vtable rows.
- String dumps: `0x00629a78` and `0x0063fb4c`.
- Verified backup: `G:\GhidraBackups\BEA_20260528-100717_post_wave954_save_load_directory_review_verified`, 19 files, 173542279 bytes, `DiffCount=0`.
- Static function-quality closure remains `6151/6151 = 100.00%`.
- Wave911 focused re-audit progress after Wave954 is `283/1408 = 20.10%`.

What this proves:

- The saved Ghidra function rows for the reviewed save/load/directory cluster remain coherent with fresh read-back evidence.
- The save/load/directory handoff still routes through the expected PC save enumeration/read/write/delete helpers and shared frontend page/vtable slots.
- The canonical FEPDirectory docs now point at the live `PCPlatform__DeleteSaveFile` entry `0x00514ec0`.

What remains unproven:

- Runtime save/load/delete/filesystem behavior.
- Exact save-name encoding behavior.
- Concrete frontend page layouts.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
