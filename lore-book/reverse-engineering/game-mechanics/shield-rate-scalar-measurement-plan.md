# Shield regen/drain scalar plan

Status: **offset hypothesis landed**; live dual-accept pending  
Scaffold: `tools/battleengine_shield_scaffold.py`

## Steam-static shields offset

| Field | Candidate offset | Evidence class |
|-------|------------------|----------------|
| Current shields float | `BattleEngine+0x100` | Steam static (walker recharge mirror) |
| Current energy float | `BattleEngine+0xFC` | paired with shields mirror |

Walker recharge decompile (after energy update) writes shields at
`main+0x100` from the energy path (source `mShields=mEnergy` in walker).
Jet mode source zeros shields.

Sampler constant: `BATTLE_ENGINE_SHIELDS_OFFSET = 0x100`.

## Next live steps

1. Sample `energy` + `shields` under receipt-bound walker idle regen (no damage).
2. Optional damage-drain attempt only with explicit runtime authority.
3. Dual-accept → contract → Core; do not promote source defaults alone.
