# Ghidra Wave900+ Through Wave1018 Recheck

Status: complete local validation
Date: 2026-05-31

This gate extends the Wave900+ structural static re-audit evidence sweep through Wave1018 (`hlcollisiondetector-event-sweep-review-wave1018`).

Expected validation:

- `npm run test:ghidra-hlcollisiondetector-event-sweep-review-wave1018`
- `npm run test:ghidra-wave900-plus-through-wave1018-recheck`
- Validation passed before commit: focused Wave1018 probe, Wave900-Wave1018 aggregate recheck, static re-audit queue probe, docsync, release profile check, curated manifest check, public allowlist, doc-commands, md-links, repo hygiene, tracked JSON/JSONL parse, `git diff --check`, and `git diff --cached --check`.
- Aggregate recheck verified 121 readiness notes, 119 covered waves, 117 package probe scripts, 117 evidence bases, 119 backup references, 37 apply scripts, 37 Wave982-Wave1018 direct probe classifications, and 0 disallowed evidence failures.
- Current queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Wave1018 adds a focused read-only HLCollisionDetector event/sweep review with verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260531-204742_post_wave1018_hlcollisiondetector_event_sweep_review_verified`.

This is structural static evidence validation only. Runtime collision behavior, exact layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Probe token anchor: Wave1018; hlcollisiondetector-event-sweep-review-wave1018; 0x00480a30 CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions; 0x00480e10 CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions; 0x00480ed0 CHLCollisionDetector__DispatchCollisionEventForPair; 0x00481060 CHLCollisionDetector__ProcessMapWhoCollisionSweep; 0x004812d0 CHLCollisionDetector__HandleScheduledCollisionEvent; 518/1408 = 36.79%; 747/1493 = 50.03%; 447/500 = 89.40%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-204742_post_wave1018_hlcollisiondetector_event_sweep_review_verified; no mutation.
