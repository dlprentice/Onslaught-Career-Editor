# ltshell.cpp - Lost Toys Shell (Application Entry Point)

**Source File:** `C:\dev\ONSLAUGHT2\ltshell.cpp`
**Debug String Address:** `0x0063dd8c`

## Overview

`ltshell.cpp` contains the main Windows application entry point (WinMain) for Battle Engine Aquila. "LTShell" stands for "Lost Toys Shell" - the main application shell that initializes all subsystems, loads saved options, creates the game window, and runs the main game loop.

The RTTI class name `PCLTShell` (found at `0x0063dc60`) indicates this was implemented as a class on the PC platform.

## Functions Found

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| `0x00512130` | `CLTShell__WinMain` | ~0x320 bytes | Main Windows entry point |

### Internal Code Blocks (within WinMain)

These are not separate functions but labeled code blocks within `CLTShell__WinMain`:

| Address | Description |
|---------|-------------|
| `0x00512040` | Unhandled exception filter - writes crash info to `OnslaughtException.txt` |
| `0x00512070` | Atexit cleanup handler - restores Windows system parameters |
| `0x00512460` | Console command handler for `cg_whatami` |

## Detailed Function Analysis

### CLTShell__WinMain (0x00512130)

**Signature:** `int __stdcall WinMain(HMODULE hInstance, HMODULE hPrevInstance, LPSTR lpCmdLine)`

This is the main Windows entry point function. It performs the following operations in sequence:

#### 1. Exception Handler Setup
```c
SetUnhandledExceptionFilter(ExceptionFilter_00512040);
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
    result = FUN_004efb10();  // Initialize all game subsystems
    if (result != 0) {
        CConsole__RegisterCommand("cg_whatami", "Shows the current graphics card detected", handler, 0);
        FUN_004f0330();  // Run front end
        FUN_004f00e0();  // Shutdown
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
- Full Game Init: `FUN_004efb10`
- Front End Loop: `FUN_004f0330`
- Shutdown: `FUN_004f00e0`
- Final Cleanup: `CD3DApplication__Cleanup3DEnvironment` (`0x0052c430`)

## Notes

1. **Platform-Specific:** This is the PC-specific entry point. The Xbox/PS2 versions would have different shell implementations.

2. **defaultoptions.bea:** This file stores the last-used game options. The name suggests it uses the BEA archive format but contains a raw `CCareer` save structure.

3. **System Parameter Restoration:** The game carefully saves and restores Windows system settings to ensure a clean state after exit, even on crash (via the atexit handler).

4. **32MB Default Heap:** The default memory allocation is 32MB (`0x2000000`), which can be modified via command-line parameters processed by `CLIParams__ParseCommandLine`.
