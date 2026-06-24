# Wave1156 SharedUnitVFunc Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1156-sharedunitvfunc-current-risk-review`

Wave1156 re-read `29 SharedUnitVFunc current-risk rows` with fresh Ghidra exports and made no mutation: no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Probe token anchor: Wave1156; wave1156-sharedunitvfunc-current-risk-review; 453/1179 = 38.42%; 29 SharedUnitVFunc current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 726; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 951 DATA xrefs; 442 instruction rows; wave1083-readback-verified=6; wave1085-readback-verified=23; SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550; SharedUnitVFunc__TestField17c19cReadiness_004fd440; SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0; SharedUnitVFunc__ForwardField208Slot10_004fce00; SharedUnitVFunc__TestField17cEntryNameMatch_004fe310; G:\GhidraBackups\BEA_20260605-231547_post_wave1156_sharedunitvfunc_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv`: `29` rows, `targets=29 found=29 missing=0`.
- `pre-tags.tsv`: `29` rows, `missing=0`.
- `pre-xrefs.tsv`: `951 DATA xrefs`, covering all `29` targets.
- `pre-instructions.tsv`: `442 instruction rows`, `targets=29 missing=0`.
- `pre-decompile/index.tsv`: `29` rows, `targets=29 dumped=29 missing=0 failed=0`.
- Provenance tags: `wave1083-readback-verified=6`, `wave1085-readback-verified=23`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-231547_post_wave1156_sharedunitvfunc_current_risk_review_verified`, local Ghidra project root, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Codex subagent usage: read-only consults audited the export evidence, backup pattern, and map-update targets; Codex root selected, exported, audited, and kept the tranche read-only.

Reviewed row groups:

| Group | Static read-back evidence |
| --- | --- |
| Vector/transform forwarders | `SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550`, `SharedUnitVFunc__CopyTransformAndNotify_00401910`, and `SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0` keep the shared unit-family vector/transform field-copy and refresh surface tied to DATA vtable xrefs. |
| Field setters/accessors | `SharedUnitVFunc__SetField1f0One_00405e10`, `SharedUnitVFunc__ClearField1f0_00405e20`, `SharedUnitVFunc__SetField15c_00405e30`, `SharedUnitVFunc__ReturnField15c_00405e40`, `SharedUnitVFunc__ReturnField210_00405e50`, `SharedUnitVFunc__SetField160_00417600`, and related float/int return helpers remain bounded field-access vfunc rows, not exact concrete layout proof. |
| List/name/readiness predicates | `SharedUnitVFunc__TestField17c19cReadiness_004fd440`, `SharedUnitVFunc__FindActiveMemberByField18c_004fda90`, `SharedUnitVFunc__TestField17cEntryNameMatch_004fe310`, and `SharedUnitVFunc__PropagateNameToField18c19c_004fdd60` keep the field `0x17c`/`0x18c`/`0x19c` list-name readiness surface tied to unit-family vtable slots. |
| Attached/child dispatch | `SharedUnitVFunc__ForwardArgToThingBridge_00401900`, `SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220`, and `SharedUnitVFunc__ForwardField208Slot10_004fce00` preserve the bounded forwarding/slot-dispatch evidence. |

Accounting after Wave1156:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%` historical-retired/non-reconstructable provenance only.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `453/1179 = 38.42%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 726.

This is static Ghidra evidence only. Runtime shared-unit vfunc behavior, exact source virtual names, exact concrete layouts, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
