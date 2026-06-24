# Ghidra Wave900-Wave1025 Static Re-Audit Recheck

Status: PASS
Date: 2026-06-01
Scope: `wave900-plus-through-wave1025-recheck`

This note extends the Wave900+ structural recheck to include Wave1025 (`cfastvb-node-tree-review-wave1025`) after the prior Wave1024 gate.

Wave1025 token anchor for focused and aggregate probes: `Wave1025`; `cfastvb-node-tree-review-wave1025`; `0x0056ff40 CFastVB__TriangleListContainsVertexTriplet_0056ff40`; `0x00570be0 CFastVB__InitializeCandidateParentLinks_00570be0`; `0x00598a81 CFastVB__NodeType9__ctor`; `0x0059902a CDXTexture__RegisterSerializedChunk`; `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex`; `0x0059a54d CFastVB__ScoreNodeTreeMatch`; `0x0059a71a CFastVB__SelectBestNodeTreeMatch`; Wave911 focused progress `576/1408 = 40.91%`; expanded static surface progress `805/1493 = 53.92%`; Wave911 top-500 risk-ranked coverage `500/500 = 100.00%`; function-quality closure `6238/6238 = 100.00%`; backup `G:\GhidraBackups\BEA_20260601-004522_post_wave1025_cfastvb_node_tree_review_verified`; no mutation.

Validation:

- `npm run test:ghidra-cfastvb-node-tree-review-wave1025`: PASS
- `npm run test:ghidra-wave900-plus-through-wave1025-recheck`: PASS
- `npm run test:ghidra-static-reaudit-queue`: PASS
- Current queue closure remains `6238/6238 = 100.00%`.
- Wave1025 backup reference: `G:\GhidraBackups\BEA_20260601-004522_post_wave1025_cfastvb_node_tree_review_verified`.

This is structural static evidence validation. It does not prove runtime shader/parser/texture behavior, exact source-layout identity, BEA patching, or rebuild parity.
