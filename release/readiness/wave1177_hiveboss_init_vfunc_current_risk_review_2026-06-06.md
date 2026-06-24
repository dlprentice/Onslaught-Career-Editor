# Wave1177 HiveBoss Init / VFunc Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-06
Scope: `wave1177-hiveboss-init-vfunc-current-risk-review`

Wave1177 accounts for `3 CHiveBoss init/vfunc current-risk rows` with fresh Ghidra metadata, tag, xref, instruction, and decompile exports. It made no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0047fe30 CHiveBoss__Init` | DATA xref `0x005e1704`; allocates/wires the HiveBoss destructable-segments controller, motion controller, base `CUnit__Init`, `core2` segment, guide object, and initial state/float fields. |
| `0x00480050 CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050` | DATA xref `0x005e1780`; gates forwarding to `CUnit__ApplyDamage` on context flag `0x01000000`. |
| `0x00480080 CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080` | DATA xref `0x005e1898`; computes a scaled output vector using the global target object, `this+0x2a0`, and `CStaticShadows__SampleShadowHeightBilinear`. |

Read-back evidence:

- Post exports: `3` metadata rows, `3` tag rows, `3` DATA xref rows, `249` function-body instruction rows, and `3` decompile rows.
- Queue/accounting after Wave1177: `6411` total functions, `6411` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, `695/1179 = 58.95%` current focused accounting, `484` remaining active focused rows.
- Verified backup: `G:\GhidraBackups\BEA_20260606-091847_post_wave1177_hiveboss_init_vfunc_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The three HiveBoss rows exist in the saved Ghidra project and match the saved names/signatures/comments.
- Fresh DATA xrefs and decompile/instruction exports support the bounded static comments.
- The rows are now explicitly counted against the active Wave1108 current-risk denominator.

What remains unproven:

- Runtime HiveBoss behavior, runtime boss damage gating, runtime guide/target/vector behavior, exact concrete layouts, exact source virtual names/source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity.

Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference; actual no-noticeable-difference parity still requires later runtime, asset, visual, control, timing, save, patch, and rebuild proof.

Probe token anchor: Wave1177; wave1177-hiveboss-init-vfunc-current-risk-review; 695/1179 = 58.95%; 3 CHiveBoss init/vfunc current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 484; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; Codex root final judgment; prior Wave397/Wave921/Wave1087/Wave1127/Wave1140 read-back evidence; 0 / 0 / 0; 6411/6411 = 100.00%; 3 xref rows; 249 instruction rows; 0x0047fe30 CHiveBoss__Init; 0x00480050 CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050; 0x00480080 CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080; G:\GhidraBackups\BEA_20260606-091847_post_wave1177_hiveboss_init_vfunc_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
