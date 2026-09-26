# CCockpit__AddShockShake

> Address: `0x004247a0` | Source family: `CCockpit` (no cockpit source in the pinned drop)

Status: renamed function note; the pre-audit notes below are leads
Last updated: 2026-09-26 (renamed from `CGeneralVolume__InitRandomizedVelocityOffsets` by the RE record audit)
Summary: `0x004247a0` is `CCockpit::AddShockShake(amount)`. Its only caller is `CBattleEngine::AddShockShake`
(`0x00407a22`, `BattleEngine.cpp:1112`, on `mCockpit` at `+0x528`), and its only calls are four to the CRT `_rand`.
The evidence is in [the second label cohort](../../../ghidra/README.md#re-audit-label-corrections-second-cohort--september-26). The notes below were written under the former label.

Source File: none — the cockpit implementation is absent from the pinned GPL drop; the call site is
`references/Onslaught/BattleEngine.cpp:1112` | Binary: BEA.exe pristine specimen, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`


## Status

- Saved Ghidra name/signature/comment: yes, Wave 321
- Saved signature: `void __thiscall CGeneralVolume__InitRandomizedVelocityOffsets(void * this, int randomRange)`
- Runtime behavior proof: not yet
- Exact source-file identity: not yet

## Summary

Initializes randomized velocity-offset fields at `this + 0x90`, `+0x94`, `+0x98`, and `+0x9c`, then zeroes phase-like field `+0xa0`. The callsite at `CGeneralVolume__RandomizeOffsets4B8_4C0` shows one explicit scalar argument, so the older saved extra float parameter was removed.

The helper also clamps the generated offset components against the observed `0.01` range token.

## Boundaries

- This is static Ghidra read-back and saved metadata only.
- It does not prove exact `CGeneralVolume` layout, random distribution semantics, runtime camera/noise behavior, tags, local names, or rebuild parity.
- It does not launch, patch, or mutate `BEA.exe`.
