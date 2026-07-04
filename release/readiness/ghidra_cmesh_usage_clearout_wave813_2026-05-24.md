# Ghidra CMesh Usage Clearout Wave813 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `cmesh-usage-clearout-wave813`

Wave813 CMesh usage clearout saved signatures, comments, and tags for four adjacent CMesh static resource-lifetime helpers from `0x004a52b0 CMesh__ClearAllUsageMarkers` through `0x004a5430 CMesh__FreeUnusedAndReportLeaks`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004a52b0 CMesh__ClearAllUsageMarkers` | Walks global mesh list `DAT_00704ad8` through next-link `+0x158`, clears usage/ref marker `+0x170`, then calls `CMesh__ClearOut`. |
| `0x004a52d0 CMesh__ClearOut` | Releases default embedded mesh resource `DAT_00704adc`, repeatedly frees global mesh-list entries whose usage/ref marker `+0x170` is zero, and emits no-leak or leak-report `DebugTrace` output. |
| `0x004a53f0 CMesh__StatusLoadingMeshResources` | Formats loading-status string `0x0062f9a0` (`Loading mesh resources`) and routes it through `CConsole__Status` / `CConsole__StatusDone` on `DAT_00663498`. |
| `0x004a5430 CMesh__FreeUnusedAndReportLeaks` | Resets `DAT_00704ae0`, frees unused global mesh-list entries, and emits end-of-level mesh leak report strings, including leaked mesh format string `0x0062f938`. |

Read-back evidence:

- `ApplyCMeshUsageClearoutWave813.java dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=4 missing=0 bad=0`
- `ApplyCMeshUsageClearoutWave813.java apply`: `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=4 missing=0 bad=0`
- `ApplyCMeshUsageClearoutWave813.java final dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 4 metadata rows, 4 tag rows, 8 xref rows, 484 instruction rows, 4 decompile rows, 4 caller metadata rows, 4 caller decompile rows, and 147 callsite instruction rows.
- Queue after Wave813: 6098 total, 5591 commented, 507 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5591/6098 = 91.69%`, strict clean-signature proxy `5591/6098 = 91.69%`.
- Next raw commentless row: `0x004aa4e0 CRTMesh__SumSubtreeField1C`.
- Commentless high-signal, signature, and name-confidence queues are empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-134919_post_wave813_cmesh_usage_clearout_verified`, 19 files, 171346823 bytes, `DiffCount=0`.

What this proves:

- The four target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ... (void)` with no parameters.
- The saved comments and tags include `cmesh-usage-clearout-wave813` and `wave813-readback-verified`.
- The observed static bodies are tied to global mesh-list cleanup/status/leak-report evidence and to callers in CLTShell shutdown, frontend loading/release, CGame loading, and one raw callsite at `0x0046ca13` that Ghidra does not currently attach to a function.

What remains unproven:

- Exact `CMesh` list/resource layout.
- Runtime shutdown/loading/end-of-level leak behavior.
- BEA patching behavior.
- Rebuild parity.
