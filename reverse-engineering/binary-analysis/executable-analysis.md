# Executable Analysis (BEA.exe)


## Executable Metadata

**File**: `BEA.exe` (Steam version)

| Property | Value |
|----------|-------|
| **MD5** | `3b456964020070efe696d2cc09464a55` |
| **SHA256** | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` |
| **File Size** | 2,506,752 bytes (~2.4 MB) |
| **Loaded Memory** | ~6.1 MB (includes BSS/uninitialized data) |
| **Architecture** | x86 32-bit |
| **Functions** | 5,771 identified |
| **Format** | PE / D3D9 |

**Notes**: CompanyName says "Lost Toys" (retail build still branded Lost Toys). The Windows retail release was published by Encore; per Stuart (Discord, Dec 2025), the retail Windows work was done in-house at Lost Toys (Jan, ex-Mucky Foot, and possibly others). D3D9 confirms retail/Steam build (not Stuart's D3D8 internal dev build).

---

## Key DLL Dependencies

| DLL | Purpose |
|-----|---------|
| BINKW32.DLL | Bink Video (cutscenes) |
| D3D9.DLL | Direct3D 9 graphics |
| DINPUT8.DLL | DirectInput 8 controls |
| DSOUND.DLL | DirectSound audio |
| OGG/VORBIS.DLL | Ogg Vorbis codec |
| ZLIB.DLL | Compression |
| AVIFIL32.DLL | AVI handling |
| WSOCK32.DLL | Networking |

---

## Save/Load Function Map

| Address | Function | Description |
|---------|----------|-------------|
| 0x00421350 | CCareer__Save | Serializes career to buffer |
| 0x004213c0 | CCareer__SaveWithFlag | Serializes career to buffer (retail save path helper; flag behavior still being mapped) |
| 0x00421200 | CCareer__Load | Deserializes buffer to career (`flag=0`: boot/defaultoptions path, applies Sound/Music and options entries/tail globals; `flag!=0`: career `.bes` load, preserves pre-load Sound/Music and skips options entries/tail apply) |
| 0x00421430 | CCareer__GetSaveSize | Calculates dynamic save size |
| 0x00420b10 | OptionsTail_Write | Writes `0x56` bytes of globals/options tail state |
| 0x00420d70 | OptionsTail_Read | Reads `0x56` bytes of globals/options tail state |
| 0x00514f80 | PCPlatform__WriteSaveFile | Generic file write wrapper (savegames folder) |
| 0x00515080 | PCPlatform__ReadSaveFile | Generic file read wrapper (savegames folder) |
| 0x00464c50 | CFEPSaveGame__CreateSave | Save-menu handler (serializes CAREER and writes `savegames\\<name>.bes`) |
| 0x00461e20 | CFEPLoadGame__DoLoad | UI handler for load menu |

---

## File Mode Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x00629038 | "rb" | Binary read (load) |
| 0x0063316c | "wb" | Binary write (save) |
| 0x0063df7c | "savegames\\*.bes" | Save file pattern |
| 0x0063df94 | "savegames\\" | Save directory |

---

## Other Interesting Ghidra Strings

**Debug frustration string** found in exe (from Dominating David, Discord #media, April 2025):
```
"SHIT DAMN FUCKING BASTARD"
```
Stuart's response: *"Sounded like a bad day in the office for someone. Could of been me."*

**Source file debug paths**: See `reverse-engineering/binary-analysis/functions/string-locations-index.md` for the current indexed debug-path strings (counts vary by scan/filtering), and `reverse-engineering/source-code/_index.md` for Stuart-source inventory context.

**PC Version History**: Original 2003 Windows release was bundled with Nvidia cards (date 26/5/03 found in file). The Steam version is a later retail build (console-port lineage) and differs from Stuart's internal PC dev snapshot; the exact lineage between console/retail variants is not fully proven yet.
