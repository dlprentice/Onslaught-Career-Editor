# collisionseekingthing.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x00425a10` → `CCollisionSeekingInfantryBloke__CheckCollisionFlagsWithDeadSideBranch` (was `CCollisionSeekingInfantryBloke__CheckSideCompatibleOrCollisionFlags`). Older conflicting text below is superseded for these rows. Use the [closeout](../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Source File: collisionseekingthing.cpp | Binary: BEA.exe
> Debug Path: 0x006246d8 (`[maintainer-local-source-export-root]\collisionseekingthing.cpp`)

## Current Status

Wave 322 (2026-05-11) supersedes the earlier stub wording. The retail database does not yet have a standalone fully mapped `collisionseekingthing.cpp` function family, but the debug-path string is now tied to concrete allocation contexts inside the recovered `CCollisionSeekingRound` cluster.

Wave1059 (`collision-seeking-round-tail-review-wave1059`, `wave1059-readback-verified`) saved function-tag normalization for the collision-seeking round tail and context rows after fresh read-back. Relevant context anchors include `0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags`, `0x00425c60 CCollisionSeekingRound__FilterCollisionCandidateByTrajectory`, `0x00426900 CCollisionSeekingRound__CheckCollisionFlags`, `0x00426920 CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance`, `0x00426a00 CCollisionSeekingRound__ProcessMapWhoCollisionSweep`, and `0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady`; primary anchors include `0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound`, `0x00425e30 CCollisionSeekingRound__UpdatePrimarySeekerLeadVector`, `0x004263f0 CCollisionSeekingRound__Destructor`, and `0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse`. The pass saved `131` tags across fourteen rows with no rename, signature, comment, boundary, or executable-byte change. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress advances to `812/1408 = 57.67%`; expanded static surface progress advances to `1140/1509 = 75.55%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified`, `19` files, `174689159` bytes, `DiffCount=0`, `HashDiffCount=0`. Probe token anchor: Wave1059; collision-seeking-round-tail-review-wave1059; 0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound; 0x00425e30 CCollisionSeekingRound__UpdatePrimarySeekerLeadVector; 0x00426300 CMeshCollisionVolume__ScalarDeletingDestructor_00426300; 0x00426370 CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset; 0x004263f0 CCollisionSeekingRound__Destructor; 0x00426480 CCollisionSeekingRound__SetCollisionMask; 0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse; 0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady; 812/1408 = 57.67%; 1140/1509 = 75.55%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified; tag normalization.

This page records public-safe allocation, ownership, and tag-normalization evidence only. It does not prove exact source bodies, concrete helper layouts, local variable names, runtime collision behavior, or rebuild parity.

## Observed Allocation Contexts

| From address | Current saved owner | Alloc size / line | Observed role |
|--------------|---------------------|-------------------|---------------|
| 0x004261be | `CCollisionSeekingRound__Init` | `0x1c`, line `0x28` | Primary CLine-style seeker/helper setup context. |
| 0x0042627a | `CCollisionSeekingRound__Init` | `0x28`, line `0x39` | Secondary CMeshCollisionVolume-style helper setup context. |
| 0x00426ad3 | `CCollisionSeekingRound__CreateEffect` | `0x34`, line `0x13a` | Effect/trace helper allocation context. |

The allocator callsites pass the `collisionseekingthing.cpp` debug path for provenance. The exact source helper class names and layouts are still bounded because the current retail evidence comes from debug-path strings, allocation sizes, vtable assignments, and the surrounding `CCollisionSeekingRound` decompile/read-back context.

## Wave416 Adjacent Lifecycle Helpers

Wave416 saved static Ghidra corrections for adjacent collision-seeking helper lifecycle targets:

| Address | Current saved owner | Observed role |
| --- | --- | --- |
| `0x00488e80` | `CCollisionSeekingInfantryBloke__scalar_deleting_dtor` | Scalar-deleting destructor wrapper with delete-flag check and optional object free. |
| `0x00488ea0` | `CCollisionSeekingInfantryBloke__dtor_body_00488ea0` | Destructor body that shuts down monitor state and chains to `CCollisionSeekingRound` cleanup. |
| `0x00488ef0` | `CCollisionSeekingThing__ctor_base` | Constructor-base helper that clears field `+0x04` and installs shared collision-seeking vtable context. |

This is saved static Ghidra metadata/read-back evidence only. It does not prove runtime collision-seeking behavior or complete helper layouts.

## Related CollisionSeekingRound State

The `CollisionSeekingRound.cpp` page now records the saved Wave 322 names/signatures/comments for the surrounding cluster, including the recovered boundaries at:

- `0x00425b50` `CCollisionSeekingRound__InitCollisionLineAndSound`
- `0x00425c60` `CCollisionSeekingRound__FilterCollisionCandidateByTrajectory`
- `0x00425e30` `CCollisionSeekingRound__UpdatePrimarySeekerLeadVector`
- `0x00426370` `CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset`
- `0x004264a0` `CCollisionSeekingRound__ResolveRoundCollisionResponse`
- `0x00426920` `CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance`
- `0x00426a00` `CCollisionSeekingRound__ProcessMapWhoCollisionSweep`
- `0x00426a20` `CCollisionSeekingRound__MarkDelayedCollisionReady`

## Remaining Work

- Recover or confirm exact helper class boundaries if future source/vtable evidence separates them from `CCollisionSeekingRound`.
- Add concrete structure types and local-variable names only after stronger layout evidence; add further tags only after fresh read-back justifies them.
- Keep runtime projectile/collision behavior separate from static saved-Ghidra evidence until copied-profile runtime proof exists.
