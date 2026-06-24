# Ghidra Mesh / Fear Grid Signature Tranche - 2026-05-13

Status: GREEN public-safe saved-Ghidra evidence

## Summary

Serialized headless dry/apply/read-back hardened `7` saved Ghidra targets around mesh deserialization helpers and the FearGrid occupancy/clearance sampler cluster. This pass corrected three caller-biased labels to `CFearGrid` ownership, corrected the constructor-style FearGrid target name, and tightened two CMesh helper signatures.

| Address | Saved name | Public-safe static evidence |
| --- | --- | --- |
| `0x0044c1c0` | `CMesh__DeserializeTripletDwords` | One `mem_buffer` stack argument, three `CDXMemBuffer__Read` dword reads into `this+0x00/+0x04/+0x08`, and `ret 0x4` callsite shape. |
| `0x0044c210` | `CMesh__DeserializeNineDwords` | One `mem_buffer` stack argument, nine `CDXMemBuffer__Read` dword reads through `this+0x28`, and `ret 0x4` callsite shape. |
| `0x0044c3d0` | `CFearGrid__ctor_base` | Constructor-style return-this body, `CFearGrid` vtable assignment, saved `grid_id` field, and immediate rebuild/schedule call. |
| `0x0044c440` | `CFearGrid__RebuildOccupancyAndScheduleTick` | Rebuilds occupancy/clearance planes, filters by grid id, calls the archetype weight lookup helper, and schedules event `1000`. |
| `0x0044c720` | `CFearGrid__GetOccupancyAtWorldVector` | Corrected from stale `CSquadNormal` ownership; called through global FearGrid pointers with a 16-byte by-value vector and samples the occupancy plane. |
| `0x0044c780` | `CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta` | Corrected from stale `OID` ownership; called through global FearGrid pointers with a 16-byte by-value vector, shadow-height threshold gate, and clearance-plane read. |
| `0x0044c810` | `CFearGrid__FindNearestFreeCellSpiral` | Corrected from stale `CSquadNormal` ownership; searches nearby free occupancy cells and updates the in/out world vector. |

## Validation

- `ApplyMeshGridSignatureTranche.java` dry run: `targets=7 updated=0 skipped=7 failed=0`.
- `ApplyMeshGridSignatureTranche.java` apply run: `targets=7 updated=7 skipped=0 failed=0`, with `REPORT: Save succeeded`.
- Read-back exports verified `7` metadata rows, `7` decompile exports, `25` xref rows, `1743` instruction rows, `348` callsite-instruction rows, and `7` tag rows.
- `cmd.exe /c npm run test:ghidra-mesh-grid-signature` passed with focused probe status `PASS`, `9/9` xref evidence hits, `13/13` instruction evidence hits, and `8/8` callsite evidence hits.
- Whole-database quality refresh reports `6008` functions, `1270` commented functions, `4738` commentless functions, `1948` undefined signatures, and `1999` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1270/6008 = 21.14%` and strict clean-signature `1208/6008 = 20.11%`. These values are not milestones or completion gates; the target remains as close to `100%` evidence-grade static RE as possible.
- The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260513_072135_post_wave366_mesh_grid_verified` with `19` files, `153226119` bytes, and `HashDiffCount=0`.

## Claim Boundary

This is saved static Ghidra name/signature/comment/tag evidence only. It does not prove exact Stuart-source method identity for every target, concrete structure layouts, local variable recovery, runtime mesh/FearGrid/AI behavior, BEA launch behavior, game patching, or rebuild parity. The older caller-biased labels are superseded for these checked targets, but adjacent callers still need their own evidence-grade review.
