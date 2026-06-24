# Ghidra StrCopyN Helper Wave825 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `strcopyn-helper-wave825`

Wave825 StrCopyN helper saved comments and tags for the raw-commentless bounded string-copy helper at `0x004d6240 StrCopyN`. The existing saved signature was already `char * __cdecl StrCopyN(char * dst, char * src, int maxLen)`, so the pass made no rename, no signature change, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004d6240 StrCopyN` | Returns the original `dst`, exits immediately when `maxLen < 1`, copies bytes from `src` to `dst` while the countdown remains positive, stops after copying the first NUL byte, and otherwise stops when `maxLen` is exhausted. |
| `0x00441740 CConsole__Printf` | Calls `StrCopyN` at `0x0044185c` to copy the formatted 700-byte stack buffer into the active 0x50-byte console ring entry, then clears the final byte at entry offset `0x58`. |
| `0x004418a0 CConsole__PrintfNoNewline` | Calls `StrCopyN` at `0x00441998` to copy the formatted 256-byte stack buffer into the same 0x50-byte console ring-entry layout, then clears the final byte at entry offset `0x58`. |

Read-back evidence:

- `ApplyStrCopyNHelperWave825.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyStrCopyNHelperWave825.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyStrCopyNHelperWave825.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 2 xref rows, 241 target instruction rows, 1 target decompile row, 2 caller metadata rows, 342 caller instruction rows, and 2 caller decompile rows.
- Queue after Wave825: 6098 total, 5633 commented, 465 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5633/6098 = 92.37%`, strict clean-signature proxy `5633/6098 = 92.37%`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Next raw commentless row: `0x004daff0 CFearGrid__LookupFearWeightByArchetype`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-193427_post_wave825_strcopyn_helper_verified`, 19 files, 171576199 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved signature remains `char * __cdecl StrCopyN(char * dst, char * src, int maxLen)`.
- The saved comment and tags include `strcopyn-helper-wave825` and `wave825-readback-verified`.
- The observed body and two console callers are static retail Ghidra evidence only.

What remains unproven:

- Exact source-body identity.
- Exact console buffer lifetime.
- Runtime truncation policy.
- Runtime console output behavior.
- BEA patching behavior.
- Rebuild parity.
