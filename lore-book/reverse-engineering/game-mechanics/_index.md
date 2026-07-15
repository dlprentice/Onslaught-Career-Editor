# Game Mechanics Documentation

> Runtime behavior, cheat systems, and gameplay mechanics

## Overview

This folder documents Battle Engine Aquila's runtime mechanics (things that happen during gameplay). Key finding: god mode/invincibility is **runtime state** and cheat-gated via save-name substring checks; the Steam build also persists a pause-menu toggle state (`g_bGodModeEnabled` at file `0x2496` / CCareer `+0x2494` in the true dword view), but that alone does not imply a per-player persisted invincibility flag.

After Ghidra function-quality closure (`6113/6113 = 100.00%`, Wave900), **Wave902** (`save-options-static-review-wave902`) documented a static review slice for retail save/options/career, including persisted `g_bGodModeEnabled`, `CCareer__Load` / `CCareer__Save`, and pause-menu persistence via `CPauseMenu__ResumeGameAndPersistOptions`. See [../binary-analysis/save-options-static-review-2026-05-26.md](../binary-analysis/save-options-static-review-2026-05-26.md) and [../save-file/_index.md](../save-file/_index.md). **Wave907** static-coherently reviewed the broader frontend/input/game-loop core (`CGame__MainLoop`, `CFrontEnd__Run`, `CPauseMenu__ResumeGameAndPersistOptions`); cheat string tables, `IsCheatActive`, and live damage/menu behavior still need runtime proof in this folder.

## Documents

| Document | Description |
|----------|-------------|
| [god-mode.md](god-mode.md) | God mode investigation (source/internal B4K42 path, Steam/retail Maladim status, runtime toggle behavior) |
| [cheat-codes.md](cheat-codes.md) | Known cheats, string search results, activation flow |

## Rebuild-grade motion / combat measurement (active)

Human front door: [campaign-scalar-status.md](campaign-scalar-status.md).

| Document | Status |
|----------|--------|
| [walker-forward-scalar-response-v2.md](walker-forward-scalar-response-v2.md) | dual-accepted → Core |
| [jet-forward-scalar-response-v1.md](jet-forward-scalar-response-v1.md) | dual-accepted → Core |
| [walker-turn-yaw-scalar-response-v1.md](walker-turn-yaw-scalar-response-v1.md) | dual-accepted → Core LookX |
| [walker-strafe-lateral-scalar-response-v1.md](walker-strafe-lateral-scalar-response-v1.md) | dual-accepted → Core |
| [walker-transform-morph-timing-v1.md](walker-transform-morph-timing-v1.md) | dual-accepted → Core |
| [camera-look-rate-measurement-plan.md](camera-look-rate-measurement-plan.md) | scaffold |
| [energy-rate-scalar-measurement-plan.md](energy-rate-scalar-measurement-plan.md) | jet drain dual-accepted; walker regen pending |
| [jet-energy-drain-scalar-response-v1.md](jet-energy-drain-scalar-response-v1.md) | dual-accepted energy-p02 |
| [jet-energy-drain-retail-to-core-translation-policy.md](jet-energy-drain-retail-to-core-translation-policy.md) | accepted |
| [energy-live-dual-accept-checklist.md](energy-live-dual-accept-checklist.md) | live dual-accept operator checklist |
| [energy-retail-to-core-translation-policy.md](energy-retail-to-core-translation-policy.md) | partial — jet drain accepted; walker regen provisional |
| [shield-rate-scalar-measurement-plan.md](shield-rate-scalar-measurement-plan.md) | offset hyp BE+0x100; live pending |
| [shield-retail-to-core-translation-policy.md](shield-retail-to-core-translation-policy.md) | draft blocked on dual-accept |
| [fire-cooldown-scalar-measurement-plan.md](fire-cooldown-scalar-measurement-plan.md) | scaffold + energy-drop edges |
| [fire-cooldown-retail-to-core-translation-policy.md](fire-cooldown-retail-to-core-translation-policy.md) | draft blocked on dual-accept |
| [projectile-speed-scalar-measurement-plan.md](projectile-speed-scalar-measurement-plan.md) | scaffold |
| [projectile-speed-retail-to-core-translation-policy.md](projectile-speed-retail-to-core-translation-policy.md) | draft blocked on dual-accept |
| [coast-friction-release-measurement-plan.md](coast-friction-release-measurement-plan.md) | scaffold M1.6 |
| [coast-friction-retail-to-core-translation-policy.md](coast-friction-retail-to-core-translation-policy.md) | draft blocked on dual-accept |
| [runtime-proof-lab-retention.md](runtime-proof-lab-retention.md) | lab hygiene |

Machine-checkable public-safe BattleEngine source-anchor coverage is recorded at `release/readiness/battleengine_logic_coverage_2026-05-06.md`. It is read-only source/docs evidence, not Steam retail binary identity proof.

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

**PC Port Note:** The Steam build uses XOR-decrypted cheat strings checked against the save name (`MALLOY`, `TURKEY`, `V3R5IOF`, `Maladim`, `Aurore`, `latête`). `MALLOY`, `TURKEY`, and `Maladim` have live Steam-build behavior evidence; `V3R5IOF` and some exact behavior boundaries remain open. See `cheat-codes.md` and `god-mode.md`. Treat the historical source-only table below as archival context, not current retail guidance.

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
| `Maladim` | God mode toggle | Confirmed: `God OFF` / `God ON` under `Controller Options`; blocks normal combat damage |
| `Aurore` | Free camera debug toggle | ✅ Verified in binary (gates free-cam button) |
| `lat\\xEAte` (may render `latête`) | Goodie UI override | ✅ Verified in binary (gates/overrides goodie display) |

## See Also

- [../binary-analysis/save-options-static-review-2026-05-26.md](../binary-analysis/save-options-static-review-2026-05-26.md) - Wave902 static review slice for save/options/career (`g_bGodModeEnabled` at `0x2496`; not runtime proof)
- [../binary-analysis/frontend-input-game-loop-static-review-2026-05-26.md](../binary-analysis/frontend-input-game-loop-static-review-2026-05-26.md) - Wave907 frontend/input/game-loop static review
- [../save-file/](../save-file/) - Save file format (where cheats write data)
- [../source-code/gameplay/_index.md](../source-code/gameplay/_index.md) - Source code analysis
- [CURRENT_CAPABILITIES.md](/CURRENT_CAPABILITIES.md) - Current app surface and supported workflows

---

*Last updated: 2026-05-26*
