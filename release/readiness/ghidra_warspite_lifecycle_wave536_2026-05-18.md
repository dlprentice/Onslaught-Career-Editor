# Ghidra Warspite Lifecycle Wave536 Readiness

Date: 2026-05-18
Scope: Static Ghidra signature/comment/tag hardening for six Warspite and WarspiteDome lifecycle helpers.

## Targets

| Address | Saved state |
| --- | --- |
| `0x00504460` | `void __thiscall CWarspite__Create(void * this, void * init_context)` |
| `0x005044f0` | `void * __thiscall CWarspite__ScalarDeletingDestructor(void * this, byte delete_flags)` |
| `0x00504510` | `void __fastcall CWarspite__Destructor(void * this)` |
| `0x005047e0` | `void __thiscall CWarspiteDome__Init(void * this, void * init_context)` |
| `0x00504990` | `void * __thiscall CWarspiteDome__ScalarDeletingDestructor(void * this, byte delete_flags)` |
| `0x005049b0` | `void __fastcall CWarspiteDome__Destructor(void * this)` |

## Evidence

- Read-only pre-export covered metadata, tags, xrefs, full entry-neighborhood instructions, and decompiles under `subagents/ghidra-static-reaudit/wave536-warspite-lifecycle-00504460/`.
- `ApplyWarspiteLifecycleWave536.java` dry-run: `updated=0 skipped=6 renamed=0 would_rename=1 missing=0 bad=0`.
- An initial apply attempt exposed a Ghidra `__thiscall` hidden-`this` read-back mismatch on `0x00504460`; the spec/probe were corrected before the final saved apply.
- Final apply: `updated=6 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final verify dry-run: `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post read-back verified `6` metadata rows, `6` tag rows, `6` target xref rows, `5527` instruction rows, and `6` target decompile exports.
- Focused probe passed: `py -3 tools\ghidra_warspite_lifecycle_wave536_probe.py --check`.
- NPM wrapper passed: `cmd.exe /c npm run test:ghidra-warspite-lifecycle-wave536`.
- Static re-audit queue passed: `cmd.exe /c npm run test:ghidra-static-reaudit-queue`.

## Queue Snapshot

- Total functions: `6083`
- Commented functions: `2609`
- Commentless functions: `3474`
- Exact-undefined signatures: `1545`
- `param_N` signatures: `1315`
- Comment-backed proxy: `2609/6083 = 42.89%`
- Strict comment-plus-clean-signature proxy: `2555/6083 = 42.00%`

These percentages are telemetry only, not completion or correctness certification.

## Backup

Verified saved-project backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260518-064708_post_wave536_warspite_lifecycle_verified
```

Backup verification: `19` files, `159222663` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Not Proven

Wave536 is static retail Ghidra metadata evidence only. It does not prove runtime Warspite AI behavior, runtime dome motion behavior, exact concrete Warspite/WarspiteDome layouts, exact source-body identity, allocator ownership beyond observed free paths, BEA launch behavior, executable patching, or rebuild parity.
