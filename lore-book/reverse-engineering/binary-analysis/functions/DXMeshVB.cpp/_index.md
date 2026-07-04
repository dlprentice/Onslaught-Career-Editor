# DXMeshVB.cpp - DirectX Mesh Vertex Buffer Management

Wave1207 measured anchor: unique-address accounting governs active current-risk progress. Wave1207 (`wave1207-d3d-render-resource-lifecycle-current-risk-review`) accounts for `6 D3D/render-resource lifecycle current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This read-only review made no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1089/1179 = 92.37%`; remaining active focused work: 90; legacy additive counter is deprecated (`1120/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `36 xref rows`, `260 instruction rows`, and `6 decompile rows`. Anchors: `CVertexShader__scalar_deleting_dtor`, `CVertexShader__VFunc_02_00501a10`, `DeviceObject__dtor_body`, `DeviceObject__scalar_deleting_dtor`, `CDXMeshVB__scalar_deleting_dtor`, and `CDXMeshVB__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-033229_post_wave1207_d3d_render_resource_lifecycle_current_risk_review_verified`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime Direct3D behavior, runtime shader behavior, runtime render-resource behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

**Source File:** `[maintainer-local-source-export-root]\DXMeshVB.cpp`
**Debug String Address:** `0x00651244`
**Total Functions Found:** 7 Wave609-saved CDXMeshVB rows, plus 1 Wave610 renderer layer-pass row, plus 15 Wave650 CDXMeshVB/CFastVB strip rows, plus 10 Wave651 CFastVB strip-selection rows, plus 8 Wave652 CFastVB strip merge/emission rows, plus 7 Wave653 CFastVB vertex-cache/scoring rows, plus 1 Wave885 CFastVB strip-batch builder row

Wave1173 current-risk review (`wave1173-cfastvb-strip-candidate-current-risk-review`) re-read `3 CFastVB strip-candidate current-risk rows` from the Wave651 strip-selection island with fresh Ghidra export evidence and no mutation. Anchors are `CFastVB__TriangleListContainsVertexTriplet_0056ff40`, `CFastVB__InsertStripCandidatesIntoBuffer_005708a0`, and `CFastVB__InitializeCandidateParentLinks_00570be0`. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is now `675/1179 = 57.25%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 504; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult spawned; `3 xref rows`; `339 instruction rows`; backup `[maintainer-local-ghidra-backup-root]\BEA_20260606-073137_post_wave1173_cfastvb_strip_candidate_current_risk_review_verified`; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Runtime strip quality, concrete D3D index-buffer/render output, exact CFastVB/strip-candidate/span/triangle-record layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

> Last updated: 2026-05-26. The current source checkout used for Wave609/Wave610/Wave650/Wave651/Wave652/Wave653/Wave885 does not include `DXMeshVB.cpp`, `DXMeshVB.h`, `FastVB.cpp`, or the matching `MeshRenderer.cpp` implementation body; this page uses retail Ghidra evidence from decompiles, instructions, xrefs, vtable slots, callsites, and saved comments/tags. The older initial table below covered only the three build/load rows.

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

This source file implements DirectX vertex buffer management for 3D mesh rendering. It handles both static geometry and skeletal (animated) meshes, creating and managing Direct3D vertex and index buffers.

The CDXMeshVB class appears to be part of the rendering subsystem, responsible for:
- Building vertex buffers from mesh data
- Creating index buffers for triangle strips
- Supporting both static and skeletal mesh rendering
- Loading/streaming vertex buffer data from files

## Wave1028 CDX Render-Resource Lifecycle Review

Wave1028 static re-audit (`cdx-render-resource-lifecycle-review-wave1028`) re-read `0x0054bff0 CDXMeshVB__scalar_deleting_dtor` and `0x0054c010 CDXMeshVB__dtor_base` with no mutation. Fresh exports kept the Wave609 destructor pair coherent: vtable `0x005e50fc` slot 0 resolves to the scalar-deleting wrapper, slot 4 resolves to `0x0054d3f0 CDXMeshVB__ReleaseResources`, and the destructor body still calls the release helper before name/render-object/device-object teardown. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-021726_post_wave1028_cdx_render_resource_lifecycle_review_verified`. Runtime D3D/render-resource lifetime behavior, exact class layout, source-body identity, BEA patching, and rebuild parity remain separate proof.

## Wave849 D3D State/Cache Core Read-Back

Wave849 D3D state/cache core (`d3d-state-cache-core-wave849`, `wave849-readback-verified`) documented the Direct3D device wrapper rows used by `CDXMeshVB__Load`, `CDXMeshVB__BuildStaticVB`, `CDXMeshVB__BuildSkeletalVB`, and `CDXMeshVB__ReleaseResources`: `0x00513770 CEngine__DeviceCall68_CheckError`, `0x005137d0 CEngine__DeviceCall6C`, and `0x00513800 IUnknown__ReleaseIfNonNull_ReturnZero`. Probe token anchor: `Wave849 D3D state/cache core`; `0x00513770 CEngine__DeviceCall68_CheckError`; `0x005137d0 CEngine__DeviceCall6C`; `CDXMeshVB__BuildStaticVB`; `5691/6098 = 93.33%`; `0x00513a80 PlatformInput__GetKeyState3Core`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-073710_post_wave849_d3d_state_cache_core_verified`.

Static evidence proves the saved metadata/signature/comment/tags and the mesh/VB xrefs only. Exact Direct3D COM method identity, concrete buffer argument schema, runtime buffer creation/lifetime behavior, BEA patching, and rebuild parity remain deferred.

## Wave801 Frontend/Render Helper Read-Back

Wave801 static read-back (`frontend-render-helpers-wave801`, `wave801-readback-verified`) saved `0x0044a0c0 CDXMeshVB__GetGlobalZeroDouble` as `double __cdecl CDXMeshVB__GetGlobalZeroDouble(void)`. The body returns global double `DAT_00672fd0`, and post-readback xrefs cover HUD target overlay, mesh rendering, texture animation, AYA/resource cache, and render queue paths. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-073450_post_wave801_frontend_render_helpers_verified`.

This is static retail Ghidra metadata only. Exact source-body identity, concrete render layout, runtime rendering behavior, BEA patching, and rebuild parity remain deferred.

## Wave609 Saved Rows

Wave609 hardened the current CDXMeshVB head without claiming source-body identity or runtime rendering proof.

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x0054bf80` | `CDXMeshVB__ctor` | `void * __thiscall CDXMeshVB__ctor(void * this)` | Constructor installs vtable `0x005e50fc`, clears fields at `+0x108/+0x10c/+0x110/+0x120/+0x124`, and zeroes 64 group-pointer slots from `+0x8`. |
| `0x0054bff0` | `CDXMeshVB__scalar_deleting_dtor` | `void * __thiscall CDXMeshVB__scalar_deleting_dtor(void * this, byte flags)` | Vtable slot `0`, `RET 0x4`, calls `CDXMeshVB__dtor_base`, and conditionally frees `this` when `flags&1`. |
| `0x0054c010` | `CDXMeshVB__dtor_base` | `void __thiscall CDXMeshVB__dtor_base(void * this)` | Destructor body calls `CDXMeshVB__ReleaseResources`, performs post-release cleanup, frees name pointer `+0x124`, and runs base device-object teardown. |
| `0x0054c0a0` | `CDXMeshVB__BuildStaticVB` | `int __thiscall CDXMeshVB__BuildStaticVB(void * this)` | Static builder groups faces by material/texture references, builds 0x24-byte static vertices, creates FVF `0x152` vertex buffers and per-group index buffers, and stores `+0x114/+0x118/+0x11c` as `0x24/0x152/4`. |
| `0x0054c920` | `CDXMeshVB__BuildSkeletalVB` | `int __thiscall CDXMeshVB__BuildSkeletalVB(void * this)` | Skeletal builder emits `Building skeletal VB`, builds 0x30-byte skeletal vertices, uses `DAT_00854e6c` as the hardware-support gate, and stores `+0x114/+0x118/+0x11c` as `0x30/0/4`. |
| `0x0054d3f0` | `CDXMeshVB__ReleaseResources` | `int __thiscall CDXMeshVB__ReleaseResources(void * this)` | Vtable slot `4`; releases shared first-group VB, clears per-group index/group records, resets group count `+0x108`, and clears/decrements vertex-shader reference `+0x110`. |
| `0x0054e160` | `CDXMeshVB__Load` | `void __thiscall CDXMeshVB__Load(void * this, void * reader, int use_hardware_shader)` | `RET 0x8` and `CMeshPart__LoadFromStream` xref prove two stack args; reads the 0x128-byte serialized header and gates hardware-shader VB creation on `DAT_00854e6c && use_hardware_shader`. |

Read-back evidence: dry/apply/final dry reported `updated=0 skipped=7 renamed=0 would_rename=4 missing=0 bad=0`, then `updated=7 skipped=0 renamed=4 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `7` metadata rows, `7` tag rows, `9` xref rows, `791` instruction rows, `7` decompile rows, and `16` vtable-slot rows. Queue after Wave609 is `6093` total, `3124` commented, `2969` commentless, `1301` exact-undefined signatures, `1060` `param_N`, comment-backed proxy `3124/6093 = 51.27%`, strict clean-signature proxy `3079/6093 = 50.53%`, and next head `0x0054d530 CMeshRenderer__RenderMeshWithLayerPasses`.

## Wave610 Renderer Layer-Pass Row

Wave610 hardened the deferred renderer pass row without claiming exact source identity or runtime rendering proof.

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x0054d530` | `CMeshRenderer__RenderMeshWithLayerPasses` | `void __thiscall CMeshRenderer__RenderMeshWithLayerPasses(void * this, void * frame_provider, uint render_flags, void * unused_render_context, void * unused_transform_payload)` | `RET 0x10` and callsites `0x0054a4b6`/`0x0054b265` prove four stack args after ECX; receiver comes from the caller's `+0x138` field and uses CDXMeshVB-style fields `+0x108/+0x10c/+0x110/+0x114/+0x118/+0x11c`; `render_flags` consumes bits `0x10/0x20/0x40`; trailing payloads are retained for ABI accuracy but not consumed by the current decompile. |

Read-back evidence: dry/apply/final dry reported `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=1 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `1` metadata row, `1` tag row, `2` xref rows, `2201` instruction rows, `763` target-function instruction rows, `1` decompile row, and `114` callsite instruction rows. Queue after Wave610 is `6093` total, `3125` commented, `2968` commentless, `1301` exact-undefined signatures, `1059` `param_N`, comment-backed proxy `3125/6093 = 51.29%`, strict clean-signature proxy `3080/6093 = 50.55%`, and next head `0x0054e500 DXPalletizer__InsertColor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-224655_post_wave610_meshrenderer_layer_passes_verified`.

## Wave650 Strip Batch / CFastVB Rows

Wave650 CDXMeshVB/CFastVB strip hardening saved the adjacent CDXMeshVB strip setup and CFastVB word-span/adjacency rows without claiming source-body identity, exact layout identity, runtime strip quality, or concrete D3D output.

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x0056eb50` | `CDXMeshVB__SetTriangleStripDebugFlag` | `void __cdecl CDXMeshVB__SetTriangleStripDebugFlag(int enabled)` | Stores the low byte of `enabled` into `DAT_009d0c40`; xrefs from landscape/static/skeletal mesh builders set it before strip-batch construction. |
| `0x0056eb60` | `CDXMeshVB__SetEmitDegenerateFlag` | `void __cdecl CDXMeshVB__SetEmitDegenerateFlag(int enabled)` | Stores `enabled` into `DAT_00656e5c`, part of the shared strip setup global state. |
| `0x0056eb70` | `CDXMeshVB__SetWordIndexModeFlag` | `void __cdecl CDXMeshVB__SetWordIndexModeFlag(int enabled)` | Stores the low byte of `enabled` into `DAT_00656e60`, read by the strip emitter when choosing packed-vs-split output. |
| `0x0056eb80` | `CDXMeshVB__SetBatchSplitThreshold` | `void __cdecl CDXMeshVB__SetBatchSplitThreshold(int threshold)` | Stores `threshold` into `DAT_009d0c3c`, adjacent to the other strip setup flags. |
| `0x0056eb90` | `CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer` | `void __cdecl CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer(void * index_words, uint index_word_count, void * out_batch_records, void * out_batch_count)` | Normalizes/grows word-index spans, runs the CFastVB strip pipeline, emits normal or debug/alternate triangle output, allocates 0x0c-byte batch records, and writes the output pointer/count fields. |
| `0x0056f260` | `CFastVB__ReleaseBufferAndResetTriplet_0056f260` | `void __fastcall CFastVB__ReleaseBufferAndResetTriplet_0056f260(void * span)` | Frees `span+0x4` and clears the begin/end/capacity triplet; xrefs include strip cleanup and unwind contexts. |
| `0x0056f280` | `CFastVB__CountWordElements` | `int __fastcall CFastVB__CountWordElements(void * span)` | Counts 16-bit words as `(end - begin) >> 1`, returning zero for an empty begin pointer. |
| `0x0056f2a0` | `CFastVB__InsertWordSpanFilled` | `void __thiscall CFastVB__InsertWordSpanFilled(void * this, void * insert_word_ptr, uint word_count, void * fill_word_ptr, void * edi_context)` | Grows/shifts a 16-bit span and inserts repeated fill-word values, reallocating through OID helpers when capacity is insufficient. |
| `0x0056f4b0` | `CFastVB__CopyWordRangeToBufferAndAdvanceEnd` | `void __thiscall CFastVB__CopyWordRangeToBufferAndAdvanceEnd(void * this, void * write_ptr, void * src_begin, void * edi_context)` | Copies 16-bit words from `src_begin` to the current span end and advances the span end pointer. |
| `0x0056f500` | `CFastVB__InitWordSpanHeader` | `void __fastcall CFastVB__InitWordSpanHeader(void * span)` | Seeds the observed header byte and clears the begin/end/capacity triplet. |
| `0x0056f520` | `CFastVB__ReleaseBufferAndResetTriplet_0056f520` | `void __fastcall CFastVB__ReleaseBufferAndResetTriplet_0056f520(void * span)` | Equivalent duplicate release/reset helper kept address-suffixed because the retail binary has two routines with distinct call/unwind contexts. |
| `0x0056f540` | `CFastVB__FindEdgeRecord` | `void * __cdecl CFastVB__FindEdgeRecord(void * edge_buckets, int vertex_a, int vertex_b)` | Scans edge-record bucket chains for either vertex order and returns the matching edge record or null. |
| `0x0056f580` | `CFastVB__ResolveOppositeAdjacencyRecord` | `void * __cdecl CFastVB__ResolveOppositeAdjacencyRecord(void * edge_buckets, int vertex_a, int vertex_b, void * current_triangle)` | Resolves an edge and returns the opposite triangle pointer from the record's triangle pair. |
| `0x0056f5c0` | `CFastVB__ContainsTriangleTriplet` | `uint __stdcall CFastVB__ContainsTriangleTriplet(void * triangle, void * triangle_span)` | Walks a triangle-record pointer span and returns a low-byte true value when the first three dwords match. |
| `0x0056f620` | `CFastVB__BuildTriangleAdjacency` | `void __thiscall CFastVB__BuildTriangleAdjacency(void * this, void * triangle_record_span, void * edge_buckets, int max_vertex_index, uint mode_flags)` | Builds 0x18-byte triangle records and 0x1c-byte edge records from a 16-bit index span, links opposite triangles, and emits duplicate/non-manifold diagnostics. |

Read-back evidence: dry/apply/final dry reported `updated=0 skipped=15 renamed=0 would_rename=0 signature_updated=15 missing=0 bad=0`, then `updated=15 skipped=0 renamed=0 would_rename=0 signature_updated=15 missing=0 bad=0`, then `updated=0 skipped=15 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `15` metadata rows, `15` tag rows, `86` xref rows, `1335` instruction rows, and `15` decompile rows. Queue after Wave650 is `6093` total, `3518` commented, `2575` commentless, `1217` exact-undefined signatures, `790` `param_N`, comment-backed proxy `3518/6093 = 57.74%`, strict clean-signature proxy `3468/6093 = 56.92%`, and next head `0x0056fce0 CFastVB__SelectTriangleWithMaxOpenEdges`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-215037_post_wave650_cdxmeshvb_cfastvb_strip_verified`.

## Wave651 Strip Selection / Candidate Rows

Wave651 CFastVB strip-selection hardening saved the next adjacent CFastVB strip-selection and candidate-link rows without claiming source-body identity, exact layout identity, runtime strip quality, or concrete D3D output.

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x0056fce0` | `CFastVB__SelectTriangleWithMaxOpenEdges` | `uint __stdcall CFastVB__SelectTriangleWithMaxOpenEdges(void * triangle_record_span, void * edge_buckets)` | Counts unresolved/open edges for each triangle record and returns the best candidate index, or `0xffffffff` when none has open edges. |
| `0x0056fdc0` | `CFastVB__SelectNextStripTriangle` | `void * __thiscall CFastVB__SelectNextStripTriangle(void * this, void * triangle_record_span, void * edge_buckets, void * edi_context)` | Selects an unclaimed triangle record, optionally starts from the open-edge selector, advances the receiver's floating selector field, and returns a triangle pointer or null. |
| `0x0056fe70` | `CFastVB__AreTriangleVertexSetsEquivalent` | `int __cdecl CFastVB__AreTriangleVertexSetsEquivalent(void * triangle_a, void * triangle_b)` | Checks whether all three vertices from one triangle appear in the other; callers use the result as a match/rotation cue. |
| `0x0056fec0` | `CFastVB__GetSharedVerticesBetweenTriangles` | `void __cdecl CFastVB__GetSharedVerticesBetweenTriangles(void * triangle_a, void * triangle_b, void * out_shared_a, void * out_shared_b)` | Initializes both output slots to `0xffffffff` and writes the first and second shared vertices between two triangle records. |
| `0x0056ff40` | `CFastVB__TriangleListContainsVertexTriplet_0056ff40` | `uint __stdcall CFastVB__TriangleListContainsVertexTriplet_0056ff40(void * triangle_list_span, void * triangle)` | Walks a span of triangle-record pointers and tracks whether the candidate triangle's three vertex ids are already represented. |
| `0x00570000` | `CFastVB__BuildTriangleStripFromSeedRecord` | `void __thiscall CFastVB__BuildTriangleStripFromSeedRecord(void * this, void * edge_buckets, int generation_context)` | Starts from a seed/candidate record, grows forward and reverse 16-bit strip word spans, stamps selected triangle owner fields, and appends candidate batches. |
| `0x00570870` | `CFastVB__StampRecordOwnerFields` | `void __thiscall CFastVB__StampRecordOwnerFields(void * this, void * triangle_record, void * edi_context)` | Writes owner/group fields on a triangle record from `this+0x1c` and `this+0x20`, preserving the observed negative-owner and nonnegative-owner forms. |
| `0x005708a0` | `CFastVB__InsertStripCandidatesIntoBuffer_005708a0` | `void __thiscall CFastVB__InsertStripCandidatesIntoBuffer_005708a0(void * this, void * primary_candidate_span, void * secondary_candidate_span, void * edi_context)` | Inserts secondary strip candidates in reverse order, then grows/shifts the main pointer buffer while inserting primary candidates. |
| `0x00570a90` | `CFastVB__HasAdjacentFaceTouchingPivotVertex_00570a90` | `int __thiscall CFastVB__HasAdjacentFaceTouchingPivotVertex_00570a90(void * this, void * triangle_record, void * edge_buckets, void * edi_context)` | Probes all three edges of a triangle record and returns a low-byte true value when an adjacent face is already stamped with the current owner/group id. |
| `0x00570be0` | `CFastVB__InitializeCandidateParentLinks_00570be0` | `void __stdcall CFastVB__InitializeCandidateParentLinks_00570be0(void * out_candidate_span, void * selected_candidate_bucket)` | Walks the selected candidate bucket, resets root parent fields, appends roots to the output span, and stamps child triangle records from each root's child span. |

Read-back evidence: dry/apply/final dry reported `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0`, then `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0`, then `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `10` metadata rows, `10` tag rows, `15` xref rows, `250` instruction rows, and `10` decompile rows. Queue after Wave651 is `6093` total, `3528` commented, `2565` commentless, `1217` exact-undefined signatures, `780` `param_N`, comment-backed proxy `3528/6093 = 57.90%`, strict clean-signature proxy `3478/6093 = 57.08%`, and next head `0x00570cb0 CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-182101_post_wave651_cfastvb_strip_selection_verified`.

## Wave652 Strip Merge / Emission Rows

Wave652 CFastVB strip merge/emission hardening saved the next adjacent CFastVB candidate-selection, merge/order, duplicate-index, and dword emission rows without claiming source-body identity, exact layout identity, runtime strip quality, or concrete D3D index buffer behavior.

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x00570cb0` | `CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0` | `bool __stdcall CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0(void * triangle_record_span, void * edge_buckets, void * candidate_root, void * out_edge_pick)` | Walks an edge bucket chosen from candidate-root side state, checks adjacent owner/group stamps, and writes the selected triangle, edge record, and side flag to the output pick record. |
| `0x00570dd0` | `CFastVB__MergeAndOrderStripBatches_Impl_00570dd0` | `void __thiscall CFastVB__MergeAndOrderStripBatches_Impl_00570dd0(void * this, void * candidate_batch_span, void * overflow_batch_span, void * output_batch_span, void * edi_context)` | Internal merge/order helper that appends overflow/output batch spans, splits oversized candidates, scores with `CFastVB__CountTriangleVerticesInSet_00572490`, and emits reordered references. |
| `0x00571060` | `CFastVB__IsEven` | `bool __stdcall CFastVB__IsEven(uint value)` | Tiny parity helper used by the strip emitter to decide whether a bridge needs an extra index. |
| `0x00571080` | `CFastVB__IsDirectedEdgeInTriangle` | `bool __stdcall CFastVB__IsDirectedEdgeInTriangle(void * triangle, int edge_start, int edge_end)` | Checks whether a triangle's ordered vertex triplet contains the directed edge across first, second, or wraparound edge. |
| `0x005710d0` | `CFastVB__EmitTriangleStripIndexBuffer` | `void __stdcall CFastVB__EmitTriangleStripIndexBuffer(void * strip_batch_span, void * out_index_span, int emit_continuity_flag, void * out_separator_count)` | Emits dword strip indices, orients adjacent triangles with vertex-set/shared-edge helpers, inserts `0xffffffff` restart separators when continuity is disabled, and updates the separator count pointer. |
| `0x005715b0` | `CFastVB__BuildStripBatchesFromIndexBuffer` | `int CFastVB__BuildStripBatchesFromIndexBuffer(void)` | Wave885 re-read of the central strip-batch builder called only from `CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer`; observed ECX receiver context and `RET 0x18`, but locked/hidden parameter storage prevents a safe forced prototype. |
| `0x00571870` | `CFastVB__HasDuplicateTriangleIndices32` | `bool __cdecl CFastVB__HasDuplicateTriangleIndices32(void * triangle)` | Checks a 32-bit triangle triplet for duplicate vertex indices; xrefs include adjacency, emission, and merge/order paths. |
| `0x00571890` | `CFastVB__HasDuplicateTriangleIndices16` | `bool __stdcall CFastVB__HasDuplicateTriangleIndices16(int index_a, int index_b, int index_c)` | Compares the low 16-bit forms of three supplied indices and is used as an adjacency degenerate-triangle guard. |
| `0x005718c0` | `CFastVB__MergeAndOrderStripBatches` | `void __thiscall CFastVB__MergeAndOrderStripBatches(void * this, void * candidate_batch_span, void * ordered_batch_span, void * edge_buckets, void * output_batch_span, void * edi_context)` | Public merge/order helper that splits oversized strip batches, filters duplicate 32-bit triangle rows, delegates the internal merge pass, and chooses batch order using edge-resolution and vertex-cache scoring. |

Read-back evidence: dry/apply/final dry reported `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`, then `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `8` metadata rows, `8` tag rows, `16` xref rows, `200` instruction rows, and `8` decompile rows. Queue after Wave652 is `6093` total, `3536` commented, `2557` commentless, `1217` exact-undefined signatures, `772` `param_N`, comment-backed proxy `3536/6093 = 58.03%`, strict clean-signature proxy `3486/6093 = 57.21%`, and next head `0x005721f0 CFastVB__SeedVertexCacheFromTriangleRefs`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-185249_post_wave652_cfastvb_strip_merge_emission_verified`.

Wave885 returned to the gap between the Wave652 strip emitter and duplicate-index guards, saving comments/tags for `0x005715b0 CFastVB__BuildStripBatchesFromIndexBuffer` with the `cfastvb-strip-batch-builder-wave885` and `wave885-readback-verified` tags. Static evidence ties the row to the only xref at `0x0056ecaa` from `CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer`, 16-bit index-word span growth/copy, `CFastVB__BuildTriangleAdjacency`, `CFastVB__GenerateStripCandidatesFromAdjacency`, `CFastVB__MergeAndOrderStripBatches`, and cleanup of candidate, edge-bucket, overflow, and local span buffers. The current signature display remains `int CFastVB__BuildStripBatchesFromIndexBuffer(void)` because Ghidra still reports locked/hidden parameter storage even though instruction evidence shows an ECX receiver context and `RET 0x18`; Wave885 records that ABI evidence without forcing a prototype. Read-back evidence: dry/apply/final dry reported `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=1 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`. Post exports verified `1` metadata row, `1` tag row, `1` xref row, `239` instruction rows, `1` decompile row, `7` context metadata rows, and `7` context decompile rows. Queue after Wave885 is `6113` total, `5968` commented, `145` commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5968/6113 = 97.63%`, strict clean-signature proxy `5968/6113 = 97.63%`, and next raw commentless row `0x00573d80 CTexture__InsertNodeIntoTree`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-015531_post_wave885_cfastvb_strip_batch_builder_verified`. Exact CFastVB container/triangle/edge/candidate layouts, exact locked ABI, runtime strip quality, concrete D3D index-buffer behavior, BEA patching, and rebuild parity remain unproven.

## Wave653 Vertex Cache / Scoring Rows

Wave653 CFastVB vertex-cache/scoring hardening saved the next adjacent CFastVB vertex-cache, overlap-score, unresolved-edge score, and candidate-generation rows without claiming source-body identity, exact layout identity, runtime strip quality, or concrete D3D output.

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x005721f0` | `CFastVB__SeedVertexCacheFromTriangleRefs` | `void __stdcall CFastVB__SeedVertexCacheFromTriangleRefs(void * vertex_cache, void * strip_batch)` | Walks a strip-batch triangle-reference span and seeds the fixed vertex cache with each triangle's three vertex ids before overlap scoring. |
| `0x00572310` | `CFastVB__SeedVertexCacheFromTriangle` | `void __stdcall CFastVB__SeedVertexCacheFromTriangle(void * vertex_cache, void * triangle)` | Corrects the stale `CDXTexture__InsertUniqueTripletAtFront` owner label; the only current xref is the CFastVB merge/order implementation, and the body inserts one triangle's vertex ids into the cache front when absent. |
| `0x005723c0` | `CFastVB__ComputeAverageVertexOverlapScore_005723c0` | `double __stdcall CFastVB__ComputeAverageVertexOverlapScore_005723c0(void * vertex_cache, void * strip_batch)` | Counts cached vertices for each strip-batch triangle and returns an average overlap score used during batch ordering. |
| `0x00572490` | `CFastVB__CountTriangleVerticesInSet_00572490` | `int __stdcall CFastVB__CountTriangleVerticesInSet_00572490(void * vertex_cache, void * triangle)` | Counts how many of a triangle's three vertex ids are present in the current vertex cache; the internal merge helper uses it to pick a temporary-batch triangle. |
| `0x00572500` | `CFastVB__CountResolvedOppositeEdges` | `char __stdcall CFastVB__CountResolvedOppositeEdges(void * triangle, void * edge_buckets)` | Probes all three triangle edges with `CFastVB__ResolveOppositeAdjacencyRecord` and returns the resolved-opposite-edge count. |
| `0x00572570` | `CFastVB__ComputeAverageUnresolvedEdgesPerBatch` | `double __stdcall CFastVB__ComputeAverageUnresolvedEdgesPerBatch(void * candidate_bucket)` | Walks a candidate bucket, subtracts each child candidate's resolved count from its triangle-reference count, and returns the average unresolved-edge score. |
| `0x005725e0` | `CFastVB__GenerateStripCandidatesFromAdjacency` | `void __thiscall CFastVB__GenerateStripCandidatesFromAdjacency(void * this, void * out_candidate_span, void * triangle_record_span, void * edge_buckets, int seed_bucket_limit, void * edi_context)` | Allocates seed candidate buckets from triangle records and edge buckets, expands linked candidates, scores buckets with `CFastVB__ComputeAverageUnresolvedEdgesPerBatch`, and initializes parent links into the output span. |

Read-back evidence: dry/apply/final dry reported `updated=0 skipped=7 renamed=0 would_rename=1 signature_updated=7 missing=0 bad=0`, then `updated=7 skipped=0 renamed=1 would_rename=0 signature_updated=7 missing=0 bad=0`, then `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `7` metadata rows, `7` tag rows, `8` xref rows, `315` instruction rows, and `7` decompile rows. Queue after Wave653 is `6093` total, `3543` commented, `2550` commentless, `1217` exact-undefined signatures, `765` `param_N`, comment-backed proxy `3543/6093 = 58.15%`, strict clean-signature proxy `3491/6093 = 57.30%`, and next head `0x00572e40 CTexture__DestroyNodeTreeAndStorage`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-192250_post_wave653_cfastvb_vertex_cache_scoring_verified`.

## Functions

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `0x0054c0a0` | `CDXMeshVB__BuildStaticVB` | ~2176 bytes | Builds vertex/index buffers for static meshes |
| `0x0054c920` | `CDXMeshVB__BuildSkeletalVB` | ~2112 bytes | Builds vertex/index buffers for skeletal meshes |
| `0x0054e160` | `CDXMeshVB__Load` | ~600 bytes | Loads vertex buffer data from stream |
| `0x0054bf80` | `CDXMeshVB__ctor` | ~112 bytes | Constructor/lifecycle row saved in Wave609 |
| `0x0054bff0` | `CDXMeshVB__scalar_deleting_dtor` | ~32 bytes | Scalar deleting destructor wrapper saved in Wave609 |
| `0x0054c010` | `CDXMeshVB__dtor_base` | ~144 bytes | Destructor body saved in Wave609 |
| `0x0054d3f0` | `CDXMeshVB__ReleaseResources` | ~208 bytes | Vtable slot-4 resource-release helper saved in Wave609 |
| `0x0054d530` | `CMeshRenderer__RenderMeshWithLayerPasses` | ~2936 bytes | CDXMeshVB-style group/layer render helper saved in Wave610 |
| `0x0056eb50` | `CDXMeshVB__SetTriangleStripDebugFlag` | ~16 bytes | Strip setup global setter saved in Wave650 |
| `0x0056eb60` | `CDXMeshVB__SetEmitDegenerateFlag` | ~16 bytes | Strip setup global setter saved in Wave650 |
| `0x0056eb70` | `CDXMeshVB__SetWordIndexModeFlag` | ~16 bytes | Strip setup global setter saved in Wave650 |
| `0x0056eb80` | `CDXMeshVB__SetBatchSplitThreshold` | ~16 bytes | Strip setup threshold setter saved in Wave650 |
| `0x0056eb90` | `CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer` | ~2768 bytes | Strip-batch/index emission helper saved in Wave650 |
| `0x0056f260` | `CFastVB__ReleaseBufferAndResetTriplet_0056f260` | ~32 bytes | Span release/reset helper saved in Wave650 |
| `0x0056f280` | `CFastVB__CountWordElements` | ~32 bytes | 16-bit span count helper saved in Wave650 |
| `0x0056f2a0` | `CFastVB__InsertWordSpanFilled` | ~528 bytes | 16-bit span insert/grow helper saved in Wave650 |
| `0x0056f4b0` | `CFastVB__CopyWordRangeToBufferAndAdvanceEnd` | ~48 bytes | 16-bit span copy/advance helper saved in Wave650 |
| `0x0056f500` | `CFastVB__InitWordSpanHeader` | ~32 bytes | Span header initializer saved in Wave650 |
| `0x0056f520` | `CFastVB__ReleaseBufferAndResetTriplet_0056f520` | ~32 bytes | Duplicate span release/reset helper saved in Wave650 |
| `0x0056f540` | `CFastVB__FindEdgeRecord` | ~64 bytes | Edge-record lookup helper saved in Wave650 |
| `0x0056f580` | `CFastVB__ResolveOppositeAdjacencyRecord` | ~64 bytes | Opposite triangle resolver saved in Wave650 |
| `0x0056f5c0` | `CFastVB__ContainsTriangleTriplet` | ~96 bytes | Triangle-record span predicate saved in Wave650 |
| `0x0056f620` | `CFastVB__BuildTriangleAdjacency` | ~1728 bytes | Triangle/edge adjacency builder saved in Wave650 |
| `0x0056fce0` | `CFastVB__SelectTriangleWithMaxOpenEdges` | ~224 bytes | Open-edge triangle selector saved in Wave651 |
| `0x0056fdc0` | `CFastVB__SelectNextStripTriangle` | ~176 bytes | Next unclaimed strip triangle selector saved in Wave651 |
| `0x0056fe70` | `CFastVB__AreTriangleVertexSetsEquivalent` | ~80 bytes | Triangle vertex-set comparison helper saved in Wave651 |
| `0x0056fec0` | `CFastVB__GetSharedVerticesBetweenTriangles` | ~128 bytes | Shared-vertex extraction helper saved in Wave651 |
| `0x0056ff40` | `CFastVB__TriangleListContainsVertexTriplet_0056ff40` | ~192 bytes | Triangle-list membership predicate saved in Wave651 |
| `0x00570000` | `CFastVB__BuildTriangleStripFromSeedRecord` | ~2160 bytes | Seed-record strip builder saved in Wave651 |
| `0x00570870` | `CFastVB__StampRecordOwnerFields` | ~48 bytes | Triangle owner/group stamping helper saved in Wave651 |
| `0x005708a0` | `CFastVB__InsertStripCandidatesIntoBuffer_005708a0` | ~496 bytes | Strip-candidate buffer insertion helper saved in Wave651 |
| `0x00570a90` | `CFastVB__HasAdjacentFaceTouchingPivotVertex_00570a90` | ~336 bytes | Adjacent-face owner predicate saved in Wave651 |
| `0x00570be0` | `CFastVB__InitializeCandidateParentLinks_00570be0` | ~208 bytes | Candidate parent-link initializer saved in Wave651 |
| `0x00570cb0` | `CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0` | ~288 bytes | Edge-chain candidate selector saved in Wave652 |
| `0x00570dd0` | `CFastVB__MergeAndOrderStripBatches_Impl_00570dd0` | ~656 bytes | Internal strip-batch merge/order helper saved in Wave652 |
| `0x00571060` | `CFastVB__IsEven` | ~32 bytes | Parity helper saved in Wave652 |
| `0x00571080` | `CFastVB__IsDirectedEdgeInTriangle` | ~80 bytes | Directed-edge triangle predicate saved in Wave652 |
| `0x005710d0` | `CFastVB__EmitTriangleStripIndexBuffer` | ~1248 bytes | Dword strip-index emission helper saved in Wave652 |
| `0x005715b0` | `CFastVB__BuildStripBatchesFromIndexBuffer` | ~704 bytes | Central strip-batch builder re-read in Wave885 |
| `0x00571870` | `CFastVB__HasDuplicateTriangleIndices32` | ~32 bytes | 32-bit duplicate-index guard saved in Wave652 |
| `0x00571890` | `CFastVB__HasDuplicateTriangleIndices16` | ~48 bytes | 16-bit duplicate-index guard saved in Wave652 |
| `0x005718c0` | `CFastVB__MergeAndOrderStripBatches` | ~2400 bytes | Public strip-batch merge/order helper saved in Wave652 |
| `0x005721f0` | `CFastVB__SeedVertexCacheFromTriangleRefs` | ~288 bytes | Strip-batch vertex-cache seed helper saved in Wave653 |
| `0x00572310` | `CFastVB__SeedVertexCacheFromTriangle` | ~176 bytes | Single-triangle vertex-cache seed helper saved in Wave653 |
| `0x005723c0` | `CFastVB__ComputeAverageVertexOverlapScore_005723c0` | ~208 bytes | Average vertex-overlap score helper saved in Wave653 |
| `0x00572490` | `CFastVB__CountTriangleVerticesInSet_00572490` | ~112 bytes | Triangle-in-cache scoring helper saved in Wave653 |
| `0x00572500` | `CFastVB__CountResolvedOppositeEdges` | ~112 bytes | Resolved opposite-edge count helper saved in Wave653 |
| `0x00572570` | `CFastVB__ComputeAverageUnresolvedEdgesPerBatch` | ~112 bytes | Average unresolved-edge score helper saved in Wave653 |
| `0x005725e0` | `CFastVB__GenerateStripCandidatesFromAdjacency` | ~2144 bytes | Candidate-bucket generator saved in Wave653 |

## Function Details

### CDXMeshVB__BuildStaticVB (0x0054c0a0)

**Purpose:** Builds DirectX vertex and index buffers for static (non-animated) mesh geometry.

**Key Characteristics:**
- Uses `thiscall` convention (ECX = this pointer)
- Allocates vertex buffer of size `numVerts * 0x24` (36 bytes per vertex)
- Allocates index buffer data of size `numVerts * 0x300` (768 bytes per vertex for indices)
- Creates up to 64 material/texture groups
- Each vertex contains: position (12 bytes), normal (12 bytes), UV (8 bytes), color (4 bytes)
- Returns HRESULT-style value: `S_OK` on success, `E_FAIL` on failure

**Vertex Format (0x24 = 36 bytes):**
```
Offset 0x00: float3 position (12 bytes)
Offset 0x0C: float3 normal (12 bytes)
Offset 0x18: float2 texcoord (8 bytes)
Offset 0x20: DWORD color (4 bytes)
```

**Memory Allocations (via OID__AllocObject):**
- Line 0x51: Vertex data buffer (`numVerts * 0x24`)
- Line 0x52: Index data buffer (`numVerts * 0x300`)
- Line 0x84: Material group structure (0x3C = 60 bytes each)
- Line 0xBA: Triangle index arrays (`numFaces * 6` bytes)

**DirectX Calls:**
- `FUN_00513770` - Creates D3D vertex buffer (FVF 0x152 = position|normal|tex1)
- `FUN_005137d0` - Creates D3D index buffer (format 0x65 = 16-bit indices)
- Uses vtable calls at offset 0x2C (Lock) and 0x30 (Unlock)

**Final State:**
- Sets `this+0x114 = 0x24` (vertex stride)
- Sets `this+0x118 = 0x152` (FVF flags)
- Sets `this+0x11C = 4` (primitive type - triangle list)

---

### CDXMeshVB__BuildSkeletalVB (0x0054c920)

**Purpose:** Builds DirectX vertex and index buffers for skeletal (bone-animated) mesh geometry.

**Key Characteristics:**
- Uses `thiscall` convention (ECX = this pointer)
- Debug message: "Building skeletal VB" at 0x00651290
- Allocates larger vertex buffer: `numVerts * 0xC00` (3072 bytes per vertex batch)
- Vertex stride is 0x30 (48 bytes) vs 0x24 for static meshes
- Includes bone weight data multiplied by 3.0 for blending
- Checks `DAT_00854e6c` flag for hardware vs software vertex processing

**Skeletal Vertex Format (0x30 = 48 bytes):**
```
Offset 0x00: float3 position (12 bytes)
Offset 0x0C: float3 blendWeights (12 bytes) - bone weights * 3.0
Offset 0x18: float3 normal (12 bytes)
Offset 0x24: float2 texcoord (8 bytes)
Offset 0x2C: DWORD color (4 bytes)
```

**Memory Allocations (via OID__AllocObject):**
- Line 0x1A9: Vertex data buffer (`numVerts * 0xC00`)
- Line 0x1AA: Index data buffer (`numVerts * 0x180`)
- Line 0x1AB: Weight data buffer (`numVerts * 2`)
- Line 0x1D8: Material group structure (0x3C bytes)
- Line 0x216: Triangle index arrays

**Bone Weight Processing:**
```c
// Converts integer bone weights to floats with 3.0 multiplier
for (int i = 0; i < 3; i++) {
    weights[i] = (float)intWeights[i] * 3.0f;
}
```

**Hardware Detection:**
- If `DAT_00854e6c != 0`: Uses hardware vertex shaders (flag 0x18, type 2)
- Otherwise: Uses software processing (flag 0x8, type 1)

**Final State:**
- Sets `this+0x114 = 0x30` (vertex stride)
- Sets `this+0x118 = 0` (custom FVF/shader)
- Sets `this+0x11C = 4` (primitive type)

---

### CDXMeshVB__Load (0x0054e160)

**Purpose:** Loads/deserializes vertex buffer data from a file stream.

**Parameters:**
- `param_1` (int): Source data pointer/stream
- `param_2` (int): Boolean flag for hardware shader support

**Key Operations:**
1. Saves and restores class state during load
2. Frees existing vertex buffer resources (up to 64 groups)
3. Reads mesh name string from stream (offset +0x2C in source)
4. Allocates and copies name to `this+0x124` (member 0x49)
5. Iterates through material groups (up to `this+0x108` count)
6. Reads per-group data: buffer sizes, vertex counts, etc.
7. Creates D3D vertex and index buffers
8. Reads texture/material references (indices 0x20-0x38)

**Memory Allocations (via OID__AllocObject):**
- Line 0x6CE: Mesh name string (strlen + 1)
- Line 0x6DC: Material group structure (0x3C bytes)

**Stream Reading (via FUN_00423960):**
- Reads vertex buffer size at offset +0x08
- Reads index buffer size at offset +0x0C
- Reads vertex count at offset +0x10
- Reads primitive count at offset +0x14
- Reads triangle count at offset +0x18
- Reads flags at offset +0x1C
- Reads 6 texture indices at offsets 0x20-0x34

**Hardware Detection:**
- Same as BuildSkeletalVB: checks `DAT_00854e6c` and `param_2`

---

## Class Structure (CDXMeshVB)

Based on decompilation analysis:

```cpp
class CDXMeshVB {
    /* 0x000 */ IDirect3DVertexBuffer* m_pVB;      // Vertex buffer pointer
    /* 0x004 */ IDirect3DIndexBuffer* m_pIB;       // Index buffer pointer
    /* 0x008 */ CMaterialGroup* m_pGroups[64];     // Material groups (0x40 entries)
    /* 0x108 */ int m_nGroupCount;                 // Number of active groups
    /* 0x10C */ CMesh* m_pSourceMesh;              // Source mesh data
    /* 0x110 */ int m_unknown110;
    /* 0x114 */ int m_nVertexStride;               // Bytes per vertex (0x24 or 0x30)
    /* 0x118 */ DWORD m_dwFVF;                     // Flexible vertex format flags
    /* 0x11C */ int m_nPrimitiveType;              // D3D primitive type
    /* 0x120 */ int m_unknown120;
    /* 0x124 */ char* m_szMeshName;                // Mesh name string
};
```

## Related Systems

- **OID__AllocObject**: Memory allocation with debug tracking (file/line)
- **FUN_00513770**: D3D vertex buffer creation wrapper
- **FUN_005137d0**: D3D index buffer creation wrapper
- **FUN_0056eb60/70/80/50**: Render state setup functions
- **FUN_0056eb90**: Triangle strip optimizer
- **CLandscapeTexture__FreeTexture**: Texture cleanup callback
- **DAT_00854e6c**: Hardware vertex shader capability flag
- **DAT_009c3df0**: D3D device critical section/lock

## Technical Notes

1. **FVF 0x152 Breakdown:**
   - `D3DFVF_XYZ` (0x002) - Position
   - `D3DFVF_NORMAL` (0x010) - Normal vector
   - `D3DFVF_TEX1` (0x100) - One texture coordinate set
   - `D3DFVF_DIFFUSE` (0x040) - Diffuse color

2. **Index Format 0x65:**
   - 16-bit indices (D3DFMT_INDEX16)
   - Used for triangle lists/strips

3. **Memory Pool:**
   - Allocation type 0x3A likely corresponds to D3DPOOL_MANAGED

4. **Error Handling:**
   - Returns `(success ? 0 : 0x80004005)` - S_OK or E_FAIL

## Cross-References

Functions called by DXMeshVB:
- `OID__AllocObject` - Memory allocation
- `OID__FreeObject` - Memory deallocation
- `FUN_00513770` - VB creation
- `FUN_005137d0` - IB creation
- `DebugTrace` - Debug trace output (ret stub in retail build; was `FUN_0040c640`)
- `CConsole__Status` - Begin status/logging section ("Building skeletal VB")
- `CConsole__StatusDone` - End status/logging section
- `FUN_0056eb90` - Strip optimization

## Version History

| Date | Change |
|------|--------|
| 2026-05-26 | Wave885 saved CFastVB strip-batch builder comments/tags for `0x005715b0 CFastVB__BuildStripBatchesFromIndexBuffer`, preserved the locked-ABI signature display, and advanced the raw queue head to `0x00573d80 CTexture__InsertNodeIntoTree`. |
| 2026-05-20 | Wave653 saved seven CFastVB vertex-cache/scoring signatures/comments/tags, corrected stale `CDXTexture__InsertUniqueTripletAtFront` ownership to `CFastVB__SeedVertexCacheFromTriangle`, and advanced the queue head to `0x00572e40 CTexture__DestroyNodeTreeAndStorage`. |
| 2026-05-20 | Wave652 saved eight CFastVB strip merge/emission signatures/comments/tags and advanced the queue head to `0x005721f0 CFastVB__SeedVertexCacheFromTriangleRefs`. |
| 2026-05-20 | Wave651 saved ten CFastVB strip-selection/candidate signatures/comments/tags, verified read-back, and advanced the queue head to `0x00570cb0 CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0`. |
| 2026-05-20 | Wave610 saved `CMeshRenderer__RenderMeshWithLayerPasses` with a `RET 0x10` four-stack-argument signature, callsite evidence, CDXMeshVB-style receiver layout notes, and queue head `0x0054e500 DXPalletizer__InsertColor`. |
| 2026-05-20 | Wave609 saved seven CDXMeshVB lifecycle/build/load signatures/comments/tags, verified vtable slots 0 and 4, and deferred `0x0054d530 CMeshRenderer__RenderMeshWithLayerPasses` to a callsite-focused wave. |
| 2025-12-16 | Initial documentation - 3 functions identified and named |
