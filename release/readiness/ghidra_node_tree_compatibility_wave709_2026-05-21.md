# Ghidra Node-Tree Compatibility Wave709 Readiness

Status: passed
Date: 2026-05-21

Wave709 node-tree compatibility saved six adjacent CFastVB node-tree compatibility/scoring rows with the `node-tree-compatibility-wave709` and `wave709-readback-verified` tags.

## Targets

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x00599d80` | `int __thiscall CFastVB__FlattenNodeTreeLeafByLinearIndex(void * this, void * node_tree, uint linear_leaf_index, void * out_leaf_scratch)` | `RET 0xc` and caller sites show parser context in ECX plus node tree, linear leaf index, and output leaf scratch. The helper walks wrapper kinds `1`, `5`, `7`, and `10`, descends to leaf kind `8`, writes normalized leaf scratch fields, and returns `0` or `0x80004005` on null/unknown paths. |
| `0x00599e48` | `int __stdcall CFastVB__ResolveCommonLeafFormat(void * left_leaf_scratch, void * right_leaf_scratch, void * out_common_format)` | `RET 0xc` and the caller at `0x0059a19d` show two leaf scratch records plus an output common-format slot; the helper uses compatibility tables at `0x005f2908/0x005f290c`. |
| `0x00599ffd` | `int __thiscall CFastVB__CompareNodePayloadBindingChain(void * this, void * left_payload, void * right_payload, void * right_binding_chain, int compare_flags)` | `RET 0x10` shows four cleaned stack arguments after ECX; the fourth cleaned argument is retained as ABI context even though the current decompile does not read it. The body compares payload descriptor/name context and linked binding records. |
| `0x0059a10a` | `int __thiscall CFastVB__ScoreNodeTreePairMismatchBits(void * this, void * left_node_tree, void * right_node_tree)` | `RET 0x8` removes the prior phantom third stack argument. The helper counts expanded leaves, flattens paired leaves, resolves common formats, and accumulates mismatch bits for count/format/flatten differences. |
| `0x0059a21f` | `int __thiscall CFastVB__AreNodeTreesCompatible(void * this, void * left_node_tree, void * right_node_tree, int relaxed_match)` | `RET 0xc` plus ECX use correct the prior `__stdcall` signature to `__thiscall`. The helper handles null-tree cases, scratch-expanded non-leaf trees, leaf shape/count/type constraints, a relaxed leaf-type path, and structural-equality fallback. |
| `0x0059a54d` | `int __thiscall CFastVB__ScoreNodeTreeMatch(void * this, void * source_payload, void * candidate_payload, void * candidate_binding_chain, int match_flags)` | `RET 0x10` removes the prior phantom fifth stack argument. The helper compares payload context, walks source binding records, applies match flag `0x10`, calls the compatibility and mismatch-score helpers, and returns `-1` or an accumulated match score. |

## Evidence

- Accepted dry/apply/final dry:
  - `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0`
  - `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0`
  - `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Candidate exports verified `7` metadata rows, `7` tag rows, `17` xref rows, `1855` instruction rows, and `7` decompile rows for the six target helpers plus deferred selector context.
- Post exports verified `6` metadata rows, `6` tag rows, `15` xref rows, `1590` instruction rows, and `6` decompile rows. The selected post decompiles no longer contain `param_`, `unaff_`, `in_stack_`, or `in_ECX`; residual `extraout_*` temporaries are decompiler boolean-return modeling, not stack/register ABI debt.
- Queue after Wave709: `6098` total, `4117` commented, `1981` commentless, `1216` exact-undefined signatures, `218` `param_N`, comment-backed proxy `4117/6098 = 67.52%`, strict clean-signature proxy `4063/6098 = 66.63%`.
- Raw commentless head remains `0x0042f220 CSPtrSet__Clear`.
- High-signal head moved to `0x0059aec0 CTexture__CanUseCompactDecodePath`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-214637_post_wave709_node_tree_compatibility_verified`, `19` files, `165481351` bytes, `DiffCount=0`.

## Deferred Selector

`0x0059a71a CFastVB__SelectBestNodeTreeMatch` was exported in the candidate context and left deferred read-only. Its candidate decompile still exposes hidden ABI artifacts including `in_ECX`, `unaff_EDI`, and multiple `in_stack_*` inputs, so Wave709 deliberately avoided mutating that selector.

## Boundaries

This is static Ghidra metadata/read-back evidence only. Exact node layout, compatibility rules, score-bit semantics, payload/binding layout, source identity, runtime parser behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave709 node-tree compatibility`, `node-tree-compatibility-wave709`, `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex`, `0x0059a54d CFastVB__ScoreNodeTreeMatch`, `0x0059a71a CFastVB__SelectBestNodeTreeMatch`, `0x0042f220 CSPtrSet__Clear`, `0x0059aec0 CTexture__CanUseCompactDecodePath`.
