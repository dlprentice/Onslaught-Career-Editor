# collisionseekingthing.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x00425a10` → `CCollisionSeekingInfantryBloke__CheckCollisionFlagsWithDeadSideBranch` (was `CCollisionSeekingInfantryBloke__CheckSideCompatibleOrCollisionFlags`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> **2026-08-12 live promotion closeout:** the five bounded implementation
> identities at `0x004263f0`, `0x004264a0`, `0x004269b0`, `0x00426a00`, and
> `0x00426a20` were reproduced in isolated Ghidra projects, rollback-tested,
> promoted into the PRE-backed-up live project, separately read back, copied to
> a verified POST backup, and refreshed into the byte-identical tracked
> snapshot. See the
> [collision-component identity correction](../collision-component-identity-correction-2026-08-12.md).
> This closes shared base implementation identity only; folded derived aliases,
> exact runtime behavior, layouts, and rebuild parity remain open.

> Source File: collisionseekingthing.cpp | Binary: BEA.exe
> Debug Path: 0x006246d8 (`[maintainer-local-source-export-root]\collisionseekingthing.cpp`)

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](_index.md#the-name-corrections-of-2026-07-28).
Old cell text is quoted below rather than deleted, so a reader who remembers the
withdrawn label can tell it was corrected and not lost.

| Address | Superseded label | Current name | Correction |
| --- | --- | --- | --- |
| `0x00425a10` | `CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags` | `CCollisionSeekingInfantryBloke__CheckCollisionFlagsWithDeadSideBranch` | same class; suffix re-read |
| `0x004261be` | `CCollisionSeekingRound__Init` | `CCollisionSeekingThing__Init` | class prefix moved; suffix unchanged |
| `0x0042627a` | `CCollisionSeekingRound__Init` | `CCollisionSeekingThing__Init` | class prefix moved; suffix unchanged |
| `0x004264a0` | `CCollisionSeekingRound__ResolveRoundCollisionResponse` | `CCollisionSeekingThing__ResolveCollisionResponse` | shared base owner and non-round-specific response recovered |
| `0x00426920` | `CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance` | `CCollisionSeekingThing__ComputeScaledMapCellChebyshevDistance` | class prefix moved; suffix unchanged |
| `0x00426ad3` | `CCollisionSeekingRound__CreateEffect` | `CCSRay__CreateEffect` | class prefix moved; suffix unchanged |

Where a row's **suffix** moved rather than only its class prefix, the behavioural
text beside it in this note was written for the old name. This sweep corrected
names against the export and re-derived no behaviour, so read any such gloss as
unverified against the new name until it is re-measured.

The 2026-08-11 round/explosion collision join supersedes the active meaning of
that row and additionally identifies `0x00426900` as
`CCSPersistentThing__CheckCollisionFlags` and `0x004269b0` as
`CCSPersistentThing__Init`. Strict RTTI fixes their slots; the pinned
`CThing::InitCollisionSeekingThing` source fixes the persistent owner; and the
retail bodies recover immediate neighbor scanning and shared owner-`Hit`
dispatch. Historical Wave1059 labels below remain a record of what that older
pass saved, not the current semantic boundary.

## Persistent hierarchy and lifecycle — 2026-08-11

The strict retail RTTI hierarchy removes the old owner ambiguity:

```text
CCollisionSeekingRound ----------> CCSPersistentThing
CCollisionSeekingInfantryBloke --> CCSPersistentThing
CCSPersistentThing --------------> CCollisionSeekingThing
CCollisionSeekingThing ----------> CMonitor -> IListener
```

That hierarchy, exact vtable slots, and the retail bodies establish this
bounded lifecycle:

| Address | Current name | Exact static contract |
| --- | --- | --- |
| `0x00426370` | `CCollisionSeekingThing__ReplacePrimarySeekerAndRefreshOffset` | Deletes the previous primary helper, installs the replacement, and stores its owner-relative centre offset. |
| `0x004263f0` | `CCollisionSeekingThing__dtor_base` | Resets the base vtable, deletes helper pointers at `+0x14/+0x18`, then shuts down the inherited monitor. |
| `0x00426460` | `CCollisionSeekingThing__ScalarDeletingDestructor` | Calls the base destructor, conditionally frees `this` when delete bit 0 is set, and returns `this`. |
| `0x00426920` | `CCollisionSeekingThing__ComputeScaledMapCellChebyshevDistance` | Scales unequal MapWho depths to a common level and returns `max(abs(dx), abs(dy))`. |
| `0x004269b0` | `CCSPersistentThing__Init` | Copies the `CInitCSThing` state, optionally arms event 3000, then performs the initial neighbor scan. |
| `0x00426a00` | `CCSPersistentThing__ProcessMapWhoCollisionSweep` | Slot 5 forwards the previous/current sector pair to the embedded detector at `this+0x24`. |
| `0x00426a20` | `CCSPersistentThing__HandleEvent` | Slot 0 accepts event number 3000 and sets collision-ready bit `0x400`; other event numbers are ignored. |
| `0x00480db0` | `CHLCollisionDetector__DispatchFilteredCollisionPair` | Rejects null/self and either failed mutual slot-8 filter, then dispatches the surviving pair. |
| `0x00480e10` | `CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions` | Recurses through four quad children and applies the same candidate/filter/dispatch path to every MapWho entry. |
| `0x00481060` | `CHLCollisionDetector__ProcessMapWhoCollisionSweep` | Scans only newly entered 3x3 cells across descending MapWho layers, using quad traversal at the current top layer. |
| `0x004812d0` | `CHLCollisionDetector__HandleScheduledCollisionEvent` | Event 2000 re-enters collision handling with its retained peer component and then clears scheduled state. |
| `0x004f3a50/0x004f3a70` | `CCSPersistentThing` destructors | Shut down the embedded detector monitor at `+0x24`, chain through the collision-seeking base destructor, and conditionally free the object. |

`CInitCSThing::mStartCollideOnNextFrame` is the dword at initializer offset
`+0x20`, not a sound/config flag. When it is true,
`CCSPersistentThing::Init` clears ready bit `0x400` and schedules event number
3000 after `mTimeBeforeStart` at `+0x2c`; the source default is `NEXT_FRAME`
(`-1.0f`). The initial scan still runs, but the shared response body cannot
complete owner `Hit` dispatch until readiness is restored. When the flag is
false, the ready bit survives and an existing overlap may be handled
synchronously during initialization, which is the path used by the small
tutorial explosion.

This is a static C1 contract. It does not establish exact runtime event cadence,
the meaning of every detector field, collision geometry beyond the named
filters, or rebuild parity.

---

## Current Status

Wave 322 (2026-05-11) superseded the earlier stub wording. Later hierarchy,
source, cross-build, and retail-body work now bounds the shared base lifecycle;
it still does not constitute a complete standalone mapping of every function
historically built from `collisionseekingthing.cpp`.

Wave1059 (`collision-seeking-round-tail-review-wave1059`, `wave1059-readback-verified`) saved function-tag normalization for the collision-seeking round tail and context rows after fresh read-back. Its historical owner labels for `0x004263f0`, `0x00426a00`, and `0x00426a20` are superseded by the hierarchy-backed lifecycle above. The pass saved `131` tags across fourteen rows with no rename, signature, comment, boundary, or executable-byte change. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress advances to `812/1408 = 57.67%`; expanded static surface progress advances to `1140/1509 = 75.55%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified`, `19` files, `174689159` bytes, `DiffCount=0`, `HashDiffCount=0`.

This page records public-safe allocation, ownership, and tag-normalization evidence only. It does not prove exact source bodies, concrete helper layouts, local variable names, runtime collision behavior, or rebuild parity.

## Observed Allocation Contexts

| From address | Current saved owner | Alloc size / line | Observed role |
|--------------|---------------------|-------------------|---------------|
| 0x004261be | `CCollisionSeekingThing__Init` | `0x1c`, line `0x28` | Primary CLine-style seeker/helper setup context. |
| 0x0042627a | `CCollisionSeekingThing__Init` | `0x28`, line `0x39` | Secondary CMeshCollisionVolume-style helper setup context. |
| 0x00426ad3 | `CCSRay__CreateEffect` | `0x34`, line `0x13a` | Effect/trace helper allocation context. |

The allocator callsites pass the `collisionseekingthing.cpp` debug path for provenance. The exact source helper class names and layouts are still bounded because the current retail evidence comes from debug-path strings, allocation sizes, vtable assignments, and the surrounding `CCollisionSeekingRound` decompile/read-back context.

## Wave416 Adjacent Lifecycle Helpers

Wave416 saved static Ghidra corrections for adjacent collision-seeking helper lifecycle targets:

| Address | Current saved owner | Observed role |
| --- | --- | --- |
| `0x00488e80` | `CCollisionSeekingInfantryBloke__scalar_deleting_dtor` | Scalar-deleting destructor wrapper with delete-flag check and optional object free. |
| `0x00488ea0` | `CCollisionSeekingInfantryBloke__dtor_body_00488ea0` | Destructor body that shuts down monitor state and chains to `CCollisionSeekingThing` base cleanup. |
| `0x00488ef0` | `CCollisionSeekingThing__ctor_base` | Constructor-base helper that clears field `+0x04` and installs shared collision-seeking vtable context. |

This is saved static Ghidra metadata/read-back evidence only. It does not prove runtime collision-seeking behavior or complete helper layouts.

## Related CollisionSeekingRound State

The `CollisionSeekingRound.cpp` page now records the saved Wave 322 names/signatures/comments for the surrounding cluster, including the recovered boundaries at:

- `0x00425b50` `CCollisionSeekingRound__InitCollisionLineAndSound`
- `0x00425c60` `CCollisionSeekingRound__FilterCollisionCandidateByTrajectory`
- `0x00425e30` `CCollisionSeekingRound__UpdatePrimarySeekerLeadVector`
- `0x00426370` `CCollisionSeekingThing__ReplacePrimarySeekerAndRefreshOffset`
- `0x004264a0` `CCollisionSeekingThing__ResolveCollisionResponse`
- `0x00426920` `CCollisionSeekingThing__ComputeScaledMapCellChebyshevDistance`
- `0x00426a00` `CCSPersistentThing__ProcessMapWhoCollisionSweep`
- `0x00426a20` `CCSPersistentThing__HandleEvent`

## Remaining Work

- Resolve the remaining helper allocations and `CCSRay`-specific overrides; the persistent/round/infantry hierarchy itself is now exact.
- Add concrete structure types and local-variable names only after stronger layout evidence; add further tags only after fresh read-back justifies them.
- Keep runtime projectile/collision behavior separate from static saved-Ghidra evidence until copied-profile runtime proof exists.
