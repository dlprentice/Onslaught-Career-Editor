# Wave1139 BattleEngine JetPart Current-Risk Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00411b70` → `CBattleEngineJetPart__GetIsDoingSpecialAirMove` (was `CBattleEngineJetPart__IsStateMachineActive`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> **Owner/name supersession (2026-07-12):** Wave1139 remains a historical
> read-back record. Current static evidence identifies `0x00411b70` as
> `CBattleEngineJetPart__GetIsDoingSpecialAirMove`, not
> `CBattleEngineJetPart__IsStateMachineActive`. See the
> [current movement crosswalk](../../reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md).

Status: complete static read-back evidence
Date: 2026-06-05
Scope: `wave1139-battleengine-jetpart-current-risk-review`

Wave1139 re-read ten Wave1108 current-risk rows in the BattleEngine JetPart movement/gravity cluster and recovered one additional source-backed function boundary:

Probe token anchor: Wave1139; wave1139-battleengine-jetpart-current-risk-review; `229/1179 = 19.42%`; 10 current-risk rows; 1 function-boundary recovery; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 950; current risk candidates: 6166; BattleEngine JetPart movement/gravity current-risk cluster; fresh Ghidra export; function-boundary recovery; `0 / 0 / 0`; `6411/6411 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`; `[maintainer-local-ghidra-backup-root]\BEA_20260605-130856_post_wave1138_battleengine_walkerpart_current_risk_review_verified`.

| Address | Evidence |
| --- | --- |
| `0x004074d0 CBattleEngine__Gravity` | Function-boundary recovery from the no-function gap before `CGame__UpdateMouseLookAngles`; source parity with `references/Onslaught/BattleEngine.cpp` lines 1064-1088; DATA xref `0x005d8a78`; two jet-state tail jumps to `CBattleEngineJetPart__Gravity`. |
| `0x00410210 CBattleEngineJetPart__ctor` | Constructor stores the main part, clears movement/state fields, seeds timing fields, calls reset configuration, and initializes the thruster value. |
| `0x004102a0 CBattleEngineJetPart__dtor_base` | Destructor-base drains owned weapon entries through the smart-pointer set before clearing it. |
| `0x00410310 CBattleEngineJetPart__Thrust` | Player-input xrefs from `CPlayer__ReceiveButtonAction`; updates thruster value, hard-forward timing, loop state, and last Y input. |
| `0x00410490 CBattleEngineJetPart__Turn` | Player-input xref; updates yaw/roll velocity through turn-rate, zoom, low-speed, slow-movement, and transform-start interpolation terms. |
| `0x00410670 CBattleEngineJetPart__Pitch` | Player-input xref; updates pitch velocity through zoom, slow-movement, and transform-start interpolation terms. |
| `0x00410740 CBattleEngineJetPart__YawLeft` | Player-input xref; tracks hard-left timing, left barrel-roll break/start, and strafing acceleration. |
| `0x004109d0 CBattleEngineJetPart__YawRight` | Player-input xref; tracks hard-right timing, right barrel-roll break/start, and strafing acceleration. |
| `0x004114d0 CBattleEngineJetPart__Gravity` | After boundary recovery, xrefs resolve from `CBattleEngine__Gravity` at `0x004074ee` and `0x00407513`; returns small gravity when linked energy is zero and otherwise zero. |
| `0x00411b70 CBattleEngineJetPart__IsStateMachineActive` | `CBattleEngine__Morph` xref; returns non-zero when local state-machine fields are active. |
| `0x004124d0 CBattleEngineJetPart__GetCurrentWeaponNameField04` | `CBattleEngine__ChangeWeapon` xref; selected weapon context/name-field accessor. |

Read-back evidence:

- Initial exports: 10 metadata rows, 10 tag rows, 12 xref rows, 814 instruction rows, and 10 decompile rows.
- Gravity callsite context export: 90 instruction rows around `0x004074ee` and `0x00407513`.
- `CreateFunctionsFromAddressList.java` dry: `would_create=1 already_exists=0 renamed=0 would_rename=0 failed=0`.
- `ApplyBattleEngineGravityBoundaryWave1139.java` dry/apply/final dry: `updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, then `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=2 missing=0 bad=0`, then `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 11 metadata rows, 11 tag rows, 13 xref rows, 833 instruction rows, and 11 decompile rows.
- Queue refresh after the boundary recovery: `6411/6411 = 100.00%`, static debt `0 / 0 / 0`.
- Current-risk refresh: current risk candidates `6166`, current focused candidates `1178`, focused threshold `15`.
- Wave1108 current focused accounting moved to `229/1179 = 19.42%`; remaining active focused work: `950`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`, 19 files, 175967111 bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-130856_post_wave1138_battleengine_walkerpart_current_risk_review_verified`.

What this proves:

- The saved Ghidra project contains the recovered `0x004074d0 CBattleEngine__Gravity` function object.
- The recovered function has a saved `float __thiscall CBattleEngine__Gravity(void * this)` signature, bounded comment, and `wave1139-readback-verified` tags.
- `CBattleEngineJetPart__Gravity` xrefs now resolve through `CBattleEngine__Gravity` instead of `<no_function>` callsites.
- The ten JetPart movement/gravity rows still have clean saved names/signatures/comments and fresh xref/decompile/instruction evidence.

What remains unproven:

- Runtime JetPart control behavior.
- Runtime flight physics.
- Runtime morph behavior.
- Exact concrete `CBattleEngine` / JetPart layouts and exact state enum names.
- `weapon_fire_breaks_stealth`.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.
