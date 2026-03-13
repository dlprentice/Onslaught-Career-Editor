# Game Mechanics Documentation

> Runtime behavior, cheat systems, and gameplay mechanics

## Overview

This folder documents Battle Engine Aquila's runtime mechanics (things that happen during gameplay). Key finding: god mode/invincibility is **runtime state** and cheat-gated via save-name substring checks; the Steam build also persists a pause-menu toggle state (`g_bGodModeEnabled`), but that alone does not imply a per-player persisted invincibility flag.

## Documents

| Document | Description |
|----------|-------------|
| [god-mode.md](god-mode.md) | God mode investigation (source/internal B4K42 path, Steam/retail Maladim status, runtime toggle behavior) |
| [cheat-codes.md](cheat-codes.md) | Known cheats, string search results, activation flow |

## Key Discovery: Save-Name Cheat Gating (Build-Specific Codes)

From `FEPSaveGame.cpp` source analysis, cheats use **substring matching**:
```cpp
// Cheat codes checked via strstr() - can appear ANYWHERE in save name
if (strstr(saveName, "B4K42") != NULL) {
    // God mode enabled at runtime
}
```

Cheat activation uses save-name substring checks (`strstr`) in both builds.
- Internal/source example: `B4K42`
- Steam/retail codes: `MALLOY`, `TURKEY`, `V3R5IOF`, `Maladim`, `Aurore`, `lat\\xEAte` (may render as `latête`)

For retail behavior and app-facing validation, use the Steam code set. This is why save patching per-player god flags does not reliably enable single-player invincibility in the Steam build.

**PC Port Note:** The Steam build uses XOR-decrypted cheat strings checked against the save name (`MALLOY`, `TURKEY`, `V3R5IOF`, `Maladim`, `Aurore`, `latête`). Some effects are still unconfirmed in user testing; see `cheat-codes.md`. Treat the historical source-only table below as archival context, not current retail guidance.

## Historical Source/Internal Cheat Codes (Not For Steam/Retail Workflows)

| Code | Effect | Mechanism |
|------|--------|-----------|
| `B4K42` | God mode | Runtime name check (strstr) |
| `!EVAH!` | All missions | Runtime name check (strstr) |
| `105770Y2` | All goodies | Runtime name check (strstr) |
| `V3R5ION` | Display version | Source/internal cheat-table string (index 2); effect unverified in retail/Steam |

## Known Cheat Codes (PC Port / Steam)

| Code | Effect | Status |
|------|--------|--------|
| `MALLOY` | All goodies unlocked | ✅ Works (Dec 2025) |
| `TURKEY` | All missions unlocked | ✅ Works (Dec 2025) |
| `V3R5IOF` | Version display | ⚠️ Decoded from BEA.exe; no call sites found yet (needs in-game confirmation) |
| `Maladim` | God mode toggle | ❓ No visible effect (needs investigation) |
| `Aurore` | Free camera debug toggle | ✅ Verified in binary (gates free-cam button) |
| `lat\\xEAte` (may render `latête`) | Goodie UI override | ✅ Verified in binary (gates/overrides goodie display) |

## See Also

- [../save-file/](../save-file/) - Save file format (where cheats write data)
- [../source-code/gameplay/_index.md](../source-code/gameplay/_index.md) - Source code analysis
- [CURRENT_CAPABILITIES.md](/CURRENT_CAPABILITIES.md) - Current app surface and supported workflows

---

*Last updated: February 2026*
