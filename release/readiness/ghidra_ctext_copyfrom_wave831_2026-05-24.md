# Ghidra CText CopyFrom Wave831 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `ctext-copyfrom-wave831`

Wave831 CText CopyFrom saved a bounded comment/tag hardening for `0x004f2660 CText__CopyFrom` after serialized headless dry/apply/read-back with the `ctext-copyfrom-wave831` and `wave831-readback-verified` tags. The pass made no rename, no signature change, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004f2660 CText__CopyFrom` | Existing signature `void __thiscall CText__CopyFrom(void * this, void * src)`; body frees the destination backing buffer with `CDXMemoryManager__Free`, copies source CText fields, allocates a new buffer through `CDXMemoryManager__Alloc`, copies bytes with `REP MOVSD/REP MOVSB`, and rebases destination text/audio pool pointers from source-buffer-relative offsets. |
| `0x00466ab0 CFrontEnd__SetLanguage` | Caller xref at `0x00466ace`; decompile calls `CFEPOptions__Cleanup()` then `CText__CopyFrom(&g_Text, (language_index * 3 + 0xbf4) * 0x10 + this)`, tying the helper to frontend language switching. |
| `0x00632dd8` | `text.cpp` debug path used by the allocation call; allocation type is `0x72` and source line token is `0x155`. |

Read-back evidence:

- `ApplyCTextCopyFromWave831.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyCTextCopyFromWave831.java apply`: `READBACK_OK` and `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`, with `REPORT: Save succeeded`
- `ApplyCTextCopyFromWave831.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 105 target instruction rows, 1 target decompile row, 9 CText context metadata rows, 9 CText context decompile rows, 1 caller metadata row, 105 caller instruction rows, and 1 caller decompile row.
- Queue after Wave831: 6098 total, 5652 commented, 446 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5652/6098 = 92.69%`, strict proxy `5652/6098 = 92.69%`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Next raw commentless row: `0x004f2710 CTextureBase__Init`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-224036_post_wave831_ctext_copyfrom_verified`, 19 files, 171772807 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project as `0x004f2660 CText__CopyFrom`.
- The saved signature remains `void __thiscall CText__CopyFrom(void * this, void * src)`.
- The saved comment and tags include `ctext-copyfrom-wave831` and `wave831-readback-verified`.
- Static retail Ghidra evidence ties the helper to `CFrontEnd__SetLanguage`, `g_Text`, `CDXMemoryManager__Free`, `CDXMemoryManager__Alloc`, debug path `0x00632dd8`, allocation type `0x72`, line token `0x155`, and pointer rebasing after buffer copy.

What remains unproven:

- Exact `text.cpp` source body identity.
- Concrete CText layout beyond observed offsets.
- Runtime language-switch behavior.
- Runtime localization behavior.
- Allocator ownership beyond the observed memory-manager calls.
- BEA patching behavior.
- Rebuild parity.
