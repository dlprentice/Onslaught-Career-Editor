# Active Goal Baton

Status: **ACTIVE** (full reconstruction campaign)  
Last updated: 2026-07-14  
Integration tip: `0cbabf39`

## Closed ledger (this slice)

| Slice | Result |
|-------|--------|
| **M2-energy-live-dual-accept** | **ADVANCEMENT** pair `energy-p02`; v1 contract; policy accepted; `JetEnergyDrainPerTick=17` |

## Current Slice

**ID:** `M2-shield-live-dual-accept`  
**Objective:** Receipt-bound walker shield regen dual-accept at BE+0x100
(offline scaffold/pair envelope ready). Measurement-before-Core; no inventing
from source. Campaign ACTIVE.

## Resume (Codex handoff)

- **Tip SHA:** `0cbabf39`
- **Closed:** M2-energy-live-dual-accept ADVANCEMENT
- **Validation:** `npm run test:rebuild-core` (51); `test:rebuild-client` (73); `npm run test:battleengine-scalar-contract-regression` PASS (6 contracts incl. jet-energy-drain v1 signed rates); energy scaffold; `test:docsync` PASS
- **Paths:** public energy v1/policy/Core 17 + goldens; regression test signed-rate fix; index status partial jet-accepted
- **Codex owns next:** `M2-shield-live-dual-accept` only
- **Confirm:** Steam/original BEA untouched; copied `game/` only; no release
