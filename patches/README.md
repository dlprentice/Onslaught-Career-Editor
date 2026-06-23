# BEA.exe Binary Patches

Binary patches for Battle Engine Aquila (Steam/PC version) discovered via Ghidra reverse engineering.

**IMPORTANT:** These scripts are **binary patch experiments** for BEA.exe. They are **not** save-file patchers and should **not** be treated as sources of truth for `.bes` format behavior. For save editing, use AppCore/C# (`OnslaughtCareerEditor.AppCore/BesFilePatcher.cs`) and the save-format docs as the authoritative implementation; archived Python patchers are historical reference only.

## Quick Start

**No patch needed for MALLOY cheat** - user testing (Dec 2025) confirmed MALLOY works via save name without any binary patches.

Simply create a save with **MALLOY** in the name to make the game treat/display Goodies as available while that save-name cheat path is active. This is not a `.bes`/`defaultoptions.bea` permanent-award patch.

The **DEV MODE ONLY** recommendation below applies specifically to `patch_devmode_goodies_logic_fix.py` (prevents `g_bAllCheatsEnabled` from triggering the goodies-only `lat\\xEAte` UI override). The display/windowing patch set (`patch_display_mode_flow.py`) is separate.

## Patch Tracks

Two-track policy is used across docs/tooling:

- **Bytes-checked stable**: patch rows whose original/patched bytes are known and guarded by catalog patch verification. Some stable rows are opt-in diagnostics or mods, not default selections.
- **Experimental**: opt-in patches with higher environment variance/risk.

Current display-flow mapping:
- Current patch catalog accounting: 29 total rows; 20 visible options (9 stable, 11 experimental); 9 hidden companions.
- Windowed + Graphics Defaults preset: bytes-checked resolution gate bypass, force windowed startup flag, extra-graphics `GEFORCE_FX_POWER` default-on, and cardid override-load bypass. The baseline compatibility copy remains the narrower windowed pair.
- Bytes-checked opt-in diagnostic: version overlay marker bytes (`V1.00 - PATCHED` when the title/menu overlay is reached in the bounded copied-game proof). Selecting this visible row also selects the hidden cave-string payload; broader overlay/gameplay paths remain unproven.
- Bytes-checked opt-in frontend color mods: dark red, dark green, and black clear-screen immediates for the DirectX frontend render-start path. Select only one color preset at a time. Red, green, and black each have one local safe-copy title-screen capture showing the selected clear-screen margins; broader menu coverage remains pending.
- Bytes-checked opt-in Goodies display mod: MALLOY-derived Goodies display flag override for copied executables only; two bounded copied-game baseline-vs-patched Goodies-wall comparison pairs show selected display-state changes, and one patched selection run shows a selected character-art presentation page.
- Bytes-checked experimental debug-camera mods: Aurore free-camera gate bypass for copied executables only, plus mutually exclusive Q-forward, Q-backward, Q-strafe-left, Q-strafe-right, Q-yaw-left, Q-yaw-right, Q-pitch-up, and Q-pitch-down companion hook/cave variants. Focused CDB runtime proof is accepted for the toggle path, four bounded one-key movement paths, and four bounded one-key orientation paths; broader control feel, joystick/analog coverage, pause/menu safety, gameplay safety, and parity remain pending.
- Bytes-checked experimental pause-key initializer candidate: `pause_o_scan_initializer_experiment` changes only the copied executable's default `BUTTON_PAUSE` row initializer byte from scan `0x01` to scan `0x18` (`O` candidate). Accepted exact-PID copied-runtime CDB proof shows the copied byte as `0x18`, the live pause row keyArg as `0x18`, ordered same-window `O` query, `BUTTON_PAUSE` dispatch, and one pause/unpause pair in a bounded free-camera context; a later bounded level-100 normal-gameplay proof shows `O` opens the pause menu and `ENTER` resumes from it. Second-`O` normal-gameplay unpause, broad pause-menu safety, gameplay safety, and control feel remain unproven.
- Experimental (optional): skip auto fullscreen-toggle gate.

## Patch Catalog v2 (Canonical)

The canonical machine-readable patch catalog is:

- `patches/catalog/patches.v2.json`

The canonical machine-readable safe-copy profile catalog is:

- `patches/catalog/safe-copy-profiles.v1.json`

This catalog is consumed by:

- C# `BinaryPatchEngine` through the WinUI Windowed & Mods/AppCore lane (legacy/internal automation IDs may still say Patch Bench).
- `tools/apply_bea_catalog_patch.py` as a safe-copy-only lab/helper surface.
- Current `patches/*.py` helper scripts only as copied-target lab/reference surfaces when deliberately invoked.

Each current catalog row carries the canonical clean Steam retail `BEA.exe` SHA-256 and file size. Product apply/verify mutation refuses the built-in fallback specs; fallback rows are verification/test-only unless a test explicitly opts in. Restore is a deliberate recovery exception: it may use fallback row shapes to classify a copied working file before restoring the full-file backup snapshot.

Safe-copy profile presets are layered on top of the patch catalog rather than replacing it. AppCore loads `safe-copy-profiles.v1.json`, validates profile patch keys against `patches.v2.json`, rejects hidden companion rows as direct profile keys, and writes `profileCatalogVersion`, `profileCatalogSha256`, module restore strategies, evidence references, and explicit non-claims into generated playable-copy manifests.

`patch_display_mode_flow.py` remains a script convenience surface for the display/windowing and version-overlay patch family. Catalog-only rows such as `frontend_clear_screen_dark_red` are exposed through the WinUI/AppCore catalog engine, not this standalone script.

Important: file patches cannot directly set `g_bAllCheatsEnabled` because it lives in **BSS** (runtime-initialized, not file-backed). To actually activate dev-mode bypass behavior you need:
- A runtime memory trainer, or
- Whatever in-game logic sets the flag (e.g. the `GameLoop_DevModeEasterEgg` timing path).

The WinUI/AppCore product path is the preferred patch lane. It prepares a playable copied game folder under an app-owned root, patches only the copied `BEA.exe`, verifies patch bytes, and leaves the installed game untouched.

Standalone active scripts are lab/reference helpers. Mutating modes require an explicit copied `BEA.exe` path plus `--allowed-root`, a generated playable copied-game manifest, verified backup hash sidecars, and refuse Program Files, Steam-library-shaped roots, reparse-point targets, and hardlinked targets. Broken/legacy scripts under `patches/archive/` are archival only and intentionally refuse to write bytes.

Custom path (if needed):
```bash
python3 patches/patch_devmode_goodies_logic_fix.py "D:\SafeCopy\BEA.exe" --allowed-root "D:\SafeCopy"
```

## Available Patches (Supported)

### patch_display_mode_flow.py (Display/Windowing And Version Overlay, Stable + Experimental)

Adds reversible display-flow patches aimed at resolution enumeration flexibility and windowed startup behavior.

Supported patch set:

| Patch | VA | File Offset | Before | After | Purpose |
|------|----|-------------|--------|-------|---------|
| Let non-4:3 display modes pass enumeration | `0x00529696` | `0x129696` | `CC` | `00` | Neutralizes one non-4:3 mode rejection gate; it does not by itself guarantee widescreen/FOV/rendering parity |
| Force windowed startup flag | `0x0052A644` | `0x12A644` | `A1 F0 2D 66 00` | `B8 01 00 00 00` | Sets the startup windowed-decision flag true when the windowed-capable path is available |
| Default GEFORCE_FX_POWER tweak on | `0x004CDD40` | `0x0CDD40` | `6A 00` | `6A 01` | Sets the `GEFORCE_FX_POWER` tweak registration default to enabled; `cardid.txt` can still override unless bypassed |
| Ignore cardid tweak override load call | `0x0052AF3F` | `0x12AF3F` | `E8 9C D7 FF FF` | `90 90 90 90 90` | Uses BEA.exe defaults directly by bypassing cardid parser/apply call |
| Install PATCHED version-overlay marker pointer | `0x0046316F` | `0x06416F` | `54 94 62 00` | `44 A4 5A 00` | Redirects bottom-left version text format pointer to the patch-owned cave payload when explicitly selected; one copied-game title/menu frame shows `V1.00 - PATCHED`, while broader overlay/gameplay paths remain unproven |
| Hidden companion: version overlay cave payload (`V%1d.%02d - PATCHED`) | `0x005AA444` | `0x1AA444` | `CC` x20 | ASCII payload bytes | Provides the opt-in visible diagnostic marker text |
| Optional: skip auto fullscreen toggle gate (**Experimental**) | `0x0052BB97` | `0x12BB97` | `75 20` | `EB 20` | Optional flow tweak to skip startup ToggleFullscreen gate |

Usage:
```bash
python3 patches/patch_display_mode_flow.py --path "D:\SafeCopy\BEA.exe" --verify
python3 patches/patch_display_mode_flow.py --path "D:\SafeCopy\BEA.exe" --allowed-root "D:\SafeCopy" --apply
python3 patches/patch_display_mode_flow.py --path "D:\SafeCopy\BEA.exe" --allowed-root "D:\SafeCopy" --apply --resolution-only
python3 patches/patch_display_mode_flow.py --path "D:\SafeCopy\BEA.exe" --allowed-root "D:\SafeCopy" --apply --windowed-only
python3 patches/patch_display_mode_flow.py --path "D:\SafeCopy\BEA.exe" --allowed-root "D:\SafeCopy" --apply --version-overlay
python3 patches/patch_display_mode_flow.py --path "D:\SafeCopy\BEA.exe" --allowed-root "D:\SafeCopy" --apply --skip-auto-toggle
python3 patches/patch_display_mode_flow.py --path "D:\SafeCopy\BEA.exe" --allowed-root "D:\SafeCopy" --restore
```

### Catalog/AppCore-only patches

These rows are bytes-checked by `patches/catalog/patches.v2.json` and the WinUI/AppCore patch engine, but are not selectable through `patch_display_mode_flow.py`.

| Patch | VA | File Offset | Before | After | Purpose |
|------|----|-------------|--------|-------|---------|
| Frontend clear-screen dark red preset | `0x00540F88` | `0x140F88` | `3F 1F 1F 00` | `1F 1F BF 00` | Changes the `CDXFrontEnd__RenderStart` clear-screen color immediate from source-backed dark blue to a dark red preset; one local safe-copy title-screen capture shows red clear-screen margins, while broader menu coverage remains pending |
| Frontend clear-screen dark green preset | `0x00540F88` | `0x140F88` | `3F 1F 1F 00` | `1F BF 1F 00` | Changes the same clear-screen immediate to a dark green preset; one local safe-copy title-screen capture shows green clear-screen margins, while broader menu coverage remains pending |
| Frontend clear-screen black preset | `0x00540F88` | `0x140F88` | `3F 1F 1F 00` | `00 00 00 00` | Changes the same clear-screen immediate to black; one local safe-copy title-screen capture shows black clear-screen margins, while broader menu coverage remains pending |
| Goodies gallery display flag override | `0x0045D7F4` | `0x05D7F4` | `E8 97 7C 00 00 F7 D8 1B C0` | `83 C4 04 83 C8 FF 90 90 90` | Skips the `IsCheatActive(0)` call, discards its already-pushed argument, and forces the `CFEPGoodies::Process` MALLOY-derived display flag path true for the copied executable; two bounded copied-game comparison pairs show selected Goodies-wall display-state changes (`To Unlock: Complete Tutorial` to `Unlocked! Hawk Winter`, and `To Unlock: Grade C on Blackout` to `Unlocked! Tatiana Kiralova`). A third patched copied-game run selected the displayed Tatiana Goodie and captured the character-art presentation page. This does not edit saves, permanently award goodies, force the `lat\\xEAte`/developer override, or prove FMV playback, 3D model viewing, or every Goodies entry |
| Experimental pause-key default O initializer | `0x005144CD` | `0x1144CD` | `01` | `18` | Changes the copied executable's `OptionsEntries__InitDefaultSingleBindingsTable` pause-row key argument candidate from scan `0x01` to scan `0x18` (`O`). Accepted exact-PID copied-runtime CDB proof shows copied byte `0x18`, live row 34 keyArg `0x18`, scoped `O` reaching `BUTTON_PAUSE`, and one pause/unpause pair in a bounded free-camera context; a later level-100 normal-gameplay proof shows `O` opens the pause menu and `ENTER` resumes from it. Second-`O` normal-gameplay unpause, broad pause/menu safety, gameplay safety, and parity remain unproven |
| Experimental Aurore free-camera gate bypass | `0x0046F83C` | `0x06F83C` | `0F 84 58 02 00 00` | `90 90 90 90 90 90` | NOPs the retail-only Aurore-inactive branch in `CGame::ReceiveButtonAction` so the existing debug button case can reach the free-camera toggle path; accepted copied-runtime CDB proof shows scoped `F` input reaches debug button `1`, the patched gate reaches `CGame__ToggleFreeCameraOn`, and a second tap restores the original camera pointer. Q-forward/Q-backward/Q-strafe-left/Q-strafe-right movement proofs and Q-yaw-left/Q-yaw-right/Q-pitch-up/Q-pitch-down orientation proofs are separate under the companion keyboard remap rows; control feel, joystick/analog coverage, pause/menu safety, gameplay safety, and parity remain pending |
| Experimental free-camera Q-forward hook plus hidden cave | Hook `0x0041A980`; cave `0x005A3A15` | Hook `0x01A980`; cave `0x1A3A15` | Hook `8B 44 24 08 81 EC C0 00 00 00`; cave `CC` x29 | Hook `E9 90 90 18 00 90 90 90 90 90`; cave maps button `31` to button `38`, replays the displaced stack allocation, and jumps back to `0x0041A98A` | Visible row `free_camera_keyboard_forward_q_hook` depends on `free_camera_aurore_gate_bypass` and hidden companion `free_camera_keyboard_forward_q_cave`; it conflicts with the other Q remap variants because all variants patch the same hook/cave bytes. Accepted copied-runtime CDB proof shows scoped `Q` reaches the hook/cave path 20 times, reads back post-cave button `38`, and produces 20 free-camera interpolation position deltas. This is one bounded movement path only, not full camera controls, gameplay safety, render parity, online/netcode, or no-noticeable-difference proof |
| Experimental free-camera Q-backward hook plus hidden cave | Hook `0x0041A980`; cave `0x005A3A15` | Hook `0x01A980`; cave `0x1A3A15` | Hook `8B 44 24 08 81 EC C0 00 00 00`; cave `CC` x29 | Hook `E9 90 90 18 00 90 90 90 90 90`; cave maps button `32` to button `39`, replays the displaced stack allocation, and jumps back to `0x0041A98A` | Visible row `free_camera_keyboard_backward_q_hook` depends on `free_camera_aurore_gate_bypass` and hidden companion `free_camera_keyboard_backward_q_cave`; it conflicts with the other Q remap variants because all variants patch the same hook/cave bytes. Accepted copied-runtime CDB proof shows scoped `Q` reaches the hook/cave path 21 times, reads back post-cave button `39`, and produces 21 free-camera interpolation position deltas. This is one bounded movement path only, not full camera controls, gameplay safety, render parity, online/netcode, or no-noticeable-difference proof |
| Experimental free-camera Q-strafe-left hook plus hidden cave | Hook `0x0041A980`; cave `0x005A3A15` | Hook `0x01A980`; cave `0x1A3A15` | Hook `8B 44 24 08 81 EC C0 00 00 00`; cave `CC` x29 | Hook `E9 90 90 18 00 90 90 90 90 90`; cave maps button `29` to button `40`, replays the displaced stack allocation, and jumps back to `0x0041A98A` | Visible row `free_camera_keyboard_strafe_left_q_hook` depends on `free_camera_aurore_gate_bypass` and hidden companion `free_camera_keyboard_strafe_left_q_cave`; it conflicts with the other Q remap variants because all variants patch the same hook/cave bytes. Accepted copied-runtime CDB proof shows scoped `Q` reaches the hook/cave path 32 times, reads back post-cave button `40`, and produces 32 free-camera interpolation position deltas. This is one bounded movement path only, not full camera controls, gameplay safety, render parity, online/netcode, or no-noticeable-difference proof |
| Experimental free-camera Q-strafe-right hook plus hidden cave | Hook `0x0041A980`; cave `0x005A3A15` | Hook `0x01A980`; cave `0x1A3A15` | Hook `8B 44 24 08 81 EC C0 00 00 00`; cave `CC` x29 | Hook `E9 90 90 18 00 90 90 90 90 90`; cave maps button `30` to button `41`, replays the displaced stack allocation, and jumps back to `0x0041A98A` | Visible row `free_camera_keyboard_strafe_right_q_hook` depends on `free_camera_aurore_gate_bypass` and hidden companion `free_camera_keyboard_strafe_right_q_cave`; it conflicts with the other Q remap variants because all variants patch the same hook/cave bytes. Accepted copied-runtime CDB proof shows scoped `Q` reaches the hook/cave path 31 times, reads back post-cave button `41`, and produces 31 free-camera interpolation position deltas. This is one bounded movement path only, not full camera controls, gameplay safety, render parity, online/netcode, or no-noticeable-difference proof |
| Experimental free-camera Q-yaw-left hook plus hidden cave | Hook `0x0041A980`; cave `0x005A3A15` | Hook `0x01A980`; cave `0x1A3A15` | Hook `8B 44 24 08 81 EC C0 00 00 00`; cave `CC` x29 | Hook `E9 90 90 18 00 90 90 90 90 90`; cave maps button `25` to button `36`, replays the displaced stack allocation, and jumps back to `0x0041A98A` | Visible row `free_camera_keyboard_yaw_left_q_hook` depends on `free_camera_aurore_gate_bypass` and hidden companion `free_camera_keyboard_yaw_left_q_cave`; it conflicts with the other Q remap variants because all variants patch the same hook/cave bytes. Accepted copied-runtime CDB proof shows scoped `Q` reaches the hook/cave path 33 times, reads back post-cave button `36`, and produces 33 free-camera interpolation orientation deltas. This is one bounded orientation path only, not full camera controls, gameplay safety, render parity, online/netcode, or no-noticeable-difference proof |
| Experimental free-camera Q-yaw-right hook plus hidden cave | Hook `0x0041A980`; cave `0x005A3A15` | Hook `0x01A980`; cave `0x1A3A15` | Hook `8B 44 24 08 81 EC C0 00 00 00`; cave `CC` x29 | Hook `E9 90 90 18 00 90 90 90 90 90`; cave maps button `27` to button `37`, replays the displaced stack allocation, and jumps back to `0x0041A98A` | Visible row `free_camera_keyboard_yaw_right_q_hook` depends on `free_camera_aurore_gate_bypass` and hidden companion `free_camera_keyboard_yaw_right_q_cave`; it conflicts with the other Q remap variants because all variants patch the same hook/cave bytes. Accepted copied-runtime CDB proof shows scoped `Q` reaches the hook/cave path 32 times, reads back post-cave button `37`, and produces 32 free-camera interpolation orientation deltas. This is one bounded orientation path only, not full camera controls, gameplay safety, render parity, online/netcode, or no-noticeable-difference proof |
| Experimental free-camera Q-pitch-up hook plus hidden cave | Hook `0x0041A980`; cave `0x005A3A15` | Hook `0x01A980`; cave `0x1A3A15` | Hook `8B 44 24 08 81 EC C0 00 00 00`; cave `CC` x29 | Hook `E9 90 90 18 00 90 90 90 90 90`; cave maps button `26` to button `34`, replays the displaced stack allocation, and jumps back to `0x0041A98A` | Visible row `free_camera_keyboard_pitch_up_q_hook` depends on `free_camera_aurore_gate_bypass` and hidden companion `free_camera_keyboard_pitch_up_q_cave`; it conflicts with the other Q remap variants because all variants patch the same hook/cave bytes. Accepted copied-runtime CDB proof shows scoped `Q` reaches the hook/cave path 31 times, reads back post-cave button `34`, and produces 31 free-camera interpolation orientation deltas. This is one bounded orientation path only, not full camera controls, user-facing camera feel, joystick/analog coverage, gameplay safety, render parity, online/netcode, or no-noticeable-difference proof |
| Experimental free-camera Q-pitch-down hook plus hidden cave | Hook `0x0041A980`; cave `0x005A3A15` | Hook `0x01A980`; cave `0x1A3A15` | Hook `8B 44 24 08 81 EC C0 00 00 00`; cave `CC` x29 | Hook `E9 90 90 18 00 90 90 90 90 90`; cave maps button `28` to button `35`, replays the displaced stack allocation, and jumps back to `0x0041A98A` | Visible row `free_camera_keyboard_pitch_down_q_hook` depends on `free_camera_aurore_gate_bypass` and hidden companion `free_camera_keyboard_pitch_down_q_cave`; it conflicts with the other Q remap variants because all variants patch the same hook/cave bytes. Accepted copied-runtime CDB proof shows scoped `Q` reaches the hook/cave path 33 times, reads back post-cave button `35`, and produces 33 free-camera interpolation orientation deltas. This is one bounded orientation path only, not full camera controls, user-facing camera feel, joystick/analog coverage, gameplay safety, render parity, online/netcode, or no-noticeable-difference proof |

### patch_devmode_goodies_logic_fix.py (Dev-Mode Workaround Only)

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
| Maladim | 3 | God mode menu toggle | Steam build exposes God OFF/God ON; God ON blocks normal combat damage in current evidence |

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
| 3 | **Maladim** | God mode toggle | Steam build exposes God OFF/God ON; God ON blocks normal combat damage in current evidence |
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
| `0x004714e3` | CGame__DrawGameStuff | Game overlay/status path |
| `0x004715ef` | CGame__DrawGameStuff | Game overlay/status path |
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

### Historical private binaries (not public payload, not patch targets)

| File | MD5 | SHA256 | Notes |
|------|-----|--------|-------|
| `BEA_Widescreen.exe` | `b2025e385b8da8d19656b538e1268fc4` | `67994e5f5f418cca2ed253ab643112ac3a82ea1647e8172027eb9c9cc7b37f61` | Historical private specimen; excluded from public candidates; offsets may differ. |
| `BEA.exe.gzf` | n/a | n/a | Historical private Ghidra packed database; excluded from public candidates and not an executable. |

## Safety

- Backup filenames differ by tool:
  - `patch_display_mode_flow.py` -> `BEA.exe.original.backup`
  - `patch_devmode_goodies_logic_fix.py` -> `BEA.exe.backup`
- Binary Patches UI restore flow uses `BEA.exe.original.backup`
- Current exposed patch rows are offline copied-game experiments only; no networked, matchmaking, anti-cheat, or public-server safety posture is proven.
- Always patch a copied executable or playable copied game folder, never the installed/original `BEA.exe`.
- WinUI/AppCore apply/restore requires an app-owned Windowed & Mods patch workspace and rejects direct mutation outside that root, Program Files targets, reparse-point targets, and hardlinked targets.
- Standalone Python scripts are reference helpers. Mutating modes require `--allowed-root` for the copied-target workspace, a generated playable copied-game manifest, backup hash sidecars, and reparse/hardlink/patch-verification guards; prefer the WinUI/AppCore path for player-facing patching.
- Prefer a SHA-256 match to the canonical clean Steam retail specimen before patching. If the copied local executable is already patched, the WinUI lane treats selected already-patched rows as a no-op only when trusted clean backup provenance exists or an explicit byte-layout-only lab/proof lane is armed.

## Discovery

Discovered via Ghidra analysis of BEA.exe (December 2025) as part of the Onslaught Career Editor project. See `reverse-engineering/` documentation for full technical details.
