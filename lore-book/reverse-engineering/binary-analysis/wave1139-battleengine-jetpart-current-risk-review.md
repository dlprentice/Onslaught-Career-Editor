# Wave1139 BattleEngine JetPart Current-Risk Review

Wave1139 (`wave1139-battleengine-jetpart-current-risk-review`) re-read ten Wave1108 current-risk rows in the BattleEngine JetPart movement/gravity cluster and recovered one additional source-backed boundary, `0x004074d0 CBattleEngine__Gravity`.

This moves Wave1108 current focused accounting to `229/1179 = 19.42%`. Static closure is now `6411/6411 = 100.00%`; static debt remains `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`. Current risk candidates: `6166`; current focused candidates: `1178`; live regenerated current focused candidates: `1178`; remaining active focused work: `950`.

Probe token anchor: Wave1139; wave1139-battleengine-jetpart-current-risk-review; `229/1179 = 19.42%`; 10 current-risk rows; 1 function-boundary recovery; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 950; current risk candidates: 6166; BattleEngine JetPart movement/gravity current-risk cluster; fresh Ghidra export; function-boundary recovery; `0 / 0 / 0`; `6411/6411 = 100.00%`; `G:\GhidraBackups\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`; `G:\GhidraBackups\BEA_20260605-130856_post_wave1138_battleengine_walkerpart_current_risk_review_verified`.

## Primary Evidence

| Address | Name | Static evidence |
| --- | --- | --- |
| `0x004074d0` | `CBattleEngine__Gravity` | Function-boundary recovery from the no-function gap before `CGame__UpdateMouseLookAngles`; source parity with `references/Onslaught/BattleEngine.cpp` lines 1064-1088; DATA xref `0x005d8a78`; state switch through `this+0x260`; dying-state gate at `this+0x2c`; two jet-state tail jumps through `this+0x57c` into `CBattleEngineJetPart__Gravity`. |
| `0x00410210` | `CBattleEngineJetPart__ctor` | Constructor stores main part at `+0x18`, clears movement/state fields, seeds timing fields, calls reset configuration, and initializes thruster state. |
| `0x004102a0` | `CBattleEngineJetPart__dtor_base` | Destructor-base drains owned weapon entries via the smart-pointer set and clears the set. |
| `0x00410310` | `CBattleEngineJetPart__Thrust` | `CPlayer__ReceiveButtonAction` xrefs at `0x004d3415` and `0x004d342a`; updates thrust input, hard-forward timing, loop-start gates, and last Y input. |
| `0x00410490` | `CBattleEngineJetPart__Turn` | `CPlayer__ReceiveButtonAction` xref at `0x004d33c1`; updates yaw/roll velocity through turn-rate, zoom, low-speed, slow-movement, and transform-start interpolation terms. |
| `0x00410670` | `CBattleEngineJetPart__Pitch` | `CPlayer__ReceiveButtonAction` xref at `0x004d33d6`; updates pitch velocity through zoom, slow-movement, and transform-start interpolation terms. |
| `0x00410740` | `CBattleEngineJetPart__YawLeft` | `CPlayer__ReceiveButtonAction` xref at `0x004d33eb`; tracks hard-left timing, left barrel-roll break/start, last X input, and strafing acceleration. |
| `0x004109d0` | `CBattleEngineJetPart__YawRight` | `CPlayer__ReceiveButtonAction` xref at `0x004d3400`; tracks hard-right timing, right barrel-roll break/start, last X input, and strafing acceleration. |
| `0x004114d0` | `CBattleEngineJetPart__Gravity` | After boundary recovery, xrefs resolve from `CBattleEngine__Gravity` at `0x004074ee` and `0x00407513`; body returns small gravity when linked main-part energy is zero and otherwise returns zero. |
| `0x00411b70` | `CBattleEngineJetPart__IsStateMachineActive` | `CBattleEngine__Morph` xref at `0x0040a5bf`; checks local JetPart state-machine fields. |
| `0x004124d0` | `CBattleEngineJetPart__GetCurrentWeaponNameField04` | `CBattleEngine__ChangeWeapon` xref at `0x0040a001`; selected weapon context/name-field accessor. |

## Evidence Counts

- Initial exports: `10` metadata rows, `10` tag rows, `12` xref rows, `814` instruction rows, and `10` decompile rows.
- Gravity callsite context export: `90` instruction rows around `0x004074ee` and `0x00407513`.
- Boundary dry/apply/final-dry evidence:
  - `CreateFunctionsFromAddressList.java` dry: `would_create=1 already_exists=0 renamed=0 would_rename=0 failed=0`.
  - `ApplyBattleEngineGravityBoundaryWave1139.java` dry: `updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
  - Apply: `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=2 missing=0 bad=0`, with `REPORT: Save succeeded`.
  - Final dry: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: `11` metadata rows, `11` tag rows, `13` xref rows, `833` instruction rows, and `11` decompile rows.
- Queue refresh: `6411/6411 = 100.00%`; static debt `0 / 0 / 0`.
- Current-risk refresh: current risk candidates `6166`; current focused candidates `1178`; focused threshold `15`; not Wave911 reconstruction.
- Verified backup: `G:\GhidraBackups\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `G:\GhidraBackups\BEA_20260605-130856_post_wave1138_battleengine_walkerpart_current_risk_review_verified`.

## Boundary

This is static Ghidra/source evidence only. Runtime JetPart control behavior, runtime flight physics, runtime morph behavior, exact concrete `CBattleEngine`/JetPart layouts, exact state enum names, `weapon_fire_breaks_stealth`, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
