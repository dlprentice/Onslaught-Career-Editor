# Ghidra SPtrSet Clear Wave797 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `sptrset-clear-wave797`

Wave797 SPtrSet clear saved a comment and tags for the raw commentless queue head `0x0042f220 CSPtrSet__Clear`. The pass made no renames, no signature changes, no function-boundary changes, and no executable-byte changes.

Static anchors:

| Address | Evidence |
| --- | --- |
| `0x0042f220 CSPtrSet__Clear` | Five-byte unconditional jump thunk (`E9 3B 6A 0B 00`) to canonical `0x004e5c60 CSPtrSet__Clear`. |
| `0x004e5c60 CSPtrSet__Clear` | Canonical SPtrSet body: if `mSize(+0xc)` is non-zero, links `mLast->next` to `g_SPtrSet_FreeListHead` when `mLast` is non-null, moves `mFirst` into `g_SPtrSet_FreeListHead`, and zeros `mFirst(+0)`, `mLast(+4)`, and `mSize(+0xc)` without touching iterator `+0x08`. |
| Xref context | Post export verified `164` xref rows to the thunk and `686` helper xref rows across the SPtrSet helper family. |

Read-back evidence:

- `ApplySPtrSetClearWave797.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplySPtrSetClearWave797.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplySPtrSetClearWave797.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 164 xref rows, 65 instruction rows, 1 decompile row, 12 helper metadata rows, 686 helper xref rows, and 12 helper decompile rows.
- Queue after Wave797: 6098 total, 5545 commented, 553 commentless, 0 exact-undefined signatures, 0 param_N signatures, comment-backed proxy `5545/6098 = 90.93%`, strict clean-signature proxy `5545/6098 = 90.93%`.
- Next raw commentless row is `0x004404f0 CThing__NegateVec3ToOut`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-054154_post_wave797_sptrset_clear_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra row at `0x0042f220` has the expected `void __fastcall CSPtrSet__Clear(void * this)` signature, Wave797 comment, and tags.
- The thunk instruction and decompile/read-back evidence tie `0x0042f220` to the canonical SPtrSet clear body at `0x004e5c60`.
- The queue advanced by one comment-backed and strict-clean row while signature debt stayed at zero.

What remains unproven:

- Exact source identity.
- Exact embedded-list owners for every xref.
- Runtime pool behavior.
- BEA patching behavior.
- Rebuild parity.
