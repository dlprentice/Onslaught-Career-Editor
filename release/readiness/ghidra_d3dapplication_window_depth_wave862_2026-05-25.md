# Ghidra D3DApplication Window/Depth Wave862 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `d3dapplication-window-depth-wave862`

Wave862 D3DApplication window/depth saved comments/tags for two important connective infrastructure rows: `0x0052a830 CD3DApplication__FindDepthStencilFormat` and `0x0052aaf0 CD3DApplication__MsgProc`. The pass corrected one signature, made no renames, made no function-boundary changes, and made no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0052a830 CD3DApplication__FindDepthStencilFormat` | Corrected to `bool __thiscall CD3DApplication__FindDepthStencilFormat(void * this, uint adapter_index, int device_type, int target_format, int * out_depth_stencil_format)`. Source reference `d3dapp.cpp` names the helper; retail xref `0x00529f8f` from `CD3DApplication__BuildDeviceList` calls it. The body reads `this+0x330b4` and `this+0x330b8` min depth/stencil requirement fields, uses the Direct3D object pointer at `this+0x32e9c`, probes observed D3DFORMAT candidate constants through vtable slots `+0x28` and `+0x30`, writes the accepted format through the output pointer, and returns true/false. |
| `0x0052aaf0 CD3DApplication__MsgProc` | Base CD3DApplication window-message handler with DATA vtable ref `0x005e4ae4` and raw WndProc-style callsite `0x00512fb5`. Source reference `d3dapp.cpp` plus `PCLTShell::MsgProc` forwarding tie the row to base shell message handling: min-track-size, active/windowed flags, fullscreen cursor suppression, command/system-command filters, mouse-move client-coordinate forwarding, timer stop/start around sizing/move, resize through `CD3DApplication__Resize3DEnvironment`, reset marking via `CEngine__MarkDeviceResetPending`, and fallback `DefWindowProcA`. |

Read-back evidence:

- `ApplyD3DApplicationWindowDepthWave862.java dry`: `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyD3DApplicationWindowDepthWave862.java apply`: `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0`, with two `READBACK_OK` rows.
- `ApplyD3DApplicationWindowDepthWave862.java final dry`: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 2 metadata rows, 2 tag rows, 3 xref rows, 882 instruction rows, and 2 decompile rows.
- Queue after Wave862: 6105 total, 5804 commented, 301 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5804/6105 = 95.07%`, strict clean-signature proxy `5804/6105 = 95.07%`.
- Next raw commentless row: `0x0052e180 CInstructionOP_PLUS__VFunc_00_0052e180`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-144206_post_wave862_d3dapplication_window_depth_verified`, 19 files, 172264327 bytes, `DiffCount=0`.

What this proves:

- The two target function rows exist in the saved Ghidra project.
- The saved function comments and tags include `d3dapplication-window-depth-wave862` and `wave862-readback-verified`.
- The `FindDepthStencilFormat` signature correction is present in saved Ghidra read-back.
- The observed bodies are static retail Ghidra evidence tied to xrefs, decompile/instruction exports, and source-reference context.

What remains unproven:

- Exact `CD3DApplication` field layout.
- Exact Direct3D enum semantics beyond observed candidate constants and source-reference names.
- Runtime window/device-loss/device-selection behavior.
- BEA patching behavior.
- Rebuild parity.
