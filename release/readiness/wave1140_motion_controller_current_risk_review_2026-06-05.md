# Wave1140 Motion-Controller Current-Risk Readiness Note

Status: complete static read-back evidence
Date: 2026-06-05
Scope: `wave1140-motion-controller-current-risk-review`

Wave1140 re-read nine Wave1108 current-risk rows in the motion-controller residual current-risk cluster with fresh Ghidra metadata, tag, xref, instruction, and decompile exports. It was a read-only review with no mutation: no rename, no signature edit, no comment/tag edit, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, and no runtime-file mutation.

Probe token anchor: Wave1140; wave1140-motion-controller-current-risk-review; `238/1179 = 20.19%`; 9 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 941; current risk candidates: 6166; motion-controller residual current-risk cluster; fresh Ghidra export; read-only review; no mutation; `0 / 0 / 0`; `6411/6411 = 100.00%`; `G:\GhidraBackups\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`; `G:\GhidraBackups\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`.

| Address | Evidence |
| --- | --- |
| `0x00497090 CMCHiveBoss__Constructor` | `CHiveBoss__Init` call xref `0x0047fed8`; constructor passes `owner_hiveboss+0x178` into the destructable-segments motion-controller base, clears cached cylinder slots, and installs vtable `0x005dc388`. |
| `0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders` | `CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0` call xref `0x004976f1`; walks model parts, compares N/S/E/W mid/top/bot cylinder names, caches matching collision-cylinder parts, and sets the ready flag. |
| `0x00494fa0 SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag` | DATA xrefs `0x005dc294` and `0x005dc3a0`; shared CMCBuggy/CMCHiveBoss vtable target that updates output bit 0 from the UnitAI indexed-entry gate. |
| `0x00494ff0 SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10` | DATA xrefs `0x005dc298` and `0x005dc3a4`; shared CMCBuggy/CMCHiveBoss vtable target that forwards an indexed-entry call through UnitAI when the state context is not locally blocked. |
| `0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0` | DATA xrefs `0x005d8900`, `0x005dbc88`, `0x005dc3c8`, and `0x005df8a4`; writes an interpolated or cached bone float and preserves the conservative virtual-name boundary. |
| `0x0049c3e0 CMCMine__Constructor` | `CMine__Init` call xrefs `0x004ba3d0` and `0x004ba3dc`; installs vtable `0x005dc3f4` and stores the owner pointer. |
| `0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440` | DATA xref `0x005dc404`; updates an interpolated owner height offset from owner fields `+0x250/+0x254`. |
| `0x0049c5d0 CMCSentinel__Constructor` | `CSentinel__Init` call xrefs `0x004deafd` and `0x004deb09`; installs vtable `0x005dc420`, stores the owner pointer, and seeds cached float fields with `0xc479c000`. |
| `0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820` | `CGillM__VFunc09_InitGroundedSpawnState` call xref `0x004799fa`, DATA xrefs `0x005e3098` and `0x005e06a8`, plus no-function callsite `0x004f4714`; initializes grounded motion components and resolves a named child through `CDestroyableSegment__FindChildByNameI`. |

Read-back evidence:

- Primary exports: 9 metadata rows, 9 tag rows, 19 xref rows, 823 instruction rows, and 9 decompile rows.
- Context exports: 15 metadata rows, 15 tag rows, 26 xref rows, 1388 instruction rows, and 15 decompile rows.
- Queue refresh after the read-only review: `6411/6411 = 100.00%`, static debt `0 / 0 / 0`.
- Current-risk refresh: current risk candidates `6166`, current focused candidates `1178`, focused threshold `15`.
- Wave1108 current focused accounting moved to `238/1179 = 20.19%`; remaining active focused work: `941`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`, 19 files, 175967111 bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `G:\GhidraBackups\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`.

What this proves:

- The nine target rows still have clean saved Ghidra names, signatures, comments, tags, xrefs, and decompile rows.
- The motion-controller cluster remains conservatively bounded across HiveBoss, shared motion-controller vfuncs, CMCMech, CMCMine, CMCSentinel, and SharedGroundUnit evidence.
- No Ghidra mutation was required for this wave.

What remains unproven:

- Runtime motion-controller behavior.
- Runtime HiveBoss, mine, sentinel, mech, or grounded-unit motion behavior.
- Exact concrete motion-controller, mesh-part, UnitAI, owner, and transform layouts.
- Exact source-body identity.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.
