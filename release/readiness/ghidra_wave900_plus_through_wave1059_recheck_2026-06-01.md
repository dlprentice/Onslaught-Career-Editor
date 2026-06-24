# Ghidra Wave900 Through Wave1059 Recheck

Status: complete local static evidence gate
Date: 2026-06-01
Scope: `wave900-plus-through-wave1059-recheck`

This note extends the Wave900-plus static recheck boundary through Wave1059. Wave900 remains the loaded-Ghidra export-contract function-quality closure point; Wave1059 adds tag normalization for the collision-seeking round tail and adjacent context rows.

Wave1059 (`collision-seeking-round-tail-review-wave1059`) re-read eight primary collision-seeking tail rows and six adjacent context rows, then saved function tags only: `0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound`, `0x00425e30 CCollisionSeekingRound__UpdatePrimarySeekerLeadVector`, `0x00426300 CMeshCollisionVolume__ScalarDeletingDestructor_00426300`, `0x00426370 CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset`, `0x004263f0 CCollisionSeekingRound__Destructor`, `0x00426460 CCollisionSeekingRound__ScalarDeletingDestructor`, `0x00426480 CCollisionSeekingRound__SetCollisionMask`, `0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse`, `0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags`, `0x00425c60 CCollisionSeekingRound__FilterCollisionCandidateByTrajectory`, `0x00426900 CCollisionSeekingRound__CheckCollisionFlags`, `0x00426920 CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance`, `0x00426a00 CCollisionSeekingRound__ProcessMapWhoCollisionSweep`, and `0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady`.

Fresh evidence:

- Primary pre/post exports: `8` metadata rows, `8` tag rows, `26` xref rows, `665` function-body instruction rows, and `8` decompile rows.
- Context pre/post exports: `6` metadata rows, `6` tag rows, `18` xref rows, `257` function-body instruction rows, and `6` decompile rows.
- Dry/apply/final-dry sequence: dry `updated=0 skipped=0 tags_added=131 missing=0 bad=0`; apply `updated=14 skipped=0 tags_added=131 missing=0 bad=0`; final dry `updated=0 skipped=14 tags_added=0 missing=0 bad=0`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress advances to `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1140/1509 = 75.55%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified`, `19` files, `174689159` bytes, `DiffCount=0`, `HashDiffCount=0`.

Validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1059-recheck
```

Boundary note: this aggregate gate is static documentation/evidence hygiene. Runtime projectile, collision, event, delayed-ready, and response behavior; exact helper layouts; exact source-body identity; BEA patching behavior; gameplay outcomes; and rebuild parity remain separate proof.

Probe token anchor: Wave1059; collision-seeking-round-tail-review-wave1059; 0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound; 0x00425e30 CCollisionSeekingRound__UpdatePrimarySeekerLeadVector; 0x00426300 CMeshCollisionVolume__ScalarDeletingDestructor_00426300; 0x00426370 CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset; 0x004263f0 CCollisionSeekingRound__Destructor; 0x00426480 CCollisionSeekingRound__SetCollisionMask; 0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse; 0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady; 812/1408 = 57.67%; 1140/1509 = 75.55%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified; tag normalization.
