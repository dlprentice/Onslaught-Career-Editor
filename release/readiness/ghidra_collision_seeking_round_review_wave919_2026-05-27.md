# Ghidra Wave919 collision-seeking round review (2026-05-27)

Status: read-only static review
Date: 2026-05-27
Branch: `main`
Tag: `collision-seeking-round-review-wave919`

## Scope

Wave919 reviewed six collision-seeking round / infantry-bloke helper rows from the Wave911 focused correction queue:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00425a10` | `CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags` | Reviewed; no mutation |
| `0x00425c60` | `CCollisionSeekingRound__FilterCollisionCandidateByTrajectory` | Reviewed; no mutation |
| `0x00426900` | `CCollisionSeekingRound__CheckCollisionFlags` | Reviewed; no mutation |
| `0x00426920` | `CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance` | Reviewed; no mutation |
| `0x00426a00` | `CCollisionSeekingRound__ProcessMapWhoCollisionSweep` | Reviewed; no mutation |
| `0x00426a20` | `CCollisionSeekingRound__MarkDelayedCollisionReady` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave919-collision-seeking-round-review/metadata.tsv
subagents/ghidra-static-reaudit/wave919-collision-seeking-round-review/tags.tsv
subagents/ghidra-static-reaudit/wave919-collision-seeking-round-review/instructions.tsv
subagents/ghidra-static-reaudit/wave919-collision-seeking-round-review/decompile/
```

Read-back result:

```text
metadata: 6/6 OK
tags: 6/6 OK (no saved tags on these six)
instructions: 257 rows
decompile: 6/6 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current static evidence. The current source snapshot references `CollisionSeekingRound.h`/`collisionseekingthing.cpp` only indirectly, so no stronger source-backed correction was available.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
G:\GhidraBackups\BEA_20260527-121935_post_wave919_collision_seeking_round_review_verified
files=19
bytes=173247367
```

## Truth boundary

This review confirms static Ghidra coherence for selected collision-seeking round helpers. It does not prove runtime collision behavior, concrete round/helper layouts, exact virtual method names, BEA patch behavior, or rebuild parity.

## Next

Continue Wave920 with another focused cluster, preferably CRound projectile/targeting helpers, HiveBoss config helpers, or frontend text/layout helpers where source-callsite evidence may be stronger.
