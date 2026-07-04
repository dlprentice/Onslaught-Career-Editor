# Ghidra Wave900+ Through Wave1080 Recheck Note

Status: PASS
Date: 2026-06-02
Scope: `wave900-plus-through-wave1080-recheck`

This note extends the post-Wave900 recheck chain through Wave1080 and records the Wave1080 local validation gate:

```powershell
npm run test:ghidra-wave900-plus-through-wave1080-recheck
```

Wave1080 (`thing-waypoint-vtable-boundary-wave1080`) recovered and saved fourteen previously unresolved CThing-family/CWaypoint true-vtable function boundaries, including `0x004013f0 SharedVFunc__ReturnColorFF000080_004013f0`, `0x00401400 SharedVFunc__ForwardField28Slot18OrFallbackFloat_00401400`, `0x004040a0 SharedVFunc__CopyVector14ToOut_004040a0`, `0x004bfb50 CWaypoint__GetClassNameString_004bfb50`, `0x004f3460 CThing__GetClassNameString_004f3460`, and `0x0052db60 CWaypoint__GetTypeId12_0052db60`. The focused readiness note is [`ghidra_thing_waypoint_vtable_boundary_wave1080_2026-06-02.md`](ghidra_thing_waypoint_vtable_boundary_wave1080_2026-06-02.md).

Aggregate result:

- Status: `PASS`
- Readiness notes: `183`
- Covered waves: `181`
- Package probe scripts: `179`
- Evidence bases: `179`
- Backup references: `181`
- Apply scripts: `60`
- Wave982-Wave1080 direct probes: `resultCount=99`, `passCount=1`, `failCount=98`, `disallowedFailureCount=0`
- Current queue: `totalFunctions=6276`, `commentlessFunctionCount=0`, `undefinedSignatureCount=0`, `paramSignatureCount=0`, `status=PASS`

Coverage anchors:

- Static function-quality closure is `6276/6276 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1387/1560 = 88.91%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-095224_post_wave1080_thing_waypoint_vtable_boundary_verified`, `19` files, `174787463` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Exact source virtual names, concrete CThing/CWaypoint/CInfantryAI layout semantics, type-mask bit labels, runtime object/class-name/type-mask/vector-copy behavior, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1080; thing-waypoint-vtable-boundary-wave1080; 0x004013f0 SharedVFunc__ReturnColorFF000080_004013f0; 0x00401400 SharedVFunc__ForwardField28Slot18OrFallbackFloat_00401400; 0x004040a0 SharedVFunc__CopyVector14ToOut_004040a0; 0x004bfb50 CWaypoint__GetClassNameString_004bfb50; 0x004f3460 CThing__GetClassNameString_004f3460; 0x0052db60 CWaypoint__GetTypeId12_0052db60; 0x005df550; 0x005dd278; 0x005dbf14; 812/1408 = 57.67%; 1387/1560 = 88.91%; 500/500 = 100.00%; 6276/6276 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-095224_post_wave1080_thing_waypoint_vtable_boundary_verified; boundary recovery.
