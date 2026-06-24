# Ghidra Wave900+ Through Wave1076 Recheck Note

Status: PASS
Date: 2026-06-02
Scope: `wave900-plus-through-wave1076-recheck`

This note extends the post-Wave900 recheck chain through Wave1076 and records the Wave1076 local validation gate:

```powershell
npm run test:ghidra-wave900-plus-through-wave1076-recheck
```

Wave1076 (`infantryunit-lifecycle-boundary-wave1076`) recovered and saved six previously missing CInfantryUnit primary-vtable function boundaries at `0x00488f10 CInfantryUnit__VFunc38_HandleHitOrDispatchHit`, `0x00488f80 CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius`, `0x00489090 CInfantryUnit__VFunc59_SelectAnimationMode`, `0x004892c0 CInfantryUnit__VFunc65_UpdateMotionAnimationState`, `0x00489650 CInfantryUnit__VFunc39_HandleCollisionDamageReaction`, and `0x00489b40 CInfantryUnit__VFunc49_HandleDeathPickupAndEffects`. The focused readiness note is [`ghidra_infantryunit_lifecycle_boundary_wave1076_2026-06-02.md`](ghidra_infantryunit_lifecycle_boundary_wave1076_2026-06-02.md).

Aggregate result:

- Status: `PASS`
- Readiness notes: `179`
- Covered waves: `177`
- Package probe scripts: `175`
- Evidence bases: `175`
- Backup references: `177`
- Apply scripts: `56`
- Wave982-Wave1076 direct probes: `resultCount=95`, `passCount=1`, `failCount=94`, `disallowedFailureCount=0`
- Current queue: `totalFunctions=6254`, `commentlessFunctionCount=0`, `undefinedSignatureCount=0`, `paramSignatureCount=0`, `status=PASS`

Coverage anchors:

- Static function-quality closure is `6254/6254 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1365/1560 = 87.50%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-065500_post_wave1076_infantryunit_lifecycle_boundary_verified`, `19` files, `174754695` bytes, `DiffCount=0`, `HashDiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Exact source virtual names, concrete CInfantryUnit/CUnitAI/layout semantics, runtime infantry behavior, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1076; infantryunit-lifecycle-boundary-wave1076; 0x00488f10 CInfantryUnit__VFunc38_HandleHitOrDispatchHit; 0x00488f80 CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius; 0x00489090 CInfantryUnit__VFunc59_SelectAnimationMode; 0x004892c0 CInfantryUnit__VFunc65_UpdateMotionAnimationState; 0x00489650 CInfantryUnit__VFunc39_HandleCollisionDamageReaction; 0x00489b40 CInfantryUnit__VFunc49_HandleDeathPickupAndEffects; 0x005e2730; 0x005e27b8; 0x005e27c8; 0x005e27cc; 0x005e27f4; 0x005e281c; 0x005e2834; 812/1408 = 57.67%; 1365/1560 = 87.50%; 500/500 = 100.00%; 6254/6254 = 100.00%; G:\GhidraBackups\BEA_20260602-065500_post_wave1076_infantryunit_lifecycle_boundary_verified; boundary recovery.
