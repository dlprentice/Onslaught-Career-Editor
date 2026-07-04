# Ghidra Wave900+ Through Wave1081 Recheck Note

Status: PASS
Date: 2026-06-02
Scope: `wave900-plus-through-wave1081-recheck`

This note extends the post-Wave900 recheck chain through Wave1081 and records the Wave1081 local validation gate:

```powershell
npm run test:ghidra-wave900-plus-through-wave1081-recheck
```

Wave1081 (`cthing-waypoint-residual-vtable-boundary-wave1081`) recovered and saved seven previously unresolved CThing/CWaypoint residual true-vtable function boundaries, including `0x004bfa00 SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa00`, `0x004f3760 CThing__AddShutdownEvent_004f3760`, `0x004f37a0 CThing__StartDieProcess_004f37a0`, `0x004f3d20 SharedVFunc__ForwardField28Slot10OrNull_004f3d20`, and `0x0043e9c0 SharedVFunc__CopyGlobal0066ea10Block10ToOut_0043e9c0`. The focused readiness note is [`ghidra_cthing_waypoint_residual_vtable_boundary_wave1081_2026-06-02.md`](ghidra_cthing_waypoint_residual_vtable_boundary_wave1081_2026-06-02.md).

Aggregate result:

- Status: `PASS`
- Readiness notes: `184`
- Covered waves: `182`
- Package probe scripts: `180`
- Evidence bases: `180`
- Backup references: `182`
- Apply scripts: `61`
- Wave982-Wave1081 direct probes: `resultCount=100`, `passCount=1`, `failCount=99`, `disallowedFailureCount=0`
- Current queue: `totalFunctions=6283`, `commentlessFunctionCount=0`, `undefinedSignatureCount=0`, `paramSignatureCount=0`, `status=PASS`

Coverage anchors:

- Static function-quality closure is `6283/6283 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1394/1560 = 89.36%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-103048_post_wave1081_cthing_waypoint_residual_vtable_boundary_verified`, `19` files, `174787463` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Exact source virtual names, concrete CThing/CWaypoint/CInfantryAI layout semantics, global block identity, runtime event-delivery/death-process/field-forward/output-copy behavior, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1081; cthing-waypoint-residual-vtable-boundary-wave1081; 0x004bfa00 SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa00; 0x004f3760 CThing__AddShutdownEvent_004f3760; 0x004f37a0 CThing__StartDieProcess_004f37a0; 0x004f3d20 SharedVFunc__ForwardField28Slot10OrNull_004f3d20; 0x0043e9c0 SharedVFunc__CopyGlobal0066ea10Block10ToOut_0043e9c0; 0x005df550; 0x005dd278; 0x005dbf14; 812/1408 = 57.67%; 1394/1560 = 89.36%; 500/500 = 100.00%; 6283/6283 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-103048_post_wave1081_cthing_waypoint_residual_vtable_boundary_verified; boundary recovery.
