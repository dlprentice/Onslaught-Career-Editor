# Ghidra HLCollisionDetector Event Sweep Review Wave1018

Status: complete read-only static read-back evidence
Date: 2026-05-31
Scope: `hlcollisiondetector-event-sweep-review-wave1018`

Wave1018 re-read five high-level collision detector scan/traverse/dispatch/sweep/event rows with no mutation. Primary anchors are `0x00480a30 CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions`, `0x00480e10 CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions`, `0x00480ed0 CHLCollisionDetector__DispatchCollisionEventForPair`, `0x00481060 CHLCollisionDetector__ProcessMapWhoCollisionSweep`, and `0x004812d0 CHLCollisionDetector__HandleScheduledCollisionEvent`.

Read-back evidence:

- Target exports: 5 metadata rows, 5 tag rows, 21 xref rows, 621 body-instruction rows, and 5 decompile rows.
- Context exports: 6 metadata rows, 14 xref rows, 282 body-instruction rows, and 6 decompile rows.
- Context anchors: `0x00480c90 CHLCollisionDetector__HandleCollisionEnter`, `0x00480db0 CHLCollisionDetector__HandleCollisionExit`, `0x00488f00 CHLCollisionDetector__ctor_base`, `0x00426a00 CCollisionSeekingRound__ProcessMapWhoCollisionSweep`, `0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady`, and `0x00426150 CCollisionSeekingRound__Init`.
- Queue closure remains `6238/6238 = 100.00%`.
- Wave911 focused re-audit progress advances to `518/1408 = 36.79%`.
- Expanded static surface progress advances to `747/1493 = 50.03%`.
- Wave911 top-500 risk-ranked coverage advances to `447/500 = 89.40%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-204742_post_wave1018_hlcollisiondetector_event_sweep_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved names, signatures, comments, and tags for the selected HLCollisionDetector scan/traverse/dispatch/sweep/event rows remain coherent with fresh static Ghidra metadata, tags, xrefs, instructions, and decompile evidence.
- The call spine ties `CCollisionSeekingRound__InitWithSound` to the HLCollisionDetector scan helper, scan/traverse/sweep bodies to the pair dispatcher, `CCollisionSeekingRound__ProcessMapWhoCollisionSweep` to the HLCollisionDetector sweep helper, and the scheduled event handler to the HLCollisionDetector vtable DATA ref.
- No rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation was needed.

What remains separate proof:

- Runtime collision behavior.
- Exact detector/component/source layouts.
- Exact source-body identity.
- Event timing behavior.
- BEA patching behavior.
- Rebuild parity.

Probe token anchor: Wave1018; hlcollisiondetector-event-sweep-review-wave1018; 0x00480a30 CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions; 0x00480e10 CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions; 0x00480ed0 CHLCollisionDetector__DispatchCollisionEventForPair; 0x00481060 CHLCollisionDetector__ProcessMapWhoCollisionSweep; 0x004812d0 CHLCollisionDetector__HandleScheduledCollisionEvent; 518/1408 = 36.79%; 747/1493 = 50.03%; 447/500 = 89.40%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260531-204742_post_wave1018_hlcollisiondetector_event_sweep_review_verified; no mutation.
