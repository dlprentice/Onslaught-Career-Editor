# Ghidra FEPDirectory Page Wave856 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `fepdirectory-page-wave856`

Wave856 FEPDirectory page saved comment/tag treatments for six `CFEPDirectory` frontend save-directory rows from `0x0051aa90 CFEPDirectory__Init` through `0x0051b460 CFEPDirectory__Render` after serialized headless dry/apply/read-back with the `fepdirectory-page-wave856` and `wave856-readback-verified` tags. The pass made no renames, no signature changes, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0051aa90 CFEPDirectory__Init` | Vtable `0x005db800` slot 2 / DATA xref `0x005db808`; clears the 0x1000-entry save-name pointer array and observed count/selection/scroll/timestamp fields. |
| `0x0051aac0 CFEPDirectory__Shutdown` | Vtable slot 3 / DATA xref `0x005db80c`; frees each non-null save-name buffer through `CDXMemoryManager__Free(&DAT_009c3df0, entry)`. |
| `0x0051aaf0 CFEPDirectory__ButtonPressed` | Vtable slot 5 / DATA xref `0x005db814`; handles save-list up/down, selected-save activation/delete confirmation, and return-to-page flow. |
| `0x0051ac40 CFEPDirectory__Process` | Vtable slot 4 / DATA xref `0x005db810`; refreshes the list and consumes the delete-confirmation message-box result before calling `PCPlatform__DeleteSaveFile`. |
| `0x0051ad30 CFEPDirectory__RefreshSaveFileList` | Called by `CFEPDirectory__Process` and `CFEPVirtualKeyboard__Process`; checks storage, enumerates `savegames\\*.bes`, allocates/fills/frees 0x200-byte save-name buffers, and clamps selection. |
| `0x0051b460 CFEPDirectory__Render` | Vtable slot 7 / DATA xref `0x005db81c`; calls `CFEPDirectory__RenderSaveFileList`, dispatches button `0x2c` on selection, draws the title bar, and applies overlay fade effects. |

Read-back evidence:

- `ApplyFEPDirectoryPageWave856.java dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_checked=6 comment_only_updated=6 missing=0 bad=0`
- `ApplyFEPDirectoryPageWave856.java apply`: `updated=6 skipped=0 renamed=0 would_rename=0 signature_checked=6 comment_only_updated=6 missing=0 bad=0`
- `ApplyFEPDirectoryPageWave856.java final dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_checked=6 comment_only_updated=0 missing=0 bad=0`
- Post exports: `6` metadata rows, `6` tag rows, `7` xref rows, `222` instruction rows, `6` decompile rows, `16` context metadata rows, `16` context decompile rows, `12` vtable slot rows, and the `FEPDirectory.cpp` string at `0x0063fb4c`.
- Queue after Wave856: `6098` total functions, `5762` commented, `336` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed proxy `5762/6098 = 94.49%`, strict clean-signature proxy `5762/6098 = 94.49%`.
- Next raw commentless row: `0x0051b600 CFEPMultiplayerStart__SubObj4034__ctor`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-114000_post_wave856_fepdirectory_page_verified`, `19` files, `172166023` bytes, `DiffCount=0`.

What this proves:

- The six target function rows exist in the saved Ghidra project.
- The saved signatures remain clean and contain no `undefined` return or `param_N` debt.
- The saved comments and tags include `fepdirectory-page-wave856` and `wave856-readback-verified`.
- The observed static behavior is important frontend save-directory infrastructure: page lifecycle, save enumeration, selection/delete control flow, shared save-list rendering, and virtual page dispatch.

What remains unproven:

- Exact `CFEPDirectory` layout.
- Runtime frontend save-directory behavior.
- Runtime filesystem/delete behavior.
- Exact save-name encoding semantics.
- Source identity.
- BEA patching behavior.
- Rebuild parity.
