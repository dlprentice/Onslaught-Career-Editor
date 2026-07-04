# Ghidra BattleLine Triangulate Mesh Review Wave934 Readiness

Status: complete read-only static read-back evidence
Date: 2026-05-28
Scope: `battleline-triangulate-mesh-review-wave934`

Wave934 re-reviewed the BattleLine-linked Triangulate mesh-topology island after the Wave911 risk-ranked continuation queue surfaced `0x004f7460 Triangulate__InsertPointOrAppendVertex` as a high-value remaining candidate. Fresh Ghidra exports matched the already-saved Wave521 and Wave589 evidence chain, so this wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x004f7170` | `Triangulate__CreateQuadMesh` | `RET 0x18`; allocates `max_vertices * 8` XY vertices and `max_vertices * 0xc` ushort triangle storage; called from `0x0053a712 CDXBattleLine__BuildMesh`. |
| `0x004f7460` | `Triangulate__InsertPointOrAppendVertex` | `RET 0x4`; scans the active triangle array, calls `Triangulate__SplitTriangleAtPointAndLegalizeEdges`, and appends an XY point when no triangle accepts it. |
| `0x004f74b0` | `Triangulate__SplitTriangleAtPointAndLegalizeEdges` | `RET 0x8`; tests point containment against epsilon `0x005d856c`, splits one triangle, appends a vertex, and calls the edge-quality helper on three new edges. |
| `0x004f7660` | `Triangulate__TryFlipSharedEdgeForQuality` | `RET 0x8`; calls `Triangulate__FindTriangleByDirectedEdge` for both edge directions, checks quality threshold `0x005d85f8`, and sets dirty flag `this+0x14` after a flip. |
| `0x004f78c0` | `Triangulate__FindTriangleByDirectedEdge` | `RET 0x8`; finds or rotates ushort triangle triplets so the requested directed edge is first, returning null when absent. |
| `0x004f7940` | `Triangulate__RelaxMeshByEdgeFlips` | ECX-only fastcall; performs up to ten dirty-flagged passes and calls `Triangulate__TryFlipSharedEdgeForQuality` for all three directed edges per triangle. |

Context anchors:

- `0x0053a5e0 CDXBattleLine__BuildMesh` allocates the 0x18-byte Triangulate work object, calls `Triangulate__CreateQuadMesh`, inserts unit/influence points through `Triangulate__InsertPointOrAppendVertex`, calls `Triangulate__RelaxMeshByEdgeFlips`, and builds vertex/index buffers.
- `0x0053b470 CDXBattleLine__RenderTriOverlayPass` remains a Wave589 overlay-render helper, not a Triangulate topology helper.
- `0x00487d10 CHud__RenderBattleline` is the HUD caller from `0x0053ed79 CDXEngine__PostRender`; it invokes pulse sprite rendering and dispatches BattleLine overlay population/render when the influence map is non-empty.

Fresh read-back evidence:

- Primary exports: 6 metadata rows, 6 tag rows, 12 xref rows, 685 instruction rows, and 6 decompile rows.
- Context exports: 3 metadata rows, 3 tag rows, 3 xref rows, 605 instruction rows, and 3 decompile rows.
- Primary xrefs confirm `0x0053a712`, `0x0053a7a4`, and `0x0053a7c0` from `CDXBattleLine__BuildMesh`; internal Triangulate calls at `0x004f7478`, `0x004f7622`, `0x004f762b`, `0x004f7634`, `0x004f7673`, `0x004f767e`, `0x004f798d`, `0x004f799a`, and `0x004f79a7`.
- Context xrefs confirm `0x0053a295 CDXBattleLine__Setup -> CDXBattleLine__BuildMesh`, `0x0053b276 CDXBattleLine__Render -> CDXBattleLine__RenderTriOverlayPass`, and `0x0053ed79 CDXEngine__PostRender -> CHud__RenderBattleline`.
- Verified read-only backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-005650_post_wave934_battleline_triangulate_mesh_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

Progress:

- Wave911 focused re-audit progress after Wave934: `146/1408 = 10.37%`.
- Static export-contract function-quality closure remains `6113/6113 = 100.00%`.

Probe token anchor: Wave934; `battleline-triangulate-mesh-review-wave934`; `0x004f7170 Triangulate__CreateQuadMesh`; `0x004f7460 Triangulate__InsertPointOrAppendVertex`; `0x004f74b0 Triangulate__SplitTriangleAtPointAndLegalizeEdges`; `0x004f7660 Triangulate__TryFlipSharedEdgeForQuality`; `0x004f78c0 Triangulate__FindTriangleByDirectedEdge`; `0x004f7940 Triangulate__RelaxMeshByEdgeFlips`; `0x0053a5e0 CDXBattleLine__BuildMesh`; `0x0053b470 CDXBattleLine__RenderTriOverlayPass`; `0x00487d10 CHud__RenderBattleline`; `146/1408 = 10.37%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-005650_post_wave934_battleline_triangulate_mesh_review_verified`; no mutation.

What this proves:

- The six Triangulate topology rows and three BattleLine/HUD context rows remain present in the saved Ghidra project with the expected names, signatures, comments, and tags.
- The fresh xrefs preserve the Wave521 owner correction boundary: the topology helpers operate on a 0x18-byte Triangulate work object allocated by `CDXBattleLine__BuildMesh`, not on the outer CDXBattleLine object.
- The fresh context read-back preserves the Wave589 and Wave412 caller chain without requiring a new mutation.

What remains unproven:

- Exact source-body identity.
- A complete Triangulate or CDXBattleLine structure layout.
- Runtime influence-map mesh behavior.
- Runtime overlay visual behavior.
- BEA patching behavior.
- Rebuild parity.
