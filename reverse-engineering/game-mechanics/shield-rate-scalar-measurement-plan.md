# Shield regen/drain scalar plan

Status: **input-free live sampler wired**; live dual-accept pending
Scaffold: `tools/battleengine_shield_scaffold.py`
Live command: `--measure shield --vehicle walker`

## Steam-static shields offset

| Field | Candidate offset | Evidence class |
|-------|------------------|----------------|
| Current shields float | `BattleEngine+0x100` | Steam static (walker recharge mirror) |
| Current energy float | `BattleEngine+0xFC` | paired with shields mirror |

Walker recharge decompile (after energy update) writes shields at
`main+0x100` from the energy path (source `mShields=mEnergy` in walker).
Jet mode source zeros shields.

Sampler constant: `BATTLE_ENGINE_SHIELDS_OFFSET = 0x100`. The live mode records
paired energy/shield fields under receipt and foreground guards without owning
Q input or invoking motion/velocity acceptance. It enforces the full QPC phase
schedule, walker state, and neutral control on every sample. Its deterministic
scaffold requires symmetric positive correlation over the union of active
energy/shield edges and rejects any material wrong-direction edge in the
no-damage setup. Its pair producer requires attempts 1 and 2 with fresh
receipt/run digests. The cleanup owner records input as not owned and never
sends backup Q for shield, including on failure. This readiness is not runtime
proof.

## Next live steps

1. Sample `energy` + `shields` under receipt-bound walker neutral-control idle
   setup (no damage)
   with `--measure shield --vehicle walker`.
2. Optional damage-drain attempt only with explicit runtime authority.
3. Dual-accept → contract → Core; do not promote source defaults alone.
