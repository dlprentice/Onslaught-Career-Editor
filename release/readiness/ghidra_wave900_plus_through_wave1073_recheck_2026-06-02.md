# Ghidra Wave900+ Through Wave1073 Recheck Note

Status: PASS
Date: 2026-06-02
Scope: `wave900-plus-through-wave1073-recheck`

This note extends the post-Wave900 recheck chain through Wave1073 and records the Wave1073 local validation gate:

```powershell
npm run test:ghidra-wave900-plus-through-wave1073-recheck
```

Wave1073 (`cworld-load-tail-review-wave1073`) re-read twenty-three existing Wave555/Wave556 CWorld load/core, CWorld tail, CWorldMeshList, and CWorldPhysicsManager factory rows plus eighteen context rows with no mutation. The focused readiness note is [`ghidra_cworld_load_tail_review_wave1073_2026-06-02.md`](ghidra_cworld_load_tail_review_wave1073_2026-06-02.md).

Aggregate result:

- Status: `PASS`
- Readiness notes: `176`
- Covered waves: `174`
- Package probe scripts: `172`
- Evidence bases: `172`
- Backup references: `174`
- Apply scripts: `53`
- Wave982-Wave1073 direct probes: `resultCount=92`, `passCount=1`, `failCount=91`, `disallowedFailureCount=0`
- Current queue: `totalFunctions=6246`, `commentlessFunctionCount=0`, `undefinedSignatureCount=0`, `paramSignatureCount=0`, `status=PASS`

Coverage anchors:

- Static function-quality closure remains `6246/6246 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1357/1560 = 86.99%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Runtime behavior, exact raw-boundary identities, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1073; cworld-load-tail-review-wave1073; 0x0050a870 CWorld__ClearSetArrays; 0x0050ac70 CWorld__LoadScriptEvents; 0x0050b520 CWorld__LoadWorldFile; 0x0050d6a0 CWorld__PushWorldTextSlot; 0x0050d9e0 CWorldMeshList__Add; 0x0050dcb0 CWorld__SpawnInitialThings; 0x0050df80 CWorldPhysicsManager__CreateThingByType; 0x00537c40; 0x004dfa47; 812/1408 = 57.67%; 1357/1560 = 86.99%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified; read-only review.
