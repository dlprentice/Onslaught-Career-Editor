# Ghidra D3D Application Shell Review Wave1092

Status: complete read-only static review
Date: 2026-06-04
Scope: `d3d-application-shell-review-wave1092`

Wave1092 re-read the saved Wave572 `CD3DApplication` application-shell surface with fresh metadata, tag, xref, instruction, decompile, vtable, queue, and backup evidence. The review made no Ghidra rename, no signature change, no comment/tag mutation, no function-boundary change, no executable-byte change, no BEA launch, and no installed-game or runtime-file mutation.

Reviewed rows:

| Address | Saved row | Fresh static evidence |
| --- | --- | --- |
| `0x00528f80 CD3DApplication__Init` | `void * __thiscall CD3DApplication__Init(void * this)` | Seeds global app pointer `DAT_0089c0f4`, installs defaults, initializes adapter records, and sets 640x480 creation dimensions. |
| `0x005290a0 CD3DApplication__Create` | `int __thiscall CD3DApplication__Create(void * this, void * hinstance)` | Calls `Direct3DCreate9(0x1f)`, builds the device list, creates/registers the D3D window, initializes the 3D environment, and starts the perf timer. |
| `0x00529350 CD3DApplication__BuildDeviceList` | `int __thiscall CD3DApplication__BuildDeviceList(void * this)` | Enumerates adapters/devices/modes and probes depth-stencil, texture, and multisample support, with widescreen allowance through `DAT_0089c0ac`. |
| `0x0052af00 CD3DApplication__Initialize3DEnvironment` | `int __thiscall CD3DApplication__Initialize3DEnvironment(void * this, bool reuse_existing_device)` | Applies cardid/CVar tweaks, builds presentation parameters, creates/resets the D3D device, and drives resource init/restore fallback paths. |
| `0x0052b760 CD3DApplication__Resize3DEnvironment` | `int __thiscall CD3DApplication__Resize3DEnvironment(void * this)` | Resets presentation/device state after size or mode changes and refreshes cursor/perf state. |
| `0x0052b840 CD3DApplication__ToggleFullscreen` | `int __thiscall CD3DApplication__ToggleFullscreen(void * this)` | Switches fullscreen/windowed state, updates saved window bounds and `g_ScreenShape`, and can fall back through `CD3DApplication__ForceWindowed`. |
| `0x0052ba50 CD3DApplication__ForceWindowed` | `int __thiscall CD3DApplication__ForceWindowed(void * this, bool target_windowed_state)` | Chooses a compatible windowable adapter/device/mode and re-enters `CD3DApplication__Initialize3DEnvironment`; reports failures through `CD3DApplication__DisplayErrorMsg`. |
| `0x0052bb80 CD3DApplication__Reset3DEnvironment` | `int __thiscall CD3DApplication__Reset3DEnvironment(void * this, bool show_device_dialog, int reset_context)` | Wraps optional device-selection dialog flow around environment reset and reset-context tracking. |
| `0x0052bc80 CD3DApplication__SelectDeviceProc` | `int __stdcall CD3DApplication__SelectDeviceProc(int dialog_hwnd, int message, int wparam, int lparam)` | Win32 dialog proc for adapter/device/mode/MSAA selection; handles `WM_INITDIALOG` and `WM_COMMAND` around global selection state `DAT_0089c048`. |
| `0x0052c430 CD3DApplication__Cleanup3DEnvironment` | `void __thiscall CD3DApplication__Cleanup3DEnvironment(void * this)` | Releases app-owned D3D state and logs final-cleanup/refcount details through `DebugTrace`. |
| `0x0052c4f0 CD3DApplication__DisplayErrorMsg` | `int __stdcall CD3DApplication__DisplayErrorMsg(int error_code, int message_type)` | Maps D3D init/reset failures to fatal/error message ids including `0xb6` through `0xc5`, returning the input error code. |
| `0x0052c730 CD3DApplication__SetResolution` | `void __thiscall CD3DApplication__SetResolution(void * this, int width, int height)` | Stores requested width at `this+0x330bc` and height at `this+0x330c0` without an in-function clamp. |
| `0x0052c780 ScreenShape_UpdateAspectScale` | `void __fastcall ScreenShape_UpdateAspectScale(void * d3d_app)` | Updates the aspect scale from backbuffer dimensions and `g_ScreenShape`, including 4:3 and 16:9 paths. |
| `0x0052c8d0 CD3DApplication__SetDeviceCursorFromIcon` | `int __cdecl CD3DApplication__SetDeviceCursorFromIcon(void * d3d_device, int icon_handle)` | Converts Win32 `ICONINFO` mask/color bitmap data into a D3D cursor surface through `GetDIBits`. |
| `0x0052cd20 CD3DApplication__PerfTimerCommand` | `double __stdcall CD3DApplication__PerfTimerCommand(int command)` | Services timer reset/start/stop/advance commands through `QueryPerformanceCounter` or `timeGetTime` fallback and returns elapsed time. |

Vtable/context evidence:

- `0x005e4ad0` exported `6` CD3DApplication vtable slots, all `OK`.
- Slot `4` points at `0x005290a0 CD3DApplication__Create`.
- Slot `5` points at `0x0052aaf0 CD3DApplication__MsgProc`.
- Context exports re-read `CD3DApplication__LoadCardIdAndApplyVendorTweaks`, `CVar__Init`, `CVar__SetValueRounded`, `CD3DApplication__FindDepthStencilFormat`, `CD3DApplication__MsgProc`, and `PlatformInput__ClearAllKeyStateTables`.

Evidence counts:

- Primary exports: `15` metadata rows, `15` tag rows, `41` xref rows, `4022` function-body instruction rows, and `15` decompile rows.
- Context exports: `6` metadata rows, `6` tag rows, `79` xref rows, `877` function-body instruction rows, and `6` decompile rows.
- Vtable export: `6` slots, all `OK`.
- Queue closure remains `6410/6410 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress reaches `1560/1560 = 100.00%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-152017_post_wave1092_d3d_application_shell_review_verified`, 19 files, 175541127 bytes, `DiffCount=0`.

What this proves:

- The saved D3D application-shell function objects still exist in the loaded Ghidra database with coherent names, signatures, comments, tags, xrefs, instruction bodies, decompile output, vtable slots, and backup read-back.
- The Wave572 static D3D shell treatment remains coherent after fresh Wave1092 re-audit exports.
- The expanded post-100 static surface tracker has reached `1560/1560 = 100.00%`.

What remains separate proof:

- Runtime Direct3D device creation/reset/window/dialog behavior.
- Exact `CD3DApplication` and Direct3D object layouts beyond observed offsets.
- Exact source-body identity for all retail helper bodies.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1092; d3d-application-shell-review-wave1092; 0x00528f80 CD3DApplication__Init; 0x005290a0 CD3DApplication__Create; 0x00529350 CD3DApplication__BuildDeviceList; 0x0052af00 CD3DApplication__Initialize3DEnvironment; 0x0052b840 CD3DApplication__ToggleFullscreen; 0x0052ba50 CD3DApplication__ForceWindowed; 0x0052bc80 CD3DApplication__SelectDeviceProc; 0x0052cd20 CD3DApplication__PerfTimerCommand; 0x005e4ad0; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-152017_post_wave1092_d3d_application_shell_review_verified; no mutation.
