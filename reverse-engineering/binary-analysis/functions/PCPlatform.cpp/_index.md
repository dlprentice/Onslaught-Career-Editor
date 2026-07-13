# PCPlatform.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x00512630` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1219 final current-risk closure note: `CFrameTimer__ctor` remains mapped to PCPlatform timer/performance-counter setup; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`. Runtime timing behavior, exact layout, and rebuild parity remain separate proof.
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

PC-specific platform abstraction layer implementation. Handles save file I/O, font loading, D3D initialization, and platform-specific features for the Windows port.

**Debug Path String:** `[maintainer-local-source-export-root]\PCPlatform.cpp` at `0x0063e03c`

Wave909 engine/platform support static review (`engine-platform-support-static-review-wave909`) records the PC platform wrapper side of a static-coherent engine/platform/math/memory support core. PCPlatform anchors include `PCPlatform__InitAsyncMusicStream` and `PCPlatform__WriteSaveFile`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified`. Runtime platform I/O and exact layouts remain separate proof.

## 2026-05-25 Wave861 Render/HUD/Platform Tail Read-Back

Wave861 render/HUD/platform tail static read-back (`render-hud-platform-tail-wave861`, `wave861-readback-verified`) hardened the async music-streaming tail and adjacent render-validation connector rows as important connective infrastructure. Probe token anchor: `Wave861 render/HUD/platform tail`; `render-hud-platform-tail-wave861`; `0x00523a70 CDXEngine__RenderMouseCursorSprite`; `0x00523b30 CVBufTexture__DestroyGlobalHudHandle89BD98`; `0x00527990 CGame__DrawLocalCoopControllerPrompt`; `0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag`; `0x00527f50 PCPlatform__AsyncMusicStreamWorkerMain`; `0x005282b0 PCPlatform__InitAsyncMusicStream`; `0x00528540 PCPlatform__KickAsyncMusicStreamRead`; `0x005285e0 PCPlatform__UpdateAsyncMusicStreamVolume`; important connective infrastructure; `0x0052a830 CD3DApplication__FindDepthStencilFormat`; `5802/6105 = 95.04%`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-141443_post_wave861_render_hud_platform_tail_verified`.

The pass corrected `0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag` to `void __fastcall CWaterRenderSystem__ResetAndMarkSourceFlag(void * validation_record)`, corrected `0x00528540 PCPlatform__KickAsyncMusicStreamRead` to `void __cdecl PCPlatform__KickAsyncMusicStreamRead(char * track_path)`, and corrected `0x005285e0 PCPlatform__UpdateAsyncMusicStreamVolume` to `void __cdecl PCPlatform__UpdateAsyncMusicStreamVolume(float normalized_volume)`. Static evidence ties `0x00527f50 PCPlatform__AsyncMusicStreamWorkerMain` through `0x005285e0` to `CreateThread`, four event handles, 44100 Hz stereo Ogg validation, DirectSound buffer fill/zero-fill, `data\music` playlist setup, track path buffer `DAT_0089bed4`, worker wake signalling, and DirectSound volume vtable slot `0x3c` after the observed clamp/attenuation conversion. Runtime water/D3D validation behavior, runtime async music/audio playback behavior, exact object layouts, BEA patching, and rebuild parity remain deferred.

Wave1028 static re-audit (`cdx-render-resource-lifecycle-review-wave1028`) re-read `0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag` in the DX render-resource lifecycle slice with no mutation. Fresh xrefs still come from `CWaterRenderSystem__RenderMainPass`, and the body still clears `DAT_00854dd8` while setting `DAT_00854dd9` from `validation_record+0x10`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-021726_post_wave1028_cdx_render_resource_lifecycle_review_verified`. Runtime water/D3D validation behavior remains separate proof.

## 2026-05-25 Wave852 PC Platform/Resource Tail Read-Back

Wave852 PC platform/resource tail (`pc-platform-resource-tail-wave852`, `wave852-readback-verified`) saved comments/tags for the important PC platform connector rows `0x00515ab0 D3DDevice__SetViewport`, `0x00515b10 PCPlatform__DeserializeFontsAndAssets`, and `0x00515db0 Registry__SetStringValue_HKCU`. Probe token anchor: `Wave852 PC platform/resource tail`; `0x00515ab0 D3DDevice__SetViewport`; `0x00515b10 PCPlatform__DeserializeFontsAndAssets`; `0x00515db0 Registry__SetStringValue_HKCU`; `Warning : deserializing font twice!`; `5736/6098 = 94.06%`; `0x005168d0 CPCSoundManager__dtor`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-093157_post_wave852_pc_platform_resource_tail_verified`.

Static evidence ties `D3DDevice__SetViewport` to CDXEngine/CEngine/Hud viewport callers, source `CPCPlatform::SetViewport`, `LT.D3D_SetViewport`, and global device `DAT_00888a50` vtable slot `0xbc`. `PCPlatform__DeserializeFontsAndAssets` is called by `CResourceAccumulator__ReadResourceFile`, frees/rebuilds font slots around `this+0x18` through `this+0x2c`, emits `Warning : deserializing font twice!`, allocates four `0x1180` CDXBitmapFont-like objects, and calls `CDXBitmapFont__Deserialize`. `Registry__SetStringValue_HKCU` writes `REG_SZ` values under `Software\Lost Toys\Battle Engine Aquila` through `RegSetValueExA`. Runtime D3D viewport behavior, runtime font/resource loading, runtime registry side effects, exact layout/schema details, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave851 PC Platform/Controller Tail Read-Back

Wave851 PC platform/controller tail (`pc-platform-controller-tail-wave851`, `wave851-readback-verified`) saved comments/tags for the PC storage/save compatibility and music/platform connector rows: `0x00514960 PCPlatform__GetStorageDeviceInfo`, `0x00514be0 EnumerateSaveFiles_Main`, `0x00515190 PCPlatform__CopyStorageDeviceId`, and `0x00515320 PCPlatform__InitMusicPlaylist`. Probe token anchor: `Wave851 PC platform/controller tail`; `0x00514960 PCPlatform__GetStorageDeviceInfo`; `0x00514be0 EnumerateSaveFiles_Main`; `0x00515320 PCPlatform__InitMusicPlaylist`; `savegames\*.bes`; `5729/6098 = 93.95%`; `0x00515ab0 D3DDevice__SetViewport`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-085618_post_wave851_pc_platform_controller_tail_verified`.

Static evidence ties the storage helpers to one-device PC compatibility reporting, inserted/formatted outputs, max free/total counts, localized display-name copy, `savegames\*.bes` enumeration, `savegames\` + `.bes` path building, attributes mask `0x16`, and overwrite return `6`. `PCPlatform__InitMusicPlaylist` initializes async music streaming and calls `CMusic__LoadPlaylistFromDir(this,"data\music")`. Runtime save/frontend filesystem behavior, runtime audio playback, exact save API error-code contract, exact music vtable owner/layout, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave850 D3D Shader/Input Tail Read-Back

Wave850 D3D shader/input tail (`d3d-shader-input-tail-wave850`, `wave850-readback-verified`) added saved static evidence for the retail key-query cores used by the PC controller layer. `0x00513a80 PlatformInput__GetKeyState3Core` is saved as `bool __thiscall PlatformInput__GetKeyState3Core(void * this, int key)` and matches the source-reference `PCPlatform KeyOn` / `LT.xKeyOn` direction by returning `this+0x332e4+key`. `0x00513a90 PlatformInput__GetKeyOnceCore` is saved as `bool __thiscall PlatformInput__GetKeyOnceCore(void * this, int key)` and matches the `PCPlatform KeyOnce` / `LT.xKeyOnce` direction by reading/clearing `this+0x331e4+key` and recording consumed keys through queue global `0x00855424`. Probe token anchor: `Wave850 D3D shader/input tail`; `PlatformInput__GetKeyState3Core`; `PlatformInput__GetKeyOnceCore`; `PCPlatform KeyOn/KeyOnce`; `5704/6098 = 93.54%`; `0x005140e0 CDXEngine__CaptureAviFrame`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-081702_post_wave850_d3d_shader_input_tail_verified`.

This is saved static retail/source-reference evidence only; exact key-table and consumed-key queue layouts, runtime input behavior, BEA patching, and rebuild parity remain deferred.

## Functions Found

| Address | Name | Purpose |
|---------|------|---------|
| `0x00513a80` | `PlatformInput__GetKeyState3Core` | Wave850 held key-state core reached by controller key-on paths |
| `0x00513a90` | `PlatformInput__GetKeyOnceCore` | Wave850 one-shot key core with consumed-key queue evidence |
| `0x005149c0` | `EnumerateSaveFiles_1` | Counts save files in savegames folder |
| `0x00514a80` | `EnumerateSaveFiles_2` | Gets save file name by index |
| `0x00514be0` | `EnumerateSaveFiles_Main` | Main save file enumeration with validation |
| `0x00514ec0` | `PCPlatform__DeleteSaveFile` | Deletes a save file |
| `0x00514f80` | `PCPlatform__WriteSaveFile` | Writes data to save file |
| `0x00515080` | `PCPlatform__ReadSaveFile` | Reads data from save file |
| `0x00515190` | `PCPlatform__CopyStorageDeviceId` | Wave851 copied storage-device id compatibility helper |
| `0x00515320` | `PCPlatform__InitMusicPlaylist` | Wave851 async music stream and `data\music` playlist initializer |
| `0x00515ab0` | `D3DDevice__SetViewport` | Wave852 D3D viewport handoff through global device vtable slot `0xbc` |
| `0x00515b10` | `PCPlatform__DeserializeFontsAndAssets` | Wave852 font/resource chunk deserialize connector |
| `0x00515db0` | `Registry__SetStringValue_HKCU` | Wave852 HKCU `REG_SZ` persistence helper for console/platform paths |
| `0x005154e0` | `PCPlatform__Init` | Platform initialization (D3D, shaders) |
| `0x005155e0` | `PCPlatform__LoadFonts` | Loads font resources |
| `0x005157b0` | `CPCPlatform__UnloadFonts` | Unloads/frees font resources |
| `0x005158f0` | `PCPlatform__DeviceFlip` | Source-aligned device/frame flip wrapper with frame-timer update |
| `0x00515950` | `PCPlatform__GetFPS` | Source-aligned FPS accessor with 1.0 fallback |

**Total: 12 functions**

## Function Details

### EnumerateSaveFiles_1 (0x005149c0)

Counts the number of save files in the `savegames\` directory.

```c
int EnumerateSaveFiles_1(int device, int *out_count)
{
    // NOTE: `device` is unused in the PC build (kept for parity with console APIs).
    *out_count = 0;
    handle = FindFirstFile("savegames\\*.bes", &findData);
    if (handle != INVALID_HANDLE_VALUE) {
        // Skip directories (FILE_ATTRIBUTE_DIRECTORY | HIDDEN | SYSTEM = 0x16)
        // Count the first entry if it is visible, then walk `FindNextFile`.
        FindClose(handle);
    }
    return 0;
}
```

**Called by:** Frontend save game UI

### EnumerateSaveFiles_2 (0x00514a80)

Gets save file name by index. Iterates through save files and writes the `index`th filename (without extension).

```c
int EnumerateSaveFiles_2(int device, int index, short *out_name)
{
    // NOTE: `device` is unused in the PC build.
    // - Enumerates: "savegames\\*.bes"
    // - Skips FILE_ATTRIBUTE_{HIDDEN,SYSTEM,DIRECTORY} (mask 0x16)
    // - Strips ".bes" (filename[length-5] = '\0')
    // - Converts to WCHAR and writes to `out_name`
    // Returns 0 on success, 1 on failure.
}
```

### EnumerateSaveFiles_Main (0x00514be0)

Main save enumeration function with file validation. Checks if a save file already exists, creates the savegames directory if needed.

**Return values:**
- `0` = Success
- `1` = Error
- `6` = File already exists (when param_4 == 0)

### PCPlatform__DeleteSaveFile (0x00514ec0)

Deletes a career save file using Win32 `DeleteFileA`.

Note: `device`/`slot` parameters are unused in the PC implementation (kept for cross-platform API parity).

```c
bool PCPlatform__DeleteSaveFile(int device, int slot, short *save_name)
{
    char path[260];
    strcpy(path, "savegames\\");
    strcat(path, FromWCHAR(save_name));
    strcat(path, ".bes");
    return DeleteFileA(path) == 0;  // Returns true on failure
}
```

### PCPlatform__WriteSaveFile (0x00514f80)

Writes career data to a save file. Constructs path from `savegames\` + name + `.bes`.

Note: `device`/`slot` parameters are unused in the PC implementation (kept for cross-platform API parity).

```c
int PCPlatform__WriteSaveFile(int device, int slot, short *save_name, void *data, int size)
{
    char path[260];
    // Build path: "savegames\" + saveName + ".bes"
    FILE *file = fopen(path, "wb");  // fopen @ 0x0055e490 (was FUN_0055e490)
    if (file != NULL) {
        int written = fwrite(data, size, 1, file);  // fwrite @ 0x0055f16e (was FUN_0055f16e)
        if (written == 1) {
            fclose(file);
            return 0;  // Success
        }
    }
    return 1;  // Failure
}
```

### PCPlatform__ReadSaveFile (0x00515080)

Reads career data from a save file. Returns bytes read via output parameter.

Note: `device`/`slot` parameters are unused in the PC implementation (kept for cross-platform API parity).

```c
int PCPlatform__ReadSaveFile(int device, int slot, short *save_name, void *buffer, int maxSize, int *bytesRead)
{
    char path[260];
    // Build path: "savegames\" + saveName + ".bes"
    FILE *file = fopen(path, "rb");  // fopen @ 0x0055e490 (was FUN_0055e490)
    if (file != NULL) {
        int read = fread(buffer, 1, maxSize, file);  // fread @ 0x0055f4d7 (was FUN_0055f4d7)
        fclose(file);
        if (read == maxSize) {
            *bytesRead = read;
            return 0;  // Success
        }
        *bytesRead = read;
    }
    return 1;  // Failure
}
```

### PCPlatform__Init (0x005154e0)

Wave562 saved the current Ghidra signature:

```c
bool __thiscall PCPlatform__Init(void * this)
```

Initializes the PC platform layer. Sets up D3D device, performance counters, and vertex shaders.

```c
int PCPlatform__Init(CPCPlatform *this)
{
    Log("Platform init");

    // Allocate and initialize the frame timer (0x38 bytes)
    void *timer = malloc(0x38, 0x80);
    if (timer == NULL)
        return 0;

    this->mFrameTimer = CFrameTimer__ctor(timer);  // 0x00423650
    if (this->mFrameTimer == NULL)
        return 0;

    CFrameTimer__Start(this->mFrameTimer, 1.0f);  // 0x00423680
    QueryPerformanceFrequency(&this->perfFreq);
    this->field_10 = 1.0f;  // 0x3f800000

    // Enable vertex shaders if supported
    if (DAT_00662f00 == 0 || DAT_00662dec != 0) {
        Log("Vertex shader suppport ENABLED");
        DAT_0063c108 = 1;
    }

    Log("Initting shaders");
    InitShaders();  // InitShaderCapabilityFlagsAndCVar (0x005016b0)

    return 1;
}
```

Wave 319 corrects the old `PCPlatform__ReadPerformanceFrequency` / `PCPlatform__InitTimerFromPerfCounter` labels at `0x00423650` and `0x00423680` to `CFrameTimer__ctor` and `CFrameTimer__Start`. The source shows `CPCPlatform::Init()` allocating a `CFrameTimer`, calling `Start(1.0f)`, then querying performance-counter frequency; the exact `CFrameTimer` source body and concrete timer layout remain bounded to retail read-back.

Wave840 Shader Capability Init (`shader-capability-init-wave840`, `wave840-readback-verified`) hardened `0x005016b0 InitShaderCapabilityFlagsAndCVar` as `void __cdecl InitShaderCapabilityFlagsAndCVar(void)`. Static evidence ties the helper to sole caller `0x005155b1 PCPlatform__Init` immediately after the `"Initting shaders"` log, Direct3D capability probing through device vtable `+0x1c`, `DAT_00854e6c` updated from a caps dword compared against `0xfffe0101`, and `cg_forcevertexshaders` CVar registration through `CConsole__RegisterVariable` with backing byte `DAT_00854e6d`. Queue after Wave840: `5664/6098 = 92.89%` strict clean-signature proxy; next raw commentless row `0x005019c0 VFuncSlot_09_005019c0`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-030308_post_wave840_shader_capability_init_verified`. Exact Direct3D caps field identity, exact console/CVar schema, runtime hardware/driver behavior, runtime shader enablement, BEA patching, and rebuild parity remain deferred.

**Key strings:**
- `"Platform init"` at `0x0063e060`
- `"Vertex shader suppport ENABLED"` at `0x0063e01c` (note: typo "suppport")
- `"Initting shaders"` at `0x0063e008`

### PCPlatform__LoadFonts (0x005155e0)

Wave562 saved the current Ghidra signature:

```c
void __thiscall PCPlatform__LoadFonts(void * this)
```

Loads font resources for the game UI. Handles 4 different fonts with lazy initialization.

```c
void PCPlatform__LoadFonts(CPCPlatform *this)
{
    // Main UI font (offset 0x18)
    if (this->mainFont == NULL) {
        Log("Warning - loading font manually");
        this->mainFont = new CFont();  // 0x1180 bytes
        this->mainFont->Load("font22_512.tga", 0x20);  // 32pt
        this->mainFont->field_168 = 1;
    }

    // Debug font (offset 0x1c)
    if (this->debugFont == NULL) {
        Log("Warning - loading debug font manually");
        this->debugFont = new CFont();
        this->debugFont->LoadSystemFont("Terminal", 7, 0);
    }

    // Small font (offset 0x20)
    if (this->smallFont == NULL) {
        Log("Warning - loading small font manually");
        this->smallFont = new CFont();
        this->smallFont->Load("Font13PS.tga", 0x10);  // 16pt
    }

    // Title font (offset 0x24)
    if (this->titleFont == NULL) {
        Log("Warning - loading title font manually");
        this->titleFont = new CFont();
        this->titleFont->Load("TitleFont.tga", 0x20);  // 32pt
    }

    this->field_28 = 0;
    this->field_2c = 0;
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
- `"Terminal"` at `0x0063e144`

Wave595 DXFont head note: the current saved Ghidra read-back names the font-object helpers used here as `CDXBitmapFont__ctor_base`, `CDXBitmapFont__InitTextureFontSlot`, and `CDXBitmapFont__InitNamedFontSlot`. Texture-backed main/small/title fonts use `CDXBitmapFont__InitTextureFontSlot(this, texture_name, glyph_cell_width)` with `RET 0x8`; the Terminal/debug font uses `CDXBitmapFont__InitNamedFontSlot(this, font_face, font_size, font_style_flags)` with `RET 0xc`. Runtime font loading behavior and exact `CDXBitmapFont` layout remain unproven.

Wave596 note: `PCPlatform__DeserializeFontsAndAssets` calls the now-saved `CDXBitmapFont__Deserialize(void * this, void * chunk_reader)` helper four times. `RET 0x4` proves one stack argument after `this`; the helper reads serialized texture/font tables, caches texture state at `this+0x170`, fills glyph data, and initializes the cached CVBufTexture formats. Runtime font deserialization behavior and exact object layouts remain unproven.

### CPCPlatform__UnloadFonts (0x005157b0)

Wave562 saved the current Ghidra signature:

```c
void __thiscall CPCPlatform__UnloadFonts(void * this)
```

Unloads/frees font resources. Called during shutdown.

```c
void CPCPlatform__UnloadFonts(CPCPlatform *this)
{
    // Free main font (offset 0x18 = index 6)
    if (this->mainFont != NULL) {
        this->mainFont->Cleanup();  // CDXBitmapFont__ReleaseFontResources
        free(this->mainFont);       // OID__FreeObject
        this->mainFont = NULL;
    }

    // Free debug font (offset 0x1c = index 7)
    if (this->debugFont != NULL) {
        this->debugFont->Cleanup();
        free(this->debugFont);
        this->debugFont = NULL;
    }

    // Free small font (offset 0x20 = index 8)
    if (this->smallFont != NULL) {
        this->smallFont->Cleanup();
        free(this->smallFont);
        this->smallFont = NULL;
    }

    // Free title font (offset 0x24 = index 9)
    if (this->titleFont != NULL) {
        this->titleFont->Cleanup();
        free(this->titleFont);
        this->titleFont = NULL;
    }

    // Free fields at offsets 0x28 and 0x2c (indices 10, 11)
    if (this->field_28 != NULL) {
        this->field_28->Cleanup();
        free(this->field_28);
        this->field_28 = NULL;
    }

    if (this->field_2c != NULL) {
        this->field_2c->Cleanup();
        free(this->field_2c);
        this->field_2c = NULL;
    }

    // Free platform data (offset 0x00)
    if (this->platformData != NULL) {
        free(this->platformData);
        this->platformData = NULL;
    }
}
```

Wave595 names the cleanup body as `CDXBitmapFont__ReleaseFontResources`: it releases cached fields at `this+0x170`, `this+0x174`, and `this+0x178`, then returns without freeing the object; `CPCPlatform__UnloadFonts` owns the later object free/nulling path.

### PCPlatform__DeviceFlip (0x005158f0)

Wave562 PCPlatform / PCSound note: `PCPlatform__Init`, `PCPlatform__LoadFonts`, and `CPCPlatform__UnloadFonts` were hardened with saved signatures/comments/tags. Runtime platform initialization, font resource loading, and shutdown behavior remain bounded to static Ghidra read-back.

Source-aligned `CPCPlatform::DeviceFlip(BOOL)` wrapper. The saved Ghidra signature is:

```c
void __thiscall PCPlatform__DeviceFlip(void *this, int inGame)
```

The retail body reads the frame-timer pointer at `this+0x0`, calls `CFrameTimer__Frame` when the timer exists, then continues into screen-dump/device-lost restore/display work. The stack-cleaned `inGame` argument is not used in the current retail body. Runtime display behavior and concrete platform layout remain unproven.

Wave561 platform/shell read-back additionally verified the adjacent device-loss helper called from this body:

```c
void __thiscall Platform__HandleDeviceLostAndRestore(void * this)
```

`Platform__HandleDeviceLostAndRestore` (`0x00512630`) is called by `PCPlatform__DeviceFlip`, waits through the Direct3D cooperative-level path, and sets `DAT_0082b5b0` after restoration. The next queue head after Wave561 remains PCPlatform/PCSound territory beginning at `PCPlatform__Init`, `PCPlatform__LoadFonts`, and `CPCPlatform__UnloadFonts`; runtime device-loss behavior and concrete CPCPlatform field layout remain deferred.

### PCPlatform__GetFPS (0x00515950)

Source-aligned `CPCPlatform::GetFPS()` helper. The saved Ghidra signature is:

```c
float __fastcall PCPlatform__GetFPS(void *this)
```

The retail body returns the frame-timer field at `+0x4` when `mFrameTimer` exists and otherwise returns `1.0f`. Exact `CFrameTimer` field identity and runtime FPS behavior remain unproven.

### CFrameTimer Helpers (0x00423650 - 0x00423720)

Wave 319 saved the adjacent timer helpers used by `PCPlatform__Init` and `PCPlatform__DeviceFlip`:

| Address | Name | Current boundary |
|---------|------|------------------|
| `0x00423650` | `CFrameTimer__ctor` | Constructor/init path after a `0x38`-byte allocation. |
| `0x00423680` | `CFrameTimer__Start` | Start-style helper called with `1.0f` from `PCPlatform__Init`. |
| `0x00423720` | `CFrameTimer__Frame` | Per-frame timing update called by `PCPlatform__DeviceFlip`. |

These names are source-adjacent plus retail read-back evidence. The exact `CFrameTimer` source body, field names, tags, locals, and runtime timing behavior remain open.

**Called by:**
- `FUN_004f00e0` (Game shutdown routine)

## CPCPlatform Class Layout

Based on analysis of Init, LoadFonts, and UnloadFonts:

```c
class CPCPlatform {
    /* 0x00 */ void *platformData;      // D3D device data
    /* 0x04 */ int field_04;
    /* 0x08 */ LARGE_INTEGER perfFreq;  // QueryPerformanceFrequency result
    /* 0x10 */ float field_10;          // 1.0f
    /* 0x14 */ int field_14;
    /* 0x18 */ CFont *mainFont;         // font22_512.tga (32pt)
    /* 0x1c */ CFont *debugFont;        // Terminal (7pt)
    /* 0x20 */ CFont *smallFont;        // Font13PS.tga (16pt)
    /* 0x24 */ CFont *titleFont;        // TitleFont.tga (32pt)
    /* 0x28 */ void *field_28;          // Unknown, freed in UnloadFonts
    /* 0x2c */ void *field_2c;          // Unknown, freed in UnloadFonts
    // ... more fields
};
```

## Global Data

| Address | Name | Purpose |
|---------|------|---------|
| `0x008898d8` | `DAT_008898d8` | FindFirstFile handle for save enumeration |
| `0x008898e0` | `DAT_008898e0` | WIN32_FIND_DATA.dwFileAttributes |
| `0x008898f4` | `DAT_008898f4` | WIN32_FIND_DATA.cFileName |
| `0x00662f00` | `DAT_00662f00` | Vertex shader disable flag |
| `0x00662dec` | `DAT_00662dec` | Force vertex shader flag |
| `0x0063c108` | `DAT_0063c108` | Vertex shader enabled status |

## String Constants

| Address | String | Used By |
|---------|--------|---------|
| `0x0063df7c` | `"savegames\\*.bes"` | Save file enumeration pattern |
| `0x0063df8c` | `".bes"` | Save file extension |
| `0x0063df94` | `"savegames\\"` | Save directory path |
| `0x0063e008` | `"Initting shaders"` | Init logging |
| `0x0063e01c` | `"Vertex shader suppport ENABLED"` | Init logging (typo preserved) |
| `0x0063e03c` | `"[maintainer-local-source-export-root]\\PCPlatform.cpp"` | Debug source path |
| `0x0063e060` | `"Platform init"` | Init logging |
| `0x0063e0d4` | `"TitleFont.tga"` | Title font file |
| `0x0063e0e4` | `"Warning - loading title font manually"` | Font loading warning |
| `0x0063e10c` | `"Font13PS.tga"` | Small font file |
| `0x0063e11c` | `"Warning - loading small font manually"` | Font loading warning |
| `0x0063e144` | `"Terminal"` | Debug font name |
| `0x0063e150` | `"Warning - loading debug font manually"` | Font loading warning |
| `0x0063e178` | `"font22_512.tga"` | Main UI font file |
| `0x0063e188` | `"Warning - loading font manually"` | Font loading warning |

## Related Files

- `Platform.cpp` - Generic platform abstraction (async save, directory creation)
- See also: [`Platform.cpp`](../Platform.cpp/_index.md)

## Notes

1. Save file operations use Win32 APIs directly (FindFirstFile, DeleteFileA, fopen/fread/fwrite)
2. Font loading has "manual" fallback paths with warning messages - suggests fonts should normally be loaded via resource system
3. The `CPCPlatform__UnloadFonts` function is called during game shutdown (found in shutdown sequence alongside CMusic__Shutdown)
4. File attribute check `(attributes & 0x16) == 0` filters out directories, hidden, and system files
5. Save path construction: `"savegames\\" + saveName + ".bes"`
