# Ghidra Wave983 CChunkReader Resource Review (2026-05-31)

Status: saved Ghidra comment/tag/signature verification
Date: 2026-05-31
Branch: `main`
Tag: `cchunkreader-resource-review-wave983`

## Scope

Wave983 re-reviewed the source-backed `CChunkReader` tagged-resource cursor helpers from `chunker.cpp`:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x004237d0` | `CChunkReader__ctor` | Comment/tag hardening; signature verified |
| `0x00423840` | `CChunkReader__dtor_base` | Comment/tag hardening; signature verified |
| `0x00423870` | `CChunkReader__OpenExistingBuffer` | Comment/tag hardening; signature verified |
| `0x004238c0` | `CChunkReader__OpenFile` | Comment/tag hardening; signature verified |
| `0x00423900` | `CChunkReader__Close` | Comment/tag hardening; signature verified |
| `0x00423910` | `CChunkReader__GetNext` | Comment/tag hardening; signature verified |
| `0x00423960` | `CChunkReader__Read` | Comment/tag hardening; signature verified |
| `0x00423990` | `CChunkReader__Skip` | Comment/tag hardening; signature verified |

The pass made no renames, no function-boundary changes, no executable-byte changes, and did not launch BEA.

## Evidence

Fresh read-back artifacts are under the ignored private evidence root:

```text
subagents/ghidra-static-reaudit/wave983-cchunkreader-resource-review/
```

Dry/apply/final-dry:

```text
dry: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=8 missing=0 bad=0
apply: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=8 missing=0 bad=0
final dry: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0
```

Read-back result:

```text
metadata: 8/8 OK
tags: 8/8 OK
xrefs: 299 rows
instructions: 153 rows
decompile: 8/8 OK
queue: 6222/6222, 0 commentless, 0 undefined signatures, 0 param_N
```

Normalized progress tokens:

```text
static closure: 6222/6222 = 100.00%
Wave911 focused re-audit progress: 384/1408 = 27.27%
expanded static surface progress: 443/1478 = 29.97%
```

Representative static xrefs tie the helpers to `CResourceAccumulator__ReadResourceFile`, `CMesh__Deserialize`, `CCutscene__Load`, `CMapTex__Deserialize`, `CMeshPart__LoadFromStream`, and texture/mesh/resource deserializers.

## Review Result

Wave983 confirms the saved `CChunkReader` names from Wave319 as the active labels and normalizes stale documentation that still used `CChunkerStream__...`, `FUN_00423910`, `FUN_00423960`, or `memcpy_wrapper` wording. These helpers are the shared read-side tagged-chunk cursor:

- `GetNext` reads the 4-byte chunk id and 4-byte chunk size.
- `Read` forwards payload reads through `CDXMemBuffer__Read` and advances `ReadSinceChunk`.
- `Skip` advances to the end of the current chunk through `CDXMemBuffer__Skip`.
- `Close` normalizes the backing buffer close status to `0` or `-1`.

## Backup

Verified post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260531-001624_post_wave983_cchunkreader_resource_review_verified
files=19
bytes=173837191
MissingCount=0
ExtraCount=0
DiffCount=0
HashDiffCount=0
```

## Wave900+ Gate

The operator requested a full recheck of Wave900+ work before proceeding hard beyond the current WIP. Wave983 was already applied in the live Ghidra project, so this closeout records the saved state. The next RE slice is a dedicated Wave900+ recheck gate before any new Wave911 candidate cluster.

## Truth Boundary

This review proves saved static Ghidra comment/tag/signature evidence for the CChunkReader cursor helpers only. It does not prove exact `CChunkReader` structure layout, runtime archive/resource I/O behavior, exact archive schema coverage, BEA patch behavior, or rebuild parity.
