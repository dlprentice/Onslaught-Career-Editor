# FEPSaveGame.cpp - Function Index

> Source File: FEPSaveGame.cpp | Category: Frontend/Save System

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Frontend save game menu implementation. Contains the XOR-encrypted cheat code system that checks save game names for special codes.

Wave900 final static tail (`final-static-tail-wave900`, `wave900-readback-verified`) closed the remaining frontend-save/CRT locale support row `0x005d0c7f CRT__LCMapStringW_AnsiCompat`, called by `CFEPSaveGame__WideCharToLowerCompat` at `0x005d0a89`. Probe token anchor: Wave900 final static tail; final-static-tail-wave900; 0x005d04e6 RtlUnwind; 0x005d06f0 CRT__InitSehFrameNoop; 0x005d08ad CRT__TmpFile_OpenUniqueBinaryStream; 0x005d0a9f CRT__LongJmpProbe_NoOp; 0x005d0c0c GetCurrentProcessId; 0x005d0c7f CRT__LCMapStringW_AnsiCompat; 0x005d5120 CTexture__FindTexture_Unwind; 6113/6113 = 100.00%; G:\GhidraBackups\BEA_20260526-090248_post_wave900_final_static_tail_verified. Static evidence shows the helper probes `LCMapStringW`/`LCMapStringA` support through `DAT_009d304c`, falls back through `WideCharToMultiByte` and `MultiByteToWideChar` when needed, and remains bounded static evidence only; exact runtime locale/save-name collation behavior, BEA patching, and rebuild parity remain deferred.

Wave802 static read-back (`frontend-save-multiplayer-wave802`, `wave802-readback-verified`) corrected the former save-game-only `0x0044d390 CFEPSaveGame__InitDialogAndLayoutState` label to shared `0x0044d390 FEMessBox__Create`. `RET 0x2c` proves eleven explicit stack arguments after `ECX=this`, and save/load/frontend callsites use the same `FEMESSBOX.Create(...)` message-box path. Verified backup: `G:\GhidraBackups\BEA_20260524-081932_post_wave802_frontend_save_multiplayer_verified`. Exact FEMessBox layout, runtime save/load dialog behavior, BEA patching, and rebuild parity remain deferred.

Wave954 (`save-load-directory-review-wave954`) re-reviewed the frontend save/load/directory handoff around `0x00461c40 CFEPLoadGame__Init`, `0x00464620 CFEPSaveGame__Init`, and `0x0051ad30 CFEPDirectory__RefreshSaveFileList`. Fresh evidence ties save context through `CFEPSaveGame__CreateSave`, `EnumerateSaveFiles_Main`, `PCPlatform__WriteSaveFile`, live `0x00514ec0 PCPlatform__DeleteSaveFile`, and the shared FEPDirectory refresh/render consumers; debug strings include `C:\dev\ONSLAUGHT2\FEPSaveGame.cpp` and `C:\dev\ONSLAUGHT2\FEPDirectory.cpp`. no mutation was needed. Wave911 focused re-audit progress after Wave954 is `283/1408 = 20.10%`; static closure remains `6151/6151 = 100.00%`; verified backup: `G:\GhidraBackups\BEA_20260528-100717_post_wave954_save_load_directory_review_verified`.

## Wave740 DInput/CRT Tail Static Read-Back

Wave740 DInput/CRT tail saved the adjacent frontend-save wide-string helpers `0x005d04ec CFEPSaveGame__WideStrCaseInsensitiveCompare` and `0x005d0a2a CFEPSaveGame__WideCharToLowerCompat` with the `dinput-crt-tail-wave740` and `wave740-readback-verified` tags. The same bounded pass also hardened support rows `0x005d04e0 DirectInput8Create`, `0x005d070f CRT__VsnprintfAndTerminate_005d070f`, `0x005d075f CRT__FormatToBufferAndTerminate`, `0x005d07f4 CRT__FSeek_Locked`, `0x005d0820 CRT__FSeek_UnlockedCore`, `0x005d09e4 CRT__IncrementDotSuffixCounter`, `0x005d0e88 CRT__WcsNLen`, and `0x005d0eb8 CRT__GetCharTypeMaskCompat`.

Static evidence: `EnumerateSaveFiles_Main` and `CFEPSaveGame__CreateSave` call the compare helper with two wide-string pointers; the compare helper folds ASCII A-Z directly when locale globals are inactive and otherwise calls the wide-char lowercase helper for both strings. The lowercase helper preserves `0xffff`, uses `CRT__GetCharTypeMaskCompat` with mask `1` for byte-range characters, and can fall back to `CRT__LCMapStringW_AnsiCompat`. Queue telemetry after Wave740: `6098` total, `4361` commented, `1737` commentless, `1214` exact-undefined signatures, `27` `param_N`, strict proxy `4303/6098 = 70.56%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005d0f10 Unwind@005d0f10`. Verified backup: `G:\GhidraBackups\BEA_20260522-141639_post_wave740_dinput_crt_tail_verified`.

Scope boundary: save enumeration runtime behavior, save-name runtime behavior, runtime locale behavior, exact CRT version, exact locale table identity, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x00464620 | [CFEPSaveGame__Init](./CFEPSaveGame__Init.md) | Named | Initialize save-game selection state |
| 0x00464630 | [CFEPSaveGame__ButtonPressed](./CFEPSaveGame__ButtonPressed.md) | Named | Handle frontend save-game menu input |
| 0x00464730 | [CFEPSaveGame__Process](./CFEPSaveGame__Process.md) | Named | Process save-game menu state and dispatch create-save flow |
| 0x00464a80 | [CFEPSaveGame__Render](./CFEPSaveGame__Render.md) | Named | Render save-game menu title, borders, overlay, and help prompt |
| 0x00464b10 | [FEPSaveLoad__TransitionNotification](./FEPSaveLoad__TransitionNotification.md) | Named | Shared save/load transition timer hook |
| 0x00464b30 | [CFEPSaveGame__RemovedMUWhinge](./CFEPSaveGame__RemovedMUWhinge.md) | Named | Shared localized storage-message dialog helper |
| 0x00464bc0 | [CFEPSaveGame__AskIfYouWantToDelete](./CFEPSaveGame__AskIfYouWantToDelete.md) | Named | Build delete/no-space storage prompt dialog |
| 0x00464c50 | [CFEPSaveGame__CreateSave](./CFEPSaveGame__CreateSave.md) | Named | Creates/overwrites save and writes `.bes` via `CCareer__SaveWithFlag` + `PCPlatform__WriteSaveFile` |
| 0x00465490 | [IsCheatActive](./IsCheatActive.md) | Named | XOR decrypts cheat codes, checks save name via strstr() |

## Cheat Code System

The PC port uses XOR-encrypted cheat codes checked against save game names at runtime.

### Memory Locations

| Address | Size | Purpose |
|---------|------|---------|
| 0x00629a64 | 10 bytes | XOR decryption key: `"HELP ME!!"` |
| 0x00629464 | ~1280 bytes | Cheat code table (256 bytes per cheat) |
| 0x00662df4 | 1 byte | `g_bDevModeEnabled` - enables all cheats if set |
| 0x00679ec1 | 1 byte | `g_bAllCheatsEnabled` - enables all cheats if set |

### Known Cheat Codes

| Index | Code | Effect | Status |
|-------|------|--------|--------|
| 0 | `MALLOY` | All goodies | Works (Dec 2025 user testing confirmed) |
| 1 | `TURKEY` | All levels | Works |
| 2 | `V3R5IOF` | Version display | Decoded from BEA.exe; no call sites found (needs in-game confirmation) |
| 3 | `Maladim` | God mode toggle UI | Call site found; later testing confirmed visible `God OFF` / `God ON` toggle plus real combat-damage effect |
| 4 | `Aurore` | Free camera debug toggle | Verified in binary (gates `BUTTON_TOGGLE_FREE_CAMERA`) |
| 5 | `latête` | Goodie UI override | Verified in binary (sets `g_Cheat_LATETE`; forces displayed goodie state to `1`) |

**Note:** Stuart's source/internal build uses `V3R5ION` (index 2) and `B4K42` (index 3). In the Steam retail build, the XOR-decrypted cheat table yields `V3R5IOF` at index 2. See `reverse-engineering/game-mechanics/cheat-codes.md` and `tools/cheat_table_decode.py`.

### How It Works

1. `IsCheatActive(int index)` is called with cheat index
2. First checks `g_bDevModeEnabled` and `g_bAllCheatsEnabled` - returns TRUE if either set
3. XOR-decrypts the cheat code at `0x00629464 + (index * 256)` using key `"HELP ME!!"`
4. Uses `strstr()` to check if the current save name **contains** the decrypted code
5. Returns TRUE if found, FALSE otherwise

### Important Notes

- **B4K42 is NOT in IsCheatActive!** The source code shows B4K42, but Ghidra reveals the binary uses `Maladim` for god mode (index 3)
- Cheat codes use **substring matching** via `strstr()` - code can appear anywhere in save name
- The MALLOY cheat works correctly via save name (Dec 2025 user testing); Ghidra-discovered inverted logic may only affect dev mode

## Cross-References

- Called by: FEPGoodies, PauseMenu, various game systems
- Related: [FEPGoodies.cpp](../FEPGoodies.cpp/_index.md) - uses IsCheatActive for goodie unlocks
- Related: [FEPLoadGame.cpp](../FEPLoadGame.cpp/_index.md) - loads save files that contain names checked by cheats

## Migration Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Cheat system discovered via Ghidra analysis of IsCheatActive
