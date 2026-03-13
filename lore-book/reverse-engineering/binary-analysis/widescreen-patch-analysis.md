# Widescreen Patch Analysis

> Analysis of BEA_Widescreen.exe modifications to understand resolution/aspect ratio patching
> Generated: December 2025
> Last updated: 2026-03-01

## Summary

| Property | Value |
|----------|-------|
| Original File | BEA.exe (Steam) |
| Original SHA256 | `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750` |
| Patched File | BEA_Widescreen.exe |
| Patched SHA256 | `67994E5F5F418CCA2ED253AB643112AC3A82EA1647E8172027EB9C9CC7B37F61` |
| File Size | 2,506,752 bytes (unchanged) |
| Total Changed Bytes | 191 |
| Change Regions | 28 |

Canonical machine-readable region table:
- [`widescreen-diff-regions-28.tsv`](./widescreen-diff-regions-28.tsv)
- Contains all 28 regions with file offsets, VAs, before/after bytes, owner attribution (`owner_fn`), evidence pointers (`evidence_refs`), and current behavior classification.
- Unresolved subset tracker: [`widescreen-diff-unresolved.md`](./widescreen-diff-unresolved.md) (bounded unknown queue; currently empty).

## Patching Technique

The widescreen patch uses a classic **code cave** technique:

1. **Hook Points**: Original instructions are replaced with 5-byte JMP instructions
2. **Code Caves**: New code is injected into unused padding areas (originally 0xCC INT3 bytes)
3. **Trampolines**: After executing new code, jumps back to continue original flow
4. **Data Storage**: New float constants for aspect ratio calculations stored in data section

## Patch Regions

### Region 1: 0x0001B087 (3 bytes)
- **VA**: 0x0041B087
- **Change**: `C4 8B 5D` → `F0 4F 9D`
- **Purpose**: Data reference update (points to new aspect ratio constant)

### Region 2: 0x000506CE (5 bytes) - MAIN HOOK
- **VA**: 0x004506CE
- **Original**: `68 00 00 40 3F` (PUSH 0x3F400000 = 0.75f)
- **Patched**: `E9 5F 78 18 00` (JMP 0x005D7F32)
- **Purpose**: Hook into resolution setup, jumps to code cave
- **Note**: 0.75f is 3:4 aspect ratio (4:3 inverted)

### Region 3: 0x00129696 (1 byte)
- **VA**: 0x00529696
- **Change**: `CC` → `00`
- **Purpose**: Neutralizes the non-4:3 reject gate in `BuildDeviceList` (functional behavior patch; this byte was formerly INT3 padding).

### Region 4: 0x0012B156 (6 bytes)
- **VA**: 0x0052B156
- **Original**: `D9 05 F0 4A 5E 00` (FLD dword ptr [0x5E4AF0])
- **Patched**: `E9 07 CD 0A 00 90` (JMP + NOP)
- **Purpose**: Hook aspect ratio loading

### Region 5: 0x0012B200 (5 bytes)
- **VA**: 0x0052B200
- **Original**: `E8 3B 65 F1 FF` (CALL)
- **Patched**: `E9 98 CD 0A 00` (JMP)
- **Purpose**: Another aspect ratio hook

### Regions 6-7: Data Reference Updates
- **VA**: 0x0052B983, 0x0052C790
- **Change**: `F0 4A 5E` → `F8 4F 9D`
- **Purpose**: Update pointers from old aspect constant to new

### Regions 8-11: FPU Instruction Hooks
- **Region 8 (0x0053E32F)**: replaces `mov edx,[ecx]; call [edx+0x10]` with `jmp 0x005D7FD1`.
  - Cave `0x005D7FD1` replays the original vcall, applies `fmul [0x009D4FF4]`, then jumps back to `0x0053E334`.
- **Region 9 (0x0053F3B7)**: replaces `fld [0x00888A40]` with `jmp 0x005A3955`.
  - Cave `0x005A3955` executes `fld [0x005DB398]; fdiv [0x009D4FF8]`, then jumps back to `0x0053F3BD`.
- **Region 10 (0x00541B59)**: replaces `fld [esp+0xC4]` start with `jmp 0x005D7FE1`.
  - Cave `0x005D7FE1` computes an adjusted value with ratio globals and rejoins via `0x005D7DB5 -> 0x005D7DE6 -> 0x00541B60`.
- **Region 11 (0x00541B5E)**: companion NOP packing for region 10 trampoline (`0x90 0x90`).

### Region 12: Code Cave Block (0x001A3955 - 0x001A3965)
- **VA**: 0x005A3955 - 0x005A3965
- **Size**: 17 bytes
- **Location**: Former INT3 padding block used as FPU cave bridge for widescreen path

### Regions 13-28: Code Cave Cluster (0x001D7DB5 - 0x001D7FFD)
- **VA**: 0x005D7DB5 - 0x005D7FFD
- **Size**: ~600 bytes of new code
- **Location**: Padding area after .text section code
- **Contains**:
  - Aspect ratio calculation routines
  - Width/height ratio computation
  - FOV (field of view) adjustments
  - Jump-back trampolines

## Key Addresses

### Original Aspect Ratio Constant
- **Address**: 0x005E4AF0 (file offset 0x1E4AF0)
- **Value**: 0.75f (3:4 = 4:3 aspect inverted)

### New Aspect Ratio Storage
- **Address**: 0x009D4FF0, 0x009D4FF4, 0x009D4FF8
- **Purpose**: Runtime-calculated aspect ratios for widescreen
- **Note**: These addresses are in .bss/uninitialized data section

### Config String
- **Address**: 0x0064BE10
- **Value**: `"ALLOW_WIDESCREEN_MODES"`
- **Purpose**: Config file option to enable widescreen resolutions

## Code Cave Disassembly (Partial)

```asm
; At 0x005D7F32 (target of hook at 0x4506CE)
005D7F32: FF35 F04F9D00    PUSH dword ptr [0x9D4FF0]  ; Push calculated aspect
005D7F38: E9 9687E7FF      JMP 0x004506D3             ; Return to original code

; At 0x005D7F9D (aspect ratio calculation)
005D7F9D: DB85 5C2E0300    FILD dword ptr [EBP+0x32E5C]  ; Load screen width
005D7FA3: DA B5 582E0300   FIDIV dword ptr [EBP+0x32E58] ; Divide by height
005D7FA9: D915 F04F9D00    FST dword ptr [0x9D4FF0]      ; Store aspect ratio
005D7FAF: D83D C48B5D00    FDIVR dword ptr [0x5D8BC4]    ; Divide by reference
005D7FB5: D915 F44F9D00    FST dword ptr [0x9D4FF4]      ; Store adjusted
; ... more FPU operations for FOV correction
```

## Windowed Mode Analysis

### Guard Flag Location
- **Address**: `DAT_00662f3e` (VA 0x00662F3E, file offset 0x262F3E)
- **Historical baseline reports**: 0x00 (disabled in some unpatched binaries)
- **Value in current repo `game/BEA.exe`**: 0x01
- **Value in current repo `BEA_Widescreen.exe`**: 0x01

### CLIParams Check (from decompilation)
```c
if ((DAT_00662f3e != '\0') &&
   (iVar3 = stricmp(pcVar9, s__forcewindowed_006244a0), iVar3 == 0)) {
  extraout_ECX[0xe] = 1;  // Reached when DAT_00662f3e != 0
}
```

The check at file offset 0x24150:
```asm
00424150: A0 3E2F6600      MOV AL, byte ptr [0x662F3E]  ; Load guard flag
00424155: 84 C0            TEST AL, AL                   ; Check if non-zero
00424157: 74 15            JZ +0x15                      ; Skip if zero (taken only when DAT_00662f3e == 0x00)
```

When the flag is `0x00`, the JZ (jump if zero) is taken and `-forcewindowed` is not processed.
In current repo binaries (`0x01`), that guard no longer blocks CLI parsing.

### Guard-Byte Normalization for Variants Where 0x262F3E == 0x00

Canonical operational guidance is maintained in [windowed-mode-analysis.md](windowed-mode-analysis.md) to avoid drift.

Quick summary:
- If guard byte `0x262F3E` is `0x00`, set it to `0x01` to allow `-forcewindowed` parsing.
- Optional branch tweak at `0x24157` (`74 15` pathway) can bypass the guard gate but does not by itself guarantee forced windowed behavior in every environment.
- Wrapper fallback (`DxWnd` / `dgVoodoo2`) can still be needed on some setups.

## Technical Notes

1. **Same file size**: Patch reuses existing padding, no section expansion needed
2. **Code caves**: Uses 0xCC (INT3) padding bytes common in MSVC-compiled code
3. **FPU heavy**: Aspect ratio math uses x87 FPU instructions (D8-DF opcodes)
4. **Config integration**: Reads `ALLOW_WIDESCREEN_MODES` from game config
5. **Runtime calculation**: Aspect ratio computed from actual screen dimensions

## Related Files

- [CLIParams.cpp.md](functions/CLIParams.cpp/_index.md) - Command-line parameter handling
- [executable-analysis.md](executable-analysis.md) - PE structure details
- [../game-mechanics/cheat-codes.md](../game-mechanics/cheat-codes.md) - Other hidden features

---

*Analysis performed December 2025; updated with 28-region canonical attribution and behavior clarifications on 2026-03-01.*
*Binary diff via Python, disassembly via Ghidra + GhydraMCP*
