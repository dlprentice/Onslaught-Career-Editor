# Wave1132 Component/UnitAI Current-Risk Review

Status: complete static tag-normalization evidence
Date: 2026-06-05
Scope: `wave1132-component-ai-current-risk-review`

Wave1132 accounts for `10 rows` from the Wave1108 current focused continuity denominator as a component/active-reader UnitAI residual cluster. This wave uses fresh Ghidra export evidence plus narrow tag-only normalization. Current focused accounting moves to `178/1179 = 15.10%` of the continuity denominator. The current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1001. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Covered anchors:

| Address | Static evidence |
| --- | --- |
| `0x00427b80 CComponent__VFunc_09_00427b80` | Component init-like virtual body clears active-reader/component-transform fields, initializes the config/init record, applies the `Thunderhead Main Gun` special case, selects `Normal` or `Activated`, and clears cached state fields. |
| `0x00427f90 CComponentBomberAI__scalar_deleting_dtor` | RTTI/vtable-backed scalar-delete wrapper for `CComponentBomberAI`; calls `CComponentBomberAI__dtor_base`, checks flags bit 0, and optionally frees through `OID__FreeObject`. |
| `0x00427fb0 CComponentBomberAI__dtor_base` | Destructor-base body resets to the shared UnitAI vtable, removes tracked set slots `+0x28/+0x24/+0x0c`, then calls `CMonitor__Shutdown`. |
| `0x00428050 CFenrirMainGunAI__scalar_deleting_dtor` | RTTI/vtable-backed scalar-delete wrapper for `CFenrirMainGunAI`; calls `CFenrirMainGunAI__dtor_base`, checks flags bit 0, and optionally frees through `OID__FreeObject`. |
| `0x00428070 CFenrirMainGunAI__dtor_base` | Parallel destructor-base body for the Fenrir main-gun component AI path; same monitored-set cleanup shape as the bomber AI row. |
| `0x00428710 CUnitAI__GetRenderPosFromActorOrCache` | Render-position virtual slot returns the caller output buffer after either forwarding to `CActor__GetRenderPos` or refreshing/copying cached component-position fields. |
| `0x00428770 CUnitAI__GetRenderOrientationFromActorOrCache` | Render-orientation virtual slot returns the caller output buffer after either forwarding to `CActor__GetRenderOrientation` or refreshing/copying the cached orientation matrix. |
| `0x00428c70 CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action` | Shared step helper calls `CUnit__ResetFieldD0ToGlobalThreshold` and dispatches vtable slot `+0x38` when flag bit 4 is set. |
| `0x00428d50 CUnitAI__PlayActivateAnimationOrFinalizeActivated` | Activation helper looks up `Activate`; if missing, it clears activation state and calls `CUnit__VFunc22_ActivateLinkedTargetsAndChildren`, otherwise it plays the animation through vtable slot `+0xf0`. |
| `0x00428e80 CComponentAI__ClearReaderIfTargetDestroyedThenForward` | Shared Component-AI vtable slot used by `CComponentBomberAI` and `CFenrirMainGunAI`; clears the active reader if the reader target has flag bit 4 set, then forwards to vtable slot `+0x2c`. |

Context rows re-read: `0x004239f0 CUnitAI__InitDefaults_AutoConfigTestPath`, `0x00427dd0 CComponent__CreateWeaponComponent`, `0x00428110 CUnitAI__UpdateActivationStateAndSpawnPickup`, `0x00428500 CUnitAI__RefreshCachedComponentTransform`, `0x00428800 CUnitAI__HandleTriggerEventAndMoveToOffset`, `0x004289b0 CUnitAI__AdvanceActivationAnimationState`, `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw`, `0x00428bc0 CUnitAI__GetTargetHeadingWithOffset`, `0x00428cb0 CUnitAI__PlayHitAnimationAndSetFlag`, and `0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped`.

Mutation status:

- Tag-only normalization.
- `91 tags` added.
- No rename.
- No signature change.
- No comment change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

Evidence:

- Pre metadata/tag/xref/instruction/decompile exports: `10` / `10` / `21` / `326` / `10`.
- Context metadata/tag/xref/instruction/decompile exports: `10` / `10` / `16` / `1173` / `10`.
- `ApplyComponentAiCurrentRiskWave1132.java dry`: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=91 missing=0 bad=0`.
- `ApplyComponentAiCurrentRiskWave1132.java apply`: `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=91 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyComponentAiCurrentRiskWave1132.java final dry`: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `10` / `10` / `21` / `326` / `10`.
- Pre/post metadata, instruction, and xref exports match exactly.
- Queue quality refresh after the Ghidra write reported `total_functions=6410 commented_functions=6410`.
- Final backup after the queue refresh: `G:\GhidraBackups\BEA_20260605-093432_post_wave1132_component_ai_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-090018_post_wave1131_heightfield_current_risk_review_verified`.
- Codex read-only consult agreed the cluster is coherent when scoped as component/active-reader UnitAI residuals, not as one exact source class.

What this proves:

- The ten target rows still exist in the saved Ghidra project with the expected names and signatures.
- The saved tags include `wave1132-component-ai-current-risk-review`, `wave1132-readback-verified`, `current-risk-review`, `component-ai-current-risk-review`, and the per-row score tags.
- The comments, xrefs, instruction windows, and decompile rows remain coherent with prior Wave324/Wave325/Wave979/Wave1115 component and UnitAI evidence.
- The Ghidra project was backed up after the write and after the queue refresh.

What remains separate:

- Runtime Component or UnitAI behavior.
- Runtime activation, render-cache, active-reader, or component cleanup behavior.
- Exact source-body identity.
- Concrete `CComponent`, `CComponentBomberAI`, `CFenrirMainGunAI`, `CUnitAI`, active-reader, component-transform, monitored-set, or vtable-slot layouts.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
