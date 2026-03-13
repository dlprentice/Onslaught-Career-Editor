# Platform.cpp Functions

Platform abstraction layer for cross-platform functionality. In the PC port, most platform-specific code is in `PCPlatform.cpp`, while `Platform.cpp` contains generic platform abstraction code.

**Debug Path String:** `C:\dev\ONSLAUGHT2\Platform.cpp` at `0x00631654`

## Functions Found

| Address | Name | Purpose |
|---------|------|---------|
| `0x004d2580` | `Platform__AsyncSaveCareer` | Asynchronous career save handler |
| `0x004d2600` | `Platform__CreateDirectoryPath` | Creates directory path recursively |
| `0x00515880` | [`PLATFORM__Process`](./PLATFORM__Process.md) | Platform event pump / quit-code polling wrapper (`CPCPlatform::Process`) |
| `0x005158c0` | [`PLATFORM__BeginScene`](./PLATFORM__BeginScene.md) | BeginScene wrapper (`CPCPlatform::BeginScene`) |
| `0x005158e0` | [`PLATFORM__EndScene`](./PLATFORM__EndScene.md) | EndScene wrapper (`CPCPlatform::EndScene`) |
| `0x00515910` | [`PLATFORM__ClearScreen`](./PLATFORM__ClearScreen.md) | Clear-screen wrapper (`CPCPlatform::ClearScreen`) |
| `0x005159e0` | [`PLATFORM__GetSysTimeFloat`](./PLATFORM__GetSysTimeFloat.md) | High-resolution time helper in seconds (`CPCPlatform::GetSysTimeFloat`) |

## Related: PCPlatform.cpp Functions

The PC-specific platform implementation is in `PCPlatform.cpp` (debug string at `0x0063e03c`):

| Address | Name | Purpose |
|---------|------|---------|
| `0x005149c0` | `EnumerateSaveFiles_1` | Counts save files in savegames folder |
| `0x00514a80` | `EnumerateSaveFiles_2` | Gets save file name by index |
| `0x00514be0` | `EnumerateSaveFiles_Main` | Main save file enumeration |
| `0x00514ec0` | `PCPlatform__DeleteSaveFile` | Deletes a save file |
| `0x00514f80` | `PCPlatform__WriteSaveFile` | Writes data to save file |
| `0x00515080` | `PCPlatform__ReadSaveFile` | Reads data from save file |
| `0x005154e0` | `PCPlatform__Init` | Platform initialization (D3D, shaders) |
| `0x005155e0` | `PCPlatform__LoadFonts` | Loads font resources |
| `0x005157b0` | `CPCPlatform__UnloadFonts` | Unloads/frees font resources (shutdown) |
| `0x00515880` | `PLATFORM__Process` | Global wrapper used by `CGame__MainLoop`/`CFrontEnd__Process` |
| `0x005158c0` | `PLATFORM__BeginScene` | Global wrapper used by game/frontend render loops |
| `0x005158e0` | `PLATFORM__EndScene` | Global wrapper used by game/frontend render loops |
| `0x00515910` | `PLATFORM__ClearScreen` | Global wrapper for clear-color/depth pre-pass |
| `0x005159e0` | `PLATFORM__GetSysTimeFloat` | Global wrapper around platform timer |

## Function Details

### Platform__AsyncSaveCareer (0x004d2580)

Per-frame async-save tick (called from the main loop and other render/update paths). Despite the name,
this function is primarily used as a deferred writer for `defaultoptions.bea` in the Steam build.

```c
void Platform__AsyncSaveCareer(int tick)
{
    // If DAT_0082b5b0 != 0:
    //   bWriteDefaultOptions = (DAT_0082b5b0 == 2);
    //   DAT_0082b5b0 = 0;
    //   CD3DApplication__Reset3DEnvironment(1,1);
    //   if bWriteDefaultOptions:
    //     size = CCareer__GetSaveSize();
    //     buf = OID__AllocObject(size, ...);
    //     CCareer__Save(&CAREER, buf);
    //     CFEPOptions__WriteDefaultOptionsFile(buf, size);
    //     OID__FreeObject(buf);
}
```

**Called by:**
- `0x0042c810` (`CConsole__RenderLoadingScreen`) - Loading-screen render/update path
- `0x00468700` (FUN_00468700)
- `0x0046eee0` (`CGame__MainLoop`)
- `0x004726b0` (`CGame__RollCredits`)
- `0x0053f2a5`, `0x0053f4d2`, `0x0053f50f` - FMV-related code

### Platform__CreateDirectoryPath (0x004d2600)

Creates a directory path by recursively creating each component. Uses `strrchr` and `strchr` to parse path separators.

```c
void Platform__CreateDirectoryPath(char *path, int stripFilename)
{
    // If stripFilename is non-zero, strips the filename from the path
    // Iterates through path components, creating each directory
    // Uses mkdir (FUN_0055f347) for each component
}
```

**Called by:**
- `CLIParams__ParseCommandLine` at `0x00423bc0`

### PCPlatform__Init (0x005154e0)

Initializes the PC platform layer. Sets up D3D device, performance counters, and shaders.

```c
int PCPlatform__Init(void)
{
    // Logs "Platform init"
    // Allocates platform structure (0x38 bytes)
    // Initializes D3D device
    // Calls QueryPerformanceFrequency for timing
    // Enables vertex shader support if available
    // Logs "Initting shaders"
}
```

**Key strings:**
- `"Platform init"` at `0x0063e060`
- `"Vertex shader suppport ENABLED"` at `0x0063e01c`
- `"Initting shaders"` at `0x0063e008`

### PCPlatform__LoadFonts (0x005155e0)

Loads font resources for the game UI. Handles 4 different fonts.

```c
void PCPlatform__LoadFonts(void)
{
    // Loads font22_512.tga (main UI font, size 0x20)
    // Loads Terminal font (debug font, 7pt)
    // Loads Font13PS.tga (small font, size 0x10)
    // Loads TitleFont.tga (title font, size 0x20)
}
```

**Key strings:**
- `"Warning - loading font manually"` at `0x0063e188`
- `"Warning - loading debug font manually"` at `0x0063e150`
- `"Warning - loading small font manually"` at `0x0063e11c`
- `"Warning - loading title font manually"` at `0x0063e0e4`
- `"font22_512.tga"` at `0x0063e178`
- `"Font13PS.tga"` at `0x0063e10c`
- `"TitleFont.tga"` at `0x0063e0d4`

### CPCPlatform__UnloadFonts (0x005157b0)

Frees all font resources during shutdown. Called from game shutdown routine.

```c
void CPCPlatform__UnloadFonts(CPCPlatform *this)
{
    // Free fonts at offsets 0x18, 0x1c, 0x20, 0x24, 0x28, 0x2c
    // Each font: Cleanup() then free()
    // Finally free platformData at offset 0x00
}
```

**Called by:**
- `FUN_004f00e0` (Game shutdown, alongside CMusic__Shutdown)

### PLATFORM__Process (0x00515880)

Source-aligned wrapper for `PLATFORM.Process()` / `CPCPlatform::Process()`.

```c
int PLATFORM__Process(void)
{
    // Repeatedly pumps system work (PLATFORM__ProcessSystemMessages)
    // Returns non-zero quit code when host/window requests exit
}
```

**Called by:**
- `CGame__MainLoop` (`0x0046eee0`)
- `CFrontEnd__Process` (`0x00466ba0`)

### PLATFORM__GetSysTimeFloat (0x005159e0)

Source-aligned wrapper for `PLATFORM.GetSysTimeFloat()` / `CPCPlatform::GetSysTimeFloat()`.

```c
float PLATFORM__GetSysTimeFloat(void)
{
    // QueryPerformanceCounter path when frequency is initialized
    // Falls back to timeGetTime()/1000.0f
}
```

**Used by:**
- `CGame__MainLoop` / `CGame__Update` timing paths
- Controller inactivity timeout checks
- Frontend/game timing and animation paths

### PLATFORM__BeginScene (0x005158c0)

Source-aligned wrapper for `PLATFORM.BeginScene()` / `CPCPlatform::BeginScene()`.

```c
bool PLATFORM__BeginScene(void)
{
    // Dispatch through platform vtable slot +0xA4
    // Returns true when scene begin succeeds (>= 0 status)
}
```

**Called by:**
- `CConsole__RenderLoadingScreen` (`0x0042c810`)
- `CGame__RollCredits` (`0x004726b0`)
- `CDXEngine__Render` (`0x0053e2e0`)
- `CDXEngine__PostRender` (`0x0053ecc0`)

### PLATFORM__ClearScreen (0x00515910)

Source-aligned wrapper for `PLATFORM.ClearScreen(col)` / `CPCPlatform::ClearScreen(DWORD col)`.

```c
void PLATFORM__ClearScreen(int color)
{
    // Dispatch through platform vtable slot +0xAC
    // Clear flags/value are passed through the wrapper's fixed parameter pattern
}
```

**Called by:**
- `CConsole__RenderLoadingScreen` (`0x0042c810`)
- `CGame__RollCredits` (`0x004726b0`)
- `FUN_00540f70` (`0x00540f70`)
- FMV/render helper cluster near `0x0053f2xx` / `0x0053f5xx`

### PLATFORM__EndScene (0x005158e0)

Source-aligned wrapper for `PLATFORM.EndScene()` / `CPCPlatform::EndScene()`.

```c
void PLATFORM__EndScene(void)
{
    // Dispatch through platform vtable slot +0xA8
}
```

**Called by:**
- `CConsole__RenderLoadingScreen` (`0x0042c810`)
- `CGame__RollCredits` (`0x004726b0`)
- `CDXEngine__Render` (`0x0053e2e0`)
- `CDXEngine__PostRender` (`0x0053ecc0`)

### Save File Operations

The save file functions all operate on the `savegames\` directory:

- **Path pattern:** `savegames\*.bes` (string at `0x0063df7c`)
- **Base path:** `savegames\` (string at `0x0063df94`)
- **File extension:** `.bes` (string at `0x0063df8c`)

#### PCPlatform__DeleteSaveFile (0x00514ec0)

Deletes a save file using Win32 `DeleteFileA`.

#### PCPlatform__WriteSaveFile (0x00514f80)

Writes career data to a save file. Constructs path from `savegames\` + name + `.bes`.

#### PCPlatform__ReadSaveFile (0x00515080)

Reads career data from a save file. Returns bytes read via output parameter.

## Global Data

| Address | Name | Purpose |
|---------|------|---------|
| `0x0082b5b0` | `DAT_0082b5b0` | Async save request flag (0=none, 2=save pending) |
| `0x008898d8` | `DAT_008898d8` | FindFirstFile handle for save enumeration |
| `0x008898e0` | `DAT_008898e0` | WIN32_FIND_DATA attributes |
| `0x008898f4` | `DAT_008898f4` | WIN32_FIND_DATA filename |

## Cross-References

### Platform__AsyncSaveCareer calls:
- `FUN_005158f0` - Unknown (param_1 related)
- `CD3DApplication__Reset3DEnvironment` - D3D reset/recovery path (invoked with `1,1` here)
- `CCareer__GetSaveSize` - Gets career save size
- `OID__AllocObject` - Memory allocation (malloc wrapper)
- `CCareer__Save` - Saves career to buffer
- `FUN_0051f680` - Unknown (buffer, size params)
- `OID__FreeObject` - Memory deallocation (free wrapper)

### PCPlatform__Init calls:
- `FUN_00423650` - D3D device creation
- `FUN_00423680` - D3D setup (1.0f param)
- `QueryPerformanceFrequency` - Win32 API for high-res timer
- `InitShaderCapabilityFlagsAndCVar` (`0x005016b0`) - Shader capability probe + `cg_forcevertexshaders` cvar registration

## Notes

1. The Platform/PCPlatform split follows the console port architecture where platform-specific code is isolated
2. Save file operations use Win32 APIs directly (DeleteFileA, FindFirstFile, etc.)
3. The async save mechanism uses a global flag checked in the main game loop
4. Font loading has fallback "manual" loading paths with warning messages
