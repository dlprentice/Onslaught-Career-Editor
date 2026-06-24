# CBattleEngineJetPart__dtor_base

> Address: `0x004102a0` | Source family: `references/Onslaught/BattleEngineJetPart.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void __thiscall CBattleEngineJetPart__dtor_base(void * this)`
- Fresh read-back: `release/readiness/ghidra_battleengine_jetpart_signature_correction_2026-05-10.md`
- Runtime behavior proof: not yet

## Summary

Destructor-base body for `CBattleEngineJetPart`. The checked retail body walks the weapon pointer set, removes entries, dispatches the deleting destructor for each weapon entry, and clears the set.

The current correction supersedes the older `CBattleEngine__DestroySPtrSetElementsAndClear` label.

## Evidence

- Source anchor: `CBattleEngineJetPart::~CBattleEngineJetPart()`.
- Read-back tokens include `CSPtrSet__Remove`, a virtual deleting-destructor dispatch, `CSPtrSet__Clear`, and a plain `ret`.
- Saved signature removes the old generic register parameter.

## Boundaries

- Does not prove destructor wrapper pairing or concrete weapon ownership layout.
- Does not prove runtime weapon ownership behavior.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
