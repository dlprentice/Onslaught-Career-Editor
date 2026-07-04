# Display Settings & Screen Mode Analysis

> **Source**: Ghidra analysis of BEA.exe (Steam release)
> **Date**: December 2025
> **Related**: See `../windowed-mode-analysis.md` for windowed mode investigation

## Overview

Battle Engine Aquila retail imports `d3d9.dll` for rendering, but parts of its app-shell/menu flow still resemble older DirectX sample-framework wiring (`d3dapp.cpp` style command routing). Display initialization is handled by `CD3DApplication`. The game supports fullscreen mode with various resolutions, and has vestigial windowed mode support that does not behave robustly in the retail build.

## Key Functions

| Address | Function | Purpose |
|---------|----------|---------|
| 0x005286e0 | `CD3DApplication__LoadCardIdAndApplyVendorTweaks` | Wave571 retail `cardid.txt` tweak loader; opens the supplied path, parses adapter/range/tweak rows, scans `DAT_0089c018` CVar entries, and applies matching tweak values |
| 0x00528f80 | `CD3DApplication__Init` | Wave572 constructor/init; seeds global app pointer, defaults, and 640x480 creation dimensions |
| 0x005290a0 | `CD3DApplication__Create` | Wave572 D3D app create path; Direct3DCreate9, device-list build, window create, environment init, timer start |
| 0x00529350 | `CD3DApplication__BuildDeviceList` | Wave572 adapter/device/mode enumeration and HAL/REF/depth/texture/MSAA probes |
| 0x0052af00 | `CD3DApplication__Initialize3DEnvironment` | Wave572 device create/reset path with cardid/CVar tweaks, presentation parameters, fallbacks, cursor/stats/backbuffer state |
| 0x0052b760 | `CD3DApplication__Resize3DEnvironment` | Wave572 D3D reset and resource restore helper after size/mode changes |
| 0x0052b840 | `CD3DApplication__ToggleFullscreen` | Wave572 fullscreen/windowed toggle and `ForceWindowed` fallback path |
| 0x0052ba50 | `CD3DApplication__ForceWindowed` | Wave572 fallback: selects compatible windowable adapter/device/mode |
| 0x0052bb80 | `CD3DApplication__Reset3DEnvironment` | Wave572 optional select-device dialog and environment reset path |
| 0x0052bc80 | `CD3DApplication__SelectDeviceProc` | Wave572 stdcall device-selection dialog callback (adapter/device/mode/MSAA) |
| 0x0052c430 | `CD3DApplication__Cleanup3DEnvironment` | Wave572 D3D cleanup/refcount logging path |
| 0x0052c4f0 | `CD3DApplication__DisplayErrorMsg` | Wave572 retail fatal/error dispatch for D3D init/reset failures |
| 0x0052c8d0 | `CD3DApplication__SetDeviceCursorFromIcon` | Wave572 icon mask/color to D3D cursor surface converter |
| 0x0052c730 | `CD3DApplication__SetResolution` | Wave572 stores requested width/height; no in-function clamp |
| 0x0052c780 | `ScreenShape_UpdateAspectScale` | Applies 4:3 vs 16:9 scaling based on `g_ScreenShape` |
| 0x005be622 | `Direct3DCreate9` | Wave739 d3d9.dll import thunk signature hardening |
| 0x005be628 | `HResultToString` | Wave739 HRESULT-to-C-string mapper signature hardening |

### Wave739 D3D Runtime Tail (0x005be622-0x005c9c66)

Wave739 D3D runtime tail saved comments/tags/signatures for `0x005be622 Direct3DCreate9` and `0x005be628 HResultToString` with the `d3d-runtime-tail-wave739` and `wave739-readback-verified` tags.

- `Direct3DCreate9(uint sdk_version)` is a six-byte import thunk that jumps through IAT pointer `0x005d8348`. `CD3DApplication__Create` caller `0x005290bc` pushes SDK version `0x1f` and stores returned EAX at `CD3DApplication +0x32e9c`.
- `HResultToString(int hresult)` is used by 22 D3D/render/texture error paths. Xref-site instruction evidence shows one HRESULT pushed before each call and returned EAX used as a log/message string; the full instruction export has a single `RET 0x4` at `0x005c9c66`, and sampled return target `0x0060bc44` resolves to `E_ABORT`.

Queue telemetry after Wave739: `6098` total, `4351` commented, `1747` commentless, `1215` exact-undefined signatures, `36` `param_N`, comment-backed proxy `4351/6098 = 71.35%`, strict proxy `4293/6098 = 70.40%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005d04e0 DirectInput8Create`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-135016_post_wave739_d3d_runtime_tail_verified`.

Scope boundary: imported `d3d9.dll` behavior, runtime graphics behavior, runtime error-reporting behavior, exact HRESULT table completeness, BEA patching, and rebuild parity remain deferred.

### Wave571 CardID / CVar Tweak Loader (0x005286e0-0x00528b00)

Wave571 hardened the retail-only display tweak loader and adjacent CVar helpers:

- `CD3DApplication__LoadCardIdAndApplyVendorTweaks(void * cardid_path)` opens the supplied file path, parses Version/Vendor/Device/range/tweak rows against the current adapter record, scans the global CVar list at `DAT_0089c018`, logs `Setting tweak`, and invokes the matched CVar vfunc.
- `CVar__Init(void * this, void * cvar_name, int initial_value)` links CVar records into `DAT_0089c018`; `RET 0x8` proves the name and initial-value stack arguments.
- `CVar__SetValueRounded(void * this, float value)` rounds the input float and stores the integer at `this+0x0c`; `RET 0x4` proves one stack argument.
- `CEngine__InvokeCallbackIfStateMinusOne(void * this, int callback_value)` removed a phantom second parameter and calls the first vfunc only when `this+0x0c == -1`.

This is saved static Ghidra read-back only. Exact cardid grammar, exact CVar layout, source identity, runtime D3D behavior, BEA patching, and rebuild parity remain deferred.

### Wave1212 Options Detail/Tweak Current-Risk Review

Wave1212 (`wave1212-options-detail-tweak-current-risk-review`) re-read `LandscapeDetail_SetLevel`, `LandscapeDetail_GetLevel`, `CTreeDetail__SetQualityLevel`, `CMultiSample__GetSampleCountLabel`, `CReconnectInterface__VFunc_07_00527d00`, `CTweak__ctor_base`, `CTweak__dtor_base`, and `CTweak__dtor_base_thunk_004530a0` as the active options/detail/tweak current-risk cluster. The read-only review ties landscape detail globals `0x009c7c54`/`0x009c7c56`, tree quality forwarding to `CRTMesh__SetQualityLevel`, MSAA label fallback `0xd4`, and `-landscape0/-landscape1/-landscape2` CLI reconnect-interface setters into one static display/options path. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-065722_post_wave1212_options_detail_tweak_current_risk_review_verified`. Runtime options-menu behavior, runtime CLI/tweak behavior, runtime device behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

### Wave572 D3D Application Shell (0x00528f80-0x0052cd20)

Wave1092 (`d3d-application-shell-review-wave1092`) re-read this saved Wave572 surface with fresh metadata, tag, xref, instruction, decompile, vtable, queue, and backup evidence and made no mutation. Primary exports verified `15` metadata rows, `15` tag rows, `41` xref rows, `4022` function-body instruction rows, and `15` decompile rows; context exports verified `6` metadata rows, `6` tag rows, `79` xref rows, `877` function-body instruction rows, and `6` decompile rows; CD3DApplication vtable `0x005e4ad0` exported `6` OK slots, including `CD3DApplication__Create` and `CD3DApplication__MsgProc`. The re-audit anchors include `0x00528f80 CD3DApplication__Init`, `0x005290a0 CD3DApplication__Create`, `0x00529350 CD3DApplication__BuildDeviceList`, `0x0052af00 CD3DApplication__Initialize3DEnvironment`, `0x0052b840 CD3DApplication__ToggleFullscreen`, `0x0052ba50 CD3DApplication__ForceWindowed`, `0x0052bc80 CD3DApplication__SelectDeviceProc`, and `0x0052cd20 CD3DApplication__PerfTimerCommand`. Queue closure remains `6410/6410 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface reaches `1560/1560 = 100.00%`; top-500 remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-152017_post_wave1092_d3d_application_shell_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`. Runtime Direct3D behavior, exact layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1092; d3d-application-shell-review-wave1092; 0x00528f80 CD3DApplication__Init; 0x005290a0 CD3DApplication__Create; 0x00529350 CD3DApplication__BuildDeviceList; 0x0052af00 CD3DApplication__Initialize3DEnvironment; 0x0052b840 CD3DApplication__ToggleFullscreen; 0x0052ba50 CD3DApplication__ForceWindowed; 0x0052bc80 CD3DApplication__SelectDeviceProc; 0x0052cd20 CD3DApplication__PerfTimerCommand; 0x005e4ad0; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-152017_post_wave1092_d3d_application_shell_review_verified; no mutation.

Wave572 hardened the adjacent retail `CD3DApplication` shell after fresh decompile/xref/instruction evidence and serialized dry/apply/read-back:

- `CD3DApplication__Init(void * this)` seeds global `DAT_0089c0f4`, initializes ten adapter-info blocks, installs the vtable, clears device/window/ready/timer fields, and sets 640x480 creation dimensions.
- `CD3DApplication__Create(void * this, void * hinstance)` calls `Direct3DCreate9(0x1f)`, builds the device list, registers/creates the D3D window when needed, initializes the environment, starts the perf timer, and marks the app ready.
- `CD3DApplication__BuildDeviceList(void * this)` enumerates adapters, devices, modes, depth-stencil, texture, and multisample support, with widescreen allowance through `DAT_0089c0ac`.
- `CD3DApplication__Initialize3DEnvironment(void * this, bool reuse_existing_device)` applies cardid/CVar tweaks, builds presentation parameters, creates or resets the device, falls back from lockable backbuffer/multisampling/friendly modes, updates stats/backbuffer/cursor state, and calls init/restore vfuncs.
- `CD3DApplication__Resize3DEnvironment`, `CD3DApplication__ToggleFullscreen`, `CD3DApplication__ForceWindowed`, and `CD3DApplication__Reset3DEnvironment` cover the reset/toggle/fallback/dialog commit shell around the D3D device.
- `CD3DApplication__SelectDeviceProc` is a four-argument stdcall Win32 dialog proc for adapter/device/mode/MSAA selection controls.
- `CD3DApplication__Cleanup3DEnvironment` releases app-owned D3D state and logs device/interface refcount text through `DebugTrace`.
- `CD3DApplication__DisplayErrorMsg` maps HRESULT-like failures to localized fatal string ids `0xb6` through `0xc5` and returns the input error code.
- `CD3DApplication__SetResolution` only stores width at `this+0x330bc` and height at `this+0x330c0`; it does not clamp. The older pseudo-C below has been corrected accordingly.
- `ScreenShape_UpdateAspectScale` writes `this+0x32e90` from backbuffer dimensions and `g_ScreenShape`.
- `CD3DApplication__SetDeviceCursorFromIcon` converts Win32 icon mask/color bitmap data into a D3D cursor surface.
- `CD3DApplication__PerfTimerCommand` returns `double` timer values through `QueryPerformanceCounter` or `timeGetTime` fallback.

Runtime D3D behavior, exact D3D/application/dialog/object layouts, exact source identity, BEA patching, and rebuild parity remain deferred.

### CD3DApplication::Init (0x00528f80)

Sets default values:
- Default resolution: 640x480
- Default mode: Fullscreen
- Initializes D3D object pointers to NULL

### CD3DApplication::BuildDeviceList (0x00529350)

Enumerates display adapters and modes:
- Queries available resolutions from D3D
- Filters modes based on minimum requirements (640x480)
- Checks for widescreen mode support via `ALLOW_WIDESCREEN_MODES` config
- Populates internal mode list for Video Options menu

### CD3DApplication::Initialize3DEnvironment (0x0052af00)

Critical function for display mode setup:
- Checks `m_bWindowed` flag to determine fullscreen vs windowed
- Creates D3D device with appropriate presentation parameters
- Handles device creation failures with fallback options
- Sets up swap chain and back buffers

### Additional Recovered Retail Helpers

Wave572 supersedes the older Wave33 shorthand for this helper group with saved signatures/comments/tags and post-export read-back.

### CD3DApplication::SetResolution (0x0052c730)

```c
void CD3DApplication::SetResolution(int width, int height)
{
    this->m_dwCreationWidth = width;
    this->m_dwCreationHeight = height;
}
```

Wave572 read-back shows no clamp inside `CD3DApplication__SetResolution`. Minimum/default handling is observed elsewhere in mode enumeration and command-line/config flow, not in this setter body.

## Key Data Addresses

### Global Instances

| Address | Type | Description |
|---------|------|-------------|
| 0x0089c0f4 | `CD3DApplication*` | Global D3D application instance pointer |

### Configuration Flags

| Address | Type | Description |
|---------|------|-------------|
| 0x00662f3e | byte | Guard flag for `-forcewindowed` (canonical Steam hash `74154bfa...` = 0x01; some historical baselines reported 0x00) |
| 0x0082b484 | int | Aspect ratio mode: 1=16:9, 2=1:1, else=4:3 |

## Structure Offsets

### CD3DApplication (instance at 0x0089c0f4)

| Offset | Type | Field | Description |
|--------|------|-------|-------------|
| 0x32e64 | bool | m_bWindowed | 0=fullscreen, non-zero=windowed |
| 0x330bc | DWORD | m_dwCreationWidth | Requested render width |
| 0x330c0 | DWORD | m_dwCreationHeight | Requested render height |

## Key Strings

| Address | String | Context |
|---------|--------|---------|
| 0x0064be10 | `"ALLOW_WIDESCREEN_MODES"` | Config file key for enabling 16:9 modes |
| 0x0064bba8 | `"Video Options"` (Unicode) | Menu title string |
| 0x006244a0 | `"-forcewindowed"` | CLI parameter string |

## Command-Line Parameters

### -res W H

Sets custom resolution:
```
BEA.exe -res 1920 1080
```

Parsed in `CLIParams::ParseCommandLine`, stored at offsets 0x164/0x168. Minimum enforced: 640x480.

### -forcewindowed

Attempts to run in windowed mode:
```
BEA.exe -forcewindowed
```

**Status**: In the canonical Steam hash used in this repo (`74154bfa...`), guard flag `0x00662f3e` is `0x01`, so parser gating does not block `-forcewindowed`; startup fullscreen flow can still override launch mode.

## Aspect Ratio Handling

The game supports multiple aspect ratios, controlled by the value at 0x0082b484:

| Value | Aspect Ratio | Notes |
|-------|--------------|-------|
| 1 | 16:9 | Widescreen mode |
| 2 | 1:1 | Square pixels (rare) |
| other | 4:3 | Default/standard |

Widescreen modes are gated by the `ALLOW_WIDESCREEN_MODES` configuration option, which may need to be enabled in a config file or via external patch.

## Resolution Constraints

- **Minimum**: 640x480 observed in mode enumeration and command-line/config handling; Wave572 shows `SetResolution` itself does not clamp
- **Default**: 640x480 (set in `Init`)
- **Maximum**: Limited by display adapter capabilities (enumerated in `BuildDeviceList`)

## Localization (0x00524830)

`0x00524830` is **not** the Video Options handler in this build; it is `Localization__GetStringById` (string lookup by id and `g_LanguageIndex`).

The retail Video Options surface is now mapped through `CFEPOptions__ProcessInput`, `CFEPOptions__Update`, `CFEPOptions__SaveDefaultOptions`, `CFEPOptions__WriteDefaultOptionsFile`, and `CFEPOptions__EnsureOptionsContext`. Remaining uncertainty is limited to individual sub-item behavior below those mapped handlers.

## Known Issues

1. **Windowed mode is multi-gate**: Canonical Steam hash `74154bfa...` already has `0x00662f3e = 0x01`; inconsistent windowed startup is primarily startup-flow behavior unless a variant binary has this byte at `0x00`.

2. **Widescreen requires config**: 16:9 modes may not appear in Video Options without enabling `ALLOW_WIDESCREEN_MODES`.

3. **Resolution changes may require restart**: Some resolution changes may not take effect until game restart.

## Related Documentation

- `../windowed-mode-analysis.md` - Detailed investigation of windowed mode failure
- `../widescreen-patch-analysis.md` - Analysis of community widescreen patches
- `CLIParams.cpp/_index.md` - Full CLI parameter documentation
