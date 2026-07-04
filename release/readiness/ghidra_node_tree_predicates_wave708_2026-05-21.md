# Ghidra Node-Tree Predicates Wave708 Readiness

Status: passed
Date: 2026-05-21

Wave708 node-tree predicates saved four adjacent CFastVB node-tree predicate/equality rows with the `node-tree-predicates-wave708` and `wave708-readback-verified` tags.

## Targets

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x00599b69` | `uint __thiscall CFastVB__NodeTreeHasBitFlag0x200(void * this, void * node_tree)` | Recursively walks node-tree wrapper kinds `1`, `5`, `7`, and `10`; leaf kind `8` returns `node +0x20 & 0x200`; unknown kinds emit the internal-error diagnostic. |
| `0x00599bd7` | `int __thiscall CFastVB__NodeTreeHasOnlyLeafType0to2(void * this, void * node_tree)` | Recursively walks the same wrapper kinds; null trees pass, leaf kind `8` passes only when `node +0x10` is `0..2`, and unknown kinds emit the internal-error diagnostic. |
| `0x00599c49` | `int __thiscall CFastVB__CountNodeTreeExpandedLeafCount(void * this, void * node_tree)` | Recursively counts expanded leaves: kind `1` sums linked children, kinds `5`/`10` unwrap child pointers, kind `7` multiplies child count by `node +0x14`, and kind `8` returns `node +0x1c * node +0x18`. |
| `0x00599cd2` | `bool __stdcall CFastVB__AreNodeTreesStructurallyEqual(void * left_node_tree, void * right_node_tree)` | Recursively compares two node trees for structural equality, including kind `1` linked children, kind `7` repeat count `+0x14`, and leaf kind `8` fields `+0x10/+0x14/+0x18/+0x1c`. |

## Evidence

- Accepted dry/apply/final dry:
  - `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0`
  - `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0`
  - `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports verified `4` metadata rows, `4` tag rows, `19` xref rows, `356` instruction rows, and `4` clean decompile rows.
- Queue after Wave708: `6098` total, `4111` commented, `1987` commentless, `1216` exact-undefined signatures, `224` `param_N`, comment-backed proxy `4111/6098 = 67.42%`, strict clean-signature proxy `4057/6098 = 66.53%`.
- Raw commentless head remains `0x0042f220 CSPtrSet__Clear`.
- High-signal head moved to `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-211737_post_wave708_node_tree_predicates_verified`, `19` files, `165481351` bytes, `DiffCount=0`.

## Boundaries

This is static Ghidra metadata/read-back evidence only. Exact node layout, field/flag/type semantics, source identity, runtime parser behavior, BEA patching, and rebuild parity remain unproven. Later node-tree scorer/selector helpers beginning at `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex` were inspected but left read-only because their ABI/story still needs a separate tranche.

Probe anchors: `Wave708 node-tree predicates`, `node-tree-predicates-wave708`, `0x00599b69 CFastVB__NodeTreeHasBitFlag0x200`, `0x00599cd2 CFastVB__AreNodeTreesStructurallyEqual`, `0x0042f220 CSPtrSet__Clear`, `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex`.
