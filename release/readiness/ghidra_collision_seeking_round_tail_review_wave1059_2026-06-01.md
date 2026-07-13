# Ghidra Collision-Seeking Round Tail Review Wave1059 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00425a10` → `CCollisionSeekingInfantryBloke__CheckCollisionFlagsWithDeadSideBranch` (was `CCollisionSeekingInfantryBloke__CheckSideCompatibleOrCollisionFlags`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static re-audit tag-normalization evidence
Date: 2026-06-01
Scope: `collision-seeking-round-tail-review-wave1059`

Wave1059 re-read the collision-seeking round tail and adjacent context rows after Wave919/Wave991 and saved function-tag normalization for fourteen already named/commented rows. The pass made no renames, no signature changes, no comment changes, no function-boundary changes, and no executable-byte changes.

Primary targets:

| Address | Existing saved identity | Fresh evidence |
| --- | --- | --- |
| `0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound` | `void __thiscall CCollisionSeekingRound__InitCollisionLineAndSound(void * this, void * roundConfig)` | DATA xref `0x005de95c`; initializes/replaces the CLine-style helper and calls `CCollisionSeekingRound__InitWithSound`. |
| `0x00425e30 CCollisionSeekingRound__UpdatePrimarySeekerLeadVector` | `void * __fastcall CCollisionSeekingRound__UpdatePrimarySeekerLeadVector(void * this)` | DATA xref `0x005de96c`; updates the primary seeker target delta/lead-vector fields. |
| `0x00426300 CMeshCollisionVolume__ScalarDeletingDestructor_00426300` | `void * __thiscall CMeshCollisionVolume__ScalarDeletingDestructor_00426300(void * this, int deleteFlags)` | DATA xref `0x005d95c8`; scalar-deleting wrapper calls the mesh collision-volume destructor body. |
| `0x00426370 CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset` | `void __thiscall CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset(void * this, void * newSeeker)` | DATA refs from five vtable/table sites including `0x005d962c`, `0x005de974`, and `0x005df6fc`; replaces the primary helper and refreshes owner-relative offset. |
| `0x004263f0 CCollisionSeekingRound__Destructor` | `void __fastcall CCollisionSeekingRound__Destructor(void * this)` | Called by unwind/destructor rows including `0x005d2e26`, `0x00426460`, `0x00488ea0`, `0x004d8a70`, and `0x004f3a70`; resets helpers and shuts down monitor state. |
| `0x00426460 CCollisionSeekingRound__ScalarDeletingDestructor` | `void * __thiscall CCollisionSeekingRound__ScalarDeletingDestructor(void * this, int deleteFlags)` | DATA xref `0x005d960c`; wraps `CCollisionSeekingRound__Destructor` and optional free. |
| `0x00426480 CCollisionSeekingRound__SetCollisionMask` | `void __thiscall CCollisionSeekingRound__SetCollisionMask(void * this, int collisionMask)` | Calls from `0x00489b77` and `0x004f7070 CTree__HandleEvent`; writes mask field and marks explicit-mask flag `0x100`. |
| `0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse` | `void __thiscall CCollisionSeekingRound__ResolveRoundCollisionResponse(void * this, void * otherRound)` | DATA refs from five vtable/table sites including `0x005d9620`, `0x005de968`, and `0x005df6f0`; gates on delayed-ready flag `0x400`, owner/self filters, helper selection, and response callbacks. |

Context rows tagged by the same normalization pass:

- `0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags`
- `0x00425c60 CCollisionSeekingRound__FilterCollisionCandidateByTrajectory`
- `0x00426900 CCollisionSeekingRound__CheckCollisionFlags`
- `0x00426920 CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance`
- `0x00426a00 CCollisionSeekingRound__ProcessMapWhoCollisionSweep`
- `0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady`

Read-back evidence:

- Primary pre/post exports: `8` metadata rows, `8` tag rows, `26` xref rows, `665` function-body instruction rows, and `8` decompile rows.
- Context pre/post exports: `6` metadata rows, `6` tag rows, `18` xref rows, `257` function-body instruction rows, and `6` decompile rows.
- Dry run reported `updated=0 skipped=0 tags_added=131 missing=0 bad=0`.
- Apply reported `updated=14 skipped=0 tags_added=131 missing=0 bad=0` with `REPORT: Save succeeded`.
- Final dry/read-back reported `updated=0 skipped=14 tags_added=0 missing=0 bad=0`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress advances to `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1140/1509 = 75.55%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified`, `19` files, `174689159` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The fourteen target/context rows exist in the saved Ghidra project with expected names and signatures.
- The saved comments remain coherent with fresh metadata/xref/instruction/decompile evidence.
- The rows now carry `collision-seeking-round-tail-review-wave1059` and `wave1059-readback-verified` function tags.
- The old tag-coverage caveat for these reviewed collision-seeking rows is superseded by read-back evidence.

What remains unproven:

- Runtime projectile, collision, delayed-ready, event, and response behavior.
- Exact helper class layouts and exact source virtual method names.
- Exact parent source-body identity.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Next candidate note: continue with the next Wave911 focused static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1059; collision-seeking-round-tail-review-wave1059; 0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound; 0x00425e30 CCollisionSeekingRound__UpdatePrimarySeekerLeadVector; 0x00426300 CMeshCollisionVolume__ScalarDeletingDestructor_00426300; 0x00426370 CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset; 0x004263f0 CCollisionSeekingRound__Destructor; 0x00426480 CCollisionSeekingRound__SetCollisionMask; 0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse; 0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady; 812/1408 = 57.67%; 1140/1509 = 75.55%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified; tag normalization.
