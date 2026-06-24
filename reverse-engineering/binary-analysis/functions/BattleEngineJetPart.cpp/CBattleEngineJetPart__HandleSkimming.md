# CBattleEngineJetPart__HandleSkimming

> Address: `0x00411500` | Source family: `references/Onslaught/BattleEngineJetPart.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void __thiscall CBattleEngineJetPart__HandleSkimming(void * this)`
- Fresh read-back: `release/readiness/ghidra_battleengine_jetpart_signature_correction_2026-05-10.md`
- Runtime behavior proof: not yet

## Summary

Source-aligned jet skimming helper. The checked retail body samples terrain/water-style height context, checks low-altitude high-speed skimming, damps velocity, applies damage-like behavior, and calls `CBattleEngine__HostileEnvironment`.

The current correction supersedes the older `CMonitor__ApplyHostileEnvironmentPenalty` label.

## Evidence

- Source anchor: `CBattleEngineJetPart::HandleSkimming()`.
- Read-back tokens include height sampling context, `SQRT`, velocity fields around `+0x7c`, `+0x80`, `+0x84`, and `CBattleEngine__HostileEnvironment`.
- Saved signature removes the old `CMonitor` owner label.

## Boundaries

- The post-signature decompile still contains a local `unaff_` artifact, so local/type cleanup remains open.
- Does not prove runtime skimming, damage, or hostile-environment behavior.
- Does not prove concrete map helper identity, layouts, tags, or local variable names.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
