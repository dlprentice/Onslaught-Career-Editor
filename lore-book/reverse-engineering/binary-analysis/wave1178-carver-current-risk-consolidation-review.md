# Wave1178 Carver Current-Risk Consolidation Review

Status: complete static tag-only normalization
Date: 2026-06-06
Scope: `wave1178-carver-current-risk-consolidation-review`

Wave1178 accounts for `20 Carver current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It performed tag-only normalization using `ApplyCarverCurrentRiskConsolidationWave1178.java`: no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation. Codex read-only consult was used for next-cluster sanity; the consult narrowed to an 11-row Carver AI wing/attack-loop slice, while Codex root widened the final wave to the coherent 20-row Carver slice after auditing the live metadata/tags/xrefs/decompile.

Current accounting after Wave1178:

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave911 focused | `812/1408 = 57.67%`, historical-retired/non-reconstructable |
| Wave911 top-500 risk-ranked | `500/500 = 100.00%` |
| Wave1108 current focused accounting | `715/1179 = 60.64%` |
| Current focused candidates | `1178` |
| Live regenerated current focused candidates | `1178` |
| Remaining active focused work | `464` |
| Current risk candidates | `6166` |

Fresh export evidence:

| Artifact | Rows |
| --- | ---: |
| Metadata | `20` |
| Tags | `20` |
| Xrefs | `23` |
| Function-body instructions | `873` |
| Decompile rows | `20` |

Ghidra tag-normalization evidence:

| Phase | Summary |
| --- | --- |
| Dry | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=206 missing=0 bad=0` |
| Apply | `updated=20 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=206 missing=0 bad=0` |
| Final dry | `updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |

Reviewed rows:

| Address | Saved name | Static read-back evidence |
| --- | --- | --- |
| `0x00422440` | `CCarver__Init` | DATA xref `0x005e0db0`; calls `CAirUnit__Init`, allocates the guide/helper pair, starts launch animation, and seeds Carver wing/attack fields. |
| `0x00422580` | `CCarverAI__dtor_base` | Scalar-deleting wrapper call xref `0x00422563`; monitor-style reader unlink/shutdown cleanup for Carver AI. |
| `0x00422620` | `CCarver__UpdateMotionAndWingPose` | DATA xref `0x005e0e94`; updates motion/trails, wing pose/blend, speed-scaled vector state, and dispatches owner vfunc `+0x70`. |
| `0x00422760` | `CCarverAI__OpenWings` | Call xref from the attack/update handler; resolves and plays the wing-open animation, then writes opening state. |
| `0x004227a0` | `CCarverAI__CloseWings` | Four call xrefs from Carver AI event/update paths; resolves and plays wing-close behavior. |
| `0x004227e0` | `CCarverAI__OnHit` | DATA xref `0x005e0e28`; hit override with explicit two-stack-argument cleanup shape. |
| `0x00422820` | `CCarverAI__Fire` | DATA xref `0x005e0e78`; fire/animation helper that returns `0`; runtime weapon effect remains separate proof. |
| `0x00422930` | `CCarverAI__SetLastAttackTime` | Call xref from `CCarverAI__CheckNearbyEnemies`; copies global time to the last-attack timestamp field. |
| `0x00422940` | `CCarverAI__IsRecentlyAttacked` | Call xref from `CCarverGuide__AcquireNearestTargetReader`; cooldown predicate over the last-attack timestamp. |
| `0x00422970` | `CCarverAI__CanStartAttack` | DATA xref `0x005e0f2c`; attack-start predicate bounded to static wing/cooldown gating. |
| `0x004229b0` | `CarverAimGlobals__ResetVector` | DATA xref `0x006220e0`; resets Carver aim/vector globals. |
| `0x004229d0` | `CarverAimGlobals__InitMatrix` | DATA xref `0x006220e4`; initializes Carver aim/orientation matrix globals. |
| `0x00422aa0` | `CCarverAI__RefreshTargetReaderAndScheduleMove` | DATA xref `0x005d9468`; event handler for target reader refresh, move scheduling, and wing-close behavior. |
| `0x00422b90` | `CCarverAI__UpdateAttackAndReschedule` | DATA xref `0x005d946c`; event handler for attack update and timer rescheduling. |
| `0x00422db0` | `CCarverAI__CheckNearbyEnemies` | Call xref from the Carver AI update handler; mapwho nearby-enemy scan and last-attack update. |
| `0x00422f90` | `CCarverGuide__ctor` | Call xref from `CCarver__Init`; installs guide behavior over the air-guide constructor path. |
| `0x00422fd0` | `CCarverGuide__dtor_base` | Call xref from the scalar-deleting wrapper; guide destructor-base cleanup. |
| `0x00423490` | `CCarverGuide__HandleEvent` | DATA xref `0x005d947c`; guide event handler for target refresh / forwarding to air-guide behavior. |
| `0x00423510` | `CCarverGuide__AcquireNearestTargetReader` | Call xref from `CCarverGuide__HandleEvent`; nearest target reader refresh. |
| `0x0050f340` | `CCarver__Destructor_VFunc01` | Destructor vfunc body clearing owned pointer sets/global-list node before forwarding to `CUnit__dtor_base`. |

Prior context:

- Wave915 re-reviewed Carver AI/guide targeting helpers read-only.
- Wave945 recovered three CCarver-local vtable boundaries.
- Wave965 re-reviewed the Carver init/combat/wing helper band.
- Wave989 re-reviewed the CarverGuide lifecycle trio.
- Wave1125 tag-normalized the score-23 Carver targeting current-risk pair.
- Wave1129 tag-normalized `CCarver__Init` and `CCarverAI__CanStartAttack` inside a lifecycle/init cluster.

Backup:

`G:\GhidraBackups\BEA_20260606-095003_post_wave1178_carver_current_risk_consolidation_review_verified`

Backup verification: `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.

Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference; actual no-noticeable-difference parity still requires later runtime, asset, visual, control, timing, save, patch, and rebuild proof.

What this proves:

- The twenty target function rows exist in the saved Ghidra database.
- Saved names/signatures/comments are stable under fresh metadata/decompile read-back.
- Wave1178 tags are present on all twenty target rows after apply/final-dry.
- The Carver init/AI/wing/attack/guide/destructor slice is now explicitly counted against the active Wave1108 current-risk denominator.

What remains separate proof:

- Runtime Carver behavior.
- Runtime wing timing.
- Runtime attack/target selection behavior.
- Runtime guide/navigation behavior.
- Exact `CCarver` / `CCarverAI` / `CCarverGuide` concrete layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1178; wave1178-carver-current-risk-consolidation-review; 715/1179 = 60.64%; 20 Carver current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 464; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=20 skipped=0; tags_added=206; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consult used; Codex root final judgment; consult narrowed to 11 rows; root widened to 20-row coherent Carver slice; 0 / 0 / 0; 6411/6411 = 100.00%; 23 xref rows; 873 instruction rows; CCarver__Init; CCarverAI__dtor_base; CCarver__UpdateMotionAndWingPose; CCarverAI__OpenWings; CCarverAI__CloseWings; CCarverAI__Fire; CCarverAI__CheckNearbyEnemies; CCarverGuide__AcquireNearestTargetReader; CCarver__Destructor_VFunc01; G:\GhidraBackups\BEA_20260606-095003_post_wave1178_carver_current_risk_consolidation_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
