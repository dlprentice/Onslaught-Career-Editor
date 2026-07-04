# Wave1177 HiveBoss Init / VFunc Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Scope: `wave1177-hiveboss-init-vfunc-current-risk-review`

Wave1177 accounts for `3 CHiveBoss init/vfunc current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation. Codex read-only consult was used for next-cluster sanity; Codex root made the final judgment and kept Wave1177 scoped to the already-exported uncounted HiveBoss mini-cluster.

Current accounting after Wave1177:

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave911 focused | `812/1408 = 57.67%`, historical-retired/non-reconstructable |
| Wave911 top-500 risk-ranked | `500/500 = 100.00%` |
| Wave1108 current focused accounting | `695/1179 = 58.95%` |
| Current focused candidates | `1178` |
| Live regenerated current focused candidates | `1178` |
| Remaining active focused work | `484` |
| Current risk candidates | `6166` |

Fresh export evidence:

| Artifact | Rows |
| --- | ---: |
| Metadata | `3` |
| Tags | `3` |
| Xrefs | `3` |
| Function-body instructions | `249` |
| Decompile rows | `3` |

Reviewed rows:

| Address | Saved name | Static read-back evidence |
| --- | --- | --- |
| `0x0047fe30` | `CHiveBoss__Init` | DATA vtable/factory xref `0x005e1704`; current decompile still sets HiveBoss init flags, allocates the `+0x178` destructable-segments controller, allocates `CMCHiveBoss` at `+0x70`, calls `CUnit__Init`, resolves `core2`, creates a guide object at `+0x208`, and seeds HiveBoss float/state fields including `+0x2a0 = 30.0f` and `+0x12c = 10.0f`. |
| `0x00480050` | `CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050` | DATA vtable xref `0x005e1780`; current decompile tests the forwarded context dword at `+0x34` for mask `0x01000000` and calls `CUnit__ApplyDamage` only when that bit is clear; retains `RET 0x10` / four explicit argument shape. |
| `0x00480080` | `CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080` | DATA vtable xref `0x005e1898`; current decompile reads the global target object at `DAT_008a9d3c`, compares position fields, normalizes/scales a horizontal offset by `this+0x2a0`, samples terrain/shadow height through `CStaticShadows__SampleShadowHeightBilinear`, and writes four dwords to the caller output vector. |

Prior context:

- Wave397 saved the original `CHiveBoss__Init` signature/comment correction.
- Wave921 re-reviewed the HiveBoss config/init/motion-controller cluster read-only.
- Wave1087 recovered the CHiveBoss/unit-family vtable-tail function boundaries from vtable `0x005e1668`.
- Wave1127 re-read and tag-normalized `0x004804c0 CHiveBoss__SetVar`.
- Wave1140 re-read the related motion-controller residual current-risk rows including `CMCHiveBoss__Constructor` and shared motion-controller vfuncs.

Backup:

`[maintainer-local-ghidra-backup-root]\BEA_20260606-091847_post_wave1177_hiveboss_init_vfunc_current_risk_review_verified`

Backup verification: `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.

Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference; actual no-noticeable-difference parity still requires later runtime, asset, visual, control, timing, save, patch, and rebuild proof.

What this proves:

- The three target function rows exist in the saved Ghidra database.
- Saved names/signatures/comments/tags remain coherent with fresh metadata, DATA xrefs, instruction rows, and decompile output.
- The HiveBoss init/vfunc mini-cluster is now explicitly counted against the active Wave1108 current-risk denominator.

What remains separate proof:

- Runtime HiveBoss behavior.
- Runtime boss damage gating.
- Runtime guide/target/vector behavior.
- Exact `CHiveBoss` / unit-family concrete layouts.
- Exact source virtual names or source-body identity.
- BEA patching behavior.
- Visual QA, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1177; wave1177-hiveboss-init-vfunc-current-risk-review; 695/1179 = 58.95%; 3 CHiveBoss init/vfunc current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 484; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; Codex root final judgment; prior Wave397/Wave921/Wave1087/Wave1127/Wave1140 read-back evidence; 0 / 0 / 0; 6411/6411 = 100.00%; 3 xref rows; 249 instruction rows; 0x0047fe30 CHiveBoss__Init; 0x00480050 CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050; 0x00480080 CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080; [maintainer-local-ghidra-backup-root]\BEA_20260606-091847_post_wave1177_hiveboss_init_vfunc_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
