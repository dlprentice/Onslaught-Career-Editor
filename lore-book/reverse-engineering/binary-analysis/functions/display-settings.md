# Display Settings & Screen Mode Analysis

> **Source**: Ghidra analysis of BEA.exe (Steam release)
> **Date**: December 2025
> **Related**: See `../windowed-mode-analysis.md` for windowed mode investigation

## Overview

Battle Engine Aquila retail imports `d3d9.dll` for rendering, but parts of its app-shell/menu flow still resemble older DirectX sample-framework wiring (`d3dapp.cpp` style command routing). Display initialization is handled by `CD3DApplication`. The game supports fullscreen mode with various resolutions, and has vestigial windowed mode support that does not behave robustly in the retail build.

## Key Functions

| Address | Function | Purpose |
|---------|----------|---------|
| 0x00528f80 | `CD3DApplication::Init` | Initializes defaults (640x480) |
| 0x005290a0 | `CD3DApplication::Create` | Creates D3D device |
| 0x00529350 | `CD3DApplication::BuildDeviceList` | Enumerates available display modes |
| 0x0052af00 | `CD3DApplication::Initialize3DEnvironment` | Creates device, handles fullscreen/windowed switch |
| 0x0052b760 | `CD3DApplication::Resize3DEnvironment` | Resets D3D device and restores resources after size/mode changes |
| 0x0052b840 | `CD3DApplication::ToggleFullscreen` | Toggles fullscreen/windowed mode and reapplies presentation params |
| 0x0052ba50 | `CD3DApplication::ForceWindowed` | Fallback: selects compatible windowable adapter/device/mode |
| 0x0052bc80 | `CD3DApplication::SelectDeviceProc` | Device-selection dialog callback (adapter/device/mode/MSAA) |
| 0x0052c4f0 | `CD3DApplication::DisplayErrorMsg` | Retail fatal/error dispatch for D3D init/reset failures |
| 0x0052c8d0 | `CD3DApplication::SetDeviceCursorFromIcon` | Converts Win32 icon mask/color into D3D cursor surface |
| 0x0052c730 | `CD3DApplication::SetResolution` | Sets width/height for rendering |
| 0x0052c780 | `ScreenShape_UpdateAspectScale` | Applies 4:3 vs 16:9 scaling based on `g_ScreenShape` |

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

### Additional Recovered Retail Helpers (Wave33)

- `CD3DApplication::Resize3DEnvironment` (`0x0052b760`): resize/reset path used by WM_EXITSIZEMOVE and fullscreen transitions.
- `CD3DApplication::ToggleFullscreen` (`0x0052b840`): main fullscreen toggle path with `ForceWindowed` fallback behavior.
- `CD3DApplication::ForceWindowed` (`0x0052ba50`): fallback mode-selection path when fullscreen reset fails or windowed-only device is required.
- `CD3DApplication::SelectDeviceProc` (`0x0052bc80`): dialog proc for adapter/device/mode/MSAA selection UI.
- `CD3DApplication::DisplayErrorMsg` (`0x0052c4f0`): retail error routing to localized fatal messages for D3D failures.
- `CD3DApplication::SetDeviceCursorFromIcon` (`0x0052c8d0`): icon-to-cursor-surface upload helper used during D3D environment initialization/reset.

### CD3DApplication::SetResolution (0x0052c730)

```c
void CD3DApplication::SetResolution(int width, int height)
{
    // Minimum resolution enforcement
    if (width < 640) width = 640;
    if (height < 480) height = 480;

    this->m_dwCreationWidth = width;
    this->m_dwCreationHeight = height;
}
```

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

- **Minimum**: 640x480 (enforced in `SetResolution`)
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
