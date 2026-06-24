# Ghidra Wave900+ Through Wave1075 Recheck Note

Status: PASS
Date: 2026-06-02
Scope: `wave900-plus-through-wave1075-recheck`

This note extends the post-Wave900 recheck chain through Wave1075 and records the Wave1075 local validation gate:

```powershell
npm run test:ghidra-wave900-plus-through-wave1075-recheck
```

Wave1075 (`cunit-vfunc08-boundary-wave1075`) recovered and saved one previously missing Ghidra function boundary at `0x004dfa40 CUnit__VFunc08_InitAndAddToWorld`. The focused readiness note is [`ghidra_cunit_vfunc08_boundary_wave1075_2026-06-02.md`](ghidra_cunit_vfunc08_boundary_wave1075_2026-06-02.md).

Aggregate result:

- Status: `PASS`
- Readiness notes: `178`
- Covered waves: `176`
- Package probe scripts: `174`
- Evidence bases: `174`
- Backup references: `176`
- Apply scripts: `55`
- Wave982-Wave1075 direct probes: `resultCount=94`, `passCount=1`, `failCount=93`, `disallowedFailureCount=0`
- Current queue: `totalFunctions=6248`, `commentlessFunctionCount=0`, `undefinedSignatureCount=0`, `paramSignatureCount=0`, `status=PASS`

Coverage anchors:

- Static function-quality closure is `6248/6248 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1359/1560 = 87.12%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-060358_post_wave1075_cunit_vfunc08_boundary_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Exact source virtual name, concrete CUnit/init/world-layout semantics, runtime init/add-to-world/static-shadow behavior, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1075; cunit-vfunc08-boundary-wave1075; 0x004dfa40 CUnit__VFunc08_InitAndAddToWorld; 0x005dfd40; 0x005dfd60; 0x004dfa47; 0x004dfa9a; 0x004dfaa0; CUnit__Init; CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk; 812/1408 = 57.67%; 1359/1560 = 87.12%; 500/500 = 100.00%; 6248/6248 = 100.00%; G:\GhidraBackups\BEA_20260602-060358_post_wave1075_cunit_vfunc08_boundary_verified; boundary recovery.
