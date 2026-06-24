# Ghidra BattleLine / Triangulate Wave521 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for the BattleLine-linked Triangulate helper island

## Summary

Wave521 hardened six saved Ghidra function records around `Triangulate__CreateQuadMesh` and the BattleLine mesh-topology helpers. The final owner correction moved five stale CDXBattleLine helper labels to `Triangulate__*` because `CDXBattleLine__BuildMesh` passes the 0x18-byte Triangulate work object returned by `Triangulate__CreateQuadMesh`, not the outer CDXBattleLine object.

Targets:

- `0x004f7170` - `Triangulate__CreateQuadMesh`
- `0x004f7460` - `Triangulate__InsertPointOrAppendVertex`
- `0x004f74b0` - `Triangulate__SplitTriangleAtPointAndLegalizeEdges`
- `0x004f7660` - `Triangulate__TryFlipSharedEdgeForQuality`
- `0x004f78c0` - `Triangulate__FindTriangleByDirectedEdge`
- `0x004f7940` - `Triangulate__RelaxMeshByEdgeFlips`

## Evidence

Read-back artifacts live under `subagents/ghidra-static-reaudit/wave521-battleline-triangulate-004f7170/`.

Verified exports:

- 6 target metadata rows
- 6 target tag rows
- 12 target xref rows
- 1398 instruction rows
- 6 target decompile exports
- 9 context metadata rows
- 15 context xref rows
- 9 context decompile exports

Final owner-corrected apply evidence:

- Dry run: `updated=0 skipped=6 renamed=0 would_rename=5 missing=0 bad=0`
- Apply run: `updated=5 skipped=1 renamed=5 would_rename=0 missing=0 bad=0`
- Save status: `REPORT: Save succeeded`
- Focused probe: `py -3 tools\ghidra_battleline_triangulate_wave521_probe.py`
- NPM probe: `npm run test:ghidra-battleline-triangulate-wave521`

## Queue Impact

Fresh queue after Wave521:

- Function objects: 6082
- Functions with comments: 2471
- Commentless functions: 3611
- Exact `undefined` signatures: 1594
- Signatures still using `param_N` names: 1387
- Comment-backed telemetry: `2471/6082 = 40.63%`
- Strict clean-signature telemetry: `2409/6082 = 39.61%`

These are queue telemetry only, not certification and not a milestone.

## Backup

Verified backup:

- Path: `G:\GhidraBackups\BEA_20260517-232432_post_wave521_battleline_triangulate_verified`
- Files: 19
- Bytes: 158665607
- MissingCount: 0
- ExtraCount: 0
- HashDiffCount: 0

## Boundaries

This wave proves saved static retail Ghidra evidence only. The unresolved item `runtime overlay mesh behavior`, runtime influence-map mesh behavior, exact source-body identity, a complete Triangulate layout, BEA patching, and rebuild parity remain unproven.
