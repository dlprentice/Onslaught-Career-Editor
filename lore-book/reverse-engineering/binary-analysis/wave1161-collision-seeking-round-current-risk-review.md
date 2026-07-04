# Wave1161 Collision-Seeking Round Current-Risk Review

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Tag: `wave1161-collision-seeking-round-current-risk-review`

Wave1161 accounts for `17 collision-seeking/mesh-collision current-risk rows` from the active `wave1108-current-risk-rank` current-risk denominator. Fresh Ghidra exports showed the saved names, signatures, comments, and tags are coherent, so this wave made no Ghidra mutation.

Probe token anchor: Wave1161; wave1161-collision-seeking-round-current-risk-review; 533/1179 = 45.21%; 17 collision-seeking/mesh-collision current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 646; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 74 xref rows; 1567 instruction rows; CCollisionSeekingRound__InitCollisionLineAndSound; CCollisionSeekingRound__ResolveRoundCollisionResponse; CCollisionSeekingRound__ProcessMapWhoCollisionSweep; CMeshCollisionVolume__TestSweptSphereAgainstMeshPart; CMeshCollisionVolume__ResolveContactNormalAndPlane; CCollisionSeekingRound__ShutdownMonitorAndDestruct; [maintainer-local-ghidra-backup-root]\BEA_20260606-014548_post_wave1161_collision_seeking_round_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

Fresh exports under `subagents/ghidra-static-reaudit/wave1161-collision-seeking-round-current-risk-review/`:

| Artifact | Rows |
| --- | ---: |
| `pre-metadata.tsv` | 17 |
| `pre-tags.tsv` | 17 |
| `pre-xrefs.tsv` | 74 |
| `pre-instructions.tsv` | 1567 |
| `pre-decompile/index.tsv` | 17 |

Reviewed anchors:

| Address | Function | Static role |
| --- | --- | --- |
| `0x00425b50` | `CCollisionSeekingRound__InitCollisionLineAndSound` | Collision-seeking vtable slot that initializes/replaces the CLine-style helper and wraps sound-aware init. |
| `0x00425e30` | `CCollisionSeekingRound__UpdatePrimarySeekerLeadVector` | Updates the primary seeker line/vector record from owner target/current position. |
| `0x00426150` | `CCollisionSeekingRound__Init` | Round configuration bridge that creates/adopts primary CLine-style seeker and optional secondary CMeshCollisionVolume-style seeker. |
| `0x00426300` | `CMeshCollisionVolume__ScalarDeletingDestructor_00426300` | Scalar-deleting destructor wrapper for the mesh collision-volume helper. |
| `0x00426340` | `CLine__ScalarDeletingDestructor_00426340` | Scalar-deleting destructor wrapper for the shared CLine-style helper. |
| `0x00426360` | `CLine__SetBaseVtable_00426360` | Owner-neutral CLine vtable reset used by destructors and unwind thunks. |
| `0x00426370` | `CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset` | Replaces the primary seeker pointer and refreshes owner-relative offset fields. |
| `0x004264a0` | `CCollisionSeekingRound__ResolveRoundCollisionResponse` | Peer collision response helper gated by delayed-ready flag `0x400`, owner filters, collision-priority bits, and helper selection. |
| `0x00426900` | `CCollisionSeekingRound__CheckCollisionFlags` | Compares candidate owner thing flags against the round collision mask. |
| `0x00426a00` | `CCollisionSeekingRound__ProcessMapWhoCollisionSweep` | Forwards `this+0x24` and sweep args to `CHLCollisionDetector__ProcessMapWhoCollisionSweep`. |
| `0x00426a20` | `CCollisionSeekingRound__MarkDelayedCollisionReady` | Event callback that sets flag `0x400` when the event timestamp/code equals `3000ms`. |
| `0x004abe50` | `CMeshCollisionVolume__VFunc_02_004abe50` | Vtable slot 2 helper that builds a local sphere/contact record and dispatches through slot `+0x0c`. |
| `0x004ac4a0` | `CMeshCollisionVolume__TestSweptSphereAgainstMeshPart` | Swept-sphere mesh-part triangle bucket search and triangle-core dispatch. |
| `0x004acf30` | `CMeshCollisionVolume__ResolveContactNormalAndPlane` | Contact normal/plane resolver that writes output contact point/normal when consistent. |
| `0x004262e0` | `CMeshCollisionVolume__VFunc_05_004262e0` | Vtable slot 5 delegate forwarder with four stack arguments. |
| `0x004d8a70` | `CCollisionSeekingRound__ShutdownMonitorAndDestruct` | Monitor shutdown at `this+0x24`, then `CCollisionSeekingRound__Destructor(this)`. |
| `0x005d3980` | `CMeshCollisionVolume__SetPartBounds_Unwind` | MeshCollisionVolume.cpp compiler-generated unwind cleanup callback tied to DATA xref `0x0061c5ec`. |

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-014548_post_wave1161_collision_seeking_round_current_risk_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave911 focused historical residual | `596` rows, historical-retired/non-reconstructable, `300` materialized focused rows |
| Wave911 top-500 risk-ranked subset | `500/500 = 100.00%` |
| Wave1108 current focused accounting | `533/1179 = 45.21%` |
| Current risk candidates | `6166` |
| Current focused candidates | `1178` |
| Live regenerated current focused candidates | `1178` |
| Remaining active focused work | `646` |

This is the active current-risk denominator, not Wave911 reconstruction.

## Boundary

This review proves static retail Ghidra metadata/decompile/xref/instruction evidence for the reviewed collision-seeking and mesh-collision rows. It does not prove runtime collision behavior, runtime projectile behavior, exact CCollisionSeekingRound/CMeshCollisionVolume/CLine layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, or rebuild parity.
