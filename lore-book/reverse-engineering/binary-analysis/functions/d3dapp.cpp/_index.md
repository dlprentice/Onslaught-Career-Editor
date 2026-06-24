# d3dapp.cpp - Direct3D Application Shell

**Source File:** `C:\dev\ONSLAUGHT2\d3dapp.cpp`

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

`d3dapp.cpp` contains the PC Direct3D application base layer used by the Lost Toys shell. The retail rows here are important connective infrastructure: they bridge the game shell, window messages, device reset/loss handling, and Direct3D device-format selection. Static source names are useful, but Steam retail Ghidra read-back remains the authority for signatures, xrefs, and exact bounded claims.

Wave1211 (`wave1211-score17-residual-current-risk-review`) re-read and tag-normalized `0x0052a830 CD3DApplication__FindDepthStencilFormat` as one of `8 score-17 residual current-risk rows` in the current-risk denominator. Fresh evidence keeps the row tied to `CD3DApplication__BuildDeviceList` at callsite `0x00529f8f`, the accepted depth/stencil output pointer, and the existing `RET 0x10` stack cleanup signature model. No rename, signature, comment, function-boundary, or executable-byte change was made. Active current-risk accounting after the wave is `1110/1179 = 94.15%`; verified backup: `G:\GhidraBackups\BEA_20260607-061324_post_wave1211_score17_residual_current_risk_review_verified`. Runtime Direct3D device selection, exact `CD3DApplication` layout, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave909 engine/platform support static review (`engine-platform-support-static-review-wave909`) records the D3D application shell side of a static-coherent engine/platform/math/memory support core. D3D anchors include `CD3DApplication__Init` and `CD3DApplication__BuildDeviceList`. Verified backup: `G:\GhidraBackups\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified`. Runtime device handling and exact layouts remain separate proof.

Wave923 (`hud-radar-pause-render-review-wave923`) re-reviewed `0x0052a830 CD3DApplication__FindDepthStencilFormat` as part of a HUD/radar/pause/sprite/D3D visible-render support slice. Fresh metadata/tags/xref/instruction/decompile evidence kept the Wave862 device-list depth/stencil selector claim intact; no mutation was needed. Wave911 focused re-audit progress after this slice is `86/1408 = 6.11%`, while export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260527-210516_post_wave923_hud_radar_pause_render_review_verified`. Runtime Direct3D device selection, exact CD3DApplication layout, patch behavior, and rebuild parity remain separate proof.

## 2026-06-06 Wave1171 D3D Device Profile Re-Audit

Wave1171 (`wave1171-d3d-device-profile-current-risk-review`) re-read two D3D device profile current-risk rows: `D3DDeviceProfileTable__GetAdapterRecord` and `D3DDeviceProfile__PackDeviceIndexKey`. Fresh evidence ties the profile-table accessor to `OptionsTail_Write`, and the packer to both `OptionsTail_Write` and `OptionsTail_Read`, keeping these rows in the options/device-profile persistence map rather than the stale CCareer helper lane. The review is read-only: no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change. Verified backup: `G:\GhidraBackups\BEA_20260606-064430_post_wave1171_d3d_device_profile_current_risk_review_verified`.

Probe token anchor: Wave1171; wave1171-d3d-device-profile-current-risk-review; 668/1179 = 56.66%; 2 D3D device profile current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 511; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult deferred; 0 / 0 / 0; 6411/6411 = 100.00%; 3 xref rows; 54 instruction rows; D3DDeviceProfileTable__GetAdapterRecord; D3DDeviceProfile__PackDeviceIndexKey; OptionsTail_Write; OptionsTail_Read; G:\GhidraBackups\BEA_20260606-064430_post_wave1171_d3d_device_profile_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Runtime Direct3D device/profile selection behavior, exact display/profile table layout, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

## 2026-06-04 Wave1092 D3D Application Shell Re-Audit

Wave1092 (`d3d-application-shell-review-wave1092`) re-read the saved Wave572 D3D application-shell tranche with no mutation. Representative anchors include `0x00528f80 CD3DApplication__Init`, `0x005290a0 CD3DApplication__Create`, `0x00529350 CD3DApplication__BuildDeviceList`, `0x0052af00 CD3DApplication__Initialize3DEnvironment`, `0x0052b840 CD3DApplication__ToggleFullscreen`, `0x0052ba50 CD3DApplication__ForceWindowed`, `0x0052bc80 CD3DApplication__SelectDeviceProc`, and `0x0052cd20 CD3DApplication__PerfTimerCommand`.

Fresh evidence verified `15` primary metadata rows, `15` primary tag rows, `41` primary xref rows, `4022` primary instruction rows, `15` primary decompile rows, `6` context metadata rows, `6` context tag rows, `79` context xref rows, `877` context instruction rows, `6` context decompile rows, and CD3DApplication vtable `0x005e4ad0` with `6` OK slots. Static context includes `DAT_0089c0f4`, `DAT_0089c0ac`, `Direct3DCreate9(0x1f)`, `g_ScreenShape`, `CD3DApplication__FindDepthStencilFormat`, and `CD3DApplication__MsgProc`.

Queue closure remains `6410/6410 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface reaches `1560/1560 = 100.00%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260604-152017_post_wave1092_d3d_application_shell_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`. Runtime Direct3D device creation/reset/window/dialog behavior, exact `CD3DApplication` and Direct3D layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1092; d3d-application-shell-review-wave1092; 0x00528f80 CD3DApplication__Init; 0x005290a0 CD3DApplication__Create; 0x00529350 CD3DApplication__BuildDeviceList; 0x0052af00 CD3DApplication__Initialize3DEnvironment; 0x0052b840 CD3DApplication__ToggleFullscreen; 0x0052ba50 CD3DApplication__ForceWindowed; 0x0052bc80 CD3DApplication__SelectDeviceProc; 0x0052cd20 CD3DApplication__PerfTimerCommand; 0x005e4ad0; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-152017_post_wave1092_d3d_application_shell_review_verified; no mutation.

## 2026-05-25 Wave862 D3DApplication Window/Depth Read-Back

Wave862 D3DApplication window/depth (`d3dapplication-window-depth-wave862`, `wave862-readback-verified`) saved comments/tags for `0x0052a830 CD3DApplication__FindDepthStencilFormat` and `0x0052aaf0 CD3DApplication__MsgProc`. The pass corrected one signature, made no renames, made no function-boundary changes, and made no executable-byte changes.

Probe token anchor: `Wave862 D3DApplication window/depth`; `d3dapplication-window-depth-wave862`; `0x0052a830 CD3DApplication__FindDepthStencilFormat`; `0x0052aaf0 CD3DApplication__MsgProc`; `0x0052e180 CInstructionOP_PLUS__VFunc_00_0052e180`; `5804/6105 = 95.07%`; `G:\GhidraBackups\BEA_20260525-144206_post_wave862_d3dapplication_window_depth_verified`.

| Address | Static evidence |
| --- | --- |
| `0x0052a830 CD3DApplication__FindDepthStencilFormat` | Corrected to `bool __thiscall CD3DApplication__FindDepthStencilFormat(void * this, uint adapter_index, int device_type, int target_format, int * out_depth_stencil_format)`. Retail xref `0x00529f8f` from `CD3DApplication__BuildDeviceList`; body probes observed D3DFORMAT candidate constants through Direct3D object vtable slots `+0x28` and `+0x30`, writes the accepted value through the output pointer, and returns true/false. |
| `0x0052aaf0 CD3DApplication__MsgProc` | Base window-message handler with DATA vtable ref `0x005e4ae4` and raw WndProc-style callsite `0x00512fb5`; handles active/windowed state, min track size, fullscreen cursor suppression, mouse forwarding, sizing/move timer commands, resize through `CD3DApplication__Resize3DEnvironment`, reset marking through `CEngine__MarkDeviceResetPending`, and fallback `DefWindowProcA`. |

Read-back evidence verified 2 metadata rows, 2 tag rows, 3 xref rows, 882 instruction rows, 2 decompile rows, queue refresh PASS, and backup `G:\GhidraBackups\BEA_20260525-144206_post_wave862_d3dapplication_window_depth_verified` with 19 files, 172264327 bytes, `DiffCount=0`. Post-Wave862 queue telemetry is 6105 total, 5804 commented, 301 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5804/6105 = 95.07%`, strict proxy `5804/6105 = 95.07%`, and next raw commentless row `0x0052e180 CInstructionOP_PLUS__VFunc_00_0052e180`.

Exact `CD3DApplication` field layout, exact Direct3D enum semantics beyond observed constants/source names, runtime window/device-loss/device-selection behavior, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Name | Evidence status |
| --- | --- | --- |
| `0x0052a830` | `CD3DApplication__FindDepthStencilFormat` | Wave862 corrected signature and saved bounded comment/tag evidence |
| `0x0052aaf0` | `CD3DApplication__MsgProc` | Wave862 saved bounded comment/tag evidence |
