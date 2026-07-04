# Ghidra PC Platform/Controller Tail Wave851 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `pc-platform-controller-tail-wave851`

Wave851 PC platform/controller tail saved comments and tags for twenty-five important PC runtime connector rows from `0x005140e0 CDXEngine__CaptureAviFrame` through `0x005159c0 PLATFORM__SetKeySink`. The pass made no renames, no signature changes, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005140e0 CDXEngine__CaptureAviFrame` | `void CDXEngine__CaptureAviFrame(void)` | `CDXEngine__PostRender` callsite `0x0053ef63`; capture flag `DAT_008892d5`; `AVIStreamWrite`; failure string `AVIStreamWrite() failed!\x0a`. |
| `0x00514210 OptionsEntries__InitDefaultSingleBindingsTable` | `void __cdecl OptionsEntries__InitDefaultSingleBindingsTable(void)` | Forty-seven `OptionsEntries__InitSingleBindingEntry` calls from `DAT_008892d8` through `DAT_00889898`, followed by the `DAT_008898b8` sentinel; source-reference `PCController.cpp` default mapping rows. |
| `0x00514620 CPCController__scalar_deleting_dtor` | `void * __thiscall CPCController__scalar_deleting_dtor(void * this, uchar free_flag)` | CPCController vtable slot 0 at `0x005e48e0`; calls `CController__dtor_Thunk`, conditionally frees through `CDXMemoryManager__Free`. |
| `0x00514640` through `0x00514900` | current `CPCController` input signatures | Exact anchor `0x00514640 CPCController__GetJoyAnalogueLeftX`; CPCController vtable slots 3-14; joystick old/current state tables, analogue axes, keyboard wrappers, and POV helpers with source-reference `PCController.cpp`/`.h` anchors. |
| `0x00514950 PCPlatform__GetStorageDeviceCount` | `int __stdcall PCPlatform__GetStorageDeviceCount(int * out_count)` | PC console-API compatibility helper; writes one storage device. |
| `0x00514960 PCPlatform__GetStorageDeviceInfo` | `int __stdcall PCPlatform__GetStorageDeviceInfo(int device, int * out_inserted, int * out_formatted, int * out_free_bytes, int * out_total_bytes)` | Called by frontend development/load/save/directory paths; reports inserted/formatted and max free/total byte counts when outputs are present. |
| `0x00514be0 EnumerateSaveFiles_Main` | `int __stdcall EnumerateSaveFiles_Main(int device, short * save_name, int * out_index, int allowed_overwrite)` | Builds `savegames\` + `FromWCHAR(save_name)` + `.bes`; enumerates `savegames\*.bes`; skips attributes mask `0x16`; compares case-insensitive wide names; returns `6` for disallowed overwrite. |
| `0x00515320 PCPlatform__InitMusicPlaylist` | `void __fastcall PCPlatform__InitMusicPlaylist(void * this)` | Music/platform initialization slot at data xref `0x005e4934`; calls async stream init and `CMusic__LoadPlaylistFromDir(this,"data\music")`. |
| `0x00515970 PlatformInput__GetKeyOn` | `uchar __stdcall PlatformInput__GetKeyOn(int key)` | Returns `DAT_00888c94[key]`; source-reference `PCPlatform::KeyOn -> LT.xKeyOn`. |
| `0x00515980 PlatformInput__ConsumeKeyOnce` | `uchar __stdcall PlatformInput__ConsumeKeyOnce(int key)` | Reads and clears `DAT_00888d94[key]`; source-reference `PCPlatform::KeyOnce -> LT.xKeyOnce`. |
| `0x005159b0 PlatformInput__ResetKeyStateTables` | `void PlatformInput__ResetKeyStateTables(void)` | Calls `PlatformInput__ClearAllKeyStateTables(&DAT_00855bb0)` from frontend/level/FMV reset contexts. |
| `0x005159c0 PLATFORM__SetKeySink` | `void __stdcall PLATFORM__SetKeySink(void * key_sink)` | Forwards to Wave848-readback `PlatformInput__SetKeySinkCore(&DAT_00855bb0,key_sink)`; source-reference `PCPlatform::SetKeytrap -> LT.SetKeytrap`. |

Read-back evidence:

- `ApplyPcPlatformControllerTailWave851.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=25 missing=0 bad=0`
- `ApplyPcPlatformControllerTailWave851.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=25 missing=0 bad=0`
- `ApplyPcPlatformControllerTailWave851.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: `25` metadata rows, `25` tag rows, `74` xref rows, `1625` instruction rows, and `25` decompile rows.
- Additional read-only evidence: `15` context metadata rows, `15` context decompile rows, `20` CPCController vtable rows, `16` music/platform vtable rows, five string dumps, and source-context search hits.
- Queue after Wave851: `6098` total functions, `5729` commented, `369` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed proxy `5729/6098 = 93.95%`, strict clean-signature proxy `5729/6098 = 93.95%`.
- Next raw commentless row: `0x00515ab0 D3DDevice__SetViewport`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-085618_post_wave851_pc_platform_controller_tail_verified`, `19` files, `172034951` bytes, `DiffCount=0`.

What this proves:

- The twenty-five target rows exist in the saved Ghidra project with the Wave851 comments/tags and current signatures above.
- The rows are important static connector infrastructure for AVI capture, control-binding defaults, CPCController vtable/input accessors, PC save/storage compatibility, music playlist initialization, and platform key-state/key-sink wrappers.

What remains unproven:

- Runtime capture output, runtime input behavior, runtime save/frontend filesystem behavior, and runtime audio playback.
- Exact Direct3D surface/AVI buffer layouts, exact pad/key table layouts, exact options-entry schema, exact save API error-code contract, exact music vtable owner/layout, and exact key-sink callback ABI.
- BEA patching behavior.
- Rebuild parity.
