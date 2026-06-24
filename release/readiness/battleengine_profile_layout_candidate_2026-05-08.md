# BattleEngine Profile Layout Candidate - 2026-05-08

Status: public-safe bounded static/source-to-retail layout candidate, not runtime activation proof

## Objective

Turn the cloak gate blocker into a stronger source-to-retail field mapping before running more copied-profile runtime input.

The previous static follow-up showed that source `CBattleEngine::Cloak()` gates activation on `mConfiguration->mStealth > 0`, while the retail candidate helper gates on current profile `+0xa0 > 0`. This probe checks whether source x86 layout and existing retail decompiles support treating retail profile `+0xa0` as the `CBattleEngineData::mStealth` candidate.

## Probe

Command:

```powershell
npm run test:battleengine-profile-layout-candidate
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_profile_layout_candidate_probe.py --check
```

Result:

```text
BattleEngine profile layout candidate probe
Status: pass
Source layout tokens: 18/18
SPtrSet tokens: 4/4
Retail profile tokens: 3/3
Retail cloak tokens: 3/3
Retail walker tokens: 2/2
Retail selection tokens: 1/1
Calculated critical offsets:
- mLife: 0x1c
- mEnergy: 0x20
- mGroundEnergyIncrease: 0x28
- mMinTransformEnergy: 0x2c
- mStoreHeat: 0x70
- mStoreValue: 0x88
- mStealth: 0xa0
- mLanguageName: 0xa4
- mConfigurationName: 0xa8
```

## What This Proves

- Stuart source `CBattleEngineData` field order plus the x86 `GenericSPtrSet` shape place `mStealth` at offset `+0xa0` and `mConfigurationName` at offset `+0xa8`.
- Existing read-only retail decompile prints the current profile name from profile `+0xa8`, matching the source `mConfigurationName` candidate.
- Existing read-only retail decompiles consume profile `+0x1c`, `+0x20`, `+0x28`, `+0x2c`, `+0x88`, `+0xa0`, and `+0xa8` in ways consistent with source life, energy, recharge, transform-energy, store-value, stealth, and configuration-name fields.
- Retail profile `+0xa0` is now a strong source-compatible `CBattleEngineData::mStealth` candidate.
- The latest copied-profile runtime blocker is consistent with a current profile whose stealth value was zero or non-positive.

## Not Proven

- Exact values for all loaded retail BattleEngine profiles.
- Which profile/configuration the latest copied runtime selected.
- A runtime profile with positive `mStealth` / profile `+0xa0`.
- Runtime cloak activation.
- Whether firing while cloaked breaks or preserves stealth.
- Ghidra rename-map mutation or semantic promotion.
- Rebuildable gameplay implementation parity.

## Next Runtime Implication

Do not broaden key guessing or send weapon-fire input yet. The next runtime wave should identify or select a BattleEngine configuration/profile whose profile `+0xa0` is positive, then rerun the latch observer to prove activation before testing downstream weapon-fire behavior.

## Privacy / Release Safety

This report is public-safe. It contains only source field names, public offsets, repo-relative command names, token counts, and explicit proof boundaries. It does not include raw decompile bodies, copied saves, copied executables, debugger logs, screenshots, private absolute paths, or runtime proof JSON.
