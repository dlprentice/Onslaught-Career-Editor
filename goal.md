# Active Goal Baton

Status: **ACTIVE** (full reconstruction campaign)  
Last updated: 2026-07-14  
Integration tip: `d9e33df3`

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

- **Tip SHA:** `d9e33df3`
- **Closed:** M2-energy-live-dual-accept ADVANCEMENT (not BLOCKED)
- **Validation:** `npm run test:rebuild-core` (51 pass); `npm run test:rebuild-client` (73 pass); energy scaffold + scalar contract regression (incl. jet-energy-drain v1); `npm run test:docsync` PASS
- **Paths:** public energy v1/policy/Core 17 + goldens; private pair under ignored `local-proofs/wt/energy-p02`
- **Codex owns next:** `M2-shield-live-dual-accept` only
- **Confirm:** Steam/original BEA untouched; copied `game/` path only; no release
