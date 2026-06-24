# Ghidra Mesh Segment Tail Wave814 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `mesh-segment-tail-wave814`

Wave814 mesh segment tail saved names, signatures, comments, and tags for four adjacent CMesh/CRTMesh/destructible-segment helper rows after serialized headless dry/apply/read-back. The pass corrected stale owners and stale phantom parameters on `0x004aa4e0` through `0x004aa8a0`, made no function-boundary changes, and made no executable-byte changes.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004aa4e0 CMesh__SumChainedField1C` | `int __thiscall CMesh__SumChainedField1C(void * this)` | Recursively follows the CMesh/resource chain pointer at `this+0x08` and sums each node's field `+0x1c`; `CRTMesh__Init` calls it on the mesh/resource pointer at `this+0x14`. |
| `0x004aa500 CMesh__GetChainedRecordNameAndIdByIndex` | `void __thiscall CMesh__GetChainedRecordNameAndIdByIndex(void * this, int record_index, void * out_name, int * out_record_id)` | Resolves a flat index across the same chain, copies the selected 0x150-byte record name at `+0x4c`, writes record field `+0x14c`, and falls back to empty string `0x00662b2c` plus `-1`; `RET 0xc` removes the stale `unused_ctx`. |
| `0x004aa6b0 CMesh__GetNameOrUnknown` | `void * __thiscall CMesh__GetNameOrUnknown(void * this)` | Scans global mesh list `DAT_00704ad8` by next-link `+0x158`, returns mesh name `+0x24`, or returns `0x0062f8d4` (`unknown mesh name`); caller read-back proves the old controller-specific one-stack-argument signature was stale. |
| `0x004aa8a0 CMesh__FindPartByNameI` | `void * __thiscall CMesh__FindPartByNameI(void * this, char * part_name)` | Scans CMesh part pointer table `this+0x160` for count `this+0x15c`, compares each part name at `part+0xdc` with `stricmp`, returns the matching part pointer or null; `RET 0x4` removes the stale `unused_ctx`. |

Read-back evidence:

- `ApplyMeshSegmentTailWave814.java dry`: `updated=0 skipped=4 renamed=0 would_rename=4 signature_updated=3 comment_only_updated=4 missing=0 bad=0`
- `ApplyMeshSegmentTailWave814.java apply`: `updated=4 skipped=0 renamed=4 would_rename=0 signature_updated=3 comment_only_updated=4 missing=0 bad=0`
- `ApplyMeshSegmentTailWave814.java final dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 4 metadata rows, 4 tag rows, 24 xref rows, 884 instruction rows, 4 decompile rows, 12 caller metadata rows, 12 caller decompile rows, and 504 callsite instruction rows.
- Queue after Wave814: 6098 total, 5595 commented, 503 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5595/6098 = 91.75%`, strict proxy `5595/6098 = 91.75%`.
- Next raw commentless row: `0x004adf80 CMesh__ClearField08`; commentless high-signal, signature, and name-confidence queues are empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-141602_post_wave814_mesh_segment_tail_verified`, 19 files, 171346823 bytes, `DiffCount=0`.

What this proves:

- The four target rows exist in the saved Ghidra project with the saved names, signatures, comments, and `mesh-segment-tail-wave814` / `wave814-readback-verified` tags.
- The observed bodies and caller decompiles support the CMesh ownership corrections and the removal of stale phantom parameters.
- The queue snapshot reflects four additional strict-clean/commented rows.

What remains unproven:

- Exact concrete CMesh, CMeshPart, CRTMesh, and destructible-segment layouts.
- Exact source-body identity for these helpers.
- Runtime mesh/destructible/RTMesh behavior.
- BEA patching behavior.
- Rebuild parity.
