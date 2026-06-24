# Ghidra Destructable Segment Signature Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 348 continued the saved-Ghidra static re-audit at the destructable/destroyable segment cluster around `0x004425a0..0x00442f60`. It saved twelve names, signatures, comments, and tags after fresh metadata, decompile, xref, instruction, tag, vtable, and caller read-back.

Stuart's checked source snapshot does not currently include a full `DestructableSegmentsController.cpp` body, so this wave treats the names as behavior-backed retail static labels rather than exact source-body closure.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x004425a0` | `CDestructableSegment__Init` | Base segment initializer with controller/index/parent/value fields, child list setup, base vtable, active flag, and global segment-monitor membership. |
| `0x00442640` | `CDestroyableSegment__scalar_deleting_dtor` | Corrected scalar-deleting destructor wrapper; calls the destructor body and frees when flags bit `0` is set. |
| `0x00442660` | `CDestroyableSegment__dtor_base` | Corrected destructor body; removes from the global segment monitor, deletes children, clears the child set, and shuts down the monitor base. |
| `0x00442700` | `CDestructableSegment__RegisterChild` | Corrects the older broad register wording; this body adds a child segment to the parent child list, not global monitor registration. |
| `0x00442710` | `CDestroyableSegment__SpawnConfiguredPickup` | Corrects the stale `CExplosionInitThing` owner label; static evidence shows a configured pickup creation path from segment/controller context. |
| `0x00442890` | `CDestroyableSegment__SumActiveValueRecursive` | Recursive active-value sum over child segments. |
| `0x00442900` | `CDestructableSegment__GetTotalHealth` | Recursive total health/value query used by controller initialization/root health context. |
| `0x004429a0` | `CDestructableSegment__DispatchChildDestructionEvents` | Child break dispatch helper with immediate dispatch or event `3000` scheduling. |
| `0x00442a80` | `CDestructableSegment__SetSubtreeActiveFlagRecursive` | Recursive active-flag setter for a segment subtree. |
| `0x00442ac0` | `CDestructableSegment__PropagateDamageToChildren` | Child fanout helper invoking a damage-style vtable slot. |
| `0x00442b20` | `CDestroyableSegment__VFunc_08_HandleSegmentBreak` | Corrected from a generic slot label; marks segment break state, updates linked segment/unit state, and dispatches child events. |
| `0x00442f60` | `CDestroyableSegment__VFunc_10_SpawnRubbleEffects` | Corrected from a generic slot label; resolves rubble mesh/effect context, applies landscape damage, and can call the configured pickup helper. |

## Evidence

- Initial read-only exports covered the twelve targets with metadata, decompile, xrefs, instructions, tags, vtable slots, and caller decompile read-back.
- `tools/ApplyDestructableSegmentSignatureTranche.java` dry/apply saved the twelve target names, signatures, comments, and tags; final apply printed `REPORT: Save succeeded`.
- Final read-back verified `12/12` metadata rows, `12/12` decompile exports, `44` xref rows, `996` instruction rows, `12/12` tag rows, and `6` vtable evidence hits.
- `py -3 tools\ghidra_destructable_segment_signature_tranche_probe_test.py` passed `2/2`; `py -3 -m py_compile tools\ghidra_destructable_segment_signature_tranche_probe.py tools\ghidra_destructable_segment_signature_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-destructable-segment-signature-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database baseline reports `5978` functions and `0` weak functions. The refreshed quality queue reports `1117` commented functions, `4861` commentless functions, `1955` undefined signatures, and `2099` `param_N` signatures.
- The current comment-backed static RE proxy is still below `20%`: `1117/5978 = 18.69%`; the stricter comment-plus-clean-signature proxy is `1054/5978 = 17.63%`.
- The post-mutation live Ghidra backup was verified on `G:` with `19` files, `152832903` bytes, and `HashDiffCount=0`.

## Claim Boundary

This is saved static Ghidra name/signature/comment/tag evidence only. It improves the current destructable/destroyable segment cluster, but it does not prove exact Stuart source identity, a certified class layout, local variable recovery, structure typing, runtime destruction or rubble behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/destructable-segment-wave348/current/`.
