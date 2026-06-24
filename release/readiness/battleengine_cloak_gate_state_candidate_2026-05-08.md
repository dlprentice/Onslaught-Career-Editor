# BattleEngine Cloak Gate State Candidate - 2026-05-08

Status: public-safe bounded static/source-to-retail candidate, not runtime activation proof

## Objective

Explain the copied-profile gate observer result without guessing more keys or sending weapon-fire input.

The latest runtime probe showed:

```text
EVENTS_WITHOUT_ACTIVATION
eventCount=4
pairCount=2
activationPairCount=0
gateBlockedPairCount=2
```

Both helper pairs reached the candidate cloak helper but failed the linked-object threshold side of the candidate activation gate.

## Probe

Command:

```powershell
npm run test:battleengine-cloak-gate-state-candidate
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_cloak_gate_state_candidate_probe.py --check
```

Result:

```text
BattleEngine cloak gate state candidate probe
Status: pass
Source cloak tokens: 9/9
Source data tokens: 4/4
Profile apply tokens: 5/5
Cloak helper tokens: 6/6
Active cloak tokens: 5/5
Walker profile tokens: 3/3
Selection profile tokens: 4/4
```

## What This Proves

- Stuart source `CBattleEngine::HandleCloak()` routes to `Cloak()` only after the energy gate.
- Stuart source `CBattleEngine::Cloak()` gates activation on `mConfiguration->mStealth > 0`.
- Stuart source `CBattleEngineData` carries `mStealth` with energy, transform, and recharge configuration fields.
- Read-only retail decompile shows `CBattleEngine__ApplyWeaponProfileByIndex` writes the current profile pointer to `this+0x4b0` and copies profile fields into current energy/life-like state.
- Read-only retail decompile shows `CGeneralVolume__Update4ACLatchFromHeightAndA0` gates candidate activation on linked profile `+0x2c <= this+0xfc` and linked profile `+0xa0 > 0`, then copies profile `+0xa0` into the target scalar.
- Read-only retail decompiles reuse the same `this+0x4b0` profile pointer for active cloak energy burn, max-energy capping, ground recharge-like configuration values, and per-slot readiness gates.

## Interpretation

This is stronger than the previous "state/setup gate" statement:

- the decoded cloak bindings are still the right current input target,
- the tested copied-profile runtime state reached the candidate helper,
- the tested linked profile/config object had a zero threshold-side value for the field that source cloak logic strongly suggests is the stealth capability/config value,
- the current blocker is probably a non-stealth-capable configuration/profile or an upstream state that has not selected a stealth-capable profile.

The next runtime wave should identify or select a profile/configuration with positive linked profile `+0xa0` before any weapon-fire input is sent.

`release/readiness/battleengine_profile_layout_candidate_2026-05-08.md` strengthens this interpretation: source x86 layout places `CBattleEngineData::mStealth` at `+0xa0` and `mConfigurationName` at `+0xa8`, while existing retail decompiles consume those same offsets as the cloak helper gate and printed profile name. The next blocker is now more specifically "select or identify a profile with positive `mStealth` / profile `+0xa0`."

## Not Proven

- Exact source-to-retail field layout for every `CBattleEngineData` member.
- Final semantic name for retail profile `+0xa0`.
- Runtime cloak activation.
- A cloak-active baseline before firing.
- Whether firing while cloaked breaks or preserves stealth.
- Retail `RF_CLOAKED` render-flag identity.
- Ghidra rename-map mutation or project semantic promotion.
- Rebuildable gameplay implementation parity.

## Privacy / Release Safety

This report is public-safe. It contains only repo-relative command names, token counts, public function names/addresses already used by the project, and explicit proof boundaries. It does not include raw decompile bodies, copied saves, copied executables, debugger logs, screenshots, private absolute paths, or runtime proof JSON.
