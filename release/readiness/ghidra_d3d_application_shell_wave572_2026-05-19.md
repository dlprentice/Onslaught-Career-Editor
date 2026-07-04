# Ghidra D3D Application Shell Wave572 Readiness Note

Date: 2026-05-19
Status: PASS

## Scope

Wave572 hardened fifteen saved Ghidra rows in the retail D3D application-shell area:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00528f80` | `void * __thiscall CD3DApplication__Init(void * this)` | Constructor/init body: constructs ten adapter-info blocks, installs the vtable, stores global `DAT_0089c0f4`, clears device/window/ready/timer fields, and seeds 640x480 creation dimensions. |
| `0x005290a0` | `int __thiscall CD3DApplication__Create(void * this, void * hinstance)` | `RET 0x4` confirms one stack argument after `this`; the body calls `Direct3DCreate9(0x1f)`, builds the device list, registers/creates the D3D window, initializes the environment, and starts the perf timer. |
| `0x00529350` | `int __thiscall CD3DApplication__BuildDeviceList(void * this)` | Retail adapter/device/mode enumeration path: adapter count and display mode queries, small-mode and widescreen filters, HAL/REF capability probes, depth/texture/MSAA probes, and `DisplayErrorMsg` warnings. |
| `0x0052af00` | `int __thiscall CD3DApplication__Initialize3DEnvironment(void * this, bool reuse_existing_device)` | `RET 0x4` confirms the reuse flag; the body applies `cardid.txt`/CVar tweaks, builds presentation parameters, creates or resets the device, falls back from lockable backbuffer/MSAA/friendly modes, updates stats/backbuffer/cursor state, and calls init/restore vfuncs. |
| `0x0052b760` | `int __thiscall CD3DApplication__Resize3DEnvironment(void * this)` | ECX-only reset helper: invalidates device objects, resets with presentation parameters at `this+0x32e58`, refreshes the backbuffer description, optionally installs fullscreen cursor, restores device objects, and restarts/stops timer state. |
| `0x0052b840` | `int __thiscall CD3DApplication__ToggleFullscreen(void * this)` | ECX-only fullscreen/windowed toggle: selects active adapter/device/mode, uses `ForceWindowed` fallback, toggles `this+0x32e44`, recomputes `g_ScreenShape` aspect scale, calls `Resize3DEnvironment`, and restores saved bounds on windowed success. |
| `0x0052ba50` | `int __thiscall CD3DApplication__ForceWindowed(void * this, bool target_windowed_state)` | `RET 0x4` proves one explicit bool; scans for a compatible windowable adapter/device when the current one is unsuitable, invalidates/deletes device objects, calls `Initialize3DEnvironment(true)`, and reports failures. |
| `0x0052bb80` | `int __thiscall CD3DApplication__Reset3DEnvironment(void * this, bool show_device_dialog, int reset_context)` | `RET 0x8` proves two stack arguments; optionally shows the `SelectDeviceProc` dialog, commits selected adapter/device/mode state, invalidates device objects with `reset_context`, and calls `Initialize3DEnvironment(true)`. |
| `0x0052bc80` | `int __stdcall CD3DApplication__SelectDeviceProc(int dialog_hwnd, int message, int wparam, int lparam)` | `RET 0x10` confirms four stdcall arguments; handles Win32 dialog init/command paths and repopulates adapter/device/mode/multisample controls through `GetDlgItem`, `SendMessageA`, and `EndDialog`. |
| `0x0052c430` | `void __thiscall CD3DApplication__Cleanup3DEnvironment(void * this)` | ECX-only cleanup helper that invalidates/deletes device objects, releases `DAT_0089c04c` plus device/D3D interfaces, logs refcounts through `DebugTrace`, nulls pointers, and calls the final-cleanup vfunc. |
| `0x0052c4f0` | `int __stdcall CD3DApplication__DisplayErrorMsg(int error_code, int message_type)` | `RET 0x8` confirms two stack arguments; maps HRESULT-like error codes to localized fatal string ids `0xb6` through `0xc5`, returns the input error code, and keeps `message_type` for observed callsite stack shape. |
| `0x0052c730` | `void __thiscall CD3DApplication__SetResolution(void * this, int width, int height)` | `RET 0x8` confirms width and height after `this`; the body stores width at `this+0x330bc` and height at `this+0x330c0` without an in-function clamp. |
| `0x0052c780` | `void __fastcall ScreenShape_UpdateAspectScale(void * d3d_app)` | ECX-carried aspect-scale helper; writes `this+0x32e90` from current backbuffer height/width and `g_ScreenShape` with 16:9, mode-2 square, and 4:3 fallback constants. |
| `0x0052c8d0` | `int __cdecl CD3DApplication__SetDeviceCursorFromIcon(void * d3d_device, int icon_handle)` | Converts Win32 icon mask/color bitmap data into a D3D cursor surface through `ICONINFO`, `GetDIBits`, temp pixel buffers, and D3D surface upload/release. |
| `0x0052cd20` | `double __stdcall CD3DApplication__PerfTimerCommand(int command)` | `RET 0x4` confirms one command argument; returns a `double` timer value through `QueryPerformanceCounter` or `timeGetTime` fallback for start/stop/advance/absolute/app/elapsed commands. |

No `source-parity` tag was applied. This tranche is bounded to saved retail binary evidence; runtime D3D behavior, exact D3D/application/dialog/object layouts, exact source identity, BEA patching, and rebuild parity remain deferred.

## Verification

- Corrected dry pass: `updated=0 skipped=15 renamed=0 would_rename=0 missing=0 bad=0`
- Corrected apply pass: `updated=15 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Corrected final dry: `updated=0 skipped=15 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Timer return correction: the first Wave572 apply used an `int` return for `CD3DApplication__PerfTimerCommand`; read-back review corrected it to `double __stdcall CD3DApplication__PerfTimerCommand(int command)`, then reran dry/apply/verify and refreshed post exports.
- Post exports: `15` metadata rows, `15` tag rows, `41` xref rows, `1815` target instruction rows, and `15` target decompiles
- Focused probe: `py -3 tools\ghidra_d3d_application_shell_wave572_probe.py --check` PASS
- Npm wrapper: `cmd.exe /c npm run test:ghidra-d3d-application-shell-wave572` PASS
- Queue refresh: `6093` total functions, `2863` commented, `3230` commentless, `1479` exact-undefined signatures, `1144` `param_N` signatures
- Post-Wave572 comment-backed proxy: `2863 / 6093 = 46.99%`
- Post-Wave572 strict clean-signature proxy: `2812 / 6093 = 46.15%`
- Next queue head: `0x0052d040 CAsmInstruction__GetAttributeValue`
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-003701_post_wave572_d3d_application_shell_verified`
- Backup verification: `19` files, `160140167` bytes, source/destination manifest hash `791DC75A282371E851C32F34F34E59D13AE099580FB9576117C52EC8A029EC95`

## Limits

This is saved static Ghidra evidence only. No runtime D3D behavior was claimed. Exact D3D device, adapter/mode-list, presentation-parameter, dialog, cursor-surface, timer, and application-object layouts, exact source identity, BEA launch, game patching, and rebuild parity remain unproven.
