# Wave1178 Carver Current-Risk Consolidation Readiness Note

Status: complete static tag-only normalization
Date: 2026-06-06
Scope: `wave1178-carver-current-risk-consolidation-review`

Wave1178 accounts for `20 Carver current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra metadata, tag, xref, instruction, and decompile exports. It performed tag-only normalization for all twenty rows: no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00422440 CCarver__Init` | DATA xref `0x005e0db0`; initializes the Carver air-unit path, creates the guide/helper pair, starts launch animation, and seeds wing/attack state fields. |
| `0x00422620 CCarver__UpdateMotionAndWingPose` | DATA xref `0x005e0e94`; updates motion/trail effects, wing blend/state, speed-scaled vector work, and owner vfunc dispatch at byte offset `+0x70`. |
| `0x00422760 CCarverAI__OpenWings` / `0x004227a0 CCarverAI__CloseWings` | Animation helpers that resolve/open/close Carver wings and write the wing state at `+0x27c`; close helper has four current call xrefs from Carver AI event handlers. |
| `0x00422970 CCarverAI__CanStartAttack` | DATA xref `0x005e0f2c`; attack-start predicate with wing/cooldown gating. |
| `0x00422aa0 CCarverAI__RefreshTargetReaderAndScheduleMove` / `0x00422b90 CCarverAI__UpdateAttackAndReschedule` | DATA xrefs `0x005d9468` and `0x005d946c`; Carver AI event handlers for target reader refresh, wing close/open behavior, attack update, and rescheduling. |
| `0x00422db0 CCarverAI__CheckNearbyEnemies` | Call xref from the Carver AI update handler; mapwho nearby-enemy scan plus last-attack timestamp update. |
| `0x00422f90 CCarverGuide__ctor` / `0x00422fd0 CCarverGuide__dtor_base` | Guide lifecycle rows tied to prior CarverGuide evidence; constructor call from `CCarver__Init` and destructor-base call from the scalar-deleting wrapper. |
| `0x00423490 CCarverGuide__HandleEvent` / `0x00423510 CCarverGuide__AcquireNearestTargetReader` | DATA xref `0x005d947c` and handler call evidence for CarverGuide target refresh / nearest-target reader acquisition. |
| `0x0050f340 CCarver__Destructor_VFunc01` | Destructor vfunc body clearing Carver-owned pointer sets/global-list node before forwarding to `CUnit__dtor_base`. |

Read-back evidence:

- `ApplyCarverCurrentRiskConsolidationWave1178.java` dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=206 missing=0 bad=0`.
- `ApplyCarverCurrentRiskConsolidationWave1178.java` apply: `updated=20 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=206 missing=0 bad=0`.
- `ApplyCarverCurrentRiskConsolidationWave1178.java` final dry: `updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post exports: `20` metadata rows, `20` tag rows, `23` xref rows, `873` instruction rows, and `20` decompile rows.
- Queue/accounting after Wave1178: `6411` total functions, `6411` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, `715/1179 = 60.64%` current focused accounting, and `464` remaining active focused rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-095003_post_wave1178_carver_current_risk_consolidation_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The twenty Carver target rows exist in the saved Ghidra project and match the saved names/signatures/comments.
- Wave1178 tags are present after read-back for all twenty target rows.
- Fresh xref, instruction, and decompile exports support a coherent static Carver init/wing/attack/guide/destructor slice.
- The rows are now explicitly counted against the active Wave1108 current-risk denominator.

What remains unproven:

- Runtime Carver behavior, runtime wing timing, runtime attack/target selection behavior, runtime guide/navigation behavior, exact `CCarver` / `CCarverAI` / `CCarverGuide` concrete layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity.

Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference; actual no-noticeable-difference parity still requires later runtime, asset, visual, control, timing, save, patch, and rebuild proof.

Probe token anchor: Wave1178; wave1178-carver-current-risk-consolidation-review; 715/1179 = 60.64%; 20 Carver current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 464; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=20 skipped=0; tags_added=206; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consult used; Codex root final judgment; consult narrowed to 11 rows; root widened to 20-row coherent Carver slice; 0 / 0 / 0; 6411/6411 = 100.00%; 23 xref rows; 873 instruction rows; CCarver__Init; CCarverAI__dtor_base; CCarver__UpdateMotionAndWingPose; CCarverAI__OpenWings; CCarverAI__CloseWings; CCarverAI__Fire; CCarverAI__CheckNearbyEnemies; CCarverGuide__AcquireNearestTargetReader; CCarver__Destructor_VFunc01; [maintainer-local-ghidra-backup-root]\BEA_20260606-095003_post_wave1178_carver_current_risk_consolidation_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
