# CMonitor__Process

> Address: `0x004081c0` | Source family: `monitor.h` / Monitor state helpers

## Status

- Named in Ghidra: yes
- Fresh read-back: `release/readiness/ghidra_monitor_gameplay_signature_tranche_2026-05-09.md`
- Runtime behavior proof: not yet

## Summary

Large monitor processing helper that reaches active-reader expiry, tracked-list updates, flight/walker transition helpers, vibration, HUD/sound/tracking/physics helpers, actor movement, camera update, and target/effect updates.

The current decompile read-back supports the helper name with these token-level signals:

- `CBattleEngine__Morph` (historical alias: `CMonitor__UpdateFlightWalkerTransitionState`)
- `s_hud__s_00623314`
- `CMonitor__PlayRandomSampleFromChain`
- `CMonitor__ProcessTrackingAndSurfaceAlignment`
- `CActor__Move`
- `CMonitor__UpdateCameraVectorsAndInput`
- `0x5d8` / `0x5dc` interpolation context
- `0x4ac` / `0xfc` cloak/fade timer decay context

## Interpretation

This function is a broad monitor process anchor, not a narrow HUD-warning proof by itself. The prior string-xref pass showed `hud_armour_low` and `hud_energy_low` xrefs landing in this function family; this note records only the fresh helper read-back tokens and keeps runtime HUD-warning behavior unclaimed.

The 2026-05-09 signature tranche saved `void __fastcall CMonitor__Process(void * monitor)` and a proof-boundary comment in Ghidra. The cloak/fade token context is useful static evidence for later cloak work, but it is not runtime cloak activation, fire-while-cloaked behavior, or exact source-method identity proof.

The follow-up linked/monitor and transition/targeting signature tranches also hardened nearby helpers called from this process family, including `LinkedPtrCursor__MoveFirstAndGet`, `LinkedPtrCursor__MoveNextAndGet`, `CMonitor__GetLastValidRangeStep100`, `CMonitor__UpdateSoundEventPlaybackForReader`, `CBattleEngine__Morph`, and `CBattleEngine__UpdateAutoAim`. Those helper names/signatures improve static readability but do not prove runtime sound, movement, target choice, transform, or cloak behavior.

## Boundaries

- Does not prove live HUD warning behavior.
- Does not prove complete monitor process semantics.
- Does not prove runtime cloak activation or fire-while-cloaked behavior.
- Does not mutate `BEA.exe`.
- Does not prove concrete structure layout, local names, tags, or rebuild parity.
