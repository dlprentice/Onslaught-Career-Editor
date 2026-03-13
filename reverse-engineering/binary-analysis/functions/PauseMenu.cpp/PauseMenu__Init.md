# PauseMenu__Init

> Address: 0x004cde60 | Source: PauseMenu.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (read-back verified in mutation snapshots)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

Pause menu constructor/initializer. Sets up the pause menu UI and conditionally adds the god mode toggle option based on cheat activation.

## Signature
```c
// Live read-back signature (wave217 snapshot)
void __thiscall PauseMenu__Init(void * this);
```

## Signature Evidence

- `scratch/deep_semantic_tail_2026-02-27/all_after_wave217.tsv` line 1804: `void __thiscall PauseMenu__Init(void * this)`.
- Same snapshot line 1820 provides adjacent persistence helper signature: `void __fastcall CPauseMenu__ResumeGameAndPersistOptions(void * param_1)`.

## God Mode Toggle

### Key Code Location: 0x004ce328

At this address, the code uses `g_bGodModeEnabled` to display the current god mode toggle state **once the toggle is visible**:

```c
// Pseudocode from Ghidra
if (IsCheatActive(3)) {  // 3 = "Maladim" cheat
    // Add god mode toggle to menu
    bool godModeEnabled = g_bGodModeEnabled;
    AddToggleOption("God Mode", godModeEnabled);
}
```

### Memory Layout

| File Offset | CCareer Offset | Field |
|-------------|----------------|-------|
| 0x2496 | 0x2494 | g_bGodModeEnabled (pause-menu toggle state) |
| 0x249A | 0x2498 | (unused/padding) |
| 0x249E | 0x249C | Invert Y (Flight/Jet) (P1) |
| 0x24A2 | 0x24A0 | Invert Y (Flight/Jet) (P2) |
| 0x24A6 | 0x24A4 | Invert Y (Walker) (P1) |
| 0x24AA | 0x24A8 | Invert Y (Walker) (P2) |

Note: File offsets are CCareer offsets + 2 bytes (16-bit version word at file offset 0x0000; CCareer dump begins at file+0x0002).

## Cheat Activation & Gating

The god mode toggle only appears when:
1. `IsCheatActive(3)` returns true
2. This requires the save game NAME to contain "Maladim" (PC port) or "B4K42" (source/internal)

**Clarification:** `IsCheatActive(3)` gates the **visibility** of the menu option; `g_bGodModeEnabled` controls the current state shown by the toggle label. User testing on the Steam build shows **no visible effect** for Maladim so far.

## Persistence Chain (Adjacent Pause Flow)

`PauseMenu__Init` controls menu construction and cheat-gated toggle visibility. Actual save/options persistence on resume/exit runs through:

1. `CPauseMenu__ResumeGameAndPersistOptions` (`0x004d06e0`)
2. `CCareer__Save`
3. Optional `PCPlatform__WriteSaveFile` slot write
4. `CFEPOptions__WriteDefaultOptionsFile` (`defaultoptions.bea` update)

See:
- `CPauseMenu__ResumeGameAndPersistOptions.md`
- `../../high-impact-call-chain-appendix.md`
- `../Career.cpp/CCareer__Save.md`

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Critical for understanding god mode UI mechanism
- `0x004ce328` is an instruction inside `PauseMenu__Init` (not a function entry point): `CMP dword ptr [g_bGodModeEnabled], 1`
