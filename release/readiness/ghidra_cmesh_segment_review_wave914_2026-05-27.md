# Ghidra Wave914 CMesh segment review (2026-05-27)

Status: read-only static review
Date: 2026-05-27
Branch: `main`
Tag: `cmesh-segment-review-wave914`

## Scope

Wave914 reviewed a CMesh segment/name tranche from the Wave911 focused correction queue.

Reviewed targets:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x004aa4e0` | `CMesh__SumChainedField1C` | Reviewed; no mutation |
| `0x004aa500` | `CMesh__GetChainedRecordNameAndIdByIndex` | Reviewed; no mutation |
| `0x004aa6b0` | `CMesh__GetNameOrUnknown` | Reviewed; no mutation |
| `0x004aa8a0` | `CMesh__FindPartByNameI` | Reviewed; no mutation |
| `0x004aa680` | `CMesh__FindEntryByPartId` | Reviewed; no mutation |
| `0x004aa820` | `CMesh__FindPartField40ByNameAndOwner` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave914-cmesh-segment-review/metadata.tsv
subagents/ghidra-static-reaudit/wave914-cmesh-segment-review/tags.tsv
subagents/ghidra-static-reaudit/wave914-cmesh-segment-review/instructions.tsv
subagents/ghidra-static-reaudit/wave914-cmesh-segment-review/decompile/
```

Read-back result:

```text
metadata: 6/6 OK
tags: 6/6 OK
instructions: 184 rows
decompile: 6/6 OK
```

## Review Result

The saved CMesh helper names remain appropriate for the current evidence. Stuart source in this repo references global mesh usage through `engine.cpp`, `ResourceAccumulator.cpp`, and Goodies helpers, but the specific `CMesh` implementation source is not present. No exact source-identity correction was available, so no Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
G:\GhidraBackups\BEA_20260527-103159_post_wave914_cmesh_segment_review_verified
files=19
bytes=173247367
```

## Truth boundary

This review confirms static Ghidra coherence for selected CMesh helper names. It does not prove concrete CMesh/CMeshPart layouts, runtime mesh/destructible behavior, BEA patch behavior, or rebuild parity.

## Next

Continue Wave915 with another focused candidate cluster. Candidate options include Carver/targeting helpers (`0x00422db0`, `0x00423510`) or high-level collision detector helpers (`0x00480a30` and neighbors).
