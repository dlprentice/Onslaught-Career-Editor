# Binary Analysis Documentation

> Executable analysis, Ghidra findings, and disassembly notes

## Overview

This folder contains documentation from analyzing the `BEA.exe` executable using Ghidra and other RE tools. Focus is on understanding runtime behavior that can't be determined from source code alone.

## Verified Binary

**Canonical retail analysis is rooted in the unmodified Steam release of `BEA.exe`.** Some documents in this folder also discuss derived patch targets (`BEA_Widescreen.exe`) or the byte-verified patches shipped by this repo, but the Steam hash below remains the base authority for retail behavior claims.

| Property | Value |
|----------|-------|
| File | `BEA.exe` (Steam version) |
| Size | 2,506,752 bytes |
| MD5 | `3b456964020070efe696d2cc09464a55` |
| SHA256 | `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750` |
| Platform | x86 32-bit Windows PE |
| Base Address | 0x00400000 |

If your BEA.exe has a different hash, it may be modified or from a different release.

### Other binaries in this repo (reference/diff targets)

| File | Purpose | Notes |
|------|---------|-------|
| `BEA_Widescreen.exe` | Community widescreen patch | Used as a diff target for widescreen attribution; not the canonical base binary for retail hash analysis. |
| `BEA.exe.gzf` | Ghidra packed database | **Not** an executable (Ghidra cache artifact). |

## Documents

| Document | Description |
|----------|-------------|
| [executable-analysis.md](executable-analysis.md) | PE metadata, DLL dependencies, source file paths |
| [GHIDRA-REFERENCE.md](GHIDRA-REFERENCE.md) | Ghidra workspace reference, project notes |
| [string-locations-index.md](functions/string-locations-index.md) | Historical Phase-1 string dump snapshot (legacy 196-address list) |
| [functions/](functions/_index.md) | **Per-source-file function mappings** (see `functions/_index.md` for current directory totals) |
| [deep-validation-status.md](deep-validation-status.md) | Static RE gate status for ownership/type/behavior contract completion |
| [high-impact-subsystem-contracts.md](high-impact-subsystem-contracts.md) | Pass-2 contract coverage for remaining high-impact subsystem bucket |
| [high-impact-call-chain-appendix.md](high-impact-call-chain-appendix.md) | Call-chain depth appendix (frontend/world/text side effects + signature snapshot) |
| [display-modernization-plan.md](display-modernization-plan.md) | Post-validation display modernization decision matrix and test plan |
| [extra-graphics-feature-gate-patch.md](extra-graphics-feature-gate-patch.md) | Retail cardid-gate default patch evidence (`0x0CDD40: 6A 00 -> 6A 01`) |
| [version-overlay-patch.md](version-overlay-patch.md) | Companion patch note for the shipped `V1.00 - PATCHED` watermark behavior |

## Function Mappings Structure

Function documentation is organized by source file in `functions/`:

```
functions/
  _index.md           # Master index (counts updated in index)
  globals.md          # Global variables
  Career.cpp/         # 23 functions - save/load, grades, kills
  FEPSaveGame.cpp/    # IsCheatActive, cheat system
  DXSnow.cpp.md       # Snow particle system, cvars
  MissionScript/      # Bytecode VM, 27 opcodes
  ...                 # Many source-file directories; see functions/_index.md for current totals
```

## Key Discoveries

| Address | Function | Purpose |
|---------|----------|---------|
| 0x0041b7c0 | CCareer__Blank | Career blank/init, graph reset, and adjacent settings-field initialization |
| 0x00465490 | IsCheatActive | XOR-decrypted cheat code checking |
| 0x004cde60 | PauseMenu__Init | God mode toggle display |
| 0x00423bc0 | CLIParams__ParseCommandLine | CLI params including guarded -forcewindowed |
| 0x0055515e | CDXSnow__Init | Snow particle system, 4 cvars |
| 0x00539b00 | CScriptObjectCode__Run | Mission script bytecode VM main loop |

## Phase 1 Completion Stats (Archived Milestone: 2026-02-02)

These numbers are archived milestone values and are not current coverage totals. For current totals/coverage, use:
- `reverse-engineering/binary-analysis/functions/FUNCTION_COVERAGE_STATE.md`
- `reverse-engineering/binary-analysis/_index.md`

- **60 per-function docs** created (`Class__Method` format)
- **36 per-source docs** created (top-level `.cpp.md` files)
- **123 source-file directories** documented
- **228 markdown files** in binary-analysis
- **196 debug path strings** indexed
- **27 bytecode opcodes** documented (mission scripting)
- **272+ physics script statements** catalogued

## Tools Used

- **Ghidra 12.0.3** - NSA reverse engineering framework (active workstation build)
- **GhydraMCP v2.2.0-rc.2** - MCP bridge/plugin used for serialized RE workflows
- **x64dbg** - Dynamic analysis (when needed)

## See Also

- [../source-code/](../source-code/) - Stuart's source code (reference for naming)
- [CURRENT_CAPABILITIES.md](/CURRENT_CAPABILITIES.md) - Current app surface and supported workflows
- [../game-assets/game-folder-analysis.md](../game-assets/game-folder-analysis.md) - Game installation layout and asset-loading context

---

*Last updated: 2026-03-05*
