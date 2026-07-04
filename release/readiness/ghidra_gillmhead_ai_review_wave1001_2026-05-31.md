# Ghidra GillMHeadAI Review Wave1001 Readiness Note

Status: complete static read-back evidence with two comment/tag corrections
Date: 2026-05-31
Scope: `gillmhead-ai-review-wave1001`

Wave1001 re-reviewed the Wave911 risk-ranked `CGillMHeadAI` component, animation-state, aim-transform, and ballistic-targeting island around the prior Wave390 owner corrections. Fresh metadata, tag, xref, instruction, decompile, vtable, and pointer-table evidence found two stale/imprecise comment claims, so this wave saved comment/tag corrections at `0x0047a900 CGillMHeadAI__AdvanceOpenAttackCloseState` and `0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader`. The pass made no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary targets:

| Address | Read-back evidence |
| --- | --- |
| `0x0047a760 CGillMHead__CreateGillMHeadAIComponent` | Pointer table `0x005e42d8` slot `63`; allocates the `0x64` byte type-`0x16` component, initializes through `CWarspite__Init`, installs `CGillMHeadAI` vtable `0x005dbcec`, clears `+0x60`, and stores the component at owner `+0x13c`. |
| `0x0047a7f0 CGillMHeadAI__ScalarDeletingDestructor` | `CGillMHeadAI` vtable `0x005dbcec` slot `1`; wraps `CGillMHeadAI__Destructor` and optionally frees through the memory manager when flags bit `0` is set. |
| `0x0047a810 CGillMHeadAI__Destructor` | Restores base `CUnitAI` vtable `0x005d8d1c`, removes active-reader/resource handles at `+0x28`, `+0x24`, and `+0x0c`, then calls `CMonitor__Shutdown`. |
| `0x0047a8b0 CGillMHeadAI__TryTransitionIdleToOpen` | Pointer table `0x005e42d8` slot `30`; checks `idle`, gates through `CUnit__UpdateDeployStateAndChargeEffects`, and requests the `open` animation. |
| `0x0047a900 CGillMHeadAI__AdvanceOpenAttackCloseState` | Pointer table `0x005e42d8` slot `3`; comment corrected to name `CUnit__HasAnyLinkedUnitBeforeTargetTimeout` before the close transition and `SharedUnitAnimation__PlayAnimationByNameIfPresent` for animation playback requests. |
| `0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader` | `CGillMHeadAI` vtable `0x005dbcec` slot `3`; comment corrected from stale `CWarspite__UpdateAimTransformAndAttachTargetReader` wording to the observed `CUnit__ForwardAimTransformAndAttachTargetReader` handoff after the 100-unit owner-facing-vector aim transform. |
| `0x0047b090 CGillMHeadAI__UpdateTargetBallisticArcFlags` | `CGillMHeadAI` vtable `0x005dbcec` slot `4`; clears stale target-reader context and updates two ballistic firing-readiness flags through `CUnit__CanFireAtTarget_BallisticArcB/A`. |

Fresh read-back evidence:

- Dry/apply/final dry: `updated=0 skipped=2 comment_only_updated=2 tags_added=8 missing=0 bad=0`, then `updated=2 skipped=0 comment_only_updated=2 tags_added=8 missing=0 bad=0`, then `updated=0 skipped=2 comment_only_updated=0 tags_added=0 missing=0 bad=0`, each with `REPORT: Save succeeded`.
- Exports: `7` metadata rows, `7` tag rows, `7` xref rows, `320` body-instruction rows, `7` decompile rows, `16` vtable-slot rows, `2` vtable type rows, and `64` pointer-table rows.
- Existing Wave390 probe passed after the correction: `test:ghidra-gillmhead-ai-wave390`.
- Queue closure remains `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress advances to `472/1408 = 33.52%`.
- Expanded static surface progress advances to `613/1478 = 41.47%`.
- Wave911 top-500 risk-ranked coverage advances to `355/500 = 71.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-104623_post_wave1001_gillmhead_ai_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1001; `gillmhead-ai-review-wave1001`; `0x0047a760 CGillMHead__CreateGillMHeadAIComponent`; `0x0047a900 CGillMHeadAI__AdvanceOpenAttackCloseState`; `CUnit__HasAnyLinkedUnitBeforeTargetTimeout`; `0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader`; `CUnit__ForwardAimTransformAndAttachTargetReader`; `472/1408 = 33.52%`; `613/1478 = 41.47%`; `355/500 = 71.00%`; `6222/6222 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260531-104623_post_wave1001_gillmhead_ai_review_verified`; comment/tag mutation only.

What this proves:

- The reviewed `CGillMHeadAI` rows exist in the saved Ghidra project with the expected names, signatures, comments, and tags.
- The saved Wave390 owner/signature corrections remain coherent after fresh vtable, pointer-table, xref, decompile, and instruction read-back.
- The two corrected rows now match current static evidence for the timeout gate and aim-transform handoff.

What remains unproven:

- Exact Stuart source-body identity.
- Concrete `CGillMHeadAI`, owner, target-reader, animation-state, or ballistic flag layouts.
- Runtime GillMHead animation, targeting, or ballistic firing behavior.
- BEA patching behavior.
- Rebuild parity.
