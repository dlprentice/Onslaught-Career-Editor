# Ghidra Destructable Vtable Tail Boundary Tranche - 2026-05-12

Status: GREEN public-safe static Ghidra correction evidence.

This wave continued the saved-Ghidra static re-audit on destructable segment vtable tails. It recovered seventeen additional function starts and saved behavior-bounded names, signatures, comments, and tags after serialized dry/apply/read-back. Stuart's checked source snapshot does not currently include the full `DestructableSegmentsController.cpp` body, so these labels are behavior-backed static retail names, not exact source-body closure.

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x00442960` | `CDestroyableSegment__VFunc_03_ApplyDamage` | Base slot-3 damage-style helper that records last damage context. |
| `0x0055df1f` | `CRT__Purecall_0055df1f` | Purecall-style CRT handler that calls `__amsg_exit(0x19)`. |
| `0x00442b00` | `CDestroyableSegment__VFunc_06_CheckParentBreakGate` | Parent break-gate helper using parent vtable slot `+0x18`. |
| `0x004bfc60` | `SharedVFunc__ReturnFloatZero_004bfc60` | Shared vtable target returning float zero. |
| `0x00405ee0`, `0x004059c0`, `0x004014a0` | shared return-value helpers | Shared vtable targets returning `3`, `2`, and `1`. |
| `0x004436d0` | `CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch` | Core event dispatcher for `3000` and `3002` event records. |
| `0x004435c0` | `CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate` | Core parent gate with field `+0x4c` and parent-slot context. |
| `0x004434c0` | `CDestroyableCoreSegment__VFunc_07_GetCoreField48` | Core field reader returning the float at `this+0x48`. |
| `0x00443660` | `CDestroyableCoreSegment__VFunc_08_HandleCoreBreakOrCascade` | Core break/cascade helper with event `3002` context. |
| `0x00443590` | `CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields` | Core damage-scale recompute helper. |
| `0x00442d40` | `CDestroyableSegment__VFunc_09_UpdatePickupAndChildSlot09` | Shared slot-9 update helper with configured-pickup and child-slot dispatch context. |
| `0x00442870` | `CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields` | Shared slot-11 damage-scale recompute helper. |
| `0x00443ea0` | `CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak` | Component break helper with owner-callback context. |
| `0x00443a20` | `CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects` | End-segment effect helper that calls the base rubble/effects path. |
| `0x004439f0` | `CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields` | End-segment damage-scale recompute helper. |

Evidence:

- `tools/ApplyDestructableVtableTailBoundaryTranche.java` dry/apply passed with `targets=17 changed_or_would_change=17 failed=0`; the apply reported `REPORT: Save succeeded`.
- Read-back verified `21` metadata rows, `21` decompile exports, `2113` xref rows, `4641` instruction rows, `21` tag rows, `72` vtable-slot rows, `17` vtable evidence hits, `10` xref evidence hits, `17` instruction evidence hits, and no stale-token or comment-overclaim failures.
- Focused validation passed: `py -3 tools\ghidra_destructable_vtable_tail_boundary_probe_test.py`, `py -3 -m py_compile tools\ghidra_destructable_vtable_tail_boundary_probe.py tools\ghidra_destructable_vtable_tail_boundary_probe_test.py`, and `cmd.exe /c npm run test:ghidra-destructable-vtable-tail-boundary`.
- The refreshed all-functions baseline reports `5999` total functions, `0` legacy weak names, `1951` undefined signatures, and `2075` `param_N` signatures.
- The refreshed quality queue reports `5999` functions, `1168` commented functions, `4831` commentless functions, `1951` undefined signatures, and `2075` `param_N` signatures.
- Current confirmation proxies remain telemetry only: comment-backed `1168/5999 = 19.47%`, strict clean-signature `1105/5999 = 18.42%`. The `20%` value is not a milestone or acceptance gate.
- The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260512_223409_post_wave353_destructable_vtable_tail_verified` with `19` files, `152931207` bytes, and `HashDiffCount=0`.

Raw proof remains ignored under `subagents/ghidra-static-reaudit/destructable-vtable-tail-wave353/current/`.

Claim boundary: this is static retail Ghidra evidence only. It corrects saved function boundaries, names, signatures, comments, and tags for seventeen destructable vtable-tail targets, but it does not prove exact source identity, concrete class layout, local/type recovery, runtime destruction/cascade/pickup/rubble behavior, BEA launch, game patching, or rebuild parity.
