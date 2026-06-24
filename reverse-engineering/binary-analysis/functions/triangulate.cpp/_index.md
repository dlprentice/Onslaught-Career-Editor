# triangulate.cpp - Mesh Triangulation

**Source file:** `C:\dev\ONSLAUGHT2\triangulate.cpp`
**Debug string address:** `0x00633ab8`
**Last updated:** 2026-05-28

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Wave521 hardened the saved Ghidra signatures, comments, tags, and owner labels for the BattleLine-linked `Triangulate` helper island at `0x004f7170..0x004f7940`. Earlier evidence made the adjacent helpers look like `CDXBattleLine` methods, but final read-back shows `CDXBattleLine__BuildMesh` allocates a separate 0x18-byte Triangulate work object, passes it through `Triangulate__CreateQuadMesh`, then calls the helper island on that object.

Wave934 (`battleline-triangulate-mesh-review-wave934`) re-reviewed the saved island read-only with fresh metadata/tags/xref/instruction/decompile exports for `0x004f7170 Triangulate__CreateQuadMesh`, `0x004f7460 Triangulate__InsertPointOrAppendVertex`, `0x004f74b0 Triangulate__SplitTriangleAtPointAndLegalizeEdges`, `0x004f7660 Triangulate__TryFlipSharedEdgeForQuality`, `0x004f78c0 Triangulate__FindTriangleByDirectedEdge`, and `0x004f7940 Triangulate__RelaxMeshByEdgeFlips`, plus context anchors `0x0053a5e0 CDXBattleLine__BuildMesh`, `0x0053b470 CDXBattleLine__RenderTriOverlayPass`, and `0x00487d10 CHud__RenderBattleline`. The fresh read-back matched Wave521/Wave589 evidence, so Wave934 made no mutation. Wave911 focused re-audit progress after Wave934 is `146/1408 = 10.37%`; static export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-005650_post_wave934_battleline_triangulate_mesh_review_verified`.

This is static retail-binary evidence only. It does not prove exact source-body identity, a complete `Triangulate` structure layout, runtime overlay mesh behavior, runtime influence-map mesh behavior, BEA patching, or rebuild parity.

Wave1127 (`wave1127-mixed-score23-current-risk-review`) re-read and tag-normalized `0x004f7460 Triangulate__InsertPointOrAppendVertex` as a score-23 current-risk row. Fresh evidence keeps the saved owner/signature/comment coherent: `CDXBattleLine__BuildMesh` calls it at `0x0053a7a4`, the body scans the active triangle count at `this+0x0c`, calls `Triangulate__SplitTriangleAtPointAndLegalizeEdges`, and appends the XY point when no candidate accepts it. Wave1127 added tags only; no rename, signature, comment, function-boundary, or executable-byte change was made. Verified backup: `G:\GhidraBackups\BEA_20260605-071212_post_wave1127_mixed_score23_current_risk_review_verified`. Runtime overlay/influence mesh behavior, exact `Triangulate` work-object layout beyond observed fields, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Functions (6 found)

| Address | Name | Saved signature | Purpose |
| --- | --- | --- | --- |
| `0x004f7170` | `Triangulate__CreateQuadMesh` | `void * __thiscall Triangulate__CreateQuadMesh(void * this, int max_vertices, float min_x, float min_y, float max_x, float max_y, int subdivision_mode)` | Allocates XY vertex and ushort-triangle buffers, then seeds a simple or subdivided rectangular mesh. |
| `0x004f7460` | `Triangulate__InsertPointOrAppendVertex` | `void __thiscall Triangulate__InsertPointOrAppendVertex(void * this, void * point_xy)` | Inserts a point into a containing triangle when possible, otherwise appends it to the vertex buffer. |
| `0x004f74b0` | `Triangulate__SplitTriangleAtPointAndLegalizeEdges` | `int __thiscall Triangulate__SplitTriangleAtPointAndLegalizeEdges(void * this, void * triangle_indices, void * point_xy)` | Tests point containment, splits one triangle into three, appends a vertex, and legalizes new shared edges. |
| `0x004f7660` | `Triangulate__TryFlipSharedEdgeForQuality` | `void __thiscall Triangulate__TryFlipSharedEdgeForQuality(void * this, int edge_start, int edge_end)` | Finds adjacent triangles for a directed edge and flips the shared edge when the quality heuristic improves. |
| `0x004f78c0` | `Triangulate__FindTriangleByDirectedEdge` | `short * __thiscall Triangulate__FindTriangleByDirectedEdge(void * this, int edge_start, int edge_end)` | Finds or rotates a triangle triplet so the requested directed edge is first. |
| `0x004f7940` | `Triangulate__RelaxMeshByEdgeFlips` | `void __fastcall Triangulate__RelaxMeshByEdgeFlips(void * this)` | Performs up to ten dirty-flagged passes over triangle triplets, trying edge flips for all three directed edges. |

## Work-Object Fields

Observed static offsets:

| Offset | Meaning |
| ---: | --- |
| `+0x00` | XY vertex buffer pointer (`float x, float y` pairs) |
| `+0x04` | triangle index buffer pointer (`uint16_t[3]` triplets) |
| `+0x08` | active vertex count |
| `+0x0c` | active triangle count |
| `+0x10` | vertex capacity / allocation count |
| `+0x14` | dirty flag used by edge-flip relaxation |

## Function Details

### `Triangulate__CreateQuadMesh` (`0x004f7170`)

- `RET 0x18` proves six explicit stack arguments after the ECX work object.
- `CDXBattleLine__BuildMesh` calls it after allocating a 0x18-byte Triangulate-style work object.
- The body allocates `max_vertices * 8` bytes for XY float pairs and `max_vertices * 0x0c` bytes for ushort triangle triplets.
- `subdivision_mode == 0` emits 4 vertices and 2 triangles.
- `subdivision_mode == 1` emits 8 vertices and 6 triangles, computing edge/midpoint vertices with the `0.5` constant at `0x005d85ec`.

### `Triangulate__InsertPointOrAppendVertex` (`0x004f7460`)

- `RET 0x4` proves one explicit stack argument after ECX.
- Scans the triangle array at `this+0x04` for the active triangle count at `this+0x0c`.
- Calls `Triangulate__SplitTriangleAtPointAndLegalizeEdges` on each candidate.
- Appends the XY point to `this+0x00` and increments `this+0x08` when no candidate accepts it.

### `Triangulate__SplitTriangleAtPointAndLegalizeEdges` (`0x004f74b0`)

- `RET 0x8` proves two explicit stack arguments after ECX.
- Capacity-checks the active vertex count against `this+0x10`.
- Uses three oriented-area tests against epsilon `0x005d856c` to decide whether `point_xy` lies inside the supplied ushort triangle.
- Rewrites the hit triangle, appends two triangle triplets, writes the new point to the vertex buffer, increments vertex/triangle counts, and tries quality flips on the three new shared edges.

### `Triangulate__TryFlipSharedEdgeForQuality` (`0x004f7660`)

- `RET 0x8` proves two explicit stack arguments after ECX.
- Finds triangles on both sides of the directed edge with `Triangulate__FindTriangleByDirectedEdge`.
- Compares shared-edge length against the opposite diagonal, applies oriented-area quality gates using epsilon `0x005d856c` and ratio threshold `0x005d85f8`, then flips the edge when the quality test improves.
- Sets the dirty flag at `this+0x14` when it mutates topology.

### `Triangulate__FindTriangleByDirectedEdge` (`0x004f78c0`)

- `RET 0x8` proves two explicit stack arguments after ECX.
- Scans active ushort triangle triplets from `this+0x04`.
- Returns a pointer when the requested directed edge is already first, or rotates a matching triangle in place so the requested edge becomes first.
- Returns null when the edge is absent.

### `Triangulate__RelaxMeshByEdgeFlips` (`0x004f7940`)

- ECX carries the Triangulate work object and the body returns without stack cleanup.
- Sets the dirty flag at `this+0x14`, then performs up to ten passes.
- Each pass clears the flag, walks all active triangle triplets, and calls `Triangulate__TryFlipSharedEdgeForQuality` for the three directed edges until no flip marks the mesh dirty.

## Cross-References

| Target | From | Caller | Ref type | Notes |
| --- | --- | --- | --- | --- |
| `0x004f7170` | `0x0053a712` | `CDXBattleLine__BuildMesh` | `UNCONDITIONAL_CALL` | Creates the Triangulate work mesh. |
| `0x004f7460` | `0x0053a7a4` | `CDXBattleLine__BuildMesh` | `UNCONDITIONAL_CALL` | Inserts BattleLine/influence points into the Triangulate work mesh. |
| `0x004f74b0` | `0x004f7478` | `Triangulate__InsertPointOrAppendVertex` | `UNCONDITIONAL_CALL` | Point-in-triangle split path. |
| `0x004f7660` | `0x004f7622`, `0x004f762b`, `0x004f7634` | `Triangulate__SplitTriangleAtPointAndLegalizeEdges` | `UNCONDITIONAL_CALL` | Legalizes the three new shared edges after a split. |
| `0x004f7660` | `0x004f798d`, `0x004f799a`, `0x004f79a7` | `Triangulate__RelaxMeshByEdgeFlips` | `UNCONDITIONAL_CALL` | Relaxation pass checks all three directed edges per triangle. |
| `0x004f78c0` | `0x004f7673`, `0x004f767e` | `Triangulate__TryFlipSharedEdgeForQuality` | `UNCONDITIONAL_CALL` | Looks up both sides of a directed edge. |
| `0x004f7940` | `0x0053a7c0` | `CDXBattleLine__BuildMesh` | `UNCONDITIONAL_CALL` | Final mesh-relaxation pass before BattleLine buffer construction. |

The debug path string at `0x00633ab8` is referenced by the two `OID__AllocObject` calls inside `Triangulate__CreateQuadMesh` for line `6` and line `7` allocation records.

## Validation

Wave521 artifacts live under `subagents/ghidra-static-reaudit/wave521-battleline-triangulate-004f7170/`. Read-back verified 6 target metadata rows, 6 tag rows, 12 target xref rows, 1398 instruction rows, 6 target decompile exports, 9 context metadata rows, 15 context xref rows, and 9 context decompile exports. The focused probe is `tools/ghidra_battleline_triangulate_wave521_probe.py`.

Wave934 artifacts live under `subagents/ghidra-static-reaudit/wave934-battleline-triangulate-mesh-review/`. Fresh read-only exports verified 6 primary metadata rows, 6 tag rows, 12 xref rows, 685 instruction rows, and 6 decompile rows, plus 3 context metadata rows, 3 tag rows, 3 xref rows, 605 instruction rows, and 3 context decompile rows. The focused Wave934 probe is `tools/ghidra_battleline_triangulate_mesh_review_wave934_probe.py`; mutation status: no mutation.
