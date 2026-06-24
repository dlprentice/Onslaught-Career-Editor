# ltshell.cpp - Lost Toys Shell (Application Entry Point)

Wave1219 final current-risk closure note: `PCLTShell__ctor` remains mapped to platform shell construction and title/input-state initialization; verified backup `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`. Runtime launch behavior, exact shell layout, and rebuild parity remain separate proof.

**Source File:** `C:\dev\ONSLAUGHT2\ltshell.cpp`
**Debug String Address:** `0x0063dd8c`

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

`ltshell.cpp` contains the main Windows application entry point (WinMain) for Battle Engine Aquila. "LTShell" stands for "Lost Toys Shell" - the main application shell that initializes all subsystems, loads saved options, creates the game window, and runs the main game loop.

The RTTI class name `PCLTShell` (found at `0x0063dc60`) indicates this was implemented as a class on the PC platform.

## 2026-05-25 Wave862 D3DApplication Window/Depth Read-Back

Wave862 D3DApplication window/depth (`d3dapplication-window-depth-wave862`, `wave862-readback-verified`) documents important connective infrastructure in the base `CD3DApplication` rows used by the PC shell path. `0x0052aaf0 CD3DApplication__MsgProc` has DATA vtable ref `0x005e4ae4`, a raw WndProc-style callsite `0x00512fb5`, and source-reference context from `PCLTShell::MsgProc` forwarding into the base `CD3DApplication::MsgProc`. The same pass corrected `0x0052a830 CD3DApplication__FindDepthStencilFormat` to a source-aligned depth/stencil selector called from `CD3DApplication__BuildDeviceList`.

Probe token anchor: `Wave862 D3DApplication window/depth`; `0x0052a830 CD3DApplication__FindDepthStencilFormat`; `0x0052aaf0 CD3DApplication__MsgProc`; `d3dapplication-window-depth-wave862`; `5804/6105 = 95.07%`; `0x0052e180 CInstructionOP_PLUS__VFunc_00_0052e180`; `G:\GhidraBackups\BEA_20260525-144206_post_wave862_d3dapplication_window_depth_verified`.

This is saved static retail/source-reference evidence only. Exact `CD3DApplication` layout, runtime window/device-loss/device-selection behavior, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave852 PC Platform/Resource Tail Read-Back

Wave852 PC platform/resource tail (`pc-platform-resource-tail-wave852`, `wave852-readback-verified`) adds saved static evidence for the resource-descriptor table rows called by shell startup/shutdown: `0x00515fb0 CResourceDescriptorTable__InitDefaultMeshNames` from `CLTShell__InitializeRuntimeAndLoadCoreResources` and `0x00516450 CResourceDescriptorTable__FreeAllEntries` from `CLTShell__ShutdownRuntimeAndReleaseResources`. Probe token anchor: `Wave852 PC platform/resource tail`; `0x00515fb0 CResourceDescriptorTable__InitDefaultMeshNames`; `0x00516450 CResourceDescriptorTable__FreeAllEntries`; `default.msh`; `5736/6098 = 94.06%`; `0x005168d0 CPCSoundManager__dtor`; `G:\GhidraBackups\BEA_20260525-093157_post_wave852_pc_platform_resource_tail_verified`.

The initializer fills a global 0x428-byte-stride descriptor table with default mesh/resource names including `default.msh`, `cannon1.msh`, `radar1.msh`, `plane1.msh`, `tree2.msh`, `tank1.msh`, `Enemymech.msh`, `bloke.msh`, `EnemyT~1.msh`, `shell.msh`, `cockpit2.msh`, and `carrier.msh`, and sets `DAT_00896488` to `0x17`. The shutdown helper walks descriptor records from `DAT_0088a510` toward `0x00896868` and frees per-descriptor arrays through `CDXMemoryManager__Free`. Runtime resource loading/shutdown behavior, exact descriptor schema, full asset taxonomy, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave850 D3D Shader/Input Tail Read-Back

Wave850 D3D shader/input tail (`d3d-shader-input-tail-wave850`, `wave850-readback-verified`) added saved static evidence for the adjacent ltshell/source-wrapper band: `0x00513c70 CEngine__DrawIndexedPrimitives` aligns to source `D3D_DrawIndexedPrimitive`, `0x00513e90 CEngine__SetVertexShaderHandleCached` / `0x00513ec0 CEngine__SetVertexShaderHandleRaw` align to `D3D_SetVertexShader` style call paths, and `0x00513f20 CEngine__CreatePixelShaderFromText` aligns to `D3D_CreatePixelShader` context. Probe token anchor: `Wave850 D3D shader/input tail`; `D3D_DrawIndexedPrimitive`; `D3D_SetVertexShader`; `D3D_CreatePixelShader`; `5704/6098 = 93.54%`; `0x005140e0 CDXEngine__CaptureAviFrame`; `G:\GhidraBackups\BEA_20260525-081702_post_wave850_d3d_shader_input_tail_verified`.

The same pass corrected `0x00513ff0` to `CEngine__DeviceCall16C_CreateVertexShaderLike` from shader loader callsites that test the device result. This is saved static retail/source-reference evidence only; exact Direct3D interface version, exact COM method names, runtime rendering/shader behavior, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave849 D3D State/Cache Core Read-Back

Wave849 D3D state/cache core (`d3d-state-cache-core-wave849`, `wave849-readback-verified`) added saved static evidence for `0x00513650 CEngine__PrintGraphicsCardInfo`, the compact retail graphics-card report matching source `cg_whatami` / `con_whatami` context. The body prints `Graphics card info`, `Description`, `Driver`, `Driver version`, and pure/impure device status strings. Probe token anchor: `Wave849 D3D state/cache core`; `0x00513650 CEngine__PrintGraphicsCardInfo`; `cg_whatami`; `Graphics card info`; `5691/6098 = 93.33%`; `0x00513a80 PlatformInput__GetKeyState3Core`; `G:\GhidraBackups\BEA_20260525-073710_post_wave849_d3d_state_cache_core_verified`.

This is saved static retail/source-reference evidence only; exact adapter structure fields, runtime console command behavior, runtime D3D device behavior, BEA patching, and rebuild parity remain deferred.

## Functions Found

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| `0x004efb10` | `CLTShell__InitializeRuntimeAndLoadCoreResources` | ~0x5c0 bytes | Runtime subsystem initialization and core resource preload |
| `0x004f00e0` | `CLTShell__ShutdownRuntimeAndReleaseResources` | ~0x120 bytes | Runtime subsystem shutdown and global resource release |
| `0x004f0200` | `CLTShell__RunStressTestLevelLoop` | ~0x130 bytes | Stress-test loop over the static level list with memory delta logging |
| `0x004f0330` | `CLTShell__RunFrontEndAndGameLoop` | ~0x420 bytes | Frontend menu loop, direct-level mode, and game-level dispatch |
| `0x00512040` | `CLTShell__UnhandledExceptionFilter` | ~0x20 bytes | WinMain-installed top-level exception filter callback (Wave847) |
| `0x00512130` | `CLTShell__WinMain` | ~0x320 bytes | Main Windows entry point |
| `0x00512670` | `PCLTShell__ctor` | ~0x5d0 bytes | PC shell/CD3DApplication construction and PCLTShell vtable install (Wave561) |
| `0x00512c40` | `PCLTShell__ConfirmDevice` | ~0x60 bytes | PCLTShell vtable slot 1 Direct3D caps acceptance gate (Wave561) |
| `0x00513120` | `PlatformInput__InitDirectInput` | read-back documented | Wave848 DirectInput startup/enumeration row matching `PCLTShell::InitDirectInput(HWND)` |
| `0x00513370` | `PlatformInput__PollPadState` | read-back documented | Wave848 per-pad DirectInput poll/update row matching `PCLTShell::UpdateJoystick(int)` |
| `0x005134a0` | `CEngine__GrabScreenshot` | read-back documented | Wave848 screenshot capture row using `grabs\scr%.4d.tga` |
| `0x00513650` | `CEngine__PrintGraphicsCardInfo` | read-back documented | Wave849 `cg_whatami` / `con_whatami` graphics-card report row |
| `0x00513c70` | `CEngine__DrawIndexedPrimitives` | read-back documented | Wave850 source-wrapper-aligned draw-indexed helper over device slot `0x148` |
| `0x00513e90` | `CEngine__SetVertexShaderHandleCached` | read-back documented | Wave850 cached `D3D_SetVertexShader` style helper |
| `0x00513ec0` | `CEngine__SetVertexShaderHandleRaw` | read-back documented | Wave850 raw `D3D_SetVertexShader` style helper |
| `0x00513f20` | `CEngine__CreatePixelShaderFromText` | read-back documented | Wave850 `D3D_CreatePixelShader` context helper over device slot `0x1a8` |
| `0x00513ff0` | `CEngine__DeviceCall16C_CreateVertexShaderLike` | read-back documented | Wave850 bounded shader-create-like helper over device slot `0x16c` |
| `0x00515fb0` | `CResourceDescriptorTable__InitDefaultMeshNames` | read-back documented | Wave852 startup default render-resource descriptor initializer |
| `0x00516450` | `CResourceDescriptorTable__FreeAllEntries` | read-back documented | Wave852 shutdown descriptor array free/null helper |

### Adjacent Startup Callback Blocks

These labels sit adjacent to `CLTShell__WinMain`; some are loaded Ghidra function rows and some remain code blocks:

| Address | Description |
|---------|-------------|
| `0x00512040` | `CLTShell__UnhandledExceptionFilter` - loaded function row hardened by Wave847; opens `OnslaughtException.txt` and returns `EXCEPTION_EXECUTE_HANDLER` |
| `0x00512070` | Atexit cleanup handler - restores Windows system parameters |
| `0x00512460` | Console command handler for `cg_whatami` |

## Detailed Function Analysis

### CLTShell__WinMain (0x00512130)

**Signature:** `int __stdcall CLTShell__WinMain(void * module_handle, void * previous_instance, char * command_line, int show_command)`

This is the main Windows entry point function. It performs the following operations in sequence:

#### 1. Exception Handler Setup
```c
SetUnhandledExceptionFilter(CLTShell__UnhandledExceptionFilter);
```
Installs a crash handler that writes exception info to "OnslaughtException.txt".

#### 2. Version Information Extraction
```c
GetModuleFileNameA(hInstance, modulePath, 300);
GetFileVersionInfoSizeA(modulePath, &handle);
GetFileVersionInfoA(modulePath, 0, size, buffer);
VerQueryValueA(buffer, "\\", &fixedInfo, &len);
```
Extracts version info from the executable's resources.

#### 3. Windows System Parameter Backup
```c
SystemParametersInfoA(SPI_GETSCREENSAVERRUNNING, ...);  // 0x3A
SystemParametersInfoA(SPI_SETSCREENSAVERRUNNING, ...);  // 0x3B - disable
SystemParametersInfoA(SPI_GETPOWEROFFACTIVE, ...);      // 0x34
SystemParametersInfoA(SPI_SETPOWEROFFACTIVE, ...);      // 0x35 - disable
SystemParametersInfoA(SPI_GETMOUSETRAILS, ...);         // 0x32
SystemParametersInfoA(SPI_SETMOUSETRAILS, ...);         // 0x33 - disable
```
Saves and disables screen saver, power-off, and mouse trails to prevent interference during gameplay. These are restored by the atexit handler at `0x00512070`.

#### 4. Memory Manager Initialization
```c
DAT_0088a0bc = 0x2000000;  // 32MB default heap
CLIParams__ParseCommandLine(lpCmdLine);
MEM_MANAGER__Init(heapSize);  // Initialize memory manager
```
Sets up the game's custom memory manager with 32MB default heap size.

#### 5. Load Previous Options
```c
fileHandle = fopen("defaultoptions.bea", "rb");
if (fileHandle != NULL) {
    saveSize = CCareer__GetSaveSize();
    buffer = malloc(saveSize);
    fread(buffer, 1, saveSize, fileHandle);
    if (readSize == saveSize) {
        CCareer__Load(&g_Career, buffer, 0);
        g_OptionsLoaded = 1;
    }
    fclose(fileHandle);
    free(buffer);
}
```
Attempts to load `defaultoptions.bea` to restore previous game settings.

#### 6. Career Initialization
```c
CCareer__Blank(&g_Career);  // at 0x00660620
```
Blanks/initializes the global career structure and mission graph.

#### 7. Window Creation
```c
result = FUN_005290a0(hInstance);  // Create D3D window
if (result < 0) return 0;

LoadAcceleratorsA(NULL, (LPCSTR)0x71);
PeekMessageA(&msg, NULL, 0, 0, PM_NOREMOVE);
```
Creates the main game window with Direct3D support.

#### 8. Game Initialization and Main Loop
```c
if (msg.message != WM_QUIT) {
    g_GameInitialized = 1;
    result = CLTShell__InitializeRuntimeAndLoadCoreResources(&DAT_00896ca4);
    if (result != 0) {
        CConsole__RegisterCommand("cg_whatami", "Shows the current graphics card detected", handler, 0);
        CLTShell__RunFrontEndAndGameLoop(&DAT_00896ca4);
        CLTShell__ShutdownRuntimeAndReleaseResources();
        CD3DApplication__Cleanup3DEnvironment();  // Final cleanup
    }
}
```

#### 9. Cleanup
```c
hMenu = GetMenu(g_hWnd);
DestroyMenu(hMenu);
DestroyWindow(g_hWnd);
return exitCode;
```

## Wave848 Platform Input Core

Wave848 platform input core (`platform-input-core-wave848`, `wave848-readback-verified`) saved bounded static metadata for the adjacent PCLTShell/platform input and screenshot path. The DirectInput rows are important platform/control connective code even though their final static claims remain bounded by Ghidra/source-reference evidence rather than runtime controller proof. Verified backup: `G:\GhidraBackups\BEA_20260525-070518_post_wave848_platform_input_core_verified`.

| Address | Evidence |
| --- | --- |
| `0x00513120 PlatformInput__InitDirectInput` | Saved `int __thiscall PlatformInput__InitDirectInput(void * this, void * window_handle)`; source-reference `PCLTShell::InitDirectInput(HWND)`; calls `DirectInput8Create`, enumerates controllers through callback `0x00512ff0`, caps joypads to four, and prints `Found %d joypads`. |
| `0x00513370 PlatformInput__PollPadState` | Saved `int __thiscall PlatformInput__PollPadState(void * this, int pad_index, bool rotate_buttons)`; source-reference `PCLTShell::UpdateJoystick(int)`; polls/reacquires the DirectInput device, rotates new-type pad button bytes, and clears inactive buffers. |
| `0x005134a0 CEngine__GrabScreenshot` | Saved `void __thiscall CEngine__GrabScreenshot(void * this, int screenshot_index)`; source-reference ltshell screenshot path; checks D3D surface formats, formats `grabs\scr%.4d.tga`, calls `ImageIO__WriteTGA24`, and releases surfaces. |

Post-Wave848 strict proxy is `5678/6098 = 93.11%`; next raw commentless row is `0x00513640 CEngine__GetConstant32`. Exact DirectInput interface layout, exact pad-state/key-sink layouts, runtime controller behavior, runtime screenshot output/filesystem behavior, runtime virtual-keyboard behavior, BEA patching, and rebuild parity remain deferred.

## Key Globals

| Address | Type | Name | Description |
|---------|------|------|-------------|
| `0x00660620` | `CCareer` | `g_Career` | Global career/options structure |
| `0x00888a44` | `HWND` | `g_hWnd` | Main window handle |
| `0x00889064` | `HMODULE` | `g_hInstance` | Application instance handle |
| `0x0088a0bc` | `DWORD` | `g_HeapSize` | Memory heap size (default 32MB) |
| `0x00888c78` | `BOOL` | `g_GameInitialized` | Game init complete flag |
| `0x008554a4` | `BOOL` | `g_OptionsLoaded` | Previous options loaded flag |
| `0x008554a8` | `DWORD[6]` | `g_SavedMouseTrails` | Saved mouse trails setting |
| `0x008554c0` | `DWORD` | `g_SavedPowerOff` | Saved power-off setting |
| `0x008554c8` | `DWORD` | `g_SavedScreenSaver` | Saved screen saver setting |

## Related Strings

| Address | String |
|---------|--------|
| `0x0063dd8c` | `"C:\dev\ONSLAUGHT2\ltshell.cpp"` |
| `0x0063dd70` | `"Loading previous options"` |
| `0x0063ddac` | `"Init game with %d bytes"` |
| `0x0063dd24` | `"Memory heap at %dMb"` |
| `0x0063dd3c` | `"cg_whatami"` |
| `0x0063dd48` | `"Shows the current graphics card detected"` |
| `0x0063dc70` | `"OnslaughtException.txt"` |

## Console Commands Registered

| Command | Description | Handler Address |
|---------|-------------|-----------------|
| `cg_whatami` | Shows the current graphics card detected | `0x00512460` (thunk to `0x0051366e`) |

## Initialization Order

1. Exception handler installed
2. Version info extracted
3. System parameters saved and disabled (screen saver, power-off, mouse trails)
4. Atexit handler registered for cleanup
5. Command line parsed (`CLIParams__ParseCommandLine`)
6. Memory manager initialized
7. Previous options loaded from `defaultoptions.bea`
8. Career structure initialized
9. Direct3D window created
10. All game subsystems initialized
11. Console commands registered
12. Front end runs (main menu)
13. Game loop
14. Shutdown and cleanup

## Cross-References

### Functions Called
- `CLIParams__ParseCommandLine` (0x00423bc0)
- `CCareer__GetSaveSize` (0x00421430)
- `CCareer__Load` (0x00421200)
- `CCareer__Blank` (0x0041b7c0)
- `CConsole__RegisterCommand` (0x0042af80)
- `CMemoryManager::Init` (0x004a13b0) via `MEM_MANAGER__Init` (`0x00548f90`)

### Key Subsystem Initialization
- Memory Manager: `MEM_MANAGER__Init` (`0x00548f90`)
- D3D Window: `FUN_005290a0`
- Full Game Init: `CLTShell__InitializeRuntimeAndLoadCoreResources` (`0x004efb10`)
- Front End Loop: `CLTShell__RunFrontEndAndGameLoop` (`0x004f0330`)
- Shutdown: `CLTShell__ShutdownRuntimeAndReleaseResources` (`0x004f00e0`)
- Final Cleanup: `CD3DApplication__Cleanup3DEnvironment` (`0x0052c430`)

## Wave847 LTShell Exception Filter (2026-05-25)

Probe token anchor: Wave847 LTShell exception filter; ltshell-exception-filter-wave847; 0x00512040 CLTShell__UnhandledExceptionFilter; int __stdcall CLTShell__UnhandledExceptionFilter(void * exception_pointers); SetUnhandledExceptionFilter; 0x0051213c; OnslaughtException.txt; 0x0063dc88; RET 0x4; 5674/6098 = 93.05%; 0x00513120 PlatformInput__InitDirectInput; G:\GhidraBackups\BEA_20260525-063403_post_wave847_ltshell_exception_filter_verified

Wave847 corrected the loaded row at `0x00512040` from stale `CLTShell__InitUnhandledExceptionLogFile` metadata to:

```cpp
int __stdcall CLTShell__UnhandledExceptionFilter(void * exception_pointers);
```

Static retail evidence: `CLTShell__WinMain` pushes `0x00512040` at `0x0051213c` before calling imported `SetUnhandledExceptionFilter`; the callback calls `SetUnhandledExceptionFilter(NULL)`, opens `OnslaughtException.txt` with mode string `0x0063dc88`, returns `1`/`EXCEPTION_EXECUTE_HANDLER`, and exits with `RET 0x4`. Source-reference evidence in `references/Onslaught/ltshell.cpp:172` has the fuller PC `ExceptionHandler(EXCEPTION_POINTERS *info)` shape, but the saved retail claim remains limited to observed Ghidra decompile/xref/instruction evidence.

Queue after Wave847: `6098` total functions, `5674` commented, `424` commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `5674/6098 = 93.05%`. Next raw commentless row: `0x00513120 PlatformInput__InitDirectInput`. Verified backup: `G:\GhidraBackups\BEA_20260525-063403_post_wave847_ltshell_exception_filter_verified`.

Full debug-symbol dump behavior, runtime crash handling, exact source-body parity, BEA patching, and rebuild parity remain deferred.

## Wave561 Static Read-Back (2026-05-18)

Wave561 hardened the platform/shell entry and adjacent PCLTShell vtable evidence:

```cpp
int __stdcall CLTShell__WinMain(void * module_handle, void * previous_instance, char * command_line, int show_command);
void * __thiscall PCLTShell__ctor(void * this);
int __stdcall PCLTShell__ConfirmDevice(void * d3d_caps, uint behavior_flags);
```

The `CLTShell__WinMain` correction restores the fourth WinMain-style stack argument proven by the `RET 0x10` epilogue. `PCLTShell__ctor` is called by the global initialization thunk with `ECX=0x00855bb0`, installs PCLTShell vtable `0x005e488c`, clears shell/input fields, copies the Battle Engine Aquila title, and returns `this`. `PCLTShell__ConfirmDevice` is PCLTShell vtable slot 1 and rejects unsupported Direct3D caps combinations with `E_FAIL`.

Evidence lives in `release/readiness/ghidra_platform_shell_wave561_2026-05-18.md`. Runtime launch behavior, exact CLTShell/PCLTShell layout, exact source-body identity, and rebuild parity remain unproven.

## Wave592 CDXEngine Shutdown Resource Helper (2026-05-19)

Wave592 corrected the stale `CLTShell__ReleaseHudRefAndTargetHandle` label to:

```cpp
void __fastcall CDXEngine__ReleaseDefaultTextureAndMeshRefs(void * this);
```

`CLTShell__ShutdownRuntimeAndReleaseResources` still owns the caller context: after console/font cleanup and `CVBufTexture__DestroyGlobalHudHandle89BD98`, it loads `ECX=0x89c9a0` and calls this CDXEngine helper. The callee releases the default texture handle at `this+0x4e4` through `CTexture__DecrementRefCountFromNameField(texture+8)`, decrements the default mesh usage counter at `this+0x28 + 0x170`, and clears both slots.

Evidence lives in `release/readiness/ghidra_dxengine_resource_tail_wave592_2026-05-19.md`. Runtime shutdown behavior, exact CLTShell/CDXEngine layouts, exact source-body identity, and rebuild parity remain unproven. Wave593 later hardened `0x0053d760 CThing__RenderDebugVolumeOverlay`; the current next queue head is `0x0053f040 CVBufTexture__SetStateCacheModeByFlag`.

The same Wave592 CDXEngine resource-tail pass saved `CDXEngine__Shutdown`, `CDXEngine__UploadScaledRgbLookupTable`, `CDXEngine__Init`, and `CDXEngine__InitResources`; those rows are documented in [`engine.cpp`](../engine.cpp/_index.md).

## Wave514 Static Read-Back (2026-05-17)

Wave514 hardened the adjacent CLTShell runtime loop signatures and comments:

```cpp
int __fastcall CLTShell__InitializeRuntimeAndLoadCoreResources(void * level_request_slot);
void __cdecl CLTShell__ShutdownRuntimeAndReleaseResources(void);
void __stdcall CLTShell__RunStressTestLevelLoop(int stress_test_count);
int __fastcall CLTShell__RunFrontEndAndGameLoop(void * level_request_slot);
```

The claim is intentionally narrow. `CLTShell__WinMain` calls init, frontend/game loop, and shutdown around the D3D application lifetime. The init body initializes pointer sets, console/controller/platform/FMV/audio/music subsystems, startup/splash/FMV gates, text/frontend/resource/font/default mesh/default texture/loading-screen resources, and default physics/BattleEngine data before storing `-1` through `level_request_slot`. The loop body routes stress-test mode through `CLTShell__RunStressTestLevelLoop`, otherwise alternates frontend selection and `CGame__RunLevel`, with direct command-line level mode using the same slot. The shutdown body releases the corresponding global resources.

Evidence lives in `release/readiness/ghidra_ltshell_runtime_wave514_2026-05-17.md`. Runtime launch behavior, concrete global shell-state layout, exact source-body identity, and rebuild parity remain unproven.

## Notes

1. **Platform-Specific:** This is the PC-specific entry point. The Xbox/PS2 versions would have different shell implementations.

2. **defaultoptions.bea:** This file stores the last-used game options. The name suggests it uses the BEA archive format but contains a raw `CCareer` save structure.

3. **System Parameter Restoration:** The game carefully saves and restores Windows system settings to ensure a clean state after exit, even on crash (via the atexit handler).

4. **32MB Default Heap:** The default memory allocation is 32MB (`0x2000000`), which can be modified via command-line parameters processed by `CLIParams__ParseCommandLine`.
