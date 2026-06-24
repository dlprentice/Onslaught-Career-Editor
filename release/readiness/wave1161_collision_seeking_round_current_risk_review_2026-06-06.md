# Wave1161 Collision-Seeking Round Current-Risk Review Readiness Note

Status: complete static read-only evidence validated
Date: 2026-06-06
Scope: `wave1161-collision-seeking-round-current-risk-review`

Wave1161 re-read `17 collision-seeking/mesh-collision current-risk rows` from the active `wave1108-current-risk-rank` current-risk denominator. Fresh Ghidra metadata, tag, xref, instruction, and decompile exports showed the saved names, signatures, comments, and tags remain coherent. No Ghidra mutation was performed.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound` | CCollisionSeekingRound vtable slot that initializes/replaces the CLine-style helper and wraps sound-aware init. |
| `0x00426150 CCollisionSeekingRound__Init` | Round configuration bridge for primary CLine-style seeker and optional secondary CMeshCollisionVolume-style seeker. |
| `0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse` | Peer collision response helper gated by delayed-ready flag `0x400`, owner filters, priority bits, and helper selection. |
| `0x00426a00 CCollisionSeekingRound__ProcessMapWhoCollisionSweep` | Thin forwarder to `CHLCollisionDetector__ProcessMapWhoCollisionSweep`. |
| `0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart` | Swept-sphere mesh-part triangle bucket search and triangle-core dispatch. |
| `0x004acf30 CMeshCollisionVolume__ResolveContactNormalAndPlane` | Contact normal/plane resolver for contact records and output point/normal vectors. |
| `0x004d8a70 CCollisionSeekingRound__ShutdownMonitorAndDestruct` | Shuts down the monitor subobject at `this+0x24`, then destructs the collision-seeking round. |
| `0x005d3980 CMeshCollisionVolume__SetPartBounds_Unwind` | MeshCollisionVolume.cpp unwind cleanup callback tied to DATA xref `0x0061c5ec`. |

Read-back evidence:

- Pre exports: `17` metadata rows, `17` tag rows, `74` xref rows, `1567` instruction rows, and `17` decompile rows.
- Queue closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt.
- Active current-risk accounting advances to `533/1179 = 45.21%`.
- Current focused candidates: `1178`; live regenerated current focused candidates: `1178`; remaining active focused work: `646`; current risk candidates: `6166`.
- Verified backup: `G:\GhidraBackups\BEA_20260606-014548_post_wave1161_collision_seeking_round_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1161; wave1161-collision-seeking-round-current-risk-review; 533/1179 = 45.21%; 17 collision-seeking/mesh-collision current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 646; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 74 xref rows; 1567 instruction rows; CCollisionSeekingRound__InitCollisionLineAndSound; CCollisionSeekingRound__ResolveRoundCollisionResponse; CCollisionSeekingRound__ProcessMapWhoCollisionSweep; CMeshCollisionVolume__TestSweptSphereAgainstMeshPart; CMeshCollisionVolume__ResolveContactNormalAndPlane; CCollisionSeekingRound__ShutdownMonitorAndDestruct; G:\GhidraBackups\BEA_20260606-014548_post_wave1161_collision_seeking_round_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

What this proves:

- The reviewed rows exist in the saved Ghidra project and have coherent names, signatures, comments, tags, xrefs, instructions, and decompile exports.
- The collision-seeking/mesh-collision tranche bridges Wave1160 weapon/projectile handoff evidence into the seeker, line-helper, mesh-collision volume, map/who sweep, contact-resolution, and teardown paths.
- No Ghidra rename, signature, comment, tag, function-boundary, or executable-byte mutation was needed in this wave.

What remains separate:

- Runtime collision behavior.
- Runtime projectile behavior.
- Exact `CCollisionSeekingRound`, `CMeshCollisionVolume`, and `CLine` concrete layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA.
- Gameplay outcomes.
- Rebuild parity.
