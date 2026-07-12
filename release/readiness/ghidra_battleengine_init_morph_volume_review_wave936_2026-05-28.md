# Ghidra BattleEngine Init Morph Volume Review Wave936 Readiness

> **Owner/name supersession (2026-07-12):** Wave936 remains a historical
> read-back record. Current static evidence identifies `0x00411b70` as
> `CBattleEngineJetPart__GetIsDoingSpecialAirMove`, not
> `CBattleEngineJetPart__IsStateMachineActive`. See the
> [current movement crosswalk](../../reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md).

Status: complete read-only static read-back evidence
Date: 2026-05-28
Scope: `battleengine-init-morph-volume-review-wave936`

Wave936 re-reviewed the BattleEngine init, auto-targeting, ballistic gate, dual volume-entry dispatch, and morph-flag helpers after the Wave911 risk-ranked continuation queue surfaced the cluster. Fresh Ghidra exports matched the saved correction boundary, and a Composer 2.5 read-only consult agreed that no mutation was justified. This wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x00404dd0` | `CBattleEngine__Init` | `void __thiscall` init helper with `RET 0x4`; DATA xref `0x005d89e8`; constructs/assigns walker/jet part groups at `+0x578` and `+0x57c`, writes state `+0x260` as `2` or `3`, sets `+0x58c`, zeros stealth-adjacent `+0x5d4/+0x5d8/+0x5dc`, then calls `CBattleEngine__SwapPrimarySecondaryPartReadersForState`. |
| `0x00406da0` | `CBattleEngine__SelectNearestForwardTargetFromGlobalSet` | `void * __thiscall` helper with `RET 0x18`; walks global candidate set `DAT_008550d0`, filters by profile/mask/range/forward-facing checks, excludes entries already tracked at `+0x294`, and has three callsites from `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`. |
| `0x0040d0f0` | `CWeaponStatement__UsesBallisticArcNoLocks` | Ballistic gate called by CUnit min/max ballistic distance and OID aim/fire paths; checks non-zero projectile-gravity context while lock-style fields `+0x50` and `+0x6c` are clear. |
| `0x0040dc30` | `CBattleEngine__EnableVolumeEntryGroupsByName` | Thin `entryName` wrapper with `RET 0x4`; dispatches `+0x578` through `CGeneralVolume__EnableEntriesByName` and `+0x57c` through `CGeneralVolume__EnableLinkedEntriesByName`; DATA xref `0x005d8b5c`. |
| `0x0040dc60` | `CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect` | Thin `entryName` wrapper with `RET 0x4`; dispatches `+0x578` through `CGeneralVolume__DisableEntriesByNameAndReselect` and `+0x57c` through `CGeneralVolume__DisableLinkedEntriesByNameAndReselect`; DATA xref `0x005d8b60`. |
| `0x0040dcc0` | `CBattleEngine__ClearFlag58CAndMorphIfState3` | Tiny transition helper: reads `+0x260`, clears `+0x58c`, and tail-jumps to `CBattleEngine__Morph` only when state is `3`. |

Context anchors:

- `0x00406460 CBattleEngine__SwapPrimarySecondaryPartReadersForState` is called by init, state/death checks, morph, and general-volume reset context.
- `0x00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` calls `0x00406da0` at `0x004068bf`, `0x00406a8b`, and `0x00406b0c` and remains projectile/auto-target evidence only, not exact `CBattleEngine::WeaponFired` identity.
- `0x0040dcb0 CBattleEngine__SetFlag58CEnabled` is the adjacent `+0x58c` setter; `0x0040dc90 CBattleEngine__CountFlag9CBySelectionMode` branches on state `+0x260` and is called by `CHud__RenderObjectiveStatusPanel`.
- `0x0040de40 CBattleEngine__AugmentWeapon` remains the static Stuart-source bridge for augmented-weapon activation and is called by `CMonitor__Process`.
- `0x00411b70 CBattleEngineJetPart__IsStateMachineActive` is called by `CBattleEngine__Morph`.
- `0x004fb650 CUnit__ForwardAimTransformAndAttachTargetReader` remains the Wave523 generic CUnit aim/reader context reached from GillMHead, Warspite, and other unit-family callsites.

Fresh read-back evidence:

- Primary exports: 6 metadata rows, 6 tag rows, 12 xref rows, 938 instruction rows, and 6 decompile rows.
- Context exports: 7 metadata rows, 7 tag rows, 22 xref rows, 828 instruction rows, and 7 decompile rows.
- Primary xrefs confirm DATA refs `0x005d89e8`, `0x005d8b5c`, and `0x005d8b60`; three `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` calls into `CBattleEngine__SelectNearestForwardTargetFromGlobalSet`; CUnit/OID ballistic callers into `CWeaponStatement__UsesBallisticArcNoLocks`; and the `0x00535099` call into `CBattleEngine__ClearFlag58CAndMorphIfState3`.
- Context xrefs confirm init/morph/reset calls into `CBattleEngine__SwapPrimarySecondaryPartReadersForState`, `CMonitor__Process` calls into both auto-target/projectile and augment helpers, `CHud__RenderObjectiveStatusPanel` calls into `CBattleEngine__CountFlag9CBySelectionMode`, and `CBattleEngine__Morph` calls into `CBattleEngineJetPart__IsStateMachineActive`.
- Verified read-only backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-013432_post_wave936_battleengine_init_morph_volume_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

Progress:

- Wave911 focused re-audit progress after Wave936: `154/1408 = 10.94%`.
- Static export-contract function-quality closure remains `6113/6113 = 100.00%`.

Probe token anchor: Wave936; `battleengine-init-morph-volume-review-wave936`; `0x00404dd0 CBattleEngine__Init`; `0x00406da0 CBattleEngine__SelectNearestForwardTargetFromGlobalSet`; `0x0040d0f0 CWeaponStatement__UsesBallisticArcNoLocks`; `0x0040dc30 CBattleEngine__EnableVolumeEntryGroupsByName`; `0x0040dc60 CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect`; `0x0040dcc0 CBattleEngine__ClearFlag58CAndMorphIfState3`; `0x00406460 CBattleEngine__SwapPrimarySecondaryPartReadersForState`; `0x00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`; `0x0040dcb0 CBattleEngine__SetFlag58CEnabled`; `0x0040dc90 CBattleEngine__CountFlag9CBySelectionMode`; `0x0040de40 CBattleEngine__AugmentWeapon`; `0x00411b70 CBattleEngineJetPart__IsStateMachineActive`; `0x004fb650 CUnit__ForwardAimTransformAndAttachTargetReader`; `154/1408 = 10.94%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-013432_post_wave936_battleengine_init_morph_volume_review_verified`; no mutation.

What this proves:

- The BattleEngine init/morph-volume/targeting rows remain present in the saved Ghidra project with the expected names, signatures, comments, xrefs, and decompile outputs.
- The saved owner boundary still favors BattleEngine dual-volume dispatch for the `+0x578/+0x57c` helpers and keeps the ballistic helper under the current `CWeaponStatement` label.
- The static join between init, `+0x260` state, `+0x58c`, morph, dual volume groups, auto-targeting, and augment context remains coherent.

What remains unproven:

- Exact source-body identity.
- Complete BattleEngine, JetPart, WalkerPart, weapon/profile, target-set, or volume-entry layouts.
- Runtime morph behavior.
- Runtime targeting/projectile/weapon-fire behavior.
- `weapon_fire_breaks_stealth`.
- Runtime volume-entry behavior.
- BEA patching behavior.
- Rebuild parity.
