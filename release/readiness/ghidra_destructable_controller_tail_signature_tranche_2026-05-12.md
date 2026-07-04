# Ghidra Destructable Controller Tail Signature Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 350 continued the saved-Ghidra static re-audit at the destructable controller tail/name-dispatch/lifecycle cluster around `0x00444450..0x00444c10`. It saved eight names, signatures, comments, and tags after fresh metadata, decompile, xref, instruction, tag, vtable, caller, and callsite read-back.

Stuart's checked source snapshot does not currently include a full `DestructableSegmentsController.cpp` body, so this wave treats the names as behavior-backed retail static labels rather than exact source-body closure.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x00444450` | `CDestructableSegmentsController__SetSegmentField0CByName` | Name-dispatch helper with float stack argument, mesh-node/name lookup context, and segment field `+0x0c` write. |
| `0x004444b0` | `CDestructableSegmentsController__SetSegmentFields0C10ByName` | Name-dispatch helper with float stack argument, writes to segment fields `+0x0c/+0x10`, and cached active-value refresh context. |
| `0x00444520` | `CDestructableSegmentsController__FindSegmentByName` | Name-dispatch lookup returning a tracked segment pointer, with `CHiveBoss__Init` caller context and warning-path evidence. |
| `0x00444580` | `CDestructableSegmentsController__SetAllSegmentsField0C` | Bulk setter over the tracked segment array with one float stack argument and field `+0x0c` write evidence. |
| `0x004445b0` | `CDestructableSegmentsController__SetSegmentActiveFlagByName` | Name-dispatch helper with bool/int active flag argument, write to segment field `+0x1c`, and cached active-value refresh context. |
| `0x00444660` | `CDestructableSegmentsController__Init` | Unit-init reached controller initializer for the `this+0x178` controller pointer, mesh/root traversal, segment-array allocation, recursive node processing, and behavior/warning setup. |
| `0x004449c0` | `CDestructableSegmentsController__CreateSegment` | Segment factory over kinds `0..3` with core init and three observed vtable variants: `0x005db148`, `0x005db114`, and `0x005db0e0`. |
| `0x00444c10` | `CDestructableSegmentsController__ProcessNode` | Recursive mesh-node processor with classification by flags/name prefixes/child state, segment creation/registration, and recursive child traversal. |

## Evidence

- Initial read-only exports covered the eight targets with metadata, decompile, xrefs, instructions, tags, vtable slots, caller decompile, and callsite instruction read-back.
- `tools/ApplyDestructableControllerTailSignatureTranche.java` dry/apply saved the eight target names, signatures, comments, and tags; final apply printed `REPORT: Save succeeded`.
- Final read-back verified `8/8` metadata rows, `8/8` decompile exports, `10` xref rows, `1816` instruction rows, `8/8` tag rows, `230` callsite instruction rows, `10` callsite evidence hits, and `8` return-evidence hits.
- Caller read-back confirmed `CUnit__Init` calls `CDestructableSegmentsController__Init`; the stale `0x00443f60` caller entry remains a non-function entry and is not a tranche failure.
- `py -3 tools\ghidra_destructable_controller_tail_signature_tranche_probe_test.py` passed `2/2`; `py -3 -m py_compile tools\ghidra_destructable_controller_tail_signature_tranche_probe.py tools\ghidra_destructable_controller_tail_signature_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-destructable-controller-tail-signature-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database baseline reports `5978` functions, `0` weak functions, `1951` undefined signatures, and `2078` `param_N` signatures.
- The refreshed quality queue reports `1143` commented functions, `4835` commentless functions, `1951` undefined signatures, and `2078` `param_N` signatures.
- The current comment-backed static RE proxy is still below `20%`: `1143/5978 = 19.12%`; the stricter comment-plus-clean-signature proxy is `1080/5978 = 18.07%`.
- The post-mutation live Ghidra backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260512_204318_post_wave350_destructable_controller_tail_verified` with `19` files, `152865671` bytes, and `HashDiffCount=0`.

## Claim Boundary

This is saved static Ghidra name/signature/comment/tag evidence only. It improves the current destructable controller tail/name-dispatch/lifecycle cluster, but it does not prove exact Stuart source identity, a certified class layout, local variable recovery, structure typing, runtime destruction, cascade, random-damage, rubble, mesh behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/destructable-controller-tail-wave350/current/`.
