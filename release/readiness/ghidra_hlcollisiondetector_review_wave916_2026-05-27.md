# Ghidra Wave916 high-level collision detector review (2026-05-27)

Status: read-only static review
Date: 2026-05-27
Branch: `main`
Tag: `hlcollisiondetector-review-wave916`

## Scope

Wave916 reviewed high-level collision detector helpers from the Wave911 focused correction queue:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00480a30` | `CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions` | Reviewed; no mutation |
| `0x00480c90` | `CHLCollisionDetector__HandleCollisionEnter` | Reviewed; no mutation |
| `0x00480db0` | `CHLCollisionDetector__HandleCollisionExit` | Reviewed; no mutation |
| `0x00480e10` | `CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions` | Reviewed; no mutation |
| `0x00480ed0` | `CHLCollisionDetector__DispatchCollisionEventForPair` | Reviewed; no mutation |
| `0x00481060` | `CHLCollisionDetector__ProcessMapWhoCollisionSweep` | Reviewed; no mutation |
| `0x004812d0` | `CHLCollisionDetector__HandleScheduledCollisionEvent` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave916-hlcollisiondetector-review/metadata.tsv
subagents/ghidra-static-reaudit/wave916-hlcollisiondetector-review/tags.tsv
subagents/ghidra-static-reaudit/wave916-hlcollisiondetector-review/instructions.tsv
subagents/ghidra-static-reaudit/wave916-hlcollisiondetector-review/decompile/
```

Read-back result:

```text
metadata: 7/7 OK
tags: 7/7 OK
instructions: 752 rows
decompile: 7/7 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current static evidence. Stuart source references `HLCollisionDetector.h` but the implementation body is not present in the tracked source snapshot, so no source-backed rename or exact-layout correction was available.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260527-113943_post_wave916_hlcollisiondetector_review_verified
files=19
bytes=173247367
```

## Truth boundary

This review confirms static Ghidra coherence for selected high-level collision detector helpers. It does not prove runtime collision behavior, concrete detector/component/event layouts, BEA patch behavior, or rebuild parity.

## Next

Continue Wave917 with a different focused cluster, preferably physics statement loaders or another group with stronger source/file-format evidence.
