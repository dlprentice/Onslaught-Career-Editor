# BEA.exe Binary Patches

Binary patches for Battle Engine Aquila (Steam/PC version) discovered via Ghidra reverse engineering.

**IMPORTANT:** These scripts are **binary patch experiments** for BEA.exe. They are **not** save-file patchers and should **not** be treated as sources of truth for `.bes` format behavior. For save editing, use `BesFilePatcher.cs` and `patcher.py` as the authoritative implementations.

## Quick Start

**No patch needed for MALLOY cheat** - user testing (Dec 2025) confirmed MALLOY works via save name without any binary patches.

Simply create a save with **MALLOY** in the name to unlock all goodies.

The **DEV MODE ONLY** recommendation below applies specifically to `patch_devmode_goodies_logic_fix.py` (prevents `g_bAllCheatsEnabled` from triggering the goodies-only `lat\\xEAte` UI override). The display/windowing patch set (`patch_display_mode_flow.py`) is separate.

## Patch Tracks

Two-track policy is used across docs/tooling:

- **Stable**: default byte-verified patches intended for normal users.
- **Experimental**: opt-in patches with higher environment variance/risk.

Current display-flow mapping:
- Stable: resolution gate bypass, force windowed startup flag, extra-graphics gate default-on, and cardid override-load bypass.
- Stable (auto companion when applying any patch): version overlay tag (`V1.00 - PATCHED`).
- Experimental (optional): skip auto fullscreen-toggle gate.

## Patch Catalog v2 (Canonical)

The canonical machine-readable patch catalog is:

- `patches/catalog/patches.v2.json`

This catalog is consumed by:

- C# `BinaryPatchEngine` (WPF Binary Patches tab)
- Python `onslaught/core/binary_patches.py` (PyQt Binary Patches tab)

`patch_display_mode_flow.py` remains a script convenience surface for the same display-flow patch family.

Important: file patches cannot directly set `g_bAllCheatsEnabled` because it lives in **BSS** (runtime-initialized, not file-backed). To actually activate dev-mode bypass behavior you need:
- A runtime memory trainer, or
- Whatever in-game logic sets the flag (e.g. the `GameLoop_DevModeEasterEgg` timing path).

Scripts default to Steam installation at:
`C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe`

Custom path (if needed):
```bash
python3 patches/patch_devmode_goodies_logic_fix.py "D:\Games\BEA.exe"
```

## Available Patches (Supported)

### patch_display_mode_flow.py (Display/Windowing, Stable + Experimental)

Adds reversible display-flow patches aimed at resolution flexibility and windowed startup behavior.

Supported patch set:

| Patch | VA | File Offset | Before | After | Purpose |
|------|----|-------------|--------|-------|---------|
| BuildDeviceList non-4:3 rejection bypass | `0x00529696` | `0x129696` | `CC` | `00` | Stops rejecting non-4:3 modes when widescreen cvar is false |
| Force windowed startup flag | `0x0052A644` | `0x12A644` | `A1 F0 2D 66 00` | `B8 01 00 00 00` | Forces startup windowed decision to true (when windowed-capable) |
| Unlock extra graphics feature default gate | `0x004CDD40` | `0x0CDD40` | `6A 00` | `6A 01` | Sets `GEFORCE_FX_POWER` default to enabled without cardid vendor/device matching |
| Ignore cardid tweak override load call | `0x0052AF3F` | `0x12AF3F` | `E8 9C D7 FF FF` | `90 90 90 90 90` | Uses BEA.exe defaults directly by bypassing cardid parser/apply call |
| Version overlay pointer -> patched format cave | `0x0046316F` | `0x06416F` | `54 94 62 00` | `44 A4 5A 00` | Redirects bottom-left version text format pointer to patch-owned cave payload |
| Version overlay cave payload (`V%1d.%02d - PATCHED`) | `0x005AA444` | `0x1AA444` | `CC` x20 | ASCII payload bytes | Provides visible watermark when patch set is active |
| Optional: skip auto fullscreen toggle gate (**Experimental**) | `0x0052BB97` | `0x12BB97` | `75 20` | `EB 20` | Optional flow tweak to skip startup ToggleFullscreen gate |

Usage:
```bash
python3 patches/patch_display_mode_flow.py --verify
python3 patches/patch_display_mode_flow.py --apply
python3 patches/patch_display_mode_flow.py --apply --resolution-only
python3 patches/patch_display_mode_flow.py --apply --windowed-only
python3 patches/patch_display_mode_flow.py --apply --skip-auto-toggle
python3 patches/patch_display_mode_flow.py --restore
```

### patch_devmode_goodies_logic_fix.py (Recommended) - DEV MODE ONLY

**STATUS: Prevents `g_bAllCheatsEnabled` from activating the goodies-only `lat\\xEAte` flag**

**NOTE:** The MALLOY cheat works WITHOUT this patch when using a save name containing "MALLOY".
This patch is only needed if you enable the `g_bAllCheatsEnabled` flag behavior (dev mode) and
want the goodies gallery to behave like “MALLOY only”.

**What it actually changes:** in `CFEPGoodies::Process` (0x0045D7E0), the game sets two runtime flags:
- `g_Cheat_MALLOY = IsCheatActive(0)`
- `g_Cheat_LATETE = IsCheatActive(5)`

When `g_bAllCheatsEnabled` is enabled, `IsCheatActive()` returns TRUE for *all* indices, so both flags become `1`.
The `lat\\xEAte` path is a goodies UI override and can interfere with the “unlock everything” experience.

This patch forces `g_Cheat_LATETE` to always be written as `0` in the goodies UI.

| Patch | VA | File Offset | Before | After |
|-------|-----|-------------|--------|-------|
| Fix 1 | `0x0045D819` | `0x5D819` | `F7 D8` (NEG EAX) | `33 C0` (XOR EAX,EAX) |

**Usage:** For dev mode exploration only. Normal users should just use save name cheats.

## Archived Patches (Reference Only)

These are kept for archival/reference. They live in `patches/archive/` and should not be used unless you know exactly what you're doing.

### archive/patch_ischeatactive_always_true_BROKEN.py (Archived) - DO NOT USE

**STATUS: BROKEN - Causes goodies to LOCK**

This patch made `IsCheatActive()` always return TRUE, which also activates the `lat\\xEAte` goodies-only
override everywhere it is consulted. In the goodies UI, this breaks the normal “MALLOY unlocks all”
flow and can effectively lock/hide items.

| Property | Value |
|----------|-------|
| Virtual Address | `0x00465490` |
| File Offset | `0x65490` |
| Original | `A1 F4 2D 66 00 81 EC 00 01 00 00` |
| Patched | `B8 01 00 00 00 C2 04 00 90 90 90` |
| Function | `IsCheatActive()` entry point |

**Intended Effects (BROKEN - see above):**
| Cheat | Index | Intended Effect | Actual Effect |
|-------|-------|-----------------|---------------|
| MALLOY/105770Y2 | 0 | All goodies unlocked | **LOCKS goodies** (lat\\xEAte interaction) |
| TURKEY/!EVAH! | 1 | All campaign levels accessible | Works |
| V3R5IOF | 2 | Version display enabled | Unknown (no call sites found yet) |
| Maladim | 3 | God mode | No visible effect |

**Technical Note:** The patch replaces the function's prologue with `MOV EAX,1; RET 4` making it immediately return TRUE without checking any flags or save names.

### archive/patch_ischeatactive_return_path_bypass.py (Legacy) - FALLBACK

**STATUS: Partial - only enables TURKEY effect**

A simpler 2-byte patch that modifies a conditional jump in `IsCheatActive()`. Prefer `patch_devmode_goodies_logic_fix.py` for dev-mode exploration; for normal users, prefer save-name cheats (no patch).

| Property | Value |
|----------|-------|
| Virtual Address | `0x004654a0` |
| Original | `75 7A` (JNZ) |
| Patched | `EB 7A` (JMP) |

Only affects the final return path in `IsCheatActive()`, not the early-exit checks.

## Deleted Patches (Dec 2025)

The following patches were removed because they don't work:

### patch_all_cheats_v2.py - DELETED

**Reason:** Attempted to patch `g_bAllCheatsEnabled` at `0x00679ec1`, but this address is in **BSS (uninitialized memory)** - it doesn't exist in the executable file. BSS variables are zero-initialized by Windows at runtime.

**BSS Analysis:**
```
.data section:
  Virtual Size:   0x3B2614 (includes BSS)
  Raw Size:       0x3F000  (file-backed only)

g_bAllCheatsEnabled offset in section: 0x57ec1
0x57ec1 > 0x3F000  (ADDRESS IS IN BSS, NOT IN FILE)
```

### patch_windowed_mode.py - DELETED

**Reason:** Replaced by `patch_display_mode_flow.py` (which includes current windowed/startup flow patches plus verification/restore).

## Cheat Codes (CORRECTED Dec 2025)

Enter these as your **save game name** (case-sensitive, can be substring):

| Index | Code | Effect | Notes |
|-------|------|--------|-------|
| 0 | **MALLOY** | All goodies | Works via save name (no patch needed) |
| 1 | **TURKEY** | All levels unlocked | Works without patch |
| 2 | **V3R5IOF** | Version display | Decoded from BEA.exe; no call sites found yet (needs in-game confirmation) |
| 3 | **Maladim** | God mode toggle | No visible effect - needs investigation |
| 4 | **Aurore** | Free camera debug toggle | Gates `BUTTON_TOGGLE_FREE_CAMERA` in `CGame::ReceiveButtonAction` |
| 5 | **lat\\xEAte** | Goodie UI override | Used in retail binary; affects how goodie state is displayed (see reverse-engineering docs) |

**XOR Decryption:** Cheat codes stored at `0x00629464`, encrypted with key `"HELP ME!!"` at `0x00629a64`.

**IMPORTANT:** B4K42 is from the internal/source build and is **not** present in the Steam PC port cheat table.

**Note:** The `g_bAllCheatsEnabled` (dev mode) code path is distinct from the normal `strstr()` cheat-name path.
The normal `strstr()` cheat code path works correctly: MALLOY unlocks goodies without any patch.

## Direct Flag Check Locations

11 code locations check `g_bAllCheatsEnabled` directly, bypassing `IsCheatActive()`. These control additional dev behaviors not covered by `archive/patch_ischeatactive_always_true_BROKEN.py`:

| Address | Function | Purpose |
|---------|----------|---------|
| `0x004654a2` | IsCheatActive | Early-exit check |
| `0x0046668b` | FUN_004662a0 | Unknown |
| `0x00466736` | FUN_004662a0 | Unknown |
| `0x00468499` | FUN_00468200 | Unknown |
| `0x004714e3` | FrontendUpdate_CheatChecks | Frontend flow |
| `0x004715ef` | FrontendUpdate_CheatChecks | Frontend flow |
| `0x004bb5d4` | FUN_004bb530 | Music selection? |
| `0x004bb64f` | FUN_004bb530 | Music selection? |
| `0x004bb86f` | FUN_004bb7e0 | Unknown |
| `0x004bb9b3` | FUN_004bb8c0 | Unknown |
| `0x0046ea34` | GameLoop_DevModeEasterEgg | Sets flag after ~20100 frames |

For FULL dev mode behavior, a runtime trainer would be needed to set `g_bAllCheatsEnabled = 1` in memory.

## Key Global Flags (All in BSS - cannot file-patch)

| Address | Name | Purpose |
|---------|------|---------|
| `0x00662df4` | `g_bDevModeEnabled` | If set, all cheats active |
| `0x00679ec1` | `g_bAllCheatsEnabled` | All cheats enabled flag |
| `0x00662ab4` | `g_bGodModeEnabled` | Current god mode state |

## Target Executable

| Property | Value |
|----------|-------|
| MD5 | `3b456964020070efe696d2cc09464a55` |
| SHA256 | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` |
| File Size | 2,506,752 bytes |
| Source | Steam (Battle Engine Aquila) |

Other versions (retail CD, GOG) may have different offsets.

### Other binaries in this repo (NOT patch targets)

| File | MD5 | SHA256 | Notes |
|------|-----|--------|-------|
| `BEA_Widescreen.exe` | `b2025e385b8da8d19656b538e1268fc4` | `67994e5f5f418cca2ed253ab643112ac3a82ea1647e8172027eb9c9cc7b37f61` | Widescreen patch executable; offsets may differ. |
| `BEA.exe.gzf` | n/a | n/a | Ghidra packed database (not an executable). |

## Safety

- Backup filenames differ by tool:
  - `patch_display_mode_flow.py` -> `BEA.exe.original.backup`
  - `patch_devmode_goodies_logic_fix.py` -> `BEA.exe.backup`
- Binary Patches UI restore flow uses `BEA.exe.original.backup`
- Patches are for single-player - no anti-cheat concerns
- Always verify SHA256 matches before patching

## Discovery

Discovered via Ghidra analysis of BEA.exe (December 2025) as part of the Onslaught Career Editor project. See `reverse-engineering/` documentation for full technical details.
