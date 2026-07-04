# Wave1140 Motion-Controller Current-Risk Review

Wave1140 (`wave1140-motion-controller-current-risk-review`) re-read nine Wave1108 current-risk rows in the motion-controller residual current-risk cluster with fresh Ghidra metadata, tag, xref, instruction, and decompile exports.

This moves Wave1108 current focused accounting to `238/1179 = 20.19%`. Static closure remains `6411/6411 = 100.00%`; static debt remains `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`. Current risk candidates: `6166`; current focused candidates: `1178`; live regenerated current focused candidates: `1178`; remaining active focused work: `941`.

Probe token anchor: Wave1140; wave1140-motion-controller-current-risk-review; `238/1179 = 20.19%`; 9 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 941; current risk candidates: 6166; motion-controller residual current-risk cluster; fresh Ghidra export; read-only review; no mutation; `0 / 0 / 0`; `6411/6411 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`; `[maintainer-local-ghidra-backup-root]\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`.

## Primary Evidence

| Address | Name | Static evidence |
| --- | --- | --- |
| `0x00497090` | `CMCHiveBoss__Constructor` | `CHiveBoss__Init` call xref `0x0047fed8`; constructor passes `owner_hiveboss+0x178` into the destructable-segments motion-controller base, clears cached cylinder slots, stores the owner pointer, and installs vtable `0x005dc388`. |
| `0x00497140` | `CDestructableSegmentsMotionController__CacheNamedCollisionCylinders` | `CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0` call xref `0x004976f1`; walks model parts, compares N/S/E/W mid/top/bot cylinder names, caches matching collision-cylinder parts, and sets the ready flag. |
| `0x00494fa0` | `SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag` | DATA xrefs `0x005dc294` and `0x005dc3a0`; shared CMCBuggy/CMCHiveBoss vtable target that updates output bit 0 from the UnitAI indexed-entry gate. |
| `0x00494ff0` | `SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10` | DATA xrefs `0x005dc298` and `0x005dc3a4`; shared CMCBuggy/CMCHiveBoss vtable target that forwards an indexed-entry call through UnitAI when the state context is not locally blocked. |
| `0x0049c1d0` | `CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0` | DATA xrefs `0x005d8900`, `0x005dbc88`, `0x005dc3c8`, and `0x005df8a4`; writes an interpolated or cached bone float and keeps exact virtual semantics bounded. |
| `0x0049c3e0` | `CMCMine__Constructor` | `CMine__Init` call xrefs `0x004ba3d0` and `0x004ba3dc`; installs vtable `0x005dc3f4` and stores the owner pointer. |
| `0x0049c440` | `CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440` | DATA xref `0x005dc404`; updates an interpolated owner height offset from owner fields `+0x250/+0x254`. |
| `0x0049c5d0` | `CMCSentinel__Constructor` | `CSentinel__Init` call xrefs `0x004deafd` and `0x004deb09`; installs vtable `0x005dc420`, stores the owner pointer, and seeds cached float fields with `0xc479c000`. |
| `0x0049f820` | `SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820` | `CGillM__VFunc09_InitGroundedSpawnState` call xref `0x004799fa`, DATA xrefs `0x005e3098` and `0x005e06a8`, plus no-function callsite `0x004f4714`; initializes grounded motion components and resolves a named child through `CDestroyableSegment__FindChildByNameI`. |

## Context Evidence

Wave1140 also exported 15 context rows around the reviewed motion-controller cluster: `0x00493020 CMCBuggy__CMCBuggy`, `0x00495260 CMCCannon__ScalarDeletingDestructor`, `0x00495280 CMCCannon__Dtor`, `0x00495930 CMCComponent__Ctor`, `0x00495960 CMCComponent__ScalarDeletingDestructor`, `0x00495980 CMCComponent__Dtor`, `0x00496090 CMCDropship__Ctor`, `0x004960c0 CMCDropship__ScalarDeletingDestructor`, `0x004960e0 CMCDropship__Dtor`, `0x00496540 CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540`, `0x004976d0 CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0`, `0x0049cad0 CMCTentacle__Constructor`, `0x0049ef80 CMCWarspiteDome__Constructor`, `0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10`, and `0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0`.

## Evidence Counts

- Primary exports: `9` metadata rows, `9` tag rows, `19` xref rows, `823` instruction rows, and `9` decompile rows.
- Context exports: `15` metadata rows, `15` tag rows, `26` xref rows, `1388` instruction rows, and `15` decompile rows.
- Queue refresh: `6411/6411 = 100.00%`; static debt `0 / 0 / 0`.
- Current-risk refresh: current risk candidates `6166`; current focused candidates `1178`; focused threshold `15`; not Wave911 reconstruction.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`.

## Boundary

This is static Ghidra evidence only. Runtime motion-controller behavior, runtime HiveBoss motion behavior, runtime mine motion behavior, runtime sentinel motion behavior, runtime grounded-unit behavior, exact concrete motion-controller/UnitAI/owner/mesh-part/transform layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
