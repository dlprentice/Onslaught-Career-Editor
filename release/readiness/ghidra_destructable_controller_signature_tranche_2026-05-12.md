# Ghidra Destructable Controller Signature Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 349 continued the saved-Ghidra static re-audit at the destructable controller/core/swap segment cluster around `0x004433f0..0x004443f0`. It saved eighteen names, signatures, comments, and tags after fresh metadata, decompile, xref, instruction, tag, vtable, and caller read-back.

Stuart's checked source snapshot does not currently include a full `DestructableSegmentsController.cpp` body, so this wave treats the names as behavior-backed retail static labels rather than exact source-body closure.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x004433f0` | `CDestroyableCoreSegment__AreCoreChildrenDestroyed` | Corrects the older controller-owner label; callers pass the root/core segment pointer, and the helper walks core children for cascade/threshold context. |
| `0x00443480` | `CDestroyableCoreSegment__Init` | Core/primary segment initializer with base init, core fields, component ordinal, and vtable `0x005db06c`. |
| `0x004434d0` | `CDestroyableCoreSegment__scalar_deleting_dtor` | Scalar-deleting destructor wrapper for the core/primary segment. |
| `0x004434f0` | `CDestroyableCoreSegment__dtor_base` | Destructor body that removes monitor membership, deletes children, clears the child set, and shuts down the monitor base. |
| `0x004435f0` | `CDestroyableCoreSegment__VFunc_03_ApplyDamage` | Core/primary segment damage-style vfunc slot 3 with damage amount/time recording and break/rubble dispatch context. |
| `0x00443780` | `CDestroyableSwapSegment__VFunc_03_ApplyDamage` | Swap-segment damage-style vfunc slot 3 with damage recording, child destruction, swap/rubble, and controller/core state context. |
| `0x00443810` | `CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak` | Swap-segment break handler that runs its one-shot swap/rubble path, then delegates to the base break handler. |
| `0x004439c0` | `CDestroyableSegment__SharedVFunc_08_HandleChildBreak` | Shared leaf/end segment vfunc slot 8 handler that can dispatch swap/rubble before delegating to the base break handler. |
| `0x00443fc0` | `CDestructableSegmentsController__Ctor` | Controller constructor-like initializer with corrected argument names for stored fields. |
| `0x00444000` | `CDestructableSegmentsController__Dtor` | Controller destructor helper for segment-array/root cleanup. |
| `0x00444030` | `CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold` | Indexed segment damage path with callback/threshold update context. |
| `0x00444160` | `CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold` | Random-damage burst path with temporary deduplication set and shared threshold update logic. |
| `0x004442d0` | `CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex` | Supersedes the older field-only getter label; damage vfuncs write the observed time source to field `+0x14`. |
| `0x00444300` | `CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex` | Supersedes the older field-only getter label; damage vfuncs write raw damage amount to field `+0x18`. |
| `0x00444330` | `CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive` | Controller health query backed by recursive active-value sum. |
| `0x00444370` | `CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive` | Controller health query backed by root total-health traversal. |
| `0x004443b0` | `CDestructableSegmentsController__GetCachedTotalHealthIfAnyActive` | Controller health query backed by cached total-health field. |
| `0x004443f0` | `CDestructableSegmentsController__TriggerCoreCascadeIfEligible` | Renames the older threshold-exceeded label to avoid overclaiming the threshold direction; static evidence shows an eligibility gate and child-damage cascade trigger. |

## Evidence

- Initial read-only exports covered the eighteen targets with metadata, decompile, xrefs, instructions, tags, vtable slots, and caller decompile read-back.
- `tools/ApplyDestructableControllerSignatureTranche.java` dry/apply saved the eighteen target names, signatures, comments, and tags; final apply printed `REPORT: Save succeeded`.
- Final read-back verified `18/18` metadata rows, `18/18` decompile exports, `22` xref rows, `666` instruction rows, `18/18` tag rows, and `6` vtable evidence hits.
- `py -3 tools\ghidra_destructable_controller_signature_tranche_probe_test.py` passed `2/2`; `py -3 -m py_compile tools\ghidra_destructable_controller_signature_tranche_probe.py tools\ghidra_destructable_controller_signature_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-destructable-controller-signature-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database baseline reports `5978` functions, `0` weak functions, `1954` undefined signatures, and `2083` `param_N` signatures.
- The refreshed quality queue reports `1135` commented functions, `4843` commentless functions, `1954` undefined signatures, and `2083` `param_N` signatures.
- The current comment-backed static RE proxy is still below `20%`: `1135/5978 = 18.99%`; the stricter comment-plus-clean-signature proxy is `1072/5978 = 17.93%`.
- The post-mutation live Ghidra backup was verified at `G:\GhidraBackups\BEA_20260512_201011_post_wave349_destructable_controller_verified` with `19` files, `152865671` bytes, and `HashDiffCount=0`.

## Claim Boundary

This is saved static Ghidra name/signature/comment/tag evidence only. It improves the current destructable controller/core/swap segment cluster, but it does not prove exact Stuart source identity, a certified class layout, local variable recovery, structure typing, runtime destruction, cascade, random-damage, or rubble behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/destructable-controller-wave349/current/`.
