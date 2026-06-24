# Ghidra Wave900 Through Wave1014 Static Re-Audit Recheck

Status: PASS
Date: 2026-05-31
Scope: Wave900-Wave1014 static re-audit evidence

Wave1014 extends the current Wave900+ recheck gate after `particle-set-load-lifecycle-review-wave1014` re-read ParticleSet load/factory/lifecycle rows and ParticleManager active-list link/unlink bridge rows with no mutation. The gate preserves the earlier Wave900-Wave981 structural audits, reruns Wave982-Wave1014 focused probes directly, and checks current queue closure.

Current Wave1014 anchors: `0x004cc020 CParticleSet__CreateByType`, `0x004cc850 CParticleSet__Init`, `0x004ccb40 CParticleSet__shared_scalar_deleting_dtor`, `0x004ccc50 CPDSelector__DispatchChildVFunc20`, `0x004cd290 CParticleSet__InitType11`, `0x004cd2d0 CParticleSet__InitType12`, `0x004cd3c0 CParticleSet__InitType13`, `0x004cd7f0 CParticleSet__LoadFromArchive`, `0x004cda60 CParticleSet__LoadParticleSetFile`, and `0x004cdbe0 CParticleManager__UnlinkNodeByOffset3C40`. Queue closure after Wave1014 is `6238/6238 = 100.00%`. Re-audit progress after Wave1014 is Wave911 focused `505/1408 = 35.87%`, expanded static surface `729/1493 = 48.83%`, and Wave911 top-500 risk-ranked `431/500 = 86.20%`.

The Wave1014 verified backup is `G:\GhidraBackups\BEA_20260531-191245_post_wave1014_particle_set_load_lifecycle_review_verified`, 18 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1014; particle-set-load-lifecycle-review-wave1014; 0x004cc020 CParticleSet__CreateByType; 0x004cc850 CParticleSet__Init; 0x004ccb40 CParticleSet__shared_scalar_deleting_dtor; 0x004ccc50 CPDSelector__DispatchChildVFunc20; 0x004cd290 CParticleSet__InitType11; 0x004cd2d0 CParticleSet__InitType12; 0x004cd3c0 CParticleSet__InitType13; 0x004cd7f0 CParticleSet__LoadFromArchive; 0x004cda60 CParticleSet__LoadParticleSetFile; 0x004cdbe0 CParticleManager__UnlinkNodeByOffset3C40; 505/1408 = 35.87%; 729/1493 = 48.83%; 431/500 = 86.20%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260531-191245_post_wave1014_particle_set_load_lifecycle_review_verified; no mutation.

Validation command:

```powershell
cmd.exe /c npm run test:ghidra-wave900-plus-through-wave1014-recheck
```

Validation result: PASS. The Wave900-Wave1014 gate verified 117 readiness notes, 115 covered waves, 113 package probe scripts, 113 ignored evidence bases, 115 backup references, and 37 apply scripts. Direct Wave982-Wave1014 focused-probe classification wrote `subagents/ghidra-static-reaudit/wave900-plus-through-wave1014-recheck/wave982-wave1014-direct-probe-results.tsv` with 33 results: 1 direct pass, 32 classified stale-current failures, and 0 disallowed evidence failures. Current queue remained `6238/6238 = 100.00%` with 0 commentless functions, 0 exact-undefined signatures, and 0 `param_N` signatures.

Boundary note: this gate validates static evidence structure, backups, apply logs, focused probe classifications, and current queue closure. It does not prove runtime particle loading, runtime effect/render behavior, exact source-layout identity, concrete layouts, BEA patching, or rebuild parity.

Prior current gate: `release/readiness/ghidra_wave900_plus_through_wave1013_recheck_2026-05-31.md`.
