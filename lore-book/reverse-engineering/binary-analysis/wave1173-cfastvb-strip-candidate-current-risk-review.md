# Wave1173 CFastVB Strip-Candidate Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Tag: `wave1173-cfastvb-strip-candidate-current-risk-review`

Wave1173 accounts for `3 CFastVB strip-candidate current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Targets:

| Address | Name | Static read-back evidence |
| --- | --- | --- |
| `0x0056ff40` | `CFastVB__TriangleListContainsVertexTriplet_0056ff40` | Called by `0x00570000 CFastVB__BuildTriangleStripFromSeedRecord`; walks a triangle-record pointer span and returns low-byte false once all three candidate vertex ids are already represented. |
| `0x005708a0` | `CFastVB__InsertStripCandidatesIntoBuffer_005708a0` | Called by `0x00570000 CFastVB__BuildTriangleStripFromSeedRecord`; inserts secondary strip candidates in reverse order, then grows/shifts the main candidate pointer buffer while inserting primary candidates. |
| `0x00570be0` | `CFastVB__InitializeCandidateParentLinks_00570be0` | Called by `0x005725e0 CFastVB__GenerateStripCandidatesFromAdjacency`; resets candidate root parent fields, appends roots to the output span, and stamps child triangle records with the root owner/group fields. |

Evidence counts:

- Fresh Ghidra export verified `3` metadata rows, `3` tag rows, `3 xref rows`, `339 instruction rows`, and `3` decompile rows.
- Saved comments/tags remain consistent with prior Wave651 strip-selection hardening and Wave1025 node-tree/strip-selection read-back; Wave1173 performs current-risk accounting with fresh current Ghidra evidence rather than a new correction.
- Verified backup: `G:\GhidraBackups\BEA_20260606-073137_post_wave1173_cfastvb_strip_candidate_current_risk_review_verified` (`19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`).
- Current-risk accounting after Wave1173: `675/1179 = 57.25%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 504; current risk candidates: 6166; focused threshold `15`; not Wave911 reconstruction.

This wave spawned a Codex read-only consult as sidecar target-selection sanity, but final claims are based on Codex root's live Ghidra exports, backup verification, and repo evidence.

Boundary: runtime strip quality, concrete D3D index-buffer/render output, exact CFastVB/strip-candidate/span/triangle-record layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1173; wave1173-cfastvb-strip-candidate-current-risk-review; 675/1179 = 57.25%; 3 CFastVB strip-candidate current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 504; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult spawned; 0 / 0 / 0; 6411/6411 = 100.00%; 3 xref rows; 339 instruction rows; CFastVB__TriangleListContainsVertexTriplet_0056ff40; CFastVB__InsertStripCandidatesIntoBuffer_005708a0; CFastVB__InitializeCandidateParentLinks_00570be0; G:\GhidraBackups\BEA_20260606-073137_post_wave1173_cfastvb_strip_candidate_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
