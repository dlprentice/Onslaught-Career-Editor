# Ghidra FearGrid Weight Wave826 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `feargrid-weight-wave826`

Wave826 FearGrid weight saved a bounded name/comment/tag correction for `0x004daff0`, changing the caller-biased `CFearGrid__LookupFearWeightByArchetype` label to `FearGridTrackedObject__LookupFearWeightByArchetype`. The pass made no function-boundary changes and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004daff0 FearGridTrackedObject__LookupFearWeightByArchetype` | `CFearGrid__RebuildOccupancyAndScheduleTick` calls this at `0x0044c4af` after loading `ECX` from the tracked object in `ESI`, not from the grid object. |
| `0x0044c440 CFearGrid__RebuildOccupancyAndScheduleTick` | Filters tracked objects by `object+0x11c == grid+0x8008`, calls the helper, scales the returned x87 value by `_DAT_005d8c4c`, and marks the occupancy plane at `grid+0x08`. |
| `DAT_008553f8` | The helper scans this global list by inline string compare against entry names at `entry+0x30`. |
| `entry+0x34` | The helper returns the matched float at this offset, or `_DAT_005d856c` when no name/list match exists. |

Read-back evidence:

- `ApplyFearGridWeightWave826.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyFearGridWeightWave826.java apply`: `updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyFearGridWeightWave826.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 301 target instruction rows, 1 target decompile row, 5 context metadata rows, 1205 context instruction rows, and 5 context decompile rows.
- Queue after Wave826: 6098 total, 5634 commented, 464 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5634/6098 = 92.39%`, strict clean-signature proxy `5634/6098 = 92.39%`.
- Next raw commentless row: `0x004df520 CActor__dtor_base`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-200047_post_wave826_feargrid_weight_verified`, 19 files, 171576199 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra row at `0x004daff0` exists as `FearGridTrackedObject__LookupFearWeightByArchetype`.
- The saved signature is `double __thiscall FearGridTrackedObject__LookupFearWeightByArchetype(void * this)`.
- The saved comments and tags include `feargrid-weight-wave826` and `wave826-readback-verified`.
- The observed caller passes the tracked object as the ECX receiver before the call.

What remains unproven:

- Exact tracked-object class.
- `DAT_008553f8` entry schema beyond observed fields.
- Exact scalar semantics.
- Runtime AI/fear behavior.
- BEA patching behavior.
- Rebuild parity.
