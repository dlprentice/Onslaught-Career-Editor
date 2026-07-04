# Ghidra FEPMultiplayerStart Runtime Wave857 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `fepmultiplayerstart-runtime-wave857`

Wave857 FEPMultiplayerStart runtime created three previously missing `CFEPMultiplayerStart` SubObj4034 vtable-slot function objects and saved comments, tags, and corrected signatures for eight important multiplayer-start frontend runtime helpers. The pass used the `fepmultiplayerstart-runtime-wave857` and `wave857-readback-verified` tags, made three function-object creations, no executable-byte changes, and no source-identity claim. `[maintainer-local-source-export-root]\FEPMultiplayerStart.cpp` exists as a retail debug-string anchor at `0x0063fc24`, but the source file is absent from the current Stuart source snapshot.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0051b600 CFEPMultiplayerStart__SubObj4034__ctor` | Called from `CFEPMultiplayerStart__ctor` at `0x00466049`; installs vtable `0x005e49b4` for owner `+0x4034`. |
| `0x0051b610 CFEPMultiplayerStart__SubObj4034__ResetFlags` | Called by the created init/process helpers at `0x0051b64e` and `0x0051b6cf`; clears `this+0x0c`, `DAT_00677614`, and manages the observed `this+0x10` gate. |
| `0x0051b640 CFEPMultiplayerStart__SubObj4034__Init` | Created from vtable `0x005e49b4` slot 0; clears `this+0x0c`, sets `this+0x14`, calls reset, and returns `1`. |
| `0x0051b660 CFEPMultiplayerStart__SubObj4034__ButtonPressed` | Created from vtable `0x005e49b4` slot 3; handles button `0x2c`, clears `DAT_006630cc`, calls `CFrontEnd__SetPage`, and plays frontend sound `1`. |
| `0x0051b6b0 CFEPMultiplayerStart__SubObj4034__Process` | Created from vtable `0x005e49b4` slot 2; checks state/movie/HUD gates, handles dev-mode timeout dispatch, updates `this+0x04`/`this+0x18`, reacts to `DAT_00677614`/`DAT_00677624`/`DAT_0067762c`, and ends through `CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture`. |
| `0x0051be70 CFEPMultiplayerStart__SubObj4034__InitRuntimeState` | DATA xref `0x005e49cc`; reads `PLATFORM__GetSysTimeFloat`, clears transition globals, calls `CFEPMultiplayerStart__SetCurrentSelection`, and clears `this+0x18`. |
| `0x0051da60 CFEPMultiplayerStart__InitSelection` | DATA xref `0x005db910`; seeds transition timing and the primary page selection/animation table. |
| `0x0051ddd0 CFEPMultiplayerStart__HandleInput` | Called from `CFEPMultiplayerStart__Render` at `0x0051ee7b` and `0x0051ef9e`; handles per-player selection left/right inputs and config-index wraparound. |

Read-back evidence:

- Create dry/apply: `would_create=3`, then `created=3`, `renamed=3`, `failed=0`.
- Metadata dry/apply/final dry: dry reported `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=5 missing=0 bad=0`; the first apply saved the eight rows but exposed a fastcall read-back mismatch at `0x0051b640`; corrective dry/apply then reported `signature_updated=1 bad=0`; final dry reported `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 8 metadata rows, 8 tag rows, 10 xref rows, 296 instruction rows, 8 decompile rows, 18 context metadata rows, 18 context decompile rows, 12 vtable rows, and FEPMultiplayerStart.cpp string read-back.
- Queue after Wave857: 6101 total functions, 5770 commented, 331 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5770/6101 = 94.57%`, strict clean-signature proxy `5770/6101 = 94.57%`.
- Next raw commentless row: `0x0051f370 CFEPOptions__GetState`. The commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-121518_post_wave857_fepmultiplayerstart_runtime_verified`, 19 files, 172198791 bytes, `DiffCount=0`.

What this proves:

- The eight target function rows exist in the saved Ghidra project.
- The three SubObj4034 vtable-slot function objects now exist at `0x0051b640`, `0x0051b660`, and `0x0051b6b0`.
- Saved names, signatures, comments, tags, xrefs, vtable slots, decompile rows, and instruction rows match the exported static retail evidence.

What remains unproven:

- Exact source method identity.
- Concrete `CFEPMultiplayerStart` / SubObj4034 layout.
- Runtime multiplayer-start behavior.
- Runtime frontend transition, movie/HUD, or input behavior.
- BEA patching behavior.
- Rebuild parity.
