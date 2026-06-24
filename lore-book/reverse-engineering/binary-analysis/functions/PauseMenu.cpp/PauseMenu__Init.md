# PauseMenu__Init

> Address: 0x004cde60 | Source: PauseMenu.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (read-back verified in mutation snapshots)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

Pause menu constructor/initializer. Sets up the pause menu UI, including the later `Controller Options` surface where the cheat-gated god toggle is exposed in the Steam build.

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

At this address, the code uses `g_bGodModeEnabled` to display the current god-mode toggle state **once the cheat-gated controller-options item is visible**:

```c
// Pseudocode from Ghidra
if (IsCheatActive(3)) {  // 3 = "Maladim" cheat
    // Add a controller-options toggle item
    bool godModeEnabled = g_bGodModeEnabled;
    AddToggleOption("God OFF" / "God ON", godModeEnabled);
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

**Clarification:** `IsCheatActive(3)` gates the **visibility** of the menu option; `g_bGodModeEnabled` controls the current state shown by the toggle label. Live Steam-build testing on 2026-03-15 confirmed that the visible item appears under `Controller Options` as `God OFF` / `God ON`, not as a new top-level root pause-menu entry. A later 2026-03-29 gameplay retest confirmed that toggling this item changes real combat-damage behavior, although the exact shield/hull/environmental boundary still belongs in [god-mode.md](../../../game-mechanics/god-mode.md).

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
- Positive-case `Maladim` runtime confirmation is preserved in `subagents/2026-03-15-runtime-maladim-wave2/session-notes.md`
- Gameplay-effect follow-up is preserved in `subagents/2026-03-29-runtime-maladim-wave3/session-notes.md`
