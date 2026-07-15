# Energy drain/regen scalar plan

Status: **offset hypothesis landed + sampler wired**; live dual-accept pending  
Core defaults remain provisional until dual-accept.

## Steam-static current-energy offset

| Field | Candidate offset | Evidence class |
|-------|------------------|----------------|
| Current energy float | `BattleEngine+0xFC` | Steam static (cloak gate, walker recharge, profile apply) |
| Profile max energy | `profile+0x20` via `BE+0x4B0` | Steam static layout candidate |
| Profile ground regen | `profile+0x28` | Steam static walker recharge |
| Profile min transform | `profile+0x2C` | Steam static cloak/energy gate |

Supporting decompile bridges (not dual-accept):

- Cloak helper gates `profile+0x2C <= *(float*)(this+0xFC)`.
- Walker recharge: `*(float*)(be+0xFC) += profile+0x28` then caps to `profile+0x20`.
- Cloak runtime observer logs `energyRaw` from `this+0xFC`.

## Sampler / harness

| Item | Path |
|------|------|
| Offsets | `BATTLE_ENGINE_ENERGY_OFFSET = 0xFC` in `battleengine_walker_trajectory_sampler.py` |
| Offline analysis | `tools/battleengine_energy_scaffold.py` |
| Live measure | `--measure energy --vehicle jet` (jet thrust hold drain protocol) |
| npm | `npm run test:battleengine-energy-scaffold` |

Live dual-accept requires two receipt-bound jet holds with stable negative
steady energy rate; walker regen is a separate protocol (not Q-hold).

## Non-claims

- Offset is a **hypothesis** until live dual-accept proves correlated drain/regen.
- Source config defaults (`mEnergy=2.5`, regen `0.01`) are **not** Core authority.
- Core `JetEnergyDrainPerTick` / `WalkerEnergyRegenerationPerTick` stay provisional.
