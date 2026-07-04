# Ghidra Wave900+ Through Wave1083 Recheck Note

Status: PASS
Date: 2026-06-02
Scope: `wave900-plus-through-wave1083-recheck`

This note extends the post-Wave900 recheck chain through Wave1083 and records the Wave1083 local validation gate:

```powershell
npm run test:ghidra-wave900-plus-through-wave1083-recheck
```

Wave1083 (`shared-unit-vtable-boundary-review-wave1083`) recovered and saved thirteen previously unresolved shared unit-family vtable-boundary functions, including `0x00405d90 SharedUnitVFunc__ReturnField130ColorMask_00405d90`, `0x004f9260 SharedUnitVFunc__BuildField164TargetVectorContext_004f9260`, and `0x004fe5f0 SharedUnitVFunc__ScheduleEvent7d0WithMinusOne_004fe5f0`. Sampled vtable starts include `0x005e3700` and `0x005dd710`. The focused readiness note is [`ghidra_shared_unit_vtable_boundary_wave1083_2026-06-02.md`](ghidra_shared_unit_vtable_boundary_wave1083_2026-06-02.md).

Aggregate result:

- Status: `PASS`
- Readiness notes: `186`
- Covered waves: `184`
- Package probe scripts: `182`
- Evidence bases: `182`
- Backup references: `184`
- Apply scripts: `63`
- Wave982-Wave1083 direct probes: `resultCount=102`, `passCount=1`, `failCount=101`, `disallowedFailureCount=0`
- Current queue: `totalFunctions=6307`, `commentlessFunctionCount=0`, `undefinedSignatureCount=0`, `paramSignatureCount=0`, `status=PASS`

Coverage anchors:

- Static function-quality closure is `6307/6307 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1418/1560 = 90.90%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-114534_post_wave1083_shared_unit_vtable_boundary_verified`, `19` files, `174820231` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Exact source virtual names, concrete unit-family layout semantics, runtime targeting/render/event/list behavior, runtime gameplay outcomes, BEA patching behavior, and rebuild parity remain separate proof.

Probe token anchor: Wave1083; shared-unit-vtable-boundary-review-wave1083; 0x00405d90 SharedUnitVFunc__ReturnField130ColorMask_00405d90; 0x004f9260 SharedUnitVFunc__BuildField164TargetVectorContext_004f9260; 0x004fe5f0 SharedUnitVFunc__ScheduleEvent7d0WithMinusOne_004fe5f0; 0x005e3700; 0x005dd710; 1418/1560 = 90.90%; 812/1408 = 57.67%; 500/500 = 100.00%; 6307/6307 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-114534_post_wave1083_shared_unit_vtable_boundary_verified; boundary recovery.
