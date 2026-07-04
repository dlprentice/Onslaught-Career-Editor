# Ghidra Building/CBuildingNamedMesh Lifecycle Review Wave944 Readiness

Status: complete read-only static review
Date: 2026-05-28
Scope: `building-namedmesh-lifecycle-review-wave944`

Wave944 re-reviewed the Building/CBuildingNamedMesh lifecycle cluster selected from the Wave911 focused queue. Cursor Composer 2.5 gave candidate and adversarial read-only consults; root Codex then ran fresh serialized Ghidra metadata, tag, xref, instruction, decompile, and vtable exports.

The fresh evidence found no Ghidra rename, signature, comment, function-boundary, or tag correction strong enough to justify a mutation. No executable bytes were changed.

Primary targets:

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x004176c0` | `CThing__InitRenderThingFromInitMeshName` | `void __thiscall` with one `init` stack argument; DATA ref `0x005d8f3c` in the CBuilding table; decompile still builds `%s.msh` render names, calls `PCRTID__CreateObject`, and stores the render object at `this+0x30`. |
| `0x00417870` | `CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward` | DATA refs at `0x005d8ebc` and `0x005dfd44` place the body in CBuilding and CSimpleBuilding slot 2; decompile removes the object from world occupancy, updates static-shadow visibility, and forwards to `0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward`. |
| `0x004178a0` | `CBuilding__ProcessClosingAndUnshuttingAnimations` | DATA ref `0x005d8fbc`; decompile preserves the closing/unshutting animation-state gate over offsets `+0x254`, `+0x25c`, `+0x260`, `+0x264`, and `+0x268`. |
| `0x00418120` | `CBuilding__AdvanceOpenCloseAnimationState` | DATA ref `0x005d8fa0`; decompile preserves the open/close/shut state stepper that compares animation ids through vfunc `+0x58`, dispatches transitions through vfunc `+0xf0`, and updates offsets `+0x254` and `+0x264`. |
| `0x004183d0` | `CBuildingNamedMesh__dtor_base` | Fresh call xref from `0x00418433 CBuildingNamedMesh__scalar_deleting_dtor`; decompile resets the CBuildingNamedMesh vtable region and forwards to `CActor__dtor_base`. |
| `0x00418450` | `CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh` | DATA ref `0x005d9114` under vtable `0x005d910c`; decompile removes this object from world occupancy and forwards to `0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward`. |

Context anchors:

- Building destructor and scalar-delete context: `0x00417590 CBuilding__dtor_body_00417590` and `0x004176a0 CBuilding__scalar_deleting_dtor`.
- CBuildingNamedMesh scalar-delete context: `0x00418430 CBuildingNamedMesh__scalar_deleting_dtor`.
- NamedMesh forward/remove context: `0x004bbcd0 CNamedMesh__VFunc_09_004bbcd0` and `0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward`.
- Shared Unit slot-2 cleanup context: `0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward`.
- Vtable snapshots: `0x005d8eb4`, `0x005dfd3c`, `0x005d910c`, and `0x005dd5f0`, 48 slots each.

Fresh read-back evidence:

- Primary exports: 6 metadata rows, 6 tag rows, 7 xref rows, 351 instruction rows, and 6 decompile rows.
- Context exports: 6 metadata rows, 6 tag rows, 28 xref rows, 288 instruction rows, and 6 decompile rows.
- Vtable export: 192 rows across `0x005d8eb4`, `0x005dfd3c`, `0x005d910c`, and `0x005dd5f0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-050722_post_wave944_building_namedmesh_lifecycle_review_verified`, 19 files, 173280135 bytes, `DiffCount=0`.
- Mutation status: read-only review; no dry/apply/final-dry mutation scripts were run because the saved rows already matched the bounded static evidence.

Progress:

- Wave911 focused re-audit progress after Wave944: `192/1408 = 13.64%`.
- Static export-contract function-quality closure remains `6113/6113 = 100.00%`.

Probe token anchor: Wave944; `building-namedmesh-lifecycle-review-wave944`; read-only review; `0x004176c0 CThing__InitRenderThingFromInitMeshName`; `0x00417870 CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward`; `0x004178a0 CBuilding__ProcessClosingAndUnshuttingAnimations`; `0x00418120 CBuilding__AdvanceOpenCloseAnimationState`; `0x004183d0 CBuildingNamedMesh__dtor_base`; `0x00418430 CBuildingNamedMesh__scalar_deleting_dtor`; `0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh`; `0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward`; `0x005d8eb4`; `0x005dfd3c`; `0x005d910c`; `0x005dd5f0`; `192/1408 = 13.64%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-050722_post_wave944_building_namedmesh_lifecycle_review_verified`.

What this proves:

- The selected Building/CBuildingNamedMesh rows remain present in the saved Ghidra project with coherent names, signatures, comments, xrefs, instruction bodies, vtable context, and decompile outputs.
- The old Wave314 stale-owner risks remain corrected: the selected rows are not currently reverted to CUnit, CCockpit, or CByteSprite owners.

What remains unproven:

- Runtime building animation behavior.
- Runtime NamedMesh/world-occupancy behavior.
- Exact CBuilding, CSimpleBuilding, CBuildingNamedMesh, CNamedMesh, and CUnit layouts.
- Exact source virtual names for slot-index helpers.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
