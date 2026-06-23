# Ghidra UnitAI Activation Signature Correction - 2026-05-12

Status: public-safe static reverse-engineering evidence.

## Scope

Wave 325 revisited the UnitAI activation, render-cache, reader/heading, and Component-AI forwarding cluster after fresh metadata, decompile, xref, instruction, vtable RTTI, and tag read-back. This wave saved twelve Ghidra signatures/comments/tags, corrected two stale owner labels, and moved one stale function boundary from `0x00429280` to the true entry at `0x00429270`.

A fresh out-of-repo backup of the live Ghidra project was made before this accounting pass. Backup verification reported `19` files, `151620487` bytes, and `DiffCount=0`.

## Saved Corrections

| Address | Saved signature | Notes |
| --- | --- | --- |
| `0x00428710` | `void * __thiscall CUnitAI__GetRenderPosFromActorOrCache(void * this, void * outRenderPos, void * unused)` | Render-position virtual slot that returns the caller output buffer after forwarding to actor render position or copying cached component position state. |
| `0x00428770` | `void * __thiscall CUnitAI__GetRenderOrientationFromActorOrCache(void * this, void * outRenderOrientation, void * unused)` | Render-orientation virtual slot that returns the caller output buffer after forwarding to actor render orientation or copying cached orientation state. |
| `0x00428800` | `bool __fastcall CUnitAI__HandleTriggerEventAndMoveToOffset(void * this)` | Trigger/event handler with destroyed-state, child-release, event-scheduling, active-reader offset, and movement-dispatch context. |
| `0x004289b0` | `bool __fastcall CUnitAI__AdvanceActivationAnimationState(void * this)` | Activation animation state machine over hit, retract, normal, activate, activated, and deactivated animation tokens. |
| `0x00428b50` | `void __thiscall CUnit__SetReaderAndComputeRelativeYaw(void * this, void * reader, void * readerContext, int unusedMode)` | Active-reader setter with reader/context storage and relative-yaw computation; the third observed stack argument remains unused in the current decompile. |
| `0x00428bc0` | `double __fastcall CUnitAI__GetTargetHeadingWithOffset(void * this)` | Returns active-reader heading plus relative-yaw offset, or the zero heading constant when no reader exists. |
| `0x00428c70` | `void __fastcall CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action(void * this)` | Shared UnitAI step that resets field-D0 context and dispatches vtable slot `0x38` when flag bit `4` is set. |
| `0x00428cb0` | `void __fastcall CUnitAI__PlayHitAnimationAndSetFlag(void * this)` | Corrects the prior `CExplosionInitThing` owner label to a UnitAI animation helper that plays the Hit token and sets field `+0x2bc`. |
| `0x00428cf0` | `void __thiscall CUnitAI__ForwardCommandToAttachedNodeThenDispatch(void * this, int command, int unusedStackParam)` | Command-forwarding helper; the decompile still carries an EDI-sourced score value, so caller-context parameter recovery remains open. |
| `0x00428d50` | `void __fastcall CUnitAI__PlayActivateAnimationOrFinalizeActivated(void * this)` | Corrects the prior generic virtual-slot label to activation-token playback/finalization context. |
| `0x00428e80` | `void __fastcall CComponentAI__ClearReaderIfTargetDestroyedThenForward(void * this)` | Corrects the prior generic virtual-slot label using `CComponentBomberAI` and `CFenrirMainGunAI` vtable context. |
| `0x00429270` | `void __fastcall CUnitAI__UpdateHeadingTowardTargetClamped(void * turnContext)` | Boundary correction: the true entry includes the prologue that loads the UnitAI pointer from the turn context before the heading/clamp logic. |

All twelve targets now carry saved Ghidra function tags: `signature-hardened`, `static-reaudit`, `unitai-activation-wave325`, and `unitai-system`. The owner-corrected targets also carry `owner-corrected`; the boundary-corrected target carries `boundary-corrected`.

## Vtable RTTI Context

| Vtable address | Read-back type name |
| --- | --- |
| `0x005d96b4` | `CComponentBomberAI` |
| `0x005d9680` | `CFenrirMainGunAI` |

## Validation

| Check | Result |
| --- | --- |
| `CreateFunctionsFromAddressList.java dry` for `0x00429270` | `would_create=1 failed=0` before the boundary move |
| `ApplyUnitAiActivationSignatureCorrection.java dry` | `updated=0 skipped=12 renamed_or_moved=0 missing=0 bad=0`; clean dry run |
| `ApplyUnitAiActivationSignatureCorrection.java apply` | `updated=12 skipped=0 renamed_or_moved=6 missing=0 bad=0`; `REPORT: Save succeeded` |
| Metadata read-back | `12/12` targets |
| Decompile read-back | `12/12` targets |
| Xref read-back | `25` rows |
| Instruction read-back | `1212` rows, `0` missing targets |
| Tag read-back | `12/12` targets |
| Vtable RTTI read-back | Confirms `CComponentBomberAI` and `CFenrirMainGunAI` context for the Component-AI slot |
| Quality queue | `5884` total functions, `773` commented, `5111` commentless, `1993` undefined signatures, `2288` `param_N` signatures |
| Focused probe | `PASS`, schema `1`, `12` targets and `3` owner/boundary corrections |

## What This Proves

- The saved Ghidra project now has hardened signatures, comments, and tags for twelve UnitAI/Component-AI activation and heading-adjacent targets.
- The prior `0x00429280` boundary for `CUnitAI__UpdateHeadingTowardTargetClamped` was stale; the saved function now starts at `0x00429270`.
- The saved owner labels for `0x00428cb0` and `0x00428e80` were corrected away from older, too-generic or caller-derived labels.
- The final read-back no longer shows the stale boundary artifact that left `unaff_ESI` / `unaff_EDI` style prologue symptoms in the heading helper.

## What This Does Not Prove

- Runtime UnitAI activation, steering, movement, render-cache, command-forwarding, or Component-AI cleanup behavior.
- Exact source-body identity or final virtual method names for every slot.
- Concrete object layouts, local variable names, structure types, exhaustive tags, or rebuild parity.
- Any mutation or execution of `BEA.exe`.

## Public/Private Boundary

This note includes only repo-relative paths, public addresses, saved names/signatures/tags, aggregate counts, and public-safe summaries. Raw decompile exports, instruction dumps, private project backups, and generated probe JSON remain outside public release scope.
