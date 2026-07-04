# Ghidra Line/Cylinder Dispatch Review Wave940 Readiness

Status: complete read-only static review
Date: 2026-05-28
Scope: `line-cylinder-dispatch-review-wave940`

Wave940 re-reviewed the line/cylinder primitive dispatch wrappers selected from the Wave911 risk-ranked continuation queue after a Composer 2.5 consult and fresh serialized Ghidra exports. The cluster ties the shared trivial vfuncs, the `CCylinder` slot-1 dispatcher, the `CLine` slot-1 dispatcher, the `CLine` copy constructor, the shared CLine-style scalar-deleting destructor/base-vtable reset, and the adjacent `CSphere`/`CMeshCollisionVolume` collision context.

The fresh evidence found no rename, signature, comment, function-boundary, or tag correction strong enough to justify a Ghidra mutation. No executable bytes were changed.

Primary targets:

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x004014c0` | `SharedVFunc__NoOpOneArg_004014c0` | Shared one-stack-argument `RET 0x4` target with broad DATA xrefs; owner-specific narrowing remains unsafe. |
| `0x00405930` | `SharedVFunc__ReturnZero_00405930` | Shared no-argument return-zero vtable target used by broad unrelated tables. |
| `0x00405940` | `SharedVFunc__ReturnZeroRet4_00405940` | Shared return-zero target that cleans one stack argument. |
| `0x004059a0` | `CCylinder__VFunc_01_004059a0` | `CCylinder` table `0x005d88cc` slots `1`, `3`, and `5`; forwards four stack arguments plus `this` into `dispatchObject` vfunc `+0x8`. |
| `0x004098c0` | `CLine__VFunc_01_004098c0` | `CLine` table `0x005d8bfc` slots `1`, `2`, `3`, and `5`; forwards four stack arguments plus `this` into `dispatch_target` vfunc `+0x10`. |
| `0x004098e0` | `CLine__ctor_copy` | Installs CGeneralVolume base table `0x005d892c`, copies three 16-byte blocks from `sourceLine`, then installs CLine table `0x005d8bfc`. |
| `0x00426340` | `CLine__ScalarDeletingDestructor_00426340` | Shared scalar-deleting destructor at `CCylinder`, `CLine`, and `0x005d95e8` sphere/context table slots; calls `CLine__SetBaseVtable_00426360` and frees only when delete flag bit 1 is set. |
| `0x00426360` | `CLine__SetBaseVtable_00426360` | Tiny base-table reset used by the scalar-deleting destructor and many unwind cleanup thunks. |

Context anchors:

- `0x0040d470 CLine__ctor_fromEndpoints` preserves the endpoint constructor shape that installs the CLine table after copying two 16-byte endpoints.
- `0x0043fde0 CCylinder__ctor`, `0x0043fe20 CCylinder__ResolveCollisionVFunc02`, `0x004e4d70 CSphere__VFunc02_ResolveCollisionAsCylinder`, and `0x00426320 CSphere__VFunc_01_00426320` keep the cylinder/sphere dispatch context joined to vtables `0x005d88cc` and `0x005d95e8`.
- `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`, `0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism`, `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord`, and `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830` preserve the adjacent MeshCollisionVolume collision context from Waves913 and 939.
- Shared trivial targets `0x004014a0 SharedVFunc__Return1_004014a0`, `0x004059c0 SharedVFunc__Return2_004059c0`, `0x00452da0 SharedVFunc__NoOp_Ret08`, and `0x00453ac0 SharedVFunc__NoOp_Ret0C` remain broad shared table entries, not owner-specific proof.

Fresh read-back evidence:

- Primary exports: 8 metadata rows, 8 tag rows, 1462 xref rows, 85 instruction rows, and 8 decompile rows.
- Context exports: 13 metadata rows, 13 tag rows, 528 xref rows, 1830 instruction rows, and 13 decompile rows.
- Vtable export: 24 rows across `0x005d88cc`, `0x005d8bfc`, and `0x005d95e8`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-030741_post_wave940_line_cylinder_dispatch_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.
- Mutation status: read-only review; no dry/apply/final-dry mutation scripts were run because the saved rows already matched the bounded static evidence.

Progress:

- Wave911 focused re-audit progress after Wave940: `178/1408 = 12.64%`.
- Static export-contract function-quality closure remains `6113/6113 = 100.00%`.

Probe token anchor: Wave940; `line-cylinder-dispatch-review-wave940`; `0x004059a0 CCylinder__VFunc_01_004059a0`; `0x004098c0 CLine__VFunc_01_004098c0`; `0x004098e0 CLine__ctor_copy`; `0x00426340 CLine__ScalarDeletingDestructor_00426340`; `0x00426360 CLine__SetBaseVtable_00426360`; `0x00426320 CSphere__VFunc_01_00426320`; `0x005d88cc`; `0x005d8bfc`; `0x005d95e8`; read-only review; `178/1408 = 12.64%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-030741_post_wave940_line_cylinder_dispatch_review_verified`.

What this proves:

- The selected line/cylinder primitive dispatch rows remain present in the saved Ghidra project with coherent names, signatures, xrefs, instructions, vtable slots, and decompile outputs.
- The saved wrappers are still best treated as primitive dispatch/context wrappers, not fully typed source methods.
- The CLine/Cylinder/Sphere vtable join remains statically coherent across the exported table slots.

What remains unproven:

- Exact source-body identity.
- Concrete CLine, CGeneralVolume, CCylinder, CSphere, contact, and primitive query layouts.
- Runtime collision/trace behavior.
- Runtime primitive dispatch behavior.
- BEA patching behavior.
- Rebuild parity.
