# PCPlatform.cpp Functions

PC-specific platform abstraction layer implementation. Handles save file I/O, font loading, D3D initialization, and platform-specific features for the Windows port.

**Debug Path String:** `C:\dev\ONSLAUGHT2\PCPlatform.cpp` at `0x0063e03c`

## Functions Found

| Address | Name | Purpose |
|---------|------|---------|
| `0x005149c0` | `EnumerateSaveFiles_1` | Counts save files in savegames folder |
| `0x00514a80` | `EnumerateSaveFiles_2` | Gets save file name by index |
| `0x00514be0` | `EnumerateSaveFiles_Main` | Main save file enumeration with validation |
| `0x00514ec0` | `PCPlatform__DeleteSaveFile` | Deletes a save file |
| `0x00514f80` | `PCPlatform__WriteSaveFile` | Writes data to save file |
| `0x00515080` | `PCPlatform__ReadSaveFile` | Reads data from save file |
| `0x00515190` | `FUN_00515190` | Simple setter (save-related) |
| `0x005154e0` | `PCPlatform__Init` | Platform initialization (D3D, shaders) |
| `0x005155e0` | `PCPlatform__LoadFonts` | Loads font resources |
| `0x005157b0` | `CPCPlatform__UnloadFonts` | Unloads/frees font resources |

**Total: 10 functions**

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

Initializes the PC platform layer. Sets up D3D device, performance counters, and vertex shaders.

```c
int PCPlatform__Init(CPCPlatform *this)
{
    Log("Platform init");

    // Allocate platform data (0x38 bytes)
    void *platformData = malloc(0x38, 0x80);
    if (platformData == NULL)
        return 0;

    this->platformData = InitD3DDevice();  // FUN_00423650
    if (this->platformData == NULL)
        return 0;

    SetupD3D(1.0f);  // FUN_00423680
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

**Key strings:**
- `"Platform init"` at `0x0063e060`
- `"Vertex shader suppport ENABLED"` at `0x0063e01c` (note: typo "suppport")
- `"Initting shaders"` at `0x0063e008`

### PCPlatform__LoadFonts (0x005155e0)

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

### CPCPlatform__UnloadFonts (0x005157b0)

Unloads/frees font resources. Called during shutdown.

```c
void CPCPlatform__UnloadFonts(CPCPlatform *this)
{
    // Free main font (offset 0x18 = index 6)
    if (this->mainFont != NULL) {
        this->mainFont->Cleanup();  // FUN_0053f770
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
| `0x0063e03c` | `"C:\\dev\\ONSLAUGHT2\\PCPlatform.cpp"` | Debug source path |
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
- See also: `Platform.cpp/_index.md`

## Notes

1. Save file operations use Win32 APIs directly (FindFirstFile, DeleteFileA, fopen/fread/fwrite)
2. Font loading has "manual" fallback paths with warning messages - suggests fonts should normally be loaded via resource system
3. The `CPCPlatform__UnloadFonts` function is called during game shutdown (found in shutdown sequence alongside CMusic__Shutdown)
4. File attribute check `(attributes & 0x16) == 0` filters out directories, hidden, and system files
5. Save path construction: `"savegames\\" + saveName + ".bes"`
